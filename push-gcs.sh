#!/bin/bash
# push config → GCS (no-cache = เห็นทันที ไม่มี jsdelivr lag)
# ใช้: ./push-gcs.sh [ไฟล์]   (default flim-v2-full.json)
set -e
BUCKET="${GCS_BUCKET:-easybear-config-578946198765}"
FILE="${1:-film.json}"
gcloud storage cp "$FILE" "gs://$BUCKET/$FILE" \
  --cache-control="no-cache, max-age=0" \
  --content-type="application/json"
echo "✓ uploaded → https://storage.googleapis.com/$BUCKET/$FILE"
