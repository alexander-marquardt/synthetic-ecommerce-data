#!/usr/bin/env python3
"""Render the dependency review table: one row per direct dependency (#16284).

Docs: dependency-review

The table answers, for each dependency a manifest declares directly, what we use it
for, where our code calls it, how much of it we call, what it pulls in, what is known
against it, and whether we keep it. Its columns come from three places:

* **the tree** (measured on every run): the direct dependencies of every
  ``pyproject.toml`` of the uv workspace (``project.dependencies`` ships, a
  ``dependency-groups`` entry is build or test only) and of every ``package.json``
  beside a ``package-lock.json`` (``dependencies`` ship in the bundle,
  ``devDependencies`` do not); their locked versions and transitive counts from
  ``uv.lock`` and ``package-lock.json``; their call sites and the names we call from a
  parse of our imports (``ast`` for Python, an import regex for TypeScript and
  JavaScript);
* **the network** (``--refresh`` only, written to the data file): known
  vulnerabilities of the locked version from the OSV database (the one ``pip-audit -s
  osv`` and GitHub's advisories feed), and the latest release, its date and the licence
  from PyPI or the npm registry;
* **review** (the data file, by hand): the one-line use, the verdict and the
  elastic/prism#16293 draft rule it applies.

Modes: ``--write`` renders the table into the repo, ``--check`` exits 1 when the
committed table differs from the render, ``--refresh`` fetches the network columns,
``--sites <name>`` prints every call site of one dependency (the table lists the first
few), ``--extras`` prints the extras ``pyproject.toml`` declares, comma-separated, for
an install of all of them before ``--check`` (``customization-ci.yaml``'s
``dependency_review`` step; it reads no venv, since it runs before that install).

Another fleet repo: ``--root <repo>`` reviews that repo's tree from a core checkout
(#16284). Imports map to the distributions in ``<repo>/.venv`` when it exists (``uv
sync --all-extras`` there). An ``[project.optional-dependencies]`` extra ships when a
Dockerfile installs it (``.[<extra>]``, ``--extra <extra>``, ``--all-extras``). The
project and its path sources (core's packages) are ours, not rows. A dependency with no
``uv.lock`` entry shows ``not locked`` in place of its version and fetched columns. The
page names the ``--root`` command and links core's method doc by URL.

What it cannot see: a call made without an import (a CLI run by a hook or a workflow,
a pytest plugin loaded by entry point, a type-stub package); those rows show no call
sites and their use line says how they are reached. A name reached through an attribute
of a ``from`` import is not counted. Transitive counts include every platform's edges.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import tomllib
import urllib.request
import warnings
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, field
from datetime import date
from importlib import metadata
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent)
)  # run as a file, `scripts` is not yet importable
from scripts import dependency_review_images as images  # noqa: E402
from scripts import docs_index_comment  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = "scripts/dependency_review_data.json"
TABLE = "docs/internals/appendix/dependency-review-table.md"
# The images and their OS packages: a page of their own, so neither page passes the
# appendix byte cap (scripts/file_size_cap.txt).
IMAGES_TABLE = "docs/internals/appendix/dependency-review-images-table.md"
# The docs index entry each page opens with here (#16478). Another repo's pages carry none.
ENTRIES = {
    TABLE: docs_index_comment.Comment(
        section="internals/appendix",
        order=700,
        title="Dependency review table",
        summary="one row per direct Python and npm dependency",
    ),
    IMAGES_TABLE: docs_index_comment.Comment(
        section="internals/appendix",
        order=710,
        title="Dependency review of the images",
        summary="each image we build and its OS packages",
    ),
}
SITES_SHOWN = 4
# vendor: a sister's vendored copy of core is not its own code.
SKIP_DIRS = {"node_modules", "dist", "build", "__pycache__", "coverage", "vendor"}
JS_SUFFIXES = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")
OSV = "https://api.osv.dev/v1"
NOT_LOCKED = "not locked"
# The command and the method doc a page names. Another repo runs the script from the
# core checkout beside it (the `../prism` a sister's `tool.uv.sources` names), so its
# page links the doc on GitHub.
COMMAND = "uv run python scripts/dependency_review.py"
FOREIGN_COMMAND = (
    "uv run --project ../prism python ../prism/scripts/dependency_review.py --root ."
)
DOC = "../dependency-review.md"
DOC_URL = (
    "https://github.com/elastic/prism/blob/main/docs/internals/dependency-review.md"
)

Fetch = Callable[[str, dict | None], dict]


@dataclass
class Dep:
    ecosystem: str  # "PyPI" or "npm"
    name: str
    version: str
    shipped: bool
    manifests: list[str]
    transitive: int = 0
    sites: list[str] = field(default_factory=list)
    names: set[str] = field(default_factory=set)
    installed: bool = True  # False: not locked and not installed, its sites unmeasured

    @property
    def key(self) -> str:
        return f"{self.ecosystem}:{self.name}"


def canon(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _walk(root: Path, suffixes: tuple[str, ...]) -> Iterator[Path]:
    for here, dirs, files in os.walk(root):
        dirs[:] = sorted(
            d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")
        )
        for name in sorted(files):
            if name.endswith(suffixes):
                yield Path(here) / name


# --- Python: manifests, uv.lock, imports ----------------------------------------


def _requirement(req: str) -> tuple[str, list[str]]:
    m = re.match(r"\s*([A-Za-z0-9._-]+)\s*(?:\[([^\]]*)\])?", req)
    if m is None:
        raise ValueError(f"not a requirement: {req!r}")
    extras = [e.strip() for e in (m.group(2) or "").split(",") if e.strip()]
    return canon(m.group(1)), extras


def _uv_closure(pkgs: dict[str, dict], name: str, extras: list[str]) -> int:
    seen: set[str] = set()
    visited: set[tuple[str, tuple[str, ...]]] = set()
    stack = [(name, tuple(extras))]
    while stack:
        current, wanted = stack.pop()
        if (current, wanted) in visited:
            continue
        visited.add((current, wanted))
        pkg = pkgs[current]
        edges = list(pkg.get("dependencies", []))
        for extra in wanted:
            edges += pkg.get("optional-dependencies", {}).get(extra, [])
        for edge in edges:
            seen.add(edge["name"])
            stack.append((edge["name"], tuple(edge.get("extra", []))))
    seen.discard(name)
    return len(seen)


def installed_extras(root: Path) -> set[str]:
    """The extras a Dockerfile installs, so ship in its image; ``*`` for ``--all-extras``."""
    found: set[str] = set()
    for image in images.images(root):
        text = (root / image.dockerfile).read_text()
        if "--all-extras" in text:
            found.add("*")
        for group in re.findall(r"\.\[([^\]]+)\]", text):
            found |= {e.strip() for e in group.split(",")}
        found |= set(re.findall(r"--extra[= ]([\w-]+)", text))
    return found


def python_deps(root: Path) -> list[Dep]:
    workspace = tomllib.loads((root / "pyproject.toml").read_text())
    members = (
        workspace.get("tool", {}).get("uv", {}).get("workspace", {}).get("members", [])
    )
    lock_file = root / "uv.lock"
    lock = tomllib.loads(lock_file.read_text()) if lock_file.exists() else {}
    pkgs = {p["name"]: p for p in lock.get("package", [])}
    local = {n for n, p in pkgs.items() if {"editable", "virtual"} & set(p["source"])}
    shipping = installed_extras(root)
    found: dict[str, Dep] = {}
    extras: dict[str, list[str]] = {}
    for manifest in ["."] + members:
        rel = str(Path(manifest) / "pyproject.toml")
        doc = tomllib.loads((root / rel).read_text())
        project = doc.get("project", {})
        # The project and its path sources (core's packages, in a sister) are ours,
        # with or without a lock entry that says so.
        sources = doc.get("tool", {}).get("uv", {}).get("sources", {})
        local.add(canon(project.get("name", "")))
        local |= {
            canon(n)
            for n, s in sources.items()
            if isinstance(s, dict) and {"path", "workspace"} & set(s)
        }
        declared = [(r, True, rel) for r in project.get("dependencies", [])]
        for extra, reqs in project.get("optional-dependencies", {}).items():
            ships = bool({extra, "*"} & shipping)
            declared += [(r, ships, f"{rel} (extra {extra})") for r in reqs]
        for group, reqs in doc.get("dependency-groups", {}).items():
            declared += [
                (r, False, f"{rel} ({group})") for r in reqs if isinstance(r, str)
            ]
        for req, shipped, where in declared:
            name, wanted = _requirement(req)
            if name in local:
                continue
            dep = found.setdefault(
                name,
                Dep(
                    "PyPI",
                    name,
                    pkgs.get(name, {}).get("version", NOT_LOCKED),
                    False,
                    [],
                ),
            )
            dep.shipped |= shipped
            dep.manifests.append(where)
            extras[name] = sorted(set(extras.get(name, [])) | set(wanted))
    for name, dep in found.items():
        if name in pkgs:
            dep.transitive = _uv_closure(pkgs, name, extras[name])
    return sorted(found.values(), key=lambda d: d.name)


def _module_of(file: str) -> str | None:
    parts = file.split("/")
    if parts[0] == ".." or ".dist-info" in file or "__pycache__" in parts:
        return None
    stem, _, suffix = parts[-1].partition(".")
    if suffix.rsplit(".", 1)[-1] not in ("py", "pyi", "so", "pyd"):
        return None
    parts = parts[:-1] if stem == "__init__" else parts[:-1] + [stem]
    return ".".join(parts) or None


def _distribution(name: str, path: list[str] | None) -> metadata.Distribution:
    if path is None:
        return metadata.distribution(name)
    for dist in metadata.distributions(name=name, path=path):
        return dist
    raise metadata.PackageNotFoundError(name)


def site_packages(root: Path) -> list[str] | None:
    """``<root>/.venv``'s site-packages, or None (this interpreter's) when it has none."""
    return sorted(str(p) for p in root.glob(".venv/lib/python*/site-packages")) or None


def module_owners(names: list[str], path: list[str] | None = None) -> dict[str, str]:
    """Map each importable module of the installed distributions to its distribution:
    those on ``path``, else this interpreter's."""
    owners: dict[str, str] = {}
    for name in sorted(names):
        try:
            files = _distribution(name, path).files or []
        except metadata.PackageNotFoundError:
            continue
        for file in files:
            module = _module_of(str(file))
            if module:
                owners.setdefault(module, name)
    return owners


