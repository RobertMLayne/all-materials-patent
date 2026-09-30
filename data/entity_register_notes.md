# Entity register notes

Prepared 29 September 2026. Companion: `entity_register.json`.

## What the artifact contains

- Exactly 138 element records in atomic-number order: 118 recognized elements and 20 hypothetical placeholders.
- Accepted names and symbols for Z = 1 through 118 follow the [IUPAC table dated 4 May 2022](https://iupac.org/wp-content/uploads/2022/07/IUPAC_Periodic_Table-04May22_CRA.pdf); the IUPAC source page was checked on 29 September 2026.
- E119 through E138 are explicitly local placeholder labels, not accepted or systematic IUPAC symbols. Their accepted-name and accepted-symbol fields are null. The cited [IUPAC recognition and naming page](https://iupac.org/what-we-do/periodic-table-of-elements/) supplies the recognized-table boundary, not evidence that these extra elements exist.
- A deliberately finite register of 17 Standard Model particle categories, with the counting convention stated below.
- Parameterization notes for composite particles, quasiparticles, hypothetical particles and nuclide identities. No complete isotope table or theoretical-particle universe is represented.

## Element identity and status

`atomic_number` is Z. `name` and `symbol` carry accepted IUPAC identities only when `status` is `recognized_element`. For a `hypothetical_placeholder`, those two fields are local descriptive labels and `symbol_kind` makes this explicit.

Each element row carries a source URL, source-table edition date, and source-check date. The 2022 edition date is not a discovery date. For hypothetical rows it identifies the recognized table used as the comparison boundary. The choice of Z = 138 is an indexing boundary, not a claimed physical limit.

Recognition of an element does not establish that all its isotopes exist, that macroscopic quantities are available, or that every composition is stable or synthesizable. Isotopes, nuclear isomers, ions, allotropes and material phases must be distinguished without counting them as additional elements. No atomic weights or property values are supplied.

## Particle counting convention

The 17 entries mean six quark-flavor categories, three charged-lepton particle/antiparticle categories, three neutrino-flavor categories, and five boson categories: photon, gluon, W pair, Z, and Higgs. W+ and W- are grouped. Gluon color components and quark colors are not separate rows. This category count is not an absolute count of elementary particles, independent states, or all physical entities.

Neutrino flavor labels are not mass-eigenstate labels. The artifact does not resolve Dirac versus Majorana nature or imply that a minimal massless-neutrino model explains measured neutrino masses. Established particle observations also do not establish stable bulk-material ingredients. [CERN Standard Model](https://home.web.cern.ch/science/physics/standard-model/), [PDG 2026 tables](https://pdg.lbl.gov/2026/tables/contents_tables.html).

Use the [PDG 2026 API edition](https://pdg.lbl.gov/2026/api/index.html) and preserve its version if numerical particle data are added. PDG includes searches as well as measured particles: inclusion in a listing is not confirmation of existence.

Composite-particle records must specify their construction level and state. Counting an atom, its nucleus and its nucleons as independent mixture constituents would double-count the same inventory unless a particular physical construction is defined. Quasiparticles require a host and conditions; illustrative labels such as phonon or magnon are not additional chemical elements. [IUPAC quasiparticle](https://goldbook.iupac.org/terms/view/08863).

## Nuclide identifiers and provenance

Use Z, A and a source-qualified nuclear-state identifier. Keep original source labels and excitation information. The local key template is `Z{Z}-A{A}-{state_local_id}@{source_edition}`. A local label such as m1 must be mapped to the actual evaluated source; labels must not silently identify different states across editions. Ion charge is a separate electronic-state qualifier.

Mathematical conditions such as integer A >= Z do not prove existence. Preserve uncertainty, limits, estimated values, unknown values and unresolved energy offsets. Do not infer zero from a blank. Existence status is distinct from whether an individual property, such as mass, is measured or estimated.

[NUBASE2020](https://www-nds.iaea.org/amdc/ame2020/NUBASE2020.pdf) reports, for its 30 October 2020 experimental-data cutoff, 3,340 ground-state nuclides and 1,938 excited isomeric states based on experimental information, plus 218 unobserved ground states and 45 unobserved isomers treated by estimates. These historical categories are not a current count of all confirmed isotopes. Its stated isomer scope uses half-lives of at least 100 ns.

The [IAEA LiveChart API guide](https://www-nds.iaea.org/relnsd/vcharthtml/api_v0_guide.html) describes an ENSDF April 2022 snapshot with other inputs including AME2020 and NUBASE2020. A 2026 retrieval date must not be substituted for an evaluation cutoff. The guide requires care in distinguishing ground and metastable states through energy information. No full nuclide-table download was performed for this artifact.

## Validation and limits

The JSON was checked for exactly 138 element records; 118 recognized and 20 hypothetical records; unique atomic numbers and symbols; consecutive Z = 1 through 138; valid source references; and 17 particle categories under the stated convention.

This is an identity and evidence-status register. It does not supply material preparation, demonstrate properties, enumerate every hypothetical particle, establish inventorship or patentability, or establish comprehensive defensive coverage. New experimental evidence requires an explicitly versioned update rather than silently changing the meaning of an existing record.
