---
type: Blueprint
title: Harness-agnostic project profile
description: Scope, shared configuration principles, and foundation adoption checklist.
tags:
  - profiles
  - policy
status: draft
owner: project-blueprints maintainers
generated:
  by: codex/okf-migration-v1
  at: '2026-11-02T13:16:03Z'
stale_after: '2027-05-01T13:16:03Z'
x-requires: []
sources:
  - id: original-harness-agnostic-project
    resource: https://github.com/grAItools/project-blueprints/blob/b90867e82cd2a06ec3a01bea8d86d4f9a2882048/harness-agnostic-project.md
    title: Original harness-agnostic-project.md
  - id: authority-1
    resource: https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
    title: https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
  - id: authority-2
    resource: https://agents.md
    title: https://agents.md
  - id: authority-3
    resource: https://github.com/agentsmd/agents.md
    title: https://github.com/agentsmd/agents.md
  - id: authority-4
    resource: https://aaif.io/
    title: https://aaif.io/
  - id: authority-5
    resource: https://agentskills.io/specification
    title: https://agentskills.io/specification
  - id: authority-6
    resource: https://agentskills.io/client-implementation/adding-skills-support.md
    title: https://agentskills.io/client-implementation/adding-skills-support.md
  - id: authority-7
    resource: https://github.com/agentskills/agentskills
    title: https://github.com/agentskills/agentskills
  - id: authority-8
    resource: https://github.com/vercel-labs/skills
    title: https://github.com/vercel-labs/skills
  - id: authority-9
    resource: https://modelcontextprotocol.io
    title: https://modelcontextprotocol.io
  - id: authority-10
    resource: https://code.claude.com/docs/en/skills
    title: https://code.claude.com/docs/en/skills
  - id: authority-11
    resource: https://github.com/anthropics/claude-code/issues/31005
    title: https://github.com/anthropics/claude-code/issues/31005
  - id: authority-12
    resource: https://learn.chatgpt.com/docs/build-skills
    title: https://learn.chatgpt.com/docs/build-skills
  - id: authority-13
    resource: https://learn.chatgpt.com/docs/config-file/config-basic
    title: https://learn.chatgpt.com/docs/config-file/config-basic
  - id: authority-14
    resource: https://opencode.ai/docs/config/
    title: https://opencode.ai/docs/config/
  - id: authority-15
    resource: https://github.com/can1357/oh-my-pi/tree/main/docs
    title: https://github.com/can1357/oh-my-pi/tree/main/docs
  - id: authority-16
    resource: https://www.ssw.com.au/rules/symlink-agents-to-claude
    title: https://www.ssw.com.au/rules/symlink-agents-to-claude
---

# Harness-Agnostic Project Blueprint

## Adoption sequence

- [Shared instructions and repository layout](../foundation/instructions.md).
- [Portable agent skills](../foundation/skills.md).
- [Shared MCP configuration](../foundation/mcp-configuration.md).
- [Harness-specific adapters](../foundation/harness-adapters.md).
- [Harness automation and ignore rules](../foundation/automation.md).
- [Migrate an existing repository](../foundation/migration.md).

Share project instructions, skills, and tool configuration across AI coding
harnesses through small, explicit adapters. Part A covers new repositories;
Part B covers migration.

This standalone foundation defines harness integration for projects in any
language and for coordination hubs.

## Scope and Terminology

