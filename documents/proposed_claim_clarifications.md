# Prospective isotope-basis and positive-target clarifications

Prepared: **30 September 2026**. Status: **PROPOSED drafting language**, with separately identified **CALCULATED** mathematical examples. Reviewed starting version: repository commit `015c3c82f21866c8a04c410543ab22ea099ec5cc`.

This ancillary document proposes wording for paragraph [0047] and claims 169 and 191-193 of the [preserved application draft](provisional_application_draft.md). It does not amend that draft, its 199 claims, the [historical textual support map](../data/claim_support_map.json), or any fixed PDF. It is outside the [fixed consolidated review edition](consolidated_review_edition.md). Preparation of this proposal asserts no filing, earlier-date entitlement, experiment, measured material property or physical enablement.

The [claim review brief](claim_group_review_brief.md) identified two concrete ambiguities. Paragraph [0047] defines isotope fractions by atom count, but claim 169 inherits both atomic and mass composition alternatives from claim 1 without distinguishing their isotope formulas. Claims 191-193 construct numerical witnesses, while their parent claim 186 separately requires assignment of a strictly positive normalized target. The following proposals make those relationships explicit while retaining both composition alternatives, the unrestricted positive domain and the separate finite grid.

## Isotope accounting: proposed claim 169

**Claim 169 - proposed wording.** The material of claim 1, wherein each selected element i has a conditional atom-count isotope-state distribution y_i,a,s with nonnegative entries summing to one over its specified isotope-state inventory, and wherein the whole-inventory nuclide-state fractions are specified on the same basis as the fractions x_i of claim 1: on an atomic-fraction basis, the nuclide-state fraction is x_i y_i,a,s; and on a mass-fraction basis, for each positively populated isotope-state entry the nuclide-state fraction is x_i y_i,a,s mu_i,a,s/M_i, where mu_i,a,s is a qualified positive mass per counted atom under an expressly identified mass-allocation convention and M_i is the positive finite sum of y_i,a,s mu_i,a,s over the positively populated entries of element i; a zero-population entry has whole-inventory fraction zero on either basis.

The symbol `mu` denotes a mass per counted atom; all such masses use compatible units and the same stated allocation convention. An unpopulated entry does not require an invented mass. An unknown mass for a positively populated entry prevents that numerical mass conversion. The atomic alternative does not acquire a requirement to supply unavailable mass values merely because a mass alternative is also described.

Both branches retain every limitation inherited from claim 1, including its closed elemental inventory and exact-zero fractions outside the selected support. The proposal does not make those physical requirements achievable, or establish the existence of a hypothetical element or nuclear state. Claims 170-172 can continue to describe pure, mixed and source-qualified conditional atom distributions. Claim 173 still requires separate review of the time-specific inventory, decay products and retained or lost material; conversion equations do not resolve those issues.

## Isotope accounting: proposed paragraph [0047]

**[0047] - proposed replacement.** For each element i, let y_i,a,s be the conditional atom-count fraction of its atoms assigned to isotope a and nuclear state s in the specified inventory, with y_i,a,s >= 0 and sum_a,s(y_i,a,s) = 1. This conditional distribution remains atom-count based regardless of the composition basis selected for the material. Let a_i denote the elemental atomic fraction and w_i the elemental mass fraction; x_i of the selected composition record equals a_i on an atomic basis or w_i on a mass basis. The whole-inventory atomic fraction of a nuclide-state entry is a_i y_i,a,s. Where mass conversion is supported, specify qualified masses mu_i,a,s per counted atom under a consistent, expressly stated mass-allocation convention, including the relevant isotope, nuclear/electronic state and any precision-dependent binding or allocation qualification. For positively populated entries define M_i = sum_a,s(y_i,a,s mu_i,a,s), with positive finite M_i, and the derived conditional mass fraction r_i,a,s = y_i,a,s mu_i,a,s/M_i. The whole-inventory nuclide-state mass fraction is w_i r_i,a,s. Entries with y_i,a,s = 0 have r_i,a,s = 0 without requiring a mass value for an unpopulated entry. Each element's nuclide-state atomic fractions sum to a_i and its nuclide-state mass fractions sum to w_i. Elemental conversions use w_i = a_i M_i/sum_j(a_j M_j) and a_i = (w_i/M_i)/sum_j(w_j/M_j) under the same convention. Unknown masses for positively populated entries prevent numerical mass conversion; they are not supplied by standard atomic weights, placeholders, blanks or assumed zeros. An atomic target and its conditional atom-count distribution can still be described without asserting an unavailable mass conversion. Natural, enriched, depleted, pure-isotope and mixed-isotope targets can be recorded. These equations are compositional accounting, not proof of state existence, availability, preparation, persistence or measured fractions; lifetime, decay products, observation time and preparation history remain separate requirements.

