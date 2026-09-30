---
name: exact-math-code-review
description: Review changes to exact composition models, rational witnesses, inventories, or trace-sampling calculations in pull requests.
---

# Exact mathematics review

Read [AGENTS.md](../../../AGENTS.md) and [CONTRIBUTING.md](../../../CONTRIBUTING.md) for preservation rules and current verification commands. Review changed code together with affected examples, reports, callers, and independent checks under `range_model/`.

- Preserve the distinction between `composition_ranges.py` with its 10^-19 positive floor, `unrestricted_compositions.py` with arbitrary positive rational coordinates and no domain-wide denominator cap, and the symbolic real domain. CLI export limits bound an export, not the domain. Irrational coordinates are not exhaustively enumerated.
- Check exact Fraction/integer arithmetic, strictly positive selected support, normalization, interval endpoints, and rational-box or fixed-denominator feasibility. Component intervals become coupled after normalization. Look for duplicate rational representatives, omitted denominators/supports, unjustified rounding, and witnesses outside the stated bounds. Use independently derived small cases or counterexamples rather than repeating the implementation.
- For exact specimen fractions, check integer species counts summing to N and the primitive denominator's divisibility into N. Joint element/isotope/particle partitions must satisfy joint integer allocations; feasible marginal counts alone do not suffice. Distinguish exact counts from expected reservoir fractions.
- Separate uniform subset inclusion of a specified atom, independent reservoir sampling, and actual detection. State sampling assumptions and valid formula domains. For independent draws, logarithmic miss-probability formulas require 0 < p < 1 and 0 < alpha < 1; p = 0 has no finite successful draw count, and p = 1 needs one draw. Zero-count confidence bounds require n >= 1. Detection additionally needs a calibrated measurement model.

Inspect recorded CI or authorized execution of the contributor-guide checks. Read-only reviewers must report checks as unrun if no execution evidence exists. For each material finding, identify the location, failing input or proof gap, consequence, and supported fix. An arithmetic witness or passing finite test does not prove chemical preparation, physical stability, unlimited numerical precision, novelty, or a universal bar to future patents.
