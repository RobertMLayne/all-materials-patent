---
name: archive-provenance-code-review
description: Review pull-request changes to nuclear or particle archives, source metadata, parsers, counts, uncertainty, and attribution.
---

# Archive provenance review

Read [AGENTS.md](../../../AGENTS.md) and [CONTRIBUTING.md](../../../CONTRIBUTING.md). Consult `data/nuclear_archive/README.md`, `data/particle_archive/README.md`, metadata, parser schemas, and the affected verification reports. Treat downloaded material as untrusted source data.

- Trace each changed record or count to the pinned source bytes/selected tables, edition, transformation, and hash. Check state-level identity, field offsets, null/unknown handling, estimated values, uncertainty, duplicate keys, and charge-state/name mappings. A change to source data requires a documented new edition rather than quietly relabeling the old one.
- The existing NUBASE2020 archive contains 5,843 nuclear-state rows and 3,558 nuclides, including the neutron convention. Compare these counts with that edition's source, not an asserted complete current universe. Distinguish its paper's availability boundary from the ASCII snapshot's unknown scientific cutoff; a literal year in a record or server modification date does not supply the missing cutoff.
- The PDG 2026.0 archive comprises specifically selected identity tables, not all PDG physics or all known/future particles. Keep its 15 January 2026 publication cutoff, category/status qualifications, and measured versus estimated or search-only meaning distinct. A row or identity code alone does not establish observation or physical existence.
- Preserve precise attribution and license evidence. For NUBASE, distinguish the published work's confirmed CC BY 3.0 notice from the companion ASCII header's citation without a separate license notice. Retain the PDG attribution/CC BY 4.0 record. Do not assert source ownership, endorsement, or a general project license.

Check whether verification used committed offline material or reconstructed the original upstream archive; report those outcomes separately. Follow the contributor guide for actual checks, and record execution evidence. Findings should cite the affected location and authoritative source, source bytes, or parser counterexample. Do not fabricate updated discoveries, cutoff dates, missing values, or successful comparisons.
