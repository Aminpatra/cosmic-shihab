"""Turn PSI's experimental tables in datasets/ into backend/data/runs/<ACCESSION>.json.

Every cell keeps PSI's original text (`raw`). What FLARE reads out of it sits beside it and never
replaces it: a number, a list, a range, or the reason it is missing. Values that look impossible
are kept and flagged, not corrected. A handful of conditions that mean the same thing across
investigations (oxygen, pressure, flow, fuel, burn time, how a test ended) are also copied into
`standard`, in one unit, with `calculated: true` whenever FLARE converted them.

Standard library only. Run from the repository root:  python3 pipeline/process_tables.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASETS = ROOT / "datasets"
OUT = ROOT / "backend" / "data" / "runs"

NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
CELL_UNITS = ["cm/s", "mm/s", "micron", "atm", "bar", "ppm", "cm", "mm", "W", "s", "K", "%"]
UNIT_RE = "|".join(re.escape(u) for u in CELL_UNITS)
RE_NUMBER = re.compile(rf"^(?P<approx>~\s*)?(?P<bound>[<>]\s*)?(?P<n>{NUM})\s*(?P<unit>{UNIT_RE})?$")
RE_RANGE = re.compile(
    rf"^(?P<approx>~\s*)?(?P<a>{NUM})\s*(?P<ua>{UNIT_RE})?\s*(?:-|–|to)\s*(?P<b>{NUM})\s*(?P<ub>{UNIT_RE})?$"
)
MISSING_TEXT = {"none", "n/a", "na"}
DASHES = {"-", "–", "—"}
RE_SHEET_ERROR = re.compile(r"^#(?:VALUE!|DIV/0!|N/A|REF!|NAME\?|NUM!|NULL!)$")

# Header units FLARE recognises, as written in PSI's headers, mapped to one spelling.
HEADER_UNITS = {
    "cm/s": "cm/s", "mm/s": "mm/s", "sec": "s", "s": "s", "minutes": "min", "mm": "mm", "cm": "cm",
    "mg/s": "mg/s", "mg/min": "mg/min", "sccm": "sccm", "atm": "atm", "bar": "bar", "mmhg": "mmHg",
    "k": "K", "c": "C", "w": "W", "ppm": "ppm", "percent": "%", "% by vol": "% by vol",
    "mole fraction": "mole fraction",
}

# Formulas that cannot be a stable fuel or diluent. In PSI's ACME tables they come from a
# spreadsheet filling a column down and counting up ("40% CH4", "40% CH5", ...).
RE_IMPOSSIBLE_FORMULA = re.compile(r"\b(?:CH[5-9]|N[3-9]|C2H[579])\b")

MATERIALS = ["PMMA", "SIBAL", "Nomex", "Kapton", "Teflon", "Silicone", "Pyrell", "Lampwick",
             "Cotton-Fiberglass", "Japan Wax", "Delrin", "Ultem", "Dibutyl Phthalate"]
SHAPES = ["spherical section", "sphere", "cylinder", "film", "rod", "slab", "fabric", "candle"]
RE_SIZE = re.compile(r'(?P<n>\d+/\d+|\d*\.?\d+)\s*(?P<u>micron|mm|cm|"|in\b)(?:\s+(?P<label>thick|wide|long|diameter))?',
                     re.I)

def _x(columns: list[str]) -> dict:
    """XO2 is the usual symbol for an oxygen mole fraction; these headers state no unit."""
    return {"column_units": {c: "mole fraction" for c in columns}, "units_inferred": columns}


# How each table is read. `row_is` says what one row stands for, so nobody counts a test day as
# a test. `standard` maps a FLARE field to the PSI column it comes from.
TABLES = {
    "PSI-100_Experimental table_SAFFIRE-3.csv": dict(row_is="test", id="Sample Number ", standard={
        "fuel": "Material", "flow_velocity": "Air Flow "}),
    "PSI-101_Experimental table_SAME-R.csv": dict(row_is="test", id="SAME Test #", standard={
        "fuel": "Sample Type", "flow_velocity": "Inlet velocity (cm/s)"}),
    "PSI-102_Experimental table_SAME.csv": dict(row_is="test", id="Sample #", standard={
        "fuel": "Sample Material  ", "flow_velocity": "Air Flow (cm/s)"}),
    "PSI-106_Experimental table_Slice.csv": dict(row_is="test_day", id="Test Date", standard={
        "fuel": "Fuel Type"}),
    "PSI-107_Experimental table_Spice.csv": dict(row_is="test", id=None, standard={
        "fuel": "Fuel", "flow_velocity": "Air Rate (cm/s)"}),
    "PSI-10_Experimental table_Flame Design_Inverse Flame.csv": dict(row_is="test", id="Test", standard={
        "oxygen": "XO2", "pressure": "pmean (atm)"},
        **_x(["XO2"])),
    "PSI-10_Experimental table_Flame Design_Normal Flame.csv": dict(row_is="test", id="Test", standard={
        "fuel": "Fuel", "oxygen": "XO2 (init)", "pressure": "pmean (atm)"},
        **_x(["XO2 (init)", "XO2 (final)"])),
    "PSI-142_Experimental table_Data Summary Table.csv": dict(row_is="published_figure", id="Data ID",
                                                              standard={}),
    "PSI-159_Experimental table_CFI-G_Inverse Flames.csv": dict(row_is="test", id="Test", standard={
        "fuel": "Fuel", "oxygen": "XO2", "pressure": "approx p (bar)", "burn_time": "burn time (sec)",
        "test_end": "Self -ext or flow term"},
        **_x(["XO2"])),
    "PSI-159_Experimental table_CFI-G_Normal Flames.csv": dict(row_is="test", id="Test", standard={
        "fuel": "Fuel", "oxygen": " XO2 before test", "pressure": "approx p (bar)",
        "burn_time": "burn time (sec)", "test_end": "Self-ext or flow term"},
        **_x([" XO2 before test", "XO2  after test"])),
    "PSI-20_Experimental table_ACME BRE.csv": dict(row_is="test_day", id=None, standard={
        "fuel": "Fuel Bottle", "oxygen": "Oxygen Conc (percent)"}),
    "PSI-21_Experimental table_CLD Flame.csv": dict(row_is="test_day", id="Test Day", standard={
        "fuel": "Fuel Bottle"}),
    "PSI-22_Experimental table_ACME E-FIELD Flames.csv": dict(row_is="test_day", id="Test Day", standard={
        "fuel": "Fuel Bottle"}),
    "PSI-23_Experimental table_ACME s-Flame.csv": dict(row_is="test_day", id="Test Day*", standard={
        "fuel": "Fuel Bottle"}),
    "PSI-25_Experimental table_BASS-II.csv": dict(row_is="test", id="Test #", standard={
        "fuel": "Fuel Sample Material", "oxygen": "Calibrated  initial O2 % by vol "}),
    "PSI-26_Experimental table_BASS.csv": dict(row_is="test", id="As Run Test #", standard={
        "fuel": "Fuel Sample Material"}),
    "PSI-39_Experimental table_CFI.csv": dict(row_is="test", id="Flex Number", standard={
        "fuel": "Fuel ", "oxygen": "Oxygen", "pressure": "Pressure"},
        # The header gives no unit; the Oxygen, Nitrogen and Helium columns add up to 1.
        column_units={"Oxygen": "mole fraction", "Nitrogen": "mole fraction", "Helium": "mole fraction"},
        units_inferred=["Oxygen", "Nitrogen", "Helium"]),
    "PSI-47_Experimental table_DAFT.csv": dict(row_is="session", id="Session Name", standard={}),
    "PSI-68_Experimental table_Flex2.csv": dict(row_is="fuel_summary", id=None, standard={
        "fuel": "Sample (Fuel Type)", "oxygen": "Oxygen Mole Fraction", "pressure": "Ambient Pressure (atm)",
        "flow_velocity": "Flow Velocity (cm/s)"}, column_units={"Oxygen Mole Fraction": "mole fraction"}),
    "PSI-69_Experimental table_FLEX.csv": dict(row_is="test", id="FLEX Test #", encoding="cp1252", standard={
        "fuel": "Fuel", "oxygen": "O initial ambient composition; mole fraction",
        "pressure": "Ambient pressure; mmHg", "burn_time": "Burn time; s", "test_end": "Test end"}),
    "PSI-98_Experimental table_SAFFIRE-1.csv": dict(row_is="test", id="Sample Number ", standard={
        "fuel": "Material", "oxygen": "Percent O2", "flow_velocity": "Air Flow (cm/s)",
        "burn_time": "Burn Time (s)"}, column_units={"Percent O2": "%"}),
    "PSI-99_Experimental table_SAFFIRE-2.csv": dict(row_is="test", id="Sample Number", standard={
        "fuel": "Material", "oxygen": "Percent O2 (Note 1)", "flow_velocity": "Air Flow (cm/s)",
        "burn_time": "Burn Time (s)"}, column_units={"Percent O2 (Note 1)": "%"}),
}

STANDARD = {  # FLARE field -> (role, unit FLARE stores it in)
    "fuel": ("condition", None),
    "oxygen": ("condition", "mole fraction"),
    "pressure": ("condition", "atm"),
    "flow_velocity": ("condition", "cm/s"),
    "burn_time": ("outcome", "s"),
    "test_end": ("outcome", None),
}
# Conversions FLARE treats as exact. Volume percent equals mole percent for ideal gases.
TO_STANDARD = {
    ("oxygen", "%"): 0.01, ("oxygen", "% by vol"): 0.01, ("oxygen", "mole fraction"): 1.0,
    ("pressure", "atm"): 1.0, ("pressure", "mmHg"): 1 / 760, ("pressure", "bar"): 1 / 1.01325,
    ("flow_velocity", "cm/s"): 1.0, ("burn_time", "s"): 1.0,
}

BASS2_MATRIX = "BASS-II Test Matrix by PI Final.xlsx"


def _number(text: str) -> int | float:
    text = text.replace("+", "")
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return float(text)


def parse_cell(raw: str) -> dict:
    """Read one cell. Always returns `raw` unchanged, plus `kind` and what FLARE read from it."""
    s = raw.strip()
    cell: dict = {"raw": raw}
    if s == "":
        return cell | {"kind": "missing", "missing": "empty"}
    if s.lower() in MISSING_TEXT:
        return cell | {"kind": "missing", "missing": "text"}
    if s in DASHES:
        return cell | {"kind": "missing", "missing": "dash"}
    if RE_SHEET_ERROR.match(s):
        return cell | {"kind": "missing", "missing": "spreadsheet_error"}

    if m := RE_NUMBER.match(s):
        cell |= {"kind": "number", "value": _number(m["n"])}
        if m["unit"]:
            cell["unit"] = m["unit"]
        if m["approx"]:
            cell["approx"] = True
        if m["bound"]:
            cell["bound"] = m["bound"].strip()
        if re.match(r"^0\d", m["n"]):
            cell["flags"] = ["leading_zero"]
        return cell

    if (m := RE_RANGE.match(s)) and (m["ua"] in (None, m["ub"]) or m["ub"] is None):
        cell |= {"kind": "range", "range": [_number(m["a"]), _number(m["b"])]}
        if unit := (m["ub"] or m["ua"]):
            cell["unit"] = unit
        if m["approx"]:
            cell["approx"] = True
        return cell

    tokens = [t for t in re.split(r"[;,]|\s+", s) if t and t.lower() not in {"or", "and", "&"}]
    unit = None
    if tokens and tokens[-1] in CELL_UNITS:
        unit = tokens.pop()
    if len(tokens) >= 2 and all(re.fullmatch(rf"{NUM}%?", t) for t in tokens):
        units = {"%" for t in tokens if t.endswith("%")}
        cell |= {"kind": "list", "values": [_number(t.rstrip("%")) for t in tokens]}
        if unit or units:
            cell["unit"] = unit or "%"
        return cell

    return cell | {"kind": "text"}


def header_unit(header: str) -> str | None:
    """The unit a PSI header states, in FLARE's spelling, or None when it states none."""
    h = header.strip().rstrip("*").strip()
    candidates = re.findall(r"\(([^()]*)\)", h)
    if ";" in h:
        candidates.append(h.rsplit(";", 1)[1])
    if "% by vol" in h:
        candidates.append("% by vol")
    for c in reversed(candidates):
        key = c.strip().lower()
        if key in HEADER_UNITS:
            return HEADER_UNITS[key]
    return None


