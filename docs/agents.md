# Agents

Each agent inherits from `LegalAgent` (`backend/app/agents/base.py`) and implements one async
`run(ctx)` method. Agents are stateless — the orchestrator builds an `AgentContext`, calls
`agent.run(ctx)`, and persists the `AgentOutput`.

## Common contract

```python
class AgentContext(BaseModel):
    case_id: UUID
    lang: Lang                     # AR or EN
    case_snapshot: dict            # parties + facts + evidence
    prior_arguments: list[dict]    # for debate agents
    statute_block: str             # the cached Egyptian corpus text
    statute_article_ids: list[str]
    extra: dict                    # per-agent kwargs (round_no, argument-to-score, ...)

class AgentOutput(BaseModel):
    content_ar: str | None
    content_en: str | None
    citations: list[UUID]
    raw: dict                      # full structured response from the LLM
    llm_used: str
```

## The nine agents

### 1. EvidenceMigrationAgent — `claude-sonnet-4-6`

Reads raw case input. Returns structured facts (disputed vs undisputed), evidence list with
`missing` flags, and a one-paragraph summary in both languages.

### 2. ProsecutionAgent — alternates `claude-opus-4-7` / `deepseek-chat`

Builds the plaintiff argument grounded in the provided statute corpus. Cites by `short_code:article_number`. The LLM rotates per round to expose model bias.

### 3. DefenseAgent — alternates `deepseek-chat` / `claude-opus-4-7`

Builds the defendant argument: procedural defenses (jurisdiction, standing, limitation),
substantive defenses, and counterclaims.

### 4. JudicialAgent — `claude-opus-4-7`

After both sides argue, the judicial agent:
- Assigns `plaintiff_success_prob` (0–100)
- Identifies critical evidence gaps
- References Court of Cassation doctrine conceptually
- Issues a reasoned ruling in both languages
- Holds **override authority** — can flag a critical legal-fundamentals error

### 5. ScoringAgent — `claude-sonnet-4-6`

Evaluates one argument on four dimensions (0–100):
- **factual** — accuracy against the case snapshot
- **provable** — support from available evidence
- **unbiased** — argumentation quality
- **legal_law_based** — grounding in cited statutes

Plus a weighted `overall`. Sonnet is intentionally chosen as the cheap evaluator.

### 6. ProceduralSpecialistAgent — `claude-sonnet-4-6`

Runs once after Evidence Migration. Identifies jurisdiction issues, standing
problems, limitation period concerns, mandatory pre-litigation steps (labour
office mediation, consumer agency filings, etc.), and competent court. Output
persisted on `cases.procedural_analysis` (JSONB).

### 7. PrecedentResearcherAgent — `claude-sonnet-4-6`

Runs once after the debate loop, before Judicial Reasoning. Surfaces Court of
Cassation doctrine and analogous precedent themes. Names doctrinal principles
rather than fabricating case numbers (we have no precedent DB). Output on
`cases.precedent_analysis`.

### 8. DamagesCalculatorAgent — `claude-sonnet-4-6`

Runs once after the Ruling. Estimates likely damages in EGP — material range,
moral damages, non-monetary remedies (seizure, recall, injunction). Output on
`cases.damages_estimate`. Feeds the Outcome's projected value.

### 9. HIL / Trainee — no LLM

Pure DB-gated checkpoints (`models/hil.py`). When training mode is active and a debate round's
side matches the trainee's role, the orchestrator creates a `TRAINEE_TURN` checkpoint and the
case enters `PAUSED_HIL`. The trainee submits their argument via
`POST /api/hil/{cp_id}/submit-trainee`, which scores their argument identically to an LLM
argument and resumes the pipeline.

## Cross-LLM debate fairness

```python
PROSECUTION_LLM_BY_ROUND = ["claude-opus", "deepseek", "claude-opus"]
DEFENSE_LLM_BY_ROUND     = ["deepseek", "claude-opus", "deepseek"]
```

Each `debate_rounds` row records `team_a_llm` / `team_b_llm` so analysis can correlate outcomes
with which model voiced each side.

## Adding a new agent

1. Create `backend/app/agents/your_agent.py` extending `LegalAgent`.
2. Export from `backend/app/agents/__init__.py`.
3. Call it from `services/orchestrator.py` in the appropriate pipeline slot.
4. Add a canned response branch in `tests/conftest.py:_canned_response` keyed on a
   **unique token** that appears only in your agent's user-prompt JSON schema
   (e.g., a unique field name). Order matters — more specific patterns first.
5. Add a test in `tests/test_agents/`. The 7 area-of-law scenario tests in
   `tests/test_scenarios.py` will automatically exercise it end-to-end.

## Scenario tests

`tests/scenarios.py` has 7 canonical case fixtures, one per area of law (IP,
Labour, Commercial, Consumer, Privacy, Corporate, Civil). `test_scenarios.py`
parametrizes over them, booting SQLite + corpus + mock LLM per test and
running the full orchestrator pipeline. No API keys, no Docker, no Postgres
required — `make test-backend` runs them all in ~2 seconds.
