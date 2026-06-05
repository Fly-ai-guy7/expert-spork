# Architecture

This document maps the EQUALISE diagram to actual code modules.

## Pipeline overview

```
POST /api/cases (or /generate)
        ↓
POST /api/cases/{id}/run (or /run-training)
        ↓
[orchestrator.run_simulation]
        ├── 1. EvidenceMigrationAgent
        │     → writes Fact, Evidence rows
        │     → HilCheckpoint(POST_EVIDENCE)
        ├── 2. Debate loop (default 3 rounds)
        │     ├── ProsecutionAgent → Argument + Score
        │     ├── (TRAINEE_TURN checkpoint if training mode)
        │     └── DefenseAgent → Argument + Score
        │     ↻ swap LLMs between rounds
        ├── 3. JudicialCouncilAgent → Ruling row + CouncilVerdict rows (one per member)
        │     → HilCheckpoint(PRE_RULING)
        ├── 4. Judicial override (rerun on weakest argument)
        ├── 5. Outcome row
        └── 6. coaching_service.generate_coaching_report (training only)
        ↓
Case status = COMPLETE
```

Every stage persists to the database before moving on. The orchestrator is idempotent — if a
stage already produced its row, it skips it. This means HIL / TRAINEE_TURN checkpoints can pause
and resume cleanly.

## Module map

| Diagram component | Code |
|---|---|
| Case input | `POST /api/cases` (`routers/cases.py:create_case`) |
| AI-generated case | `services/case_generator.py:generate_case` |
| Evidence Migration LLM | `agents/evidence_migration.py` |
| Prosecution Agent | `agents/prosecution.py` |
| Defense Agent | `agents/defense.py` |
| Judicial Council (multi-LLM panel) | `agents/judicial_council.py` (members are `agents/judicial.py`) |
| Council member verdicts | `models/council.py` (`council_verdicts`), `services/orchestrator.py` step 3 |
| Advisory Counsel (trainee mentor) | `agents/advisory_counsel.py`, `services/counsel_service.py`, `POST /api/hil/{cp_id}/counsel` |
| Scoring Layer | `agents/scoring.py` |
| HIL / Trainee Seat | `routers/hil.py`, `services/orchestrator.py` (TRAINEE_TURN handling) |
| Cross-LLM Debate | `services/orchestrator.py` (PROSECUTION_LLM_BY_ROUND / DEFENSE_LLM_BY_ROUND) |
| 100% Legal Law-Based | Scoring agent's `legal_law_based` dimension + statute citations |
| Ultimate Authority Override | JudicialAgent's `override_applied` field |
| Ruling | `models/ruling.py`, written by orchestrator step 3 |
| Pretrial Resolution + Outcome | `models/outcome.py`, written by orchestrator step 4 |
| Coaching Report | `services/coaching_service.py`, `training_sessions.coaching_report` jsonb |
| Statute Corpus | `corpus/*.json` loaded via `app/corpus_loader.py` |
| PDF Export | `services/pdf_service.py` (WeasyPrint, bilingual templates) |

## Persistence

PostgreSQL schema. Every table includes a UUID PK and `created_at`/`updated_at` via the
`TimestampMixin`. Bilingual content lives in side-by-side `_ar`/`_en` columns (no separate
translation table — the scaffold prioritizes simplicity over normalization).

Relationships:

```
cases ──< parties
       ──< facts
       ──< evidence
       ──< debate_rounds ──< arguments ──── scores
       ──< arguments              (also via debate_round_id)
       ──< hil_checkpoints
       ──< training_sessions
       ──── ruling (1:1) ──< council_verdicts
       ──── outcome (1:1)
statutes ──< statute_articles
```

## Background execution

Simulation runs in FastAPI's `BackgroundTasks`. For production scale, swap in
Celery or RQ; the orchestrator is already designed to take a `Session` and a case_id, so the
swap is contained.

## Deferred (explicitly NOT in scaffold)

- K8s manifests — see `infra/k8s/README.md`
- Authentication / authorization — `created_by` is a plain string
- Full statute text — 5–10 articles per code
- The three feedback loops (Feedback / Criterial / PTRL) as actual retraining — modeled
  as DB rows + log events only
- Court of Cassation precedent DB — referenced conceptually by the JudicialAgent
- Auto-translation between Arabic/English — agents emit in `language_primary`
- Streaming responses (SSE / WebSocket)
- OTel / Sentry / rate limiting / quota enforcement
- Mobile UI

## Disclaimer enforcement

- Backend: every agent's system prompt is prefixed with `SYSTEM_DISCLAIMER_PREFIX` from
  `app/disclaimer.py`
- Every PDF page footer is rendered via `@page { @bottom-center }` in `reports/styles.css`
- Every JSON API response payload that includes findings includes a `disclaimer` field
- Frontend: `DisclaimerBanner` is mounted at the top of every page, sticky
