"""Validate additive provenance exhibits without inferring legal/physical results.

The supplied root is always used, including copied fixtures. PDF integrity and
recorded page metadata are checked here; parsing and visual review remain
separate authoring operations with their own receipts.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import tempfile

INDEX = "data/evidence_edition_index_2026-10-04.json"
GUIDE = "documents/evidence_edition_index_2026-10-04.md"
READINESS = "documents/review_readiness_2026-10-04.md"
SOURCE = "documents/provisional_application_substantive_review_2026-10-03.md"
SOURCE_SHA = "5ccb71d5448a07f41041302f4be2b962e9a214c83b2f92e39ed642a3b8b1ec23"
PDF_SHA = "531dccb58202a5cd6cb24f307a2173ed38abac49ec1d251ed8f3e8a743697a9c"
PACKET = "documents/pdf/materials_review_completion_2026-10-04.pdf"
AUTHORING = "data/review_completion_authoring_2026-10-04.json"
SNAPSHOTS = {
    "tools/pdf/build_completion_exhibits.py": "data/review_completion_authoring_2026-10-04/builder.py.txt",
    "tools/pdf/build_consolidated_review.py": "data/review_completion_authoring_2026-10-04/layout.py.txt",
    "tools/pdf/build_identity_review_annex.py": "data/review_completion_authoring_2026-10-04/output_helper.py.txt",
}
PACKET_INPUTS = {
    "documents/review_readiness_2026-10-04.md", "documents/evidence_edition_index_2026-10-04.md",
    "documents/material_state_process_coverage_2026-10-04.md", SOURCE,
    "documents/pdf/provisional_application_substantive_review_2026-10-03.pdf",
    "data/claim_scenarios_2026-10-04.json", INDEX, "data/material_state_process_coverage_2026-10-04.json",
    "data/claim_review_2026-10-03.json", "data/claim_support_map_substantive_review_2026-10-03.json",
    "tools/pdf/requirements-pdf.txt", *SNAPSHOTS,
}
FALSE_FLAGS = (
    "filing_asserted", "earliest_public_availability_certified", "legal_inventorship_confirmed",
    "applicant_experiments_performed", "complete_chronological_novelty_search", "universal_blocking_established",
)
# The edition IDs are historical identities, not interchangeable positions in
# a list. Bind their artifact names as well as checking the supplied hashes.
EDITION_ARTIFACTS = [
    ("draft", "", None),
    ("working_2026-09-30", "working_2026-09-30", "working_application_2026-09-30"),
    ("property_evidence_2026-09-30", "property_evidence_2026-09-30", "application_property_evidence_2026-09-30"),
    ("preparation_evidence_2026-09-30", "preparation_evidence_2026-09-30", "application_preparation_evidence_2026-09-30"),
    ("electrical_evidence_2026-09-30", "electrical_evidence_2026-09-30", "application_electrical_evidence_2026-09-30"),
    ("oxide_defect_evidence_2026-09-30", "oxide_defect_evidence_2026-09-30", "application_oxide_defect_evidence_2026-09-30"),
    ("phase_specific_evidence_2026-10-01", "phase_specific_evidence_2026-10-01", "application_phase_specific_evidence_2026-10-01"),
    ("family_evidence_2026-10-01", "family_evidence_2026-10-01", "application_family_evidence_2026-10-01"),
    ("metal_glass_evidence_2026-10-01", "metal_glass_evidence_2026-10-01", "application_metal_glass_evidence_2026-10-01"),
    ("theoretical_review_2026-10-01", "theoretical_review_2026-10-01", "application_theoretical_review_2026-10-01"),
    ("substantive_review_2026-10-03", "substantive_review_2026-10-03", "application_substantive_review_2026-10-03"),
]
EVIDENCE_PATHS = {
    "data/electrical_source_review_2026-09-30.json", "data/family_source_review_2026-10-01.json",
    "data/hydrogel_preparation_source_review_2026-09-30.json", "data/magneli_source_review_2026-10-01.json",
    "data/metal_glass_source_review_2026-10-01.json", "data/oxide_defect_source_review_2026-09-30.json",
    "documents/reference_entry_support.md", "documents/composite_comparator_source_review_2026-09-30.md",
    "data/nuclear_archive/source_metadata.json", "data/nuclear_archive/portable_bundle_manifest.json",
    "data/particle_archive/pdg2026_identity_metadata.json", "data/publication_observation.json",
    "data/edition_identity_corrections_2026-10-03.json", "data/technical_review_2026-10-03.json",
}
# Source identity/locator bindings are separate from a scientific or statutory
# conclusion. Scope prose can remain qualified without allowing a replaced ID
# or unrelated URL to masquerade as one of the reviewed source contexts.
COMPARATOR_IDENTITIES = {
    "ALLOY": ("https://doi.org/10.1038/s41598-017-12551-9", "documents/alloy_claim_comparison_2026-09-30.md"),
    "GLASS": ("https://authors.library.caltech.edu/records/4r2k2-70t09", "documents/glass_claim_comparison_2026-10-01.md"),
    "OXIDE": ("https://www.nature.com/articles/srep01411", "documents/oxide_claim_comparison_2026-10-01.md"),
    "POLYMER": ("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7694064/fullTextXML", "specification [0040] polymer evidence block"),
    "HYDROGEL": ("https://www.nature.com/articles/s41467-018-04508-x", "documents/hydrogel_claim_comparison_2026-09-30.md"),
    "ELECTRICAL": ("https://www.nature.com/articles/nnano.2011.40", "documents/electrical_claim_comparison_2026-09-30.md"),
    "MOLECULAR": ("https://journals.iucr.org/m/issues/2021/06/00/yc5034/index.html", "specification [0040] and [0086]"),
    "COMPOSITE": ("https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=920936", "specification [0040] and [0089]"),
    "NUCLEAR": ("https://www-nds.iaea.org/amdc/ame2020/NUBASE2020.pdf", "specification [0046]-[0050], data/nuclear_archive"),
    "PARTICLE": ("https://pdg.lbl.gov/2026/tables/contents_tables.html", "specification [0051]-[0056], data/particle_archive"),
}
HOST_PATH = re.compile(
    r"(?<![A-Za-z0-9_.])(?:[A-Za-z]:[\\/]|\\\\[A-Za-z0-9_.-]+[\\/])"
    r"|(?<![:/A-Za-z0-9_.])//[A-Za-z0-9_.-]+/"
    r"|(?<![:/A-Za-z0-9_.])/(?:Users|home|root|tmp|private|Volumes|mnt|etc|var|workspace)/"
    r"|source[\\/]context[\\/]private"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(root: Path) -> dict:
    return json.loads((root / INDEX).read_text(encoding="utf-8"))


def strings(value):
    """Inspect decoded JSON keys and values, including backslash host paths."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def safe_path(root: Path, relative: str) -> Path:
    """Validate a portable package locator before reading its contents."""
    require(isinstance(relative, str) and bool(relative) and not Path(relative).is_absolute()
            and ":" not in relative and "\\" not in relative and "//" not in relative
            and not any(part in {".", ".."} for part in relative.split("/")),
            "Review artifact path is unsafe")
    result = root / relative
    require(result.resolve().is_relative_to(root.resolve()), "Review artifact path escapes root")
    return result


