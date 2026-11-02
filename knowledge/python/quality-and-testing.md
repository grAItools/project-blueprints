---
type: Blueprint
title: Python quality and testing
description: Repository checks, four blocking type checkers, tests, and coverage.
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
  - id: authority-1
    resource: https://github.com/KyleKing/mdformat-mkdocs
    title: https://github.com/KyleKing/mdformat-mkdocs
  - id: authority-2
    resource: https://learn.scientific-python.org/development/guides/style/
    title: https://learn.scientific-python.org/development/guides/style/
  - id: authority-3
    resource: https://github.com/RobertCraigie/pyright-python
    title: https://github.com/RobertCraigie/pyright-python
  - id: authority-4
    resource: https://github.com/microsoft/pyright/blob/main/docs/configuration.md
    title: https://github.com/microsoft/pyright/blob/main/docs/configuration.md
  - id: authority-5
    resource: https://learn.scientific-python.org/development/guides/pytest/
    title: https://learn.scientific-python.org/development/guides/pytest/
  - id: authority-6
    resource: https://coverage.readthedocs.io/en/latest/config.html#run-relative-files
    title: https://coverage.readthedocs.io/en/latest/config.html#run-relative-files
---

# Python quality and testing

Prerequisite: [Python project profile](../profiles/python.md).

## 6. Code quality and tests

### Repository checks

Include file hygiene in `lint`: conflict markers, case-conflicting paths,
broken symlinks, oversized additions, YAML syntax, trailing whitespace, final
newlines, and line endings. Reuse maintained checks such as pre-commit-hooks
through the shared runner, with their Python dependencies in the locked dev
group. Check configuration schemas with `validate-pyproject` and
`check-jsonschema` for GitHub workflows and the selected dependency updater.
Run ShellCheck over maintained shell scripts, including the foundation's
hidden scripts, and Zizmor over workflows. Lock their Python-distributed
runners in the dev group where supported, otherwise pin the executable
separately and document how contributors obtain it.

Build filename lists from tracked and non-ignored untracked maintained files,
including hidden paths, rather than relying on staged changes. Pass explicit
paths to filename-based checks and use `--enforce-all` for
`check-added-large-files` when checking the whole project. Apply documented
exclusions to generated files and fixtures whose contents must be preserved.

