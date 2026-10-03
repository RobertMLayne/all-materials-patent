"""Check the reviewed edition and its claim screening without PDF dependencies.

These checks validate preserved text, evidence boundaries and recorded authoring
coverage. They do not independently parse/render a PDF or decide patentability.
The caller supplies package path and assertion helpers, so copied self-test
fixtures never read the original checkout implicitly.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from math import lcm
from pathlib import Path
import re
from urllib.parse import urlsplit

SOURCE = "documents/provisional_application_substantive_review_2026-10-03.md"
SUPPORT = "data/claim_support_map_substantive_review_2026-10-03.json"
EDITION = "data/application_substantive_review_2026-10-03.json"
PDF = "documents/pdf/provisional_application_substantive_review_2026-10-03.pdf"
CLAIM_REVIEW = "data/claim_review_2026-10-03.json"
TECHNICAL_REVIEW = "data/technical_review_2026-10-03.json"
GUIDE = "documents/application_substantive_review_2026-10-03.md"
OLD_SOURCE = "documents/provisional_application_theoretical_review_2026-10-01.md"
OLD_SUPPORT = "data/claim_support_map_theoretical_review_2026-10-01.json"
OLD_EDITION = "data/application_theoretical_review_2026-10-01.json"
BASELINE = "4ee2a5eb9001d6313df705d66358a9e575b0a04d"
AUTHORING = {
    "tools/pdf/build_working_application.py": "data/application_substantive_review_authoring_2026-10-03/builder.py.txt",
    "tools/pdf/build_consolidated_review.py": "data/application_substantive_review_authoring_2026-10-03/layout.py.txt",
    "tools/pdf/build_identity_review_annex.py": "data/application_substantive_review_authoring_2026-10-03/output_helper.py.txt",
}
FILES = {SOURCE, SUPPORT, EDITION, PDF, CLAIM_REVIEW, TECHNICAL_REVIEW, GUIDE,
         "tools/substantive_review_checks.py", "tools/technical_review_calculations.py", *AUTHORING.values()}
DIMENSIONS = {"textual_support", "physical_enablement", "novelty", "obviousness",
              "eligibility", "definiteness", "unity", "inventorship"}
# This edition records preliminary screening, not resolved statutory outcomes.
# Controlled wording rejects a contradictory promotion even when a caller has
# deliberately refreshed an outer manifest or an authoring fingerprint.
DETERMINATIONS = {
    "textual_support": {"text correspondence checked; legal possession unresolved"},
    "physical_enablement": {"full physical scope not demonstrated enabled",
                            "record operations described; physical material manufacture not claimed"},
    "novelty": {"conditional substantive comparison; statutory outcome unresolved"},
    "obviousness": {"differences/rationale/expectation screened; statutory outcome unresolved"},
    "eligibility": {"claim-as-a-whole screening; statutory outcome unresolved"},
    "definiteness": {"dependency and terminology screening; legal outcome unresolved"},
    "unity": {"common-feature screening; unity/restriction outcome unresolved"},
    "inventorship": {"proposed name preserved; claim-specific human conception unresolved"},
}
BOUNDARY = "## 1 Technical field\n"
OLD_NOVELTY = "Novelty has not been assessed for any of claims 1-199."
NEW_NOVELTY = ("Claims 1-199 receive the separate preliminary feature screening identified in the "
               "companion review; no complete chronological novelty search or final statutory "
               "novelty determination is asserted. The inherited historical novelty-assessment "
               "flags remain unchanged.")
STATUS_REPLACEMENTS = {
    OLD_NOVELTY: NEW_NOVELTY,
    "Every claim remains novelty-unassessed.": (
        "Every claim has a separate preliminary substantive screening; a complete chronological novelty "
        "search and final statutory determinations remain unresolved. Historical individual assessment flags are preserved."),
    "Operations are mathematically described; novelty, eligibility, inventive contribution and full legal support remain unassessed.": (
        "Operations are mathematically described and preliminarily screened; a complete chronological novelty search, "
        "final eligibility, human inventive contribution and full legal support remain unresolved."),
}
# Independent editorial anchors prevent a refreshed map/manifest from approving
# a silently altered theoretical outcome or administrative certification.
PREFACE_SHA256 = "7d61347e62154bca857cda7513b1c7663f12250cb10d7360a8d88b5ed38e6f93"
ADDITIONS_SHA256 = "a5a03fa39c9744757b51618647a8b78728a99bab1bfd586638139d059721ff81"
CLAIM_REVIEW_SHA256 = "0a624b5a57e100582cc08f39ad138ff22585ee7afcd20f685e0653c30808a942"
TECHNICAL_REVIEW_SHA256 = "a6e8c869e6f8cf7a2b4ec85929aebe847f7c9aacc2d1c51755efa7a00d8b8550"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(root: Path, name: str):
    return json.loads((root / name).read_text(encoding="utf-8"))


def check(root: Path, require, safe_path, block_counts, technical_check) -> dict:
    old_bytes, new_bytes = (root / OLD_SOURCE).read_bytes(), (root / SOURCE).read_bytes()
    old, new = old_bytes.decode("utf-8"), new_bytes.decode("utf-8")
    support, historical = read_json(root, SUPPORT), read_json(root, OLD_SUPPORT)
    require(support.get("source_path") == SOURCE and support.get("source_sha256") == digest(new_bytes),
            "Substantive source/map hash differs")
    require(support.get("prepared_date") == "2026-10-03" and support.get("derived_from") == {
        "path": OLD_SOURCE, "sha256": digest(old_bytes), "repository_baseline": BASELINE},
        "Substantive source derivation differs")
    require(support.get("claims") == historical["claims"] and support.get("claim_count") == 199
            and support.get("changed_claims") == [], "Substantive historical claim records differ")
    require(support.get("changed_status_notes") == ["claim_annex_note", "claim_support_intro",
            "record_method_status_row"], "Substantive status-note inventory differs")
    old_paragraphs = re.findall(r"^\[(\d{4})\] (.+)$", old, re.M)
    paragraphs = re.findall(r"^\[(\d{4})\] (.+)$", new, re.M)
    require(len(old_paragraphs) == 94 and paragraphs[:94] == old_paragraphs,
            "Substantive inherited numbered paragraphs differ")
    require([n for n, _ in paragraphs] == [f"{n:04d}" for n in range(1, 100)]
            and support.get("source_paragraph_count") == 99
            and support.get("added_paragraphs") == [f"{n:04d}" for n in range(95, 100)]
            and support.get("changed_paragraphs") == [], "Substantive paragraph inventory differs")
    require(new.count(BOUNDARY) == old.count(BOUNDARY) == 1, "Substantive section boundary differs")
    preface, body = new.split(BOUNDARY)
    require(digest(" ".join(preface.split()).encode()) == PREFACE_SHA256,
            "Substantive reviewed preface qualifications differ")
    addition_start, addition_end = body.index("[0095] "), body.index("## 16 Draft abstract")
    additions = body[addition_start:addition_end]
    require(digest(" ".join(additions.split()).encode()) == ADDITIONS_SHA256,
            "Substantive reviewed additions differ")
    remaining = body[:addition_start] + body[addition_end:]
    expected = old.split(BOUNDARY, 1)[1].replace(Path(OLD_SUPPORT).name, Path(SUPPORT).name, 1)
    for earlier, reviewed in STATUS_REPLACEMENTS.items():
        require(expected.count(earlier) == 1, "Substantive inherited assessment note differs")
        expected = expected.replace(earlier, reviewed, 1)
    require(remaining == expected, "Substantive source changed outside identified additions")
    printed = re.findall(r"^\*\*Claim (\d+)\.\*\* (.+)$", new, re.M)
    require(printed == [(str(c["claim_number"]), c["text"]) for c in historical["claims"]],
            "Substantive printed candidate claims differ")
    for key in ("proposed_inventor", "universal_blocking_status", "applicant_physical_experiments"):
        require(support.get(key) == historical.get(key), "Substantive designation or evidence status differs")

    screening = read_json(root, CLAIM_REVIEW)
    require(screening.get("schema_version") == 1 and screening.get("review_date") == "2026-10-03",
            "Substantive claim review identity differs")
    for key in ("complete_chronological_novelty_search", "final_statutory_determination",
                "applicant_physical_experiments_performed", "universal_blocking_established",
                "legal_inventorship_confirmed"):
        require(screening.get(key) is False, "Substantive claim review promoted an unresolved outcome")
    require(screening.get("proposed_sole_inventor") == "Robert M. Layne"
            and screening.get("source_specification") == OLD_SOURCE
            and screening.get("source_specification_sha256") == digest(old_bytes)
            and screening.get("source_claim_map") == OLD_SUPPORT
            and screening.get("source_claim_map_sha256") == digest((root / OLD_SUPPORT).read_bytes()),
            "Substantive claim review source or designation differs")
    entries = screening.get("claims", [])
    require([c.get("claim_number") for c in entries] == list(range(1, 200)),
            "Substantive claim review inventory differs")
    families = {f["id"] for f in screening["families"]}
    legal_ids = {s["id"] for s in screening["legal_sources"]}
    comparator_ids = set(screening["comparators"])
    issue_ids = {i["id"] for i in screening["drafting_issues"]}
    common_ids = set(screening["common_assessments"])
    paragraph_ids = {n for n, _ in paragraphs}
    ancestors = {}
    independent = []
    for item, original in zip(entries, historical["claims"], strict=True):
        number, text = item["claim_number"], original["text"]
        require(item.get("exact_text") == text and item.get("screen_complete") is True
                and item.get("statutory_determination") == "unresolved",
                "Substantive claim text or assessment boundary differs")
        parent = re.match(r"The .+? of claim (\d+),", text)
        direct = [int(parent[1])] if parent else []
        if not direct:
            independent.append(number)
        require(item.get("direct_dependencies") == direct
                and item.get("independent") is (not direct)
                and all(0 < n < number for n in direct), "Substantive claim direct dependency differs")
        chain = direct + (ancestors[direct[0]] if direct else [])
        ancestors[number] = chain
        require(item.get("transitive_dependencies") == chain, "Substantive claim inherited dependency differs")
        require(item.get("own_mapped_paragraphs") == original["textual_support_paragraphs"]
                and item.get("family_id") in families
                and bool(item.get("actual_additional_feature")), "Substantive claim support correspondence differs")
        inherited = set()
        for ancestor in chain:
            inherited.update(historical["claims"][ancestor - 1]["textual_support_paragraphs"])
        require(set(item.get("inherited_mapped_paragraphs", [])) == inherited
                and set(item.get("complete_combination_mapped_paragraphs", []))
                == inherited | set(original["textual_support_paragraphs"])
                and set(item.get("supplemental_review_paragraphs", [])) <= paragraph_ids,
                "Substantive claim inherited support differs")
        require(set(item.get("source_comparator_ids", [])) <= comparator_ids
                and set(item.get("drafting_issue_ids", [])) <= issue_ids,
                "Substantive claim comparator or issue reference differs")
        dimensions = item.get("dimensions", {})
        require(set(dimensions) == DIMENSIONS, "Substantive claim review dimensions differ")
        for name, dimension in dimensions.items():
            require(dimension.get("screen_complete") is True
                    and bool(dimension.get("claim_application"))
                    and set(dimension.get("legal_source_ids", [])) <= legal_ids,
                    "Substantive claim review dimension evidence differs")
            require(dimension.get("determination") in DETERMINATIONS[name],
                    "Substantive claim dimension promoted or changed a reviewed outcome")
            require(set(dimension.get("comparator_ids", [])) <= comparator_ids
                    and set(dimension.get("drafting_issue_ids", [])) <= issue_ids
                    and ("family_ref" not in dimension or dimension["family_ref"] in families)
                    and ("common_assessment_ref" not in dimension
                         or dimension["common_assessment_ref"] in common_ids),
                    "Substantive claim dimension reference differs")
    require(independent == [1, 139, 186, 194], "Substantive independent claim inventory differs")
    for item in screening["legal_sources"]:
        url = urlsplit(item["url"])
        require(url.scheme == "https" and url.hostname in {"www.uspto.gov", "www.wipo.int",
                "www.federalregister.gov", "www.govinfo.gov", "uscode.house.gov"}
                and bool(item.get("principle")), "Substantive legal source is not an identified primary source")
    scenarios = screening.get("later_claim_scenarios", [])
    require([s.get("id") for s in scenarios] == ["LC01", "LC02", "LC03", "LC04"],
            "Substantive later-claim scenario inventory differs")
    for scenario in scenarios:
        for key in ("concrete_example", "disclosed_features", "missing_features", "possible_section_102_argument",
                    "possible_section_103_argument", "unresolved_questions"):
            require(bool(scenario.get(key)), "Substantive later-claim scenario lacks a comparison field")
        require(bool(scenario.get("legal_source_ids"))
                and set(scenario["legal_source_ids"]) <= legal_ids,
                "Substantive later-claim scenario source differs")
    require(digest((root / CLAIM_REVIEW).read_bytes()) == CLAIM_REVIEW_SHA256,
            "Substantive reviewed claim assessments differ")

    technical = read_json(root, TECHNICAL_REVIEW)
    require(technical.get("schema_version") == 1
            and technical.get("applicant_physical_experiments_performed") is False
            and technical.get("full_scope_physical_enablement_established") is False,
            "Substantive technical review promoted an unresolved physical outcome")
    for key in ("applicant_physical_experiments_planned", "universal_defensive_preemption_established",
                "new_preparation_or_measurement_results_added"):
        require(technical.get(key) is False, "Substantive technical review promoted an unresolved physical outcome")
    require(technical.get("reviewed_specification") == {"path": SOURCE, "sha256": digest(new_bytes),
            "paragraph_count": 99, "claim_count": 199}, "Substantive technical review source differs")
    baselines = technical.get("source_baseline_hashes", [])
    require(technical.get("review_date") == "2026-10-03" and len(baselines) == 4
            and {b["path"] for b in baselines} == {OLD_SOURCE, OLD_SUPPORT, OLD_EDITION,
                "documents/pdf/provisional_application_theoretical_review_2026-10-01.pdf"},
            "Substantive technical baseline inventory differs")
    for item in baselines:
        require(digest(safe_path(root, item["path"]).read_bytes()) == item["sha256"],
                "Substantive technical baseline source differs")
    require([f.get("id") for f in technical.get("findings", [])]
            == [f"TECH-{n:02d}" for n in range(1, 9)]
            and [c.get("id") for c in technical.get("independent_calculation_checks", [])]
            == [f"C{n:02d}" for n in range(1, 16)],
            "Substantive technical review coverage differs")
    for finding in technical["findings"]:
        disposition = finding.get("disposition", {})
        require(disposition.get("status") == "addressed_in_review_narrative"
                and disposition.get("type") in {"narrative_qualification", "narrative_clarification",
                                                 "narrative_correction"}
                and bool(disposition.get("resolution")) and bool(disposition.get("physical_scope_status"))
                and bool(disposition.get("added_paragraphs"))
                and set(disposition["added_paragraphs"]) <= {f"{n:04d}" for n in range(95, 100)},
                "Substantive technical finding disposition differs")
    arithmetic = technical_check(technical, require)
    require(digest((root / TECHNICAL_REVIEW).read_bytes()) == TECHNICAL_REVIEW_SHA256,
            "Substantive reviewed technical assessments differ")
    # Recalculate the illustrative inventory distinctions independently of the
    # report: reduction of the elemental ratio cannot guarantee whole units.
    joint = [Fraction(1, 2) * Fraction(1, 2), Fraction(1, 2) * Fraction(1, 2), Fraction(1, 2)]
    denominator = lcm(*(v.denominator for v in joint))
    require(denominator == 4 and any((2 * v).denominator != 1 for v in joint)
            and [int(4 * v) for v in joint] == [1, 1, 2], "Joint finite-inventory calculation failed")
    require(Fraction(6, 12) == Fraction(1, 2) and 12 % 2 == 0 and 2 % 12 != 0,
            "Whole-molecule finite-inventory calculation failed")

    edition = read_json(root, EDITION)
    require(edition.get("prepared_date") == "2026-10-03"
            and edition.get("edition_status") == "substantively reviewed unfiled theoretical provisional draft"
            and edition.get("repository_baseline") == BASELINE
            and edition.get("filing_asserted") is False and edition.get("physical_enablement_certified") is False,
            "Substantive edition identity or factual status differs")
    for key in ("proposed_inventor", "universal_blocking_status", "applicant_physical_experiments"):
        require(edition.get(key) == historical.get(key), "Substantive edition designation differs")
    old_record = read_json(root, OLD_EDITION)
    expected_sources = {e["path"] for e in old_record["sources"]} - {OLD_SOURCE, OLD_SUPPORT}
    expected_sources |= {SOURCE, SUPPORT, CLAIM_REVIEW, TECHNICAL_REVIEW}
    captures = edition.get("sources", [])
    require(len(captures) == 17 and {s["path"] for s in captures} == expected_sources,
            "Substantive PDF captured-source inventory differs")
    for capture in captures:
        snapshot = AUTHORING.get(capture["path"])
        require(capture.get("snapshot_path") == snapshot and digest(safe_path(root,
                snapshot or capture["path"]).read_bytes()) == capture["sha256"],
                "Substantive PDF captured-source identity differs")
    pdf = edition.get("pdf", {})
    pdf_bytes = safe_path(root, PDF).read_bytes()
    require(pdf.get("path") == PDF and type(pdf.get("page_count")) is int and pdf["page_count"] > 0
            and pdf_bytes.startswith(b"%PDF-") and b"%%EOF" in pdf_bytes[-1024:]
            and len(pdf_bytes) == pdf.get("size_bytes") and digest(pdf_bytes) == pdf.get("sha256"),
            "Substantive PDF bytes differ from record")
    locations = edition.get("location_map", {})
    require(locations.keys() == {f"paragraph_{n:04d}" for n in range(1, 100)}
            | {f"claim_{n}" for n in range(1, 200)}
            and all(type(p) is int and 1 <= p <= pdf["page_count"] for p in locations.values()),
            "Substantive PDF recorded locations differ")
    section = body[body.index("## Hypothetical embodiments for review")
                   + len("## Hypothetical embodiments for review"):addition_end]
    require(edition.get("complete_numbered_text_checked") == {"paragraphs": 99, "claims": 199}
            and edition.get("vector_drawings_checked") == 2
            and edition.get("complete_theoretical_review_text_checked") == block_counts(section)
            and edition.get("complete_theoretical_preface_checked") == block_counts(preface),
            "Substantive recorded text coverage differs")
    for key in ("complete_metal_glass_text_checked", "complete_family_text_checked", "complete_phase_specific_text_checked",
                "complete_preparation_text_checked", "complete_electrical_text_checked", "complete_oxide_defect_text_checked",
                "complete_property_table_checked"):
        require(edition.get(key) == old_record.get(key), "Substantive inherited evidence coverage differs")
    visual = edition.get("visual_review", {})
    require(isinstance(visual, dict) and visual.get("status") == "completed"
            and visual.get("pages_reviewed") == list(range(1, pdf["page_count"] + 1))
            and visual.get("remaining_actionable_visual_findings") == 0,
            "Substantive recorded appearance review is incomplete")
    return {"numbered_paragraphs": 99, "candidate_claims": 199, "claims_individually_screened": 199,
            "dimensions_per_claim": 8, "later_claim_scenarios": 4, "technical_findings": 8,
            "independent_calculation_groups_reviewed": 15, "fresh_technical_arithmetic": arithmetic,
            "captured_sources_checked": len(captures),
            "recorded_pdf_pages": pdf["page_count"], "historical_claims_and_paragraphs_preserved": True,
            "pdf_parsed_or_appearance_rechecked_by_this_check": False,
            "legal_or_full_scope_physical_outcome_certified": False}


def negative_tests(root: Path, checker, require, error_type) -> list[str]:
    """Exercise substantive omissions/promotions inside an already copied fixture."""
    names = [SOURCE, SUPPORT, EDITION, CLAIM_REVIEW, TECHNICAL_REVIEW,
             AUTHORING["tools/pdf/build_working_application.py"]]
    originals = {name: (root / name).read_bytes() for name in names}
    cases = [
        ("substantive_consistent_outcome_promotion_rejected", "Substantive reviewed additions differ"),
        ("substantive_inherited_claim_change_rejected", "Substantive historical claim records differ"),
        ("substantive_claim_review_omission_rejected", "Substantive claim review inventory differs"),
        ("substantive_claim_dimension_omission_rejected", "Substantive claim review dimensions differ"),
        ("substantive_dependency_chain_loss_rejected", "Substantive claim inherited dependency differs"),
        ("substantive_final_novelty_promotion_rejected", "Substantive claim review promoted an unresolved outcome"),
        ("substantive_later_claim_gap_omission_rejected", "Substantive later-claim scenario lacks a comparison field"),
        ("substantive_snapshot_drift_rejected", "Substantive PDF captured-source identity differs"),
        ("substantive_old_pdf_coverage_rejected", "Substantive recorded text coverage differs"),
        ("substantive_technical_promotion_rejected", "Substantive technical review promoted an unresolved physical outcome"),
        ("substantive_covariance_drift_rejected", "Technical review arithmetic mismatch: C14"),
        ("substantive_joint_count_promotion_rejected", "Technical review joint inventory mismatch"),
        ("substantive_nested_comparator_rejected", "Substantive claim dimension reference differs"),
        ("substantive_nested_family_rejected", "Substantive claim dimension reference differs"),
        ("substantive_nested_common_rejected", "Substantive claim dimension reference differs"),
        ("substantive_nested_issue_rejected", "Substantive claim dimension reference differs"),
        ("substantive_dimension_promotion_rejected", "Substantive claim dimension promoted or changed a reviewed outcome"),
        ("substantive_status_note_omission_rejected", "Substantive status-note inventory differs"),
        ("substantive_narrative_status_promotion_rejected", "Substantive technical finding disposition differs"),
        ("substantive_narrative_type_promotion_rejected", "Substantive technical finding disposition differs"),
    ]
    rejected = []
    checker(root)
    for case, message in cases:
        try:
            source = originals[SOURCE].decode()
            support = json.loads(originals[SUPPORT])
            edition = json.loads(originals[EDITION])
            claims = json.loads(originals[CLAIM_REVIEW])
            technical = json.loads(originals[TECHNICAL_REVIEW])
            if "consistent_outcome" in case:
                source = source.replace("[0097] CALCULATED", "[0097] ESTABLISHED", 1)
                support["source_sha256"] = digest(source.encode())
            elif "inherited_claim" in case:
                support["claims"][0]["text"] += " Every material is physically enabled."
            elif "review_omission" in case:
                claims["claims"].pop()
            elif "dimension_omission" in case:
                claims["claims"][0]["dimensions"].pop("inventorship")
            elif "dependency_chain" in case:
                claims["claims"][159]["transitive_dependencies"] = [159]
            elif "final_novelty" in case:
                claims["complete_chronological_novelty_search"] = True
            elif "later_claim_gap" in case:
                claims["later_claim_scenarios"][0]["missing_features"] = []
            elif "snapshot" in case:
                name = AUTHORING["tools/pdf/build_working_application.py"]
                (root / name).write_bytes(originals[name] + b"\n# Uncaptured edit.\n")
            elif "old_pdf" in case:
                edition["complete_numbered_text_checked"]["paragraphs"] = 94
            elif "covariance" in case:
                technical["independent_calculation_checks"][13]["values"]["fraction_covariance"][0][0] = "1/250"
            elif "joint_count" in case:
                technical["structured_test_vectors"]["joint_isotope_counts"]["inventories"][0]["joint_count_compatible"] = True
            elif "nested_comparator" in case:
                claims["claims"][0]["dimensions"]["novelty"]["comparator_ids"] = ["NO_SUCH_COMPARATOR"]
            elif "nested_family" in case:
                claims["claims"][0]["dimensions"]["novelty"]["family_ref"] = "NO_SUCH_FAMILY"
            elif "nested_common" in case:
                claims["claims"][0]["dimensions"]["physical_enablement"]["common_assessment_ref"] = "NO_SUCH_COMMON"
            elif "nested_issue" in case:
                claims["claims"][0]["dimensions"]["definiteness"]["drafting_issue_ids"] = ["NO_SUCH_ISSUE"]
            elif "dimension_promotion" in case:
                claims["claims"][0]["dimensions"]["physical_enablement"]["determination"] = "Full physical scope is established enabled."
            elif "status_note_omission" in case:
                support["changed_status_notes"].pop()
            elif "narrative_status" in case:
                technical["findings"][0]["disposition"]["status"] = "physically_validated"
            elif "narrative_type" in case:
                technical["findings"][0]["disposition"]["type"] = "experimental_validation"
            else:
                technical["full_scope_physical_enablement_established"] = True
            (root / SOURCE).write_bytes(source.encode())
            for name, value in [(SUPPORT, support), (CLAIM_REVIEW, claims), (TECHNICAL_REVIEW, technical)]:
                # Preserve frozen bytes for unchanged inputs. Reformatting an
                # unrelated JSON input would trigger its independent anchor and
                # conceal whether the intended semantic regression was caught.
                if value == json.loads(originals[name]):
                    (root / name).write_bytes(originals[name])
                else:
                    (root / name).write_text(json.dumps(value) + "\n", encoding="utf-8", newline="\n")
            # Refresh capture fingerprints to ensure the semantic requirement,
            # rather than unrelated outer checksum drift, rejects each case.
            for capture in edition["sources"]:
                if capture["path"] in {SOURCE, SUPPORT, CLAIM_REVIEW, TECHNICAL_REVIEW}:
                    capture["sha256"] = digest((root / capture["path"]).read_bytes())
            (root / EDITION).write_text(json.dumps(edition) + "\n", encoding="utf-8", newline="\n")
            try:
                checker(root)
            except error_type as error:
                require(message in str(error), f"Substantive failure fixture rejected for an unrelated reason: {case}: {error}")
                rejected.append(case)
            else:
                require(False, f"Substantive failure fixture was accepted: {case}")
        finally:
            for name, data in originals.items():
                (root / name).write_bytes(data)
    require(len(rejected) == len(cases), "Substantive failure coverage differs")
    return rejected
