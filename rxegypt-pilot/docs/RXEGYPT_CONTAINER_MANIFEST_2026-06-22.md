# RXEGYPT™ Container Manifest — 2026-06-22

## Purpose

This file establishes the RXEGYPT™ GitHub documentation container for the Phase 1 staging completion sprint.

## Source-of-truth files to maintain

- `RXEGYPT_BRG_MASTER_v1.0.5.md`
- `DRUG_MATRIX_v1.0.md`
- `PRODUCTION_PREP_SCHEDULE.md`
- `WEEKLY_UPDATE_2026-06-22.md`
- `GITHUB_REPOSITORY_PACK.md`
- `GOOGLE_DRIVE_CONTAINER_STRUCTURE.md`
- `PRODUCTION_GAP_BACKLOG.md`

## Current GitHub anchor

- Repository: `Fly-ai-guy7/expert-spork`
- Historical RxEgypt scaffold: `rxegypt-pilot/`
- Active P0 issue: `#11 — Expand RxEgypt medication container to 250 records for Q-imminent build`

## Current readiness

```text
Backend Core:          [██████████] 100%
Staging Readiness:     [█████████░] 90%
Production Prep:       [███████░░░] 72%
Overall Readiness:     [████████░░] 76%
```

## Immediate next actions

1. Commit the BRG master pack.
2. Commit the drug matrix in Markdown, CSV, and JSON.
3. Add the six-week production-prep schedule.
4. Add weekly Notion update template/export.
5. Expand the historical seed container from 30 records to exactly 250 records.
6. Validate seed count, barcode uniqueness, Rx gating, search, and staging deployment.

## Governance notes

- All medication data is staging/reference data until pharmacist/legal verification is complete.
- Controlled medicines must remain blocked from self-serve checkout.
- Prices and barcodes are indicative unless pharmacy-verified.
- The GitHub repo is the source of truth for build artefacts; Google Drive is evidence/docs container; Notion is operating dashboard.

## AI vs Human comparison

- AI time so far: under 1 hour
- Human comparison time: 1–2 days
