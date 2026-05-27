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

## The thirteen agents

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

### 9. CourtClerkAgent — `claude-sonnet-4-6`

Runs first, before any other agent. Generates the docket: case number, competent
court designation, list of required filings per area of law, flags missing
mandatory documents. Output on `cases.docket`.

### 10. ExpertWitnessAgent — `claude-sonnet-4-6`

Court-appointed expert per Code of Civil and Commercial Procedures art. 104.
Runs after Evidence Migration **only when disputed facts exist**. Provides a
neutral expert opinion on the disputed matters (trademark similarity, defective
product, valuation, etc.). Output on `cases.expert_testimony`.

### 11. MediatorAgent — `claude-sonnet-4-6`

Runs after Damages Calculator. Proposes pretrial settlement terms — EGP value,
non-monetary terms, recommendation (PROCEED / SETTLE / MIXED). Mandatory in
labour disputes (12/2003 art. 82); valuable for trainees learning when to settle
vs. proceed. Output on `cases.mediation_proposal`.

### 12. CassationPanelAgent — three LLMs

Three-judge Court of Cassation appellate review of the trial Judicial Reasoning
agent's ruling. Each panel member is voiced by a different LLM
(`claude-opus`, `deepseek`, `claude-sonnet`) for cross-LLM diversity. Each judge
votes AFFIRM / REVERSE / REMAND independently; the panel decision is the
majority vote. Calls run in parallel via `asyncio.gather`. Output on
`cases.cassation_review` includes the panel decision, the vote tally, and each
judge's individual opinion.

### 13. HIL / Trainee — no LLM

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
parametrizes over them, booting SQLite + corpus + mock LLM per test and running
the full orchestrator pipeline.

`tests/severity.py` adds:
- a **difficulty grid** that derives 21 fixtures from the base 7 (difficulty 1
  = all undisputed, difficulty 3 = base, difficulty 5 = multi-issue with missing
  evidence)
- 5 named **edge cases**: `missing_evidence_dominant`, `counterclaim_driven`,
  `single_disputed_fact`, `multi_defendant`, `limitation_borderline`

Plus two training-mode pause-and-resume tests for trainee-as-Prosecution and
trainee-as-Defense, and one orchestrator idempotency test.

Total: **46 backend tests**, all running against in-memory SQLite + mocked LLM
in ~7 seconds. No API keys, no Docker, no Postgres required.
