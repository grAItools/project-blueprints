# Plan to convert project-blueprints to an OKF bundle

Reviewed plan v4, 2026-11-01. This document proposes the conversion; it does
not implement it or authorize publication or a license change.

Independent review: APPROVED for implementation under the prerequisites below
by an OMP agent using Swiss AI's DeepSeek V4.1 Flash, Paseo agent
`cd223ee2-de6d-4c86-a0d8-d094f4847ce5`. The review's final accepted amendment
Q1 (immutable evidence and generated-file tooling scope) is incorporated here.

Use one distributable OKF v0.2 bundle under `knowledge/`. Preserve the
existing dependency chain: harness foundation → Python baseline → community
extension. Keep repository maintenance instructions and tooling outside the
bundle. Profiles explain adoption; topic concepts own detailed requirements.

## Specification and compatibility contract

Target [OKF v0.2 at commit
0b87c52c6ef999286c745e19998fdfcd03d5dbee](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/0b87c52c6ef999286c745e19998fdfcd03d5dbee/SPEC.md).
The raw SPEC.md SHA-256 is
`26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101`.
Record these constants in the implementation's tooling configuration and
CONTRIBUTING.md. A scheduled upstream comparison reports changes; it must
never silently update the target or require a network fetch during PR checks.

Distinguish spec conformance from this repo's stricter authoring policy.
Unknown extension keys remain valid OKF. Local checks enforce the documented
repo profile and diagnose those violations separately from spec violations.

## Bundle and repository structure

```text
project-blueprints/
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
├── OKF-MIGRATION-PLAN.md
├── pyproject.toml
├── uv.lock
├── knowledge/
│   ├── index.md
│   ├── selection.md
│   ├── profiles/
│   │   ├── index.md
│   │   ├── harness-agnostic.md
│   │   ├── python.md
│   │   └── python-community.md
│   ├── foundation/
│   │   ├── index.md
│   │   ├── instructions.md
│   │   ├── skills.md
│   │   ├── mcp-configuration.md
│   │   ├── harness-adapters.md
│   │   ├── automation.md
│   │   └── migration.md
│   ├── python/
│   │   ├── index.md
│   │   ├── packaging.md
│   │   ├── dependencies-and-compatibility.md
│   │   ├── executable-workflow.md
│   │   ├── quality-and-testing.md
│   │   └── documentation-ci-and-releases.md
│   └── community/
│       ├── index.md
│       ├── governance.md
│       ├── compatibility-and-downstreams.md
│       ├── releases-and-continuity.md
│       └── scientific-python.md
├── migration/
│   ├── mapping.yaml
│   ├── sources/                   # Exact pre-migration source snapshots
│   └── rights-review.yaml
├── tools/
│   ├── versions.json
│   ├── bundle-policy.toml
│   └── compatibility-exceptions.json
├── scripts/
│   ├── check.py
│   └── bundle.py
├── tests/fixtures/
└── .github/workflows/
    ├── check.yml
    └── health.yml
```

This starts with 20 concepts and five reserved indexes. Split further only
when a topic becomes difficult to retrieve independently. Keep policy,
examples, and caveats together. Generated indexes contain navigation rather
than normative requirements.

Type assignments: `selection.md` is `Reference`; all three profiles and the
foundation/Python/community topics are `Blueprint`, except
`foundation/migration.md`, which is `Playbook`.

`selection.md` owns profile choice. Each profile owns scope, ordered adoption,
prerequisites, design principles, default decisions, and its acceptance
checklist. In particular, `profiles/harness-agnostic.md` owns the foundation's
core classification principle; `profiles/python.md` owns the Python design
principles and default-profile table. Topic concepts own implementation detail.
Community concepts link to baseline requirements and state additions or
tightening explicitly. Preserve all four blocking type checkers and every
existing coverage, compatibility, release, and exception commitment.

## Metadata, relationships, and trust

Require `type`, `title`, `description`, `tags`, `status`, `generated`, and custom `owner`
for authored concepts. Use `draft|stable|deprecated` for status. Document the
small tag vocabulary in bundle policy. These are local requirements; indexes
follow their separate reserved-file rules.

Use custom `x-requires` as a list of bundle-root concept IDs, without `.md`.
Keep prerequisites in visible prose too. The Python profile requires the
harness profile; the community profile requires the Python profile. Check
targets, prerequisite cycles, and consistency between metadata and profile
adoption order. Semantic policy ownership is recorded in the migration map
and reviewed; a graph alone cannot prove that requirements are not duplicated.

