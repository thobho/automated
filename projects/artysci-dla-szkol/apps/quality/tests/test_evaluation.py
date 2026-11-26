"""Automatic evaluation, part 1 (US-11.3A): runner, independent reviewer, command, admin.
A scripted fake AI client answers both the generator and the reviewer; no network."""

import copy
import json
from decimal import Decimal
from io import StringIO

import pytest
from django.core.management import CommandError, call_command
from django.test import Client
from django.urls import reverse

from apps.accounts.tests.conftest import make_admin, queue  # noqa: F401  (fixture)
from apps.profiles import ai
from apps.profiles.generator_components import INSTRUCTIONS as GENERATOR_INSTRUCTIONS
from apps.profiles.models import AICall
from apps.quality import evaluation, reviewer, scripted, testset
from apps.quality.models import (
    EvaluationRun,
    Generation,
    PackageEvaluation,
    RegistryImmutable,
)
from apps.trust import services as trust
from config.settings.storage import build_storages

pytestmark = pytest.mark.django_db

SLUGS = ["gliniane-ludki", "iluzjonista-marek", "kwartet-allegretto"]
GOOD_SCORES = {
    "wiernosc": 5,
    "kompletnosc": 4,
    "przydatnosc": 4,
    "jezyk": 5,
    "ton": 5,
    "uczciwosc": 3,
}


@pytest.fixture(autouse=True)
def _env(queue, settings, tmp_path):  # noqa: F811
    settings.STORAGE_BACKEND = "filesystem"
    settings.STORAGES = build_storages(
        "filesystem",
        public_base_url="http://media.test:8101/",
        private_root=tmp_path / "private",
        public_root=tmp_path / "public",
        signed_url_ttl=settings.MEDIA_SIGNED_URL_TTL,
    )
    settings.MALWARE_SCANNER_FAKE_RESULT = "clean"
    settings.QUALITY_LAB_ENABLED = True
    settings.AI_PER_CALL_CAP_USD = "0.05"
    settings.AI_DAILY_CAP_USD = "5"


def good_review(**changes):
    data = {
        "scores": dict(GOOD_SCORES),
        "problems": [
            {"dimension": "ton", "quote": "Sprawdź termin", "explanation": "Zbyt ogólne."}
        ],
    }
    data.update(changes)
    return json.dumps(data)


class Script:
    """Scripted fake client: the draft is the scripted profile of the input, the review a reply
    chosen per call by `review` (a string, a list consumed in order, or a callable)."""

    def __init__(self, monkeypatch, review=None, draft=None, cost="0.002"):
        self.review = review if review is not None else good_review()
        self.draft = draft
        self.review_requests = []
        self.client = ai.FakeClient(reply=self._reply, cost_usd=cost, model="fake/model-1")
        monkeypatch.setattr(ai, "get_client", lambda: self.client)

    def _reply(self, request):
        if request.purpose == "profile_review":
            self.review_requests.append(request)
            item = self.review
            if isinstance(item, list):
                item = item.pop(0)
            return item(request) if callable(item) else item
        if request.purpose != "profile_draft":  # a repair round: the same reply again
            return self.last_draft
        data = json.loads(request.messages[1]["content"])
        self.last_draft = (
            self.draft(data) if self.draft else json.dumps(scripted.scripted_profile(data))
        )
        return self.last_draft


@pytest.fixture
def script(monkeypatch):
    return lambda **kwargs: Script(monkeypatch, **kwargs)


def run_with(*slugs, level=""):
    return evaluation.evaluate(evaluation.start_run(slugs, level))


def test_two_packages_give_a_run_with_scores_problems_and_the_summed_cost(script):
    script()
    run = run_with(*SLUGS[:2])
    assert run.status == EvaluationRun.Status.COMPLETE and run.finished_at
    rows = list(run.evaluations.order_by("slug"))
    assert [r.slug for r in rows] == SLUGS[:2]
    for row in rows:
        assert row.generation_status == "ready" and row.hard_pass
        assert row.validator["ok"] is True and row.validator["hard"] == []
        assert row.expectations and all("passed" in e for e in row.expectations)
        assert (row.score_wiernosc, row.score_kompletnosc, row.score_uczciwosc) == (5, 4, 3)
        assert row.review_status == "ok"
        assert row.problems == [
            {
                "dimension": "ton",
                "quote": "Sprawdź termin",
                "explanation": "Zbyt ogólne.",
                "unverified": False,
            }
        ]
        linked = AICall.objects.filter(profile_generation=row.generation) | AICall.objects.filter(
            pk__in=row.review_call_ids
        )
        assert linked.count() == 2 and row.cost_usd == Decimal("0.004")
    assert run.cost_usd == Decimal("0.008") == sum(c.cost_usd for c in AICall.objects.all())
    assert run.generator_components["instructions:profile_draft"]["version"]
    assert set(run.reviewer_components) == {"instructions:profile_review", "schema:profile_review"}


