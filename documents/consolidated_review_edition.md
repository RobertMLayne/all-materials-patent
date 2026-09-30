# Consolidated provisional materials disclosure: review edition

Prepared 30 September 2026. This guide describes a separately dated review packet, its included content, and optional authoring tools. It does not assert a filing, accepted priority date, inventor certification, fee payment, physical enablement, or universal bar to later patents. Preparation dates, observed repository access, and any future official filing date remain different facts.

| Review artifact | Declared contents |
| --- | --- |
| [Core review PDF](pdf/materials_provisional_review_2026-09-30.pdf) | 66 review pages: source/version map; the original application; actual technical and material-reference supplements; current status; full-scope audit; and a per-claim textual-support/page map. |
| [Identity-data companion](pdf/materials_identity_data_review_annex.pdf) | 795 review pages: complete declared entity vocabulary, the retained NUBASE snapshot, selected PDG identity/name/mapping/code tables, schemas, provenance, unknown conventions, and attribution. |
| [Packet manifest](../data/review_packet_manifest.json) | Exact PDF/source hashes, actual page counts, included scope and verification/visual-review evidence for this packet. Read its recorded results rather than treating this guide as a verification receipt. |

The page counts above describe these reviewed artifacts; they are not PCT chargeable-sheet calculations or guarantees that another font or source version will paginate identically. The companion is separate from the core PDF. A file link or hash does not embed its contents in another document or an eventual application. If relying on the identity records, review and preserve the companion itself and the actual accepted filing representation.

## Preserved description and additions

The original [application source](provisional_application_draft.md) and [original PDF](pdf/provisional_application_draft.pdf) retain their 29 September 2026 preparation date. The core imports the original 27 PDF pages without reflow or overlays, preserving paragraphs [0001]-[0080], candidate claims 1-199, and the two drawings on original pages 10-11. Its consolidated page map and PDF labels distinguish new navigation from original printed page numbers.

The core prints the [technical supplement](technical_scope_supplement.md) and [material reference entries](reference_entry_support.md), including five material classes, source-supported preparation/characterization fields, accounting qualifications and proposed study cards. It also prints the [current-status addendum](current_status_addendum.md) and [full-scope audit](full_scope_completion_audit.md). Historical statements in older filing memoranda and earlier PDFs retain their historical context; old page counts and checks do not certify a new edition.

ESTABLISHED identifies attributed published teachings; CALCULATED identifies stated mathematical/model results; PROPOSED identifies unperformed preparations or tests; UNSUPPORTED identifies possibilities lacking adequate support. A proposed comparison must retain its specimen boundary, quantity basis, conditions, observable, uncertainty and decision rule. Nominal formulas, host phases, feed ratios and reinforcement loading do not establish a closed whole-product assay or exact-zero impurities. Textual claim locations do not establish novelty, legal support, physical enablement, eligibility, unity or inventorship. TECH-001 and the unperformed experimental work remain unresolved.

## Identity annex scope and interpretation

The vocabulary contains 138 element labels: 118 recognized and 20 hypothetical placeholders. Its 17 particle categories follow an explicit counting convention. These are different objects from nuclides, nuclear states and PDG charge-state rows.

NUBASE completeness means all 5,843 source-state rows, representing 3,558 (A,Z) pairs, in the retained 761,906-byte ASCII snapshot. The annex includes the exact 25-line header and raw-column schema, actual short slices, unassigned gaps and two rows extending past column 209. Quoted slices and column offsets permit row reconstruction; the original source file remains the byte-exact authority. Z=0 includes the free neutron. A `#` qualifies a property estimated from systematics, not observation status; state indices can have edition-specific meanings, secondary half-life fields can contain bounds/annotations, and `non-exist` remains a literal token. The paper's 2020-10-30 availability boundary, unknown ASCII scientific cutoff, server modification date, retrieval date and literal 2021 discovery-year field remain separate. The published work's CC BY 3.0 notice is distinguished from the companion ASCII header's citation and lack of a separate license notice.

PDG completeness means the pinned 2026.0 selections: 1,170 `pdgparticle`, 450 `pdgid` (`PART`/`SRCH` only), 3,270 `pdgitem`, 1,341 `pdgitem_map`, 71 `pdgdoc`, and 10 source metadata rows. All selected source columns, primary keys, repeated names, nulls, empty strings, numeric zero, question marks and compound quantum strings remain distinct. Twelve groups without charge-state rows remain included. Production status, category flags, MCIDs and conjugation codes do not certify discovery; names/aliases are not additional physical species. The 15 January 2026 publication cutoff, release and retrieval observations remain distinct. PDG attribution and CC BY 4.0 are retained. The selection excludes the full property, measurement, decay and reference database.

Neither archive represents all present/future entities or supplies arbitrary synthesis, confinement, stability, material use or patent enablement.

## Optional maintained tools

