---
type: Blueprint
title: Dependencies and compatibility
description: Interpreter policy, dependency contracts, and environment compatibility.
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
    resource: https://docs.astral.sh/uv/concepts/projects/sync/
    title: https://docs.astral.sh/uv/concepts/projects/sync/
  - id: authority-2
    resource: https://docs.astral.sh/uv/concepts/resolution/#resolution-strategy
    title: https://docs.astral.sh/uv/concepts/resolution/#resolution-strategy
---

# Dependencies and compatibility

Prerequisite: [Python project profile](../profiles/python.md).

### Environments and compatibility

Put runtime requirements in `project.dependencies`, consumer-installable
features in `[project.optional-dependencies]`, and checkout tooling in
`[dependency-groups]`. Keep heavy optional test integrations in separate groups.
Set `[tool.uv].default-groups = ["dev"]` explicitly.

Maintain three separate declarations: `requires-python` for consumers,
`.python-version` for the default development interpreter, and the CI matrix
for verified Python/platform combinations. Override the interpreter explicitly
in matrix jobs. Default `.python-version` to the minimum supported Python so
local coverage and the canonical CI coverage job use the same baseline. A
local run on another interpreter supplements that baseline rather than replacing
it. Confirm that development-tool Python requirements do not
accidentally exclude a supported test interpreter; split tool and test groups
or environments if necessary.

Express `requires-python` as a lower bound without an upper cap. The CI matrix
and classifiers record verified versions. When starting a project, identify
the latest officially released stable Python minor version, excluding alpha,
beta, and release-candidate versions. Set the minimum no more than two minor
releases behind it. For example, if Python 3.15 is the latest stable release,
start with `requires-python = ">=3.13"` or a newer minimum. User and dependency
needs may require a newer floor, but must not lower this starting bound.
This rule applies at project inception; review subsequent support changes
under the project's published compatibility policy rather than automatically
changing existing requirements whenever Python releases a new minor version.

Commit `uv.lock`. After editing dependencies, regenerate it and review the
change. CI starts with `uv sync --locked`; `--frozen` uses the lock without
checking freshness, so it cannot replace that validation. The lock controls
the selected development environment; consumers resolve declared package
requirements independently. See [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/).

Give every direct runtime dependency, including dependencies of published
extras, a verified lower bound where the requirement format permits one.
For conditional requirements, verify each bound in an applicable environment.
Use a disposable minimum-Python environment and `lowest-direct` resolution
over the package's runtime requirements, without applying that strategy to
the development groups or modifying the normal lock. Take the direct test-tool
versions from `uv.lock`, constraining the tested direct runtime
dependencies to the selected minima so the tools cannot silently upgrade them.
If these requirements conflict, adjust the test harness or the declared floor.
This checks direct dependency floors, not every possible combination of
transitive dependencies. Test published extras and meaningful optional
integrations separately. See [uv resolution strategies](https://docs.astral.sh/uv/concepts/resolution/#resolution-strategy).

## Provenance

Migrated from the original blueprints[^original-python-project].

External authorities supporting this guidance[^authority-1][^authority-2].

[^original-python-project]: Original python-project.md

[^authority-1]: https://docs.astral.sh/uv/concepts/projects/sync/

[^authority-2]: https://docs.astral.sh/uv/concepts/resolution/#resolution-strategy
