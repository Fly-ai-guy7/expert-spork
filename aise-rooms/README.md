# AISE Rooms — Interior Design Tool (v1.0)

A browser-based 3D room designer for the Egypt / MENA market. Hotel partners,
developers, and homeowners visualise a furnished space, drag furniture into
place, pick a supplier per item, and export an instant EGP cost sheet — no app
download, no account.

**Everything is one self-contained file: [`index.html`](./index.html).**
Zero build step. Open it in a browser, or serve it statically.

```bash
# Run locally
cd aise-rooms
python3 -m http.server 8080
# → http://localhost:8080
```

## v1.0 Features

| Feature | Status |
|---|---|
| 3D room render (Three.js r163) | ✅ |
| Full orbit / pan / zoom (OrbitControls) | ✅ |
| Transparent overhead **Plan** view | ✅ |
| 2D floor-plan canvas (used in PDF) | ✅ |
| Room types: Living, Kitchen, Lounge, Bedroom | ✅ |
| Room selector tabs | ✅ |
| Catalogue sidebar (40 items) | ✅ |
| Cost panel + per-item retailer switching | ✅ |
| **Drag-to-reposition** (Pointer Events, mouse + touch) | ✅ |
| Grid snap (0.1 m) + footprint + highlight while dragging | ✅ |
| Double-tap / double-click to rotate (22.5° steps) | ✅ |
| Room dimension setup screen | ✅ |
| CSV export | ✅ |
| **Save / load** to localStorage (+ 30 s autosave) | ✅ |
| **Share via URL** (pako-compressed state) | ✅ |
| **PDF export** (jsPDF: cover + 3D + plan + BOM) | ✅ |
| GLB loader architecture w/ procedural fallback | ✅ |
| Loading progress screen | ✅ |
| White-label config (one object) | ✅ |
| Mobile controls, large tap targets, double-tap zoom blocked | ✅ |

## White-label in under 5 minutes

All branding lives in the `AISE_CONFIG` object at the top of the `<script>` in
`index.html`:

```js
const AISE_CONFIG = {
  brandName:    'AISE Rooms',     // → 'Arena Beach Interiors'
  brandLogo:    null,             // → URL to hotel logo
  primaryColor: '#0058A3',        // → hotel brand colour
  accentColor:  '#FFDA1A',        // → hotel accent
  currency:     'EGP',            // → 'USD' | 'EUR'
  eurRate:      53,               // EGP per EUR
  showPricing:  true,             // → false for design-only mode
  rooms:        ['living','kitchen','lounge','bedroom'], // subset per property
  footerText:   'Powered by AISE Rooms',
  useGLB:       false,            // flip on once GLB assets/CDN are wired
};
```

**Per-hotel deployment:** copy `index.html` → edit `AISE_CONFIG` → deploy to
`{hotel}.aise-rooms.com`. Budget ~2 hours per new property.

## Sharing

The **Share** button serializes the room state (type, dimensions, every item's
position / rotation / chosen retailer), deflates it with `pako`, base64-encodes
it into `?room=…`, and copies the link to the clipboard. Opening that link
restores the exact room — no backend.

## Deploy (Fly.io static)

A static `Dockerfile` is included. From this directory:

```bash
fly launch --no-deploy   # first time only
fly deploy
```

## Tech

Three.js r163 · jsPDF 2.5.1 · pako 2.1.0 — all from CDN. DRACO + GLTF loaders
are wired for future photoreal GLB models, with graceful fallback to the
procedural proxy meshes if a model fails to load.
