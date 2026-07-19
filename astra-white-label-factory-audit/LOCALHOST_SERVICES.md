# Phase 2 — Localhost and Process Audit

**Audited:** 2026-07-15, inside the remote container.

## Active services in this container

`ss -tlnp` returned **no user-space application listeners**. The only
processes running are the Claude Code harness itself (`claude`,
`environment-manager`, the container init). Docker daemon is not running.

**Conclusion: 0 active application services, 0 orphaned services, 0 live port
conflicts in the audited environment.** No process was terminated or
restarted (none existed to touch).

## The Mac's known services — status: not observable

The brief's references live on the Mac and could not be probed from this
container (no network path to the user's localhost):

| Port | Claimed association | Status from this session |
|---|---|---|
| 8080 | Dashy (Bruce OS dashboard) | not observable — verify on the Mac |
| 4173 | Atlas Voyage `#workflow` (Vite preview port) | not observable |
| 3000 | Unidentified web app | not observable — **candidate identified below** |
| 8000 | Historic multi-backend collision | not observable — **collision confirmed in-repo below** |

### Evidence this repo contributes to the Mac's port picture

- **Port 8000 collision is real and reproducible from this repo alone.** Both
  backends document/default to `--port 8000`:
  - Luxor: `README.md` → `uvicorn app.main:app --reload --port 8000`
  - RxEgypt: `rxegypt-pilot/README.md` → `uvicorn main:app --reload --port 8000`
  Running both apps locally at once collides. Recommended assignments are in
  `PORT_REGISTRY.md`.
- **Port 3000 candidate:** RxEgypt's frontend is served with
  `python -m http.server 3000` (`rxegypt-pilot/README.md`), and its backend
  CORS default is `http://localhost:3000`. The "unidentified app on port
  3000" on the Mac may simply be the RxEgypt static frontend (or any CRA/Next
  dev server). Verify with `lsof -iTCP:3000 -sTCP:LISTEN` on the Mac.
- **Port 4173** is Vite's default `preview` port, consistent with Atlas
  Voyage being a Vite build. Luxor's frontend is also Vite (`npm run preview`
  would take 4173) — a second latent collision if both previews run.
- **Port 8080**: Luxor's frontend production container (nginx) listens on
  8080 (`PROJECT_STATUS.md`: "docker build frontend/ (nginx :8080)") — this
  would collide with Dashy on the Mac if the container were run with
  `-p 8080:8080`. Remap when running locally alongside Dashy.

## Dashy linkage

Dashy's config was not reachable; whether it links these services is
**unknown**. Recorded as an open item in `RISKS_AND_UNKNOWNS.md`. Dashy was
not modified (not reachable, and prohibited this phase).

## Mac-side audit commands (for the follow-up local session)

```bash
lsof -nP -iTCP -sTCP:LISTEN            # every listener + pid
lsof -iTCP:3000 -sTCP:LISTEN           # identify the port-3000 mystery
ps -o pid,command -p <PID>; lsof -p <PID> | grep cwd   # working directory
```
