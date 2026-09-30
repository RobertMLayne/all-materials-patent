"""Standard-library regressions for output safeguards, using synthetic bytes only.

Run from the package root: python -B tools/pdf/test_pdf_outputs.py
No PDFs are authored, optional PDF libraries are unnecessary, and fixtures stay
inside the ignored generated_reports/ directory with checked cleanup boundaries.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import build_identity_review_annex as outputs


PACKAGE_ROOT = Path(__file__).resolve().parents[2]


class OutputSafeguardsTests(unittest.TestCase):
    def setUp(self) -> None:
        # Reject a redirected scratch parent before creating or deleting files.
        self.scratch_parent = PACKAGE_ROOT / "generated_reports"
        if self.scratch_parent.resolve() != self.scratch_parent:
            raise RuntimeError("generated_reports is redirected; refuse fixture writes")
        self.scratch_parent.mkdir(exist_ok=True)
        self.scratch = Path(tempfile.mkdtemp(prefix="pdf-output-tests-", dir=self.scratch_parent))
        self.addCleanup(self.clean_scratch)
        self.assertEqual(self.scratch.resolve().parent, self.scratch_parent)
        self.pdf_source = self.scratch / "source.pdf"
        self.report_source = self.scratch / "source.json"
        self.pdf_source.write_bytes(b"SYNTHETIC PDF PAYLOAD; not a PDF document")
        self.report_source.write_bytes(b"SYNTHETIC REPORT PAYLOAD")
        self.pdf = self.scratch / "review.pdf"
        self.report = self.scratch / "review.json"
        self.pairs = [(self.pdf_source, self.pdf), (self.report_source, self.report)]

    def clean_scratch(self) -> None:
        resolved = self.scratch.resolve()
        if (self.scratch_parent.resolve() != self.scratch_parent
                or resolved != self.scratch or resolved.parent != self.scratch_parent
                or not resolved.name.startswith("pdf-output-tests-")):
            raise RuntimeError("Fixture cleanup escaped its checked absolute scratch boundary")
        if resolved.exists():
            shutil.rmtree(resolved)

    @staticmethod
    def identity(path: Path) -> tuple[int, int]:
        info = path.stat()
        return info.st_dev, info.st_ino

    def test_existing_destination_is_preserved(self) -> None:
        original = b"Previous edition remains intact"
        self.pdf.write_bytes(original)
        original_identity = self.identity(self.pdf)
        with self.assertRaises(FileExistsError):
            outputs.publish_exclusive(self.pdf_source, self.pdf)
        self.assertEqual(self.pdf.read_bytes(), original)
        self.assertEqual(self.identity(self.pdf), original_identity)
        self.assertEqual(self.pdf_source.read_bytes(), b"SYNTHETIC PDF PAYLOAD; not a PDF document")

    def test_partial_copy_is_removed_and_original_exception_survives(self) -> None:
        failure = OSError("Injected interruption after a partial write")

        def interrupted_copy(stream, target) -> None:
            target.write(stream.read(7))
            raise failure

        with patch.object(outputs.shutil, "copyfileobj", side_effect=interrupted_copy):
            with self.assertRaises(OSError) as caught:
                outputs.publish_exclusive(self.pdf_source, self.pdf)
        self.assertIs(caught.exception, failure)
        self.assertFalse(self.pdf.exists())
        self.assertEqual(self.pdf_source.read_bytes(), b"SYNTHETIC PDF PAYLOAD; not a PDF document")

    def test_returned_identity_is_from_exclusive_open(self) -> None:
        opened_identities = []
        real_fstat = os.fstat

        def capture_fstat(descriptor):
            info = real_fstat(descriptor)
            opened_identities.append((info.st_dev, info.st_ino))
            return info

        with patch.object(outputs.os, "fstat", side_effect=capture_fstat):
            result = outputs.publish_exclusive(self.pdf_source, self.pdf)
        self.assertEqual(opened_identities, [result])
        self.assertEqual(result, self.identity(self.pdf))
        self.assertEqual(self.pdf.read_bytes(), self.pdf_source.read_bytes())

    def test_matching_ownership_removes_published_file(self) -> None:
        owned = outputs.publish_exclusive(self.pdf_source, self.pdf)
        outputs.remove_owned_output(self.pdf, owned)
        self.assertFalse(self.pdf.exists())
        self.assertTrue(self.pdf_source.exists())

    def test_substituted_ownership_preserves_replacement(self) -> None:
        owned = outputs.publish_exclusive(self.pdf_source, self.pdf)
        replacement = self.scratch / "replacement.pdf"
        replacement.write_bytes(b"Replacement from a different owner")
        self.assertNotEqual(self.identity(replacement), owned)
        os.replace(replacement, self.pdf)
        outputs.remove_owned_output(self.pdf, owned)
        self.assertEqual(self.pdf.read_bytes(), b"Replacement from a different owner")

    def test_missing_owned_output_is_tolerated(self) -> None:
        owned = outputs.publish_exclusive(self.pdf_source, self.pdf)
        self.pdf.unlink()
        outputs.remove_owned_output(self.pdf, owned)
        self.assertFalse(self.pdf.exists())
        self.assertTrue(self.pdf_source.exists())

    def test_successful_pair_preserves_both_sources_and_outputs(self) -> None:
        source_bytes = [source.read_bytes() for source, _ in self.pairs]
        outputs.publish_outputs_exclusive(self.pairs)
        self.assertEqual([destination.read_bytes() for _, destination in self.pairs], source_bytes)
        self.assertEqual([source.read_bytes() for source, _ in self.pairs], source_bytes)

    def test_report_collision_removes_only_still_owned_pdf(self) -> None:
        self.report.write_bytes(b"Existing report must survive")
        report_identity = self.identity(self.report)
        with self.assertRaises(FileExistsError):
            outputs.publish_outputs_exclusive(self.pairs)
        self.assertFalse(self.pdf.exists())
        self.assertEqual(self.report.read_bytes(), b"Existing report must survive")
        self.assertEqual(self.identity(self.report), report_identity)
        self.assertTrue(self.pdf_source.exists())

    def test_other_process_replacement_survives_second_publication_failure(self) -> None:
        self.report.write_bytes(b"Existing report must survive")
        real_publish = outputs.publish_exclusive
        report_failures = []
        opened_pdf_identities = []
        replacement = self.scratch / "process-replacement.pdf"
        worker = (
            "import os,pathlib,sys; "
            "replacement=pathlib.Path(sys.argv[2]); "
            "replacement.write_bytes(b'Replacement from a separate process'); "
            "os.replace(replacement, pathlib.Path(sys.argv[1]))"
        )

        def replace_then_publish(source, destination):
            if destination == self.report:
                # The second publication really fails at exclusive open; only
                # the schedule between publications is controlled by the test.
                subprocess.run(
                    [sys.executable, "-I", "-B", "-c", worker, str(self.pdf), str(replacement)],
                    check=True, capture_output=True, timeout=15,
                )
                self.assertNotEqual(self.identity(self.pdf), opened_pdf_identities[0])
            try:
                result = real_publish(source, destination)
            except FileExistsError as failure:
                report_failures.append(failure)
                raise
            if destination == self.pdf:
                opened_pdf_identities.append(result)
            return result

        with patch.object(outputs, "publish_exclusive", side_effect=replace_then_publish):
            with self.assertRaises(FileExistsError) as caught:
                outputs.publish_outputs_exclusive(self.pairs)
        self.assertEqual(len(report_failures), 1)
        self.assertIs(caught.exception, report_failures[0])
        self.assertEqual(self.pdf.read_bytes(), b"Replacement from a separate process")
        self.assertEqual(self.report.read_bytes(), b"Existing report must survive")

    def test_pair_rollback_tolerates_pdf_already_removed(self) -> None:
        self.report.write_bytes(b"Existing report must survive")
        real_publish = outputs.publish_exclusive

        def remove_then_publish(source, destination):
            if destination == self.report:
                self.pdf.unlink()
            return real_publish(source, destination)

        with patch.object(outputs, "publish_exclusive", side_effect=remove_then_publish):
            with self.assertRaises(FileExistsError):
                outputs.publish_outputs_exclusive(self.pairs)
        self.assertFalse(self.pdf.exists())
        self.assertEqual(self.report.read_bytes(), b"Existing report must survive")

    def test_valid_output_paths_are_resolved_without_writes(self) -> None:
        package = self.scratch / "fixture-package"
        package.mkdir()
        pdf = package / "generated_reports" / "future.pdf"
        report = package / "generated_reports" / "future.json"
        self.assertEqual(outputs.validate_outputs(package, pdf, report, [self.pdf_source]),
                         (pdf.resolve(), report.resolve()))
        self.assertEqual(outputs.validate_outputs(package, self.pdf, self.report, [self.pdf_source]),
                         (self.pdf.resolve(), self.report.resolve()))
        self.assertFalse((package / "generated_reports").exists())
        self.assertFalse(self.pdf.exists())
        self.assertFalse(self.report.exists())

    def test_invalid_output_paths_are_refused_without_mutation(self) -> None:
        package = self.scratch / "fixture-package"
        package.mkdir()
        pdf = package / "generated_reports" / "future.pdf"
        report = package / "generated_reports" / "future.json"
        self.pdf.write_bytes(b"Existing PDF must survive")
        self.report.write_bytes(b"Existing report must survive")
        cases = [
            ("identical destinations", pdf, pdf, "must be distinct"),
            ("PDF input alias", self.pdf_source, report, "aliases a read-only input"),
            ("report input alias", pdf, self.report_source, "aliases a read-only input"),
            ("normalized alias", self.scratch / "unused" / ".." / "source.pdf", report,
             "aliases a read-only input"),
            ("protected PDF", package / "documents" / "future.pdf", report,
             "below ignored generated_reports"),
            ("protected report", pdf, package / "data" / "future.json",
             "below ignored generated_reports"),
            ("existing PDF", self.pdf, report, "already exists"),
            ("existing report", pdf, self.report, "already exists"),
            ("wrong PDF suffix", self.scratch / "future.txt", report, ".pdf output"),
            ("wrong report suffix", pdf, self.scratch / "future.txt", ".json validation report"),
        ]
        before = {path.relative_to(self.scratch): path.read_bytes()
                  for path in self.scratch.rglob("*") if path.is_file()}
        for label, out, validation, message in cases:
            with self.subTest(label=label):
                with self.assertRaisesRegex(ValueError, message):
                    outputs.validate_outputs(package, out, validation,
                                             [self.pdf_source, self.report_source])
        after = {path.relative_to(self.scratch): path.read_bytes()
                 for path in self.scratch.rglob("*") if path.is_file()}
        self.assertEqual(after, before)
        self.assertFalse((package / "generated_reports").exists())

    def test_helper_import_does_not_require_pdf_libraries_or_network(self) -> None:
        # An isolated process blocks optional libraries even if installed on
        # this machine, proving these regressions need only the standard library.
        worker = """
import builtins, pathlib, socket, sys
original_import = builtins.__import__
def guarded_import(name, *args, **kwargs):
    if name.split('.')[0] in {'reportlab', 'pypdf'}:
        raise AssertionError('Optional PDF dependency was imported')
    return original_import(name, *args, **kwargs)
def forbidden_network(*args, **kwargs):
    raise AssertionError('Network attempted')
builtins.__import__ = guarded_import
socket.socket = forbidden_network
socket.create_connection = forbidden_network
sys.path.insert(0, sys.argv[1])
import build_identity_review_annex as helper
base = pathlib.Path(sys.argv[2])
assert helper.validate_outputs(base, base/'generated_reports/a.pdf',
                               base/'generated_reports/a.json', [])
"""
        subprocess.run(
            [sys.executable, "-I", "-B", "-c", worker, str(Path(__file__).resolve().parent),
             str(self.scratch)], check=True, capture_output=True, timeout=15,
        )
        self.assertFalse((self.scratch / "generated_reports").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
