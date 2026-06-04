# EQUALISE Design Tokens & Context

A compact reference for LLM-driven UI work on this project. Read this
before generating or modifying any UI — it captures the brand layer,
token layer, component patterns, and the design decisions made on
this branch.

## Brand Layer

- **Product**: EQUALISE Egypt — AI legal simulation for trainee lawyers.
- **Archetype**: Sage (truth/knowledge) with Ruler accents (authority).
- **Voice**: clear, deliberate, never flippant. Legal context demands it.
- **Audience**: trainee lawyers practicing in Arabic and English.
- **Disclaimer constraint**: every user-facing surface (UI + PDF) must
  carry the "AI Simulation Only — Not Legal Advice" notice. Never style
  it away.

## Token Layer

Defined in `frontend/tailwind.config.js`. Compressed view:

```json
{
  "colors": {
    "brand": {"DEFAULT": "#11214d", "50": "#f4f6fb", "100": "#e8eef9", "900": "#0a173a"},
    "role": {
      "prosecution": "#11214d",
      "defense":     "#f43f5e",
      "judicial":    "#10b981",
      "trainee":     "#f59e0b"
    }
  },
  "fontFamily": {
    "sans":   ["Inter", "system-ui", "sans-serif"],
    "arabic": ["Noto Naskh Arabic", "Amiri", "serif"]
  }
}
```

Neutrals come from Tailwind's `slate-*` scale. Pipeline state colors
(`emerald-*`/`amber-*`/`slate-*`) are raw Tailwind — not role colors,
don't tokenize them.

## Component Patterns

| Pattern | Classes |
|---|---|
| Page H1 | `text-3xl md:text-4xl font-bold text-slate-900` |
| Section H2 | `text-lg font-medium mb-3` (or `text-sm font-semibold mb-2` inside cards) |
| Card / panel | `bg-white rounded-lg border p-6` |
| Primary CTA | `rounded-md bg-brand px-6 py-2.5 text-sm font-semibold text-white disabled:opacity-50` |
| Pill chip (meta) | `rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700` |
| Debate card | left border = `border-l-4 border-l-role-{prosecution\|defense\|judicial\|trainee}` |
| Dialog | `role="dialog" aria-modal="true" aria-labelledby="<h2 id>"`; overlay `fixed inset-0 z-40 bg-black/40` |
| Disclaimer | `bg-rose-50 border-rose-200 text-rose-900` (semantic warning) |

## i18n Rules

- All user-facing strings go through `t()` — including `aria-label`,
  `placeholder`, and fallback values like `(untitled)`.
- Bilingual content has paired `_en` / `_ar` fields; render with
  `i18n.language === "ar" ? x_ar : x_en` and fall back to the other.
- Tailwind direction-agnostic utilities (`flex`, `grid`, `gap`) flip
  visually with `dir="rtl"`. Use logical CSS overrides only when needed
  (see `argument-block` in `backend/app/reports/styles.css`).
- Hardcoded English in code = blocker. Add a key in `src/i18n/en.json`
  and `ar.json` first.

## Hierarchy Rule (Visual Focal Point)

Only one element per page should own brand color:
- H1 = neutral (`text-slate-900`), so the **CTA** owns `bg-brand`.
- Exception: CoachingReportPage's grade chip owns brand color because
  the grade *is* the focal point of the page.

## Decisions Log

Track non-obvious choices so future sessions don't re-litigate them:

1. **Role colors tokenized in tailwind.config** (`role.prosecution/defense/judicial/trainee`).
   Rationale: prevents drift between `DebateRoundCard` and any future role-aware UI.
2. **Pipeline state colors NOT tokenized.** They mean "done/active/pending",
   not "judicial/trainee". Semantic separation, even though emerald is reused.
3. **Page H1 hierarchy** uses `text-3xl md:text-4xl font-bold text-slate-900`
   across all 5 pages. Don't reach for `text-brand` on H1.
4. **Meta strings as pill chips** (status / source / area / difficulty)
   instead of `·`-separated text. Easier to scan, easier to translate.
5. **PDF party roles** are translated via `PARTY_ROLE_LABELS_{EN,AR}` maps
   injected through `pdf_service.render_html` — never `{{ p.role }}` raw.
6. **`fontFamily.arabic` is wired up** via `@apply font-arabic` in the
   `html[dir="rtl"] body` selector — single source of truth for the font stack.

## Adding to This Doc

When you make a non-obvious design choice during a session, add a line
to the Decisions Log. When you add a new component pattern that gets
reused, add a row to Component Patterns. Keep the doc compact — the
goal is fast LLM context, not exhaustive documentation.