def _numbers(cell: dict) -> list:
    return [cell["value"]] if "value" in cell else cell.get("values") or cell.get("range") or []


def check_cell(cell: dict, unit: str | None, gas_column: bool = False) -> None:
    """Flag readings no instrument could give. The value itself is left as PSI wrote it."""
    unit = cell.get("unit") or unit
    flags = cell.setdefault("flags", [])
    nums = _numbers(cell)
    if unit in {"ppm", "%", "% by vol", "mole fraction"} and any(n < 0 for n in nums):
        flags.append("negative_concentration")
    if unit in {"%", "% by vol"} and any(n > 100 for n in nums):
        flags.append("percent_over_100")
    if unit == "mole fraction" and any(n > 1 for n in nums):
        flags.append("fraction_over_1")
    if gas_column and cell["kind"] == "text" and RE_IMPOSSIBLE_FORMULA.search(cell["raw"]):
        flags.append("impossible_formula")
    if not flags:
        del cell["flags"]


def parse_fuel(raw: str) -> dict:
    """Split a sample description into material, shape and sizes, only as far as the text says."""
    out: dict = {}
    low = raw.lower()
    if found := [m for m in MATERIALS if m.lower() in low]:
        out["material"] = found if len(found) > 1 else found[0]
    if shape := next((s for s in SHAPES if re.search(rf"\b{s}\b", low)), None):
        out["shape"] = shape
    sizes = []
    for m in RE_SIZE.finditer(raw):
        n, u = m["n"], m["u"].lower()
        value = int(n.split("/")[0]) / int(n.split("/")[1]) if "/" in n else _number(n)
        size = {"value": value, "unit": "in" if u in {'"', "in"} else u, "text": m.group(0).strip()}
        if m["label"]:
            size["label"] = m["label"].lower()
        sizes.append(size)
    if sizes:
        out["sizes"] = sizes
    return out


