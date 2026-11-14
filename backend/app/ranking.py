"""Rank PSI investigations against a fire scenario by scoring each of their tests.

Design: docs/superpowers/specs/2026-11-14-ranking-engine-design.md. Every test row is compared
with the scenario on the variables the user set; a variable the row lacks scores 0, so measuring
less never ranks higher. The score says how closely NASA's tests match the scenario. It is not a
safety assessment.
"""

import re
from dataclasses import dataclass, field
from functools import cache

from app import catalogue, runs

NUMERIC = ("oxygen", "pressure", "flow_velocity")
UNITS = {"oxygen": "mole fraction", "pressure": "atm", "flow_velocity": "cm/s"}
VARIABLES = NUMERIC + ("fuel", "fuel_phase", "concern")
DEFAULT_WEIGHTS = {variable: 1.0 for variable in VARIABLES}
WEIGHTS_REASON = ("Equal weights: FLARE claims no variable matters more for fire safety. "
                  "Override per request.")
CLOSE = 0.8  # a test this close or closer counts towards close_tests and as a match
GRAVITY = {"spacecraft": 0.0, "lunar": 0.17, "mars": 0.38}  # in g; custom takes gravity_g

# Formula names in PSI's fuel text, spelled the way a user would type them.
FORMULAS = {
    "c2h4": "ethylene", "ch4": "methane", "c2h6": "ethane", "c3h8": "propane",
    "c3h6": "propylene", "c4h10": "butane", "c7h16": "heptane", "c12h26": "dodecane",
    "ch3oh": "methanol", "c2h5oh": "ethanol",
}


def normalize_fuel(text: str) -> str:
    words = re.sub(r"[^a-z0-9]+", " ", text.lower()).split()
    return " ".join(FORMULAS.get(word, word) for word in words)


def _fuel_words(text: str) -> list[str]:
    return [word for word in normalize_fuel(text).split() if len(word) > 1]


@dataclass(frozen=True)
class Scenario:
    environment: str | None = None
    gravity_g: float | None = None
    oxygen: float | None = None
    pressure: float | None = None
    flow_velocity: float | None = None
    fuel: str | None = None
    fuel_phase: str | None = None
    concern: str | None = None
    weights: dict[str, float] = field(default_factory=dict)

    def weight(self, variable: str) -> float:
        return self.weights.get(variable, DEFAULT_WEIGHTS[variable])

    def set_variables(self) -> list[str]:
        """The variables that take part in the score: given, with a weight above 0."""
        chosen = []
        for variable in VARIABLES:
            value = getattr(self, variable)
            if value is None or self.weight(variable) <= 0:
                continue
            if variable == "fuel" and not _fuel_words(value):
                continue
            chosen.append(variable)
        return chosen

    def gravity(self) -> float | None:
        if self.environment == "custom":
            return self.gravity_g
        return GRAVITY.get(self.environment)


def scorable_value(row: dict, variable: str) -> float | None:
    """A standard field's single number, unless its cell was flagged as looking wrong."""
    standard = row.get("standard", {}).get(variable)
    if not standard:
        return None
    value = standard.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if row.get("cells", {}).get(standard.get("column"), {}).get("flags"):
        return None
    return float(value)


def _all_rows():
    for content in runs.runs().values():
        for table in content["tables"]:
            yield from table["rows"]


@cache
def tolerances() -> dict[str, float]:
    """A quarter of each numeric variable's span across every scorable row: derived from the
    data, not from fire science."""
    result = {}
    for variable in NUMERIC:
        values = [v for row in _all_rows() if (v := scorable_value(row, variable)) is not None]
        result[variable] = (max(values) - min(values)) / 4
    return result


def closeness(scenario_value: float, row_value: float, tolerance: float) -> float:
    return max(0.0, 1 - abs(row_value - scenario_value) / tolerance)


def fuel_matches(scenario_fuel: str, row_fuel: dict) -> bool:
    words = _fuel_words(scenario_fuel)
    material = row_fuel.get("material") or []
    if isinstance(material, str):
        material = [material]
    row_words = set(normalize_fuel(" ".join([*material, row_fuel.get("text") or ""])).split())
    return bool(words) and all(word in row_words for word in words)


def tag_values(tags: dict, key: str) -> list[str] | None:
    """A tag's values, or None when the record does not state it."""
    raw = (tags.get(key) or "").strip()
    if not raw or raw == "not stated":
        return None
    return [value.strip() for value in raw.split(";")]


def _part(scenario: Scenario, variable: str, row: dict, tags: dict) -> float | None:
    if variable in NUMERIC:
        value = scorable_value(row, variable)
        if value is None:
            return None
        return closeness(getattr(scenario, variable), value, tolerances()[variable])
    if variable == "fuel":
        row_fuel = row.get("standard", {}).get("fuel")
        if not row_fuel or not (row_fuel.get("text") or row_fuel.get("material")):
            return None
        return 1.0 if fuel_matches(scenario.fuel, row_fuel) else 0.0
    key = "fuel_phase" if variable == "fuel_phase" else "fire_safety_role"
    values = tag_values(tags, key)
    if values is None:
        return None
    return 1.0 if getattr(scenario, variable) in values else 0.0


def score_row(scenario: Scenario, row: dict, tags: dict) -> tuple[float, dict[str, float | None]]:
    """The row's weighted mean closeness, with an unavailable variable counted as 0."""
    variables = scenario.set_variables()
    parts = {variable: _part(scenario, variable, row, tags) for variable in variables}
    total = sum(scenario.weight(v) for v in variables)
    if not total:
        return 0.0, parts
    return sum(scenario.weight(v) * (parts[v] or 0.0) for v in variables) / total, parts


