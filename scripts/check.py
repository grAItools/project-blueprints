"""One command owner for OKF validation, navigation, health and packaging."""

from __future__ import annotations

import argparse
import collections
import fnmatch
import json
import re
import subprocess
import sys
import tempfile
import tomllib
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import bundle
import files

ROOT = Path(__file__).resolve().parents[1]


def read_config(root=ROOT):
    return tomllib.loads((root / "tools/bundle-policy.toml").read_text())


def execute(args, **kwargs):
    display = list(map(str, args))
    if len(display) > 12:
        display = display[:4] + [f"[{len(display) - 4} explicit paths]"]
    print("+ " + " ".join(display), flush=True)
    subprocess.run(list(map(str, args)), check=True, cwd=ROOT, **kwargs)


def tool(name, required=True):
    config = json.loads((ROOT / "tools/versions.json").read_text())["tools"][name]
    path = ROOT / ".tools/bin" / config["binary"]
    if not path.is_file():
        if required:
            raise ValueError(f"missing pinned {name}; run python3 scripts/bootstrap.py {name}")
        return None
    result = subprocess.run([str(path), *config["version_args"]], capture_output=True, text=True)
    if name == "okf":
        try:
            actual_version = json.loads(result.stdout).get("version")
        except ValueError:
            actual_version = None
    else:
        pattern = r"^version:\s*(\S+)" if name == "shellcheck" else rf"^{name}\s+(\S+)"
        match = re.search(pattern, result.stdout, re.M)
        actual_version = match[1] if match else None
    if result.returncode or actual_version != config["version"]:
        raise ValueError(f"{name}: installed version differs from pin")
    return path


def repo_markdown(root=ROOT):
    return sorted([*root.glob("*.md"), *(root / "knowledge").rglob("*.md")])


def python_sources():
    return sorted([*(ROOT / "scripts").glob("*.py"), *(ROOT / "tests").glob("test_*.py")])


def fixture_integrity(root=ROOT):
    base = root / "tests/fixtures/upstream"
    manifest = json.loads((base / "manifest.json").read_text())
    errors = []
    actual = {p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file()}
    if actual != {*manifest["files"], "manifest.json"}:
        errors.append("upstream fixture inventory differs from pinned snapshot")
    for filename, digest in manifest["files"].items():
        path = base / filename
        if not path.is_file() or bundle.sha(path.read_bytes()) != digest:
            errors.append(f"upstream snapshot checksum mismatch: {filename}")
    versions = json.loads((root / "tools/versions.json").read_text())
    if manifest["commit"] != versions["spec"]["commit"]:
        errors.append("golden snapshot and spec commits differ")
    if bundle.sha((base / "SPEC.md").read_bytes()) != versions["spec"]["sha256"]:
        errors.append("pinned SPEC checksum mismatch")
    return errors


def generated(root=ROOT):
    mapping = bundle.load_yaml((root / "migration/mapping.yaml").read_text())
    return {
        **bundle.index_outputs(root / "knowledge", read_config(root)),
        **bundle.landing_outputs(root, mapping),
    }


def guard_repository_inputs():
    # Check directory aliases before traversing, then all prospective inputs.
    directories = [ROOT / name for name in ("knowledge", "scripts", "tests", "tools", "migration")]
    files.check_paths(ROOT, directories)
    files.check_paths(
        ROOT,
        [
            *repo_markdown(),
            *python_sources(),
            *(ROOT / "knowledge").rglob("*"),
            ROOT / "migration/mapping.yaml",
            ROOT / "tools/bundle-policy.toml",
        ],
    )


def index():
    guard_repository_inputs()
    outputs = generated()
    files.check_paths(ROOT, outputs)
    for path, text in outputs.items():
        files.write_text(ROOT, path, text)
        print(path.relative_to(ROOT))