Use `sources` with IDs for authoritative external claims and version-sensitive
tool behavior. Attribute individual claims with footnotes keyed to those IDs.
Ordinary further-reading links may remain ordinary links. Preserve source
attribution during splitting; do not invent authorship or source timestamps.

Use `generated.by`/`generated.at` for actual production and meaningful changes.
Require both `generated.by` and `generated.at` under the local profile.
Actors are `human:<github-handle>`, `process:<id>`, or `<producer>/<version>`.
Agent authors record themselves accurately and must not create human
verification events. For this repo, only maintainers add `verified` following
an actual content review. Check actor syntax and human reviewer identity
against the explicit maintainer list in `tools/bundle-policy.toml`; require
maintainer review of verification changes. Detect stale sign-offs using the
spec-native comparison `verified.at < generated.at`, evaluating events
individually. Maintainers must update `generated.at` for meaningful changes;
cosmetic changes need not renew it. This timestamp signal cannot prove factual
truth or detect a falsely dated edit. Lint success is not verification
of factual content and must never create or refresh a human sign-off.

Declare the exact freshness scope as a concept-ID-to-review-class mapping in
`tools/bundle-policy.toml`, with classes `tool-behavior` and `policy`. Maintainers
classify every version-sensitive concept there during mapping review; do not
infer membership from prose. Both `check` and `health` load this same mapping.
Reject unknown concept IDs, selected concepts missing `stale_after`, and
concepts carrying `stale_after` outside the selection (add them to the mapping
or remove the field). New concepts require an explicit freshness-scope decision
in review. The universal `owner` requirement applies independently of scope.
Use explicit
timezone-aware ISO 8601 datetimes, not a parallel review-date field. Keep
existing verification events as history, and flag events predating the
current meaningful content change. Do not renew a review merely because a
URL responds. Date syntax is a deterministic PR check; overdue status is a
scheduled health finding. Recommend review within 90 days for tool behavior,
180 days for stable policy, with justified owner-assigned exceptions.

## Links, indexes, and standalone consumption

Prefer relative Markdown links for GitHub browsing. Accept and correctly
resolve bundle-root `/...` links as well. Validate files, heading fragments,
reference-style links, images, and local metadata paths. Reject path escapes,
symlinks, case collisions, and dependencies on repository-only files.

Every local link originating inside `knowledge/` must resolve inside the
bundle. Links to repository tooling or history must be external, preferably
commit-pinned URLs. Repository landing pages may link inward to concepts.
This boundary also applies to local `sources` references and other path-valued
metadata; `x-requires` is always an intra-bundle concept reference.

`scripts/bundle.py` is the sole index generator. Emit the §8 heading-and-bullet
shape deterministically, sort entries consistently, and copy descriptions
from frontmatter. Always emit `okf_version: "0.2"` in the root index's
frontmatter; other indexes have no frontmatter. Include every concept and
child directory. `check` generates into a temporary tree, compares output,
and separately asserts the root version declaration. Do not run `okf index`
as another writer. Report disconnected narrative subgraphs as advisory
findings in addition to enforcing reachability through navigation.

Keep example scripts, MCP JSON, and README templates in their existing concept
fences initially. Extract explicitly designated complete examples into
temporary files for syntax checks or executable tests. Use a Markdown AST,
including fence boundaries, for extraction and splitting. Incomplete examples
must be identified rather than accidentally executed. Do not add a second
authoritative copy of a template under repository tooling.

## Tooling and command ownership

Use a lightweight non-package uv project and a committed `uv.lock`. This
documentation repository does not implement the full application blueprint.
`scripts/check.py check` remains the single completion gate, implemented with
documentation-oriented checks rather than the baseline application's exact
subcommand set. Local hooks and CI call the same runner.

The repo validator in `scripts/bundle.py`, using maintained YAML/Markdown
parsers, owns blocking conformance, local metadata, paths, and freshness-syntax
checks. Test it against spec examples and deliberately invalid fixtures.

