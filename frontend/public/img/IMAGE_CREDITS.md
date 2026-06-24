# Luxor imagery — placeholders & how to swap in real photos

The `.svg` files here are **license-clean placeholders authored in this repo**
(no third-party rights, safe to ship). They replaced the previous LoremFlickr
hotlinks, which pulled random, unlicensed images and failed to load offline.

## Slots

| File | Used by (`src/styles.css`) | Subject |
|---|---|---|
| `hero.svg` | `.hero` | Luxor / Nile panorama |
| `valley.svg` | `.ph-valley` | Valley of the Kings |
| `hatshepsut.svg` | `.ph-hatshepsut` | Temple of Hatshepsut |
| `balloon.svg` | `.ph-balloon` | Hot-air balloon |
| `boat.svg` | `.ph-boat` | Nile felucca |
| `village.svg` | `.ph-village` | West Bank village |
| `suite.svg` | `.ph-suite` | Guest suite interior |
| `map.svg` | `.ph-map` | Location map |

## Swapping in real photos

1. Source **public-domain / CC0 / CC-BY** photos (see below). Prefer ~1600×900
   for the hero, ~800×600 for tiles. Compress (JPEG/WebP) for fast loads.
2. Save each into this folder, e.g. `hero.jpg`, `valley.jpg`, …
3. In `frontend/src/styles.css`, change the matching `url('/img/<name>.svg')`
   to `url('/img/<name>.jpg')`. The brand-gradient fallback layer can stay.
4. `npm run build` and verify.
5. For **CC-BY** images, record attribution in the "Credits" section below
   (author + source URL + licence) — required by the licence.

> Note: this environment's network policy blocks image hosts, so the photos
> could not be fetched here. Fetch them from a normal network or attach them.

## Recommended free sources (verify the licence on each file)

- **Wikimedia Commons** — filter to *Public domain* or *CC0*:
  - Valley of the Kings: `commons.wikimedia.org/wiki/Category:Valley_of_the_Kings`
  - Temple of Hatshepsut: `.../Category:Mortuary_Temple_of_Hatshepsut`
  - Karnak / Luxor Nile: `.../Category:Nile_in_Luxor`, `.../Category:Karnak`
  - Feluccas: `.../Category:Feluccas_on_the_Nile`
  - Ballooning over Luxor: `.../Category:Hot_air_ballooning_in_Egypt`
- **Openverse** (`openverse.org`) — filter licence to CC0 / Public Domain.
- **Unsplash / Pexels** — free to use (Unsplash/Pexels licence; not strictly
  "open source" but permissive and attribution-free). Search "Luxor", "Nile
  felucca", "Valley of the Kings".

## Credits

_(none yet — placeholders are original to this repo, CC0. Add real-photo
attributions here when you swap them in.)_

---
🌿 ✦ ASTRA INTELLIGENCE SERVICES ✦ 🌿 | ⚜ MISR ⚜
