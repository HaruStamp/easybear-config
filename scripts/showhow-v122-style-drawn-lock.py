#!/usr/bin/env python3
"""showhow-v122 — สไตล์วาด (3D/อนิเมะ/ดินน้ำมัน/ลายเส้น) ช่วงแรกหลุดเป็นภาพสมจริง (พี่หมีทัก 2026-10-13)

อาการ (docs/qa/2026-10-12-pet-3d): การ์ตูน 3D · 20 วิ — บอร์ดช่วง 1 น้องปอมเหมือนรูปถ่าย วิดีโอช่วง 1 เลยสมจริงตาม
  ช่วง 2 เป็น 3D ชัด (มีเจ้าของตัวการ์ตูน + บอร์ดช่วง 1 แนบไปด้วย) · prompt ทั้ง 2 ช่วงมีคำว่า 3D เท่ากัน
ราก: บอร์ดช่วง 1 ไม่มีภาพอ้างอิงให้ยึดสไตล์ · คำสไตล์มีแค่ประโยคเดียวและไม่มีคำห้ามภาพถ่าย
  (ประโยคสมจริงเดิมมี "ห้ามเป็นภาพวาด การ์ตูน…" แต่ประโยค 3D ไม่มีคำห้ามฝั่งกลับ) ⇒ สัตว์จริงดึงกลับไปเป็นรูปถ่าย

แก้ (ยังเป็นท่า "แทนที่ ไม่ต่อท้าย"):
1) styleBoard ของสไตล์วาด: ระบุ "ทุกช่องทุกสิ่ง ทั้งสัตว์ คน ห้อง" + "ห้ามเป็นภาพถ่ายจริง" — ยาว ≤ ประโยคสมจริงเดิม (86)
2) วิดีโอ: lookup ใหม่ styleNegEN ต่อท้ายบรรทัด Negative (หลัง castNegEN) — Negative คือส่วนเดียวที่ยอมให้ถูกตัด
   ⇒ ไม่กินของก่อน Negative ตามเกณฑ์ G9 · สไตล์สมจริง ('', real, thai, clean) และ cyber = ว่าง (ยาวเท่าเดิม)
ใช้: python3 scripts/showhow-v122-style-drawn-lock.py  (รันบน v121)
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
J = lambda x: json.dumps(x, ensure_ascii=False)
L = c['lookups']
B_OLD = L['styleBoard']['real']

DRAWN = ('pixar', 'anime', 'clay', 'ink')
L['styleBoard'].update({
    'pixar': 'การ์ตูน 3D แบบหนังแอนิเมชัน ทุกช่องทุกสิ่ง ทั้งสัตว์ คน ห้อง ตาโต ห้ามเป็นภาพถ่ายจริง',
    'anime': 'อนิเมะ 2D เส้นสะอาด สีสด ทุกช่องทุกสิ่ง ทั้งสัตว์ คน ห้อง ห้ามเป็นภาพถ่ายจริง',
    'clay': 'ดินน้ำมันสต็อปโมชัน มีรอยนิ้ว ทุกช่องทุกสิ่ง ทั้งสัตว์ คน ห้อง ห้ามเป็นภาพถ่ายจริง',
    'ink': 'ลายเส้นหมึกแบบนิยายภาพ เส้นดำหนา สีหม่นอุ่น ทุกช่องทุกสิ่ง ห้ามเป็นภาพถ่ายจริง',
})
L['styleNegEN'] = {k: '' for k in L['styleVideoEN']}
L['styleNegEN'].update({k: ', no photoreal or live-action footage' for k in DRAWN})

NEG = {'op': 'lookup', 'table': 'styleNegEN', 'key': '{values.svStyle}', 'fallback': ''}
n = 0
for o in c['ops']:
    if not o['id'].startswith('mnVideo'):
        continue
    parts = o['prompt']['parts']
    i = next(i for i, p in enumerate(parts) if isinstance(p, dict) and p.get('table') == 'castNegEN')
    assert i == len(parts) - 1, f"{o['id']}: castNegEN ต้องอยู่ท้ายสุด"
    assert isinstance(parts[i - 1], str) and parts[i - 1].lstrip().startswith('Negative:'), o['id']
    if any(isinstance(p, dict) and p.get('table') == 'styleNegEN' for p in parts):
        continue
    parts.append(NEG)
    n += 1
assert n in (0, 6), n

# ── ยาม ──
for k, v in L['styleBoard'].items():
    assert len(v) <= len(B_OLD), f'styleBoard[{k}] ยาว {len(v)} > {len(B_OLD)}'
for k in DRAWN:
    assert 'ห้ามเป็นภาพถ่ายจริง' in L['styleBoard'][k], k
assert set(L['styleNegEN']) == set(L['styleVideoEN']) == set(L['styleBoard'])
assert all(ord(ch) < 128 for v in L['styleNegEN'].values() for ch in v)
for o in c['ops']:
    if o['id'].startswith('mnVideo'):
        assert J(o['prompt']).count('"styleNegEN"') == 1, o['id']
print(f'✅ v122: styleBoard สไตล์วาด 4 ตัว ≤ {len(B_OLD)} · styleNegEN ต่อท้าย Negative {n} op')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
