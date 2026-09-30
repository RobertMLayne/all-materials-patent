# Alloy comparison against working claims 1, 4, 5 and 163

Prepared 30 September 2026. Status: preliminary source-to-limitation comparison, with claim construction, statutory dates and outcomes open. This is attributed third-party evidence, not an applicant experiment or a finding that any candidate claim is patentable. It addresses concrete composition and impurity questions left open in the [alloy reference family](reference_entry_support.md#alloy-reference-family). The original reference entry, application and reviewed PDFs remain unchanged.

## Exact candidate version

This chart uses the [30 September working application](provisional_application_working_2026-09-30.md), source SHA-256 `1b508938a31b1e7a19b59b3f06edfd21e8378d6ba9e375551250ceb79a8fd198`, at repository baseline `a85536a94d4eb633c098d0299824e73dca55e3e4`.

- Claim 1 requires a material with a closed inventory of 2–138 distinct constituents from atomic numbers 1–138; each selected fraction is positive on an identified atomic or mass basis; selected fractions sum to one; outside constituents have zero fraction on that basis.
- Claim 4 restricts k in claim 1 to exactly 4.
- Claim 5 restricts k in claim 1 to exactly 5.
- Claim 163 adds fraction `1/k` for every constituent to claim 1.

Claims 4, 5 and 163 each depend directly on claim 1. They are separate candidates; this chart does not combine their added limitations into one claim. The working description distinguishes feed, retained product and local measurement at D[0010]–[0013], and spatial accounting at D[0037].

## Primary evidence and locators

Vaidya et al., *Scientific Reports* 7, 12293, DOI [10.1038/s41598-017-12551-9](https://doi.org/10.1038/s41598-017-12551-9), recorded publication date 25 September 2017. [Primary full-text JATS XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5612997/fullTextXML). The reviewed download contains 103,222 bytes; SHA-256 `6d401ee84c0f3e1ade3ce1b4f0db997900d70da53946b913d7c5ec983f2ec856`. Facts below are paraphrased; chart analysis is separate.

| Anchor | XML locator | Reported evidence |
| --- | --- | --- |
| A | `.//body//sec[@id='Sec2']/p[1]` | Equiatomic CoCrFeNi and CoCrFeMnNi feed from 99.99 wt.% metal pieces, with arc melting, remelting and homogenization. |
| B | `.//body//sec[@id='Sec4']/p[1]` | Figure 2c presents estimated bulk principal-element composition. |
| C | `.//body//sec[@id='Sec4']/p[2]` | Figure 3a: selected CoCrFeNi atom-probe volume contains a high-angle grain boundary and detected carbon at 0.0087 at.%; principal-element composition is described as equiatomic. |
| D | `.//body//sec[@id='Sec4']/p[3]` | Figure 3b: CoCrFeMnNi analysis reports additional C/N/O and nearly equiatomic composition within grains and at the boundary. |

Locators are namespace-free JATS XPath positions for the identified bytes. Extract displayed paragraph content with `''.join(paragraph.itertext())`. No plotted values were digitized, no figures were reproduced, and no whole-specimen composition was reconstructed from these local measurements.

## Limitation-by-limitation comparison

| Actual requirement | Relevant teaching | Consequence and unresolved issue |
| --- | --- | --- |
| Claim 1: material, permitted element labels and cardinality | A–D: named alloy systems and trace constituents. | There is clear subject-matter overlap. Additional impurities can belong to a larger permitted support; impurity detection does not automatically take an alloy outside claim 1. |
| Claim 1: positive normalized fractions on an identified basis | A–D: nominal and measured composition. | Distinguish principal-element normalization, sampled atom counts and the actual claimed inventory. No complete numerical whole-specimen atomic or mass vector is supplied by this chart. |
| Claim 1: closed inventory and zero outside it | A, C, D: preparation and local inventory. | Determine the claimed material boundary and whether closure is a substantive restriction or merely selecting all constituents actually present. A missing exhaustive assay alone does not resolve disclosure or inherency. |
| Claim 4: exactly four constituents, plus every claim 1 requirement | A, C: quaternary-system comparison. | Four principal names do not establish a complete four-constituent inventory. Assess the sampled material, source interpretation and any idealized teaching separately; do not silently omit a detected constituent. |
| Claim 5: exactly five constituents, plus every claim 1 requirement | A, C, D: two possible support interpretations. | Five principal names do not establish an exhaustive inventory. Compare the quinary principal system and, separately, the quaternary system with its additional constituent as a possible five-element candidate. Five identified constituents alone do not establish that no others are present. |
| Claim 163: every inventory fraction equals `1/k`, plus claim 1 | A–D: principal-element equality terminology. | Determine which denominator the teaching uses. Exact whole-inventory equality is not established by the principal-element terminology alone. Atomic equality also does not establish the alternative mass equality; conversion needs qualified constituent masses. |

These observations distinguish the reported specimens, nominal/idealized teaching and claim interpretation. The source's local impurity observations must retain their sampling and preparation context; they are not automatically a quantitative certificate for the entire original coupon. No claim is declared novel because this one source lacks a complete measured match.

## Possible statutory arguments and their limits

For section 102, compare all limitations as arranged in the particular claim against one qualifying reference, including justified inherent features and relevant enablement. An enabled species inside a broad genus can anticipate the genus; the reference need not enable every other embodiment of the candidate's broad claim. Thus claim 1 can remain exposed to a species argument even when an exact-four, exact-five or equal-fraction comparison requires additional analysis. The converse does not follow: a broad candidate claim or menu does not automatically anticipate every later selected species. [MPEP §2131, including §2131.02](https://www.uspto.gov/web/offices/pac/mpep/s2131.html).

Reference enablement may draw on skilled-person knowledge and supporting evidence. Actual synthesis or an exhaustive measured inventory is not categorically required in every reference. An asserted inherent feature needs necessity supported by facts or technical reasoning; possibility alone is insufficient. Preserve the distinction between a source's imperfect assay and failure to disclose or enable a claimed embodiment. [MPEP §2121](https://www.uspto.gov/web/offices/pac/mpep/s2121.html), [§2112](https://www.uspto.gov/web/offices/pac/mpep/s2112.html).

For section 103, first settle the actual difference after interpreting inventory and basis. Identify supporting teachings, a reasoned selection or modification rationale and a reasonable expectation of success. This chart supplies no established route to absolute impurity exclusion or exact all-constituent equality, and does not turn a finite-purity starting material into either result. No obviousness conclusion is recorded. [MPEP §2143](https://www.uspto.gov/web/offices/pac/mpep/s2143.html).

The candidate claims' effective filing dates and applicable exceptions are unprovided. The article's recorded publication date is a source fact, not a completed statutory-reference determination. Inventorship, applicant contribution, full-scope enablement, unity and later claims with additional structure/process/use limitations remain separate inquiries.

## Evidence needed to finish this comparison

Clarify the intended specimen boundary and the meaning of closed inventory, outside-zero fractions and exact equality in the actual relied-on application. Assess the source's nominal teaching and any asserted inherency with supporting technical evidence. Establish relevant filing/disclosure chronology and exceptions. Then record a claim-specific statutory outcome, with any remaining limitations explicit.

The claim-support maps remain novelty-unassessed; this preliminary chart does not change their status or count as a completed novelty opinion. It strengthens a concrete comparison and identifies the directional genus/species issue, while the full requested universal physical and legal result remains unproved.
