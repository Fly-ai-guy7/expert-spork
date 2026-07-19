# Risks and Unknowns

## Unknowns (honest gaps in this audit)

| # | Unknown | Impact | Resolution |
|---|---|---|---|
| U1 | **The Mac's filesystem was not audited** — 23 named projects unobserved; the audited repo may be a small fraction of the estate | Canonical/pilot recommendations are provisional for the travel family | Step 0 of `MIGRATION_SEQUENCE.md` |
| U2 | Atlas Voyage's existence, quality and white-label maturity | Could change the travel-template donor decision | Mac audit |
| U3 | Marina Ember status | Restaurant pilot undefined until inspected | Mac audit |
| U4 | Identity of the Mac's port-3000 service; Dashy's actual links | Port registry incomplete | `lsof` checks on the Mac |
| U5 | Whether standalone forks of Luxor/RxEgypt exist on the Mac (e.g. "Luxor Smart Trip Planner", a standalone "RXEGYPT") | Possible unmerged features / divergent lines | Lineage checklist in `DUPLICATION_REPORT.md` |
| U6 | Mac-side Claude Code config, versions, memory | Operating-layer plan may need adjustment | Mac audit |
| U7 | Whether other GitHub repos exist beyond `expert-spork` (session was repo-scoped; org listing not permitted) | Registry completeness | List repos from an authorised session |

## Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| K1 | **Template extraction quietly breaks the working Luxor app** | Med | High | Never modify the donor; extract into the factory; original retired only after its client instance passes QA in production (principle 2) |
| K2 | Premature abstraction: building 14 packages for 2 products creates maintenance surface with no consumers | High if brief followed literally | Med | Amendment 1 in the architecture proposal: 4 seeded packages; "second consumer" rule |
| K3 | RxEgypt compliance risks leak into the factory narrative (heuristic Rx flags, unsigned PSA) if it is white-labelled early | Med | High (legal/patient safety) | Pharmacy template is pilot 3, gated on R1–R3 |
| K4 | Port collisions during multi-app local dev (8000/8000 confirmed; 8080 vs Dashy; 4173 vs Atlas Voyage) | High | Low each, corrosive over time | Adopt `registry/ports.json` assignments in step 2 |
| K5 | PII exposure if Luxor deploys publicly before auth (finding L1) | Med | High | L1 is a hard gate in the pilot plan |
| K6 | Skill-ecosystem conflict: Compound OS governance skills vs new factory commands; `aise-deploy-monitor` assumes a Vercel+Supabase stack this repo doesn't use | Med | Med | Register factory commands with `skill-governor`; reconcile stack assumptions before deployment automation (CLAUDE_CODE_AUDIT addendum) |
| K7 | Mixed frontend stacks (React vs static HTML) tempt a rewrite-everything move | Med | Med | Factory explicitly supports heterogeneous templates; contracts (tokens/schemas) are the shared layer, not a single framework |
| K8 | Free-tier ephemeral storage loses booking PII silently | High (until fixed) | Med | Persistent disk / managed DB before relying on data (Luxor's own docs) |
| K9 | Two brands' facts drift (WhatsApp number duplicated in JSX + ledger; rating literals) | Present today | Low-Med | Single-source-of-truth rule enforced during extraction |
| K10 | This audit itself goes stale as the Mac audit lands | Certain | Low | Registries are the living artefact; markdown docs dated; `/discover-local` re-runs refresh them |
