"""Measure which files Claude Code's shell `grep` (bundled ugrep, wrapper flags) silently skips in real source trees."""
import collections
import json
import os
import subprocess
import sys
from pathlib import Path

EXE = os.environ["CLAUDE_CODE_EXECPATH"]
WRAPPER_FLAGS = ["-G", "--ignore-files", "--hidden", "-I", "--exclude-dir=.git", "--exclude-dir=.svn",
                 "--exclude-dir=.hg", "--exclude-dir=.bzr", "--exclude-dir=.jj", "--exclude-dir=.sl"]
TEXT_EXT = {".c", ".h", ".cc", ".cpp", ".py", ".rb", ".pl", ".pm", ".t", ".php", ".js", ".mjs", ".ts", ".java",
            ".el", ".vim", ".sh", ".txt", ".md", ".rst", ".po", ".html", ".xml", ".json", ".yml", ".yaml",
            ".sql", ".in", ".pod", ".tex", ".texi", ".1", ".3", ".8", ".s", ".S", ".rs", ".go", ".m4", ".cfg"}


def searched_by_wrapper(tree: Path) -> set[str]:
    r = subprocess.run(["ugrep", *WRAPPER_FLAGS, "-r", "-l", "", "."], executable=EXE, cwd=tree,
                       capture_output=True, check=False)
    return {os.path.normpath(p) for p in r.stdout.decode("utf-8", "surrogateescape").splitlines() if p}


def classify(data: bytes) -> str:
    if b"\x00" in data:
        return "nul"
    try:
        data.decode("utf-8")
        return "utf8"
    except UnicodeDecodeError:
        return "non_utf8"


def survey(tree: Path):
    searched = searched_by_wrapper(tree)
    counts = collections.Counter()
    examples = collections.defaultdict(list)
    ext_counts = collections.Counter()
    for dirpath, dirnames, filenames in os.walk(tree):
        dirnames[:] = [d for d in dirnames if d not in {".git", ".svn", ".hg"}]
        for fn in filenames:
            p = Path(dirpath, fn)
            if p.is_symlink() or not p.is_file():
                continue
            data = p.read_bytes()
            if not data:
                continue
            rel = os.path.normpath(os.path.relpath(p, tree))
            kind = classify(data)
            counts[f"all_{kind}"] += 1
            if rel in searched:
                counts["searched"] += 1
                if kind == "non_utf8":
                    counts["non_utf8_but_searched"] += 1
                continue
            counts[f"skipped_{kind}"] += 1
            if kind == "non_utf8":
                ext_counts[p.suffix or "(none)"] += 1
                if p.suffix in TEXT_EXT:
                    counts["skipped_non_utf8_source_ext"] += 1
            if len(examples[kind]) < 4:
                examples[kind].append(rel)
    return counts, examples, ext_counts


root = Path(sys.argv[1])
results = {}
for tree in sorted(root.iterdir()):
    if not tree.is_dir():
        continue
    inner = next(tree.iterdir())  # tarball top-level dir
    counts, examples, exts = survey(inner)
    results[tree.name] = {"counts": counts, "examples": examples, "exts": exts.most_common(6)}
    c = counts
    total_text = c["all_utf8"] + c["all_non_utf8"]
    print(f"{tree.name:<26} text files {total_text:>6} | non-UTF-8 text skipped {c['skipped_non_utf8']:>4} "
          f"(source-like ext {c['skipped_non_utf8_source_ext']:>4}) | UTF-8 skipped (ignore rules) {c['skipped_utf8']:>4} "
          f"| non-UTF-8 searched anyway {c['non_utf8_but_searched']:>3}", flush=True)
(Path(sys.argv[2])).write_text(json.dumps(results, indent=1, default=dict))
