"""Build a complete, source-scoped identity REVIEW annex without modifying inputs.

The default paths are relative to this script's package. Under python -B (or
PYTHONDONTWRITEBYTECODE), import and --check perform no file writes or network
access. PDF generation is deliberately a
separate command; the calling workflow must record the PDF artifact operation
before running it. This rendered view never replaces the original raw archives.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any


DEFAULT_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
TABLE_COUNTS = {
    "pdgparticle": 1170,
    "pdgid": 450,
    "pdgitem": 3270,
    "pdgitem_map": 1341,
    "pdgdoc": 71,
}
INPUT_NAMES = (
    "entity_register.json",
    "entity_register_notes.md",
    "nuclear_archive/nubase_4.mas20.txt",
    "nuclear_archive/schema_header.txt",
    "nuclear_archive/column_schema.json",
    "nuclear_archive/source_metadata.json",
    "nuclear_archive/license_attribution.md",
    "nuclear_archive/archive_counts.json",
    "nuclear_archive/README.md",
    "particle_archive/pdg2026_identity_archive.json",
    "particle_archive/pdg2026_identity_metadata.json",
    "particle_archive/README.md",
)
FONT_SIZE = 9.0
LEADING = 11.7
PAGE_WIDTH = 612.0
PAGE_HEIGHT = 792.0
MARGIN = 48.0
TEXT_WIDTH = PAGE_WIDTH - 2 * MARGIN
TOP = PAGE_HEIGHT - 60.0
BOTTOM = 48.0
BODY_FONT = "IdentityMono"


def require(condition: bool, message: str) -> None:
    """Use explicit checks: optimized Python must not disable validation."""
    if not condition:
        raise ValueError(message)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validate_baseline(value: str) -> str:
    """Record a caller-selected full Git object ID, without inventing a match."""
    import re

    require(bool(re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", value)),
            "--baseline-commit must be a full 40- or 64-digit hexadecimal commit ID")
    return value.lower()


def validate_outputs(package_root: Path, output: Path, report: Path,
                     input_paths: list[Path]) -> tuple[Path, Path]:
    """Reject aliases and protected package destinations before any write.

    Explicit outputs may be outside the package. Within the package they must
    be below ignored generated_reports/, never documents/, data/ or tools/.
    resolve() also catches a symlink/junction that redirects an ignored path
    back into a protected source directory.
    """
    package_root = package_root.resolve()
    output, report = output.resolve(), report.resolve()
    inputs = {path.resolve() for path in input_paths}
    require(output != report, "PDF and validation-report paths must be distinct")
    require(output not in inputs and report not in inputs, "An output aliases a read-only input")
    for path in (output, report):
        try:
            relative = path.relative_to(package_root)
        except ValueError:
            pass
        else:
            require(len(relative.parts) > 1 and relative.parts[0] == "generated_reports",
                    "In-package outputs must be below ignored generated_reports/")
        require(not path.exists(), "Output already exists and will not be replaced: " + path.name)
    require(output.suffix.lower() == ".pdf" and report.suffix.lower() == ".json",
            "Select a .pdf output and a .json validation report")
    return output, report


def report_path_label(path: Path, package_root: Path) -> str:
    """Keep private absolute paths out of generated provenance records."""
    try:
        return path.resolve().relative_to(package_root.resolve()).as_posix()
    except ValueError:
        return path.name


def compact(value: Any) -> str:
    # JSON preserves null, empty strings, zero, '?' and compound source strings.
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


@dataclass(frozen=True)
class Record:
    identifier: str
    payload: str
    annotation: str = ""
    raw_columns: bool = False


@dataclass(frozen=True)
class Section:
    key: str
    title: str
    note: str
    records: tuple[Record, ...]


@dataclass
class Bundle:
    files: dict[str, bytes]
    inventory: list[dict[str, Any]]
    register: dict[str, Any]
    nuclear_metadata: dict[str, Any]
    nuclear_schema: dict[str, Any]
    nuclear_counts: dict[str, Any]
    nuclear_rows: tuple[Record, ...]
    particle_archive: dict[str, Any]
    particle_metadata: dict[str, Any]
    checks: dict[str, Any]


def load_bundle(stage: Path) -> Bundle:
    """Validate only the declared dated source selections; never infer existence."""
    data = stage / "data"
    files = {name: (data / name).read_bytes() for name in INPUT_NAMES}
    inventory = [
        {"path": "data/" + name, "bytes": len(files[name]), "sha256": sha256(files[name])}
        for name in INPUT_NAMES
    ]

    def parsed(name: str) -> Any:
        return json.loads(files[name].decode("utf-8"))

    register = parsed("entity_register.json")
    elements = register["elements"]
    categories = register["standard_model_particle_categories"]["records"]
    require([row["atomic_number"] for row in elements] == list(range(1, 139)),
            "Element register must contain the declared ordered 138 label rows")
    statuses = Counter(row["status"] for row in elements)
    require(statuses == {"recognized_element": 118, "hypothetical_placeholder": 20},
            "Recognized/hypothetical element status counts changed")
    require(len(categories) == 17 and len({r["id"] for r in categories}) == 17,
            "Particle vocabulary category identities changed")

    nm = parsed("nuclear_archive/source_metadata.json")
    ns = parsed("nuclear_archive/column_schema.json")
    nc = parsed("nuclear_archive/archive_counts.json")
    raw = files["nuclear_archive/nubase_4.mas20.txt"]
    require(sha256(raw) == nm["source_sha256"] and len(raw) == nm["source_bytes"],
            "NUBASE source bytes/hash do not match the reviewed metadata")
    require(nm["source_edition"] == "NUBASE2020", "Unexpected nuclear edition")
    source_lines = raw.splitlines(keepends=True)
    require(all(line.endswith(b"\n") and b"\r" not in line for line in source_lines),
            "Unexpected NUBASE line endings; retain source rather than normalizing")
    header_count = nm["source_header_line_count"]
    require(header_count == 25 and len(source_lines) == nm["source_line_count"],
            "NUBASE header/line count changed")
    require(b"".join(source_lines[:header_count]) == files["nuclear_archive/schema_header.txt"],
            "NUBASE header copy is not the exact source header")
    fields = ns["fields"]
    require([column for f in fields for column in range(f["start"], f["end"] + 1)]
            == list(range(1, 210)), "NUBASE slices must cover columns 1-209 exactly")

    rows: list[Record] = []
    row_ids: set[str] = set()
    nuclides: set[tuple[int, int]] = set()
    state_counts: Counter[str] = Counter()
    offset = sum(map(len, source_lines[:header_count]))
    overflow = 0
    max_width = 0
    late_rows: list[str] = []
    for number, line in enumerate(source_lines[header_count:], header_count + 1):
        literal = line[:-1].decode("ascii", errors="strict")
        require(len(literal) >= 8, f"Short identity at NUBASE line {number}")
        mass_number = int(literal[0:3])
        atomic_number = int(literal[4:7])
        state_index = literal[7:8]
        require(state_index.isdecimal(), f"Invalid state index at line {number}")
        identity = f"NUBASE2020:Z{atomic_number:03d}:A{mass_number:03d}:S{state_index}"
        require(identity not in row_ids, f"Duplicate nuclear source identity {identity}")
        reconstructed = "".join(literal[f["start"] - 1:f["end"]] for f in fields)
        reconstructed += literal[209:]
        require(reconstructed == literal, f"Raw column reconstruction failed: {identity}")
        annotation = f"line={number} byte={offset} width={len(literal)} suffix={compact(literal[16:17])}"
        rows.append(Record(identity, literal, annotation, raw_columns=True))
        row_ids.add(identity)
        nuclides.add((mass_number, atomic_number))
        state_counts[state_index] += 1
        overflow += len(literal) > 209
        max_width = max(max_width, len(literal))
        if literal[114:118] == "2021":
            late_rows.append(identity)
        offset += len(line)
    require(len(rows) == 5843 == nm["source_state_record_count"] == nc["record_count"],
            "The complete declared NUBASE snapshot must have 5,843 source rows")
    require(len(nuclides) == 3558 == nm["source_unique_A_Z_nuclide_count"],
            "NUBASE unique nuclide count changed")
    require(dict(state_counts) == nc["state_index_counts"], "NUBASE state-index counts changed")
    require(overflow == 2 == nc["overflow_record_count"] and max_width == 217,
            "NUBASE overflow records changed")
    require(late_rows == ["NUBASE2020:Z047:A127:S2"], "Literal 2021 field evidence changed")
    require(offset == len(raw), "NUBASE byte accounting is incomplete")

    pa = parsed("particle_archive/pdg2026_identity_archive.json")
    pm = parsed("particle_archive/pdg2026_identity_metadata.json")
    archive_bytes = files["particle_archive/pdg2026_identity_archive.json"]
    require(sha256(archive_bytes) == pm["archive_sha256"]
            and len(archive_bytes) == pm["archive_bytes"], "PDG selected archive hash/size changed")
    require(pa["source_database_sha256"] == pm["source_download_observation"]["sha256"],
            "PDG source database identity disagreement")
    require(pm["database_release_version_from_official_filename"] == "2026.0",
            "Unexpected PDG release")
    require(set(pa["tables"]) == set(TABLE_COUNTS), "PDG selected table inventory changed")
    for table, count in TABLE_COUNTS.items():
        records = pa["tables"][table]
        require(len(records) == count == pm["diagnostics"]["exported_row_counts"][table],
                f"PDG selected count changed: {table}")
        ids = [row["id"] for row in records]
        require(ids == sorted(ids) and len(set(ids)) == count,
                f"PDG source ID order/uniqueness changed: {table}")
        column_names = [column["name"] for column in pm["source_schema"][table]]
        require(all(list(row) == column_names for row in records),
                f"PDG source columns/order changed: {table}")
        require(all(json.loads(compact(row)) == row for row in records),
                f"PDG JSON values do not round-trip: {table}")
    info_rows = pa["source_database_info_rows"]
    require(len(info_rows) == 10 and len({r["id"] for r in info_rows}) == 10,
            "PDG source metadata rows changed")
    require(Counter(row["data_type"] for row in pa["tables"]["pdgid"])
            == {"PART": 439, "SRCH": 11}, "PDG PART/SRCH selection changed")
    groups = {row["pdgid"] for row in pa["tables"]["pdgid"]}
    charge_groups = {row["pdgid"] for row in pa["tables"]["pdgparticle"]}
    require(charge_groups <= groups and len(groups - charge_groups) == 12,
            "PDG groups without charge-state rows were lost")
    duplicate = [r for r in pa["tables"]["pdgparticle"] if r["name"] == "P_c_cbar(4312)+"]
    require(len(duplicate) == 2 and {r["pdgid"] for r in duplicate} == {"B185", "B205"},
            "The known distinct duplicate-name rows were altered")
    checks = {
        "element_label_rows": 138, "recognized_element_rows": 118,
        "hypothetical_element_rows": 20, "particle_vocabulary_categories": 17,
        "nuclear_source_rows": len(rows), "nuclear_unique_A_Z_pairs": len(nuclides),
        "nuclear_header_lines": header_count, "nuclear_raw_columns_reconstruct": True,
        "nuclear_overflow_rows": overflow, "nuclear_maximum_width": max_width,
        "nuclear_literal_2021_discovery_field_ids": late_rows,
        "pdg_selected_table_rows": dict(TABLE_COUNTS), "pdginfo_rows": len(info_rows),
        "pdg_groups_without_charge_state_rows": 12,
        "pdg_all_selected_columns_and_values_retained": True,
        "physical_existence_assessments_performed": 0,
        "preparation_or_patent_enablement_assessed": False,
    }
    return Bundle(files, inventory, register, nm, ns, nc, tuple(rows), pa, pm, checks)


def make_sections(bundle: Bundle, prepared_date: str, baseline_commit: str) -> tuple[Section, ...]:
    """Include complete source records, schema, attribution and local provenance."""
    register = bundle.register
    categories = register["standard_model_particle_categories"]
    register_metadata = {key: value for key, value in register.items()
                         if key not in {"elements", "standard_model_particle_categories"}}
    register_metadata["standard_model_particle_categories"] = {
        key: value for key, value in categories.items() if key != "records"
    }

    def json_record(identifier: str, value: Any) -> Record:
        return Record(identifier, compact(value))

    def text_record(identifier: str, filename: str) -> Record:
        # JSON string representation keeps source line breaks and unknown text
        # explicit while avoiding ambiguous visual whitespace in the annex.
        return json_record(identifier, bundle.files[filename].decode("utf-8"))

    source_records = tuple(json_record(f"SOURCE:{i:02d}", entry)
                           for i, entry in enumerate(bundle.inventory, 1))
    particle_preamble = {key: value for key, value in bundle.particle_archive.items()
                         if key not in {"tables", "source_database_info_rows"}}
    sections = [
        Section("scope", "Review scope and source identities",
                f"Prepared {prepared_date}; REVIEW, not a filing. Caller-selected baseline reference "
                f"{baseline_commit}; exact source hashes below identify the actual input bytes. "
                "All content is limited to the named "
                "source snapshots and selections. Table membership, codes, placeholders and estimated "
                "properties do not establish existence, discovery, stability, preparation, usable "
                "materials, applicant inventions, or physical/patent enablement. This PDF is a rendered "
                "view, not a byte-exact replacement for the retained source files. No data is truncated.",
                source_records),
        Section("register-context", "Entity vocabulary: scope and source notes",
                "This historical register has 118 recognized element labels, 20 hypothetical placeholders "
                "and 17 particle categories under its stated counting convention; these are different "
                "counting objects from nuclear states and PDG charge-state rows.",
                (json_record("REGISTER:metadata", register_metadata),
                 text_record("REGISTER:notes", "entity_register_notes.md"))),
        Section("elements", "Complete element-label register (138 rows)",
                "Every source field is shown. Z=119-138 remain hypothetical placeholders.",
                tuple(json_record(f"ELEMENT:Z{row['atomic_number']:03d}", row)
                      for row in register["elements"])),
        Section("particle-categories", "Complete particle-category vocabulary (17 rows)",
                "Category counting is defined in the register; categories are not additional discovered species.",
                tuple(json_record("CATEGORY:" + row["id"], row) for row in categories["records"])),
        Section("nuclear-provenance", "NUBASE2020: provenance, chronology and attribution",
                "Paper availability boundary 2020-10-30; ASCII scientific cutoff unknown. Retrieval and "
                "server modification dates are separate. Retain the literal 2021 discovery-year row without "
                "inferring a revised scientific cutoff. Published-work CC BY 3.0 is distinct from the "
                "companion ASCII header, which states a citation but no independent license notice.",
                (json_record("NUBASE:metadata", bundle.nuclear_metadata),
                 text_record("NUBASE:license-evidence", "nuclear_archive/license_attribution.md"),
                 text_record("NUBASE:README", "nuclear_archive/README.md"),
                 json_record("NUBASE:counts", bundle.nuclear_counts))),
        Section("nuclear-schema", "NUBASE2020: exact header and complete raw-column schema",
                "One-based inclusive ASCII byte columns; all gaps, short slices and overflow beyond "
                "column 209 are retained. The # marker qualifies a property estimated from systematics, "
                "not observation status. Indices 3-6 may also label isomers. Bounds and isospin annotations "
                "must not become ordinary error bars; non-exist tokens remain literal source text.",
                (text_record("NUBASE:exact-header", "nuclear_archive/schema_header.txt"),
                 json_record("NUBASE:column-schema", bundle.nuclear_schema))),
        Section("nuclear-rows", "Complete NUBASE2020 snapshot (5,843 source-state rows)",
                "Source order retained. Each card identifies Z, A, source state index, suffix, source line, "
                "zero-based byte offset and actual row width. Cnnn-nnn labels give original one-based "
                "columns; the quoted slices are JSON strings. Decode and join slices without adding "
                "spaces to reconstruct a row. The LF terminator is not printed. No numeric property is "
                "recalculated or interpreted as proof of an observed/usable state. Z=0 includes the free neutron.",
                bundle.nuclear_rows),
        Section("pdg-provenance", "PDG 2026.0: selections, schema and attribution",
                "The selected identity archive retains all columns of its declared rows, including null, "
                "empty string, zero, question marks and repeated names. Publication cutoff 2026-01-15 "
                "is separate from database release/retrieval dates. Source CC BY 4.0 attribution and "
                "modifications are recorded below. No property/decay/measurement archive is added.",
                (json_record("PDG:archive-preamble", particle_preamble),
                 json_record("PDG:metadata", bundle.particle_metadata),
                 text_record("PDG:README", "particle_archive/README.md"))),
        Section("pdginfo", "Complete PDG source metadata rows (10 rows)",
                "The complete source_database_info_rows preamble represents the selected pdginfo table. "
                "Production is a database-release status, not a physical-existence assessment.",
                tuple(json_record(f"PDG2026:pdginfo:{row['id']}", row)
                      for row in bundle.particle_archive["source_database_info_rows"])),
    ]
    for table, count in TABLE_COUNTS.items():
        note = ("All PART and SRCH source rows; other pdgid types are outside this selection. "
                "The 12 groups without charge-state rows remain present."
                if table == "pdgid" else "All rows and columns of this selected source table are present.")
        note += (" IDs are edition/table/source-key qualified. Compact JSON preserves source types and "
                 "values; join visible chunks without adding characters. A row, name, MCID, flag, "
                 "quantum-number string or conjugation code does not certify discovery.")
        sections.append(Section(table, f"Complete selected {table} records ({count:,} rows)", note,
                                tuple(json_record(f"PDG2026:{table}:{row['id']}", row)
                                      for row in bundle.particle_archive["tables"][table])))
    identifiers = [record.identifier for section in sections for record in section.records]
    require(len(identifiers) == len(set(identifiers)), "Annex row identities must be globally unique")
    return tuple(sections)


def choose_font(requested: Path | None) -> Path:
    candidates = [requested] if requested else [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/consola.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf"),
    ]
    for candidate in candidates:
        if candidate is not None and candidate.is_file():
            return candidate.resolve()
    raise ValueError("Supply --mono-font with a Unicode TrueType monospace font; none found")


def register_font(font_path: Path, sections: tuple[Section, ...]) -> dict[str, Any]:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font = TTFont(BODY_FONT, str(font_path))
    characters = set("\n".join(section.title + section.note + "".join(
        record.identifier + record.annotation + record.payload for record in section.records
    ) for section in sections))
    # JSON source strings use literal backslash escapes; generated labels are ASCII.
    missing = sorted(ord(char) for char in characters if char not in "\n\r\t"
                     and ord(char) not in font.face.charWidths)
    require(not missing, f"Font lacks source characters: {missing}")
    pdfmetrics.registerFont(font)
    return {"name": font_path.name, "sha256": sha256(font_path.read_bytes()),
            "body_font_points": FONT_SIZE, "all_source_characters_supported": True}


def wrap_plain(text: str, prefix: str = "", size: float = FONT_SIZE) -> list[str]:
    from reportlab.pdfbase.pdfmetrics import stringWidth

    lines: list[str] = []
    for original in text.split("\n"):
        if not original:
            lines.append(prefix)
            continue
        remaining = original
        while remaining:
            limit = min(len(remaining), 140)
            while limit and stringWidth(prefix + remaining[:limit], BODY_FONT, size) > TEXT_WIDTH:
                limit -= 1
            require(limit > 0, "A source character or prefix exceeds the printable width")
            lines.append(prefix + remaining[:limit])
            remaining = remaining[limit:]
    return lines


def record_lines(record: Record) -> list[str]:
    from reportlab.pdfbase.pdfmetrics import stringWidth

    if not record.raw_columns:
        return wrap_plain(record.payload, "JSON ")
    lines: list[str] = []
    offset = 0
    recovered: list[str] = []
    while offset < len(record.payload):
        count = min(110, len(record.payload) - offset)
        while count:
            prefix = f"C{offset + 1:03d}-{offset + count:03d}: "
            quoted = compact(record.payload[offset:offset + count])
            if stringWidth(prefix + quoted, BODY_FONT, FONT_SIZE) <= TEXT_WIDTH:
                break
            count -= 1
        require(count > 0, "Cannot fit a raw source slice at the minimum font size")
        lines.append(prefix + quoted)
        recovered.append(json.loads(quoted))
        offset += count
    require("".join(recovered) == record.payload, f"Display slices lost source bytes: {record.identifier}")
    return lines


def layout_sections(sections: tuple[Section, ...]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Calculate the complete layout before authoring; no output file is opened."""
    entries: list[dict[str, Any]] = []
    page = 0
    y = TOP
    page_map: dict[str, Any] = {"sections": [], "rows": []}

    def line(text: str, size: float = FONT_SIZE, gap: float = LEADING) -> None:
        nonlocal y
        require(y >= BOTTOM, "Layout crossed the bottom printable boundary")
        entries.append({"page": page, "y": y, "text": text, "size": size})
        y -= gap

    def new_page(section: Section) -> None:
        nonlocal page, y
        page += 1
        y = TOP
        entries.append({"page": page, "section": section.key, "new_page": True})

    for section in sections:
        new_page(section)
        first = page
        entries.append({"page": page, "bookmark": section.key, "title": section.title})
        for title_line in wrap_plain(section.title, size=13.0):
            line(title_line, 13.0, 17.0)
        y -= 5.0
        for text_line in wrap_plain(section.note):
            if y < BOTTOM + LEADING:
                new_page(section)
            line(text_line)
        y -= 11.0
        for ordinal, record in enumerate(section.records, 1):
            header = "ROW " + record.identifier
            annotation = wrap_plain(record.annotation) if record.annotation else []
            body_lines = record_lines(record)
            height = (1 + len(annotation) + len(body_lines)) * LEADING + 5.0
            if y - min(height, 9 * LEADING) < BOTTOM:
                new_page(section)
            record_pages: list[int] = [page]
            if ordinal % 500 == 1 and len(section.records) > 500:
                entries.append({"page": page, "bookmark": f"{section.key}-row-{ordinal}",
                                "title": f"{section.title}: source row {ordinal}", "level": 1})
            line(header)
            for text_line in annotation + body_lines:
                if y < BOTTOM + LEADING:
                    new_page(section)
                    record_pages.append(page)
                    line("CONT " + record.identifier)
                line(text_line)
            y -= 5.0
            page_map["rows"].append({"id": record.identifier, "section": section.key,
                                     "first_page": record_pages[0], "last_page": record_pages[-1],
                                     "payload_lines": len(body_lines)})
        page_map["sections"].append({"key": section.key, "title": section.title,
                                     "first_page": first, "last_page": page,
                                     "printed_record_count": len(section.records)})
    page_map["page_count"] = page
    require(len(page_map["rows"]) == sum(len(section.records) for section in sections),
            "A declared annex record was lost during layout")
    from reportlab.pdfbase.pdfmetrics import stringWidth

    require(all(stringWidth(entry["text"], BODY_FONT, entry["size"]) <= TEXT_WIDTH
                and BOTTOM <= entry["y"] <= TOP for entry in entries if "text" in entry),
            "A source-bearing line exceeds the printable bounds")
    return entries, page_map


