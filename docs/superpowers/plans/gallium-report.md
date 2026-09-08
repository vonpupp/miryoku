# Report — Add GALLIUM alpha alternative (babel → qmk → firmware → docs)

Date: 2026-09-08. Status: COMPLETE (all steps green, including fix round below).

## Commits / run

| Repo | Commit | Pushed |
|---|---|---|
| vonpupp/miryoku_babel (miryoku-LAYOUT_split_3x6_3_ex2) | `4d72224` Add GALLIUM alphas alternative (Gallium Colstag) | yes (64791c9..4d72224) |
| vonpupp/miryoku_qmk (miryoku-LAYOUT_split_3x6_3_ex2) | `9761fe3f96` Default to GALLIUM alphas; refresh miryoku_babel headers | yes (72c47eb788..9761fe3f96) |
| vonpupp/miryoku (miryoku-LAYOUT_split_3x6_3_ex2) | `555c3d0` Gallium default: roadmap tick + keymap update | yes (600efb8..555c3d0) |

Workflow run: https://github.com/vonpupp/miryoku_qmk/actions/runs/34231427965
(`Build Inputs`, keyboard=xtips/v4s/103c, no merge input) → completed / success.
Artifact id 10058018259 (`miryoku_qmk-xtips_v4s_103c`).

## Firmware hashes

- Old (Colemak build): `e6f9843cfa12d7c7aad26ac8e58cc3cfd64f016d770d352784b95c05ae2c7667`
- New (Gallium build):  `b5393b43ac911b93eb89e797c2e74c6c7ef29525ca6d9ee8b3af25c4b90ab3c8`
- Hashes differ (required). New .bin copied to
  `~/repos/miryoku/tmp/firmware-final/xtips_v4s_103c_manna-harbour_miryoku.bin`
  (replaced old). Not flashed.

## Step 1 — babel wiring (readme.org)

Wired sites (every COLEMAKDH site class has a GALLIUM sibling; COLEMAKDHK kept beside both):

