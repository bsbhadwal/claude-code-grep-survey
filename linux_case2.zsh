#!/bin/zsh
L=$(ls -d ${0:A:h}/work/repos/torvalds__linux/*)
W=(-G --ignore-files --hidden -I --exclude-dir=.git --exclude-dir=.svn --exclude-dir=.hg --exclude-dir=.bzr --exclude-dir=.jj --exclude-dir=.sl)
echo "== negation / perf lines in tools/perf ignore file:"
/usr/bin/grep -n -E '^!|perf' "$L/tools/perf/.gitignore" | head -20
for start in "$L" "$L/tools" "$L/tools/perf"; do
  echo "== wrapper from ${start#$L}/ :"
  (cd "$start" && ARGV0=ugrep "$CLAUDE_CODE_EXECPATH" $W -rln 'struct perf_dlfilter_fns {' . ; echo "exit=$?")
done
echo "== /usr/bin/grep from repo root:"
(cd "$L" && /usr/bin/grep -rln 'struct perf_dlfilter_fns {' tools ; echo "exit=$?")
