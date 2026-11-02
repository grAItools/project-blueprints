---
type: Blueprint
title: Shared instructions and repository layout
description: Canonical instructions, repository layout, and agent maintenance template.
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
  - id: authority-1
    resource: https://agents.md
    title: https://agents.md
---

# Shared instructions and repository layout

Prerequisite: [Harness-agnostic project profile](../profiles/harness-agnostic.md).

### A.1 Directory Layout

```
repo/
  AGENTS.md                  # Shared instructions
  CLAUDE.md                  # "@AGENTS.md" + Claude Code-specific overrides
  .agents/
    README.md                # How to maintain this directory (not AGENTS.md, see A.8)
    skills/<name>/SKILL.md   # Shared skills, with optional references/ and scripts/
    skills-local/.gitkeep    # Private skills (gitignored)
    mcp/servers.json         # Canonical MCP servers
    scripts/
      sync-skills.sh         # Links skills into harness directories
      sync-mcp.sh            # Renders harness MCP configs
  .claude/
    skills/<name> -> ../../.agents/skills/<name>
    settings.json            # Harness-specific
  .omp/                      # oh-my-pi
    rules/                   # Harness-specific
    mcp.json                 # Generated
  .opencode/agents/          # Harness-specific
  opencode.json              # Harness-specific; `mcp` key generated
  .codex/config.toml         # Harness-specific; `[mcp_servers.*]` tables generated
  .mcp.json                  # Generated (Claude Code)
  .gemini/settings.json      # Optional: makes Gemini CLI read AGENTS.md
```

### A.2 Instructions (AGENTS.md)

[AGENTS.md](https://agents.md), the AAIF/Linux Foundation standard, holds the project overview, layout, setup commands, coding standards, git conventions, and a link to `.agents/README.md`. Codex, omp, Copilot, Devin, and other harnesses read it natively. Adapter examples:

- **Claude Code** reads `CLAUDE.md`. Import `AGENTS.md`, then add any Claude Code-specific overrides:

  ```markdown
  @AGENTS.md
  ```

- **Gemini CLI** reads `GEMINI.md` unless `.gemini/settings.json` says otherwise: `{"context": {"fileName": ["AGENTS.md", "GEMINI.md"]}}`.

The Gemini example covers instructions only. Full support also requires skill discovery and MCP adapters (B.6), not provided here.

For nested packages, add files such as `src/package/AGENTS.md`. Codex and omp load each `AGENTS.md` from the repo root to the working directory. Claude Code ignores `AGENTS.md` once `CLAUDE.md` exists, so place a `CLAUDE.md` containing `@AGENTS.md` beside each nested one.

### A.8 `.agents/README.md` Template

Link this maintenance guide from root `AGENTS.md`. Name it `README.md`: omp loads `.agents/AGENTS.md` at the root's level, hiding the root `AGENTS.md`.

```markdown
# .agents/

Harness-agnostic configuration following the [Agent Skills](https://agentskills.io)
and [AGENTS.md](https://agents.md) conventions.

## Supported Harnesses

Record tested support below. When adding or upgrading a harness, verify instruction
loading, duplicate-free skill discovery, and MCP server discovery and connectivity.
Record adapters, limitations, and unsupported harness/skill combinations.

| Harness | Tested version | Validated on | Adapters | Limitations |
|---------|----------------|--------------|----------|-------------|
| <name> | <version> | <YYYY-MM-DD> | <required adapters> | <known limitations or none> |

## Layout

- `skills/` — Shared skills (committed), one directory with a `SKILL.md` each
- `skills-local/` — Private skills (gitignored)
- `mcp/servers.json` — Canonical MCP servers
- `scripts/` — Sync scripts

## Adding a skill

1. Create `.agents/skills/<name>/SKILL.md` with `name` and `description` frontmatter
   (or `npx skills add <repo>@<skill> -y`)
2. Run `.agents/scripts/sync-skills.sh`
3. Commit the skill and its links

## Adding an MCP server

1. Edit `.agents/mcp/servers.json`
2. Run `.agents/scripts/sync-mcp.sh`
3. Commit all generated files

## Rules

- Edit shared skills here, not through `.claude/skills/` links.
- For harness-specific skills (A.3), use a location incompatible harnesses do not
  scan, make the skill portable, or keep its harness-specific location and record
  unsupported combinations under Supported Harnesses.
- Edit MCP servers only in `mcp/servers.json`; the harness MCP configs are generated
- The pre-commit hook syncs skills and blocks commits missing links or new skills
```

## Provenance

Migrated from the original blueprints[^original-harness-agnostic-project].

External authorities supporting this guidance[^authority-1].

[^original-harness-agnostic-project]: Original harness-agnostic-project.md

[^authority-1]: https://agents.md
