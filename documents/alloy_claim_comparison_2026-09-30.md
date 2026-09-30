# Alloy comparison against working claims 1, 4, 5 and 163

Prepared 30 September 2026. Status: preliminary source-to-limitation comparison, with claim construction, statutory dates and outcomes open. This is attributed third-party evidence, not an applicant experiment or a finding that any candidate claim is patentable. It addresses concrete composition and impurity questions left open in the [alloy reference family](reference_entry_support.md#alloy-reference-family). The original reference entry, application and reviewed PDFs remain unchanged.

## Exact candidate version

This chart uses the [30 September working application](provisional_application_working_2026-09-30.md), source SHA-256 `1b508938a31b1e7a19b59b3f06edfd21e8378d6ba9e375551250ceb79a8fd198`, at repository baseline `a85536a94d4eb633c098d0299824e73dca55e3e4`.

The same-day construction follow-up starts from chart baseline `b1e6dd5475358e04363e00af5887ae4c33292410`. It resolves the complete-actual-support branch of the closure question below; the candidate application text is unchanged.

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
| Claim 1: positive normalized fractions on an identified basis | A–D: nominal and measured composition. | Under the complete-actual-support reading below, positivity and normalization follow from total atom counts without prescribed fraction values. The expressly identified basis still needs interpretation. No complete measured whole-specimen vector is supplied. |
| Claim 1: closed inventory and zero outside it | A, C, D: preparation and local inventory. | Under that reading, outside-zero follows from defining support by actual positive atom counts. Impurities can enlarge the permitted support; an incomplete exhaustive assay alone does not exclude the source material. A fixed-list or additional inventory-declaration reading requires separate assessment. |
| Claim 4: exactly four constituents, plus every claim 1 requirement | A, C: quaternary-system comparison. | Four principal names do not establish a complete four-constituent inventory. Assess the sampled material, source interpretation and any idealized teaching separately; do not silently omit a detected constituent. |
| Claim 5: exactly five constituents, plus every claim 1 requirement | A, C, D: two possible support interpretations. | Five principal names do not establish an exhaustive inventory. Compare the quinary principal system and, separately, the quaternary system with its additional constituent as a possible five-element candidate. Five identified constituents alone do not establish that no others are present. |
| Claim 163: every inventory fraction equals `1/k`, plus claim 1 | A–D: principal-element equality terminology. | Determine which denominator the teaching uses. Exact whole-inventory equality is not established by the principal-element terminology alone. Atomic equality also does not establish the alternative mass equality; conversion needs qualified constituent masses. |

These observations distinguish the reported specimens, nominal/idealized teaching and claim interpretation. The source's local impurity observations must retain their sampling and preparation context; they are not automatically a quantitative certificate for the entire original coupon. No claim is declared novel because this one source lacks a complete measured match.

## Conditional construction: complete actual support

Claim 1 does not fix a particular constituent list, individual fraction values, purity threshold, phase or uniform spatial distribution. D[0010] defines atomic fractions by a stated inventory; D[0013] identifies support through positive fractions; D[0014] includes all constituents in a closed denominator. Consider the reading under which the selected inventory may include every elemental constituent actually present in one defined specimen at one time. This is a construction hypothesis consistent with those definitions, not a final legal construction. U.S. examination applies a reasonable interpretation in light of the specification; restrictions absent from the claim should not be imported merely from a particular embodiment. [MPEP §2111 and §2111.01(II)](https://www.uspto.gov/web/offices/pac/mpep/s2111.html).

Assume a finite, well-defined elemental atom inventory consisting entirely of recognized elements with Z = 1–118 and containing at least two distinct elements. Let N_Z be each element's actual atom count, S = {Z : N_Z > 0}, N = sum over S of N_Z, k = |S|, and x_Z = N_Z/N. Then 2 <= k <= 118, each selected fraction is positive, sum over S of x_Z = 1, and each outside fraction is zero. These accounting relationships are necessary under the stated assumptions. They require no prescribed target proportions or physical removal of impurities. Additional elements join S. Summing counts over the same specimen boundary also permits gradients or multiple phases; a local assay and a whole-coupon inventory remain different boundaries.

Consequently, on this reading, closure and normalization impose no further physical restriction on that class of ordinary multielement specimens. An incomplete exhaustive assay does not by itself defeat claim 1's accounting conditions. The argument supplies neither missing constituent identities nor their measured values, and nondetection is not treated as absence. It concerns elemental atom accounting, not arbitrary free-particle systems or hypothetical-element availability. It uses the atomic alternative without converting to mass fractions.

The words “selected” and “expressly identified” still matter. If they require a constituent list fixed independently of the actual support, or an additional complete-inventory declaration accompanying the material, the counting identity alone does not establish those requirements. The source uses atomic-composition conventions, but principal-element and local reporting are not a complete inventory declaration. Claim 1 does not expressly recite claim 186's record operations; those operations should not be silently added or an express claim-1 limitation silently removed.

This resolves one conditional branch of the comparison: the source's prepared ordinary alloy can remain a species within claim 1's broad genus despite unquantified trace constituents. The exact-four, exact-five and all-constituent-equality limitations remain separate. A justified inherency argument must connect the source material to the defined finite atomic inventory and reasonable construction; the identity above is technical reasoning about necessary count relationships, not a prediction of an unreported physical result. The source's qualification and enablement, including relevant skilled-person knowledge, still require assessment under the statutory framework below.

## Possible statutory arguments and their limits

For section 102, compare all limitations as arranged in the particular claim against one qualifying reference, including justified inherent features and relevant enablement. An enabled species inside a broad genus can anticipate the genus; the reference need not enable every other embodiment of the candidate's broad claim. Thus claim 1 can remain exposed to a species argument even when an exact-four, exact-five or equal-fraction comparison requires additional analysis. The converse does not follow: a broad candidate claim or menu does not automatically anticipate every later selected species. [MPEP §2131, including §2131.02](https://www.uspto.gov/web/offices/pac/mpep/s2131.html).

Reference enablement may draw on skilled-person knowledge and supporting evidence. Actual synthesis or an exhaustive measured inventory is not categorically required in every reference. An asserted inherent feature needs necessity supported by facts or technical reasoning; possibility alone is insufficient. Preserve the distinction between a source's imperfect assay and failure to disclose or enable a claimed embodiment. [MPEP §2121](https://www.uspto.gov/web/offices/pac/mpep/s2121.html), [§2112](https://www.uspto.gov/web/offices/pac/mpep/s2112.html).

For section 103, first settle the actual difference after interpreting inventory and basis. Identify supporting teachings, a reasoned selection or modification rationale and a reasonable expectation of success. This chart supplies no established route to absolute impurity exclusion or exact all-constituent equality, and does not turn a finite-purity starting material into either result. No obviousness conclusion is recorded. [MPEP §2143](https://www.uspto.gov/web/offices/pac/mpep/s2143.html).

The candidate claims' effective filing dates and applicable exceptions are unprovided. The article's recorded publication date is a source fact, not a completed statutory-reference determination. Inventorship, applicant contribution, full-scope enablement, unity and later claims with additional structure/process/use limitations remain separate inquiries.

## Evidence needed to finish this comparison

Settle the intended specimen boundary and construction of “selected” and “expressly identified” against the actual relied-on application. The complete-actual-support branch now has the conditional accounting analysis above; an independently fixed-list or additional-declaration construction remains open. Assess the source's nominal teaching, exact cardinality/equality and any asserted inherency with supporting technical evidence. Establish relevant filing/disclosure chronology and exceptions. Then record a claim-specific statutory outcome, with any remaining limitations explicit.

The claim-support maps remain novelty-unassessed; this preliminary chart does not change their status or count as a completed novelty opinion. It strengthens a concrete comparison and identifies the directional genus/species issue, while the full requested universal physical and legal result remains unproved.