def check_unchanged(stage: Path, inventory: list[dict[str, Any]]) -> None:
    for item in inventory:
        current = (stage / item["path"]).read_bytes()
        require(len(current) == item["bytes"] and sha256(current) == item["sha256"],
                "Input changed during this run: " + item["path"])


def author_pdf(path: Path, entries: list[dict[str, Any]], prepared_date: str) -> None:
    from reportlab.pdfgen import canvas

    document = canvas.Canvas(str(path), pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
                             pageCompression=1, invariant=1)
    document.setTitle("Materials identity data annex - complete scoped REVIEW edition")
    document.setSubject("Dated source records; review preparation is not filing or patent enablement")
    document.setAuthor("")
    for entry in entries:
        if entry.get("new_page"):
            if entry["page"] > 1:
                document.showPage()
            document.setFillColorRGB(0.23, 0.27, 0.31)
            document.setFont(BODY_FONT, 8.5)
            document.drawString(MARGIN, PAGE_HEIGHT - 32,
                                "Identity annex | REVIEW | " + entry["section"])
            document.drawString(MARGIN, 25, "Prepared " + prepared_date + " | Not a filing")
            document.drawRightString(PAGE_WIDTH - MARGIN, 25, str(entry["page"]))
        elif "bookmark" in entry:
            document.bookmarkPage(entry["bookmark"])
            document.addOutlineEntry(entry["title"], entry["bookmark"],
                                     level=entry.get("level", 0), closed=False)
        else:
            document.setFillColorRGB(0.05, 0.07, 0.09)
            document.setFont(BODY_FONT, entry["size"])
            document.drawString(MARGIN, entry["y"], entry["text"])
    document.save()


