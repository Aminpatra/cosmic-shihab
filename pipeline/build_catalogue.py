"""Turn the harvested PSI responses into the files the FLARE backend reads.

    python3 pipeline/build_catalogue.py

Reads  .cache/psi/raw/        (written by pipeline/harvest.py)
       datasets/              (the experimental tables)
       research/investigation_tags.csv   (hand-written tags, each with its source)
Writes backend/data/investigations/<ACCESSION>.json   one per investigation
       backend/data/files.csv                         one row per PSI file
       datasets/SOURCES.csv                           where each dataset file came from
       research/investigation_inventory.csv           one row per investigation, tags included

Every value copied from PSI keeps PSI's own field name and is not changed.
Anything FLARE computed sits under the "derived" key. Contact e-mail addresses
and phone numbers are left out; names, affiliations and roles are kept.

AI use: written with Claude Code (Claude Fable 5.2), reviewed by the team. The
output files are NASA data rearranged by this script, not AI-generated content.
"""

from __future__ import annotations

import csv
import datetime
import email.utils
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psi_client as psi  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, ".cache", "psi", "raw")
DATASETS = os.path.join(ROOT, "datasets")
RESEARCH = os.path.join(ROOT, "research")
OUT = os.path.join(ROOT, "backend", "data")

# Copied from the PSI record exactly as given.
COPIED = (
    "accession", "title", "investigationAcronym", "proposalTitle", "doi",
    "licenseIdentifier", "licenseName", "licenseLink",
    "researchArea", "subResearchArea", "projectType",
    "flightProgram", "spaceProgram", "managingNasaCenter", "funding",
    "investigationStartDate", "investigationEndDate", "releaseDate", "modifiedDate",
    "version", "versionReason",
    "objective", "hypothesis", "approach", "researchImpacts", "description",
    "experimentHardware", "experimentHardwareLink", "related_glds",
    "public", "restricted", "totalFileSize",
)

KINDS = {
    "archive_or_video": {".zip", ".ziip", ".ts", ".mp4", ".avi", ".mpg"},
    "document": {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".rtf"},
    "table": {".csv", ".xls", ".xlsx"},
    "text": {".txt", ".log", ".asc"},
    "numeric": {".dat"},
}
# Allowed values of each tag in research/investigation_tags.csv; "; " joins several.
# hardware_facility is free text. Every tag needs a non-empty *_source column.
TAG_VALUES = {
    "platform": {"ISS", "Cygnus (after leaving the ISS)", "computation",
                 "ground laboratory and computation"},
    "fuel_phase": {"solid", "liquid", "gas", "none (no fuel burned)", "not stated"},
    "fire_safety_role": {"prevention", "detection", "suppression", "not stated"},
    "gravity_level": {"microgravity", "normal gravity", "not stated"},
    "flare_data": {"run table", "test-day log", "test matrix", "figure index",
                   "catalogue metadata only"},
}
TAGS = ("hardware_facility", *TAG_VALUES)

MANIFEST_COLUMNS = (
    "accession", "file_id", "file_name", "category", "subcategory",
    "extension", "kind", "bytes", "version", "updated",
)


def kind_of(extension: str) -> str:
    for kind, extensions in KINDS.items():
        if extension in extensions:
            return kind
    return "other"


def iso_date(http_date: str) -> str:
    """'Sat, 07 Jun 2025 03:42:47 GMT' -> '2025-06-07T03:42:47Z'; empty stays empty."""
    if not http_date:
        return ""
    return email.utils.parsedate_to_datetime(http_date).strftime("%Y-%m-%dT%H:%M:%SZ")


def table_shape(path: str) -> tuple[int, int]:
    """Data rows and columns of an experimental table (blank rows not counted)."""
    with open(path, "rb") as handle:
        text = handle.read().decode("utf-8-sig", errors="replace")
    rows = [row for row in csv.reader(io.StringIO(text)) if any(cell.strip() for cell in row)]
    return len(rows) - 1, len(rows[0])


def load(path: str, what: str):
    with open(path, "rb") as handle:
        return psi.parse_json(handle.read(), what)


def retrieved_on(path: str) -> str:
    stamp = datetime.datetime.fromtimestamp(os.path.getmtime(path), datetime.timezone.utc)
    return stamp.strftime("%Y-%m-%d")


