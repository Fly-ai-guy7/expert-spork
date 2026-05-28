#!/bin/sh
# Daily Postgres backup. Writes a gzipped dump to /backups and keeps the most
# recent RETENTION files. For off-site durability, set S3_BUCKET (+ AWS creds)
# and the dump is also copied there via the aws CLI if present.
set -eu

RETENTION="${RETENTION:-14}"
TS="$(date +%Y%m%d-%H%M%S)"
OUT="/backups/equalise-${TS}.sql.gz"

echo "[backup] dumping ${PGDATABASE:-equalise} -> ${OUT}"
pg_dump --no-owner --no-privileges | gzip > "$OUT"

# Local retention
ls -1t /backups/equalise-*.sql.gz 2>/dev/null | tail -n +$((RETENTION + 1)) | xargs -r rm -f

# Optional off-site copy
if [ -n "${S3_BUCKET:-}" ] && command -v aws >/dev/null 2>&1; then
	echo "[backup] uploading to s3://${S3_BUCKET}/"
	aws s3 cp "$OUT" "s3://${S3_BUCKET}/$(basename "$OUT")"
fi

echo "[backup] done: ${OUT}"
