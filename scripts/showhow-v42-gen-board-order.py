#!/usr/bin/env python3
"""showhow v42 — ปุ่ม gen ("ทำของที่ยังไม่มี") ยังไล่บอร์ด 6→1 · แก้เป็น 1→6

รากเดียวกับบั๊กที่เจอเมื่อเช้า (v31 `auto.productLoop.gens`) แต่คนละที่:
  v11 เปลี่ยนลำดับบอร์ดเป็น 1→6 ที่ `stages` · v31 ตามไปแก้ `auto.productLoop.gens`
  **แต่ `chain` ที่ฝังอยู่ในปุ่มไม่มีใครตามไปแก้** — ยาม G8 ก็ยังไม่ครอบ
ทำไมลำดับสำคัญ: `mnBoardK` (K≥2) อ้างบอร์ดช่วง 1 (หมุดมุมเปิด) + บอร์ดช่วง K-1 ⇒ วาดจากท้ายมาหน้า = อ้างของที่ยังไม่มี

🪤 ปุ่ม gen ข้ามช่องที่เต็มแล้ว ⇒ ถ้าผู้ใช้มีบอร์ดครบอยู่แล้วจะไม่เห็นอาการ — โผล่เฉพาะตอนไม่มีบอร์ดเลย (เคสที่เจอเช้านี้พอดี)
🪤 วิดีโอ **ห้ามแก้** — 6→1 เป็นความตั้งใจ (แอปตัดสิน "คลิปเสร็จ" จาก `slots.video` ของช่วงแรก)
"""
import json, pathlib

P = pathlib.Path(__file__).resolve().parent.parent / 'showhow-dev.json'
d = json.loads(P.read_text(encoding='utf-8'))
RIGHT = ['mnBoard'] + [f'mnBoard{k}' for k in range(2, 7)]
WRONG = list(reversed(RIGHT))

hits = []
def walk(n):
    # 🪤 ลำดับฝังอยู่ 2 คีย์: `chain` (ปุ่มในการ์ด) และ `ops` (ปุ่ม gen-phase ระดับหน้า) — เช็กคีย์เดียวจะเหลือค้าง
    if isinstance(n, dict):
        for key in ('chain', 'ops'):
            if n.get(key) == WRONG: hits.append((n, key))
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)
walk(d.get('phases'))
assert hits, 'ไม่เจอ chain บอร์ด 6→1 เลย — แก้ไปแล้วหรือโครงเปลี่ยน'
for n, key in hits: n[key] = list(RIGHT)
assert json.dumps(WRONG, ensure_ascii=False) not in json.dumps(d, ensure_ascii=False), 'ยังมี 6→1 ค้าง'

P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'แก้ลำดับบอร์ด {len(hits)} จุด (chain/ops): 6→1 เป็น 1→6 ·', sorted({str(n.get('el')) for n, _ in hits}))
