"""Automatic evaluation, part 2 (US-11.3B): page metrics, screenshot review, command. The browser
and Lighthouse are replaced by fakes; the fake AI client answers the review. No network."""

import json
from decimal import Decimal
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import CommandError, call_command

from apps.accounts.tests.conftest import queue  # noqa: F401  (fixture)
from apps.profiles import ai
from apps.profiles.ai import images
from apps.profiles.models import AICall
from apps.quality import evaluation, pagemetrics, screenshots, testset
from apps.quality.models import PageMetrics, RegistryImmutable

from .test_evaluation import (
    Script,
    _env,  # noqa: F401  (fixture)
)

pytestmark = pytest.mark.django_db

SLUG = "gliniane-ludki"


@pytest.fixture
def script(monkeypatch):
    return lambda **kwargs: Script(monkeypatch, **kwargs)


PNG = images.PNG_MAGIC + b"PIXELDATA"


def good_axe(**counts):
    violations = [
        {"id": rule, "impact": impact, "help": "h", "nodes": [{}]}
        for impact, rule in counts.items()
    ]
    return pagemetrics.summarise_axe(violations)


def fake_capture(axe=None, png=PNG):
    def capture(base_url, cookie):
        assert cookie[0] == "sessionid" and cookie[1]
        return {w: {"png": png, "axe": axe or good_axe(minor="region")} for w in pagemetrics.WIDTHS}

    return capture


def lighthouse_ok(base_url, cookie):
    return {"status": "ok", "performance": 91, "lcp_ms": 1800}


def package(slug=SLUG):
    return testset.get_package(slug)


def measure(tmp_path, **kwargs):
    kwargs.setdefault("capturer", fake_capture())
    kwargs.setdefault("lighthouse", lighthouse_ok)
    return pagemetrics.measure([package()], "http://x.test", tmp_path, **kwargs)


def test_a_package_has_axe_and_screenshots_for_both_widths_and_one_lighthouse_score(tmp_path):
    (result,) = measure(tmp_path)
    assert set(result["axe"]) == {"360", "1440"}
    assert result["axe"]["360"]["violations"][0]["id"] == "region"
    assert result["lighthouse"] == {"status": "ok", "performance": 91, "lcp_ms": 1800}
    assert (tmp_path / f"{SLUG}-360.png").read_bytes() == PNG
    assert (tmp_path / f"{SLUG}-1440.png").exists()
    assert result["review"]["status"] == "ok"
    assert set(result["review"]["viewports"]) == {"360", "1440"}
    assert pagemetrics.failures([result]) == []


def test_the_page_shown_is_the_scripted_profile_without_a_run_and_is_not_duplicated(tmp_path):
    from apps.profiles import pages

    (first,) = measure(tmp_path)
    artist = testset.load_package(SLUG)
    versions = pages.versions_of(artist)
    assert len(versions) == 1 and versions[0].content["tagline"]
    measure(tmp_path)
    assert len(pages.versions_of(artist)) == 1
    assert first["origin"] == "synthetic"


def test_the_axe_rule_and_impact_are_named_and_a_critical_one_is_a_failure(tmp_path):
    axe = good_axe(critical="button-name")
    (result,) = measure(tmp_path, capturer=fake_capture(axe))
    assert result["axe"]["360"]["violations"][0] == {
        "id": "button-name",
        "impact": "critical",
        "help": "h",
        "nodes": 1,
    }
    problems = pagemetrics.failures([result])
    assert any("button-name" in p and "critical" in p for p in problems)


def test_a_missing_axe_result_is_brak_pomiaru_and_a_failure(tmp_path):
    def broken(base_url, cookie):
        return {
            360: {"png": None, "axe": pagemetrics.missing("Playwright nie jest zainstalowany")},
            1440: {"png": PNG, "axe": good_axe()},
        }

    (result,) = measure(tmp_path, capturer=broken)
    assert result["axe"]["360"]["status"] == "brak pomiaru"
    assert result["review"]["status"] == "brak oceny"
    assert "zrzut" in result["review"]["reason"]
    assert any("brak pomiaru" in p for p in pagemetrics.failures([result]))


