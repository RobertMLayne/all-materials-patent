# Project strategy and development decisions

Recorded 30 September 2026 UTC against reviewed repository baseline `f836ba7f781b885c7ba1eb6bd4a89b250ec08c2d`. This revision supplies the selected repository configuration. Installed editor state, exact remote check results and reboot readiness belong in a fresh local checkpoint. [Contribution workflow](../CONTRIBUTING.md).

## Objective and present result

The user selected option 1: all known elements without arbitrary exclusions, with later scope extending to 138 labels, proportions, isotope/particle qualifications and conditional property outcomes. The desired defensive prior-art effect remains all or nearly all later materials patents. The package retains that objective and explicitly records that the universal physical/legal result is unproved. Options excluding selected elements reduce vocabulary coverage while leaving the central disclosure-support problem unresolved. [Original blueprint](pct_defensive_disclosure_blueprint.md), [full-scope audit](full_scope_completion_audit.md).

The package supplies a reviewable description, 199 candidate claims, exact numerical models, dated identity archives and particular literature records. It does not establish blanket unprotected status, a universal preparation route, an applicant technical contribution or a completed patent filing. Public repository access and a patent filing have separate evidentiary records. Original documents remain historical artifacts; the current-status addendum qualifies later publication and procedural facts. [Current-status addendum](current_status_addendum.md).

## Recorded technical decisions

| Decision | Reason and alternative tradeoff | Evidence or limitation |
| --- | --- | --- |
| Separate recognized Z=1…118 from hypothetical Z=119…138 | Retains the requested indexing breadth without treating placeholders as discovered ingredients. Restricting every index to recognized labels would obscure the separately requested hypothetical scope. | Recognition does not establish isotope availability or preparation. [Entity notes](../data/entity_register_notes.md). |
| Define real targets symbolically and rational targets exactly | Finite decimal lists omit values such as 1/3. The original 10^-19 grid remains useful as a bounded subset; the unrestricted rational model has no universal concentration floor or denominator cap. | A finite export is not enumeration of the infinite domain. [Technical supplement](technical_scope_supplement.md). |
| Use canonical supports and joint interval/count constraints | Increasing support tuples remove duplicate set permutations. Normalization, positivity and integer inventories prevent invalid independent endpoint combinations. | Spatial arrangements, phases and isotope partitions require additional descriptions; a count witness is not a specimen. |
| Keep physical identity/preparation/measurement separate from composition addresses | Equal overall fractions can describe different phases, molecules, polymers or composite structures. An address generator cannot fill missing recipes or observations. | Literature entries retain reproduction gaps and third-party provenance. [Reference entries](reference_entry_support.md). |
| Treat contrary property responses as conditional scenarios | A baseline, conditions, mechanism and discriminating test make a proposed response assessable. Listing every sign alone supplies no prediction or necessary inherency. | No universal applicant result exists. [Technical supplement](technical_scope_supplement.md). |
| Preserve raw dated archives and unknown values | Raw bytes, columns, identifiers and provenance permit independent audit. Aggressive numeric coercion, name deduplication or discovery inference would lose source meaning. | NUBASE covers its selected ASCII snapshot; PDG covers declared identity selections. Neither closes all current/future entities or properties. [Nuclear archive](../data/nuclear_archive/README.md), [particle archive](../data/particle_archive/README.md). |
| Use Python 3.12 standard library and offline package verification | The workload is document/data integrity and exact arithmetic. Additional frameworks, package managers, servers and automatic acquisition increase maintenance without a demonstrated requirement. | New workloads may justify dependencies through a separately reviewed decision. [README](../README.md). |
| Preserve the original review PDFs and numbering | Supports version comparison and prevents revised text from being presented as an older artifact. Automatically regenerating originals would erase that distinction. | New filing/review versions need their own exact content, checks and dates. |
| Keep large optional views reconstructable | The full normalized nuclear view can be created in memory; the pinned PDG SQLite is external scratch. Committing duplicates increases distribution size without improving the ordinary offline checks. | Source comparison requiring the SQLite cache is a separate reproducibility check; committed hashes alone are not the source database. |

## Selected local and review conventions

Use one independent checkout per repository outside cloud synchronization, with a reviewed catalog connecting similar projects. Keep active folders stable until their chats finish and local changes are accounted for. Grouping through a catalog avoids conflating similar repositories, forks or unrelated histories. This research package contains its own public project documentation; private multi-repository inventory stays outside it.

Within this repository, maintain the following responsibilities:

| Location | Responsibility |
| --- | --- |
| `documents/` | Drafts, technical/legal review records, versioned PDFs and drawings |
| `data/` | Entity/claim maps, publication observation and attributed source-qualified archives |
| `range_model/` | Exact arithmetic, independent checks, model definitions and deterministic reports |
| `verify_package.py`, `integrity_manifest.json` | Explicit package inventory and reproducible integrity/record checks |
| `.github/workflows/` | Committed CI verification; repository/account settings remain separate |
| `.vscode/`, `.editorconfig` | Reviewable editor/task conventions without machine-specific paths |
| `generated_reports/` | Ignored temporary verification copies and local checkpoint material |
| External reviewed scratch | Optional downloaded databases or acquisition outputs; no automatic download during routine checks |

The proposed editor configuration disables automatic formatting, whitespace trimming and newline insertion, leaves existing encoding/line-ending conventions intact, and marks the two original nuclear source text files read-only in VS Code. EditorConfig `unset` removes inherited property assignments rather than imposing a conversion. These controls reduce accidental rewriting; source hashes remain the check of actual bytes. [EditorConfig specification](https://spec.editorconfig.org/), [VS Code file-setting definitions](https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/files/browser/files.contribution.ts).

Search/watch exclusions are scoped to generated reports, Python caches and the optional large normalized view. Authoritative committed documents and source data remain available for review. This is a scope adjustment, not a measured performance improvement. Global security, privacy, credentials, account plans and unrelated projects are not implied by project files.

The proposed tasks manually run the existing verifier using the selected Python interpreter as a process. They contain no shell-built commands, automatic startup execution, download, push or filing step. Extension recommendations identify Python, Pylance, EditorConfig and Copilot Chat; each installation, effective setting and sign-in requires actual observation. [VS Code task guidance](https://code.visualstudio.com/docs/debugtest/tasks), [extension recommendation guidance](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace#_workspace-recommended-extensions).

Use focused commits and reviewable pull requests, preserve history and inspect every automated review suggestion against current authoritative evidence. Fast-forward updates are preferred after checking local changes and divergence. Git LFS remains an asset-specific decision; ordinary text and the existing small PDFs do not need conversion. Required checks and access settings depend on the actual repository and plan, so document their verified state separately.

## Next decisions needing evidence

Applicant technical contribution, meaningful material-specific support, justified generalizations, claim-by-claim prior-art analysis, filing identities/entitlement and the accepted submitted set remain open. Future work should resolve these gaps with evidence, rather than substitute more labels, decimal points, archives or green checks for the original objective. [Full-scope audit](full_scope_completion_audit.md).

For a new significant choice, add its date, status, concrete problem, selected approach, alternatives, evidence, validation and consequences here. Keep recommendations distinct from completed changes. A claim of speed, coverage, publication, filing or deployed behavior requires its corresponding evidence.