def _owner(module: str, owners: dict[str, str]) -> str | None:
    parts = module.split(".")
    for end in range(len(parts), 0, -1):
        if (hit := owners.get(".".join(parts[:end]))) is not None:
            return hit
    return None


def python_sites(
    root: Path,
    deps: dict[str, Dep],
    owners: dict[str, str],
    wanted: Callable[[str], bool] = lambda rel: True,
) -> None:
    for path in _walk(root, (".py",)):
        rel = path.relative_to(root).as_posix()
        if not wanted(rel):
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, ValueError):
            continue
        aliases: dict[str, Dep] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and not node.level:
                dep = deps.get(_owner(node.module, owners) or "")
                if dep:
                    dep.sites.append(f"{rel}:{node.lineno}")
                    dep.names.update(a.name for a in node.names)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    dep = deps.get(_owner(alias.name, owners) or "")
                    if dep:
                        dep.sites.append(f"{rel}:{node.lineno}")
                        aliases[alias.asname or alias.name.split(".")[0]] = dep
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and (dep := aliases.get(node.value.id)) is not None
            ):
                dep.names.add(node.attr)


# --- npm: package.json, package-lock.json, imports -------------------------------


def _npm_resolve(packages: dict[str, dict], at: str, dep: str) -> str | None:
    base = at
    while True:
        candidate = f"{base}/node_modules/{dep}" if base else f"node_modules/{dep}"
        if candidate in packages:
            return candidate
        if not base:
            return None
        cut = base.rfind("/node_modules/")
        base = base[:cut] if cut >= 0 else ""


