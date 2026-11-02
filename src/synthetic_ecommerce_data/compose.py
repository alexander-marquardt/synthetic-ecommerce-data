"""Compose the domains' builds into ONE catalog (gen#125, slice 4 of the 2026-10-28 ruling).

    ecom-generate compose --domain industrial=out/industrial --domain retail=out/retail \\
        --out out/catalog

The generator owns the combined catalog: a release ships one catalog asset and one pin, beside
the one image pin of gen#706, so the catalogue repository reads one input built at one commit.
Each ``--domain`` names a domain's finished build, a directory holding its ``nested.jsonl`` and
``flat.jsonl`` (``ecom-generate build --out`` writes both; the retail build writes them with
``scale --out`` and ``--flat``). Compose writes, into ``--out``:

``catalog.ndjson``
    every domain's ``flat.jsonl``, byte for byte, in the order the domains are given: each
    domain keeps its own flat projection (industrial's ``emit.flat_documents``, retail's
    ``standard.flat_documents``), so a domain's documents are the same in the catalog as in its
    own build.
``provenance.json``
    where each domain's lines sit (``first_line``, counted from 1), its ``documents`` (flat
    lines, one per SKU), its ``products`` (nested documents) and the sha256 of its flat bytes;
    the whole file's line count and sha256 beside them.

Before anything is written, compose refuses (exit 1, ``--out`` untouched):

- a ``--domain`` that is not ``<domain>=<build directory>``, an unknown domain (:data:`DOMAINS`),
  or one named twice;
- a domain whose flat and nested files are not one build: their SKUs differ;
- a union the output standard refuses: :func:`.core.standard.check_catalog` over every domain's
  nested documents TOGETHER. A domain's own build checks its own documents; only the union can
  show a ``sku`` or ``product_id`` two domains share, or a key two domains name differently.
  Each domain's text-match decoys stay exempt by id, as in its own check. The check runs without
  ``one_class_per_key``: the industrial build does not meet it on its own (gen#286).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from synthetic_ecommerce_data.core import standard

CATALOG = "catalog.ndjson"
PROVENANCE = "provenance.json"
NESTED = "nested.jsonl"
FLAT = "flat.jsonl"
#: How many of a refused union's problems are printed; the count is always printed.
SHOWN_PROBLEMS = 20


def _industrial_exempt(docs: Iterable[Mapping[str, Any]]) -> frozenset[str]:
    from synthetic_ecommerce_data.domains.industrial import hammers  # noqa: PLC0415

    return hammers.decoy_ids(docs)


def _retail_exempt(docs: Iterable[Mapping[str, Any]]) -> frozenset[str]:
    from synthetic_ecommerce_data.domains.retail import scale  # noqa: PLC0415

    return scale.TEXT_EXEMPT


#: Each domain compose takes, and the ids of its text-match decoys (exempt from the text check,
#: as the domain's own check exempts them). A new domain is a row here.
DOMAINS: dict[str, Callable[[Iterable[Mapping[str, Any]]], frozenset[str]]] = {
    "industrial": _industrial_exempt,
    "retail": _retail_exempt,
}


class ComposeError(Exception):
    """A refused composition: its message says why, and nothing was written."""


@dataclass(frozen=True)
class Build:
    """One domain's finished build: its nested documents and its flat file's bytes."""

    domain: str
    nested: list[dict[str, Any]]
    flat: bytes


def parse_domains(given: list[str]) -> list[tuple[str, Path]]:
    """The ``--domain`` values as ``(domain, directory)``, in order, each known and once."""
    out: list[tuple[str, Path]] = []
    for value in given:
        name, sep, directory = value.partition("=")
        if not sep or not name or not directory:
            raise ComposeError(f"{value!r} is not <domain>=<build directory>")
        if name not in DOMAINS:
            raise ComposeError(f"unknown domain {name!r} (known: {', '.join(DOMAINS)})")
        if name in (n for n, _ in out):
            raise ComposeError(f"domain {name!r} is named twice")
        out.append((name, Path(directory)))
    if not out:
        raise ComposeError("no --domain given")
    return out


def read_build(domain: str, directory: Path) -> Build:
    """A domain's build, refused unless its flat file holds exactly its nested file's SKUs."""
    for name in (NESTED, FLAT):
        if not (directory / name).is_file():
            raise ComposeError(f"{domain}: no {name} in {directory}")
    nested = [json.loads(line) for line in (directory / NESTED).read_text("utf-8").splitlines()]
    flat = (directory / FLAT).read_bytes()
    if flat and not flat.endswith(b"\n"):
        raise ComposeError(f"{domain}: {FLAT} does not end in a newline")
    flat_skus = Counter(json.loads(line)["sku"] for line in flat.splitlines())
    nested_skus = Counter(v["sku"] for doc in nested for v in doc["variants"])
    if flat_skus != nested_skus:
        only_flat = sorted((flat_skus - nested_skus).elements())
        only_nested = sorted((nested_skus - flat_skus).elements())
        raise ComposeError(
            f"{domain}: {FLAT} and {NESTED} are not one build: {len(only_flat)} SKUs only in "
            f"{FLAT} {only_flat[:5]}, {len(only_nested)} only in {NESTED} {only_nested[:5]}"
        )
    return Build(domain, nested, flat)


def union_problems(builds: list[Build]) -> list[str]:
    """Every way the union of the builds' nested documents breaks the output standard."""
    docs = [doc for build in builds for doc in build.nested]
    exempt = frozenset().union(*(DOMAINS[b.domain](b.nested) for b in builds))
    return standard.check_catalog(docs, text_exempt=exempt)


