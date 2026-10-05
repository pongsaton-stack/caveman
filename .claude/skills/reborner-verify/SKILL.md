---
name: reborner-verify
description: Verify a REBORNER (Godot game in reborner/) change before reporting it done — Godot setup in a fresh session, the test suite, battle seed fingerprint, Sim before/after, web export, animation-test page, and the evidence to put in the report. Use after any change under reborner/ (core, data, world, scenes, assets, tools/web, project.godot, addons) and whenever asked to test, check, verify, export or publish REBORNER.
---

# Verify a REBORNER change

REBORNER's CLAUDE.md (`reborner/CLAUDE.md`) is the rulebook; this skill is the procedure. Iron rule from it: work that is not proven is not done — every report carries evidence and says plainly what was not checked. Reply to kwan in Thai.

All commands run from `reborner/`.

## 0. Fresh session setup (once)

```
GODOT=$(tools/get_godot.sh | tail -1)        # Godot 4.7.1 into ~/.cache/godot (cached after first run)
GODOT=$(tools/get_godot.sh --web | tail -1)  # + web export template, only before a web export (1.28 GB download)
"$GODOT" --headless --path . --import        # only if .godot/ is missing or "Could not find type" errors flood
```

`xvfb-run` is needed for tests that open real scenes; without it those are skipped and the runner says so.

## 1. Pick the checks by what changed

| Changed | Run |
|---|---|
| `core/` or `data/` (battle, formulas, CSV) | 2 + 3 (Sim before **and** after) — mandatory per CLAUDE.md rule 7 |
| `world/`, `scenes/`, UI, save, `project.godot`, `addons/` | 2, plus 4 if the change shows on screen |
| Art, animation, VFX | animation-test page first (step 5); in-game screenshot (`--shots`) only after kwan approves it into the game |
| Anything that ships to players | 2 + web export (step 6) |
| Docs/tools only | none of the game checks; say so |

## 2. Test suite + seed

```
GODOT=$GODOT tools/run_tests.sh
```

Passes only with exit 0 and the last line `== ผ่าน N · ไม่ผ่าน 0`. It runs `tests/check/*` (OK/FAIL contract), the gdUnit4 suites in `tests/unit/` (new focused tests go here: `test_*.gd`, `extends GdUnitTestSuite`, expected values derived from game constants), and compares the fixed-seed battle fingerprint with `tests/seed.md5`.

- A seed change after touching `core/` or `data/` is expected only if you can explain it. Then update `tests/seed.md5` in the same commit and state old → new md5 and why. An unexplained change is a bug.
- Tests use a separate save (`REBORNER_SAVE=user://test_save.json`); never point them at the real save.
- A failing test is a finding: fix it, or report it with the log `tests/out/<name>.log`. Never delete or weaken a test to get green.

## 3. Sim before / after (core/ or data/ changes)

Capture the baseline **before** editing, then compare:

```
GODOT=$GODOT tools/run_tests.sh --sim          # → tests/out/sim.txt
```

Copy the before run aside (e.g. `cp tests/out/sim.txt /tmp/sim_before.txt`) before you change anything. Sim is unseeded: about 21–23 differing lines is normal noise. A larger shift must be explained against the targets in CLAUDE.md "เป้าสมดุล". First line must read `เวอร์ชัน:` matching `VERSION` in `core/Sim.gd`.

## 4. Real screenshots

```
GODOT=$GODOT tools/run_tests.sh --shots        # → tests/out/<script>_<i>.png
```

Open the PNGs and look. Check Thai UI: ≤2 lines per box, nothing overflowing 384x216, new symbols present in the font subset (they show as boxes on the web otherwise).

## 5. Animation-test page (art, poses, VFX)

```
python3 tools/web/anim_test_build.py <scratch>/anim_test.html
```

Publish over the pinned URL (Artifact tool, `url` = https://claude.ai/artifact/MoNVTd5ckQLmb4tsfqsikw). Drive it with Playwright: no page errors, no horizontal scroll at 400 px, the new clip/tab present. Drafts stay in their draft folders (`.gdignore`) until kwan approves.

## 6. Web export (when the game itself changed)

```
GODOT=$GODOT tools/export_web.sh <scratch>/web
```

Produces `index.html` with the correct `fileSizes`, `index.js`, `index.wasm.gz.wasm`, `index.pck.wasm`. Serve the folder locally (`python3 -m http.server`) and load it in Chromium to see the overworld render before publishing over https://claude.ai/artifact/G2xSXyKupn1WSNnu96uHan. Report the pck size; a jump needs a reason. `tools/web/reborner.html` in the repo is updated only together with a publish.

## 7. Report (in Thai)

Include, as applicable: test line (`ผ่าน N · ไม่ผ่าน 0`), seed md5 (same / old → new + reason), Sim diff line count and any target moved, screenshots or page link, pck size. Then list what was **not** checked and why (no xvfb, not published, needs kwan to play it). Before committing, delete stray `*.import` files Godot creates under `docs/` and never commit `tests/out/` or `.godot/`.
