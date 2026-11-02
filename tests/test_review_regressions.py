"""Adversarial regressions found by independent implementation reviewers."""

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import bundle
import check
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def clone(tmp_path):
    root = tmp_path / "checkout"
    root.mkdir()
    for name in ("knowledge", "migration", "tools", "scripts"):
        shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns("__pycache__"))
    for path in ROOT.glob("*.md"):
        shutil.copy(path, root)
    shutil.copy(ROOT / "pyproject.toml", root)
    return root


@pytest.mark.parametrize(
    "command,kind",
    [
        ("fmt", "concept"),
        ("fmt", "python"),
        ("fmt", "directory"),
        ("index", "root-index"),
        ("index", "landing"),
        ("index", "directory"),
    ],
)
def test_cli_writers_refuse_symlinks_before_any_source_write(clone, tmp_path, command, kind):
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n\nText   with extra spaces.\n")
    if kind == "concept":
        path = clone / "knowledge/selection.md"
    elif kind == "python":
        path = clone / "scripts/unrelated.py"
    elif kind == "root-index":
        path = clone / "knowledge/index.md"
    elif kind == "landing":
        path = clone / "python-project.md"
    else:
        path = clone / "knowledge/python"
        shutil.rmtree(path)
        path.symlink_to(tmp_path, target_is_directory=True)
    if kind != "directory":
        path.unlink(missing_ok=True)
        path.symlink_to(outside)
    before = outside.read_bytes()
    source_before = (clone / "knowledge/profiles/python.md").read_bytes()
    result = subprocess.run(
        [sys.executable, str(clone / "scripts/check.py"), command],
        cwd=clone,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "symlink" in result.stderr
    assert "Traceback" not in result.stderr
    assert outside.read_bytes() == before
    assert (clone / "knowledge/profiles/python.md").read_bytes() == source_before


@pytest.mark.parametrize(
    "mutation", ["drop-block", "duplicate-block", "block-type", "heading-title", "heading-level"]
)
def test_accounting_is_recomputed_from_ast(clone, mutation):
    mapping = bundle.load_yaml((clone / "migration/mapping.yaml").read_text())
    source = mapping["sources"]["python-project.md"]
    if mutation == "drop-block":
        source["units"][1]["blocks"].pop()
    elif mutation == "duplicate-block":
        source["units"][1]["blocks"].append(copy.deepcopy(source["units"][1]["blocks"][0]))
    elif mutation == "block-type":
        source["units"][1]["blocks"][0]["type"] = "paragraph_open"
    elif mutation == "heading-title":
        source["headings"][0]["title"] = "A different title with the same stored slug"
    else:
        source["headings"][0]["level"] = 6
    errors = bundle.migration_check(clone, mapping)
    assert any("block inventory" in e or "unaccounted heading" in e for e in errors)


def test_coordinated_snapshot_concept_and_hash_tampering_cannot_rebaseline(clone):
    mapping = bundle.load_yaml((clone / "migration/mapping.yaml").read_text())
    snapshot = clone / "migration/sources/python-project.md"
    snapshot.write_text(snapshot.read_text().replace("95%", "50%"))
    lines = snapshot.read_text().splitlines(keepends=True)
    source = mapping["sources"]["python-project.md"]
    source["sha256"] = bundle.sha(snapshot.read_bytes())
    for unit in source["units"]:
        unit["sha256"] = bundle.sha("".join(lines[unit["start"] : unit["end"]]).encode())
        for block in unit["blocks"]:
            block["sha256"] = bundle.sha("".join(lines[block["start"] : block["end"]]).encode())
    for cid, record in mapping["concepts"].items():
        path = clone / "knowledge" / (cid + ".md")
        path.write_text(path.read_text().replace("95%", "50%"))
        _, body = bundle.frontmatter(path.read_text())
        record["body_sha256"] = bundle.sha(body.encode())
    errors = bundle.migration_check(clone, mapping)
    assert any("pinned Git tree" in e for e in errors)
    assert any("independently pinned" in e for e in errors)


def test_git_proof_is_offline_and_rejects_a_replaced_commit(clone):
    mapping = bundle.load_yaml((clone / "migration/mapping.yaml").read_text())
    assert not (clone / ".git").exists()
    assert not bundle.source_proof_check(clone, mapping)
    mapping["source_commit"] = "0" * 40
    assert any("source_commit" in e for e in bundle.source_proof_check(clone, mapping))


@pytest.mark.parametrize(
    "case", ["missing-definition", "unmatched", "uncited", "valid", "prose-note"]
)
def test_citations_are_a_bidirectional_local_contract(case):
    source_ids = {"source"}
    bodies = {
        "missing-definition": "Text[^source].\n",
        "unmatched": "Text[^wrong].\n\n[^wrong]: Wrong.\n",
        "uncited": "Text.\n\n[^source]: Unused.\n",
        "valid": "Text[^source].\n\n[^source]: The source.\n",
        "prose-note": "Text[^source] and note[^note-extra].\n\n[^source]: The source.\n[^note-extra]: A note.\n",
    }
    errors = bundle.citation_errors(bodies[case], source_ids)
    assert bool(errors) == (case not in {"valid", "prose-note"})


def test_scope_descriptors_and_extensionless_paths_are_distinguished(clone):
    assert bundle.source_is_scope("all queries in project.example.com")
    assert bundle.source_is_scope("scope:single-word")
    assert not bundle.source_is_scope("references/attesters/missing")
    with pytest.raises(ValueError, match="missing target"):
        bundle.check_target(
            clone / "knowledge", clone / "knowledge/selection.md", "references/attesters/missing"
        )


@pytest.mark.parametrize("mutation", ["missing-date", "bad-date", "bad-event", "missing-generated"])
def test_health_reports_malformed_review_metadata(clone, monkeypatch, mutation):
    import yaml

    path = clone / "knowledge/selection.md"
    meta, body = bundle.frontmatter(path.read_text())
    if mutation == "missing-date":
        meta.pop("stale_after")
    elif mutation == "bad-date":
        meta["stale_after"] = "not-a-datetime"
    elif mutation == "missing-generated":
        meta["verified"] = {"by": "process:fixture", "at": "2026-01-01T00:00:00Z"}
        meta.pop("generated")
    else:
        meta["verified"] = [42]
    path.write_text("---\n" + yaml.safe_dump(meta) + "---\n\n" + body)
    monkeypatch.setattr(check, "ROOT", clone)
    check.health(offline=True)
    report = json.loads((clone / "reports/health.json").read_text())
    assert any(f["rule"] in {"bundle-validation", "review-metadata"} for f in report["findings"])


@pytest.mark.parametrize("mutation", ["omitted", "duplicate", "unknown"])
def test_example_inventory_is_complete(clone, monkeypatch, mutation):
    path = clone / "tools/examples.json"
    manifest = json.loads(path.read_text())
    if mutation == "omitted":
        manifest["examples"].pop()
    elif mutation == "duplicate":
        manifest["examples"].append(copy.deepcopy(manifest["examples"][0]))
    else:
        manifest["examples"][0]["fence"] = 99
    path.write_text(json.dumps(manifest))
    monkeypatch.setattr(check, "ROOT", clone)
    monkeypatch.setattr(check, "tool", lambda _name: ROOT / ".tools/bin/shellcheck")
    errors = check.examples()
    assert any("inventory" in e or "unclassified" in e for e in errors)


def test_qualification_exceptions_must_match_actual_recorded_findings(clone, monkeypatch):
    monkeypatch.setattr(check, "ROOT", clone)
    assert not check.compatibility_contract()
    path = clone / "tools/compatibility-exceptions.json"
    data = json.loads(path.read_text())
    data["entries"].pop()
    path.write_text(json.dumps(data))
    assert check.compatibility_contract()


@pytest.mark.parametrize("field", ["title", "description"])
def test_generator_metadata_errors_are_clean_cli_diagnostics(clone, field):
    import yaml

    path = clone / "knowledge/selection.md"
    meta, body = bundle.frontmatter(path.read_text())
    del meta[field]
    path.write_text("---\n" + yaml.safe_dump(meta) + "---\n\n" + body)
    result = subprocess.run(
        [sys.executable, str(clone / "scripts/check.py"), "check"],
        cwd=clone,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert field in result.stderr and "Traceback" not in result.stderr


def test_index_generator_has_a_directory_label_fallback(tmp_path):
    path = tmp_path / "newdir/concept.md"
    path.parent.mkdir()
    path.write_text(
        "---\ntype: Reference\ntitle: Example\ndescription: Example concept.\n---\n# Example\n"
    )
    output = bundle.index_outputs(tmp_path, {"directories": {".": "Example bundle"}})
    assert "newdir/index.md" in output[tmp_path / "index.md"]


@pytest.mark.parametrize(
    "quoted",
    [
        "`[example](python-project.md)`",
        "``[example](python-project.md)``",
        "`first line\n[example](python-project.md)`",
        "~~~markdown\n[example](python-project.md)\n~~~\n",
    ],
)
def test_link_relocation_preserves_code_and_still_rewrites_real_links(quoted):
    mapping = bundle.load_yaml((ROOT / "migration/mapping.yaml").read_text())
    raw = quoted + "\n\n[Actual](python-project.md)\n"
    rewritten = bundle.rewrite_source_links(
        raw, "python-project-community.md", "community/governance", mapping
    )
    assert quoted in rewritten
    assert "[Actual](../profiles/python.md)" in rewritten


def test_escaped_backticks_are_not_mistaken_for_code():
    mapping = bundle.load_yaml((ROOT / "migration/mapping.yaml").read_text())
    raw = r"\`[Actual](python-project.md)\`"
    assert "[Actual](../profiles/python.md)" in bundle.rewrite_source_links(
        raw, "python-project-community.md", "community/governance", mapping
    )


def test_health_report_cannot_follow_a_symlink(clone, tmp_path, monkeypatch):
    outside = tmp_path / "outside-reports"
    outside.mkdir()
    sentinel = outside / "health.json"
    sentinel.write_text("Do not overwrite.\n")
    (clone / "reports").symlink_to(outside, target_is_directory=True)
    monkeypatch.setattr(check, "ROOT", clone)
    with pytest.raises(ValueError, match="symlink"):
        check.health(offline=True)
    assert sentinel.read_text() == "Do not overwrite.\n"


@pytest.mark.parametrize(
    "resource,expected",
    [
        ("a file.txt", True),
        ("./a file.txt", False),
        ("scope:all queries in project/dataset", True),
        ("references/no-extension", False),
    ],
)
def test_scope_ambiguity_has_explicit_path_and_scope_prefixes(resource, expected):
    assert bundle.source_is_scope(resource) is expected


def test_package_receipt_symlink_is_rejected_before_archive_creation(clone, tmp_path, monkeypatch):
    outside = tmp_path / "outside-receipt.json"
    outside.write_text("Unchanged.\n")
    (clone / "dist").mkdir()
    (clone / "dist/provenance.json").symlink_to(outside)
    monkeypatch.setattr(check, "ROOT", clone)
    monkeypatch.setattr(check, "check", lambda: None)
    monkeypatch.setattr(sys, "argv", ["check.py", "package"])

    def must_not_build(*_args):
        pytest.fail("archive construction must not begin for an unsafe receipt path")

    monkeypatch.setattr(check, "build_archive", must_not_build)
    assert check.main() == 1
    assert outside.read_text() == "Unchanged.\n"


def test_shared_atomic_writer_rejects_binary_symlinks(tmp_path):
    import files

    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside-binary"
    outside.write_bytes(b"Unchanged")
    (root / "binary").symlink_to(outside)
    with pytest.raises(ValueError, match="symlink"):
        files.write_bytes(root, root / "binary", b"Replacement", mode=0o755)
    assert outside.read_bytes() == b"Unchanged"
