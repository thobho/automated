"""The page measuring tool of the test set (US-11.3B) in a real browser: axe names a rule and its
impact for an element without an accessible name, and one package is measured at 360 px and
1440 px against the live server (Lighthouse is stubbed here: the `pages` CI workflow runs it)."""

from pathlib import Path

import pytest

from apps.profiles.ai import images


def test_axe_names_the_rule_and_the_impact_of_a_button_without_a_name(page):
    from apps.quality import pagemetrics

    page.set_content(
        "<!doctype html><html lang='pl'><title>t</title><main><button></button></main>"
    )
    summary = pagemetrics.run_axe(page)
    rules = {(v["id"], v["impact"]) for v in summary["violations"]}
    assert ("button-name", "critical") in rules
    assert summary["by_impact"]["critical"] >= 1
    failing = pagemetrics.failures(
        [
            {
                "slug": "fixture",
                "axe": {"360": summary, "1440": summary},
                "lighthouse": {"status": "ok", "performance": 90, "lcp_ms": 1000},
            }
        ]
    )
    assert any("button-name" in line for line in failing)


@pytest.mark.usefixtures("django_db_blocker")
def test_one_package_is_measured_at_both_widths_against_the_live_server(
    base_url, browser, django_db_blocker, tmp_path, shot_dir
):
    from apps.quality import pagemetrics, testset

    def capture(url, cookie):  # the test's own browser: Playwright cannot be started twice
        return {w: pagemetrics.capture_width(browser, url, cookie, w) for w in pagemetrics.WIDTHS}

    with django_db_blocker.unblock():
        package = testset.get_package("gliniane-ludki")
        (result,) = pagemetrics.measure(
            [package],
            base_url,
            tmp_path,
            review=False,
            capturer=capture,
            lighthouse=lambda *a: {"status": "ok", "performance": 100, "lcp_ms": 900},
        )
    for width in ("360", "1440"):
        assert result["axe"][width]["status"] == "ok", result["axe"][width]
        assert result["axe"][width]["by_impact"]["critical"] == 0
        png = Path(tmp_path / result["screenshots"][width]).read_bytes()
        assert images.sniff(png) == "image/png"
        (shot_dir / f"page-metrics-{width}.png").write_bytes(png)
    assert pagemetrics.failures([result]) == []
