# Contributing to the materials disclosure package

This is a research and drafting package for a broad defensive-disclosure objective. The requested outcome remains prevention of all or nearly all later materials patents; that outcome is **unproved**. Numerical coverage, document preparation and passing software checks do not establish physical enablement, novelty, inventorship or legal effect. Start with the [README](README.md), [project instructions](AGENTS.md), [full-scope audit](documents/full_scope_completion_audit.md) and [current-status addendum](documents/current_status_addendum.md).

## Start from the right checkout

Use an independent Git checkout outside cloud synchronization. Keep related repositories grouped through a reviewed catalog. Preserve other active chats and working directories; a move needs their work to be finished and their local changes accounted for. Private machine locations and account inventories belong in a local checkpoint or catalog, rather than this public research package.

Before changing files, read applicable parent and repository instructions and inspect:

```console
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
git remote -v
git log -1 --format=fuller
```

Confirm the expected repository, branch and remote. Account for local changes before fetching or updating. After fetching, inspect local/upstream divergence. Use a fast-forward update when appropriate. A divergence, conflict or unknown local change requires analysis; do not discard work, force-push or overwrite it to make a check pass.

## Local tools and verification

The supported verification runtime is Python 3.12 and its standard library. No package installation, web framework, database server or external data download is required for package checks. From the repository root run:

```console
python --version
python verify_package.py
```

The package verifier checks the reviewed inventory, hashes, document/entity/claim records, links and recorded calculation/archive results without writing repository files. For a verifier or integrity-rule change also run:

```console
python verify_package.py --self-test
```

Verification deliberately rejects `-O`, `-OO` and `PYTHONOPTIMIZE`: assertion-based independent checks must be enabled. The runtime remains dependency-free. For development correctness lint, create an ignored `.venv`, install the pinned development dependency, and run:

```console
python -m pip install --only-binary=:all: -r requirements-dev.txt
python -m ruff check --no-cache .
```

Before deliberately refreshing integrity records, inspect the complete diff and run `python tools/update_manifest.py` to report changed hashes. Use `python tools/update_manifest.py --write` only for reviewed changes, then rerun package verification. The helper preserves manifest metadata and checks the explicit inventory; it does not approve scientific changes or replace testing. Dependabot updates require the same reviewed refresh.

Refresh commands serialize through an exclusive `generated_reports/manifest-update.lock`. If a refresh is interrupted, inspect the saved lock, manifest and temporary files before manually removing the lock; never assume a lock is stale merely from its age. External editors do not participate in this protocol, so keep the manifest and reviewed package files unchanged while a refresh runs. A detected byte mismatch stops publication; it is not an atomic compare-and-swap against arbitrary external edits.

The self-test deliberately introduces failures in temporary copies under ignored `generated_reports/`, then removes its temporary copies. Check its exit status and output. A successful result proves the stated package checks, not the requested scientific or legal outcome.

In VS Code, open the repository root and select a Python 3.12 interpreter with **Python: Select Interpreter**. The project task definitions use that selection; they do not commit a machine-specific interpreter path. Run **Tasks: Run Test Task** for ordinary verification, or choose the named failure-check task when relevant. The command-line workflow remains available without editor extensions. [Official Python environment guidance](https://code.visualstudio.com/docs/python/environments), [VS Code task guidance](https://code.visualstudio.com/docs/debugtest/tasks).

## Preserve source evidence and exact arithmetic

Keep the original PDFs, paragraph/claim numbering and preparation dates intact. Update review text through an explicitly identified new version or addendum when historical statements need qualification. Check the current-status addendum before repeating an older publication or filing statement.

Keep ESTABLISHED, CALCULATED, PROPOSED and UNSUPPORTED statements distinct. Attribute literature teachings; state missing reproduction fields. Never invent applicant experiments, physical existence, preparation success, measurements, filing receipts, public-availability dates or patent-status conclusions. A variant does not inherit all evidence from its parent material.

Preserve exact fraction and decimal strings, correlated normalization, and the distinction between the original bounded/grid model and the unrestricted rational model. Do not convert these records through binary floating-point arithmetic. Preserve unknowns, nulls, units, uncertainty operators and original state identifiers. Archive fidelity to a dated source is distinct from current or future completeness.

Do not format or resave the NUBASE fixed-width source or its original header. `.gitattributes` disables Git text conversion for the ASCII source; editor read-only patterns are an additional convenience, not a security boundary or a replacement for hashes. A newly evaluated source needs separate provenance, schema, licensing and verification review. Routine checks stay offline; a source download is a deliberate versioned acquisition into reviewed scratch space.

The proposed editor conventions leave encoding and line-ending normalization unset and disable save-time formatting and whitespace rewriting. Confirm their effective values in the installed editor, including language-specific overrides and other extensions. No editor setting guarantees unchanged bytes after an intentional edit. [EditorConfig specification](https://spec.editorconfig.org/), [VS Code file-setting definitions](https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/files/browser/files.contribution.ts).

## Review a coherent change

Keep changes focused on a concrete research, documentation or verification problem. Explain non-obvious constraints in code comments; avoid comments that merely repeat the next statement. Add independent, meaningful checks for changed arithmetic, parsers, integrity rules or unsafe filesystem behavior. Simple documentation/editor changes need proportionate structural and link review.

When deliberately adding or changing package files, review the verifier's explicit inventory and the integrity manifest together. Explain every intentional inventory/hash change and preserve independent checks. A hash mismatch is evidence to investigate; regenerating the manifest alone does not establish correctness. Ordinary text and the existing small review PDFs remain in regular Git. Evaluate Git LFS for genuinely appropriate large binary assets only after checking attributes, quotas and consumer availability.

Before a commit, inspect the full working diff and staged diff, run the relevant package checks, and review private data, credentials, generated files and source attributions. Stage only understood paths. Use a clear commit message describing the problem and resulting behavior. A pull request should identify validation and material limitations. Fetch and reassess divergence before pushing; preserve history and the established review workflow.

CI runs the committed verification workflow with Python 3.12, read-only permissions, pinned actions, scoped concurrency and a ten-minute job limit. Check the actual result for the exact proposed commit. This workflow does not publish a patent application, submit a filing or establish legal coverage. Repository settings, Copilot access and required branch checks must be verified separately; their presence cannot be inferred from a configuration file.

## Use assistance with accountable decisions

Read project instructions and relevant source records into the task context. Ask assistants to identify changed files, evidence status, exact validation and unresolved work. Review generated code and scientific/legal statements before accepting them. Copilot extension recommendations are not installation, sign-in or proof of a plan entitlement. Confirm the active account and access in the installed editor; retain existing privacy and permission choices. [VS Code extension recommendations](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace#_workspace-recommended-extensions), [official Copilot setup](https://code.visualstudio.com/docs/setup/copilot).

Record significant tradeoffs in the [decision log](documents/workflow_decisions.md). Before interrupting work or restarting the computer, follow the [checkpoint guide](documents/restart_checkpoint.md) and record actual results rather than assuming other chats or remote jobs are finished.
