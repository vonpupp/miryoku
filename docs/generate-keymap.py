#!/usr/bin/env python3
"""Generate docs/keymap.yaml (keymap-drawer format) for the X.Tips V4s 46-key
Miryoku build, straight from miryoku_babel's tangled QMK layer data.

Source of truth: ~/repos/miryoku/miryoku_babel/tangled/qmk/miryoku_layer_alternatives.h
Physical layout: the vendored keyboard.json (keymap_info_json) — copy kept
next to this script as xtips-v4s-103c-layout.json.

Mapping: virtual LAYOUT_miryoku (4 rows x 10 cols, thumbs row3 cols 2..7)
-> our 46-slot board order (12/14/14/6) exactly as the community shim in
vonpupp/miryoku_qmk defines it (DF keys on the right home/bottom inner
extras; outer columns and left inner extras unused).
"""
import re, json, subprocess, pathlib, shutil

BABEL = pathlib.Path.home() / "repos/miryoku/miryoku_babel/tangled/qmk/miryoku_layer_alternatives.h"
KBD_JSON_SRC = pathlib.Path.home() / "repos/miryoku_qmk/keyboards/xtips/v4s/103c/keyboard.json"
HERE = pathlib.Path(__file__).resolve().parent

MACROS = {  # display name -> macro define
    "Base": "MIRYOKU_ALTERNATIVES_BASE_COLEMAKDH",
    "Extra (QWERTY)": "MIRYOKU_ALTERNATIVES_BASE_QWERTY",
    "Tap": "MIRYOKU_ALTERNATIVES_TAP_COLEMAKDH",
    "Nav": "MIRYOKU_ALTERNATIVES_NAV",
    "Mouse": "MIRYOKU_ALTERNATIVES_MOUSE",
    "Media": "MIRYOKU_ALTERNATIVES_MEDIA",
    "Num": "MIRYOKU_ALTERNATIVES_NUM",
    "Sym": "MIRYOKU_ALTERNATIVES_SYM",
    "Fun": "MIRYOKU_ALTERNATIVES_FUN",
    "Button": "MIRYOKU_ALTERNATIVES_BUTTON",
}

NAMES = {
    "KC_QUOT": "'", "KC_COMM": ",", "KC_DOT": ".", "KC_SLSH": "/", "KC_MINS": "-",
    "KC_SCLN": ";", "KC_BSLS": "\\", "KC_GRV": "`", "KC_LBRC": "[", "KC_RBRC": "]",
    "KC_EQL": "=", "KC_LEFT": "←", "KC_RGHT": "→", "KC_UP": "↑", "KC_DOWN": "↓",
    "KC_MS_L": "MS ←", "KC_MS_R": "MS →", "KC_MS_U": "MS ↑", "KC_MS_D": "MS ↓",
    "KC_WH_L": "WH ←", "KC_WH_R": "WH →", "KC_WH_U": "WH ↑", "KC_WH_D": "WH ↓",
    "KC_BTN1": "BTN1", "KC_BTN2": "BTN2", "KC_BTN3": "BTN3",
    "KC_ENT": "Enter", "KC_BSPC": "Bksp", "KC_DEL": "Del", "KC_ESC": "Esc",
    "KC_SPC": "Space", "KC_TAB": "Tab", "KC_INS": "Ins", "KC_APP": "App",
    "KC_PSCR": "PScr", "KC_SLCK": "SLck", "KC_PAUS": "Pause", "KC_CAPS": "Caps",
    "KC_HOME": "Home", "KC_END": "End", "KC_PGUP": "PgUp", "KC_PGDN": "PgDn",
    "KC_VOLU": "Vol +", "KC_VOLD": "Vol −", "KC_MUTE": "Mute", "KC_MPLY": "Play",
    "KC_MNXT": "Next", "KC_MPRV": "Prev", "KC_MSTP": "Stop",
    "KC_LGUI": "LGui", "KC_RGUI": "RGui", "KC_LALT": "LAlt", "KC_RALT": "RAlt",
    "KC_LCTL": "LCtl", "KC_RCTL": "RCtl", "KC_LSFT": "LSft", "KC_RSFT": "RSft",
    "KC_PSTE": "Paste",
    "U_RDO": "Redo", "U_PST": "Paste", "U_CPY": "Copy", "U_CUT": "Cut", "U_UND": "Undo",
    "RGB_TOG": "RGB Tog", "RGB_MOD": "RGB Mode", "RGB_HUI": "RGB Hue", "RGB_SAI": "RGB Sat", "RGB_VAI": "RGB Val",
    "U_NU": None, "U_NA": None,  # unused / not available -> blank
}
TD_FEAT = {"U_TD_U_BASE": "Base", "U_TD_U_EXTRA": "Extra", "U_TD_U_TAP": "Tap", "U_TD_BOOT": "Boot"}
MODS = {"GUI": "Gui", "ALT": "Alt", "CTL": "Ctl", "SFT": "Sft", "ALGR": "AltGr"}

