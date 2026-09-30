#!/usr/bin/env python3
"""Verify this research package without dependencies or repository writes.

The manifest checks consistency, not authenticity or public-availability time.
The exact model tests concern mathematics, not physical material enablement.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True

MANIFEST = "integrity_manifest.json"
RANGE_REPORT = "range_model/verification_report.json"
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
})
EXPECTED_FILES = EXPECTED_HASHED | {MANIFEST, RANGE_REPORT}


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
            parts[0] == "generated_reports" or
            relative == "package_verification_report.json" or
            relative.endswith((".pyc", ".pyo")))


def check_inventory(root: Path) -> int:
    actual = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if ignored(relative):
            continue
        require(not path.is_symlink(), f"Package contains a symbolic link: {relative}")
        if path.is_file():
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


def check_math(root: Path) -> dict:
    spec = importlib.util.spec_from_file_location("package_composition_ranges", root / "range_model/composition_ranges.py")
    require(spec is not None and spec.loader is not None, "Could not load range verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for filename, generated in (("composition_range_model.json", module.build_model()),
                                ("numeric_examples.json", module.build_examples())):
        saved = load_json(root / "range_model" / filename)
        require(no_floats(saved) and no_floats(generated), f"Inexact binary float in {filename}")
        require(saved == generated, f"Mathematical JSON does not reproduce: {filename}")
    report = module.verify()
    require(report.get("status") == "passed" and report.get("test_group_count") == 27,
            "Exact range verifier did not pass all 27 finite groups")
    require(report == load_json(root / RANGE_REPORT), "Recorded range verification report differs from fresh result")
    return {"mathematical_json_artifacts_reproduced": 2, "range_test_groups_passed": 27,
            "recorded_range_report_reproduced": True,
            "scope": "Executable positive floor 10^-19; not exhaustive physical or broader symbolic-domain validation."}


def check_workflow(root: Path) -> None:
    content = (root / ".github/workflows/verify.yml").read_text(encoding="utf-8")
    for fragment in ("permissions:\n  contents: read", "timeout-minutes: 10",
                     "cancel-in-progress: true", "python-version: '3.12'",
                     "persist-credentials: false", "run: python verify_package.py",
                     "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683",
                     "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065"):
        require(fragment in content, f"Reviewed workflow control missing: {fragment}")


def run(root: Path) -> dict:
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
    check_workflow(root)
    return {"status": "passed", "package_files": file_count, "sha256_records_checked": hashed,
            **claim_result, **registry_result, "local_markdown_links_checked": links, **math_result,
            "pdf_binary_integrity_checked": 3, "pdf_layout_rechecked_by_this_script": False,
            "workflow_controls_checked": True, "github_actions_run_observed": False,
            "supplied_artifacts_modified": 0,
            "limitations": ["Checksums are not authentication or a trusted publication timestamp.",
                            "No patent filing, universal prior-art effect, novelty or physical enablement is certified."]}


def self_test(root: Path) -> dict:
    """Exercise failure paths using temporary copies; preserve the package."""
    from contextlib import contextmanager
    import shutil
    import uuid

    caught = []
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
        shutil.copytree(root, fixture, ignore=shutil.ignore_patterns(".git", "__pycache__", "generated_reports"))
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
        report = load_json(report_path)
        report["test_group_count"] = 26
        report_path.write_text(json.dumps(report), encoding="utf-8")
        try:
            check_math(fixture)
        except VerificationError:
            caught.append("unhashed_report_drift_rejected")
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
    require(len(caught) == 10, f"Expected 10 deliberate failure checks, got {len(caught)}")
    return {"status": "passed", "deliberate_failure_cases_rejected": len(caught), "cases": caught}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Also exercise 10 failure cases in temporary copies")
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
