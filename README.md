# Materials disclosure research package

This package contains a draft materials disclosure, candidate claims, filing analysis, and exact composition-range tools. It explores broad elemental composition descriptions while explicitly preserving the difference between a mathematical description and an enabled physical material.

**No patent application filing, granted patent, or universal bar to later materials patents is asserted by this package.** The 199 candidate claims have not received claim-specific novelty assessment, and full-scope physical enablement remains unestablished. No applicant experiments or successful preparation results are fabricated or implied.

Draft preparation date: **29 September 2026**. Dates printed inside the documents are preparation or source-check dates, not filing dates or public-availability dates. Any publication record must use the actual public Git commit/release and evidence of when it became publicly accessible. A pre-existing private commit timestamp alone does not establish public availability. This README assigns no earlier publication date.

## Read the documents

| Document | Readable PDF | Editable source |
| --- | --- | --- |
| Application working draft - 27 review pages, 80 numbered paragraphs, 199 complete candidate claims | [Application PDF](documents/pdf/provisional_application_draft.pdf) | [Application Markdown](documents/provisional_application_draft.md) |
| Provisional/PCT filing review memorandum - five review pages | [Filing memorandum PDF](documents/pdf/provisional_filing_strategy.pdf) | [Filing memorandum Markdown](documents/provisional_filing_strategy.md) |
| Earlier defensive-disclosure blueprint - retained as an earlier planning artifact | [Blueprint PDF](documents/pdf/pct_defensive_disclosure_blueprint.pdf) | [Blueprint Markdown](documents/pct_defensive_disclosure_blueprint.md) |

The completed application and companion memorandum are the current working draft; the earlier blueprint is retained for provenance. Review page counts are not PCT chargeable-sheet determinations. All supplied PDFs were visually reviewed before packaging; this repository's automated checks do not replace that review.

## Data, calculations, and drawings

- [Entity register](data/entity_register.json) and [register notes](data/entity_register_notes.md): 138 elemental labels, comprising 118 recognized elements and 20 hypothetical placeholders, plus 17 particle categories under an explicit counting convention.
- [Claim support map](data/claim_support_map.json): all 199 claims mapped to numbered textual locations, with textual support distinguished from unresolved physical enablement. Every claim is marked novelty-unassessed.
- [Composition range model](range_model/composition_range_model.json): continuous real domains, all-rational domains, an optional denominator-10^19 grid, decimal endpoint intervals, and exact counts.
- [Exact numeric examples](range_model/numeric_examples.json), [range generator and verifier](range_model/composition_ranges.py), and [recorded verification results](range_model/verification_report.json).
- [Composition simplex drawing](documents/drawings/composition_simplex.svg) and [material-record sequence drawing](documents/drawings/material_record_sequence.svg).

The executable range model uses a minimum positive coordinate of 10^-19. The manuscript also defines broader strictly positive symbolic domains below that floor. The 27 range-verifier groups do not establish exhaustive test coverage of those broader domains. A fixed denominator-10^19 grid excludes fractions such as 1/3; the distinct all-rational domain includes them. The requested 10^-16% through 10^-15% interval corresponds to fractions 10^-18 through 10^-17, with 91 inclusive fixed-grid points and 90 elementary bins.

Elemental labels do not supply structures, preparation methods, stability, availability, measurement precision, or properties. Hypothetical element and particle labels remain hypothetical. A finite category register is not an exhaustive catalog of future physical entities. Source editions and their historical limits remain attached to the supplied documents and registers.

## Verify the package

Use Python 3.12 and its standard library from the repository root; no package installation is needed:

```console
python verify_package.py
```

This checks [SHA-256 integrity records](integrity_manifest.json), the expected artifact inventory, paragraph and claim numbering, claim dependencies, registry counts and status, local Markdown links, and exact regeneration of the mathematical JSON artifacts in memory. It also reruns the 27 finite range-verifier groups and compares their result with the recorded report. It writes no repository files.

Use `python verify_package.py --self-test` to also check ten deliberate failure cases, including altered/missing artifacts, unreviewed extra files, report drift, unsafe paths, and changed evidence status. This optional mode creates and removes temporary copies under the ignored `generated_reports/` directory; it leaves the supplied artifacts unchanged.

To run only the mathematical verifier, use its `verify` subcommand:

```console
python range_model/composition_ranges.py verify
```

To inspect a bounded example without claiming an exhaustive enumeration:

```console
python range_model/composition_ranges.py generate --support 1,6,8 --domain rational --max-denominator 3 --limit 3
```

Exact arithmetic uses integer fractions. Terminating decimal strings are exact; nonterminating decimal fields are null and retain an exact rational value. Reproducibility here concerns the mathematical JSON and verification result. The PDFs are preserved byte-for-byte and checksum-checked, not rebuilt by the standard-library verifier.

The manifest intentionally excludes itself, the regenerated range verification report, optional local verification reports, Python caches, and Git internals. The range report is instead compared with a fresh verifier result. Checksums identify consistency with this package's manifest; they are not a digital signature, trusted timestamp, patent filing receipt, or legal opinion.

## Automated verification

[The workflow](.github/workflows/verify.yml) runs on pushes, pull requests, and manual dispatch with Python 3.12, a ten-minute job limit, read-only repository permissions, and cancellation of superseded runs for the same workflow/ref. It uses official actions pinned to the verified [checkout v4.2.2 commit](https://github.com/actions/checkout/commit/11bd71901bbe5b1630ceea73d27597364c9af683) and [setup-python v5.6.0 commit](https://github.com/actions/setup-python/commit/a26af69be951a213d495a4c3e4e4022e16d87065). Workflow controls follow [GitHub's syntax documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).

Local verification is distinct from a completed GitHub Actions run. Review the actual workflow status after publication. The workflow does not deploy, publish, file an application, or commit changes.

## Continuing the work

[AGENTS.md](AGENTS.md) records preservation rules and pending technical work. The substantive next work is to identify actual inventive contributions and supported material embodiments, document reproducible preparation and characterization, assess claim-specific novelty and support, and preserve any real filing or publication evidence. A more detailed numerical list does not resolve those experimental and legal questions.

## License

No license grant is included in this package. No `LICENSE` file is supplied. This statement does not assert ownership of attributed third-party source material.