def _npm_closure(packages: dict[str, dict], start: str) -> int:
    seen: set[str] = set()
    stack = [start]
    while stack:
        at = stack.pop()
        entry = packages[at]
        wanted = {
            **entry.get("dependencies", {}),
            **entry.get("optionalDependencies", {}),
        }
        wanted.update(entry.get("peerDependencies", {}))
        for name in wanted:
            hit = _npm_resolve(packages, at, name)
            if hit and hit not in seen:
                seen.add(hit)
                stack.append(hit)
    names = {p.rsplit("node_modules/", 1)[1] for p in seen}
    names.discard(start.rsplit("node_modules/", 1)[1])
    return len(names)


_JS_IMPORT = re.compile(
    r"""(?:^|[;\s])(?:import|export)\s+(?:type\s+)?([\w*{}\s,$]*?)\s*from\s*['"]([^'"]+)['"]"""
    r"""|(?:^|[;\s])import\s*['"]([^'"]+)['"]"""
    r"""|\b(?:import|require)\s*\(\s*['"]([^'"]+)['"]\s*\)""",
    re.M,
)


def _js_package(spec: str) -> str:
    # A relative, absolute or node: spec yields a name no manifest declares.
    parts = spec.split("/")
    return "/".join(parts[:2]) if spec.startswith("@") else parts[0]