def check_public_paths(value, context: str) -> None:
    """Keep host paths out of public receipts without mistaking HTTPS URLs.

    Drive/UNC forms and known POSIX host/private roots are host locators.
    Relative source paths, HTTPS URLs and JSON pointers such as /claims/0
    remain permitted; file-valued fields separately require safe relative
    paths. This is bounded screening, not complete sensitive-data detection.
    """
    require(not any(HOST_PATH.search(text) for text in strings(value)),
            context + " contains an absolute/private host path")


def check_packet(root: Path) -> dict:
    record = json.loads((root / AUTHORING).read_text(encoding="utf-8"))
    check_public_paths(record, "Completion PDF authoring record")
    require(record["prepared_date"] == "2026-10-05" and record["task_identifier_date"] == "2026-10-04",
            "Completion PDF preparation identity differs")
    require(record["status"] == "local unfiled review; visual inspection completed"
            and record["filing_asserted"] is False and record["application_content_adoption"] is False
            and record["legal_or_physical_sufficiency_certified"] is False,
            "Completion PDF status differs")
    require(record["authoring_versions"] == {"python": "3.12.14", "reportlab": "4.4.9", "pypdf": "6.19.0"},
            "Completion PDF authoring versions differ")
    pdf = record["pdf"]
    value = (root / PACKET).read_bytes()
    require(pdf["path"] == PACKET and len(value) == pdf["size_bytes"]
            and sha256(value).hexdigest() == pdf["sha256"], "Completion PDF bytes differ")
    require(pdf["application_pages"] == 47 and pdf["review_pages"] > 0
            and pdf["application_first_packet_page"] == pdf["review_pages"] + 1
            and pdf["total_pages"] == pdf["review_pages"] + 47, "Completion PDF page map differs")
    require(record["scenario_navigation_ids_checked"] == 796
            and record["exact_application_claim_bodies_checked"] == 199
            and record["application_page_texts_unchanged"] is True
            and record["original_application_bytes_unchanged"] is True,
            "Completion PDF recorded coverage differs")
    require(record["visual_review"]["status"] == "completed"
            and record["visual_review"]["rendered_page_count"] == pdf["total_pages"]
            and record["visual_review"]["all_contact_pages_inspected"] is True
            and record["visual_review"]["actionable_layout_findings_remaining"] == 0,
            "Completion PDF visual-review receipt differs")
    require({s["path"] for s in record["sources"]} == PACKET_INPUTS and len(record["sources"]) == len(PACKET_INPUTS),
            "Completion PDF authoring input inventory differs")
    for source in record["sources"]:
        relative = source["path"]
        body = safe_path(root, relative).read_bytes()
        require(len(body) == source["size_bytes"] and sha256(body).hexdigest() == source["sha256"],
                "Completion PDF authoring source differs: " + relative)
        if relative in SNAPSHOTS:
            require((root / SNAPSHOTS[relative]).read_bytes() == body, "Completion authoring snapshot differs")
    require(set(SNAPSHOTS) <= {s["path"] for s in record["sources"]}, "Completion PDF builders not captured")
    return {"recorded_packet_pages": pdf["total_pages"], "authoring_source_hashes_checked": len(record["sources"]),
            "inert_authoring_snapshots_checked": len(SNAPSHOTS),
            "recorded_visual_review_checked": True, "pdf_parsed_or_rendered_by_checker": False}