def validate_pdf(path: Path, entries: list[dict[str, Any]], page_map: dict[str, Any]) -> dict[str, Any]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    require(len(reader.pages) == page_map["page_count"], "Authored PDF pagination changed")
    expected_by_page: dict[int, list[str]] = {}
    for entry in entries:
        if "text" in entry:
            expected_by_page.setdefault(entry["page"], []).append(entry["text"])
    observed_ids: list[str] = []
    for number, page in enumerate(reader.pages, 1):
        actual = [line.rstrip() for line in (page.extract_text() or "").splitlines()]
        expected = [line.rstrip() for line in expected_by_page[number]]
        # Cover all source-bearing lines, not just a small sentinel sample.
        # Headers/footers are outside the body sequence and may be interleaved.
        cursor = 0
        for line in actual:
            if cursor < len(expected) and line == expected[cursor]:
                cursor += 1
            if line.startswith("ROW "):
                observed_ids.append(line[4:])
        require(cursor == len(expected), f"PDF extraction lost/changed body content on page {number}")
        require(tuple(round(float(x), 2) for x in page.mediabox[2:])
                == (PAGE_WIDTH, PAGE_HEIGHT), "Unexpected PDF page size")
    expected_ids = [row["id"] for row in page_map["rows"]]
    require(observed_ids == expected_ids, "PDF row identities were lost, duplicated or reordered")
    require(reader.outline, "Section bookmarks are missing")
    return {"page_count": len(reader.pages), "every_printed_body_line_verified": True,
            "every_printed_body_line_within_geometry_bounds": True,
            "ordered_row_id_count": len(observed_ids), "ordered_row_ids_match": True,
            "minimum_body_font_points": FONT_SIZE, "minimum_header_footer_font_points": 8.5,
            "visual_review": "pending; extraction and geometry do not establish visual legibility"}


