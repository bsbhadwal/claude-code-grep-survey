# claude-code-grep-survey

Measurements behind the post [Claude Code's grep is not grep, and it fails silently](https://bsbhadwal.com/posts/claude-code-grep-is-not-grep/).

On native macOS and Linux builds of Claude Code (since 2.1.117), the Bash tool's `grep` is a shell function that runs a
bundled ugrep as `ugrep -G --ignore-files --hidden -I --exclude-dir=.git ...`. This repository measures what that
skips compared with GNU grep, BSD grep and ripgrep.

## Results (measured 2026-11-11)

Environment: Claude Code 2.1.322 (bundled ugrep 7.8.4), Apple Silicon macOS; GNU grep 3.11 (debian:stable-slim);
BSD grep 2.6.0 (macOS); upstream ugrep 7.8.5 (debian:testing-slim).

**Nine-file corpus** (`run_corpus.zsh`): the shim silently misses 6 of 9 planted matches (Latin-1 byte, Windows-1252
quotes, one invalid byte 200 KB from the match, a NUL byte, a gitignored directory, a gitignored glob). GNU grep's
only silent miss is UTF-16.

**Twelve source trees** (`fetch_repos.py`, then `survey.py`; default branches on 2026-11-11): searching from each root
with the shim's flags skips 680 of 242,379 text files for invalid UTF-8 (284 with source-like extensions) and 58
tracked files because of ignore rules. Every skipped file was re-checked against a listing with the recovering flag
added (`verify_paths.py`, `verify_a.py`). Per-repository counts and examples: `survey-results-2026-11-11.json`.

**Nested negation** (`min_repro.zsh`, `linux_case2.zsh`): with `perf` then `!include/perf/` in a nested `.gitignore`,
ugrep `--ignore-files` drops the re-included directory when the search starts above it. git agrees the file is not
ignored. In the Linux kernel this hides `tools/perf/include/perf/perf_dlfilter.h` from a root search while three
other files are returned with exit 0. Reproduces in upstream ugrep 7.8.5.

**Workarounds** (tested): `grep -a` recovers all 680 encoding skips (`-U` recovers 679; a Shift-JIS file ending in a
truncated multibyte character stays hidden). `grep -a --no-ignore-files` finds all 9 corpus matches.

**Correction (2026-11-11):** the first version said 60 ignore-rule skips and recommended `-U`. Two of the 60 were
BOM-only files that an empty pattern cannot match. `survey-results-2026-11-11.json` is the raw first-pass output and
still counts them.

## Run it

```sh
zsh run_corpus.zsh                       # inside Claude Code's Bash tool, or with CLAUDE_CODE_EXECPATH set
zsh min_repro.zsh
python3 fetch_repos.py work/repos        # downloads ~1.5 GB of source tarballs over HTTPS; nothing is executed
CLAUDE_CODE_EXECPATH=... python3 survey.py work/repos work/survey.json
zsh linux_case2.zsh                      # after fetch_repos.py
```

`CLAUDE_CODE_EXECPATH` is the Claude Code binary (inside its Bash tool it is already set). The scripts invoke its
bundled ugrep the same way the shim does (`argv[0]` = `ugrep`).

## Related reports

- anthropics/claude-code: #56644 (NUL bytes), #84161 (silent .gitignore), #102875 (ignore semantics differ from git),
  #69736 (opt-out for the shims), #101399 (`^` alternatives).
- New reports filed with this survey are linked from the post.

## License

MIT
