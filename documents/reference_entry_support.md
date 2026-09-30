# Source supported material reference entries

These entries provide concrete preparation and characterization evidence for the broad composition disclosure architecture. They describe published third-party work, not an applicant invention, performed applicant experiments, or a conclusion that all composition ranges are physically enabled. Their role is to make the architecture more specific while retaining the full requested scope and its unresolved technical gaps.

## Current package evidence

The existing preparation framework in `documents/provisional_application_draft.md`, paragraphs [0038]-[0043], identifies the categories of information an entry needs. Paragraphs [0039]-[0040] list route classes rather than composition-specific recipes. Paragraph [0044] summarizes a real TiO2(B) publication but explicitly leaves the complete methods to that source. Paragraph [0045] correctly limits what can be inferred from the host formula. Paragraphs [0062]-[0067] provide mechanism examples with proposed extrapolations, rather than an applicant-specific experimentally validated material series. Paragraph [0080] records unresolved full-scope preparation and property support.

The blueprint's `Disclosure entry architecture` already provides a useful field schema. Its existing `MAT LIT 0001` is an attributed source locator, and says it is not a substitute recipe. The records below supply additional concrete fields and expose gaps that a composition vector alone cannot resolve. They do not convert a source summary into a demonstrated complete reproduction by the applicant.

## Alloy reference family