def check(root: Path) -> dict:
    data = load(root)
    require(data["schema_version"] == 1 and data["task_identity_date"] == "2026-10-04"
            and data["prepared_date"] == "2026-10-05", "Review index date/schema differs")
    require(all(data.get(key) is False for key in FALSE_FLAGS), "Review index promotes an unresolved outcome")
    require(data["operative_edition_id"] == "E11", "Review index operative edition differs")
    rows = data["editions"]
    require([r["id"] for r in rows] == [f"E{i:02}" for i in range(1, 12)], "Review index edition coverage differs")
    require([r["prepared_date"] for r in rows] == ["2026-09-29"] + ["2026-09-30"] * 5
            + ["2026-10-01"] * 4 + ["2026-10-03"], "Review index edition chronology differs")
    fingerprints = list(data["evidence_records"])
    require({row["path"] for row in fingerprints} == EVIDENCE_PATHS
            and len(fingerprints) == len(EVIDENCE_PATHS), "Review index evidence inventory differs")
    for row, (application, support, authoring_name) in zip(rows, EDITION_ARTIFACTS):
        require(row["application"]["path"] == f"documents/provisional_application_{application}.md"
                and row["support_map"]["path"] == f"data/claim_support_map{'_' + support if support else ''}.json"
                and row["pdf"]["path"] == f"documents/pdf/provisional_application_{application}.pdf",
                "Review index historical edition artifact identity differs")
        require((authoring_name is None and "authoring_record" not in row)
                or (authoring_name is not None and row.get("authoring_record", {}).get("path")
                    == f"data/{authoring_name}.json"), "Review index historical authoring record identity differs")
        require(row["earlier_filing_or_publication_assigned"] is False
                and row["later_review_exhibits_adopted"] is False, "Review index backdates later content")
        fingerprints.extend(row[k] for k in ("application", "support_map", "pdf"))
        if "authoring_record" in row:
            fingerprints.append(row["authoring_record"])
            authoring = json.loads(safe_path(root, row["authoring_record"]["path"]).read_text(encoding="utf-8"))
            for index_field, authoring_field in (
                    ("captured_sources", "sources"), ("recorded_pdf_metadata", "pdf"),
                    ("recorded_visual_review", "visual_review")):
                require(row.get(index_field) == authoring.get(authoring_field)
                        and index_field in row and authoring_field in authoring,
                        "Review index copied historical field differs: " + index_field)
            require(all(row["pdf"][field] == authoring["pdf"][field]
                        for field in ("path", "sha256", "size_bytes")),
                    "Review index historical PDF differs from authoring record")
            source_hashes = {source["path"]: source["sha256"] for source in authoring["sources"]}
            require(all(source_hashes.get(row[field]["path"]) == row[field]["sha256"]
                        for field in ("application", "support_map")),
                    "Review index historical source differs from authoring record")
        text = safe_path(root, row["application"]["path"]).read_text(encoding="utf-8")
        require(row["claim_count"] == len(re.findall(r"^\*\*Claim \d+\.\*\* ", text, re.M)) == 199,
                "Review index claim count differs")
        require(row["numbered_paragraph_count"] == len(re.findall(r"^\[\d{4}\] ", text, re.M)),
                "Review index paragraph count differs")
    require(rows[-1]["application"]["path"] == SOURCE and rows[-1]["application"]["sha256"] == SOURCE_SHA
            and rows[-1]["pdf"]["sha256"] == PDF_SHA and rows[-1]["numbered_paragraph_count"] == 99,
            "Review index current application binding differs")
    for row in fingerprints:
        relative = row["path"]
        path = safe_path(root, relative)
        value = path.read_bytes()
        require(len(value) == row["size_bytes"] and sha256(value).hexdigest() == row["sha256"],
                "Review index artifact fingerprint differs: " + relative)
    require(data["publication_observation"] == json.loads((root / "data/publication_observation.json").read_text()),
            "Review index historical observation differs")
    require([c["id"] for c in data["comparators"]] == list(COMPARATOR_IDENTITIES)
            and all((c["primary_url"], c["local_locator"]) == COMPARATOR_IDENTITIES[c["id"]]
                    for c in data["comparators"]), "Review index comparator identity/locator inventory differs")
    require(len(data["comparators"]) == 10 and all(c["applicant_result"] is False
            and c["chronological_prior_art_qualification"] == "unresolved" for c in data["comparators"]),
            "Review index comparator qualification differs")
    check_public_paths([data, (root / GUIDE).read_text(encoding="utf-8"),
                        (root / READINESS).read_text(encoding="utf-8")], "Review exhibits")
    return {"edition_count": len(rows), "artifact_fingerprints_checked": len(fingerprints),
            "finite_comparator_contexts": len(data["comparators"]), "current_claim_count": 199,
            "later_content_backdated": False, "filing_or_legal_result_certified": False,
            "pdf_layout_rechecked_by_this_checker": False, "completion_packet": check_packet(root)}


