#!/bin/bash
# minimal-public r26 (อัปเดตใหญ่ 26 พ.ย. 2569) — สร้างไฟล์ตัวขายผู้สมัครจาก "ตัวขายปัจจุบัน" + เฉพาะของที่เทสสดผ่านบน Dev
#   ฐาน = minimal-public.json ที่ a8eba37 (= minimal-dev ก่อน v59 ทุกไบต์ · md5 56445f71) · ไม่ยก dev ทั้งก้อน
#   ใส่: v59 (โมเดลรูป 3 · ตามบอร์ด · ล็อกฟอนต์ · svSell · ปก+แคปชัน) · v60 (บอร์ด ref ท้าย) · v61 (sizeInfo + ปก aux) · v64 (ปกหัวข้อไทย)
#   ไม่ใส่: v62 สัตว์เลี้ยง · v63 ตั้งค่าเฉพาะสินค้า (ยังไม่เทสสด)
#   หลักฐานเทส: easybear/apps/minimal/docs/qa/2026-11-26-big-update/README.md
# ใช้ (จากราก easybear-config): ./scripts/minimal-public-r26-build.sh   → เขียนทับ minimal-public.json (ห้าม push main จนสั่งปล่อย)
set -euo pipefail
cd "$(dirname "$0")/.."
BASE=a8eba37
git show "$BASE:minimal-public.json" > minimal-public.json
[ "$(md5 -q minimal-public.json)" = 56445f71a05832540f90db852a182a36 ] || { echo "🔴 ฐานไม่ตรง"; exit 1; }
for s in minimal-v59-model-board-font-sell-cover minimal-v60-board-last-follow minimal-v61-sizeinfo-parity minimal-v64-cover-thai-headline; do
  python3 "scripts/$s.py" minimal-public.json
done
echo "md5 $(md5 -q minimal-public.json)"
