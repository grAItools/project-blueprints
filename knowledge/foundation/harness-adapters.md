---
type: Blueprint
title: Harness-specific adapters
description: Ownership boundaries for native harness settings and adapters.
tags:
  - foundation
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
  - id: original-harness-agnostic-project
    resource: https://github.com/grAItools/project-blueprints/blob/b90867e82cd2a06ec3a01bea8d86d4f9a2882048/harness-agnostic-project.md
    title: Original harness-agnostic-project.md
---

# Harness-specific adapters

Prerequisite: [Harness-agnostic project profile](../profiles/harness-agnostic.md).

### A.5 Harness-Specific Files (Leave As-Is)

| File                                                    | Harness     | Contents                                                                                                                                              |
| ------------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.omp/rules/*.md`                                       | omp         | Rules triggered by `description`, `alwaysApply`, `condition`, `globs`. Loaded only from the directory omp starts in, so launch omp from the repo root |
| `opencode.json` (except `mcp`), `.opencode/agents/*.md` | opencode    | Settings, subagents                                                                                                                                   |
| `.codex/config.toml` (except `mcp_servers`)             | Codex       | Models, sandbox, approvals                                                                                                                            |
| `.claude/settings.json`, `.claude/agents/*.md`          | Claude Code | Hooks, subagents                                                                                                                                      |
| `.claude/settings.local.json`                           | Claude Code | Machine-local permissions (gitignored)                                                                                                                |

Do not sync between these formats. Keep shared guidance in `AGENTS.md` and harness-specific files thin: an `.omp/rules/` rule adds only its trigger and a link to shared guidance; a Claude Code hook calls a script in `.agents/scripts/`.

## Provenance

Migrated from the original blueprints[^original-harness-agnostic-project].

[^original-harness-agnostic-project]: Original harness-agnostic-project.md
