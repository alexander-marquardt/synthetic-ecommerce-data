"""The image half of the dependency review: one row per image a Dockerfile builds (#16284).

Docs: dependency-review-images

``scripts/dependency_review.py`` imports this module and renders its two sections into
the same table page. The columns come from three places:

* **the tree** (read on every run): each ``Dockerfile`` and ``Dockerfile.*`` of the
  repository, its runtime stage (the last ``FROM``, with ``ARG`` defaults put in), the
  base image and tag, full or minimal from that tag, the digest pin, and the OS
  packages its ``RUN`` lines install (``apt-get install``, ``apk add``). Those are the
  image's direct OS dependencies, one dependency row each. Their call sites are the
  lines that name the package's command, in the same Dockerfile (outside the install)
  and in the compose services built from it;
* **docker** (``--images`` only, written to the data file): each image is built from
  the repository root and measured: its size, its OS packages, the build tools on its
  ``PATH``, the user it runs as (``id -un``), and its known vulnerabilities (Trivy, run
  as a container on the built image). Each installed package's version, licence (its
  ``copyright`` file) and transitive count (its ``Depends`` closure among the image's
  packages) are measured too, and its release date comes from snapshot.debian.org. A
  move-to-minimal verdict names a base, and that base is pulled and measured so that the
  row can give the expected size and package count;
* **review** (the data file, by hand): the verdict, the rule it applies and the base it
  names.

What it cannot see: a command the package provides under another name, or a call made
from a script the image copies in. A build stage that does not ship is not measured.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from prism_engine.strict_yaml import safe_load_strict

from scripts.bounded_process import run_bounded

_DOCKER_LIMIT = 3600.0  # seconds: a build of the largest image, ended with its process group (#10290)
Run = Callable[[list[str]], str]
Fetch = Callable[[str, dict | None], dict]

TRIVY = "aquasec/trivy:0.69.3"
TRIVY_CACHE = "prism-review-trivy-cache"
TOOLS = ("gcc", "cc", "c++", "make", "git", "pip", "npm", "node", "uv")
MINIMAL = re.compile(r"slim|alpine|distroless|chiseled|minimal|micro")
SEVERE = ("CRITICAL", "HIGH")
SKIP_DIRS = {"node_modules", "tests"}  # a test fixture is no image we build
SNAPSHOT = "https://snapshot.debian.org/mr/package"
NOT_MEASURED = "not measured for this Dockerfile: run --images"

PROBE = r"""
. /etc/os-release; echo "os $ID $VERSION_ID"; echo "user $(id -un)"
for t in TOOLS; do command -v "$t" >/dev/null 2>&1 && echo "tool $t"; done
if command -v dpkg-query >/dev/null 2>&1; then
  dpkg-query -W -f 'pkg ${Package}\t${Version}\t${source:Package}\t${source:Version}\t${Pre-Depends}, ${Depends}\n'
else
  apk info 2>/dev/null | sed 's/^/pkg /'
fi
for p in "$@"; do
  echo "licence $p	$(sed -n 's/^License: *//p' /usr/share/doc/$p/copyright 2>/dev/null | head -n 1)"
