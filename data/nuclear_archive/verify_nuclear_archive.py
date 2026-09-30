"""Independently check the archive against source bytes and documented columns.

Verification logic is independent of the parser's field extraction functions.
When the optional large JSON is absent, the CLI requests an in-memory parser
result, then checks it against original bytes and independently read columns.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_SHA = "1585a5eea86c5e17e90307c7e6e786d060049c4039e392a261ff6db977df9859"
EXPECTED_COUNT = 5843
EXPECTED_STATES = {"0": 3558, "1": 1378, "2": 463, "3": 201, "4": 42,
                   "5": 11, "6": 4, "8": 162, "9": 24}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_numeric(field: dict, expected_raw: str) -> None:
    require(field["raw"] == expected_raw, "Parsed property's raw source slice changed")
    require(field["systematics_marker"] == ("#" in expected_raw), "Systematics flag mismatch")
    if field["kind"] != "numeric":
        return
    text = expected_raw.strip().replace("#", "").strip()
    expected_operator = text[0] if text[:1] in {"<", ">", "~"} else "="
    if expected_operator != "=":
        text = text[1:].strip()
    require(field["operator"] == expected_operator, "Numeric operator mismatch")
    require(Decimal(field["value_decimal"]) == Decimal(text), "Numeric value mismatch")
    require(field["value_decimal"] == text, "Numerical precision/token spelling changed")


def verify_payload(payload: dict, schema: dict, source_bytes: bytes) -> dict:
    require(hashlib.sha256(source_bytes).hexdigest() == EXPECTED_SHA, "Unexpected source SHA256")
    require(payload["source_sha256"] == EXPECTED_SHA, "Archive provenance mismatch")
    text = source_bytes.decode("ascii", errors="strict")
    complete_lines = text.splitlines(keepends=True)
    header = "".join(line for line in complete_lines if line.startswith("#") or not line.strip())
    require((ROOT / "schema_header.txt").read_bytes() == header.encode("ascii"), "Original header preservation mismatch")
    documented_ranges = {
        (int(match[1]), int(match[2]))
        for line in header.splitlines()
        if (match := re.match(r"#\s+(\d+):\s*(\d+)\s", line))
    }
    described_ranges = {(field["start"], field["end"]) for field in schema["fields"]
                        if not field["name"].startswith("unassigned_")}
    require(documented_ranges == described_ranges, "Schema disagrees with original header columns")
    positions = [column for field in schema["fields"] for column in range(field["start"], field["end"] + 1)]
    require(positions == list(range(1, 210)), "Schema gaps/overlaps or column order mismatch")
    source_rows = []
    byte_offset = 0
    for line_number, full_line in enumerate(complete_lines, 1):
        row = full_line.rstrip("\r\n")
        if re.match(r"^\d{3} \d{4} ", row):
            source_rows.append((line_number, byte_offset, row, full_line[len(row):]))
        elif row and not row.startswith("#"):
            raise ValueError(f"Unclassified source row at line {line_number}")
        byte_offset += len(full_line.encode("ascii"))
    states = payload["states"]
    require(len(source_rows) == EXPECTED_COUNT == len(states) == payload["state_count"], "Missing/extra source state")
    identities = set()
    for state, (line_number, offset, raw, ending) in zip(states, source_rows):
        A, Z, index = int(raw[0:3]), int(raw[4:7]), int(raw[7])
        identity = f"NUBASE2020:Z{Z:03}:A{A:03}:S{index}"
        require(state["id"] == identity, "Record identity changed")
        require(identity not in identities, "Duplicate record identity")
        identities.add(identity)
        require((state["A"], state["Z"], state["N"], state["source_state_index"]) == (A, Z, A - Z, index), "A/Z/N/state mismatch")
        require(state["raw_line"] == raw, "Original record altered")
        require((state["source_line"], state["source_byte_offset"], state["source_line_ending"]) == (line_number, offset, ending), "Source location mismatch")
        require(state["source_byte_length"] == len(raw) + len(ending), "Source record byte length mismatch")
        require(source_bytes[offset:offset + state["source_byte_length"]].decode("ascii") == raw + ending, "Source byte lookup mismatch")
        for field in schema["fields"]:
            require(state["raw_fields"][field["name"]] == raw[field["start"] - 1:field["end"]], "Fixed-width source slice mismatch")
        require(state["raw_fields"]["overflow_after_209"] == raw[209:], "Trailing source content lost")
        reconstruction = "".join(state["raw_fields"][field["name"]] for field in schema["fields"]) + state["raw_fields"]["overflow_after_209"]
        require(reconstruction == raw, "Raw fields fail complete character reconstruction")
        for name, value_columns, uncertainty_columns in [
            ("mass_excess", (18, 31), (31, 42)),
            ("excitation_energy", (42, 54), (54, 65)),
        ]:
            check_numeric(state[name]["value"], raw[slice(*value_columns)])
            check_numeric(state[name]["uncertainty"], raw[slice(*uncertainty_columns)])
            require(state[name]["value"]["unit"] == "keV", "Energy unit mismatch")
        check_numeric(state["half_life"]["value"], raw[69:78])
        require(state["half_life"]["value"]["unit"] == (raw[78:80].strip() or None), "Half-life unit changed")
        secondary = state["half_life"]["secondary"]
        require(secondary["raw"] == raw[81:88], "Half-life secondary raw field changed")
        if secondary["kind"] == "auxiliary_bound":
            require(state["half_life"]["reported_uncertainty"] is None, "A bound was incorrectly treated as an error bar")
            require(raw[81:88].strip().startswith(secondary["operator"]), "Secondary bound operator mismatch")
        elif secondary["kind"] == "reported_uncertainty":
            require(state["half_life"]["reported_uncertainty"] == secondary, "Reported numerical uncertainty lost")
            uncertainty_text = raw[81:88].strip().replace("#", "").strip()
            require(secondary["value_decimal"] == uncertainty_text, "Reported uncertainty token changed")
            require(Decimal(secondary["value_decimal"]) == Decimal(uncertainty_text), "Reported uncertainty value changed")
        require(state["spin_parity_isospin"]["raw"] == raw[88:102], "Spin/parity raw field changed")
        require(state["spin_parity_isospin"]["systematics_marker"] == ("#" in raw[88:102]), "Spin systematic flag mismatch")
        require(state["observation_status"] == "not inferred from property markers; requires source review", "Unreviewed existence classification introduced")
        require(state["discovery_year_raw"] == raw[114:118], "Discovery year raw field mismatch")
        expected_year = int(raw[114:118]) if raw[114:118].strip().isdigit() else None
        require(state["discovery_year"] == expected_year, "Reported year changed")
        require(state["decay_and_abundance"]["raw"] == raw[119:209], "Decay text changed")
        original_parts = [part for part in raw[119:209].split(";") if part.strip()]
        require([item["raw"] for item in state["decay_and_abundance"]["items"]] == original_parts, "Decay/abundance item dropped or changed")
    state_counts = dict(sorted(Counter(str(s["source_state_index"]) for s in states).items()))
    require(state_counts == EXPECTED_STATES, "Edition state-index counts mismatch")
    require(len({(s["A"], s["Z"]) for s in states}) == 3558, "Nuclide count mismatch")
    return {"record_count": len(states), "unique_nuclides": 3558, "state_index_counts": state_counts,
            "all_source_rows_accounted_for": True, "all_raw_columns_reconstruct": True}


def sample_checks(payload: dict) -> list[str]:
    by_id = {state["id"]: state for state in payload["states"]}
    sample_ids = []
    neutron = by_id["NUBASE2020:Z000:A001:S0"]
    require((neutron["A"], neutron["Z"], neutron["N"]) == (1, 0, 1), "Free neutron mislabeled as an element")
    require(neutron["half_life"]["value"]["value_decimal"] == "609.8", "Neutron half-life token mismatch")
    sample_ids.append(neutron["id"])
    tc99m = by_id["NUBASE2020:Z043:A099:S1"]
    require(tc99m["source_state_symbol"] == "m", "Isomer suffix changed")
    require(tc99m["excitation_energy"]["value"]["value_decimal"] == "142.6836", "Isomer excitation token mismatch")
    require(tc99m["half_life"]["reported_uncertainty"]["value_decimal"] == "0.0002", "Isomer half-life uncertainty changed")
    sample_ids.append(tc99m["id"])
    hydrogen7 = by_id["NUBASE2020:Z001:A007:S0"]
    require(hydrogen7["mass_excess"]["value"]["systematics_marker"], "Estimated mass flag lost")
    require(hydrogen7["discovery_year"] == 2003, "Known reported discovery year lost")
    sample_ids.append(hydrogen7["id"])
    boron18 = by_id["NUBASE2020:Z005:A018:S0"]
    require(boron18["half_life"]["secondary"]["kind"] == "auxiliary_bound", "Secondary bound misclassified")
    require((boron18["half_life"]["secondary"]["operator"], boron18["half_life"]["secondary"]["value_decimal"],
             boron18["half_life"]["secondary"]["unit"]) == ("<", "26", "ns"), "Bound operator/value/unit changed")
    sample_ids.append(boron18["id"])
    silver127n = by_id["NUBASE2020:Z047:A127:S2"]
    require((silver127n["source_line"], silver127n["source_byte_offset"], silver127n["discovery_year_raw"]) == (2442, 318061, "2021"), "2021 source row provenance mismatch")
    sample_ids.append(silver127n["id"])
    return sample_ids


def negative_checks(payload: dict, schema: dict, source_bytes: bytes) -> list[str]:
    cases = []
    # Each mutation is rejected before publication; the saved archive is untouched.
    edits = [
        ("missing state", lambda p: p["states"].pop()),
        ("altered source hash", lambda p: p.update(source_sha256="0" * 64)),
        ("altered identity", lambda p: p["states"][0].update(id="invented")),
        ("lost raw field", lambda p: p["states"][0]["raw_fields"].update(mass_excess="")),
        ("false observation classification", lambda p: p["states"][0].update(observation_status="observed")),
    ]
    for description, mutate in edits:
        changed = copy.deepcopy(payload)
        mutate(changed)
        try:
            verify_payload(changed, schema, source_bytes)
        except ValueError:
            cases.append(description)
        else:
            raise ValueError(f"Verifier accepted deliberate defect: {description}")
    changed = copy.deepcopy(payload)
    bound_record = next(s for s in changed["states"] if s["id"] == "NUBASE2020:Z005:A018:S0")
    bound_record["half_life"]["reported_uncertainty"] = bound_record["half_life"]["secondary"]
    try:
        verify_payload(changed, schema, source_bytes)
    except ValueError:
        cases.append("bound presented as uncertainty")
    else:
        raise ValueError("Verifier accepted a bound as an error bar")
    return cases


def main() -> None:
    source_bytes = (ROOT / "nubase_4.mas20.txt").read_bytes()
    normalized_path = ROOT / "nuclear_states.json"
    if normalized_path.exists():
        payload = json.loads(normalized_path.read_text(encoding="utf-8"))
    else:
        from parse_nubase import parse_snapshot
        payload, _, _, _ = parse_snapshot()
    schema = json.loads((ROOT / "column_schema.json").read_text(encoding="utf-8"))
    report = verify_payload(payload, schema, source_bytes)
    report["manual_sample_ids"] = sample_checks(payload)
    report["deliberate_defects_rejected"] = negative_checks(payload, schema, source_bytes)
    report["source_bytes"] = len(source_bytes)
    report["source_sha256"] = EXPECTED_SHA
    report["result"] = "pass"
    report["scope"] = "faithful dated ASCII archive and conservative parsing, not physical enablement or current/future completeness"
    (ROOT / "verification_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"result": report["result"], "records": report["record_count"],
                      "negative_checks": len(report["deliberate_defects_rejected"])}))


if __name__ == "__main__":
    main()
