"""Download default-branch source tarballs of public projects (no git, nothing executed) and extract them."""
import json
import sys
import tarfile
import urllib.request
from pathlib import Path

dest = Path(sys.argv[1])
dest.mkdir(parents=True, exist_ok=True)
REPOS = [
    "git/git", "python/cpython", "vim/vim", "postgres/postgres", "curl/curl", "openssl/openssl",
    "php/php-src", "Perl/perl5", "emacs-mirror/emacs", "torvalds/linux", "ruby/ruby", "nodejs/node",
]
UA = {"User-Agent": "encoding-survey/1.0"}


def default_branch(repo):
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["default_branch"]


for repo in REPOS:
    out = dest / repo.replace("/", "__")
    if out.exists():
        print("have", repo)
        continue
    try:
        br = default_branch(repo)
        url = f"https://codeload.github.com/{repo}/tar.gz/refs/heads/{br}"
        tgz = dest / (out.name + ".tar.gz")
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=600) as r, open(tgz, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
        out.mkdir()
        with tarfile.open(tgz) as t:
            t.extractall(out, filter="data")  # 'data' filter: no absolute paths, links outside, devices
        tgz.unlink()
        print("ok", repo, br, flush=True)
    except Exception as exc:
        print("FAIL", repo, exc, flush=True)
