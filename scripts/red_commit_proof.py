"""CI proves each declared red commit is red on an assertion (elastic/prism#11680).

    python3 scripts/red_commit_proof.py --range <base>..<head>     # a pull request's commits

Stub: accepts every range. The proof follows in the next commit.
"""

from __future__ import annotations

import sys


def declared_tests(values: list[str]) -> list[str]:
    return list(values)


def main(argv: list[str] | None = None) -> int:
    return 0


if __name__ == "__main__":
    sys.exit(main())
