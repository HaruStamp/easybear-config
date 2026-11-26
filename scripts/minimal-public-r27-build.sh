#!/bin/bash
# minimal-public r27 (อัปเดตใหญ่ รอบ 2 · 27 พ.ย. 2569) = r26 + ของที่เทสสดผ่านบน Dev a4b56175 (engine 1.25) รอบ 2
#   ใส่เพิ่ม: v62 สัตว์เลี้ยงร่วมแสดง 1-3 ตัว · v63 ตั้งค่าเฉพาะสินค้า (สไตล์การขาย/การนำเสนอ/โมเดลภาพ/โมเดลวิดีโอ)
#   ค่าเริ่มคงเดิม (Omni 1.1 Flash · 720p · Nano Banana Pro) — own ปิด = prompt เดิมทุกไบต์
#   หลักฐานเทส: easybear/apps/minimal/docs/qa/2026-11-27-round2/README.md
# ใช้ (จากราก easybear-config): ./scripts/minimal-public-r27-build.sh → เขียนทับ minimal-public.json
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/minimal-public-r26-build.sh >/dev/null
[ "$(md5 -q minimal-public.json)" = 778c2d5ab5e9cda602edbe7161c3051f ] || { echo "🔴 ฐาน r26 ไม่ตรง"; exit 1; }
for s in minimal-v62-pets-multi minimal-v63-own-product-settings; do
  python3 "scripts/$s.py" minimal-public.json
done
echo "md5 $(md5 -q minimal-public.json)"
