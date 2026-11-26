"""Page metrics of the test set (US-11.3B, D12, D59, D110).

    results = measure(packages, base_url, out_dir, run=None)    # `manage.py measure_testset_pages`

Each package page is the owner preview (`/panel/podglad/`) of the package artist, with the real
template. The page shown is the profile of an evaluation run (`--run`: the generation of the
package evaluation) or the scripted profile (T41) when no run is given. Per package and at 360 px
and 1440 px: a full-page screenshot (a file in the output folder; never git, never public storage)
and the axe violations by impact; plus one Lighthouse 12 mobile run (performance score, LCP), run
like the `lighthouse` CI job with up to 3 attempts. A tool that is missing or a measurement that
fails is stored as `brak pomiaru` with the reason, never as a score. With a run the result is
stored append-only in `PageMetrics`, once per package evaluation. The screenshot review by a vision
model is `apps.quality.screenshots`.
"""

import json
import logging
import os
import subprocess  # noqa: S404  (runs Lighthouse with a fixed argument list, no shell)
import tempfile
import time
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.test import Client
from django.utils import timezone

from apps.profiles import inputs, pages
from apps.profiles.models import PageVersion
from apps.quality import screenshots, scripted, testset
from apps.quality.models import EvaluationRun, PackageEvaluation, PageMetrics

logger = logging.getLogger("apps.quality.pagemetrics")

PREVIEW_PATH = "/panel/podglad/"
WIDTHS = screenshots.VIEWPORTS
VIEWPORT_HEIGHT = 900
IMPACTS = ("critical", "serious", "moderate", "minor")
NO_MEASUREMENT = "brak pomiaru"
OK = "ok"
LIGHTHOUSE_ATTEMPTS = 3
LIGHTHOUSE_TIMEOUT_SECONDS = 300
LIGHTHOUSE_RETRY_PAUSE_SECONDS = 5
LIGHTHOUSE_VERSION = "12"
LIGHTHOUSE_WARN_BELOW = 85  # shown, never enforced here (US-3.8)
REPORT_FORMAT = "page-metrics-report/1"


class MeasureRefused(Exception):
    """The measurement cannot start. The message says why."""


def missing(reason: str) -> dict:
    return {"status": NO_MEASUREMENT, "reason": reason[:300]}


# --- axe and screenshots (Playwright) ----------------------------------------------------------


def summarise_axe(violations: list[dict]) -> dict:
    """axe violations as `{id, impact, help, nodes}` plus the counts by impact."""
    rows = [
        {
            "id": v.get("id", ""),
            "impact": v.get("impact") or "minor",
            "help": v.get("help", ""),
            "nodes": len(v.get("nodes", [])),
        }
        for v in violations
    ]
    rows.sort(key=lambda r: (IMPACTS.index(r["impact"]) if r["impact"] in IMPACTS else 9, r["id"]))
    by_impact = {impact: sum(1 for r in rows if r["impact"] == impact) for impact in IMPACTS}
    return {"status": OK, "violations": rows, "by_impact": by_impact}


def run_axe(page) -> dict:
    from axe_playwright_python.sync_playwright import Axe

    return summarise_axe(Axe().run(page).response["violations"])


