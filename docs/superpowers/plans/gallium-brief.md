# Brief — Add GALLIUM alpha alternative (babel → qmk → firmware → docs)

Goal: `MIRYOKU_ALPHAS=GALLIUM` works exactly like the stock alternatives, and
the user's fork builds Gallium as the default base layer.

## The layout (fixed content — use verbatim)

Gallium Colstag (GalileoBlues, 2023), adapted to miryoku's punctuation
conventions (letters exactly as Gallium; `'` top-right, `, . /` bottom-right —
same skeleton as COLEMAKDH; `/` would otherwise live on an 11th key that
miryoku's 3x10 tables don't have):

```
| B | L | D | C | V | J | Y | O | U | ' |
| N | R | T | S | G | P | H | A | E | I |
| X | Q | M | W | Z | K | F | , | . | / |
```

In babel org-table syntax, matching the existing tables' style exactly
(compare `#+NAME: colemakdh` at readme.org:90 and its AZERTY/BEAKL15
neighbours — mind the MINS/DOT/PIPE/DQUO special spellings; here only `DOT`
and plain `'` are needed; use `|` cells exactly like the colemakdh table
uses for `'`):

#+NAME: gallium
| B | L | D | C | V | J | Y | O | U | ' |
| N | R | T | S | G | P | H | A | E | I |
| X | Q | M | W | Z | K | F | , | DOT | / |

## Repos / branch / auth

- babel: ~/repos/miryoku/miryoku_babel (origin=vonpupp/miryoku_babel,
  branch miryoku-LAYOUT_split_3x6_3_ex2, clean at upstream master + our empty
  branch — verify with git status; it should have NO local commits yet)
