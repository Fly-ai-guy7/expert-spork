Codex

You are working in the GitHub repository `Fly-ai-guy7/expert-spork` on branch `rxegypt-p0-drug-expansion-250`.

Project context:
RxEgypt Pilot is a B2B pharmacy management and patient-facing platform for Experts Pharmacy, Al Ahyaa, Hurghada, Egypt. The recovered scaffold lives under `rxegypt-pilot/` and includes FastAPI backend, vanilla HTML/JS frontend, patient app, pharmacy POS, Dawai bilingual patient app, JWT auth, drugs, inventory, orders, Rx gating, PDPL consent, and bilingual health-information disclaimers.

Primary objective:
Expand `rxegypt-pilot/backend/seed/drugs_egypt.json` from 30 records to exactly 250 records while preserving compatibility with the existing SQLAlchemy `Drug` model and `seed/seed_drugs.py` seeder.

Hard constraints:
- Do not change live medical behaviour into advice, diagnosis, severity scoring, or Rx suggestions.
- Do not weaken Rx gating.
- Do not allow patient self-serve checkout for controlled medicines.
- If Rx/control status is uncertain, set `rx: true`.
- Keep this as a verified-pharmacy-catalogue scaffold, not medical advice.
- Preserve JSON validity.
- Preserve the current field schema exactly:
  - `name_en`
  - `name_ar`
  - `generic`
  - `form`
  - `strength`
  - `category`
  - `manufacturer`
  - `barcode`
  - `price_egp`
  - `rx`
- Do not introduce fields unless you also update model, schema, routes, docs and tests. Prefer no schema migration for this sprint.

Implementation requirements:
1. Replace `rxegypt-pilot/backend/seed/drugs_egypt.json` with exactly 250 records.
2. Keep the existing 30 records unless duplicated or obviously invalid.
3. Add Egyptian pharmacy-relevant coverage across:
   - analgesics / NSAIDs
   - antibiotics
   - antifungals / antivirals
   - antihistamines / ENT
   - gastrointestinal
   - cardiovascular
   - diabetes / endocrine
   - respiratory
   - CNS / controlled-drug sensitive classes
   - dermatology
   - ophthalmic / ENT
   - gynaecology / urology
   - vitamins / supplements
   - first aid / devices / consumables, only where the app treats them as pharmacy catalogue items
4. Generate unique placeholder EAN-13-compatible barcodes only when verified barcodes are unavailable. Add a note in docs that placeholder barcodes must be replaced before production.
5. Ensure `price_egp` is a number. Use conservative reference values only and mark them as needing pharmacist validation in docs.
6. Run or add a lightweight validation script that confirms:
   - JSON parses
   - count is exactly 250
   - all required fields exist
   - all barcodes are unique
   - `rx` is boolean
   - `price_egp` is numeric
7. Update `P0_Q_IMMINENT_BUILD_PLAN.md` after completion with the final count and remaining blockers.

Validation commands:
From `rxegypt-pilot/backend`:

```bash
python - <<'PY'
import json
from pathlib import Path
p = Path('seed/drugs_egypt.json')
data = json.loads(p.read_text(encoding='utf-8'))
required = {'name_en','name_ar','generic','form','strength','category','manufacturer','barcode','price_egp','rx'}
assert len(data) == 250, len(data)
seen = set()
for i, row in enumerate(data, 1):
    missing = required - set(row)
    assert not missing, (i, missing)
    assert isinstance(row['rx'], bool), (i, row['name_en'], 'rx')
    assert isinstance(row['price_egp'], (int, float)), (i, row['name_en'], 'price_egp')
    assert row['barcode'] not in seen, (i, row['barcode'])
    seen.add(row['barcode'])
print('RxEgypt seed validation OK:', len(data), 'records')
PY
python seed/seed_drugs.py
```

Expected output:
- Validation prints `RxEgypt seed validation OK: 250 records`.
- Seeder runs idempotently.
- No backend import errors.

Commit message:
`Expand RxEgypt drug seed catalogue to 250 records`

Output after implementation:
- Summary of exact changed files.
- Final record count.
- Any records/classes that require pharmacist/legal verification.
- Any production blockers.

[██████░░░░] 60%
AI time so far: under 1 hour
Human comparison time: 1-2 days
