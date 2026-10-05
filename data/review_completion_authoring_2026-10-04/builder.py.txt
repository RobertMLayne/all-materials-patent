"""Author a separate local review packet and append the preserved application.

Uses the existing layout/output helpers. Outputs are exclusively created; on a
publication failure retained files need inspection, not automatic deletion.
This optional authoring tool is outside offline standard-library verification.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
from io import BytesIO
import json
from pathlib import Path
import re
import sys
import tempfile

sys.dont_write_bytecode = True
from build_consolidated_review import configure_fonts, inline, render  # noqa: E402
from build_identity_review_annex import (  # noqa: E402
    publish_outputs_exclusive, report_path_label, require, validate_outputs,
)
from pypdf import PdfReader, PdfWriter  # noqa: E402
import pypdf  # noqa: E402
import reportlab  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
TASK = "2026-10-04"
PDF = f"documents/pdf/materials_review_completion_{TASK}.pdf"
RECORD = f"data/review_completion_authoring_{TASK}.json"
DOCUMENTS = [f"documents/review_readiness_{TASK}.md", f"documents/evidence_edition_index_{TASK}.md",
             f"documents/material_state_process_coverage_{TASK}.md"]
APPLICATION = "documents/provisional_application_substantive_review_2026-10-03.md"
APPLICATION_PDF = "documents/pdf/provisional_application_substantive_review_2026-10-03.pdf"
INPUTS = DOCUMENTS + [APPLICATION, APPLICATION_PDF, f"data/claim_scenarios_{TASK}.json",
                     f"data/evidence_edition_index_{TASK}.json", f"data/material_state_process_coverage_{TASK}.json",
                     "data/claim_review_2026-10-03.json", "data/claim_support_map_substantive_review_2026-10-03.json",
                     "tools/pdf/requirements-pdf.txt"]
HELPERS = ["tools/pdf/build_completion_exhibits.py", "tools/pdf/build_consolidated_review.py",
           "tools/pdf/build_identity_review_annex.py"]


def normalize(text: str) -> str:
    return " ".join(text.split())


def completion_outputs(root: Path, output: Path, record: Path) -> tuple[Path, Path]:
    """Reject nested destinations before rendering or creating directories.

    A report path cannot also be an output's parent directory. Keep this
    additive guard here so historical authoring helper bytes remain preserved.
    """
    output, record = validate_outputs(root, output, record,
                                      [root / name for name in INPUTS + HELPERS])
    require(not output.is_relative_to(record) and not record.is_relative_to(output),
            "Completion output and record paths cannot contain one another")
    return output, record


def fragments(markdown: str) -> list[str]:
    """Expected printed text, including table cells, independently of pagination."""
    result = []
    for line in markdown.splitlines():
        line = line.strip()
        if not line or line.startswith("```"):
            continue
        if line.startswith("|"):
            pieces = [c.strip() for c in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c.replace(" ", "")) for c in pieces):
                continue
        else:
            pieces = [re.sub(r"^#{1,3}\s+", "", line)]
        for piece in pieces:
            value = unescape(re.sub(r"<[^>]+>", "", inline(piece)))
            if value:
                result.append(value)
    return result


def compose(root: Path) -> tuple[str, list[str]]:
    texts = [(root / name).read_text(encoding="utf-8") for name in DOCUMENTS]
    data = json.loads((root / f"data/claim_scenarios_{TASK}.json").read_text(encoding="utf-8"))
    table = ["# All-199 scenario navigation", "",
             "Each row links the exact candidate to four explicit later-claim comparison records. Feature text below is a navigation excerpt; the appended application contains all complete candidate texts. Full disclosed/missing features, contexts, qualified arguments and counterarguments remain in the separately supplied editable scenario exhibit and JSON. No final statutory outcome or actual later claim is asserted.", "",
             "| Claim / family | Added-feature excerpt | Four scenario IDs | Textual locators |",
             "| --- | --- | --- | --- |"]
    ids = []
    for claim in data["claims"]:
        number = claim["claim_number"]
        own = claim["actual_additional_feature"]
        if len(own) > 125:
            own = own[:122].rsplit(" ", 1)[0] + "..."
        sids = [r["id"] for r in claim["scenario_records"]]
        require(len(sids) == 4, "Each crosswalk claim needs four scenarios")
        ids.extend(sids)
        locators = ", ".join(f"[{p}]" for p in claim["complete_combination_mapped_paragraphs"])
        table.append(f"| {number} / {claim['family_id']} | {own.replace('|', '/')} | {', '.join(sids)} | {locators} |")
    preface = "\n".join([
        "# Materials application completion review packet", "", "Prepared 5 October 2026 | Local review exhibits for task 2026-10-04", "",
        "Proposed sole inventor: Robert M. Layne, as instructed; legal conception and filing particulars remain unconfirmed.", "",
        "This packet presents the additive decision guide, eleven-edition evidence index, material/state/process matrix and navigation to 796 later-claim scenarios. The preserved 47-page 3 October application follows as a separate part with its own preparation label and page numbering. Review companions are not silently content of that application or an earlier disclosure.", "",
        "No applicant physical experiments are performed or planned. No filing, earliest public availability, complete chronological novelty search, final statutory result, legal inventorship confirmation, license grant or universal blocking is asserted.", "",
        "The editable Markdown/JSON sidecars retain source locators, exact fractions, assumptions and evidence categories. Use those detailed records for an actual comparison; navigation excerpts supply no independent legal or physical support.", "",
    ])
    return "\n\n".join([preface, *texts, "\n".join(table)]), ids


def main() -> int:
    require(reportlab.Version == "4.4.9" and pypdf.__version__ == "6.19.0",
            "Use the repository's pinned optional ReportLab 4.4.9 / pypdf 6.19.0 authoring runtime")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--record", type=Path)
    parser.add_argument("--check", action="store_true", help="Read inputs and validate outputs without authoring")
    args = parser.parse_args()
    root = args.package_root.resolve()
    # Author only into ignored scratch. A reviewed adoption step copies the
    # exact output bytes into the explicit package inventory after visual QA.
    generated_pdf = root / "generated_reports" / "pdf"
    output, record = completion_outputs(root, args.output or generated_pdf / Path(PDF).name,
                                        args.record or generated_pdf / Path(RECORD).name)
    captures = {name: (root / name).read_bytes() for name in INPUTS + HELPERS}
    text, ids = compose(root)
    if args.check:
        print(json.dumps({"inputs": len(captures), "claims": 199, "scenario_ids": len(ids), "files_written": 0}))
        return 0
    generated = root / "generated_reports"
    require(not generated.is_symlink() and not generated.is_junction(), "Authoring scratch must be ordinary")
    generated.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="completion-review-", dir=generated) as directory:
        scratch = Path(directory)
        annex = scratch / "annex.pdf"
        fonts = configure_fonts(None, [text])
        label = "Completion review 2026-10-05"
        headings = render(text, annex, label)
        annex_reader = PdfReader(annex)
        body_pages = []
        for number, page in enumerate(annex_reader.pages, 1):
            lines = (page.extract_text() or "").splitlines()
            # The retained layout helper draws its footer first. Validate that
            # footer separately before matching paragraphs across page breaks.
            require(lines[:2] == [label + " - REVIEW; no filing asserted", str(number)],
                    "Review PDF footer/page extraction differs")
            body_pages.append("\n".join(lines[2:]))
        actual = normalize("\n".join(body_pages))
        expected = fragments(text)
        # Wrapped long relative filenames can acquire extraction whitespace
        # inside a token. Match the full character sequence while ignoring
        # whitespace; this retains every source-bearing glyph and punctuation.
        def compact(value):
            return re.sub(r"\s+", "", value)
        compact_actual = compact(actual)
        missing = [value for value in expected if compact(value) not in compact_actual]
        require(not missing, "Review PDF omitted printed fragments: " + str(missing[:3]))
        require(all(id_ in actual for id_ in ids) and len(ids) == len(set(ids)) == 796,
                "Review PDF lost scenario navigation")
        app_reader = PdfReader(BytesIO(captures[APPLICATION_PDF]))
        require(len(app_reader.pages) == 47, "Preserved application page count differs")
        writer = PdfWriter()
        writer.append(annex_reader, import_outline=True)
        app_start = len(writer.pages)
        writer.append(app_reader, import_outline=True)
        writer.add_outline_item("Preserved 3 October application: 47 pages", app_start)
        writer.add_metadata({"/Title": "Materials application and completion review exhibits",
                             "/Author": "Materials disclosure review package",
                             "/Subject": "Local unfiled review; later exhibits not backdated"})
        final = scratch / "packet.pdf"
        with final.open("xb") as stream:
            writer.write(stream)
        reread = PdfReader(final)
        for a, b in zip(app_reader.pages, reread.pages[app_start:]):
            require(normalize(a.extract_text() or "") == normalize(b.extract_text() or ""),
                    "Packet changed application page text")
        claims = re.findall(r"^\*\*Claim (\d+)\.\*\* (.+)$", captures[APPLICATION].decode("utf-8"), re.M)
        app_text = normalize("\n".join(p.extract_text() or "" for p in reread.pages[app_start:]))
        require(len(claims) == 199 and all(normalize(body) in app_text for _, body in claims),
                "Packet lost complete candidate claim text")
        for name, original in captures.items():
            require((root / name).read_bytes() == original, "Authoring input changed during run: " + name)
        metadata = {"schema_version": 1, "task_identifier_date": TASK, "prepared_date": "2026-10-05",
                    "recorded_utc": datetime.now(timezone.utc).isoformat(),
                    "status": "local unfiled review; visual inspection pending",
                    "baseline_commit": "e0233fe2863b2fd9d43be634b6dc6022b5cc0074",
                    "authoring_versions": {"python": sys.version.split()[0], "reportlab": reportlab.Version,
                                           "pypdf": pypdf.__version__},
                    "fonts": fonts,
                    "sources": [{"path": n, "size_bytes": len(v), "sha256": sha256(v).hexdigest()}
                                for n, v in captures.items()],
                    "pdf": {"path": report_path_label(output, root), "intended_archive_path": PDF,
                            "size_bytes": final.stat().st_size, "sha256": sha256(final.read_bytes()).hexdigest(),
                            "review_pages": app_start, "application_first_packet_page": app_start + 1,
                            "application_pages": 47, "total_pages": len(reread.pages)},
                    "headings": headings, "complete_printed_fragments_checked": len(expected),
                    "review_footer_page_labels_checked": len(body_pages),
                    "printed_fragment_match_convention": "All non-whitespace characters retained; wrapped filename extraction may add internal whitespace.",
                    "scenario_navigation_ids_checked": len(ids), "exact_application_claim_bodies_checked": 199,
                    "application_page_texts_unchanged": True, "original_application_bytes_unchanged": True,
                    "visual_review": {"status": "pending"}, "filing_asserted": False,
                    "application_content_adoption": False, "legal_or_physical_sufficiency_certified": False}
        report = scratch / "authoring.json"
        report.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        output.parent.mkdir(parents=True, exist_ok=True)
        record.parent.mkdir(parents=True, exist_ok=True)
        publish_outputs_exclusive([(final, output), (report, record)])
    print(json.dumps(metadata["pdf"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