def test_lighthouse_retries_three_times_then_is_brak_pomiaru_with_the_reason(tmp_path):
    calls, sleeps = [], []

    def runner(command, **kwargs):
        calls.append(command)

    result = pagemetrics.run_lighthouse(
        "http://x.test", ("sessionid", "abc"), runner=runner, sleep=sleeps.append
    )
    assert len(calls) == 3 and len(sleeps) == 2
    assert result["status"] == "brak pomiaru" and "3 próbach" in result["reason"]
    assert calls[0][:3] == ["npx", "--yes", "lighthouse@12"]
    assert "--form-factor=mobile" in calls[0] and "abc" in " ".join(calls[0])
    (checked,) = measure(tmp_path, lighthouse=lambda *a: result)
    assert any("Lighthouse" in p for p in pagemetrics.failures([checked]))


def test_lighthouse_reads_the_report_of_a_later_attempt():
    attempts = []

    def runner(command, **kwargs):
        attempts.append(1)
        if len(attempts) == 2:
            path = next(c for c in command if c.startswith("--output-path=")).split("=", 1)[1]
            report = {
                "audits": {"largest-contentful-paint": {"numericValue": 2149.6}},
                "categories": {"performance": {"score": 0.84}},
            }
            Path(path).write_text(json.dumps(report))

    result = pagemetrics.run_lighthouse(
        "http://x.test", ("sessionid", "abc"), runner=runner, sleep=lambda s: None
    )
    assert result == {"status": "ok", "performance": 84, "lcp_ms": 2150}
    table = pagemetrics.markdown_table(
        [{"slug": "a", "axe": {}, "lighthouse": result, "review": {"status": "brak oceny"}}]
    )
    assert "84 ⚠️" in table


def test_a_missing_node_is_brak_pomiaru_not_a_score():
    def runner(command, **kwargs):
        raise FileNotFoundError("npx")

    result = pagemetrics.run_lighthouse("http://x.test", ("a", "b"), runner=runner)
    assert result["status"] == "brak pomiaru" and "npx" in result["reason"]


def test_the_review_sends_two_images_and_no_image_data_is_stored_or_logged(tmp_path, monkeypatch):
    client = ai.FakeClient(cost_usd="0.003")
    monkeypatch.setattr(ai, "get_client", lambda: client)
    (result,) = measure(tmp_path)
    (request,) = client.requests
    parts = request.messages[1]["content"]
    assert [p["type"] for p in parts] == ["text", "image", "image"]
    assert request.purpose == "page_screenshot_review"
    # no generator reasoning, no validator report: the instructions and the two images only
    assert "validator" not in json.dumps(request.messages[0]).lower()
    call = AICall.objects.get(purpose="page_screenshot_review")
    assert "PIXELDATA" not in json.dumps([str(getattr(call, f.name)) for f in call._meta.fields])
    assert result["review"]["cost_usd"] == "0.003"


def test_a_package_that_is_not_synthetic_sends_nothing(monkeypatch):
    client = ai.FakeClient()
    monkeypatch.setattr(ai, "get_client", lambda: client)
    other = {**package(), "origin": "consented"}
    with pytest.raises(screenshots.ScreenshotRefused):
        screenshots.review_screenshots(other, {360: PNG, 1440: PNG}, 1)
    assert client.requests == [] and AICall.objects.count() == 0


@pytest.mark.parametrize(
    "reply",
    [
        "not json",
        json.dumps({"viewports": {"360": {"verdict": "ok", "problems": []}}}),
        json.dumps(
            {
                "viewports": {
                    "360": {
                        "verdict": "ok",
                        "problems": [{"kind": "empty_place", "description": "x", "place": "y"}],
                    },
                    "1440": {"verdict": "ok", "problems": []},
                }
            }
        ),
        json.dumps(
            {
                "viewports": {
                    "360": {
                        "verdict": "problem",
                        "problems": [{"kind": "colour", "description": "x", "place": "y"}],
                    },
                    "1440": {"verdict": "ok", "problems": []},
                }
            }
        ),
    ],
)
def test_an_invalid_reply_is_brak_oceny_and_the_other_results_stay(tmp_path, monkeypatch, reply):
    monkeypatch.setattr(ai, "get_client", lambda: ai.FakeClient(reply=reply))
    (result,) = measure(tmp_path)
    assert result["review"]["status"] == "brak oceny" and result["review"]["reason"]
    assert result["axe"]["360"]["status"] == "ok" and result["lighthouse"]["status"] == "ok"
    assert pagemetrics.failures([result]) == []