def _js_names(clause: str, text: str) -> set[str]:
    names: set[str] = set()
    named = re.search(r"\{([^}]*)\}", clause)
    if named:
        for item in named.group(1).split(","):
            word = item.strip().removeprefix("type ").split(" as ")[0].strip()
            if word:
                names.add(word)
    rest = re.sub(r"\{[^}]*\}", "", clause)
    namespace = re.search(r"\*\s*as\s+([\w$]+)", rest)
    if namespace:
        names.update(re.findall(rf"\b{re.escape(namespace.group(1))}\.(\w+)", text))
    elif re.search(r"[\w$]", rest.replace(",", "")):
        names.add("default")
    return names


def npm_deps(root: Path) -> list[Dep]:
    found: dict[str, Dep] = {}
    for manifest in _walk(root, (".json",)):
        lockfile = manifest.with_name("package-lock.json")
        if manifest.name != "package.json" or not lockfile.exists():
            continue
        rel = manifest.relative_to(root).as_posix()
        doc = json.loads(manifest.read_text())
        packages = json.loads(lockfile.read_text())["packages"]
        for section, shipped in (("dependencies", True), ("devDependencies", False)):
            for name in doc.get(section, {}):
                path = f"node_modules/{name}"
                dep = found.setdefault(
                    name, Dep("npm", name, packages[path]["version"], False, [])
                )
                dep.shipped |= shipped
                dep.manifests.append(f"{rel} ({section})")
                dep.transitive = max(dep.transitive, _npm_closure(packages, path))
    return sorted(found.values(), key=lambda d: d.name)


def npm_sites(
    root: Path,
    deps: dict[str, Dep],
    wanted: Callable[[str], bool] = lambda rel: True,
) -> None:
    manifests = {m.split(" (")[0] for d in deps.values() for m in d.manifests}
    for base in sorted(root / Path(m).parent for m in manifests):
        for path in _walk(base, JS_SUFFIXES):
            rel = path.relative_to(root).as_posix()
            if not wanted(rel):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for m in _JS_IMPORT.finditer(text):
                spec = m.group(2) or m.group(3) or m.group(4)
                dep = deps.get(_js_package(spec))
                if dep is None:
                    continue
                dep.sites.append(f"{rel}:{text.count(chr(10), 0, m.end()) + 1}")
                dep.names |= (
                    _js_names(m.group(1), text) if m.group(2) else {"(whole module)"}
                )


# --- network columns (--refresh) ------------------------------------------------


