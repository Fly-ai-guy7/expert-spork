# EQUALISE Design Review

Applied the premium-saas-design Define → Build → Review → Refine loop
to the state of the UI on branch `claude/todo-implementation-JmYwU`.
Forward-looking: lists the next concrete refinements, not a celebration.

## Define (Intended Experience)

A trainee lawyer should:

1. Land on **Training Dashboard** and start a practice case in ≤3 clicks.
2. Read **Case Detail** as a courtroom debate — prosecution vs. defense
   stacked side by side, judicial ruling and trainee turn distinct.
3. Receive a **Coaching Report** whose *grade* is the visual focal
   point, not the page title.
4. Trust every screen as a serious legal artifact — never decorative,
   always disclaimed, fully bilingual.

The brand voice is Sage with Ruler accents (`docs/design-tokens.md`):
deep navy authority, generous whitespace, no marketing flourish.

## Build (What's Shipped on This Branch)

| Surface | State |
|---|---|
| Training Dashboard | H1 hierarchy fixed, CTA separated from filter grid, sessions list localized |
| Case Detail | H1 + meta chips, all section headers localized, untitled fallback through t() |
| Case List | Pill-chip meta, full i18n, consistent H1 |
| New Case / Statutes / Coaching Report | H1 hierarchy unified, all hardcoded strings localized |
| Shared components | Dialog ARIA semantics, LangToggle aria-label localized, role colors tokenized |
| PDF reports | Party role enums now render `المدعي` / `Plaintiff` instead of raw `PLAINTIFF` |
| Tokens | `role.{prosecution,defense,judicial,trainee}` in tailwind.config; `font-arabic` wired up |

## Review (What's Still Off)

Honest gaps the skill's checklist would flag:

1. **No focus styles on interactive elements.** Buttons, links, and
   selects rely on browser defaults. A trainee using a keyboard can't
   see what's focused. Per design-principles a11y: critical fix.
2. **No loading skeletons.** Every page returns `<p>{t("loading")}</p>`
   as a layout-shifting full-page swap. Page chrome should stay; the
   data area should skeleton.
3. **Dialog has no Escape-to-close and no focus trap.** ARIA is now
   correct but keyboard UX is incomplete.
4. **PipelineTimeline labels overflow on mobile.** 7 chips in a row
   wrap awkwardly under 400px. Needs a vertical or scroll variant.
5. **CaseDetail mixes side-by-side Prosecution/Defense with a stacked
   Trainee/Judicial block below.** Reading order isn't obvious — a
   debate is chronological, but the layout implies parallelism.
6. **Empty states are bare.** "No training sessions yet." is correct
   but does nothing to nudge action. Should suggest "Start a case →".
7. **No dark mode.** Likely fine to defer, but worth naming.

## Refine (Targets — Status)

### 1. Global focus styles ✓ Done

Added a `@layer base` rule in `frontend/src/index.css` that applies
`outline-none ring-2 ring-brand ring-offset-2` to every focused
button / link / input / select / textarea / role=button / tabindex
element. Keyboard focus is now visible across the whole app without
touching individual components.

### 2. PipelineTimeline mobile variant ✓ Done

`PipelineTimeline.tsx` now stacks vertically with a monospace step
number below `md:` and renders as horizontal pills at `md:` and up.
The active step gets bold weight on desktop for stronger emphasis.

### 3. Empty-state nudges ✓ Done

- TrainingDashboard: empty session list now renders as a centered card
  with a hint ("Pick your filters above and start your first practice
  case.") instead of a single grey line.
- CaseListPage: empty state now includes a brand-colored
  "Create your first case" link to `/cases/new`.

## Remaining (Separate Workstreams)

- Dialog focus trap + Escape-to-close (ARIA is correct; keyboard UX is
  incomplete).
- Debate reading order on CaseDetail (chronological flow vs. current
  parallel-column layout).
- Dark mode.

## How to Run the Loop Again

When picking up: pick **one** Refine target, do Define→Build→Review for
that target alone in a fresh session, and append the outcome to this
doc. Don't re-audit the whole system every time.
