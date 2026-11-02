---
type: Blueprint
title: Shared MCP configuration
description: Canonical server definitions and harness-specific rendering contracts.
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

# Shared MCP configuration

Prerequisite: [Harness-agnostic project profile](../profiles/harness-agnostic.md).

### A.4 MCP Configuration

Store shared MCP server definitions in `.agents/mcp/servers.json` and generate each harness's format:

| Harness     | File                 | Format                                                                                                       |
| ----------- | -------------------- | ------------------------------------------------------------------------------------------------------------ |
| Claude Code | `.mcp.json`          | JSON, servers under `mcpServers`; URL servers need `"type": "http"`                                          |
| omp         | `.omp/mcp.json`      | JSON, servers under `mcpServers`; `type` is `stdio`/`http`/`sse`. Read only from the directory omp starts in |
| opencode    | `opencode.json`      | JSON(C), servers under `mcp`; `type` is `local` (`command` as an array) or `remote` (`url`)                  |
| Codex       | `.codex/config.toml` | TOML, `[mcp_servers.<name>]` tables. Loaded only for trusted projects                                        |

**Canonical format:**

```json
{
  "figma": {
    "type": "http",
    "url": "https://mcp.figma.com/mcp"
  },
  "my-tool": {
    "type": "stdio",
    "command": "uvx",
    "args": ["my-mcp-server"],
    "env": { "MY_TOOL_API_KEY": "${MY_TOOL_API_KEY}" }
  }
}
```

Use a bare map of server names, without a `mcpServers` wrapper. Servers are `stdio` (`command`, `args`, `env`) or `http` (`url`, `headers`). Store no secrets: use `${NAME}` as a whole `env` or header value, or `Bearer ${NAME}` in an `Authorization` header.

**Implement `sync-mcp.sh`** (not included), typically in Python or `jq`. It should:

- render each server for each supported harness based on its `type`:
  - Claude Code: canonical fields under `mcpServers`; placeholders work as-is
  - opencode: `local`/`remote`; `command` and `args` merged into one `command` array; `environment` instead of `env`; `{env:NAME}` instead of `${NAME}`
  - Codex: an `env` entry `${NAME}` with the same name becomes `env_vars = ["NAME"]`; `Bearer ${NAME}` becomes `bearer_token_env_var = "NAME"`; other placeholder headers go in `env_http_headers`, static ones in `http_headers`
  - omp: check its docs for placeholder support
- never expand placeholders into values
- in `opencode.json` and `.codex/config.toml`, rewrite only the `mcp` key or the `[mcp_servers.*]` tables (with a JSONC-aware tool for `opencode.jsonc`), and remove only servers it generated
- write files atomically
- support `check`: render to a temporary location, compare, exit non-zero on differences, change nothing
- fail on a field or placeholder it can't map, instead of dropping it

For definitions outside this format (SSE, OAuth, harness-specific options), extend the format and generator or configure them per harness. Track generated server names so hand-maintained entries remain untouched.

**Codex trust:** Codex loads `.codex/` only in trusted projects; review the checkout, then trust it. Writing to `~/.codex/config.toml` affects every project and risks name collisions. Offer that only as an explicit opt-in, such as `install-codex`, with a marked block (`# BEGIN <repo> managed MCP` / `# END <repo> managed MCP`), collision refusal, and matching uninstall.

## Provenance

Migrated from the original blueprints[^original-harness-agnostic-project].

[^original-harness-agnostic-project]: Original harness-agnostic-project.md