def formatting(write=False):
    guard_repository_inputs()
    generated_paths = set(generated())
    errors = []
    # Never discover snapshot/fixture paths, even with an empty git index.
    for path in repo_markdown():
        original = path.read_text()
        expected = bundle.formatted(original)
        if original != expected:
            if write and path not in generated_paths:
                files.write_text(ROOT, path, expected)
            else:
                errors.append(f"Markdown format differs: {path.relative_to(ROOT)}")
    return errors


def examples():
    errors = []
    manifest = json.loads((ROOT / "tools/examples.json").read_text())
    concepts, parse_errors = bundle.read_concepts(ROOT / "knowledge")
    errors.extend(parse_errors)
    inventory = {
        (cid, i): token
        for cid, concept in concepts.items()
        for i, token in enumerate(t for t in bundle.MD.parse(concept.body) if t.type == "fence")
    }
    seen = set()
    shellcheck = tool("shellcheck")
    for record in manifest["examples"]:
        cid, index = record.get("concept"), record.get("fence")
        if not isinstance(cid, str) or type(index) is not int or index < 0:
            errors.append("invalid example inventory record")
            continue
        key = (cid, index)
        if key not in inventory or key in seen:
            errors.append(f"example inventory unknown/duplicate fence: {key}")
            continue
        seen.add(key)
        token = inventory[key]
        if not record.get("reason"):
            errors.append(f"example classification needs a reason: {key}")
        if bundle.sha(token.content.encode()) != record["sha256"]:
            errors.append(f"example inventory changed: {record['concept']} fence {record['fence']}")
        kind = record["check"]
        if kind == "json":
            json.loads(token.content)
        elif kind == "toml":
            tomllib.loads(token.content)
        elif kind == "yaml":
            bundle.load_yaml(token.content)
        elif kind == "bash-syntax":
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "example.sh"
                path.write_text(token.content)
                result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
                if result.returncode:
                    errors.append(result.stderr)
                result = subprocess.run(
                    [str(shellcheck), "--shell=bash", "--severity=warning", str(path)],
                    capture_output=True,
                    text=True,
                )
                if result.returncode:
                    errors.append(result.stdout + result.stderr)
        elif kind != "illustrative":
            errors.append(f"unknown example check: {kind}")
    for key in sorted(inventory.keys() - seen):
        errors.append(f"unclassified example fence: {key}")
    return errors


def repository_hygiene():
    errors = []
    action_pins = json.loads((ROOT / "tools/action-pins.json").read_text())
    actions_used = set()
    maintained = [
        *repo_markdown(),
        *python_sources(),
        ROOT / "pyproject.toml",
        ROOT / "uv.lock",
        ROOT / ".githooks/pre-commit",
        *(ROOT / "tools").glob("*"),
        *(ROOT / "migration").glob("*.yaml"),
        *(ROOT / "migration").glob("*.json"),
        *(ROOT / ".github/workflows").glob("*.yml"),
    ]
    for path in maintained:
        if not path.is_file():
            continue
        data = path.read_bytes()
        if b"\r" in data or not data.endswith(b"\n"):
            errors.append(f"LF/final-newline hygiene: {path.relative_to(ROOT)}")
        if re.search(rb"^(?:<{7}|={7}|>{7})(?: |$)", data, re.M):
            errors.append(f"merge conflict marker: {path.relative_to(ROOT)}")
        if path.suffix == ".json":
            json.loads(data)
        elif path.suffix == ".toml":
            tomllib.loads(data.decode())
        elif path.suffix in {".yml", ".yaml"}:
            bundle.load_yaml(data.decode())
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        workflow = bundle.load_yaml(path.read_text())
        for job in workflow["jobs"].values():
            for step in job["steps"]:
                if "uses" in step and not re.fullmatch(r"[\w./-]+@[a-f0-9]{40}", step["uses"]):
                    errors.append(f"workflow action must have an immutable SHA: {path}")
                elif "uses" in step:
                    name, revision = step["uses"].rsplit("@", 1)
                    actions_used.add(name)
                    if action_pins.get(name) != revision:
                        errors.append(
                            f"workflow action differs from registered pin: {path}: {name}"
                        )
    if actions_used != set(action_pins):
        errors.append("action pin registry has missing or unused actions")
    return errors


