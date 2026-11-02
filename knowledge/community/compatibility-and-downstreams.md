---
type: Blueprint
title: Community compatibility and downstreams
description: Support commitments, downstream testing, and packager distributions.
tags:
  - community
  - tool-behavior
status: draft
owner: project-blueprints maintainers
generated:
  by: codex/okf-migration-v1
  at: '2026-11-02T13:16:03Z'
stale_after: '2027-01-31T13:16:03Z'
x-requires:
  - profiles/python-community
sources:
  - id: original-python-project-community
    resource: https://github.com/grAItools/project-blueprints/blob/b90867e82cd2a06ec3a01bea8d86d4f9a2882048/python-project-community.md
    title: Original python-project-community.md
---

# Community compatibility and downstreams

Prerequisite: [Python community profile](../profiles/python-community.md).

## 3. Support and compatibility

Publish Python, platform, and dependency support windows, the release lines
receiving fixes, and the process for changing them. For scientific ecosystem
projects, use the SPEC 0 policy described below; otherwise state a policy
suited to the consumers. For new projects, satisfy both the baseline's starting
Python bound and the chosen support-window policy, using the newer minimum
when they differ. Review support decisions at least quarterly and when
preparing releases. Update metadata, CI, contributor instructions, and user
documentation together. The baseline's development interpreter remains tied
to the actual minimum rather than a permanently fixed Python version.

Specify the warning, documentation, and migration period for deprecated public
APIs, plus the release in which removal may occur. Announce supported-version
drops and breaking changes early enough for downstream users to respond.
Document exceptions for urgent security or correctness fixes.

Keep the baseline's locked CI and minimum-dependency tests. Add scheduled tests
with freshly resolved runtime dependencies, and prerelease/development builds
of important upstream dependencies where available. Prepare disposable
environments with controlled test tooling and the intended runtime versions;
invoke the shared test runner using that environment's interpreter without
resynchronizing it to the ordinary project lock. Record what was installed.
Bind nightly dependencies to explicitly selected trusted indexes. Any upload
credential must be scoped, expiring, inventoried, and restricted to a protected
integration-branch publishing environment, never PR runs. Define unique PEP 440
development versions in disposable build trees as validated derivatives of the
baseline version authority; never modify a release tag or the ordinary lock.

Give scheduled failures an owner and a notification path, such as a deduplicated
issue. Keep experimental upstream jobs separate from required PR checks, but
require investigation and resolution of known failures affecting a release.
Maintain representative downstream integration tests or coordinate testing with
consumers when public API changes can break them. Add platforms and compiled
wheel matrices according to the published support promise; compiled projects
still require the baseline's additional native-build design.

## 4. Distributions for downstream packagers

For libraries, extend the baseline sdist allow-list to include maintained tests,
fixtures, and required test helpers. Include other necessary test inputs
deliberately, keeping harness settings and private tooling excluded. Declare
test dependencies in a dedicated dependency group that downstream packagers
can install without the full contributor toolchain. Include `pytest>=9` and
state this requirement in packager instructions; older pytest may silently
ignore the native TOML configuration.

Keep the suite independent of editable installs and checkout-relative runtime
resources. Run the full applicable suite against the installed wheel and a
wheel rebuilt from the sdist in fresh environments outside the checkout,
using tests from the unpacked sdist. For non-library CLIs retaining a minimal
sdist, copy the suite and its inputs from the same verified source commit
instead. Assert that package imports resolve to the installed distribution.
These runs supplement the baseline smoke checks with
only runtime dependencies; test tools must not replace those smoke checks.
Document separately provisioned services or slow integrations and how packagers
run the meaningful offline subset. Add this validation to required PR and
release jobs by reusing the baseline's package validation entry point.

## Provenance

Migrated from the original blueprints[^original-python-project-community].

[^original-python-project-community]: Original python-project-community.md
