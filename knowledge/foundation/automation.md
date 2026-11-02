---
type: Blueprint
title: Harness automation and ignore rules
description: Hooks, staging checks, and ignore rules for shared agent configuration.
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

# Harness automation and ignore rules

Prerequisite: [Harness-agnostic project profile](../profiles/harness-agnostic.md).

### A.6 Automation

**Pre-commit hooks** (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: local
    hooks:
      - id: sync-agent-skills
        name: "Sync .agents/skills to harness directories"
        entry: .agents/scripts/sync-skills.sh
        language: script
        pass_filenames: false
        always_run: true  # `files:` never matches deletions, so stale links would slip through
      - id: check-agent-mcp
        name: "Verify MCP configs are current"
        entry: .agents/scripts/sync-mcp.sh check
        language: script
        pass_filenames: false
        always_run: true  # Also catches hand edits to generated files and generator changes
```

Stage every new skill and managed link. Sync changes, untracked or unstaged links, and untracked new skills stop the commit; fix staging and retry. Keep drafts in `.agents/skills-local/` so untracked skills do not block every commit.

During `git commit`, pre-commit sets aside unstaged tracked edits, so checks see the staged links. `pre-commit run --all-files` also sees unstaged edits.

Hooks run only after `pre-commit install` in each clone, and `--no-verify` skips them. Also run `pre-commit run --all-files` in CI.

### A.7 .gitignore

```gitignore
.agents/skills-local/*
!.agents/skills-local/.gitkeep
.claude/settings.local.json
.claude/worktrees/
```

In a repo where `*` ignores everything, put allow-list entries before machine-local ignores. Git's last matching pattern wins; reversing the order would re-include private files:

```gitignore
!.agents/
!.agents/**
!.claude/
!.claude/**
!.codex/
!.codex/**
!.omp/
!.omp/**
!.opencode/
!.opencode/**
!.gemini/
!.gemini/settings.json
!opencode.json
!opencode.jsonc
!.mcp.json
!AGENTS.md
!CLAUDE.md
!.gitignore
!.pre-commit-config.yaml

# Machine-local, must come after the allow-list
.agents/skills-local/*
!.agents/skills-local/.gitkeep
.claude/settings.local.json
.claude/worktrees/
```

## Provenance

Migrated from the original blueprints[^original-harness-agnostic-project].

[^original-harness-agnostic-project]: Original harness-agnostic-project.md
