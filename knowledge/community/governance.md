---
type: Blueprint
title: Community governance and documentation
description: Shared contribution, review, governance, and repository documentation requirements.
tags:
  - community
  - policy
status: draft
owner: project-blueprints maintainers
generated:
  by: codex/okf-migration-v1
  at: '2026-11-02T13:16:03Z'
stale_after: '2027-05-01T13:16:03Z'
x-requires:
  - profiles/python-community
sources:
  - id: original-python-project-community
    resource: https://github.com/grAItools/project-blueprints/blob/b90867e82cd2a06ec3a01bea8d86d4f9a2882048/python-project-community.md
    title: Original python-project-community.md
  - id: authority-1
    resource: https://repo-review.readthedocs.io/en/latest/
    title: https://repo-review.readthedocs.io/en/latest/
---

# Community governance and documentation

Prerequisite: [Python community profile](../profiles/python-community.md).

## 2. Governance and contributions

Document how maintainers are appointed, how decisions are made, how disputes
are escalated, and how responsibilities are transferred. Identify release,
security, review, and conduct contacts. Several roles can belong to the same
person, while independent release authorization requires another maintainer.
Keep conduct reports separate from public technical decision records.

Use contribution templates to request reproduction steps, relevant testing,
compatibility impact, and release-note information. Link the baseline AI policy
and explain who is responsible for assisted submissions and reviewer responses.
Record significant design and compatibility decisions in issues or short design
notes; ordinary fixes do not need a formal proposal.

Protect integration and maintained release branches with required CI checks
and at least one independent review. Use CODEOWNERS for maintained areas and
release/CI configuration, with a backup owner for critical components. Configure
review requirements explicitly: a CODEOWNERS file alone does not enforce them.
Require independent approval of the final pushed commit by dismissing stale
approvals or requiring approval of the most recent reviewable push.
Document merge strategy and emergency fixes, including who can authorize an
exception and the required retrospective review. Conventional Commits remain
a project choice; do not duplicate a manually maintained changelog unnecessarily.

## 6. Documentation and repository review

Maintain a complete public API reference, support policy, migration guidance,
and contribution/release instructions. Use generated API extraction when it
reduces drift and a verified integration supports the chosen engine. Keep the
baseline's Zensical setup unless another engine meets a demonstrated need.

Publish versioned documentation for maintained release lines and retain access
to older release docs. Add PR previews where they help review; preview jobs
must not receive production deployment credentials while executing PR content.
Read the Docs and external coverage reporting are optional service choices.

Add pinned `sp-repo-review[cli]` to the locked dev group and run it through the
baseline `lint` subcommand against the implemented repository in CI. Reuse the
baseline's schema checks. Assign narrow documented ignores for equivalent
behavior, such as the baseline's custom runner and locked local hooks, and
for inapplicable services. Do not duplicate commands or tools for recognition
by the checker. Review ignores as the blueprint and checker evolve; a green
report is supporting evidence, not proof that release/access policies work.
See [repo-review](https://repo-review.readthedocs.io/en/latest/).

## Provenance

Migrated from the original blueprints[^original-python-project-community].

External authorities supporting this guidance[^authority-1].

[^original-python-project-community]: Original python-project-community.md

[^authority-1]: https://repo-review.readthedocs.io/en/latest/