done
""".replace("TOOLS", " ".join(TOOLS))


def run_command(argv: list[str]) -> str:
    """Run ``docker <argv>``, ended with its process group at the limit."""
    return run_bounded(
        ["docker", *argv], timeout=_DOCKER_LIMIT, check=True, capture_output=True
    ).stdout


@dataclass
class Image:
    dockerfile: str
    base: str
    installs: list[str]
    body: list[tuple[int, str]] = field(default_factory=list)
    ecosystem: str = "Debian"  # "Alpine" when an `apk add` installs the packages

    @property
    def tag(self) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", self.dockerfile.lower()).strip("-")
        return f"prism-review/{slug}:local"

    @property
    def minimal(self) -> bool:
        return bool(MINIMAL.search(self.base))

    @property
    def pinned(self) -> bool:
        return "@sha256:" in self.base


# --- the tree --------------------------------------------------------------------


def _logical(text: str) -> list[tuple[int, str]]:
    """Each instruction with its first line number: continuations joined, comments and heredoc bodies skipped."""
    lines = text.splitlines()
    out: list[tuple[int, str]] = []
    i = 0
    while i < len(lines):
        start, line = i, lines[i].strip()
        i += 1
        if not line or line.startswith("#"):
            continue
        while line.endswith("\\") and i < len(lines):
            line = line[:-1].rstrip() + " " + lines[i].strip()
            i += 1
        out.append((start + 1, line))
        if heredoc := re.search(r"<<-?\s*['\"]?(\w+)['\"]?", line):
            while i < len(lines) and lines[i].strip() != heredoc.group(1):
                i += 1
            i += 1
    return out


def _installs(run: str) -> list[str]:
    found: list[str] = []
    for segment in re.split(r"&&|\|\||;", run):
        words = segment.split()
        for manager, verb in (
            ("apt-get", "install"),
            ("apt", "install"),
            ("apk", "add"),
        ):
            if manager in words and verb in words[words.index(manager) :]:
                rest = words[words.index(verb, words.index(manager)) + 1 :]
                found += [w.split("=")[0] for w in rest if not w.startswith("-")]
    return found


def parse(root: Path, rel: str) -> Image:
    args: dict[str, str] = {}
    stages: list[tuple[str, list[tuple[int, str]]]] = []
    for number, line in _logical((root / rel).read_text()):
        word, _, rest = line.partition(" ")
        if word.upper() == "ARG" and not stages:
            name, _, default = rest.partition("=")
            args[name.strip()] = default.strip().strip("\"'")
        elif word.upper() == "FROM":
            ref = re.sub(r"--\S+\s+", "", rest).split()[0]
            ref = re.sub(
                r"\$\{?(\w+)\}?", lambda m: args.get(m.group(1), m.group(0)), ref
            )
            stages.append((ref, []))
        elif stages:
            stages[-1][1].append((number, line))
    if not stages:
        raise ValueError(f"{rel}: no FROM line")
    base, body = stages[-1]
    installs = [
        p
        for _, line in body
        if line.upper().startswith("RUN ")
        for p in _installs(line)
    ]
    alpine = any(_installs(line) and "apk" in line.split() for _, line in body)
    return Image(
        rel, base, list(dict.fromkeys(installs)), body, "Alpine" if alpine else "Debian"
    )


def images(root: Path) -> list[Image]:
    found = []
    for here, dirs, files in os.walk(root):
        dirs[:] = sorted(
            d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")
        )
        for name in sorted(files):
            if (
                name == "Dockerfile" or name.startswith("Dockerfile.")
            ) and not name.endswith(".dockerignore"):
                found.append(
                    parse(root, (Path(here) / name).relative_to(root).as_posix())
                )
    return found


COMPOSE_TAGS = {"!reset", "!override"}


def _untag(node: yaml.Node) -> None:
    """Read compose's merge tags (``!reset []``, ``ports: !override``) as the YAML they tag."""
    if node.tag in COMPOSE_TAGS:
        value = node.value if isinstance(node, yaml.ScalarNode) else None
        node.tag = yaml.resolver.Resolver().resolve(type(node), value, (True, False))
    if isinstance(node, yaml.MappingNode):
        for key, child in node.value:
            _untag(key)
            _untag(child)
    elif isinstance(node, yaml.SequenceNode):
        for child in node.value:
            _untag(child)


