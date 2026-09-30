---
name: github-actions-failure-review
description: Diagnose failing verification, Python correctness lint, or CodeQL checks for this repository using actual run evidence and scoped reproduction.
---

# GitHub Actions failure review

Read [AGENTS.md](../../../AGENTS.md) and [CONTRIBUTING.md](../../../CONTRIBUTING.md). Identify the exact workflow, job, commit, platform, conclusion, and failing log section before proposing a correction. Separate a timeout, missing permission/service, unsupported runtime, or configuration problem from a source defect.

Use available GitHub read tools to inspect run/check output and relevant changed files. Reproduce the failure using the contributor guide and committed configuration when execution is available and authorized. The package verification command is `python -B verify_package.py --self-test`; the configured correctness check is `python -m ruff check --no-cache .`, using the pinned development dependency. Respect the guide if these commands change. Read-only tools cannot run them.

- For integrity/report failures, inspect deliberate edits and source provenance. A reviewed manifest update may accompany a legitimate artifact change; do not suppress checks, overwrite preserved PDFs, or regenerate scientific outputs merely to conceal a mismatch.
- For arithmetic or archive failures, use the corresponding review skill and an independent counterexample. Distinguish fixture isolation, temporary files, platform differences, and real output drift.
- For CodeQL upload/configuration failures, check language categories, job-scoped permissions, runtime compatibility, and whether default setup conflicts with advanced setup. Do not grant broad write permissions or run untrusted PR code through `pull_request_target` to make the job pass.
- Keep official action pins and development dependencies reproducible. Inspect release compatibility before an update. Do not introduce caches, larger runners, or repeated full runs without evidence they address the failure.

When fixing within the task's authorization, make the narrow supported correction, inspect the diff, run meaningful checks, and observe the relevant remote run. Stop repeated retries when the same failure requires unavailable administration, an external service change, or user information; record the exact remaining dependency. Report local versus remote results separately, and do not infer successful CI, deployment, publication, or filing from a local pass.
