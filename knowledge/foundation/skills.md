---
type: Blueprint
title: Portable agent skills
description: Skill discovery, compatibility, and the canonical skill-linking script.
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
    resource: https://agentskills.io/specification
    title: https://agentskills.io/specification
  - id: authority-2
    resource: https://github.com/vercel-labs/skills
    title: https://github.com/vercel-labs/skills
---

# Portable agent skills

Prerequisite: [Harness-agnostic project profile](../profiles/harness-agnostic.md).

### A.3 Skills (SKILL.md)

Skills package reusable instructions and workflows for agents. The [Agent Skills spec](https://agentskills.io/specification) defines a shared format:

```yaml
---
name: my-skill          # Lowercase and hyphens, matches the directory name
description: What this skill does and when to use it.
---

Step-by-step instructions for the agent...
```

Keep `SKILL.md` under 500 lines and move details to `references/`.

A shared format does not guarantee compatible behavior. Claude Code's `context: fork` and inline shell-command substitution are not portable by default; the spec's experimental `allowed-tools` field also has varying support. Use only instructions, resources, and features compatible with all supported harnesses in shared skills. Keep harness-specific skills separate, subject to the discovery rules below.

**Discovery.** Link skills only into harnesses that do not scan `.agents/skills/`; extra links are redundant and Codex lists them as duplicates.

| Harness     | Reads `.agents/skills/`?     | Sync target       |
| ----------- | ---------------------------- | ----------------- |
| Claude Code | No                           | `.claude/skills/` |
| Codex       | Yes (cwd up to repo root)    | None              |
| omp         | Yes (cwd up to repo root)    | None              |
| opencode    | Yes (cwd up to git worktree) | None              |

omp and opencode also scan `.claude/skills/`; verify that your versions deduplicate the links.

Harness-specific directories do not ensure isolation. For incompatible skills, use a location other supported harnesses do not scan. If none exists, make the skill portable or keep it in its harness-specific directory and record unsupported harness/skill combinations in `.agents/README.md`. Recording a limitation does not resolve incompatibility.

**The sync script** (`.agents/scripts/sync-skills.sh`):

```bash
#!/usr/bin/env bash
# Exits 0 if the links are in sync and none are missing from the commit, 1 if it changed
# anything or a link or new skill is untracked or unstaged (so a pre-commit hook stops),
# 2 if something it doesn't manage is in the way, or git fails.
set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$AGENTS_DIR/.." && pwd)"
MANAGED="../../.agents/skills"
# Harnesses that don't discover .agents/skills/ natively
TARGETS=(".claude/skills")
# Harnesses that do (omp, opencode) and leftovers from older setups: never sync here, only
# clean up old links
NATIVE=(".omp/skills" ".opencode/skills" ".codex/skills")
changed=0

# The script owns only links of the exact form it creates: $MANAGED/<one skill name>
is_managed() {
    local name="${1#"$MANAGED"/}"
    [ "$name" != "$1" ] && [ -n "$name" ] && [[ "$name" != */* ]] &&
        [ "$name" != "." ] && [ "$name" != ".." ]
}

for target_dir in "${TARGETS[@]}"; do
    if [ -L "$REPO_ROOT/$target_dir" ]; then
        # Linking the whole dir (e.g., .claude/skills -> ../.agents/skills) already covers it
        [ "$(readlink "$REPO_ROOT/$target_dir")" = "../.agents/skills" ] && continue
        echo "ERROR: $target_dir is a symlink to somewhere other than .agents/skills." >&2; exit 2
    fi
    mkdir -p "$REPO_ROOT/$target_dir"

    for skill_dir in "$AGENTS_DIR"/skills/*/; do
        [ -d "$skill_dir" ] || continue
        name="$(basename "$skill_dir")"
        link_target="$MANAGED/$name"
        link_path="$REPO_ROOT/$target_dir/$name"

        if [ -L "$link_path" ]; then
            current="$(readlink "$link_path")"
            [ "$current" = "$link_target" ] && continue
            if ! is_managed "$current"; then
                echo "ERROR: $link_path is a hand-made link to $current; rename one of the skills." >&2; exit 2
            fi
            rm "$link_path"
        elif [ -e "$link_path" ]; then
            echo "ERROR: $link_path exists but is not a symlink." >&2; exit 2
        fi

        ln -s "$link_target" "$link_path"
        echo "Synced: $link_path -> $link_target"; changed=1
    done

    # Prune links to skills that no longer exist (including dangling ones)
    for link in "$REPO_ROOT/$target_dir"/*; do
        [ -L "$link" ] || continue
        target="$(readlink "$link")"
        is_managed "$target" || continue
        [ -d "$AGENTS_DIR/skills/${target#"$MANAGED"/}" ] && continue
        rm "$link"; echo "Pruned: $link"; changed=1
    done
done

# Remove old links from harnesses that read .agents/skills/ natively (they duplicate skills)
for native_dir in "${NATIVE[@]}"; do
    if [ -L "$REPO_ROOT/$native_dir" ]; then
        # Never prune through a dir alias: it could point at .claude/skills or .agents/skills
        echo "ERROR: $native_dir is a symlink; this harness reads .agents/skills/ natively, so remove it." >&2; exit 2
    fi
    for link in "$REPO_ROOT/$native_dir"/*; do
        [ -L "$link" ] || continue
        is_managed "$(readlink "$link")" || continue
        rm "$link"; echo "Pruned (reads .agents/skills/ natively): $link"; changed=1
    done
done

# Fail while a link or a new skill would be left out of the commit
if git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    links="$(git -C "$REPO_ROOT" status --porcelain --untracked-files=all -- "${TARGETS[@]}" "${NATIVE[@]}")" ||
        { echo "ERROR: git status failed." >&2; exit 2; }
    skills="$(git -C "$REPO_ROOT" status --porcelain --untracked-files=all -- .agents/skills)" ||
        { echo "ERROR: git status failed." >&2; exit 2; }
    # Second status column set: not staged (or untracked) yet
    pending="$({ printf '%s\n' "$links" | grep '^.[^ ]'; printf '%s\n' "$skills" | grep '^??'; } || true)"
    if [ -n "$pending" ]; then
        echo "Not staged yet (stage them, or move draft skills to .agents/skills-local/):" >&2
        echo "$pending" >&2; changed=1
    fi
fi

exit "$changed"
```

- Runs on macOS's bash 3.2.
- Manages only links of the form `../../.agents/skills/<name>`; conflicts stop it with exit 2. Exclude hand-made, machine-local links (e.g., to `~/.agents/skills/`) through `.git/info/exclude` so staging checks ignore them.
- Handles the adjacent `.agents/skills/`. Package-scoped skills need that package's own directory, script, and hook entry; root skills are visible repo-wide.
- Creates symlinks only. On Windows, use Git Bash or WSL and enable `core.symlinks` plus Developer Mode (or admin rights) before cloning. Otherwise links check out as text files and trigger exit 2. Where symlinks are unavailable, implement a copy mode that tracks owned copies and removes stale ones.

**Third-party skills** ([Vercel skills CLI](https://github.com/vercel-labs/skills)):

```bash
npx skills add <repo>@<skill-name> -y
.agents/scripts/sync-skills.sh
```

Always run the sync script after installation: the CLI selects harness directories by detection. If it copied a skill into `.claude/skills/`, sync stops. Verify it matches (`diff -r .claude/skills/<name> .agents/skills/<name>`), delete the copy, and rerun.

**Private skills** go in `.agents/skills-local/` (gitignored). If you extend the script to link them, don't commit those links.

## Provenance

Migrated from the original blueprints[^original-harness-agnostic-project].

External authorities supporting this guidance[^authority-1][^authority-2].

[^original-harness-agnostic-project]: Original harness-agnostic-project.md

[^authority-1]: https://agentskills.io/specification

[^authority-2]: https://github.com/vercel-labs/skills
