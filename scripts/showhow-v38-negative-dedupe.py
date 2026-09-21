#!/usr/bin/env python3
"""showhow v38 — ตัดคำซ้ำในบรรทัด Negative (คืน 25 ตัวอักษร · ทำให้เคส p95 ทุกช่องพร้อมกันลงใต้เพดานได้พอดี)

ซ้ำจริง: บรรทัดหัว prompt เขียนอยู่แล้วว่า
  "One continuous shot through 5 scenes in order — no grid, split-screen, panels or borders."
แล้ว Negative ท้าย prompt เขียนซ้ำอีกว่า "no grid, no split screen, …"
⇒ ตัดเฉพาะ 2 คำนี้ออกจาก Negative · **ของที่เหลือใน Negative ห้ามแตะ** (no tripod or camera gear = ตัวแก้บั๊กขาตั้งกล้องโผล่ คลิปแรก 2026-09-15)

หลังแก้: ชั้นตัดสิน p95 mnVideo ยาวสุด 3,915 → 3,890 (ใต้ 3,900) ⇒ แม้เคสสังเคราะห์สุดขีดของชั้นตัดสินก็ไม่มีอะไรโดนตัดเลย
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent.parent / 'showhow-dev.json'
s = P.read_text(encoding='utf-8')
OLD = 'Negative: no grid, no split screen, no tripod or camera gear in frame,'
NEW = 'Negative: no tripod or camera gear in frame,'
n = s.count(OLD)
assert n == 6, f'เจอ {n} จุด (คาด 6 = mnVideo 1-6) — หยุด'
assert 'no grid, split-screen, panels or borders' in s, 'กฎห้ามตารางหายจากหัว prompt — ห้ามตัดคำซ้ำถ้าต้นฉบับไม่อยู่แล้ว'
P.write_text(s.replace(OLD, NEW), encoding='utf-8')
print(f'ตัดคำซ้ำ {n} จุด · คืน {len(OLD)-len(NEW)} ตัวอักษรต่อ prompt')