def name_of(kc):
    if kc in NAMES: return NAMES[kc]
    if kc.startswith("KC_"): return kc[3:]
    if kc.startswith("RGB_"): return kc
    return kc

def key(spec):
    spec = spec.strip()
    if not spec: return {t: ""} if False else ""
    m = re.fullmatch(r"(L|R)(GUI|ALT|CTL|SFT|ALGR)_T\((\w+)\)", spec)
    if m: return {"t": name_of(m.group(3)), "h": MODS[m.group(2)]}
    m = re.fullmatch(r"LT\((\w+),(\w+)\)", spec)
    if m: return {"t": name_of(m.group(2)), "h": m.group(1).removeprefix("U_")}
    m = re.fullmatch(r"TD\(U_TD_(\w+)\)", spec)
    if m: return {"t": f"2× {TD_FEAT.get('U_TD_'+m.group(1), m.group(1))}"}
    if spec in ("U_NA", "U_NU"): return {"t": "", "type": "ghost"} if spec == "U_NU" else ""
    return name_of(spec)

def split_args(line):
    out, depth, cur = [], 0, ""
    for ch in line:
        if ch == "(": depth += 1
        if ch == ")": depth -= 1
        if ch == "," and depth == 0:
            out.append(cur); cur = ""
        else: cur += ch
    if cur.strip(): out.append(cur)
    return [a.strip() for a in out]

def macro_body(text, name):
    m = re.search(rf"#define {name} \\\n(.*?)(?=\n#define|\Z)", text, re.S)
    if not m: raise SystemExit(f"macro {name} not found")
    body = m.group(1)
    body = " ".join(l.rstrip().rstrip("\\").strip() for l in body.splitlines())
    args = split_args(body)
    assert len(args) == 40, f"{name}: expected 40 virtual keys, got {len(args)}"
    return args  # 4 rows x 10 cols, row-major

text = BABEL.read_text()
virtual = {disp: macro_body(text, mac) for disp, mac in MACROS.items()}

def slotmap(v):  # v = 40 virtual keys -> 46 board slots
    r0, r1, r2, r3 = v[0:10], v[10:20], v[20:30], v[30:40]
    return [
        {"type": "ghost"},                       #  1 L top outer (unused)
        *[key(k) for k in r0[0:5]],              #  2-6 L top alphas
        *[key(k) for k in r0[5:10]],             #  7-11 R top alphas
        {"type": "ghost"},                       # 12 R top outer (unused)
        {"type": "ghost"},                       # 13 L home outer (unused)
        *[key(k) for k in r1[0:5]],              # 14-18 L home alphas
        {"type": "ghost"},                       # 19 L home inner extra (unused)
        {"t": "QWERTY", "bl": "DF"},             # 20 R home inner extra = DF(U_EXTRA)
        *[key(k) for k in r1[5:10]],             # 21-25 R home alphas
        {"type": "ghost"},                       # 26 R home outer (unused)
        {"type": "ghost"},                       # 27 L bottom outer (unused)
        *[key(k) for k in r2[0:5]],              # 28-32 L bottom alphas
        {"type": "ghost"},                       # 33 L bottom inner extra (unused)
        {"t": "Colemak", "bl": "DF"},            # 34 R bottom inner extra = DF(U_BASE)
        *[key(k) for k in r2[5:10]],             # 35-39 R bottom alphas
        {"type": "ghost"},                       # 40 R bottom outer (unused)
        *[key(k) for k in r3[2:5]],              # 41-43 L thumbs
        *[key(k) for k in r3[5:8]],              # 44-46 R thumbs
    ]

layers = {disp: slotmap(v) for disp, v in virtual.items()}

# keep a copy of the physical layout json next to the yaml
shutil.copy(KBD_JSON_SRC, HERE / "xtips-v4s-103c-layout.json")

doc = {
    "layout": {
        "qmk_info_json": "xtips-v4s-103c-layout.json",
        "layout_name": "LAYOUT_split_3x6_3_ex2",
    },
    "layers": layers,
}
import yaml  # available via keymap-drawer deps
(HERE / "keymap.yaml").write_text(
    "# Generated by generate-keymap.py from miryoku_babel layer data + our fork's\n"
    "# split_3x6_3_ex2 shim (DF keys on right home/bottom inner extras).\n"
    "# Draw with:  keymap draw keymap.yaml -o keymap.svg   (or paste into\n"
    "# https://caksoylar.github.io/keymap-drawer and upload the layout json)\n"
    + yaml.dump(doc, sort_keys=False, allow_unicode=True, default_flow_style=None, width=100)
)
print(f"wrote {HERE/'keymap.yaml'}")
for disp, v in virtual.items():
    print(f"  {disp}: {len(v)} virtual keys -> 46 slots")
