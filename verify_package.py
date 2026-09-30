#!/usr/bin/env python3
"""Verify this research package without dependencies or repository writes.

The manifest checks consistency, not authenticity or public-availability time.
The exact model tests concern mathematics, not physical material enablement.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager, redirect_stdout
from fractions import Fraction
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True

MANIFEST = "integrity_manifest.json"
RANGE_REPORT = "range_model/verification_report.json"
NUCLEAR_DIRECTORY = "data/nuclear_archive"
PARTICLE_DIRECTORY = "data/particle_archive"
OPTIONAL_NUCLEAR_VIEW = f"{NUCLEAR_DIRECTORY}/nuclear_states.json"
REVIEW_PACKET = "data/review_packet_manifest.json"
REVIEW_PREPARED_DATE = "2026-09-30"
WORKING_SOURCE = "documents/provisional_application_working_2026-09-30.md"
WORKING_MAP = "data/claim_support_map_working_2026-09-30.json"
WORKING_EDITION = "data/working_application_2026-09-30.json"
WORKING_CHANGED_PARAGRAPHS = {"0008", "0010", "0011", "0018", "0030", "0031", "0032", "0047", "0075"}
WORKING_CHANGED_CLAIMS = {147, 169, 191, 192, 193}
WORKING_AUTHORING = {
    "tools/pdf/build_working_application.py": "data/working_application_authoring_2026-09-30/builder.py.txt",
    "tools/pdf/build_consolidated_review.py": "data/working_application_authoring_2026-09-30/layout.py.txt",
    "tools/pdf/build_identity_review_annex.py": "data/working_application_authoring_2026-09-30/output_helper.py.txt",
}
PROPERTY_SOURCE = "documents/provisional_application_property_evidence_2026-09-30.md"
PROPERTY_MAP = "data/claim_support_map_property_evidence_2026-09-30.json"
PROPERTY_EDITION = "data/application_property_evidence_2026-09-30.json"
PROPERTY_PDF = "documents/pdf/provisional_application_property_evidence_2026-09-30.pdf"
PROPERTY_BASELINE = "2352f733bcf4fc6d786ccd5f162037a252d2608a"
PROPERTY_AUTHORING = {
    "tools/pdf/build_working_application.py": "data/application_property_evidence_authoring_2026-09-30/builder.py.txt",
    "tools/pdf/build_consolidated_review.py": "data/application_property_evidence_authoring_2026-09-30/layout.py.txt",
    "tools/pdf/build_identity_review_annex.py": "data/application_property_evidence_authoring_2026-09-30/output_helper.py.txt",
}
PREPARATION_SOURCE = "documents/provisional_application_preparation_evidence_2026-09-30.md"
PREPARATION_MAP = "data/claim_support_map_preparation_evidence_2026-09-30.json"
PREPARATION_EDITION = "data/application_preparation_evidence_2026-09-30.json"
PREPARATION_PDF = "documents/pdf/provisional_application_preparation_evidence_2026-09-30.pdf"
PREPARATION_REVIEW = "data/hydrogel_preparation_source_review_2026-09-30.json"
PREPARATION_BASELINE = "b31593f84ccb26a19cf1642d4a6115cb6a1543f0"
PREPARATION_HEADING = "### Preparation associated with [0065]: identities, operations and composition basis"
PREPARATION_AUTHORING = {
    "tools/pdf/build_working_application.py": "data/application_preparation_evidence_authoring_2026-09-30/builder.py.txt",
    "tools/pdf/build_consolidated_review.py": "data/application_preparation_evidence_authoring_2026-09-30/layout.py.txt",
    "tools/pdf/build_identity_review_annex.py": "data/application_preparation_evidence_authoring_2026-09-30/output_helper.py.txt",
}
REVIEW_AUTHORING_FILES = {
    "builder": "data/review_packet_authoring/core_builder_2026-09-30.py.txt",
    "helper": "data/review_packet_authoring/core_shared_helper_2026-09-30.py.txt",
}
REVIEW_SOURCE_FILES = frozenset({
    "documents/pdf/provisional_application_draft.pdf", "documents/provisional_application_draft.md",
    "documents/technical_scope_supplement.md", "documents/reference_entry_support.md",
    "documents/current_status_addendum.md", "documents/full_scope_completion_audit.md",
    "data/claim_support_map.json", "documents/drawings/composition_simplex.svg",
    "documents/drawings/material_record_sequence.svg", "data/entity_register.json",
    "data/entity_register_notes.md", "data/nuclear_archive/nubase_4.mas20.txt",
    "data/nuclear_archive/schema_header.txt", "data/nuclear_archive/column_schema.json",
    "data/nuclear_archive/source_metadata.json", "data/nuclear_archive/license_attribution.md",
    "data/nuclear_archive/archive_counts.json", "data/nuclear_archive/README.md",
    "data/particle_archive/pdg2026_identity_archive.json",
    "data/particle_archive/pdg2026_identity_metadata.json", "data/particle_archive/README.md",
})
NUCLEAR_FILES = frozenset({
    "archive_counts.json", "column_schema.json", "license_attribution.md",
    "nubase_4.mas20.txt", "parse_nubase.py", "portability_report.json",
    "portable_bundle_manifest.json", "README.md", "schema_header.txt",
    "source_metadata.json", "verification_report.json", "verify_nuclear_archive.py",
})
PARTICLE_FILES = frozenset({
    "adversarial_verification_report.json", "extract_pdg_identities.py",
    "pdg2026_identity_archive.json", "pdg2026_identity_metadata.json",
    "README.md", "verification_report.json",
})
EXPECTED_HASHED = frozenset({
    ".gitattributes", ".github/workflows/verify.yml", ".gitignore", "AGENTS.md", "README.md",
    "verify_package.py", "data/claim_support_map.json", "data/entity_register.json",
    "data/entity_register_notes.md", "documents/provisional_application_draft.md",
    "documents/provisional_filing_strategy.md", "documents/pct_defensive_disclosure_blueprint.md",
    "documents/pdf/provisional_application_draft.pdf",
    "documents/pdf/provisional_filing_strategy.pdf",
    "documents/pdf/pct_defensive_disclosure_blueprint.pdf",
    "documents/drawings/composition_simplex.svg",
    "documents/drawings/material_record_sequence.svg",
    "range_model/composition_ranges.py", "range_model/composition_range_model.json",
    "range_model/numeric_examples.json",
    "data/publication_observation.json", "documents/current_status_addendum.md",
    "documents/reference_entry_support.md", "documents/technical_scope_supplement.md",
    "documents/composite_comparator_source_review_2026-09-30.md",
    "documents/alloy_claim_comparison_2026-09-30.md",
    "documents/hydrogel_property_evidence_2026-09-30.md",
    "documents/hydrogel_claim_comparison_2026-09-30.md",
    "data/hydrogel_candidate_record_review_2026-09-30.json",
    "documents/full_scope_completion_audit.md",
    "range_model/unrestricted_compositions.py",
    "range_model/unrestricted_composition_model.json",
    "range_model/unrestricted_numeric_examples.json",
    "range_model/unrestricted_verification_report.json",
    "range_model/independent_unrestricted_checks.py",
    "range_model/independent_unrestricted_report.json",
    "range_model/claim_clarification_checks.py", "range_model/claim_clarification_report.json",
    "range_model/trace_sampling_calculations.py", "range_model/trace_sampling_report.json",
}) | {f"{NUCLEAR_DIRECTORY}/{name}" for name in NUCLEAR_FILES} | {
    f"{PARTICLE_DIRECTORY}/{name}" for name in PARTICLE_FILES
}
EXPECTED_HASHED = EXPECTED_HASHED | {
    WORKING_SOURCE, WORKING_MAP, WORKING_EDITION,
    "documents/working_application_2026-09-30.md",
    "documents/pdf/provisional_application_working_2026-09-30.pdf",
    "tools/pdf/build_working_application.py", *WORKING_AUTHORING.values(),
    ".editorconfig", ".vscode/settings.json", ".vscode/extensions.json", ".vscode/tasks.json",
    "CONTRIBUTING.md", "documents/workflow_decisions.md", "documents/restart_checkpoint.md",
    "documents/github_settings.md", "tools/update_manifest.py", "pyproject.toml", "requirements-dev.txt",
    ".github/CODEOWNERS", ".github/pull_request_template.md", ".github/dependabot.yml",
    ".github/workflows/codeql.yml", ".github/workflows/copilot-setup-steps.yml",
    ".github/copilot-instructions.md",
    ".github/agents/exact-math-reviewer.agent.md",
    ".github/agents/archive-provenance-reviewer.agent.md",
    ".github/agents/scientific-evidence-reviewer.agent.md",
    ".github/skills/exact-math-code-review/SKILL.md",
    ".github/skills/archive-provenance-code-review/SKILL.md",
    ".github/skills/scientific-evidence-code-review/SKILL.md",
    ".github/skills/github-actions-failure-review/SKILL.md",
    "documents/consolidated_review_edition.md", "documents/applicant_evidence_intake.md",
    "documents/claim_group_review_brief.md", "documents/proposed_claim_clarifications.md",
    REVIEW_PACKET,
    *REVIEW_AUTHORING_FILES.values(),
    "documents/pdf/materials_provisional_review_2026-09-30.pdf",
    "documents/pdf/materials_identity_data_review_annex.pdf",
    "tools/pdf/build_consolidated_review.py", "tools/pdf/build_identity_review_annex.py",
    "tools/pdf/requirements-pdf.txt", "tools/pdf/test_pdf_outputs.py",
    PROPERTY_SOURCE, PROPERTY_MAP, PROPERTY_EDITION, PROPERTY_PDF,
    "documents/application_property_evidence_2026-09-30.md", *PROPERTY_AUTHORING.values(),
    PREPARATION_SOURCE, PREPARATION_MAP, PREPARATION_EDITION, PREPARATION_PDF, PREPARATION_REVIEW,
    "documents/application_preparation_evidence_2026-09-30.md", *PREPARATION_AUTHORING.values(),
}
EXPECTED_FILES = EXPECTED_HASHED | {MANIFEST, RANGE_REPORT}
MODULE_NAMES = frozenset({
    "composition_ranges", "unrestricted_compositions", "independent_unrestricted_checks",
    "trace_sampling_calculations", "claim_clarification_checks", "parse_nubase", "verify_nuclear_archive",
    "extract_pdg_identities",
})


class VerificationError(Exception):
    """A package consistency requirement was not met."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def safe_path(root: Path, relative: str) -> Path:
    """Accept portable manifest-relative paths and reject symlink escapes."""
    require(isinstance(relative, str) and bool(relative), "Empty or non-string path")
    parsed = PurePosixPath(relative)
    require(not parsed.is_absolute() and not any(p in {".", ".."} for p in relative.split("/")),
            f"Unsafe relative path: {relative}")
    require("\\" not in relative and ":" not in relative and "//" not in relative,
            f"Nonportable relative path: {relative}")
    candidate = root.joinpath(*parsed.parts)
    require(candidate.resolve().is_relative_to(root.resolve()), f"Path escapes package: {relative}")
    return candidate


def ignored(relative: str) -> bool:
    parts = PurePosixPath(relative).parts
    return (".git" in parts or "__pycache__" in parts or
            parts[0] in {"generated_reports", ".venv", ".ruff_cache"} or
            relative == "package_verification_report.json" or
            relative == OPTIONAL_NUCLEAR_VIEW or
            relative.endswith((".pyc", ".pyo")))


