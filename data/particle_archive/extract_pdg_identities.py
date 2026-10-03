"""Archive the identity tables of the pinned official PDG 2026.0 SQLite file.

Only Python's standard library is used. Database reads are explicitly read-only;
no PDG REST endpoints, package installation, or discovery inference is involved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SOURCE_URL = "https://pdg.lbl.gov/2026/api/pdg-2026.0.sqlite"
SOURCE_SHA256 = "40dc2587d9ae912d26fafb6b41f300f341d2a1f4bd620ff5b5f03827c39453fe"
SOURCE_BYTES = 25_751_552
ARCHIVE_FILE = "pdg2026_identity_archive.json"
METADATA_FILE = "pdg2026_identity_metadata.json"
SCRIPT_VERSION = "1.0"

# The identity scope includes all search identifiers even if they lack a
# charge-state entry. Alias/text rows are exported as names, not new particles.
SELECTORS = {
    "pdgparticle": "SELECT * FROM pdgparticle ORDER BY id",
    "pdgid": "SELECT * FROM pdgid WHERE data_type IN ('PART', 'SRCH') ORDER BY id",
    "pdgitem": "SELECT * FROM pdgitem ORDER BY id",
    "pdgitem_map": "SELECT * FROM pdgitem_map ORDER BY id",
    "pdgdoc": "SELECT * FROM pdgdoc ORDER BY id",
}
EXPECTED_COUNTS = {
    "pdgparticle": 1170,
    "pdgid": 450,
    "pdgitem": 3270,
    "pdgitem_map": 1341,
    "pdgdoc": 71,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def encoded_json(value: Any) -> bytes:
    """Use deterministic UTF-8/LF; retain SQLite NULL as JSON null."""
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_source(path: Path) -> None:
    require(path.is_file(), f"Database not found: {path}")
    require(path.stat().st_size == SOURCE_BYTES, "Unexpected database size; review a changed release separately")
    require(file_sha256(path) == SOURCE_SHA256, "Unexpected database hash; this script is pinned to the observed 2026.0 file")


def read_database(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    check_source(path)
    # Joining identity records always uses numeric primary/foreign keys, as
    # prescribed by PDG. Repeated textual names are not merged or corrected.
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        require([row[0] for row in connection.execute("PRAGMA integrity_check")] == ["ok"], "SQLite integrity failure")
        require(not list(connection.execute("PRAGMA foreign_key_check")), "SQLite foreign-key failure")
        info_rows = [dict(row) for row in connection.execute("SELECT * FROM pdginfo ORDER BY id")]
        info = {row["name"]: row["value"] for row in info_rows}
        require(info.get("edition") == "2026", "Wrong source edition")
        require(info.get("schema_version") == "0.3", "Unreviewed database schema")
        require(info.get("license") == "CC BY 4.0", "Unreviewed source license")
        tables = {
            table: [dict(row) for row in connection.execute(query)]
            for table, query in SELECTORS.items()
        }
        schema = {
            table: [dict(row) for row in connection.execute(f"PRAGMA table_info({table})")]
            for table in SELECTORS
        }
        source_counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in SELECTORS
        }
        source_counts["pdginfo"] = len(info_rows)
        archive = {
            "archive_format_version": 1,
            "source_database_sha256": SOURCE_SHA256,
            "source_database_info_rows": info_rows,
            "table_selectors": SELECTORS,
            "tables": tables,
        }
        diagnostics = summarize_and_validate(archive, schema)
        return archive, {
            "source_database_info": info,
            "source_table_row_counts": source_counts,
            "source_schema": schema,
            "diagnostics": diagnostics,
        }


def summarize_and_validate(archive: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    require(archive.get("archive_format_version") == 1, "Unknown archive format")
    require(archive.get("source_database_sha256") == SOURCE_SHA256, "Archive source identity changed")
    require(archive.get("table_selectors") == SELECTORS, "Archive selection scope changed")
    tables = archive["tables"]
    require(set(tables) == set(SELECTORS), "Missing or unexpected identity table")
    for table, count in EXPECTED_COUNTS.items():
        rows = tables[table]
        require(len(rows) == count, f"Incomplete {table}: {len(rows)} rather than {count}")
        ids = [row["id"] for row in rows]
        require(ids == sorted(ids) and len(ids) == len(set(ids)), f"Duplicate or unsorted {table} primary keys")
        columns = {column["name"] for column in schema[table]}
        require(all(set(row) == columns for row in rows), f"Lost or added source columns in {table}")
    info = {row["name"]: row["value"] for row in archive["source_database_info_rows"]}
    require(len(info) == 10, "Source metadata rows changed")
    require(info.get("license") == "CC BY 4.0", "License attribution changed")
    require(info.get("edition") == "2026", "Edition attribution changed")
    identifiers = {row["id"]: row for row in tables["pdgid"]}
    items = {row["id"]: row for row in tables["pdgitem"]}
    particles = tables["pdgparticle"]
    for row in particles:
        require(row["pdgid_id"] in identifiers, "Missing particle identifier reference")
        identifier = identifiers[row["pdgid_id"]]
        require(row["pdgid"] == identifier["pdgid"], "Conflicting numeric/textual identifier")
        require(identifier["data_type"] == "PART", "Unexpected charge-state identifier type")
        require(row["pdgitem_id"] in items, "Missing particle name reference")
    for row in tables["pdgitem_map"]:
        require(row["pdgitem_id"] in items and row["target_id"] in items, "Broken name/alias mapping")
    types = Counter(row["data_type"] for row in identifiers.values())
    require(dict(types) == {"PART": 439, "SRCH": 11}, "Particle/search scope changed")
    # This particular source contains an ambiguous repeated name. Both source
    # records must survive; deduplication by name would silently destroy data.
    repeated_names = sorted(
        [
            {"name": name, "row_count": count}
            for name, count in Counter(row["name"] for row in particles).items()
            if count > 1
        ],
        key=lambda row: row["name"],
    )
    require(repeated_names == [{"name": "P_c_cbar(4312)+", "row_count": 2}], "Unexpected source-name multiplicity")
    referenced_identifiers = {row["pdgid_id"] for row in particles}
    identities_without_charge_states = [
        {"id": row["id"], "pdgid": row["pdgid"], "description": row["description"], "data_type": row["data_type"], "flags": row["flags"]}
        for row in identifiers.values()
        if row["id"] not in referenced_identifiers
    ]
    require(len(identities_without_charge_states) == 12, "Missing identity/search groups without charge rows")
    particle_columns = [column["name"] for column in schema["pdgparticle"]]
    null_counts = {column: sum(row[column] is None for row in particles) for column in particle_columns}
    marker_counts = {
        column: dict(sorted(Counter(row[column] for row in particles if row[column] in ("?", "")).items()))
        for column in particle_columns
        if column.startswith("quantum_")
    }
    return {
        "exported_row_counts": {table: len(rows) for table, rows in tables.items()},
        "identifier_type_counts": dict(sorted(types.items())),
        "charge_conjugation_code_counts": dict(sorted(Counter(row["cc_type"] for row in particles).items())),
        "particle_identifier_flag_counts": dict(sorted(Counter(identifiers[row["pdgid_id"]]["flags"] for row in particles).items())),
        "name_item_type_counts": dict(sorted(Counter(row["item_type"] for row in items.values()).items())),
        "distinct_charge_state_names": len({row["name"] for row in particles}),
        "distinct_charge_state_pdg_identifiers": len(referenced_identifiers),
        "duplicate_source_names_preserved": repeated_names,
        "identity_groups_without_charge_states": identities_without_charge_states,
        "particle_null_counts_by_column": null_counts,
        "literal_unknown_marker_counts": marker_counts,
        "physical_existence_assessments_performed": 0,
    }


def metadata_for(archive_bytes: bytes, database_details: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    require(observation["url"] == SOURCE_URL, "Download observation URL changed")
    require(observation["sha256"] == SOURCE_SHA256, "Download observation hash changed")
    require(observation["length_bytes"] == SOURCE_BYTES, "Download observation size changed")
    return {
        "metadata_format_version": 1,
        "extraction_script_version": SCRIPT_VERSION,
        "archive_file": ARCHIVE_FILE,
        "archive_sha256": hashlib.sha256(archive_bytes).hexdigest(),
        "archive_bytes": len(archive_bytes),
        "source_download_observation": observation,
        "database_filename": "pdg-2026.0.sqlite",
        "database_release_version_from_official_filename": "2026.0",
        "publication_cutoff": {
            "date": "2026-01-15",
            "applies_to": "PDG 2026 Listings and Summary Tables",
            "source_url": "https://pdg.lbl.gov/2026/listings/contents_listings.html",
            "retrieval_date_utc": "2026-09-30",
            "note": "Publication data cutoff, database release time and retrieval time are different dates.",
        },
        "license": {
            "identifier": "CC-BY-4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "source_license_literal": "CC BY 4.0",
            "attribution": database_details["source_database_info"]["citation"],
            "documentation_url": "https://pdgapi.lbl.gov/doc/schema.html#license",
            "modifications": "Selected identity/name/mapping/code tables from SQLite; serialized as deterministic UTF-8 JSON. No source row values corrected, deduplicated or scientifically reclassified.",
        },
        "scope": {
            "complete_source_tables": ["pdgparticle", "pdgitem", "pdgitem_map", "pdgdoc", "pdginfo"],
            "filtered_source_table": {"table": "pdgid", "condition": "data_type IN ('PART', 'SRCH')", "purpose": "All particle identity and search groups, including groups with no charge-state row."},
            "not_exported": ["property and branching-fraction identifiers", "summary property values", "literature measurements", "decay records", "references", "footnotes", "listing text", "historical Summary Table editions"],
            "not_asserted": ["complete universe of physical particles", "discovery of every listed particle or search candidate", "all future theoretical entities", "every nuclear isotope or isomer", "a preparation route or stable material containing any listed entity", "patent enablement or universal defensive coverage"],
        },
        "interpretation": {
            "unknowns": "SQLite NULL remains JSON null. Literal question marks, blanks, ambiguous strings and original quantum-number text remain unchanged. They are not converted to zero, a measured result or a guessed value.",
            "physical_existence_status": None,
            "physical_existence_status_basis": "No particle discovery/existence-status column is supplied in these identity tables. PART, SRCH, category flags, Monte Carlo numbers, quantum numbers and CC_TYPE are preserved metadata, not discovery certificates. Release-level pdginfo.status=production describes the database, not all particles.",
            "charge_conjugation": "CC_TYPE encodes particle, antiparticle or self-conjugate state, with the original code meanings retained in pdgdoc.",
            "names": "Use numeric source primary keys and edition-qualified PDG identifiers for joins. Names are not necessarily unique; aliases/generic names/texts are not additional physical species.",
            "charge": "The source REAL value is retained as a JSON number without new rounding; this identity value is not an independently measured charge or uncertainty record.",
            "monte_carlo_ids": "MCID is distinct from a PDG Identifier and may be null. The source numbering conventions are not rewritten.",
        },
        "upstream_api_limits": {
            "documentation_url": "https://pdgapi.lbl.gov/doc/status.html",
            "checked_date_utc": "2026-09-30",
            "limits": ["fit information and correlation matrices inaccessible", "conservation-law data inaccessible", "some listing header text/notes inaccessible", "some listing text values lack parentheses", "some limits lack numerical values and only have text"],
            "note": "Identity-only extraction also deliberately omits available property/measurement tables; upstream limitations are not confused with this archive's selection scope.",
        },
        "access_method": {
            "method": "One official versioned SQLite download; offline standard-library SQL extraction",
            "bulk_rest_used": False,
            "rest_terms_url": "https://pdgapi.lbl.gov/doc/restapi.html#terms-of-use",
            "schema_url": "https://pdgapi.lbl.gov/doc/schema.html",
            "download_index_url": "https://pdg.lbl.gov/2026/api/index.html",
        },
        **database_details,
    }


def extract(args: argparse.Namespace) -> None:
    archive, details = read_database(args.database)
    observation = json.loads(args.download_observation.read_text(encoding="utf-8-sig"))
    archive_bytes = encoded_json(archive)
    metadata = metadata_for(archive_bytes, details, observation)
    args.output_directory.mkdir(parents=True, exist_ok=True)
    (args.output_directory / ARCHIVE_FILE).write_bytes(archive_bytes)
    (args.output_directory / METADATA_FILE).write_bytes(encoded_json(metadata))
    print(json.dumps({"archive_bytes": len(archive_bytes), "counts": details["diagnostics"]["exported_row_counts"]}))


def verify(args: argparse.Namespace) -> None:
    directory = args.archive_directory
    archive_path = directory / ARCHIVE_FILE
    metadata = json.loads((directory / METADATA_FILE).read_text(encoding="utf-8"))
    archive_bytes = archive_path.read_bytes()
    archive = json.loads(archive_bytes)
    require(encoded_json(archive) == archive_bytes, "Archive is not in its documented deterministic format")
    require(len(archive_bytes) == metadata["archive_bytes"], "Archive byte count changed")
    require(hashlib.sha256(archive_bytes).hexdigest() == metadata["archive_sha256"], "Archive checksum mismatch")
    require(metadata["source_download_observation"]["sha256"] == SOURCE_SHA256, "Wrong metadata source hash")
    require(metadata["source_download_observation"]["url"] == SOURCE_URL, "Wrong metadata download URL")
    require(metadata["interpretation"]["physical_existence_status"] is None, "An unsupported global discovery status was added")
    diagnostics = summarize_and_validate(archive, metadata["source_schema"])
    require(diagnostics == metadata["diagnostics"], "Metadata diagnostics mismatch")
    require(metadata["license"]["identifier"] == "CC-BY-4.0", "Archive license changed")
    require(metadata["publication_cutoff"]["date"] == "2026-01-15", "Publication cutoff changed")
    source_comparison = "not run; pass --database for complete source-row comparison"
    if args.database:
        regenerated, details = read_database(args.database)
        require(encoded_json(regenerated) == archive_bytes, "Export differs from complete selected source tables")
        require(details["source_schema"] == metadata["source_schema"], "Source schema changed")
        require(details["source_database_info"] == metadata["source_database_info"], "Source release metadata changed")
        source_comparison = "passed: all columns and all selected rows match pinned SQLite, including NULLs and repeated names"
    result = {
        "passed": True,
        "archive_sha256": metadata["archive_sha256"],
        "archive_bytes": len(archive_bytes),
        "exported_row_counts": diagnostics["exported_row_counts"],
        "source_comparison": source_comparison,
        "physical_existence_assessments_performed": 0,
        "patent_enablement_assessed": False,
    }
    if args.report:
        args.report.write_bytes(encoded_json(result))
    print(json.dumps(result, indent=2))


def download(args: argparse.Namespace) -> None:
    """Fetch one pinned database; never bulk-crawl REST or overwrite a file."""
    destination = args.destination.resolve()
    requested_partial = destination.with_suffix(destination.suffix + ".part")
    partial = requested_partial.resolve()
    observation_path = args.observation.resolve()
    # Resolve aliases and validate every output before creating directories or
    # fetching bytes: metadata must never replace the database or its partial.
    require(len({destination, partial, observation_path}) == 3,
            "Destination, partial download and observation must be distinct paths")
    require(all(left not in right.parents and right not in left.parents
                for left, right in ((destination, partial), (destination, observation_path),
                                    (partial, observation_path))),
            "Destination, partial download and observation must not be ancestors or descendants")
    require(not (args.destination.exists() or args.destination.is_symlink() or destination.exists()),
            "Destination already exists; verify/reuse it instead of overwriting")
    require(not (requested_partial.exists() or requested_partial.is_symlink() or partial.exists()),
            "Unreviewed partial download already exists")
    require(not (args.observation.exists() or args.observation.is_symlink() or observation_path.exists()),
            "Observation already exists; preserve and review it instead of overwriting")
    destination.parent.mkdir(parents=True, exist_ok=True)
    observation_path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "PDGIdentityArchive/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response, partial.open("xb") as output:
        status_code = response.status
        content_type = response.headers.get("Content-Type")
        last_modified = response.headers.get("Last-Modified")
        etag = response.headers.get("ETag")
        for chunk in iter(lambda: response.read(1024 * 1024), b""):
            output.write(chunk)
    check_source(partial)
    # Publish the verified sibling file without replacing a concurrent writer.
    # This requires same-filesystem hard-link support; unsupported filesystems
    # fail closed and retain the partial for review rather than falling back to
    # a Unix rename that could overwrite an existing destination.
    destination.hardlink_to(partial)
    partial.unlink()
    observation = {
        "url": SOURCE_URL,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "status_code": status_code,
        "content_type": content_type,
        "last_modified": last_modified,
        "etag": etag,
        "length_bytes": SOURCE_BYTES,
        "sha256": SOURCE_SHA256,
    }
    # Another writer can create the observation after preflight. Exclusive
    # creation preserves that file rather than overwriting its provenance.
    with observation_path.open("xb") as output:
        output.write(encoded_json(observation))
    print(json.dumps(observation, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    extraction = subparsers.add_parser("extract", help="Extract identities from the pinned source file")
    extraction.add_argument("--database", required=True, type=Path)
    extraction.add_argument("--download-observation", required=True, type=Path)
    extraction.add_argument("--output-directory", required=True, type=Path)
    extraction.set_defaults(function=extract)
    verification = subparsers.add_parser("verify", help="Verify archive; optionally compare every selected source row")
    verification.add_argument("--archive-directory", type=Path, default=Path(__file__).resolve().parent)
    verification.add_argument("--database", type=Path)
    verification.add_argument("--report", type=Path)
    verification.set_defaults(function=verify)
    downloading = subparsers.add_parser("download", help="One optional official SQLite download, never REST crawling")
    downloading.add_argument("--destination", required=True, type=Path)
    downloading.add_argument("--observation", required=True, type=Path)
    downloading.set_defaults(function=download)
    args = parser.parse_args()
    try:
        args.function(args)
    except (OSError, ValueError, sqlite3.Error, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