def load_tags() -> dict[str, dict]:
    """Read the hand-written tags, refusing unknown values and missing sources."""
    path = os.path.join(RESEARCH, "investigation_tags.csv")
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    tags = {}
    for row in rows:
        accession = row["accession"]
        for tag in TAGS:
            if not row[tag].strip() or not row[f"{tag}_source"].strip():
                raise ValueError(f"{path}: {accession} lacks {tag} or its source")
            allowed = TAG_VALUES.get(tag)
            if allowed and not set(row[tag].split("; ")) <= allowed:
                raise ValueError(f"{path}: {accession} {tag}={row[tag]!r} is not one of {allowed}")
        tags[accession] = {
            "values": {tag: row[tag] for tag in TAGS},
            "sources": {tag: row[f"{tag}_source"] for tag in TAGS},
            "notes": row["notes"],
        }
    return tags


def normalize(accession: str, tags: dict) -> tuple[dict, list[dict]]:
    record_path = os.path.join(RAW, f"inv_{accession}.json")
    record = psi.check_record(load(record_path, accession), accession)
    missing = [key for key in COPIED if key not in record]
    if missing:
        raise psi.PSIFormatError(f"{accession}: record lacks {missing}")
    tree = load(os.path.join(RAW, f"files_{accession}.json"), f"{accession} file list")
    files = psi.flatten_files(tree)

    blocked = [f["file_name"] for f in files
               if f["status"] != "active" or f["restricted"] or f["visible"] is not True]
    if blocked:
        raise psi.PSIFormatError(f"{accession}: files that are not open: {blocked[:3]}")

    out = {key: record[key] for key in COPIED}
    out["contacts"] = [
        {
            "firstName": person.get("firstName", ""),
            "midInitials": person.get("midInitials", ""),
            "lastName": person.get("lastName", ""),
            "affiliation": person.get("affiliation", ""),
            "roles": [role.get("annotationValue", "") for role in person.get("roles") or []],
        }
        for person in record.get("contacts") or []
    ]
    out["publications"] = [
        {
            "title": item.get("title", ""),
            "authorList": item.get("authorList", ""),
            "doi": item.get("doi", ""),
            "pubMedID": item.get("pubMedID", ""),
            "status": (item.get("status") or {}).get("annotationValue", ""),
        }
        for item in record.get("publications") or []
    ]

    by_kind: dict[str, dict] = {}
    rows = []
    for entry in sorted(files, key=lambda f: (f["category"], f["file_name"], f["file_id"])):
        kind = kind_of(entry["extension"])
        tally = by_kind.setdefault(kind, {"files": 0, "bytes": 0})
        tally["files"] += 1
        tally["bytes"] += entry["bytes"]
        rows.append({
            "accession": accession,
            "file_id": entry["file_id"],
            "file_name": entry["file_name"],
            "category": entry["category"],
            "subcategory": entry["subcategory"],
            "extension": entry["extension"],
            "kind": kind,
            "bytes": entry["bytes"],
            "version": entry["version"],
            "updated": iso_date(entry["updated"]),
        })

    tables = []
    for entry in rows:
        if entry["category"] != "Experimental table":
            continue
        path = os.path.join(DATASETS, entry["file_name"])
        if not os.path.exists(path) or os.path.getsize(path) != entry["bytes"]:
            raise psi.PSIFormatError(f"{entry['file_name']}: missing from datasets/ or wrong size")
        data_rows, columns = table_shape(path)
        tables.append({"file_name": entry["file_name"], "bytes": entry["bytes"],
                       "rows": data_rows, "columns": columns})

    out["derived"] = {
        "note": "Computed by FLARE (pipeline/build_catalogue.py); not part of the PSI record.",
        "retrieved": retrieved_on(record_path),
        "page_url": psi.PAGE_URL.format(accession=accession),
        "doi_url": f"https://doi.org/{record['doi']}" if record["doi"] else "",
        "licence_stated": bool(record["licenseIdentifier"]),
        "file_count": len(rows),
        "bytes_listed": int(psi.listed_bytes(tree)),
        "files_by_kind": dict(sorted(by_kind.items())),
        "experimental_tables": tables,
        "tags": {
            "note": "Written by FLARE in research/investigation_tags.csv, drafted with Claude "
                    "Code (Claude Opus 5.5); each tag cites a field of this record "
                    "(record.<field>) or a dataset file.",
            **tags,
        },
    }
    return out, rows


