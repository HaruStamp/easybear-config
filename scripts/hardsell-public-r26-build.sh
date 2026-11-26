#!/bin/bash
# hardsell-public r26 (อัปเดตใหญ่ 26 พ.ย. 2569) — สร้างไฟล์ตัวขายผู้สมัครจาก "ตัวขายปัจจุบัน" (v22.4 + แก้ POV 4230297) + เฉพาะของที่เทสสดผ่านบน Dev
#   ไม่ยก dev ทั้งก้อน: ไม่มี Omni 1.2 / 360p / ถอด Veo Fast ของ dev v22.5-v22.8
#   ใส่: r26-a (โมเดลรูป Pro·2.1 + มีข้อความ=Pro · ค่าเริ่มวิดีโอ Veo 3.1 - Lite) · v23 3D อารมณ์ตามโทน · v24 +2 Lite
#        r26-b (= v25 10 วิ Omni ไม่มีส่วน 360p) · v26 เสียงรอยต่อ 16 วิ · v27 ฉากที่แก้ถึงวิดีโอ · v28 ฉากหลัง · v29 ท่า+ขนาดสินค้า
#        v30 ปากทาลิป (เทมเพลตเพิ่มล้วน · ยังไม่เทสสด)
#        v35 ปากทาลิปโคลสอัปปากทุกช่วง (เทสสด 26 พ.ย.: ช่วง 2 ถอยกล้องเห็นหน้า · fallback = ข้อความเดิม เทมเพลตอื่นไม่เปลี่ยน)
#        v36 mnPlan prompt ≤3850 (ย้ายกฎคงที่ไปท้าย systemInstruction · เทสสด prompt-too-long 4017)
#   ไม่ใส่: v31 20 วิ (ต้อง engine v1.25 trimTailIfNext) · v32-v34 ปก/แคปชัน/ตั้งค่ารายสินค้า (ยังไม่เทสสด)
#   หลักฐานเทส: easybear/apps/hardsell/docs/qa/2026-11-26-big-update/README.md
# ใช้ (จากราก easybear-config): ./scripts/hardsell-public-r26-build.sh   → เขียนทับ hardsell-public.json (ห้าม push main จนสั่งปล่อย)
set -euo pipefail
cd "$(dirname "$0")/.."
BASE=a8eba37
git show "$BASE:hardsell-public.json" > hardsell-public.json
[ "$(md5 -q hardsell-public.json)" = "$(git show 4230297:hardsell-public.json | md5 -q)" ] || { echo "🔴 ฐานไม่ตรง"; exit 1; }
for s in hardsell-public-r26-a-models hardsell-v23-d3-tone-mood hardsell-v24-nb2-lite hardsell-public-r26-b-omni-10s \
         hardsell-v26-voice-seam hardsell-v27-scene-edits hardsell-v28-background hardsell-v29-pose-size hardsell-v30-ugc-lips \
         hardsell-v35-lips-all-parts hardsell-v36-plan-prompt-fit; do
  python3 "scripts/$s.py" hardsell-public.json
done
echo "md5 $(md5 -q hardsell-public.json)"
