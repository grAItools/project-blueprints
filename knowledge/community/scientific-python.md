---
type: Blueprint
title: Scientific Python commitments
description: Applicable SPEC commitments and explicit adoption exceptions.
tags:
  - community
  - tool-behavior
status: draft
owner: project-blueprints maintainers
generated:
  by: codex/okf-migration-v1
  at: '2026-11-02T13:16:03Z'
stale_after: '2027-01-31T13:16:03Z'
x-requires:
  - profiles/python-community
sources:
  - id: original-python-project-community
    resource: https://github.com/grAItools/project-blueprints/blob/b90867e82cd2a06ec3a01bea8d86d4f9a2882048/python-project-community.md
    title: Original python-project-community.md
  - id: authority-1
    resource: https://learn.scientific-python.org/development/
    title: https://learn.scientific-python.org/development/
  - id: authority-2
    resource: https://scientific-python.org/specs/
    title: https://scientific-python.org/specs/
  - id: authority-3
    resource: https://scientific-python.org/specs/spec-0000/
    title: https://scientific-python.org/specs/spec-0000/
  - id: authority-4
    resource: https://scientific-python.org/specs/spec-0004/
    title: https://scientific-python.org/specs/spec-0004/
  - id: authority-5
    resource: https://scientific-python.org/specs/spec-0006/
    title: https://scientific-python.org/specs/spec-0006/
  - id: authority-6
    resource: https://scientific-python.org/specs/spec-0008/
    title: https://scientific-python.org/specs/spec-0008/
  - id: authority-7
    resource: https://scientific-python.org/specs/spec-0005/
    title: https://scientific-python.org/specs/spec-0005/
  - id: authority-8
    resource: https://scientific-python.org/specs/spec-0009/
    title: https://scientific-python.org/specs/spec-0009/
---

# Scientific Python commitments

Prerequisite: [Python community profile](../profiles/python-community.md).

## 7. Scientific Python ecosystem commitments

The [Development Guide](https://learn.scientific-python.org/development/)
informs repository engineering; [SPECs](https://scientific-python.org/specs/)
coordinate particular ecosystem practices. Record applicability and adoption
for each relevant SPEC, the source revision/date reviewed, exceptions, and
the responsible maintainer. Do not claim universal SPEC compliance.

| SPEC                                                                                                                        | Policy for participating scientific projects                                                                                                                                                                                                                                         |
| --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [0: minimum dependencies](https://scientific-python.org/specs/spec-0000/)                                                   | Adopt its rolling support policy: three years for Python feature releases and two for core dependency feature releases. Use its current drop schedule when updating floors, recording justified exceptions.                                                                          |
| [4: nightly wheels](https://scientific-python.org/specs/spec-0004/)                                                         | Test available upstream nightly wheels at least weekly and notify maintainers on failure. Publish development wheels at least weekly for downstream testing when relevant, with distinct development versions and retention rules. Document omissions before claiming full adoption. |
| [6: resource access](https://scientific-python.org/specs/spec-0006/)                                                        | Apply the access and continuity requirements above.                                                                                                                                                                                                                                  |
| [8: secure releases](https://scientific-python.org/specs/spec-0008/)                                                        | Apply the release authorization and provenance requirements above; audit actual service configuration before claiming adoption.                                                                                                                                                      |
| [5: CI](https://scientific-python.org/specs/spec-0005/) and [9: governance](https://scientific-python.org/specs/spec-0009/) | Check their status before adoption. Treat draft versions as informative inputs to explicit project policies rather than final standards.                                                                                                                                             |

Evaluate other SPECs individually when their subject applies. Check current
status before adopting a SPEC or adding a badge. Generic community projects
keep explicit support and governance policies without having to adopt the
Scientific Python ecosystem's dependency windows or nightly infrastructure.

## Provenance

Migrated from the original blueprints[^original-python-project-community].

External authorities supporting this guidance[^authority-1][^authority-2][^authority-3][^authority-4][^authority-5][^authority-6][^authority-7][^authority-8].

[^original-python-project-community]: Original python-project-community.md

[^authority-1]: https://learn.scientific-python.org/development/

[^authority-2]: https://scientific-python.org/specs/

[^authority-3]: https://scientific-python.org/specs/spec-0000/

[^authority-4]: https://scientific-python.org/specs/spec-0004/

[^authority-5]: https://scientific-python.org/specs/spec-0006/

[^authority-6]: https://scientific-python.org/specs/spec-0008/

[^authority-7]: https://scientific-python.org/specs/spec-0005/

[^authority-8]: https://scientific-python.org/specs/spec-0009/