def legacy_names() -> dict[str, str]:
    """Old PSI file names -> today's names.

    PSI renamed its files to "PSI-n_Category_name". A record's change log keeps
    the old path of each renamed file, which lets us trace an earlier download.
    """
    names: dict[str, str] = {}
    for raw_name in os.listdir(RAW):
        if not raw_name.startswith("inv_"):
            continue
        record = load(os.path.join(RAW, raw_name), raw_name)
        for entry in record.get("added") or []:
            old = (entry.get("psi_legacy_s3_path") or "").rsplit("/", 1)[-1]
            if old and entry.get("file_name"):
                names[old] = entry["file_name"]
    return names


def write_sources(investigations: dict[str, dict], manifest: list[dict]) -> None:
    """Record where every file in datasets/ came from, as far as PSI's list shows."""
    by_name = {row["file_name"]: row for row in manifest}
    renamed = legacy_names()
    lines = []
    for name in sorted(os.listdir(DATASETS)):
        path = os.path.join(DATASETS, name)
        if not os.path.isfile(path) or name in ("SOURCES.csv", "README.md"):
            continue
        row = by_name.get(name) or by_name.get(renamed.get(name, ""))
        local = os.path.getsize(path)
        if row is None:
            lines.append([name, "", "", "", "", "", local, "", "not found in PSI's file list"])
            continue
        investigation = investigations[row["accession"]]
        same = "yes" if local == row["bytes"] else "no"
        lines.append([
            name, row["accession"], investigation["investigationAcronym"],
            investigation["derived"]["doi_url"], row["file_name"], row["category"],
            local, row["bytes"], f"same size as PSI: {same}",
        ])
    with open(os.path.join(DATASETS, "SOURCES.csv"), "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["file", "accession", "investigation", "doi_url", "psi_file_name",
                         "psi_category", "bytes_here", "bytes_at_psi", "check"])
        writer.writerows(lines)


def write_inventory(investigations: dict[str, dict]) -> None:
    """One row per investigation: PSI's facts, FLARE's counts and the tags."""
    columns = ("accession", "acronym", "title", "project_type", "flight_program",
               "start_date", "end_date", "doi_url", "page_url", "licence", "file_count",
               "bytes_listed", "experimental_tables", "table_rows", *TAGS, "retrieved")
    with open(os.path.join(RESEARCH, "investigation_inventory.csv"), "w", newline="",
              encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        for accession, record in investigations.items():
            derived = record["derived"]
            tables = derived["experimental_tables"]
            writer.writerow([
                accession, record["investigationAcronym"], record["title"],
                record["projectType"], record["flightProgram"],
                record["investigationStartDate"], record["investigationEndDate"],
                derived["doi_url"], derived["page_url"],
                record["licenseIdentifier"] or "not stated",
                derived["file_count"], derived["bytes_listed"], len(tables),
                sum(table["rows"] for table in tables),
                *(derived["tags"]["values"][tag] for tag in TAGS), derived["retrieved"],
            ])


def main() -> None:
    accessions = sorted(
        (name[4:-5] for name in os.listdir(RAW) if name.startswith("inv_") and name.endswith(".json")),
        key=lambda accession: int(accession.split("-")[1]),
    )
    if not accessions:
        sys.exit(f"nothing in {RAW}; run pipeline/harvest.py first")
    tags = load_tags()
    if set(tags) != set(accessions):
        sys.exit(f"tags and PSI records differ: {sorted(set(tags) ^ set(accessions))}")
    os.makedirs(os.path.join(OUT, "investigations"), exist_ok=True)
    investigations, manifest = {}, []
    for accession in accessions:
        investigation, rows = normalize(accession, tags[accession])
        investigations[accession] = investigation
        manifest.extend(rows)
        path = os.path.join(OUT, "investigations", f"{accession}.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(investigation, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
    with open(os.path.join(OUT, "files.csv"), "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, MANIFEST_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)
    write_sources(investigations, manifest)
    write_inventory(investigations)
    total = sum(row["bytes"] for row in manifest)
    print(f"{len(investigations)} investigations, {len(manifest)} files, {total / 1e12:.2f} TB")


if __name__ == "__main__":
    main()