def test_the_reviewer_is_not_a_generator_component():
    from apps.profiles.generator_components import COMPONENTS

    assert not set(reviewer.COMPONENTS) & set(COMPONENTS)
    assert [c.version for c in reviewer.COMPONENTS] == ["0.1", "0.1"]


def test_the_review_request_holds_only_the_input_and_the_profile(script):
    fake = script()
    run_with(SLUGS[0])
    (request,) = fake.review_requests
    system, user = request.messages
    assert system["content"] == reviewer.INSTRUCTIONS.text()
    payload = json.loads(user["content"])
    assert set(payload) == {"source_input", "profile"}
    assert "artist" in payload["source_input"] and "hero" in payload["profile"]
    assert "claims_audit" not in payload["profile"]
    everything = system["content"] + user["content"]
    assert "claims_audit" not in everything
    assert GENERATOR_INSTRUCTIONS.text() not in everything
    assert "Napraw" not in everything and '"rule"' not in everything  # no repair or findings
    assert request.purpose == "profile_review" and request.schema["title"].startswith("Ocena")


@pytest.mark.parametrize(
    "bad",
    [
        json.dumps({"scores": {**GOOD_SCORES, "ton": 6}, "problems": []}),
        json.dumps(
            {"scores": {k: v for k, v in GOOD_SCORES.items() if k != "jezyk"}, "problems": []}
        ),
        "to nie jest JSON",
        json.dumps({"scores": {**GOOD_SCORES, "ton": 4.5}, "problems": []}),
    ],
)
def test_an_invalid_review_gives_no_scores_and_the_run_goes_on(script, bad):
    fake = script(review=[bad, good_review()])
    run = run_with(*SLUGS[:2])
    first, second = run.evaluations.order_by("slug")
    assert run.status == EvaluationRun.Status.COMPLETE
    assert first.review_status == "brak oceny" and first.review_reason
    assert first.score_ton is None and first.problems == []
    assert "6" not in first.review_reason.split("(")[0] or "schemat" in first.review_reason
    assert second.review_status == "ok" and second.score_ton == 5
    assert len(fake.review_requests) == 2  # one call per package, no retry
    assert evaluation.summary(run)["means"]["ton"] == {"mean": 5.0, "scored": 1}
    assert evaluation.summary(run)["unscored"] == 1


def test_a_quote_that_is_not_in_the_profile_is_marked_unverified(script):
    problems = [
        {"dimension": "jezyk", "quote": "Sprawdź\n  termin", "explanation": "Spacje."},
        {"dimension": "wiernosc", "quote": "Wymyślony cytat spoza profilu", "explanation": "x"},
        {"dimension": "kompletnosc", "quote": "", "explanation": "Brak zdjęć."},
    ]
    script(review=good_review(problems=problems))
    row = run_with(SLUGS[0]).evaluations.get()
    assert [p["unverified"] for p in row.problems] == [False, True, False]
    assert row.problems[1]["quote"] == "Wymyślony cytat spoza profilu"
    assert evaluation.summary(row.run)["unverified_quotes"] == 1


def test_an_error_generation_fails_and_has_no_review_call(script):
    fake = script(draft=lambda data: "nie json")
    row = run_with(SLUGS[0]).evaluations.get()
    assert row.generation_status == "error" and row.hard_pass is False
    assert row.review_status == "brak oceny" and "błędem" in row.review_reason
    assert fake.review_requests == [] and row.review_call_ids == []
    assert row.expectations == [] and row.score_wiernosc is None


