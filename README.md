# EQUALISE™ EGYPT

**AI-Powered Legal Simulation & Case Intelligence System for Egyptian Law**

> ⚠ **AI Simulation Only — Not Legal Advice — All outputs require review by a qualified Egyptian lawyer.**
>
> محاكاة بالذكاء الاصطناعي فقط — ليست استشارة قانونية — جميع النتائج تتطلب مراجعة من محامٍ مصري مؤهل.

A courtroom simulator for **trainee lawyers**. Trainees practice against AI opposing counsel on
fact patterns they author or generate, walk away with a coaching report identifying missed
statutes and weak arguments, and reduce the load on legal research teams through automated fact
extraction, statute lookup, and opposing-counsel argumentation.

## Architecture

```
case input  →  Evidence Migration LLM  →  Cross-LLM Debate (Prosecution vs Defense)
                                                ↓
                                          Scoring Layer
                                                ↓
                                    Judicial Reasoning + Override
                                                ↓
                                  Ruling → Outcome → Coaching Report
```

Six agents, each grounded in the Egyptian statute corpus shipped in `corpus/`:

| Agent | LLM | Role |
|---|---|---|
| Evidence Migration | Claude Sonnet | Fact extraction, disputed/undisputed tagging |
| Prosecution | Claude Opus / DeepSeek (alternating) | Plaintiff arguments |
| Defense | DeepSeek / Claude Opus (alternating) | Defendant arguments |
| Judicial Reasoning | Claude Opus | Ruling + override authority |
| Scoring | Claude Sonnet | Argument quality on 4 dimensions |
| HIL / Trainee | none | DB-gated checkpoint |

Cross-LLM swap per round means Claude argues Prosecution in round 1, Defense in round 2, etc., to
expose model bias.

## Stack

- **Backend**: FastAPI · SQLAlchemy 2.0 · Postgres 16 · Anthropic SDK · OpenAI SDK (DeepSeek) · WeasyPrint (bilingual PDF) · Alembic
- **Frontend**: Vite · React 18 · TypeScript · TanStack Query · react-i18next · Tailwind
- **Infra**: docker-compose for local dev; K8s manifests deferred

## Quickstart

```sh
# 1. Setup
cp .env.example .env
# fill in ANTHROPIC_API_KEY and DEEPSEEK_API_KEY

# 2. Bring up the stack
make dev
# (db + backend with auto-migrate + corpus seed + frontend on :5173)

# 3. Open the app
open http://localhost:5173
```

The Training Dashboard at `/` is the entry point: pick area-of-law, difficulty, and role
(Prosecution / Defense). It generates a synthetic case via Claude Opus and drops you into the
courtroom against AI opposing counsel.

## API tour

```sh
# AI-generate a practice case
curl -X POST http://localhost:8000/api/cases/generate \
  -H 'Content-Type: application/json' \
  -d '{"area_of_law":"IP","difficulty":2,"language":"en"}'

# Start training session — trainee plays Defense
curl -X POST http://localhost:8000/api/cases/<CASE_ID>/run-training \
  -H 'Content-Type: application/json' \
  -d '{"trainee_role":"DEFENSE","user_id":"trainee","difficulty":2}'

# Poll status — when TRAINEE_TURN appears, submit:
curl -X POST http://localhost:8000/api/hil/<CP_ID>/submit-trainee \
  -H 'Content-Type: application/json' \
  -d '{"content_en":"...","citations":["82/2002:115"]}'

# Bilingual PDF ruling + coaching report
curl http://localhost:8000/api/cases/<CASE_ID>/report.pdf -o ruling.pdf
curl http://localhost:8000/api/training/<SESSION_ID>/coaching | jq
```

## Layout

```
expert-spork/
├── backend/                 # FastAPI app, agents, services, models, prompts
├── frontend/                # Vite + React + TS, bilingual UI, RTL-aware
├── corpus/                  # 8 Egyptian statutes, 5–10 articles each
├── infra/                   # postgres init.sql; k8s placeholder
├── docs/                    # architecture, agents, prompt caching notes
├── docker-compose.yml
└── Makefile                 # make dev | make seed | make test
```

See `docs/` for deeper documentation:

- `docs/architecture.md` — maps the diagram to code modules
- `docs/agents.md` — per-agent role, LLM choice, I/O contract
- `docs/prompt-caching.md` — how the statute corpus is cached
- `docs/training-mode.md` — trainee workflow
- `docs/i18n.md` — Arabic/RTL notes

## Make targets

- `make dev` — bring up the full stack with hot reload
- `make seed` — re-run the statute corpus loader (idempotent)
- `make test` — backend pytest + frontend vitest
- `make migrate m="add foo"` — generate alembic revision
- `make upgrade` — apply migrations
- `make down` / `make clean` — tear down

## Prompt caching

Every agent receives the Egyptian statute corpus as a cacheable system block. With ~6 agent calls
per case sharing the block, Anthropic's prompt caching cuts repeat-call cost ~90% and latency
~50%. DeepSeek calls inline a trimmed subset of articles relevant to the case. See
`docs/prompt-caching.md`.

## Not in this scaffold

K8s manifests, auth/login, full statute text (we ship 5–10 representative articles per law),
the three feedback loops as real retraining, Court of Cassation precedent DB, auto-translation,
streaming responses, OTel/Sentry, rate limiting, mobile UI. These are explicit non-goals for v0
— see `docs/architecture.md` for the deferred list.

## License

MIT. See `LICENSE`.