def self_test(root: Path) -> dict:
    original = load(root)
    authoring = json.loads((root / AUTHORING).read_text(encoding="utf-8"))
    files = {INDEX, GUIDE, READINESS, "data/publication_observation.json", AUTHORING, PACKET, *SNAPSHOTS.values()}
    files.update(s["path"] for s in authoring["sources"])
    for row in original["editions"]:
        files.update(row[k]["path"] for k in ("application", "support_map", "pdf"))
        if "authoring_record" in row:
            files.add(row["authoring_record"]["path"])
    files.update(row["path"] for row in original["evidence_records"])
    cases = []
    # A test copy retains historical PDFs/sources. No mutation touches a live
    # application or an authoritative intake record.
    with tempfile.TemporaryDirectory(prefix="materials-index-check-") as directory:
        fixture = Path(directory)
        for relative in files:
            source = safe_path(root, relative)
            target = safe_path(fixture, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        check(fixture)
        mutations = {
            "legal_status_promotion": lambda d: d.update(filing_asserted=True),
            "missing_historical_edition": lambda d: d["editions"].pop(0),
            "backdated_later_teaching": lambda d: d["editions"][-1].update(later_review_exhibits_adopted=True),
            "wrong_current_pdf": lambda d: d["editions"][-1]["pdf"].update(sha256="0" * 64),
            "wrong_observed_public_date": lambda d: d["publication_observation"].update(observation_time_utc="2026-09-29"),
            "private_host_path": lambda d: d.update(scoped_private_intake="C:/Users/example/synthetic-fixture"),
            "private_backslash_host_path": lambda d: d.update(scoped_private_intake="C:\\Users\\example\\synthetic-fixture"),
            "copied_source_inventory_loss": lambda d: d["editions"][1].update(captured_sources=[]),
            "copied_source_hash_drift": lambda d: d["editions"][1]["captured_sources"][0].update(sha256="0" * 64),
            "copied_pdf_metadata_drift": lambda d: d["editions"][1]["recorded_pdf_metadata"].update(page_count=999),
            "copied_visual_receipt_drift": lambda d: d["editions"][1]["recorded_visual_review"].update(status="fabricated"),
            "historical_authoring_record_omitted": lambda d: d["editions"][1].pop("authoring_record"),
            "historical_authoring_record_swapped": lambda d: d["editions"][1].update(authoring_record=d["editions"][2]["authoring_record"]),
            "historical_application_identity_swapped": lambda d: d["editions"][1].update(application=d["editions"][2]["application"]),
            "evidence_inventory_loss": lambda d: d.update(evidence_records=[]),
            "comparator_identity_drift": lambda d: d["comparators"][0].update(id="UNREFERENCED"),
            "comparator_url_drift": lambda d: d["comparators"][0].update(primary_url="https://example.invalid"),
            "comparator_locator_drift": lambda d: d["comparators"][0].update(local_locator="unrelated record"),
            "private_host_key": lambda d: d.update({"C:\\Users\\example\\private": {}}),
            "absolute_drive_path": lambda d: d.update(extra_locator="C:/secret/private-record.json"),
            "private_unc_path": lambda d: d.update(extra_locator="\\\\example\\private\\record.json"),
            "private_posix_path": lambda d: d.update(extra_locator="/home/example/private/record.json"),
            "unsafe_file_locator": lambda d: d["editions"][0]["application"].update(path="../outside.md"),
        }
        for name, mutate in mutations.items():
            candidate = deepcopy(original)
            mutate(candidate)
            (fixture / INDEX).write_text(json.dumps(candidate), encoding="utf-8")
            try:
                check(fixture)
            except (ValueError, KeyError, OSError):
                cases.append(name)
            else:
                raise ValueError("Review index accepted invalid fixture: " + name)
        (fixture / INDEX).write_text(json.dumps(original), encoding="utf-8")
        packet_mutations = {
            "packet_filing_promotion": lambda d: d.update(filing_asserted=True),
            "packet_omitted_input": lambda d: d["sources"].pop(0),
            "packet_unperformed_visual_review": lambda d: d["visual_review"].update(all_contact_pages_inspected=False),
            "packet_private_host_key": lambda d: d.update({"C:\\Users\\example\\private": {}}),
        }
        for name, mutate in packet_mutations.items():
            candidate = deepcopy(authoring)
            mutate(candidate)
            (fixture / AUTHORING).write_text(json.dumps(candidate), encoding="utf-8")
            try:
                check(fixture)
            except (ValueError, KeyError, OSError):
                cases.append(name)
            else:
                raise ValueError("Completion packet accepted invalid fixture: " + name)
    require(len(cases) == len(mutations) + len(packet_mutations), "Review index negative-case coverage differs")
    # These are legitimate public locators, not host file paths. Keep this
    # positive control alongside rejection tests so screening cannot quietly
    # break the index's HTTPS citations and JSON navigation vocabulary.
    check_public_paths({"json_pointer": "/claims/0/dimensions", "local_file": "data/review.json",
                        "source_url": "https://www.uspto.gov/web/offices/pac/mpep/s2131.html"},
                       "Public locator positive control")
    return {"invalid_cases_rejected": len(cases), "cases": cases, "live_source_mutations": 0,
            "public_json_pointers_and_https_urls_preserved": True}