def compatibility_contract():
    report = json.loads((ROOT / "tools/okf-qualification.json").read_text())
    exceptions = json.loads((ROOT / "tools/compatibility-exceptions.json").read_text())
    expected = {
        (case, finding["rule"], finding["concept"], report["tool_version"])
        for case, result in report["cases"].items()
        for finding in result["findings"]
    }
    actual, errors = set(), []
    for entry in exceptions["entries"]:
        if (
            not isinstance(entry, dict)
            or not all(
                isinstance(entry.get(k), str) and entry[k]
                for k in ("fixture", "rule", "tool_version", "owner", "reason")
            )
            or not isinstance(entry.get("concepts"), list)
            or not entry["concepts"]
            or any(not isinstance(cid, str) or not cid for cid in entry["concepts"])
        ):
            errors.append("compatibility exception has missing scope/owner/reason")
            continue
        try:
            bundle.timestamp(entry.get("expires"))
        except ValueError as exc:
            errors.append(f"invalid compatibility exception expiration: {exc}")
        for cid in entry["concepts"]:
            key = (entry["fixture"], entry["rule"], cid, entry["tool_version"])
            if key in actual:
                errors.append(f"duplicate compatibility exception: {key}")
            actual.add(key)
    if actual != expected:
        errors.append("compatibility exceptions differ from exact qualification findings")
    return errors


def health_exceptions():
    entries = json.loads((ROOT / "tools/health-exceptions.json").read_text())["entries"]
    for entry in entries:
        if entry.get("rule") not in {
            "external-url",
            "review-overdue",
            "stale-verification",
            "narrative-orphan",
        }:
            raise ValueError("unknown health exception rule")
        if not all(
            isinstance(entry.get(k), str) and entry[k] for k in ("match", "owner", "reason")
        ):
            raise ValueError("health exceptions need match, owner and reason")
        bundle.timestamp(entry["expires"])
    return entries


def check(run_tests=True):
    errors = formatting()
    tool("uv")
    execute([sys.executable, "-m", "ruff", "check", *python_sources()])
    execute([sys.executable, "-m", "ruff", "format", "--check", *python_sources()])
    execute([sys.executable, "-m", "codespell_lib", *repo_markdown()])
    errors.extend(bundle.validate(ROOT / "knowledge", read_config()))
    mapping = bundle.load_yaml((ROOT / "migration/mapping.yaml").read_text())
    errors.extend(bundle.migration_check(ROOT, mapping))
    errors.extend(fixture_integrity())
    errors.extend(bundle.check_links(ROOT, sorted(ROOT.glob("*.md"))))
    # Raw comparison after format checks; the generator is the only writer.
    with tempfile.TemporaryDirectory() as tmp:
        for path, expected in generated().items():
            temporary = Path(tmp) / path.relative_to(ROOT)
            temporary.parent.mkdir(parents=True, exist_ok=True)
            temporary.write_text(expected)
            if not path.is_file() or path.read_bytes() != temporary.read_bytes():
                errors.append(f"generated drift: {path.relative_to(ROOT)}")
    errors.extend(examples())
    errors.extend(repository_hygiene())
    errors.extend(compatibility_contract())
    health_exceptions()  # Validate syntax, not elapsed wall-clock time.
    if errors:
        raise ValueError("\n".join(errors))
    if run_tests:
        execute([sys.executable, "-m", "pytest"])
    print("Completion gate passed (offline, no source edits).")