**Candidate identifiers:** MAT-LIT-ALLOY-0001A and MAT-LIT-ALLOY-0001B. **Evidence:** ESTABLISHED third-party report; no applicant repetition. **Known published teaching:** Vaidya et al., *Scientific Reports* 7, 12293, September 25, 2017, DOI 10.1038/s41598-017-12551-9. [Primary article](https://www.nature.com/articles/s41598-017-12551-9)

| Field | Source supported detail |
| --- | --- |
| Nominal composition | Equiatomic CoCrFeNi and CoCrFeMnNi; respectively 25 and 20 atomic percent per principal element. |
| Starting materials | Solid constituent metals, 99.99 weight percent purity. |
| Preparation | Arc-melting chamber evacuated to 10^-5 mbar and purged with purified argon; four or five remelts; homogenization at 1473 K for 50 hours. |
| Structure and composition checks | Single FCC phase reported; Cu K-alpha XRD, SEM with EBSD and EDS, and grain-boundary atom-probe analysis. |
| Atom-probe conditions | Tips at 60 K; laser pulses at 250 kHz and 20 pJ. |
| Conditional property evidence | Nickel grain-boundary diffusion in the five-component alloy exceeded the four-component alloy above approximately 800 K; the relationship reversed at lower temperatures. |
| Pinpoints | Methods; Results and Discussion, microstructure analysis; temperature dependence of Ni grain-boundary diffusion; Figures 2-4 and 6. |
| Not captured for reproduction | Charge masses, melt parameters, homogenization atmosphere/cooling, specimen-wide impurity uncertainty, and quantitative composition acceptance limits. |

The original paper and its supplementary material remain the controlling technical sources for the cited experiment. The two records must retain separate identities. Neither may acquire an assumed composition tolerance, impurity budget, cooling path, or property result through a default value in the proposed record generator.

**Inference for the requested scope:** a principal-element vector is only part of the material record. The exact rational targets (1/4, 1/4, 1/4, 1/4) and (1/5, 1/5, 1/5, 1/5, 1/5) are mathematical descriptions of nominal principal-element ratios. They do not assert that every atom in the isolated specimen belongs to those principal elements, or that measured ratios have infinite precision. Actual specimen-wide fractions require an assay and a denominator that accounts for the chosen impurity policy.

**Proposed extension requiring independent support:** a non-equiatomic composition, an added constituent, a different phase, an isotope-enriched feedstock, or a new annealing path becomes a new record linked to this family as background. Its preparation, measured identity, and property scenario remain PROPOSED or UNSUPPORTED until separately supported. The fifth-element comparison does not supply a rule for every sixth through 138th constituent.

## Inorganic reference family

**Candidate identifier:** MAT-LIT-OXIDE-0001, extending the existing MAT LIT 0001. **Evidence:** ESTABLISHED third-party report; no applicant repetition. **Known published teaching:** Xiang et al., *Scientific Reports* 3, 1411, March 11, 2013, DOI 10.1038/srep01411. [Primary publisher PDF](https://www.nature.com/articles/srep01411.pdf), [archived full article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3593223/)

| Field | Source supported detail |
| --- | --- |
| Identity | TiO2(B) nanosheets with exposed (010) faces; Ti:O = 1:2 describes the oxide host. |
| Selected precursor route | 1 mL TiCl4, 1 mL deionized water, and 30 mL ethylene glycol in a 40 mL Teflon-lined autoclave; stir 30 seconds; seal; heat at 150 degrees C for six hours. |
| Isolation | Centrifuge; wash four times using water and ethanol. |
| Confirmation | Cu K-alpha XRD: wavelength 1.5418 angstrom, 40 kV, 200 mA, scan 6 degrees/minute; HRTEM at 200 kV. Raman and thermal analyses also inform identification. |
| Whole-product qualification | Surface ethylene glycol was estimated at about 22 weight percent. Water exposure could favor conversion to anatase. |
| Pinpoints | PDF page 2, Results and Figure 1; page 4, Discussion; page 5, Methods. |
| Not captured for reproduction | Precursor grades, cooling, centrifuge settings, wash volumes, drying/storage, yield, and quantitative impurity acceptance limits. |

**Accounting inference:** this literature product should not be used as an established example of a whole isolated specimen containing only two elements. Its host formula describes one constituent phase. Retained molecular surface material introduces additional elemental inventory into whole-product accounting. The host, surface layer, and whole-product denominator must therefore have separate fields. The existing draft's host-formula arithmetic remains useful; a whole-product purity assumption would not be justified by that arithmetic.

**Proposed extension requiring independent support:** different Ti/O ratios, oxygen-vacancy concentrations, dopants, other polymorphs, different ligands, or trace constituent targets require distinct identities, routes, assays, and stability records. A source-backed preparation for this particular morphology does not transfer automatically to every point in the Ti/O composition simplex or to multicomponent oxide systems.

## Evidence boundaries for record generation

Use the following field rules across every material family. These are proposed disclosure controls, not assertions about a particular source's successful experiments.

| Field | Required rule | State when evidence is absent |
| --- | --- | --- |
| Composition basis | State principal-element, host-phase, or whole-product accounting; retain exact target fractions separately from measured fractions and uncertainty. | Nominal target only. |
| Preparation | Preserve supported quantities and conditions together; record every unresolved critical step. | PROPOSED route or UNSUPPORTED feasibility, as applicable. |
| Identity | Establish which phase, morphology, connectivity, defect state, and sample history the record actually concerns. | Candidate identity only. |
| Characterization | Specify measurements able to distinguish realistic alternative products; add calibration, sampling, detection limits, and reference data. | Unconfirmed product or stated analytical gap. |
| Property | Bind a result to a named material, state, method, units, baseline, temperature, and other relevant conditions. | PROPOSED test or UNSUPPORTED prediction. |
| Variations | State which substitutions, interval regions, or process changes have independent supporting evidence. | No inherited evidence from a parent entry. |
| Provenance | Keep source teachings separate from applicant contributions and unperformed applicant work. | No applicant experiment, contribution, or inventorship established. |

The broad range generator can reference these entry identifiers without representing either as a universal preparation algorithm. Generated records with no technical content must keep unresolved fields explicit. A process class, a property sign, or a list of opposite outcomes must never default to ESTABLISHED.

## Property scenarios and unresolved breadth

The user's request to describe expected and contrary responses can be implemented as a conditional scenario structure: specified baseline, mechanistic rationale, candidate change, defined test, decision threshold, and unresolved alternatives. A scenario containing both signs remains a proposal until evidence distinguishes them. Storing both possible responses does not establish that either occurs for an arbitrary element combination, and cannot establish a quantitative property threshold by itself.

For these reference families, a future applicant study would need specimen provenance, raw composition and structural records, and a separately defined property protocol. No study has been run here. Changes at 10^-19 fractional abundance, all constituent counts through 138, hypothetical elements, isotope-state availability, and particle containment remain outside the support provided by these two published families.

These references are existing public teachings. Republishing them adds an attributed record to this package; it does not make the underlying work newly disclosed by the applicant. No patent-status search, freedom-to-operate determination, claim-specific anticipation opinion, full-scope enablement conclusion, or universal patent bar is asserted. The records strengthen the evidence architecture while leaving the requested full scope intact for further technical and legal assessment.
