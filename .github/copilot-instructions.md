# Repository review instructions

Read [AGENTS.md](../AGENTS.md) and [CONTRIBUTING.md](../CONTRIBUTING.md) for preservation rules, evidence labels, and current check commands. This is a research and drafting package. Mathematical enumeration and successful CI do not establish prepared materials, novelty, patent coverage, publication timing, or filing.

Use these repository skills when their scope matches the change:

- [Exact mathematics review](skills/exact-math-code-review/SKILL.md): rational domains, witnesses, inventory constraints, sampling assumptions, and independent counterexamples.
- [Archive provenance review](skills/archive-provenance-code-review/SKILL.md): source editions, hashes, parsing, uncertainty, identity/status, and attribution.
- [Scientific evidence review](skills/scientific-evidence-code-review/SKILL.md): disclosure assertions, claim-support references, hypothetical entities, and date/filing evidence.
- [Actions failure review](skills/github-actions-failure-review/SKILL.md): actual failing job evidence and scoped reproduction.

Review the diff and affected callers/evidence. Report concrete findings with repository locations, a reproducer or source, impact, and a supported correction; distinguish unresolved questions from confirmed defects. Preserve exact fractions, normalization, source qualifications, supplied PDFs, and recognized versus hypothetical status. Do not fabricate experiments, properties, inventorship, or legal conclusions.

Check execution evidence for `python -B verify_package.py --self-test` and `python -m ruff check --no-cache .`; distinguish local results from completed remote checks. Committing profiles/skills does not prove they ran. SVG drawings and PDF layout require their existing checks and appropriate human inspection; AI review is supplementary.
