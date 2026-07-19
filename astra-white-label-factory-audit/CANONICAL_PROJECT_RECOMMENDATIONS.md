# Canonical Project Recommendations

Per product family. "No candidate in scope" means nothing was observable in
this session — it does **not** mean nothing exists on the Mac.

| # | Product family | Canonical recommendation | Confidence | Basis |
|---|---|---|---|---|
| 1 | Travel platforms | **`luxor-guest-house`** (provisional) | Medium | Only travel app in scope; tested, CI-green, deploy-ready, ledger-driven content. **Must be challenged against Atlas Voyage / Voyara on the Mac before final** — the brief describes Atlas Voyage as an existing white-label travel workflow, which (if functional) may outrank a single-property prototype for the *template* role. |
| 2 | Hotel & hospitality | `luxor-guest-house` (adjacent coverage) | Low | A guest house is a small hotel; rooms/booking/enquiry flows transfer. Hotel OS Modular Platform not observable. |
| 3 | Restaurant platforms | No candidate in scope | — | Marina Ember + Hurghada Restaurant Opportunity Platform not observable. |
| 4 | Health & pharmacy | **`rxegypt-pilot`** | High | 70 tests, migrations, auth/roles, audit trail, PDPL rights, payments scaffold, CI, deploy config. Strongest engineering in scope, period. |
| 5 | Compliance & safety | `rxegypt-pilot` compliance modules (as capability donor, not a product) | Medium | Rx gating, consent logging, audit trail, human-verification queue are exactly the primitives SafePlate/REYEYE-class products need. |
| 6 | Legal & case management | No candidate in scope | — | EQUALISE not observable. |
| 7 | Residential & compound | No candidate in scope | — | Compound OS not observable. |
| 8 | Command centres & orchestration | No candidate in scope | — | Bruce OS/Dashy/The Hive/Family ELM/OmniCore/BridgeOS not observable. Dashy is third-party — it is a *consumer* of the factory registry, not a factory product. |
| 9 | Shared infrastructure & component libraries | **AISE design-token contract** (`DESIGN_SYSTEM.md`) | High | Already implemented by two brands; the factory's first package. |
| 10 | Archived experiments | None identified | — | Nothing in scope qualifies; archiving decisions deferred to the Mac audit. |
| 11 | Unknown / unclassified | 23 named-but-not-observable projects | — | Held in `project-registry.json → namedButNotObservable` without forced classification, per the brief. |

## Explicit non-forcing note

The brief instructs not to force uncertain projects into categories. Families
3, 6, 7, 8 therefore have **no canonical recommendation yet** rather than a
guessed one.
