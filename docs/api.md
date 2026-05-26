# API Reference

Base URL (local): `http://localhost:8000`

All endpoints return JSON. Every response includes the AI-simulation disclaimer in some form.

## Health

- `GET /health` → `{status, db, disclaimer}`

## Cases

- `POST /api/cases` — create draft (user-authored)
- `POST /api/cases/generate` — AI-generate a practice case
  ```json
  {"area_of_law": "IP", "difficulty": 2, "language": "en"}
  ```
- `GET /api/cases` — list
- `GET /api/cases/{id}` — detail (with nested parties / facts / evidence)
- `POST /api/cases/{id}/run` — kick off non-training simulation
- `GET /api/cases/{id}/status` — pipeline state + arguments + pending checkpoint
- `GET /api/cases/{id}/report` — full structured JSON report
- `GET /api/cases/{id}/report.pdf` — bilingual PDF

## Training

- `POST /api/cases/{id}/run-training`
  ```json
  {"trainee_role": "DEFENSE", "user_id": "trainee", "difficulty": 2}
  ```
- `GET /api/training/sessions` — list (optional `?user_id=`)
- `GET /api/training/{session_id}/coaching` — coaching report

## HIL / Trainee

- `GET /api/hil/pending?case_id=` — list pending checkpoints
- `POST /api/hil/{cp_id}/approve` — approve checkpoint (resumes pipeline)
- `POST /api/hil/{cp_id}/modify` — modify pipeline state then resume
- `POST /api/hil/{cp_id}/halt` — stop the case
- `POST /api/hil/{cp_id}/submit-trainee` — trainee submits an argument
  ```json
  {"content_en": "...", "citations": ["82/2002:113", "131/1948:163"]}
  ```

## Statutes

- `GET /api/statutes` — list all 8 statutes
- `GET /api/statutes/{id}` — articles for one statute
- `GET /api/statutes/search?q=` — full-text search across articles (AR + EN)