def _compose_services(root: Path) -> list[tuple[str, str, int, int]]:
    """(compose file, Dockerfile it builds, first line, last line) of each service that builds one."""
    found = []
    for path in sorted(root.glob("docker-compose*.y*ml")):
        node = yaml.compose(path.read_text())
        if node is None:
            continue
        _untag(node)
        top = {k.value: v for k, v in node.value}
        for _, service in getattr(top.get("services"), "value", []):
            spec = safe_load_strict(yaml.serialize(service), source=path) or {}
            build = spec.get("build")
            if build is None:
                continue
            build = {"context": build} if isinstance(build, str) else build
            dockerfile = os.path.normpath(
                os.path.join(
                    build.get("context", "."), build.get("dockerfile", "Dockerfile")
                )
            )
            found.append(
                (
                    path.name,
                    dockerfile,
                    service.start_mark.line + 1,
                    service.end_mark.line,
                )
            )
    return found


def call_sites(root: Path, imgs: list[Image]) -> dict[str, list[str]]:
    """Each installed package's call sites: lines that name its command in our Dockerfiles and their compose services."""
    installs = {p for image in imgs for p in image.installs}
    sites: dict[str, list[str]] = {p: [] for p in installs}

    def scan(rel: str, lines: list[tuple[int, str]], packages: set[str]) -> None:
        for number, line in lines:
            for package in packages:
                if re.search(rf"(?<![\w-]){re.escape(package)}(?![\w-])", line):
                    sites[package].append(f"{rel}:{number}")

    for image in imgs:
        body = [(n, line) for n, line in image.body if not _installs(line)]
        scan(image.dockerfile, body, set(image.installs))
    by_file = {image.dockerfile: set(image.installs) for image in imgs}
    for compose, dockerfile, first, last in _compose_services(root):
        text = (root / compose).read_text().splitlines()
        lines = [
            (n, text[n - 1])
            for n in range(first, last + 1)
            if not text[n - 1].lstrip().startswith("#")
        ]
        scan(compose, lines, by_file.get(dockerfile, set()))
    return {
        p: sorted(set(s), key=lambda s: (s.rsplit(":", 1)[0], int(s.rsplit(":", 1)[1])))
        for p, s in sites.items()
    }


# --- docker (--images) -----------------------------------------------------------


def probe(ref: str, runner: Run, packages: Sequence[str] = ()) -> dict:
    out = runner(
        [
            "run",
            "--rm",
            "--entrypoint",
            "sh",
            ref,
            "-c",
            PROBE,
            "probe",
            *packages,
        ]
    )
    found: dict = {"tools": [], "packages": {}, "licences": {}}
    for line in out.splitlines():
        kind, _, rest = line.partition(" ")
        if kind == "os":
            found["os"] = rest
        elif kind == "user":
            found["user"] = rest
        elif kind == "tool":
            found["tools"].append(rest)
        elif kind == "pkg":
            name, *cols = rest.split("\t")
            version, source, source_version, depends = (cols + ["", "", "", ""])[:4]
            names = {
                re.split(r"[\s:(]", a.strip())[0] for a in re.split(r"[,|]", depends)
            }
            found["packages"][name] = {
                "version": version,
                "source": source or name,
                "source_version": source_version or version,
                "depends": sorted(n for n in names if n),
            }
        elif kind == "licence":
            name, _, licence = rest.partition("\t")
            found["licences"][name] = licence or "not stated"
    size = runner(["image", "inspect", "-f", "{{.Size}}", ref]).strip()
    found["size"] = int(size)
    return found


def closure(packages: dict[str, dict], name: str) -> int:
    seen: set[str] = set()
    stack = [name]
    while stack:
        for dep in packages.get(stack.pop(), {}).get("depends", []):
            if dep in packages and dep not in seen:
                seen.add(dep)
                stack.append(dep)
    seen.discard(name)
    return len(seen)


def scan(ref: str, runner: Run) -> list[dict]:
    out = runner(
        [
            "run", "--rm",
            "-v", "/var/run/docker.sock:/var/run/docker.sock",
            "-v", f"{TRIVY_CACHE}:/root/.cache",
            TRIVY, "image", "--quiet", "--format", "json", "--scanners", "vuln", ref,
        ]
    )  # fmt: skip
    vulns = []
    for result in json.loads(out).get("Results", []):
        for v in result.get("Vulnerabilities") or []:
            vulns.append(
                {
                    "id": v["VulnerabilityID"],
                    "package": v["PkgName"],
                    "source": v.get("SrcName") or v["PkgName"],
                    "severity": v.get("Severity", "UNKNOWN").lower(),
                    "fixed": v.get("FixedVersion") or "",
                }
            )
    return vulns


