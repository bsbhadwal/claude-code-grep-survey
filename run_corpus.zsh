#!/bin/zsh
# Build the nine-file corpus (with and without a repository marker) and search it with each tool.
# Run inside Claude Code's Bash tool to exercise its `grep`/`rg` shims, or set CLAUDE_CODE_EXECPATH yourself.
# GNU grep runs in a container if docker is available.
H=${0:A:h}
W=(-G --ignore-files --hidden -I --exclude-dir=.git --exclude-dir=.svn --exclude-dir=.hg --exclude-dir=.bzr --exclude-dir=.jj --exclude-dir=.sl)
P='needle_[a-z0-9_]*'
for variant in norepo repo; do
  D=$H/work/corpus_$variant
  if [[ $variant == repo ]]; then python3 $H/make_corpus.py $D --repo; else python3 $H/make_corpus.py $D; fi
  cd $D
  echo "===== $variant"
  if [[ -x ${CLAUDE_CODE_EXECPATH:-} ]]; then
    echo "-- Claude Code grep shim (ugrep with the shim's flags)"; ARGV0=ugrep $CLAUDE_CODE_EXECPATH $W -rno $P . | sort
    echo "-- Claude Code bundled rg"; ARGV0=rg $CLAUDE_CODE_EXECPATH -no $P . | sort
  fi
  echo "-- system grep: $(command grep --version | head -1)"; command grep -rno $P . 2>&1 | sort
  if command -v docker >/dev/null && docker ps >/dev/null 2>&1; then
    echo "-- GNU grep (debian:stable-slim)"
    docker run --rm --network none -v $D:/c:ro -w /c debian:stable-slim sh -c "grep --version | head -1; grep -rno '$P' . 2>&1 | sort"
  fi
done
