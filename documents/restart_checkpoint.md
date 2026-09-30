# Safe checkpoint and restart guide

This guide explains how to make an interrupted session recoverable. Its existence does not mean the computer is ready to reboot, every chat has finished, a push succeeded or remote checks passed. Record fresh observations at the stopping point. Keep machine paths, private account details and cross-project chat status in a local ignored checkpoint, such as `generated_reports/restart_checkpoint.md`.

## Before closing the session

1. Save intended editor changes explicitly. Check for unsaved editors in every project involved. Do not rely solely on editor backup/restore behavior. [VS Code save and backup guidance](https://code.visualstudio.com/docs/editing/codebasics).
2. Inspect the repository root, branch, full commit ID, status and remote. Record staged, unstaged and untracked files that are intentional. Review their diff; do not reset, blindly stage, stash or discard them to obtain a clean display.
3. Run the relevant package checks from [CONTRIBUTING](../CONTRIBUTING.md). Record the command, Python version, timestamp, exit status and result. For changed verifier behavior include its failure checks. Preserve failure output and next steps if a check fails.
4. Record any commit, pushed branch, pull request and remote-check result for the exact revision. A local commit, a successful push and a passing remote workflow are separate states. Fetch/read remote state when authorized before describing synchronization; do not perform a blind pull or repeat a push with uncertain outcome.
5. Check active tasks and chats. Record which are complete, still running, awaiting an external result or need user input. Save each relevant project's own checkpoint. Moving finished folders later requires a fresh finished-state and local-change check; the materials repository's status says nothing about another chat.
6. Record active background processes and external jobs. Let finite local writes/checks finish or reach a documented safe interruption boundary. A remote workflow may continue while the computer is off; note its exact identifier and pending status. Do not describe all work as stopped from a missing update or timeout.
7. Close the current session only after saving the checkpoint and accounting for active local work. Restart the computer through the normal user-controlled operating-system action after the stopping state is actually verified.

## Local checkpoint template

Fill every field with observed facts, or mark it `not checked`/`pending`. Do not commit private paths or credentials.

```text
Recorded at (UTC):
Repository location:
Repository identity and remote:
Branch / upstream:
Full HEAD commit:
Working tree and staged changes:
Untracked files and why they matter:
Python version / selected editor interpreter:
Latest checks: commands, revision, exit statuses, results:
Commit / push / pull-request state:
Remote workflow: exact revision and observed result or pending job:
Other chats: complete / running / waiting / not checked:
Background work and safe interruption point:
Saved artifact/checkpoint locations:
Next concrete action:
Unresolved evidence, limitations or blockers:
```

A clean stopping point can include intentionally saved uncommitted work if its files, diff and recovery action are recorded. A clean working tree alone is insufficient if an editor still holds unsaved changes or another local process is writing files.

## After restarting

Open the same independent repository checkout outside cloud synchronization and read its local checkpoint, applicable instructions and [current-status addendum](current_status_addendum.md). Confirm repository identity, branch, HEAD, status and remotes before changing anything. Compare these observations with the checkpoint; investigate any mismatch.

Select Python 3.12 through **Python: Select Interpreter** in VS Code, then confirm the actual runtime. Project tasks resolve the selected interpreter through the Python extension. A recommended extension is not proof that it is installed or enabled. If the task cannot resolve the interpreter, use the command-line workflow with a verified Python 3.12 installation and correct working directory. Do not commit an absolute interpreter location. [Official Python guidance](https://code.visualstudio.com/docs/python/environments), [VS Code task guidance](https://code.visualstudio.com/docs/debugtest/tasks).

Run `python verify_package.py` before resuming edits. Routine verification does not need a data download or package installation. The optional nuclear normalized view is reconstructable in memory. A PDG comparison against the original SQLite requires the reviewed external cache and is separate from the ordinary committed-archive checks. If that cache is unavailable, record that source-comparison check as unperformed rather than imply the database is present.

Read pending remote jobs and other chats by their saved identities. Do not duplicate their work or move directories until current state is understood. Fetch before an authorized remote update, inspect divergence and use an appropriate fast-forward when possible. Resume the saved next action, update the checkpoint as state changes, and retain unresolved scientific/legal requirements from the [full-scope audit](full_scope_completion_audit.md).