def _released(source: str, version: str, fetch: Fetch) -> str:
    """The day the Debian archive first held this source version: its ``.dsc`` file's
    first sighting. The orig tarball can be years older (one upstream release, many
    Debian revisions), so the other files' dates are not read."""
    doc = fetch(
        f"{SNAPSHOT}/{source}/{version.replace('+', '%2B')}/srcfiles?fileinfo=1", None
    )
    seen = [
        f["first_seen"]
        for files in doc.get("fileinfo", {}).values()
        for f in files
        if f.get("name", "").endswith(".dsc")
    ]
    return f"{min(seen)[:4]}-{min(seen)[4:6]}-{min(seen)[6:8]}" if seen else "unknown"


def _vuln_text(v: dict) -> str:
    return f"{v['id']} ({v['severity']}, {('fixed in ' + v['fixed']) if v['fixed'] else 'no fixed release'})"


def measure(root: Path, data: dict, runner: Run, fetch: Fetch) -> dict[str, dict]:
    """Build and measure every image; the data file's ``images`` entries, ``measured`` filled in."""
    reviews = data.setdefault("images", {})
    for image in images(root):
        runner(
            [
                "build",
                "-q",
                "-f",
                image.dockerfile,
                "-t",
                image.tag,
                str(root),
            ]
        )
        built = probe(image.tag, runner, image.installs)
        base = probe(image.base, runner)
        digests = runner(
            [
                "image",
                "inspect",
                "-f",
                '{{join .RepoDigests " "}}',
                image.base,
            ]
        )
        vulns = scan(image.tag, runner)
        installs = {}
        for name in image.installs:
            pkg = built["packages"].get(name, {})
            source = pkg.get("source", name)
            installs[name] = {
                "version": pkg.get("version") or "unknown",
                "transitive": closure(built["packages"], name),
                "licence": built["licences"].get(name, "not stated"),
                "released": _released(source, pkg["source_version"], fetch)
                if pkg.get("source_version")
                else "unknown",
                "vulnerabilities": sorted(
                    {
                        _vuln_text(v)
                        for v in vulns
                        if v["package"] == name or v["source"] == source
                    }
                ),
            }
        severe: dict[str, dict] = {}
        for v in vulns:
            if v["severity"].upper() in SEVERE:
                entry = severe.setdefault(
                    v["id"],
                    {"severity": v["severity"], "fixed": v["fixed"], "packages": []},
                )
                entry["packages"] = sorted(set(entry["packages"]) | {v["package"]})
        measured = {
            "base": image.base,
            "installs": installs,
            "os": built.get("os", "unknown"),
            "size": built["size"],
            "packages": len(built["packages"]),
            "tools": built["tools"],
            "user": built.get("user", "unknown"),
            "base_size": base["size"],
            "base_packages": len(base["packages"]),
            "base_digest": (digests.split() or ["none"])[0]
            .rsplit("@", 1)[-1]
            .removeprefix("sha256:"),
            "severe": severe,
        }
        review = reviews.setdefault(image.dockerfile, {})
        if review.get("minimal"):
            runner(["pull", "-q", review["minimal"]])
            candidate = probe(review["minimal"], runner)
            measured["minimal"] = {
                "ref": review["minimal"],
                "size": candidate["size"] + built["size"] - base["size"],
                "packages": len(candidate["packages"])
                + len(built["packages"])
                - len(base["packages"]),
            }
        review["measured"] = measured
    return reviews


# --- render ----------------------------------------------------------------------

