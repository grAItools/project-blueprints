---
type: Blueprint
title: Community releases and continuity
description: Independent release authorization, shared access, and recovery responsibilities.
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
    resource: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
    title: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
  - id: authority-2
    resource: https://scientific-python.org/specs/spec-0008/
    title: https://scientific-python.org/specs/spec-0008/
  - id: authority-3
    resource: https://scientific-python.org/specs/spec-0006/
    title: https://scientific-python.org/specs/spec-0006/
---

# Community releases and continuity

Prerequisite: [Python community profile](../profiles/python-community.md).

## 5. Releases, access, and continuity

Document release roles, steps, required permissions, support-line selection,
rollback limitations, and incident response in the contributor documentation.
Keep release notes and migration guidance useful to downstream maintainers.
An intentional release trigger identifies the exact verified commit and
artifacts; all baseline validation and publishing protections still apply.

Require authorization by at least one other release maintainer before publishing
to an index or public release channel. Use the baseline's environment-bound
trusted publisher, with self-approval and administrator bypass disabled.
Audit branch/tag ruleset bypass lists and document any emergency exception.
Reviewers approve the identified commit and artifact hashes; changed artifacts
require new validation and authorization. Keep any pre-approval GitHub release
as a draft until the authorized publishing step.

Confirm that the host/plan enforces approval. If unavailable, disable automatic
publication and the source repository's trusted-publisher registrations for
this release path. After independently recorded approval, a release manager
publishes the retained CI artifacts from a controlled external environment,
verifying their hashes and using a project-scoped credential held outside the
source repository. The credential holder must be a different maintainer from
the release initiator and independently approve the identified commit and
artifacts. This is a two-person procedural control. This fallback replaces
automatic index/public-release
publication; a tag push alone cannot publish. See [GitHub environment protections](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).

Restrict permitted release actions and reusable workflows. Generate provenance
attestations for release artifacts and document how consumers verify them,
including the expected repository/workflow identity. Verify attestations before
publishing when artifacts cross workflow boundaries. Distinguish publisher
attestations from claims of fully reproducible builds. Recommend signed release
commits and document the signing and verification process if adopted.
Only the isolated authorized provenance/publishing job gets the required
`id-token: write` and `attestations: write`; build/test jobs do not. Document
the provenance mechanism and credential boundary for the external fallback.
These measures follow [SPEC 8](https://scientific-python.org/specs/spec-0008/).

Inventory restricted resources, their owners, and access/recovery procedures.
Ensure at least two maintainers can recover each critical service, including
source hosting, package publication, documentation, and relevant domains.
Grant individual least-privilege access; shared secrets, where unavoidable,
belong in an encrypted access-controlled vault. Review access at least annually
and on role changes; remove departing maintainers and rotate secrets they could
have retained. Set token expiry and document renewal, rotation, and revocation.
Publish resource names, roles, and procedures; keep sensitive account identifiers,
recovery contacts, and backup-code locations in the restricted vault.
Test a release/access handover and document succession when
maintainers become unavailable. See [SPEC 6](https://scientific-python.org/specs/spec-0006/).

## Provenance

Migrated from the original blueprints[^original-python-project-community].

External authorities supporting this guidance[^authority-1][^authority-2][^authority-3].

[^original-python-project-community]: Original python-project-community.md

[^authority-1]: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments

[^authority-2]: https://scientific-python.org/specs/spec-0008/

[^authority-3]: https://scientific-python.org/specs/spec-0006/
