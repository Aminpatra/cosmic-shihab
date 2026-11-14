"""Exploratory analysis of PSI's processed experimental runs (master prompt section 4).

Reads backend/data/runs/ (written by pipeline/process_tables.py) and writes, next to this file:

  column_profile.csv     every PSI column: how each cell was read, how complete it is
  standard_coverage.csv  per table, how many rows give each comparable condition or outcome
  condition_ranges.csv   the tested range of each condition, suspect values left out
  suspect_values.csv     values that look wrong: the pipeline's flags and the checks below
  flex_relationships.csv rank correlations between FLEX conditions and outcomes, per fuel
  flex_test_end.csv      how FLEX tests ended, per fuel and band of initial oxygen
  summary.md             the tables above in short, regenerated on every run
  figures/*.png          the three charts described in README.md

Nothing here changes a value. A suspect value is listed and left out of ranges, charts and
correlations; it stays in backend/data/runs/ exactly as PSI wrote it.

Run from the repository root:  python3 research/analysis/explore_runs.py
Needs matplotlib (research/analysis/requirements.txt); the CSV and summary need only the
standard library.
"""

from __future__ import annotations

import csv
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUNS = ROOT / "backend" / "data" / "runs"
FIGURES = HERE / "figures"

FIELDS = ["fuel", "oxygen", "pressure", "flow_velocity", "burn_time", "test_end"]
NUMERIC = ["oxygen", "pressure", "flow_velocity", "burn_time"]
UNITS = {"oxygen": "mole fraction", "pressure": "atm", "flow_velocity": "cm/s", "burn_time": "s"}
ROLE = {"fuel": "condition", "oxygen": "condition", "pressure": "condition", "flow_velocity": "condition",
        "burn_time": "outcome", "test_end": "outcome"}
MISSING = ["empty", "text", "dash", "spreadsheet_error"]

# FLEX columns used for the relationship table. Conditions are set before a test; outcomes are
# measured during or after it.
FLEX_CONDITIONS = {
    "oxygen": "O initial ambient composition; mole fraction",
    "helium": "He initial ambient composition; mole fraction",
    "pressure": "Ambient pressure; mmHg",
    "initial_diameter": "Droplet initial diameter; mm",
}
FLEX_OUTCOMES = {
    "burn_time": "Burn time; s",
    "burning_rate": "Burning rate; mm",
    "extinction_diameter": "Visible flame extinction diameter; mm",
}


def load() -> list[dict]:
    """Every table, with its accession, in accession-number then file order."""
    tables = []
    paths = sorted(RUNS.glob("*.json"), key=lambda p: int(p.stem.removeprefix("PSI-")))
    for path in paths:
        entry = json.loads(path.read_text(encoding="utf-8"))
        for table in entry["tables"]:
            tables.append(table | {"accession": entry["accession"]})
    if not tables:
        raise FileNotFoundError(f"no runs files in {RUNS}; run pipeline/process_tables.py first")
    return tables


def short(table: dict) -> str:
    """'PSI-25 BASS-II': the accession and the part of the file name after 'Experimental table_'."""
    name = table["file"].split("Experimental table_", 1)[-1].removesuffix(".csv")
    return f"{table['accession']} {name}"


# ---------------------------------------------------------------------------------------------
# Suspect values


