#!/bin/bash
# push config → GCS (no-cache = เห็นทันที ไม่มี jsdelivr lag)
# ใช้: ./push-gcs.sh <ไฟล์>   (default film-dev.json · มาตรฐาน -dev/-public 2026-09-17: ทีม push เฉพาะ <app>-dev.json · <app>-public.json push เมื่อพี่หมีสั่งเท่านั้น)
set -e
BUCKET="${GCS_BUCKET:-easybear-config-578946198765}"
FILE="${1:-film-dev.json}"
gcloud storage cp "$FILE" "gs://$BUCKET/$FILE" \
  --cache-control="no-cache, max-age=0" \
  --content-type="application/json"
echo "✓ uploaded → https://storage.googleapis.com/$BUCKET/$FILE"
