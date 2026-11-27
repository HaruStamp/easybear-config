#!/bin/bash
# ตัวขาย r33 "ป้ายบทพร้อมแล้ว" (ใบลูกค้า podcast 27 พ.ย. 2569 19:44 · ห้อง easybear)
#   = ตัวขาย r31 ทุกไบต์ + scripts/plan-ready-banner.py (UI หน้าผลิตเท่านั้น · ops/values เท่าเดิมทุกไบต์ · ค่าเริ่มคงเดิม)
#   แก้ป้าย "บทที่ได้มาไม่สมบูรณ์" ที่ขึ้นผิดหลังกดสมอง (บทครบแต่ยังไม่จัดคิว) + เพิ่มปุ่มเริ่ม/จัดคิวในป้าย (หน้าผลิตเดิมไม่มีปุ่มเมื่อคิวว่าง)
# ใช้ (จากราก easybear-config): ./scripts/plan-ready-public-r33.sh <app>…   → เขียนทับ <app>-public.json
set -euo pipefail
cd "$(dirname "$0")/.."
base() { case "$1" in
  podcast) echo "8e4c6b8 4ead1d5d480e17876e78474f07155a3a";;
  *) echo "🔴 ยังไม่ได้ตั้งฐานของแอป $1" >&2; exit 1;; esac; }
[ $# -eq 0 ] && set -- podcast
for a in "$@"; do
  read -r ref sum <<<"$(base "$a")"
  git show "$ref:$a-public.json" > "$a-public.json"
  [ "$(md5 -q "$a-public.json")" = "$sum" ] || { echo "🔴 $a ฐานไม่ตรง"; exit 1; }
  python3 scripts/plan-ready-banner.py "$a-public.json"
  echo "$a md5 $(md5 -q "$a-public.json")"
done
