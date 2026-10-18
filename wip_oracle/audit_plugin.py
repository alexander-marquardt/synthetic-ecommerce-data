"""Records every repo file a test session opens or imports (one-off oracle for ci_select)."""
import json
import os
import sys

ROOT = os.path.realpath(os.environ["AUDIT_ROOT"])
OUT = os.environ["AUDIT_OUT"]
opened: set[str] = set()


def _hook(event, args):
    if event == "open":
        path = args[0]
        if isinstance(path, (str, bytes, os.PathLike)):
            try:
                p = os.path.realpath(os.fsdecode(path))
            except Exception:
                return
            if p.startswith(ROOT + "/") and "/.venv/" not in p and "/.agent/" not in p and "/.git/" not in p:
                opened.add(os.path.relpath(p, ROOT))


sys.addaudithook(_hook)


def pytest_sessionfinish(session, exitstatus):
    files = sorted({os.path.relpath(os.path.realpath(m.__file__), ROOT)
                    for m in list(sys.modules.values())
                    if getattr(m, "__file__", None)
                    and os.path.realpath(m.__file__).startswith(ROOT + "/")
                    and "/.venv/" not in m.__file__})
    names = sorted({str(i.fspath) for i in session.items})
    with open(OUT, "a") as f:
        f.write(json.dumps({"tests": [os.path.relpath(n, ROOT) for n in names],
                            "imported": files, "opened": sorted(opened)}) + "\n")
