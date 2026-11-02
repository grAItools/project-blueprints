# Repository instructions

This repo authors the OKF bundle under `knowledge/`. Read
[CONTRIBUTING.md](CONTRIBUTING.md) for commands and invariants.

- Run `uv run --locked python scripts/check.py check` after changes. Bootstrap
  pinned external tools as documented before the first run.
- Edit canonical concepts, not generated indexes or the three root blueprint
  landing pages. Regenerate those with `scripts/check.py index`.
- Never rewrite `migration/sources/` or vendored upstream fixtures. They are
  hash-checked evidence, excluded from formatting and link checking.
- Preserve prerequisite ownership and all existing technical commitments.
  Record substantive source dispositions rather than changing reconstruction
  hashes to conceal omissions.
- Do not invent human authorship, verification, review, license clearance, or
  maintainer identities. Agents must not create human verification events.
- Keep bundle links inside the bundle or use external URLs for repo tooling.
- `package` must keep refusing distribution while rights are unresolved. Do
  not bypass that gate or publish artifacts without separate authorization.
