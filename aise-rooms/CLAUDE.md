# CLAUDE.md — AISE Rooms

Project conventions for the AISE Rooms interior-design tool. Ref:
`SKILL-3DR-003-SPRINT`.

## Golden rule

**This is a single self-contained file: `index.html`. No build step, no
bundler, no framework.** Three.js / jsPDF / pako load from CDN. Keep it that
way — fast iteration and "copy file → edit config → deploy" is the product.

## File map (inside `index.html`)

1. `<style>` — all CSS, driven by CSS vars `--brand` / `--accent`.
2. `AISE_CONFIG` — the white-label control object. **All branding,
   currency, room subset, and feature flags go here.** Never hardcode a
   brand colour or currency elsewhere.
3. `RETAILERS` + `RETAILER_MULT` — supplier list and price posture.
4. `CATALOGUE` — flat array of catalogue items, one object each.
5. `PRESETS` — per-room default dimensions + starting layout.
6. Three.js scene / lights / groups (`roomGroup`, `furnitureGroup`).
7. `buildRoomShell` — refactored room geometry, dimension-driven.
8. `buildShape` — procedural furniture builders, keyed by `shape`.
9. Drag system (Pointer Events + raycaster + drag plane).
10. 2D plan, catalogue UI, BOM/cost panel.
11. State: `buildRoomState` / `restoreFromState`, save, share, PDF.

## Catalogue item shape

```js
{ id:'l_sofa3', name:'3-Seat Sofa', room:'living',
  w:2.2, d:0.92, h:0.82,        // metres; origin at floor, centred on x/z
  shape:'sofa',                  // → buildShape() switch key
  color:0x6d7b8d,                // base colour
  base:18500 }                   // base EGP; final = base × retailer mult
```

- `id` is unique and prefixed by room (`l_`, `k_`, `lo_`, `b_`).
- Price is **always** derived via `priceFor(id, retailerIndex)` — never store
  per-retailer prices by hand.

## Room geometry conventions

- Units are **metres**. World origin is the room centre; floor is `y = 0`.
- Room spans `[-W/2, W/2]` × `[-D/2, D/2]`; height `H`.
- Furniture meshes are built so their **base sits on `y = 0`** and they are
  centred on local x/z. `buildShape` must honour this for new shapes.
- Furniture is clamped to room bounds via `clampX` / `clampZ` (0.4 m margin).
- Drag snaps to a **0.1 m grid**.
- A new furniture `shape` = add a `case` in `buildShape` returning a
  `THREE.Group`, then reference it from `CATALOGUE`.

## Adding a room type

1. Add a key to `PRESETS` with `dims` + `items` (`{id,x,z,rotY}`).
   Use `ref:` on an item to reuse a catalogue id for a duplicate (e.g. a
   second stool) without colliding ids.
2. Add catalogue items with `room:'<type>'`.
3. Add the type to `AISE_CONFIG.rooms`.

## State / share invariants

- `buildRoomState()` is the single source of truth for save / share / load.
  If you add a persisted property, update both `buildRoomState` **and**
  `restoreFromState`.
- Share URLs use a 1-char codec prefix: `p` = pako-deflated, `r` = raw base64.
  Keep decoding backward-compatible.

## Don'ts

- Don't introduce a build tool or npm install for the runtime app.
- Don't break the single-file deploy story.
- Don't put the model identifier or internal notes into shipped files.