def standard_field(name: str, column: str, cell: dict, unit: str | None) -> dict:
    """Copy one cell into a FLARE field, converting the unit only when the conversion is exact."""
    role, target = STANDARD[name]
    field = {"column": column, "role": role}
    if cell["kind"] == "missing":
        return field | {"missing": cell["missing"]}
    if name in {"fuel", "test_end"} or cell["kind"] == "text":
        field["text"] = cell["raw"].strip()
        if name == "fuel":
            field |= parse_fuel(cell["raw"])
        return field
    source_unit = cell.get("unit") or unit
    factor = TO_STANDARD.get((name, source_unit))
    if factor is None:
        return field | {"unconverted": True, "unit": source_unit, "text": cell["raw"].strip()}
    key = "value" if "value" in cell else "values" if "values" in cell else "range"
    original = cell[key]
    converted = original * factor if key == "value" else [n * factor for n in original]
    tidy = (lambda x: float(f"{x:.10g}")) if factor != 1.0 else (lambda x: x)
    field |= {key: tidy(converted) if key == "value" else [tidy(x) for x in converted], "unit": target}
    if cell.get("approx"):
        field["approx"] = True
    if factor != 1.0:
        field |= {"calculated": True, "original": {key: original, "unit": source_unit}}
    return field


def read_xlsx(path: Path) -> dict[str, list[list[str]]]:
    """Every sheet of an .xlsx as rows of strings, in sheet order. Standard library only."""
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    t_tag = f"{{{ns['m']}}}t"
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns):
                shared.append("".join(t.text or "" for t in si.iter(t_tag)))
        rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        sheets = {}
        for sheet in ET.fromstring(z.read("xl/workbook.xml")).find("m:sheets", ns):
            target = rels[sheet.get(f"{{{ns['r']}}}id")].lstrip("/")
            target = target if target.startswith("xl/") else "xl/" + target
            rows = []
            for row in ET.fromstring(z.read(target)).find("m:sheetData", ns):
                values = {}
                for c in row:
                    col = re.match(r"[A-Z]+", c.get("r"))[0]
                    v = c.find("m:v", ns)
                    if c.get("t") == "s":
                        text = shared[int(v.text)]
                    elif c.get("t") == "inlineStr":
                        text = "".join(t.text or "" for t in c.iter(t_tag))
                    else:
                        text = "" if v is None else v.text
                    values[col] = text
                width = max((_col_index(k) for k in values), default=-1) + 1
                cells = [""] * width
                for k, text in values.items():
                    cells[_col_index(k)] = text
                rows.append(cells)
            sheets[sheet.get("name")] = rows
    return sheets


