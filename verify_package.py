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
ELECTRICAL_SOURCE = "documents/provisional_application_electrical_evidence_2026-09-30.md"
ELECTRICAL_MAP = "data/claim_support_map_electrical_evidence_2026-09-30.json"
ELECTRICAL_EDITION = "data/application_electrical_evidence_2026-09-30.json"
ELECTRICAL_PDF = "documents/pdf/provisional_application_electrical_evidence_2026-09-30.pdf"
ELECTRICAL_REVIEW = "data/electrical_source_review_2026-09-30.json"
ELECTRICAL_BASELINE = "e9471e2dc71560e930d062a16b40ae4732d1e90a"
ELECTRICAL_HEADING = "### Electrical evidence associated with [0066]: preparation, coordinates and conditional response"
ELECTRICAL_AUTHORING = {
    "tools/pdf/build_working_application.py": "data/application_electrical_evidence_authoring_2026-09-30/builder.py.txt",
    "tools/pdf/build_consolidated_review.py": "data/application_electrical_evidence_authoring_2026-09-30/layout.py.txt",
    "tools/pdf/build_identity_review_annex.py": "data/application_electrical_evidence_authoring_2026-09-30/output_helper.py.txt",
}
OXIDE_SOURCE = "documents/provisional_application_oxide_defect_evidence_2026-09-30.md"
OXIDE_MAP = "data/claim_support_map_oxide_defect_evidence_2026-09-30.json"
OXIDE_EDITION = "data/application_oxide_defect_evidence_2026-09-30.json"
OXIDE_PDF = "documents/pdf/provisional_application_oxide_defect_evidence_2026-09-30.pdf"
OXIDE_REVIEW = "data/oxide_defect_source_review_2026-09-30.json"
OXIDE_BASELINE = "6d25542eb72f46ab148f6bad9ab81a2aaccdfe9a"
OXIDE_HEADING = "### Oxide and defect evidence associated with [0064]: preparation, diagnostics and conditional response"
# Fingerprints anchor reviewed source provenance, table and differences without
# duplicating that source summary. Encode UTF-8 JSON with sorted object keys,
# no ASCII escaping and separators (",", ":"); array order remains significant.
OXIDE_TABLE_SHA256 = "e59f688ff9888189221bce65eaab68ff88421fc2884234791a2980f45fc84f4e"
OXIDE_DIFFERENCES_SHA256 = "81b6b4befcdf13ce85abd7a6f3c3b5062a4257f4e9095fa7b9cc73f86290aabf"
OXIDE_PROVENANCE_SHA256 = "933d140f64a4e5a883349dcdf542bb8306b50749224f98ea1dbed3bd2c8ee7ca"
# The reviewed diagnostic sentence uses whitespace-normalized UTF-8 text.
OXIDE_DIAGNOSTIC_SHA256 = "7e501e4e29f5d04e743f209ef57acab8d01084f8cde3602fa58d6532a8d37c01"
OXIDE_AUTHORING = {
    "tools/pdf/build_working_application.py": "data/application_oxide_defect_evidence_authoring_2026-09-30/builder.py.txt",
    "tools/pdf/build_consolidated_review.py": "data/application_oxide_defect_evidence_authoring_2026-09-30/layout.py.txt",
    "tools/pdf/build_identity_review_annex.py": "data/application_oxide_defect_evidence_authoring_2026-09-30/output_helper.py.txt",
}
PHASE_SOURCE = "documents/provisional_application_phase_specific_evidence_2026-10-01.md"
PHASE_MAP = "data/claim_support_map_phase_specific_evidence_2026-10-01.json"
PHASE_EDITION = "data/application_phase_specific_evidence_2026-10-01.json"
PHASE_PDF = "documents/pdf/provisional_application_phase_specific_evidence_2026-10-01.pdf"
PHASE_REVIEW = "data/magneli_source_review_2026-10-01.json"
PHASE_RECORD = "data/oxide_candidate_record_review_2026-10-01.json"
PHASE_BASELINE = "ad590d8fb6e2646e27234fa51efce071044e4bf8"
PHASE_HEADING = "### Phase-specific evidence and worked record associated with [0064]"
# These pins identify reviewed input records and the whitespace-normalized
# application source account without duplicating its scientific summary.
PHASE_REVIEW_SHA256 = "ec22f63bffef4d22e594bebf3827405df13f10527c7801bd2eab0054c65b7768"
PHASE_RECORD_SHA256 = "031d389236fbe42f81d3b607f7146a4a359e48db7892533a2c5f77aaf5bf0efa"
PHASE_ACCOUNT_SHA256 = "462b6a266c19d1a377f5d44d83a010694e1131bb1168ba4e1c55da28fad05fb3"
# Freeze the reviewed block's field statuses and qualifications independently
# of refreshed source/map and outer hashes; no missing evidence is promoted.
PHASE_BLOCK_SHA256 = "fa290887cabcb57c3208fe666db5612307fc435fef3f91b17b24f7f48cd2fa38"
PHASE_AUTHORING = {
    "tools/pdf/build_working_application.py": "data/application_phase_specific_evidence_authoring_2026-10-01/builder.py.txt",
    "tools/pdf/build_consolidated_review.py": "data/application_phase_specific_evidence_authoring_2026-10-01/layout.py.txt",
    "tools/pdf/build_identity_review_annex.py": "data/application_phase_specific_evidence_authoring_2026-10-01/output_helper.py.txt",
}
FAMILY_SOURCE = "documents/provisional_application_family_evidence_2026-10-01.md"
FAMILY_MAP = "data/claim_support_map_family_evidence_2026-10-01.json"
FAMILY_EDITION = "data/application_family_evidence_2026-10-01.json"
FAMILY_PDF = "documents/pdf/provisional_application_family_evidence_2026-10-01.pdf"
FAMILY_REVIEW = "data/family_source_review_2026-10-01.json"
FAMILY_CONTEXT = "documents/reference_entry_support.md"
FAMILY_BASELINE = "7e9b9419e26a179a2288b427e0e82f42389b8366"
FAMILY_PREFACE_SHA256 = "9f15451239cca8c2752cc5c55704873539ad76bc43706f53e14e6f3ad3562513"
FAMILY_HEADINGS = {
    "molecular": "### Molecular evidence associated with [0040]: identity, crystallization and accounting",
    "polymer": "### Polymer evidence associated with [0040]: stereochemistry, processing and accounting",
    "composite": "### Composite evidence associated with [0040]: constituents, preparation and accounting",
}
# Reviewed identities and qualifications are anchored independently of source,
# captured-input and outer hashes. These pins do not certify physical outcomes.
FAMILY_REVIEW_SHA256 = "056c83e78d38d0fc6421150994f097081a8fd6efd98ca83951f5230a3d679e40"
FAMILY_BLOCK_SHA256 = {
    "molecular": "bd3d4834506ecd293a06f46d2a620ac7c4a3736962cc038d8ee08071eb45613a",
    "polymer": "2eef656a65855427a7bcc6985c11f57cc2c951187b744240457a4740a096d5f9",
    "composite": "604dc64a9d62e521b1e3793598662552df8a547800fe271f07e8af0ece078666",
}
FAMILY_AUTHORING = {
    "tools/pdf/build_working_application.py": "data/application_family_evidence_authoring_2026-10-01/builder.py.txt",
    "tools/pdf/build_consolidated_review.py": "data/application_family_evidence_authoring_2026-10-01/layout.py.txt",
    "tools/pdf/build_identity_review_annex.py": "data/application_family_evidence_authoring_2026-10-01/output_helper.py.txt",
}
METAL_GLASS_SOURCE = "documents/provisional_application_metal_glass_evidence_2026-10-01.md"
METAL_GLASS_MAP = "data/claim_support_map_metal_glass_evidence_2026-10-01.json"
METAL_GLASS_EDITION = "data/application_metal_glass_evidence_2026-10-01.json"
METAL_GLASS_PDF = "documents/pdf/provisional_application_metal_glass_evidence_2026-10-01.pdf"
METAL_GLASS_REVIEW = "data/metal_glass_source_review_2026-10-01.json"
METAL_GLASS_BASELINE = "eae10a2cfd8467a4adee9f7883c8a76f77914832"
METAL_GLASS_HEADINGS = {
    "alloy": "### Alloy evidence associated with [0039]: preparation, principal inventory and conditional transport",
    "glass": "### Glass evidence associated with [0063]: preparation, phase identity and conditional response",
}
METAL_GLASS_POINTERS = {
    "0039": " The adjoining alloy-evidence block records a selected attributed preparation, principal-inventory accounting and a conditional transport inquiry.",
    "0063": " The adjoining glass-evidence block records a selected attributed preparation, principal-inventory accounting and a conditional thermal-path inquiry.",
}
# Reviewed whitespace-normalized UTF-8 spans and the exact metadata bytes
# preserve qualifications independently of refreshed captured and outer hashes.
METAL_GLASS_PREFACE_SHA256 = "317a7609c61210bd782a11c1c0735296042c9cf697f9ba74bc72ff32c717fb29"
METAL_GLASS_REVIEW_SHA256 = "4f681b721c96d0c8071c0fdcd0b00d8fc281b3fa90db479fadcd30679be43731"
METAL_GLASS_BLOCK_SHA256 = {
    "alloy": "36671b1e2965e001878662ec987b49847cdc4b441eeaf280a005c87bb2d4c9c9",
    "glass": "856649b3f175d919f6bc13deea914236314a39f30b3aa959c23ebd8a970ac9b1",
}
METAL_GLASS_AUTHORING = {
    "tools/pdf/build_working_application.py": "data/application_metal_glass_evidence_authoring_2026-10-01/builder.py.txt",
    "tools/pdf/build_consolidated_review.py": "data/application_metal_glass_evidence_authoring_2026-10-01/layout.py.txt",
    "tools/pdf/build_identity_review_annex.py": "data/application_metal_glass_evidence_authoring_2026-10-01/output_helper.py.txt",
}
THEORETICAL_SOURCE = "documents/provisional_application_theoretical_review_2026-10-01.md"
THEORETICAL_MAP = "data/claim_support_map_theoretical_review_2026-10-01.json"
THEORETICAL_EDITION = "data/application_theoretical_review_2026-10-01.json"
THEORETICAL_PDF = "documents/pdf/provisional_application_theoretical_review_2026-10-01.pdf"
THEORETICAL_BASELINE = "f4aa17dbf10e872af18266c71eba2772622f4b65"
THEORETICAL_HEADING = "## Hypothetical embodiments for review"
# These reviewed whitespace-normalized UTF-8 fingerprints are independent of
# source/map, capture and manifest hashes. Their content remains prospective.
THEORETICAL_PREFACE_SHA256 = "0a9d5b5da5633bb557e01d14bc8a3ec91af568975da49acfaf298319d14fe337"
THEORETICAL_BLOCK_SHA256 = "06c9fe988c173237b9158c837b086cb0e544c12d09749d9b0245c8290fb9997e"
THEORETICAL_INVENTOR = {
    "name": "Robert M. Layne", "designation_status": "USER_DIRECTED_REVIEW_DESIGNATION",
    "legal_inventorship_certified": False, "filing_particulars_confirmed": False,
}
THEORETICAL_SOURCE_NOTE_OLD = "No applicant identity, inventor signature, priority claim, micro-entity certification, complete current isotope archive, or worldwide patent-status finding is assumed."
THEORETICAL_SOURCE_NOTE_NEW = "Robert M. Layne is named as proposed sole inventor for this review draft at his instruction; no inventor signature, applicant entitlement, priority claim, micro-entity certification, complete current isotope archive, or worldwide patent-status finding is assumed."
THEORETICAL_AUTHORING = {
    "tools/pdf/build_working_application.py": "data/application_theoretical_review_authoring_2026-10-01/builder.py.txt",
    "tools/pdf/build_consolidated_review.py": "data/application_theoretical_review_authoring_2026-10-01/layout.py.txt",
    "tools/pdf/build_identity_review_annex.py": "data/application_theoretical_review_authoring_2026-10-01/output_helper.py.txt",
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
    "documents/electrical_claim_comparison_2026-09-30.md",
    "data/electrical_candidate_record_review_2026-09-30.json",
    "documents/oxide_claim_comparison_2026-10-01.md",
    "data/oxide_candidate_record_review_2026-10-01.json",
    "data/magneli_source_review_2026-10-01.json",
    "documents/glass_claim_comparison_2026-10-01.md",
    "documents/theoretical_disclosure_strategy_2026-10-01.md",
    "data/glass_candidate_record_review_2026-10-01.json",
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
    ELECTRICAL_SOURCE, ELECTRICAL_MAP, ELECTRICAL_EDITION, ELECTRICAL_PDF, ELECTRICAL_REVIEW,
    "documents/application_electrical_evidence_2026-09-30.md", *ELECTRICAL_AUTHORING.values(),
    OXIDE_SOURCE, OXIDE_MAP, OXIDE_EDITION, OXIDE_PDF, OXIDE_REVIEW,
    "documents/application_oxide_defect_evidence_2026-09-30.md", *OXIDE_AUTHORING.values(),
    PHASE_SOURCE, PHASE_MAP, PHASE_EDITION, PHASE_PDF,
    "documents/application_phase_specific_evidence_2026-10-01.md", *PHASE_AUTHORING.values(),
    FAMILY_SOURCE, FAMILY_MAP, FAMILY_EDITION, FAMILY_PDF, FAMILY_REVIEW,
    "documents/application_family_evidence_2026-10-01.md", *FAMILY_AUTHORING.values(),
    METAL_GLASS_SOURCE, METAL_GLASS_MAP, METAL_GLASS_EDITION, METAL_GLASS_PDF, METAL_GLASS_REVIEW,
    "documents/application_metal_glass_evidence_2026-10-01.md", *METAL_GLASS_AUTHORING.values(),
    THEORETICAL_SOURCE, THEORETICAL_MAP, THEORETICAL_EDITION, THEORETICAL_PDF,
    "documents/application_theoretical_review_2026-10-01.md", *THEORETICAL_AUTHORING.values(),
}
EXPECTED_FILES = EXPECTED_HASHED | {MANIFEST, RANGE_REPORT}
SUBSTANTIVE_CHECKER = "tools/substantive_review_checks.py"
SUBSTANTIVE_FILES = {
    SUBSTANTIVE_CHECKER, "tools/technical_review_calculations.py",
    "documents/provisional_application_substantive_review_2026-10-03.md",
    "documents/pdf/provisional_application_substantive_review_2026-10-03.pdf",
    "documents/application_substantive_review_2026-10-03.md",
    "data/claim_support_map_substantive_review_2026-10-03.json",
    "data/application_substantive_review_2026-10-03.json",
    "data/claim_review_2026-10-03.json", "data/technical_review_2026-10-03.json",
    "data/application_substantive_review_authoring_2026-10-03/builder.py.txt",
    "data/application_substantive_review_authoring_2026-10-03/layout.py.txt",
    "data/application_substantive_review_authoring_2026-10-03/output_helper.py.txt",
}
EXPECTED_HASHED = EXPECTED_HASHED | SUBSTANTIVE_FILES
EXPECTED_FILES = EXPECTED_HASHED | {MANIFEST, RANGE_REPORT}
MODULE_NAMES = frozenset({
    "composition_ranges", "unrestricted_compositions", "independent_unrestricted_checks",
    "trace_sampling_calculations", "claim_clarification_checks", "parse_nubase", "verify_nuclear_archive",
    "extract_pdg_identities", "substantive_review_checks", "technical_review_calculations",
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


def evidence_block(source: str, heading: str, next_paragraph: str) -> str:
    """Bound an unnumbered addition by a unique heading and paragraph start."""
    require(source.count(heading) == 1 and re.search(r"^" + re.escape(heading) + r"$", source, re.M),
            "Missing or ambiguous evidence-block heading")
    remaining = source.split(heading, 1)[1]
    boundaries = list(re.finditer(r"^\[" + re.escape(next_paragraph) + r"\] ", remaining, re.M))
    require(len(boundaries) == 1, "Missing or ambiguous evidence-block terminator")
    return remaining[:boundaries[0].start()]


def evidence_block_counts(block: str) -> dict:
    """Count displayed source blocks using the Markdown table convention."""
    prose, rows = 0, 0
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", cell.replace(" ", "")) for cell in cells):
                continue
            rows += 1
        else:
            prose += 1
    return {"complete_prose_blocks": prose, "complete_table_rows_including_headers": rows,
            "checked_in_order": True}


def check_electrical_application(root: Path) -> dict:
    """Bind the new electrical edition to its preserved predecessor and inputs.

    A numerical wt% fit coordinate differs from a normalized mass fraction.
    Captured rendering checks do not repeat PDF parsing or establish enablement.
    """
    preceding_bytes = (root / PREPARATION_SOURCE).read_bytes()
    source_bytes = (root / ELECTRICAL_SOURCE).read_bytes()
    preceding, application = preceding_bytes.decode("utf-8"), source_bytes.decode("utf-8")
    support = load_json(root / ELECTRICAL_MAP)
    require(support.get("source_path") == ELECTRICAL_SOURCE and support.get("source_sha256")
            == hashlib.sha256(source_bytes).hexdigest(), "Electrical source/map hash differs")
    require(support.get("prepared_date") == "2026-09-30" and support.get("derived_from") == {
        "path": PREPARATION_SOURCE, "sha256": hashlib.sha256(preceding_bytes).hexdigest(),
        "repository_baseline": ELECTRICAL_BASELINE,
    }, "Electrical source derivation differs")
    require(support.get("changed_paragraphs") == ["0066"] and support.get("changed_claims") == [],
            "Electrical change inventory differs")
    require(support.get("claims") == load_json(root / PREPARATION_MAP).get("claims"),
            "Electrical map changed individual claim records")
    claim_result = check_claims(application, support)
    require(re.findall(r"^\*\*Claim (\d+)\.\*\* (.+)$", application, re.M)
            == re.findall(r"^\*\*Claim (\d+)\.\*\* (.+)$", preceding, re.M),
            "Electrical candidate claims differ from preparation edition")
    old_paragraphs = dict(re.findall(r"^\[(\d{4})\] (.+)$", preceding, re.M))
    new_paragraphs = dict(re.findall(r"^\[(\d{4})\] (.+)$", application, re.M))
    require(old_paragraphs.keys() == new_paragraphs.keys()
            and {n for n in old_paragraphs if old_paragraphs[n] != new_paragraphs[n]} == {"0066"},
            "Unexpected electrical paragraph changes")
    boundary = "## 1 Technical field\n"
    require(application.count(boundary) == preceding.count(boundary) == 1,
            "Electrical technical-field boundary differs")
    preface, body = application.split(boundary)
    lines = [line for line in preface.splitlines() if line]
    require(len(lines) == 4 and lines[0]
            == "# Provisional materials disclosure with attributed electrical evidence - 30 September 2026"
            and lines[1] == "Prepared **30 September 2026** | **Prospective unfiled electrical-evidence edition** for applicant and patent counsel.",
            "Electrical edition preface differs")
    block = evidence_block(body, ELECTRICAL_HEADING, "0067")
    old_body = preceding.split(boundary, 1)[1]
    old_body = old_body.replace("[0066] " + old_paragraphs["0066"], "[0066] " + new_paragraphs["0066"], 1)
    old_reference, new_reference = PurePosixPath(PREPARATION_MAP).name, PurePosixPath(ELECTRICAL_MAP).name
    require(old_body.count(old_reference) == body.count(new_reference) == 1
            and old_reference not in body, "Electrical companion-map reference differs")
    old_body = old_body.replace(old_reference, new_reference, 1)
    require(body.replace(ELECTRICAL_HEADING + block, "", 1) == old_body,
            "Electrical source changed outside the identified additions")
    check_registry(load_json(root / "data/entity_register.json"), application)

    review = load_json(root / ELECTRICAL_REVIEW)
    threshold = review.get("threshold_coordinate", {})
    require(threshold.get("reported_percent") == "0.443"
            and threshold.get("calculated_fraction") == str(Fraction("0.443") / 100)
            and threshold.get("evidence_status") == "CALCULATED representation of source-reported given threshold"
            and threshold.get("exact_product_assay") is False,
            "Electrical threshold coordinate or basis differs")
    require(review.get("fit_convention") == {
        "x": "Numerical PEDOT:PSS wt%", "y": "log10 conductivity in S/m", "t": "1.92",
        "sigma_0": "0.952", "fraction_prefactor_rescaling": "sigma0_fraction=sigma0_percent*100^t",
        "new_curve_generated": False,
    }, "Electrical fit convention or prefactor rescaling differs")
    table_rows = review.get("source_table_rows")
    require(table_rows == [
        ["Electrical quantity", "Reported value", "Basis and source", "Evidence"],
        ["Fixed SWCNT loading", "0.35 wt%; 0.26 vol%", "Figure 2 composite loading", "ESTABLISHED report"],
        ["PEDOT:PSS threshold", "0.443 wt%", "Figure 2 given threshold; numerical wt%", "ESTABLISHED source coordinate"],
        ["Exponent t", "1.92", "Figure 2 fitted exponent", "CALCULATED source fit"],
        ["Prefactor sigma_0", "0.952", "Figure 2; S/m in numerical wt% convention", "CALCULATED source fit"],
        ["Moulding temperature", "453 K", "Supplement page 3", "ESTABLISHED report"],
        ["xi_rr; xi_ss; xi_sr", "About 1; 10; 5 nm", "Supplement page 3 effective coupling lengths", "CALCULATED model"],
    ], "Electrical reviewed source table differs")
    table = ["| " + " | ".join(table_rows[0]) + " |", "| --- | --- | --- | --- |"]
    table.extend("| " + " | ".join(row) + " |" for row in table_rows[1:])
    require(block.count("\n".join(table)) == 1, "Electrical source table differs from reviewed rows")
    require(all(fragment in block for fragment in (
        "p_c/100 = 443/100000", "sigma_0,f = sigma_0,p 100^t",
        "PROPOSED present verification:", "UNSUPPORTED extensions",
    )), "Electrical coordinate conversion or conditional evidence boundary differs")
    require(review.get("review_date") == "2026-09-30" and review.get("doi") == "10.1038/nnano.2011.40"
            and all(review.get(key) is False for key in
                    ("applicant_experiment_asserted", "physical_enablement_certified", "filing_asserted")),
            "Electrical source factual status differs")

    edition = load_json(root / ELECTRICAL_EDITION)
    require(edition.get("prepared_date") == "2026-09-30"
            and edition.get("edition_status") == "prospective unfiled electrical-evidence edition"
            and edition.get("repository_baseline") == ELECTRICAL_BASELINE
            and edition.get("filing_asserted") is False and edition.get("physical_enablement_certified") is False,
            "Electrical edition baseline or factual status differs")
    expected_sources = {ELECTRICAL_SOURCE, ELECTRICAL_MAP, ELECTRICAL_REVIEW, PREPARATION_REVIEW,
                        *ELECTRICAL_AUTHORING, "documents/drawings/composition_simplex.svg",
                        "documents/drawings/material_record_sequence.svg"}
    entries = edition.get("sources", [])
    require(len(entries) == len(expected_sources) and {entry["path"] for entry in entries} == expected_sources,
            "Electrical PDF source inventory differs")
    for entry in entries:
        snapshot = ELECTRICAL_AUTHORING.get(entry["path"])
        require(entry.get("snapshot_path") == snapshot, "Electrical authoring snapshot identity differs")
        require(hashlib.sha256(safe_path(root, snapshot or entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
                "Electrical PDF captured-source hash differs")
    pdf = edition.get("pdf", {})
    require(pdf.get("path") == ELECTRICAL_PDF and type(pdf.get("page_count")) is int
            and pdf["page_count"] > 0, "Invalid electrical PDF identity")
    data = safe_path(root, pdf["path"]).read_bytes()
    require(len(data) == pdf.get("size_bytes") and hashlib.sha256(data).hexdigest() == pdf.get("sha256"),
            "Electrical PDF bytes differ from record")
    locations = edition.get("location_map", {})
    expected_locations = {f"paragraph_{n:04d}" for n in range(1, 81)} | {f"claim_{n}" for n in range(1, 200)}
    require(locations.keys() == expected_locations
            and all(type(page) is int and 1 <= page <= pdf["page_count"] for page in locations.values()),
            "Electrical recorded PDF locations differ")
    require(edition.get("complete_numbered_text_checked") == {"paragraphs": 80, "claims": 199}
            and edition.get("vector_drawings_checked") == 2
            and edition.get("complete_property_table_checked") == {
                "data_rows": 10, "columns": 4, "headers_and_complete_rows_checked_in_order": True},
            "Electrical recorded application content checks differ")
    preparation = evidence_block(body, PREPARATION_HEADING, "0066")
    require(edition.get("complete_preparation_text_checked") == evidence_block_counts(preparation),
            "Electrical inherited preparation coverage differs")
    require(edition.get("complete_electrical_text_checked") == evidence_block_counts(block),
            "Electrical complete rendered block checks differ")
    visual = edition.get("visual_review", {})
    require(isinstance(visual, dict) and visual.get("status") == "completed"
            and visual.get("pages_reviewed") == list(range(1, pdf["page_count"] + 1))
            and visual.get("remaining_actionable_visual_findings") == 0,
            "Electrical recorded appearance review is incomplete")
    return {**claim_result, "changed_paragraphs": ["0066"], "changed_claims": [],
            "recorded_pdf_pages": pdf["page_count"], "recorded_pdf_locations_checked": len(locations),
            "captured_sources_checked": len(entries), "source_table_data_rows_checked": len(table_rows) - 1,
            "threshold_mass_fraction_recomputed": str(Fraction("0.443") / 100),
            "preceding_hydrogel_blocks_and_remaining_body_preserved": True,
            "pdf_parsed_or_appearance_rechecked_by_this_check": False,
            "filing_or_earlier_entitlement_or_enablement_certified": False}


def check_ideal_oxide_host(review: dict) -> dict:
    """Recompute five exact ideal inventories without assigning physical states."""
    model = review.get("ideal_host_accounting", {})
    expected_definition = {
        "evidence_status": "CALCULATED present ideal atom-count model; not a source assay",
        "basis": "Ideal Ti/O host atom counts", "selected_atomic_numbers": [8, 22],
        "delta_domain": "Rational 0 <= delta < 2; irrational cases symbolic",
        "x_Ti_formula": "1/(3-delta)", "x_O_formula": "(2-delta)/(3-delta)",
        "finite_count_rule": "delta=V/N; N positive integer; V integer; 0 <= V < 2N",
        "charge_model": "Neutral O^2- host compensated only by Ti^3+/Ti^4+: fraction(Ti^3+ among Ti atoms)=2*delta for 0 <= delta <= 1/2",
        "physical_candidates_prepared": False, "source_OH_or_positron_values_assigned_to_delta": False,
    }
    require(all(model.get(key) == value for key, value in expected_definition.items())
            and model.get("physical_candidates_prepared") is False
            and model.get("source_OH_or_positron_values_assigned_to_delta") is False,
            "Oxide ideal-host definition or evidence basis differs")
    deltas = (Fraction(0), Fraction(1, 10**20), Fraction(1, 4), Fraction(1),
              Fraction(2) - Fraction(1, 10**20))
    cases = model.get("cases", [])
    require(isinstance(cases, list) and len(cases) == len(deltas), "Oxide ideal-host case inventory differs")
    for case, delta in zip(cases, deltas):
        require(case.get("delta") == str(delta) and 0 <= delta < 2, "Oxide ideal-host delta differs")
        n, v = delta.denominator, delta.numerator
        oxygen, total = 2 * n - v, 3 * n - v
        fractions = {"x_Ti": Fraction(1, 3 - delta), "x_O": Fraction(2 - delta, 3 - delta)}
        require(all(value > 0 for value in fractions.values()) and sum(fractions.values()) == 1,
                "Invalid recomputed ideal-host fractions")
        require(all(case.get(key) == str(value) for key, value in fractions.items())
                and all(type(case.get(key)) is int and case[key] == value for key, value in
                        {"Ti_count": n, "O_count": oxygen, "total_atoms": total}.items())
                and Fraction(n, total).denominator == total,
                "Oxide ideal-host fractions or canonical counts differ")
        admissible = delta <= Fraction(1, 2)
        require(case.get("only_Ti3_Ti4_charge_model_admissible") is admissible,
                "Oxide restricted charge-model boundary differs")
        if admissible:
            # These integer formal-charge populations are consequences of the
            # restricted model, not measured Ti oxidation-state populations.
            require(0 <= 2 * v <= n and 3 * (2 * v) + 4 * (n - 2 * v) == 2 * oxygen,
                    "Recomputed restricted charge balance differs")
    trace = Fraction(cases[-1]["x_O"])
    require(trace < Fraction(1, 10**19), "Oxide near-two trace does not fall below the original floor")
    return {"exact_ideal_host_cases_recomputed": len(cases), "canonical_integer_inventories_checked": len(cases),
            "near_two_oxygen_fraction": str(trace), "near_two_below_original_positive_floor": True,
            "physical_realization_or_measured_defect_population_certified": False}


def check_oxide_application(root: Path) -> dict:
    """Verify the fifth edition while preserving every preceding application.

    The external source review and ideal-host calculations have separate bases.
    Recorded PDF coverage binds bytes; this offline check does not parse a PDF.
    """
    preceding_bytes = (root / ELECTRICAL_SOURCE).read_bytes()
    source_bytes = (root / OXIDE_SOURCE).read_bytes()
    preceding, application = preceding_bytes.decode("utf-8"), source_bytes.decode("utf-8")
    support = load_json(root / OXIDE_MAP)
    require(support.get("source_path") == OXIDE_SOURCE and support.get("source_sha256")
            == hashlib.sha256(source_bytes).hexdigest(), "Oxide source/map hash differs")
    require(support.get("prepared_date") == "2026-09-30" and support.get("derived_from") == {
        "path": ELECTRICAL_SOURCE, "sha256": hashlib.sha256(preceding_bytes).hexdigest(),
        "repository_baseline": OXIDE_BASELINE,
    }, "Oxide source derivation differs")
    require(support.get("changed_paragraphs") == ["0064"] and support.get("changed_claims") == [],
            "Oxide change inventory differs")
    require(support.get("claims") == load_json(root / ELECTRICAL_MAP).get("claims"),
            "Oxide map changed individual claim records")
    claim_result = check_claims(application, support)
    require(re.findall(r"^\*\*Claim (\d+)\.\*\* (.+)$", application, re.M)
            == re.findall(r"^\*\*Claim (\d+)\.\*\* (.+)$", preceding, re.M),
            "Oxide candidate claims differ from electrical edition")
    old_paragraphs = dict(re.findall(r"^\[(\d{4})\] (.+)$", preceding, re.M))
    new_paragraphs = dict(re.findall(r"^\[(\d{4})\] (.+)$", application, re.M))
    require(old_paragraphs.keys() == new_paragraphs.keys()
            and {n for n in old_paragraphs if old_paragraphs[n] != new_paragraphs[n]} == {"0064"},
            "Unexpected oxide paragraph changes")
    boundary = "## 1 Technical field\n"
    require(application.count(boundary) == preceding.count(boundary) == 1,
            "Oxide technical-field boundary differs")
    preface, body = application.split(boundary)
    lines = [line for line in preface.splitlines() if line]
    require(len(lines) == 4 and lines[0]
            == "# Provisional materials disclosure with attributed oxide and defect evidence - 30 September 2026"
            and lines[1] == "Prepared **30 September 2026** | **Prospective unfiled oxide-defect-evidence edition** for applicant and patent counsel.",
            "Oxide edition preface differs")
    block = evidence_block(body, OXIDE_HEADING, "0065")
    old_body = preceding.split(boundary, 1)[1]
    old_body = old_body.replace("[0064] " + old_paragraphs["0064"], "[0064] " + new_paragraphs["0064"], 1)
    old_reference, new_reference = PurePosixPath(ELECTRICAL_MAP).name, PurePosixPath(OXIDE_MAP).name
    require(old_body.count(old_reference) == body.count(new_reference) == 1
            and old_reference not in body, "Oxide companion-map reference differs")
    old_body = old_body.replace(old_reference, new_reference, 1)
    require(body.replace(OXIDE_HEADING + block, "", 1) == old_body,
            "Oxide source changed outside the identified additions")
    check_registry(load_json(root / "data/entity_register.json"), application)

    review = load_json(root / OXIDE_REVIEW)
    require(review.get("source_basis") == {
        "OH": "See D[0064] diagnostic basis.",
        "positron_lifetimes_are_charge_carrier_lifetimes": False,
        "T2_positron_values_present_in_Figure_1f": False,
        "whole_product_elemental_inventory_assayed": False, "retained_Pt_fraction_assayed": False,
        "reported_hydrogen_rate_units": "micromol h^-1 g^-1", "source_conflicts_resolved": False,
    }, "Oxide diagnostic or assay basis differs")
    table_rows = review.get("source_table_rows")
    def reviewed_digest(value):
        return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                        separators=(",", ":")).encode("utf-8")).hexdigest()
    require(reviewed_digest({key: review.get(key) for key in
                             ("doi", "published_date_reported", "primary_article", "acquired_public_sources")})
            == OXIDE_PROVENANCE_SHA256, "Oxide reviewed upstream provenance differs")
    require(isinstance(table_rows, list) and len(table_rows) == 5
            and all(isinstance(row, list) and len(row) == 4
                    and all(isinstance(cell, str) for cell in row) for row in table_rows)
            and reviewed_digest(table_rows) == OXIDE_TABLE_SHA256
            and review.get("source_table_statuses") == [
        "ESTABLISHED measurement report", "ESTABLISHED measurement report",
        "ESTABLISHED measurement report", "CALCULATED source estimate",
    ], "Oxide reviewed source table or quantity status differs")
    table = ["| " + " | ".join(table_rows[0]) + " |", "| --- | --- | --- | --- |"]
    table.extend("| " + " | ".join(row) + " |" for row in table_rows[1:])
    require(block.count("\n".join(table)) == 1, "Oxide source table differs from reviewed rows")
    require(reviewed_digest(review.get("unresolved_source_differences")) == OXIDE_DIFFERENCES_SHA256,
            "Oxide unresolved source differences were changed or resolved")
    diagnostics = re.findall(r"\bFigure 1f [^.\n]*\.", block)
    require(len(diagnostics) == 1 and hashlib.sha256(" ".join(diagnostics[0].split()).encode("utf-8")).hexdigest()
            == OXIDE_DIAGNOSTIC_SHA256, "Oxide reviewed diagnostic sentence differs")
    require(all(fragment in block for fragment in (
        "x_Ti = 1/(3-delta)", "x_O = (2-delta)/(3-delta)", "0 <= delta <= 1/2",
        "Neither measures whole-specimen elemental fractions or charge-carrier lifetimes.",
        "methanol-assisted hydrogen evolution", "../data/oxide_defect_source_review_2026-09-30.json",
        "PROPOSED present verification and alternative", "UNSUPPORTED extensions",
    )), "Oxide source calculation or diagnostic boundary differs")
    model_result = check_ideal_oxide_host(review)
    require(review.get("review_date") == "2026-09-30" and review.get("doi") == "10.1038/ncomms6881"
            and all(review.get(key) is False for key in
                    ("applicant_experiment_asserted", "physical_enablement_certified", "novelty_assessed", "filing_asserted")),
            "Oxide source factual status differs")

    edition = load_json(root / OXIDE_EDITION)
    require(edition.get("prepared_date") == "2026-09-30"
            and edition.get("edition_status") == "prospective unfiled oxide-defect-evidence edition"
            and edition.get("repository_baseline") == OXIDE_BASELINE
            and edition.get("filing_asserted") is False and edition.get("physical_enablement_certified") is False,
            "Oxide edition baseline or factual status differs")
    expected_sources = {OXIDE_SOURCE, OXIDE_MAP, OXIDE_REVIEW, PREPARATION_REVIEW, ELECTRICAL_REVIEW,
                        *OXIDE_AUTHORING, "documents/drawings/composition_simplex.svg",
                        "documents/drawings/material_record_sequence.svg"}
    entries = edition.get("sources", [])
    require(len(entries) == len(expected_sources) and {entry["path"] for entry in entries} == expected_sources,
            "Oxide PDF source inventory differs")
    for entry in entries:
        snapshot = OXIDE_AUTHORING.get(entry["path"])
        require(entry.get("snapshot_path") == snapshot, "Oxide authoring snapshot identity differs")
        require(hashlib.sha256(safe_path(root, snapshot or entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
                "Oxide PDF captured-source hash differs")
    pdf = edition.get("pdf", {})
    require(pdf.get("path") == OXIDE_PDF and type(pdf.get("page_count")) is int
            and pdf["page_count"] > 0, "Invalid oxide PDF identity")
    data = safe_path(root, pdf["path"]).read_bytes()
    require(len(data) == pdf.get("size_bytes") and hashlib.sha256(data).hexdigest() == pdf.get("sha256"),
            "Oxide PDF bytes differ from record")
    locations = edition.get("location_map", {})
    expected_locations = {f"paragraph_{n:04d}" for n in range(1, 81)} | {f"claim_{n}" for n in range(1, 200)}
    require(locations.keys() == expected_locations
            and all(type(page) is int and 1 <= page <= pdf["page_count"] for page in locations.values()),
            "Oxide recorded PDF locations differ")
    require(edition.get("complete_numbered_text_checked") == {"paragraphs": 80, "claims": 199}
            and edition.get("vector_drawings_checked") == 2
            and edition.get("complete_property_table_checked") == {
                "data_rows": 10, "columns": 4, "headers_and_complete_rows_checked_in_order": True},
            "Oxide recorded application content checks differ")
    for key, heading, ending in (
        ("complete_preparation_text_checked", PREPARATION_HEADING, "0066"),
        ("complete_electrical_text_checked", ELECTRICAL_HEADING, "0067"),
        ("complete_oxide_defect_text_checked", OXIDE_HEADING, "0065"),
    ):
        require(edition.get(key) == evidence_block_counts(evidence_block(body, heading, ending)),
                "Oxide complete rendered block checks differ: " + key)
    visual = edition.get("visual_review", {})
    require(isinstance(visual, dict) and visual.get("status") == "completed"
            and visual.get("pages_reviewed") == list(range(1, pdf["page_count"] + 1))
            and visual.get("remaining_actionable_visual_findings") == 0,
            "Oxide recorded appearance review is incomplete")
    return {**claim_result, **model_result, "changed_paragraphs": ["0064"], "changed_claims": [],
            "recorded_pdf_pages": pdf["page_count"], "recorded_pdf_locations_checked": len(locations),
            "captured_sources_checked": len(entries), "source_table_data_rows_checked": len(table_rows) - 1,
            "preceding_hydrogel_and_electrical_blocks_and_remaining_body_preserved": True,
            "pdf_parsed_or_appearance_rechecked_by_this_check": False,
            "filing_or_earlier_entitlement_or_enablement_certified": False}


def check_phase_application(root: Path) -> dict:
    """Check the sixth edition's actual teaching, boundaries and captured bytes.

    Calculations independently use stipulated atom counts. Neither the source
    pins nor recorded PDF checks establish physical realization or appearance.
    """
    previous_bytes = (root / OXIDE_SOURCE).read_bytes()
    source_bytes = (root / PHASE_SOURCE).read_bytes()
    previous, application = previous_bytes.decode("utf-8"), source_bytes.decode("utf-8")
    support = load_json(root / PHASE_MAP)
    require(support.get("source_path") == PHASE_SOURCE and support.get("source_sha256")
            == hashlib.sha256(source_bytes).hexdigest(), "Phase source/map hash differs")
    require(support.get("prepared_date") == "2026-10-01" and support.get("derived_from") == {
        "path": OXIDE_SOURCE, "sha256": hashlib.sha256(previous_bytes).hexdigest(),
        "repository_baseline": PHASE_BASELINE,
    }, "Phase source derivation differs")
    require(support.get("claims") == load_json(root / OXIDE_MAP).get("claims")
            and support.get("changed_claims") == [] and support.get("changed_paragraphs") == ["0064"],
            "Phase individual claim records or change inventory differ")
    claims = check_claims(application, support)
    old_paragraphs = dict(re.findall(r"^\[(\d{4})\] (.+)$", previous, re.M))
    new_paragraphs = dict(re.findall(r"^\[(\d{4})\] (.+)$", application, re.M))
    require(old_paragraphs.keys() == new_paragraphs.keys()
            and {n for n in old_paragraphs if old_paragraphs[n] != new_paragraphs[n]} == {"0064"},
            "Unexpected phase paragraph changes")
    boundary = "## 1 Technical field\n"
    require(application.count(boundary) == previous.count(boundary) == 1,
            "Phase technical-field boundary differs")
    preface, body = application.split(boundary)
    lines = [line for line in preface.splitlines() if line]
    require(len(lines) == 4 and lines[0]
            == "# Provisional materials disclosure with phase-specific evidence and a worked record - 1 October 2026"
            and lines[1] == "Prepared **1 October 2026** | **Prospective unfiled phase-specific-evidence edition** for applicant and patent counsel.",
            "Phase edition preface differs")
    starts = list(re.finditer(r"^" + re.escape(PHASE_HEADING) + r"$", body, re.M))
    ends = list(re.finditer(r"^" + re.escape(OXIDE_HEADING) + r"$", body, re.M))
    require(len(starts) == len(ends) == 1 and starts[0].end() < ends[0].start(),
            "Phase evidence boundary differs")
    block = body[starts[0].end():ends[0].start()]
    old_body = previous.split(boundary, 1)[1]
    old_body = old_body.replace("[0064] " + old_paragraphs["0064"], "[0064] " + new_paragraphs["0064"], 1)
    old_map, new_map = PurePosixPath(OXIDE_MAP).name, PurePosixPath(PHASE_MAP).name
    require(old_body.count(old_map) == body.count(new_map) == 1 and old_map not in body,
            "Phase companion-map reference differs")
    require(body.replace(PHASE_HEADING + block, "", 1) == old_body.replace(old_map, new_map, 1),
            "Phase source changed outside identified additions")
    account = re.findall(r"^Zhang et al\.[^\n]+$", block, re.M)
    require(len(account) == 1 and hashlib.sha256(" ".join(account[0].split()).encode("utf-8")).hexdigest()
            == PHASE_ACCOUNT_SHA256, "Phase reviewed source account differs")
    for path, expected in ((PHASE_REVIEW, PHASE_REVIEW_SHA256), (PHASE_RECORD, PHASE_RECORD_SHA256)):
        require(hashlib.sha256((root / path).read_bytes()).hexdigest() == expected,
                "Phase reviewed input identity differs: " + path)
    record = load_json(root / PHASE_RECORD)
    composition, sites = record["composition"], record["site_and_charge_accounting"]
    # Independent count normalization, distinct site denominator and formal
    # charge balance; no production generator or specimen result is inferred.
    target = {"Ti": Fraction(4, 11), "O": Fraction(7, 11)}
    baseline = {"Ti": Fraction(1, 3), "O": Fraction(2, 3)}
    require(sum(target.values()) == sum(baseline.values()) == 1
            and composition["assigned_target_fractions"] == {k: str(v) for k, v in target.items()}
            and composition["changed_minus_baseline"] == {k: str(target[k] - baseline[k]) for k in target}
            and Fraction(sites["reference_vacancy_site_fraction"]) == Fraction(1, 8)
            and Fraction(sites["occupied_atom_O_fraction"]) == target["O"]
            and 3 * 2 + 4 * 2 - 2 * 7 == 0 and 10**19 % 11 != 0,
            "Phase exact count or denominator accounting differs")
    require(all(fragment in block for fragment in (
        "on a stipulated occupied-atom basis, not a feed, site or whole-product assay basis",
        "x_Ti = 4/11 and x_O = 7/11", "(+1/33,-1/33)", "V/(2*N_Ti) = 1/8",
        "candidate applicability and conditioning prerequisites PROPOSED",
        "optical results as UNSUPPORTED", "actual candidate outcomes UNSUPPORTED",
        "A(lambda)=1-R(lambda)-T(lambda)",
        "compatible total reflected/transmitted power fractions", "No candidate comparison has been performed.",
        "no original article bytes or PDF hash were acquired", "No permissive reuse grant is verified.",
    )), "Phase target basis or evidence boundary differs")
    require(hashlib.sha256(" ".join(block.split()).encode("utf-8")).hexdigest() == PHASE_BLOCK_SHA256,
            "Phase reviewed record fields or qualifications differ")
    edition = load_json(root / PHASE_EDITION)
    require(edition.get("prepared_date") == "2026-10-01"
            and edition.get("edition_status") == "prospective unfiled phase-specific-evidence edition"
            and edition.get("repository_baseline") == PHASE_BASELINE
            and edition.get("filing_asserted") is False and edition.get("physical_enablement_certified") is False,
            "Phase edition baseline or factual status differs")
    expected_sources = {PHASE_SOURCE, PHASE_MAP, PHASE_REVIEW, PHASE_RECORD, OXIDE_REVIEW,
                        PREPARATION_REVIEW, ELECTRICAL_REVIEW, *PHASE_AUTHORING,
                        "documents/drawings/composition_simplex.svg", "documents/drawings/material_record_sequence.svg"}
    entries = edition.get("sources", [])
    require(len(entries) == len(expected_sources) and {e["path"] for e in entries} == expected_sources,
            "Phase PDF source inventory differs")
    for entry in entries:
        snapshot = PHASE_AUTHORING.get(entry["path"])
        require(entry.get("snapshot_path") == snapshot
                and hashlib.sha256(safe_path(root, snapshot or entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
                "Phase PDF captured-source identity differs")
    pdf = edition.get("pdf", {})
    require(pdf.get("path") == PHASE_PDF and type(pdf.get("page_count")) is int and pdf["page_count"] > 0,
            "Invalid phase PDF identity")
    data = safe_path(root, PHASE_PDF).read_bytes()
    require(len(data) == pdf.get("size_bytes") and hashlib.sha256(data).hexdigest() == pdf.get("sha256"),
            "Phase PDF bytes differ from record")
    locations = edition.get("location_map", {})
    require(locations.keys() == {f"paragraph_{n:04d}" for n in range(1, 81)} | {f"claim_{n}" for n in range(1, 200)}
            and all(type(page) is int and 1 <= page <= pdf["page_count"] for page in locations.values()),
            "Phase PDF recorded locations differ")
    require(edition.get("complete_numbered_text_checked") == {"paragraphs": 80, "claims": 199}
            and edition.get("vector_drawings_checked") == 2
            and edition.get("complete_phase_specific_text_checked") == evidence_block_counts(block)
            and edition.get("complete_property_table_checked") == {
                "data_rows": 10, "columns": 4, "headers_and_complete_rows_checked_in_order": True},
            "Phase recorded application coverage differs")
    for key, heading, ending in (
        ("complete_preparation_text_checked", PREPARATION_HEADING, "0066"),
        ("complete_electrical_text_checked", ELECTRICAL_HEADING, "0067"),
        ("complete_oxide_defect_text_checked", OXIDE_HEADING, "0065"),
    ):
        require(edition.get(key) == evidence_block_counts(evidence_block(body, heading, ending)),
                "Phase inherited block coverage differs: " + key)
    visual = edition.get("visual_review", {})
    require(isinstance(visual, dict) and visual.get("status") == "completed"
            and visual.get("pages_reviewed") == list(range(1, pdf["page_count"] + 1))
            and visual.get("remaining_actionable_visual_findings") == 0,
            "Phase recorded appearance review is incomplete")
    return {**claims, "changed_paragraphs": ["0064"], "changed_claims": [],
            "captured_sources_checked": len(entries), "recorded_pdf_pages": pdf["page_count"],
            "recorded_pdf_locations_checked": len(locations), "new_source_account_words": len(account[0].split()),
            "preceding_evidence_and_remaining_body_preserved": True,
            "physical_realization_or_filing_or_earlier_entitlement_certified": False,
            "pdf_parsed_or_appearance_rechecked_by_this_check": False}


def check_family_application(root: Path) -> dict:
    """Check the seventh edition's preserved body and three qualified records.

    Count models use declared subinventories, chain assumptions and dry-input
    categories. These checks establish neither preparation nor legal coverage.
    """
    previous_bytes = (root / PHASE_SOURCE).read_bytes()
    source_bytes = (root / FAMILY_SOURCE).read_bytes()
    previous, application = previous_bytes.decode("utf-8"), source_bytes.decode("utf-8")
    support = load_json(root / FAMILY_MAP)
    require(support.get("source_path") == FAMILY_SOURCE and support.get("source_sha256")
            == hashlib.sha256(source_bytes).hexdigest(), "Family source/map hash differs")
    require(support.get("prepared_date") == "2026-10-01" and support.get("derived_from") == {
        "path": PHASE_SOURCE, "sha256": hashlib.sha256(previous_bytes).hexdigest(),
        "repository_baseline": FAMILY_BASELINE,
    }, "Family source derivation differs")
    require(support.get("claims") == load_json(root / PHASE_MAP).get("claims")
            and support.get("changed_claims") == [] and support.get("changed_paragraphs") == ["0040"],
            "Family individual claim records or change inventory differ")
    claims = check_claims(application, support)
    old_paragraphs = dict(re.findall(r"^\[(\d{4})\] (.+)$", previous, re.M))
    new_paragraphs = dict(re.findall(r"^\[(\d{4})\] (.+)$", application, re.M))
    require(old_paragraphs.keys() == new_paragraphs.keys()
            and {n for n in old_paragraphs if old_paragraphs[n] != new_paragraphs[n]} == {"0040"},
            "Unexpected family paragraph changes")
    pointer = (" The following selected molecular, polymer and composite records supply attributed operations, "
               "present composition accounting and conditional inquiries; candidate realization and broader applicability remain unresolved.")
    require(new_paragraphs["0040"] == old_paragraphs["0040"] + pointer,
            "Family preparation paragraph or pointer differs")
    boundary = "## 1 Technical field\n"
    require(application.count(boundary) == previous.count(boundary) == 1,
            "Family technical-field boundary differs")
    preface, body = application.split(boundary)
    lines = [line for line in preface.splitlines() if line]
    require(len(lines) == 4 and lines[0]
            == "# Provisional materials disclosure with molecular, polymer and composite evidence - 1 October 2026"
            and lines[1] == "Prepared **1 October 2026** | **Prospective unfiled family-evidence edition** for applicant and patent counsel.",
            "Family edition preface differs")
    require(hashlib.sha256(" ".join(preface.split()).encode("utf-8")).hexdigest() == FAMILY_PREFACE_SHA256,
            "Family reviewed preface qualifications differ")
    starts = [list(re.finditer(r"^" + re.escape(h) + r"$", body, re.M)) for h in FAMILY_HEADINGS.values()]
    ends = list(re.finditer(r"^\[0041\] ", body, re.M))
    require(all(len(s) == 1 for s in starts) and len(ends) == 1,
            "Missing or ambiguous family evidence boundary")
    positions = [s[0] for s in starts]
    require(positions[0].start() < positions[1].start() < positions[2].start() < ends[0].start(),
            "Family evidence order differs")
    spans, blocks = {}, {}
    for i, key in enumerate(FAMILY_HEADINGS):
        end = positions[i + 1].start() if i < 2 else ends[0].start()
        spans[key] = body[positions[i].start():end]
        blocks[key] = body[positions[i].end():end]
    old_body = previous.split(boundary, 1)[1]
    old_body = old_body.replace("[0040] " + old_paragraphs["0040"], "[0040] " + new_paragraphs["0040"], 1)
    old_map, new_map = PurePosixPath(PHASE_MAP).name, PurePosixPath(FAMILY_MAP).name
    require(old_body.count(old_map) == body.count(new_map) == 1 and old_map not in body,
            "Family companion-map reference differs")
    remaining = body[:positions[0].start()] + body[ends[0].start():]
    require(remaining == old_body.replace(old_map, new_map, 1),
            "Family source changed outside identified additions")
    # Assert the intended basis/status before full pins, so coherent negative
    # fixtures demonstrate rejection at their concrete evidence boundary.
    require("actual candidate outcomes UNSUPPORTED" in blocks["molecular"]
            and "actual candidate outcomes UNSUPPORTED" in blocks["polymer"]
            and "actual candidate outcomes UNSUPPORTED" in blocks["composite"],
            "Family candidate outcome status differs")
    require("selected-crystallite count quantities, not bulk mass or volume phase fractions" in blocks["molecular"],
            "Family molecular occurrence basis differs")
    require("distinct from elemental fractions, repeat populations and final retained composition" in blocks["polymer"],
            "Family polymer feed basis differs")
    require("not the source's actual batch masses, a stoichiometric cure prescription or retained cured-product assay" in blocks["composite"],
            "Family composite conditional basis differs")
    for key, span in spans.items():
        require(hashlib.sha256(" ".join(span.split()).encode("utf-8")).hexdigest() == FAMILY_BLOCK_SHA256[key],
                "Family reviewed block qualifications differ: " + key)
    require(hashlib.sha256((root / FAMILY_REVIEW).read_bytes()).hexdigest() == FAMILY_REVIEW_SHA256,
            "Family reviewed source identities differ")
    review = load_json(root / FAMILY_REVIEW)
    require(review.get("application_source_path") == FAMILY_SOURCE
            and review.get("historical_context_path") == FAMILY_CONTEXT
            and review.get("historical_context_sha256") == hashlib.sha256((root / FAMILY_CONTEXT).read_bytes()).hexdigest(),
            "Family historical context differs")
    sources = review.get("primary_sources", [])
    require(len(sources) == 3 and [s["id"] for s in sources] == list(FAMILY_HEADINGS),
            "Family primary-source inventory differs")
    for s in sources:
        account = blocks[s["id"]].strip().splitlines()[0]
        require(s.get("application_source_path") == FAMILY_SOURCE
                and s.get("reviewed_block_sha256") == FAMILY_BLOCK_SHA256[s["id"]]
                and s.get("selected_account_sha256") == hashlib.sha256(" ".join(account.split()).encode()).hexdigest(),
                "Family source account identity differs")
    # Independent formula-unit normalization and conditional finite inventories;
    # the production enumeration routines and source outcomes are not oracles.
    accounting = review["present_accounting"]
    for key, counts, target in (
        ("unsolvated", (12, 15, 2, 1), ("2/5", "1/2", "1/15", "1/30")),
        ("dihydrate", (16, 15, 2, 3), ("4/9", "5/12", "1/18", "1/12")),
    ):
        normalized = tuple(str(Fraction(n, sum(counts))) for n in counts)
        require(normalized == target
                and accounting["molecular"][key + "_atom_counts"] == list(counts)
                and accounting["molecular"][key + "_fractions"] == list(target),
                "Family molecular count accounting differs")
    for m, q in ((1, 0), (1, 2), (3, 6), (2, 7)):
        counts = (12*m + 2*q, 15*m, 2*m, m + q)
        require(sum(counts) == 30*m + 3*q and all(n > 0 for n in counts),
                "Family conditional water inventory differs")
    repeat = tuple(str(Fraction(n, 9)) for n in (3, 4, 2))
    require(accounting["polymer"]["ideal_repeat_counts"] == [3, 4, 2]
            and accounting["polymer"]["ideal_repeat_fractions"] == list(repeat),
            "Family polymer repeat accounting differs")
    for r, k in ((1, 1), (3, 1), (3, 3), (100, 7)):
        counts = (3*r, 4*r + 2*k, 2*r + k)
        require(sum(counts) == 9*r + 3*k and sum(Fraction(n, sum(counts)) for n in counts) == 1,
                "Family conditional chain inventory differs")
    stock, target = Fraction(1, 100), Fraction(9, 1250)
    dispersion = target / stock
    dry = (target, (1-stock)*dispersion, 1-dispersion)
    require(sum(dry) == 1 and all(x > 0 for x in dry)
            and accounting["composite"]["conditional_stock_fraction"] == str(dispersion)
            and accounting["composite"]["conditional_dry_fractions"] == [str(x) for x in dry],
            "Family conditional dry-input accounting differs")
    edition = load_json(root / FAMILY_EDITION)
    require(edition.get("prepared_date") == "2026-10-01"
            and edition.get("edition_status") == "prospective unfiled family-evidence edition"
            and edition.get("repository_baseline") == FAMILY_BASELINE
            and edition.get("filing_asserted") is False and edition.get("physical_enablement_certified") is False,
            "Family edition baseline or factual status differs")
    expected_sources = {FAMILY_SOURCE, FAMILY_MAP, FAMILY_REVIEW, FAMILY_CONTEXT, PHASE_REVIEW, PHASE_RECORD,
                        OXIDE_REVIEW, PREPARATION_REVIEW, ELECTRICAL_REVIEW, *FAMILY_AUTHORING,
                        "documents/drawings/composition_simplex.svg", "documents/drawings/material_record_sequence.svg"}
    entries = edition.get("sources", [])
    require(len(entries) == 14 and {e["path"] for e in entries} == expected_sources,
            "Family PDF source inventory differs")
    for entry in entries:
        snapshot = FAMILY_AUTHORING.get(entry["path"])
        require(entry.get("snapshot_path") == snapshot
                and hashlib.sha256(safe_path(root, snapshot or entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
                "Family PDF captured-source identity differs")
    pdf = edition.get("pdf", {})
    require(pdf.get("path") == FAMILY_PDF and type(pdf.get("page_count")) is int and pdf["page_count"] > 0,
            "Invalid family PDF identity")
    data = safe_path(root, FAMILY_PDF).read_bytes()
    require(len(data) == pdf.get("size_bytes") and hashlib.sha256(data).hexdigest() == pdf.get("sha256"),
            "Family PDF bytes differ from record")
    locations = edition.get("location_map", {})
    require(locations.keys() == {f"paragraph_{n:04d}" for n in range(1, 81)} | {f"claim_{n}" for n in range(1, 200)}
            and all(type(page) is int and 1 <= page <= pdf["page_count"] for page in locations.values()),
            "Family PDF recorded locations differ")
    require(edition.get("complete_numbered_text_checked") == {"paragraphs": 80, "claims": 199}
            and edition.get("vector_drawings_checked") == 2
            and edition.get("complete_family_text_checked") == {k: evidence_block_counts(b) for k, b in blocks.items()}
            and edition.get("complete_phase_specific_text_checked") == evidence_block_counts(evidence_block(body, PHASE_HEADING, "0065").split(OXIDE_HEADING, 1)[0]),
            "Family recorded new or inherited phase coverage differs")
    prior_edition = load_json(root / PHASE_EDITION)
    for key in ("complete_preparation_text_checked", "complete_electrical_text_checked",
                "complete_oxide_defect_text_checked", "complete_property_table_checked"):
        require(edition.get(key) == prior_edition.get(key), "Family inherited block coverage differs: " + key)
    visual = edition.get("visual_review", {})
    require(isinstance(visual, dict) and visual.get("status") == "completed"
            and visual.get("pages_reviewed") == list(range(1, pdf["page_count"] + 1))
            and visual.get("remaining_actionable_visual_findings") == 0,
            "Family recorded appearance review is incomplete")
    return {**claims, "changed_paragraphs": ["0040"], "changed_claims": [],
            "captured_sources_checked": len(entries), "recorded_pdf_pages": pdf["page_count"],
            "recorded_pdf_locations_checked": len(locations), "qualified_family_records_checked": 3,
            "preceding_evidence_and_remaining_body_preserved": True,
            "physical_realization_or_filing_or_earlier_entitlement_certified": False,
            "pdf_parsed_or_appearance_rechecked_by_this_check": False}


def check_metal_glass_application(root: Path) -> dict:
    """Check the eighth edition's distinct inventories and preserved teaching.

    Principal targets and stipulated count witnesses are mathematics, not
    whole-specimen assays, successful preparations or legal conclusions.
    """
    previous_bytes = (root / FAMILY_SOURCE).read_bytes()
    source_bytes = (root / METAL_GLASS_SOURCE).read_bytes()
    previous, application = previous_bytes.decode("utf-8"), source_bytes.decode("utf-8")
    support = load_json(root / METAL_GLASS_MAP)
    require(support.get("source_path") == METAL_GLASS_SOURCE and support.get("source_sha256")
            == hashlib.sha256(source_bytes).hexdigest(), "Metal/glass source/map hash differs")
    require(support.get("prepared_date") == "2026-10-01" and support.get("derived_from") == {
        "path": FAMILY_SOURCE, "sha256": hashlib.sha256(previous_bytes).hexdigest(),
        "repository_baseline": METAL_GLASS_BASELINE,
    }, "Metal/glass source derivation differs")
    require(support.get("claims") == load_json(root / FAMILY_MAP).get("claims")
            and support.get("changed_claims") == [] and support.get("changed_paragraphs") == ["0039", "0063"],
            "Metal/glass individual claim records or change inventory differ")
    claims = check_claims(application, support)
    old_paragraphs = dict(re.findall(r"^\[(\d{4})\] (.+)$", previous, re.M))
    new_paragraphs = dict(re.findall(r"^\[(\d{4})\] (.+)$", application, re.M))
    require(old_paragraphs.keys() == new_paragraphs.keys()
            and {n for n in old_paragraphs if old_paragraphs[n] != new_paragraphs[n]} == set(METAL_GLASS_POINTERS),
            "Unexpected metal/glass paragraph changes")
    for paragraph, key in (("0039", "alloy"), ("0063", "glass")):
        require(new_paragraphs[paragraph] == old_paragraphs[paragraph] + METAL_GLASS_POINTERS[paragraph],
                "Metal/glass " + key + " preparation paragraph or pointer differs")
    boundary = "## 1 Technical field\n"
    require(application.count(boundary) == previous.count(boundary) == 1,
            "Metal/glass technical-field boundary differs")
    preface, body = application.split(boundary)
    lines = [line for line in preface.splitlines() if line]
    require(len(lines) == 4 and lines[0]
            == "# Provisional materials disclosure with metal and glass evidence - 1 October 2026"
            and lines[1] == "Prepared **1 October 2026** | **Prospective unfiled metal-glass-evidence edition** for applicant and patent counsel.",
            "Metal/glass edition preface differs")
    require(hashlib.sha256(" ".join(preface.split()).encode("utf-8")).hexdigest() == METAL_GLASS_PREFACE_SHA256,
            "Metal/glass reviewed preface qualifications differ")
    blocks = {}
    for key, previous_number, next_number in (("alloy", "0039", "0040"), ("glass", "0063", "0064")):
        heading = METAL_GLASS_HEADINGS[key]
        block = evidence_block(body, heading, next_number)
        require(body.index("[" + previous_number + "] ") < body.index(heading),
                "Metal/glass evidence placement differs: " + key)
        blocks[key] = block
    old_body = previous.split(boundary, 1)[1]
    for paragraph in METAL_GLASS_POINTERS:
        old_body = old_body.replace("[" + paragraph + "] " + old_paragraphs[paragraph],
                                    "[" + paragraph + "] " + new_paragraphs[paragraph], 1)
    old_map, new_map = PurePosixPath(FAMILY_MAP).name, PurePosixPath(METAL_GLASS_MAP).name
    require(old_body.count(old_map) == body.count(new_map) == 1 and old_map not in body,
            "Metal/glass companion-map reference differs")
    remaining = body
    for key, block in blocks.items():
        remaining = remaining.replace(METAL_GLASS_HEADINGS[key] + block, "", 1)
    require(remaining == old_body.replace(old_map, new_map, 1),
            "Metal/glass source changed outside identified additions")
    # Concrete evidence boundaries precede full pins so coherently refreshed
    # fixtures fail at the actual unsupported outcome or denominator change.
    require(all("actual candidate outcomes UNSUPPORTED" in b for b in blocks.values()),
            "Metal/glass candidate outcome status differs")
    require("and f is not assumed one" in blocks["alloy"]
            and "The target r_target is not substituted for measured r_i" in blocks["alloy"]
            and "The source-nominal r_target does not supply measured r_i or f" in blocks["glass"],
            "Metal/glass principal/whole inventory basis differs")
    for key, block in blocks.items():
        span = METAL_GLASS_HEADINGS[key] + block
        require(hashlib.sha256(" ".join(span.split()).encode("utf-8")).hexdigest() == METAL_GLASS_BLOCK_SHA256[key],
                "Metal/glass reviewed block qualifications differ: " + key)
    review_bytes = (root / METAL_GLASS_REVIEW).read_bytes()
    review = load_json(root / METAL_GLASS_REVIEW)
    require(review.get("application_source_path") == METAL_GLASS_SOURCE,
            "Metal/glass review application pointer differs")
    accounting = review["present_accounting"]
    require(accounting["whole_transfer"].get("target_substituted_for_measured_ratios") is False
            and accounting["whole_transfer"].get("f_assumed_one") is False
            and accounting["whole_transfer"].get("unknown_constituents_resolved") is False,
            "Metal/glass principal/whole inventory basis differs")
    status = review.get("present_record_status", {})
    require(status.get("candidate_preparation_performed") is False
            and status.get("candidate_outcomes") == "UNSUPPORTED"
            and status.get("conditional_scenarios") == "PROPOSED",
            "Metal/glass candidate outcome status differs")
    # Normalize the stipulated counts directly; production generators and
    # physical measurements are not used as mathematical test oracles.
    from math import gcd, lcm
    alloy = accounting["alloy"]
    require([len(s) for s in alloy["ordered_principal_supports"]] == [4, 5]
            and alloy["principal_targets"] == [[str(Fraction(1, n))] * n for n in (4, 5)],
            "Metal/glass nominal principal accounting differs")
    glass = accounting["glass"]
    counts = tuple(glass["principal_counts"])
    require(counts == (32, 5, 160, 87, 686, 30)
            and all(type(n) is int and n > 0 for n in counts)
            and len(glass["ordered_principal_support"]) == len(counts)
            and glass["principal_total"] == sum(counts) == 1000
            and glass["principal_target"] == [str(Fraction(n, sum(counts))) for n in counts]
            and gcd(*counts) == 1 and 10**19 % sum(counts) == 0,
            "Metal/glass nominal principal accounting differs")
    for m, c in ((1, 0), (1, 1), (2, 3)):
        occupied = ((c,) if c else ()) + (m,) * 4
        require(len(occupied) == (5 if c else 4) and all(n > 0 for n in occupied)
                and sum(occupied) == 4*m + c
                and sum(Fraction(n, sum(occupied)) for n in occupied) == 1,
                "Metal/glass additional-count support differs")
    witness = alloy["below_grid"]
    scale = 10**20
    occupied = (4,) + (scale-1,) * 4
    total = sum(occupied)
    fractions = tuple(Fraction(n, total) for n in occupied)
    primitive = total // gcd(*occupied)
    require(witness.get("L") == str(scale) and witness.get("c") == "4"
            and witness.get("m") == str(scale-1) and witness.get("total") == str(total)
            and witness.get("fractions") == [str(x) for x in fractions]
            and witness.get("primitive_denominator") == str(primitive)
            and primitive == lcm(*(x.denominator for x in fractions)) == 4*scale
            and 0 < fractions[0] < Fraction(1, 10**19) and sum(fractions) == 1,
            "Metal/glass below-grid count accounting differs")
    require(hashlib.sha256(review_bytes).hexdigest() == METAL_GLASS_REVIEW_SHA256,
            "Metal/glass reviewed source identities differ")
    sources = review.get("primary_sources", [])
    require(len(sources) == 2 and [s["id"] for s in sources] == list(METAL_GLASS_HEADINGS),
            "Metal/glass primary-source inventory differs")
    for source in sources:
        account = blocks[source["id"]].strip().splitlines()[0]
        require(source.get("application_source_path") == METAL_GLASS_SOURCE
                and source.get("reviewed_block_sha256") == METAL_GLASS_BLOCK_SHA256[source["id"]]
                and source.get("selected_account_sha256") == hashlib.sha256(" ".join(account.split()).encode("utf-8")).hexdigest(),
                "Metal/glass source account identity differs")
    edition = load_json(root / METAL_GLASS_EDITION)
    require(edition.get("prepared_date") == "2026-10-01"
            and edition.get("edition_status") == "prospective unfiled metal-glass-evidence edition"
            and edition.get("repository_baseline") == METAL_GLASS_BASELINE
            and edition.get("filing_asserted") is False and edition.get("physical_enablement_certified") is False,
            "Metal/glass edition baseline or factual status differs")
    expected_sources = {METAL_GLASS_SOURCE, METAL_GLASS_MAP, METAL_GLASS_REVIEW, FAMILY_REVIEW, FAMILY_CONTEXT,
                        PHASE_REVIEW, PHASE_RECORD, OXIDE_REVIEW, PREPARATION_REVIEW, ELECTRICAL_REVIEW,
                        *METAL_GLASS_AUTHORING, "documents/drawings/composition_simplex.svg",
                        "documents/drawings/material_record_sequence.svg"}
    entries = edition.get("sources", [])
    require(len(entries) == 15 and {e["path"] for e in entries} == expected_sources,
            "Metal/glass PDF source inventory differs")
    for entry in entries:
        snapshot = METAL_GLASS_AUTHORING.get(entry["path"])
        require(entry.get("snapshot_path") == snapshot
                and hashlib.sha256(safe_path(root, snapshot or entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
                "Metal/glass PDF captured-source identity differs")
    pdf = edition.get("pdf", {})
    require(pdf.get("path") == METAL_GLASS_PDF and type(pdf.get("page_count")) is int and pdf["page_count"] > 0,
            "Invalid metal/glass PDF identity")
    data = safe_path(root, METAL_GLASS_PDF).read_bytes()
    require(len(data) == pdf.get("size_bytes") and hashlib.sha256(data).hexdigest() == pdf.get("sha256"),
            "Metal/glass PDF bytes differ from record")
    locations = edition.get("location_map", {})
    require(locations.keys() == {f"paragraph_{n:04d}" for n in range(1, 81)} | {f"claim_{n}" for n in range(1, 200)}
            and all(type(page) is int and 1 <= page <= pdf["page_count"] for page in locations.values()),
            "Metal/glass PDF recorded locations differ")
    require(edition.get("complete_numbered_text_checked") == {"paragraphs": 80, "claims": 199}
            and edition.get("vector_drawings_checked") == 2
            and edition.get("complete_metal_glass_text_checked") == {k: evidence_block_counts(b) for k, b in blocks.items()},
            "Metal/glass recorded new text coverage differs")
    family_blocks = {
        "molecular": evidence_block(body, FAMILY_HEADINGS["molecular"], "0041").split(FAMILY_HEADINGS["polymer"], 1)[0],
        "polymer": evidence_block(body, FAMILY_HEADINGS["polymer"], "0041").split(FAMILY_HEADINGS["composite"], 1)[0],
        "composite": evidence_block(body, FAMILY_HEADINGS["composite"], "0041"),
    }
    require(edition.get("complete_family_text_checked") == {k: evidence_block_counts(b) for k, b in family_blocks.items()},
            "Metal/glass inherited family coverage differs")
    prior_edition = load_json(root / FAMILY_EDITION)
    for key in ("complete_family_text_checked", "complete_phase_specific_text_checked", "complete_preparation_text_checked",
                "complete_electrical_text_checked", "complete_oxide_defect_text_checked", "complete_property_table_checked"):
        require(edition.get(key) == prior_edition.get(key), "Metal/glass inherited block coverage differs: " + key)
    visual = edition.get("visual_review", {})
    require(isinstance(visual, dict) and visual.get("status") == "completed"
            and visual.get("pages_reviewed") == list(range(1, pdf["page_count"] + 1))
            and visual.get("remaining_actionable_visual_findings") == 0,
            "Metal/glass recorded appearance review is incomplete")
    return {**claims, "changed_paragraphs": ["0039", "0063"], "changed_claims": [],
            "captured_sources_checked": len(entries), "recorded_pdf_pages": pdf["page_count"],
            "recorded_pdf_locations_checked": len(locations), "qualified_metal_glass_records_checked": 2,
            "preceding_evidence_and_remaining_body_preserved": True,
            "physical_realization_or_filing_or_earlier_entitlement_certified": False,
            "pdf_parsed_or_appearance_rechecked_by_this_check": False}


def check_theoretical_application(root: Path) -> dict:
    """Verify the complete unfiled review draft, without certifying support.

    The new map alone defines its paragraph count. Fixed historical checks
    still verify the preserved 80-paragraph editions independently.
    """
    previous_bytes = (root / METAL_GLASS_SOURCE).read_bytes()
    source_bytes = (root / THEORETICAL_SOURCE).read_bytes()
    previous, application = previous_bytes.decode("utf-8"), source_bytes.decode("utf-8")
    support = load_json(root / THEORETICAL_MAP)
    require(support.get("source_path") == THEORETICAL_SOURCE and support.get("source_sha256")
            == hashlib.sha256(source_bytes).hexdigest(), "Theoretical source/map hash differs")
    require(support.get("prepared_date") == "2026-10-01" and support.get("derived_from") == {
        "path": METAL_GLASS_SOURCE, "sha256": hashlib.sha256(previous_bytes).hexdigest(),
        "repository_baseline": THEORETICAL_BASELINE,
    }, "Theoretical source derivation differs")
    require(support.get("claims") == load_json(root / METAL_GLASS_MAP).get("claims")
            and support.get("changed_claims") == [], "Theoretical individual claim records differ")
    paragraph_count = support.get("source_paragraph_count")
    require(type(paragraph_count) is int and 80 < paragraph_count <= 9999,
            "Invalid theoretical paragraph count")
    matches = re.findall(r"^\[(\d{4})\] (.+)$", application, re.M)
    ids = [n for n, _ in matches]
    require(ids == [f"{n:04d}" for n in range(1, paragraph_count + 1)],
            "Theoretical paragraph IDs must be contiguous and ordered")
    added = ids[80:]
    require(support.get("changed_paragraphs") == [] and support.get("added_paragraphs") == added,
            "Theoretical paragraph change inventory differs")
    old_paragraphs = re.findall(r"^\[(\d{4})\] (.+)$", previous, re.M)
    require(matches[:80] == old_paragraphs, "Theoretical inherited numbered paragraphs differ")
    require(support.get("proposed_inventor") == THEORETICAL_INVENTOR
            and support.get("universal_blocking_status") == "ASPIRATIONAL_NOT_ESTABLISHED"
            and support.get("applicant_physical_experiments") == "UNPERFORMED_NOT_PLANNED",
            "Theoretical review designation or evidence status differs")
    boundary = "## 1 Technical field\n"
    require(application.count(boundary) == previous.count(boundary) == 1,
            "Theoretical technical-field boundary differs")
    preface, body = application.split(boundary)
    require("Proposed sole inventor: Robert M. Layne" in preface
            and "universal blocking is aspirational" in preface
            and "No applicant physical experiments are performed or planned." in preface,
            "Theoretical preface review designation or evidence status differs")
    require(hashlib.sha256(" ".join(preface.split()).encode("utf-8")).hexdigest() == THEORETICAL_PREFACE_SHA256,
            "Theoretical reviewed preface qualifications differ")
    require(body.count(THEORETICAL_HEADING) == body.count("## 16 Draft abstract") == 1,
            "Theoretical hypothetical-section boundary differs")
    start, end = body.index(THEORETICAL_HEADING), body.index("## 16 Draft abstract")
    require(body.index("[0080] ") < start < end, "Theoretical hypothetical-section placement differs")
    block = body[start + len(THEORETICAL_HEADING):end]
    require([n for n, _ in re.findall(r"^\[(\d{4})\] (.+)$", block, re.M)] == added,
            "Theoretical added paragraphs lie outside the reviewed section")
    require(all(status in block for status in ("ESTABLISHED", "CALCULATED", "PROPOSED", "UNSUPPORTED")),
            "Theoretical hypothetical evidence labels differ")
    require(hashlib.sha256(" ".join((THEORETICAL_HEADING + block).split()).encode("utf-8")).hexdigest()
            == THEORETICAL_BLOCK_SHA256, "Theoretical reviewed hypothetical qualifications differ")
    old_body = previous.split(boundary, 1)[1]
    old_map, new_map = PurePosixPath(METAL_GLASS_MAP).name, PurePosixPath(THEORETICAL_MAP).name
    require(old_body.count(old_map) == body.count(new_map) == 1 and old_map not in body,
            "Theoretical companion-map reference differs")
    require(old_body.count(THEORETICAL_SOURCE_NOTE_OLD) == body.count(THEORETICAL_SOURCE_NOTE_NEW) == 1,
            "Theoretical source-note review designation differs")
    expected_body = old_body.replace(old_map, new_map, 1).replace(THEORETICAL_SOURCE_NOTE_OLD,
                                                                THEORETICAL_SOURCE_NOTE_NEW, 1)
    remaining = body[:start] + body[end:]
    require(remaining == expected_body, "Theoretical source changed outside identified additions")
    # The original checker continues to enforce all 199 wordings, dependencies
    # and per-claim statuses against an 80-paragraph representation. Only the
    # new section is removed; its contiguous IDs and complete pin were checked.
    claims = check_claims(preface + boundary + remaining, {**support, "source_paragraph_count": 80})
    edition = load_json(root / THEORETICAL_EDITION)
    require(edition.get("prepared_date") == "2026-10-01"
            and edition.get("edition_status") == "complete unfiled theoretical provisional review draft"
            and edition.get("repository_baseline") == THEORETICAL_BASELINE
            and edition.get("filing_asserted") is False and edition.get("physical_enablement_certified") is False,
            "Theoretical edition baseline or factual status differs")
    require(edition.get("proposed_inventor") == THEORETICAL_INVENTOR
            and edition.get("universal_blocking_status") == "ASPIRATIONAL_NOT_ESTABLISHED"
            and edition.get("applicant_physical_experiments") == "UNPERFORMED_NOT_PLANNED",
            "Theoretical edition review designation or evidence status differs")
    expected_sources = {THEORETICAL_SOURCE, THEORETICAL_MAP, METAL_GLASS_REVIEW, FAMILY_REVIEW, FAMILY_CONTEXT,
                        PHASE_REVIEW, PHASE_RECORD, OXIDE_REVIEW, PREPARATION_REVIEW, ELECTRICAL_REVIEW,
                        *THEORETICAL_AUTHORING, "documents/drawings/composition_simplex.svg",
                        "documents/drawings/material_record_sequence.svg"}
    entries = edition.get("sources", [])
    require(len(entries) == 15 and {e["path"] for e in entries} == expected_sources,
            "Theoretical PDF source inventory differs")
    for entry in entries:
        snapshot = THEORETICAL_AUTHORING.get(entry["path"])
        require(entry.get("snapshot_path") == snapshot
                and hashlib.sha256(safe_path(root, snapshot or entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
                "Theoretical PDF captured-source identity differs")
    pdf = edition.get("pdf", {})
    require(pdf.get("path") == THEORETICAL_PDF and type(pdf.get("page_count")) is int and pdf["page_count"] > 0,
            "Invalid theoretical PDF identity")
    data = safe_path(root, THEORETICAL_PDF).read_bytes()
    require(data.startswith(b"%PDF-") and b"%%EOF" in data[-1024:]
            and len(data) == pdf.get("size_bytes") and hashlib.sha256(data).hexdigest() == pdf.get("sha256"),
            "Theoretical PDF bytes differ from record")
    locations = edition.get("location_map", {})
    require(locations.keys() == {f"paragraph_{n:04d}" for n in range(1, paragraph_count + 1)}
            | {f"claim_{n}" for n in range(1, 200)}
            and all(type(page) is int and 1 <= page <= pdf["page_count"] for page in locations.values()),
            "Theoretical PDF recorded locations differ")
    require(edition.get("complete_numbered_text_checked") == {"paragraphs": paragraph_count, "claims": 199}
            and edition.get("vector_drawings_checked") == 2
            and edition.get("complete_theoretical_review_text_checked") == evidence_block_counts(block)
            and edition.get("complete_theoretical_preface_checked") == evidence_block_counts(preface),
            "Theoretical recorded new text coverage differs")
    previous_edition = load_json(root / METAL_GLASS_EDITION)
    for key in ("complete_metal_glass_text_checked", "complete_family_text_checked", "complete_phase_specific_text_checked",
                "complete_preparation_text_checked", "complete_electrical_text_checked", "complete_oxide_defect_text_checked",
                "complete_property_table_checked"):
        require(edition.get(key) == previous_edition.get(key), "Theoretical inherited block coverage differs: " + key)
    visual = edition.get("visual_review", {})
    require(isinstance(visual, dict) and visual.get("status") == "completed"
            and visual.get("pages_reviewed") == list(range(1, pdf["page_count"] + 1))
            and visual.get("remaining_actionable_visual_findings") == 0,
            "Theoretical recorded appearance review is incomplete")
    return {**claims, "numbered_paragraphs": paragraph_count, "added_paragraphs": added,
            "changed_paragraphs": [], "changed_claims": [], "captured_sources_checked": len(entries),
            "recorded_pdf_pages": pdf["page_count"], "recorded_pdf_locations_checked": len(locations),
            "preceding_evidence_and_remaining_body_preserved": True,
            "physical_realization_or_filing_or_legal_inventorship_certified": False,
            "pdf_parsed_or_appearance_rechecked_by_this_check": False}


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


def check_substantive_application(root: Path) -> dict:
    """Load the new edition checker from the supplied package or test fixture."""
    with module_environment(root / "tools"):
        module = import_local("substantive_review_checks", root / SUBSTANTIVE_CHECKER)
        arithmetic = import_local("technical_review_calculations", root / "tools/technical_review_calculations.py")
        require(module.FILES == SUBSTANTIVE_FILES, "Substantive verifier inventory differs")
        return module.check(root, require, safe_path, evidence_block_counts, arithmetic.check)


def run(root: Path) -> dict:
    require(__debug__, "Verification requires enabled assertions; run Python without -O, -OO or PYTHONOPTIMIZE.")
    file_count = check_inventory(root)
    hashed = check_integrity(root)
    application = (root / "documents/provisional_application_draft.md").read_text(encoding="utf-8")
    claim_result = check_claims(application, load_json(root / "data/claim_support_map.json"))
    working_result = check_working_application(root)
    property_result = check_property_application(root)
    preparation_result = check_preparation_application(root)
    electrical_result = check_electrical_application(root)
    oxide_result = check_oxide_application(root)
    phase_result = check_phase_application(root)
    family_result = check_family_application(root)
    metal_glass_result = check_metal_glass_application(root)
    theoretical_result = check_theoretical_application(root)
    substantive_result = check_substantive_application(root)
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
            "electrical_application_edition_verification": electrical_result,
            "oxide_defect_application_edition_verification": oxide_result,
            "phase_specific_application_edition_verification": phase_result,
            "family_application_edition_verification": family_result,
            "metal_glass_application_edition_verification": metal_glass_result,
            "theoretical_provisional_review_verification": theoretical_result,
            "substantive_provisional_review_verification": substantive_result,
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
        electrical_path, electrical_map_path = fixture / ELECTRICAL_SOURCE, fixture / ELECTRICAL_MAP
        electrical_review_path = fixture / ELECTRICAL_REVIEW
        originals = {path: path.read_bytes() for path in
                     (electrical_path, electrical_map_path, electrical_review_path)}
        check_electrical_application(fixture)
        for case, expected_error in (
            ("electrical_source_map_drift_rejected", "Electrical source/map hash differs"),
            ("electrical_claim_drift_rejected_after_consistent_map_update", "Electrical map changed individual claim records"),
            ("electrical_inherited_hydrogel_drift_rejected_after_consistent_map_update", "Electrical source changed outside the identified additions"),
            ("electrical_threshold_basis_drift_rejected_after_consistent_records", "Electrical threshold coordinate or basis differs"),
        ):
            try:
                text = originals[electrical_path].decode("utf-8")
                support = json.loads(originals[electrical_map_path])
                if case == "electrical_source_map_drift_rejected":
                    electrical_path.write_bytes(originals[electrical_path] + b"\nUnadopted addition.\n")
                else:
                    if "claim_drift" in case:
                        old_claim = support["claims"][0]["text"]
                        new_claim = old_claim.replace("positive normalized fraction", "nonnegative normalized fraction", 1)
                        require(old_claim != new_claim, "Electrical claim fixture lost its target")
                        text = text.replace("**Claim 1.** " + old_claim, "**Claim 1.** " + new_claim, 1)
                        support["claims"][0]["text"] = new_claim
                    elif "hydrogel_drift" in case:
                        row = "| 1.25 | 65.1 | 184 | 95 |"
                        require(text.count(row) == 1, "Electrical hydrogel fixture lost its target")
                        text = text.replace(row, row.replace("| 95 |", "| 96 |"), 1)
                    else:
                        # Keep the edited prose, map and review mutually
                        # consistent while confusing percent with fraction.
                        conversion = "p_c/100 = 443/100000"
                        require(text.count(conversion) == 1, "Electrical threshold fixture lost its target")
                        text = text.replace(conversion, "p_c/100 = 443/1000", 1)
                        review = json.loads(originals[electrical_review_path])
                        review["threshold_coordinate"]["calculated_fraction"] = "443/1000"
                        electrical_review_path.write_text(json.dumps(review), encoding="utf-8")
                    electrical_path.write_text(text, encoding="utf-8", newline="\n")
                    support["source_sha256"] = hashlib.sha256(electrical_path.read_bytes()).hexdigest()
                    electrical_map_path.write_text(json.dumps(support), encoding="utf-8")
                try:
                    check_electrical_application(fixture)
                except VerificationError as error:
                    require(expected_error in str(error), "Electrical mutation failed for another reason: " + str(error))
                    extended.append(case)
                require(case in extended, "Electrical mutation was accepted: " + case)
            finally:
                for path, data in originals.items():
                    path.write_bytes(data)
        oxide_path, oxide_map_path, oxide_review_path = fixture / OXIDE_SOURCE, fixture / OXIDE_MAP, fixture / OXIDE_REVIEW
        oxide_edition_path = fixture / OXIDE_EDITION
        originals = {path: path.read_bytes() for path in
                     (oxide_path, oxide_map_path, oxide_review_path, oxide_edition_path, manifest_path)}
        check_oxide_application(fixture)
        for case, expected_error in (
            ("oxide_source_map_drift_rejected", "Oxide source/map hash differs"),
            ("oxide_claim_drift_rejected_after_consistent_map_update", "Oxide map changed individual claim records"),
            ("oxide_inherited_electrical_drift_rejected_after_consistent_map_update", "Oxide source changed outside the identified additions"),
            ("oxide_host_fraction_drift_rejected_after_consistent_records", "Oxide ideal-host fractions or canonical counts differ"),
            ("oxide_positron_carrier_confusion_rejected_after_consistent_records", "Oxide diagnostic or assay basis differs"),
            ("oxide_upstream_provenance_substitution_rejected_after_consistent_records", "Oxide reviewed upstream provenance differs"),
        ):
            try:
                text = originals[oxide_path].decode("utf-8")
                support = json.loads(originals[oxide_map_path])
                review = json.loads(originals[oxide_review_path])
                if case == "oxide_source_map_drift_rejected":
                    oxide_path.write_bytes(originals[oxide_path] + b"\nUnadopted addition.\n")
                elif "provenance_substitution" in case:
                    # Refresh both consistency layers to isolate the reviewed
                    # upstream pin, rather than merely catching a stale hash.
                    review["primary_article"] = "https://example.invalid/substituted-article"
                    review["acquired_public_sources"][0].update({
                        "source": review["primary_article"] + ".pdf",
                        "sha256": "0" * 64, "filename": "substituted_article.pdf",
                    })
                    oxide_review_path.write_text(json.dumps(review), encoding="utf-8")
                    edition = json.loads(originals[oxide_edition_path])
                    entries = [entry for entry in edition["sources"] if entry["path"] == OXIDE_REVIEW]
                    require(len(entries) == 1, "Oxide provenance fixture lost its captured-input target")
                    entries[0]["sha256"] = hashlib.sha256(oxide_review_path.read_bytes()).hexdigest()
                    oxide_edition_path.write_text(json.dumps(edition), encoding="utf-8")
                    refreshed = json.loads(originals[manifest_path])
                    for entry in refreshed["files"]:
                        if entry["path"] in {OXIDE_REVIEW, OXIDE_EDITION}:
                            changed = (fixture / entry["path"]).read_bytes()
                            entry.update(size_bytes=len(changed), sha256=hashlib.sha256(changed).hexdigest())
                    manifest_path.write_text(json.dumps(refreshed), encoding="utf-8")
                    check_integrity(fixture)
                else:
                    if "claim_drift" in case:
                        old_claim = support["claims"][0]["text"]
                        new_claim = old_claim.replace("positive normalized fraction", "nonnegative normalized fraction", 1)
                        require(old_claim != new_claim, "Oxide claim fixture lost its target")
                        text = text.replace("**Claim 1.** " + old_claim, "**Claim 1.** " + new_claim, 1)
                        support["claims"][0]["text"] = new_claim
                    elif "electrical_drift" in case:
                        row = "| PEDOT:PSS threshold | 0.443 wt% |"
                        require(text.count(row) == 1, "Oxide electrical fixture lost its target")
                        text = text.replace(row, row.replace("0.443", "0.444"), 1)
                    elif "host_fraction" in case:
                        # Confuse deficiency delta with a normalized Ti atom
                        # fraction and update both the prose and review case.
                        heading = "**Conditional charge model"
                        require(text.count(heading) == 1, "Oxide host fixture lost its target")
                        text = text.replace(heading, "At delta = 1/4, x_Ti = 1/4 and x_O = 3/4, with counts (1,3).\n\n" + heading, 1)
                        review["ideal_host_accounting"]["cases"][2].update({
                            "x_Ti": "1/4", "x_O": "3/4", "Ti_count": 1, "O_count": 3, "total_atoms": 4,
                        })
                        oxide_review_path.write_text(json.dumps(review), encoding="utf-8")
                    else:
                        diagnostics = re.findall(r"\bFigure 1f [^.\n]*\.", evidence_block(text, OXIDE_HEADING, "0065"))
                        require(len(diagnostics) == 1, "Oxide positron fixture lost its target")
                        diagnostic = diagnostics[0]
                        text = text.replace(diagnostic, "Figure 1f measures charge-carrier lifetimes for T-2.", 1)
                        review["source_basis"]["positron_lifetimes_are_charge_carrier_lifetimes"] = True
                        review["source_basis"]["T2_positron_values_present_in_Figure_1f"] = True
                        oxide_review_path.write_text(json.dumps(review), encoding="utf-8")
                    oxide_path.write_text(text, encoding="utf-8", newline="\n")
                    support["source_sha256"] = hashlib.sha256(oxide_path.read_bytes()).hexdigest()
                    oxide_map_path.write_text(json.dumps(support), encoding="utf-8")
                try:
                    check_oxide_application(fixture)
                except VerificationError as error:
                    require(expected_error in str(error), "Oxide mutation failed for another reason: " + str(error))
                    extended.append(case)
                require(case in extended, "Oxide mutation was accepted: " + case)
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

        phase_path, phase_map_path = fixture / PHASE_SOURCE, fixture / PHASE_MAP
        phase_review_path, phase_edition_path = fixture / PHASE_REVIEW, fixture / PHASE_EDITION
        originals = {path: path.read_bytes() for path in
                     (phase_path, phase_map_path, phase_review_path, phase_edition_path, manifest_path)}
        check_phase_application(fixture)
        for case, expected_error in (
            ("phase_source_map_drift_rejected", "Phase source/map hash differs"),
            ("phase_claim_drift_rejected_after_consistent_records", "Phase individual claim records"),
            ("phase_inherited_evidence_drift_rejected_after_consistent_records", "Phase source changed outside identified additions"),
            ("phase_target_basis_drift_rejected_after_consistent_records", "Phase target basis or evidence boundary differs"),
            ("phase_source_access_promotion_rejected_after_consistent_records", "Phase reviewed input identity differs"),
            ("phase_candidate_outcome_promotion_rejected_after_consistent_records", "Phase target basis or evidence boundary differs"),
        ):
            try:
                text = originals[phase_path].decode("utf-8")
                support = json.loads(originals[phase_map_path])
                if case == "phase_source_map_drift_rejected":
                    phase_path.write_bytes(originals[phase_path] + b"\nUnadopted addition.\n")
                else:
                    if "claim_drift" in case:
                        old_claim = support["claims"][0]["text"]
                        new_claim = old_claim.replace("positive normalized fraction", "nonnegative normalized fraction", 1)
                        require(old_claim != new_claim, "Phase claim fixture lost its target")
                        text = text.replace("**Claim 1.** " + old_claim, "**Claim 1.** " + new_claim, 1)
                        support["claims"][0]["text"] = new_claim
                    elif "inherited_evidence" in case:
                        row = "| PEDOT:PSS threshold | 0.443 wt% |"
                        require(text.count(row) == 1, "Phase inherited fixture lost its target")
                        text = text.replace(row, row.replace("0.443", "0.444"), 1)
                    elif "target_basis" in case:
                        target = "on a stipulated occupied-atom basis, not a feed, site or whole-product assay basis"
                        require(text.count(target) == 1, "Phase basis fixture lost its target")
                        text = text.replace(target, "on a stipulated mass-fraction basis", 1)
                    elif "candidate_outcome" in case:
                        target = "actual candidate outcomes UNSUPPORTED"
                        require(text.count(target) == 1, "Phase outcome fixture lost its target")
                        text = text.replace(target, "actual candidate outcomes ESTABLISHED", 1)
                    else:
                        review = json.loads(originals[phase_review_path])
                        review["access"]["original_pdf_sha256"] = "0" * 64
                        phase_review_path.write_bytes((json.dumps(review) + "\n").encode("utf-8"))
                    phase_path.write_bytes(text.encode("utf-8"))
                    support["source_sha256"] = hashlib.sha256(phase_path.read_bytes()).hexdigest()
                    phase_map_path.write_bytes((json.dumps(support) + "\n").encode("utf-8"))
                    # Refresh captured and outer hashes to challenge semantic
                    # preservation rather than merely detecting stale records.
                    edition = json.loads(originals[phase_edition_path])
                    for entry in edition["sources"]:
                        if entry["path"] in {PHASE_SOURCE, PHASE_MAP, PHASE_REVIEW}:
                            entry["sha256"] = hashlib.sha256((fixture / entry["path"]).read_bytes()).hexdigest()
                    phase_edition_path.write_bytes((json.dumps(edition) + "\n").encode("utf-8"))
                    refreshed = json.loads(originals[manifest_path])
                    for entry in refreshed["files"]:
                        if entry["path"] in {PHASE_SOURCE, PHASE_MAP, PHASE_REVIEW, PHASE_EDITION}:
                            changed = (fixture / entry["path"]).read_bytes()
                            entry.update(size_bytes=len(changed), sha256=hashlib.sha256(changed).hexdigest())
                    manifest_path.write_bytes((json.dumps(refreshed) + "\n").encode("utf-8"))
                    check_integrity(fixture)
                try:
                    check_phase_application(fixture)
                except VerificationError as error:
                    require(expected_error in str(error), "Phase mutation failed for another reason: " + str(error))
                    extended.append(case)
                require(case in extended, "Phase mutation was accepted: " + case)
            finally:
                for path, data in originals.items():
                    path.write_bytes(data)

        family_path, family_map_path = fixture / FAMILY_SOURCE, fixture / FAMILY_MAP
        family_review_path, family_edition_path = fixture / FAMILY_REVIEW, fixture / FAMILY_EDITION
        originals = {path: path.read_bytes() for path in
                     (family_path, family_map_path, family_review_path, family_edition_path, manifest_path)}
        check_family_application(fixture)
        for case, expected_error in (
            ("family_source_map_drift_rejected", "Family source/map hash differs"),
            ("family_preface_filing_promotion_rejected_after_consistent_records", "Family reviewed preface qualifications differ"),
            ("family_claim_drift_rejected_after_consistent_records", "Family individual claim records"),
            ("family_inherited_evidence_drift_rejected_after_consistent_records", "Family source changed outside identified additions"),
            ("family_preparation_paragraph_drift_rejected_after_consistent_records", "Family preparation paragraph or pointer differs"),
            ("family_source_access_promotion_rejected_after_consistent_records", "Family reviewed source identities differ"),
            ("family_candidate_outcome_promotion_rejected_after_consistent_records", "Family candidate outcome status differs"),
            ("family_molecular_basis_drift_rejected_after_consistent_records", "Family molecular occurrence basis differs"),
            ("family_polymer_basis_drift_rejected_after_consistent_records", "Family polymer feed basis differs"),
            ("family_composite_basis_drift_rejected_after_consistent_records", "Family composite conditional basis differs"),
        ):
            try:
                text = originals[family_path].decode("utf-8")
                support = json.loads(originals[family_map_path])
                if case == "family_source_map_drift_rejected":
                    family_path.write_bytes(originals[family_path] + b"\nUnadopted addition.\n")
                else:
                    if "claim_drift" in case:
                        old_claim = support["claims"][0]["text"]
                        new_claim = old_claim.replace("positive normalized fraction", "nonnegative normalized fraction", 1)
                        require(old_claim != new_claim, "Family claim fixture lost its target")
                        text = text.replace("**Claim 1.** " + old_claim, "**Claim 1.** " + new_claim, 1)
                        support["claims"][0]["text"] = new_claim
                    elif "inherited_evidence" in case:
                        row = "| PEDOT:PSS threshold | 0.443 wt% |"
                        require(text.count(row) == 1, "Family inherited fixture lost its target")
                        text = text.replace(row, row.replace("0.443", "0.444"), 1)
                    elif "preface_filing" in case:
                        preface, tail = text.split("## 1 Technical field\n", 1)
                        lines = preface.splitlines()
                        indices = [i for i, line in enumerate(lines) if line]
                        require(len(indices) == 4, "Family preface fixture lost its target")
                        lines[indices[2]] += " A completed filing and earlier priority entitlement are asserted."
                        text = "\n".join(lines) + "\n## 1 Technical field\n" + tail
                    elif "source_access" in case:
                        review = json.loads(originals[family_review_path])
                        review["primary_sources"][0].update(original_bytes_acquired=True, original_sha256="0" * 64)
                        family_review_path.write_bytes((json.dumps(review) + "\n").encode("utf-8"))
                    else:
                        targets = {
                            "family_preparation_paragraph_drift_rejected_after_consistent_records":
                                ("The actual precursors, stoichiometry, atmosphere, thermal schedule, isolation and phase-confirmation steps are necessary.",
                                 "The actual precursors, stoichiometry, atmosphere, thermal schedule, isolation and phase-confirmation steps are optional."),
                            "family_candidate_outcome_promotion_rejected_after_consistent_records":
                                ("actual candidate outcomes UNSUPPORTED", "actual candidate outcomes ESTABLISHED"),
                            "family_molecular_basis_drift_rejected_after_consistent_records":
                                ("selected-crystallite count quantities, not bulk mass or volume phase fractions",
                                 "bulk mass phase fractions"),
                            "family_polymer_basis_drift_rejected_after_consistent_records":
                                ("distinct from elemental fractions, repeat populations and final retained composition",
                                 "equivalent to final retained composition"),
                            "family_composite_basis_drift_rejected_after_consistent_records":
                                ("not the source's actual batch masses, a stoichiometric cure prescription or retained cured-product assay",
                                 "the observed actual batch masses and retained cured-product assay"),
                        }
                        target, replacement = targets[case]
                        require(target in text, "Family semantic fixture lost its target")
                        text = text.replace(target, replacement, 1)
                    family_path.write_bytes(text.encode("utf-8"))
                    support["source_sha256"] = hashlib.sha256(family_path.read_bytes()).hexdigest()
                    family_map_path.write_bytes((json.dumps(support) + "\n").encode("utf-8"))
                    # Coherent captured and outer hashes must not promote a
                    # counting model, input balance or unknown outcome to an assay.
                    edition = json.loads(originals[family_edition_path])
                    for entry in edition["sources"]:
                        if entry["path"] in {FAMILY_SOURCE, FAMILY_MAP, FAMILY_REVIEW}:
                            entry["sha256"] = hashlib.sha256((fixture / entry["path"]).read_bytes()).hexdigest()
                    family_edition_path.write_bytes((json.dumps(edition) + "\n").encode("utf-8"))
                    refreshed = json.loads(originals[manifest_path])
                    for entry in refreshed["files"]:
                        if entry["path"] in {FAMILY_SOURCE, FAMILY_MAP, FAMILY_REVIEW, FAMILY_EDITION}:
                            changed = (fixture / entry["path"]).read_bytes()
                            entry.update(size_bytes=len(changed), sha256=hashlib.sha256(changed).hexdigest())
                    manifest_path.write_bytes((json.dumps(refreshed) + "\n").encode("utf-8"))
                    check_integrity(fixture)
                try:
                    check_family_application(fixture)
                except VerificationError as error:
                    require(expected_error in str(error), "Family mutation failed for another reason: " + str(error))
                    extended.append(case)
                require(case in extended, "Family mutation was accepted: " + case)
            finally:
                for path, data in originals.items():
                    path.write_bytes(data)

        metal_path, metal_map_path = fixture / METAL_GLASS_SOURCE, fixture / METAL_GLASS_MAP
        metal_review_path, metal_edition_path = fixture / METAL_GLASS_REVIEW, fixture / METAL_GLASS_EDITION
        originals = {path: path.read_bytes() for path in
                     (metal_path, metal_map_path, metal_review_path, metal_edition_path, manifest_path)}
        check_metal_glass_application(fixture)
        for case, expected_error in (
            ("metal_glass_source_map_drift_rejected", "Metal/glass source/map hash differs"),
            ("metal_glass_claim_drift_rejected_after_consistent_records", "Metal/glass individual claim records"),
            ("metal_glass_inherited_evidence_drift_rejected_after_consistent_records", "Metal/glass source changed outside identified additions"),
            ("metal_glass_alloy_prefix_drift_rejected_after_consistent_records", "Metal/glass alloy preparation paragraph or pointer differs"),
            ("metal_glass_glass_prefix_drift_rejected_after_consistent_records", "Metal/glass glass preparation paragraph or pointer differs"),
            ("metal_glass_preface_filing_promotion_rejected_after_consistent_records", "Metal/glass reviewed preface qualifications differ"),
            ("metal_glass_source_acquisition_promotion_rejected_after_consistent_records", "Metal/glass reviewed source identities differ"),
            ("metal_glass_candidate_outcome_promotion_rejected_after_consistent_records", "Metal/glass candidate outcome status differs"),
            ("metal_glass_principal_whole_conflation_rejected_after_consistent_records", "Metal/glass principal/whole inventory basis differs"),
            ("metal_glass_nominal_count_drift_rejected_after_consistent_records", "Metal/glass nominal principal accounting differs"),
            ("metal_glass_below_grid_count_drift_rejected_after_consistent_records", "Metal/glass below-grid count accounting differs"),
        ):
            try:
                text = originals[metal_path].decode("utf-8")
                support = json.loads(originals[metal_map_path])
                review = json.loads(originals[metal_review_path])
                if case == "metal_glass_source_map_drift_rejected":
                    metal_path.write_bytes(originals[metal_path] + b"\nUnadopted addition.\n")
                else:
                    if "claim_drift" in case:
                        old_claim = support["claims"][0]["text"]
                        new_claim = old_claim.replace("positive normalized fraction", "nonnegative normalized fraction", 1)
                        require(old_claim != new_claim, "Metal/glass claim fixture lost its target")
                        text = text.replace("**Claim 1.** " + old_claim, "**Claim 1.** " + new_claim, 1)
                        support["claims"][0]["text"] = new_claim
                    elif "inherited_evidence" in case:
                        target = "selected-crystallite count quantities, not bulk mass or volume phase fractions"
                        require(text.count(target) == 1, "Metal/glass inherited fixture lost its target")
                        text = text.replace(target, "bulk specimen mass fractions", 1)
                    elif "prefix_drift" in case:
                        target, replacement = (
                            ("The selected route must address", "The selected route need not address")
                            if "alloy_prefix" in case else
                            ("A candidate record specifies the melt", "A candidate record need not specify the melt")
                        )
                        require(text.count(target) == 1, "Metal/glass prefix fixture lost its target")
                        text = text.replace(target, replacement, 1)
                    elif "preface_filing" in case:
                        preface, tail = text.split("## 1 Technical field\n", 1)
                        lines = preface.splitlines()
                        indices = [i for i, line in enumerate(lines) if line]
                        require(len(indices) == 4, "Metal/glass preface fixture lost its target")
                        lines[indices[2]] += " A completed filing and earlier priority entitlement are asserted."
                        text = "\n".join(lines) + "\n## 1 Technical field\n" + tail
                    elif "source_acquisition" in case:
                        source = review["primary_sources"][0]
                        require(source["supplement_inspected"] is False,
                                "Metal/glass acquisition fixture lost its target")
                        source.update(supplement_inspected=True, supplement_original_bytes_acquired=True,
                                      supplement_original_sha256="0" * 64)
                    elif "candidate_outcome" in case or "principal_whole" in case:
                        heading = METAL_GLASS_HEADINGS["alloy"]
                        block = evidence_block(text, heading, "0040")
                        if "candidate_outcome" in case:
                            target, replacement = "actual candidate outcomes UNSUPPORTED", "actual candidate outcomes ESTABLISHED"
                            review["present_record_status"].update(candidate_preparation_performed=True,
                                                                    candidate_outcomes="ESTABLISHED")
                        else:
                            target, replacement = "and f is not assumed one", "and f is assumed one"
                            review["present_accounting"]["whole_transfer"]["f_assumed_one"] = True
                        require(block.count(target) == 1, "Metal/glass evidence fixture lost its target")
                        text = text.replace(heading + block, heading + block.replace(target, replacement, 1), 1)
                    elif "nominal_count" in case:
                        glass = review["present_accounting"]["glass"]
                        glass["principal_counts"][0] += 1
                        glass["principal_total"] = sum(glass["principal_counts"])
                        glass["principal_target"] = [str(Fraction(n, glass["principal_total"]))
                                                     for n in glass["principal_counts"]]
                    else:
                        require("below_grid_count" in case, "Unknown metal/glass fixture")
                        witness = review["present_accounting"]["alloy"]["below_grid"]
                        witness["primitive_denominator"] = witness["L"]
                    metal_path.write_bytes(text.encode("utf-8"))
                    support["source_sha256"] = hashlib.sha256(metal_path.read_bytes()).hexdigest()
                    metal_map_path.write_bytes((json.dumps(support) + "\n").encode("utf-8"))
                    metal_review_path.write_bytes((json.dumps(review) + "\n").encode("utf-8"))
                    # Consistent provenance layers do not turn subinventory
                    # targets into assays or missing evidence into outcomes.
                    edition = json.loads(originals[metal_edition_path])
                    for entry in edition["sources"]:
                        if entry["path"] in {METAL_GLASS_SOURCE, METAL_GLASS_MAP, METAL_GLASS_REVIEW}:
                            entry["sha256"] = hashlib.sha256((fixture / entry["path"]).read_bytes()).hexdigest()
                    metal_edition_path.write_bytes((json.dumps(edition) + "\n").encode("utf-8"))
                    refreshed = json.loads(originals[manifest_path])
                    for entry in refreshed["files"]:
                        if entry["path"] in {METAL_GLASS_SOURCE, METAL_GLASS_MAP, METAL_GLASS_REVIEW, METAL_GLASS_EDITION}:
                            changed = (fixture / entry["path"]).read_bytes()
                            entry.update(size_bytes=len(changed), sha256=hashlib.sha256(changed).hexdigest())
                    manifest_path.write_bytes((json.dumps(refreshed) + "\n").encode("utf-8"))
                    check_integrity(fixture)
                try:
                    check_metal_glass_application(fixture)
                except VerificationError as error:
                    require(expected_error in str(error), "Metal/glass mutation failed for another reason: " + str(error))
                    extended.append(case)
                require(case in extended, "Metal/glass mutation was accepted: " + case)
            finally:
                for path, data in originals.items():
                    path.write_bytes(data)

        theoretical_path, theoretical_map_path = fixture / THEORETICAL_SOURCE, fixture / THEORETICAL_MAP
        theoretical_edition_path = fixture / THEORETICAL_EDITION
        theoretical_snapshot_path = fixture / THEORETICAL_AUTHORING["tools/pdf/build_working_application.py"]
        originals = {path: path.read_bytes() for path in
                     (theoretical_path, theoretical_map_path, theoretical_edition_path,
                      theoretical_snapshot_path, manifest_path)}
        check_theoretical_application(fixture)
        for case, expected_error in (
            ("theoretical_stale_source_map_rejected", "Theoretical source/map hash differs"),
            ("theoretical_consistent_claim_change_rejected", "Theoretical individual claim records differ"),
            ("theoretical_inherited_paragraph_drift_rejected", "Theoretical inherited numbered paragraphs differ"),
            ("theoretical_new_paragraph_gap_rejected", "Theoretical paragraph IDs must be contiguous and ordered"),
            ("theoretical_preface_filing_promotion_rejected", "Theoretical reviewed preface qualifications differ"),
            ("theoretical_physical_outcome_promotion_rejected", "Theoretical reviewed hypothetical qualifications differ"),
            ("theoretical_administrative_row_omission_rejected", "Theoretical reviewed preface qualifications differ"),
            ("theoretical_legal_inventorship_promotion_rejected", "Theoretical review designation or evidence status differs"),
            ("theoretical_snapshot_identity_drift_rejected", "Theoretical PDF captured-source identity differs"),
            ("theoretical_fixed_old_pdf_coverage_rejected", "Theoretical recorded new text coverage differs"),
        ):
            try:
                text = originals[theoretical_path].decode("utf-8")
                support = json.loads(originals[theoretical_map_path])
                edition = json.loads(originals[theoretical_edition_path])
                if case == "theoretical_stale_source_map_rejected":
                    theoretical_path.write_bytes(originals[theoretical_path] + b"\nUnadopted addition.\n")
                else:
                    if "claim_change" in case:
                        old_claim = support["claims"][0]["text"]
                        new_claim = old_claim.replace("positive normalized fraction", "nonnegative normalized fraction", 1)
                        require(old_claim != new_claim, "Theoretical claim fixture lost its target")
                        text = text.replace("**Claim 1.** " + old_claim, "**Claim 1.** " + new_claim, 1)
                        support["claims"][0]["text"] = new_claim
                    elif "inherited_paragraph" in case:
                        old = re.findall(r"^\[0005\] .+$", text, re.M)
                        require(len(old) == 1, "Theoretical inheritance fixture lost its target")
                        text = text.replace(old[0], old[0] + " All candidate materials are physically enabled.", 1)
                    elif "paragraph_gap" in case:
                        last = support["added_paragraphs"][-1]
                        require(text.count("[" + last + "] ") == 1, "Theoretical numbering fixture lost its target")
                        text = text.replace("[" + last + "] ", f"[{int(last) + 1:04d}] ", 1)
                        support["added_paragraphs"][-1] = f"{int(last) + 1:04d}"
                    elif "preface_filing" in case:
                        preface, tail = text.split("## 1 Technical field\n", 1)
                        text = preface + "A completed patent filing and earlier priority entitlement are asserted.\n\n" + "## 1 Technical field\n" + tail
                    elif "administrative_row_omission" in case:
                        preface, tail = text.split("## 1 Technical field\n", 1)
                        rows = re.findall(r"^\| Inventor residence \|.+$", preface, re.M)
                        require(len(rows) == 1, "Theoretical administrative fixture lost its target")
                        replacement = preface.replace(rows[0] + "\n", "", 1)
                        require(replacement != preface, "Theoretical administrative row was not removed")
                        text = replacement + "## 1 Technical field\n" + tail
                    elif "physical_outcome" in case:
                        start, end = text.index(THEORETICAL_HEADING), text.index("## 16 Draft abstract")
                        block = text[start:end]
                        paragraphs = re.findall(r"^\[\d{4}\] .+$", block, re.M)
                        require(bool(paragraphs), "Theoretical outcome fixture lost its target")
                        replacement = block.replace(paragraphs[0], paragraphs[0]
                                                    + " The proposed physical product has been synthesized and characterized.", 1)
                        text = text[:start] + replacement + text[end:]
                    elif "legal_inventorship" in case:
                        support["proposed_inventor"]["legal_inventorship_certified"] = True
                        edition["proposed_inventor"]["legal_inventorship_certified"] = True
                    elif "snapshot_identity" in case:
                        theoretical_snapshot_path.write_bytes(originals[theoretical_snapshot_path] + b"\n# Uncaptured change.\n")
                    else:
                        require("fixed_old_pdf_coverage" in case, "Unknown theoretical fixture")
                        edition["complete_numbered_text_checked"]["paragraphs"] = 80
                    theoretical_path.write_bytes(text.encode("utf-8"))
                    support["source_sha256"] = hashlib.sha256(theoretical_path.read_bytes()).hexdigest()
                    theoretical_map_path.write_bytes((json.dumps(support) + "\n").encode("utf-8"))
                    preface = text.split("## 1 Technical field\n", 1)[0]
                    start = text.index(THEORETICAL_HEADING) + len(THEORETICAL_HEADING)
                    end = text.index("## 16 Draft abstract")
                    edition["complete_theoretical_preface_checked"] = evidence_block_counts(preface)
                    edition["complete_theoretical_review_text_checked"] = evidence_block_counts(text[start:end])
                    for entry in edition["sources"]:
                        if entry["path"] in {THEORETICAL_SOURCE, THEORETICAL_MAP}:
                            entry["sha256"] = hashlib.sha256((fixture / entry["path"]).read_bytes()).hexdigest()
                    theoretical_edition_path.write_bytes((json.dumps(edition) + "\n").encode("utf-8"))
                    # Updated outer and capture hashes cannot approve a changed
                    # historical teaching or certify an unperformed outcome.
                    refreshed = json.loads(originals[manifest_path])
                    changed_paths = {THEORETICAL_SOURCE, THEORETICAL_MAP, THEORETICAL_EDITION,
                                     THEORETICAL_AUTHORING["tools/pdf/build_working_application.py"]}
                    for entry in refreshed["files"]:
                        if entry["path"] in changed_paths:
                            changed = (fixture / entry["path"]).read_bytes()
                            entry.update(size_bytes=len(changed), sha256=hashlib.sha256(changed).hexdigest())
                    manifest_path.write_bytes((json.dumps(refreshed) + "\n").encode("utf-8"))
                    check_integrity(fixture)
                try:
                    check_theoretical_application(fixture)
                except VerificationError as error:
                    require(expected_error in str(error), "Theoretical mutation failed for another reason: " + str(error))
                    extended.append(case)
                require(case in extended, "Theoretical mutation was accepted: " + case)
            finally:
                for path, data in originals.items():
                    path.write_bytes(data)

        with module_environment(fixture / "tools"):
            substantive_module = import_local("substantive_review_checks", fixture / SUBSTANTIVE_CHECKER)
            extended.extend(substantive_module.negative_tests(
                fixture, check_substantive_application, require, VerificationError))

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
            payload["states"][0]["observation_status"] = "not inferred from property markers; requires source review"
            numeric = payload["states"][0]["mass_excess"]["value"]
            original_numeric = numeric.copy()
            require(numeric["kind"] == "numeric", "Numeric mutation fixture is not numeric")
            for kind in ("missing", "unparsed_text", "source_category"):
                numeric.update(kind=kind, operator=None, value_decimal=None)
                try:
                    nuclear_verifier.verify_payload(payload, schema, nuclear_parser.SOURCE.read_bytes())
                except ValueError as error:
                    require("Numeric source mislabeled" in str(error), "Numeric mutation failed for another reason")
                    extended.append("nuclear_numeric_mislabeled_as_" + kind + "_rejected")
                else:
                    raise VerificationError("Numeric source was accepted as " + kind)
                finally:
                    numeric.clear()
                    numeric.update(original_numeric)

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

                destination = download_root / "separate-database" / "source.bin"
                observation = download_root / "separate-observation" / "metadata" / "source.json"
                require(not observation.parent.exists(), "Separate observation parent fixture already exists")
                with patch.object(downloader.urllib.request, "urlopen", return_value=OfflineResponse(download_bytes)) as response, \
                        redirect_stdout(io.StringIO()):
                    downloader.download(argparse.Namespace(destination=destination, observation=observation))
                require(response.call_count == 1 and destination.read_bytes() == download_bytes,
                        "Separate-parent transfer did not preserve pinned bytes")
                require(load_json(observation)["sha256"] == download_sha and not destination.with_suffix(".bin.part").exists(),
                        "Separate-parent transfer failed to publish provenance or remove the partial")
                downloader_cases.append("separate_observation_parent_created_and_pinned_transfer_published")

                destination = download_root / "preexisting-observation-database" / "source.bin"
                observation = download_root / "preexisting-observation.json"
                preserved_observation = b"Preserve this existing observation.\n"
                observation.write_bytes(preserved_observation)
                with patch.object(downloader.urllib.request, "urlopen") as response:
                    try:
                        downloader.download(argparse.Namespace(destination=destination, observation=observation))
                    except ValueError as error:
                        require("Observation already exists" in str(error), "Observation preflight failed for another reason")
                    else:
                        raise VerificationError("Preexisting observation was accepted")
                require(response.call_count == 0 and observation.read_bytes() == preserved_observation,
                        "Observation preflight fetched bytes or altered existing provenance")
                require(not destination.parent.exists(), "Observation preflight created destination directories")
                downloader_cases.append("preexisting_observation_preserved_before_directory_creation_or_fetch")

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
    # Preserve all ten theoretical-edition cases and the three archive repairs.
    require(len(extended) == 96, f"Expected 96 extension failure checks, got {len(extended)}")
    require(len(downloader_cases) == 4, "Expected the four durable downloader publication regressions")
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