def remove_owned_output(destination: Path, identity: tuple[int, int]) -> None:
    """Clean up only the file identified by this invocation's exclusive open."""
    try:
        current = destination.stat()
        if (current.st_dev, current.st_ino) == identity:
            destination.unlink()
    except FileNotFoundError:
        pass


def publish_exclusive(source: Path, destination: Path) -> tuple[int, int]:
    """Do not replace a previous review edition or a concurrent writer's output."""
    with destination.open("xb") as target:
        owned = os.fstat(target.fileno())
        try:
            with source.open("rb") as stream:
                shutil.copyfileobj(stream, target)
            target.flush()
            os.fsync(target.fileno())
        except BaseException:
            # Exclusive open succeeded, so this invocation owns the partial
            # output. Close it before unlinking on Windows, and avoid removing
            # a file another process substituted at the same path.
            target.close()
            remove_owned_output(destination, (owned.st_dev, owned.st_ino))
            raise
    return owned.st_dev, owned.st_ino


def publish_outputs_exclusive(pairs: list[tuple[Path, Path]]) -> None:
    """Roll back a failed output set without deleting a substituted file."""
    created: list[tuple[Path, tuple[int, int]]] = []
    try:
        for source, destination in pairs:
            # Capture the opened file's identity, not a later path lookup that
            # could identify another process's replacement instead.
            identity = publish_exclusive(source, destination)
            created.append((destination, identity))
    except BaseException:
        for destination, identity in created:
            remove_owned_output(destination, identity)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", "--stage", dest="package_root", type=Path,
                        default=DEFAULT_PACKAGE_ROOT)
    parser.add_argument("--output", type=Path, help="New PDF path; default generated_reports/pdf/")
    parser.add_argument("--report", type=Path, help="New JSON path; default generated_reports/pdf/")
    parser.add_argument("--prepared-date", required=True,
                        help="Actual review preparation date YYYY-MM-DD; not a filing date")
    parser.add_argument("--baseline-commit", required=True,
                        help="Caller-selected full Git commit ID; source hashes identify exact inputs")
    parser.add_argument("--mono-font", type=Path, help="Optional Unicode TrueType monospace font")
    parser.add_argument("--check", action="store_true", help="Check inputs and complete layout; write no files")
    args = parser.parse_args(argv)
    require(date.fromisoformat(args.prepared_date).isoformat() == args.prepared_date,
            "Preparation date must be an explicit ISO calendar date")
    baseline = validate_baseline(args.baseline_commit)
    stage = args.package_root.resolve()
    generated = stage / "generated_reports/pdf"
    pdf_path, report_path = validate_outputs(
        stage, args.output or generated / "materials_identity_data_review_annex.pdf",
        args.report or generated / "identity_annex_validation.json",
        [stage / "data" / name for name in INPUT_NAMES],
    )
    bundle = load_bundle(stage)
    sections = make_sections(bundle, args.prepared_date, baseline)
    font_metadata = register_font(choose_font(args.mono_font), sections)
    entries, page_map = layout_sections(sections)
    check_unchanged(stage, bundle.inventory)
    summary = {"status": "read-only input/layout checks passed", "checks": bundle.checks,
               "prepared_date": args.prepared_date, "baseline_commit": baseline,
               "baseline_interpretation": "Caller-selected reference; input hashes identify the exact package bytes",
               "estimated_complete_layout_pages": page_map["page_count"],
               "section_pages": page_map["sections"], "font": font_metadata,
               "files_written": 0, "authoring_executed": False}
    if args.check:
        print(json.dumps(summary, ensure_ascii=True, indent=2))
        return 0

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="identity-annex-", dir=pdf_path.parent) as scratch:
        temporary_pdf = Path(scratch) / "annex.pdf"
        author_pdf(temporary_pdf, entries, args.prepared_date)
        validation = validate_pdf(temporary_pdf, entries, page_map)
        check_unchanged(stage, bundle.inventory)
        payload = temporary_pdf.read_bytes()
        report = {"report_version": 1, "prepared_date": args.prepared_date,
                  "baseline_commit": baseline,
                  "baseline_interpretation": "Caller-selected reference; input hashes identify the exact package bytes",
                  "purpose": "Complete declared dated identity selections for REVIEW; not filing or enablement",
                  "inputs": bundle.inventory, "unchanged_input_hashes_after_authoring": True,
                  "source_checks": bundle.checks, "font": font_metadata,
                  "pdf": {"path": report_path_label(pdf_path, stage), "bytes": len(payload),
                          "sha256": sha256(payload), **validation},
                  "page_map": page_map,
                  "scope": "Complete retained register, NUBASE raw snapshot and selected PDG identity tables; "
                           "not entire evaluations, current/future universes, physical observation or preparation",
                  "builder_sha256": sha256(Path(__file__).read_bytes())}
        temporary_report = Path(scratch) / "validation.json"
        temporary_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        publish_outputs_exclusive([(temporary_pdf, pdf_path), (temporary_report, report_path)])
    print(json.dumps({"status": "authored and automatically validated; visual review pending",
                      "pdf": report["pdf"], "validation_report": report_path_label(report_path, stage),
                      "source_checks": bundle.checks}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