Use codespell for spelling and mdformat with locked dialect plugins for
Markdown. Preserve YAML skill frontmatter, GFM tables, and documentation
extensions: explicitly include `mdformat-mkdocs`, `mdformat-gfm`, and
`mdformat-front-matters` in the locked dev group for compatible Zensical
syntax, and enable those extensions when using its Python
API. Verify representative skills and documentation by formatting round-trip
and rendered output; exclude any unsupported dialect rather than rewriting
its meaning. Never run plain CommonMark formatting over those files.
See the [plugin's syntax and dependency documentation](https://github.com/KyleKing/mdformat-mkdocs).
Format Python examples with a verified integration using the selected Ruff
version; preserve intentionally incomplete examples. Include maintained
documentation and utilities under hidden directories.
`lint` checks without modifying files; `fmt` applies the supported fixes.
Hooks call these same commands rather than implementing a second check list.
See the guide's [style checks](https://learn.scientific-python.org/development/guides/style/).

### Python linting and typing

Use Ruff for formatting and the adopted lint rules. Enable the `D` rule family
with `[tool.ruff.lint.pydocstyle].convention = "google"`, relaxing missing
docstring rules where appropriate. Pick the remaining rule families explicitly
or use `ALL` with explained exclusions, and avoid redundant formatters. Adopt
module imports, absolute imports, and import-alias conventions where they help
the public design; allow intentional facade re-exports. Do not assume Ruff
proves that every imported symbol is a module.

For the default four-checker profile, configure mypy in strict mode and Pyright
in standard mode over package source and maintained utilities. Configure Zuban
and Pyrefly to include maintained tests, relaxing test signature requirements
where appropriate while checking their bodies. The wider pair covers tests
without requiring annotations on every fixture-driven function; mypy and
Pyright focus on the typed package and utilities. Give Zuban an explicit section
when its scope differs from mypy's. Resolve each checker's interpreter from
the active environment and explicitly set each checker's target Python version
to the package minimum, including when its own execution interpreter is newer.
Avoid hard-coded `.venv/bin/python` paths.

Pyright's Python wrapper targets a checker version but may provision Node
and npm assets outside the Python environment. Use `pyright[nodejs]` in the
locked dev group or provision a pinned Node runtime separately, and document
first-run network/cache requirements. Avoid environment overrides that select
an unpinned checker version. See the [wrapper documentation](https://github.com/RobertCraigie/pyright-python).

Keep deliberate invalid input and generated snapshots separate from maintained
test harness code. Exclude data only where checking or formatting it would
destroy the test's purpose. Verify hidden-path discovery and project-mode
exclusions for each checker; a successful exit must not conceal an empty scope.
Use accurate annotations and narrowing, with narrow documented suppressions
only at unavoidable boundaries. Standard `# type: ignore[code]` comments can
affect multiple checkers; do not treat them as private to the checker that
motivated them. Set Pyright's `enableTypeIgnoreComments = false` and use
`# pyright: ignore[rule]` for Pyright-specific exceptions. Enable unused-ignore
reporting where available, including `reportUnnecessaryTypeIgnoreComment` for
Pyright. Inspect the unsuppressed diagnostics before adding a shared ignore,
then rerun all adopted checkers for regressions; a passing rerun cannot prove
that the comment has hidden no other diagnostic. See
[Pyright configuration](https://github.com/microsoft/pyright/blob/main/docs/configuration.md).

### Tests and coverage

Require pytest 9 or newer in the development environment and configure its
native TOML section in `pyproject.toml`:

```toml
[tool.pytest]
minversion = "9.0"
testpaths = ["tests"]
strict = true
addopts = ["-ra"]
filterwarnings = ["error"]
log_level = "INFO"
```

Strict configuration, markers, and expected failures catch mistakes that
coverage cannot. Register custom markers and add narrow, explained warning
exceptions rather than hiding all dependency warnings. Enable `--showlocals`
locally when useful, considering whether traceback values contain secrets.
Keep `tests/` non-importable unless its design requires otherwise. See the
guide's [pytest configuration](https://learn.scientific-python.org/development/guides/pytest/).

Start with focused `tests/test_*.py` files. Add layers such as `unit/`,
`integration/`, `behavior/`, `golden/`, and `perf/` when the suite benefits.
Test supported public behavior, error behavior, and compatibility boundaries.
Use property, differential, corpus, and performance checks when the product's
claims need them; keep expensive external checks scheduled or manually
triggered and document when a change requires them before merging.

Configure coverage.py with the whole package as `source`, `branch = true`, and
`fail_under = 95` for the default profile. This threshold combines statements
and branches; it does not require 95% branch coverage independently. Produce
terminal, XML, and HTML reports even when tests or the threshold fail, while
preserving the failing final result. Subprocess execution needs separate
measurement configuration; do not count it implicitly.

By default, the Linux job on the minimum supported Python enforces this
threshold; other matrix jobs run correctness tests without a coverage gate.
If substantial platform-specific code requires combined measurement, collect
compatible branch data in the relevant jobs, configure relative paths and
path mappings, and apply the threshold after combining. Do not silently
exclude platform code to preserve a single-platform score. See
[coverage data paths](https://coverage.readthedocs.io/en/latest/config.html#run-relative-files).

Test architecture or documentation contracts where drift would matter. Ensure
examples run. An editable checkout test run does not establish that a wheel
contains required files or declares every runtime dependency; release
verification must exercise installed artifacts separately.

## Provenance

Migrated from the original blueprints[^original-python-project].

External authorities supporting this guidance[^authority-1][^authority-2][^authority-3][^authority-4][^authority-5][^authority-6].

[^original-python-project]: Original python-project.md

[^authority-1]: https://github.com/KyleKing/mdformat-mkdocs

[^authority-2]: https://learn.scientific-python.org/development/guides/style/

[^authority-3]: https://github.com/RobertCraigie/pyright-python

[^authority-4]: https://github.com/microsoft/pyright/blob/main/docs/configuration.md

[^authority-5]: https://learn.scientific-python.org/development/guides/pytest/

[^authority-6]: https://coverage.readthedocs.io/en/latest/config.html#run-relative-files
