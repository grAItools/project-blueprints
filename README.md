# project-blueprints

Project blueprints for software development with coding agents, organized as
an Open Knowledge Format (OKF) v0.2 bundle.

Start at the [bundle index](knowledge/index.md) or
[choose a profile](knowledge/selection.md). Adopt the
[harness foundation](knowledge/profiles/harness-agnostic.md), then the
[Python baseline](knowledge/profiles/python.md). Add the
[community extension](knowledge/profiles/python-community.md) when shared
maintainership or downstream commitments require it.

Each topic has one canonical home. Community guidance inherits the baseline's
technical configuration, including all four blocking type checkers.
The original three filenames remain as generated section maps, preserving
their heading links:

- [Harness-agnostic project](harness-agnostic-project.md)
- [Python project](python-project.md)
- [Python community project](python-project-community.md)

## Validation

The full tooling workflow currently supports Linux x86_64 with Python 3.11
or newer. Bootstrap pinned external tools, install the locked dependencies,
and run the shared completion gate:

```bash
python3 scripts/bootstrap.py uv shellcheck
.tools/bin/uv sync --locked
.tools/bin/uv run --locked python scripts/check.py check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for authoring, health reports, tool
qualification, and archive validation, and the
[approved migration plan](OKF-MIGRATION-PLAN.md) for the design.

## Migration status and distribution

The content migration is implemented, with immutable originals and a
section/block mapping under `migration/`. Migrated concepts are explicitly
draft and unverified pending maintainer review. No human verification is
implied by successful automated checks.

Distribution is blocked until maintainers resolve the third-party rights
inventory and approve distribution. `package` enforces that prerequisite before writing an
archive. This repository does not automatically publish releases.

## License

Original project content and tooling are available under the
[MIT License](LICENSE.txt). Third-party material is excluded from that grant;
see [LICENSING.md](LICENSING.md) for scope and outstanding permissions.

## Credits

Harness integration reference:
[davidgibsonp's gist](https://gist.github.com/davidgibsonp/337be9b80b3f03eccd188235c287bb05).
The original attribution is preserved; permission status is recorded in
`migration/rights-review.yaml`. Licensed upstream OKF test fixtures retain
their Apache-2.0 license under `tests/fixtures/upstream/` and are excluded from
the distributable bundle.