Here the isotope index `a` in `y_i,a,s` is distinct from the elemental atomic-fraction symbol `a_i`. An eventual typeset application should retain that distinction or select unambiguous alternative notation. State identifiers, mass sources, units, uncertainty, observation time and the specimen boundary must accompany any numerical application. A neutral-atom, ion or nuclear mass is not automatically interchangeable with the mass allocated to an atom in a declared specimen. If molar masses are used instead, every relevant quantity and conversion must use compatible molar units consistently. [Existing qualified-mass and finite-inventory discussion](technical_scope_supplement.md).

### CALCULATED example with anonymous masses

This example uses arbitrary toy mass units, not measured isotope masses, named elements or a preparation recipe. Element I has conditional atom fractions `(1/2, 1/2)` with qualified toy masses `(1, 2)`. Element II has one populated state with toy mass `3`. Select elemental atomic fractions `(4/5, 1/5)`.

| Quantity | Exact result |
| --- | --- |
| Effective masses M_I and M_II | `(3/2, 3)` |
| Elemental mass fractions w_I and w_II | `(2/3, 1/3)` |
| Conditional mass fractions within element I | `(1/3, 2/3)` |
| Whole-inventory atomic state fractions | `(2/5, 2/5, 1/5)` |
| Whole-inventory mass state fractions | `(2/9, 4/9, 1/3)` |
| Inverse-converted elemental atomic fractions | `(4/5, 1/5)` |

Both whole-inventory vectors sum exactly to one. Each element's state fractions sum to its elemental fraction on the corresponding basis. With a toy inventory of five counted atoms, the integer counts are `(2, 2, 1)` and the allocated masses are `(2, 4, 3)`, totaling nine toy mass units. The mass fractions are therefore `(2/9, 4/9, 3/9)`. Simply multiplying w_I by its atom-count fractions would instead give `(1/3, 1/3)` for element I's two states, which is incorrect for these unequal masses.

## Numerical witnesses: proposed claims 191-193

For these proposals, `k` is the size of the selected constituent support and `i` indexes that support in a stated order. Bounds and fractions use the composition basis selected in claim 186. A tested interval box and a record's accepted target are different objects. Every completed method of claim 186 still assigns a positive normalized target and records its structural, preparation, measurement, property and evidence-status fields.

**Claim 191 - proposed wording.** The method of claim 186, comprising selecting component bounds L_i and U_i for the selected support; testing 0 <= L_i <= U_i <= 1 for every component and sum_i(L_i) <= 1 <= sum_i(U_i); when those tests are satisfied, constructing a preliminary nonnegative normalized witness z_i within the bounds by starting at z_i = L_i and allocating the residual 1-sum_i(L_i) in support order without exceeding any U_i until sum_i(z_i) = 1; and assigning as the positive target fractions of claim 186 a strictly positive normalized witness within those bounds, using the preliminary witness as that target only when every coordinate is positive and otherwise constructing a separate strictly positive witness before target assignment.

