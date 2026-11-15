"""Rank PSI investigations against a scenario, and the real ranges a Scenario page can offer.

The scenario arrives as query parameters, so a ranking is a shareable URL. Design:
docs/superpowers/specs/2026-11-14-ranking-engine-design.md.
"""

from collections import Counter
from typing import Annotated, Any, Literal

from fastapi import APIRouter, HTTPException, Query

from app import ranking, runs

router = APIRouter(prefix="/api", tags=["ranking"])

Weight = Annotated[float | None, Query(ge=0, le=10)]

# Values FLARE's charts leave out as suspect (research/analysis/README.md, Visualization.jsx): a
# pressure at or below 0 and a negative airflow. The ranking still scores them (#87, option 2), so
# `min`/`max` stay the ranking's own span, which sets its tolerances and the charts' window (#65);
# `tested` is the range without them, which is what the Scenario page shows as NASA's tested span.
SUSPECT = {"pressure": lambda value: value <= 0, "flow_velocity": lambda value: value < 0}


def _span(values: list[float]) -> dict[str, Any]:
    return {"min": min(values), "max": max(values), "rows": len(values)}


@router.get("/rank")
def rank(
    environment: Literal["spacecraft", "lunar", "mars", "custom"] | None = None,
    gravity_g: Annotated[float | None, Query(ge=0, le=1, description="Only with environment=custom")] = None,
    oxygen: Annotated[float | None, Query(ge=0, le=1, description="Mole fraction")] = None,
    pressure: Annotated[float | None, Query(ge=0, le=10, description="atm")] = None,
    flow_velocity: Annotated[float | None, Query(ge=0, le=1000, description="cm/s")] = None,
    fuel: Annotated[str | None, Query(max_length=100)] = None,
    fuel_phase: Literal["gas", "liquid", "solid"] | None = None,
    concern: Literal["prevention", "detection", "suppression"] | None = None,
    weight_oxygen: Weight = None,
    weight_pressure: Weight = None,
    weight_flow_velocity: Weight = None,
    weight_fuel: Weight = None,
    weight_fuel_phase: Weight = None,
    weight_concern: Weight = None,
) -> dict[str, Any]:
    """Investigations ranked by their closest tests, each with why. Not a safety assessment."""
    if gravity_g is not None and environment != "custom":
        raise HTTPException(status_code=422, detail="gravity_g is only used with environment=custom")
    given = {key: value for key, value in locals().items() if value is not None}
    weights = {key.removeprefix("weight_"): value for key, value in given.items() if key.startswith("weight_")}
    fields = {key: value for key, value in given.items() if not key.startswith("weight_")}
    result = ranking.rank(ranking.Scenario(**fields, weights=weights))
    return {"scenario": given, **result}


def _fuel_name(text: str) -> str:
    """normalize_fuel without amounts, so "75 % Propylene" is offered as "propylene"."""
    return " ".join(word for word in ranking.normalize_fuel(text).split() if not word.isdigit())


@router.get("/rank/options")
def options() -> dict[str, Any]:
    """Ranges, fuels and environments taken from the data, for building scenario inputs."""
    values = {variable: [] for variable in ranking.NUMERIC}
    fuels: Counter = Counter()
    for content in runs.runs().values():
        for table in content["tables"]:
            for row in table["rows"]:
                for variable in ranking.NUMERIC:
                    if (value := ranking.scorable_value(row, variable)) is not None:
                        values[variable].append(value)
                fuel = row.get("standard", {}).get("fuel") or {}
                material = fuel.get("material") or []
                names = material if isinstance(material, list) else [material]
                if not names and fuel.get("text"):
                    names = [fuel["text"]]
                for name in {_fuel_name(n) for n in names} - {""}:
                    fuels[name] += 1
    return {
        "variables": {
            v: {"unit": ranking.UNITS[v], **_span(xs),
                "tested": _span([x for x in xs if not SUSPECT.get(v, lambda _: False)(x)])}
            for v, xs in values.items()
        },
        "fuels": [{"name": name, "rows": count} for name, count in fuels.most_common()],
        "fuel_phases": ["gas", "liquid", "solid"],
        "concerns": ["prevention", "detection", "suppression"],
        "environments": ranking.GRAVITY,
    }
