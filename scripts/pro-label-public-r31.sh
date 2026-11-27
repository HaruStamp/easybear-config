#!/bin/bash
# ตัวขาย r31 "คำอธิบาย Nano Banana Pro สั้นลง" (พี่หมี 27 พ.ย. 2569: "ปรับคำอธิบาย โมเดล nano banana pro ให้สั้นกระชับกว่านี้")
#   = ตัวขาย r30 ทุกไบต์ + scripts/pro-label-short.py (ข้อความ UI เท่านั้น · ops เท่าเดิม · ค่าเริ่มคงเดิม)
# ใช้ (จากราก easybear-config): ./scripts/pro-label-public-r31.sh <app>…   (ไม่ใส่ = ทั้ง 7 แอป) → เขียนทับ <app>-public.json
set -euo pipefail
cd "$(dirname "$0")/.."
base() { case "$1" in
  minimal) echo "c97c334 996c9a4f090d7337ffe41bda84ceb4d7";; fashion) echo "723a9a3 0eeb2318a08ae43ac975af9c6d721c2b";;
  hardsell) echo "cff1e4f a8b84b3cac8f7eb3520fe819c1184aed";; showhow) echo "b3fa1ce 890bb660456667c7d8d622cfd156a1c9";;
  podcast) echo "d24ef48 912c9c1558e95709f557be13973fe8aa";; petdance) echo "1b809de d68d2791cd1ecbb5ce59d94ac8632d3f";;
  parody) echo "bdf354d d971fbcd7710fcd41e2bbd4b6efb596d";;
  *) echo "🔴 ไม่รู้จักแอป $1" >&2; exit 1;; esac; }
[ $# -eq 0 ] && set -- minimal fashion hardsell showhow podcast petdance parody
for a in "$@"; do
  read -r ref sum <<<"$(base "$a")"
  git show "$ref:$a-public.json" > "$a-public.json"
  [ "$(md5 -q "$a-public.json")" = "$sum" ] || { echo "🔴 $a ฐานไม่ตรง"; exit 1; }
  python3 scripts/pro-label-short.py "$a-public.json"
  echo "$a md5 $(md5 -q "$a-public.json")"
done
