# Application edition with attributed preparation evidence

Prepared 30 September 2026. This prospective, unfiled edition derives from the [preserved property-evidence application](provisional_application_property_evidence_2026-09-30.md), SHA-256 `b311bc0f86eb4b15955a275ba0539bcc8753a59052411739288a645f7ee2476e`, at repository baseline `b31593f84ccb26a19cf1642d4a6115cb6a1543f0`.

The [new application source](provisional_application_preparation_evidence_2026-09-30.md), [review PDF](pdf/provisional_application_preparation_evidence_2026-09-30.pdf), [textual claim map](../data/claim_support_map_preparation_evidence_2026-09-30.json), [source review and calculations](../data/hydrogel_preparation_source_review_2026-09-30.json) and [authoring record](../data/application_preparation_evidence_2026-09-30.json) identify the actual edition. The seven earlier PDFs and their sources, maps, records and actual authoring snapshots remain historical artifacts. The fixed consolidated review still contains the original application.

## Applied content and decisions

Numbered paragraph [0065] now identifies its added preparation record. The adjacent new block prints the specific monomer connectivities, source-reported modified operations, PIC preparation and gel assembly, and a calculated monomer-only feed balance. The preceding ten-row property table and all four evidence notes are preserved. Outside the identified preface, [0065] block and edition-map reference, the body is unchanged. All other numbered paragraphs, all 199 claims and every individual claim-map record retain their wording and assessment statuses.

Checking the actual structural graphic exposed identity conflicts that a generic reference summary would miss. The application retains those conflicts and distinguishes the source-specific inputs. No corrected stereoisomer, supplier identity, complete shorter-monomer route or final specimen assay is invented. Nominal feed amounts support a bounded calculation; they do not establish the incorporated polymer's composition. The source review records primary locators, acquisition hashes and failed acquisition limits. The older precursor source was available as cached primary text but not as downloaded PDF bytes or verified page images; the record states that distinction. Detailed older recipes and copyrighted figures are not reproduced.

A new application edition was chosen to make the verified operations part of its actual description while preserving earlier source-to-PDF provenance. Editing the earlier edition would obscure that provenance, and keeping only another companion would leave the application without this detail. Additional claims were not justified by attributed prior literature. The broad requested scope remains subject to its unresolved support and legal limits.

The legal review applies the scope-dependent, skilled-reader inquiry in [MPEP §2164](https://www.uspto.gov/web/offices/pac/mpep/s2164.html) and the reference-enablement distinction in [MPEP §2121](https://www.uspto.gov/web/offices/pac/mpep/s2121.html). A standalone synthesis tree for every upstream reagent and an applicant repetition are not categorical requirements. This does not excuse unresolved identities or establish preparation without undue experimentation. [PCT ISPE 4.25-4.27](https://www.wipo.int/en/web/pct-system/texts/ispe/4_02_27) supports retaining essential content in the description; citations are not treated as automatic incorporation of omitted essential teaching.

## Authoring and verification

The maintained Python builder accepts `--edition preparation-evidence`; its default remains the first working edition. The named preparation selection uses the same checked inputs and exclusive-output protections. It captures the additional source-review record, checks every complete new prose block and table row in PDF order, and retains the existing checks for 80 full numbered paragraphs, 199 full claims, their 279 start locations, both vector drawings and ten complete property rows. The formula/tail and feed tables have explicit column widths.

Optional authoring uses Python 3.12.14, ReportLab 4.4.9 and pypdf 6.19.0, existing isolated dependencies and recorded font hashes. No tooling is installed. Inert snapshots retain the three code files actually used. The edition record binds eight captured inputs to the actual PDF and distinguishes its authoring output from its archival path. Rendering and appearance findings are recorded after inspection; extraction alone does not establish appearance.

The final PDF has 31 pages. Text checks covered all 279 numbered starts, the ten complete added prose blocks, both added tables' eight complete rows including headers, and the preceding property table's ten rows. All 31 pages were rendered with Poppler 26.07.0 at 108 dpi and inspected in eight contact sheets; pages 9-12 and both drawing pages, 14 and 15, received full-page inspection. No actionable visual findings remained. The source, PDF and actual authoring snapshots were independently checked; 22 historical artifacts and both preceding edition-check functions were confirmed unchanged. These are text, provenance and appearance checks, not physical or legal certification.

The offline standard-library verifier checks derivation, unchanged surrounding body, preservation of the preceding property block, claim/map identity, exact table relationships, independently recomputed ideal feed amounts/fractions, captured input hashes, PDF bytes and recorded navigation/content counts. It does not repeat PDF parsing or appearance review. Meaningful negative cases exercise provenance drift, altered claims despite consistent map updates, and feed-basis corruption. Repository conventions require configured Ruff, package/output-safety checks, reviewed explicit staging, focused commits and the protected-branch review workflow. Actual CI and review results attach to the reviewed commit.

Input-only checking with the pinned optional libraries does not create a PDF:

```powershell
python -B tools/pdf/build_working_application.py --edition preparation-evidence --baseline-commit b31593f84ccb26a19cf1642d4a6115cb6a1543f0 --check
```

Generating another review copy requires unused output and report paths, followed by rendered-page inspection. Do not overwrite this retained edition or relabel its snapshots as later code.

## Remaining work

Resolve the source identity and route-applicability questions before treating this example as a precisely specified preparation. The particular source teaching does not establish whole-product elemental inventory, arbitrary trace abundance, hypothetical constituent availability, all nuclear/particle states or every property. Applicant contribution, actual inventive identity, chronology and filing facts remain unresolved. No earlier entitlement, applicant experiment, filing, measured workflow speedup or universal patent bar is asserted. The [full-scope audit](full_scope_completion_audit.md) remains applicable.
