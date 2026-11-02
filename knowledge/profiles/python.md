---
type: Blueprint
title: Python project profile
description: Design principles, default development stack, and Python adoption checklist.
tags:
  - profiles
  - tool-behavior
status: draft
owner: project-blueprints maintainers
generated:
  by: codex/okf-migration-v1
  at: '2026-11-02T13:16:03Z'
stale_after: '2027-01-31T13:16:03Z'
x-requires:
  - profiles/harness-agnostic
sources:
  - id: original-python-project
    resource: https://github.com/grAItools/project-blueprints/blob/b90867e82cd2a06ec3a01bea8d86d4f9a2882048/python-project.md
    title: Original python-project.md
---

# Python Project Repository Blueprint

Prerequisite: [Harness-agnostic project profile](harness-agnostic.md).

## Adoption sequence

- [Python packaging and layout](../python/packaging.md).
- [Dependencies and compatibility](../python/dependencies-and-compatibility.md).
- [One executable Python workflow](../python/executable-workflow.md).
- [Python quality and testing](../python/quality-and-testing.md).
- [Documentation, CI, and releases](../python/documentation-ci-and-releases.md).

This blueprint defines a development stack for installable Python libraries
and command-line applications: package layout, dependencies, code quality,
testing, documentation, CI, and releases.

This blueprint builds on the [Harness-Agnostic Project Blueprint](harness-agnostic.md),
which defines shared instructions, skills, and harness configuration. It adds
the Python stack and workflow.

Use this baseline for solo maintainers and small teams that want strong
automated checks with little coordination overhead. The four-checker typing
profile and coverage gate remain deliberate technical commitments.

## 1. Design principles

1. **Separate deliverables from development infrastructure.** Consumers install
   the package under `src/`; repository tooling, tests, and documentation have
   their own locations and distribution policies.
1. **Give each decision one owner.** Metadata and tool scope belong in
   `pyproject.toml`; executable checks belong in shared scripts. Hooks and CI
   reuse those definitions instead of maintaining separate command lists.
1. **Validate promises at their boundaries.** Test public behavior, supported
   platforms, package contents, and installation independently of editable
   development imports. Measure coverage as supporting evidence.
1. **Keep portability explicit.** Development commands work on supported
   platforms. Declare interpreter, shell, system-package, and network
   requirements rather than relying on one developer's environment.
1. **Make checks reproducible and inspectable.** Commit dependency resolution,
   reuse commands locally and in CI, reject stale dependency locks, and publish
   the artifacts that were actually verified.

## 2. Default profile and project decisions

The following is an opinionated default profile. Record deliberate variations
in `CONTRIBUTING.md` and keep commands, CI, and documentation consistent with
them.

| Concern     | Default                                                                                                            |
| ----------- | ------------------------------------------------------------------------------------------------------------------ |
| Packaging   | Hatchling; one typed import package under `src/`                                                                   |
| Environment | uv; committed `uv.lock`; explicit `dev` and `docs` groups                                                          |
| Python      | Start no more than two minor releases behind the latest stable Python; declare and test the actual supported range |
| Style       | Ruff for lint, import ordering, and formatting; 100 columns; Google-style docstrings                               |
| Typing      | mypy, Pyright, Zuban, and Pyrefly as blocking checks                                                               |
| Tests       | pytest and coverage.py; branch measurement; 95% combined coverage gate                                             |
| Hooks       | prek using the pre-commit configuration format                                                                     |
| Docs        | Markdown and Zensical; strict builds                                                                               |
| CI          | GitHub Actions; Linux and Windows correctness tests                                                                |
| History     | Maintained changelog; Conventional Commits optional                                                                |
| License     | BSD-3-Clause when appropriate for the project's ownership and distribution policy                                  |

Four type checkers and a 95% threshold are policy choices, not prerequisites
for Python packaging. Adopt this profile deliberately; document a different
checker set or coverage target when justified. Never quietly weaken an adopted
gate to accommodate a failing change. Select macOS and other platform jobs
when they are part of the support promise. Compiled extensions require an
additional platform-wheel and native-toolchain design beyond this pure-Python
baseline.

Choose a published versioning policy and summarize user-visible changes in
`CHANGELOG.md`. Conventional Commits can drive generated release notes, but
are optional for this baseline. A project adopting them must enforce its
chosen convention consistently. A solo maintainer can review and release
their own work.

## 8. Acceptance checklist

- [ ] Declare distribution/import names, Python/platform support, dependency floors, license, and profile deviations; verify the starting Python minimum is no more than two minor releases behind the latest stable release.
- [ ] Create the `src/` package, public API, typed marker, and any CLI entry points.
- [ ] Define metadata, explicit wheel/sdist contents, dependency groups, interpreter pin, and committed lock.
- [ ] Implement shared check commands; configure Ruff, adopted type checkers, pytest, coverage, and strict docs.
- [ ] Write README, contributor instructions, architecture, changelog, security/AI policies, and relevant user docs.
- [ ] Configure ignore rules, LF checkout, and any adopted source-header policy.
- [ ] Install one locked prek hook setup per clone, including commit-message validation when adopted; validate hooks on Linux CI.
- [ ] Verify the completion gate and compatibility tests on the declared interpreters and platforms.
- [ ] Require the full CI set through branch protection; restrict release-tag creation and prevent updates/deletion, documenting any host limitations and trusted publishing fallback.
- [ ] Run shared package validation on PRs; configure repository/schema/shell/workflow checks and reviewed dependency updates.
- [ ] Test runtime dependency floors separately from development-tool resolution; define the coverage-gating job.
- [ ] Configure documentation deployment and release verification/publication.
- [ ] Assert archive contents and install both wheel and sdist, including promised extras, independently outside the checkout before release.
- [ ] Separate artifact validation from privileged publishing; configure SHA pins, environment-bound trusted publishers, and secure account recovery.

## Provenance

Migrated from the original blueprints[^original-python-project].

[^original-python-project]: Original python-project.md