Evaluate community `okfcli/okf` as an advisory independent cross-check, starting
with the inspected release v0.5.1. Its lifecycle validator parses
`stale_after` as `YYYY-MM-DD` and rejects the spec's datetime example; its
indexer preserves an existing root version but does not add it. These are
tool compatibility findings, not reasons to change the bundle's format.
See [v0.5.1 validation source](https://github.com/okfcli/okf/blob/v0.5.1/internal/validate/v02.go)
and [index source](https://github.com/okfcli/okf/blob/v0.5.1/internal/index/index.go).
Do not use the CLI's raw exit status as the blocking bundle gate. Never
rewrite datetime metadata to accommodate the tool.

Before selecting its pin, evaluate all four canonical upstream bundles
(`acme_retail`, `crypto_bitcoin`, `ga4`, `stackoverflow`) at recorded immutable
commits, alongside minimal fixtures for dates, indexes, unknown fields,
reserved files, and broken links. Record exact expected findings by tool
version, fixture, rule ID, rationale, owner, and review deadline. Unexpected
findings or execution failures fail tool qualification. Normal PR checks
remain independent of the advisory CLI; qualify upgrades before changing its
pin. Store licensed fixture snapshots locally so checks do not fetch them.

Use mdformat with pinned compatible frontmatter/GFM plugins, codespell,
targeted ShellCheck, and Lychee for scheduled external links. Formatting
round-trip fixtures must preserve frontmatter, tables, fences, and semantics.
Python dependencies live in `uv.lock`; separately downloaded tools (including
uv, the optional OKF CLI, Lychee, and ShellCheck) have exact versions,
immutable download sources, supported platform assets, SHA-256 checksums, and
version checks in `tools/versions.json`. Pin Actions by commit. Establish
these actual pins during the tooling step rather than inventing untested
version numbers in this plan. Bootstrap may use network; `check` and archive
validation must run offline after dependencies and fixtures are provisioned.

The runner owns explicit file lists for each check, rather than relying on
tool-specific glob or exclusion support. `migration/sources/**` is immutable
evidence: exclude it from formatting, spelling, hygiene rewrites, and
link/fragment checks, including scheduled external-link checks. Its only
automated content check is SHA-256 recomputation against the mapping. Every
auto-fix entry point must refuse to write those snapshots. Apply the same
scope exclusions consistently across local hooks, CI, and health checks.

Generated indexes and root landing pages are written only by the generator;
formatting tools check them without rewriting them. Require generator output
to be formatter-stable, with committed representative fixtures for the root
index, a sub-index, and a landing page containing named anchors and duplicate
headings: `mdformat(generated) == generated`. If a required construct cannot
be made stable, document a narrowly scoped format-check exclusion and retain
raw generation-drift and rendered-anchor checks. In `check`, run format checks
before comparing raw generated output against committed files. Do not apply
one-sided normalization or let an auto-fix silently reverse the drift check.

Proposed commands:

```bash
uv run --locked python scripts/check.py check
uv run --locked python scripts/check.py index
uv run --locked python scripts/check.py health
uv run --locked python scripts/check.py package
```

- `check`: no source edits, no external network, no wall-clock-dependent
  failures. Includes conformance/local policy, links/fragments, inheritance,
  mapping coverage, index drift, hygiene, example checks, and focused tooling
  tests. Reject malformed deadlines and exceptions regardless of current date.
- `index`: explicit regeneration through the one generator.
- `health`: scheduled external-link retries, overdue reviews, stale
  verification, upstream-spec changes, and advisory tool/graph findings.
  Publish a machine-readable report for maintainer triage; do not fail an
  unrelated PR because time passed. Exceptions require reason, owner, and
  bounded expiration, which health checks report when expired.
- `package`: run the completion gate, enforce the rights/license gate below,
  build the allow-listed archive, extract it outside the checkout, and apply
  the same bundle validator to that extracted root. No publishing.

The archive root contains `index.md` and the bundle directories directly.
Explicitly add approved `LICENSE.txt` and `NOTICE.txt` from the rights record;
retain required third-party notices. Do not include repository instructions,
tooling, test fixtures, or migration records. Check exact member inventory,
reject unsafe paths and symlinks, and validate all local references after
extraction. Keep release/provenance metadata outside the bundle archive unless
explicitly included in the allow-list. The validator receives the extracted
root as input; bundle consumption itself needs no Python environment.

## Content preservation and legacy compatibility

Before splitting, record the source Git commit and hashes of the four current
Markdown files. Commit exact copies in `migration/sources/`, with their hashes
recorded in `migration/mapping.yaml`. Reconstruction checks use those local,
hash-verified snapshots, so shallow clones and offline checks do not require
the original Git objects. The source commit remains provenance; fetching it
is not a hidden validation prerequisite. Include these snapshots in the rights
inventory and exclude them from the bundle archive. Commit stable mapping
entries for every
real heading and content block, source file/anchor/block hash, destination
concept and heading, type, and policy owner. Treat fenced template headings
as content, not section boundaries. Assign explicit owners to cross-cutting
principles and acceptance items rather than putting them in generated indexes.

Use block-level accounting and a reconstruction comparison against the source
revision. Allow only recorded heading, link, and citation relocation transforms
in the initial structural conversion; keep code/template bytes unchanged.
Show normalized reconstruction diffs for human review rather than claiming
that normalization proves semantic equivalence. Any omission, duplicate,
rewrite, or rights-driven replacement needs an explicit mapping disposition,
reviewed diff, reason, and maintainer acceptance. Defer unrelated policy changes
to separate work. Preserve technical requirements in any approved replacement.

Keep the three original filenames as generated landing pages with a section
map and the full set of original actual heading anchors, including anchors
currently targeted by the community table. Prefer reproducing original heading
text and order so native GitHub slugs, including duplicate-heading suffixes,
remain unchanged. Where a rename is unavoidable, use a compatible named
anchor such as `<a name="old-slug"></a>`; do not rely on raw HTML `id`
attributes surviving GitHub sanitization. Include these anchors and duplicate
headings in formatter round-trip fixtures. At migration acceptance, render
all three landing pages with a local renderer using GitHub's heading-slug and
sanitization behavior, then test every legacy fragment against the rendered
anchor targets. Record the renderer version and results; source-only checking
does not certify rendered compatibility. If that renderer cannot demonstrate
compatibility, keep the original headings instead of relying on HTML anchors.
Generate these pages from the mapping, not a second hand-maintained list.
Rewrite inter-concept links to canonical destinations. Validate both the new
bundle and old entry points. Do not promise HTTP redirects for Markdown
fragments. Full reading editions can be added later as generated outputs.

## Rights and publication prerequisite

The repo currently has no explicit license file and credits a third-party
gist. Record the origin and permission status of borrowed prose, scripts,
and templates in `migration/rights-review.yaml`; line similarity is a signal
for review, not a legal determination. Attribution alone is not the project's
record of permission. The original plan did not select Apache-2.0, and this
revision does not select or apply any license automatically.

Before producing a distributable archive or publishing migrated content, a
maintainer must select the appropriate license, confirm rights and required
notices, and record permission, an existing applicable grant, an approved
replacement, or exclusion for each uncertain source. If necessary, obtain
permission or replace affected material while preserving intended requirements.
Do not send requests to third parties as part of this planning task.

This is a hard distribution acceptance gate, not a prerequisite to approving
the plan or doing unpublished structural/tooling work. While unresolved,
technical staging checks may run but `package` must refuse to produce a
distributable artifact. Fixture redistribution also requires applicable notices.

## Implementation sequence and acceptance

1. Establish the pinned spec contract, local metadata/types/identity policy,
   rights inventory, and source-to-concept mapping before moving content.
1. Build and test the small runner, validator, sole index generator, exact
   tool pins, golden fixtures, and compatibility report. Demonstrate offline
   validation and the known datetime discrepancy without adopting that dialect.
1. Pilot the foundation using AST-aware extraction. Verify unchanged scripts
   and templates, reconstruction accounting, anchors, and retrieval paths.
1. Convert Python and community topics. Review inheritance, policy owners,
   all four typing gates, coverage/compatibility commitments, and sources.
1. Generate legacy landing pages and indexes; run required PR checks and
   scheduled health reporting. Document setup and diagnosis in CONTRIBUTING.md.
1. After the rights gate is satisfied, validate the extracted standalone
   archive and record the exact source commit and archive digest. Publishing
   is a separate authorized action; tags alone do not authorize publication.

Completion requires every source block and requirement accounted for with
reviewed dispositions; no accidental policy weakening; valid metadata;
complete navigation; working internal links, anchors, and prerequisites;
one owner per policy; repeatable indexes; passing focused regression tests;
and a rights-cleared standalone archive that validates offline. Exercise
fixtures with missing types, invalid datetimes, missing root version, index
drift, broken fragments, path escapes, prerequisite cycles, unaccounted
source blocks, and incomplete examples. Human review remains necessary for
truth, policy meaning, and rights clearance.

Finally, perform three retrieval checks from `knowledge/index.md` without
opening the original blueprints: start a harness-agnostic repo; identify the
Python baseline's stack and gates; identify only the community additions and
their prerequisites. Record expected concepts and answers in test fixtures
and compare with maintainer-reviewed expectations.