Routine `python verify_package.py` uses the standard library and does not regenerate PDFs. Authoring is a separate optional workflow using [the pinned authoring requirements](../tools/pdf/requirements-pdf.txt): ReportLab 4.4.9 and pypdf 6.10.0. These direct version pins are not a full transitive dependency lock or a guarantee of byte-identical output. Reuse an existing suitable environment; installing additional tools is a separate user-controlled step. Do not install fonts automatically or redistribute system fonts.

The [identity builder](../tools/pdf/build_identity_review_annex.py) accepts `--package-root` (alias `--stage`), `--prepared-date`, `--baseline-commit`, optional `--mono-font`, and explicit `--output`/`--report` paths. The [core builder](../tools/pdf/build_consolidated_review.py) accepts the same package/date/baseline/output/report controls plus `--companion` and optional `--font-directory`. The core supports installed Arial, DejaVu Sans or Liberation Sans families with all four styles. The identity tool supports an installed Unicode monospace TrueType font and checks source glyph coverage.

Dates and the full baseline commit ID are supplied by the caller. A baseline label is a reference, not proof that a checkout is clean or that changed working bytes belong to that commit. Source hashes identify the actual captured input bytes. Tools perform no network requests, source amendments or automatic installation. Their default outputs are ignored `generated_reports/pdf/` files. An explicit destination inside the package must remain below `generated_reports/`; external destinations are allowed. Existing outputs, identical PDF/report paths and aliases of input files are refused. Do not point outputs at the committed PDFs.

From the package root, replace the bracketed commit with the reviewed baseline before running read-only checks:

```console
python -B tools/pdf/build_identity_review_annex.py --package-root . --prepared-date 2026-09-30 --baseline-commit <full-reviewed-commit> --check
python -B tools/pdf/build_consolidated_review.py --package-root . --prepared-date 2026-09-30 --baseline-commit <full-reviewed-commit> --companion documents/pdf/materials_identity_data_review_annex.pdf --check
```

`--check` creates no PDF, report, temporary directory or source change. The identity check validates the complete source selection and calculates its layout. The core check validates original paragraph/claim maps, fonts, sources and the actual companion hash/page count; it does not author or promise a future pagination result.

For a new authoring run, choose new output paths, use the actual preparation date, and remove `--check`. Build and validate the identity annex first; supply that exact PDF to the core. The tools refuse replacement of existing review editions. Output reports record source hashes, locations, counts, fonts and automated checks. The core preserves original text, page geometry and content streams and records physical paragraph/claim locations. The companion's own report is needed for its all-line/row validation; the core's companion hash/page observation is not a substitute for that validation.

## Review and release checks

Before releasing a newly generated edition, inspect its final diff and source inventory, run the package's required checks, verify the printed record counts/maps and source hashes, and render every PDF page for layout inspection. Use contact sheets to inspect overall margins, section transitions and recurring navigation, then enlarge equations, tables, raw/unknown/overflow records, source metadata and long strings. Text extraction and geometric bounds do not prove appearance. Check retained original pages against their original rendering, and record exactly which pages were inspected and any remaining limits.

The current packet's observed checks and scoped visual-review results belong in its manifest. This guide does not approve an unrendered future build. The package maintainer handles reviewed inclusion, manifest changes and publication; generating a PDF alone does not file or publish it.

The maintained [output-safeguard regressions](../tools/pdf/test_pdf_outputs.py) run with `python -B tools/pdf/test_pdf_outputs.py`. The fifteen tests retain the reproduced second-output failure and subprocess-substitution cases, plus exclusive-write, sync/close and path-boundary checks, using synthetic files and the standard library. Failure handling retains empty, partial or earlier outputs and attaches inspection guidance to the original exception. The output set is sequential and non-atomic; inspect retained files and choose new output paths before retrying. No destination is deleted during failure handling. CI is configured to run them on Windows and Linux without installing authoring dependencies. These tests exercise file behavior; they do not author PDFs or establish material properties.

## Retained authoring provenance and evidence intake

The 66-page core was reproduced byte for byte with the exact retained [core builder](../data/review_packet_authoring/core_builder_2026-09-30.py.txt) and [shared helper](../data/review_packet_authoring/core_shared_helper_2026-09-30.py.txt). These inert text snapshots preserve the code actually used for that reproduction; maintained executable tools can subsequently change without silently changing this artifact's provenance. The packet manifest links their exact paths and hashes separately from the outer integrity manifest and records the preparation date as 2026-09-30. Its earlier builder-hash record remains in Git history and as an explicitly prior recorded value. The reproduction leaves the PDF hash, all included source bytes, 80 original paragraphs, 199 candidate claims, page maps and scientific content unchanged.

A maintainer who deliberately reruns the retained code must copy both snapshots to reviewed scratch space with their original module names, pass an explicit package root, date, baseline, companion and new output/report paths, and repeat the release checks. The snapshots do not supply fonts or a full dependency lock; byte identity observed in the recorded environment is not a promise for another environment.

The ancillary [applicant evidence intake](applicant_evidence_intake.md) connects TECH-001 and the proposed study cards to missing actual contribution, preparation, characterization and chronology records. It is a blank template outside the core and companion PDFs. Complete a private working copy; no applicant identity, conception record or experimental result is supplied by the template itself.