HEADER = [
    "Image (Dockerfile)",
    "Runtime base",
    "Full or minimal",
    "Size",
    "OS packages",
    "Build tools at runtime",
    "Runtime user",
    "Pinned by digest",
    "Known high and critical",
    "Verdict (rule)",
]


def _mb(size: int) -> str:
    return f"{size / 1e6:.0f} MB"


def _severe(severe: dict[str, dict]) -> str:
    if not severe:
        return "none"
    counts = []
    for level in ("critical", "high"):
        ids = [i for i, v in severe.items() if v["severity"] == level]
        if ids:
            counts.append(f"{len(ids)} {level}")
    fixed = sorted(
        f"{i} ({', '.join(v['packages'])}, fixed in {v['fixed']})"
        for i, v in severe.items()
        if v["fixed"]
    )
    text = ", ".join(counts) + f" ({len(fixed)} with a fixed release"
    return text + (f": {'; '.join(fixed)})" if fixed else ")")


def current(image: Image, review: dict) -> dict:
    """The measured entry when it was measured for this Dockerfile's base and installs, else {}."""
    measured = review.get("measured", {})
    if measured.get("base") != image.base or sorted(
        measured.get("installs", {})
    ) != sorted(image.installs):
        return {}
    return measured


def row(image: Image, review: dict) -> list[str]:
    measured = current(image, review)
    verdict = review.get("verdict", "not reviewed")
    if measured.get("minimal"):
        m = measured["minimal"]
        verdict += (
            f" `{m['ref']}` (expected {_mb(m['size'])}, {m['packages']} OS packages)"
        )
    if review.get("rule"):
        verdict += f" (`{review['rule']}`)"
    if review.get("note"):
        verdict += f": {review['note']}"
    kind = "minimal" if image.minimal else "full"
    if not measured:
        return [
            f"`{image.dockerfile}`",
            f"`{image.base}`",
            kind,
            *[NOT_MEASURED] * 6,
            verdict,
        ]
    tools = measured["tools"]
    pin = "yes" if image.pinned else f"no (now `sha256:{measured['base_digest'][:12]}`)"
    return [
        f"`{image.dockerfile}`",
        f"`{image.base}` ({measured['os']})",
        kind,
        f"{_mb(measured['size'])} (base {_mb(measured['base_size'])})",
        f"{measured['packages']} (base {measured['base_packages']})",
        f"yes: {', '.join(tools)}" if tools else "no",
        measured["user"],
        pin,
        _severe(measured["severe"]),
        verdict,
    ]


def os_packages(root: Path, imgs: list[Image], data: dict) -> list[dict]:
    """One entry per OS package a Dockerfile installs, with its measured columns merged across images."""
    sites = call_sites(root, imgs)
    found: dict[str, dict] = {}
    for image in imgs:
        measured = current(image, data.get("images", {}).get(image.dockerfile, {}))
        for name in image.installs:
            entry = found.setdefault(
                f"{image.ecosystem}:{name}",
                {
                    "ecosystem": image.ecosystem,
                    "name": name,
                    "manifests": [],
                    "sites": sites[name],
                },
            )
            entry["manifests"].append(image.dockerfile)
            if (
                got := measured.get("installs", {}).get(name)
            ) and "fetched" not in entry:
                entry["version"], entry["transitive"] = (
                    got["version"],
                    got["transitive"],
                )
                entry["fetched"] = {
                    "version": got["version"],
                    "vulnerabilities": got["vulnerabilities"],
                    "latest": got["version"],
                    "released": got["released"],
                    "licence": got["licence"],
                }
    return [found[k] for k in sorted(found)]


def section(
    imgs: list[Image], data: dict, table: Callable[[list[list[str]]], list[str]]
) -> list[str]:
    if not imgs:
        return []
    reviews = data.get("images", {})
    rows = [row(image, reviews.get(image.dockerfile, {})) for image in imgs]
    return ["", "## Images", "", *table([HEADER, *rows])]