def test_problems_of_a_reply_are_kept(tmp_path, monkeypatch):
    reply = {
        "viewports": {
            "360": {
                "verdict": "problem",
                "problems": [
                    {"kind": "cut_off_content", "description": "Ucięty", "place": "galeria"}
                ],
            },
            "1440": {"verdict": "ok", "problems": []},
        }
    }
    monkeypatch.setattr(ai, "get_client", lambda: ai.FakeClient(reply=json.dumps(reply)))
    (result,) = measure(tmp_path)
    assert result["review"]["viewports"] == reply["viewports"]
    assert "360: problem (1)" in pagemetrics.markdown_table([result])


def test_the_cost_cap_is_brak_oceny(tmp_path, settings, monkeypatch):
    settings.AI_DAILY_CAP_USD = "0.0001"
    client = ai.FakeClient()
    monkeypatch.setattr(ai, "get_client", lambda: client)
    (result,) = measure(tmp_path)
    assert (
        result["review"]
        == {
            "status": "brak oceny",
            "reason": "limit kosztów AI",
            "viewports": {},
            "call_ids": [],
            "cost_usd": "0",
        }
        or result["review"]["status"] == "brak oceny"
    )
    assert client.requests == []
    assert result["axe"]["360"]["status"] == "ok"


def test_the_kill_switch_is_brak_oceny(tmp_path, settings):
    settings.AI_KILL_SWITCH = True
    (result,) = measure(tmp_path)
    assert result["review"]["status"] == "brak oceny"


def test_no_review_flag_skips_the_call(tmp_path, monkeypatch):
    client = ai.FakeClient()
    monkeypatch.setattr(ai, "get_client", lambda: client)
    (result,) = measure(tmp_path, review=False)
    assert client.requests == [] and "pominięto" in result["review"]["reason"]


# --- with a run ----------------------------------------------------------------------------


def test_metrics_of_a_run_are_stored_once_and_appear_in_the_report(script, tmp_path):
    script()
    run = evaluation.evaluate(evaluation.start_run([SLUG]))
    results = pagemetrics.measure(
        [package()],
        "http://x.test",
        tmp_path,
        run=run,
        capturer=fake_capture(),
        lighthouse=lighthouse_ok,
    )
    row = run.evaluations.get()
    metrics = PageMetrics.objects.get(evaluation=row)
    assert metrics.lighthouse["performance"] == 91 and metrics.axe["1440"]["status"] == "ok"
    assert metrics.review_call_ids == results[0]["review"]["call_ids"]
    assert {"instructions:page_screenshot_review", "schema:page_screenshot_review"} == set(
        metrics.components
    )
    report = evaluation.report(run)
    assert report["format"] == "evaluation-report/2"
    assert report["packages"][0]["page_metrics"]["lighthouse"]["lcp_ms"] == 1800
    with pytest.raises(pagemetrics.MeasureRefused, match="already measured"):
        pagemetrics.measure([package()], "http://x.test", tmp_path, run=run)
    assert PageMetrics.objects.count() == 1
    with pytest.raises(RegistryImmutable):
        metrics.save()
    with pytest.raises(RegistryImmutable):
        PageMetrics.objects.all().delete()
    with pytest.raises(RegistryImmutable):
        PageMetrics.objects.update(cost_usd=0)


