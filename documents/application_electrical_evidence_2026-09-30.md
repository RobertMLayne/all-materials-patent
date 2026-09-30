# Application edition with attributed electrical evidence

Prepared 30 September 2026. This prospective, unfiled edition derives from the [preserved preparation-evidence application](provisional_application_preparation_evidence_2026-09-30.md), SHA-256 `c9b8f44b79f970379054cf89508cb81853906dbb825a6bca476eb4b0216f575e`, at repository baseline `e9471e2dc71560e930d062a16b40ae4732d1e90a`.

The [application source](provisional_application_electrical_evidence_2026-09-30.md), [review PDF](pdf/provisional_application_electrical_evidence_2026-09-30.pdf), [textual claim map](../data/claim_support_map_electrical_evidence_2026-09-30.json), [source review](../data/electrical_source_review_2026-09-30.json) and [actual authoring record](../data/application_electrical_evidence_2026-09-30.json) identify this edition. The eight earlier PDFs and their captured sources, maps, records and code snapshots remain historical artifacts.

## Applied content and reasons

Numbered paragraph [0066] identifies the new adjacent electrical evidence block. Its seven prose blocks and six data rows distinguish reported preparation, the given loading threshold, fitted parameters, model quantities and unperformed verification. All other numbered paragraphs, all 199 claims and their individual assessment records remain unchanged. The complete inherited hydrogel property and preparation blocks are preserved.

Inspecting the publisher's actual Figure 2 was necessary to distinguish its percentage coordinate from a normalized fraction and its logarithmic ordinate from conductivity. The new block prints the coordinate conversion and required prefactor rescaling rather than applying the reported prefactor to a different unit convention. Reviewing the original Methods identifies reported input grades and measurement operations; it leaves missing lot, impurity, retained-product and measurement details open. Independent review corrected the distinction between a given threshold and two fitted parameters, and between an experimentally observed cooperative response and a theoretical antagonistic prediction. The proposed alternative is conditional and unperformed.

A separate application edition puts the verified teaching into an actual description while preserving earlier provenance. Another companion alone would leave that description unchanged, and replacing an old PDF would obscure which source it contained. Existing literature does not justify an invented applicant experiment or new applicant claim. No new curve or digitized data are generated, and copyrighted source graphics are not republished.

Publisher HTML, Figure 2 graphics and supplementary PDF bytes were acquired and identified locally. Relevant supplement pages were inspected visually and all five pages by text. Original journal Methods were available through coauthor-uploaded cached primary text whose identity matches the publisher; native acquisition failed. The record does not claim raw main-PDF bytes, a main-PDF hash or complete graphical verification. The upload date and original publication date remain distinct.

The scope-dependent inquiry in [MPEP §2164](https://www.uspto.gov/web/offices/pac/mpep/s2164.html) and the reference-enablement distinction in [MPEP §2121](https://www.uspto.gov/web/offices/pac/mpep/s2121.html) remain applicable. Known operations can assist a skilled reader without a categorical requirement to reproduce every upstream synthesis. Their actual applicability and preparation without undue experimentation still require assessment. [PCT ISPE 4.25-4.27](https://www.wipo.int/en/web/pct-system/texts/ispe/4_02_27) supports retaining essential teaching in the description; hyperlinks are not treated as automatic incorporation of omitted essential content.

## Authoring and validation

The maintained builder adds `--edition electrical-evidence`, retaining its earlier default and named selections. It captures nine inputs and checks complete new prose/table rows in reading order, every full numbered paragraph and claim, all 279 numbered starts, both vector drawings and inherited property/preparation content. Explicit electrical-table widths support readable wrapping. An exact leading-footer check avoids deleting an unrelated matching table number. Bounded source extraction uses paragraph-start terminators, so inline cross-references cannot truncate the teaching.

Optional authoring uses the existing Python 3.12.14 runtime, ReportLab 4.4.9, pypdf 6.19.0 and recorded Arial font hashes. No tooling is installed. Three inert snapshots retain the code actually used. The authoring record separates the generated output from its archival path and binds the captured inputs to its PDF bytes. Text extraction and subsequent rendered-page inspection have distinct scopes.

The final PDF has 32 pages. Text checks covered all 279 numbered starts, the seven complete electrical prose blocks and seven complete table rows including the header, the inherited ten preparation prose blocks and eight table rows, and the ten property data rows. All 32 pages were rendered with Poppler 26.07.0 at 108 dpi and inspected in eight contact sheets; pages 12, 13, 15 and 16 received full-page inspection. Root independently inspected those four pages. No actionable visual findings remained. A separate byte comparison confirmed 33 historical artifacts, including all eight earlier PDFs, unchanged from the baseline. These are text, provenance and appearance checks, not physical or legal certification.

The offline standard-library verifier checks derivation, surrounding-body preservation, claim/map identity, table relationships, independent percent-to-fraction arithmetic, the fit convention, captured input hashes, PDF identity and recorded coverage. It does not parse the PDF or repeat visual inspection. Four new failure cases reject stale source/map hashes, consistently altered claims, inherited hydrogel drift and confused threshold coordinates despite internally updated records. All three historical edition checks remain unchanged. Configured Ruff, package verification and output-safeguard checks are required locally; protected-branch CI and automated reviews must be verified for the final commit.

Input-only checking with the pinned optional libraries creates no PDF:

```powershell
python -B tools/pdf/build_working_application.py --edition electrical-evidence --baseline-commit e9471e2dc71560e930d062a16b40ae4732d1e90a --check
```

Another review copy requires unused output/report paths and subsequent visual inspection. Preserve this edition's artifact and snapshots rather than assigning later code to its authoring history.

## Remaining work

Resolve the stated input, loading-basis, retained-composition and measurement gaps before treating a new candidate as a precisely specified preparation or measured response. This particular teaching does not establish complete elemental inventory, arbitrary trace abundance, hypothetical constituent availability, all nuclear/particle states or every property. Applicant technical contribution, inventive identity, chronology and filing facts remain unresolved. No filing, earlier entitlement, applicant experiment, measured workflow speedup or universal patent bar is asserted. The [full-scope audit](full_scope_completion_audit.md) remains applicable.
