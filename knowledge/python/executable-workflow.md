---
type: Blueprint
title: One executable Python workflow
description: Shared check commands, locked environments, and hook ownership.
tags:
  - python
  - tool-behavior
status: draft
owner: project-blueprints maintainers
generated:
  by: codex/okf-migration-v1
  at: '2026-11-02T13:16:03Z'
stale_after: '2027-01-31T13:16:03Z'
x-requires:
  - profiles/python
sources:
  - id: original-python-project
    resource: https://github.com/grAItools/project-blueprints/blob/b90867e82cd2a06ec3a01bea8d86d4f9a2882048/python-project.md
    title: Original python-project.md
---

# One executable Python workflow

Prerequisite: [Python project profile](../profiles/python.md).

## 5. One executable workflow

Use `scripts/check.py` as the command owner. It invokes tools with argument
lists and the active Python environment, resolves paths relative to the
repository, and propagates failures. Keep its subcommand definitions in one
place; hooks, CI, and optional Make targets call those definitions.
Use portable Python for orchestration rather than requiring Make on Windows.
Provide `--help` with the available subcommands and print invoked checks so
contributors can inspect failures. uv owns environments; this runner owns
commands. Add an environment runner such as Nox only when its isolation or
matrix management is needed, preserving one authoritative command definition.

Implement the following interfaces:

| Subcommand of `scripts/check.py` | Responsibility                                                                                           |
| -------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `lint`                           | Ruff and repository/configuration checks below; adopted source-header check                              |
| `type`                           | Every adopted type checker over its configured project scope                                             |
| `test`                           | pytest without coverage                                                                                  |
| `test-minimum`                   | Disposable runtime-dependency-floor environment and tests described in the compatibility contract        |
| `coverage`                       | pytest under coverage.py; reports and the configured threshold                                           |
| `docs`                           | Zensical strict build using the docs dependency group                                                    |
| `check`                          | `lint`, `type`, `coverage`, and `docs`; no autofixing                                                    |
| `package`                        | Shared build, archive, metadata, and installed-artifact checks; no publishing or release-tag requirement |
| `fmt`                            | Explicitly requested source and prose fixes and formatting                                               |

The local completion gate is `scripts/check.py check`: all four validation
subcommands above must pass. The full required CI set also includes `package`,
the declared Python/platform correctness matrix, and `test-minimum` for
applicable runtime requirements and extras. Every applicable check must pass
on the exact commit before merging or releasing; skipped checks are not passes.
Invoke subcommands with
`uv run --locked python scripts/check.py <subcommand>`, adding `--group docs`
before `python` for `docs` and `check`. Dependencies are resolved before the
Python runner starts. Run the local completion gate with:

```bash
uv sync --locked --group docs
uv run --locked prek install
uv run --locked --group docs python scripts/check.py check
```

Configure both `pre-commit` and `commit-msg` installation when using a
Conventional Commits hook; keep ordinary file hooks out of the `commit-msg`
stage. Every clone installs its own hooks. Pin uv in CI and document the
required local version. Run Ruff and Python checkers from the locked project
environment; pin any separately downloaded hook environments too. Use local
`language: system` hooks whose entries call these shared commands through
`uv run --locked`. The default commit-time checks are `lint` and `type`;
tests, coverage, and documentation builds belong to the completion gate.

Keep tool scope and exclusions in `pyproject.toml`, including maintained
utilities under hidden directories. Whole-project hooks use
`pass_filenames: false`; changing a configuration file must trigger the checks
it affects. Use `always_run: true` for checks that must notice deletions or
configuration-only changes. Merge this stack's hooks with the foundation
blueprint's hooks in one configuration and preserve each
blueprint's ownership of its checks. Use the locked prek runner wherever that
blueprint says `pre-commit`; install one hook manager per clone. Shell-based hooks
retain the foundation blueprint's platform prerequisites. Windows contributors
using those hooks must satisfy those prerequisites; Python correctness tests
do not depend on running the entire hook suite.

`prek run --all-files` selects Git-known files for filename-based hooks; it may
miss untracked new files. The completion gate must discover maintained source
directly as well. Run the configured hook suite once in a Linux CI job so local
installation is not the only enforcement point. CI can distribute completion
subcommands across jobs: when the hook job already runs the full `lint` and
`type` scopes, separate jobs run `coverage` and `docs` without repeating them.
All those required jobs together satisfy the completion gate.
The all-files run does not exercise `commit-msg` hooks. When Conventional
Commits are adopted, enforce them separately in CI against PR commit messages,
or the PR title when squash merging is the required merge policy.

Local hooks reuse the locked environment to avoid separate tool versions and
command lists. The GitHub Actions hook job is the default enforcement service;
pre-commit.ci is optional only after verifying that its environment and network
restrictions support the selected hooks.

## Provenance

Migrated from the original blueprints[^original-python-project].

[^original-python-project]: Original python-project.md
