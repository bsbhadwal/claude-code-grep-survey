"""Path-level check for every skipped file: absent from the shim's listing AND present in the recovery listing."""
import collections
import os
import subprocess
import sys
from pathlib import Path

EXE = os.environ["CLAUDE_CODE_EXECPATH"]
SHIM = ["-G", "--ignore-files", "--hidden", "-I", "--exclude-dir=.git", "--exclude-dir=.svn",
        "--exclude-dir=.hg", "--exclude-dir=.bzr", "--exclude-dir=.jj", "--exclude-dir=.sl"]
ENC_RECOVER = SHIM + ["-U"]
IGN_RECOVER = [f for f in SHIM if f != "--ignore-files"] + ["-U"]


def listing(tree, flags):
    r = subprocess.run(["ugrep", *flags, "-r", "-l", "", "."], executable=EXE, cwd=tree, capture_output=True)
    return {os.path.normpath(p) for p in r.stdout.decode("utf-8", "surrogateescape").splitlines() if p}


def classify(data):
    if b"\x00" in data:
        return "nul"
    try:
        data.decode("utf-8")
        return "utf8"
    except UnicodeDecodeError:
        return "non_utf8"


tally = collections.Counter()
for repo in sorted(Path(sys.argv[1]).iterdir()):
    tree = next(repo.iterdir())
    shim, enc_rec, ign_rec = listing(tree, SHIM), listing(tree, ENC_RECOVER), listing(tree, IGN_RECOVER)
    for dirpath, _, filenames in os.walk(tree):
        for fn in filenames:
            p = Path(dirpath, fn)
            if p.is_symlink() or not p.is_file():
                continue
            data = p.read_bytes()
            rel = os.path.normpath(os.path.relpath(p, tree))
            if not data or rel in shim:
                continue
            kind = classify(data)
            if kind == "non_utf8":
                ok = rel in enc_rec or rel in ign_rec; tally[("encoding", "CONFIRMED" if ok else "UNEXPLAINED")] += 1
                if not ok: print("  UNEXPLAINED encoding", repo.name, rel, len(data), data[:40])
            elif kind == "utf8":
                ok = rel in ign_rec
                tally[("ignore", "CONFIRMED" if ok else "UNEXPLAINED")] += 1
                if not ok:
                    print("  UNEXPLAINED ignore", repo.name, rel)
for k, n in sorted(tally.items()):
    print(k, n)
