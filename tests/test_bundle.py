"""Boundary tests for the bundle format, source preservation, and distribution."""

import difflib
import json
import shutil
import subprocess
from pathlib import Path

import bundle
import check
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def sample(tmp_path):
    policy = {
        "types": ["Blueprint", "Reference", "Playbook"],
        "tags": ["policy"],
        "maintainers": ["human:test-maintainer"],
        "freshness": {"concept": "policy"},
        "profile_requires": {},
        "directories": {".": "Example"},
    }
    meta = {
        "type": "Blueprint",
        "title": "Example",
        "description": "A small example.",
        "tags": ["policy"],
        "status": "draft",
        "owner": "test maintainers",
        "generated": {"by": "process:test", "at": "2026-01-01T00:00:00Z"},
        "stale_after": "2026-07-01T00:00:00+00:00",
        "x-requires": [],
    }

    def write(data=None, body="# Example\n\n## Details\n\nExample text.\n"):
        import yaml

        (tmp_path / "concept.md").write_text(
            "---\n" + yaml.safe_dump(meta if data is None else data) + "---\n\n" + body
        )

    write()
    (tmp_path / "index.md").write_text(
        '---\nokf_version: "0.2"\n---\n\n# Example\n\n- [Example](concept.md) - A small example.\n'
    )
    return tmp_path, policy, meta, write


def test_valid_unknown_extension_and_full_datetime(sample):
    root, policy, meta, write = sample
    meta["x-unregistered"] = {"opaque": "preserved"}
    meta["verified"] = {"by": "human:test-maintainer", "at": "2026-01-02T00:00:00Z"}
    write(meta)
    assert bundle.validate(root, policy) == []


@pytest.mark.parametrize(
    "field,value,fragment",
    [
        ("type", None, "type"),
        ("tags", "policy", "tags"),
        ("status", "approved", "status"),
        ("generated", {}, "generated"),
        ("stale_after", "2027-01-01", "stale_after"),
        ("stale_after", "2027-01-01T00:00:00", "stale_after"),
        ("verified", {"by": "human:invented", "at": "2026-01-01T00:00:00Z"}, "maintainer"),
        ("x-requires", ["absent"], "prerequisite"),
    ],
)
def test_metadata_boundary_failures(sample, field, value, fragment):
    root, policy, meta, write = sample
    meta[field] = value
    write(meta)
    assert any(fragment in error for error in bundle.validate(root, policy))


def test_duplicate_yaml_and_missing_frontmatter(sample):
    root, policy, _, _ = sample
    (root / "concept.md").write_text("---\ntype: Blueprint\ntype: Reference\n---\n# Example\n")
    assert any("duplicate" in e for e in bundle.validate(root, policy))
    (root / "concept.md").write_text("# Example\n")
    assert any("frontmatter" in e for e in bundle.validate(root, policy))


def test_root_version_is_required_only_by_local_policy(sample):
    root, policy, _, _ = sample
    (root / "index.md").write_text("# Example\n")
    assert any("version" in e for e in bundle.validate(root, policy))
    assert not bundle.validate(root)


def test_freshness_selection_is_bidirectional(sample):
    root, policy, meta, write = sample
    del meta["stale_after"]
    write(meta)
    assert any("scope" in e for e in bundle.validate(root, policy))
    policy["freshness"] = {}
    assert bundle.validate(root, policy) == []
    meta["stale_after"] = "2027-01-01T00:00:00Z"
    write(meta)
    assert any("scope" in e for e in bundle.validate(root, policy))


def test_prerequisite_cycles(sample):
    root, policy, meta, write = sample
    meta["x-requires"] = ["concept"]
    write(meta)
    assert any("cycle" in e for e in bundle.validate(root, policy))


@pytest.mark.parametrize(
    "target,fragment",
    [
        ("concept.md#missing", "fragment"),
        ("missing.md", "missing"),
        ("../outside.md", "escapes"),
        ("%2e%2e/outside.md", "escapes"),
        ("/../outside.md", "escapes"),
    ],
)
def test_links_and_path_escape(sample, target, fragment):
    root, policy, meta, write = sample
    write(meta, "# Example\n\n[Target](" + target + ")\n")
    assert any(fragment in e for e in bundle.validate(root, policy))


def test_reference_links_images_root_links_and_ignored_code(sample):
    root, policy, meta, write = sample
    write(
        meta,
        "# Example\n\n[Reference][r] ![Alt](/concept.md#example)\n\n[r]: concept.md#example\n\n```markdown\n[Not a link](missing.md)\n```\n",
    )
    assert bundle.validate(root, policy) == []
    write(meta, "# Example\n\n![Image](missing.png)\n")
    assert any("missing.png" in e for e in bundle.validate(root, policy))


@pytest.mark.parametrize("resource", ["../scripts/check.py", "concept.md#absent", 42])
def test_source_metadata_obeys_the_same_path_and_fragment_boundary(sample, resource):
    root, policy, meta, write = sample
    meta["sources"] = [{"id": "source", "resource": resource}]
    write(meta)
    assert bundle.validate(root, policy)