**Claim 192 - proposed wording.** The method of claim 191, further comprising, for a box satisfying the tests of claim 191, determining strictly positive feasibility for the selected support by requiring U_i > 0 for every component; when sum_i(L_i) = 1, additionally requiring L_i > 0 for every component and using the lower-bound vector as the positive witness; and when sum_i(L_i) < 1, setting epsilon = min(min_i(U_i), (1-sum_i(L_i))/(2k)), replacing each lower bound by L'_i = max(L_i, epsilon), and constructing a strictly positive normalized witness by allocating the residual 1-sum_i(L'_i) within the unchanged upper bounds; and assigning the resulting positive witness as the target fractions of claim 186.

**Claim 193 - proposed clarification.** The method of claim 186, comprising selecting a k-component box with 0 <= L_i <= U_i <= 1; calculating b_i = max(1, ceiling(D L_i)) and c_i = min(D-k+1, floor(D U_i)) for D = 10^19; accepting the box as numerically feasible on the positive D-grid only when b_i <= c_i for every component and sum_i(b_i) <= D <= sum_i(c_i); and, on acceptance, constructing integers n_i within those bounds with sum_i(n_i) = D by residual allocation and assigning x_i = n_i/D as the positive normalized target fractions of claim 186.

Claims 191 and 192 retain their dependency chain `192 -> 191 -> 186`; claim 193 retains `193 -> 186`. In claim 192, the preliminary construction inherited from claim 191 remains required even when the later strictly positive construction is needed. Claim 193 does not acquire an unstated continuous-witness step from claim 191.

### Proposed accompanying explanation for [0029]-[0032]

Record failure of ordinary feasibility, positive-support feasibility or a chosen grid as a rejected numerical request with its reason. Rejection alone does not complete the positive-target assignment required by claim 186. A box admitting only a zero-containing vector cannot supply a positive target for that selected support. Conversely, a zero in one greedy witness does not establish that the box lacks another, strictly positive witness. A smaller support produced by removing zero coordinates must be recorded as a separate candidate with its own support and bounds.

The epsilon construction is local to a feasible box; it imposes no global minimum fraction and no common denominator on the unrestricted rational domain. For S = sum_i(L_i) < 1 and every U_i > 0, epsilon is positive, every raised lower bound remains within its upper bound, and

```text
sum_i(max(L_i, epsilon)) <= S + k*epsilon
                          <= (1+S)/2 < 1.
```

The original sum_i(U_i) >= 1 leaves enough upper capacity to allocate the remaining residual. Every resulting coordinate is positive. For S = 1, the lower-bound vector is the only feasible vector, so every lower bound must be positive for that support. These are mathematical statements about the box, not preparation or property results.

For claim 193, every positive integer vector summing to D has n_i <= D-k+1. The cap therefore removes no valid positive D-grid vector. The lower/upper sum conditions are necessary, and residual allocation supplies sufficiency. The result x_i = n_i/D is strictly positive, normalized and within the selected bounds. D is an accounting denominator; it does not automatically equal a specimen's atom count, particularly on a mass basis. Grid rejection does not reject the wider rational or real domain. The exact vector `(1/3, 2/3)` remains in the unrestricted rational domain although it is absent from the denominator-10^19 grid.

The original executable and the separate unrestricted executable remain unchanged. The latter uses a different positive-witness allocation procedure from paragraph [0030]'s epsilon construction; equivalent feasibility decisions do not make their procedural steps identical. This proposal preserves the original epsilon formula rather than silently substituting executable steps.

### CALCULATED boundary review

Independent review used standard-library exact fractions and separately enumerated positive vectors. The preserved epsilon procedure agreed with the current positive allocator and denominator-12 positive tuples on 3,615 quarter-endpoint boxes with k = 1-3; 1,318 were feasible. The claim 193 cap, inequalities and integer allocation agreed with independent positive integer tuples on 21,930 bounded cases with toy D = 2-8 and k <= 3. These finite checks supplement the arguments above; they do not exhaust an infinite domain or verify material behavior.

