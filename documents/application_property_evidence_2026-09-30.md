# Application edition with attributed hydrogel evidence

Prepared 30 September 2026. This prospective, unfiled edition derives from the [preceding working application](provisional_application_working_2026-09-30.md), SHA-256 `1b508938a31b1e7a19b59b3f06edfd21e8378d6ba9e375551250ceb79a8fd198`, at repository baseline `2352f733bcf4fc6d786ccd5f162037a252d2608a`. It is the separately identified application edition containing the verified property example, rather than a companion whose contents are assumed to appear in the application.

The [application source](provisional_application_property_evidence_2026-09-30.md), [29-page PDF](pdf/provisional_application_property_evidence_2026-09-30.pdf), [textual claim map](../data/claim_support_map_property_evidence_2026-09-30.json) and [version record](../data/application_property_evidence_2026-09-30.json) identify this edition. Preserve the preceding source, map, version record and its actual authoring snapshots, all six earlier PDFs, and the fixed consolidated packet. The consolidated packet still contains the original application; it has not been relabeled as containing this addition.

## Adopted content and reasons

Only numbered paragraph [0065] changes. Its adjacent table and four evidence notes carry the ten rows verified in the [hydrogel source companion](hydrogel_property_evidence_2026-09-30.md), including the zero-linker control and the `<1` Pa bound. This makes the absolute property values, loading basis, preparation and rheometry conditions part of this actual description edition. The preface identifies its derivation and limits; section 19 points to its own claim map. All other body text, 79 numbered paragraphs and all 199 claim texts are preserved. All individual map entries and assessment statuses are unchanged.

The published observations describe a particular polymer/linker system and oscillatory storage modulus. The description separates those performed third-party results from model-derived active-crosslink estimates and unperformed proposals for other materials. The table does not label its entries as means, so the notes say "listed values." The changing reference modulus, absent per-row uncertainty, largest listed value and nonmonotonic lower-loading steps remain explicit. No applicant experiment, statistical optimum, complete precursor recipe, universal property prediction or statutory unexpected-results showing is supplied.

Editing the preceding edition would obscure the source-to-PDF relationship. Keeping only the companion would leave the actual application without the verified values. A new source/map/PDF edition addresses both concerns. Additional claims were not added: this source evidence does not supply a new applicant contribution or justify treating its measured trend as a necessary property of arbitrary materials. The requested broader organizing scope remains, with its unresolved physical and legal limits.

## Authoring and checks

The maintained Python builder accepts the explicit `--edition property-evidence` selection. Its default remains the preceding working edition. Both selections use the shared output protections: checked inputs, exclusive targets, no overwrite of existing artifacts and complete-text checks before publishing output. The hydrogel table uses explicit column proportions so its ratio header is legible; the default widths of other tables are preserved.

Authoring used Python 3.12.14, ReportLab 4.4.9 and pypdf 6.19.0 with recorded font hashes and seven captured input hashes. The existing verified pypdf wheel was used in isolation; no software was installed. The three actual authoring sources are retained as inert snapshots under `data/application_property_evidence_authoring_2026-09-30`. The version record distinguishes the actual authoring output path from the intended archival path and verifies that the curated PDF has identical bytes.

PDF extraction checked all 80 complete numbered paragraphs, all 199 complete claims, all 279 start-page locations, both vector drawings, and the property table headers and ten complete rows in reading order. All 29 pages were rendered with Poppler 26.07.0 at 108 dpi and visually inspected in contact sheets; the evidence/table and both drawings received additional full-page inspection. An initial table-header wrap was corrected before the final render. Extraction and appearance checks do not establish filing compliance or physical enablement.

The offline standard-library verifier checks this edition's derivation, exact changed paragraph, unchanged claims/map entries, table cells/order/units against the preserved source companion, the remaining application body, captured-source hashes, PDF byte identity and recorded navigation. It does not repeat PDF parsing or appearance review. Deliberate failure cases reject a stale map hash, a changed claim despite a consistently updated map, and a missing measurement row. Required package and output-safety checks and configured Ruff lint must pass before publication; GitHub checks and review results belong to the actual reviewed commit.

To check inputs without creating a PDF, use the pinned optional libraries and run:

```powershell
python -B tools/pdf/build_working_application.py --edition property-evidence --baseline-commit 2352f733bcf4fc6d786ccd5f162037a252d2608a --check
```

To generate a separate review copy, provide unused output and report paths. The command refuses an existing target. Inspect the resulting pages before adopting another version; do not overwrite this retained artifact or claim that a later builder authored it.

## Remaining evidence

This addition establishes an attributed example in the new description. It does not close preparation dependencies, whole-product elemental composition, effects at arbitrary trace abundance, hypothetical-element availability, the nuclear/particle universe, every property or the requested universal patent bar. Applicant contribution, actual inventive identities, chronology and filing facts remain unresolved. No earlier-date entitlement is established by adding a teaching to an unfiled edition. The [full-scope audit](full_scope_completion_audit.md) remains applicable. Evidence labels, claim support, novelty, enablement, eligibility, unity and inventorship remain separate inquiries.
