#!/bin/bash
# minimal-public r28 (polish อัปเดตใหญ่ · 27 พ.ย. 2569) = r27 + v65 โหมดเห็นแต่มือ บอร์ดย้ำห้ามหน้าท้าย prompt
#   ค่าเริ่มคงเดิม (Omni 1.1 Flash · 720p · Nano Banana Pro) · หลักฐานเทส: easybear/apps/minimal/docs/qa/2026-11-27-polish/
# ใช้ (จากราก easybear-config): ./scripts/minimal-public-r28-build.sh → เขียนทับ minimal-public.json
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/minimal-public-r27-build.sh >/dev/null
[ "$(md5 -q minimal-public.json)" = 34b9b6ba13cc441022b2134a6b7f4c82 ] || { echo "🔴 ฐาน r27 ไม่ตรง"; exit 1; }
python3 scripts/minimal-v65-hands-board-no-face.py minimal-public.json
echo "md5 $(md5 -q minimal-public.json)"
