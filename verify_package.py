#!/usr/bin/env python3
"""Verify this research package without dependencies or repository writes.

The manifest checks consistency, not authenticity or public-availability time.
The exact model tests concern mathematics, not physical material enablement.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager, redirect_stdout
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
    "documents/full_scope_completion_audit.md",
    "range_model/unrestricted_compositions.py",
    "range_model/unrestricted_composition_model.json",
    "range_model/unrestricted_numeric_examples.json",
    "range_model/unrestricted_verification_report.json",
    "range_model/independent_unrestricted_checks.py",
    "range_model/independent_unrestricted_report.json",
    "range_model/trace_sampling_calculations.py", "range_model/trace_sampling_report.json",
}) | {f"{NUCLEAR_DIRECTORY}/{name}" for name in NUCLEAR_FILES} | {
    f"{PARTICLE_DIRECTORY}/{name}" for name in PARTICLE_FILES
}
EXPECTED_HASHED = EXPECTED_HASHED | {
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
}
EXPECTED_FILES = EXPECTED_HASHED | {MANIFEST, RANGE_REPORT}
MODULE_NAMES = frozenset({
    "composition_ranges", "unrestricted_compositions", "independent_unrestricted_checks",
    "trace_sampling_calculations", "parse_nubase", "verify_nuclear_archive",
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
                require(not path.is_symlink(), f"Package contains a symbolic link: {relative}")
        for name in filenames:
            path = parent / name
            relative = path.relative_to(root).as_posix()
            if not ignored(relative):
                require(not path.is_symlink(), f"Package contains a symbolic link: {relative}")
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
                     "run: python -m ruff check --no-cache ."):
        require(fragment in content, f"Reviewed workflow control missing: {fragment}")
    # SHA syntax is checked here; release identities are reviewed before a
    # manifest update. This permits reviewed Dependabot pin updates.
    for relative in (".github/workflows/verify.yml", ".github/workflows/codeql.yml", ".github/workflows/copilot-setup-steps.yml"):
        workflow = (root / relative).read_text(encoding="utf-8")
        require("pull_request_target" not in workflow, f"Privileged PR trigger in {relative}")
        references = re.findall(r"uses:\s*(\S+)", workflow)
        require(bool(references) and all(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+@[0-9a-f]{40}", ref)
                                         for ref in references), f"Unpinned action in {relative}")


def run(root: Path) -> dict:
    require(__debug__, "Verification requires enabled assertions; run Python without -O, -OO or PYTHONOPTIMIZE.")
    file_count = check_inventory(root)
    hashed = check_integrity(root)
    application = (root / "documents/provisional_application_draft.md").read_text(encoding="utf-8")
    claim_result = check_claims(application, load_json(root / "data/claim_support_map.json"))
    registry_result = check_registry(load_json(root / "data/entity_register.json"), application)
    links = check_local_links(root)
    for relative in EXPECTED_HASHED:
        if relative.endswith(".pdf"):
            data = (root / relative).read_bytes()
            require(data.startswith(b"%PDF-") and b"%%EOF" in data[-1024:], f"Invalid PDF envelope: {relative}")
    math_result = check_math(root)
    unrestricted_result = check_unrestricted_math(root)
    nuclear_result = check_nuclear_archive(root)
    particle_result = check_particle_archive(root)
    publication_result = check_publication_record(root)
    check_workflow(root)
    return {"status": "passed", "package_files": file_count, "sha256_records_checked": hashed,
            **claim_result, **registry_result, "local_markdown_links_checked": links, **math_result,
            "unrestricted_domain_verification": unrestricted_result,
            "dated_nuclear_archive_verification": nuclear_result,
            "dated_particle_archive_verification": particle_result,
            "publication_observation_verification": publication_result,
            "pdf_binary_integrity_checked": 3, "pdf_layout_rechecked_by_this_script": False,
            "workflow_controls_checked": True, "github_actions_run_observed": False,
            "supplied_artifacts_modified_by_verifier": 0,
            "limitations": ["Checksums are not authentication or a trusted publication timestamp.",
                            "No patent filing, universal prior-art effect, novelty or physical enablement is certified."]}


def self_test(root: Path) -> dict:
    """Exercise failure paths using temporary copies; preserve the package."""
    require(__debug__, "Verification requires enabled assertions; run Python without -O, -OO or PYTHONOPTIMIZE.")
    import shutil
    import subprocess
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
    require(len(extended) == 4, f"Expected 4 extension failure checks, got {len(extended)}")
    return {"status": "passed", "deliberate_failure_cases_rejected": len(caught), "cases": caught,
            "extension_failure_cases_rejected": len(extended), "extension_cases": extended,
            "fixture_import_isolation_checked": True,
            "optimized_interpreter_rejection_checked": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Also exercise 10 baseline and 4 extension failure cases in temporary copies")
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