def test_invalid_utf8_is_a_diagnostic(sample):
    root, policy, _, _ = sample
    (root / "concept.md").write_bytes(b"\xff\n")
    assert bundle.validate(root, policy)


def test_symlinks_are_rejected_before_traversing(sample):
    root, policy, _, _ = sample
    (root / "alias.md").symlink_to(root / "concept.md")
    assert any("symlink" in e for e in bundle.validate(root, policy))


def test_rendered_anchor_model_sanitizes_html_and_handles_duplicate_headings():
    text = '# One `code`\n\n## Details\n\n## Details\n\n<a name="old-slug"></a>\n\n<a id="stripped-id"></a>\n'
    targets = bundle.rendered_anchors(text)
    assert {"one-code", "details", "details-1", "old-slug"} <= targets
    assert "stripped-id" not in targets


def test_real_mapping_preserves_sources_and_legacy_rendered_targets():
    mapping = bundle.load_yaml((ROOT / "migration/mapping.yaml").read_text())
    assert not bundle.migration_check(ROOT, mapping)


def test_mapping_catches_unclaimed_blocks_and_snapshot_tampering(tmp_path):
    shutil.copytree(ROOT / "migration", tmp_path / "migration")
    shutil.copytree(ROOT / "knowledge", tmp_path / "knowledge")
    for path in ROOT.glob("*-project*.md"):
        shutil.copy(path, tmp_path)
    mapping = bundle.load_yaml((tmp_path / "migration/mapping.yaml").read_text())
    mapping["sources"]["python-project.md"]["units"][-1]["end"] -= 1
    assert any(
        "tail" in e or "reconstruction" in e for e in bundle.migration_check(tmp_path, mapping)
    )
    source = tmp_path / "migration/sources/README.md"
    source.write_text(source.read_text() + "changed\n")
    assert any("immutable" in e for e in bundle.migration_check(tmp_path, mapping))


def test_intentional_revision_requires_exact_diff_and_configured_human(tmp_path):
    shutil.copytree(ROOT / "migration", tmp_path / "migration")
    shutil.copytree(ROOT / "knowledge", tmp_path / "knowledge")
    (tmp_path / "tools").mkdir()
    policy_path = tmp_path / "tools/bundle-policy.toml"
    policy_path.write_text((ROOT / "tools/bundle-policy.toml").read_text())
    for path in ROOT.glob("*-project*.md"):
        shutil.copy(path, tmp_path)
    mapping = bundle.load_yaml((tmp_path / "migration/mapping.yaml").read_text())
    path = tmp_path / "knowledge/selection.md"
    original = path.read_text()
    _, body = bundle.frontmatter(original)
    changed = bundle.formatted(body + "\nFixture-only intentional content change.\n")
    path.write_text(original[: len(original) - len(body)] + changed)
    assert any("content differs" in e for e in bundle.migration_check(tmp_path, mapping))
    diff = "".join(
        difflib.unified_diff(
            body.splitlines(keepends=True),
            changed.splitlines(keepends=True),
            fromfile="source-reconstruction",
            tofile="selection.md",
        )
    )
    mapping["concepts"]["selection"]["approved_change"] = {
        "by": "human:test-maintainer",
        "at": "2026-11-02T00:00:00Z",
        "reason": "Synthetic test approval, never applied to the real content.",
        "body_sha256": bundle.sha(changed.encode()),
        "diff_sha256": bundle.sha(diff.encode()),
    }
    assert any("content differs" in e for e in bundle.migration_check(tmp_path, mapping))
    policy_path.write_text(
        policy_path.read_text().replace(
            "maintainers = []", 'maintainers = ["human:test-maintainer"]'
        )
    )
    assert not bundle.migration_check(tmp_path, mapping)
    path.write_text(path.read_text() + "\nUnapproved later change.\n")
    assert any("content differs" in e for e in bundle.migration_check(tmp_path, mapping))


def test_generated_fixtures_are_formatter_stable():
    for path in (ROOT / "tests/fixtures/generated").glob("*.md"):
        text = path.read_text()
        assert bundle.formatted(text) == text, path


def test_generation_detects_drift_without_editing_source(tmp_path):
    root = tmp_path / "knowledge"
    shutil.copytree(ROOT / "knowledge", root)
    before = {p: p.read_bytes() for p in root.rglob("*.md")}
    output = bundle.index_outputs(root, check.read_config())
    assert all(path.read_text() == text for path, text in output.items())
    (root / "index.md").write_text("# Drift\n")
    assert output[root / "index.md"] != (root / "index.md").read_text()
    assert all(p.read_bytes() == data for p, data in before.items() if p != root / "index.md")