def test_a_generation_for_review_fails_the_hard_rules_but_is_reviewed(script):
    def bad(data):
        profile = scripted.scripted_profile(data)
        profile["facts"] = [{"label": "Czas", "value": "45 min (ok)"}]
        return json.dumps(profile)

    fake = script(draft=bad)
    row = run_with(SLUGS[0]).evaluations.get()
    assert row.generation_status == "review" and row.hard_pass is False
    assert row.validator["ok"] is False and row.validator["hard"]
    assert row.validator["repair_rounds"] == 2
    assert row.review_status == "ok" and len(fake.review_requests) == 1
    # profile, validator findings and repair rounds are not shown to the reviewer
    assert '"rule"' not in fake.review_requests[0].messages[1]["content"]
    assert Generation.objects.get(pk=row.generation_id).repair_rounds == 2


def test_the_report_names_the_catalog_code_next_to_a_validator_finding(script):
    def bad(data):
        profile = scripted.scripted_profile(data)
        profile["facts"] = [{"label": "Czas", "value": "45 min (ok)"}]
        profile["seo"]["description"] = "Na podstawie przesłanych materiałów."
        return json.dumps(profile)

    script(draft=bad)
    run = run_with(SLUGS[0])
    report = evaluation.report(run)
    assert report["format"] == "evaluation-report/2"
    hard = report["packages"][0]["validator"]["hard"]
    by_rule = {f["rule"]: f["catalog"] for f in hard}
    assert by_rule["fakty"] == "fakt-z-nawiasem"
    assert by_rule["bez języka procesu i bez dodanych obietnic"] == "jezyk-procesu"
    summary = evaluation.summary(run)
    assert {"slug": SLUGS[0], "code": "jezyk-procesu", "count": 1} in summary["catalog_findings"]


def test_a_finding_whose_rule_is_not_in_the_catalog_has_no_code():
    validator = {"ok": False, "hard": [{"rule": "limity długości", "path": "$"}], "soft": []}
    assert evaluation._with_catalog(validator, {"fakty": "x"})["hard"][0]["catalog"] is None


def test_the_daily_cap_stops_the_run_and_resume_does_the_missing_ones(script, settings):
    fake = script()
    settings.AI_PER_CALL_CAP_USD = "0.01"
    settings.AI_DAILY_CAP_USD = "0.012"
    run = run_with(*SLUGS)
    assert run.status == EvaluationRun.Status.INCOMPLETE and run.note
    assert [r.slug for r in run.evaluations.order_by("slug")] == SLUGS[:1]
    calls = AICall.objects.count()
    assert calls == 2 and len(fake.client.requests) == 2  # nothing was sent after the cap

    settings.AI_DAILY_CAP_USD = "5"
    resumed = evaluation.resume(run.pk)
    assert resumed.pk == run.pk and resumed.status == EvaluationRun.Status.COMPLETE
    assert [r.slug for r in resumed.evaluations.order_by("slug")] == SLUGS
    assert AICall.objects.count() == 6  # only the two missing packages were evaluated
    assert resumed.cost_usd == Decimal("0.012")


def test_the_kill_switch_stops_the_run_without_a_call(script, settings):
    fake = script()
    settings.AI_KILL_SWITCH = True
    run = run_with(SLUGS[0])
    assert run.status == EvaluationRun.Status.INCOMPLETE
    assert run.evaluations.count() == 0 and fake.client.requests == []


def test_resume_refuses_a_changed_reviewer_model_or_package(script, settings, monkeypatch):
    script()
    settings.AI_PER_CALL_CAP_USD = "0.01"
    settings.AI_DAILY_CAP_USD = "0.012"
    run = run_with(*SLUGS[:2])
    assert run.status == EvaluationRun.Status.INCOMPLETE
    settings.AI_DAILY_CAP_USD = "5"

    bumped = reviewer.Component(
        "instructions",
        "profile_review",
        "0.2",
        files=("apps/quality/prompts/review_instructions.md",),
    )
    monkeypatch.setattr(reviewer, "COMPONENTS", (bumped, reviewer.SCHEMA))
    with pytest.raises(evaluation.EvaluationRefused, match="reviewer component"):
        evaluation.resume(run.pk)
    monkeypatch.undo()

    settings.AI_MODEL = "other/model"
    with pytest.raises(evaluation.EvaluationRefused, match="AI model"):
        evaluation.resume(run.pk)
    settings.AI_MODEL = run.generator_model

    real = testset.get_package
    changed = {SLUGS[1]: {**copy.deepcopy(real(SLUGS[1])), "site_text": "Zmieniony tekst."}}
    monkeypatch.setattr(
        testset,
        "check_all",
        lambda: [(s, changed.get(s, real(s)), []) for s in SLUGS[:2]],
    )
    with pytest.raises(evaluation.EvaluationRefused, match="package"):
        evaluation.resume(run.pk)
    run.refresh_from_db()
    assert run.status == EvaluationRun.Status.INCOMPLETE


