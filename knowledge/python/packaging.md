---
type: Blueprint
title: Python packaging and layout
description: Repository layout, distribution metadata, and explicit package contents.
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
    resource: https://hatch.pypa.io/latest/history/hatchling/#1270-2024-11-26
    title: https://hatch.pypa.io/latest/history/hatchling/#1270-2024-11-26
  - id: authority-2
    resource: https://hatch.pypa.io/latest/config/build/#file-selection
    title: https://hatch.pypa.io/latest/config/build/#file-selection
  - id: authority-3
    resource: https://hatch.pypa.io/latest/plugins/builder/sdist/#default-file-selection
    title: https://hatch.pypa.io/latest/plugins/builder/sdist/#default-file-selection
---

# Python packaging and layout

Prerequisite: [Python project profile](../profiles/python.md).

## 3. Repository layout

Use a distribution name such as `project-name` and a valid import name such as
`project_name`. Keep the distinction in metadata, imports, commands, and tests.

```text
project-name/
├── pyproject.toml
├── uv.lock
├── .python-version                 # Development interpreter pin
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── SECURITY.md
├── AI_POLICY.md
├── LICENSE
├── .license-header.txt              # If canonical source notices are adopted
├── .gitignore
├── .gitattributes
├── .pre-commit-config.yaml
├── Makefile                         # Optional thin command aliases
├── src/project_name/
│   ├── __init__.py                  # Deliberate public exports
│   ├── py.typed
│   ├── api.py                       # Optional public facade
│   ├── cli.py                       # Optional CLI implementation
│   ├── __main__.py                  # Optional python -m entry point
│   └── ...                          # Domain modules and subpackages
├── tests/
│   ├── conftest.py
│   ├── test_*.py
│   └── fixtures/                    # Optional input data
├── docs/
│   ├── index.md
│   ├── quickstart.md
│   ├── api.md
│   ├── architecture.md
│   └── ...                          # Configuration, limitations, assets as needed
├── zensical.toml
├── examples/                        # Optional runnable examples
├── scripts/
│   ├── check.py                     # Shared validation and formatting commands
│   ├── release.py                   # Metadata, Git-state, artifact validation
│   ├── package_smoke.py             # Isolated installed-artifact checks
│   └── license_headers.py           # If source notices are adopted
└── .github/
    ├── dependabot.yml               # Or equivalent Renovate configuration
    ├── workflows/
    │   ├── ci.yml
    │   ├── docs.yml
    │   └── release.yml
    └── release-notes/               # Optional curated per-version summaries
```

The tree shows the Python development stack. Keep developer utilities in
`scripts/` and workflow-specific orchestration in `.github/workflows/`.
Git does not retain empty directories: use placeholders only where a directory
must survive cloning.

## 4. Package and dependency contracts

### Metadata and distribution contents

Define the Hatchling backend in `[build-system]`. Put the distribution name,
version, description, README, Python requirement, license, classifiers, URLs,
and runtime dependencies in `[project]` and its subtables. Set
`[tool.hatch.build.targets.wheel].packages = ["src/project_name"]`.
Require `hatchling>=1.27` in `build-system.requires` so the baseline uses modern
license metadata and core metadata 2.4 by default. Keep build constraints
compatible with this floor. See the [Hatchling release history](https://hatch.pypa.io/latest/history/hatchling/#1270-2024-11-26).
Use an SPDX license expression, such as `license = "BSD-3-Clause"`, and
`license-files = ["LICENSE"]`; omit deprecated `License ::` classifiers.

Declare wheel and source-distribution contents deliberately. The wheel must
contain `py.typed`, runtime resources, and required license metadata. The sdist
must contain everything needed to build the wheel without the original Git
checkout. Exclude private settings, scratch trees, environments, and
repository-only configuration from published distributions unless a documented
use requires them. Git ignore rules alone are not a complete distribution
policy. Define an explicit sdist allow-list, for example:

```toml
[tool.hatch.build.targets.sdist]
only-include = ["src", "pyproject.toml", "README.md", "LICENSE"]
```

This default omits repository tests and developer tooling. Include additional
build inputs when needed. If tests are shipped for downstream use, include
their fixtures and helpers and verify they run from the unpacked sdist.
Release validation must assert required and unexpected archive paths, accounting
for generated metadata and files Hatchling always includes. See
[Hatch file selection](https://hatch.pypa.io/latest/config/build/#file-selection)
and the [sdist defaults](https://hatch.pypa.io/latest/plugins/builder/sdist/#default-file-selection).

Keep `__init__.py` small and make public exports deliberate. Use `__all__` when
the package presents a facade. Organize implementation into domain modules,
introducing subpackages when there are meaningful boundaries. For a CLI,
declare `[project.scripts]` and have `__main__.py` call the same function in
`cli.py`, propagating its exit code.

Use `project.version` as the version authority and read the installed version
with `importlib.metadata` when runtime access is needed. If a different version
source is chosen, define it explicitly and validate every derived copy. Do not
silently return a plausible release version from an uninstalled source tree.

## Provenance

Migrated from the original blueprints[^original-python-project].

External authorities supporting this guidance[^authority-1][^authority-2][^authority-3].

[^original-python-project]: Original python-project.md

[^authority-1]: https://hatch.pypa.io/latest/history/hatchling/#1270-2024-11-26

[^authority-2]: https://hatch.pypa.io/latest/config/build/#file-selection

[^authority-3]: https://hatch.pypa.io/latest/plugins/builder/sdist/#default-file-selection