def suspects(tables: list[dict]) -> list[dict]:
    """Everything that looks wrong, one line each. The pipeline's own flags come first."""
    out = []

    def add(table, row, column, rule, raw, detail=""):
        out.append({"accession": table["accession"], "table": table["file"], "line": row["line"] if row else "",
                    "run_id": (row or {}).get("run_id") or "", "column": column, "rule": rule, "raw": raw,
                    "detail": detail})

    for t in tables:
        for row in t["rows"]:
            for column, cell in row["cells"].items():
                for flag in cell.get("flags", []):
                    add(t, row, column, flag, cell["raw"], "flagged by pipeline/process_tables.py")
            for field, std in row["standard"].items():
                cell = row["cells"].get(std["column"], {})
                value = std.get("value")
                if cell.get("flags") and any(k in std for k in ("value", "values", "range")):
                    add(t, row, std["column"], "standard_value_from_flagged_cell", cell["raw"],
                        f"standard.{field} = {std.get('value', std.get('values', std.get('range')))} "
                        f"{std.get('unit', '')}, converted from a flagged cell")
                elif field == "pressure" and isinstance(value, (int, float)) and value <= 0:
                    add(t, row, std["column"], "zero_or_negative_pressure", cell.get("raw", ""),
                        f"a test that burned cannot run at {value} atm; probably a missing reading entered as 0")
                elif field == "flow_velocity" and isinstance(value, (int, float)) and value < 0:
                    add(t, row, std["column"], "negative_flow_velocity", cell.get("raw", ""),
                        "an air rate below zero; possibly a sensor offset with the fan off")
                elif field == "oxygen" and isinstance(value, (int, float)) and not 0 <= value <= 1:
                    add(t, row, std["column"], "oxygen_fraction_outside_0_1", cell.get("raw", ""), str(value))
            if "same_as_line" in row:
                add(t, row, "(whole row)", "exact_duplicate_row", "", f"same as line {row['same_as_line']}")
        # Category spellings that differ only in case or spaces ("75 % Propylene", "75% Propylene").
        for column in (c["name"] for c in t["columns"]):
            raws = Counter(r["cells"][column]["raw"].strip() for r in t["rows"]
                           if r["cells"][column]["kind"] == "text")
            if not 2 <= len(raws) <= 40:
                continue
            groups = defaultdict(dict)
            for raw, n in raws.items():
                groups[re.sub(r"\s+", "", raw.lower())][raw] = n
            for variants in groups.values():
                if len(variants) > 1:
                    add(t, None, column, "spelling_variant", " | ".join(sorted(variants)),
                        "; ".join(f"{v!r}: {n} rows" for v, n in sorted(variants.items())))
    return out


def excluded(table: dict, row: dict, field: str, suspect_keys: set) -> bool:
    """True when a standard value must stay out of ranges, charts and correlations."""
    std = row["standard"].get(field, {})
    return (table["file"], row["line"], std.get("column")) in suspect_keys


def usable(table: dict, row: dict, field: str, suspect_keys: set) -> float | None:
    """A standard field's single number, or None when it has none or is suspect."""
    value = row["standard"].get(field, {}).get("value")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or excluded(table, row, field, suspect_keys):
        return None
    return value


# ---------------------------------------------------------------------------------------------
# Tables


def column_profile(tables: list[dict]) -> list[dict]:
    out = []
    for t in tables:
        mapped = {column: field for field, column in t["standard_columns"].items()}
        for col in t["columns"]:
            cells = [r["cells"][col["name"]] for r in t["rows"]]
            kinds = Counter(c["kind"] for c in cells)
            missing = Counter(c["missing"] for c in cells if c["kind"] == "missing")
            numbers = [c["value"] for c in cells if c["kind"] == "number"]
            n = len(cells)
            field = mapped.get(col["name"], "")
            out.append({
                "accession": t["accession"], "table": t["file"], "row_is": t["row_is"], "column": col["name"],
                "unit": col["unit"] or "", "unit_inferred": "yes" if col.get("unit_inferred") else "",
                "standard_field": field, "role": ROLE.get(field, ""), "rows": n,
                "number": kinds["number"], "list": kinds["list"], "range": kinds["range"], "text": kinds["text"],
                **{f"missing_{m}": missing[m] for m in MISSING},
                "filled_pct": round(100 * (n - kinds["missing"]) / n, 1) if n else "",
                "distinct": len({c["raw"].strip() for c in cells}),
                "min": min(numbers) if numbers else "", "max": max(numbers) if numbers else "",
                "flagged": sum(1 for c in cells if c.get("flags")),
            })
    return out


