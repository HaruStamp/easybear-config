#!/bin/bash
# hardsell-public r27 (อัปเดตใหญ่ รอบ 2 · 27 พ.ย. 2569) = r26 + ของที่เทสสดผ่านบน Dev df5b3dbb (engine 1.25) รอบ 2
#   ใส่เพิ่ม: v31 คลิป 20 วิ Omni (ผ่อน 360p แบบ r26-b) · v32 แคปชัน+แฮชแท็ก+ปก · v33 ตั้งค่าเฉพาะสินค้า · v34 ปกหัวข้อไทยห้ามแปล
#   ค่าเริ่มคงเดิม (Veo 3.1 - Lite · 8 วิ · Nano Banana Pro)
#   หลักฐานเทส: easybear/apps/hardsell/docs/qa/2026-11-27-round2/README.md
# ใช้ (จากราก easybear-config): ./scripts/hardsell-public-r27-build.sh → เขียนทับ hardsell-public.json
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/hardsell-public-r26-build.sh >/dev/null
[ "$(md5 -q hardsell-public.json)" = 16b4e62fda44481075514b31483579ad ] || { echo "🔴 ฐาน r26 ไม่ตรง"; exit 1; }
for s in hardsell-public-r27-v31-omni-20s hardsell-v32-caption-cover hardsell-v33-per-product hardsell-v34-cover-thai-headline; do
  python3 "scripts/$s.py" hardsell-public.json
done
echo "md5 $(md5 -q hardsell-public.json)"