def qualification():
    binary = tool("okf")
    config = json.loads((ROOT / "tools/versions.json").read_text())
    cases = {}
    for path in sorted((ROOT / "tests/fixtures/upstream/bundles").iterdir()):
        if path.is_dir():
            cases["upstream/" + path.name] = path
    for path in sorted((ROOT / "tests/fixtures/qualification").iterdir()):
        if path.is_dir():
            cases["minimal/" + path.name] = path
    previous = json.loads((ROOT / "tools/okf-qualification.json").read_text())
    if (
        previous["tool_version"] != config["tools"]["okf"]["version"]
        or previous["upstream_commit"] != config["spec"]["commit"]
    ):
        raise ValueError("tool/spec pin changed; requalify before accepting new expectations")
    expected = previous.get("cases", {})
    actual = {}
    for name, path in cases.items():
        result = subprocess.run(
            [str(binary), "validate", str(path)], capture_output=True, text=True
        )
        if result.returncode not in (0, 1):
            raise ValueError(f"OKF CLI execution failure on {name}: {result.stderr}")
        report = json.loads(result.stdout)
        if "findings" not in report:
            raise ValueError(f"OKF CLI failed to load {name}: {report}")
        signatures = collections.Counter(
            (f.get("concept_id", ""), f["rule"], f["severity"]) for f in report["findings"]
        )
        actual[name] = {
            "exit_code": result.returncode,
            "findings": [
                {"concept": cid, "rule": rule, "severity": severity, "count": count}
                for (cid, rule, severity), count in sorted(signatures.items())
            ],
        }
        if actual[name] != expected.get(name):
            raise ValueError(f"unexpected OKF findings for {name}; inspect before updating the pin")
    if set(actual) != set(expected):
        raise ValueError("qualification fixture inventory changed")
    errors = compatibility_contract()
    if errors:
        raise ValueError("\n".join(errors))
    print(f"Qualified advisory OKF CLI against {len(actual)} pinned cases.")
    return previous


def rights_gate(root):
    rights = bundle.load_yaml((root / "migration/rights-review.yaml").read_text())
    if (
        rights.get("status") != "cleared"
        or not rights.get("license")
        or not rights.get("maintainer_approval")
        or not rights.get("sources")
        or any(s.get("status") != "cleared" for s in rights["sources"])
    ):
        raise ValueError(
            "Distribution blocked: rights-review.yaml is unresolved; maintainer license/rights clearance required."
        )
    policy = read_config(root)
    approval = rights["maintainer_approval"]
    if (
        not isinstance(approval.get("by"), str)
        or not approval["by"].startswith("human:")
        or approval["by"] not in policy["maintainers"]
    ):
        raise ValueError(
            "Distribution blocked: approval must identify a configured human maintainer."
        )
    bundle.timestamp(approval.get("at"))
    notices = rights.get("archive_notices", [])
    required = {"LICENSE.txt"}
    scopes = []
    for source in rights["sources"]:
        if not source.get("scope") or not source.get("evidence"):
            raise ValueError("Distribution blocked: each source needs scope and rights evidence.")
        if not isinstance(source.get("required_notices"), list):
            raise ValueError("Distribution blocked: each source must declare required_notices.")
        required.update(source["required_notices"])
        scopes.extend(source["scope"])
    if not required.issubset({n.get("archive_path") for n in notices}):
        raise ValueError("Distribution blocked: missing required approved license/notice.")
    for path in (root / "knowledge").rglob("*"):
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            if not any(fnmatch.fnmatchcase(relative, scope) for scope in scopes):
                raise ValueError(
                    f"Distribution blocked: content lacks cleared rights scope: {relative}"
                )
    result = {}
    for item in notices:
        archive_path = item["archive_path"]
        source = root / item["source"]
        if archive_path not in {"LICENSE.txt", "NOTICE.txt"} or not source.resolve().is_relative_to(
            root.resolve()
        ):
            raise ValueError("invalid archive notice path")
        if archive_path in result:
            raise ValueError("duplicate approved archive notice")
        files.check_paths(root, [source])
        data = source.read_bytes()
        if bundle.sha(data) != item["sha256"]:
            raise ValueError("approved notice checksum changed")
        result[archive_path] = data
    return result