| Box or target | Numerical conclusion and consequence |
| --- | --- |
| Fixed binary `(0, 1)` | Nonnegative feasibility passes; positive binary feasibility fails. A unary candidate is a separate support. |
| Binary L = `(0, 0)`, U = `(1, 1)` | The ordered preliminary greedy witness can be `(1, 0)`. The epsilon construction yields `(3/4, 1/4)`, showing why the zero-containing preliminary witness is not an infeasibility certificate. |
| Fixed binary `(1/3, 2/3)` | Positive and rationally feasible; not on the D = 10^19 grid. |
| Binary L = `(10^-100, 0)`, U = `(10^-99, 1)` | The epsilon construction supplies a positive witness without introducing a domain-wide floor. |
| 138 coordinates with L_i = 0 and U_i = 1 | Epsilon = 1/276 gives a positive normalized witness; this verifies arithmetic, not existence or preparation of 138 elements. |
| Any component U_i = 0 in a selected positive support | Strictly positive feasibility fails for that support. |
| Three lower bounds of 2/5 | Ordinary normalization fails because the lower sum is 6/5. |

## Version-specific support and next review

The following are locations to inspect, not findings of original legal support. The reviewed starting application version is identified above; an actual earlier filed version, if any, would need its own comparison.

| Proposal | Existing textual locations | Added explicit relationship and remaining question |
| --- | --- | --- |
| Claim 169 and [0047] | Original [0010]-[0011], [0046]-[0050], claims 147 and 169-173; qualified-mass discussion in the technical supplement | Preserve y as atom-count conditional fractions; identify conditional mass fractions, per-state mass qualification and both branches. Does the application version relied upon support the particular definitions and their combination? |
| Claim 191 | Original [0029]-[0030], [0032], claims 186 and 191 | Distinguish preliminary z from the positive boxed target; preserve completion of every parent limitation. Is the relationship and successful path clearly expressed? |
| Claim 192 | Original [0030], claims 186, 191 and 192 | Retain the original epsilon procedure, equality case and positive target; distinguish rejected requests from completion. Is the dependency chain consistent with the chosen claim language? |
| Claim 193 | Original [0031], claims 186 and 193 | Make sum(n_i) = D and x_i = n_i/D explicit without importing claim 191. Is the finite-grid alternative and parent target assignment clear? |

An original filed claim can itself supply disclosure, but amendments cannot add unsupported subject matter to the application as filed. Mathematical correctness or an obvious derivation alone does not establish original possession or earlier-date entitlement. Assess the particular definitions and combination against the actual application version relied upon. [USPTO MPEP 2163, II.A.3(b), 2163.06 and 2163.07](https://www.uspto.gov/web/offices/pac/mpep/s2163.html).

Define the controlling basis, variables, alternatives and antecedents clearly. Breadth or alternative wording alone does not establish indefiniteness; a dependent claim must retain every parent limitation and add a further limitation. [USPTO MPEP 2173.03-.04 and 2173.05(e), (h)](https://www.uspto.gov/web/offices/pac/mpep/s2173.html), [MPEP 608.01(n), III](https://www.uspto.gov/web/offices/pac/mpep/s608.html).

For PCT review, examine the corresponding dependency/alternative provisions, clarity and specific priority support. A later amendment may not go beyond the international application as filed. [ISPE/14, paragraphs 5.15-5.18, 5.31-5.32 and 6.07-6.10](https://www.wipo.int/documents/d/pct-system/docs-en-texts-ispe-14.pdf), [PCT Article 34(2)(b)](https://www.wipo.int/en/web/pct-system/texts/articles/a34).

Before adoption, review the exact proposed claim/description set, inherited limitations, technical evidence and support for the selected application version. Any adopted edition needs its own source records, support map and checked rendered documents. The missing applicant contribution, contributor facts, material-specific preparation and characterization evidence, property support, claim-specific legal review and filing facts remain open in the [full-scope audit](full_scope_completion_audit.md) and [evidence intake](applicant_evidence_intake.md). These proposals do not establish a universal bar to later materials patents or turn the particle-record claims into demonstrated physical preparation methods.
