#!/bin/zsh
# Minimal reproduction: a nested ignore file with a negation is honoured only when the search starts in its directory.
R=${0:A:h}/work/min_repro
rm -rf $R; mkdir -p $R/sub/include/perf
printf 'perf\n!include/perf/\n' > $R/sub/.gitignore
echo 'needle' > $R/sub/include/perf/api.h
echo 'needle' > $R/sub/other.c
U=(ARGV0=ugrep)
echo "== bundled ugrep: $(ARGV0=ugrep $CLAUDE_CODE_EXECPATH --version | head -1)"
echo "-- from root:";  (cd $R && ARGV0=ugrep $CLAUDE_CODE_EXECPATH --ignore-files -rl needle . | sort)
echo "-- from sub/:";  (cd $R/sub && ARGV0=ugrep $CLAUDE_CODE_EXECPATH --ignore-files -rl needle . | sort)
echo "-- /usr/bin/grep from root (no ignore support, reference):"; (cd $R && /usr/bin/grep -rl needle . | sort)
echo "== ugrep -I description:"
ARGV0=ugrep $CLAUDE_CODE_EXECPATH --help 2>&1 | /usr/bin/grep -A3 -E '^ *-I, ' | head -6
