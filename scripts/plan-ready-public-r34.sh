#!/bin/bash
# ตัวขาย r34 ทุกแอป engine "ป้ายบทพร้อมแล้ว + บรรทัดเตือนหน้าผลิต" (ห้อง easybear 27 พ.ย. 2569 ค่ำ · ต่อจากใบลูกค้า podcast 19:44)
#   = ตัวขายรุ่นล่าสุดของแต่ละแอปทุกไบต์ + scripts/plan-ready-banner.py + scripts/produce-warn-line.py (UI เท่านั้น · ops/values เท่าเดิมทุกไบต์ · ค่าเริ่มคงเดิม)
#   ① ป้าย "บทที่ได้มาไม่สมบูรณ์" ที่ขึ้นผิดหลังกดสมอง → "บทพร้อมแล้ว" + ปุ่มเริ่ม/จัดคิวในป้าย (podcast มีแล้วตั้งแต่ r33)
#   ② บรรทัดเตือนท้ายการ์ดสถานะหน้าผลิต "ระหว่างรอวิดีโอ อย่าสลับแอปหรือล็อกจอ…" (minimal มีแล้วตั้งแต่ r32)
# ฐาน: podcast r33 · minimal r32 · showhow/hardsell/petdance/parody/fashion r31
# ใช้ (จากราก easybear-config): ./scripts/plan-ready-public-r34.sh [<app>…]   → เขียนทับ <app>-public.json (ไม่ระบุ = ครบ 7 แอป)
set -euo pipefail
cd "$(dirname "$0")/.."
base() { case "$1" in
  podcast) echo "3dc51c5 07c9c91e7095dfdc134e118bf1aa4159";;
  minimal) echo "9ea53a3 e649926de45431ca3e9e373b9d196b8d";;
  showhow) echo "b8d19af 802a058ab63166a453a15bf3cd4e42b7";;
  hardsell) echo "61af36c fb11688a5d7d4a842f496e6838f152e0";;
  petdance) echo "31cdadb fff2c404b56d47187abce20317d3b6d3";;
  parody) echo "a7e071a 7a87c197e16a4d63be98521b4d34c3af";;
  fashion) echo "e7c4a78 7564d1896f1d2704c9a27f7f6c2e98d0";;
  *) echo "🔴 ยังไม่ได้ตั้งฐานของแอป $1" >&2; exit 1;; esac; }
[ $# -eq 0 ] && set -- podcast minimal showhow hardsell petdance parody fashion
for a in "$@"; do
  read -r ref sum <<<"$(base "$a")"
  git show "$ref:$a-public.json" > "$a-public.json"
  [ "$(md5 -q "$a-public.json")" = "$sum" ] || { echo "🔴 $a ฐานไม่ตรง"; exit 1; }
  python3 scripts/plan-ready-banner.py "$a-public.json"
  python3 scripts/produce-warn-line.py "$a-public.json"
  echo "$a md5 $(md5 -q "$a-public.json")"
done
