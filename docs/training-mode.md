# Training Mode

EQUALISE Egypt's primary user is a **lawyer in training**. Training mode turns the courtroom
simulation into a practice environment.

## Flow

1. Trainee opens **Training Dashboard** (`/`).
2. Picks **area of law** (IP / Labour / Commercial / Consumer / Privacy / Corporate / Civil),
   **difficulty** (1–5), and **role** (Prosecution or Defense).
3. Backend AI-generates a synthetic case (`POST /api/cases/generate` →
   `services/case_generator.py`).
4. Backend starts a `TrainingSession` and kicks off the pipeline
   (`POST /api/cases/{id}/run-training`).
5. The orchestrator runs Evidence Migration as usual. When the debate loop reaches a round
   where the trainee's side comes up, instead of calling the corresponding LLM agent, it:
   - Creates a `HilCheckpoint(stage=TRAINEE_TURN, status=PENDING)` with `modified_payload={"side":..., "round_no":...}`.
   - Marks the case `PAUSED_HIL`.
   - Returns immediately.
6. The frontend, polling `/api/cases/{id}/status`, sees the pending checkpoint, opens
   `TraineeSeatDialog`, and the trainee writes their argument with citations.
7. `POST /api/hil/{cp_id}/submit-trainee` saves the argument as a TRAINEE-role `Argument`,
   scores it via the same `ScoringAgent` used for the LLMs, and **resumes** the pipeline by
   calling `orchestrator.run_simulation` again. Because the orchestrator is idempotent, it picks
   up at the next round.
8. After the pipeline completes, `coaching_service.generate_coaching_report` runs:
   - Compares trainee citations against opponent citations → `missed_citations`
   - Surfaces the JudicialAgent's identified gaps → `evidence_gaps_to_address`
   - Computes per-round scores
   - Picks the trainee's two weakest dimensions → `weak_patterns`
   - Computes letter grade A/B/C/D/F from average overall score
9. Coaching report is shown at `/training/{sessionId}` and can be exported as PDF.

## Why this is the "research-team replacement"

The classic legal research team burden is: "Given this fact pattern, find every relevant
statute and precedent and draft opposing arguments." EQUALISE automates exactly that:

- **Evidence Migration** structures the fact pattern.
- **Opposing-side agent** (Prosecution or Defense) drafts the argument the research team would
  draft — including statute citations and procedural defenses.
- **Statute Browser** at `/statutes` lets trainees verify citations and look up surrounding
  articles, with full-text search across the corpus.
- **Coaching Report** explicitly lists what the trainee missed so the research workflow is
  internalized over multiple sessions.

## Difficulty levels

Difficulty 1–5 is currently a hint passed to the `case_generator` prompt:

- **1** — single-issue, clear-cut fact pattern, all facts undisputed
- **2** — single-issue with one disputed fact
- **3** — two intersecting claims, some evidence marked missing
- **4** — multi-claim with procedural complications (jurisdiction, limitation)
- **5** — multi-claim, heavily disputed, intentionally ambiguous

A curriculum/recommendation engine (which case to suggest next given a trainee's session
history) is deferred. The data is available on `training_sessions.coaching_report` to build it
later.

## Switching between training and non-training

A case has at most one active `TrainingSession`. To run the same case without trainee
participation, don't create a training session — call `POST /api/cases/{id}/run` instead, and
both sides will be played by LLMs.
