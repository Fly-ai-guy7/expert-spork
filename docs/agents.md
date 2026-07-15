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

## The six agents

### 1. EvidenceMigrationAgent — `claude-sonnet-4-6`

Reads raw case input. Returns structured facts (disputed vs undisputed), evidence list with
`missing` flags, and a one-paragraph summary in both languages.

### 2. ProsecutionAgent — alternates `claude-opus-4-7` / `deepseek-chat`

Builds the plaintiff argument grounded in the provided statute corpus. Cites by `short_code:article_number`. The LLM rotates per round to expose model bias.

### 3. DefenseAgent — alternates `deepseek-chat` / `claude-opus-4-7`

Builds the defendant argument: procedural defenses (jurisdiction, standing, limitation),
substantive defenses, and counterclaims.

### 4. JudicialCouncilAgent — panel of `claude-opus-4-7` + `claude-sonnet-4-6` + `deepseek-chat`

After both sides argue, a **panel of judges** rules. Each member is a `JudicialAgent`
bound to a different LLM, run concurrently. The council then aggregates:
- `plaintiff_success_prob` = mean across members
- a **majority verdict** with a recorded vote tally (`council_vote`); a tie resolves
  for the defendant (the plaintiff carries — and has not met — the burden of proof)
- **dissents** — non-majority members' reasoning, persisted on the ruling and in
  `council_verdicts`
- merged (deduped) critical evidence gaps and precedent references
- **override authority** — applied when a strict majority of members flag a critical
  legal-fundamentals error

Each member's verdict is persisted to `council_verdicts` (one row per member) so analysis
can correlate outcomes with which model sat on the panel. The single-model `JudicialAgent`
remains the council's building block and can still be used directly.

### 5. ScoringAgent — `claude-sonnet-4-6`

Evaluates one argument on four dimensions (0–100):
- **factual** — accuracy against the case snapshot
- **provable** — support from available evidence
- **unbiased** — argumentation quality
- **legal_law_based** — grounding in cited statutes

Plus a weighted `overall`. Sonnet is intentionally chosen as the cheap evaluator.

### 6. AdvisoryCounselAgent — `claude-sonnet-4-6`

A private mentor for the trainee, invoked **on demand** (not part of the automatic
pipeline). Given the case, the debate so far, and the trainee's draft, it returns
strategic guidance, suggested statute citations, strengths to press, risks the opponent
will attack, and arguments not yet made. It coaches — it never writes the argument or
argues the case itself.

Two entry points, both backed by `services/counsel_service.py`:

- `POST /api/hil/{cp_id}/counsel` — during the debate, at a `TRAINEE_TURN` checkpoint.
  Role is derived from the checkpoint side.
- `POST /api/cases/{case_id}/counsel` — pre-turn prep, before any HIL. Role is derived
  from the active training session on that case, or supplied via `trainee_role` in the
  request body for pure prep mode.

The response is advisory only and does not mutate the simulation, so a trainee can call
either endpoint repeatedly. Each call is persisted to `counsel_logs` and is reviewable
at `GET /api/training/{session_id}/counsel-log`; the coaching report includes
`counsel_calls_count` as a usage signal.

### 7. HIL / Trainee — no LLM

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
4. Add a canned response branch in `tests/conftest.py:_canned_response` and a test in
   `tests/test_agents/`.
