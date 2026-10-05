---
name: aseprite
description: Move REBORNER sprites in and out of Aseprite (.aseprite/.ase files) — export game sprites or drafts as .aseprite with tags and frame durations so kwan can hand-edit them in Aseprite, and import edited .aseprite files back to PNG frames. Use when kwan sends or asks for an .aseprite/.ase file, mentions Aseprite, or wants to hand-edit a sprite or animation.
---

# Aseprite ↔ REBORNER

Aseprite itself is **not** in this repo and must never be added: its source is under an EULA (compile for personal use only, no distribution). Everything here works from the published file-format spec (`docs/ase-file-specs.md` in github.com/aseprite/aseprite) with pure Python (PIL + zlib). kwan runs Aseprite on their own machine.

The repo carries the official source **only as a git submodule pointer** (`third_party/aseprite`, pinned to tag `v1.3.18.6`, outside `reborner/` so Godot never scans it). A submodule stores a link to github.com/aseprite/aseprite, not a copy of its code, so nothing is redistributed. Never vendor the files, commit a build, or add a release binary.

### Build Aseprite for your own use (optional)

The `.aseprite` tools below do not need it. Build only when kwan wants the real program, on their own machine (EULA: personal compile only).

```
git submodule update --init --recursive third_party/aseprite      # source + its own submodules (laf, third_party)
cd third_party/aseprite && ./build.sh                             # official script: downloads prebuilt Skia, runs cmake + ninja
# Linux packages first: g++ clang cmake ninja-build unzip libx11-dev libxcursor-dev libxi-dev libxrandr-dev libgl1-mesa-dev libfontconfig1-dev
```

The binary lands in `third_party/aseprite/build/bin/aseprite`. `build/` is outside version control; never `git add` it. To move to a newer release: `cd third_party/aseprite && git fetch --depth 1 origin tag <vX.Y.Z> && git checkout <vX.Y.Z>`, then commit the new pointer and update the tag named above.

All tool paths below are relative to `reborner/`.

## Tools

| File | Job |
|---|---|
| `tools/sprites/aseprite_io.py` | `read(path)` → frames (RGBA), durations (ms), tags, layers, notes · `write(path, frames, durations, tags)` |
| `tools/sprites/aseprite_export.py` | Game sprites + drafts → `docs/art-bible/aseprite/{game,poses64,spells,npcs}/` |
| `tools/sprites/aseprite_import.py` | `.aseprite` → PNG per frame + `meta.json` |
| `tools/sprites/aseprite_check.py` | Round-trip check: every exported frame reads back pixel-identical. Exit 1 on mismatch |

## Export (to kwan)

```
python3 tools/sprites/aseprite_export.py            # all sets
python3 tools/sprites/aseprite_export.py game      # only the in-game Rion + dog sheets
```

- `game/rion.aseprite`, `game/dog.aseprite`: the sprites the game actually loads. One tag per file-name prefix: `south`, `south_w`, `west_a`, `west_h`, `west_k` … (tag `south_w` frame 0 = `south_w0.png`).
- Frame durations come from game constants (`MOVE_TIME`, `ATTACK_FRAME_SEC`, `FOE_IDLE_SEC`) read out of the `.gd` files. Never type a duration by hand.
- Identical frames are written as linked cels, so editing one updates every frame linked to it.
- The palette panel is filled with the sprite's own colours (≤256).

## Import (from kwan)

```
python3 tools/sprites/aseprite_import.py <file.aseprite>                 # → docs/art-bible/aseprite/imported/<name>/ (staging)
python3 tools/sprites/aseprite_import.py <file.aseprite> --into <dir>    # overwrite game sprites — only after kwan approves
```

- Output names follow tags: a 1-frame tag → `<tag>.png`, a multi-frame tag → `<tag><i>.png`, no tags → `frame_<i>.png`.
- Visible layers are flattened (a hidden group hides its children). Layer and cel opacity are applied; non-Normal blend modes, tilemaps and per-cel z-index are read as plain Normal and reported in `notes` / `meta.json`. Tell kwan when notes appear.
- RGBA, Grayscale and Indexed sprites are all supported.

## Rules

1. Default import goes to staging. Writing into `assets/sprites/` needs kwan's explicit approval (CLAUDE.md: experimental art does not enter the game before approval).
2. A file kwan drops into the repo (e.g. uploaded through GitHub) is read, never modified in place.
3. After changing `aseprite_io.py`, run `aseprite_check.py`; it must print `mismatch 0`.
4. If imported game sprites change size or frame count, check `world/Overworld.gd` / `world/BattleScreen.gd` still match (walk = 4 frames, attack = 4, etc.) and report any mismatch to kwan instead of changing game code silently.
5. After importing into the game, rebuild the animation test page (`python3 tools/web/anim_test_build.py <out>`) and republish it.

## Verified

- The reader parses all 20 sample sprites in Aseprite's own `tests/sprites/` (layers, groups, linked cels, tags, indexed/grayscale).
- Files from the writer open without errors in the independent `ase-parser` (npm) with correct tags, durations and palette.