def test_an_unexpected_error_in_the_review_gives_brak_oceny_and_the_run_goes_on(script):
    def broken(request):
        raise RuntimeError("connection reset")

    script(review=[broken, good_review()])
    run = run_with(*SLUGS[:2])
    assert run.status == EvaluationRun.Status.COMPLETE
    first, second = run.evaluations.order_by("slug")
    assert first.review_status == "brak oceny" and "połączenia" in first.review_reason
    assert "connection reset" not in first.review_reason
    assert second.review_status == "ok"


def test_a_crash_closes_the_run_as_resumable_and_resume_finishes_it(script, monkeypatch):
    script()
    real = testset.load_package

    def flaky(slug):
        if slug == SLUGS[1]:
            raise testset.PackageError("unreadable")
        return real(slug)

    run = evaluation.start_run(SLUGS[:2])
    monkeypatch.setattr(testset, "load_package", flaky)
    with pytest.raises(testset.PackageError):
        evaluation.evaluate(run)
    run.refresh_from_db()
    assert run.status == EvaluationRun.Status.INCOMPLETE and run.note
    assert run.evaluations.count() == 1

    monkeypatch.setattr(testset, "load_package", real)
    resumed = evaluation.resume(run.pk)
    assert resumed.status == EvaluationRun.Status.COMPLETE and resumed.evaluations.count() == 2
    assert resumed.cost_usd == Decimal("0.008") == sum(c.cost_usd for c in AICall.objects.all())


def test_a_stale_running_run_can_be_resumed_a_fresh_one_cannot(script, settings):
    script()
    run = evaluation.start_run(SLUGS[:1])  # `trwa`, as left by a killed process
    with pytest.raises(evaluation.EvaluationRefused, match="not incomplete"):
        evaluation.resume(run.pk)
    settings.GENERATION_STALE_SECONDS = -1
    resumed = evaluation.resume(run.pk)
    assert resumed.status == EvaluationRun.Status.COMPLETE and resumed.evaluations.count() == 1


def test_a_cap_between_generation_and_review_keeps_the_cost_and_resume_redoes_the_package(
    script, settings
):
    fake = script()
    settings.AI_PER_CALL_CAP_USD = "0.01"
    settings.AI_DAILY_CAP_USD = "0.011"  # the generation fits, the review does not
    run = run_with(SLUGS[0])
    assert run.status == EvaluationRun.Status.INCOMPLETE
    assert run.evaluations.count() == 0 and fake.review_requests == []
    assert run.abandoned_cost_usd == Decimal("0.002")
    assert run.cost_usd == Decimal("0.002") == sum(c.cost_usd for c in AICall.objects.all())

    settings.AI_DAILY_CAP_USD = "5"
    resumed = evaluation.resume(run.pk)
    assert resumed.status == EvaluationRun.Status.COMPLETE and resumed.evaluations.count() == 1
    assert resumed.cost_usd == Decimal("0.006") == sum(c.cost_usd for c in AICall.objects.all())


def test_the_kill_switch_at_the_review_keeps_the_generation_cost(script, settings, monkeypatch):
    script()
    real = evaluation.profile_generation.run_generation

    def generate_then_switch_off(pk):
        generation = real(pk)
        settings.AI_KILL_SWITCH = True
        return generation

    monkeypatch.setattr(evaluation.profile_generation, "run_generation", generate_then_switch_off)
    run = run_with(SLUGS[0])
    assert run.status == EvaluationRun.Status.INCOMPLETE and run.evaluations.count() == 0
    assert run.cost_usd == Decimal("0.002") == sum(c.cost_usd for c in AICall.objects.all())


