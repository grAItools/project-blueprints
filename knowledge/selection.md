---
type: Reference
title: Choose a project blueprint
description: Choose the foundation, Python baseline, and optional community extension.
tags:
  - selection
  - policy
status: draft
owner: project-blueprints maintainers
generated:
  by: codex/okf-migration-v1
  at: '2026-11-02T13:16:03Z'
stale_after: '2027-05-01T13:16:03Z'
x-requires: []
sources:
  - id: original-readme
    resource: https://github.com/grAItools/project-blueprints/blob/b90867e82cd2a06ec3a01bea8d86d4f9a2882048/README.md
    title: Original README.md
  - id: authority-1
    resource: https://gist.github.com/davidgibsonp/337be9b80b3f03eccd188235c287bb05
    title: https://gist.github.com/davidgibsonp/337be9b80b3f03eccd188235c287bb05
---

# project-blueprints

Recommended project blueprints for modern software development processes leveraging coding agents.

## Contents

- [`harness-agnostic-project.md`](profiles/harness-agnostic.md): Standalone foundation for sharing instructions, skills, and tool configuration across supported AI coding harnesses, for both new and existing project repositories.
- [`python-project.md`](profiles/python.md): Shared Python baseline for solo maintainers and small teams, with strong automated checks and little coordination overhead.
- [`python-project-community.md`](profiles/python-community.md): Extends the Python baseline with contributor governance, compatibility commitments, downstream testing, and shared release/access processes; includes applicable Scientific Python SPEC guidance.

Use the foundation, then the Python baseline. Add the community extension when
external contributions, shared maintainership, downstream consumers, or ecosystem
commitments need formal coordination. Tool configuration and commands are owned
by the baseline and inherited by the extension, including all four blocking
type checkers.

Blueprints link only to their prerequisites; this index owns profile selection.

## Credits

Harness integration reference: [davidgibsonp's gist](https://gist.github.com/davidgibsonp/337be9b80b3f03eccd188235c287bb05).

## Provenance

Migrated from the original blueprints[^original-readme].

External authorities supporting this guidance[^authority-1].

[^original-readme]: Original README.md

[^authority-1]: https://gist.github.com/davidgibsonp/337be9b80b3f03eccd188235c287bb05