def check_inventory(root: Path) -> int:
    actual = set()
    def reject_walk_error(error: OSError) -> None:
        raise VerificationError("Cannot inspect the complete package inventory") from error
    # Prune local environments and caches before traversal. Walking a full
    # interpreter installation adds no evidence about the reviewed package.
    for directory, directories, filenames in os.walk(root, followlinks=False, onerror=reject_walk_error):
        parent = Path(directory)
        for name in directories[:]:
            path = parent / name
            relative = path.relative_to(root).as_posix()
            if ignored(relative):
                directories.remove(name)
            else:
                require(not (path.is_symlink() or path.is_junction()),
                        f"Package contains a symbolic link or directory junction: {relative}")
        for name in filenames:
            path = parent / name
            relative = path.relative_to(root).as_posix()
            if not ignored(relative):
                require(not (path.is_symlink() or path.is_junction()),
                        f"Package contains a symbolic link or directory junction: {relative}")
                actual.add(relative)
    require(actual == EXPECTED_FILES,
            f"Inventory mismatch; missing={sorted(EXPECTED_FILES - actual)}, "
            f"unexpected={sorted(actual - EXPECTED_FILES)}")
    return len(actual)


def check_integrity(root: Path) -> int:
    manifest = load_json(root / MANIFEST)
    require(manifest.get("schema_version") == "1.0" and manifest.get("algorithm") == "SHA-256",
            "Unsupported integrity manifest format")
    entries = manifest.get("files", [])
    require(len(entries) == len(EXPECTED_HASHED), "Manifest file count differs from reviewed inventory")
    require(manifest.get("file_count") == len(entries), "Manifest file-count summary mismatch")
    names = [entry.get("path") for entry in entries]
    require(len(set(names)) == len(names) and set(names) == EXPECTED_HASHED,
            "Manifest paths are duplicated or differ from reviewed inventory")
    for entry in entries:
        relative = entry["path"]
        path = safe_path(root, relative)
        data = path.read_bytes()
        require(type(entry.get("size_bytes")) is int and entry["size_bytes"] == len(data),
                f"Size mismatch: {relative}")
        digest = entry.get("sha256", "")
        require(bool(re.fullmatch(r"[0-9a-f]{64}", digest)), f"Invalid checksum: {relative}")
        require(hashlib.sha256(data).hexdigest() == digest, f"SHA-256 mismatch: {relative}")
    return len(entries)


def check_registry(register: dict, application: str) -> dict:
    elements = register.get("elements", [])
    require([e.get("atomic_number") for e in elements] == list(range(1, 139)),
            "Element register must contain ordered atomic numbers 1-138")
    require(len({e.get("symbol") for e in elements}) == 138, "Element symbols are not unique")
    require(all(e.get("name") and e.get("symbol") for e in elements), "Empty element identity")
    require(all(e.get("status") == "recognized_element" for e in elements[:118]),
            "Recognized-element status changed")
    require(all(e.get("status") == "hypothetical_placeholder" for e in elements[118:]),
            "Hypothetical-element status changed")
    require(register.get("element_count_summary") == {
        "records": 138, "recognized": 118, "hypothetical_placeholders": 20,
        "atomic_number_range": [1, 138]}, "Register count summary mismatch")
    particles = register.get("standard_model_particle_categories", {})
    records = particles.get("records", [])
    require(particles.get("category_count") == 17 and len(records) == 17,
            "Particle category count mismatch")
    require(len({p.get("id") for p in records}) == 17, "Particle category identifiers are not unique")
    require(all(p.get("name") and p.get("counting_note") for p in records),
            "Missing particle identity or counting convention")
    section = application.split("## 18 Element and particle register", 1)[1].split("## 19 ", 1)[0]
    rows = re.findall(r"^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", section, re.M)
    require(len(rows) == 138, "Application must print all 138 element register rows")
    for (z, symbol, name, status), expected in zip(rows, elements):
        require((int(z), symbol.strip(), name.strip()) ==
                (expected["atomic_number"], expected["symbol"], expected["name"]),
                f"Application element row disagrees at atomic number {z}")
        require(status.strip() == ("Recognized" if int(z) <= 118 else "Hypothetical placeholder"),
                f"Application element status disagrees at atomic number {z}")
    require(all(p["name"] in section for p in records), "Application omits a particle category")
    return {"element_labels": 138, "recognized_elements": 118, "hypothetical_labels": 20,
            "particle_categories": 17}


def check_claims(application: str, support: dict) -> dict:
    paragraphs = re.findall(r"^\[(\d{4})\]", application, re.M)
    require(paragraphs == [f"{i:04d}" for i in range(1, 81)],
            "Application must contain each numbered paragraph 0001-0080 once, in order")
    matches = re.findall(r"^\*\*Claim (\d+)\.\*\* (.+)$", application, re.M)
    require([int(n) for n, _ in matches] == list(range(1, 200)),
            "Candidate claims must be complete and numbered 1-199")
    entries = support.get("claims", [])
    require(support.get("claim_count") == 199 and len(entries) == 199,
            "Claim support count mismatch")
    require(support.get("source_paragraph_count") == 80, "Support map paragraph count mismatch")
    dependencies = 0
    for (number, text), entry in zip(matches, entries):
        n = int(number)
        require(entry.get("claim_number") == n and entry.get("text") == text,
                f"Support-map text differs from candidate claim {n}")
        require(entry.get("novelty_assessed") is False, f"Novelty-unassessed status changed for claim {n}")
        require(entry.get("category") == ("material" if n <= 185 else "method"),
                f"Claim category mismatch for claim {n}")
        references = entry.get("textual_support_paragraphs", [])
        require(bool(references) and set(references) <= set(paragraphs),
                f"Invalid textual support location for claim {n}")
        require(bool(entry.get("enablement_status")) and bool(entry.get("textual_support_status")),
                f"Missing separate support/enablement statuses for claim {n}")
        for dependency in re.findall(r"\bclaim (\d+)\b", text, re.I):
            require(1 <= int(dependency) < n, f"Invalid dependency in claim {n}: {dependency}")
            dependencies += 1
        if 2 <= n <= 138:
            require(text == f"The material of claim 1, wherein k is exactly {n}.",
                    f"Exact component-count candidate changed at claim {n}")
    require("single-element" in matches[138][1] and "fraction one" in matches[138][1],
            "Unary candidate claim 139 is missing")
    return {"numbered_paragraphs": 80, "candidate_claims": 199,
            "earlier_claim_dependencies_checked": dependencies,
            "claim_specific_novelty_assessments": 0}


