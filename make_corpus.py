import os
import sys
from pathlib import Path

root = Path(sys.argv[1])
fake_git = len(sys.argv) > 2 and sys.argv[2] == "--repo"
if root.exists():
    import shutil
    shutil.rmtree(root)
root.mkdir(parents=True)
if fake_git:
    (root / ".git").mkdir()  # marks a repository root for tools that require one (no git binary invoked)
    (root / ".git" / "HEAD").write_text("ref: refs/heads/main\n")

files = {
    "utf8.c": "int needle_utf8 = 1;\n".encode(),
    "latin1.c": b"/* auteur: Ren\xe9 */\nint needle_latin1 = 1;\n",
    "cp1252.txt": b"\x93quoted\x94 needle_cp1252\n",
    "late_invalid.txt": ("ok line\n" * 25000).encode() + b"caf\xe9\nneedle_late\n",
    "utf16.txt": "﻿needle_utf16\n".encode("utf-16-le"),
    "nul.txt": b"needle_nul\n\x00\nmore\n",
    ".hidden.c": b"int needle_hidden = 1;\n",
    "generated/out.c": b"int needle_gitignored_dir = 1;\n",
    "app.log": b"needle_gitignored_glob\n",
}
for name, data in files.items():
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
(root / ".gitignore").write_text("generated/\n*.log\n")
print("corpus at", root, "repo-marker" if fake_git else "no-repo")