A **harness** surrounds a model with software and configuration for loading instructions, exposing tools, managing context, and enforcing execution policies. An **agent** combines a model and a harness to perform tasks; one harness implementation can support multiple agents or subagents with different roles. [LangChain's model-plus-harness definition](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness) includes instructions, tools, and skills in the harness.

This blueprint distinguishes **harness implementations** (Claude Code, Codex CLI, oh-my-pi, opencode) from the **project inputs** they load (instructions, skills, MCP definitions). "Across harnesses" means across implementations; "harness-specific" means tied to one implementation. Below, **Codex** means Codex CLI and **omp** means oh-my-pi.

**Harness-agnostic** means shared guidance and workflows are independent of any single implementation. Supported harnesses consume canonical sources through native discovery, imports, links, settings that point to shared files, or generated configuration. Adapters and validation are still required; behavior can differ across harnesses and models.

Keep the established names `AGENTS.md`, `.agents/`, and **Agent Skills**: they identify files, directories, and a specification shared across harnesses.

Record supported harnesses and tested versions in `.agents/README.md` (A.8). Validate instruction loading, skill discovery, and MCP configuration in each supported version. Check version-dependent examples against that harness's documentation.

______________________________________________________________________

## The Core Principle

Classify configuration items by how they can be shared. One file may contain generated and harness-specific sections.

| Category                                            | Strategy                                                                                                                                         | Examples                                   |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------ |
| **Portable** (shared format and compatible meaning) | Store once at the root or in `.agents/`; use native discovery, a symlink, an import (`CLAUDE.md` → `@AGENTS.md`), or a setting that points to it | `AGENTS.md`, portable `SKILL.md` skills    |
| **Generated** (shared data, different formats)      | Store canonical data in `.agents/`; render each supported harness's configuration                                                                | Shared MCP server definitions              |
| **Harness-specific** (no portable mapping)          | Keep in the harness's configuration; refer to shared sources instead of copying them                                                             | `.omp/rules/*.md`, `.claude/settings.json` |

______________________________________________________________________

## Part A: New Project Repository Template

### A.9 New Project Repository Checklist

1. Create `AGENTS.md` and the adapters your supported harnesses need, such as `CLAUDE.md` (`@AGENTS.md`) for Claude Code or `.gemini/settings.json` for Gemini CLI
1. Create `.agents/` (A.1) and its support record in `README.md` (A.8)
1. Add `sync-skills.sh`, write `sync-mcp.sh` (A.4), and `chmod +x .agents/scripts/*.sh`
1. Add skills and run `sync-skills.sh`. It exits 1 after creating links and until they are staged, so don't chain it with `&&`
1. Run `sync-mcp.sh`
1. Update `.gitignore` (A.7)
1. Add `.pre-commit-config.yaml`, install pre-commit (e.g., `uv tool install pre-commit`), and run `pre-commit install`; every clone needs this
1. Stage everything, run `pre-commit run --all-files`, and validate each harness as described in A.8

______________________________________________________________________

## Sources

| Source                   | Covers                                   | Link                                                                                                                                                        |
| ------------------------ | ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AGENTS.md / AAIF         | Shared agent instructions                | [agents.md](https://agents.md), [spec repo](https://github.com/agentsmd/agents.md), [AAIF](https://aaif.io/)                                                |
| Agent Skills             | SKILL.md format and discovery            | [specification](https://agentskills.io/specification), [client implementation guide](https://agentskills.io/client-implementation/adding-skills-support.md) |
| skills-ref               | Skill validation CLI                     | [github.com/agentskills/agentskills](https://github.com/agentskills/agentskills)                                                                            |
| Vercel Skills CLI        | `npx skills add`                         | [github.com/vercel-labs/skills](https://github.com/vercel-labs/skills)                                                                                      |
| Model Context Protocol   | MCP                                      | [modelcontextprotocol.io](https://modelcontextprotocol.io)                                                                                                  |
| Claude Code docs         | Claude skill discovery                   | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)                                                                                    |
| Claude Code issue #31005 | Request for native `.agents/` scanning   | [github.com/anthropics/claude-code#31005](https://github.com/anthropics/claude-code/issues/31005)                                                           |
| Codex docs               | Codex skills and project config          | [build skills](https://learn.chatgpt.com/docs/build-skills), [config basics](https://learn.chatgpt.com/docs/config-file/config-basic)                       |
| opencode docs            | opencode config, skills, MCP             | [opencode.ai/docs](https://opencode.ai/docs/config/)                                                                                                        |
| oh-my-pi docs            | omp skills, rules, MCP, context files    | [github.com/can1357/oh-my-pi/tree/main/docs](https://github.com/can1357/oh-my-pi/tree/main/docs)                                                            |
| SSW Rules                | Symlinking harness directories to Claude | [ssw.com.au/rules/symlink-agents-to-claude](https://www.ssw.com.au/rules/symlink-agents-to-claude)                                                          |

## Provenance

Migrated from the original blueprints[^original-harness-agnostic-project].

External authorities supporting this guidance[^authority-1][^authority-2][^authority-3][^authority-4][^authority-5][^authority-6][^authority-7][^authority-8][^authority-9][^authority-10][^authority-11][^authority-12][^authority-13][^authority-14][^authority-15][^authority-16].

[^original-harness-agnostic-project]: Original harness-agnostic-project.md

[^authority-1]: https://www.langchain.com/blog/the-anatomy-of-an-agent-harness

[^authority-2]: https://agents.md

[^authority-3]: https://github.com/agentsmd/agents.md

[^authority-4]: https://aaif.io/

[^authority-5]: https://agentskills.io/specification

[^authority-6]: https://agentskills.io/client-implementation/adding-skills-support.md

[^authority-7]: https://github.com/agentskills/agentskills

[^authority-8]: https://github.com/vercel-labs/skills

[^authority-9]: https://modelcontextprotocol.io

[^authority-10]: https://code.claude.com/docs/en/skills

[^authority-11]: https://github.com/anthropics/claude-code/issues/31005

[^authority-12]: https://learn.chatgpt.com/docs/build-skills

[^authority-13]: https://learn.chatgpt.com/docs/config-file/config-basic

[^authority-14]: https://opencode.ai/docs/config/

[^authority-15]: https://github.com/can1357/oh-my-pi/tree/main/docs

[^authority-16]: https://www.ssw.com.au/rules/symlink-agents-to-claude