def test_distribution_refuses_uncleared_rights_before_writing(tmp_path):
    with pytest.raises(ValueError, match="Distribution blocked"):
        check.build_archive(ROOT, tmp_path / "should-not-exist.zip")
    assert not (tmp_path / "should-not-exist.zip").exists()


def test_cleared_synthetic_archive_validates_outside_checkout(sample, tmp_path, monkeypatch):
    import yaml

    root, policy, _, _ = sample
    concepts = root / "knowledge"
    concepts.mkdir()
    for name in ("index.md", "concept.md"):
        shutil.move(root / name, concepts / name)
    (root / "migration").mkdir()
    (root / "LICENSE.txt").write_text("Synthetic test fixture license; not a repository license.\n")
    rights = {
        "status": "cleared",
        "license": "LicenseRef-Synthetic-Test",
        "maintainer_approval": {"by": "human:test-maintainer", "at": "2026-01-01T00:00:00Z"},
        "sources": [
            {
                "id": "synthetic",
                "status": "cleared",
                "scope": ["knowledge/**"],
                "evidence": "Synthetic fixture only.",
                "required_notices": [],
            }
        ],
        "archive_notices": [
            {
                "archive_path": "LICENSE.txt",
                "source": "LICENSE.txt",
                "sha256": bundle.sha((root / "LICENSE.txt").read_bytes()),
            }
        ],
    }
    (root / "migration/rights-review.yaml").write_text(yaml.safe_dump(rights))
    monkeypatch.setattr(check, "read_config", lambda _root=None: policy)
    monkeypatch.setattr(subprocess, "check_output", lambda *_a, **_k: "synthetic-source-commit\n")
    destination = root / "result.zip"
    receipt = check.build_archive(root, destination)
    assert receipt["members"] == ["LICENSE.txt", "concept.md", "index.md"]
    first = destination.read_bytes()
    check.build_archive(root, destination)
    assert destination.read_bytes() == first
    policy["archive_assets"] = ["missing.dat"]
    with pytest.raises(ValueError, match="declared archive assets are missing"):
        check.build_archive(root, destination)
    policy.pop("archive_assets")
    rights["sources"][0]["required_notices"] = ["NOTICE.txt"]
    (root / "migration/rights-review.yaml").write_text(yaml.safe_dump(rights))
    with pytest.raises(ValueError, match="required approved"):
        check.build_archive(root, destination)
    rights["sources"][0]["required_notices"] = []
    rights["sources"][0]["scope"] = ["knowledge/unrelated/**"]
    (root / "migration/rights-review.yaml").write_text(yaml.safe_dump(rights))
    with pytest.raises(ValueError, match="rights scope"):
        check.build_archive(root, destination)
    assert destination.read_bytes() == first
    rights["sources"][0]["scope"] = ["knowledge/**"]
    (root / "migration/rights-review.yaml").write_text(yaml.safe_dump(rights))
    (concepts / "secret.env").write_text("This must never enter the archive.\n")
    with pytest.raises(ValueError, match="unlisted"):
        check.build_archive(root, destination)
    assert destination.read_bytes() == first


def test_original_sync_script_on_clean_repo_and_conflict(tmp_path):
    _, body = bundle.frontmatter((ROOT / "knowledge/foundation/skills.md").read_text())
    script = next(
        t.content
        for t in bundle.MD.parse(body)
        if t.type == "fence" and t.content.startswith("#!/usr/bin/env bash")
    )
    path = tmp_path / ".agents/scripts/sync-skills.sh"
    path.parent.mkdir(parents=True)
    path.write_text(script)
    skill = tmp_path / ".agents/skills/example/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("---\nname: example\ndescription: Example.\n---\n")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    first = subprocess.run(["bash", str(path)], cwd=tmp_path, capture_output=True, text=True)
    assert first.returncode == 1, first.stdout + first.stderr
    assert (tmp_path / ".claude/skills/example").is_symlink()
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    assert subprocess.run(["bash", str(path)], cwd=tmp_path, capture_output=True).returncode == 0
    (tmp_path / ".claude/skills/example").unlink()
    (tmp_path / ".claude/skills/example").mkdir()
    assert subprocess.run(["bash", str(path)], cwd=tmp_path, capture_output=True).returncode == 2


def test_retrieval_from_index_without_legacy_documents():
    root = ROOT / "knowledge"
    tasks = json.loads((ROOT / "tests/fixtures/retrieval.json").read_text())
    reachable, pending = set(), [root / "index.md"]
    while pending:
        path = pending.pop()
        if path in reachable:
            continue
        reachable.add(path)
        for target in bundle.links(path.read_text()):
            destination, _ = bundle.resolve_local(root, path, target)
            if destination and destination.suffix == ".md":
                pending.append(destination)
    concepts, _ = bundle.read_concepts(root)
    assert all(c.path in reachable for c in concepts.values())
    for task in tasks:
        for cid, terms in task["expected"].items():
            concept = concepts[cid]
            assert concept.path in reachable
            assert all(term in concept.body for term in terms), task["task"]
