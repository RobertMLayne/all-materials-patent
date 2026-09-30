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

## Molecular reference family

**Identifier:** MAT-LIT-MOLECULAR-0001. **Evidence:** ESTABLISHED third-party crystallization report; CALCULATED formula accounting; PROPOSED follow-up comparisons. No applicant experiment is reported.

Broadhurst et al., *IUCrJ* 8 (2021), 860–866, DOI 10.1107/S2052252521010101, report time-resolved carbamazepine crystallization. [Primary article, sections 2–3](https://journals.iucr.org/m/issues/2021/06/00/yc5034/index.html). Carbamazepine's formula is C15H12N2O; its molecular identity requires the specified connectivity, not that formula alone. [NIST Chemistry WebBook identity](https://webbook.nist.gov/cgi/cbook.cgi?ID=C298464).

| Field | Attributed experimental detail |
| --- | --- |
| Feed and solvent | 0.1125 g carbamazepine in 25.6257 g ethanol; water measured as 0.03%; gravity filtration. |
| Local preparation | Deposit 3 microlitres on a Quantifoil R2/2 grid plasma-treated for 45 s; hold at 298 K and 21% humidity for 20–180 s; pressure-assisted blotting and immediate vitrification in liquid ethane. |
| Characterization | CryoTEM and three-dimensional electron diffraction at 200 kV and 100 K. |
| Observations | At 30 s, dihydrate predominated and minor forms II, III and IV were identified. At 180 s, only dihydrate was observed. Powder X-ray diffraction detected dihydrate at both times. |
| Source limits | This is a grid crystallization study, not an isolated pure bulk batch of each minor phase; supporting information controls the detailed analysis. |

**CALCULATED accounting:** excluding solvent, substrate, impurities and any bound water, a nominal carbamazepine formula unit has 30 atoms. In the ordered support (H,C,N,O), x=(2/5,1/2,1/15,1/30). Adding exactly two water molecules gives a nominal dihydrate unit C15H16N2O3 with 36 atoms and x=(4/9,5/12,1/18,1/12). Both sums are exactly one. These are formula-unit targets, not measured whole-product atomic fractions. The different unsolvated crystal forms retain the same nominal vector; a material address must also identify connectivity, crystal form, hydration and history.

**Unresolved reproduction fields:** quantitative phase fractions and their uncertainty, chosen-crystal sampling bias, a bulk isolation route for each minor form, residual solvent/impurity inventory, classification limits and preservation after warming. A detected crystallite does not establish a bulk phase fraction; a bulk nondetection does not establish absolute absence.

**PROPOSED conditional scenario:** compare the occurrence of non-dihydrate crystallites in a prespecified, consistently sampled region after short versus longer holds, under matched solution and environmental conditions. The reported time dependence motivates a decrease hypothesis. An increase or persistence must remain an unperformed alternative, with nucleation, transformation kinetics and sampling/measurement effects assessed separately. Do not assign an opposite strength, conductivity or solubility result from this study; those observables need their own specimens and protocols. Changing humidity, solvent or quench timing creates a new comparison and cannot silently inherit this source's result.

**Coverage consequence:** the record supplies molecular identity, a particular crystallization route and time-resolved structural observations. It does not supply every molecule sharing the element ratios, every polymorph, a closed whole-product impurity specification, or later manufacturing/use limitations. Retain this source as attributed background; no newly invented applicant material or universal molecular preparation rule is established.

## Polymer reference family

**Candidate identifiers:** MAT-LIT-POLYMER-0001A (PLLA control) and MAT-LIT-POLYMER-0001B (PDLA/PLLA stereocomplex). **Status:** ESTABLISHED third-party reported preparation/measurements; no applicant repetition. Prepared 30 September 2026.

**Primary publication:** Su, Feng and Yu, *Polymers* 12 (2020), 2515, published 28 October 2020, DOI [10.3390/polym12112515](https://doi.org/10.3390/polym12112515). [Publisher article](https://www.mdpi.com/2073-4360/12/11/2515), [open archived article](https://pmc.ncbi.nlm.nih.gov/articles/PMC7694064/), [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7694064/fullTextXML). The article carries CC BY 4.0; no figures or full text are reproduced here.

### Source data record

| Field | Attributed detail |
| --- | --- |
| Identity/basis | PLLA versus PDLA/PLLA 1:1 **polymer mass** blend; PLLA grade 4032D. |
| Preparation | Vacuum-dry 40 °C overnight; melt-blend 190–220 °C, 15 rpm; cool 20 °C, granulate; hot-press 230 °C, 15 minutes; cool 20 °C. |
| DSC protocol | 10 mg; nitrogen; 30–250 °C, 10 °C/min heating/cooling; 250 °C/3 minutes, then 30 °C/3 minutes; reported second heating. |
| Thermal result | Melting peaks: PLLA 171.2 °C; 1:1 blend 227.7 °C. Blend stereocomplex crystallinity: 43.7%. |
| Structure check | XRD: 2θ 5–30°, 5°/minute, 20 °C; stereocomplex peaks 11.9°, 20.7°, 24.0°. |
| Tensile protocol/result | 20 °C, 20 mm/min, ISO-527-2, ≥5 tests. PLLA → blend: strength 52.98 → 83.70 MPa; modulus 1.13 → 2.04 GPa. |
| Pinpoints | Methods §§2.1–2.3; results §§3.1, 3.5; Figures 1, 8. |

### Accounting and material identity

**CALCULATED ideal repeat-unit accounting:** the constitutional repeat `–O–CH(CH3)–C(=O)–` contains C3H4O2. Its C/H/O atom fractions are 1/3, 4/9, and 2/9. The two stereochemical chain types share this bookkeeping vector, yet their sequence stereochemistry and crystal packing remain different record fields. [PubChem's L-lactide](https://pubchem.ncbi.nlm.nih.gov/compound/L-Lactide) and [D-lactide](https://pubchem.ncbi.nlm.nih.gov/compound/d-lactide) records independently distinguish the monomer stereochemistry while giving the same C6H8O4 formula.

The 1:1 feed ratio is neither a ratio of polymer molecules nor a whole-specimen elemental assay. Finite chains require end-group/initiator accounting; commercial material may also contain residual monomer, additives, moisture, or degradation products. No impurity budget, exact specimen-wide atom vector, or infinite measured precision is supplied by this calculation. Separate as-pressed film history from the thermal cycle imposed by DSC; a second-heating result must not automatically become an as-delivered service property. The reported crystallinity is not 100% of the specimen.

### Reproduction gaps and source ambiguity

**Our audit; unresolved:** batch masses, vacuum pressure, extrusion residence/geometry, pressing pressure, cooling rate, optical purity, moisture/impurity limits, and raw uncertainty/calibration need completion. The PDLA Mn/PDI sentence is internally inconsistent; confirm its assignment independently. These gaps prevent this summary from being treated as a complete applicant reproduction. Keep the publication's route qualified rather than filling missing fields with assumed defaults.

### Expected and contrary scenarios

**Source interpretation:** stereocomplex packing/physical junctions are associated with increased stiffness (§§3.3, 3.5). Physical junctions do not by themselves establish newly formed covalent branching.

**PROPOSED matched-feed and lot test:** hold feedstock lots and the 1:1 mass ratio fixed, then compare controlled thermal histories that favor retained crystallinity versus suppressed crystallization. Define an expected response as greater modulus when a measured stereocomplex fraction is greater, under a common temperature, strain-rate, geometry, conditioning, and molecular-weight protocol. Determine actual phase fractions before interpreting the mechanical result; matched feed does not establish matched final product composition.

**PROPOSED contrary response:** lower or unchanged modulus could occur if the chosen history instead limits crystallization, changes molecular weight, or introduces porosity/defects. Test those alternatives through structural, molecular-weight, and density evidence rather than declaring a contradiction from feed composition alone. A modulus increase also does not imply increased ductility or every form of toughness; choose separate response variables and decision thresholds before testing. Neither proposed comparison has been performed here.

This family supplies a concrete existing teaching for a particular polymer system. It does not establish new applicant subject matter, all-polymer preparation, properties for arbitrary elemental compositions, or a universal bar to later patents.

## Composite reference family

**Candidate:** MAT-LIT-COMPOSITE-0001. **Classification:** ESTABLISHED third-party literature report; applicant reproduction NOT PERFORMED. **Reviewed:** September 30, 2026. This proposal extends the material-class support architecture with a composite example. It is neither an applicant invention nor evidence that the full proposed composition domain is enabled.

### Bounded source record

Nguyen et al. (2017), *Carbon*, original NIST research. [NIST record](https://www.nist.gov/publications/impact-uv-irradiation-multiwall-carbon-nanotubes-nanocomposites-formation-entangled); [author manuscript](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=920936).

| Field | Source-supported detail |
| --- | --- |
| Constituents/basis | Multiwall carbon nanotubes (MWCNTs), reported 0.72 mass% in amine-cured DGEBA epoxy; starting resin dispersion 1 mass%; polyoxypropylenetriamine hardener; no UV stabilizers. |
| Preparation | Magnetic stirring 1 h; room-temperature degassing 1 h; bar drawdown on PET; approximately 150 µm films. Toluene used, amount unspecified. |
| Cure | 24 °C/45% RH, three days; postcure 110 °C, 4 h, circulating-air oven. |
| Exposure | 295–400 nm, approximately 140 W/m²; 50 °C/75% RH. Characterization coupons 25 × 25 mm; release specimen approximately 78.5 cm². |
| Measurements | Mass change, ATR-FTIR (4 cm^-1, 128 scans), XPS, SEM/AFM/EFM; nanotube-rich surface network observed. Collector SEM detected no release after 4865 MJ/m². |
| Interface hypotheses | Anchoring, entanglement, residual-matrix bonding, and nanotube attractions proposed; individual contributions unverified. |
| Reproduction gaps | Batch masses, stirring speed, solvent quantity, nanotube lot/purity, quantitative release detection limit not supplied here. |
| Pinpoints | Manuscript §§2.1–2.3, lines 87–181; §§3.3–3.4, lines 282–490; PDF pages 5–9, 15–26. |

### Composition and identity interpretation

The entry generator must keep constituent loading, constituent identity, and whole-product elemental composition in separate fields. The percent-to-fraction conversion of a reported 0.72 mass% is 0.0072 = 9/1250. That arithmetic does not make a rounded formulation statement an exact specimen assay. A record that uses 9/1250 should label it a representation of the reported loading, with measurement uncertainty unresolved, rather than an infinitely precise composition.

A nanotube mass fraction cannot be substituted for an atomic fraction or a volume fraction. Whole-product elemental fractions would require the matrix's constituent amounts and identities, reinforcement purity, residuals and contaminants, and an explicit denominator. A surface-sensitive analysis cannot establish those fractions throughout the specimen. Likewise, the record needs separate morphology and interface evidence; a nominal constituent vector does not encode dispersion, exposed-filler geometry, or adhesion strength.

The preparation fields above are useful source support, but they are not a complete executable protocol. Before an applicant repetition, obtain the missing formulation and instrument settings, specify material acceptance criteria and metrology uncertainty, and document the original source's supplementary methods. Do not silently supply those fields through generator defaults. Collector nondetection must retain its technique and collection conditions; it cannot become a numerical zero, a detection limit, or a general release guarantee.

### Distinct published comparator

Zhao et al. (2023), *NanoImpact*, another original study: [NIST publication record and abstract](https://www.nist.gov/publications/quantitative-evaluation-released-nanomaterials-carbon-nanotube-epoxy-nanocomposites). Its radiolabeled nanotube/epoxy specimens underwent UV plus water spray, followed by shaking or ultrasonication. Collected nanotube mass was reported as 0.23% of embedded nanotube mass during weathering; subsequent mechanical treatment released approximately 0.27% (mass/mass). The authors linked release to disruption of the surface network by spray. The 0.23% denominator is embedded nanotube mass, not whole-composite mass; the 0.27% denominator requires confirmation from the full methods. These are separate specimens and conditions, not measurements on MAT-LIT-COMPOSITE-0001. Only the official abstract was verified here; detailed formulation, spray settings, treatment durations, detection limits, and recovery corrections require the full methods before reproduction.

### Proposed contrasting test and mechanisms

**PROPOSED; no applicant result.** Prepare independently documented replicate batches of the candidate and matched neat-matrix controls. Use a factorial comparison of UV exposure and calibrated water/mechanical stress, with temperature, humidity, specimen geometry, aging dose, and conditioning recorded. Include UV-only, stress-only, combined, and unexposed groups. Predefine the nanotube release measurement, blank correction, recovery, detection limit, sampling schedule, replicate count, and uncertainty. Record both released nanotube mass per initial embedded nanotube mass and per initial whole-specimen mass; retain particle morphology so nanotube-containing fragments are distinguished from isolated tubes.

The conditional response to test is whether a surface network persists under UV-only exposure but loses retention under the added stress. Retention could reflect geometrical interlocking and remaining matrix attachment; stress could remove the network or rupture its attachments. A release difference alone would not separate those mechanisms. Compare cross-sectional and surface microscopy, matrix chemical change, and independently measured interface response before and after treatment. If attachment and network geometry remain unchanged while release rises, investigate collection efficiency, degradation fragments, and other explanations before assigning a mechanism. These are testable alternatives, not promised outcomes.

### Effect on the full-scope disclosure

This is a known published teaching and should be identified as background evidence. Its public provenance is established by the linked records; the exact legally operative publication date and claim comparison remain matters for the prior-art analysis. It supplies a concrete composite entry format and a bounded conditional property scenario. It does not provide preparation or property support for every matrix, filler, loading, interface, manufacturing route, isotope choice, or later use. Each extension needs its own identity, route, characterization, and support status; the universal defensive objective remains unresolved.

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

The broad range generator can reference these entry identifiers without representing any as a universal preparation algorithm. Generated records with no technical content must keep unresolved fields explicit. A process class, a property sign, or a list of opposite outcomes must never default to ESTABLISHED.

## Specimen accounting declarations for proposed studies

These declarations specify what a new study must account for. They are PROPOSED boundaries and unresolved assay fields, rather than completed specimen certificates. Source nominal ratios remain those described above.

| Family | Proposed physical boundary and accounting basis | Required residual or state treatment |
| --- | --- | --- |
| Alloy | One isolated, conditioned coupon; principal-element target reported separately from a whole-coupon atomic/mass inventory. | Identify measured impurities, surface material, porosity and local segregation; report bounds/unknowns rather than setting every other element to zero. |
| Inorganic | Isolated nanosheet product after a named washing, drying and storage procedure; report oxide-host and whole-product inventories separately. | Include retained ligand, hydration, solvent and non-host phases; specify their mass or atom bases and assay uncertainty. |
| Molecular | Selected crystallites in defined grid regions at the observation state; formula-unit calculations remain separate from grid/whole-deposit inventory. | Specify hydration/solvation, unclassified crystals and retained solvent; exclude the support only under an explicit crystal-only boundary. |
| Polymer | Conditioned molded specimen from identified feed lots and thermal history; feed masses and incorporated product composition are separate records. | Include end groups, additives, residuals, degradation and porosity; do not equate matched feed with an established matched final composition. |
| Composite | Isolated cured film plus separately tracked collected material; define dry/wet conditioning and cured-film loading. | Track resin, hardener, nanotubes, retained solvent, voids, surface enrichment and collection losses; embedded-nanotube and whole-film mass denominators remain distinct. |

For a particle-system extension, declare whether the counted population consists of atoms, ions, nuclei, electrons, other particles or host-dependent excitations. Specify the boundary, host, population/occupation convention, normalization, observation interval and lifetime treatment. Do not reuse a chemical elemental fraction as a particle-population fraction without a justified conversion. Hypothetical entities remain unresolved identities and never receive measured population or persistence by default.

## Proposed property scenario cards

All five cards below are unperformed applicant-study designs. Published observations remain ESTABLISHED third-party background, the accounting examples remain CALCULATED, and the new comparison outcomes/mechanisms remain PROPOSED or UNSUPPORTED as stated. These cards do not supply new measured signs, thresholds, confidence levels or acceptance limits. Complete the unresolved protocol fields before conducting or interpreting a study.

For each card, preserve individual specimen and batch identifiers, raw data, calibration records, excluded observations and the reason for each exclusion. Use an initial pilot with independently prepared specimens to estimate variability and then justify the replicate count and sampling frame for the intended precision. A repeated measurement or multiple crystals from one preparation is not automatically an independent preparation. Randomize or counterbalance assignments where appropriate and retain failed preparations. The comparison must use the same defined observable and units in both branches.

Predeclare a meaningful-change threshold tau>0 and a justified uncertainty interval [L_Delta,U_Delta] for the signed difference Delta. Use an interval wholly above tau for increase, wholly below -tau for decrease, wholly within [-tau,tau] for no meaningful change, and otherwise inconclusive. A null finding is not a negative-sign response; an inconclusive interval is not evidence of equivalence. Set confidence/model conventions and threshold equality in the protocol. Account for shared calibration, covariance, clustering and multiple comparisons when applicable. No value of tau or uncertainty is fabricated here.

### SC-ALLOY-01: transport under specified temperature conditions

| Protocol field | Proposed definition and unresolved input |
| --- | --- |
| Baseline and change | Compare MAT-LIT-ALLOY-0001A with 0001B at each nominated common temperature, with independently prepared, characterized coupons. Composition and temperature changes have separate identities. |
| Observable and units | Within a common B-type analysis, use Delta=ln(P_B/P_A), dimensionless, for P=s delta D_gb in m^3/s, requiring P_A>0 and P_B>0. A nondetection or interval reaching zero remains censored/bounded; it cannot be inserted as zero in this logarithm. Within a C-type analysis, use the separately identified D_gb in m^2/s. Do not compare a triple product directly with a diffusion coefficient. |
| Necessary state record | Grain structure, phase, composition/residuals, tracer boundary, annealing temperature/time, penetration-depth calibration and fitting regime. A conversion between quantities must retain the chosen segregation/width model and its uncertainty. |
| Background and branches | The source reports a temperature-dependent ordering. The new experiment must determine its own sign at each stated temperature; no ordering transfers to arbitrary temperatures, added elements or hypothetical labels. |
| Discriminating evidence | Raw tracer profiles, justified regime/fitting limits, fit uncertainty and independently assessed microstructure. A response does not by itself establish the proposed mechanism. |
| Unresolved fields | Exact nominated temperatures, tracer inventory/procedure, profile sampling, model parameters, preparation tolerances, replicate count, tau and uncertainty method. |

The distinction between P and D_gb follows the [primary article's B/C regime analysis and Figure 6](https://www.nature.com/articles/s41598-017-12551-9). Their interchange requires an additional physical model, rather than a unit relabeling.

### SC-OXIDE-01: phase response to a defined exposure

| Protocol field | Proposed definition and unresolved input |
| --- | --- |
| Baseline and change | Split a characterized starting product into matched aliquots; compare a declared water-exposure history with a declared control history. Match initial host/surface-material accounting. |
| Observable and units | Delta=f_anatase,exposed-f_anatase,control, dimensionless, using phase fractions under one validated quantitative convention. Separately report TiO2(B), other phases and any unquantified material. |
| Necessary state record | Initial phase fractions, surface ligand/hydration, specimen mass, exposure temperature/time and storage/measurement history. Retained material can change the whole-product elemental inventory. |
| Expected and other branches | A conversion concern motivates a proposed increase. Persistence is a null alternative. A decrease requires its own mechanism or remains UNSUPPORTED; it is not supplied by listing the opposite sign. |
| Discriminating evidence | Calibrated quantitative phase analysis and an independent structural check, with detection/quantification limits and preparation replicates. Distinguish crystallite detection from bulk phase fraction. |
| Unresolved fields | Exposure schedule, complete phase-quantification method, standards/model, residual treatment, replicate count, tau and uncertainty method. |

### SC-MOLECULAR-01: sampled crystallite occurrence over time

| Protocol field | Proposed definition and unresolved input |
| --- | --- |
| Baseline and change | Compare short and longer holds from matched solution lots and preparation conditions, with separately prepared grids. Fix region-selection rules before inspection. |
| Observable and denominator | p_minor=(classified non-dihydrate crystallites)/(all evaluated crystallites); Delta=p_minor,long-p_minor,short. Report unclassified counts separately and bound their possible effect. This is a count fraction, not a bulk mass/volume phase fraction. |
| Necessary state record | Hold/quench timing, local environment, grid region, hydration/solvation and classification conditions. Matching the initial solution does not establish matching final deposits. |
| Expected and other branches | Source observations motivate a proposed decrease. An increase is a separate unperformed kinetic/sampling hypothesis; unchanged frequency and inconclusive evidence are separate outcomes. |
| Discriminating evidence | Prespecified sampled regions, crystal classifications and reliability checks, independent grid/preparation replicates, and an uncertainty method that accounts for within-grid clustering and unclassified crystals. |
| Unresolved fields | Representative sampling frame, target times, classification error, preservation after quench, repeat count, tau and interval method. No representative population frequency is inferred from the existing selected-crystal observations. |

### SC-POLYMER-01: thermal history with matched feed and lot

| Protocol field | Proposed definition and unresolved input |
| --- | --- |
| Baseline and change | Compare two declared thermal histories for matched 1:1 PDLA/PLLA feed masses and lots. Final specimen composition and molecular-weight distributions require independent checks. |
| Observable and units | Delta=E_history A-E_history B, in GPa, under the same specimen geometry, conditioning and tensile/modulus fitting protocol. Specify gauge length or local strain measurement and fitting interval; crosshead speed alone is not strain rate. |
| Necessary state record | As-processed stereocomplex/homocrystal fractions, porosity, chain/end-group/degradation evidence and retained residuals. Second-heating DSC does not automatically characterize the original tensile-test specimen state. |
| Expected and other branches | More stereocomplex crystallinity motivates a proposed modulus increase; degradation, voids or inadequate crystallization may produce a lower or unresolved result. Neither branch is an applicant measurement or a guaranteed causal relationship. |
| Discriminating evidence | Independent processing batches, phase measurements in the tensile-test state, local strain/modulus analysis and chain/porosity controls. Keep the source control/blend comparison separate from this fixed-feed comparison. |
| Unresolved fields | Source molecular-weight ambiguity, exact histories/press pressure/cooling, purity/lot checks, specimen protocol, replicate count, tau and uncertainty method. |

### SC-COMPOSITE-01: release under matched exposure and collection

| Protocol field | Proposed definition and unresolved input |
| --- | --- |
| Baseline and change | Within one characterized formulation, compare UV-only treatment with a declared combined exposure/stress treatment using matched conditioning, dose and collection. The two published studies do not establish matched specimens. |
| Observable and denominator | r_CNT=(recovered released nanotube mass)/(initial embedded nanotube mass); Delta=r_combined-r_UV. Separately report release relative to initial whole-film mass, collection recovery and possible unrecovered material. |
| Necessary state record | Cured loading, formulation, retained solvent, film geometry, dose, water/mechanical conditions, collector boundaries and time. Distinguish isolated nanotubes from nanotube-containing fragments. |
| Expected and other branches | Added exposure/stress motivates a proposed increase. Unchanged release remains a separate outcome. A negative branch needs an independently supported mechanism or remains UNSUPPORTED; a nondetection is a bounded observation, not an exact zero. |
| Discriminating evidence | Blanks, recovery controls, limits of detection/quantification, mass balance and released-material morphology with independently prepared films. Preserve isotope-label/assay conventions if used. |
| Unresolved fields | Complete matched cure/exposure/stress protocol, initial embedded mass, recovery/calibration, collection geometry, repeat count, tau and uncertainty method. The comparator abstract's 0.27% denominator is not silently assumed. |

## Property scenarios and unresolved breadth

The user's request to describe expected and contrary responses can be implemented as a conditional scenario structure: specified baseline, mechanistic rationale, candidate change, defined test, decision threshold, and unresolved alternatives. A scenario containing both signs remains a proposal until evidence distinguishes them. Storing both possible responses does not establish that either occurs for an arbitrary element combination, and cannot establish a quantitative property threshold by itself.

For these reference families, a future applicant study would need specimen provenance, raw composition and structural records, and a separately defined property protocol. No study has been run here. Changes at 10^-19 fractional abundance, all constituent counts through 138, hypothetical elements, isotope-state availability, and particle containment remain outside the support provided by these five published families.

These references are existing public teachings. Republishing them adds an attributed record to this package; it does not make the underlying work newly disclosed by the applicant. No patent-status search, freedom-to-operate determination, claim-specific anticipation opinion, full-scope enablement conclusion, or universal patent bar is asserted. The records strengthen the evidence architecture while leaving the requested full scope intact for further technical and legal assessment.


## Specific claim fields and later claim comparisons

The original claims 176, 177 and 178 identify molecular, polymer and composite fields. They all depend on claim 1, including its closed atomic/mass inventory and exact zero outside that inventory. The following is an evidence map, not a novelty or complete support finding.

| Original candidate | New entry fields available for review | Required features still unresolved |
| --- | --- | --- |
| Claim 176 | Molecular identity, hydration, time-dependent solid forms and a local crystallization procedure. | Whole-specimen inventory and exact-zero residuals; relevant stereochemistry/solvation and quantitative phase selection; independently assessed full claim scope. |
| Claim 177 | Named chain stereochemistry, ideal repeat unit, feed mass ratio, processing and measured phase/property comparisons. | Incorporated whole-product elemental ratios, end groups, chain/sequence distributions and network completeness; source ambiguity and exact-zero residuals. |
| Claim 178 | Identified matrix/reinforcement, loading basis, film preparation, interface questions and conditional release measurements. | Complete constituent inventory, retained loading, directional/volume accounting, quantified interface/dispersion and exact-zero residuals. |
| Claims 197–199 | Baselines, conditional alternatives, proposed distinguishing measurements and local evidence labels. | Applicant-specific conception, novelty/eligibility and support for the claimed methods; physical outcomes remain unperformed where stated. |

These entries also make the blueprint's hypothetical later-claim tests more concrete:

| Later limitation scenario | Features to compare | Missing features and possible argument |
| --- | --- | --- |
| A material and preparation matching one identified entry | Match identity, state, quantity basis and the linked preparation steps together in the controlling source. | A section 102 argument is a candidate only after verifying every limitation, enablement and a qualifying date. A summary's omitted critical steps must be checked in the source and relevant skilled-person knowledge. |
| The same elements/nominal proportions with a selected solid form or architecture | Separately locate the claimed form, chain stereochemistry or interface geometry. | An element vector alone leaves these features open. An observed minor crystal does not establish an isolated high-purity bulk product. Section 103 would need particular teachings, reasoning and a supported expectation of success. |
| A selected composition or loading from a very large catalog | Identify the particular jointly taught embodiment and denominator, including any necessarily inherent features or limited combination that a skilled person would at once envisage, rather than independently selecting unrelated menus. | A named species can be disclosed in a large list; an unspecified selection is not automatically anticipated. A narrower range, critical value or morphology needs its own comparison. |
| A later manufacturing method or use | Compare every step, operating condition and functional limitation with the particular source. | Product identity alone does not establish additional method or use limitations. Assess whether each limitation is expressly taught or necessarily inherent, and separately assess any supported section 103 rationale. No blanket rejection follows. |

This map does not assess a real later patent claim or assign a blocked percentage. Anticipation and obviousness require their distinct, fact-specific analyses. [USPTO MPEP 2131](https://www.uspto.gov/web/offices/pac/mpep/s2131.html), [MPEP 2143](https://www.uspto.gov/web/offices/pac/mpep/s2143.html).

## Content to include in an actual filing

If these teachings are relied upon, include their necessary identity, preparation, conditions, equations and drawings directly in the accepted description or clearly identified description annex. Identify the exact pages supporting each relied-on feature. Preserve the uploaded and accepted versions. A repository link, current script or live supplement does not automatically become application content. If earlier provisional support is sought, the relied-on content must be present in that earlier filing; later additions do not retroactively enter it. PCT missing-part incorporation has specific prior-application, document and timing conditions and is not a general incorporation of a live repository. [WIPO ISPE 4.12 and 4.26–4.27](https://www.wipo.int/en/web/pct-system/texts/ispe/4_02_27), [PCT Rule 20.6](https://www.wipo.int/en/web/pct-system/texts/rules/r20), [USPTO provisional guidance](https://www.uspto.gov/patents/basics/apply/provisional-application).

The applicant's actual technical contribution remains TECH-001. These attributed published experiments do not become applicant discoveries by being summarized here. Inventorship and any new claimed contribution must be established separately; experiments are not categorically required in every case. [USPTO MPEP 2109](https://www.uspto.gov/web/offices/pac/mpep/s2109.html).
