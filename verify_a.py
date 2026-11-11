"""How many of the encoding-skipped files does each recovery flag bring back? (-U vs -a), from each repo root."""
import os
import subprocess
import sys
from pathlib import Path

EXE = os.environ["CLAUDE_CODE_EXECPATH"]
SHIM = ["-G", "--ignore-files", "--hidden", "-I", "--exclude-dir=.git", "--exclude-dir=.svn",
        "--exclude-dir=.hg", "--exclude-dir=.bzr", "--exclude-dir=.jj", "--exclude-dir=.sl"]


def listing(tree, flags):
    r = subprocess.run(["ugrep", *flags, "-r", "-l", "", "."], executable=EXE, cwd=tree, capture_output=True)
    return {os.path.normpath(p) for p in r.stdout.decode("utf-8", "surrogateescape").splitlines() if p}


tot = {"skipped": 0, "-U": 0, "-a": 0}
for repo in sorted(Path(sys.argv[1]).iterdir()):
    tree = next(repo.iterdir())
    shim, u, a = listing(tree, SHIM), listing(tree, SHIM + ["-U"]), listing(tree, SHIM + ["-a"])
    for dirpath, _, filenames in os.walk(tree):
        for fn in filenames:
            p = Path(dirpath, fn)
            if p.is_symlink() or not p.is_file():
                continue
            data = p.read_bytes()
            rel = os.path.normpath(os.path.relpath(p, tree))
            if not data or rel in shim or b"\x00" in data:
                continue
            try:
                data.decode("utf-8")
                continue
            except UnicodeDecodeError:
                pass
            tot["skipped"] += 1
            tot["-U"] += rel in u
            tot["-a"] += rel in a
print(tot)