def build_archive(root, destination):
    # Rights gate runs before creating a directory or opening any archive.
    notices = rights_gate(root)
    errors = bundle.validate(root / "knowledge", read_config(root))
    if errors:
        raise ValueError("\n".join(errors))
    members = {}
    assets = set(read_config(root).get("archive_assets", []))
    for path in (root / "knowledge").rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root / "knowledge").as_posix()
        if path.suffix != ".md" and relative not in assets:
            raise ValueError(f"unlisted non-Markdown archive asset: {relative}")
        members[relative] = path.read_bytes()
    members.update(notices)
    missing_assets = assets - members.keys()
    if missing_assets:
        raise ValueError(f"declared archive assets are missing: {sorted(missing_assets)}")
    with tempfile.TemporaryDirectory() as tmp:
        temporary = Path(tmp) / "bundle.zip"
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(members.items()):
                entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                entry.external_attr = 0o100644 << 16
                entry.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(entry, data)
        extracted = Path(tmp) / "extracted"
        with zipfile.ZipFile(temporary) as archive:
            if set(archive.namelist()) != set(members):
                raise ValueError("archive inventory differs from allow-list")
            for info in archive.infolist():
                if Path(info.filename).is_absolute() or ".." in Path(info.filename).parts:
                    raise ValueError("unsafe archive member")
                if (info.external_attr >> 16) & 0o170000 != 0o100000:
                    raise ValueError("archive member is not a regular file")
            archive.extractall(extracted)
        errors = bundle.validate(extracted, read_config(root))
        if errors:
            raise ValueError("extracted archive invalid: " + "; ".join(errors))
        files.check_paths(root, [destination])
        destination.parent.mkdir(parents=True, exist_ok=True)
        files.write_bytes(root, destination, temporary.read_bytes())
    return {
        "archive_sha256": bundle.sha(destination.read_bytes()),
        "members": sorted(members),
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "working_tree_dirty": bool(
            subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
        ),
    }


