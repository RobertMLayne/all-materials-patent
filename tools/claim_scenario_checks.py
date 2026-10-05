"""Check the prospective all-199 scenario supplement against preserved sources.

These checks establish document consistency and selected exact calculations.
They do not decide physical enablement, patentability, inventorship or filing.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any


DATA_PATH = "data/claim_scenarios_2026-10-04.json"
GUIDE_PATH = "documents/claim_scenarios_2026-10-04.md"
SPEC_PATH = "documents/provisional_application_substantive_review_2026-10-03.md"
MAP_PATH = "data/claim_support_map_substantive_review_2026-10-03.json"
REVIEW_PATH = "data/claim_review_2026-10-03.json"
PRESERVED_HASHES = {
    SPEC_PATH: "5ccb71d5448a07f41041302f4be2b962e9a214c83b2f92e39ed642a3b8b1ec23",
    MAP_PATH: "325102864ecbe4065d2e3dfa138383dab6a9aa1e84fb09cff2531ddcf4f06b8d",
    REVIEW_PATH: "0a624b5a57e100582cc08f39ad138ff22585ee7afcd20f685e0653c30808a942",
    "documents/provisional_application_theoretical_review_2026-10-01.md":
        "61ffc4ec1aa89d32dcc4cd44d35852a4b315b13d514c2898c4aabf460e3235f7",
}
FALSE_FLAGS = (
    "complete_chronological_novelty_search",
    "final_statutory_determination",
    "full_scope_physical_enablement_established",
    "applicant_physical_experiments_performed",
    "applicant_physical_experiments_planned",
    "universal_blocking_established",
    "filing_asserted",
    "legal_inventorship_confirmed",
    "historical_edition_texts_changed",
)
SCENARIO_TYPES = {"S1", "S2", "S3", "S4"}
PROPORTION_VARIATION_REQUEST_MARKERS = {
    144: "change positive atom-count proportions",
    145: "change atom proportions",
    146: "mass targets consequently change",
    148: "change positive rational target",
    149: "change positive primitive target",
    152: "change the positive atomic target",
    153: "change the positive atomic target",
    154: "change the positive atomic target",
    160: "change x_a from 10/d to 50/d",
    166: "change positive atomic proportions",
    167: "change positive atomic proportions",
    168: "change positive atomic targets",
    172: "change the within-carbon isotope-state population",
    184: "change nominal positive ratios",
}
D = 10**19


def require(condition: bool, message: str) -> None:
    """Keep standalone checks effective even if assertions are disabled."""
    if not condition:
        raise ValueError(message)


def exact_values(values: list[str]) -> list[Fraction]:
    require(all(isinstance(v, str) for v in values), "Exact values must be strings")
    return [Fraction(v) for v in values]


def exact_symbolic(expression: str, parameters: dict[str, Fraction]) -> Fraction:
    """Evaluate only the arithmetic grammar used by qualified mass targets."""
    def visit(node: ast.AST) -> Fraction:
        if isinstance(node, ast.Name):
            require(node.id in parameters, "Unknown symbolic mass parameter")
            return parameters[node.id]
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return Fraction(node.value)
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
        raise ValueError("Unsupported symbolic arithmetic expression")
    return visit(ast.parse(expression, mode="eval").body)


def safe_local(root: Path, value: str) -> Path:
    require(isinstance(value, str) and bool(value), "Empty source path")
    rel = PurePosixPath(value)
    require(
        not rel.is_absolute() and ".." not in rel.parts
        and "\\" not in value and ":" not in value,
        f"Nonportable source path: {value}",
    )
    path = (root / value).resolve()
    require(path.is_relative_to(root.resolve()), f"Source escapes root: {value}")
    return path


def scan_types(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("Binary floating-point value in exact scenario record")
    if isinstance(value, str):
        require(
            not re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]|/Users/|/home/", value),
            "Private absolute path in public scenario record",
        )
    elif isinstance(value, dict):
        for child in value.values():
            scan_types(child)
    elif isinstance(value, list):
        for child in value:
            scan_types(child)


def parse_claims(text: str) -> dict[int, str]:
    claims = {
        int(n): t.strip()
        for n, t in re.findall(
            r"\*\*Claim (\d+)\.\*\* (.*?)(?=\n\n|\Z)", text, re.S
        )
    }
    require(set(claims) == set(range(1, 200)), "Operative claim annex is not 1-199")
    return claims


def dependencies(claims: dict[int, str]) -> tuple[dict[int, list[int]], dict[int, list[int]]]:
    direct: dict[int, list[int]] = {}
    transitive: dict[int, list[int]] = {}
    for n, text in claims.items():
        match = re.match(r"The (?:material|method) of claim (\d+),", text)
        direct[n] = [int(match.group(1))] if match else []
        require(all(p < n for p in direct[n]), f"Forward/circular claim dependency {n}")
        inherited = set(direct[n])
        for parent in direct[n]:
            inherited.update(transitive[parent])
        transitive[n] = sorted(inherited)
    require([n for n in claims if not direct[n]] == [1, 139, 186, 194],
            "Independent claim set changed")
    return direct, transitive


def check_contexts(data: dict[str, Any], paragraph_ids: set[str], root: Path) -> dict[str, int]:
    contexts = data["bounded_contexts"]
    fractions_checked = 0
    for wid, context in contexts.items():
        require(context["id"] == wid, f"Context ID mismatch: {wid}")
        require(context["evidence_label"] == "CALCULATED", f"Context promoted: {wid}")
        require(context["physical_realization_established"] is False,
                f"Physical context promoted: {wid}")
        require(bool(context["qualification"]), f"Missing context scope: {wid}")
        require(set(context["specification_paragraphs"]) <= paragraph_ids,
                f"Unknown context locator: {wid}")
        support = context["support_atomic_numbers"]
        target = exact_values(context["exact_target_fractions"])
        require(support == sorted(set(support)), f"Noncanonical context support: {wid}")
        require(all(1 <= z <= 138 for z in support), f"Unknown element label: {wid}")
        if target:
            require(len(target) == len(support), f"Target dimension mismatch: {wid}")
            require(all(v > 0 for v in target) and sum(target) == 1,
                    f"Not a positive normalized target: {wid}")
            fractions_checked += len(target)
        if "counts" in context:
            counts = [int(v) for v in context["counts"]]
            total = int(context["inventory_N"])
            require(total > 0 and sum(counts) == total, f"Count total mismatch: {wid}")
            require([Fraction(v, total) for v in counts] == target,
                    f"Count/target mismatch: {wid}")
        if "lower" in context:
            lower = exact_values(context["lower"])
            upper = exact_values(context["upper"])
            require(len(lower) == len(upper) == len(target), f"Bound dimensions: {wid}")
            require(all(0 <= lo <= x <= hi <= 1 for lo, x, hi in zip(lower, target, upper)),
                    f"Target outside correlated box: {wid}")
        if "before_exact_target_fractions" in context:
            before = exact_values(context["before_exact_target_fractions"])
            require(len(before) == len(target) == len(support) and
                    all(v > 0 for v in before) and sum(before) == 1 and before != target,
                    f"S2 substitutes representation for actual positive-ratio variation: {wid}")
            if "lower" in context:
                require(all(lo <= x <= hi for lo, x, hi in zip(lower, before, upper)),
                        f"S2 before target fails fixed selected box: {wid}")
            if "endpoint_parameters" in context:
                p = context["endpoint_parameters"]
                denominator = 10**int(p["p"])
                require(0 <= int(p["p"]) <= 19 and
                        [Fraction(int(v), denominator) for v in p["l"]] == lower and
                        [Fraction(int(v), denominator) for v in p["u"]] == upper,
                        f"S2 decimal endpoint accounting mismatch: {wid}")
                if wid == "W-S2-154":
                    require(all(int(upper_endpoint) - int(lower_endpoint) == 1
                                for lower_endpoint, upper_endpoint in zip(p["l"], p["u"])),
                            "S2 claim 154 lost elementary cells")
            if "decade_parameters" in context:
                p = context["decade_parameters"]
                scale = Fraction(10)**(int(p["e"]) - int(p["r"]))
                require([int(j)*scale for j in p["j"]] == lower and
                        [(int(j)+1)*scale for j in p["j"]] == upper,
                        f"S2 decade cell accounting mismatch: {wid}")
            if wid == "W-S2-160":
                denominator = int(context["grid_denominator"])
                require(denominator == D and all((v*D).denominator == 1 for v in before+target),
                        "S2 trace ratio variation left the inherited positive grid")
            if wid == "W-S2-149":
                for phase, expected in (("before", before), ("after", target)):
                    q = int(context[f"{phase}_primitive_q"])
                    nums = [int(v) for v in context[f"{phase}_primitive_n"]]
                    require(q >= len(support) and all(n > 0 for n in nums) and
                            sum(nums) == q and math.gcd(q, *nums) == 1 and
                            [Fraction(n,q) for n in nums] == expected,
                            f"S2 claim 149 lost valid primitive {phase} reduction")
            if wid == "W-S2-184":
                require(Fraction(context["before_target_tolerance"]) > 0 and
                        Fraction(context["after_target_tolerance"]) > 0 and
                        bool(context["sampling_convention"]) and
                        context["tolerance_is_not_validated_measurement_uncertainty"] is True,
                        "S2 target tolerance promoted to validated assay uncertainty")
        if wid == "W-S2-172":
            phases = []
            for phase in ("before", "after"):
                joint = exact_values(context[f"{phase}_joint_coordinates"])
                counts = [int(v) for v in context[f"{phase}_joint_counts"]]
                total = int(context[f"{phase}_inventory_N"])
                require(len(joint) == len(counts) == 3 and all(v > 0 for v in joint) and
                        sum(joint) == 1 and sum(counts) == total and
                        [Fraction(v,total) for v in counts] == joint,
                        f"S2 isotope-state {phase} population/count mismatch")
                require([joint[0]+joint[1],joint[2]] == target,
                        f"S2 isotope-state {phase} variation changes elemental fractions")
                phases.append(joint)
            require(phases[0] != phases[1] and
                    context["state_labels"] == ["C-12 ground", "C-13 ground", "O-16 ground"],
                    "S2 state-ID relabeling substituted for actual state-population variation")
    for k in range(2, 139):
        w = contexts[f"W-K{k:03d}"]
        require(w["support_atomic_numbers"] == list(range(1, k + 1)),
                f"Exact-k witness support changed: {k}")
        require(w["exact_target_fractions"] == [f"1/{k}"] * k,
                f"Exact-k witness fractions changed: {k}")
        require(w["hypothetical_label_minimum"] == max(0, k - 118),
                f"Hypothetical-label count changed: {k}")
        variant = w["same_support_ratio_variant"]
        varied = exact_values(variant["exact_target_fractions"])
        varied_counts = [int(v) for v in variant["counts"]]
        varied_total = int(variant["inventory_N"])
        require(len(varied) == k and all(v > 0 for v in varied) and sum(varied) == 1,
                f"S2 ratio variation changes selected positive support: {k}")
        require(varied != exact_values(w["exact_target_fractions"]) and
                sum(varied_counts) == varied_total and
                [Fraction(v, varied_total) for v in varied_counts] == varied,
                f"S2 same-support ratio/count calculation mismatch: {k}")

    iso = contexts["W-ISO"]
    joint = exact_values(iso["joint_coordinates"])
    require(joint == [Fraction(1, 4), Fraction(1, 4), Fraction(1, 2)],
            "Joint isotope witness changed")
    require(int(iso["inventory_N"]) == 4 and
            [int(v) for v in iso["joint_counts"]] == [1, 1, 2],
            "Joint isotope counts mismatch")
    require(any((2 * v).denominator != 1 for v in joint) and
            all((4 * v).denominator == 1 for v in joint),
            "Joint denominator boundary was lost")

    volume = contexts["W-VOLUME"]
    masses = exact_values(volume["mass_fractions"])
    densities = exact_values(volume["densities"])
    volumes = [m / rho for m, rho in zip(masses, densities)]
    volumes.append(Fraction(volume["void_volume"]))
    require([v / sum(volumes) for v in volumes] ==
            exact_values(volume["volume_fractions_including_void"]),
            "Mass/phase/void volume calculation mismatch")

    layer = contexts["W-LAYER"]
    totals = [int(v) for v in layer["phase_atom_totals"]]
    profiles = [exact_values(v) for v in layer["phase_profiles"]]
    require(all(sum(p) == 1 for p in profiles), "Phase profile normalization mismatch")
    weighted = [sum(total * p[i] for total, p in zip(totals, profiles)) / sum(totals)
                for i in range(2)]
    require(weighted == exact_values(layer["exact_target_fractions"]),
            "Region-count weighted inventory mismatch")
    require(weighted != [sum(p[i] for p in profiles) / 2 for i in range(2)],
            "Unequal region weights no longer distinguish simple average")

    bounds = contexts["W-BOUND"]
    lower = exact_values(bounds["input_lower"])
    upper = exact_values(bounds["input_upper"])
    expected_lower = [lower[i] / (lower[i] + sum(upper[j] for j in range(2) if j != i))
                      for i in range(2)]
    expected_upper = [upper[i] / (upper[i] + sum(lower[j] for j in range(2) if j != i))
                      for i in range(2)]
    require(expected_lower == exact_values(bounds["normalized_lower"]) and
            expected_upper == exact_values(bounds["normalized_upper"]),
            "Normalized deterministic bounds mismatch")

    prefix = contexts["W-PREFIX"]["primitive_tuples"]
    expected_prefix = [(q, n, q - n) for q in range(2, 6) for n in range(1, q)
                       if math.gcd(n, q) == 1]
    require([(int(t["q"]), *[int(n) for n in t["n"]]) for t in prefix] == expected_prefix,
            "Primitive finite prefix mismatch")
    enum = contexts["W-ENUM"]["enumerated_label_statuses"]
    require([v["atomic_number"] for v in enum] == list(range(1, 139)),
            "Unary support enumerator omitted or duplicated a label")
    require(all(v["status"] == ("Recognized" if v["atomic_number"] <= 118
                                else "Hypothetical placeholder") for v in enum),
            "Unary support status promotion")

    positive = contexts["W-POSITIVE"]
    require(exact_values(positive["preliminary"]) == [Fraction(1), Fraction(0)] and
            Fraction(positive["epsilon"]) == Fraction(1, 4) and
            exact_values(positive["exact_target_fractions"]) == [Fraction(3, 4), Fraction(1, 4)],
            "Nonnegative/positive witness separation changed")
    require(exact_values(positive["rejected_upper"])[0] == 0,
            "Strictly positive rejection boundary changed")
    grid = contexts["W-GRID-TEST"]
    require(int(grid["denominator"]) == D and
            sum(int(v) for v in grid["accepted_numerators"]) == D,
            "Grid acceptance denominator mismatch")
    require(any((D * v).denominator != 1 for v in exact_values(grid["rejected_point"])),
            "Grid rejection no longer rejects rational thirds")

    particle = contexts["W-PARTICLE"]
    energies = exact_values(particle["mode_energies"])
    counts = [int(v) for v in particle["mode_counts"]]
    total = sum(n * e for n, e in zip(counts, energies))
    require(total == Fraction(particle["excitation_energy"]) and
            [n * e / total for n, e in zip(counts, energies)] ==
            exact_values(particle["energy_shares"]), "Excitation-energy accounting mismatch")
    prop = contexts["W-PROPERTY"]
    require(Fraction(prop["direct_term"]) + Fraction(prop["linked_term"]) ==
            Fraction(prop["total_derivative"]), "Linked derivative mismatch")
    record = contexts["W-RECORD"]["fields"]
    require(set(record) == {"structural", "preparation", "measurement", "property", "target"},
            "Complete worked-record fields missing")
    require(record["measurement"]["evidence_label"] == "UNSUPPORTED" and
            record["preparation"]["evidence_label"] == "PROPOSED",
            "Candidate preparation/measurement status promoted")
    glass = contexts["W-GLASS"]
    original = json.loads(safe_local(root, glass["source_record_path"]).read_text(encoding="utf-8"))
    require(glass["exact_target_fractions"] == original["composition"]["principal_target"] and
            glass["support_atomic_numbers"] == original["composition"]["atomic_numbers"],
            "Preserved glass principal target changed")
    mass_variation = contexts["W-S2-146"]
    before_counts = [int(v) for v in mass_variation["before_atomic_counts"]]
    after_counts = [int(v) for v in mass_variation["after_atomic_counts"]]
    require(before_counts == [2, 1] and after_counts == [1, 1] and
            mass_variation["applicable_basis"] == "elemental mass",
            "S2 mass comparison lacks an actual same-support count/ratio variation")
    # Anonymous positive probes independently compare the symbolic targets with
    # mass-weighted integer counts. They assign no real isotope or specimen mass.
    for mo, mti in ((1, 1), (1, 2), (2, 3), (7, 11)):
        params = {"M_O": Fraction(mo), "M_Ti": Fraction(mti)}
        phases = []
        for name, counts in (("before", before_counts), ("after", after_counts)):
            weighted = [n * m for n, m in zip(counts, (mo, mti))]
            expected = [Fraction(m, sum(weighted)) for m in weighted]
            actual = [exact_symbolic(t, params)
                      for t in mass_variation[f"{name}_symbolic_mass_targets"]]
            require(actual == expected and all(v > 0 for v in actual) and sum(actual) == 1,
                    f"S2 symbolic {name} mass targets fail qualified count conversion")
            phases.append(actual)
        require(phases[0] != phases[1], "S2 mass comparison changes representation only")
    return {"bounded_contexts": len(contexts), "exact_target_coordinates": fractions_checked,
            "independent_arithmetic_examples": 13,
            "substantive_ratio_or_state_variation_contexts": len(PROPORTION_VARIATION_REQUEST_MARKERS)}


def check_payload(root: Path, data: dict[str, Any]) -> dict[str, Any]:
    scan_types(data)
    require(data["schema_version"] == 1, "Unsupported scenario schema")
    require(data["task_identifier_date"] == "2026-10-04" and
            data["prepared_date"] == "2026-10-05", "Prospective edition date changed")
    require(data["operative_specification"] == SPEC_PATH and
            data["operative_claim_support_map"] == MAP_PATH and
            data["source_claim_review"] == REVIEW_PATH, "Operative source identity changed")
    require(data["proposed_sole_inventor"] == "Robert M. Layne",
            "User-directed proposed inventor changed")
    for flag in FALSE_FLAGS:
        require(data[flag] is False, f"Unproved outcome promoted: {flag}")
    bindings = data["source_bindings"]
    by_path = {b["path"]: b["sha256"] for b in bindings}
    require(len(by_path) == len(bindings), "Duplicate source bindings")
    require(set(PRESERVED_HASHES) <= set(by_path), "Required preserved source binding missing")
    for p, h in PRESERVED_HASHES.items():
        require(by_path[p] == h, f"Preserved edition hash changed: {p}")
    for p, h in by_path.items():
        require(re.fullmatch(r"[0-9a-f]{64}", h) is not None, f"Invalid hash: {p}")
        require(hashlib.sha256(safe_local(root, p).read_bytes()).hexdigest() == h,
                f"Bound source bytes differ: {p}")
    review = json.loads((root / REVIEW_PATH).read_text(encoding="utf-8"))
    original = {c["claim_number"]: c for c in review["claims"]}
    map_data = json.loads((root / MAP_PATH).read_text(encoding="utf-8"))
    map_claims = {c["claim_number"]: c for c in map_data["claims"]}
    spec = (root / SPEC_PATH).read_text(encoding="utf-8")
    claims = parse_claims(spec)
    direct, transitive = dependencies(claims)
    paragraph_ids = set(re.findall(r"^\[(\d{4})\]", spec, re.M))
    require(len(paragraph_ids) == 99, "Preserved 99-paragraph edition changed")
    require(data["family_profiles"] == {f["id"]: f for f in review["families"]},
            "Family profile changed from attributed current review")
    require(data["comparators"] == review["comparators"], "Comparator source scope changed")
    require(set(data["scenario_types"]) == SCENARIO_TYPES, "Scenario types changed")
    require(data["claim_count"] == 199 and data["scenario_count"] == 796,
            "Declared claim/scenario count mismatch")
    rows = data["claims"]
    require([c["claim_number"] for c in rows] == list(range(1, 200)),
            "Missing, repeated or unordered candidate")
    total = 0
    legal_ids = {s["id"] for s in review["legal_sources"]}
    for c in rows:
        n = c["claim_number"]
        require(c["exact_text"] == claims[n] == map_claims[n]["text"],
                f"Exact current claim text mismatch: {n}")
        prefix = re.match(r"The (?:material|method) of claim \d+, (.*)", claims[n], re.S)
        actual_feature = prefix.group(1) if prefix else claims[n]
        require(c["actual_additional_feature"] == actual_feature ==
                original[n]["actual_additional_feature"], f"Own feature mismatch: {n}")
        require(c["direct_dependencies"] == direct[n] and
                sorted(c["transitive_dependencies"]) == transitive[n],
                f"Actual dependency graph mismatch: {n}")
        require(c["independent"] is (not direct[n]), f"Independence mismatch: {n}")
        require(c["family_id"] == original[n]["family_id"] and
                c["category"] == original[n]["category"], f"Family/category mismatch: {n}")
        require(c["complete_combination_mapped_paragraphs"] ==
                original[n]["complete_combination_mapped_paragraphs"] and
                c["supplemental_review_paragraphs"] == original[n]["supplemental_review_paragraphs"],
                f"Current paragraph mapping changed: {n}")
        require(c["historical_novelty_assessed"] is False, f"Historical status promoted: {n}")
        require(c["current_support_gap_assessment_ref"] ==
                {"path": REVIEW_PATH, "claim_number": n}, f"Current assessment link mismatch: {n}")
        probe = c["additional_boundary_probe"]
        require(probe["statutory_determination"] == "unresolved" and
                probe["physical_result_asserted"] is False and
                "not one of the four" in probe["role"],
                f"Boundary probe substituted for representative scenario: {n}")
        scenarios = c["scenario_records"]
        require(len(scenarios) == 4 and
                {s["scenario_type_id"] for s in scenarios} == SCENARIO_TYPES,
                f"Four scenario coverage missing: {n}")
        for s in scenarios:
            tid = s["scenario_type_id"]
            require(s["id"] == f"C{n:03d}-{tid}", f"Scenario identity mismatch: {n}/{tid}")
            require(s["own_feature_assessed"] == actual_feature,
                    f"Scenario omitted/changed own feature: {n}/{tid}")
            require(s["complete_candidate_combination"] == sorted({n, *transitive[n]}),
                    f"Scenario imports sibling or omits parent: {n}/{tid}")
            require(s["hypothetical_later_claim"] is True and
                    s["statutory_determination"] == "unresolved" and
                    s["physical_enablement_established"] is False and
                    s["applicant_experiment_asserted"] is False,
                    f"Scenario status/outcome promoted: {n}/{tid}")
            if tid == "S2":
                variation = s["variation_scope"]
                require(variation["boundary_probes_are_separate"] is True,
                        f"S2 substitutes a boundary probe: {n}")
                request = s["hypothetical_request"]
                if c["category"] == "material":
                    require(variation["selected_element_labels_preserved"] is True and
                            variation["support_cardinality_preserved"] is True,
                            f"Physical S2 alters selected labels/k: {n}")
                    require(request.startswith(
                        "For the same selected elemental support, all the same labels remain positive and k is unchanged. "),
                        f"Physical S2 lacks same-element comparison: {n}")
                    forbidden = ("change the complete positive support from", "add a second positively retained",
                                 "omit one of the", "remove every label", "require a positively retained e119",
                                 "replace one constituent")
                    require(not any(p in request.lower() for p in forbidden),
                            f"Physical S2 contradicts support-preservation rule: {n}")
                    if 2 <= n <= 138:
                        require(f"same {n} selected labels and exactly k={n}" in request,
                                f"Exact-k S2 does not preserve own count: {n}")
                    if n == 139:
                        require("same single element and atomic fraction one" in request,
                                "Unary S2 must vary structure/state while fraction remains one")
                    if n in PROPORTION_VARIATION_REQUEST_MARKERS:
                        require(s["actual_variation_context_id"] == f"W-S2-{n}" and
                                s["actual_variation_context_id"] in s["bounded_context_ids"] and
                                s["representation_observations_are_ancillary"] is True and
                                PROPORTION_VARIATION_REQUEST_MARKERS[n] in request.lower(),
                                f"Material S2 substitutes basis/address/representation changes only: {n}")
                else:
                    require(variation["selected_element_labels_preserved"] ==
                            "not a physical-material support comparison" and
                            request.startswith("Keep the same"),
                            f"Method S2 does not compare a qualified same-input variation: {n}")
                    fault_substitutions = ("omit the measurement/property field",
                                           "count a nominated atom and its contained nucleus/quarks again",
                                           "promote an unconfirmed model candidate to an observed entity")
                    require(not any(p in request.lower() for p in fault_substitutions),
                            f"Method S2 substitutes a fault/accounting probe: {n}")
            require(f"claim {n}" in s["possible_section_102_argument"] and
                    bool(s["claim_specific_application"]) and bool(s["hypothetical_request"]),
                    f"Missing individual application: {n}/{tid}")
            require(len(s["missing_features"]) >= 3 and len(s["unresolved_questions"]) >= 5,
                    f"Missing gaps/questions: {n}/{tid}")
            require(all(s["bounded_context_ids"]) and
                    set(s["bounded_context_ids"]) <= set(data["bounded_contexts"]),
                    f"Unknown bounded context: {n}/{tid}")
            require(s["comparator_ids"] == original[n]["source_comparator_ids"],
                    f"Comparator scope substituted: {n}/{tid}")
            require(set(s["legal_source_ids"]) <= legal_ids, f"Unknown legal source: {n}/{tid}")
            require(s["disclosed_features"][0]["feature"] == actual_feature and
                    s["disclosed_features"][0]["evidence_label"] == "PROPOSED" and
                    s["disclosed_features"][1]["evidence_label"] == "CALCULATED",
                    f"Disclosed feature/status changed: {n}/{tid}")
            for feature in s["disclosed_features"]:
                require(set(feature.get("specification_paragraphs", [])) <= paragraph_ids,
                        f"Unknown scenario locator: {n}/{tid}")
            total += 1
    require(total == 796, "Actual scenario count mismatch")
    arithmetic = check_contexts(data, paragraph_ids, root)
    return {"claims": 199, "scenario_records": total, "source_bindings": len(bindings),
            "exact_texts_and_dependencies_checked": True,
            "unresolved_statuses_preserved": True, **arithmetic}


def check(root: Path) -> dict[str, Any]:
    root = Path(root)
    data = json.loads((root / DATA_PATH).read_text(encoding="utf-8"))
    result = check_payload(root, data)
    guide = (root / GUIDE_PATH).read_text(encoding="utf-8")
    scan_types(guide)
    require(re.findall(r"^### Claim (\d+)$", guide, re.M) ==
            [str(n) for n in range(1, 200)], "Readable crosswalk missing a candidate")
    require("Prepared **5 October 2026**" in guide, "Readable guide has stale preparation date")
    for n in range(1, 200):
        for tid in SCENARIO_TYPES:
            require(f"C{n:03d}-{tid}" in guide, f"Readable scenario missing {n}/{tid}")
    return result


def self_test(root: Path) -> dict[str, int]:
    """Reject targeted corruptions in memory; do not write or alter any source."""
    root = Path(root)
    base = json.loads((root / DATA_PATH).read_text(encoding="utf-8"))
    check_payload(root, base)
    mutations = [
        ("claim text", lambda d: d["claims"][0].update(exact_text="Changed claim")),
        ("dependency", lambda d: d["claims"][182].update(transitive_dependencies=[1])),
        ("scenario missing", lambda d: d["claims"][138]["scenario_records"].pop()),
        ("own feature", lambda d: d["claims"][190]["scenario_records"][0].update(own_feature_assessed="Only target arithmetic")),
        ("sibling import", lambda d: d["claims"][181]["scenario_records"][0]["complete_candidate_combination"].append(181)),
        ("legal promotion", lambda d: d["claims"][197]["scenario_records"][1].update(statutory_determination="established")),
        ("experimental promotion", lambda d: d.update(applicant_physical_experiments_performed=True)),
        ("source hash", lambda d: d["source_bindings"][0].update(sha256="0" * 64)),
        ("absolute source", lambda d: d["source_bindings"][0].update(path="C:/private/source.md")),
        ("float", lambda d: d["bounded_contexts"]["W-HALF"]["exact_target_fractions"].__setitem__(0, 0.5)),
        ("isotope counts", lambda d: d["bounded_contexts"]["W-ISO"].update(inventory_N="2")),
        ("grid rejection", lambda d: d["bounded_contexts"]["W-GRID-TEST"].update(rejected_point=["1/2", "1/2"])),
        ("hypothetical label promotion", lambda d: d["bounded_contexts"]["W-ENUM"]["enumerated_label_statuses"][118].update(status="Recognized")),
        ("physical context", lambda d: d["bounded_contexts"]["W-K138"].update(physical_realization_established=True)),
        ("coordinate", lambda d: d["bounded_contexts"]["W-K138"]["exact_target_fractions"].__setitem__(0, "2/138")),
        ("record status", lambda d: d["bounded_contexts"]["W-RECORD"]["fields"]["measurement"].update(evidence_label="ESTABLISHED")),
        ("S2 support replacement", lambda d: d["claims"][0]["scenario_records"][1].update(hypothetical_request="Replace one constituent and change the support")),
        ("S2 exact-count change", lambda d: d["claims"][1]["scenario_records"][1].update(hypothetical_request="For the same selected elemental support, all the same labels remain positive and k is unchanged. Change the complete positive support from exactly 2 to 3 labels.")),
        ("S2 unary addition", lambda d: d["claims"][138]["scenario_records"][1].update(hypothetical_request="For the same selected elemental support, all the same labels remain positive and k is unchanged. Add a second positively retained elemental label.")),
        ("S2 ratio positivity", lambda d: d["bounded_contexts"]["W-K003"]["same_support_ratio_variant"]["exact_target_fractions"].__setitem__(1, "0/1")),
        ("S2 method corruption substitute", lambda d: d["claims"][185]["scenario_records"][1].update(hypothetical_request="Omit the measurement field instead of changing a qualified input")),
        ("S2 atom basis relabel only", lambda d: d["claims"][143]["scenario_records"][1].update(hypothetical_request="For the same selected elemental support, all the same labels remain positive and k is unchanged. State the same atom inventory on a mass basis.")),
        ("S2 primitive duplicate only", lambda d: d["claims"][148]["scenario_records"][1].update(hypothetical_request="For the same selected elemental support, all the same labels remain positive and k is unchanged. Replace (1,1)/2 by (2,2)/4 without changing ratios.")),
        ("S2 interval address only", lambda d: d["claims"][151]["scenario_records"][1].update(hypothetical_request="For the same selected elemental support, all the same labels remain positive and k is unchanged. Assign a different box address to the unchanged target.")),
        ("S2 identical ratio contexts", lambda d: d["bounded_contexts"]["W-S2-144"].update(before_exact_target_fractions=["1/2", "1/2"])),
        ("S2 mass count relabel only", lambda d: d["bounded_contexts"]["W-S2-146"].update(after_atomic_counts=["2", "1"])),
        ("S2 nonprimitive q", lambda d: d["bounded_contexts"]["W-S2-149"].update(after_primitive_q="8", after_primitive_n=["6", "2"])),
        ("S2 trace outside fixed range", lambda d: d["bounded_contexts"]["W-S2-160"].update(exact_target_fractions=[f"101/{D}", f"{D-101}/{D}"])),
        ("S2 symbolic mass error", lambda d: d["bounded_contexts"]["W-S2-146"].update(after_symbolic_mass_targets=["2*M_O/(2*M_O+M_Ti)", "M_Ti/(2*M_O+M_Ti)"])),
        ("S2 state-ID relabel only", lambda d: d["claims"][171]["scenario_records"][1].update(hypothetical_request="For the same selected elemental support, all the same labels remain positive and k is unchanged. Merge source state identifiers without changing populations.")),
        ("S2 tolerance relabel only", lambda d: d["claims"][183]["scenario_records"][1].update(hypothetical_request="For the same selected elemental support, all the same labels remain positive and k is unchanged. Narrow a target tolerance while preserving unchanged proportions and state.")),
        ("S2 identical isotope state populations", lambda d: d["bounded_contexts"]["W-S2-172"].update(after_joint_coordinates=["1/4", "1/4", "1/2"], after_joint_counts=["2", "2", "4"])),
    ]
    rejected = 0
    for label, mutate in mutations:
        damaged = copy.deepcopy(base)
        mutate(damaged)
        try:
            check_payload(root, damaged)
        except (ValueError, AssertionError, KeyError, TypeError):
            rejected += 1
        else:
            raise ValueError(f"Scenario self-test failed to reject: {label}")
    return {"mutations_rejected": rejected, "repository_files_modified": 0}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    require(not sys.flags.optimize, "Run scenario checks without -O/-OO")
    root = Path(__file__).resolve().parents[1]
    result = check(root)
    if args.self_test:
        result["self_test"] = self_test(root)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
