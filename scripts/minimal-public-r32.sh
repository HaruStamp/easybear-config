#!/bin/bash
# ตัวขาย minimal r32 (27 พ.ย. 2569 · ห้อง easybear หลัง QA เด้งออก) = ตัวขาย r31 (44d36b7 · md5 d60d06ed) + scripts/minimal-v68-tap-res-warn.py
#   ปุ่มแปลงเป็นบทวิดีโอ 44px บนมือถือ · 360p ค้าง 20/30 วิ ส่ง 720p ชัดทั้ง 2 รุ่น · บรรทัดเตือนในการ์ดสถานะหน้าผลิต · ใช้ได้กับ engine 1.22+ (ตัวขายเก่าอ่านไฟล์เดียวกัน)
set -euo pipefail
cd "$(dirname "$0")/.."
git show 44d36b7:minimal-public.json > minimal-public.json
[ "$(md5 -q minimal-public.json)" = "d60d06eda8902b8b8e1f1bd43fe7791d" ] || { echo "🔴 ฐานไม่ตรง"; exit 1; }
python3 scripts/minimal-v68-tap-res-warn.py minimal-public.json
echo "minimal-public md5 $(md5 -q minimal-public.json)"
