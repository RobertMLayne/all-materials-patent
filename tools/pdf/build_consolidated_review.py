"""Create a read-only, separately dated review consolidation; never edit sources.

This optional local authoring tool is separate from the package's offline
standard-library verifier. It requires ReportLab 4.4.9 and pypdf 6.10.0.
The original application PDF is appended without overlays or reflow.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from hashlib import sha256
from html import escape
from io import BytesIO
import json
import os
from pathlib import Path
import re
import sys
import tempfile

from pypdf import PdfReader, PdfWriter
from pypdf.constants import PageLabelStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import LongTable, Paragraph, SimpleDocTemplate, TableStyle
# The optional sibling helper must not create bytecode during a read-only check.
sys.dont_write_bytecode = True
from build_identity_review_annex import (  # noqa: E402 - set bytecode guard before this local import
    publish_outputs_exclusive, report_path_label, require, validate_baseline, validate_outputs,
)

DEFAULT_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
INPUTS = (
    "documents/pdf/provisional_application_draft.pdf", "documents/provisional_application_draft.md",
    "documents/technical_scope_supplement.md", "documents/reference_entry_support.md",
    "documents/current_status_addendum.md", "documents/full_scope_completion_audit.md",
    "data/claim_support_map.json", "documents/drawings/composition_simplex.svg",
    "documents/drawings/material_record_sequence.svg",
)
WIDTH = letter[0] - 96


def configure_fonts(directory: Path | None, texts: list[str]) -> list[dict]:
    """Select installed Unicode fonts without installation or import-time reads."""
    directories = [directory] if directory else [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts",
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/share/fonts/truetype/liberation2"),
    ]
    profiles = [
        ("arial.ttf", "arialbd.ttf", "ariali.ttf", "arialbi.ttf"),
        ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans-Oblique.ttf", "DejaVuSans-BoldOblique.ttf"),
        ("LiberationSans-Regular.ttf", "LiberationSans-Bold.ttf", "LiberationSans-Italic.ttf", "LiberationSans-BoldItalic.ttf"),
    ]
    selected = None
    for candidate in directories:
        for names in profiles:
            paths = [candidate / name for name in names]
            if all(path.is_file() for path in paths):
                selected = paths
                break
        if selected:
            break
    require(selected is not None, "Supply --font-directory with all four Arial, DejaVu Sans or Liberation Sans styles")
    characters = set("".join(texts).replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-"))
    metadata = []
    aliases = ("ReviewArial", "ReviewArialBold", "ReviewArialItalic", "ReviewArialBI")
    for alias, path in zip(aliases, selected):
        font = TTFont(alias, str(path))
        missing = sorted(ord(char) for char in characters if char not in "\n\r\t"
                         and ord(char) not in font.face.charWidths)
        require(not missing, f"Font {path.name} lacks source characters: {missing}")
        pdfmetrics.registerFont(font)
        metadata.append({"name": path.name, "sha256": digest(path)})
    pdfmetrics.registerFontFamily("ReviewArial", normal="ReviewArial", bold="ReviewArialBold",
                                 italic="ReviewArialItalic", boldItalic="ReviewArialBI")
    return metadata


BODY = ParagraphStyle("ReviewBody", fontName="ReviewArial", fontSize=10, leading=13.8,
                      spaceAfter=7, allowWidows=0, allowOrphans=0)
TITLE = ParagraphStyle("ReviewTitle", parent=BODY, fontName="ReviewArialBold", fontSize=19,
                       leading=24, spaceAfter=14, keepWithNext=True)
H1 = ParagraphStyle("ReviewHeading", parent=BODY, fontName="ReviewArialBold", fontSize=13,
                    leading=17, spaceBefore=12, spaceAfter=7, keepWithNext=True)
H2 = ParagraphStyle("ReviewSubheading", parent=H1, fontSize=11, leading=15, spaceBefore=9)
CELL = ParagraphStyle("ReviewCell", parent=BODY, fontSize=8.8, leading=11.5, spaceAfter=0)
HEAD = ParagraphStyle("ReviewHeaderCell", parent=CELL, fontName="ReviewArialBold", textColor=colors.white)
TOKEN = re.compile(r"\[([^\]]+)\]\(([^\s)]+)\)|\*\*(.+?)\*\*|`([^`]+)`")


def inline(value: str) -> str:
    # Display normalization only; input bytes and original PDF are preserved.
    value = value.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    out, cursor = [], 0
    for match in TOKEN.finditer(value):
        out.append(escape(value[cursor:match.start()]))
        if match.group(1) is not None:
            label, url = match.group(1), match.group(2)
            if url.startswith(("https://", "http://")):
                out.append(f'<link href="{escape(url, quote=True)}" color="#1c5277">{escape(label)}</link>')
            else:
                out.append(escape(label) + " (source file: " + escape(url) + ")")
        elif match.group(3) is not None:
            out.append("<b>" + escape(match.group(3)) + "</b>")
        else:
            out.append(escape(match.group(4)))
        cursor = match.end()
    out.append(escape(value[cursor:]))
    return "".join(out)


def table(block: list[str]) -> LongTable:
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in block]
    rows = [r for r in rows if not all(re.fullmatch(r":?-+:?", c.replace(" ", "")) for c in r)]
    if not rows or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("Inconsistent Markdown table column count")
    n = len(rows[0])
    proportions = {2: [0.29, 0.71], 3: [0.22, 0.34, 0.44], 4: [0.12, 0.25, 0.25, 0.38]}.get(n, [1/n]*n)
    values = [[Paragraph(inline(v), HEAD if i == 0 else CELL) for v in row] for i, row in enumerate(rows)]
    result = LongTable(values, colWidths=[WIDTH*p for p in proportions], repeatRows=1,
                       hAlign="LEFT", spaceBefore=4, spaceAfter=10)
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#29465b")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f6f8")]),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#c5cfd8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return result


class ReviewDoc(SimpleDocTemplate):
    def __init__(self, path: Path, label: str):
        super().__init__(str(path), pagesize=letter, leftMargin=48, rightMargin=48,
                         topMargin=48, bottomMargin=48, title=label,
                         author="Materials disclosure review package")
        self.label = label
        self.headings: list[dict] = []

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in ("ReviewTitle", "ReviewHeading", "ReviewSubheading"):
            title = flowable.getPlainText()
            key = f"section-{len(self.headings)}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title, key, level=0)
            self.headings.append({"title": title, "part_page": self.page})

    def footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("ReviewArial", 8)
        canvas.setFillColor(colors.HexColor("#526171"))
        canvas.drawString(48, 28, self.label + " - REVIEW; no filing asserted")
        canvas.drawRightString(letter[0]-48, 28, str(doc.page))
        canvas.restoreState()


def render(text: str, output: Path, label: str) -> list[dict]:
    lines, story, i = text.splitlines(), [], 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            story.append(table(block))
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            style = {1: TITLE, 2: H1, 3: H2}[len(heading.group(1))]
            story.append(Paragraph(inline(heading.group(2)), style))
            i += 1
            continue
        if line.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            if i == len(lines):
                raise ValueError("Unterminated code block")
            story.extend(Paragraph(escape(v) or " ", BODY) for v in block)
            i += 1
            continue
        bullet = line.startswith("- ") or re.match(r"^\d+\.\s", line)
        if bullet:
            story.append(Paragraph(inline(line), BODY))
            i += 1
            continue
        block = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(("#", "|", "- ", "```")):
            block.append(lines[i].strip())
            i += 1
        story.append(Paragraph(inline(" ".join(block)), BODY))
    document = ReviewDoc(output, label)
    document.build(story, onFirstPage=document.footer, onLaterPages=document.footer)
    return document.headings


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", "--stage", dest="package_root", type=Path,
                        default=DEFAULT_PACKAGE_ROOT)
    parser.add_argument("--output", type=Path, help="New PDF path; default ignored generated_reports/pdf/")
    parser.add_argument("--report", type=Path, help="New JSON path; default ignored generated_reports/pdf/")
    parser.add_argument("--companion", type=Path, help="Exact identity-annex PDF relied upon")
    parser.add_argument("--prepared-date", required=True, help="Actual review preparation date YYYY-MM-DD")
    parser.add_argument("--baseline-commit", required=True, help="Caller-selected full Git commit ID")
    parser.add_argument("--font-directory", type=Path, help="Directory with a supported Unicode font family")
    parser.add_argument("--check", action="store_true", help="Read inputs and validate maps; write no files")
    args = parser.parse_args(argv)
    require(date.fromisoformat(args.prepared_date).isoformat() == args.prepared_date,
            "Preparation date must be an explicit ISO calendar date")
    baseline = validate_baseline(args.baseline_commit)
    stage = args.package_root.resolve()
    inputs = INPUTS
    companion = (args.companion or stage / "documents/pdf/materials_identity_data_review_annex.pdf").resolve()
    generated = stage / "generated_reports/pdf"
    output, report_path = validate_outputs(
        stage, args.output or generated / f"materials_provisional_review_{args.prepared_date}.pdf",
        args.report or generated / f"consolidated_review_validation_{args.prepared_date}.json",
        [stage / name for name in inputs] + [companion],
    )
    input_bytes = {name: (stage/name).read_bytes() for name in inputs}
    before = {name: sha256(payload).hexdigest() for name, payload in input_bytes.items()}
    companion_bytes = companion.read_bytes()
    companion_reader = PdfReader(BytesIO(companion_bytes))
    companion_hash = sha256(companion_bytes).hexdigest()
    companion_pages = len(companion_reader.pages)
    original = PdfReader(BytesIO(input_bytes[inputs[0]]))
    original_texts = [page.extract_text() for page in original.pages]
    if len(original.pages) != 27:
        raise ValueError("Original application PDF changed; reassess provenance")
    full_original = "\n".join(original_texts)
    paragraph_locations = {}
    claim_locations = {}
    for index, text in enumerate(original_texts, 1):
        for number in re.findall(r"(?m)^\[(\d{4})\][ \t]+(?=\S)", text):
            # Later support tables repeat paragraph references. The first
            # actual paragraph opening identifies its original definition.
            paragraph_locations.setdefault(number, {index})
        for number in re.findall(r"Claim\s+(\d+)\.", text):
            claim_locations[int(number)] = index
    if sorted(claim_locations) != list(range(1, 200)):
        raise ValueError("Original PDF does not contain the complete candidate claim sequence")
    if not all(f"[{i:04d}]" in full_original for i in range(1, 81)):
        raise ValueError("Original PDF is missing a numbered paragraph")
    if sorted(paragraph_locations) != [f"{i:04d}" for i in range(1, 81)]:
        raise ValueError("Cannot uniquely locate the original numbered paragraphs")
    claims = json.loads(input_bytes["data/claim_support_map.json"].decode("utf-8"))["claims"]
    require([claim["claim_number"] for claim in claims] == list(range(1, 200)),
            "Claim-support map does not contain the ordered 199 candidates")
    require(all(p in paragraph_locations for claim in claims for p in claim["textual_support_paragraphs"]),
            "Claim-support map refers to a missing original paragraph")
    original_source = input_bytes[inputs[1]].decode("utf-8")
    require(re.findall(r"(?m)^\[(\d{4})\]", original_source) == [f"{n:04d}" for n in range(1, 81)],
            "Original Markdown paragraph sequence changed")
    require([int(n) for n in re.findall(r"(?m)^\*\*Claim (\d+)\.\*\*", original_source)] == list(range(1, 200)),
            "Original Markdown candidate-claim sequence changed")
    fonts = configure_fonts(args.font_directory, [input_bytes[name].decode("utf-8")
                                                for name in inputs if name.endswith(".md")])
    paragraph_map = {number: sorted(pages) for number, pages in sorted(paragraph_locations.items())}
    summary = {"status": "read-only input and original-location checks passed",
               "prepared_date": args.prepared_date, "baseline_commit": baseline,
               "baseline_interpretation": "Caller-selected reference; source hashes identify exact input bytes",
               "source_hashes": before, "original_application_pages": len(original.pages),
               "original_numbered_paragraphs": 80, "candidate_claims": 199,
               "paragraph_map_part_A_pages": paragraph_map,
               "claim_map_part_A_pages": claim_locations, "fonts": fonts,
               "companion": {"filename": companion.name, "pages": companion_pages, "sha256": companion_hash},
               "files_written": 0, "authoring_executed": False}
    require({name: digest(stage/name) for name in inputs} == before and digest(companion) == companion_hash,
            "Input changed during read-only checks")
    if args.check:
        print(json.dumps(summary, indent=2, ensure_ascii=True))
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="materials-review-", dir=output.parent) as scratch:
        scratch = Path(scratch)
        parts = [{"label": "A", "title": "Original application working draft (29 September 2026)",
                  "path": BytesIO(input_bytes[inputs[0]]), "headings": []}]
        for label, title, source in (("B", "Technical definitions and accounting", inputs[2]),
                                     ("C", "Five material families and proposed study cards", inputs[3]),
                                     ("D", "Current publication and filing status", inputs[4]),
                                     ("E", "Full requested-scope audit and unresolved facts", inputs[5])):
            target = scratch/f"part-{label}.pdf"
            headings = render(input_bytes[source].decode("utf-8"), target, f"Part {label}: {title}")
            parts.append({"label": label, "title": title, "path": target, "headings": headings})
        page_map = []
        offset = 0
        for part in parts:
            pages = len(PdfReader(part["path"]).pages)
            part.update(page_count=pages, body_start=offset+1, body_end=offset+pages)
            page_map.append({k: part[k] for k in ("label", "title", "page_count", "body_start", "body_end")})
            offset += pages
        support_rows = ["| Claim | Original paragraph locations | Part A claim page | Review status |",
                        "| --- | --- | --- | --- |"]
        for claim in claims:
            refs = ", ".join(f"[{p}] (A {','.join(map(str, sorted(paragraph_locations.get(p, []))))})" for p in claim["textual_support_paragraphs"])
            support_rows.append(f"| {claim['claim_number']} | {refs} | A {claim_locations[claim['claim_number']]} | Textual map; novelty, legal support and relevant physical scope remain unresolved. |")
        support_text = ("# Per-claim page and textual-support map\n\nEvery claim remains a candidate. Textual locations do not establish physical enablement, novelty, eligibility, unity or inventorship. Original Part A page numbers are used below.\n\n"
                        + "\n".join(support_rows)
                        + "\n\n## New partial evidence\n\nPart B supplies exact-domain and accounting qualifications. Part C adds the five individually identified literature families and SC-ALLOY-01, SC-OXIDE-01, SC-MOLECULAR-01, SC-POLYMER-01 and SC-COMPOSITE-01. Claims 176-178 still inherit claim 1's closed whole-product inventory and exact zero outside it. Formula, host, feed and filler-loading accounting does not establish those limitations. Claims 197-199 receive further proposed scenario/evidence fields without new applicant measurements or validated universal mechanisms.\n\nActual physical preparations, unknown recipe fields, assay limits and human contribution must be evaluated separately. No map row promotes a candidate to allowed, enabled or novelty-cleared status.\n")
        support_path = scratch/"part-F.pdf"
        support_headings = render(support_text, support_path, "Part F: Claim page and support map")
        support_pages = len(PdfReader(support_path).pages)
        parts.append({"label": "F", "title": "Per-claim page and textual-support map", "path": support_path,
                      "headings": support_headings, "page_count": support_pages, "body_start": offset+1, "body_end": offset+support_pages})
        body_pages = offset+support_pages
        # The cover's own count is measured, then rendered again with true physical offsets.
        def cover_text(cover_pages: int) -> str:
            rows = ["| Part | Included content | Physical PDF pages |", "| --- | --- | --- |"]
            rows += [f"| {p['label']} | {p['title']} ({p['page_count']} pages) | {p['body_start']+cover_pages}-{p['body_end']+cover_pages} |" for p in parts]
            source_rows = ["| Included source file | SHA-256 |", "| --- | --- |"]
            source_rows += [f"| {name} | {value} |" for name, value in before.items()]
            return (f"# Consolidated provisional materials disclosure\n\n**REVIEW edition - prepared {args.prepared_date}.** No application filing, priority entitlement, fee payment, inventorship certification, full-scope enablement or universal bar to later patents is asserted.\n\n"
                    f"Caller-selected baseline reference {baseline}; exact package source hashes are identified below. The baseline label does not certify a clean checkout or an exact commit match. This edition has {body_pages+cover_pages} pages, including this front matter. Preparation is not a certified public-availability date.\n\n"
                    "## Scope and remaining facts\n\nThe requested scope remains all nonempty supports through 138 elemental labels, all normalized rational targets including arbitrarily small positive fractions, symbolic real domains, isotope/state and particle constructions, and expected/contrary property scenarios. The 118 recognized labels and 20 hypothetical placeholders retain separate status. Numerical descriptions and dated identities do not establish arbitrary preparation, properties or future legal effect.\n\n"
                    "The original 80 numbered paragraphs and 199 candidate claims are preserved in Part A. Its original printed page numbers and preparation date remain unchanged; PDF labels and this map provide consolidated navigation. The two drawings appear on Part A pages 10-11. Parts B/C print the actual new technical and literature text. Part D qualifies earlier publication-stage statements. Part E retains the complete requested objective and its unresolved evidence. Part F maps every candidate to actual original pages.\n\n"
                    f"The separate companion {companion.name} has {companion_pages} review pages and SHA-256 {companion_hash}. Its intended scope is the complete scoped NUBASE ASCII rows and PDG identity selections with schema/provenance; validate its own source counts and values using the annex tool and report. Those full record sets are NOT embedded in this core PDF; include and validate the companion if relying on them. No full PDG property database or unrestricted current/future entity universe is included. External links identify sources and do not replace absent essential technical content. Review page counts are not a PCT chargeable-sheet or accepted-filing-format determination.\n\n"
                    "TECH-001 remains open: identify the actual human technical contribution and responsible inventors. Complete source-critical preparation gaps, selected embodiment support, claim-specific patent analysis and actual applicant/entitlement information before calling a packet ready to submit. No applicant facts or experiments are invented. The original filing memorandum and earlier PDFs remain separate historical review artifacts; their old page/check counts do not certify this edition.\n\n"
                    "## Included content and navigation\n\n" + "\n".join(rows)
                    + "\n\n## Exact source versions\n\nThese hashes identify read-only build inputs. They are not trusted timestamps or proof of earliest publication.\n\n"
                    + "\n".join(source_rows) + "\n")
        cover = scratch/"front-matter.pdf"
        estimated = 0
        for _ in range(3):
            render(cover_text(estimated), cover, "Review version and included-content map")
            actual = len(PdfReader(cover).pages)
            if actual == estimated:
                break
            estimated = actual
        else:
            raise ValueError("Front-matter pagination did not stabilize")
        writer = PdfWriter()
        writer.append(cover, outline_item="Review version and included-content map")
        writer.set_page_label(0, estimated-1, style=PageLabelStyle.DECIMAL, prefix="Review-")
        offset = estimated
        for part in parts:
            writer.append(part["path"], outline_item=f"Part {part['label']}: {part['title']}")
            writer.set_page_label(offset, offset+part["page_count"]-1, style=PageLabelStyle.DECIMAL,
                                  prefix=part["label"]+"-")
            part["physical_start"], part["physical_end"] = offset+1, offset+part["page_count"]
            for heading in part["headings"]:
                heading["physical_page"] = offset+heading["part_page"]
            offset += part["page_count"]
        writer.add_metadata({"/Title": "Consolidated provisional materials disclosure - REVIEW edition",
                             "/Subject": "Unfiled review edition; mathematical domain and technical evidence remain distinct"})
        temporary_output = scratch / "consolidated.pdf"
        writer.write(temporary_output)
        final = PdfReader(temporary_output)
        if len(final.pages) != offset:
            raise ValueError("Merged page count mismatch")
        for i, page in enumerate(original.pages):
            merged = final.pages[estimated+i]
            original_content = page.get_contents()
            merged_content = merged.get_contents()
            if (merged.extract_text() != original_texts[i] or merged.mediabox != page.mediabox
                    or merged.cropbox != page.cropbox or merged.rotation != page.rotation
                    or (merged_content.get_data() if merged_content else b"")
                    != (original_content.get_data() if original_content else b"")):
                raise ValueError(f"Original page {i+1} changed text, geometry or content stream")
        final_text = "\n".join(page.extract_text() for page in final.pages)
        for marker in ("SC-ALLOY-01", "SC-OXIDE-01", "SC-MOLECULAR-01", "SC-POLYMER-01", "SC-COMPOSITE-01",
                       "MAT-LIT-MOLECULAR-0001", "MAT-LIT-POLYMER-0001", "MAT-LIT-COMPOSITE-0001",
                       "mixture-effective molar mass", "necessarily inherent"):
            if marker not in final_text:
                raise ValueError("Missing rendered content marker: " + marker)
        after = {name: digest(stage/name) for name in inputs}
        if after != before:
            raise ValueError("Input source bytes changed during build")
        if digest(companion) != companion_hash:
            raise ValueError("Companion annex changed during build")
        application_offset = next(part["physical_start"] - 1 for part in parts if part["label"] == "A")
        physical_paragraph_map = {number: [page + application_offset for page in pages]
                                  for number, pages in paragraph_map.items()}
        physical_claim_map = {number: page + application_offset for number, page in claim_locations.items()}
        report = {"prepared_date": args.prepared_date, "build_observed_utc": datetime.now(timezone.utc).isoformat(),
                  "baseline_commit": baseline,
                  "baseline_interpretation": "Caller-selected reference; source hashes identify exact input bytes",
                  "output": report_path_label(output, stage), "sha256": digest(temporary_output), "pages": len(final.pages),
                  "source_hashes_before": before, "source_hashes_unchanged": before == after,
                  "original_application_pages": 27, "original_text_geometry_content_streams_unchanged": True,
                  "original_numbered_paragraphs_present": 80, "candidate_claim_sequence_present": 199,
                  "front_matter_pages": estimated,
                  "companion": {"filename": companion.name, "pages": companion_pages, "sha256": companion_hash},
                  "paragraph_map_physical_pages": physical_paragraph_map,
                  "claim_map_physical_pages": physical_claim_map,
                  "paragraph_map_part_A_pages": paragraph_map, "claim_map_part_A_pages": claim_locations,
                  "font_files": fonts, "builder_sha256": digest(Path(__file__)),
                  "parts": [{k: p[k] for k in ("label", "title", "page_count", "physical_start", "physical_end", "headings")} for p in parts],
                  "visual_review": "Pending rendered-page inspection; text checks do not establish appearance.",
                  "limitations": "Review edition only; no filing, full-scope enablement, inventorship or universal prior-art effect established."}
        temporary_report = scratch / "validation.json"
        temporary_report.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
        publish_outputs_exclusive([(temporary_output, output), (temporary_report, report_path)])
        print(json.dumps({"output": report_path_label(output, stage), "pages": len(final.pages),
                          "report": report_path_label(report_path, stage),
                          "parts": [(p["label"], p["page_count"]) for p in parts],
                          "source_hashes_unchanged": True, "visual_review": "pending"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