def capture(base_url: str, cookie: tuple[str, str]) -> dict[int, dict]:
    """`{width: {"png": bytes | None, "axe": dict}}` for the preview page. Never raises: a
    missing Playwright or a failed width is `brak pomiaru` with the reason."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        reason = "Playwright nie jest zainstalowany (uv sync --group e2e)"
        return {w: {"png": None, "axe": missing(reason)} for w in WIDTHS}
    out: dict[int, dict] = {}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                for width in WIDTHS:
                    out[width] = _capture_width(browser, base_url, cookie, width)
            finally:
                browser.close()
    except Exception as exc:  # browser missing or crashed
        reason = f"przeglądarka niedostępna ({type(exc).__name__})"
        for width in WIDTHS:
            out.setdefault(width, {"png": None, "axe": missing(reason)})
    return out


def _capture_width(browser, base_url: str, cookie: tuple[str, str], width: int) -> dict:
    context = browser.new_context(viewport={"width": width, "height": VIEWPORT_HEIGHT})
    try:
        context.add_cookies([{"name": cookie[0], "value": cookie[1], "url": base_url}])
        page = context.new_page()
        response = page.goto(base_url + PREVIEW_PATH, wait_until="networkidle")
        if response is None or response.status != 200:
            return {
                "png": None,
                "axe": missing(f"strona zwróciła HTTP {getattr(response, 'status', '?')}"),
            }
        png = page.screenshot(full_page=True, type="png")
        try:
            axe = run_axe(page)
        except Exception as exc:
            axe = missing(f"axe nie zadziałał ({type(exc).__name__})")
        return {"png": png, "axe": axe}
    except Exception as exc:
        return {"png": None, "axe": missing(f"pomiar nie powiódł się ({type(exc).__name__})")}
    finally:
        context.close()


# --- Lighthouse --------------------------------------------------------------------------------


def _chrome_path() -> str | None:
    if os.environ.get("CHROME_PATH"):
        return None
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            return playwright.chromium.executable_path
    except Exception:
        return None


def lighthouse_command(url: str, cookie: tuple[str, str], output: Path) -> list[str]:
    headers = json.dumps({"Cookie": f"{cookie[0]}={cookie[1]}"})
    return [
        "npx",
        "--yes",
        f"lighthouse@{LIGHTHOUSE_VERSION}",
        url,
        "--only-categories=performance",
        "--form-factor=mobile",
        "--quiet",
        f"--extra-headers={headers}",
        # One renderer process: otherwise the trace can miss navigationStart (NO_NAVSTART, #181).
        "--chrome-flags=--headless=new --no-sandbox --renderer-process-limit=1",
        "--output=json",
        f"--output-path={output}",
    ]


def read_lighthouse(path: Path) -> dict | None:
    """Score (0-100) and LCP (ms) from a Lighthouse JSON report; None when it has no LCP."""
    try:
        report = json.loads(path.read_text("utf-8"))
        lcp = report["audits"]["largest-contentful-paint"]["numericValue"]
        score = report["categories"]["performance"]["score"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if lcp is None or score is None:
        return None
    return {"status": OK, "performance": round(score * 100), "lcp_ms": round(lcp)}


def run_lighthouse(
    base_url: str,
    cookie: tuple[str, str],
    *,
    runner: Callable = subprocess.run,
    sleep: Callable = time.sleep,
    attempts: int = LIGHTHOUSE_ATTEMPTS,
) -> dict:
    """Lighthouse 12 mobile performance of the preview, retried when no report is produced
    (as in the `lighthouse` CI job). Never raises."""
    env = dict(os.environ)
    chrome = _chrome_path()
    if chrome:
        env["CHROME_PATH"] = chrome
    reason = ""
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "lighthouse.json"
        command = lighthouse_command(base_url + PREVIEW_PATH, cookie, output)
        for attempt in range(1, attempts + 1):
            output.unlink(missing_ok=True)
            try:
                runner(  # noqa: S603  (fixed argument list)
                    command,
                    env=env,
                    capture_output=True,
                    timeout=LIGHTHOUSE_TIMEOUT_SECONDS,
                    check=False,
                )
            except FileNotFoundError:
                return missing("Lighthouse niedostępny: brak npx (Node.js)")
            except subprocess.TimeoutExpired:
                reason = "przekroczono czas"
            except OSError as exc:
                reason = f"nie uruchomiono ({type(exc).__name__})"
            else:
                result = read_lighthouse(output)
                if result:
                    return result
                reason = "Lighthouse nie zapisał raportu"
            if attempt < attempts:
                sleep(LIGHTHOUSE_RETRY_PAUSE_SECONDS)
    return missing(f"{reason} po {attempts} próbach")


# --- the page shown ----------------------------------------------------------------------------


def show_profile(artist, profile: dict) -> None:
    """Make `profile` the current page of the artist (a new version only when it differs)."""
    content = pages.content_from_profile(profile)
    current, _ = pages.current_content(artist)
    if current != {**pages.empty_content(), **content}:
        pages.create_version(artist, content, PageVersion.Source.GENERATED, [])


def session_cookie(artist) -> tuple[str, str]:
    client = Client()
    client.force_login(artist.user)
    return settings.SESSION_COOKIE_NAME, client.cookies[settings.SESSION_COOKIE_NAME].value


def _profile_for(artist, evaluation: PackageEvaluation | None) -> tuple[dict | None, str]:
    if evaluation is None:
        return scripted.scripted_profile(inputs.build_input(artist)), ""
    generation = evaluation.generation
    if generation is None or not isinstance(generation.result, dict):
        return None, "ocena pakietu nie ma wygenerowanego profilu"
    return generation.result, ""


# --- one package and the whole set -------------------------------------------------------------


def measure_package(
    package: dict,
    base_url: str,
    out_dir: Path,
    *,
    evaluation: PackageEvaluation | None = None,
    review: bool = True,
    capturer: Callable = capture,
    lighthouse: Callable = run_lighthouse,
) -> dict:
    slug = package["slug"]
    artist = testset.load_package(slug)
    profile, why = _profile_for(artist, evaluation)
    result = {
        "slug": slug,
        "level": package["level"],
        "origin": package.get("origin", ""),
        "axe": {},
        "lighthouse": {},
        "screenshots": {},
        "review": {"status": screenshots.MISSING, "reason": "nie uruchomiono", "viewports": {}},
    }
    if profile is None:
        for width in WIDTHS:
            result["axe"][str(width)] = missing(why)
        result["lighthouse"] = missing(why)
        result["review"] = {"status": screenshots.MISSING, "reason": why, "viewports": {}}
        return result
    show_profile(artist, profile)
    cookie = session_cookie(artist)
    captured = capturer(base_url, cookie)
    shots: dict[int, bytes] = {}
    for width in WIDTHS:
        item = captured.get(width) or {"png": None, "axe": missing("brak wyniku")}
        result["axe"][str(width)] = item["axe"]
        if item["png"]:
            name = f"{slug}-{width}.png"
            (out_dir / name).write_bytes(item["png"])
            result["screenshots"][str(width)] = name
            shots[width] = item["png"]
    result["lighthouse"] = lighthouse(base_url, cookie)
    if review and set(shots) == set(WIDTHS):
        outcome = screenshots.review_screenshots(package, shots, artist.pk)
        result["review"] = {
            "status": outcome.status,
            "reason": outcome.reason,
            "viewports": outcome.viewports,
            "call_ids": outcome.call_ids,
            "cost_usd": outcome.cost_usd,
        }
    elif review:
        result["review"]["reason"] = "brak zrzutów ekranu"
    else:
        result["review"]["reason"] = "pominięto (--no-review)"
    return result


def _store(evaluation: PackageEvaluation, result: dict) -> PageMetrics:
    review = result["review"]
    return PageMetrics.objects.create(
        evaluation=evaluation,
        axe=result["axe"],
        lighthouse=result["lighthouse"],
        screenshot_review=review,
        components={
            c.key: {"version": c.version, "content_hash": c.content_hash}
            for c in screenshots.COMPONENTS
        },
        review_call_ids=review.get("call_ids", []),
        cost_usd=Decimal(review.get("cost_usd", "0")),
        measured_at=timezone.now(),
    )


def measure(
    packages: list[dict],
    base_url: str,
    out_dir: Path,
    *,
    run: EvaluationRun | None = None,
    **kwargs,
) -> list[dict]:
    """Measure `packages` in order. With `run`, each package must have an evaluation in it that is
    not yet measured (refused before anything is measured); results are stored in `PageMetrics`."""
    testset.require_enabled()
    evaluations: dict[str, PackageEvaluation] = {}
    if run is not None:
        by_slug = {e.slug: e for e in run.evaluations.select_related("generation")}
        for package in packages:
            row = by_slug.get(package["slug"])
            if row is None:
                raise MeasureRefused(f"{package['slug']}: not evaluated in run {run.pk}")
            if PageMetrics.objects.filter(evaluation=row).exists():
                raise MeasureRefused(
                    f"{package['slug']}: already measured in run {run.pk} (metrics are append-only)"
                )
            evaluations[package["slug"]] = row
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for package in packages:
        row = evaluations.get(package["slug"])
        result = measure_package(package, base_url, out_dir, evaluation=row, **kwargs)
        if row is not None:
            _store(row, result)
        results.append(result)
    return results


# --- verdict and report ------------------------------------------------------------------------


def failures(results: list[dict]) -> list[str]:
    """Why the job fails: no axe or Lighthouse result, or a critical axe violation."""
    out = []
    for result in results:
        slug = result["slug"]
        for width, axe in result["axe"].items():
            if axe["status"] != OK:
                out.append(f"{slug}: axe {width} px: {NO_MEASUREMENT} ({axe['reason']})")
            elif axe["by_impact"]["critical"]:
                rules = ", ".join(v["id"] for v in axe["violations"] if v["impact"] == "critical")
                out.append(f"{slug}: axe {width} px: critical violation ({rules})")
        if result["lighthouse"].get("status") != OK:
            out.append(
                f"{slug}: Lighthouse: {NO_MEASUREMENT} ({result['lighthouse'].get('reason', '')})"
            )
    return out


def _axe_cell(axe: dict) -> str:
    if axe.get("status") != OK:
        return NO_MEASUREMENT
    counts = axe["by_impact"]
    return " / ".join(str(counts[i]) for i in IMPACTS)


def _review_cell(review: dict) -> str:
    if review.get("status") != screenshots.OK:
        return screenshots.MISSING
    parts = [f"{w}: {v['verdict']} ({len(v['problems'])})" for w, v in review["viewports"].items()]
    return ", ".join(parts)


def markdown_table(results: list[dict]) -> str:
    """Short table for the CI job summary. Scores below 85 are marked, not enforced."""
    lines = [
        "| pakiet | axe 360 (kryt./poważne/umiark./drobne) | axe 1440 | Lighthouse | LCP ms "
        "| ocena zrzutów |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        lh = r["lighthouse"]
        if lh.get("status") == OK:
            mark = " ⚠️" if lh["performance"] < LIGHTHOUSE_WARN_BELOW else ""
            score, lcp = f"{lh['performance']}{mark}", str(lh["lcp_ms"])
        else:
            score, lcp = NO_MEASUREMENT, "-"
        lines.append(
            f"| {r['slug']} | {_axe_cell(r['axe'].get('360', {}))} | "
            f"{_axe_cell(r['axe'].get('1440', {}))} | {score} | {lcp} | "
            f"{_review_cell(r['review'])} |"
        )
    return "\n".join(lines) + "\n"


def report(results: list[dict], run: EvaluationRun | None = None) -> dict:
    return {
        "format": REPORT_FORMAT,
        "run": run.pk if run else None,
        "components": {
            c.key: {"version": c.version, "content_hash": c.content_hash}
            for c in screenshots.COMPONENTS
        },
        "failures": failures(results),
        "packages": results,
    }
