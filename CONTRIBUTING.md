# Maintaining project-blueprints

This repo maintains an OKF knowledge bundle, rather than an installable
Python library. Its shared runner implements a documentation-oriented
completion gate; the application blueprint's four-checker stack remains
guidance for adopting projects. It is not this repo's tooling profile.

## Setup and commands

The complete workflow supports Linux x86_64, Python 3.11+, and Bash for the
preserved shell examples. Bundle reading requires none of these tools.
Other platforms can read and edit concepts, but must use a Linux environment
for the full gate until additional verified binary assets are committed.

```bash
python3 scripts/bootstrap.py uv shellcheck
.tools/bin/uv sync --locked
.tools/bin/uv run --locked python scripts/check.py check
```

All Python dependencies are locked in `uv.lock`. External tool versions,
download assets, archive members, and SHA-256 checksums are pinned in
`tools/versions.json`. Bootstrap is an explicit network operation and verifies
checksums before writing `.tools/bin`. The completion gate performs no
network requests, source edits, or wall-clock-dependent failures. uv may need
network on its first synchronization; use `uv run --locked --offline` after
provisioning to enforce an offline environment too.

The runner discovers maintained files directly, including untracked concepts;
it does not rely on the Git index. It excludes immutable migration sources
and upstream fixtures from spelling, formatting, and link checks. Snapshots
are evidence: their SHA-256 hashes and pinned Git object identities are checked. No formatting
entry point accepts arbitrary paths or writes those sources.

| Command after `python scripts/check.py` | Behavior                                                                                                    |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `check`                                 | Format/spelling, Python lint, bundle metadata/links, reconstruction, indexes, examples, and focused tests   |
| `index`                                 | Explicitly regenerate indexes and legacy landing pages                                                      |
| `fmt`                                   | Format authored Markdown and Python; never rewrite snapshots or generated Markdown                          |
| `validate PATH`                         | Apply this repo's local bundle policy to an independent bundle root                                         |
| `qualify`                               | Compare the advisory OKF CLI with committed expected findings                                               |
| `health`                                | Check review deadlines, upstream changes, external links, and advisory tooling; write `reports/health.json` |
| `health --offline`                      | Skip external requests while checking local health                                                          |
| `package`                               | Run the gate, require rights clearance, build and validate a standalone archive; never publish              |

Optional local hooks use the same gate:

```bash
git config core.hooksPath .githooks
```

This is an explicit per-clone Git setting. CI enforces the shared gate whether
or not local hooks are enabled.

## Format contract

The exact target is OKF v0.2 SPEC.md at commit
`0b87c52c6ef999286c745e19998fdfcd03d5dbee`, SHA-256
`26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101`.
An immutable licensed copy is under `tests/fixtures/upstream/SPEC.md`.
Only `type` is universally required by OKF. This repo deliberately requires
more metadata and stronger link integrity; diagnostics distinguish these
local requirements from the portable format.

Every authored concept under `knowledge/` needs `type`, `title`,
`description`, `tags`, `status`, `owner`, and `generated.by`/`generated.at`.
Types, tag vocabulary, profile prerequisites, directory labels, maintainer
identities, and the exact freshness scope live in `tools/bundle-policy.toml`.
Unknown extension keys are preserved. Status is `draft`, `stable`, or
`deprecated`. Root `index.md` declares the string version `0.2`; other indexes
have no frontmatter. Indexes and root landing pages are owned by the generator.

Use relative Markdown links for GitHub browsing, or `/...` links relative to
the bundle root. Every local concept link, image, fragment, and path-valued
metadata reference must stay inside the bundle. Link to repo-only material
through an external, preferably commit-pinned URL. Concept IDs are paths
without `.md`. `x-requires` lists those IDs, and visible prose describes the
same prerequisites. Profile prerequisites are additionally enforced by policy.

## Authorship, sources, and review

Record real production with `generated.by` and the time of meaningful change
in `generated.at`. Cosmetic formatting need not renew the date. Supported
actor conventions are `human:<github-handle>`, `process:<id>`, and
`<producer>/<version>`. The initial migration records its agent identity and
actual migration time; original provenance remains in `sources` and the map.

No maintainer identity has been inferred. Add confirmed identities to the
policy's `maintainers` list before recording human verification. Agents must
not create human verification events. Only maintainers add `verified` after
content review, and changes to that field require maintainer review in the
repository's review process. The configuration file alone does not enforce
branch protection; repository administrators must configure that enforcement.
An automated pass never creates a content verification event. Health reports
flag individual verification dates older than the last meaningful change.

Use `sources` with unique IDs for authoritative claims and version-sensitive
tool behavior. Cite those IDs using Markdown footnotes; ordinary further
reading may remain inline links. The migration preserves original authority
links and collects their citations by topic; source-block mapping supports
review of individual statements. Do not invent timestamps for external sources.

Every source ID needs both a matching footnote definition and a citation.
Unrelated prose footnotes use the `note-` prefix. Multi-word source scope
descriptors are preserved. Use `scope:` for a single-word scope or a scope
containing `/`; use `./` or `/` to identify a local filename containing spaces.
Other relative resources, including extensionless paths, must resolve inside
the bundle. Every fenced example must appear exactly once in the classified
example inventory.

Freshness membership is explicit and bidirectional: a selected concept must
have `stale_after`; a concept outside the selection must not. Dates must be
ISO 8601 datetimes with an explicit timezone. Default review horizons are
90 days for `tool-behavior` and 180 days for `policy`. Date syntax is required
in PRs; elapsed deadlines are scheduled advisory findings. Do not reset dates
just because a link responds. Exceptions need an owner, reason, and expiration.

