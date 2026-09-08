# PRD — Miryoku on `LAYOUT_split_3x6_3_ex2` (Corne V4, 46 keys)

Date: 2026-09-07
Branch (all repos): `miryoku-LAYOUT_split_3x6_3_ex2`
Status: implemented and hardware-accepted (2026-09-08) — see §10 for the hardware pivot addendum

## 1. Context

The user types on a 46-key split keyboard: a Corne V4 clone ("V4a", Umux-manufactured,
purchased via goofish, listing advertises dedicated copy/paste/cut/undo keys "in the
middle" — confirming the extra keys' inner placement). The physical layout matches
upstream QMK's `crkbd/rev4_0/standard` keyboard with `LAYOUT_split_3x6_3_ex2`:

- 42 standard keys: 3 rows × 6 columns + 3 thumb keys per half.
- 4 extra keys (`ex2`): a vertical pair per half on the innermost column, directly
  above the inner thumb key (top + home rows only; no bottom-row key).
- Verified from `keyboards/crkbd/rev4_0/info.json` in upstream QMK: the `ex2` layout
  is exactly `split_3x6_3` plus `[(6,0.7),(6,1.7)]` (left) and `[(8,0.7),(8,1.7)]`
  (right) in KLE units. Both `rev4_0` and `rev4_1` are RP2040.

Reference material:

- justinmklam/corne-keyboard — same keyboard/layout (`crkbd/rev4_0/standard`,
  `LAYOUT_split_3x6_3_ex2`); secondary hardware reference, not a keymap source.
- `tmp/2026-09-02-miryoku-qwerty-colemak.vil` — the user's current Vial config.
  REFERENCE ONLY for phase 2 (already miryoku-flavored: Colemak-DH alphas, miryoku
  thumb layer-taps, tap-dance home-row mods, `DF` QWERTY/Colemak switching on the
  extra keys). Not to be copied in phase 1.

## 2. Goal

Run **stock Miryoku (QMK implementation), unmodified**, on this keyboard — a migration
as faithful as possible — using Miryoku's own build method (fork + GitHub Actions
workflows). Of the 4 extra keys, the two right inner ones provide instant
default-layer switching (`DF(U_EXTRA)` → QWERTY on home, `DF(U_BASE)` → Colemak on
top — the user's documented daily-driver aid; stock needs no options since U_EXTRA
defaults to QWERTY); the two left inner extras stay inert.

## 3. Non-goals (deferred to phase 2+)

