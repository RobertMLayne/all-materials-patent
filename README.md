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

The application and companion memorandum remain working drafts; the earlier blueprint is retained for provenance. Review page counts are not PCT chargeable-sheet determinations. All supplied PDFs were visually reviewed before packaging; this repository's automated checks do not replace that review.

The **30 September 2026 extension** adds an [unrestricted technical supplement](documents/technical_scope_supplement.md), [full-scope completion audit](documents/full_scope_completion_audit.md), and [source-supported reference entries](documents/reference_entry_support.md). Read the [current-status addendum](documents/current_status_addendum.md) alongside the older filing memorandum: the package is publicly accessible, and the older memorandum's statement about publication is historical. The [access observation](data/publication_observation.json) records an observed repository version without certifying its earliest public-availability date. The original 80 paragraphs, 199 candidate claims, and three review PDFs are preserved unchanged by this extension.

## Data, calculations, and drawings

- [Entity register](data/entity_register.json) and [register notes](data/entity_register_notes.md): 138 elemental labels, comprising 118 recognized elements and 20 hypothetical placeholders, plus 17 particle categories under an explicit counting convention.
- [Claim support map](data/claim_support_map.json): all 199 claims mapped to numbered textual locations, with textual support distinguished from unresolved physical enablement. Every claim is marked novelty-unassessed.
- [Composition range model](range_model/composition_range_model.json): continuous real domains, all-rational domains, an optional denominator-10^19 grid, decimal endpoint intervals, and exact counts.
- [Exact numeric examples](range_model/numeric_examples.json), [range generator and verifier](range_model/composition_ranges.py), and [recorded verification results](range_model/verification_report.json).
- [Unrestricted rational model](range_model/unrestricted_composition_model.json), [implementation](range_model/unrestricted_compositions.py), [examples](range_model/unrestricted_numeric_examples.json), and [verification report](range_model/unrestricted_verification_report.json): no minimum positive fraction or domain-wide denominator cap; exact interval feasibility and finite atom/conditional partition accounting.
- [Independent numerical checks](range_model/independent_unrestricted_checks.py) and [their recorded result](range_model/independent_unrestricted_report.json), plus [trace-sampling calculations](range_model/trace_sampling_calculations.py) and [calculated examples](range_model/trace_sampling_report.json).
- [NUBASE2020 archive](data/nuclear_archive/README.md): all 5,843 nuclear-state records and source bytes in the downloaded official ASCII table, covering 3,558 distinct nuclides. Its schema, provenance, attribution, parser, and independent verifier are included. A large generated JSON view is reconstructed in memory rather than committed.
- [PDG 2026.0 identity archive](data/particle_archive/README.md): 1,170 charge-state rows, 450 particle/search groups, 3,270 name entries, and 1,341 mappings from explicitly identified tables. The selected identity JSON and provenance are included; the 25 MB upstream SQLite database is an optional separately downloaded source for full regeneration.
- [Composition simplex drawing](documents/drawings/composition_simplex.svg) and [material-record sequence drawing](documents/drawings/material_record_sequence.svg).

The original executable range model retains its minimum positive coordinate of 10^-19. The new unrestricted module implements the manuscript's broader strictly positive **rational** domain without that floor, including fractions such as 1/3 and 10^-100. An infinite enumerator and a finite exported sample are different: CLI denominator and output limits restrict a particular export. Irrational real coordinates remain a symbolic domain, not an exhaustively enumerable table. Neither module proves physical preparation. The requested 10^-16% through 10^-15% interval corresponds to fractions 10^-18 through 10^-17, with 91 inclusive points and 90 elementary bins on the optional denominator-10^19 grid.

Elemental labels do not supply structures, preparation methods, stability, availability, measurement precision, or properties. Hypothetical labels remain hypothetical. The new archives account for their specified source records, not every nuclear state or future physical entity. A table entry, estimated value, search code, or particle category is not automatically evidence of physical existence. NUBASE's paper boundary and ASCII snapshot dates are recorded separately; PDG's publication cutoff is 15 January 2026. Source unknowns and qualifications are retained.

## Verify the package

Use Python 3.12 and its standard library from the repository root; no package installation is needed:

```console
python verify_package.py
```

This checks [SHA-256 integrity records](integrity_manifest.json), the expected artifact inventory, paragraph and claim numbering, claim dependencies, registry counts and status, local Markdown links, and exact regeneration of the mathematical JSON artifacts in memory. It reruns the original 27 finite groups, the unrestricted module's finite checks, independent numerical checks, and trace-sampling calculations. It checks the nuclear source reconstruction and selected particle archive offline; the particle archive's documented original full-SQLite comparison is distinct from that offline check. It writes no repository files.

Use `python verify_package.py --self-test` to also check ten baseline and four extension deliberate failure cases, including altered/missing artifacts, unreviewed extra files, report drift, unsafe paths, and unsupported observation/discovery status. This optional mode creates and removes temporary copies under the ignored `generated_reports/` directory; it leaves the supplied artifacts unchanged and checks fixture import isolation.

To run only the mathematical verifier, use its `verify` subcommand:

```console
python range_model/composition_ranges.py verify
```

To inspect bounded examples without claiming an exhaustive enumeration:

```console
python range_model/composition_ranges.py generate --support 1,6,8 --domain rational --max-denominator 3 --limit 3
python range_model/unrestricted_compositions.py generate --support 1,6,8 --max-denominator 3 --limit 3
```

Exact arithmetic uses integer fractions. Terminating decimal strings are exact; nonterminating decimal fields are null and retain an exact rational value. Reproducibility here concerns the mathematical JSON and verification result. The PDFs are preserved byte-for-byte and checksum-checked, not rebuilt by the standard-library verifier.

The manifest intentionally excludes itself, the original regenerated range verification report, optional local verification reports, Python caches, and Git internals. The original range report is instead compared with a fresh verifier result; the new reviewed reports are both hashed and checked as applicable. Checksums identify consistency with this package's manifest; they are not a digital signature, trusted timestamp, patent filing receipt, or legal opinion.

## Automated verification

[The workflow](.github/workflows/verify.yml) runs on pushes, pull requests, and manual dispatch with Python 3.12, a ten-minute job limit, read-only repository permissions, and cancellation of superseded runs for the same workflow/ref. It uses official actions pinned to the verified [checkout v4.2.2 commit](https://github.com/actions/checkout/commit/11bd71901bbe5b1630ceea73d27597364c9af683) and [setup-python v5.6.0 commit](https://github.com/actions/setup-python/commit/a26af69be951a213d495a4c3e4e4022e16d87065). Workflow controls follow [GitHub's syntax documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).

Local verification is distinct from a completed GitHub Actions run. Review the actual workflow status after publication. The workflow does not deploy, publish, file an application, or commit changes.

## Continuing the work

[AGENTS.md](AGENTS.md) records preservation rules and pending technical work. The substantive next work is to identify actual inventive contributions and supported material embodiments, document reproducible preparation and characterization, assess claim-specific novelty and support, and preserve any real filing or publication evidence. A more detailed numerical list does not resolve those experimental and legal questions.

## License

No general license grant or `LICENSE` file is supplied for this project's draft or code. Third-party data retain their own provenance and attribution: see the [nuclear archive license evidence](data/nuclear_archive/license_attribution.md) and [PDG archive attribution](data/particle_archive/README.md). The NUBASE published work's confirmed CC BY 3.0 notice is distinguished from the companion ASCII header, which contains a citation but no separate license notice. The PDG archive records CC BY 4.0. No third-party ownership or endorsement is asserted.
