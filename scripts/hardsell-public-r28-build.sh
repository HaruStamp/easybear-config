#!/bin/bash
# hardsell-public r28 (polish อัปเดตใหญ่ · 27 พ.ย. 2569) = r27 + v37 ป้ายความยาวอ่านค่ารายสินค้า (หน้าผลิต + หน้าคลัง)
#   ค่าเริ่มคงเดิม (Veo 3.1 - Lite · 8 วิ · Nano Banana Pro) · หลักฐานเทส: easybear/apps/hardsell/docs/qa/2026-11-27-polish/
# ใช้ (จากราก easybear-config): ./scripts/hardsell-public-r28-build.sh → เขียนทับ hardsell-public.json
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/hardsell-public-r27-build.sh >/dev/null
[ "$(md5 -q hardsell-public.json)" = 965ef2936bc5ad9b27e1354ea7c37608 ] || { echo "🔴 ฐาน r27 ไม่ตรง"; exit 1; }
python3 scripts/hardsell-v37-len-label-per-product.py hardsell-public.json
echo "md5 $(md5 -q hardsell-public.json)"