## Source preservation and generated pages

`migration/sources/` contains the exact four originals from the recorded Git
commit. `migration/mapping.yaml` assigns every real heading and Markdown AST
block to one canonical concept, records hashes and relocation transforms,
and retains the original fenced examples. Reconstruction uses these local
snapshots, so shallow clones and offline validation need no historical Git
objects. No published archive contains this migration evidence.

`migration/source-proof.json` carries the original commit and root-tree
objects. The validator checks their Git object IDs against the separately
pinned source revision and checks each snapshot against the committed blob.
The initial mapping's semantic projection also has an independent digest in
the validator, excluding only explicitly reviewed `approved_change` records.
Changing snapshots and their adjacent hashes together cannot rebaseline the
gate. Changing the validator's provenance pins remains a deliberate code
change requiring review; this is not protection against someone replacing
the validator itself. AST block inventories and full heading records are
recomputed, not accepted merely because listed hashes happen to match.

The initial migrated concept inventory is deliberately frozen by this audit.
Adding or removing concepts currently requires an explicit, reviewed mapping
and validator-pin rebaseline. It is not an automatic inventory extension;
never change provenance pins merely to conceal a preservation failure.

The initial migration gate compares canonical bodies with source reconstruction.
An intentional future policy edit requires a separately reviewed migration
disposition and updated reconstruction expectation; never simply weaken the
gate to hide an accidental omission. A metadata-only edit must preserve the
source attribution contract. Keep substantive changes separate from mechanical
splitting. `check` never accepts a changed reconstruction automatically.

For an intentional change, keep the baseline reconstruction hash unchanged
and add `approved_change` to that concept's mapping record. It needs `by`
(a configured human maintainer), `at`, `reason`, `body_sha256`, and
`diff_sha256`. The diff is the UTF-8 unified diff from the formatted baseline
body to the new body, with filenames `source-reconstruction` and
`<concept-id>.md`, including final newlines. Changes to fenced examples also
need an approved `fences_sha256` list. These fields record a maintainer's
decision; agents must not invent approval. The validator checks the exact
content and diff hashes rather than accepting a replacement baseline hash.

The generator retains original heading text and order in all three root
landing pages. A pinned Markdown renderer, sanitizer model, and GitHub slugger
check every legacy fragment against rendered targets. This local compatibility
model is not proof of GitHub's private implementation; retain native headings
instead of depending on raw HTML IDs. Named HTML anchors, duplicate headings,
and generated documents have formatter round-trip fixtures. Raw drift checks
follow format checks; neither check rewrites generated output.

## Advisory tool qualification and health

```bash
python3 scripts/bootstrap.py okf lychee
.tools/bin/uv run --locked python scripts/check.py qualify
.tools/bin/uv run --locked python scripts/check.py health
```

The pinned OKF CLI is an independent advisory cross-check. v0.5.1 rejects
the spec's full `stale_after` datetime as a date-format error; this repo keeps
spec-correct datetimes. Its other upstream citation findings are preserved
in `tools/okf-qualification.json`, scoped exceptions, and the qualification
report. Do not make its raw exit status the completion gate.

Qualification covers four licensed upstream bundles pinned to the target
commit and minimal cases for dates, unknown fields, reserved files, and broken
links. Unexpected findings or process failures reject the candidate tool pin.
Review versions and exact finding signatures before changing the recorded
expectations; the runtime command never updates them. External-link checks
use the same maintained Markdown scope and retry transient failures. Scheduled
health reports are uploaded by GitHub Actions for maintainer triage; no tool
automatically contacts third parties or publishes verification events.

The qualification report owns observed severity and count. Compatibility
exceptions own the fixture/rule/concept/version scope and the rationale,
owner, and expiration. The gate reconciles those scopes; qualification
compares the entire observed findings, including severity and count, to the
report. Runtime qualification is read-only and has no expectation-update mode.

`tools/health-exceptions.json` accepts exact-match exceptions with `rule`,
`match`, `owner`, `reason`, and timezone-aware `expires`. Supported rules are
`external-url` (match an exact URL), `review-overdue`, `stale-verification`,
and `narrative-orphan` (match a concept ID). Expired exceptions stop applying
and appear in the report. Active exceptions remain visible; no broad wildcard
URL exclusions are generated.

## Distribution gate

Original project content and tooling use the [MIT License](LICENSE.txt), with
third-party exclusions described in [LICENSING.md](LICENSING.md).
`migration/rights-review.yaml` records the selection and unresolved third-party
permissions. Before distribution, a human maintainer must confirm permissions,
clear every source record, and approve exact hashes of `LICENSE.txt` and any
required `NOTICE.txt`. The gate rejects unresolved rights before creating an
archive. See the file's current entries for the outstanding work.

Each cleared source must declare its evidence, covered path scopes, and an
explicit `required_notices` list. All bundle files must fall under cleared
scopes, and all required notices must be included with approved hashes.

For cleared content, `package` creates a deterministic ZIP with the bundle at
its root, approved notices, an exact member allow-list, and no symlinks or
repository tooling. It extracts into a temporary directory outside the
checkout and re-runs validation there. `dist/provenance.json` records the
archive hash, base source revision, and working-tree dirty status. For a local
dirty-tree build, the archive hash identifies the exact artifact; the Git
revision identifies its base rather than claiming the tree is unchanged.
Explicitly declared assets must exist; they are never silently omitted.
Artifact validation and publication remain
separate; this repo has no publishing workflow. Synthetic tests exercise
archive extraction and rights rejection without declaring this content cleared.
