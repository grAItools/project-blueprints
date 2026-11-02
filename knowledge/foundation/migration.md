---
type: Playbook
title: Migrate an existing repository
description: Assess and migrate instructions, skills, and MCP configuration by layer.
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

# Migrate an existing repository

Prerequisite: [Harness-agnostic project profile](../profiles/harness-agnostic.md).

## Part B: Migration Guide

### B.1 Assessment

```bash
# Harness config files, at any depth
find . \( -name .git -o -name .venv -o -name node_modules \) -prune -o \( \
  -name "AGENTS.md" -o -name "CLAUDE.md" -o -name "GEMINI.md" -o \
  -name ".mcp.json" -o -name "mcp.json" -o \
  -path "*/rules/*.md" -o -path "*/agents/*.md" -o -name "SKILL.md" -o \
  -name "settings.json" -o -name "settings.local.json" -o \
  -name "config.toml" -o -name "opencode.json*" \
\) -print

# Symlinked skills (the search above doesn't follow them)
find . \( -name .git -o -name .venv -o -name node_modules \) -prune -o \
  -type l -path "*skills*" -exec ls -l {} +
```

### B.2 Classification Matrix

| Asset                                                                                                                 | Category                     | Action                                                                                                         |
| --------------------------------------------------------------------------------------------------------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `AGENTS.md`                                                                                                           | Portable                     | Keep at root; create if missing                                                                                |
| `CLAUDE.md` with full instructions                                                                                    | Portable + harness-specific  | Move shared guidance to `AGENTS.md`; retain its import and Claude Code-specific overrides in `CLAUDE.md`       |
| Real skill dirs under `.claude/skills/`, `.omp/skills/`, `.opencode/skills/`, `.codex/skills/`                        | Portable or harness-specific | Move portable skills to `.agents/skills/`; apply A.3's discovery rules and fallback to harness-specific skills |
| `.agents/skills/*/`                                                                                                   | Portable                     | None                                                                                                           |
| `.mcp.json`, `.omp/mcp.json`, `opencode.json` `mcp` key, `.codex/config.toml` `[mcp_servers.*]`                       | Generated                    | Merge into `.agents/mcp/servers.json`, then generate                                                           |
| `.omp/rules/`, `.claude/settings*.json`, other `opencode.json` and `.codex/config.toml` settings, `.opencode/agents/` | Harness-specific             | Leave                                                                                                          |

### B.3 Migration Steps by Layer

Go from lowest to highest risk:

1. **Instructions.** Make `AGENTS.md` canonical: keep it if present, create it otherwise. Move or merge shared guidance from `CLAUDE.md`, leaving only the import and Claude Code-specific overrides there.
1. **Skills.**
   - Check every skills directory from B.2, including in nested packages.
   - Apply A.3's discovery rules and fallback to harness-specific skills.
   - Merge same-named skills with different content by hand.
   - `git mv` each portable skill's whole directory, including resources and scripts, to `.agents/skills/` at the same root or package scope (A.3).
   - Run `sync-skills.sh` and add the hook.
1. **MCP.**
   - Collect server definitions from every supported harness.
   - Convert them to the canonical format (A.4): take the entries without the wrapper (e.g., `jq .mcpServers .mcp.json`), translate harness-specific fields back (opencode `local` with a command array becomes `stdio` with `command` and `args`), and replace literal secrets with placeholders.
   - Resolve conflicting same-named servers by hand.
   - Implement and run `sync-mcp.sh`; diff against the originals and verify every change is intentional.
   - Add the check to pre-commit and CI.
1. **Cleanup.** Add `.agents/README.md` (rename `.agents/AGENTS.md` if present; see A.8), update `.gitignore`, and run `pre-commit run --all-files`.

### B.4 Archetype-Specific Guidance

**Partially migrated project** (already has root `AGENTS.md` and `.agents/skills/`, possibly with a skill-copy script): replace copy scripts with `sync-skills.sh` (symlinks only, A.3), add hooks, cover every supported harness in MCP generation, and land the migration in one commit.

**Repo with submodules and harness-specific rules:**

- Leave `.omp/rules/` as is (A.5); the parent's rules handle only meta-level navigation.
- Migrate each submodule on its own instead of centralizing its config in the parent.
- MCP discovery starts from the session's launch directory, not the edited file: omp reads only that directory; opencode searches up to the Git boundary. A parent-root session uses the parent's servers even when editing a submodule; a submodule-root session uses the submodule's (for omp, start at that exact root). User-level servers apply in both cases. Give submodules their own `.agents/mcp/servers.json` when people start sessions there.

**Coordination hub** (not a code project; many sub-projects in their own repos):

- Allow each supported harness directory in an allow-list `.gitignore` (A.7); add entries when adopting new harnesses.

- Skills are operational workflows (triage tickets, dispatch work to sub-projects); the format is the same.

- `AGENTS.md` is a router rather than a code guide:

  ```markdown
  ## Routing
  - **Billing service**: see `billing/AGENTS.md`
  - **Release notes**: follow `docs/templates/release-notes.md`
  ```

- The hub's MCP servers apply to sessions started at the hub root; sub-projects have their own.

### B.5 Decision Tree

```
Does this item have the same format and compatible meaning across supported harnesses,
using native discovery, links, imports, or settings that point to shared files?
  YES -> Portable: one source at the root or in .agents/; adapt discovery.
  NO  -> Can a generator translate shared data into each supported harness's format without losing meaning?
    YES -> Generated: canonical source in .agents/, rendered by a script.
    NO  -> Harness-specific: leave it, referring to portable sources where possible.
```

### B.6 Ongoing Maintenance

| Task                        | How                                                                                                                                                                                          |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Add or install a skill      | Create it in `.agents/skills/` or `npx skills add`, run `sync-skills.sh`, commit skill and links                                                                                             |
| Add an MCP server           | Edit `.agents/mcp/servers.json`, run `sync-mcp.sh`, commit generated files                                                                                                                   |
| Support a new harness       | Add any needed instruction adapter and MCP rendering; add it to `TARGETS` in `sync-skills.sh` unless it reads `.agents/skills/` natively; validate and record support in `.agents/README.md` |
| Upgrade a supported harness | Recheck instruction loading, skill discovery and behavior, and MCP connectivity; update the tested version, validation date, and limitations in `.agents/README.md`                          |
| Validate a skill            | `skills-ref validate .agents/skills/<name>`                                                                                                                                                  |

______________________________________________________________________

## Provenance

Migrated from the original blueprints[^original-harness-agnostic-project].

[^original-harness-agnostic-project]: Original harness-agnostic-project.md