def test_an_invalid_json_generation_that_uses_up_the_cap_is_stored_as_failed(script, settings):
    script(draft=lambda data: "nie json")
    settings.AI_PER_CALL_CAP_USD = "0.01"
    settings.AI_DAILY_CAP_USD = "0.011"
    run = run_with(SLUGS[0])
    assert run.status == EvaluationRun.Status.COMPLETE
    row = run.evaluations.get()
    assert row.generation_status == "error" and row.hard_pass is False
    assert row.review_call_ids == []
    assert run.cost_usd == sum(c.cost_usd for c in AICall.objects.all())


def test_resume_is_refused_when_the_ai_client_changed(script, settings):
    fake = script()
    settings.AI_CLIENT = "openrouter"  # the scripted client stands in for the real one
    settings.AI_PER_CALL_CAP_USD = "0.01"
    settings.AI_DAILY_CAP_USD = "0.012"
    run = run_with(*SLUGS[:2])
    assert run.status == EvaluationRun.Status.INCOMPLETE and run.ai_client == "openrouter"
    assert evaluation.report(run)["run"]["ai_client"] == "openrouter"

    settings.AI_CLIENT = "fake"
    settings.AI_DAILY_CAP_USD = "5"
    calls = len(fake.client.requests)
    with pytest.raises(evaluation.EvaluationRefused, match="AI client"):
        evaluation.resume(run.pk)
    assert len(fake.client.requests) == calls


def test_a_finished_run_and_its_rows_cannot_change(script):
    script()
    run = run_with(SLUGS[0])
    row = run.evaluations.get()
    run.note = "x"
    with pytest.raises(RegistryImmutable):
        run.save()
    with pytest.raises(RegistryImmutable):
        run.delete()
    with pytest.raises(RegistryImmutable):
        EvaluationRun.objects.all().delete()
    with pytest.raises(RegistryImmutable):
        EvaluationRun.objects.all().update(note="x")
    row.score_ton = 1
    with pytest.raises(RegistryImmutable):
        row.save()
    with pytest.raises(RegistryImmutable):
        row.delete()
    with pytest.raises(RegistryImmutable):
        PackageEvaluation.objects.all().delete()
    with pytest.raises(RegistryImmutable):
        PackageEvaluation.objects.all().update(score_ton=1)
    with pytest.raises(evaluation.EvaluationRefused, match="not incomplete"):
        evaluation.resume(run.pk)  # a finished run is not resumed
    with pytest.raises(evaluation.EvaluationRefused, match="already finished"):
        evaluation.evaluate(run)
    with pytest.raises(RegistryImmutable):
        PackageEvaluation.objects.create(
            run=run, slug="x", level="weak", package_hash="0", generation_status="error",
            hard_pass=False, review_status="brak oceny", created_at=run.started_at,
        )  # fmt: skip


def test_the_summary_has_means_per_level_and_the_hard_pass_share(script):
    script(review=[good_review(), good_review(scores={**GOOD_SCORES, "ton": 1}), good_review()])
    run = run_with(*SLUGS)
    data = evaluation.summary(run)
    assert data["packages"] == 3 and data["hard_pass_share"] == 1.0
    assert data["means"]["wiernosc"] == {"mean": 5.0, "scored": 3}
    assert data["means"]["ton"]["mean"] == pytest.approx(3.67, abs=0.01)
    assert set(data["means_by_level"]) <= set(testset.LEVELS) and data["means_by_level"]
    assert data["cost_usd"] == str(run.cost_usd)


# --- command ----------------------------------------------------------------------------------


def command(*args):
    out = StringIO()
    call_command("evaluate_testset", *args, stdout=out)
    return out.getvalue()


def test_the_command_prints_a_line_per_package_a_summary_and_writes_the_report(
    script, tmp_path, settings
):
    script()
    report_file = tmp_path / "report.json"
    output = command("--package", SLUGS[0], "--package", SLUGS[1], "--output", str(report_file))
    lines = output.splitlines()
    assert lines[0].startswith(SLUGS[0]) and lines[1].startswith(SLUGS[1])
    assert "hard rules passed: 2/2" in output and "cost: 0.008" in output
    assert "wiernosc=5.0(2)" in output

    text = report_file.read_text(encoding="utf-8")
    report = json.loads(text)
    assert report["format"] == "evaluation-report/2"
    assert [p["slug"] for p in report["packages"]] == SLUGS[:2]
    package = report["packages"][0]
    assert package["profile"]["hero"] and package["review"]["scores"]["wiernosc"] == 5
    assert package["validator"]["ok"] is True and package["expectations"]
    assert report["summary"]["packages"] == 2
    for forbidden in ("OPENROUTER", "niezależnym recenzentem", GENERATOR_INSTRUCTIONS.text()[:80]):
        assert forbidden not in text
    assert "claims_audit" in text  # only as a key of the profile the generator produced