def standard_coverage(tables: list[dict], suspect_keys: set) -> list[dict]:
    out = []
    for t in tables:
        for field in FIELDS:
            base = {"accession": t["accession"], "table": t["file"], "row_is": t["row_is"], "rows": t["row_count"],
                    "field": field, "role": ROLE[field]}
            if field not in t["standard_columns"]:
                out.append(base | {"recorded": "no", "single_value": 0, "list_or_range": 0, "text_only": 0,
                                   "missing": 0, "suspect": 0, "usable_pct": ""})
                continue
            c = Counter()
            for row in t["rows"]:
                std = row["standard"][field]
                if field in ("fuel", "test_end"):
                    c["single_value" if "text" in std else "missing"] += 1
                elif excluded(t, row, field, suspect_keys) and "value" in std:
                    c["suspect"] += 1
                elif "value" in std:
                    c["single_value"] += 1
                elif "values" in std or "range" in std:
                    c["list_or_range"] += 1
                elif "text" in std:
                    c["text_only"] += 1
                else:
                    c["missing"] += 1
            out.append(base | {"recorded": "yes", **{k: c[k] for k in
                               ("single_value", "list_or_range", "text_only", "missing", "suspect")},
                               "usable_pct": round(100 * c["single_value"] / t["row_count"], 1)})
    return out


def condition_ranges(tables: list[dict], suspect_keys: set) -> list[dict]:
    out = []
    for t in tables:
        for field in NUMERIC:
            if field not in t["standard_columns"]:
                continue
            values = [v for r in t["rows"] if (v := usable(t, r, field, suspect_keys)) is not None]
            left_out = sum(1 for r in t["rows"] if "value" in r["standard"][field]) - len(values)
            if not values:
                continue
            out.append({"accession": t["accession"], "table": t["file"], "row_is": t["row_is"], "field": field,
                        "role": ROLE[field], "unit": UNITS[field], "n": len(values), "left_out_suspect": left_out,
                        "min": _g(min(values)), "median": _g(statistics.median(values)), "max": _g(max(values)),
                        "distinct": len(set(values))})
    return out


def _g(x: float) -> float:
    return float(f"{x:.4g}")


def flex_relationships(tables: list[dict], suspect_keys: set) -> list[dict]:
    """Spearman rank correlation, per fuel, between each FLEX condition and outcome.

    Only rows where both cells are plain numbers and neither is suspect. A correlation describes
    these tests; it says nothing about cause."""
    flex = next(t for t in tables if t["accession"] == "PSI-69")
    bad = {(line, col) for (file, line, col) in suspect_keys if file == flex["file"]}
    out = []
    by_fuel = defaultdict(list)
    for row in flex["rows"]:
        by_fuel[row["standard"]["fuel"]["text"]].append(row)
    for fuel, rows in sorted(by_fuel.items()):
        for cname, ccol in FLEX_CONDITIONS.items():
            for oname, ocol in FLEX_OUTCOMES.items():
                pairs = [(r["cells"][ccol]["value"], r["cells"][ocol]["value"]) for r in rows
                         if plain(r["cells"][ccol]) and plain(r["cells"][ocol])
                         and (r["line"], ccol) not in bad and (r["line"], ocol) not in bad]
                xs, ys = zip(*pairs) if pairs else ((), ())
                rho = (statistics.correlation(xs, ys, method="ranked")
                       if len(pairs) >= 10 and len(set(xs)) > 1 and len(set(ys)) > 1 else None)
                out.append({"fuel": fuel, "condition": cname, "condition_column": ccol, "outcome": oname,
                            "outcome_column": ocol, "n": len(pairs), "distinct_condition_values": len(set(xs)),
                            "spearman_rho": round(rho, 2) if rho is not None else ""})
    return out


def plain(cell: dict) -> bool:
    """A cell holding one number as written: no "~", "<" or ">"."""
    return cell["kind"] == "number" and not cell.get("approx") and not cell.get("bound")


def flex_test_end(tables: list[dict], suspect_keys: set) -> list[dict]:
    """How FLEX tests ended, per fuel and band of initial oxygen. Burn time means something
    different for each ending, so this is read before any burn-time comparison."""
    flex = next(t for t in tables if t["accession"] == "PSI-69")
    counts = Counter()
    for row in flex["rows"]:
        oxygen = usable(flex, row, "oxygen", suspect_keys)
        end = row["standard"]["test_end"].get("text")
        if oxygen is None or end is None:
            continue
        band = "below 0.18" if oxygen < 0.18 else "0.18 to 0.22" if oxygen <= 0.22 else "above 0.22"
        counts[(row["standard"]["fuel"]["text"], band, end)] += 1
    bands = ["below 0.18", "0.18 to 0.22", "above 0.22"]
    ends = sorted({k[2] for k in counts})
    return [{"fuel": fuel, "oxygen_band": band, "tests": sum(counts[(fuel, band, e)] for e in ends),
             **{e.lower(): counts[(fuel, band, e)] for e in ends}}
            for fuel in sorted({k[0] for k in counts}) for band in bands]


