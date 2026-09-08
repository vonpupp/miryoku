# Brief — Rename keymap identity: manna-harbour_miryoku -> vonpupp_miryoku

Goal: the user's firmware builds as `xtips_v4s_103c_vonpupp_miryoku.bin`.
Rename the keymap/userspace ID in the fork; keep authorship attribution
(copyright headers, provenance URLs) untouched — those say "Manna Harbour"
on purpose (GPL credit), do NOT scrub them.

Work in ~/repos/miryoku_qmk, branch miryoku-LAYOUT_split_3x6_3_ex2
(tip c40db8589a, clean). Auth: `env -u GITHUB_TOKEN ...` for gh/push; git
writes need the Bash sandbox disabled.

## Changes (two commits)

Commit 1 (code, NO [miryoku-github] prefix):
1. `git mv users/manna-harbour_miryoku users/vonpupp_miryoku`
2. Inside it: `git mv manna-harbour_miryoku.c vonpupp_miryoku.c` and
   `manna-harbour_miryoku.h vonpupp_miryoku.h`; update all internal
   references: `#include "manna-harbour_miryoku.h"` in the .c,
   `INTROSPECTION_KEYMAP_C = manna-harbour_miryoku.c` and the
   `include users/manna-harbour_miryoku/...` paths in rules.mk
   (config.h includes?), any `-I`/path strings. Keep license/copyright
   headers byte-identical.
3. `git mv layouts/community/split_3x6_3_ex2/manna-harbour_miryoku
   layouts/community/split_3x6_3_ex2/vonpupp_miryoku` (only OUR shim dir;
   the 11 stock community shims stay untouched).
4. Update textual references to the old userspace path/name in:
   `miryoku-split_3x6-3-ex2-branch-notes.md` (repo root) and
   `keyboards/xtips/v4s/103c/readme.md` if it names the keymap.
5. Grep gate: `grep -rn "manna-harbour_miryoku" --include='*' .` must return
   ONLY hits inside users/ file HEADERS (copyright comment URLs like
   github.com/manna-harbour/miryoku are fine to keep — they are provenance,
   not the keymap id; distinguish carefully: the string
   `manna-harbour_miryoku` (underscore) should be GONE from all functional
   paths/includes; `manna-harbour/miryoku` (slash, URL) may remain in
   comments) plus the stock community shim dirs (leave those).
   Commit: `Rename keymap to vonpupp_miryoku`

Commit 2 (.github, [miryoku-github] prefix):
6. `.github/workflows/main.yml`: `-km manna-harbour_miryoku` ->
   `-km vonpupp_miryoku`; `user='users/manna-harbour_miryoku'` ->
   vonpupp; the copy glob `cp *manna-harbour_miryoku*` ->
   `cp *vonpupp_miryoku*`. Nothing else.
   Commit: `[miryoku-github] Build vonpupp_miryoku keymap`

Push both.

## Build + verify

7. Dispatch Build Inputs (keyboard=xtips/v4s/103c, no merge), poll <=20 min.
8. Green: download THIS run's artifact by id. EXPECT the firmware file named
   `xtips_v4s_103c_vonpupp_miryoku.bin`. sha256 vs
   6275d4d9486dfc377167cb962a9d30af39653b54371d830acb0e955eda30208c —
   report whether identical or different (either is plausible; name does not
   necessarily change bytes). Copy the new .bin to
   ~/repos/miryoku/tmp/firmware-final/ and DELETE the old-named
   xtips_v4s_103c_manna-harbour_miryoku.bin there.
9. Failure: full --log-failed capture, report BLOCKED.

## Report

Append to ~/repos/miryoku/docs/superpowers/plans/rename-report.md.
Return ONLY: status, two commit shas, run URL, artifact filename + sha256,
one-line summary, concerns. No subagents; flash nothing.
