# REBORNER — Environment Tiles Prompt Pack (kwan ส่ง 7 ต.ค. 2026)

ชีตตัวอย่างที่มากับ prompt: `environment_tileset_sheet.png` (1536×1024 · ภาพที่ส่งมา ไม่ใช่ 4K จริง)

## ⚠ ขัดกับเกม — kwan ตัดสิน 7 ต.ค.: **ยึดเกมเดิม**
- prompt/ชีต = มุม 3/4 ไอโซเมตริก ช่อง 32×32 · เกม = มุมบนลงล่าง ช่อง **24×24** (`world/Overworld.gd` `TILE := 24` · `assets/tiles_ll/`)
- ใช้ชีตเป็นแนวสี/ของวางบนแผนที่ ย่อให้ขนาดเท่าของในเกม (ลังในเกม 20px) — ไม่ใช้เป็นไทล์พื้น
- ถ้าจะเจนแพ็กต่อ: แก้ PACK 13 เป็น "24×24 px base tiles · top-down (ไม่ใช่ isometric)" ก่อนส่ง และแนบภาพในเกม (`docs/art-bible/previews/map_tiles_ingame.png`) ตามกฎกลางใน `../grok_prompts.md`
- ชีตมีแพ็ก 10 "Season/Weather" — เกมยังไม่มีระบบฤดู/สภาพอากาศ (GDD ไม่มี)

ตัดแล้ว: หมวด Props & Interactive 42 ชิ้น (`tools/sprites/env_sheet_cut.py` → `assets/sprites/env_sheet_draft/` · ร่าง) · หมวดอื่นยังไม่ตัด

---

## MASTER STYLE PROMPT

REBORNER, original hand-crafted pixel art for a Thai post-apocalyptic JRPG, modern 16-bit / SNES-quality pixel art, quality bar inspired by classic Dragon Quest VII and Romancing SaGa 3 without copying existing artwork.

Top-down / 3/4 isometric environment tiles, readable gameplay silhouettes, charming but mysterious post-apocalyptic atmosphere, warm nostalgic feeling, everyday-world objects mixed with ruined civilization and nature reclaiming everything.

Crisp pixel clusters, deliberate pixel placement, clean silhouettes, controlled dithering, rich readable shading, consistent perspective, consistent pixel scale, modular game-production-ready assets.

NO photorealism, NO 3D-rendered look, NO smooth vector art, NO painterly brushwork, NO blurry edges, NO excessive bloom, NO random perspective, NO characters unless specifically requested, NO UI, NO watermark.

Transparent background for isolated tiles and props. Output target: 4096 × 4096 PNG.

## PACK 01 — TERRAIN TILES

Create a complete modular REBORNER terrain tileset.

Include grass, tall grass, dirt, dry dirt, mud, cracked earth, gravel, stone, mossy stone, ruined concrete, broken asphalt, contaminated ground, glowing crystal ground, scorched ground, snow and ice.

For every terrain type create center, edges, inner corners, outer corners, transition tiles, decorative variants, damaged variants and overgrown variants.

Top-down / 3/4 perspective, seamless modular construction, consistent tile scale, transparent background.

## PACK 02 — ROAD & STREET

Create a modular post-apocalyptic road and street tileset for REBORNER.

Include straight roads, curves, diagonals, T-junctions, 4-way intersections, broken asphalt, cracks, faded lane markings, pedestrian crossings, sidewalks, curbs, drains, manholes, sewer covers, barriers, cones, damaged signs, street lamps, debris, collapsed roads, wooden bridges and broken bridges.

Create seamless transitions between asphalt, dirt, grass, ruins and water.

## PACK 03 — BUILDINGS & STRUCTURES

Create modular REBORNER buildings and structures in top-down / 3/4 isometric pixel art.

Include abandoned houses, shops, convenience stores, cafés, workshops, warehouses, apartments, offices, hospitals, schools, train-related buildings, industrial buildings, rooftops, water towers, communication towers, electrical towers, bridges, gates and fences.

Show five condition levels: intact, abandoned, damaged, heavily ruined, nature-reclaimed.

Use fictional Thai/Asian urban visual language and keep every building modular.

## PACK 04 — NATURE & DECORATION

Create a large REBORNER nature decoration tileset showing nature reclaiming civilization.

Include small/medium/large trees, dead trees, fallen trees, bushes, vines, flowers, grass clusters, mushrooms, roots, moss, ferns, tropical plants, rocks, boulders, branches, stumps and leaf piles.

Create normal, damaged, overgrown and mysterious variants.
Mix Southeast Asian vegetation with a nostalgic JRPG atmosphere.

## PACK 05 — PROPS & INTERACTIVE OBJECTS

Create a comprehensive REBORNER prop and interactive-object tileset.

Include wooden crates, cardboard boxes, barrels, trash cans, dumpsters, lockers, shelves, tables, chairs, benches, vending machines, refrigerators, generators, fuel containers, toolboxes, signs, lamps, street lights, cables, pipes, construction equipment, traffic cones, barriers, broken machines, treasure-like containers, save-point-like objects and mysterious glowing objects.

Create new, abandoned, damaged, broken and overgrown variants.

## PACK 06 — INTERIOR TILES

Create modular REBORNER interior tiles for abandoned buildings.

Include wooden floors, tile floors, concrete floors, cracked floors, carpets, walls, damaged walls, doors, windows, stairs, shelves, desks, counters, beds, sofas, cabinets, kitchen objects, bathroom objects, shops, workshops, classrooms, offices, storage rooms and laboratory-like rooms.

Create clean modular floor and wall transitions with warm indoor lighting and post-apocalyptic decay.

## PACK 07 — RUINS & POST-APOCALYPSE