def health(offline=False):
    now = datetime.now(UTC)
    findings = []
    checks = []
    active_exceptions = []
    for entry in health_exceptions():
        if now >= bundle.timestamp(entry["expires"]):
            findings.append({"rule": "exception-expired", "exception": entry})
        else:
            active_exceptions.append(entry)
    concepts, errors = bundle.read_concepts(ROOT / "knowledge")
    findings.extend({"rule": "parse", "message": e} for e in errors)
    for error in bundle.validate(ROOT / "knowledge", read_config()):
        findings.append({"rule": "bundle-validation", "message": error})
    for cid in read_config()["freshness"]:
        concept = concepts.get(cid)
        if concept is None:
            findings.append({"rule": "freshness-scope", "concept": cid})
            continue
        try:
            if now >= bundle.timestamp(concept.meta.get("stale_after")):
                findings.append(
                    {"rule": "review-overdue", "concept": cid, "owner": concept.meta.get("owner")}
                )
            events = concept.meta.get("verified", [])
            if isinstance(events, dict):
                events = [events]
            for event in events:
                if bundle.timestamp(event["at"]) < bundle.timestamp(
                    concept.meta["generated"]["at"]
                ):
                    findings.append(
                        {"rule": "stale-verification", "concept": cid, "by": event["by"]}
                    )
        except (ValueError, TypeError, KeyError) as exc:
            findings.append({"rule": "review-metadata", "concept": cid, "message": str(exc)})
    exceptions = json.loads((ROOT / "tools/compatibility-exceptions.json").read_text())
    for entry in exceptions["entries"]:
        if now >= bundle.timestamp(entry["expires"]):
            findings.append({"rule": "exception-expired", "exception": entry})
    # Narrative graph ignores directory indexes and generated source citations.
    incoming = collections.Counter()
    for concept in concepts.values():
        for target in bundle.links(concept.body):
            try:
                path, _ = bundle.resolve_local(ROOT / "knowledge", concept.path, target)
                if path and path.suffix == ".md":
                    incoming[path.relative_to(ROOT / "knowledge").with_suffix("").as_posix()] += 1
            except ValueError as exc:
                findings.append({"rule": "local-link", "message": str(exc)})
    for cid in concepts:
        if not incoming[cid] and cid != "selection":
            findings.append({"rule": "narrative-orphan", "concept": cid})
    if not offline:
        versions = json.loads((ROOT / "tools/versions.json").read_text())
        try:
            url = (
                "https://raw.githubusercontent.com/"
                + versions["spec"]["repository"]
                + "/main/SPEC.md"
            )
            with urllib.request.urlopen(url, timeout=30) as response:
                digest = bundle.sha(response.read())
            if digest != versions["spec"]["sha256"]:
                findings.append({"rule": "upstream-spec-changed", "sha256": digest})
        except Exception as exc:
            findings.append({"rule": "upstream-unavailable", "message": str(exc)})
        try:
            binary = tool("lychee", required=False)
        except (ValueError, OSError) as exc:
            binary = None
            findings.append({"rule": "external-tool", "message": str(exc)})
        if binary:
            args = [
                str(binary),
                "--no-progress",
                "--max-retries",
                "2",
                "--timeout",
                "20",
                "--format",
                "json",
                "--scheme",
                "http",
                "--scheme",
                "https",
                *[
                    arg
                    for entry in active_exceptions
                    if entry["rule"] == "external-url"
                    for arg in ("--exclude", "^" + re.escape(entry["match"]) + "$")
                ],
                "--",
                *map(str, repo_markdown()),
            ]
            result = subprocess.run(args, capture_output=True, text=True)
            external = {
                "rule": "external-links",
                "exit_code": result.returncode,
                "report": json.loads(result.stdout)
                if result.stdout.strip().startswith("{")
                else result.stdout,
                "diagnostics": result.stderr,
            }
            checks.append(external)
            if result.returncode:
                findings.append(external)
        else:
            findings.append({"rule": "external-links-skipped", "reason": "bootstrap lychee"})
    try:
        qualified = qualification()
        checks.append(
            {"rule": "advisory-okf", "cases": len(qualified["cases"]), "status": "qualified"}
        )
    except (ValueError, OSError) as exc:
        findings.append({"rule": "advisory-okf", "message": str(exc)})
    for finding in findings:
        for entry in active_exceptions:
            if finding["rule"] == entry["rule"] and finding.get("concept") == entry["match"]:
                finding.update(suppressed=True, exception=entry)
    for entry in active_exceptions:
        if entry["rule"] == "external-url":
            findings.append({"rule": "external-url-exception", "exception": entry})
    report = {"at": now.isoformat(), "offline": offline, "findings": findings, "checks": checks}
    output = ROOT / "reports/health.json"
    files.check_paths(ROOT, [output])
    output.parent.mkdir(exist_ok=True)
    files.write_text(ROOT, output, json.dumps(report, indent=2) + "\n")
    print(f"Health report: {output.relative_to(ROOT)} ({len(findings)} advisory findings)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
    commands.add_parser("index")
    commands.add_parser("fmt")
    commands.add_parser("package")
    commands.add_parser("qualify")
    health_parser = commands.add_parser("health")
    health_parser.add_argument("--offline", action="store_true")
    validate_parser = commands.add_parser("validate")
    validate_parser.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "check":
            check()
        elif args.command == "index":
            index()
        elif args.command == "fmt":
            errors = formatting(write=True)
            execute([sys.executable, "-m", "ruff", "format", *python_sources()])
            if errors:
                raise ValueError("\n".join(errors) + "\nRegenerate generated files with index.")
        elif args.command == "validate":
            errors = bundle.validate(args.root, read_config())
            if errors:
                raise ValueError("\n".join(errors))
        elif args.command == "health":
            health(args.offline)
        elif args.command == "qualify":
            qualification()
        elif args.command == "package":
            check()
            provenance = ROOT / "dist/provenance.json"
            files.check_paths(ROOT, [provenance])
            receipt = build_archive(ROOT, ROOT / "dist/project-blueprints.zip")
            files.write_text(ROOT, provenance, json.dumps(receipt, indent=2) + "\n")
            print("Validated archive: dist/project-blueprints.zip")
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
