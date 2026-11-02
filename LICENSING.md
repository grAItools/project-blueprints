# Licensing

The project's original documentation, knowledge concepts, examples, and tooling
are licensed under the [MIT License](LICENSE.txt), to the extent the project
contributors hold the rights to license them. This includes the validation
scripts under `scripts/` and the project's own tests and configuration.

Third-party material is excluded from this grant:

- **Harness integration reference:** material reused or adapted from
  [davidgibsonp's Agent-Agnostic Repository Guide](https://gist.github.com/davidgibsonp/337be9b80b3f03eccd188235c287bb05)
  has no established license or permission in the project's records. It is
  not offered under MIT by this project. The potentially affected paths are
  `knowledge/profiles/harness-agnostic.md`, `knowledge/foundation/**`, and
  `migration/sources/harness-agnostic-project.md`. Attribution is preserved;
  it does not establish permission to redistribute that material.
- **Upstream OKF fixtures:** `tests/fixtures/upstream/` retains its own
  Apache-2.0 license and notices. These fixtures are excluded from the bundle
  archive.
- **Immutable migration snapshots:** `migration/sources/` preserves historical
  source bytes. The MIT grant covers only project-owned portions of those
  files; it does not relicense included third-party material.

The MIT selection was authorized by the repository user. It does not record
third-party permission or human content verification. The detailed distribution
inventory remains in [migration/rights-review.yaml](migration/rights-review.yaml).
Packaging remains blocked until the outstanding permissions and distribution
approval are recorded; adding a license does not clear those entries.
