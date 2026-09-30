# Dated NUBASE2020 nuclear state archive

This archive preserves the specific official ASCII table identified by `source_metadata.json`. It accounts for all 5,843 state rows in that snapshot, including 3,558 distinct `(A,Z)` pairs and the free neutron at `Z=0`. It supplies concrete isotope and nuclear-state identifiers for the disclosure framework without assuming that every listed state is observed, stable, synthesizable, or usable in a material.

## Source and chronology

Credit the [NUBASE2020 evaluation by Kondev and colleagues](https://doi.org/10.1088/1674-1137/abddae), Chinese Physics C 45, 030001 (2021). The original data came from the [official IAEA dissemination site](https://www-nds.iaea.org/amdc/). The publisher's CC BY 3.0 notice and the companion file's attribution distinction are documented in `license_attribution.md`.

Keep three dates separate: the paper's stated experimental-data availability boundary of October 30, 2020; the server's November 11, 2022 Last-Modified header; and this download's September 30, 2026 UTC response date. One literal discovery-year field is `2021`: source line 2442, byte offset 318061, columns 115-118, for `NUBASE2020:Z047:A127:S2`. Its complete row is retained in `archive_counts.json`. A discovery year does not itself reveal when information reached the evaluators. No new scientific cutoff is inferred from any of these dates.

## Preserved files

| File | Role |
| --- | --- |
| `nubase_4.mas20.txt` | Original 761,906 ASCII bytes, unchanged. |
| `schema_header.txt` | Original 25 header lines, including the source fixed-width schema. |
| `column_schema.json` | One-based inclusive columns, documented fields, unassigned gaps, and preservation policies. |
| `source_metadata.json` | Edition, URLs, citation, chronology, license evidence, original hash, and limits. |
| `parse_nubase.py` | Portable standard-library parser; no network requests and no parsing on import. |
| `verify_nuclear_archive.py` | Independent byte, column, identity, property, sample, and deliberate-defect checks. |
| `archive_counts.json` | Counts, source-index distributions, late-year row, and ambiguous-token counts. |
| `verification_report.json` | Actual offline verification result. |
| `portability_report.json` | Verification with normalized JSON omitted, plus import and report-identity checks. |
| `portable_bundle_manifest.json` | Required portable files and hashes; optional normalized JSON is recorded separately. |
| `nuclear_states.json` | Optional generated normalized view; 18,118,327 bytes. It may be omitted from a distribution. |

The source SHA-256 is `1585a5eea86c5e17e90307c7e6e786d060049c4039e392a261ff6db977df9859`. The parser rejects a different input hash until that new snapshot is reviewed deliberately.

## Conservative normalization

Each state keeps the source's `(Z,A,state index)`, suffix, line number, byte offset, complete original row, and every raw fixed-width field. Gaps are retained. Two rows extend beyond documented column 209; their trailing content is kept without assigning it an invented meaning. Short rows retain actual slices rather than fabricated padding.

Parsed decimal values remain strings. Numeric values, operators, uncertainties, and units occupy separate fields. Unrecognized text stays raw. The nominal half-life uncertainty columns actually contain 299 auxiliary bounds and two isospin annotations; those are not treated as numerical error bars. Sixteen excitation fields contain `non-exist`, preserved as the source's token. Compact decay/abundance uncertainty tokens are not automatically rescaled.

The `#` marker is kept at the property level. It must not determine whether a nucleus or state was observed. State indices and suffixes also remain edition-specific: some indices normally associated with levels or resonances can represent additional isomers. No blanket state-kind classification is inferred.

## Offline verification

From any working directory, run the verifier by its path with Python 3:

```text
python path/to/nuclear_archive/verify_nuclear_archive.py
```

If `nuclear_states.json` is present, verification reads it. If absent, the parser constructs the same complete view in memory and the independently implemented checks compare it against original source bytes and column documentation. This mode does not write the large normalized file or download anything. The verifier writes its deterministic report next to the archived files.

To regenerate the optional normalized JSON explicitly:

```text
python path/to/nuclear_archive/parse_nubase.py
```

The checks account for every source row, reconstruct every original character from field slices, confirm identity/counts and byte locations, and test representative difficult cases. Six deliberate defects must be rejected. Passing proves archive fidelity within that scope; it does not establish current nuclear-data completeness, isotope availability, physical preparation, material properties, patent enablement, or prior-art effect.
