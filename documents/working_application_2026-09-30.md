# Working application edition - 30 September 2026

This is a **prospective, unfiled working application edition**, derived from repository baseline `9cbd8323b2546088c19225143dd23fa38577e4b1`. It incorporates reviewed accounting and positive-target clarifications into the application description and claim annex. The [working source](provisional_application_working_2026-09-30.md), [28-page review PDF](pdf/provisional_application_working_2026-09-30.pdf), [edition-specific textual map](../data/claim_support_map_working_2026-09-30.json) and [version record](../data/working_application_2026-09-30.json) refer to this edition.

The original [29 September source](provisional_application_draft.md), its [historical map](../data/claim_support_map.json), the three original PDFs, the 66-page consolidated edition and the 795-page identity annex remain byte-for-byte preserved. The consolidated edition still contains the original application. Preparation and repository dates do not establish filing, priority or earliest public availability.

## What changed and why

A conditional isotope distribution defined by atom counts must not silently become a conditional mass distribution. A preliminary witness that permits zeros must not silently satisfy a parent method requiring a strictly positive target. Incorporating the [reviewed proposals](proposed_claim_clarifications.md) also exposed the generic composition-coordinate ambiguity in claim 147 and the distinction between mass and atom-count denominators.

| Location | Adopted relationship | Purpose and remaining limit |
| --- | --- | --- |
| [0008] | Rational atomic and mass vectors use their identified bases. | The atomic vector's primitive denominator determines atom-count compatibility. A rational mass vector alone does not establish that condition. |
| [0010]-[0011], claim 147 | Generic `x_i` equals atomic `a_i` or mass `w_i` on the selected basis; conversions distinguish them. | Prevents treating a mass coordinate as atomic. Effective masses must be positive, finite, qualified and use a consistent allocation/unit convention. |
| [0018], [0031], abstract | `D = 10^19` is the decimal composition accounting denominator. | Retains the grid while distinguishing its numerators from specimen atom inventory `N`. |
| [0047], claim 169 | Conditional `y` remains atom-count based. Atomic and mass branches use their own formulas; mass sums include populated entries only. | Zero-population entries need no fabricated mass. Unknown populated-state masses prevent mass conversion; the atomic alternative retains no such requirement. |
| [0030], claim 191 | Preliminary nonnegative witness and accepted positive target are distinct. | A zero-containing preliminary vector requires a separate positive witness before target assignment. |
| [0030], claim 192 | Preserve local epsilon and raise every lower bound with `max(L_i, epsilon)`. | Handles positivity without a global floor. Dependency `192 -> 191 -> 186` and every parent operation remain. |
| [0031], claim 193 | Positive integer bounds, `sum(n_i) = D` and `x_i = n_i/D` are explicit. | Retains `193 -> 186` without importing claim 191. Grid rejection does not reject unrestricted rationals. |
| [0032], [0075] | Rejected requests and partial numerical outputs differ from completed positive-target records. | Code does not supply all structure, preparation, measurement, property and source fields or every operation of claim 186. |
| Section 19 and version notes | The map identifies this source; isotope index `a` differs from atomic fraction `a_i`. | Textual locations do not decide physical enablement, original legal support or earlier entitlement. |

Exactly **nine numbered paragraphs and five claims** changed. All **80 paragraph identifiers and 199 claim identifiers** remain. Claims other than **147, 169, 191, 192 and 193** retain their original text, including the unary candidate, every constituent count 2-138, closed-inventory limitations, structures, particles and conditional-property scenarios. Both composition alternatives, recognized/hypothetical labels, unrestricted positive rationals, symbolic reals, the separate grid and below-grid targets remain.

## Calculations, review and preservation

The [exact checker](../range_model/claim_clarification_checks.py) and [recorded report](../range_model/claim_clarification_report.json) retain 3,615 epsilon-box cases, 1,318 feasible boxes, 21,930 small integer-grid cases, ten boundaries and three unknown-mass cases. Two additional **CALCULATED anonymous** cases are reported separately:

- The existing toy atomic vector `(4/5, 1/5)` converts to mass vector `(2/3, 1/3)` using qualified toy masses `(3/2, 3)`. Incorrectly using the mass vector as atomic instead produces `(1/2, 1/2)`.
- With toy masses `(1, 2)`, mass vector `(1/2, 1/2)` converts to atomic vector `(2/3, 1/3)`. A two-atom inventory is incompatible; a three-atom inventory has counts `(2, 1)`. The atomic denominator controls that test.

These are arithmetic examples with arbitrary mass units, not measured isotope masses, synthesis instructions or verified specimens. Both production composition algorithms remain unchanged. Independent prose/claim and mathematical reviews checked dependencies and preserved scope; these reviews did not decide novelty or physical enablement.

The new PDF prints all 80 paragraphs and all 199 complete candidate claims and renders both drawings as vectors. Authoring extraction checked every paragraph and claim's displayed wording. The version record preserves actual source hashes, ReportLab 4.4.9, pypdf 6.19.0, installed-font hashes and paragraph/claim start pages. Retained code snapshots record the implementation actually used. The optional builder reuses the output safeguards, refuses existing outputs and neither amends sources nor installs tools.

The curated record identifies the preserved PDF and the ignored authoring-output path from which its bytes were copied. The captured builder snapshot labeled its intended archival destination in the initial raw report; that report is retained locally, and curation verifies the bytes at both paths. The maintained builder now reports its actual output path separately from the intended archival path. This subsequent reporting correction does not rewrite the earlier code snapshot or PDF.

Ordinary `python -B verify_package.py` remains offline and standard-library-only. It checks source/map identity, actual changed paragraph/claim sets, adoption of the reviewed isotope/target wording, unchanged support statuses, captured-source/PDF hashes and recorded navigation bounds. It does not parse PDFs or repeat visual review. `--self-test` includes a stale source-map failure and an incorrect isotope basis even after a consistent map update. The PDF's recorded visual review is a separate completed authoring observation.

## Decisions and next substantive work

A separate edition preserves which wording each earlier source, map and PDF contains. Rebuilding the 66/795-page historical packet would replace a version with existing provenance. Another proposal alone would leave the application unchanged. This edition adopts the corrections directly and keeps each earlier artifact identifiable.

Adoption into a prospective unfiled source does not establish support in an earlier application. If an earlier filing is supplied, each relied-on limitation and combination must be assessed against that actual filed version. Mathematical correctness does not backfill an earlier disclosure. [USPTO written-description guidance, MPEP 2163](https://www.uspto.gov/web/offices/pac/mpep/s2163.html), [USPTO provisional filing guidance](https://www.uspto.gov/patents/basics/apply/provisional-application).

The objective remains a broad defensive materials disclosure with the PCT route retained. This edition improves drafting consistency; the universal patent bar remains unestablished. The [full-scope audit](full_scope_completion_audit.md) and [evidence-intake instructions](applicant_evidence_intake.md) retain the unresolved work: actual technical contribution and contributor facts, specific preparation/characterization support, justified generalizations, property evidence or qualified models, claim-specific legal comparisons and filing facts. No private participant information is added to this public edition. No filing, novelty, physical enablement or legal coverage is asserted.

## Optional authoring

Reuse an environment with [the pinned optional requirements](../tools/pdf/requirements-pdf.txt); new installation is an interactive user-controlled step. The [builder](../tools/pdf/build_working_application.py) uses installed Arial, DejaVu Sans or Liberation Sans and a checked SVG vocabulary for the two drawings. It is not a general SVG renderer. Font files are not redistributed.

```console
python -B tools/pdf/build_working_application.py --package-root . --baseline-commit 9cbd8323b2546088c19225143dd23fa38577e4b1 --check
python -B tools/pdf/build_working_application.py --package-root . --baseline-commit 9cbd8323b2546088c19225143dd23fa38577e4b1 --output generated_reports/pdf/working_application_2026-09-30.pdf --report generated_reports/pdf/working_application_2026-09-30.json
```

The baseline identifies derivation; input hashes identify captured bytes. Outputs are exclusive and stay under ignored `generated_reports/` inside the package or an explicit external destination. Routine verification does not regenerate PDFs. Source or snapshot changes require a deliberately reviewed version/provenance update.