def test_the_command_with_a_key_file_never_prints_the_key(script, tmp_path):
    script()
    key_file = tmp_path / "secrets.env"
    key_file.write_text("OPENROUTER_API_KEY=sk-or-v1-supersecretvalue\n")
    report_file = tmp_path / "report.json"
    output = command(
        "--package", SLUGS[0], "--key-file", str(key_file), "--output", str(report_file)
    )
    assert "supersecretvalue" not in output + report_file.read_text()


def test_the_command_refuses_when_the_lab_is_off_and_makes_no_ai_call(script, settings):
    fake = script()
    settings.QUALITY_LAB_ENABLED = False
    with pytest.raises(CommandError, match="QUALITY_LAB_ENABLED"):
        command("--package", SLUGS[0])
    assert fake.client.requests == [] and not EvaluationRun.objects.exists()


def test_the_command_refuses_a_consented_package(script, monkeypatch):
    fake = script()
    real = testset.check_all()
    consented = [(s, {**p, "origin": "consented"}, []) for s, p, _ in real if p]
    monkeypatch.setattr(testset, "check_all", lambda: consented)
    with pytest.raises(CommandError, match="consented"):
        command("--package", SLUGS[0])
    assert fake.client.requests == [] and not EvaluationRun.objects.exists()


def test_the_command_refuses_an_unknown_package_and_resume_with_a_selection(script):
    script()
    with pytest.raises(CommandError, match="no such package"):
        command("--package", "nie-ma-takiego")
    with pytest.raises(CommandError, match="--resume"):
        command("--resume", "1", "--package", SLUGS[0])
    with pytest.raises(CommandError, match="no such run"):
        command("--resume", "999")


def test_the_command_level_filter_and_resume(script, settings):
    script()
    settings.AI_PER_CALL_CAP_USD = "0.01"
    settings.AI_DAILY_CAP_USD = "0.012"
    output = command("--level", "weak")
    assert "incomplete" in output.lower() or "niekompletny" in output
    run = EvaluationRun.objects.get()
    assert run.level == "weak"
    assert all(testset.get_package(s)["level"] == "weak" for s in run.slugs)
    settings.AI_DAILY_CAP_USD = "5"
    output = command("--resume", str(run.pk))
    run.refresh_from_db()
    assert run.status == EvaluationRun.Status.COMPLETE and f"run {run.pk}" in output


# --- admin ------------------------------------------------------------------------------------


def test_the_admin_shows_runs_read_only_to_staff_only(script, django_user_model):
    script()
    run = run_with(SLUGS[0])
    row = run.evaluations.get()
    urls = [
        reverse("admin:quality_evaluationrun_changelist"),
        reverse("admin:quality_evaluationrun_change", args=[run.pk]),
        reverse("admin:quality_packageevaluation_changelist"),
        reverse("admin:quality_packageevaluation_change", args=[row.pk]),
    ]
    admin_user = make_admin()
    trust.accept_pending(admin_user, [d.pk for d in trust.pending_acceptances(admin_user)])
    staff = Client()
    staff.force_login(admin_user)
    for url in urls:
        assert staff.get(url).status_code == 200
    assert staff.post(urls[1], {"note": "x"}).status_code == 403
    assert (
        staff.post(reverse("admin:quality_evaluationrun_delete", args=[run.pk])).status_code == 403
    )
    assert staff.get(reverse("admin:quality_evaluationrun_add")).status_code == 403

    user = django_user_model.objects.create_user(
        email="zwykly@example.invalid", password="x-y-z-12345"
    )
    visitor = Client()
    visitor.force_login(user)
    for url in urls:
        assert visitor.get(url).status_code in (302, 403)
