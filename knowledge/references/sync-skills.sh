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
