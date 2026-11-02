"""OKF parsing, local policy, deterministic navigation and migration accounting.

The input root is always explicit. No network, clock or source writes occur
during validation. Optional OKF fields are not local requirements in spec mode.
"""

from __future__ import annotations

import base64
import copy
import difflib
import hashlib
import html
import json
import re
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from itertools import accumulate
from pathlib import Path
from urllib.parse import unquote, urlsplit

import bleach
import mdformat
import yaml
from github_slugger import GithubSlugger
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin

REPO = Path(__file__).resolve().parents[1]
MD = MarkdownIt("commonmark", {"html": True}).enable("table").use(footnote_plugin)
FORMAT_EXTENSIONS = {"gfm", "front_matters", "footnote"}
RESERVED = {"index.md", "log.md"}
SOURCE_COMMIT = "b90867e82cd2a06ec3a01bea8d86d4f9a2882048"
# Deliberately independent of editable mapping hashes. Rebaselining requires
# an explicit validator change; approved future content diffs are excluded.
BASELINE_SHA256 = "dd8cd1b8ced2ab898406cbde799a7191c6d5ed8035cfe4167e2e6d54a2a7fe1e"
ACTOR = re.compile(r"^(human:[\w.-]+|process:[\w.-]+|[\w.-]+/[^\s/]+)$")


class Loader(yaml.SafeLoader):
    """Keep timestamps as strings and reject ambiguous duplicate YAML keys."""


Loader.yaml_implicit_resolvers = copy.deepcopy(Loader.yaml_implicit_resolvers)
for key, values in Loader.yaml_implicit_resolvers.items():
    Loader.yaml_implicit_resolvers[key] = [
        (tag, regex)
        for tag, regex in values
        if tag not in {"tag:yaml.org,2002:timestamp", "tag:yaml.org,2002:bool"}
    ]