NOTICE = ("A relevance score shows how closely NASA's tests match this scenario. "
          "It is not a safety assessment.")
EMPTY = "Set at least one condition to rank."
VERSION = "1"


def _summary(record: dict) -> dict:
    return {key: record[key] for key in ("accession", "title", "investigationAcronym", "doi")}


def _has_fuel(row: dict) -> bool:
    fuel = row.get("standard", {}).get("fuel") or {}
    return bool(fuel.get("text") or fuel.get("material"))


def _structural_reason(accession: str) -> str | None:
    """Why an investigation cannot be ranked whatever the scenario, or None."""
    content = runs.runs().get(accession)
    if content is None:
        return "No experimental table: catalogue only"
    if all(table["row_is"] == "published_figure" for table in content["tables"]):
        return "An index of published figures, not tests"
    rows = [row for table in content["tables"] for row in table["rows"]]
    if not any(_has_fuel(r) or any(scorable_value(r, v) is not None for v in NUMERIC) for r in rows):
        return "No test conditions recorded"
    return None


def _gravity_note(g: float | None, tags: dict | None = None) -> str | None:
    if not g:  # microgravity (0) or unknown (custom without gravity_g)
        return None
    if tags is None:
        evidence = "NASA's evidence comes from microgravity and normal-gravity tests"
    else:
        levels = tag_values(tags, "gravity_level") or ["untagged"]
        evidence = f"The evidence comes from {' and '.join(levels)} tests"
    return f"This scenario is at {g:g} g. {evidence}, not partial gravity."


def _comparison(scenario, variable, scored, tags) -> dict:
    entry = {"variable": variable, "scenario": getattr(scenario, variable)}
    if variable in NUMERIC:
        values = [v for _, _, _, row in scored if (v := scorable_value(row, variable)) is not None]
        target = getattr(scenario, variable)
        entry |= {"tested_min": min(values), "tested_max": max(values),
                  "closest": min(values, key=lambda v: abs(v - target)), "unit": UNITS[variable]}
    elif variable == "fuel":
        texts = {row["standard"]["fuel"].get("text") for _, _, _, row in scored if _has_fuel(row)}
        entry["tested"] = sorted(t for t in texts if t)[:10]
    else:
        entry["tested"] = tag_values(tags, "fuel_phase" if variable == "fuel_phase" else "fire_safety_role")
    return entry


def _rank_one(scenario: Scenario, variables: list[str], record: dict, content: dict, g) -> dict:
    tags = record["derived"]["tags"]["values"]
    scored = []
    for table in content["tables"]:
        for row in table["rows"]:
            score, parts = score_row(scenario, row, tags)
            scored.append((score, parts, table, row))
    scored.sort(key=lambda entry: -entry[0])  # stable: equal scores keep PSI's row order
    best_score, best_parts = scored[0][0], scored[0][1]

    matches, differences, unavailable = [], [], []
    for variable in variables:
        if all(parts[variable] is None for _, parts, _, _ in scored):
            unavailable.append(variable)
            continue
        entry = _comparison(scenario, variable, scored, tags)
        (matches if (best_parts[variable] or 0) >= CLOSE else differences).append(entry)

    best_tests = []
    for score, _, table, row in scored[:3]:
        standard = row.get("standard", {})
        values = {v: standard[v] for v in variables if v in standard}
        best_tests.append({"file": table["file"], "line": row["line"], "run_id": row.get("run_id"),
                           "score": round(score * 100), "values": values})
    outcomes = {key for _, _, _, row in scored for key, value in row.get("standard", {}).items()
                if value.get("role") == "outcome"}
    units = sorted({table["row_is"] for table in content["tables"]})
    return {
        **_summary(record),
        "score": round(best_score * 100),
        "close_tests": sum(1 for score, _, _, _ in scored if score >= CLOSE),
        "rows_scored": len(scored),
        "row_unit": "; ".join(units),
        "used_variables": {v: scenario.weight(v) for v in variables},
        "matches": matches,
        "differences": differences,
        "unavailable": unavailable,
        "best_tests": best_tests,
        "measured_outcomes": sorted(outcomes),
        "gravity_note": _gravity_note(g, tags),
    }


def rank(scenario: Scenario) -> dict:
    """Every investigation, ranked against the scenario or listed as not ranked with a reason."""
    variables = scenario.set_variables()
    g = scenario.gravity()
    out = {
        "message": None if variables else EMPTY,
        "gravity_note": _gravity_note(g),
        "method": {"variables": variables, "weights": {v: scenario.weight(v) for v in variables},
                   "weights_reason": WEIGHTS_REASON, "tolerances": tolerances(), "units": UNITS,
                   "close": CLOSE, "version": VERSION},
        "notice": NOTICE,
        "items": [],
        "not_ranked": [],
    }
    for accession, record in catalogue.investigations().items():
        reason = _structural_reason(accession) or (None if variables else EMPTY)
        if reason:
            out["not_ranked"].append({**_summary(record), "reason": reason})
        else:
            out["items"].append(_rank_one(scenario, variables, record, runs.runs()[accession], g))
    out["items"].sort(key=lambda i: (-i["score"], -i["close_tests"],
                                     catalogue._accession_number(i["accession"])))
    return out
