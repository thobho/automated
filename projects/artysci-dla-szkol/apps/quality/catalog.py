"""Error catalog of the profile generator (US-11.7, D13, D14).

Every error type found in generated profiles gets a stable code, a way it is prevented
(`validator_rule`: a `RULE_*` constant of `apps/profiles/validator.py`, or `instruction_example`:
a marked anchor `<!-- katalog:<anchor> -->` in the generator instructions) and at least one
regression case:

- `validator` case: a synthetic package plus a profile JSON fixture in `error_cases/<code>/` that
  contains the error. The validator must flag it with the entry's rule, while the package's
  scripted good profile is not flagged with that rule.
- `expectation` case: a synthetic package plus one of its expectations (D118), which
  `evaluate_testset` checks on every run.

`check()` returns one `EntryResult` per entry; `manage.py error_catalog_check` and a pytest test
run it. The catalog is the registered component `catalog:error_catalog` (not part of the generator
`COMPONENTS`): a change to the catalog, its schema or a fixture needs a version bump.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from django.conf import settings
from jsonschema import Draft202012Validator

from apps.profiles import inputs, validation, validator
from apps.quality import scripted, testset
from apps.quality.registry import Component, registry

CATALOG_VERSION = "0.2"
HERE = Path(__file__).resolve().parent
CATALOG_FILE = HERE / "error_catalog.json"
SCHEMA_FILE = HERE / "error_catalog.schema.json"
CASES_DIR = HERE / "error_cases"
INSTRUCTIONS_FILE = "apps/profiles/prompts/profile_instructions.md"
ANCHOR_FORMAT = "<!-- katalog:{anchor} -->"

COMPONENT = registry.register(
    Component(
        "catalog",
        "error_catalog",
        CATALOG_VERSION,
        files=(
            "apps/quality/error_catalog.json",
            "apps/quality/error_catalog.schema.json",
            *(
                str(path.relative_to(HERE.parent.parent))
                for path in sorted(CASES_DIR.glob("*/*.json"))
            ),
        ),
    )
)


class CatalogError(Exception):
    """The catalog file cannot be read or breaks its schema. `problems` has one line each."""

    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


@dataclass
class EntryResult:
    code: str
    handling: str
    cases: list[str] = field(default_factory=list)  # one line per case that passed
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def line(self) -> str:
        status = "OK" if self.ok else "FAIL"
        detail = "; ".join([*self.cases, *self.errors])
        return f"{self.code} [{self.handling}] {status}: {detail}"


def _json_path(parts) -> str:
    return "$" + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in parts)


def load(path: Path | None = None, schema_path: Path | None = None) -> dict:
    """The catalog, checked against its schema. Raises `CatalogError` naming the JSON path."""
    path = path or CATALOG_FILE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise CatalogError([f"{path.name}: file not found"]) from None
    except (OSError, ValueError) as exc:
        raise CatalogError([f"{path.name}: not valid JSON ({exc})"]) from None
    schema = json.loads((schema_path or SCHEMA_FILE).read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(data), key=lambda e: list(map(str, e.path))
    )
    if errors:
        raise CatalogError([f"{_json_path(e.absolute_path)}: {e.message[:200]}" for e in errors])
    codes = [entry["code"] for entry in data["errors"]]
    duplicated = sorted({c for c in codes if codes.count(c) > 1})
    if duplicated:
        raise CatalogError([f"$.errors: duplicate code {code!r}" for code in duplicated])
    return data


def codes_by_rule() -> dict[str, str]:
    """Validator rule name (the finding's `rule` text) -> catalog code, for the evaluation
    report. The first entry of a rule wins. An unreadable catalog gives an empty mapping."""
    try:
        data = load()
    except CatalogError:
        return {}
    mapping: dict[str, str] = {}
    for entry in data["errors"]:
        handling = entry["handling"]
        if handling["kind"] == "validator_rule":
            rule = getattr(validator, handling["rule"], None)
            if isinstance(rule, str):
                mapping.setdefault(rule, entry["code"])
    return mapping


def _describe(handling: dict) -> str:
    if handling["kind"] == "validator_rule":
        extra = f" + instruction_example {handling['anchor']}" if "anchor" in handling else ""
        return f"validator_rule {handling['rule']}{extra}"
    return f"instruction_example {handling['anchor']}"


def _check_handling(handling: dict, instructions: Path) -> str | None:
    """The reason the prevention does not work, or None."""
    if handling["kind"] == "validator_rule":
        if handling["rule"] not in validator_rule_names():
            return f"rule {handling['rule']} is not defined in the validator"
        if "anchor" not in handling:
            return None
    marker = ANCHOR_FORMAT.format(anchor=handling["anchor"])
    try:
        text = instructions.read_text(encoding="utf-8")
    except OSError:
        return f"instructions file {instructions.name} cannot be read"
    if marker not in text:
        return f"anchor {marker} is missing in {instructions.name}"
    return None


def validator_rule_names() -> set[str]:
    return {name for name in dir(validator) if name.startswith("RULE_")}


def _package(slug: str, root: Path | None) -> tuple[dict | None, str | None]:
    try:
        package = testset.get_package(slug, root)
    except Exception:  # noqa: BLE001  (unknown or unreadable package: the message names it)
        return None, f"package {slug} does not exist"
    if package.get("origin") != "synthetic":
        return None, f"package {slug} is not synthetic (D12, D57)"
    return package, None


def _check_validator_case(entry, case, rule_value, cases_dir, root) -> str | None:
    label = f"{case['package']}/{case['fixture']}"
    package, problem = _package(case["package"], root)
    if problem:
        return f"case {label}: {problem}"
    fixture_path = cases_dir / case["fixture"]
    try:
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return f"case {label}: fixture is missing or not valid JSON"
    schema_problems = validation.schema_errors(fixture)
    if schema_problems:
        return f"case {label}: fixture breaks the profile schema ({schema_problems[0]})"
    artist = testset.load_package(case["package"], root=root)
    data = inputs.build_input(artist)
    sources = inputs.collect_sources(artist, data)
    report = validator.validate_profile(fixture, sources)
    flagged = {f.rule for f in (*report.hard, *report.soft)}
    if rule_value not in flagged:
        rule = entry["handling"]["rule"]
        return f"case {label}: the validator does not flag the fixture with {rule}"
    good = validator.validate_profile(scripted.scripted_profile(data), sources)
    if rule_value in {f.rule for f in (*good.hard, *good.soft)}:
        return (
            f"case {label}: the scripted good profile is flagged with {entry['handling']['rule']}"
        )
    return None


def _check_expectation_case(case, root) -> str | None:
    label = f"{case['package']}/{case['expectation'].get('kind')}"
    package, problem = _package(case["package"], root)
    if problem:
        return f"case {label}: {problem}"
    if case["expectation"] not in package.get("expectations", []):
        return f"case {label}: the package has no such expectation"
    return None


def check(
    path: Path | None = None,
    *,
    schema_path: Path | None = None,
    cases_dir: Path | None = None,
    instructions: Path | None = None,
    packages_root: Path | None = None,
) -> list[EntryResult]:
    """Check every entry. Raises `CatalogError` when the file itself is broken. Validator cases
    load the synthetic package (database, needs `QUALITY_LAB_ENABLED`)."""
    data = load(path, schema_path)
    cases_dir = cases_dir or CASES_DIR
    instructions = instructions or Path(settings.BASE_DIR) / INSTRUCTIONS_FILE
    results = []
    for entry in data["errors"]:
        result = EntryResult(entry["code"], _describe(entry["handling"]))
        problem = _check_handling(entry["handling"], instructions)
        if problem:
            result.errors.append(problem)
        if not entry["cases"]:
            result.errors.append("no regression case")
        rule_value = None
        if entry["handling"]["kind"] == "validator_rule":
            rule_value = getattr(validator, entry["handling"]["rule"], None)
        for case in entry["cases"]:
            if case["kind"] == "validator":
                if not isinstance(rule_value, str):
                    result.errors.append(
                        f"case {case['package']}/{case['fixture']}: needs a validator_rule"
                    )
                    continue
                problem = _check_validator_case(entry, case, rule_value, cases_dir, packages_root)
                label = f"{case['package']}/{case['fixture']}"
            else:
                problem = _check_expectation_case(case, packages_root)
                label = f"{case['package']}/{case['expectation']['kind']}"
            if problem:
                result.errors.append(problem)
            else:
                result.cases.append(f"case {label} ok")
        results.append(result)
    return results
