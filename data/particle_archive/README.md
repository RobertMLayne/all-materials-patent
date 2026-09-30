# PDG 2026.0 particle identity archive

Prepared and checked 30 September 2026 UTC. This is an edition-qualified identity/name archive for the materials disclosure research package. It does not establish that every listed entity is discovered, preparable or a stable material constituent. No patent enablement assessment is made.

The archive was extracted offline from the official [pdg-2026.0.sqlite download](https://pdg.lbl.gov/2026/api/pdg-2026.0.sqlite), selected through the [PDG 2026 API download index](https://pdg.lbl.gov/2026/api/index.html). The source database is 25,751,552 bytes, with SHA-256 `40dc2587d9ae912d26fafb6b41f300f341d2a1f4bd620ff5b5f03827c39453fe`. Its stored schema version is `0.3`, edition is `2026`, and release timestamp is `2026-05-30 13:41:24 PDT`. The official publisher gives **15 January 2026** as the [Listings/Summary Tables cutoff](https://pdg.lbl.gov/2026/listings/contents_listings.html). These dates have separate meanings; the retrieval did not advance the source cutoff.

The successful download was observed at `2026-09-30T02:30:54Z`. Server metadata reported Last-Modified `Mon, 01 Jun 2026 18:25:28 GMT`. Those fields are preserved as download observations, not proof of a patent priority date or an independently trusted timestamp. The database's internal release metadata is retained without rewriting it to match the server header.

## Included records

| SQLite source table | Selection | Exported rows | Meaning |
| --- | --- | ---: | --- |
| `pdgparticle` | Every row and source column | 1,170 | Charge-state identity rows, with original primary keys, PDG identifiers, Monte Carlo IDs, names, charge, conjugation type and quantum-number strings |
| `pdgid` | Every `PART` and `SRCH` row | 450 | 439 particle groups and 11 search groups; includes groups with no charge-state row |
| `pdgitem` | Every row and source column | 3,270 | Names, aliases, generic names, shortcuts, lists and textual entries, retaining their source types |
| `pdgitem_map` | Every row and source column | 1,341 | Source name/alias/set mappings, retaining source and target IDs |
| `pdgdoc` | Every row and source column | 71 | Original code definitions, including types, flags and conjugation codes |
| `pdginfo` | Every row and source column | 10 | Source metadata and citation, retained in the archive preamble |

The [normalized JSON](pdg2026_identity_archive.json) stores these source columns in deterministic primary-key order. [Metadata](pdg2026_identity_metadata.json) records schemas, selections, source metadata, download evidence, counts, nulls, known ambiguities and scope limits. “Complete” means complete for these selections from the pinned database; it does not mean every theoretical particle, nuclear state, excitation or property is represented.

There are 438 distinct PDG identity groups referenced by the 1,170 charge-state rows. Twelve of the 450 exported particle/search groups have no such row: all 11 search groups and the source `f_0(2330)` group. They remain in the export. Generic names, decay texts and aliases are separate table entries and are not counted as new physical species.

## Scientific interpretation and original unknowns

No discovery/existence-status column is provided in these identity tables, and **zero physical-existence assessments** were performed. The database-level `status = production` describes the database release. `PART`, `SRCH`, category flags, Monte Carlo IDs, spin strings and conjugation codes are not discovery certificates. For example, the source includes a graviton identity row of type `PART` and category `G`; inclusion does not establish its discovery.

`cc_type` describes particle, antiparticle or self-conjugate state. The original codebook is included. This classification does not state whether a particle has been observed. PDG identifiers, Monte Carlo IDs and source row IDs are different identifiers and retain their distinct fields.

SQLite `NULL` values remain JSON `null`; literal question marks, blanks, compound strings and source quantum-number values remain unchanged. There are 554 null Monte Carlo IDs and 17 null spin fields. A known source ambiguity is deliberately retained: two rows share the name `P_c_cbar(4312)+` and name-item ID 1593 while referencing distinct PDG identifiers `B185` and `B205` and different isospin strings. No correction or deduplication by name was attempted. Join through numeric source primary/foreign keys and edition-qualified identifiers, following the [PDG schema documentation](https://pdgapi.lbl.gov/doc/schema.html).

This selection omits available measurements, masses/lifetimes, property uncertainties and limits, decays, references, footnotes, listing text and historical Summary Table editions. Those data require a separate extraction and interpretation. The upstream [API development-status page](https://pdgapi.lbl.gov/doc/status.html) also identifies inaccessible fit/correlation information, conservation-law data, some headers/notes, incomplete parentheses in some text values and missing numerical values for some limits. The identity archive does not fill those omissions or convert a limit into a discovery.

## Attribution and reuse

Source: **F. Takahashi et al. (Particle Data Group), Int. J. Mod. Phys. A 41, 2630011 (2026)**. The original citation is retained in source metadata; see the [official 2026 author/citation page](https://pdg.lbl.gov/2026/html/authors_2026.html).

The source database explicitly records `CC BY 4.0`; PDG's [license documentation](https://pdgapi.lbl.gov/doc/schema.html#license) identifies that license for editions starting in 2024. Source-derived records here are provided with attribution under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). Changes consist of selecting identity/name/mapping/code tables and serializing them into deterministic UTF-8 JSON. Source values were not scientifically reclassified, corrected or deduplicated. This attribution applies to the PDG-derived data.

## Reproduce and verify

The [extraction/verification script](extract_pdg_identities.py) requires Python 3.12 and its standard library, with no package or global installation. Its download command performs one versioned SQLite download. It uses no bulk REST requests, consistent with [PDG's terms](https://pdgapi.lbl.gov/doc/restapi.html#terms-of-use).

Run the offline archive checks from this directory:

```console
python extract_pdg_identities.py verify
```

For the following reproduction commands, first change to the **repository root**. The sibling `../materials-archive-scratch/` holds the downloaded database, observation and regenerated output outside the repository; it is not a directory inside this archive. Replace it with another outside-repository location if needed:

```console
python data/particle_archive/extract_pdg_identities.py download --destination ../materials-archive-scratch/pdg-2026.0.sqlite --observation ../materials-archive-scratch/download_observation.json
python data/particle_archive/extract_pdg_identities.py extract --database ../materials-archive-scratch/pdg-2026.0.sqlite --download-observation ../materials-archive-scratch/download_observation.json --output-directory ../materials-archive-scratch/regenerated
python data/particle_archive/extract_pdg_identities.py verify --database ../materials-archive-scratch/pdg-2026.0.sqlite
```

The downloader requires distinct database, partial and observation paths, refuses existing output files, and preserves an unexpected partial download for inspection. Publication uses an exclusive same-filesystem hard link after verifying the bytes; a destination created by another writer is preserved. A filesystem without suitable hard-link support causes a safe failure, with the verified partial retained for inspection. The extractor refuses a database with a different size, hash, edition, schema or license. A changed upstream release needs explicit review rather than a silent regeneration. The raw SQLite file remains scratch material and is not part of this text archive.

[Recorded verification](verification_report.json) passed complete selected-table comparison against the pinned SQLite file, including every selected source row/column, null and repeated name. The source passed SQLite integrity and foreign-key checks. Exported references, row counts, source schema, deterministic bytes and source/derived hashes were also checked. Checksums demonstrate consistency with the recorded source snapshot; they do not prove scientific existence, legal effect or a trusted publication timestamp.

The [additional verification record](adversarial_verification_report.json) records six successful checks: import/offline verification with network requests disabled; rejection of an edited spin, a removed charge-state row, removed search groups and an unsupported discovery assertion; and rejection of an edited/rehashed spin through comparison against the raw source. This last check confirms the distinction between internal archive consistency and agreement with the source database.