1. Alternative Layouts / Alphas doc section: new `***** Gallium` entry with
   `~MIRYOKU_ALPHAS=GALLIUM~`, `#+NAME: gallium` table (B L D C V / N R T S G /
   X Q M W Z K F `,` `DOT` `/` — `'` top-right), one-line provenance comment
   (Gallium Colstag, https://github.com/GalileoBlues/Gallium, punct adapted to
   miryoku conventions). Placed between Dvorak and Halmak (see Concerns #1).
2. Per-target generation blocks — 4 GALLIUM defines per target × 5 targets
   (qmk 1445+, zmk 1690+, kmonad 1930+, svg 2169+, kmk 2410+):
   `MIRYOKU_ALTERNATIVES_{BASE,TAP}_GALLIUM{,_FLIP}` referencing
   `alphas_table=gallium`, each inserted beside its COLEMAKDH sibling.
3. Selection chains: the shared `layer-body` block (used by all five
   `miryoku_layer_selection.h` tanglings via noweb) — GALLIUM arm added to all
   6 chains (BASE/EXTRA/TAP × FLIP/plain), between DVORAK and HALMAK.
   The `#else` defaults were left at COLEMAKDH (upstream default unchanged;
   the fork selects GALLIUM via custom_rules.mk).

Count check (case-sensitive):

```
before: grep -c colemakdh readme.org                     = 43
after:  grep -c colemakdh readme.org                     = 43   (untouched)
after:  grep -c -e colemakdh -e gallium readme.org       = 64   (+21 = new gallium lines)
after:  grep -c gallium readme.org                       = 21   (20 noweb sites + 1 #+NAME)
after:  grep -c GALLIUM readme.org                       = 33   (20 defines + 12 selection-arm lines + 1 doc line)
per-target defines: qmk 4, zmk 4, kmonad 4, svg 4, kmk 4
```

COLEMAKDH baseline: 20 noweb alternatives sites + 6 selection arms — exactly
matched by GALLIUM (20 + 6), plus table/heading/doc line.

## Step 2 — tangle

```
emacs --batch -Q -l ob-python \
  --eval "(setq org-confirm-babel-evaluate nil python-indent-guess-indent-offset-verbose nil)" \
  --eval "(progn (find-file \"readme.org\") (org-babel-tangle))"
→ "Tangled 15 code blocks from readme.org"
```

`git diff --stat tangled/`: 10 files changed, 180 insertions(+), 0 deletions —
no formatting churn at all.

```
grep -c GALLIUM tangled/qmk/miryoku_layer_alternatives.h = 4   (>= 4 required)
  → MIRYOKU_ALTERNATIVES_BASE_GALLIUM_FLIP / _BASE_GALLIUM /
     TAP_GALLIUM_FLIP / TAP_GALLIUM, all with correct keycodes
grep GALLIUM tangled/qmk/miryoku_layer_selection.h → 6 new arms (BASE/EXTRA/TAP × FLIP/plain)
```

## Step 3 — qmk fork

- `tangled/qmk/*.h` copied to `users/manna-harbour_miryoku/miryoku_babel/`
  (miryoku_layer_alternatives.h +24, miryoku_layer_selection.h +12;
  layer_list.h byte-identical).
- `users/manna-harbour_miryoku/custom_rules.mk`: appended `MIRYOKU_ALPHAS = GALLIUM`
  (file previously contained only the copyright header).
- Confirmed via `post_rules.mk`: `MIRYOKU_ALPHAS` → `-DMIRYOKU_ALPHAS_GALLIUM`
  → layer-body selects `MIRYOKU_ALTERNATIVES_BASE_GALLIUM`.
- Artifact's own `custom_rules.mk` shows `MIRYOKU_ALPHAS = GALLIUM` — the CI
  build used it.

## Step 4 — build + decode verification

Dispatched with `env -u GITHUB_TOKEN gh workflow run 'Build Inputs' --ref
miryoku-LAYOUT_split_3x6_3_ex2 --repo vonpupp/miryoku_qmk -f
keyboard=xtips/v4s/103c` (no merge input). Green in ~5 min.

Keycode ground truth from the fork's own `quantum/keycodes.h`
(KC_A=4 … KC_Z=29, KC_QUOTE=0x34, KC_COMMA=0x36, KC_DOT=0x37, KC_SLASH=0x38;
QK_MOD_TAP=0x2000, QK_LAYER_TAP=0x4000, QK_DEF_LAYER=0x5240).

Keymap block located at file offset `0x791e` (unique hit for the uint16-LE
sequence 05 00 0F 00 07 00 06 00 19 00). Layer 0 (BASE) decodes to:

```
row1 left : 0x0005 KC_B   0x000F KC_L   0x0007 KC_D   0x0006 KC_C   0x0019 KC_V
row2 left : 0x2811 LGUI_T(KC_N)  0x2415 LALT_T(KC_R)  0x2117 LCTL_T(KC_T)  0x2216 LSFT_T(KC_S)  0x000A KC_G
row3 left : 0x431B LT(U_BUTTON,KC_X)  0x3414 ALGR_T(KC_Q)  0x0010 KC_M  0x001A KC_W  0x001D KC_Z
row1 right: 0x000D KC_J   0x001C KC_Y   0x0012 KC_O   0x0018 KC_U   0x0034 KC_QUOTE
row2 right: 0x0013 KC_P   0x220B LSFT_T(KC_H)  0x2104 LCTL_T(KC_A)  0x2408 LALT_T(KC_E)  0x280C LGUI_T(KC_I)
row3 right: 0x000E KC_K   0x0009 KC_F   0x0036 KC_COMMA  0x3437 ALGR_T(KC_DOT)  0x4338 LT(U_BUTTON,KC_SLSH)
thumbs    : LT(Media,ESC) LT(Nav,SPC) LT(Mouse,TAB) LT(Sym,ENT) LT(Num,BSPC) LT(Fun,DEL); DF(0)/DF(1) on the extras
```

Top-left row = B,L,D,C,V and home row = N,R,T,S,G — exactly Gallium, with the
mod-tap skeleton identical to BASE_COLEMAKDH (P plain; H,A,E,I carry
Sft,Ctl,Alt,Gui). PASS.

## Step 5 — docs

- `readme.org` Roadmap: heading "(direction, not started)" → "Roadmap";
  line now reads "Gallium (done 2026-09-08), Sturdy, Magic Sturdy, Canary …".
- `docs/keymap.yaml`: Base and Tap layers transcribed from the tangled
  BASE_GALLIUM / TAP_GALLIUM blocks (same letters/holds as decoded above);
  header comment "(stock)" → "(Gallium alphas)". Extra layer (QWERTY) and all
  other layers untouched.
- Re-rendered: `keymap draw keymap.yaml -o
  keymap.svg && rsvg-convert -w 1600 keymap.svg -o keymap.png`; render visually
  checked (Base/Tap show Gallium, mods on N R T S / H A E I).

## Concerns

1. Placement interpretation: the brief said "between BEAKL15/COLEMAK* entries
   following the existing ordering". The existing ordering is alphabetical
   everywhere (…COLEMAKDHK, DVORAK, HALMAK…), so GALLIUM sits between Dvorak
   and Halmak in the doc section, the selection chains, and all five
   alternatives blocks. If a position between BEAKL-15 and Colemak was actually
   wanted, it's a one-move change in readme.org + re-tangle.
2. Tap-layer mismatch between doc and firmware: the brief had the doc's Tap
   layer updated to Gallium letters (done, = TAP_GALLIUM block), but the build
   only sets `MIRYOKU_ALPHAS = GALLIUM`; `MIRYOKU_TAP` is unset, so the
   firmware's DF(U_TAP) layer still defaults to Colemak-DH letters. The doc's
   "Colemak" DF label was left as-is for that reason. If the plain-letters
   layer should be Gallium on-device, append `MIRYOKU_TAP = GALLIUM` to
   custom_rules.mk and rebuild (expected: only the TAP layer rows change).
3. `miryoku_layer_list.h` is byte-identical after re-tangle (layer names don't
   change), so only 2 of the 3 copied headers show a diff in qmk.
4. Sandbox: all writes under ~/repos/miryoku_qmk required
   sandbox-disabled commands (predicted "Read-only file system" tell);
   babel/docs commits and pushes ran sandboxed.
5. babel working tree has pre-existing untracked files (`.claude/`,
   `.mcp.json`); left uncommitted, as with `tmp/` and dotfiles in the docs repo.

## Fix round — Tap layer matches base (MIRYOKU_TAP = GALLIUM)

Resolves Concern #2: the user's config intent is "Tap layer matches base".

1. `users/manna-harbour_miryoku/custom_rules.mk`: appended
   `MIRYOKU_TAP = GALLIUM` on its own line after `MIRYOKU_ALPHAS = GALLIUM`.
2. qmk commit `c40db8589a` "Set Tap layer to GALLIUM (matches base)"
   (pushed 9761fe3f96..c40db8589a).
3. Re-dispatched `Build Inputs` (keyboard=xtips/v4s/103c, no merge input):
   https://github.com/vonpupp/miryoku_qmk/actions/runs/34232368104 →
   completed / success. Artifact id 10058393979; its custom_rules.mk confirms
   both `MIRYOKU_ALPHAS = GALLIUM` and `MIRYOKU_TAP = GALLIUM`.
4. Hashes (all three distinct):
   - Colemak build:      `e6f9843cfa12d7c7aad26ac8e58cc3cfd64f016d770d352784b95c05ae2c7667`
   - Gallium base only:  `b5393b43ac911b93eb89e797c2e74c6c7ef29525ca6d9ee8b3af25c4b90ab3c8`
   - Gallium base+tap:   `6275d4d9486dfc377167cb962a9d30af39653b54371d830acb0e955eda30208c`
5. Decode verification (keycode values from the fork's `quantum/keycodes.h`;
   layers are 56 uint16 each; indices confirmed by the `layers` table order
   U_BASE=0, U_EXTRA=1, U_TAP=2):
   - layer 0 BASE @ 0x791e: unchanged — B,L,D,C,V top; LGUI_T(N), LALT_T(R),
     LCTL_T(T), LSFT_T(S), G home.
   - layer 1 EXTRA @ +56: Q,W,E,R,T (QWERTY default) — stride/indexing cross-check.
   - layer 2 U_TAP @ 0x79fe: **plain keycodes, no mod-taps**:
     `KC_B KC_L KC_D KC_C KC_V | KC_N KC_R KC_T KC_S KC_G | KC_X KC_Q KC_M KC_W KC_Z`
     right hand `KC_J KC_Y KC_O KC_U KC_QUOTE | KC_P KC_H KC_A KC_E KC_I |
     KC_K KC_F KC_COMMA KC_DOT KC_SLASH`, thumbs ESC SPC TAB (ENT BSPC DEL) —
     exactly the tangled TAP_GALLIUM block. PASS.
6. New .bin installed at
   `~/repos/miryoku/tmp/firmware-final/xtips_v4s_103c_manna-harbour_miryoku.bin`
   (replaced b5393b43…). Not flashed.

Fix-round concerns: none open. (The docs keymap.yaml Tap layer — already
Gallium — and the "Colemak" DF label are now the only stale artifacts; the
label could be renamed "Gallium" or "Base" in a future docs pass since
DF(U_TAP) now leads to Gallium letters.)