Create a dedicated REBORNER ruined-city environment pack.

Include collapsed buildings, broken walls, exposed rooms, fallen concrete slabs, rubble, destroyed vehicles, abandoned buses and cars, broken signs, collapsed bridges, cracked streets, damaged power infrastructure, ruined shops, destroyed apartments, overgrown ruins, vines, abandoned camps and makeshift shelters.

The world should feel abandoned but not excessively grim: cute, mysterious, nostalgic JRPG storytelling.

## PACK 08 — WATER & COAST

Create a modular REBORNER water and coastline tileset.

Include shallow water, deep water, rivers, streams, ponds, lakes, ocean, shorelines, sandy beaches, rocky shores, wet ground, docks, wooden piers, broken boats, fishing objects, buoys, lighthouse elements, water debris and ruined coastal structures.

Create seamless water edges, corners and transitions.

## PACK 09 — LARGE PROPS / SET PIECES

Create large modular REBORNER environmental set pieces.

Include abandoned buses, train cars, ruined trucks, giant generators, water towers, wind turbines, industrial tanks, shipping containers, giant billboards, collapsed bridges, giant trees, giant rock formations, ruined towers, radio towers, factory machinery and large gates.

Keep the same 16-bit pixel-art universe, 3/4 isometric perspective and clear ground shadows.

## PACK 10 — SEASON / WEATHER VARIANTS

Create alternate versions of the same REBORNER environment tiles for five states:
1. Normal
2. Rain
3. Snow
4. Sandstorm / dry wasteland
5. Night

Apply variations consistently to terrain, roads, buildings, vegetation, props, ruins and water.

Do not redesign the objects between variants. Preserve identical geometry and gameplay readability.

## PACK 11 — SPECIAL / MYSTERIOUS AREAS

Create special REBORNER environmental tiles for mysterious late-game areas.

Themes: glowing ruins, underground structures, crystal growth, corrupted machinery, mysterious energy fields, abandoned laboratories, sealed doors, strange terminals, dimensional cracks, glowing plants, forgotten shrines, mechanical ruins and hidden chambers.

Keep the everyday-object foundation of REBORNER while introducing subtle supernatural elements.

## PACK 12 — SAMPLE SCENE / MAP COMPOSITION

Create six polished REBORNER sample maps demonstrating how the tiles assemble into playable scenes:

1. Abandoned city street reclaimed by vegetation
2. Forest settlement around old ruins
3. Coastal village with docks and ruined infrastructure
4. Abandoned factory district
5. Snowy mountain settlement
6. Mysterious neon-lit ruined district at night

Top-down / 3/4 isometric composition. Show believable paths, walkable areas, obstacles, points of interest and environmental storytelling. No UI and no characters.

## PACK 13 — TILE TECHNICAL SHEET

Create a clean technical reference sheet for REBORNER environment tiles.

Show base terrain tile, edge tile, inner corner, outer corner, transition tile, wall tile, road tile, water edge, bridge tile, decorative overlay and shadow overlay.

Recommended logical sizes:
32×32 px base tiles
64×64 px decorative objects
larger objects built from multiples of the base grid.

Keep artwork pixel-perfect and production-oriented.

## PACK 14 — CONSISTENCY LOCK

Match the existing REBORNER environment art direction exactly.

Same pixel density, 3/4 perspective, camera angle, object scale, lighting direction, shadow language, palette philosophy, outline treatment, pixel detail and post-apocalyptic warm/adventurous mood.

Do not introduce a new art style. Do not change perspective. Do not make assets more realistic. Do not add characters, UI or text.

## NEGATIVE PROMPT

photorealistic, realistic 3D render, low-poly 3D, vector art, smooth gradients, blurry pixels, anti-aliased edges, excessive bloom, excessive glow, painterly brush strokes, concept-art painting, random perspective, inconsistent scale, inconsistent lighting, modern realistic architecture, cyberpunk overload, horror gore, characters, people, text, watermark, logo, UI, HUD, frame, border, duplicated objects, malformed objects, floating objects, cut-off objects, excessive noise

## PRODUCTION WORKFLOW

Generate each pack separately rather than attempting the entire library in one image:

1. Terrain
2. Road
3. Buildings
4. Nature
5. Props
6. Interior
7. Ruins
8. Water
9. Large Props
10. Weather
11. Special Areas
12. Sample Scenes
13. Technical Sheet

Target: 4096×4096 PNG per generated sheet, then crop/repack assets into game atlases.

## REBORNER ART DIRECTION

Everyday objects become important again.

The world has collapsed, but it is not empty.
Nature returns.
Old technology remains.
Ordinary objects become weapons, tools and landmarks.

Cute + mysterious + nostalgic + adventurous.
Modern 16-bit pixel-art JRPG.
Thai post-apocalyptic identity.
Readable gameplay first.
Atmosphere second.
Detail third.

## FINAL MASTER PROMPT

Create a professional 4K REBORNER environment tileset for a 2D Thai post-apocalyptic JRPG.

Original hand-crafted modern 16-bit pixel art, SNES-era quality, DQ7 × Romancing SaGa 3 quality bar, cute warm mysterious atmosphere, everyday civilization reclaimed by nature.

Top-down / 3/4 isometric perspective. Modular game-ready tiles. Consistent pixel density, camera, scale and lighting. Crisp pixel clusters, readable gameplay silhouettes, rich material definition and transparent background for isolated assets.

Create only the requested environment category. No characters, UI or unrelated objects. No photorealism, smooth vector graphics, 3D-rendered aesthetics, blur or anti-aliasing.

Output as a polished 4096×4096 PNG reference sheet suitable for building the REBORNER game world.
