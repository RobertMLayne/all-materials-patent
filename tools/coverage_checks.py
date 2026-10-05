"""Verify the later coverage exhibit without writes, network or PDF dependencies.

Exact calculations and source/claim relationships are checked independently of
the composition modules. Passing checks do not establish a physical embodiment,
an empirical property, filing, inventorship or legal effect.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from math import lcm
from pathlib import Path, PurePosixPath
import re

REPORT = "data/material_state_process_coverage_2026-10-04.json"
DOCUMENT = "documents/material_state_process_coverage_2026-10-04.md"
APP = "documents/provisional_application_substantive_review_2026-10-03.md"
APP_SHA256 = "5ccb71d5448a07f41041302f4be2b962e9a214c83b2f92e39ed642a3b8b1ec23"
CLAIMS = "data/claim_review_2026-10-03.json"
ROWS = {"DOM", "ALLOY", "GLASS", "OXIDE-B", "OXIDE-RED", "MOLECULAR", "POLYMER",
        "HYDROGEL", "CNT-COMPOSITE", "ELECTRICAL", "UNARY", "SPATIAL", "NUCLEAR",
        "PARTICLE", "RECORD"}
DIMENSIONS = {"composition", "structure", "state", "process", "property", "remaining_physical_support"}
LABELS = {"ESTABLISHED", "CALCULATED", "PROPOSED", "UNSUPPORTED"}
PROPERTIES = {"mechanical", "electrical", "thermal", "optical", "magnetic", "chemical_stability",
              "catalytic", "diffusion_sorption_permeability_wetting", "radiation", "biological",
              "release_recovery"}


def _require(condition, message):
    if not condition:
        raise ValueError(f"Coverage exhibit: {message}")


def _fraction(value):
    _require(type(value) in (int, str), "inexact or boolean arithmetic input")
    return Fraction(value)


def _vector(values):
    return tuple(_fraction(value) for value in values)


def _path(root, relative):
    _require(isinstance(relative, str) and "\\" not in relative, "invalid relative source path")
    p = PurePosixPath(relative)
    _require(not p.is_absolute() and ":" not in relative and ".." not in p.parts,
             "source path escapes the package")
    return root / relative


def _json(root, relative):
    return json.loads(_path(root, relative).read_text(encoding="utf-8"))


def _pointer(value, pointer):
    if not pointer:
        return value
    _require(pointer.startswith("/"), "invalid JSON source pointer")
    for token in pointer[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def _profile(values):
    row = _vector(values)
    _require(bool(row) and all(v > 0 for v in row) and sum(row) == 1, "positive target does not normalize")
    return row


def _check_data(root, data):
    _require(data.get("schema_version") == 1 and data.get("operative_application") == APP,
             "schema/application identity differs")
    _require(data.get("application_paragraph_count") == 99 and data.get("unchanged_candidate_claim_count") == 199,
             "application/claim counts differ")
    _require(hashlib.sha256((root / APP).read_bytes()).hexdigest() == APP_SHA256,
             "preserved 3 October application bytes differ")
    for key in ("applicant_physical_experiments_performed", "applicant_physical_experiments_planned",
                "filing_asserted", "physical_enablement_certified", "universal_blocking_established"):
        _require(data.get(key) is False, f"unsupported outcome promoted: {key}")
    _require("separate review content" in data["edition_boundary"] and "not retroactively adopted" in data["edition_boundary"],
             "later exhibit boundary missing")
    app = (root / APP).read_text(encoding="utf-8")
    paragraphs = set(re.findall(r"^\[(\d{4})\] ", app, re.M))
    claims = {c["claim_number"]: c for c in _json(root, CLAIMS)["claims"]}
    manifest = {r["path"]: r["sha256"] for r in data["source_manifest"]}
    _require(len(manifest) == len(data["source_manifest"]), "duplicate source manifest row")
    for path, recorded in manifest.items():
        _require(hashlib.sha256(_path(root, path).read_bytes()).hexdigest() == recorded,
                 f"source bytes differ: {path}")
    source_pointers = 0
    for item in data["coverage_rows"] + data["later_worked_records"]:
        _require(item["application_paragraphs"] and set(item["application_paragraphs"]) <= paragraphs,
                 "missing application locator")
        for reference in item["source_records"]:
            path = reference["path"]
            _require(path in manifest, "source reference lacks a fingerprint")
            if reference["json_pointer"]:
                _pointer(_json(root, path), reference["json_pointer"])
                source_pointers += 1
    rows = data["coverage_rows"]
    _require({r["id"] for r in rows} == ROWS and len(rows) == len(ROWS), "material/record row inventory differs")
    electrical = next(row for row in rows if row["id"] == "ELECTRICAL")
    stock_source = _json(root, "data/electrical_candidate_record_review_2026-09-30.json")["composition"]
    _require(electrical["family"] == "SWCNT/PEDOT:PSS/PS and electrical loading"
             and "PS_latex_stock_dry_category" in stock_source["support"],
             "electrical matrix identity differs from the source PS category")
    for row in rows:
        _require(set(row["dimensions"]) == DIMENSIONS, "missing coverage dimension")
        for value in row["dimensions"].values():
            _require(value["evidence_status"] in LABELS and bool(value["description"]), "missing field evidence/description")
        _require(row["dimensions"]["remaining_physical_support"]["evidence_status"] == "UNSUPPORTED"
                 and row["applicant_physical_outcome"] == "UNSUPPORTED", "physical coverage gap promoted")
        _require(row["physical_experiments_performed"] is False and row["physical_experiments_planned"] is False,
                 "unperformed/unplanned status differs")
        _require(set(row["illustrative_claims"]) <= set(claims), "invalid illustrative claim number")
    alignment = data["claim_alignment"]
    _require([r["claim_number"] for r in alignment] == list(range(1, 200)), "199-claim alignment inventory differs")
    own = {r["claim_number"]: set(r["own_coverage_rows"]) for r in alignment}
    for r in alignment:
        c = claims[r["claim_number"]]
        _require(r["exact_text_sha256"] == hashlib.sha256(c["exact_text"].encode()).hexdigest(), "exact claim text hash differs")
        for key in ("direct_dependencies", "transitive_dependencies"):
            _require(r[key] == c[key], "claim parent graph differs")
        _require(r["application_paragraphs"] == c["complete_combination_mapped_paragraphs"], "claim support locators differ")
        inherited = {row for n in c["transitive_dependencies"] for row in own[n]}
        _require(set(r["inherited_coverage_rows"]) == inherited, "inherited coverage rows differ")
        _require(bool(own[r["claim_number"]]) and own[r["claim_number"]] <= ROWS, "claim lacks valid coverage association")
        _require(r["complete_physical_feature_match_verified"] is False and bool(r["coverage_qualification"]),
                 "claim alignment promoted to physical proof")
    props = data["property_dimension_accounting"]
    _require({p["id"] for p in props} == PROPERTIES and len(props) == len(PROPERTIES), "property category inventory differs")
    for p in props:
        _require(set(p["paragraphs"]) <= paragraphs and set(p["rows"]) <= ROWS and p["candidate_outcome"] == "UNSUPPORTED",
                 "property coverage locators/outcome differ")

    records = {w["id"]: w for w in data["later_worked_records"]}
    _require(set(records) == {"W-U", "W-L", "W-R", "W-P"} and len(records) == len(data["later_worked_records"]),
             "later workflow inventory differs")
    for w in records.values():
        _require(w["candidate_outcome"] == "UNSUPPORTED" and w["physical_experiments_performed"] is False
                 and w["physical_experiments_planned"] is False, "worked physical outcome promoted")
        for key in ("structure", "state", "preparation", "measurement", "property"):
            _require(w[key]["evidence_status"] in LABELS and bool(w[key]["description"]), "worked field lacks evidence status")
    unary = records["W-U"]["composition"]
    _require(unary["support"] == [6] and unary["atoms"] == 7 and unary["counts"] == [7], "unary inventory differs")
    _require(_profile(unary["fractions"]) == (Fraction(1),) and unary["primitive_denominator"] == 1, "unary count ratio differs")
    carbon = _pointer(_json(root, "data/entity_register.json"), "/elements/5")
    _require(carbon["atomic_number"] == 6 and carbon["status"] == "recognized_element", "unary identity attribution differs")

    spatial = records["W-L"]["composition"]
    _require(spatial["support"] == [6, 8] and len(spatial["regions"]) == 2, "spatial support/dimensions differ")
    counts = [Fraction(0), Fraction(0)]
    local_profiles = []
    for r in spatial["regions"]:
        volume, density = _fraction(r["anonymous_volume"]), _fraction(r["anonymous_number_density"])
        _require(volume > 0 and density > 0, "spatial model has nonpositive volume/density")
        local = _vector(r["local_counts"])
        _require(len(local) == 2 and all(n >= 0 and n.denominator == 1 for n in local)
                 and sum(local) == volume * density, "spatial count/density relation differs")
        _require(_vector(r["local_atomic"]) == tuple(n / sum(local) for n in local), "local atomic profile differs")
        local_profiles.append(_vector(r["local_atomic"]))
        counts = [a + b for a, b in zip(counts, local, strict=True)]
    total = sum(counts)
    global_profile = tuple(n / total for n in counts)
    _require(_vector(spatial["global_counts"]) == tuple(counts) and spatial["total_atoms"] == total,
             "global spatial count inventory differs")
    _require(_profile(spatial["global_atomic"]) == global_profile == (Fraction(3, 5), Fraction(2, 5)),
             "density-weighted global ratio differs")
    mean = tuple(sum(p[i] for p in local_profiles) / len(local_profiles) for i in range(2))
    _require(_vector(spatial["unweighted_local_mean"]) == mean and mean != global_profile,
             "unequal-region counterexample differs")
    _require(spatial["primitive_denominator"] == lcm(*(v.denominator for v in global_profile))
             and spatial["orders"] == [["A", "B"], ["B", "A"]], "spatial ordering/denominator differs")

    procedure = records["W-R"]["composition"]
    export = procedure["finite_export"]
    _require(export["max_denominator"] == 4 and export["infinite_domain_completed"] is False,
             "finite prefix promoted or budget differs")
    # Separator positions generate integer compositions independently of the
    # recursive target generator; reduced-vector sets remove representations.
    expected = set()
    for q in range(1, 5):
        for cuts in combinations(range(1, q), 1):
            expected.add((Fraction(cuts[0], q), Fraction(q - cuts[0], q)))
    prefix = [_profile(row) for row in export["primitive_vectors"]]
    _require(len(prefix) == len(expected) and set(prefix) == expected, "primitive bounded prefix differs")
    queries = {q["id"]: q for q in procedure["queries"]}
    _require(set(queries) == {"Q-thirds", "Q-zero-boundary"}, "query inventory differs")
    thirds = queries["Q-thirds"]
    _require(thirds["bounds"] == [["1/3", "1/3"], ["2/3", "2/3"]], "thirds bounds differ")
    x = _profile(thirds["assigned_positive_target"])
    _require(x == (Fraction(1, 3), Fraction(2, 3)) and thirds["positive_rational_feasible"] is True
             and thirds["complete_positive_record"] is True, "accepted positive record differs")
    _require(tuple(thirds["integer_counts"]) == tuple(thirds["inventory_atoms"] * v for v in x)
             and thirds["on_D_10_pow_19_grid"] is all((10**19 * v).denominator == 1 for v in x),
             "thirds atomic/grid compatibility differs")
    rejected = queries["Q-zero-boundary"]
    _require(rejected["bounds"] == [["0", "0"], ["1", "1"]]
             and rejected["nonnegative_witness"] == ["0", "1"]
             and rejected["positive_rational_feasible"] is False and rejected["assigned_positive_target"] is None
             and rejected["complete_positive_record"] is False
             and rejected["lower_support_boundary"] == {"support": [8], "fractions": ["1"]},
             "zero-only support rejection/lower-support boundary differs")

    particle = records["W-P"]
    identity = particle["identity"]
    source_row = _pointer(_json(root, "data/particle_archive/pdg2026_identity_archive.json"), "/tables/pdgparticle/0")
    _require(identity["source_edition"] == "PDG 2026.0" and identity["source_table"] == "pdgparticle"
             and identity["source_primary_key"] == source_row["id"] == 1
             and identity["pdgid"] == source_row["pdgid"] and identity["source_name"] == source_row["name"]
             and identity["cc_type"] == source_row["cc_type"] and identity["mcid"] == source_row["mcid"],
             "particle source identity join differs")
    _require(identity["physical_existence_status_from_identity_export"] is None
             and identity["source_property_mass_or_lifetime_available_in_export"] is False,
             "identity export promoted to discovery/property evidence")
    _require(identity["source_quantum_numbers"] == {key: value for key, value in source_row.items()
                                                   if key.startswith("quantum_")},
             "source quantum-number text/nulls differ")
    p = particle["composition"]
    _require(p["host_support"] == [6] and p["host_atom_counts"] == [7] and p["host_atomic"] == ["1"],
             "host atomic inventory differs")
    n, energy = _vector(p["mode_counts"]), _vector(p["anonymous_mode_energies"])
    _require(len(n) == len(energy) == 2 and all(v > 0 and v.denominator == 1 for v in n)
             and all(e > 0 for e in energy), "excitation input domains differ")
    energy_total = sum(count * eps for count, eps in zip(n, energy, strict=True))
    _require(p["excitation_count_total"] == sum(n) and _fraction(p["excitation_energy_total"]) == energy_total,
             "excitation energy/count totals differ")
    _require(_profile(p["excitation_count_shares"]) == tuple(v / sum(n) for v in n)
             and _profile(p["excitation_energy_shares"]) == tuple(count * eps / energy_total for count, eps in zip(n, energy, strict=True)),
             "count versus energy-share accounting differs")
    return {"status": "passed", "coverage_rows": len(rows), "claim_numbers_aligned": len(alignment),
            "source_hashes_checked": len(manifest), "json_source_pointers_checked": source_pointers,
            "property_categories_accounted_for": len(props), "later_worked_records_checked": len(records),
            "bounded_prefix_vectors_checked": len(prefix), "package_files_written": 0,
            "scope": "Selected field relationships, exact arithmetic and evidence boundaries; no physical or legal result certified."}


def check(root: Path) -> dict:
    """Return fresh exhibit verification or raise ValueError; never write files."""
    return _check_data(Path(root), _json(Path(root), REPORT))


def self_test(root: Path) -> dict:
    """Reject meaningful record defects in memory without changing source files."""
    root = Path(root)
    original = _json(root, REPORT)
    defects = [
        ("source_hash", lambda d: d["source_manifest"][0].update(sha256="0" * 64)),
        ("coverage_field", lambda d: d["coverage_rows"][0]["dimensions"].pop("state")),
        ("electrical_family", lambda d: next(row for row in d["coverage_rows"] if row["id"] == "ELECTRICAL").update(family="SWCNT/PEDOT:PSS/PVAc and electrical loading")),
        ("physical_promotion", lambda d: d["coverage_rows"][0].update(applicant_physical_outcome="ESTABLISHED")),
        ("claim_inventory", lambda d: d["claim_alignment"].pop()),
        ("claim_text", lambda d: d["claim_alignment"][0].update(exact_text_sha256="0" * 64)),
        ("unary_ratio", lambda d: d["later_worked_records"][0]["composition"].update(fractions=["1/2"])),
        ("spatial_weight", lambda d: d["later_worked_records"][1]["composition"].update(global_atomic=["1/2", "1/2"])),
        ("prefix_duplicates", lambda d: d["later_worked_records"][2]["composition"]["finite_export"]["primitive_vectors"].append(["1/2", "1/2"])),
        ("positive_rejection", lambda d: d["later_worked_records"][2]["composition"]["queries"][1].update(complete_positive_record=True)),
        ("particle_discovery", lambda d: d["later_worked_records"][3]["identity"].update(physical_existence_status_from_identity_export="discovered")),
        ("particle_unknown", lambda d: d["later_worked_records"][3]["identity"]["source_quantum_numbers"].update(quantum_g="0")),
        ("energy_share", lambda d: d["later_worked_records"][3]["composition"].update(excitation_energy_shares=["3/4", "1/4"])),
        ("property_outcome", lambda d: d["property_dimension_accounting"][0].update(candidate_outcome="ESTABLISHED")),
    ]
    rejected = []
    for name, mutate in defects:
        candidate = deepcopy(original)
        mutate(candidate)
        try:
            _check_data(root, candidate)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError(f"Coverage self-test accepted defect: {name}")
    return {"status": "passed", "in_memory_defects_rejected": len(rejected), "defects": rejected,
            "package_files_written": 0, "scope": "Bounded arithmetic, relation and evidence-boundary regression cases."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    package_root = Path(__file__).resolve().parent.parent
    result = check(package_root)
    if args.self_test:
        result["self_test"] = self_test(package_root)
    print(json.dumps(result, indent=2))