def write_csv(name: str, rows: list[dict]) -> None:
    with open(HERE / name, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------------------------
# Summary


def summary(tables, coverage, ranges, suspect_rows, relations, ends) -> str:
    tests = [t for t in tables if t["row_is"] == "test"]
    lines = [
        "# Summary of the PSI runs",
        "",
        "Generated by `explore_runs.py` from `backend/data/runs/`; do not edit by hand. What the",
        "numbers mean, and what they do not, is in `README.md`.",
        "",
        f"- {len(tables)} tables, {sum(t['row_count'] for t in tables)} rows, "
        f"{len({t['accession'] for t in tables})} investigations.",
        f"- {len(tests)} tables have one row per test: {sum(t['row_count'] for t in tests)} tests in "
        f"{len({t['accession'] for t in tests})} investigations. The others are test-day logs, sessions, a "
        "fuel summary and an index of published figures.",
        "",
        "## How many test rows give each field",
        "",
        "Rows with one usable value (suspect values left out). `-` means the table has no such column.",
        "",
        "| Table | Tests | " + " | ".join(FIELDS) + " |",
        "|---|---:|" + "---:|" * len(FIELDS),
    ]
    cov = {(c["table"], c["field"]): c for c in coverage}
    for t in tests:
        cells = []
        for field in FIELDS:
            c = cov[(t["file"], field)]
            cells.append("-" if c["recorded"] == "no" else str(c["single_value"]))
        lines.append(f"| {short(t)} | {t['row_count']} | " + " | ".join(cells) + " |")
    recorded = Counter(c["field"] for c in coverage if c["recorded"] == "yes" and c["row_is"] == "test")
    lines += ["", "Test tables recording each field: " + ", ".join(f"{f} {recorded[f]} of {len(tests)}" for f in FIELDS)
              + ".", "", "## Tested ranges", "", "| Table | Field | n | Min | Median | Max | Left out |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for r in ranges:
        t = next(t for t in tables if t["file"] == r["table"])
        lines.append(f"| {short(t)} | {r['field']} ({r['unit']}) | {r['n']} | {r['min']} | {r['median']} | "
                     f"{r['max']} | {r['left_out_suspect']} |")
    by_rule = Counter(s["rule"] for s in suspect_rows)
    lines += ["", "## How FLEX tests ended, by initial oxygen", "",
              "Burn time means something different for each ending, so it is not one outcome.", "",
              "| Fuel | Oxygen (mole fraction) | Tests | " + " | ".join(k.capitalize() for k in ends[0]
                                                            if k not in ("fuel", "oxygen_band", "tests")) + " |",
              "|---|---|---:|" + "---:|" * (len(ends[0]) - 3)]
    lines += [f"| {e['fuel']} | {e['oxygen_band']} | {e['tests']} | " + " | ".join(
        str(v) for k, v in e.items() if k not in ("fuel", "oxygen_band", "tests")) + " |" for e in ends]
    lines += ["", "## Suspect values", "", "| Rule | Count |", "|---|---:|"]
    lines += [f"| `{rule}` | {n} |" for rule, n in sorted(by_rule.items())]
    lines += ["", "Every one is listed in `suspect_values.csv` with its file, line and original text.", "",
              "## FLEX: conditions and outcomes, per fuel", "",
              "Spearman rank correlation over the FLEX tests where both values are plain numbers (no `~`, `<` or `>`). "
              "A correlation describes these tests; it does not show cause.", "",
              "| Fuel | Condition | Outcome | n | rho |", "|---|---|---|---:|---:|"]
    for r in relations:
        if r["spearman_rho"] != "":
            lines.append(f"| {r['fuel']} | {r['condition']} | {r['outcome']} | {r['n']} | {r['spearman_rho']} |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------------------------
# Figures. Dark surface and brand colours from frontend/src/styles/tokens.css; palette checked
# with the dataviz validator (Blue Yonder and orange pass all-pairs on Deep Blue).

SURFACE, TEXT, TEXT_2, GRID, HATCH = "#07173f", "#e6ecf8", "#b9c6e4", "#28467f", "#5c77ae"
SERIES = ["#2e96f5", "#d95926"]  # Blue Yonder, then orange


def figures(tables, coverage, suspect_keys) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Rectangle

    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "text.color": TEXT, "axes.labelcolor": TEXT_2, "xtick.color": TEXT_2, "ytick.color": TEXT_2,
        "axes.edgecolor": GRID, "grid.color": GRID, "grid.linewidth": 0.6, "font.family": "DejaVu Sans",
        "font.size": 10, "axes.titlesize": 11, "axes.titlelocation": "left", "hatch.color": HATCH,
        "hatch.linewidth": 0.8, "svg.hashsalt": "flare",
    })
    FIGURES.mkdir(exist_ok=True)
    meta = {"Software": None}
    tests = [t for t in tables if t["row_is"] == "test"]

    # 1. Coverage: share of test rows giving each field.
    cov = {(c["table"], c["field"]): c for c in coverage}
    fig, ax = plt.subplots(figsize=(9.5, 6.4))
    cmap = LinearSegmentedColormap.from_list("blue", ["#0e2760", "#2e96f5", "#d6ebfd"])
    for i, t in enumerate(tests):
        for j, field in enumerate(FIELDS):
            c = cov[(t["file"], field)]
            if c["recorded"] == "no":
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor=SURFACE, edgecolor=HATCH, hatch="///", lw=0))
                continue
            share = c["single_value"] / t["row_count"]
            ax.add_patch(Rectangle((j, i), 1, 1, facecolor=cmap(share), edgecolor=SURFACE, lw=2))
            ax.text(j + 0.5, i + 0.5, f"{round(100 * share)}%", ha="center", va="center", fontsize=9,
                    color=SURFACE if share > 0.55 else TEXT)
    ax.set_xlim(0, len(FIELDS))
    ax.set_ylim(len(tests), 0)
    ax.set_xticks([j + 0.5 for j in range(len(FIELDS))],
                  [f"{f.replace('_', ' ')}\n({ROLE[f]})" for f in FIELDS])
    ax.set_yticks([i + 0.5 for i in range(len(tests))], [f"{short(t)}  ({t['row_count']})" for t in tests])
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    fig.suptitle("Which comparable fields each test table gives", x=0.02, ha="left", fontsize=13, color=TEXT)
    fig.text(0.02, 0.015, "Share of test rows with one usable value (suspect values left out). Hatched: the "
             "table has no such column.\nSource: NASA PSI experimental tables, processed by FLARE "
             "(backend/data/runs/).", fontsize=8.5, color=TEXT_2)
    fig.subplots_adjust(left=0.36, right=0.98, top=0.86, bottom=0.1)
    fig.savefig(FIGURES / "coverage.png", dpi=200, metadata=meta)
    plt.close(fig)

    # 2. Condition space: oxygen by pressure, one panel per table that records both.
    panels = [t for t in tests if {"oxygen", "pressure"} <= set(t["standard_columns"])]
    points = {t["file"]: [(o, p) for r in t["rows"]
                          if (o := usable(t, r, "oxygen", suspect_keys)) is not None
                          and (p := usable(t, r, "pressure", suspect_keys)) is not None] for t in panels}
    everything = [pt for pts in points.values() for pt in pts]
    cols = 3
    fig, axes = plt.subplots(-(-len(panels) // cols), cols, figsize=(11, 7), sharex=True, sharey=True)
    for ax, t in zip(axes.flat, panels):
        ax.scatter(*zip(*everything), s=16, color=GRID, lw=0, zorder=1)
        ax.scatter(*zip(*points[t["file"]]), s=30, color=SERIES[0], edgecolor=SURFACE, lw=0.8, zorder=2)
        ax.set_title(f"{short(t)}\n{len(points[t['file']])} of {t['row_count']} tests", color=TEXT, fontsize=10)
        ax.grid(True, zorder=0)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    for ax in axes.flat[len(panels):]:
        ax.set_visible(False)
    for ax in axes[-1]:
        ax.set_xlabel("Oxygen (mole fraction)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Pressure (atm)")
    fig.suptitle("Where the tests sit in oxygen and pressure", x=0.02, ha="left", fontsize=13, color=TEXT)
    fig.text(0.02, 0.012, "Each panel: one table's tests (blue) over every table's tests (grey). Empty areas "
             "were not tested in these tables. Suspect values left out.\nIn the two inverse-flame tables the "
             "oxygen is the burner's stream, not the room's. Source: NASA PSI, processed by FLARE.",
             fontsize=8.5, color=TEXT_2)
    fig.subplots_adjust(left=0.07, right=0.98, top=0.86, bottom=0.14, hspace=0.45, wspace=0.12)
    fig.savefig(FIGURES / "condition_space.png", dpi=200, metadata=meta)
    plt.close(fig)

    # 3. FLEX: burning rate by oxygen, one panel per fuel, coloured by the inert gas.
    flex = next(t for t in tables if t["accession"] == "PSI-69")
    bad = {(line, col) for (file, line, col) in suspect_keys if file == flex["file"]}
    he_col, br_col, o_col = FLEX_CONDITIONS["helium"], FLEX_OUTCOMES["burning_rate"], FLEX_CONDITIONS["oxygen"]
    fuels = sorted({r["standard"]["fuel"]["text"] for r in flex["rows"]})
    fig, axes = plt.subplots(1, len(fuels), figsize=(10.5, 4.6), sharey=True)
    for ax, fuel in zip(axes, fuels):
        rows = [r for r in flex["rows"] if r["standard"]["fuel"]["text"] == fuel
                and plain(r["cells"][br_col]) and plain(r["cells"][o_col])
                and (r["line"], br_col) not in bad and (r["line"], o_col) not in bad]
        for k, (label, with_he) in enumerate([("no helium", False), ("with helium", True)]):
            sel = [r for r in rows if (r["cells"][he_col].get("value", 0) > 0) == with_he]
            if sel:
                ax.scatter([r["cells"][o_col]["value"] for r in sel], [r["cells"][br_col]["value"] for r in sel],
                           s=30, color=SERIES[k], edgecolor=SURFACE, lw=0.8, label=f"{label} ({len(sel)})",
                           zorder=2)
        ax.set_title(f"{fuel}: {len(rows)} tests", color=TEXT)
        ax.set_xlabel("Initial oxygen (mole fraction)")
        ax.grid(True, zorder=0)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        legend = ax.legend(frameon=False, loc="upper left", fontsize=9)
        for text in legend.get_texts():
            text.set_color(TEXT_2)
    axes[0].set_ylabel("Burning rate (PSI's column; unit given as mm)")
    fig.suptitle("FLEX droplet burning rate by oxygen", x=0.02, ha="left", fontsize=13, color=TEXT)
    fig.text(0.02, 0.012, "One dot per FLEX test with both values. Pressure, droplet size and the inert gas "
             "also vary, so this shows a pattern in these tests, not a cause.\nSource: NASA PSI-69 "
             "experimental table, processed by FLARE.", fontsize=8.5, color=TEXT_2)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.82, bottom=0.22, wspace=0.08)
    fig.savefig(FIGURES / "flex_burning_rate.png", dpi=200, metadata=meta)
    plt.close(fig)


def main() -> int:
    tables = load()
    suspect_rows = suspects(tables)
    suspect_keys = {(s["table"], s["line"], s["column"]) for s in suspect_rows if s["line"] != ""}
    coverage = standard_coverage(tables, suspect_keys)
    ranges = condition_ranges(tables, suspect_keys)
    relations = flex_relationships(tables, suspect_keys)
    ends = flex_test_end(tables, suspect_keys)
    write_csv("column_profile.csv", column_profile(tables))
    write_csv("standard_coverage.csv", coverage)
    write_csv("condition_ranges.csv", ranges)
    write_csv("suspect_values.csv", suspect_rows)
    write_csv("flex_relationships.csv", relations)
    write_csv("flex_test_end.csv", ends)
    (HERE / "summary.md").write_text(summary(tables, coverage, ranges, suspect_rows, relations, ends),
                                     encoding="utf-8", newline="\n")
    if "--no-figures" not in sys.argv:
        figures(tables, coverage, suspect_keys)
    print(f"{len(tables)} tables, {len(suspect_rows)} suspect values; wrote {HERE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
