# Project Status — Astra White-Label Factory (Audit Phase)

_Last updated: 2026-07-15_

## Phase state

| Phase | State | Notes |
|---|---|---|
| 1 — Environment audit | ✅ complete (remote scope) | Mac-side capture outstanding |
| 2 — Localhost/process audit | ✅ complete (remote scope) | 0 services running here; Mac ports unverified; 8000-collision confirmed from repo evidence |
| 3 — Project discovery | ✅ complete for reachable estate | 2 confirmed apps fully profiled; 23 named projects registered as not-observable |
| 4 — Duplication & lineage | ✅ complete for reachable estate | Sibling pair, not forks; Mac checklist prepared |
| 5 — Reusability analysis | ✅ complete | 30+ capabilities ranked; 4 P0s identified |
| 6 — White-label readiness | ✅ complete | Luxor 5/10 (2–4 days to convert), RxEgypt 5/10 (1–2 weeks) |
| 7 — Factory architecture | ✅ proposed | With 3 evidence-based amendments to the brief's structure |
| Client config schema | ✅ proposed | With validation rules |
| Operating layer | ✅ adoption plan | Reconciled against existing Compound OS skills |
| QA automation | ✅ plan | 19 stages, 3 rollout waves |
| **Overall audit-phase completion** | **~70%** | The remaining ~30% is the Mac-side discovery (Step 0), which this session could not physically reach |

## Executive summary

1. **Environment:** healthy modern toolchain (Node 22, Python 3.11, Docker,
   Claude Code 2.1.210) in the remote container; the audited environment is
   Linux, not the Mac — macOS-side facts are explicitly marked unverified.
2. **Directories inspected:** the full `expert-spork` tree (~110 files),
   `/home/user`, and the container home; the Mac's search areas are pending.
3. **Candidate projects found:** 3 (2 applications + 1 shared design
   contract).
4. **Confirmed application repositories:** 2 — Luxor Guest House MVP,
   RxEgypt Pilot. Both CI-covered, Docker-ready, documented.
5. **Active localhost services:** 0 in the audited environment.
6. **Port conflicts:** 1 confirmed (both backends default to 8000); 2 latent
   (nginx container vs Dashy on 8080; Vite preview vs Atlas Voyage on 4173).
7. **Unidentified running services:** none here; the Mac's :3000 remains
   unidentified (candidate: RxEgypt static frontend).
8. **Duplicate/related groups:** 1 (Luxor+RxEgypt as convention-sharing
   siblings); external lineage checks pre-scripted for the Mac.
9. **Strongest canonical per family:** travel → Luxor (provisional);
   health/pharmacy → RxEgypt (high confidence); shared-infra → AISE token
   contract; 8 families have no observable candidate.
10. **Strongest reusable components:** design-token contract (P0), runtime
    config injection (`docker-entrypoint.sh` + `config.js`), JWT/role auth,
    token-driven UI kit (buttons/cards/forms/KPIs), photo-slot system.
11. **Strongest reusable workflows:** booking-enquiry funnel, WhatsApp
    contact/verification flows, deterministic no-LLM concierge, Rx-style
    human-verification queue, PDPL consent + data-subject rights, audit
    trail, provenance-verified content import.
12. **White-label readiness:** Luxor 5/10, RxEgypt 5/10 — both have the
    right bones (externalised content / env-driven config) with brand baked
    into the frontends.
13. **Recommended shared packages (initial):** design-tokens, config, auth,
    integrations — the other ten in the brief wait for a second consumer.
14. **Recommended templates (initial):** guesthouse (from Luxor), then
    restaurant (donor TBD), then pharmacy (from RxEgypt, gated).
15. **Recommended pilots:** 1) Luxor → travel template + client instance #1;
    2) restaurant (Marina Ember pending inspection); 3) RxEgypt pharmacy.
16. **Factory architecture:** adopted from the brief with amendments —
    4 seeded packages not 14; templates follow evidence; the factory never
    absorbs running repos until QA-proven (see proposal doc).
17. **Operating layer:** 9 commands + 5 subagents phased A/B/C, explicitly
    reconciled with the existing Compound OS skill ecosystem.
18. **Major security findings:** Luxor's unauthenticated PII endpoints
    (high, on deploy); RxEgypt's heuristic Rx flags pending EDA
    reconciliation (high, compliance); no committed secrets anywhere.
19. **Major migration risks:** breaking working apps during extraction,
    premature abstraction, pharmacy compliance leakage, port collisions —
    all with mitigations in `RISKS_AND_UNKNOWNS.md`.
20. **Recommended order:** Mac discovery → decisions gate → skeleton +
    tokens → travel pilot → synthetic client #2 → restaurant → shared
    backend packages → pharmacy → registry-driven ops.
21. **Current priority:** complete the Mac-side discovery
    (`CURRENT_PRIORITY.md`).
22. **One next action:** run the Phase-0 discovery pass on the Mac and merge
    into the registries (`NEXT_ACTION.md`).
23. **Phase completion:** ~70% of the audit phase; 0% of the build phase
    (by design — stop condition honoured).

## Stop condition — honoured

No components extracted, no monorepo created, no refactoring of active
projects, nothing installed, Dashy untouched, nothing deployed/migrated/
archived, no changes committed to application source. The only writes are
this audit directory on the designated audit branch.
