"""Archive every NUBASE2020 ASCII record without promoting estimates to observations.

The upstream bytes and fixed-width fields are authoritative. Parsed numbers remain
decimal strings: this archive does not round them or convert compact uncertainties.
Run from any directory; outputs are written next to this script.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "nubase_4.mas20.txt"
SOURCE_URL = "https://www-nds.iaea.org/amdc/ame2020/nubase_4.mas20.txt"
EXPECTED_SOURCE_SHA256 = "1585a5eea86c5e17e90307c7e6e786d060049c4039e392a261ff6db977df9859"

# One-based inclusive columns come from the actual downloaded file's header.
# Unassigned spans are retained as fields so no character is silently discarded.
COLUMNS = [
    ("mass_number", 1, 3, "Mass number"),
    ("unassigned_004", 4, 4, "Unassigned column"),
    ("atomic_number_and_state", 5, 8, "Atomic number and edition-specific state index"),
    ("unassigned_009_011", 9, 11, "Unassigned columns"),
    ("mass_and_element_label", 12, 16, "Mass number and element label"),
    ("state_symbol", 17, 17, "Edition-specific state suffix"),
    ("unassigned_018", 18, 18, "Unassigned column"),
    ("mass_excess", 19, 31, "Mass excess in keV"),
    ("mass_excess_uncertainty", 32, 42, "Mass excess uncertainty in keV"),
    ("excitation_energy", 43, 54, "Excitation energy in keV or source text"),
    ("excitation_energy_uncertainty", 55, 65, "Excitation energy uncertainty in keV"),
    ("excitation_origin", 66, 67, "Origin of excitation energy"),
    ("ordering_uncertainty", 68, 68, "Ground/isomer ordering uncertainty flag"),
    ("ordering_reversal", 69, 69, "Ordering reversal relative to ENSDF flag"),
    ("half_life", 70, 78, "Half-life value or source category"),
    ("half_life_unit", 79, 80, "Source half-life unit"),
    ("unassigned_081", 81, 81, "Unassigned column"),
    ("half_life_secondary", 82, 88, "Documented dT field; also bounds or annotations in actual rows"),
    ("spin_parity_isospin", 89, 102, "Spin, parity, direct measurement/systematics flags, isospin"),
    ("ensdf_update_year", 103, 104, "Source two-digit ENSDF update year"),
    ("unassigned_105_114", 105, 114, "Unassigned columns"),
    ("discovery_year", 115, 118, "Reported discovery year"),
    ("unassigned_119", 119, 119, "Unassigned column"),
    ("decay_modes_intensities", 120, 209, "Decay modes, intensities/uncertainties, isotopic abundance in percent"),
]

NUMBER = re.compile(r"^([<>~]?)\s*([+-]?\d+(?:\.\d*)?(?:[Ee][+-]?\d+)?)\s*(#?)$")
BOUND_WITH_UNIT = re.compile(r"^([<>~])\s*([+-]?\d+(?:\.\d*)?)\s*(#?)\s*([A-Za-z]+)$")
DECAY_ITEM = re.compile(r"^([^=<>~?]+?)([=<>~?])(.*)$")
ISOSPIN = re.compile(r"T\s*=\s*([^ ]+)")


def token(raw: str, unit: str | None = None) -> dict:
    """Parse only an unambiguous complete token; never force unknown source text."""
    stripped = raw.strip()
    result = {
        "raw": raw,
        "text": stripped,
        "operator": None,
        "value_decimal": None,
        "unit": unit,
        "systematics_marker": "#" in raw,
        "kind": "missing" if not stripped else "unparsed_text",
    }
    match = NUMBER.fullmatch(stripped)
    if match:
        result.update(kind="numeric", operator=match[1] or "=", value_decimal=match[2])
    elif stripped in {"stbl", "p-unst", "non-exist"}:
        result.update(kind="source_category", category=stripped)
    return result


def half_life_secondary(raw: str, primary_unit: str) -> dict:
    """A bound in the nominal dT columns is not a numerical error bar."""
    parsed = token(raw, primary_unit or None)
    if parsed["kind"] == "numeric":
        parsed["kind"] = "reported_uncertainty"
        parsed["uncertainty_convention"] = "source token; not rescaled"
    bound = BOUND_WITH_UNIT.fullmatch(raw.strip())
    if bound:
        parsed.update(
            kind="auxiliary_bound",
            operator=bound[1],
            value_decimal=bound[2],
            unit=bound[4],
            systematics_marker=bool(bound[3]),
        )
    elif raw.strip().startswith("T="):
        parsed.update(kind="isospin_annotation", unit=None)
    return parsed


def decay_items(raw: str) -> list[dict]:
    """Keep compact branch/abundance uncertainty as a token, without rescaling."""
    result = []
    for part in raw.split(";"):
        stripped = part.strip()
        if not stripped:
            continue
        item = {"raw": part, "mode": None, "operator": None, "value_decimal": None,
                "uncertainty_token": None, "unit": "%", "systematics_marker": "#" in part,
                "kind": "unparsed_text"}
        match = DECAY_ITEM.fullmatch(stripped)
        if match:
            mode, operator, payload = match.groups()
            item.update(mode=mode.strip(), operator=operator)
            # Square-bracket branch assignments and extra operators remain raw.
            pieces = payload.strip().split()
            first = token(pieces[0]) if pieces else None
            if first and first["kind"] == "numeric" and first["operator"] == "=":
                item.update(kind="numeric_with_reported_operator", value_decimal=first["value_decimal"])
                if len(pieces) == 2:
                    item["uncertainty_token"] = pieces[1]
                elif len(pieces) > 2:
                    item["kind"] = "partially_parsed_text"
            elif operator == "?":
                item["kind"] = "source_question_marker"
            else:
                item["kind"] = "partially_parsed_text"
        result.append(item)
    return result


def parse_snapshot() -> tuple[dict, dict, dict, bytes]:
    """Return the complete archive in memory, with no writes or network requests."""
    source_bytes = SOURCE.read_bytes()
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    if source_sha != EXPECTED_SOURCE_SHA256:
        raise ValueError("The downloaded source differs from the reviewed snapshot; inspect before rebuilding")
    text = source_bytes.decode("ascii", errors="strict")
    source_lines = text.splitlines(keepends=True)
    header = []
    states = []
    offset = 0
    for line_number, complete_line in enumerate(source_lines, 1):
        raw_line = complete_line.rstrip("\r\n")
        ending = complete_line[len(raw_line):]
        if raw_line.startswith("#") or not raw_line:
            header.append(complete_line)
            offset += len(complete_line)
            continue
        if not re.fullmatch(r"\d{3} \d{4} .*", raw_line):
            raise ValueError(f"Unexpected record layout at source line {line_number}")
        fields = {name: raw_line[start - 1:end] for name, start, end, _ in COLUMNS}
        fields["overflow_after_209"] = raw_line[209:]
        if "".join(fields.values()) != raw_line:
            raise ValueError(f"Raw field reconstruction failed at line {line_number}")
        mass_number = int(raw_line[0:3])
        atomic_number = int(raw_line[4:7])
        state_index = int(raw_line[7])
        if mass_number < atomic_number:
            raise ValueError(f"Invalid neutron count at line {line_number}")
        unit = fields["half_life_unit"].strip()
        spin = fields["spin_parity_isospin"]
        secondary = half_life_secondary(fields["half_life_secondary"], unit)
        record = {
            "id": f"NUBASE2020:Z{atomic_number:03}:A{mass_number:03}:S{state_index}",
            "A": mass_number,
            "Z": atomic_number,
            "N": mass_number - atomic_number,
            "source_state_index": state_index,
            "source_state_symbol": fields["state_symbol"].strip() or None,
            "label": (fields["mass_and_element_label"] + fields["state_symbol"]).strip(),
            "identity_scope": "edition-specific nucleus/state record; not an elemental mixture",
            "observation_status": "not inferred from property markers; requires source review",
            "source_line": line_number,
            "source_byte_offset": offset,
            "source_byte_length": len(complete_line),
            "source_line_ending": ending,
            "raw_line": raw_line,
            "raw_fields": fields,
            "mass_excess": {
                "value": token(fields["mass_excess"], "keV"),
                "uncertainty": token(fields["mass_excess_uncertainty"], "keV"),
            },
            "excitation_energy": {
                "value": token(fields["excitation_energy"], "keV"),
                "uncertainty": token(fields["excitation_energy_uncertainty"], "keV"),
                "origin_raw": fields["excitation_origin"],
                "ordering_uncertain": fields["ordering_uncertainty"] == "*",
                "ordering_reversed_relative_to_ensdf": fields["ordering_reversal"] == "&",
            },
            "half_life": {
                "value": token(fields["half_life"], unit or None),
                "secondary": secondary,
                "reported_uncertainty": secondary if secondary["kind"] == "reported_uncertainty" else None,
            },
            "spin_parity_isospin": {
                "raw": spin,
                "direct_measurement_marker": "*" in spin,
                "systematics_marker": "#" in spin,
                "isospin_tokens": ISOSPIN.findall(spin),
                "semantic_spin_parity_parse": "not attempted",
            },
            "ensdf_update_year_raw": fields["ensdf_update_year"],
            "discovery_year_raw": fields["discovery_year"],
            "discovery_year": int(fields["discovery_year"]) if fields["discovery_year"].strip().isdigit() else None,
            "decay_and_abundance": {
                "raw": fields["decay_modes_intensities"],
                "items": decay_items(fields["decay_modes_intensities"]),
                "uncertainty_convention": "compact source token; no automatic last-digit rescaling",
            },
        }
        states.append(record)
        offset += len(complete_line)
    if offset != len(source_bytes):
        raise ValueError("Source byte offsets do not cover the whole downloaded file")
    if len(states) != 5843 or len({s["id"] for s in states}) != 5843:
        raise ValueError("State identity or reviewed edition count mismatch")
    schema = {
        "schema_version": 1,
        "source_format": "NUBASE2020 nubase_4.mas20.txt header",
        "column_convention": "one-based inclusive ASCII byte columns",
        "fields": [{"name": n, "start": a, "end": b, "description": d}
                   for n, a, b, d in COLUMNS],
        "overflow_policy": "preserve every byte after documented column 209 without inventing a meaning",
        "trailing_short_record_policy": "preserve actual slices; never pad the source raw record",
        "state_index_policy": "retain source index and symbol; index 3-6 can also designate isomers; do not infer state type from index alone",
        "estimation_policy": "a # marks a systematics-derived property, not whether the nucleus/state was observed",
        "uncertainty_policy": "raw, operator, numerical token and unit are distinct; secondary half-life bounds are not error bars",
    }
    archive = {
        "schema_version": 1,
        "source_edition": "NUBASE2020",
        "source_file": SOURCE.name,
        "source_url": SOURCE_URL,
        "source_sha256": source_sha,
        "state_count": len(states),
        "states": states,
    }
    counts = {
        "record_count": len(states),
        "unique_nuclide_count": len({(s["A"], s["Z"]) for s in states}),
        "state_index_counts": dict(sorted(Counter(str(s["source_state_index"]) for s in states).items())),
        "minimum_Z": min(s["Z"] for s in states),
        "maximum_Z": max(s["Z"] for s in states),
        "maximum_record_width": max(len(s["raw_line"]) for s in states),
        "overflow_record_count": sum(bool(s["raw_fields"]["overflow_after_209"]) for s in states),
        "discovery_year_maximum": max(s["discovery_year"] for s in states if s["discovery_year"] is not None),
        "discovery_year_2021_records": [{"id": s["id"], "source_line": s["source_line"], "source_byte_offset": s["source_byte_offset"],
            "field_columns": [115, 118], "field_raw": s["discovery_year_raw"], "raw_line": s["raw_line"]}
            for s in states if s["discovery_year"] == 2021],
        "excitation_non_exist_token_count": sum(s["excitation_energy"]["value"].get("category") == "non-exist" for s in states),
        "half_life_secondary_kind_counts": dict(sorted(Counter(s["half_life"]["secondary"]["kind"] for s in states).items())),
    }
    return archive, schema, counts, "".join(header).encode("ascii")


def build() -> None:
    archive, schema, counts, original_header = parse_snapshot()
    (ROOT / "schema_header.txt").write_bytes(original_header)
    (ROOT / "column_schema.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8", newline="\n")
    # This optional generated view is large. Raw source plus parser suffice for
    # portable offline reconstruction; a public package need not duplicate it.
    (ROOT / "nuclear_states.json").write_text(json.dumps(archive, separators=(",", ":"), ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "archive_counts.json").write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"records": len(archive["states"]), "source_bytes": SOURCE.stat().st_size, "source_sha256": archive["source_sha256"],
                     "normalized_json_bytes": (ROOT / "nuclear_states.json").stat().st_size,
                     "discovery_2021_count": len(counts["discovery_year_2021_records"])}))


if __name__ == "__main__":
    build()
