---
type: Blueprint
title: Documentation, CI, and releases
description: Documentation, workflow security, and installed-artifact release validation.
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
    resource: https://diataxis.fr/
    title: https://diataxis.fr/
  - id: authority-2
    resource: https://learn.scientific-python.org/development/guides/docs/
    title: https://learn.scientific-python.org/development/guides/docs/
  - id: authority-3
    resource: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
    title: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
  - id: authority-4
    resource: https://learn.scientific-python.org/development/guides/security/
    title: https://learn.scientific-python.org/development/guides/security/
  - id: authority-5
    resource: https://docs.astral.sh/uv/concepts/projects/build/
    title: https://docs.astral.sh/uv/concepts/projects/build/
  - id: authority-6
    resource: https://docs.astral.sh/uv/reference/cli/#uv-build
    title: https://docs.astral.sh/uv/reference/cli/#uv-build
  - id: authority-7
    resource: https://twine.readthedocs.io/en/stable/changelog.html#twine-6-1-0-2025-01-17
    title: https://twine.readthedocs.io/en/stable/changelog.html#twine-6-1-0-2025-01-17
  - id: authority-8
    resource: https://docs.pypi.org/trusted-publishers/adding-a-publisher/
    title: https://docs.pypi.org/trusted-publishers/adding-a-publisher/
  - id: authority-9
    resource: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch
    title: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch
---

# Documentation, CI, and releases

Prerequisite: [Python project profile](../profiles/python.md).

## 7. Documentation, CI, and release

### Documentation and contributor policy

Keep the README focused on purpose, installation, one working example, and
links. Put usage, public API, configuration, architecture, and limitations in
`docs/`. `CONTRIBUTING.md` owns the contributor workflow, tool prerequisites,
support matrix, completion gate, and release procedure. Build Zensical with
strict warning handling.