def fetch_json(url: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(  # noqa: S310  # https URLs this script builds itself (OSV, PyPI, npm), never user input
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "prism-dependency-review",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310  # see the Request above
        result: dict = json.load(response)
        return result


def _licence(info: dict) -> str:
    if info.get("license_expression"):
        return str(info["license_expression"])
    for classifier in info.get("classifiers", []):
        if classifier.startswith("License :: OSI Approved :: "):
            return str(classifier.rsplit(" :: ", 1)[1])
    text = (info.get("license") or "").strip().splitlines()
    return str(text[0][:40]) if text else "not stated"


def _registry(dep: Dep, fetch: Fetch) -> tuple[str, str, str]:
    if dep.ecosystem == "PyPI":
        doc = fetch(f"https://pypi.org/pypi/{dep.name}/json", None)
        info = doc["info"]
        released = doc["urls"][0]["upload_time"][:10] if doc.get("urls") else "unknown"
        return info["version"], released, _licence(info)
    doc = fetch(f"https://registry.npmjs.org/{dep.name.replace('/', '%2F')}", None)
    latest = doc["dist-tags"]["latest"]
    licence = (
        doc.get("license") or doc["versions"][latest].get("license") or "not stated"
    )
    licence = (
        licence.get("type", "not stated") if isinstance(licence, dict) else licence
    )
    return latest, doc["time"][latest][:10], licence


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(n) for n in re.findall(r"\d+", version.split("-")[0]))


def _fixed_in(detail: dict, dep: Dep) -> str:
    """The lowest fixed version above the locked one, from the advisory's ranges."""
    fixes = [
        event["fixed"]
        for affected in detail.get("affected", [])
        if canon(affected.get("package", {}).get("name", "")) == canon(dep.name)
        for ranged in affected.get("ranges", [])
        for event in ranged.get("events", [])
        if "fixed" in event and _version_key(event["fixed"]) > _version_key(dep.version)
    ]
    return min(fixes, key=_version_key) if fixes else "no fixed release"


def refresh(deps: list[Dep], fetch: Fetch = fetch_json) -> dict[str, dict]:
    deps = [d for d in deps if d.version != NOT_LOCKED]  # OSV needs a version
    queries = [
        {"package": {"name": d.name, "ecosystem": d.ecosystem}, "version": d.version}
        for d in deps
    ]
    results = fetch(f"{OSV}/querybatch", {"queries": queries})["results"]
    fetched: dict[str, dict] = {}
    for dep, result in zip(deps, results, strict=True):
        vulns = []
        for vuln in result.get("vulns", []):
            detail = fetch(f"{OSV}/vulns/{vuln['id']}", None)
            severity = detail.get("database_specific", {}).get("severity") or "unrated"
            fixed = _fixed_in(detail, dep)
            vulns.append(f"{vuln['id']} ({severity.lower()}, fixed in {fixed})")
        latest, released, licence = _registry(dep, fetch)
        fetched[dep.key] = {
            "version": dep.version,
            "vulnerabilities": vulns,
            "latest": latest,
            "released": released,
            "licence": licence,
        }
    return fetched


# --- render ---------------------------------------------------------------------

_HEADER = [
    "Dependency",
    "Locked",
    "Declared in",
    "Use",
    "Reach",
    "Call sites",
    "Names called",
    "Transitive",
    "Known vulnerabilities",
    "Latest release",
    "Licence",
    "Verdict (draft rule)",
]


def _table(rows: list[list[str]]) -> list[str]:
    """A table in prettier's form: every column padded to its widest cell."""
    widths = [max(3, *(len(row[i]) for row in rows)) for i in range(len(rows[0]))]
    out = [
        "| " + " | ".join(c.ljust(w) for c, w in zip(row, widths, strict=True)) + " |"
        for row in rows
    ]
    out.insert(1, "| " + " | ".join("-" * w for w in widths) + " |")
    return out


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _sites(dep: Dep) -> str:
    if not dep.installed:
        return "not measured: not installed"
    if not dep.sites:
        return "none (no import)"
    # Files, not lines: a line number in a page goes stale as the file grows (#8344).
    # --sites prints every path:line.
    files = list(dict.fromkeys(s.rsplit(":", 1)[0] for s in dep.sites))
    shown = ", ".join(f"`{f}`" for f in files[:SITES_SHOWN])
    more = len(files) - SITES_SHOWN
    return f"{len(dep.sites)}: {shown}" + (f", and {more} more" if more > 0 else "")


def _row(dep: Dep, review: dict) -> list[str]:
    fetched = review.get("fetched", {})
    stale = fetched and fetched.get("version") != dep.version
    if dep.version == NOT_LOCKED:
        vulns = latest = licence = "not locked: no version to look up"
    elif not fetched or stale:
        vulns = latest = licence = "not fetched for this version: run --refresh"
    else:
        vulns = ", ".join(fetched["vulnerabilities"]) or "none"
        latest = f"{fetched['latest']} ({fetched['released']})"
        licence = fetched["licence"]
    verdict = review.get("verdict", "not reviewed")
    if review.get("rule"):
        verdict += f" (`{review['rule']}`)"
    if review.get("note"):
        verdict += f": {review['note']}"
    cells = [
        f"`{dep.name}`",
        dep.version,
        ", ".join(f"`{m}`" for m in dep.manifests),
        review.get("use", "not reviewed"),
        "shipped" if dep.shipped else "build or test only",
        _sites(dep),
        str(len(dep.names)),
        NOT_LOCKED if dep.version == NOT_LOCKED else str(dep.transitive),
        vulns,
        latest,
        licence,
        verdict,
    ]
    return [_cell(c) for c in cells]


def render(
    groups: dict[str, list[Dep]],
    data: dict,
    tail: Sequence[str] = (),
    page: tuple[str, str] = ("dependency-review-table", "Dependency review table"),
    measured: str = "",
    origin: tuple[str, str] = (COMMAND, DOC),
) -> str:
    """One appendix page: ``page`` is its anchor and title, ``measured`` a sentence on
    where its measured columns come from (default: the registries' columns), ``origin``
    the command that writes it and the method doc it links."""
    lines = [
        f'<a id="{page[0]}"></a>',
        "",
        f"# Appendix: {page[1]}",
        "",
        "<!-- audience: internals -->",
        "",
        f"Generated by `{origin[0]} --write`; never edit it by hand.",
        f"The use, verdict and rule of each row are review, kept in `{DATA}`.",
        measured
        or "The vulnerability, release and licence columns are the OSV database and the package\n"
        f"registry as of {data.get('fetched_on', 'never')} (`--refresh`).",
        "The method and the command behind each column, and the elastic/prism#16293 draft",
        f"rules a verdict names: [Dependency review]({origin[1]}).",
    ]
    reviews = data.get("dependencies", {})
    for title, deps in groups.items():
        lines += ["", f"## {title}", ""]
        lines += _table([_HEADER] + [_row(d, reviews.get(d.key, {})) for d in deps])
    return "\n".join([*lines, *tail]) + "\n"


def os_group(root: Path, imgs: list[images.Image], data: dict) -> list[Dep]:
    """The OS packages our Dockerfiles install, as dependency rows; their columns are measured by --images."""
    deps = []
    for entry in images.os_packages(root, imgs, data):
        dep = Dep(
            entry["ecosystem"],
            entry["name"],
            entry.get("version", images.NOT_MEASURED),
            True,
            [f"{m} (RUN)" for m in entry["manifests"]],
            entry.get("transitive", 0),
            entry["sites"],
            {entry["name"]} if entry["sites"] else set(),
        )
        review = data.setdefault("dependencies", {}).setdefault(dep.key, {})
        review.pop("fetched", None)
        if "fetched" in entry:
            review["fetched"] = entry["fetched"]
        deps.append(dep)
    return deps


def collect(root: Path) -> dict[str, list[Dep]]:
    python = python_deps(root)
    npm = npm_deps(root)
    by_name = {d.name: d for d in python}
    venv = site_packages(root)
    owners = module_owners(list(by_name), venv)
    unmapped = sorted(set(by_name) - set(owners.values()))
    # Another interpreter (the system python3) lacks the workspace's packages, and
    # its table would show their call sites as "none (no import)". A dependency the
    # lock leaves out (an extra past an override marker) is never installed: its row
    # says so.
    if missing := [n for n in unmapped if by_name[n].version != NOT_LOCKED]:
        where = f"{root}/.venv" if venv else "this interpreter"
        raise SystemExit(
            f"not installed in {where}: {', '.join(missing)}; "
            f"run uv sync --all-extras in {root}, or uv run python scripts/dependency_review.py"
        )
    for name in unmapped:
        by_name[name].installed = False
    python_sites(root, by_name, owners)
    npm_sites(root, {d.name: d for d in npm})
    for dep in python + npm:
        dep.sites.sort(key=lambda s: (s.rsplit(":", 1)[0], int(s.rsplit(":", 1)[1])))
    return {"Python (uv.lock)": python, "npm (package-lock.json)": npm}


def main(
    argv: list[str] | None = None,
    fetch: Fetch = fetch_json,
    run: images.Run = images.run_command,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--write", action="store_true", help="render the table into the repo"
    )
    mode.add_argument(
        "--check", action="store_true", help="exit 1 if the table is stale"
    )
    mode.add_argument(
        "--refresh", action="store_true", help="fetch the network columns"
    )
    mode.add_argument(
        "--images", action="store_true", help="build and measure every image (docker)"
    )
    mode.add_argument(
        "--sites", metavar="NAME", help="print every call site of one dependency"
    )
    mode.add_argument(
        "--extras",
        action="store_true",
        help="print the extras pyproject.toml declares, comma-separated",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.extras:
        project = tomllib.loads((root / "pyproject.toml").read_text()).get(
            "project", {}
        )
        print(",".join(project.get("optional-dependencies", {})))
        return 0
    groups = collect(root)
    data_path = root / DATA
    data = json.loads(data_path.read_text()) if data_path.exists() else {}
    if args.sites:
        for dep in (
            d for deps in groups.values() for d in deps if d.name == args.sites
        ):
            print("\n".join(dep.sites) or "none")
        return 0
    if args.refresh:
        fetched = refresh([d for deps in groups.values() for d in deps], fetch)
        reviews = data.setdefault("dependencies", {})
        for key, values in fetched.items():
            reviews.setdefault(key, {})["fetched"] = values
        data["fetched_on"] = date.today().isoformat()
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        print(f"refreshed {len(fetched)} dependencies into {DATA}")
        return 0
    imgs = images.images(root)
    if args.images:
        measured = images.measure(root, data, run, fetch)
        data_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        print(f"measured {len(measured)} images into {DATA}")
        return 0
    view = json.loads(
        json.dumps(data)
    )  # the OS rows' measured columns, never written back
    origin = (COMMAND, DOC) if root == ROOT else (FOREIGN_COMMAND, DOC_URL)
    pages = {TABLE: render(groups, view, origin=origin)}
    if imgs:
        os_deps = os_group(root, imgs, view)
        pages[IMAGES_TABLE] = render(
            {"OS packages (Dockerfile installs)": os_deps} if os_deps else {},
            view,
            images.section(imgs, view, _table),
            ("dependency-review-images-table", "Dependency review of the images"),
            "The other columns are measured by `--images` (docker and Trivy) on each image"
            " the repository builds.",
            origin,
        )
    if root == ROOT:
        pages = {
            name: f"{docs_index_comment.format_comment(ENTRIES[name])}\n\n{text}"
            for name, text in pages.items()
        }
    stale = []
    for name, text in pages.items():
        table = root / name
        if args.check:
            if not (table.exists() and table.read_text() == text):
                stale.append(name)
            continue
        table.parent.mkdir(parents=True, exist_ok=True)
        table.write_text(text)
        print(f"wrote {name}")
    for name in stale:
        print(f"{name} is stale: run {origin[0]} --write")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
