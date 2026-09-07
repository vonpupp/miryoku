# Miryoku on `LAYOUT_split_3x6_3_ex2` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run stock, unmodified Miryoku (QMK) on a 46-key Corne V4 clone (`crkbd/rev4_0/standard`, `LAYOUT_split_3x6_3_ex2`), built with Miryoku's own fork + GitHub Actions workflow method, with the 4 extra keys inert.

**Architecture:** Add a `split_3x6_3_ex2` subset-mapping shim (community-layout pattern) to a fork of `manna-harbour/miryoku_qmk`, register it in `crkbd/rev4_0/info.json`, and build via manna-harbour's unmodified reusable workflow (`main.yml`) with the `merge` option pulling `qmk/qmk_firmware/master` (the fork's `miryoku` branch predates `crkbd/rev4_0`). A zero-code baseline build runs first to prove the pipeline on the hardware.

**Tech Stack:** GitHub (fork, Actions workflows, artifacts), git, QMK build system (community layouts / `locate_keymap.mk`), RP2040 UF2 flashing.

**Spec:** `docs/superpowers/specs/2026-09-07-miryoku-split-3x6-3-ex2-design.md` — the spec travels with this plan; executors read both.

## Global Constraints

- Branch name in every repo: `miryoku-LAYOUT_split_3x6_3_ex2`. Fork lives under the GitHub account `vonpupp`.
- Keyboard target is always `crkbd/rev4_0/standard`; merge source is always `qmk/qmk_firmware/master`.
- No edits to `miryoku_babel`, no edits to `.github/workflows/main.yml` or `build-inputs.yml`, no layer customizations, no options overrides (stock `default` alphas/nav/clipboard/layers).
- The 4 extra keys map to `XXX` (`KC_NO`) — inert, by design (spec §2, §6).
- Commits touching `.github/**` are prefixed `[miryoku-github]` (canonical prefix; the build's merge step reverts such commits before merging QMK master). **All other commits MUST NOT use that prefix** — they must survive the merge.
- Local working set: this docs repo at `/home/av/repos/miryoku`, babel clone at `/home/av/repos/miryoku/miryoku_babel` (already done), QMK fork clone at `/home/av/repos/miryoku_qmk` (sibling).
- Hardware acceptance gates: if the board never shows an `RPI-RP2` USB drive in BOOTSEL mode, STOP — that is spec §8 contingency C (custom keyboard def) and is out of this plan's scope.

---

### Task 1: Prerequisites — gh auth + hardware pre-flight

**Files:** none (verification only).

**Interfaces:**
- Consumes: nothing.
- Produces: working `gh` CLI; confirmed RP2040 bootloader on both halves (gates all later tasks).

- [ ] **Step 1: Fix gh authentication (user action if interactive login is needed)**

The token in `GITHUB_TOKEN` is invalid. In this session the user can run `! gh auth login` (or outside: `gh auth login`, then `unset GITHUB_TOKEN` in the shell profile if it shadows the keyring). Then verify:

Run: `gh auth status`
Expected: `Logged in to github.com account vonpupp` with a valid token, no failure lines.

- [ ] **Step 2: Hardware pre-flight — RP2040 check (user action, gates everything)**

Unplug the keyboard. Hold the BOOTSEL button (or short the RESET/BOOT pads per the board's silkscreen) on the **left/primary half**, plug in USB, release. A USB mass-storage drive named `RPI-RP2` must appear. Eject it, repeat for the **right half** (plug its USB-C directly, or use the TRRS-connected procedure per the vendor's guide).

Expected: `RPI-RP2` appears for both halves. If either half never shows it → STOP, escalate to spec §8 contingency C.

- [ ] **Step 3: Record results**

Note gh status OK and RPI-RP2 observed on both halves in the session log / plan checkboxes. No commit.

---

### Task 2: Fork `miryoku_qmk`, clone, create the branch

**Files:**
- Create: local clone at `/home/av/repos/miryoku_qmk` (from `vonpupp/miryoku_qmk`, branch `miryoku`, depth 1)
- Create (on GitHub): branch `miryoku-LAYOUT_split_3x6_3_ex2` in `vonpupp/miryoku_qmk`

**Interfaces:**
- Consumes: working `gh` (Task 1).
- Produces: remote branch `vonpupp/miryoku_qmk/miryoku-LAYOUT_split_3x6_3_ex2` at the same commit as `miryoku`; local clone with that branch checked out; Actions enabled on the fork. All later tasks push here.

- [ ] **Step 1: Fork**

Run: `gh repo fork manna-harbour/miryoku_qmk --clone=false`
Expected: `Created fork vonpupp/miryoku_qmk` (or "already exists"). Wait ~30s for the fork to finish copying.

- [ ] **Step 2: Enable Actions on the fork**

Run:
```bash
gh api -X PUT repos/vonpupp/miryoku_qmk/actions/permissions -F enabled=true -F allowed_actions=all
```
Expected: HTTP 204 (empty success). Fallback: web UI → fork → Actions tab → "I understand my workflows, go ahead and enable them".

- [ ] **Step 3: Clone (shallow) and branch**

```bash
cd /home/av/repos
git clone --depth 1 -b miryoku git@github.com:vonpupp/miryoku_qmk.git
cd miryoku_qmk
git checkout -b miryoku-LAYOUT_split_3x6_3_ex2
git push -u origin miryoku-LAYOUT_split_3x6_3_ex2
```
(A push of a branch pointing at the fork's existing `miryoku` HEAD transfers no objects; shallow is fine. If SSH auth fails, use the HTTPS remote `https://github.com/vonpupp/miryoku_qmk.git`.)

- [ ] **Step 4: Verify**

Run: `gh api repos/vonpupp/miryoku_qmk/branches/miryoku-LAYOUT_split_3x6_3_ex2 --jq .name`
Expected: `miryoku-LAYOUT_split_3x6_3_ex2`

---

### Task 3: Baseline build — spec Step 0, zero code changes

**Files:** none created or modified. Runs the stock `Build Inputs` workflow.

**Interfaces:**
- Consumes: fork with Actions enabled (Task 2).
- Produces: proof that checkout → revert `[miryoku-github]` → merge QMK master → `qmk compile` → artifact all work for `crkbd/rev4_0/standard`; a flashable baseline UF2 in `$TMPDIR/miryoku-baseline/`.

- [ ] **Step 1: Dispatch the Build Inputs workflow**

```bash
gh workflow run 'Build Inputs' \
  --ref miryoku-LAYOUT_split_3x6_3_ex2 \
  --repo vonpupp/miryoku_qmk \
  -f keyboard=crkbd/rev4_0/standard \
  -f merge=qmk/qmk_firmware/master
```
Expected: `✓ Created workflow_dispatch event for Build Inputs`. (First run on a fork may need ~1 min before it appears.)

- [ ] **Step 2: Watch it to completion**

Run: `gh run watch --repo vonpupp/miryoku_qmk` (or `gh run list --repo vonpupp/miryoku_qmk --limit 1` then `gh run watch <id> --repo vonpupp/miryoku_qmk`)
Expected: the `Build Inputs` run reaches **success**. The log's *Merge branches* step must show `git merge qmk-qmk_firmware/master` completing and *Build* must show `qmk compile` producing firmware. On failure: read `gh run view <id> --log-failed --repo vonpupp/miryoku_qmk`; a merge conflict means QMK master diverged on a file the `miryoku` branch touches — report back before proceeding.

- [ ] **Step 3: Download the artifact**

```bash
mkdir -p "$TMPDIR/miryoku-baseline"
gh run download --repo vonpupp/miryoku_qmk --dir "$TMPDIR/miryoku-baseline"
ls "$TMPDIR/miryoku-baseline"
```
Expected: a directory containing at least `crkbd_rev4_0_standard_manna-harbour_miryoku.uf2` (plus hex files and the copied `custom_rules.mk`/`custom_config.h`).

---

### Task 4: Flash baseline + hardware smoke test (user)

**Files:** none.

**Interfaces:**
- Consumes: baseline UF2 (Task 3); RP2040 bootloader confirmed (Task 1).
- Produces: confirmed end-to-end pipeline on the real hardware. Gates Tasks 5–8.

- [ ] **Step 1: Flash both halves**

For each half: BOOTSEL-plug (drive `RPI-RP2` appears), copy the **same** UF2 onto the drive, wait for it to auto-eject and reboot. Reconnect TRRS/USB as normal.

```bash
# per half, after its RPI-RP2 drive appears:
cp "$TMPDIR/miryoku-baseline"/*/crkbd_rev4_0_standard_manna-harbour_miryoku.uf2 /media/$USER/RPI-RP2/
```

- [ ] **Step 2: Smoke test**

Open a text editor. Expected: Colemak Mod-DH output from the inner 5 columns per hand (left home row `ARSTG`), thumbs produce Space/Tab/Esc and Enter/Bspc/Del, layer-holds work (hold inner-left thumb + right hand moves cursor). The outer columns and the 4 inner extras are expected to be **dead** at this stage (baseline resolves via a stock 36/42-key shim) — that is fine; this build only proves the pipeline. Both halves must respond.

- [ ] **Step 3: Checkpoint**

If keys on the secondary half don't register, reseat TRRS and reflash both halves once. Still failing → stop and report (split-communication issue, spec §7).

---

### Task 5: Shim — `layouts/community/split_3x6_3_ex2/manna-harbour_miryoku/`

**Files:**
- Create: `/home/av/repos/miryoku_qmk/layouts/community/split_3x6_3_ex2/manna-harbour_miryoku/config.h`
- Create: `/home/av/repos/miryoku_qmk/layouts/community/split_3x6_3_ex2/manna-harbour_miryoku/keymap.c`

**Interfaces:**
- Consumes: `LAYOUT_split_3x6_3_ex2` macro declared by `crkbd/rev4_0/info.json` (46 args, order verified from the layout array: top 14 = left outer→inner then right inner→outer; home 14; bottom 12; thumbs 6 = `(x4,3.7)(x5,3.7)(x6,3.2)(x8,3.2)(x9,3.7)(x10,3.7)`).
- Produces: `LAYOUT_miryoku` (the virtual 10×4 keymap the userspace fills) expanding to the physical 46-key layout. Later tasks rely on this dir existing so `locate_keymap.mk` can resolve `manna-harbour_miryoku` for this layout.

- [ ] **Step 1: Create `keymap.c`** (license stub only — the keymap array itself comes from the userspace via `INTROSPECTION_KEYMAP_C`)

```c
// Copyright 2022 Manna Harbour
// https://github.com/manna-harbour/miryoku

// This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
```

- [ ] **Step 2: Create `config.h`** (the subset mapping; `XXX` = unused. Miryoku's 5 alpha columns land on the inner 5 columns per hand, exactly as the stock `split_3x6_3` shim; outer columns and the two LEFT inner extras are `XXX`; the two RIGHT inner extras are default-layer switches per Ruling 9: top = `DF(U_BASE)` → Colemak, home = `DF(U_EXTRA)` → QWERTY — keycodes already exist in the userspace layer enum and U_EXTRA defaults to QWERTY, so no build options are needed)

```c
// Copyright 2022 Manna Harbour
// https://github.com/manna-harbour/miryoku

// This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

#pragma once

#define XXX KC_NO

#define LAYOUT_miryoku( \
      K00,  K01,  K02,  K03,  K04,         K05,  K06,  K07,  K08,  K09, \
      K10,  K11,  K12,  K13,  K14,         K15,  K16,  K17,  K18,  K19, \
      K20,  K21,  K22,  K23,  K24,         K25,  K26,  K27,  K28,  K29, \
      N30,  N31,  K32,  K33,  K34,         K35,  K36,  K37,  N38,  N39 \
) \
LAYOUT_split_3x6_3_ex2( \
XXX,  K00,  K01,  K02,  K03,  K04,  XXX,   DF(U_BASE),  K05,  K06,  K07,  K08,  K09,  XXX, \
XXX,  K10,  K11,  K12,  K13,  K14,  XXX,   DF(U_EXTRA), K15,  K16,  K17,  K18,  K19,  XXX, \
XXX,  K20,  K21,  K22,  K23,  K24,         K25,  K26,  K27,  K28,  K29,  XXX, \
                  K32,  K33,  K34,         K35,  K36,  K37 \
)
```

Sanity check before committing: arg counts 14 + 14 + 12 + 6 = 46.

- [ ] **Step 3: Commit and push** (NOT `[miryoku-github]` — must survive merges)

```bash
cd /home/av/repos/miryoku_qmk
git add layouts/community/split_3x6_3_ex2/
git commit -m "Add split_3x6_3_ex2 subset mapping for manna-harbour_miryoku"
git push
```

---

### Task 6: Register the community layout

**Files:**
- Modify: `/home/av/repos/miryoku_qmk/keyboards/crkbd/rev4_0/info.json` — the `community_layouts` array.

**Interfaces:**
- Consumes: shim directory (Task 5).
- Produces: `LAYOUTS` (the keymap-search list QMK generates from `community_layouts`) containing exactly `split_3x6_3_ex2`, so the stock build command `qmk compile -kb crkbd/rev4_0/standard -km manna-harbour_miryoku` resolves to our shim with no `FORCE_LAYOUT` and no workflow edits (deliberate refinement of the spec's "FORCE_LAYOUT, plumbing TBD": with exactly one candidate, resolution is deterministic — if it fails, the build errors loudly with "Could not find keymap" instead of silently using another layout).

- [ ] **Step 1: Edit `keyboards/crkbd/rev4_0/info.json`**

Change (line 84 of the file, exact current formatting):

```json
    "community_layouts": [ "split_3x5_3", "split_3x6_3" ],
```

to:

```json
    "community_layouts": [ "split_3x6_3_ex2" ],
```

(Replaced rather than appended on purpose: append would leave `split_3x5_3` first in the search order and it would silently win. Keeping only our layout makes the fork's default resolution unambiguous. To build other mappings later, re-add entries and use `FORCE_LAYOUT`.)

- [ ] **Step 2: Validate JSON**

Run: `python3 -m json.tool /home/av/repos/miryoku_qmk/keyboards/crkbd/rev4_0/info.json > /dev/null && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit and push** (NOT `[miryoku-github]`)

```bash
cd /home/av/repos/miryoku_qmk
git add keyboards/crkbd/rev4_0/info.json
git commit -m "Register split_3x6_3_ex2 as crkbd rev4_0 community layout"
git push
```

---

### Task 7: One-click build workflow + build

**Files:**
- Create: `/home/av/repos/miryoku_qmk/.github/workflows/build-example-crkbd-rev4-0-standard.yml`

**Interfaces:**
- Consumes: manna-harbour's reusable workflow `./.github/workflows/main.yml` (inputs `keyboard`, `merge`; unchanged).
- Produces: a dispatchable "one-click" build of the final firmware on our branch; the UF2 artifact consumed by Task 8.

- [ ] **Step 1: Create the workflow file**

```yaml
# Copyright 2021 Manna Harbour
# https://github.com/manna-harbour/miryoku

name: 'Build Example crkbd rev4_0 standard'
on:
  - workflow_dispatch
jobs:
  build:
    uses: ./.github/workflows/main.yml
    with:
      keyboard: '["crkbd/rev4_0/standard"]'
```

(No `merge` option — Ruling 8: the branch already contains QMK pinned at `6b38dc17cd^` (2025-07, last pre-keycode-rework ref); merging current `qmk/qmk_firmware/master` would reintroduce the API drift and userspace purge that broke earlier builds.)

- [ ] **Step 2: Commit and push** (IS `[miryoku-github]` — GitHub-specific, canonical per upstream docs)

```bash
cd /home/av/repos/miryoku_qmk
git add .github/workflows/build-example-crkbd-rev4-0-standard.yml
git commit -m "[miryoku-github] Add build example for crkbd/rev4_0/standard"
git push
```

- [ ] **Step 3: Run it**

```bash
gh workflow run 'Build Example crkbd rev4_0 standard' \
  --ref miryoku-LAYOUT_split_3x6_3_ex2 \
  --repo vonpupp/miryoku_qmk
gh run watch --repo vonpupp/miryoku_qmk
```
Expected: success. Success itself proves the shim engaged: with `community_layouts` containing only `split_3x6_3_ex2`, a failed resolution is a loud `Could not find keymap` error, never a silent 36/42-key build. On failure: `gh run view <id> --log-failed --repo vonpupp/miryoku_qmk`; a C preprocessor macro-arg-count error means the shim's arg count/order is off — recheck against `keyboards/crkbd/rev4_0/info.json` `layouts.LAYOUT_split_3x6_3_ex2.layout` (46 entries, row-major as documented in Task 5 Interfaces).

- [ ] **Step 4: Download the final artifact**

```bash
mkdir -p "$TMPDIR/miryoku-final"
gh run download --repo vonpupp/miryoku_qmk --dir "$TMPDIR/miryoku-final"
ls "$TMPDIR/miryoku-final"
```
Expected: `crkbd_rev4_0_standard_manna-harbour_miryoku.uf2` present.

---

### Task 8: Flash final firmware + acceptance (user)

**Files:** none in the QMK fork; spec status update in the docs repo at the end.

**Interfaces:**
- Consumes: final UF2 (Task 7).
- Produces: accepted phase-1 deliverable (spec §7).

- [ ] **Step 1: Flash both halves** — same BOOTSEL procedure as Task 4, using `$TMPDIR/miryoku-final` UF2. If flashing or behavior misbehaves (spec §8 wrong-rev risk): rebuild with `keyboard=crkbd/rev4_1/standard` in the workflow file and retry — both revs are RP2040 with identical layout macros.

- [ ] **Step 2: Acceptance checklist (spec §7)** — all must pass:
  - Inner 5 columns per hand = stock Colemak Mod-DH (left top `QWFPB`, home `ARSTG`, bottom `ZXCDV`; right `JLUY;` / `MNEIO` / `KH,./`).
  - Left thumbs: Space / Tab / Esc (primary/secondary/tertiary as held layers Nav/Mouse/Media). Right thumbs: Enter / Bspc / Del (layers Num/Sym/Fun). Opposite-hand keys activate while holding.
  - Auto-Shift works on Num/Sym layers (hold a number → shifted symbol).
  - Additional Features: hold a thumb, double-tap top-row pinkie key → bootloader (board re-enumerates as `RPI-RP2`); double-tap top-row index = Base, middle = Extra (QWERTY).
  - Extra keys: left inner top/home and both outer columns produce nothing; right inner **home** switches default layer to QWERTY, right inner **top** switches back to Colemak, and the choice persists across unplug/reboot.
  - Both halves register; OLED/RGB behave per crkbd defaults.

- [ ] **Step 3: Real-work session** — the user types on it for at least one working session before phase 2 begins.

- [ ] **Step 4: Close out** — in `/home/av/repos/miryoku`, update the spec's `Status:` line to `implemented`, tick this plan's boxes, and commit:

```bash
cd /home/av/repos/miryoku
git add docs/superpowers/
git commit -m "Mark split_3x6_3_ex2 phase 1 implemented"
```
