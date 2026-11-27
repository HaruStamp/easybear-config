#!/bin/bash
# ตัวขาย r30 "มาตรฐานโมเดลทุกแอป" (พี่หมี 27 พ.ย. 2569) = ตัวขายปัจจุบันทุกไบต์ + model-standard.py สูตรของแอป
#   บล็อกตั้งค่าเดียวกัน: โมเดลภาพ Pro/2.1/2 Lite · โมเดลวิดีโอ Omni 1.1/1.2 (hardsell + Veo 3.1 Lite · ถอด Veo Fast/Quality) · 720p/360p ทั้ง 2 รุ่น · สรุปเครดิต
#   ค่าเริ่มคงเดิม (Omni 1.1 / hardsell Veo 3.1 Lite · ภาพเดิมของแต่ละแอป · 720p) · ไม่ยก dev ทั้งก้อน
#   fashion = easybear-fashion release/r30 build-public-r30.py (ธง FASHION_OMNI360/STDUI)
# ใช้ (จากราก easybear-config): ./scripts/model-standard-public-r30.sh <app>…   (ไม่ใส่ = ทั้ง 6 แอป) → เขียนทับ <app>-public.json
set -euo pipefail
cd "$(dirname "$0")/.."
base() { case "$1" in
  minimal) echo "28bcc87 345bb988cbaf189a17ef43d0d6baa9ac";; hardsell) echo "4a6c850 b2407363f9efee657a226e78b654513a";;
  showhow) echo "cbe2518 c8717d4ee4541fa3b283eb45a0400ce8";; podcast) echo "3cdf374 cbf1271c29f7fb6e35fcdd57b94c8a8e";;
  petdance) echo "0a6ea39 628ef73c00fba4bf9bcc566f1f1756ac";; parody) echo "06851e8 bfb2cc0365daa91005ef971984f66949";;
  *) echo "🔴 ไม่รู้จักแอป $1" >&2; exit 1;; esac; }
[ $# -eq 0 ] && set -- minimal hardsell showhow podcast petdance parody
for a in "$@"; do
  read -r ref sum <<<"$(base "$a")"
  git show "$ref:$a-public.json" > "$a-public.json"
  [ "$(md5 -q "$a-public.json")" = "$sum" ] || { echo "🔴 $a ฐานไม่ตรง"; exit 1; }
  python3 scripts/model-standard.py "$a" "$a-public.json" | tail -2 | head -1 | cut -c1-160
  echo "$a md5 $(md5 -q "$a-public.json")"
done