- Any layer customization (alphas are stock Colemak Mod-DH, etc.).
- Extra-key functions beyond the two `DF` switches (e.g. home-row tap-dance
  mods, the clone's clipboard keys) — still phase 2.
- Editing `miryoku_babel` org sources.
- Vial/VIA support (flashing Miryoku firmware replaces the current Vial firmware;
  live remapping returns only if VIA is added in a later phase).
- ZMK / KMK / kmonad targets.

## 4. How Miryoku works (architecture recap)

- `manna-harbour/miryoku` (this repo) is docs + data only. No firmware code.
- Layer data originates in `manna-harbour/miryoku_babel`: `readme.org` holds the
  layer tables as org tables; org-babel + embedded Python tangle them into
  `tangled/{qmk,zmk,kmk,kmonad,svg}/...` headers, copied into each implementation.
  Phase 1 requires **no** babel changes — layer data is keyboard-agnostic.
- The QMK implementation lives in the `miryoku` branch of `manna-harbour/miryoku_qmk`
  (a QMK fork). The keymap is written once against a virtual `LAYOUT_miryoku`
  (10×4 grid: 30 alphas + 6 thumbs). Physical keyboards are supported by **subset
  mapping shims**: `layouts/community/<layout>/manna-harbour_miryoku/config.h`
  re-expands `LAYOUT_miryoku(...)` into the physical `LAYOUT_<layout>(...)`, padding
  unmapped positions with `KC_NO` (`XXX`).
- The `miryoku` branch snapshot predates `crkbd/rev4_0`; Miryoku's documented remedy
  is the workflow `merge` option (merge `qmk/qmk_firmware/master` at build time after
  auto-reverting `[miryoku-github]` commits).

## 5. Working set

| Repo | Role | Branch |
|---|---|---|
| `manna-harbour/miryoku` (local clone) | Docs, PRD home | `miryoku-LAYOUT_split_3x6_3_ex2` |
| `manna-harbour/miryoku_babel` (local clone at `./miryoku_babel`, git-excluded) | Ground truth for layers; untouched in phase 1 | same |
| fork of `manna-harbour/miryoku_qmk` (to be created under the user's GitHub account) | All code changes; workflow builds | same |

## 6. Plan

### Step 0 — Baseline build (no code changes)

1. Fork `manna-harbour/miryoku_qmk` on GitHub; enable Actions; create branch
   `miryoku-LAYOUT_split_3x6_3_ex2`.
2. Run the built-in **Build Inputs** workflow:
   - Keyboard: `crkbd/rev4_0/standard`
   - Merge: `qmk/qmk_firmware/master`
3. Download the firmware artifact and flash it. This exercises the entire
   fork → workflow → merge → flash chain on the clone before writing any code.
   Expected behavior: stock Miryoku via the existing `split_3x6_3` community shim
   (42 keys live; 4 extras dead).

### Step A — The conversion (two commits + one workflow file in the fork)

1. **Shim commit** — `layouts/community/split_3x6_3_ex2/manna-harbour_miryoku/`:
   - `keymap.c`: license stub only (as in the existing `split_3x6_3` shim).
   - `config.h`: defines `LAYOUT_miryoku(...)` expanding to
     `LAYOUT_split_3x6_3_ex2(...)`. Mapping (verified arg order from
     `crkbd/rev4_0/info.json`; `XXX` = `KC_NO`):

     ```
     top    (14): XXX, K00 K01 K02 K03 K04, XXX   |  DF(U_BASE),   K05 K06 K07 K08 K09, XXX
     home   (14): XXX, K10 K11 K12 K13 K14, XXX   |  DF(U_EXTRA),  K15 K16 K17 K18 K19, XXX
     bottom (12): XXX, K20 K21 K22 K23 K24        |  K25 K26 K27 K28 K29, XXX
     thumbs ( 6):        K32 K33 K34              |  K35 K36 K37
     ```

     Per half, columns run outer→inner; the innermost column (x6/x8) carries the two
     extras (top, home): left extras `XXX`, right extras `DF(U_BASE)` (top, → Colemak)
     and `DF(U_EXTRA)` (home, → QWERTY). The outermost column is `XXX` exactly as in
     the stock `split_3x6_3` shim. Thumbs: left `K32 K33 K34` = (x4,3.7) (x5,3.7)
     (x6,3.2); right `K35 K36 K37` = (x8,3.2) (x9,3.7) (x10,3.7).
2. **Registration commit** — add `"split_3x6_3_ex2"` to `community_layouts` in the
   crkbd rev4_0 `info.json` that declares the layouts (verify during implementation
   whether the `standard/` subdir owns its own `info.json`). The ex2 layout is then
   selected at build time via QMK's standard `FORCE_LAYOUT` mechanism; exact
   plumbing (workflow option vs `custom_rules.mk`) follows the existing Build
   Example patterns.
3. **Build workflow** — one Build-Example copy in the fork targeting
   `crkbd/rev4_0/standard`, giving one-click reproducible builds. No `merge`
   option: the branch's QMK is deliberately pinned at `6b38dc17cd^` (2025-07,
   last ref before the keycode removals) — merging current QMK master would
   reintroduce API drift.

## 7. Verification & acceptance

- **Pre-flight (gates everything):** BOOTSEL-plug the board; a `RPI-RP2` USB mass
  storage device must appear (RP2040 confirmed). If not, fall back to contingency C.
- Flash Step 0 baseline, then Step A firmware (UF2 drag-drop, both halves).
- Acceptance criteria:
  - All 36 Miryoku positions behave per the reference manual: default Colemak
    Mod-DH alphas; thumb layer-taps (Space/Tab/Esc left, Enter/Bspc/Del right);
    Nav/Mouse/Media via left thumbs; Num/Sym/Fun via right thumbs; Auto Shift;
    Additional Features (bootloader, base-layer switching) on double-tap holds.
  - Extra keys: left inner top/home produce nothing; right inner **home** switches
    the default layer to QWERTY, right inner **top** switches back to Colemak;
    the choice persists across reboot/unplug.
  - Both halves communicate (keys on the secondary half register).
  - OLED/RGB behave per crkbd defaults.
- The user types on it for real work before phase 2 begins.

## 8. Risks & contingencies

| Risk | Mitigation |
|---|---|
| Clone's MCU/hardware may deviate despite matching layout | Pre-flight BOOTSEL check; contingency C: add a custom keyboard def informed by the current firmware's source |
| Fork's `info.json` edit conflicts on future `merge` runs with QMK master | One-line array addition; trivially resolvable |
| `crkbd/rev4_0` missing from the `miryoku` branch | By design: `merge` option |
| Wrong rev guess (`rev4_0` vs `rev4_1`) | Both are RP2040 with identical layouts; build the other rev if flashing misbehaves |
| Losing Vial live-remap | Accepted trade-off; `.vil` preserved in `tmp/` for phase 2 reference |

## 9. Future phases (informative)

- Phase 2: layer customization via `miryoku_babel` org tables → tangle → copy into
  fork (babel's own tangle workflow or local emacs); candidate ideas from the `.vil`:
  home-row mods, QWERTY/Colemak dual base layers on the extra keys.
- Phase 3 (optional): VIA support; other firmware targets.

## 10. Addendum — hardware pivot (implemented reality)

During the deferred hardware session (design §7 pre-flight), the board turned
out NOT to be an RP2040 Corne v4: it is an **X.Tips V4s** (umux.com, USB
`5262:4e4b`, Geehy APM32F103C8T6 = STM32F103C8 clone, `stm32duino` Maple DFU
bootloader). The vendor publishes the keyboard definition at
`X-Tips/QMK-Keyboard` (`v4s/103c`). Phase 1 was completed against that target:

- `keyboards/xtips/v4s/103c/` vendored into the fork (vendor files
  byte-identical; layouts replaced with a board-true 46-key
  `LAYOUT_split_3x6_3_ex2` — the inner extra keys sit on the home and bottom
  rows, unlike crkbd's top+home) plus `community_layouts` registration.
- The community shim was retargeted to that argument order: right home inner
  extra = `DF(U_EXTRA)` (QWERTY), right bottom inner extra = `DF(U_BASE)`
  (Colemak) — the user's original Vial placement; left extras and outer
  columns inert.
- All crkbd-era work (rev4_0 registrations, default layout definition, RP2040
  artifacts in `tmp/firmware-crkbd-rp2040-reference/`) is retained on the
  branch as reference only.
- Firmware: `xtips_v4s_103c_manna-harbour_miryoku.bin` (33,624 B, 51% of the
  64 KB flash), flashed to both halves via `dfu-util -a 2 -d 1eaf:0003`
  (flash @ 0x8002000); bootloader entry via bootmagic (hold `E`/`I` while
  plugging). Accepted by use.