Loader.add_implicit_resolver(
    "tag:yaml.org,2002:bool", re.compile(r"^(?:true|false)$", re.I), list("tTfF")
)


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise ValueError(f"duplicate or non-string YAML key: {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def load_yaml(text):
    return yaml.load(text, Loader=Loader)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_proof_check(repo, mapping):
    errors = []
    baseline = copy.deepcopy(mapping)
    for record in baseline.get("concepts", {}).values():
        record.pop("approved_change", None)
    encoded = json.dumps(
        baseline, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    if sha(encoded) != BASELINE_SHA256:
        errors.append("migration baseline differs from the independently pinned conversion record")
    if mapping.get("source_commit") != SOURCE_COMMIT:
        errors.append("source_commit differs from the pinned original revision")
    try:
        proof = json.loads((repo / "migration/source-proof.json").read_text())
        commit = base64.b64decode(proof["commit"], validate=True)
        tree = base64.b64decode(proof["tree"], validate=True)

        def object_id(kind, data):
            return hashlib.sha1(f"{kind} {len(data)}\0".encode() + data).hexdigest()

        if object_id("commit", commit) != SOURCE_COMMIT:
            raise ValueError("commit object does not match pinned source_commit")
        if commit.splitlines()[0] != b"tree " + object_id("tree", tree).encode():
            raise ValueError("root tree object does not match the pinned commit")
        entries = {}
        while tree:
            header, rest = tree.split(b"\0", 1)
            mode, filename = header.split(b" ", 1)
            entries[filename.decode()] = (mode, rest[:20].hex())
            tree = rest[20:]
        for filename in mapping["sources"]:
            data = (repo / "migration/sources" / filename).read_bytes()
            if entries.get(filename) != (b"100644", object_id("blob", data)):
                errors.append(f"{filename}: original snapshot does not match the pinned Git tree")
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        errors.append(f"source Git proof: {exc}")
    return errors


def formatted(text: str) -> str:
    return mdformat.text(text, extensions=FORMAT_EXTENSIONS)


def frontmatter(text: str):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing YAML frontmatter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError("unterminated YAML frontmatter")
    data = load_yaml("".join(lines[1:end]))
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data, "".join(lines[end + 1 :]).lstrip("\n")


def timestamp(value):
    if not isinstance(value, str) or "T" not in value:
        raise ValueError("expected an ISO 8601 datetime with timezone")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("datetime has no timezone")
    return parsed


def inline_text(token):
    return "".join(
        c.content for c in token.children or [] if c.type in {"text", "code_inline", "image"}
    )


def headings(text):
    tokens = MD.parse(text)
    slugger = GithubSlugger()
    result = []
    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            title = inline_text(tokens[i + 1])
            result.append(
                {
                    "title": tokens[i + 1].content,
                    "slug": slugger.slug(title),
                    "level": int(token.tag[1:]),
                    "line": token.map[0],
                }
            )
    return result


class RenderedTargets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = set()
        self.slugger = GithubSlugger()
        self.heading = None
        self.words = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and "name" in attrs:
            self.targets.add(attrs["name"])
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading, self.words = tag, []
        if self.heading and tag == "img":
            self.words.append(attrs.get("alt", ""))

    def handle_data(self, data):
        if self.heading:
            self.words.append(data)

    def handle_endtag(self, tag):
        if tag == self.heading:
            self.targets.add(self.slugger.slug("".join(self.words)))
            self.heading = None


def rendered_anchors(text):
    """Sanitize author HTML before deriving GitHub-style heading slugs.

    This is a pinned local compatibility model, not a claim that GitHub's
    private production pipeline is identical. Legacy pages retain headings.
    """
    markup = bleach.clean(
        MD.render(text),
        tags={
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "a",
            "p",
            "em",
            "strong",
            "code",
            "pre",
            "ul",
            "ol",
            "li",
            "table",
            "thead",
            "tbody",
            "tr",
            "th",
            "td",
            "img",
        },
        attributes={"a": ["name", "href"], "img": ["src", "alt"]},
        strip=True,
    )
    parser = RenderedTargets()
    parser.feed(markup)
    return parser.targets


def links(text):
    for token in MD.parse(text):
        for child in token.children or []:
            if child.type in {"link_open", "image"}:
                yield child.attrGet("href" if child.type == "link_open" else "src")
            elif child.type == "html_inline":
                # Markdown-native links are preferred; also cover author HTML.
                for match in re.finditer(r"(?:href|src)=[\"\']([^\"\']+)", child.content):
                    yield html.unescape(match[1])
        if token.type == "html_block":
            for match in re.finditer(r"(?:href|src)=[\"\']([^\"\']+)", token.content):
                yield html.unescape(match[1])


@dataclass
class Concept:
    path: Path
    id: str
    meta: dict
    body: str


def read_concepts(root):
    result, errors = {}, []
    for path in sorted(root.rglob("*.md")):
        if path.name in RESERVED:
            continue
        try:
            meta, body = frontmatter(path.read_text(encoding="utf-8"))
            cid = path.relative_to(root).with_suffix("").as_posix()
            result[cid] = Concept(path, cid, meta, body)
        except (ValueError, yaml.YAMLError, UnicodeError, OSError) as exc:
            errors.append(f"{path}: {exc}")
    return result, errors


def resolve_local(root, origin, target):
    if not isinstance(target, str) or not target.strip():
        raise ValueError("resource/link must be a non-empty string")
    parts = urlsplit(target)
    if parts.scheme or parts.netloc:
        if parts.scheme not in {"https", "http", "mailto"} or parts.netloc and not parts.scheme:
            raise ValueError(f"unsupported URL: {target}")
        return None, None
    decoded = unquote(parts.path)
    if "\\" in decoded:
        raise ValueError(f"non-portable local path: {target}")
    path = root / decoded.lstrip("/") if decoded.startswith("/") else origin.parent / decoded
    path = path if decoded else origin
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"path escapes root: {target}")
    path = resolved
    if path.is_dir():
        path = path / "index.md"
    if not path.is_file():
        raise ValueError(f"missing target: {target}")
    return path, unquote(parts.fragment)


def check_target(root, origin, target, anchor_cache=None):
    path, fragment = resolve_local(root, origin, target)
    if path and fragment:
        if path.suffix != ".md":
            raise ValueError(f"fragment on unsupported local format: {target}")
        cache = {} if anchor_cache is None else anchor_cache
        if path not in cache:
            text = path.read_text(encoding="utf-8")
            if text.startswith("---\n"):
                _, text = frontmatter(text)
            cache[path] = rendered_anchors(text)
        if fragment not in cache[path]:
            raise ValueError(f"missing fragment: {target}")
    return path, fragment


def check_links(root, paths):
    errors, cache = [], {}
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            continue
        for target in links(text):
            try:
                check_target(root, path, target, cache)
            except (ValueError, OSError, UnicodeError) as exc:
                errors.append(f"{path.relative_to(root)}: {exc}")
    return errors


def citation_errors(body, source_ids):
    env = {}
    tokens = MD.parse(body, env)
    definitions = {label.removeprefix(":") for label in env.get("footnotes", {}).get("refs", {})}
    used, unresolved = set(), set()
    for token in tokens:
        for child in token.children or []:
            if child.type == "footnote_ref":
                used.add(child.meta["label"])
            elif child.type == "text":
                unresolved.update(re.findall(r"\[\^([^\]\n]+)\]", child.content))
    errors = [f"unresolved footnote: {label}" for label in sorted(unresolved)]
    for label in sorted(source_ids - (definitions & used)):
        errors.append(f"source ID must have a definition and citation: {label}")
    for label in sorted((definitions | used) - source_ids):
        if not label.startswith("note-"):
            errors.append(f"footnote has no matching source ID (prose notes use note-): {label}")
    return errors


def source_is_scope(resource):
    # Multi-word descriptions are OKF scopes, not extension heuristics. For
    # ambiguous one-word scopes use the explicit scope: convention locally.
    return resource.startswith("scope:") or (
        any(c.isspace() for c in resource) and "/" not in resource
    )


def validate(root, policy=None):
    root = Path(root).absolute()
    errors = []
    if not root.is_dir() or root.is_symlink():
        return [f"bundle root is not a real directory: {root}"]
    names = set()
    for path in sorted(root.rglob("*")):
        name = path.relative_to(root).as_posix()
        if path.is_symlink():
            errors.append(f"symlink forbidden: {name}")
        if name.casefold() in names:
            errors.append(f"case-conflicting path: {name}")
        names.add(name.casefold())
    if errors:
        return errors
    concepts, parse_errors = read_concepts(root)
    errors.extend(parse_errors)
    for path in sorted(root.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
            if path.name == "index.md":
                if text.startswith("---\n"):
                    meta, _ = frontmatter(text)
                    if path.parent != root or set(meta) != {"okf_version"}:
                        errors.append(f"{path}: invalid reserved index frontmatter")
                    elif str(meta["okf_version"]) != "0.2":
                        errors.append(f"{path}: unsupported OKF version")
                if policy and path == root / "index.md":
                    if (
                        not text.startswith("---\n")
                        or frontmatter(text)[0].get("okf_version") != "0.2"
                    ):
                        errors.append("root index must explicitly declare OKF version 0.2")
            if path.name == "log.md":
                if text.startswith("---\n"):
                    errors.append(f"{path}: log must not have frontmatter")
                for h in headings(text):
                    if h["level"] == 2:
                        try:
                            datetime.strptime(h["title"], "%Y-%m-%d")
                        except ValueError:
                            errors.append(f"{path}: log date heading must be YYYY-MM-DD")
        except (ValueError, UnicodeError, yaml.YAMLError, OSError) as exc:
            errors.append(f"{path}: {exc}")
    for cid, concept in concepts.items():
        meta = concept.meta
        prefix = f"{cid}: "
        if not isinstance(meta.get("type"), str) or not meta["type"].strip():
            errors.append(prefix + "type must be a non-empty string (OKF)")
        if policy:
            for field in ("title", "description", "owner"):
                if not isinstance(meta.get(field), str) or not meta[field].strip():
                    errors.append(prefix + f"missing local field {field}")
            if meta.get("type") not in policy["types"]:
                errors.append(prefix + "unknown local concept type")
            if not isinstance(meta.get("status"), str) or meta["status"] not in {
                "draft",
                "stable",
                "deprecated",
            }:
                errors.append(prefix + "invalid local status")
            tags = meta.get("tags")
            if (
                not isinstance(tags, list)
                or not tags
                or any(not isinstance(t, str) or t not in policy["tags"] for t in tags)
            ):
                errors.append(prefix + "tags must use the configured vocabulary")
            if not isinstance(meta.get("generated"), dict):
                errors.append(prefix + "generated.by/at required locally")
            selected = cid in policy["freshness"]
            if selected != ("stale_after" in meta):
                errors.append(prefix + "stale_after must match explicit freshness scope")
        for family in ("generated", "verified"):
            events = meta.get(family, [])
            if isinstance(events, dict):
                events = [events]
            if not isinstance(events, list):
                errors.append(prefix + f"invalid {family} shape")
                continue
            for event in events:
                try:
                    if not isinstance(event, dict) or not ACTOR.fullmatch(event.get("by", "")):
                        raise ValueError("invalid actor")
                    timestamp(event.get("at"))
                    if policy and family == "verified" and event["by"].startswith("human:"):
                        if event["by"] not in policy["maintainers"]:
                            raise ValueError("human verifier is not a configured maintainer")
                except (ValueError, TypeError) as exc:
                    errors.append(prefix + f"{family}: {exc}")
        if "stale_after" in meta:
            try:
                timestamp(meta["stale_after"])
            except (ValueError, TypeError) as exc:
                errors.append(prefix + f"stale_after: {exc}")
        sources = meta.get("sources", [])
        if not isinstance(sources, list):
            errors.append(prefix + "sources must be a list")
            sources = []
        source_ids = set()
        for source in sources:
            if (
                not isinstance(source, dict)
                or not isinstance(source.get("id"), str)
                or not source["id"]
                or not isinstance(source.get("resource"), str)
                or not source["resource"]
            ):
                errors.append(prefix + "source needs id and resource")
                continue
            if source["id"] in source_ids:
                errors.append(prefix + "duplicate source ID")
            source_ids.add(source["id"])
            resource = source["resource"]
            if not source_is_scope(resource):
                try:
                    check_target(root, concept.path, resource)
                except ValueError as exc:
                    errors.append(prefix + str(exc))
        if policy:
            errors.extend(prefix + error for error in citation_errors(concept.body, source_ids))
        for key in ("resource", "computation"):
            if key in meta:
                try:
                    check_target(root, concept.path, meta[key])
                except (ValueError, TypeError) as exc:
                    errors.append(prefix + f"{key}: {exc}")
        for family in ("executor", "attester"):
            if family in meta and isinstance(meta[family], dict) and "resource" in meta[family]:
                try:
                    check_target(root, concept.path, meta[family]["resource"])
                except (ValueError, TypeError) as exc:
                    errors.append(prefix + f"{family}: {exc}")
        if meta.get("type") == "Attested Computation" and not meta.get("runtime"):
            errors.append(prefix + "Attested Computation needs runtime")
        requires = meta.get("x-requires", [])
        if not isinstance(requires, list) or any(not isinstance(x, str) for x in requires):
            errors.append(prefix + "x-requires must be a list of concept IDs")
        else:
            for target in requires:
                if target not in concepts:
                    errors.append(prefix + f"missing prerequisite {target}")
    visiting, visited = set(), set()

    def visit(cid):
        if cid in visiting:
            errors.append(f"prerequisite cycle at {cid}")
            return
        if cid in visited:
            return
        visiting.add(cid)
        requires = concepts[cid].meta.get("x-requires", [])
        for target in requires if isinstance(requires, list) else []:
            if isinstance(target, str) and target in concepts:
                visit(target)
        visiting.remove(cid)
        visited.add(cid)

    for cid in concepts:
        visit(cid)
    if policy:
        for cid, review_class in policy["freshness"].items():
            if cid not in concepts or review_class not in {"tool-behavior", "policy"}:
                errors.append(f"unknown freshness selection/class: {cid}")
        for cid, required in policy.get("profile_requires", {}).items():
            if cid not in concepts or concepts[cid].meta.get("x-requires", []) != required:
                errors.append(f"profile prerequisite mismatch: {cid}")
        if not (root / "index.md").is_file():
            errors.append("missing root index")
    errors.extend(check_links(root, sorted(root.rglob("*.md"))))
    return errors


def index_outputs(root, policy):
    concepts, errors = read_concepts(root)
    if errors:
        raise ValueError("; ".join(errors))
    for concept in concepts.values():
        for field in ("title", "description"):
            if not isinstance(concept.meta.get(field), str) or not concept.meta[field].strip():
                raise ValueError(f"{concept.id}: index requires a non-empty {field}")
    output = {}
    directories = {root, *(c.path.parent for c in concepts.values())}
    for directory in sorted(directories):
        relative = directory.relative_to(root).as_posix()
        title = policy["directories"].get(relative, relative)
        prefix = '---\nokf_version: "0.2"\n---\n\n' if directory == root else ""
        text = prefix + f"# {title}\n\n"
        for child in sorted(directories):
            if child != directory and child.parent == directory:
                name = child.relative_to(root).as_posix()
                label = policy["directories"].get(name, name)
                text += f"- [{label}]({child.name}/index.md) - {label} concepts.\n"
        for concept in sorted(concepts.values(), key=lambda c: c.path.name):
            if concept.path.parent == directory:
                text += (
                    f"- [{concept.meta['title']}]({concept.path.name}) - "
                    f"{concept.meta['description']}\n"
                )
        output[directory / "index.md"] = formatted(text)
    return output


def landing_outputs(root, mapping):
    output = {}
    for filename, source in mapping["sources"].items():
        if filename == "README.md":
            continue
        text = "<!-- Generated from migration/mapping.yaml; edit the canonical concepts. -->\n\n"
        text += "This blueprint is now part of the [OKF bundle](knowledge/index.md).\n\n"
        for heading in source["headings"]:
            text += "#" * heading["level"] + " " + heading["title"] + "\n\n"
            unit = next(u for u in source["units"] if u["start"] <= heading["line"] < u["end"])
            cid = unit["concept"]
            target = f"knowledge/{cid}.md#{heading['destination_slug']}"
            text += f"See the [canonical guidance]({target}).\n\n"
        output[root / filename] = formatted(text)
    return output


def rewrite_source_links(raw, filename, cid, mapping):
    """Relocate source links while preserving block and inline code verbatim."""
    import os

    lookup = {}
    profiles = {
        "README.md": "selection",
        "harness-agnostic-project.md": "profiles/harness-agnostic",
        "python-project.md": "profiles/python",
        "python-project-community.md": "profiles/python-community",
    }
    for fn, source in mapping["sources"].items():
        lookup[(fn, "")] = (profiles[fn], "")
        for heading in source["headings"]:
            unit = next(u for u in source["units"] if u["start"] <= heading["line"] < u["end"])
            lookup[(fn, heading["slug"])] = (unit["concept"], heading["destination_slug"])

    def replace(match):
        name, _, fragment = match[2].partition("#")
        target = lookup.get((name or filename, fragment))
        if target is None:
            return match[0]
        dest, slug = target
        relative = os.path.relpath(dest + ".md", str(Path(cid).parent))
        return match[1] + relative + ("#" + slug if slug else "") + match[3]

    def rewrite_prose(text):
        output, cursor = [], 0
        # CommonMark code spans use matching backtick runs, can span lines,
        # and do not interpret escapes inside the span.
        for opening in re.finditer(r"`+", text):
            prefix = text[: opening.start()]
            if opening.start() < cursor or (len(prefix) - len(prefix.rstrip("\\"))) % 2:
                continue
            closing = re.search(
                r"(?<!`)`{" + str(len(opening[0])) + r"}(?!`)", text[opening.end() :]
            )
            if closing is None:
                continue
            end = opening.end() + closing.end()
            output.append(re.sub(r"(\]\()([^\s)]+)(\))", replace, text[cursor : opening.start()]))
            output.append(text[opening.start() : end])
            cursor = end
        output.append(re.sub(r"(\]\()([^\s)]+)(\))", replace, text[cursor:]))
        return "".join(output)

    offsets = list(accumulate(map(len, raw.splitlines(keepends=True)), initial=0))
    output, cursor = [], 0
    for token in MD.parse(raw):
        if token.type in {"fence", "code_block"} and token.map:
            start, end = (offsets[line] for line in token.map)
            output.extend((rewrite_prose(raw[cursor:start]), raw[start:end]))
            cursor = end
    output.append(rewrite_prose(raw[cursor:]))
    return "".join(output)


def migration_check(repo, mapping):
    errors, units = source_proof_check(repo, mapping), {}
    for filename, source in mapping["sources"].items():
        data = (repo / "migration/sources" / filename).read_bytes()
        if sha(data) != source["sha256"]:
            errors.append(f"immutable source changed: {filename}")
            continue
        lines = data.decode().splitlines(keepends=True)
        cursor = 0
        for unit in source["units"]:
            if unit["start"] != cursor or unit["end"] <= cursor:
                errors.append(f"source gap, overlap or empty unit: {unit['id']}")
            cursor = unit["end"]
            raw = "".join(lines[unit["start"] : unit["end"]])
            if sha(raw.encode()) != unit["sha256"]:
                errors.append(f"source section hash mismatch: {unit['id']}")
            expected_blocks = []
            for token in MD.parse(raw):
                if token.level == 0 and token.map:
                    start, end = (unit["start"] + offset for offset in token.map)
                    expected_blocks.append(
                        {
                            "type": token.type,
                            "start": start,
                            "end": end,
                            "sha256": sha("".join(lines[start:end]).encode()),
                        }
                    )
            if unit["blocks"] != expected_blocks:
                errors.append(f"source block inventory/coverage mismatch: {unit['id']}")
            if unit["id"] in units or unit["owner"] != unit["concept"]:
                errors.append(f"duplicate unit or ambiguous policy owner: {unit['id']}")
            units[unit["id"]] = (filename, unit, raw)
        if cursor != len(lines):
            errors.append(f"unaccounted source tail: {filename}")
        reconstructed = "".join(units[u["id"]][2] for u in source["units"])
        if reconstructed.encode() != data:
            errors.append(f"source reconstruction failed: {filename}")
        snapshot_headings = headings(data.decode())
        if snapshot_headings != [
            {key: h[key] for key in ("title", "slug", "level", "line")} for h in source["headings"]
        ]:
            errors.append(f"unaccounted heading: {filename}")
    concepts, parse_errors = read_concepts(repo / "knowledge")
    errors.extend(parse_errors)
    if set(concepts) != set(mapping["concepts"]):
        errors.append("concept inventory differs from migration map")
    consumed = []
    for cid, record in mapping["concepts"].items():
        if cid not in concepts:
            continue
        items = []
        for uid in record["units"]:
            if uid not in units:
                errors.append(f"missing mapped source unit: {uid}")
                continue
            filename, unit, raw = units[uid]
            if unit["concept"] != cid:
                errors.append(f"unit has multiple destination owners: {uid}")
            consumed.append(uid)
            items.append(rewrite_source_links(raw, filename, cid, mapping))
        assembled = "\n".join(items)
        if assembled.startswith("# "):
            first, rest = assembled.split("\n", 1)
            expected = first + "\n\n" + record["preamble"] + rest.lstrip("\n")
        else:
            expected = record["preamble"] + assembled
        citations = record["citations"]
        expected += "\n## Provenance\n\nMigrated from the original blueprints"
        expected += "".join(f"[^{s['id']}]" for s in citations if s["id"].startswith("original-"))
        expected += ".\n\n"
        authorities = [s for s in citations if s["id"].startswith("authority-")]
        if authorities:
            expected += "External authorities supporting this guidance"
            expected += "".join(f"[^{s['id']}]" for s in authorities) + ".\n\n"
        for source in citations:
            expected += f"[^{source['id']}]: {source['title']}\n\n"
        expected = formatted(expected)
        concept = concepts[cid]
        diff = "".join(
            difflib.unified_diff(
                expected.splitlines(keepends=True),
                concept.body.splitlines(keepends=True),
                fromfile="source-reconstruction",
                tofile=cid + ".md",
            )
        )
        approved = record.get("approved_change", {})
        accepted_change = False
        if approved:
            import tomllib

            maintainers = tomllib.loads((repo / "tools/bundle-policy.toml").read_text())[
                "maintainers"
            ]
            try:
                timestamp(approved.get("at"))
                accepted_change = (
                    isinstance(approved.get("by"), str)
                    and approved["by"].startswith("human:")
                    and approved["by"] in maintainers
                    and bool(approved.get("reason"))
                    and approved.get("diff_sha256") == sha(diff.encode())
                    and approved.get("body_sha256") == sha(concept.body.encode())
                )
            except ValueError:
                pass
        if sha(expected.encode()) != record["body_sha256"]:
            errors.append(f"{cid}: baseline reconstruction expectation changed")
        if concept.body != expected and not accepted_change:
            errors.append(
                f"{cid}: content differs from mapped source reconstruction; review the diff\n"
                + "".join(diff.splitlines(keepends=True)[:60])
            )
        fences = [sha(t.content.encode()) for t in MD.parse(concept.body) if t.type == "fence"]
        expected_fences = (
            approved.get("fences_sha256", record["fences_sha256"])
            if accepted_change
            else record["fences_sha256"]
        )
        if fences != expected_fences:
            errors.append(f"{cid}: original fenced examples changed")
        if concept.meta.get("sources") != citations or concept.meta.get("type") != record["type"]:
            errors.append(f"{cid}: source attribution/type differs from map")
    if sorted(consumed) != sorted(units):
        errors.append("source units omitted or claimed more than once")
    for filename, source in mapping["sources"].items():
        if filename == "README.md":
            continue
        path = repo / filename
        targets = rendered_anchors(path.read_text())
        for heading in source["headings"]:
            if heading["slug"] not in targets:
                errors.append(f"{filename}: lost rendered legacy anchor {heading['slug']}")
    return errors