def check_working_application(root: Path) -> dict:
    """Check actual edition adoption separately from historical or legal support.

    Retained authoring snapshots bind this PDF to its actual code, without
    pretending that future maintained-tool changes authored an earlier PDF.
    This offline check validates recorded navigation; it does not parse PDFs.
    """
    original = (root / "documents/provisional_application_draft.md").read_text(encoding="utf-8")
    working_bytes = (root / WORKING_SOURCE).read_bytes()
    working = working_bytes.decode("utf-8")
    support = load_json(root / WORKING_MAP)
    proposal = (root / "documents/proposed_claim_clarifications.md").read_text(encoding="utf-8")
    require(support.get("source_path") == WORKING_SOURCE and support.get("source_sha256")
            == hashlib.sha256(working_bytes).hexdigest(), "Working source/map hash differs")
    require(support.get("prepared_date") == "2026-09-30" and support.get("derived_from") == {
        "path": "documents/provisional_application_draft.md",
        "sha256": hashlib.sha256((root / "documents/provisional_application_draft.md").read_bytes()).hexdigest(),
        "repository_baseline": "9cbd8323b2546088c19225143dd23fa38577e4b1",
    }, "Working source derivation differs")
    require(support.get("changed_claims") == sorted(WORKING_CHANGED_CLAIMS)
            and support.get("changed_paragraphs") == sorted(WORKING_CHANGED_PARAGRAPHS),
            "Working change inventory differs")
    def paragraphs(text):
        return dict(re.findall(r"^\[(\d{4})\] (.+)$", text, re.M))

    def claims(text):
        return {int(n): body for n, body in re.findall(r"^\*\*Claim (\d+)\.\*\* (.+)$", text, re.M)}
    old_paragraphs, new_paragraphs = paragraphs(original), paragraphs(working)
    old_claims, new_claims = claims(original), claims(working)
    require(old_paragraphs.keys() == new_paragraphs.keys()
            and {n for n in old_paragraphs if old_paragraphs[n] != new_paragraphs[n]}
            == WORKING_CHANGED_PARAGRAPHS, "Unexpected working paragraph changes")
    require(old_claims.keys() == new_claims.keys()
            and {n for n in old_claims if old_claims[n] != new_claims[n]} == WORKING_CHANGED_CLAIMS,
            "Unexpected working claim changes")
    for n in (169, 191, 192, 193):
        proposed = re.findall(rf"^\*\*Claim {n} - proposed (?:wording|clarification)\.\*\* (.+)$", proposal, re.M)
        require(len(proposed) == 1 and new_claims[n] == proposed[0],
                f"Working claim {n} differs from reviewed proposal")
    proposed_paragraph = re.findall(r"^\*\*\[0047\] - proposed replacement\.\*\* (.+)$", proposal, re.M)
    require(len(proposed_paragraph) == 1 and new_paragraphs["0047"] == proposed_paragraph[0],
            "Working isotope paragraph differs from reviewed proposal")
    claim_result = check_claims(working, support)
    check_registry(load_json(root / "data/entity_register.json"), working)
    historical_map = load_json(root / "data/claim_support_map.json")
    for old_entry, new_entry in zip(historical_map["claims"], support["claims"]):
        permitted = {"text", "textual_support_paragraphs"} if old_entry["claim_number"] in WORKING_CHANGED_CLAIMS else set()
        require({key: value for key, value in old_entry.items() if key not in permitted}
                == {key: value for key, value in new_entry.items() if key not in permitted},
                "Working map silently changed support or physical/legal statuses")
    edition = load_json(root / WORKING_EDITION)
    require(edition.get("prepared_date") == "2026-09-30"
            and edition.get("repository_baseline") == "9cbd8323b2546088c19225143dd23fa38577e4b1"
            and edition.get("filing_asserted") is False
            and edition.get("physical_enablement_certified") is False,
            "Working edition preparation, baseline or factual status differs")
    expected_sources = {WORKING_SOURCE, WORKING_MAP, "documents/drawings/composition_simplex.svg",
                        "documents/drawings/material_record_sequence.svg", *WORKING_AUTHORING}
    entries = edition.get("sources", [])
    require(len(entries) == len(expected_sources) and {entry["path"] for entry in entries} == expected_sources,
            "Working PDF source inventory differs")
    for entry in entries:
        snapshot = WORKING_AUTHORING.get(entry["path"])
        require(entry.get("snapshot_path") == snapshot, "Working authoring snapshot identity differs")
        data = safe_path(root, snapshot or entry["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == entry["sha256"], "Working PDF captured-source hash differs")
    pdf = edition.get("pdf", {})
    require(pdf.get("path") == "documents/pdf/provisional_application_working_2026-09-30.pdf"
            and type(pdf.get("page_count")) is int and pdf["page_count"] > 0, "Invalid working PDF identity")
    pdf_bytes = safe_path(root, pdf["path"]).read_bytes()
    require(len(pdf_bytes) == pdf.get("size_bytes") and hashlib.sha256(pdf_bytes).hexdigest() == pdf.get("sha256"),
            "Working PDF bytes differ from edition record")
    locations = edition.get("location_map", {})
    expected_locations = {f"paragraph_{n:04d}" for n in range(1, 81)} | {f"claim_{n}" for n in range(1, 200)}
    require(locations.keys() == expected_locations
            and all(type(page) is int and 1 <= page <= pdf["page_count"] for page in locations.values()),
            "Working recorded PDF locations differ or are out of bounds")
    require(edition.get("complete_numbered_text_checked") == {"paragraphs": 80, "claims": 199}
            and edition.get("vector_drawings_checked") == 2, "Working recorded content counts differ")
    return {**claim_result, "changed_paragraphs": sorted(WORKING_CHANGED_PARAGRAPHS),
            "changed_claims": sorted(WORKING_CHANGED_CLAIMS), "recorded_pdf_pages": pdf["page_count"],
            "recorded_pdf_locations_checked": len(locations), "captured_sources_checked": len(entries),
            "pdf_parsed_or_appearance_rechecked_by_this_check": False,
            "filing_or_earlier_entitlement_or_enablement_certified": False}


def check_property_application(root: Path) -> dict:
    """Bind the property edition to its source, unchanged claims and actual PDF.

    This separate record preserves the earlier working edition and its captured
    authoring bytes. Recorded text and appearance checks remain authoring
    evidence; this dependency-free verifier does not repeat PDF parsing or QA.
    """
    working_bytes = (root / WORKING_SOURCE).read_bytes()
    working = working_bytes.decode("utf-8")
    property_bytes = (root / PROPERTY_SOURCE).read_bytes()
    application = property_bytes.decode("utf-8")
    support = load_json(root / PROPERTY_MAP)
    require(support.get("source_path") == PROPERTY_SOURCE and support.get("source_sha256")
            == hashlib.sha256(property_bytes).hexdigest(), "Property source/map hash differs")
    require(support.get("prepared_date") == "2026-09-30" and support.get("derived_from") == {
        "path": WORKING_SOURCE,
        "sha256": hashlib.sha256(working_bytes).hexdigest(),
        "repository_baseline": PROPERTY_BASELINE,
    }, "Property source derivation differs")
    require(support.get("changed_paragraphs") == ["0065"] and support.get("changed_claims") == [],
            "Property change inventory differs")

    def paragraphs(text):
        return dict(re.findall(r"^\[(\d{4})\] (.+)$", text, re.M))

    def claims(text):
        return {int(n): body for n, body in re.findall(r"^\*\*Claim (\d+)\.\*\* (.+)$", text, re.M)}

    old_paragraphs, new_paragraphs = paragraphs(working), paragraphs(application)
    require(old_paragraphs.keys() == new_paragraphs.keys()
            and {n for n in old_paragraphs if old_paragraphs[n] != new_paragraphs[n]} == {"0065"},
            "Unexpected property paragraph changes")
    require(claims(working) == claims(application), "Property candidate claims differ from working edition")
    # Paragraph comparisons alone omit headings, tables and unnumbered prose.
    # Permit the identified preface, hydrogel block and edition map reference,
    # preserving other text rather than accepting unrelated additions.
    boundary = "## 1 Technical field\n"
    require(working.count(boundary) == application.count(boundary) == 1,
            "Property edition technical-field boundary differs")
    preface, new_body = application.split(boundary)
    _, old_body = working.split(boundary)
    preface_lines = [line for line in preface.splitlines() if line]
    require(len(preface_lines) == 4 and preface_lines[0]
            == "# Provisional materials disclosure with attributed property evidence - 30 September 2026"
            and preface_lines[1] == "Prepared **30 September 2026** | **Prospective unfiled property-evidence edition** for applicant and patent counsel.",
            "Property edition preface structure differs")
    hydrogel_block = r"^\[0065\] .*?(?=^\[0066\] )"
    require(len(re.findall(hydrogel_block, old_body, re.M | re.S)) == 1
            and len(re.findall(hydrogel_block, new_body, re.M | re.S)) == 1,
            "Property hydrogel-block boundary differs")
    old_map_reference = PurePosixPath(WORKING_MAP).name
    new_map_reference = PurePosixPath(PROPERTY_MAP).name
    require(old_body.count(old_map_reference) == new_body.count(new_map_reference) == 1
            and old_map_reference not in new_body,
            "Property application companion-map reference differs")
    old_body = old_body.replace(old_map_reference, new_map_reference, 1)
    require(re.sub(hydrogel_block, "[0065] ADOPTED HYDROGEL BLOCK\n\n", old_body, flags=re.M | re.S)
            == re.sub(hydrogel_block, "[0065] ADOPTED HYDROGEL BLOCK\n\n", new_body, flags=re.M | re.S),
            "Property source changed outside the preface, paragraph 0065 block or companion-map reference")

    def hydrogel_table(text):
        lines = text.splitlines()
        header = "| DBCO/azide ratio | Linker 2a concentration (µM) | G′ at 37 °C (Pa) | G′ at 5 °C (Pa) |"
        require(lines.count(header) == 1, "Property hydrogel table header differs or is duplicated")
        first = lines.index(header)
        table = []
        for line in lines[first:]:
            if not line.startswith("|"):
                break
            table.append(line)
        require(len(table) == 12, "Property hydrogel table must contain exactly ten data rows")
        return table

    companion = (root / "documents/hydrogel_property_evidence_2026-09-30.md").read_text(encoding="utf-8")
    require(hydrogel_table(application) == hydrogel_table(companion),
            "Property hydrogel table cells, units or row order differ from source companion")
    claim_result = check_claims(application, support)
    check_registry(load_json(root / "data/entity_register.json"), application)
    require(support.get("claims") == load_json(root / WORKING_MAP).get("claims"),
            "Property map silently changed claim support or physical/legal statuses")
    edition = load_json(root / PROPERTY_EDITION)
    require(edition.get("prepared_date") == "2026-09-30"
            and edition.get("repository_baseline") == PROPERTY_BASELINE
            and edition.get("filing_asserted") is False
            and edition.get("physical_enablement_certified") is False,
            "Property edition preparation, baseline or factual status differs")
    expected_sources = {PROPERTY_SOURCE, PROPERTY_MAP, "documents/drawings/composition_simplex.svg",
                        "documents/drawings/material_record_sequence.svg", *PROPERTY_AUTHORING}
    entries = edition.get("sources", [])
    require(len(entries) == len(expected_sources) and {entry["path"] for entry in entries} == expected_sources,
            "Property PDF source inventory differs")
    for entry in entries:
        snapshot = PROPERTY_AUTHORING.get(entry["path"])
        require(entry.get("snapshot_path") == snapshot, "Property authoring snapshot identity differs")
        data = safe_path(root, snapshot or entry["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == entry["sha256"], "Property PDF captured-source hash differs")
    pdf = edition.get("pdf", {})
    require(pdf.get("path") == PROPERTY_PDF and type(pdf.get("page_count")) is int
            and pdf["page_count"] > 0, "Invalid property PDF identity")
    pdf_bytes = safe_path(root, pdf["path"]).read_bytes()
    require(len(pdf_bytes) == pdf.get("size_bytes") and hashlib.sha256(pdf_bytes).hexdigest() == pdf.get("sha256"),
            "Property PDF bytes differ from edition record")
    locations = edition.get("location_map", {})
    expected_locations = {f"paragraph_{n:04d}" for n in range(1, 81)} | {f"claim_{n}" for n in range(1, 200)}
    require(locations.keys() == expected_locations
            and all(type(page) is int and 1 <= page <= pdf["page_count"] for page in locations.values()),
            "Property recorded PDF locations differ or are out of bounds")
    require(edition.get("complete_numbered_text_checked") == {"paragraphs": 80, "claims": 199}
            and edition.get("vector_drawings_checked") == 2, "Property recorded content counts differ")
    require(edition.get("complete_property_table_checked") == {
        "data_rows": 10, "columns": 4, "headers_and_complete_rows_checked_in_order": True,
    }, "Property recorded PDF table checks differ")
    return {**claim_result, "changed_paragraphs": ["0065"], "changed_claims": [],
            "recorded_pdf_pages": pdf["page_count"], "recorded_pdf_locations_checked": len(locations),
            "captured_sources_checked": len(entries), "hydrogel_source_table_data_rows_checked": 10,
            "remaining_application_text_preserved": True,
            "pdf_parsed_or_appearance_rechecked_by_this_check": False,
            "filing_or_earlier_entitlement_or_enablement_certified": False}


def check_preparation_application(root: Path) -> dict:
    """Verify the new preparation edition without relabeling historical PDFs.

    Feed arithmetic has an explicit monomer-only basis. This check binds the
    recorded rendering evidence to bytes; it does not repeat parsing or QA.
    """
    preceding_bytes = (root / PROPERTY_SOURCE).read_bytes()
    source_bytes = (root / PREPARATION_SOURCE).read_bytes()
    preceding, application = preceding_bytes.decode("utf-8"), source_bytes.decode("utf-8")
    support = load_json(root / PREPARATION_MAP)
    require(support.get("source_path") == PREPARATION_SOURCE and support.get("source_sha256")
            == hashlib.sha256(source_bytes).hexdigest(), "Preparation source/map hash differs")
    require(support.get("prepared_date") == "2026-09-30" and support.get("derived_from") == {
        "path": PROPERTY_SOURCE, "sha256": hashlib.sha256(preceding_bytes).hexdigest(),
        "repository_baseline": PREPARATION_BASELINE,
    }, "Preparation source derivation differs")
    require(support.get("changed_paragraphs") == ["0065"] and support.get("changed_claims") == [],
            "Preparation change inventory differs")
    require(support.get("claims") == load_json(root / PROPERTY_MAP).get("claims"),
            "Preparation map changed individual claim records")
    claim_result = check_claims(application, support)
    def claims(text):
        return re.findall(r"^\*\*Claim (\d+)\.\*\* (.+)$", text, re.M)
    require(claims(application) == claims(preceding), "Preparation candidate claims differ from property edition")
    old_paragraphs = dict(re.findall(r"^\[(\d{4})\] (.+)$", preceding, re.M))
    new_paragraphs = dict(re.findall(r"^\[(\d{4})\] (.+)$", application, re.M))
    require(old_paragraphs.keys() == new_paragraphs.keys()
            and {n for n in old_paragraphs if old_paragraphs[n] != new_paragraphs[n]} == {"0065"},
            "Unexpected preparation paragraph changes")
    boundary = "## 1 Technical field\n"
    require(application.count(boundary) == preceding.count(boundary) == 1,
            "Preparation technical-field boundary differs")
    preface, body = application.split(boundary)
    lines = [line for line in preface.splitlines() if line]
    require(len(lines) == 4 and lines[0]
            == "# Provisional materials disclosure with attributed preparation evidence - 30 September 2026"
            and lines[1] == "Prepared **30 September 2026** | **Prospective unfiled preparation-evidence edition** for applicant and patent counsel.",
            "Preparation edition preface differs")
    require(body.count(PREPARATION_HEADING) == 1, "Preparation block is missing or ambiguous")
    block = body.split(PREPARATION_HEADING, 1)[1].split("[0066] ", 1)[0]
    old_body = preceding.split(boundary, 1)[1]
    old_body = old_body.replace("[0065] " + old_paragraphs["0065"], "[0065] " + new_paragraphs["0065"], 1)
    old_reference, new_reference = PurePosixPath(PROPERTY_MAP).name, PurePosixPath(PREPARATION_MAP).name
    require(old_body.count(old_reference) == body.count(new_reference) == 1
            and old_reference not in body, "Preparation companion-map reference differs")
    old_body = old_body.replace(old_reference, new_reference, 1)
    require(body.replace(PREPARATION_HEADING + block, "", 1) == old_body,
            "Preparation source changed outside the identified additions")
    check_registry(load_json(root / "data/entity_register.json"), application)

    review = load_json(root / PREPARATION_REVIEW)
    expected_formulas = {"methoxy_2018": dict(zip("CHNO", (14, 24, 2, 6))),
                         "azide_2018": dict(zip("CHNO", (15, 25, 5, 6))),
                         "four_ethylene_methoxy_counterpart": dict(zip("CHNO", (16, 28, 2, 7)))}
    require(review.get("calculated_neutral_formulas") == expected_formulas
            and review.get("nominal_monomer_feed_umol") == {"methoxy_2018": 790, "azide_2018": 27},
            "Preparation nominal monomer inputs differ")
    amounts = {e: 790 * expected_formulas["methoxy_2018"][e] + 27 * expected_formulas["azide_2018"][e]
               for e in "CHNO"}
    total = sum(amounts.values())
    fractions = {e: str(Fraction(amount, total)) for e, amount in amounts.items()}
    require(review.get("calculated_feed_atom_amount_umol") == amounts
            and review.get("calculated_feed_atomic_fractions") == fractions
            and review.get("ideal_feed_total_atom_amount_umol") == total
            and review.get("azide_monomer_mole_fraction") == "27/817",
            "Preparation feed calculation or basis differs")
    feed_header = "| Element | Ideal feed amount (µmol of atoms) | Exact ideal atomic fraction |"
    table = [feed_header, "| --- | --- | --- |"] + [f"| {e} | {amounts[e]} | {fractions[e]} |" for e in "CHNO"]
    require(application.count("\n".join(table)) == 1, "Preparation feed table differs from calculation")
    monomer_rows = (
        "| 2018 methoxy | CH2CH2-O-CH2CH2-O-CH2CH2-O-CH3 | C14H24N2O6 | 46 |",
        "| 2018 azide | CH2CH2-O-CH2CH2-O-CH2CH2-O-CH2CH2-N3 | C15H25N5O6 | 51 |",
    )
    require(all(application.count(row) == 1 for row in monomer_rows), "Preparation monomer table differs")
    require(all(review.get(key) is False for key in
                ("applicant_experiment_asserted", "physical_enablement_certified", "filing_asserted")),
            "Preparation source factual status differs")
    edition = load_json(root / PREPARATION_EDITION)
    require(edition.get("prepared_date") == "2026-09-30"
            and edition.get("edition_status") == "prospective unfiled preparation-evidence edition"
            and edition.get("repository_baseline") == PREPARATION_BASELINE
            and edition.get("filing_asserted") is False and edition.get("physical_enablement_certified") is False,
            "Preparation edition baseline or factual status differs")
    expected_sources = {PREPARATION_SOURCE, PREPARATION_MAP, PREPARATION_REVIEW, *PREPARATION_AUTHORING,
                        "documents/drawings/composition_simplex.svg", "documents/drawings/material_record_sequence.svg"}
    entries = edition.get("sources", [])
    require(len(entries) == len(expected_sources) and {e["path"] for e in entries} == expected_sources,
            "Preparation PDF source inventory differs")
    for entry in entries:
        snapshot = PREPARATION_AUTHORING.get(entry["path"])
        require(entry.get("snapshot_path") == snapshot, "Preparation authoring snapshot identity differs")
        require(hashlib.sha256(safe_path(root, snapshot or entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
                "Preparation PDF captured-source hash differs")
    pdf = edition.get("pdf", {})
    require(pdf.get("path") == PREPARATION_PDF and type(pdf.get("page_count")) is int
            and pdf["page_count"] > 0, "Invalid preparation PDF identity")
    data = safe_path(root, pdf["path"]).read_bytes()
    require(len(data) == pdf.get("size_bytes") and hashlib.sha256(data).hexdigest() == pdf.get("sha256"),
            "Preparation PDF bytes differ from record")
    locations = edition.get("location_map", {})
    expected_locations = {f"paragraph_{n:04d}" for n in range(1, 81)} | {f"claim_{n}" for n in range(1, 200)}
    require(locations.keys() == expected_locations
            and all(type(p) is int and 1 <= p <= pdf["page_count"] for p in locations.values()),
            "Preparation recorded PDF locations differ")
    require(edition.get("complete_numbered_text_checked") == {"paragraphs": 80, "claims": 199}
            and edition.get("vector_drawings_checked") == 2
            and edition.get("complete_property_table_checked") == {
                "data_rows": 10, "columns": 4, "headers_and_complete_rows_checked_in_order": True},
            "Preparation recorded application content checks differ")
    prose = sum(bool(line.strip()) and not line.startswith("|") for line in block.splitlines())
    rows = sum(line.startswith("|") and not re.fullmatch(r"[|\s-]+", line) for line in block.splitlines())
    require(edition.get("complete_preparation_text_checked") == {
        "complete_prose_blocks": prose, "complete_table_rows_including_headers": rows, "checked_in_order": True},
            "Preparation complete rendered block checks differ")
    visual = edition.get("visual_review", {})
    require(isinstance(visual, dict) and visual.get("status") == "completed"
            and visual.get("pages_reviewed") == list(range(1, pdf["page_count"] + 1))
            and visual.get("remaining_actionable_visual_findings") == 0,
            "Preparation recorded appearance review is incomplete")
    return {**claim_result, "changed_paragraphs": ["0065"], "changed_claims": [],
            "recorded_pdf_pages": pdf["page_count"], "recorded_pdf_locations_checked": len(locations),
            "captured_sources_checked": len(entries), "ideal_feed_fractions_recomputed": fractions,
            "preceding_property_block_and_remaining_body_preserved": True,
            "pdf_parsed_or_appearance_rechecked_by_this_check": False,
            "filing_or_earlier_entitlement_or_enablement_certified": False}


def check_local_links(root: Path) -> int:
    checked = 0
    for relative in EXPECTED_FILES:
        if not relative.endswith(".md"):
            continue
        path = root / relative
        content = path.read_text(encoding="utf-8")
        require("GENERATED_CLAIMS" not in content and "GENERATED_REGISTER" not in content,
                f"Unresolved generation marker: {relative}")
        require(not re.search(r"(?i)(?:[A-Z]:[\\/]Users[\\/]|/Users/|/home/)", content),
                f"Local user-home path in public Markdown: {relative}")
        for target in re.findall(r"!?\[[^\]\n]+\]\(([^)\n]+)\)", content):
            target = target.strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("#"):
                continue
            require(not target.startswith("//"), f"Protocol-relative Markdown target: {relative}")
            destination = (path.parent / unquote(parsed.path)).resolve()
            require(destination.is_relative_to(root.resolve()), f"Markdown link escapes package: {relative}")
            require(destination.is_file(), f"Broken local link in {relative}: {target}")
            checked += 1
    return checked


def no_floats(value) -> bool:
    if isinstance(value, float):
        return False
    if isinstance(value, dict):
        return all(no_floats(v) for v in value.values())
    if isinstance(value, list):
        return all(no_floats(v) for v in value)
    return True


@contextmanager
def module_environment(*directories: Path):
    """Resolve every local import against this package or its test fixture.

    A previously imported module from the original package must never validate
    a changed temporary fixture. Restore the caller's import state afterwards.
    """
    original_path = sys.path[:]
    original_modules = {name: sys.modules[name] for name in MODULE_NAMES if name in sys.modules}
    for name in MODULE_NAMES:
        sys.modules.pop(name, None)
    sys.path[:0] = [str(directory.resolve()) for directory in directories]
    try:
        yield
    finally:
        sys.path[:] = original_path
        for name in MODULE_NAMES:
            sys.modules.pop(name, None)
        sys.modules.update(original_modules)


def import_local(name: str, path: Path):
    require(name in MODULE_NAMES, f"Unreviewed local module: {name}")
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"Could not load local module: {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check_math(root: Path) -> dict:
    directory = root / "range_model"
    with module_environment(directory):
        module = import_local("composition_ranges", directory / "composition_ranges.py")
        for filename, generated in (("composition_range_model.json", module.build_model()),
                                    ("numeric_examples.json", module.build_examples())):
            saved = load_json(directory / filename)
            require(no_floats(saved) and no_floats(generated), f"Inexact binary float in {filename}")
            require(saved == generated, f"Mathematical JSON does not reproduce: {filename}")
        report = module.verify()
    require(report.get("status") == "passed" and report.get("test_group_count") == 27,
            "Exact range verifier did not pass all 27 finite groups")
    require(report == load_json(root / RANGE_REPORT), "Recorded range verification report differs from fresh result")
    return {"mathematical_json_artifacts_reproduced": 2, "range_test_groups_passed": 27,
            "recorded_range_report_reproduced": True,
            "scope": "Executable positive floor 10^-19; not exhaustive physical or broader symbolic-domain validation."}


def check_unrestricted_math(root: Path) -> dict:
    directory = root / "range_model"
    with module_environment(directory):
        import_local("composition_ranges", directory / "composition_ranges.py")
        unrestricted = import_local("unrestricted_compositions", directory / "unrestricted_compositions.py")
        for filename, generated in (
            ("unrestricted_composition_model.json", unrestricted.model()),
            ("unrestricted_numeric_examples.json", unrestricted.examples()),
        ):
            saved = load_json(directory / filename)
            require(no_floats(saved) and no_floats(generated), f"Inexact binary float in {filename}")
            require(saved == generated, f"Unrestricted mathematical JSON does not reproduce: {filename}")
        report = unrestricted.verify()
        require(report.get("status") == "passed" and report.get("test_group_count") == 11,
                "Unrestricted verifier must pass all 11 reviewed finite groups")
        require(report.get("exhaustive_unbounded_domain_tested") is False,
                "Unbounded exhaustive testing is not established")
        require(report == load_json(directory / "unrestricted_verification_report.json"),
                "Recorded unrestricted verification report differs from fresh result")
        independent = import_local("independent_unrestricted_checks", directory / "independent_unrestricted_checks.py")
        # The independent checker must resolve the same fixture modules rather
        # than a sibling staging directory or cached original package module.
        require(independent.target is unrestricted, "Independent checker imported a different unrestricted module")
        independent_report = independent.run()
        require(no_floats(independent_report) and independent_report.get("status") == "passed",
                "Independent unrestricted checks did not pass with exact results")
        require(independent_report == load_json(directory / "independent_unrestricted_report.json"),
                "Recorded independent unrestricted report differs from fresh result")
        trace = import_local("trace_sampling_calculations", directory / "trace_sampling_calculations.py")
        trace_report = trace.calculate()
        require(no_floats(trace_report), "Inexact binary float in trace accounting report")
        require(trace_report == load_json(directory / "trace_sampling_report.json"),
                "Recorded trace sampling report differs from fresh calculation")
    return {
        "mathematical_json_artifacts_reproduced": 2,
        "test_groups_passed": 11,
        "independent_report_reproduced": True,
        "independent_case_counts": {
            key: value for key, value in independent_report.items()
            if type(value) is int and key != "seed"
        },
        "trace_sampling_report_reproduced": True,
        "imposed_positive_coordinate_floor": None,
        "unbounded_domain_exhaustively_tested": False,
        "scope": "Exact rational feasibility, finite count compatibility and stated idealized sampling models; no preparation, detection performance or patent effect certified.",
    }


def check_claim_clarifications(root: Path) -> dict:
    """Reproduce the scoped claim-proposal mathematics from this exact fixture."""
    directory = root / "range_model"
    with module_environment(directory):
        import_local("composition_ranges", directory / "composition_ranges.py")
        unrestricted = import_local("unrestricted_compositions", directory / "unrestricted_compositions.py")
        checker = import_local("claim_clarification_checks", directory / "claim_clarification_checks.py")
        require(checker.target is unrestricted, "Claim checker imported a different unrestricted module")
        report = checker.verify()
    require(no_floats(report) and report.get("status") == "passed",
            "Claim-clarification checks did not pass with exact results")
    require(report == load_json(directory / "claim_clarification_report.json"),
            "Recorded claim-clarification report differs from fresh result")
    return {"recorded_report_reproduced": True, **report}


def check_nuclear_archive(root: Path) -> dict:
    directory = root / NUCLEAR_DIRECTORY
    bundle = load_json(directory / "portable_bundle_manifest.json")
    entries = bundle.get("files", [])
    expected_names = NUCLEAR_FILES - {"portable_bundle_manifest.json"}
    require(bundle.get("schema_version") == 1 and bundle.get("file_count") == len(expected_names),
            "Nuclear portable manifest format/count changed")
    require(len(entries) == len(expected_names) and {entry.get("path") for entry in entries} == expected_names,
            "Nuclear portable manifest inventory differs from the reviewed source bundle")
    total_bytes = 0
    for entry in entries:
        data = safe_path(directory, entry["path"]).read_bytes()
        require(type(entry.get("bytes")) is int and len(data) == entry["bytes"],
                f"Nuclear portable bundle byte count changed: {entry['path']}")
        require(hashlib.sha256(data).hexdigest() == entry.get("sha256"),
                f"Nuclear portable bundle checksum mismatch: {entry['path']}")
        total_bytes += len(data)
    require(total_bytes == bundle.get("total_bytes"), "Nuclear portable bundle byte summary mismatch")
    optional = bundle.get("optional_generated_normalized_json", {})
    require(optional.get("path") == "nuclear_states.json" and optional.get("excluded_from_required_bundle") is True,
            "Large normalized nuclear view must remain optional and excluded from this reviewed inventory")
    with module_environment(directory):
        parser = import_local("parse_nubase", directory / "parse_nubase.py")
        verifier = import_local("verify_nuclear_archive", directory / "verify_nuclear_archive.py")
        payload, generated_schema, generated_counts, generated_header = parser.parse_snapshot()
        source_bytes = (directory / "nubase_4.mas20.txt").read_bytes()
        require(generated_schema == load_json(directory / "column_schema.json"), "Nuclear column schema does not reproduce")
        require(generated_counts == load_json(directory / "archive_counts.json"), "Nuclear archive counts do not reproduce")
        require(generated_header == (directory / "schema_header.txt").read_bytes(), "Nuclear raw header does not reproduce")
        require(no_floats(payload), "Nuclear parsed numeric tokens must retain exact decimal strings")
        optional_path = safe_path(root, OPTIONAL_NUCLEAR_VIEW)
        optional_present = optional_path.exists()
        if optional_present:
            require(optional_path.is_file() and not optional_path.is_symlink(),
                    "Optional nuclear view must be a regular file within this package")
            optional_bytes = optional_path.read_bytes()
            require(type(optional.get("bytes")) is int and len(optional_bytes) == optional["bytes"],
                    "Optional nuclear view byte count differs from its reviewed manifest record")
            require(hashlib.sha256(optional_bytes).hexdigest() == optional.get("sha256"),
                    "Optional nuclear view checksum differs from its reviewed manifest record")
            require(json.loads(optional_bytes) == payload,
                    "Optional nuclear view differs from fresh source parsing")
        report = verifier.verify_payload(payload, generated_schema, source_bytes)
        report["manual_sample_ids"] = verifier.sample_checks(payload)
        report["deliberate_defects_rejected"] = verifier.negative_checks(payload, generated_schema, source_bytes)
        report["source_bytes"] = len(source_bytes)
        report["source_sha256"] = verifier.EXPECTED_SHA
        report["result"] = "pass"
        report["scope"] = "faithful dated ASCII archive and conservative parsing, not physical enablement or current/future completeness"
        require(report == load_json(directory / "verification_report.json"), "Recorded nuclear verification report differs from fresh result")
        metadata = load_json(directory / "source_metadata.json")
        require(metadata.get("source_sha256") == report["source_sha256"] and metadata.get("source_bytes") == len(source_bytes),
                "Nuclear source metadata hash/size mismatch")
        require(metadata.get("source_state_record_count") == report["record_count"] and
                metadata.get("source_unique_A_Z_nuclide_count") == report["unique_nuclides"],
                "Nuclear source metadata identity counts mismatch")
        require(metadata.get("ascii_snapshot_scientific_cutoff_date") is None and
                metadata.get("paper_stated_experimental_data_availability_boundary") == "2020-10-30" and
                metadata.get("maximum_reported_discovery_year") == generated_counts["discovery_year_maximum"] == 2021,
                "Nuclear snapshot chronology was silently replaced by the paper cutoff")
        require(metadata.get("paper_license") == "CC BY 3.0" and bool(metadata.get("license_scope_note")),
                "Nuclear publication license/companion-file distinction is missing")
    return {
        "source_records_verified_in_memory": report["record_count"],
        "unique_source_nuclides": report["unique_nuclides"],
        "source_sha256": report["source_sha256"],
        "source_bytes": len(source_bytes),
        "portable_manifest_files_verified": len(entries),
        "recorded_report_reproduced": True,
        "deliberate_archive_defects_rejected": len(report["deliberate_defects_rejected"]),
        "optional_normalized_view_present_and_verified": optional_present,
        "normalized_json_written": False,
        "scope": "Every row/byte of this dated source snapshot; no all-current/future-state coverage, observation classification or physical preparation certified.",
    }


def check_particle_archive(root: Path) -> dict:
    directory = root / PARTICLE_DIRECTORY
    with module_environment(directory):
        verifier = import_local("extract_pdg_identities", directory / "extract_pdg_identities.py")
        captured = io.StringIO()
        # The recorded source comparison used a raw SQLite scratch download.
        # CI verifies the portable JSON offline, with that stronger provenance
        # preserved as history rather than presented as a fresh database check.
        with redirect_stdout(captured):
            verifier.verify(argparse.Namespace(archive_directory=directory, database=None, report=None))
        fresh = json.loads(captured.getvalue())
        require(fresh.get("passed") is True, "Portable particle archive verification failed")
        recorded = load_json(directory / "verification_report.json")
        for key in ("archive_sha256", "archive_bytes", "exported_row_counts",
                    "physical_existence_assessments_performed", "patent_enablement_assessed"):
            require(fresh.get(key) == recorded.get(key), f"Particle recorded report differs for {key}")
        require(fresh.get("physical_existence_assessments_performed") == 0 and
                fresh.get("patent_enablement_assessed") is False,
                "Particle identities were promoted to physical or patent determinations")
        require(fresh.get("source_comparison", "").startswith("not run;"),
                "Offline particle check must not claim a raw SQLite comparison")
        require(recorded.get("source_comparison", "").startswith("passed:"),
                "Previously recorded particle source comparison is missing")
        adversarial = load_json(directory / "adversarial_verification_report.json")
        require(adversarial.get("passed") is True and adversarial.get("checks_count") == 6 and
                len(adversarial.get("checks", [])) == 6 and all(check.get("passed") is True for check in adversarial["checks"]),
                "Recorded particle adversarial evidence is inconsistent")
    return {
        "offline_portable_archive_verified": True,
        "exported_row_counts": fresh["exported_row_counts"],
        "archive_sha256": fresh["archive_sha256"],
        "raw_sqlite_compared_by_this_script": False,
        "previous_source_comparison_record_preserved": True,
        "recorded_adversarial_checks": adversarial["checks_count"],
        "physical_existence_assessments_performed": 0,
        "scope": "Pinned edition identity/name data and internal integrity, not particle discovery, bulk material preparation or patent enablement.",
    }


def check_publication_record(root: Path) -> dict:
    observation = load_json(root / "data/publication_observation.json")
    require(observation.get("repository") == "RobertMLayne/all-materials-patent" and
            observation.get("source_url") == "https://github.com/RobertMLayne/all-materials-patent",
            "Publication observation repository changed")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", observation.get("sha", ""))), "Invalid observed public commit identity")
    require(observation.get("ref") == "refs/heads/main" and bool(observation.get("observation_time_utc")),
            "Publication observation lacks its version/time")
    require(observation.get("earliest_public_availability_certified") is False and
            observation.get("filing_asserted") is False and observation.get("public_access_browser_observed") is True,
            "Publication observation was promoted to an earliest-date or filing certification")
    return {"record_consistency_checked": True, "external_access_rechecked_by_this_script": False,
            "earliest_public_availability_certified": False, "filing_asserted": False}


def check_workflow(root: Path) -> None:
    content = (root / ".github/workflows/verify.yml").read_text(encoding="utf-8")
    for fragment in ("permissions:\n  contents: read", "timeout-minutes: 10",
                     "cancel-in-progress: true", "python-version: '3.12'",
                     "os: [ubuntu-24.04, windows-2025]", "fail-fast: false",
                     "persist-credentials: false", "run: python -B verify_package.py --self-test",
                     "run: python -m ruff check --no-cache .",
                     "run: python -B tools/pdf/test_pdf_outputs.py"):
        require(fragment in content, f"Reviewed workflow control missing: {fragment}")
    # SHA syntax is checked here; release identities are reviewed before a
    # manifest update. This permits reviewed Dependabot pin updates.
    for relative in (".github/workflows/verify.yml", ".github/workflows/codeql.yml", ".github/workflows/copilot-setup-steps.yml"):
        workflow = (root / relative).read_text(encoding="utf-8")
        require("pull_request_target" not in workflow, f"Privileged PR trigger in {relative}")
        references = re.findall(r"uses:\s*(\S+)", workflow)
        require(bool(references) and all(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+@[0-9a-f]{40}", ref)
                                         for ref in references), f"Unpinned action in {relative}")


def check_review_packet(root: Path) -> dict:
    """Reject stale linked sources and inconsistent recorded navigation.

    Source freshness is separate from refreshing the package hash manifest.
    These offline checks do not extract or render PDFs; the recorded counts
    and appearance findings are review evidence, not independently measured
    page counts or a physical/legal enablement conclusion.
    """
    record = load_json(root / REVIEW_PACKET)
    require(type(record.get("schema_version")) is int and record.get("schema_version") == 1 and
            record.get("status") == "review_only_unfiled",
            "Review-packet version/status changed without supported review")
    # This is a fixed reviewed edition, not a freely mutable date label.
    # A refreshed outer manifest must not conceal changed preparation history.
    require(record.get("prepared_date") == REVIEW_PREPARED_DATE,
            "Review-packet preparation date differs from the reviewed edition")
    sources = record.get("sources")
    require(isinstance(sources, list) and all(isinstance(entry, dict) for entry in sources),
            "Review source records must be a list of objects")
    names = [entry.get("path") for entry in sources]
    require(all(isinstance(name, str) for name in names) and
            len(names) == len(REVIEW_SOURCE_FILES) and set(names) == REVIEW_SOURCE_FILES,
            "Review packet must link every exact included source once")
    for entry in sources:
        payload = safe_path(root, entry["path"]).read_bytes()
        require(entry.get("bytes") == len(payload) and entry.get("sha256") == hashlib.sha256(payload).hexdigest(),
                f"Review PDF source is stale: {entry['path']}; prepare and review a new edition")
    artifacts = record.get("artifacts")
    require(isinstance(artifacts, list) and all(isinstance(entry, dict) for entry in artifacts),
            "Review artifact records must be a list of objects")
    expected_artifacts = {
        "documents/pdf/materials_provisional_review_2026-09-30.pdf": 66,
        "documents/pdf/materials_identity_data_review_annex.pdf": 795,
    }
    require(len(artifacts) == 2 and {entry.get("path") for entry in artifacts} == set(expected_artifacts),
            "Review-packet artifact identities changed")
    for entry in artifacts:
        payload = safe_path(root, entry["path"]).read_bytes()
        require(entry.get("bytes") == len(payload) and entry.get("sha256") == hashlib.sha256(payload).hexdigest(),
                f"Review-packet artifact differs: {entry['path']}")
        require(entry.get("review_pages") == expected_artifacts[entry["path"]],
                "Recorded review page count changed; inspect and record the new edition")
    core = record.get("core", {})
    require(isinstance(core, dict), "Core review record must be an object")
    for role, relative in REVIEW_AUTHORING_FILES.items():
        # Preserve the actual authoring bytes separately from maintained tools;
        # later tool fixes cannot silently revise this artifact provenance.
        require(core.get(f"authoring_{role}_path") == relative,
                f"Core authoring {role} must identify its exact retained snapshot")
        payload = safe_path(root, relative).read_bytes()
        require(core.get(f"authoring_{role}_sha256") == hashlib.sha256(payload).hexdigest(),
                f"Core authoring {role} hash differs from retained bytes")
    require(core.get("front_matter_pages") == 2 and core.get("original_numbered_paragraphs") == 80 and
            core.get("candidate_claims") == 199 and core.get("original_application_pages_preserved") == 27,
            "Recorded original-application preservation counts changed")
    parts = core.get("parts", [])
    require(isinstance(parts, list) and all(isinstance(part, dict) for part in parts) and
            [part.get("label") for part in parts] == list("ABCDEF"), "Core part map changed")
    last = 2
    for part in parts:
        first, end, count = (part.get(key) for key in ("physical_start", "physical_end", "page_count"))
        require(all(type(number) is int for number in (first, end, count)) and
                first == last + 1 and end >= first and count == end - first + 1,
                "Core recorded page map has a gap, overlap or inconsistent count")
        last = end
    require(last == 66 and parts[0]["page_count"] == 27, "Core recorded page map does not cover this edition")
    expected_sections = {
        "scope": 12, "register-context": 2, "elements": 138, "particle-categories": 17,
        "nuclear-provenance": 4, "nuclear-schema": 2, "nuclear-rows": 5843,
        "pdg-provenance": 3, "pdginfo": 10, "pdgparticle": 1170, "pdgid": 450,
        "pdgitem": 3270, "pdgitem_map": 1341, "pdgdoc": 71,
    }
    sections = record.get("annex", {}).get("sections", [])
    require(isinstance(sections, list) and all(isinstance(section, dict) for section in sections) and
            [section.get("key") for section in sections] == list(expected_sections), "Annex selection/page map changed")
    last = 0
    for section in sections:
        first, end = section.get("first_page"), section.get("last_page")
        require(type(first) is int and type(end) is int and first == last + 1 and end >= first,
                "Annex recorded page map has a gap or overlap")
        require(section.get("printed_record_count") == expected_sections[section["key"]],
                "Recorded annex selection count differs from the reviewed source scope")
        last = end
    require(last == 795, "Annex recorded page map does not cover this edition")
    return {"source_hash_links_checked": len(sources), "artifact_hash_links_checked": len(artifacts),
            "recorded_page_maps_checked": 2, "authoring_source_hash_links_checked": 2,
            "prepared_date_checked": REVIEW_PREPARED_DATE,
            "pdf_pages_independently_parsed_by_this_check": False,
            "appearance_rechecked_by_this_check": False, "filing_or_enablement_certified": False}


def run(root: Path) -> dict:
    require(__debug__, "Verification requires enabled assertions; run Python without -O, -OO or PYTHONOPTIMIZE.")
    file_count = check_inventory(root)
    hashed = check_integrity(root)
    application = (root / "documents/provisional_application_draft.md").read_text(encoding="utf-8")
    claim_result = check_claims(application, load_json(root / "data/claim_support_map.json"))
    working_result = check_working_application(root)
    property_result = check_property_application(root)
    preparation_result = check_preparation_application(root)
    registry_result = check_registry(load_json(root / "data/entity_register.json"), application)
    links = check_local_links(root)
    for relative in EXPECTED_HASHED:
        if relative.endswith(".pdf"):
            data = (root / relative).read_bytes()
            require(data.startswith(b"%PDF-") and b"%%EOF" in data[-1024:], f"Invalid PDF envelope: {relative}")
    math_result = check_math(root)
    unrestricted_result = check_unrestricted_math(root)
    clarification_result = check_claim_clarifications(root)
    nuclear_result = check_nuclear_archive(root)
    particle_result = check_particle_archive(root)
    publication_result = check_publication_record(root)
    review_result = check_review_packet(root)
    check_workflow(root)
    return {"status": "passed", "package_files": file_count, "sha256_records_checked": hashed,
            **claim_result, **registry_result, "local_markdown_links_checked": links, **math_result,
            "unrestricted_domain_verification": unrestricted_result,
            "claim_clarification_verification": clarification_result,
            "working_application_edition_verification": working_result,
            "property_application_edition_verification": property_result,
            "preparation_application_edition_verification": preparation_result,
            "dated_nuclear_archive_verification": nuclear_result,
            "dated_particle_archive_verification": particle_result,
            "publication_observation_verification": publication_result,
            "review_packet_source_and_navigation_verification": review_result,
            "pdf_binary_integrity_checked": sum(path.endswith(".pdf") for path in EXPECTED_HASHED),
            "pdf_layout_rechecked_by_this_script": False,
            "workflow_controls_checked": True, "github_actions_run_observed": False,
            "supplied_artifacts_modified_by_verifier": 0,
            "limitations": ["Checksums are not authentication or a trusted publication timestamp.",
                            "No patent filing, universal prior-art effect, novelty or physical enablement is certified."]}


def self_test(root: Path) -> dict:
    """Exercise failure paths using temporary copies; preserve the package."""
    require(__debug__, "Verification requires enabled assertions; run Python without -O, -OO or PYTHONOPTIMIZE.")
    import shutil
    import subprocess
    from unittest.mock import patch
    import uuid

    caught = []
    extended = []
    scratch = root / "generated_reports"
    require(scratch.resolve().is_relative_to(root.resolve()) and not scratch.is_symlink(),
            "Self-test scratch directory must stay inside this package")
    scratch.mkdir(exist_ok=True)
    @contextmanager
    def temporary_fixture():
        # Default directory permissions are portable to managed Windows hosts.
        directory = scratch / ("self-test-" + uuid.uuid4().hex)
        require(directory.resolve().is_relative_to(scratch.resolve()), "Unsafe scratch path")
        directory.mkdir()
        try:
            yield directory
        finally:
            require(directory.resolve().is_relative_to(scratch.resolve()), "Unsafe cleanup path")
            shutil.rmtree(directory)

    with temporary_fixture() as temporary:
        fixture = Path(temporary) / "package"
        shutil.copytree(root, fixture, ignore=shutil.ignore_patterns(".git", "__pycache__", "generated_reports", ".venv", ".ruff_cache"))
        # Reject a stale starting fixture so a test cannot pass by catching an
        # unrelated, pre-existing checksum or inventory failure.
        check_inventory(fixture)
        check_integrity(fixture)
        check_review_packet(fixture)

        # A refreshed global integrity record must not conceal a PDF whose
        # linked source is older. Exercise this separate provenance boundary.
        review_path = fixture / REVIEW_PACKET
        review_original = review_path.read_bytes()
        manifest_path = fixture / MANIFEST
        manifest_original = manifest_path.read_bytes()
        linked = fixture / "documents/reference_entry_support.md"
        linked_original = linked.read_bytes()
        linked.write_bytes(linked_original + b"\nNew unresolved preparation field.\n")
        refreshed = json.loads(manifest_original)
        for entry in refreshed["files"]:
            if entry["path"] == "documents/reference_entry_support.md":
                entry["size_bytes"] = linked.stat().st_size
                entry["sha256"] = hashlib.sha256(linked.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(refreshed), encoding="utf-8")
        check_integrity(fixture)
        try:
            check_review_packet(fixture)
        except VerificationError as error:
            require("source is stale" in str(error), "Stale review-source test failed for an unrelated reason")
            extended.append("stale_review_source_after_integrity_refresh_rejected")
        finally:
            linked.write_bytes(linked_original)
            manifest_path.write_bytes(manifest_original)
        require("stale_review_source_after_integrity_refresh_rejected" in extended,
                "A refreshed integrity record concealed a stale review source")

        # Retained authoring bytes are an independent provenance link. A
        # maintenance refresh must not approve an altered historical builder.
        for role, relative in REVIEW_AUTHORING_FILES.items():
            historical = fixture / relative
            historical_original = historical.read_bytes()
            historical.write_bytes(historical_original + b"\n# Deliberate historical-source defect.\n")
            refreshed = json.loads(manifest_original)
            for entry in refreshed["files"]:
                if entry["path"] == relative:
                    payload = historical.read_bytes()
                    entry["size_bytes"] = len(payload)
                    entry["sha256"] = hashlib.sha256(payload).hexdigest()
            manifest_path.write_text(json.dumps(refreshed), encoding="utf-8")
            check_integrity(fixture)
            case = f"review_retained_{role}_drift_after_integrity_refresh_rejected"
            try:
                check_review_packet(fixture)
            except VerificationError as error:
                require(f"{role} hash" in str(error), f"Authoring-byte test failed for an unrelated reason: {role}")
                extended.append(case)
            finally:
                historical.write_bytes(historical_original)
                manifest_path.write_bytes(manifest_original)
            require(case in extended, f"Altered retained authoring {role} was accepted")

        review_defects = (
            ("review_preparation_date_changed_rejected", ("prepared_date",), "2026-09-29", "preparation date"),
            ("review_preparation_date_null_rejected", ("prepared_date",), None, "preparation date"),
            ("review_builder_hash_changed_rejected", ("core", "authoring_builder_sha256"), "0" * 64, "builder hash"),
            ("review_builder_path_changed_rejected", ("core", "authoring_builder_path"),
             "tools/pdf/build_consolidated_review.py", "retained snapshot"),
            ("review_helper_hash_changed_rejected", ("core", "authoring_helper_sha256"), "0" * 64, "helper hash"),
            ("review_status_promoted_to_filed_rejected", ("status",), "filed", "status"),
            ("review_core_page_overlap_rejected", ("core", "parts", 1, "physical_start"), 29, "gap, overlap"),
            ("review_annex_row_loss_rejected", ("annex", "sections", 6, "printed_record_count"), 5842, "selection count"),
        )
        for case, address, value, expected_error in review_defects:
            changed = json.loads(review_original)
            destination = changed
            for key in address[:-1]:
                destination = destination[key]
            destination[address[-1]] = value
            review_path.write_text(json.dumps(changed), encoding="utf-8")
            refreshed = json.loads(manifest_original)
            for entry in refreshed["files"]:
                if entry["path"] == REVIEW_PACKET:
                    payload = review_path.read_bytes()
                    entry["size_bytes"] = len(payload)
                    entry["sha256"] = hashlib.sha256(payload).hexdigest()
            manifest_path.write_text(json.dumps(refreshed), encoding="utf-8")
            check_integrity(fixture)
            try:
                check_review_packet(fixture)
            except VerificationError as error:
                require(expected_error in str(error), f"Review failure case caught an unrelated error: {case}")
                extended.append(case)
            finally:
                review_path.write_bytes(review_original)
                manifest_path.write_bytes(manifest_original)
            require(case in extended, f"Review-packet defect was not rejected: {case}")

        changed = json.loads(review_original)
        del changed["prepared_date"]
        review_path.write_text(json.dumps(changed), encoding="utf-8")
        refreshed = json.loads(manifest_original)
        for entry in refreshed["files"]:
            if entry["path"] == REVIEW_PACKET:
                payload = review_path.read_bytes()
                entry["size_bytes"] = len(payload)
                entry["sha256"] = hashlib.sha256(payload).hexdigest()
        manifest_path.write_text(json.dumps(refreshed), encoding="utf-8")
        check_integrity(fixture)
        try:
            check_review_packet(fixture)
        except VerificationError as error:
            require("preparation date" in str(error), "Missing preparation-date test failed for an unrelated reason")
            extended.append("review_preparation_date_missing_rejected")
        finally:
            review_path.write_bytes(review_original)
            manifest_path.write_bytes(manifest_original)
        require("review_preparation_date_missing_rejected" in extended, "Missing preparation date was accepted")

        changed = json.loads(review_original)
        changed["sources"].pop()
        review_path.write_text(json.dumps(changed), encoding="utf-8")
        try:
            check_review_packet(fixture)
        except VerificationError as error:
            require("every exact included source" in str(error), "Missing source test failed for an unrelated reason")
            extended.append("review_missing_source_link_rejected")
        finally:
            review_path.write_bytes(review_original)
        require("review_missing_source_link_rejected" in extended, "Missing review source link was accepted")
        # An optimized subprocess must fail before claiming that assertion-based
        # math checks passed. It receives no self-test flag, preventing recursion.
        optimized = subprocess.run(
            [sys.executable, "-B", "-O", str(fixture / "verify_package.py")],
            cwd=fixture, capture_output=True, text=True, timeout=30, check=False,
        )
        require(optimized.returncode == 1, "Optimized interpreter did not reject verification")
        optimized_error = json.loads(optimized.stderr)
        require(optimized_error.get("status") == "failed" and
                "requires enabled assertions" in optimized_error.get("error", ""),
                "Optimized interpreter failed for an unrelated reason")
        sample = fixture / "README.md"
        original = sample.read_bytes()
        sample.write_bytes(original + b"\nchanged\n")
        try:
            check_integrity(fixture)
        except VerificationError:
            caught.append("changed_artifact_rejected")
        sample.write_bytes(original)
        extra = fixture / "unreviewed_private_inventory.txt"
        extra.write_text("fixture", encoding="utf-8")
        try:
            check_inventory(fixture)
        except VerificationError:
            caught.append("unreviewed_extra_file_rejected")
        extra.unlink()
        sample.unlink()
        try:
            check_inventory(fixture)
        except VerificationError:
            caught.append("missing_artifact_rejected")
        sample.write_bytes(original)
        report_path = fixture / RANGE_REPORT
        report_original = report_path.read_bytes()
        report = json.loads(report_original)
        report["test_group_count"] = 26
        report_path.write_text(json.dumps(report), encoding="utf-8")
        try:
            check_math(fixture)
        except VerificationError:
            caught.append("unhashed_report_drift_rejected")
        report_path.write_bytes(report_original)
        clarification_path = fixture / "range_model/claim_clarification_report.json"
        clarification_original = clarification_path.read_bytes()
        clarification_report = json.loads(clarification_original)
        clarification_report["status"] = "not run"
        clarification_path.write_text(json.dumps(clarification_report), encoding="utf-8")
        try:
            check_claim_clarifications(fixture)
        except VerificationError as error:
            require("differs from fresh result" in str(error),
                    "Claim-report drift fixture failed for an unrelated reason")
            extended.append("claim_clarification_report_drift_rejected")
        clarification_path.write_bytes(clarification_original)
        working_map_path = fixture / WORKING_MAP
        working_map_original = working_map_path.read_bytes()
        working_map = json.loads(working_map_original)
        working_map["source_sha256"] = "0" * 64
        working_map_path.write_text(json.dumps(working_map), encoding="utf-8")
        try:
            check_working_application(fixture)
        except VerificationError as error:
            require("Working source/map hash differs" in str(error), "Working-map fixture failed for another reason")
            extended.append("working_source_map_drift_rejected")
        working_map_path.write_bytes(working_map_original)
        working_source_path = fixture / WORKING_SOURCE
        working_source_original = working_source_path.read_bytes()
        working_source = working_source_original.decode("utf-8")
        marker = "**Claim 169.** The material of claim 1, wherein each selected element i has a conditional atom-count"
        require(working_source.count(marker) == 1, "Working isotope mutation fixture lost its target")
        altered = working_source.replace(marker, marker.replace("atom-count", "mass"))
        working_source_path.write_text(altered, encoding="utf-8", newline="\n")
        working_map = json.loads(working_map_original)
        working_map["claims"][168]["text"] = working_map["claims"][168]["text"].replace("conditional atom-count", "conditional mass", 1)
        working_map["source_sha256"] = hashlib.sha256(working_source_path.read_bytes()).hexdigest()
        working_map_path.write_text(json.dumps(working_map), encoding="utf-8")
        try:
            check_working_application(fixture)
        except VerificationError as error:
            require("Working claim 169 differs from reviewed proposal" in str(error),
                    "Wrong-basis fixture failed for another reason")
            extended.append("working_isotope_basis_drift_rejected_after_consistent_map_update")
        working_source_path.write_bytes(working_source_original)
        working_map_path.write_bytes(working_map_original)
        property_source_path = fixture / PROPERTY_SOURCE
        property_source_original = property_source_path.read_bytes()
        property_map_path = fixture / PROPERTY_MAP
        property_map_original = property_map_path.read_bytes()
        # Editing this application source cannot silently re-use a map from the
        # previous bytes, even when a general package manifest is not consulted.
        property_source_path.write_bytes(property_source_original + b"\nUnadopted source addition.\n")
        try:
            check_property_application(fixture)
        except VerificationError as error:
            require("Property source/map hash differs" in str(error),
                    "Property source-drift fixture failed for another reason")
            extended.append("property_source_map_drift_rejected")
        finally:
            property_source_path.write_bytes(property_source_original)
        require("property_source_map_drift_rejected" in extended, "Stale property source map was accepted")

        # Keep the edited claim and map mutually consistent. The independent
        # adoption boundary must still reject expansion of unchanged claim 1.
        property_source = property_source_original.decode("utf-8")
        marker = "**Claim 1.** "
        claim_lines = re.findall(r"^\*\*Claim 1\.\*\* (.+)$", property_source, re.M)
        require(len(claim_lines) == 1 and claim_lines[0].count("positive normalized fraction") == 1,
                "Property claim-mutation fixture lost its target")
        altered_claim = claim_lines[0].replace("positive normalized fraction", "nonnegative normalized fraction", 1)
        altered_source = property_source.replace(marker + claim_lines[0], marker + altered_claim, 1)
        property_source_path.write_text(altered_source, encoding="utf-8", newline="\n")
        property_map = json.loads(property_map_original)
        property_map["claims"][0]["text"] = altered_claim
        property_map["source_sha256"] = hashlib.sha256(property_source_path.read_bytes()).hexdigest()
        property_map_path.write_text(json.dumps(property_map), encoding="utf-8")
        try:
            check_property_application(fixture)
        except VerificationError as error:
            require("Property candidate claims differ from working edition" in str(error),
                    "Property changed-claim fixture failed for another reason")
            extended.append("property_claim_drift_rejected_after_consistent_map_update")
        finally:
            property_source_path.write_bytes(property_source_original)
            property_map_path.write_bytes(property_map_original)
        require("property_claim_drift_rejected_after_consistent_map_update" in extended,
                "A consistently updated property map concealed an altered claim")
        table_row = "| 1.25 | 65.1 | 184 | 95 |\n"
        require(property_source.count(table_row) == 1, "Property table-mutation fixture lost its target")
        property_source_path.write_text(property_source.replace(table_row, "", 1), encoding="utf-8", newline="\n")
        property_map = json.loads(property_map_original)
        property_map["source_sha256"] = hashlib.sha256(property_source_path.read_bytes()).hexdigest()
        property_map_path.write_text(json.dumps(property_map), encoding="utf-8")
        try:
            check_property_application(fixture)
        except VerificationError as error:
            require("Property hydrogel table must contain exactly ten data rows" in str(error),
                    "Property missing-table-row fixture failed for another reason")
            extended.append("property_table_row_loss_rejected_after_consistent_map_update")
        finally:
            property_source_path.write_bytes(property_source_original)
            property_map_path.write_bytes(property_map_original)
        require("property_table_row_loss_rejected_after_consistent_map_update" in extended,
                "A consistently updated property map concealed a missing measured data row")
        preparation_path, preparation_map_path = fixture / PREPARATION_SOURCE, fixture / PREPARATION_MAP
        preparation_review_path = fixture / PREPARATION_REVIEW
        originals = {path: path.read_bytes() for path in
                     (preparation_path, preparation_map_path, preparation_review_path)}
        for case, expected_error in (
            ("preparation_source_map_drift_rejected", "Preparation source/map hash differs"),
            ("preparation_claim_drift_rejected_after_consistent_map_update", "Preparation map changed individual claim records"),
            ("preparation_feed_basis_drift_rejected_after_consistent_records", "Preparation feed calculation or basis differs"),
        ):
            try:
                text = originals[preparation_path].decode("utf-8")
                support = json.loads(originals[preparation_map_path])
                if case == "preparation_source_map_drift_rejected":
                    preparation_path.write_bytes(originals[preparation_path] + b"\nUnadopted addition.\n")
                elif "claim_drift" in case:
                    old_claim = support["claims"][0]["text"]
                    new_claim = old_claim.replace("positive normalized fraction", "nonnegative normalized fraction", 1)
                    require(old_claim != new_claim, "Preparation claim fixture lost its target")
                    text = text.replace("**Claim 1.** " + old_claim, "**Claim 1.** " + new_claim, 1)
                    preparation_path.write_text(text, encoding="utf-8", newline="\n")
                    support["claims"][0]["text"] = new_claim
                    support["source_sha256"] = hashlib.sha256(preparation_path.read_bytes()).hexdigest()
                    preparation_map_path.write_text(json.dumps(support), encoding="utf-8")
                else:
                    # Deliberately confuse a monomer number fraction with an
                    # elemental fraction, updating the map and source record.
                    row = "| H | 19635 | 19635/37717 |"
                    require(text.count(row) == 1, "Preparation feed fixture lost its target")
                    preparation_path.write_text(text.replace(row, "| H | 19635 | 27/817 |", 1),
                                                encoding="utf-8", newline="\n")
                    support["source_sha256"] = hashlib.sha256(preparation_path.read_bytes()).hexdigest()
                    preparation_map_path.write_text(json.dumps(support), encoding="utf-8")
                    review = json.loads(originals[preparation_review_path])
                    review["calculated_feed_atomic_fractions"]["H"] = "27/817"
                    preparation_review_path.write_text(json.dumps(review), encoding="utf-8")
                try:
                    check_preparation_application(fixture)
                except VerificationError as error:
                    require(expected_error in str(error), "Preparation mutation failed for another reason: " + str(error))
                    extended.append(case)
                require(case in extended, "Preparation mutation was accepted: " + case)
            finally:
                for path, data in originals.items():
                    path.write_bytes(data)
        for path in ("../outside.txt", "/absolute.txt", "C:/outside.txt", "a\\b"):
            try:
                safe_path(fixture, path)
            except VerificationError:
                caught.append("unsafe_path_rejected:" + path)
        application = (fixture / "documents/provisional_application_draft.md").read_text(encoding="utf-8")
        register = load_json(fixture / "data/entity_register.json")
        register["elements"][-1]["status"] = "recognized_element"
        try:
            check_registry(register, application)
        except VerificationError:
            caught.append("hypothetical_status_change_rejected")
        support = load_json(fixture / "data/claim_support_map.json")
        support["claims"][0]["novelty_assessed"] = True
        try:
            check_claims(application, support)
        except VerificationError:
            caught.append("unreviewed_novelty_status_change_rejected")

        model_path = fixture / "range_model/unrestricted_composition_model.json"
        model_original = model_path.read_bytes()
        model = json.loads(model_original)
        model["unreviewed_coordinate_floor"] = "10^-19"
        model_path.write_text(json.dumps(model), encoding="utf-8")
        try:
            check_unrestricted_math(fixture)
        except VerificationError:
            extended.append("unrestricted_model_semantic_drift_rejected")
        model_path.write_bytes(model_original)

        directory = fixture / NUCLEAR_DIRECTORY
        with module_environment(directory):
            nuclear_parser = import_local("parse_nubase", directory / "parse_nubase.py")
            nuclear_verifier = import_local("verify_nuclear_archive", directory / "verify_nuclear_archive.py")
            payload, schema, _, _ = nuclear_parser.parse_snapshot()
            payload["states"][0]["observation_status"] = "observed"
            try:
                nuclear_verifier.verify_payload(payload, schema, nuclear_parser.SOURCE.read_bytes())
            except ValueError:
                extended.append("nuclear_presence_promoted_to_observation_rejected")

        metadata_path = fixture / PARTICLE_DIRECTORY / "pdg2026_identity_metadata.json"
        metadata_original = metadata_path.read_bytes()
        metadata = json.loads(metadata_original)
        metadata["interpretation"]["physical_existence_status"] = "all discovered"
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        try:
            check_particle_archive(fixture)
        except ValueError:
            extended.append("particle_identity_promoted_to_discovery_rejected")
        metadata_path.write_bytes(metadata_original)

        optional_path = fixture / OPTIONAL_NUCLEAR_VIEW
        optional_original = optional_path.read_bytes() if optional_path.exists() else None
        optional_path.write_text("{}", encoding="utf-8")
        try:
            check_nuclear_archive(fixture)
        except VerificationError:
            extended.append("optional_nuclear_view_integrity_drift_rejected")
        if optional_original is None:
            optional_path.unlink()
        else:
            optional_path.write_bytes(optional_original)

        # These literal test bytes have their own pinned hash. They exercise the
        # real download-integrity and publication code without distributing the
        # raw PDG SQLite file or asserting another official-source comparison.
        download_bytes = b"Offline pinned downloader regression bytes, not PDG SQLite.\n"
        download_sha = "91974da12e56c858e6079db36b012ef42b3dcdd769925b58c3949accdc7ca476"
        require(hashlib.sha256(download_bytes).hexdigest() == download_sha, "Downloader test fixture hash changed")
        download_root = fixture / "generated_reports" / "downloader-tests"
        download_root.mkdir(parents=True)
        downloader_cases = []
        class OfflineResponse(io.BytesIO):
            status = 200
            headers = {"Content-Type": "application/octet-stream", "ETag": "offline test fixture"}

        directory = fixture / PARTICLE_DIRECTORY
        with module_environment(directory):
            downloader = import_local("extract_pdg_identities", directory / "extract_pdg_identities.py")
            with patch.object(downloader, "SOURCE_BYTES", len(download_bytes)), \
                    patch.object(downloader, "SOURCE_SHA256", download_sha):
                destination = download_root / "success.bin"
                observation = download_root / "success.json"
                with patch.object(downloader.urllib.request, "urlopen", return_value=OfflineResponse(download_bytes)) as response, \
                        redirect_stdout(io.StringIO()):
                    downloader.download(argparse.Namespace(destination=destination, observation=observation))
                require(response.call_count == 1, "Mock downloader did not use exactly one mocked request")
                downloader.check_source(destination)
                require(destination.read_bytes() == download_bytes and not destination.with_suffix(".bin.part").exists(),
                        "Successful exclusive publication did not preserve bytes or remove its partial")
                require(load_json(observation)["sha256"] == download_sha, "Successful observation lacks the pinned test hash")
                downloader_cases.append("mocked_pinned_test_bytes_exclusive_publication")

                destination = download_root / "competing.bin"
                observation = download_root / "competing.json"
                competitor_bytes = b"Preserve this concurrent destination.\n"
                real_check_source = downloader.check_source
                def appear_before_publication(partial: Path) -> None:
                    real_check_source(partial)
                    destination.write_bytes(competitor_bytes)

                with patch.object(downloader.urllib.request, "urlopen", return_value=OfflineResponse(download_bytes)) as response, \
                        patch.object(downloader, "check_source", side_effect=appear_before_publication), \
                        redirect_stdout(io.StringIO()):
                    try:
                        downloader.download(argparse.Namespace(destination=destination, observation=observation))
                    except FileExistsError:
                        pass
                    else:
                        raise VerificationError("Concurrent downloader destination was replaced")
                require(response.call_count == 1 and destination.read_bytes() == competitor_bytes,
                        "Concurrent destination bytes were not preserved")
                partial = destination.with_suffix(".bin.part")
                real_check_source(partial)
                require(partial.read_bytes() == download_bytes and not observation.exists(),
                        "Refused publication lost its verified partial or wrote a success observation")
                downloader_cases.append("concurrent_destination_preserved_partial_retained_no_observation")

        # The parent owns the real marker before launching the competing helper,
        # so contention is deterministic and requires no timing assumptions.
        helper_path = fixture / "tools/update_manifest.py"
        specification = importlib.util.spec_from_file_location("manifest_lock_selftest", helper_path)
        require(specification is not None and specification.loader is not None, "Could not load manifest lock helper")
        helper = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(helper)
        lock = fixture / "generated_reports" / "manifest-update.lock"
        manifest_before = (fixture / MANIFEST).read_bytes()
        with helper.manifest_write_lock():
            lock_before = lock.read_bytes()
            competing_writer = subprocess.run(
                [sys.executable, "-B", str(helper_path), "--write"],
                cwd=fixture, capture_output=True, text=True, timeout=30, check=False,
            )
            require(competing_writer.returncode != 0 and "Manifest update lock already exists" in competing_writer.stderr,
                    "Competing manifest writer was not rejected by the held lock")
            require(lock.read_bytes() == lock_before and (fixture / MANIFEST).read_bytes() == manifest_before,
                    "Competing manifest writer changed the held lock or manifest")
        require(not lock.exists(), "Manifest lock regression left its owned lock behind")

        # A Windows junction is not a symlink. Model that classification on every
        # platform and make any descent into its outside target observable.
        junction = fixture / "junction-regression"
        junction.mkdir()
        outside = Path(temporary) / "outside-junction-target"
        outside.mkdir()
        (outside / "sentinel.txt").write_text("Must never be traversed", encoding="utf-8")
        traversal = {"outside_visited": False}
        real_is_junction = Path.is_junction
        def classify_junction(path: Path) -> bool:
            return path == junction or real_is_junction(path)
        def junction_walk(*args, **kwargs):
            directories = [junction.name]
            yield str(fixture), directories, []
            if junction.name in directories:
                traversal["outside_visited"] = True
                yield str(outside), [], ["sentinel.txt"]

        require(not junction.is_symlink(), "Junction regression must cover the non-symlink classification")
        with patch.object(Path, "is_junction", classify_junction), patch.object(os, "walk", junction_walk):
            try:
                check_inventory(fixture)
            except VerificationError as error:
                require("directory junction" in str(error) and junction.name in str(error),
                        "Junction fixture failed for an unrelated inventory reason")
            else:
                raise VerificationError("Inventory accepted a directory junction")
        require(not traversal["outside_visited"], "Inventory descended into a junction's outside target")
        junction.rmdir()

        # Simulate a caller that has already imported the original package.
        # A fixture must still execute its own module and restore that caller.
        import types
        cached = types.ModuleType("unrestricted_compositions")
        prior = sys.modules.get("unrestricted_compositions")
        sys.modules["unrestricted_compositions"] = cached
        try:
            directory = fixture / "range_model"
            with module_environment(directory):
                imported = import_local("unrestricted_compositions", directory / "unrestricted_compositions.py")
                require(imported is not cached and Path(imported.__file__).resolve().is_relative_to(fixture.resolve()),
                        "Fixture reused a caller's cached original module")
            require(sys.modules.get("unrestricted_compositions") is cached, "Caller module was not restored")
        finally:
            if prior is None:
                sys.modules.pop("unrestricted_compositions", None)
            else:
                sys.modules["unrestricted_compositions"] = prior
    require(len(caught) == 10, f"Expected 10 deliberate failure checks, got {len(caught)}")
    require(len(extended) == 26, f"Expected 26 extension failure checks, got {len(extended)}")
    require(len(downloader_cases) == 2, "Expected the two durable downloader publication regressions")
    return {"status": "passed", "deliberate_failure_cases_rejected": len(caught), "cases": caught,
            "extension_failure_cases_rejected": len(extended), "extension_cases": extended,
            "downloader_regression_case_count": len(downloader_cases), "downloader_regression_cases": downloader_cases,
            "downloader_regression_real_network_calls": 0,
            "downloader_fixture_scope": "Mock transfer of fixed test bytes with pinned test hash; no raw PDG SQLite comparison.",
            "cooperating_manifest_lock_contention_checked": True,
            "workflow_regression_checks": {"cooperating_manifest_lock_contention": True,
                                           "directory_junction_rejected_before_descent": True},
            "fixture_import_isolation_checked": True,
            "optimized_interpreter_rejection_checked": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Also exercise failure paths and offline publication/locking regressions in temporary copies")
    args = parser.parse_args()
    try:
        root = Path(__file__).resolve().parent
        result = run(root)
        if args.self_test:
            result["verifier_self_tests"] = self_test(root)
        print(json.dumps(result, indent=2))
        return 0
    except (VerificationError, OSError, ValueError, KeyError, IndexError, TypeError) as error:
        print(json.dumps({"status": "failed", "error": str(error)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