def _col_index(letters: str) -> int:
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def bass2_matrix_index() -> dict[str, dict]:
    """BASS-II test ID -> where the same test sits in PSI's test matrix workbook."""
    index = {}
    for sheet, rows in read_xlsx(DATASETS / BASS2_MATRIX).items():
        header = [h.strip() for h in rows[0]]
        test_col, date_col = header.index("Test no."), 0
        for i, row in enumerate(rows[1:], start=2):
            if len(row) <= test_col or not row[test_col].strip():
                continue
            test = row[test_col].strip()
            link = {"file": BASS2_MATRIX, "sheet": sheet, "row": i}
            serial = row[date_col].strip()
            if re.fullmatch(r"\d+(\.\d+)?", serial):
                link["date"] = (date(1899, 12, 30) + timedelta(days=int(float(serial)))).isoformat()
            if test in index:
                raise ValueError(f"test {test} appears twice in {BASS2_MATRIX}")
            index[test] = link
    return index


def process_table(file_name: str, sources: dict[str, dict]) -> dict:
    spec = TABLES[file_name]
    encoding = spec.get("encoding", "utf-8-sig")
    with open(DATASETS / file_name, encoding=encoding, newline="") as f:
        lines = list(csv.reader(f))
    header = [h.lstrip("﻿") for h in lines[0]]
    units = {h: spec.get("column_units", {}).get(h) or header_unit(h) for h in header}
    for name, column in spec["standard"].items():
        if column not in header:
            raise ValueError(f"{file_name}: column {column!r} for {name} is not in the header")

    matrix = bass2_matrix_index() if file_name == "PSI-25_Experimental table_BASS-II.csv" else None
    rows, seen = [], {}
    for line_no, values in enumerate(lines[1:], start=2):
        if not any(v.strip() for v in values):
            continue  # PSI-159's inverse-flame table has 861 empty lines between real rows.
        cells = {}
        for h, v in zip(header, values):
            cell = parse_cell(v)
            check_cell(cell, units[h], gas_column=bool(re.search(r"fuel|atmosphere", h, re.I)))
            cells[h] = cell
        row = {"line": line_no, "run_id": values[header.index(spec["id"])].strip() if spec["id"] else None,
               "cells": cells,
               "standard": {n: standard_field(n, c, cells[c], units[c]) for n, c in spec["standard"].items()}}
        key = tuple(v.strip() for v in values)
        if key in seen:
            row["same_as_line"] = seen[key]
        else:
            seen[key] = line_no
        if matrix is not None:
            link = matrix.pop(row["run_id"], None)
            if link is None:
                raise ValueError(f"BASS-II test {row['run_id']} is not in {BASS2_MATRIX}")
            row["linked"] = [link]
        rows.append(row)
    if matrix:
        raise ValueError(f"{BASS2_MATRIX} has tests the BASS-II table lacks: {sorted(matrix)}")

    source = sources[file_name]
    return {
        "file": file_name,
        "psi_file_name": source["psi_file_name"],
        "doi_url": source["doi_url"],
        "encoding": encoding.replace("-sig", ""),
        "row_is": spec["row_is"],
        "row_count": len(rows),
        "columns": [{"name": h, "unit": units[h]} | ({"unit_inferred": True} if h in spec.get("units_inferred", [])
                                                      else {}) for h in header],
        "standard_columns": spec["standard"],
        "rows": rows,
    }


def build() -> dict[str, dict]:
    with open(DATASETS / "SOURCES.csv", encoding="utf-8", newline="") as f:
        sources = {r["file"]: r for r in csv.DictReader(f)}
    missing = sorted(set(TABLES) - set(sources))
    if missing:
        raise ValueError(f"not in SOURCES.csv: {missing}")
    by_accession: dict[str, dict] = {}
    for file_name in sorted(TABLES):
        accession = sources[file_name]["accession"]
        entry = by_accession.setdefault(accession, {"accession": accession, "tables": []})
        entry["tables"].append(process_table(file_name, sources))
    return by_accession


def write(by_accession: dict[str, dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        if old.stem not in by_accession:
            old.unlink()
    for accession, entry in by_accession.items():
        text = json.dumps(entry, ensure_ascii=False, indent=1) + "\n"
        tmp = OUT / f"{accession}.json.tmp"
        tmp.write_text(text, encoding="utf-8", newline="\n")
        tmp.replace(OUT / f"{accession}.json")


def main() -> int:
    by_accession = build()
    write(by_accession)
    total = sum(t["row_count"] for e in by_accession.values() for t in e["tables"])
    print(f"wrote {len(by_accession)} files, {total} rows, to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
