# AISE Design-Token Contract

_One design system, two brand palettes. Last updated 2026-06-24._

AISE products share a **single set of semantic CSS custom-property names** (the
"token contract"). Each product implements the contract with its own brand
palette, so the engineering approach to theming is consistent while each product
keeps its own identity.

The two products can't share a single CSS file (different stacks/deploys), so the
contract is the shared artefact:

| Product | Stack | Token source |
|---|---|---|
| Luxor Guest House | React + Vite | `frontend/src/styles.css` (`:root`) |
| RxEgypt Pilot | Static HTML/CSS | `rxegypt-pilot/frontend/theme.css` (`:root`) |

## The contract — semantic token names

Every AISE product defines these in `:root`. Use the semantic name in component
CSS; never hard-code a hex value that a token already covers.

| Token | Meaning | Luxor value | RxEgypt value |
|---|---|---|---|
| `--ink` | Primary text | `#2b2620` | `#1c2421` |
| `--muted` | Secondary text | `#6b6358` | `#6b756e` |
| `--line` | Borders / dividers | `#e6ddcd` | `#cfd6d1` |
| `--sand` | App background / surface tint | `#f1e7d2` | `#f6f4ee` |
| `--accent` | Brand accent (primary action) | `--gold` (`#c79a3a`) | `--green` (`#1f7a4d`) |
| `--accent-d` | Accent, darker (hover / headings) | `--gold-d` (`#a87f26`) | `--green-d` (`#14573a`) |
| `--radius` | Default corner radius | `14px` | `8px` |
| `--shadow` | Default elevation | soft warm | soft neutral |

**`--accent` is the bridge.** Shared/portable components should reference
`--accent` / `--accent-d` rather than a product-specific colour name, so the same
markup renders on-brand in either product.

### Product-specific tokens (not part of the shared contract)

- **Luxor:** `--gold`, `--gold-d`, `--nile`, `--cream`, `--body`, `--dark`,
  `--wa`, `--serif`, `--sans`.
- **RxEgypt:** `--green`, `--green-d`, `--rx` (prescription red).

These stay product-local; `--accent` aliases the brand colour into the shared
vocabulary.

## Conventions

- **Box-sizing reset:** `* { box-sizing: border-box; }` in every product.
- **Badges/buttons:** RxEgypt centralises `.rx-badge`, `.otc-badge`,
  `.btn-primary` in `theme.css`; Luxor uses `.btn` + `.btn-gold` etc. Button
  geometry (radius, padding, weight) should track `--radius`.
- **Single source of truth:** within a product, declare tokens once
  (RxEgypt: `theme.css`; Luxor: `styles.css`) — don't re-declare `:root` per page
  (RxEgypt pages were de-duplicated to follow this).

## Adding a new AISE product

1. Copy the token contract into the product's root stylesheet.
2. Set brand values for `--accent` / `--accent-d` and the surface/text tokens.
3. Keep brand-only colours as product-local tokens.
4. Reference `--accent` (not the raw brand colour) in any shareable component.

---
🌿 ✦ ASTRA INTELLIGENCE SERVICES ✦ 🌿 | ⚜ MISR ⚜
Portfolio · Design-Token Contract · 2026-06-24
