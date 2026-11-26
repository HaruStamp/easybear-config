#!/bin/bash
# minimal-public r29 (ปิดอัปเดตใหญ่ · 27 พ.ย. 2569) = r28 + v66 หน้าตัดต่อรับครบทุกช่วง video..video3 (คลิป 20-30 วิ)
#   ค่าเริ่มคงเดิม (Omni 1.1 Flash · 720p · Nano Banana Pro) · หลักฐานเทส: easybear/apps/minimal/docs/qa/2026-11-27-editor-seg/
# ใช้ (จากราก easybear-config): ./scripts/minimal-public-r29-build.sh → เขียนทับ minimal-public.json
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/minimal-public-r28-build.sh >/dev/null
[ "$(md5 -q minimal-public.json)" = 3dfd70b2fcea0eab1a3865f66bed23e4 ] || { echo "🔴 ฐาน r28 ไม่ตรง"; exit 1; }
python3 scripts/minimal-v66-editor-segments.py minimal-public.json
echo "md5 $(md5 -q minimal-public.json)"