- qmk: ~/repos/miryoku_qmk (same branch, tip 7c38d6c or later)
- ALL gh/git-push commands: `env -u GITHUB_TOKEN ...`; git writes outside
  ~/repos/miryoku need the Bash sandbox disabled ("Read-only file
  system" is the tell).

## Step 1 — babel readme.org wiring

Every place the alternative is wired has a COLEMAKDH sibling to copy the
pattern from. Find them all with:
`grep -n "COLEMAKDH\|colemakdh" readme.org`
Expected site classes (verify counts yourself; do not skip any):
1. The Alphas alternatives section: add a `*** Gallium` heading with
   `~MIRYOKU_ALPHAS=GALLIUM~` + the named table + a one-line provenance
   comment (Gallium Colstag, https://github.com/GalileoBlues/Gallium,
   punct adapted to miryoku conventions), placed between BEAKL15/COLEMAK*
   entries following the existing ordering.
2. Per-target generation blocks (qmk ~line 1445+, zmk ~1690+, kmonad ~1930+,
   svg later): each target has `#if defined (MIRYOKU_ALPHAS_*)`-guarded
   BASE/BASE_FLIP/TAP/TAP_FLIP blocks referencing
   `<<table-layer-taphold(alphas_table=colemakdh...)>>` /
   `<<table-layer-full(...alphas_table=colemakdh...)>>`. Add the matching
   GALLIUM block beside each COLEMAKDH one (same guard style, MIRYOKU_ALPHAS_GALLIUM).
3. Selection chains (`#if defined (MIRYOKU_ALPHAS_AZERTY)` around line 1037
   and equivalents per target in the layer_selection tangle): add the
   GALLIUM arm wherever COLEMAKDH has one.
Count check: `grep -c colemakdh readme.org` before vs
`grep -c -e colemakdh -e gallium` after should differ by exactly the number
of new gallium sites, and `grep -c gallium` should equal the colemakdh site
count (plus table+heading).

## Step 2 — tangle locally

```
cd ~/repos/miryoku/miryoku_babel
emacs --batch -Q -l ob-python \
  --eval "(setq org-confirm-babel-evaluate nil python-indent-guess-indent-offset-verbose nil)" \
  --eval "(progn (find-file \"readme.org\") (org-babel-tangle))" 2>&1 | tail -5
git status --short tangled/
```
Expect: tangled/qmk/miryoku_layer_alternatives.h + selection/list headers
modified. Formatting churn elsewhere is possible (local org version vs
upstream's) — if the diff touches files/lines unrelated to alternatives,
report it as a concern but proceed (our fork, regeneration is legitimate).
Hard requirement: `grep -c GALLIUM tangled/qmk/miryoku_layer_alternatives.h`
>= 4 (BASE, TAP, and flip variants) and
`grep GALLIUM tangled/qmk/miryoku_layer_selection.h` shows the new arm.
If emacs fails (ob-python/session issues), report BLOCKED with the error.

## Step 3 — copy to qmk fork + default

1. `cp tangled/qmk/*.h ~/repos/miryoku_qmk/users/manna-harbour_miryoku/miryoku_babel/`
2. In ~/repos/miryoku_qmk/users/manna-harbour_miryoku/custom_rules.mk:
   append `MIRYOKU_ALPHAS = GALLIUM` (read the file first; follow its style).
3. Commit babel: `Add GALLIUM alphas alternative (Gallium Colstag)`; push
   (`env -u GITHUB_TOKEN git push`, HTTPS works for babel).
4. Commit qmk: `Default to GALLIUM alphas; refresh miryoku_babel headers`;
   push.

## Step 4 — build + verify

Dispatch: `env -u GITHUB_TOKEN gh workflow run 'Build Inputs' --ref
miryoku-LAYOUT_split_3x6_3_ex2 --repo vonpupp/miryoku_qmk -f
keyboard=xtips/v4s/103c` (NO merge input). Poll <= 20 min.
Green: download THIS run's artifact by id; sha256 MUST differ from
e6f9843cfa12d7c7aad26ac8e58cc3cfd64f016d770d352784b95c05ae2c7667 (the
Colemak build). Then decode-verify like Task 9 did: locate the keymap block
in the .bin and confirm layer 0's left-top row is B,L,D,C,V and home row
N,R,T,S,G (KC_B=0x0005...: B=4? verify via quantum/keycode_values or
basic-keycode ordering: A=4,B=5,...,Z=29; report the decoded first row).
Copy the .bin to ~/repos/miryoku/tmp/firmware-final/ (replacing the
old one; note old+new hashes).
Failure: capture full `--log-failed`, report BLOCKED.

## Step 5 — docs

1. ~/repos/miryoku/readme.org Roadmap: mark Gallium done (move line
   out of "direction" or annotate "(done 2026-09-08)").
2. docs/keymap.yaml: update the Base and Tap layers' letters to Gallium
   (B L D C V J Y O U ' / N R T S G P H A E I / X Q M W Z K F , . / with the
   same home-row mod-tap holds: N=Gui R=Alt T=Ctl S=Sft left, and right
   home P H A E I has NO mod-taps except... check: miryoku mod-taps sit on
   home row cols 1-4 both hands: left N R T S, right H A E I? NO — look at
   the tangled BASE_GALLIUM block YOU generated in step 2 and transcribe
   exactly). Re-render:
   `cd ~/repos/miryoku/docs && keymap draw keymap.yaml -o keymap.svg && rsvg-convert -w 1600 keymap.svg -o keymap.png`
3. Commit docs: `Gallium default: roadmap tick + keymap update`; push
   (`env -u GITHUB_TOKEN git -C ~/repos/miryoku push` — careful: run
   git with -C ~/repos/miryoku, the shell cwd resets).

## Report

Write ~/repos/miryoku/docs/superpowers/plans/gallium-report.md
(commands, grep counts, tangle diff stat, hashes, decoded letters, run URL).
Return ONLY: status, babel commit, qmk commit, docs commit, run URL, new
bin sha256, one-line summary, concerns. Do not dispatch subagents. Do not
flash anything.
