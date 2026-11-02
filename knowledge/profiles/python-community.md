---
type: Blueprint
title: Python community profile
description: Additional requirements for shared maintainership and downstream consumers.
tags:
  - profiles
  - policy
status: draft
owner: project-blueprints maintainers
generated:
  by: codex/okf-migration-v1
  at: '2026-11-02T13:16:03Z'
stale_after: '2027-05-01T13:16:03Z'
x-requires:
  - profiles/python
sources:
  - id: original-python-project-community
    resource: https://github.com/grAItools/project-blueprints/blob/b90867e82cd2a06ec3a01bea8d86d4f9a2882048/python-project-community.md
    title: Original python-project-community.md
---

# Python Project Community Extension

Prerequisite: [Python project profile](python.md).

## Adoption sequence

- [Community governance and documentation](../community/governance.md).
- [Community compatibility and downstreams](../community/compatibility-and-downstreams.md).
- [Community releases and continuity](../community/releases-and-continuity.md).
- [Scientific Python commitments](../community/scientific-python.md).

This document extends the [Python Project Repository Blueprint](python.md),
which in turn uses the [Harness-Agnostic Project Blueprint](harness-agnostic.md).
Use the baseline for technical configuration and commands; this extension only
adds or tightens requirements for shared maintenance and downstream users.
Use the baseline's four-checker typing profile, scopes, and suppression rules.

Adopt this extension when regular external contributions, multiple maintainers
with merge/release rights, downstream packages or redistributors, or ecosystem
commitments require explicit coordination. A small scientific library can
need these processes; a non-scientific community library can need them too.
Scale responsibilities to the actual team and publish any unmet requirements
with an owner and adoption plan rather than claiming full conformance.
For a single-maintainer project with downstream users, record independent
approval and shared recovery as unmet until a backup maintainer or successor
with the necessary access is available.

## 1. Additions to the baseline

Each requirement has one owner. Link to the baseline instead of copying tool
settings, scripts, command definitions, or release-validation steps. Where this
document tightens a baseline default, the following table identifies the change.

| Baseline area                                                                                         | Additional community requirement                                                  |
| ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| [Profile decisions](python.md#2-default-profile-and-project-decisions)                                | Maintainer roles, review responsibilities, and published policy decisions         |
| [Package contents](../python/packaging.md#metadata-and-distribution-contents)                         | Library tests, fixtures, and test helpers in the sdist for downstream use         |
| [Compatibility](../python/dependencies-and-compatibility.md#environments-and-compatibility)           | Support windows, deprecation commitments, and upstream/downstream testing         |
| [Tests](../python/quality-and-testing.md#tests-and-coverage)                                          | Full tests against installed distributions in addition to smoke checks            |
| [Contributor policy](../python/documentation-ci-and-releases.md#documentation-and-contributor-policy) | Governance, conduct and review rules; maintained API reference and versioned docs |
| [CI](../python/documentation-ci-and-releases.md#continuous-integration-and-maintenance)               | Independent reviews on protected branches and scheduled compatibility jobs        |
| [Releases](../python/documentation-ci-and-releases.md#release-and-artifact-validation)                | Independent authorization, provenance, shared access, and documented recovery     |

Add `GOVERNANCE.md`, `CODE_OF_CONDUCT.md`, `.github/CODEOWNERS`, issue/PR
templates, and `docs/development/` pages for compatibility, releases, and
project operations. Keep one authoritative home for each policy and link to
it from contributor instructions. Never store recovery codes,
credentials, or private incident details in these public documents.

## 8. Additional acceptance checklist

Complete the baseline checklist, then verify these additions:

- [ ] Publish roles, conduct/decision rules, contribution templates, and policy owners.
- [ ] Configure branch protections, required CI/reviews, CODEOWNERS, and emergency procedures.
- [ ] Publish support/deprecation windows and schedule owned compatibility testing.
- [ ] Ship library tests and inputs in sdists; run the applicable full suite against installed distributions.
- [ ] Verify independent release authorization, provenance, and artifact handover.
- [ ] Inventory access, establish backup maintainers, and exercise recovery/succession.
- [ ] Publish maintained-version documentation and verify any preview isolation.
- [ ] Run repository review with justified ignores; record SPEC applicability, status, and exceptions.

## Provenance

Migrated from the original blueprints[^original-python-project-community].

[^original-python-project-community]: Original python-project-community.md