def test_the_page_of_a_run_is_the_profile_of_its_generation(script, tmp_path):
    from apps.profiles import pages

    script()
    run = evaluation.evaluate(evaluation.start_run([SLUG]))
    pagemetrics.measure(
        [package()], "http://x.test", tmp_path, run=run, capturer=fake_capture(),
        lighthouse=lighthouse_ok, review=False,
    )  # fmt: skip
    artist = testset.load_package(SLUG)
    generation = run.evaluations.get().generation
    content, _ = pages.current_content(artist)
    shown = pages.content_from_profile(generation.result)
    assert content["tagline"] == shown["tagline"] and content["about"] == shown["about"]


def test_a_package_not_in_the_run_is_refused_before_anything_is_measured(script, tmp_path):
    script()
    run = evaluation.evaluate(evaluation.start_run([SLUG]))
    with pytest.raises(pagemetrics.MeasureRefused, match="not evaluated"):
        pagemetrics.measure([package("iluzjonista-marek")], "http://x.test", tmp_path, run=run)


# --- command -------------------------------------------------------------------------------


def command(tmp_path, *args):
    out, err = StringIO(), StringIO()
    call_command(
        "measure_testset_pages", "--output", str(tmp_path / "out"), *args, stdout=out, stderr=err
    )
    return out.getvalue(), err.getvalue()


@pytest.fixture
def fakes(monkeypatch):
    monkeypatch.setattr(pagemetrics, "capture", fake_capture())
    monkeypatch.setattr(pagemetrics, "run_lighthouse", lighthouse_ok)

    def patched(*args, **kwargs):
        kwargs.setdefault("capturer", fake_capture())
        kwargs.setdefault("lighthouse", lighthouse_ok)
        return original(*args, **kwargs)

    original = pagemetrics.measure_package
    monkeypatch.setattr(pagemetrics, "measure_package", patched)


def test_the_command_writes_the_report_and_the_summary(tmp_path, fakes):
    out, _ = command(tmp_path, "--package", SLUG)
    report = json.loads((tmp_path / "out" / "page-metrics.json").read_text("utf-8"))
    assert report["format"] == "page-metrics-report/1" and report["failures"] == []
    assert report["packages"][0]["lighthouse"]["performance"] == 91
    assert SLUG in out and SLUG in (tmp_path / "out" / "summary.md").read_text("utf-8")
    assert (tmp_path / "out" / f"{SLUG}-360.png").exists()


def test_a_critical_violation_makes_the_command_fail_after_writing_the_report(
    tmp_path, monkeypatch
):
    original = pagemetrics.measure_package
    monkeypatch.setattr(
        pagemetrics,
        "measure_package",
        lambda *a, **k: (
            original(
                *a,
                **k,
                capturer=fake_capture(good_axe(critical="button-name")),
                lighthouse=lighthouse_ok,
            )
            if "capturer" not in k
            else original(*a, **k)
        ),
    )
    with pytest.raises(CommandError, match="measurement problem"):
        command(tmp_path, "--package", SLUG)
    assert (tmp_path / "out" / "page-metrics.json").exists()


def test_the_command_with_a_run_writes_the_evaluation_report_and_refuses_a_second_time(
    script, tmp_path, fakes
):
    script()
    run = evaluation.evaluate(evaluation.start_run([SLUG]))
    command(tmp_path, "--run", str(run.pk))
    report = json.loads((tmp_path / "out" / "evaluation-report.json").read_text("utf-8"))
    assert report["packages"][0]["page_metrics"]["axe"]["360"]["status"] == "ok"
    with pytest.raises(CommandError, match="already measured"):
        command(tmp_path, "--run", str(run.pk))
    with pytest.raises(CommandError, match="no such run"):
        command(tmp_path, "--run", "9999")


def test_the_command_refuses_when_the_lab_is_off(tmp_path, settings, fakes):
    settings.QUALITY_LAB_ENABLED = False
    with pytest.raises(CommandError):
        command(tmp_path, "--package", SLUG)


def test_summarise_axe_orders_by_impact():
    summary = good_axe(minor="a", critical="b", serious="c")
    assert [v["impact"] for v in summary["violations"]] == ["critical", "serious", "minor"]
    assert summary["by_impact"] == {"critical": 1, "serious": 1, "moderate": 0, "minor": 1}
    assert Decimal("0") == 0