def provenance(builds: list[Build]) -> dict[str, Any]:
    """Where each domain's lines sit in the composed catalog, and each part's digest."""
    rows: list[dict[str, Any]] = []
    line = 1
    for build in builds:
        documents = build.flat.count(b"\n")
        rows.append(
            {
                "domain": build.domain,
                "first_line": line,
                "documents": documents,
                "products": len(build.nested),
                "content_sha256": hashlib.sha256(build.flat).hexdigest(),
            }
        )
        line += documents
    whole = b"".join(build.flat for build in builds)
    return {
        "catalog": CATALOG,
        "documents": line - 1,
        "content_sha256": hashlib.sha256(whole).hexdigest(),
        "domains": rows,
    }


def compose(given: list[str], out: Path) -> dict[str, Any]:
    """Check the named builds and write the composed catalog and its provenance into ``out``.

    Raises :class:`ComposeError`, with nothing written, on any refusal."""
    builds = [read_build(domain, directory) for domain, directory in parse_domains(given)]
    problems = union_problems(builds)
    if problems:
        shown = "\n".join(problems[:SHOWN_PROBLEMS])
        names = ", ".join(b.domain for b in builds)
        raise ComposeError(f"{len(problems)} problems in the union of {names}:\n{shown}")
    record = provenance(builds)
    out.mkdir(parents=True, exist_ok=True)
    (out / CATALOG).write_bytes(b"".join(build.flat for build in builds))
    (out / PROVENANCE).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ecom-generate compose", description=__doc__)
    parser.add_argument(
        "--domain",
        action="append",
        default=[],
        help="<domain>=<build directory holding nested.jsonl and flat.jsonl>; repeat, in order",
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        record = compose(args.domain, args.out)
    except ComposeError as error:
        print(f"compose REFUSED: {error}", file=sys.stderr)
        return 1
    parts = ", ".join(
        f"{row['domain']} {row['documents']} from line {row['first_line']}"
        for row in record["domains"]
    )
    print(f"{args.out / CATALOG}  {record['documents']} documents ({parts})")
    print(f"content sha256 {record['content_sha256']}")
    return 0