Consider the [Diátaxis framework](https://diataxis.fr/) for organizing user
documentation: tutorials guide learning, how-to guides address specific tasks,
reference describes APIs and configuration, and explanation develops concepts
and design rationale. Use these distinctions to shape pages and navigation as
the documentation grows, without requiring a fixed directory structure.

The API page may be handwritten; update it alongside public behavior and
cross-check its names and examples against the package. Automated extraction
is optional and requires a separately verified documentation integration.
Zensical is supported by the Scientific Python guide; Sphinx or another engine
is a project choice when cross-references, output formats, or API tooling
justify it. See the guide's [documentation options](https://learn.scientific-python.org/development/guides/docs/).
Keep the foundation blueprint's project instructions concise
and link to `CONTRIBUTING.md` and the shared commands for authoritative workflow
details rather than maintaining a second command reference.

Keep `SECURITY.md` brief: supported release lines and a private vulnerability
reporting channel monitored by the maintainer. Use two-factor authentication
on project services and keep account recovery instructions and recovery codes
in a secure location outside the repository. `AI_POLICY.md` states disclosure,
human responsibility for submitted work, and expectations for review
responses. Link both policies from contributor instructions and link the AI
policy from `AGENTS.md`; the harness adapters do not replace contributor policy.

### Continuous integration and maintenance

CI validates PRs and pushes to the integration branch. Sync with `--locked`,
selecting the `docs` group in the documentation job. Run the Linux hook job
and the completion subcommands as described above; test every declared Python
minor version on Linux. Cover at least the minimum and newest supported Python
on Windows using `scripts/check.py test`, without the merged shell-hook suite.
Linux versions other than the coverage baseline also use `scripts/check.py test`.
Add platforms when promised. Static checks run once on their declared
interpreter. Configure `.gitattributes` for LF, use explicit UTF-8 and newline
handling in test writers, and make path and interpreter discovery portable.

Run `scripts/check.py package` in an unprivileged job on PRs and integration
pushes. It delegates to `scripts/release.py` and `scripts/package_smoke.py`
for the artifact validation described below, without requiring a release tag
or a changelog entry for an unreleased version. The same implementation runs
for a release, alongside its additional version and Git-state checks.

Require the full CI set through branch rulesets or equivalent protection on
integration and maintained release branches; the baseline needs no independent
review requirement. Restrict creation of `v*` tags to designated release
maintainers. Use separate tag rulesets for creation and for preventing updates
and deletion, so creation privileges do not also permit rewriting release tags.
Enable immutable releases where available. If the host or plan cannot enforce
these protections, disable automatic tag-triggered publication and require a
trusted release operator to verify branch eligibility and the full required CI
set outside workflow code from the tagged commit before publishing the retained
artifacts. A green local completion gate is insufficient. See [GitHub rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets).

Configure Dependabot or Renovate for reviewed updates to Actions, Python
dependencies and `uv.lock`, and external hooks when present. Group related
updates and require the normal CI checks. Choose a regular schedule and record
how the lock is refreshed; local hooks use the versions from that lock.

Only trusted integration-branch runs deploy documentation. If deployment
follows another workflow, use the exact verified commit or artifact, not the
branch's newer tip. Give validation read-only permissions and grant deployment
or publishing permissions only to the relevant jobs. Pin external actions to
verified full commit SHAs with readable version comments, and pin tools.
Maintain those pins through reviewed updates. Never run untrusted PR code
with publishing credentials or a privileged `pull_request_target` checkout.
Use workflow schema checks and Zizmor to enforce this policy. See the guide's
[CI security recommendations](https://learn.scientific-python.org/development/guides/security/).

### Release and artifact validation

The default release starts from a `v<version>` tag. A solo maintainer can
initiate it after the required checks pass; no second approver is required.

An automated release follows this contract:

1. Resolve a `v<version>` tag to an immutable commit on the integration branch
   or a protected maintained release branch.
   Require agreement with package metadata, changelog, and any
   other version copies; do not infer review or passing CI from ancestry alone.
1. Verify the full required CI set on that commit, including compatibility
   and applicable dependency-floor jobs, by running it or checking its exact
   commit results. Reject unexplained checkout changes, a stale lockfile,
   inconsistent release metadata, or incomplete required checks.
1. Build into an empty output directory with `uv build --no-sources`. This
   disables uv source overrides during build dependency resolution; it neither
   tests runtime dependency availability nor substitutes for installation
   checks. A development lockfile alone does not pin every isolated build
   requirement. Pin build tooling or supply build constraints when stronger
   repeatability is required. See [uv distribution builds](https://docs.astral.sh/uv/concepts/projects/build/)
   and its [CLI reference](https://docs.astral.sh/uv/reference/cli/#uv-build).
1. Validate the wheel and sdist against the archive policy. Install
   each independently into a fresh environment outside the checkout, with only
   declared runtime dependencies, at least on the minimum supported Python.
   Verify every promised extra from the built artifacts in separate environments
   or documented compatible combinations. Import the public API, check installed
   version and `py.typed`, run representative behavior, and exercise CLI entry
   points when present. Do not let `PYTHONPATH`, an editable install, or a
   cached project wheel substitute for building the sdist.
   Keep the smoke assertions standard-library-only apart from imports of the
   installed package and its declared dependencies; test tools must not mask
   missing runtime requirements. Validate distribution metadata and README
   rendering with `twine check --strict`. Lock metadata-compatible tools in
   the dev group: at least `twine>=6.1` and `packaging>=24.2` for Metadata 2.4.
   See the [Twine changelog](https://twine.readthedocs.io/en/stable/changelog.html#twine-6-1-0-2025-01-17).
1. Retain those exact verified artifacts with a hash manifest. A separate
   publishing job creates the public GitHub release and, only if enabled,
   publishes to PyPI using those files. Use OIDC trusted publishing, binding
   each PyPI/TestPyPI publisher to the exact repository, workflow filename,
   and publishing environment name; restrict that environment to release refs.
   Document any service limitation requiring another authentication method.
   The job retrieves the verified artifacts and does not build, install, or
   import project code. Retain publisher-provided attestations when supported.
   Release builds and publishing jobs must not restore caches. Serialize all
   publication triggers per version without cancelling an in-progress publish.
   Recover partial publication using the retained artifacts and only the failed
   steps, verifying already published files against their hashes; never rebuild,
   overwrite an existing tag, or replace an occupied version on retry.

Configure publisher identity according to [PyPI's trusted-publisher documentation](https://docs.pypi.org/trusted-publishers/adding-a-publisher/).

Manual release dispatch is optional. If implemented, resolve its input to the
immutable tag/commit before validation, apply the same checks, and document
input handling. Dispatch the workflow on the release tag ref allowed by the
publishing environment; a tag supplied only as an input to a run on another
ref is insufficient. Require any tag input to match that execution ref. See
[workflow dispatch refs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch).
It uses the same publication serialization and recovery rules
as tag-triggered releases. Keep this orchestration outside ordinary check commands.

Installation from a repository, publication of release artifacts, and
publication to a package index are distinct capabilities. State which are
supported and document any repository/environment setup required for release.

## Provenance

Migrated from the original blueprints[^original-python-project].

External authorities supporting this guidance[^authority-1][^authority-2][^authority-3][^authority-4][^authority-5][^authority-6][^authority-7][^authority-8][^authority-9].

[^original-python-project]: Original python-project.md

[^authority-1]: https://diataxis.fr/

[^authority-2]: https://learn.scientific-python.org/development/guides/docs/

[^authority-3]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets

[^authority-4]: https://learn.scientific-python.org/development/guides/security/

[^authority-5]: https://docs.astral.sh/uv/concepts/projects/build/

[^authority-6]: https://docs.astral.sh/uv/reference/cli/#uv-build

[^authority-7]: https://twine.readthedocs.io/en/stable/changelog.html#twine-6-1-0-2025-01-17

[^authority-8]: https://docs.pypi.org/trusted-publishers/adding-a-publisher/

[^authority-9]: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch
