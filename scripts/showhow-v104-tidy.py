#!/usr/bin/env python3
"""showhow-v104 — เก็บกวาดจากรอบตรวจความเรียบร้อย (2026-09-24)

① 🐛 ตัวละคร "สุ่มตัวละคร" ไม่เห็นช่อง เพศ / ช่วงวัย / ป้าย "บอกใบ้เพิ่มได้"
   ตัวเลือกสุ่มเปลี่ยน value เป็น '' ตั้งแต่ v83 (กฎค่าว่างต้องมีปุ่มถูกเลือก) แต่ `when` 3 จุดยังเทียบกับค่าเก่า
   "AI เลือกนาย/นางแบบ…" ⇒ ซ่อนตลอดในค่าตั้งต้น (บทยังรับเพศ/วัยอยู่ แต่ผู้ใช้กรอกไม่ได้)
   แก้: เงื่อนไขเป็น "ไม่ได้ใช้รูปตัวละคร" — ครอบทั้ง '' และค่าเก่าของงานที่บันทึกไว้
② ข้อความเตือนบนหน้างาน 6 จุดขึ้นต้นด้วย emoji (🔒 ⚠️ ✅) — ผิดกฎ "ไอคอน material เท่านั้น" → ย้ายเป็น `icon`
ใช้: python3 scripts/showhow-v104-tidy.py
"""
import json, re
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
J = lambda x: json.dumps(x, ensure_ascii=False)
AI = 'AI เลือกนาย/นางแบบให้เหมาะกับสินค้า'
FACE = 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


# ①
n1 = 0
for n in walk(c['phases']):
    if isinstance(n, dict) and n.get('when') == {'op': 'eq', 'a': '{item.peopleSrc}', 'b': AI}:
        n['when'] = {'op': 'not', 'a': {'op': 'eq', 'a': '{item.peopleSrc}', 'b': FACE}}; n1 += 1
assert n1 == 3, n1
print(f'① เงื่อนไขช่องตัวละครแบบสุ่ม {n1} จุด → "ไม่ได้ใช้รูปตัวละคร"')

# ②
ICON = {'🔒': 'lock', '⚠️': 'warning', '✅': 'check_circle'}
n2 = 0
for n in walk(c['phases']):
    if isinstance(n, dict) and n.get('el') == 'text' and isinstance(n.get('value'), str):
        for e, ic in ICON.items():
            if n['value'].startswith(e):
                n['value'] = n['value'][len(e):].lstrip(); n['icon'] = ic; n2 += 1
assert n2 == 6, n2
print(f'② emoji → ไอคอน {n2} จุด')

# ── ยาม ──
s = J(c['phases'])
assert AI not in s.replace('"value": "' + AI, '')  # เหลือได้แค่ในตัวเลือก (ถ้ามี) ไม่อยู่ในเงื่อนไข
bad = re.compile('[\U0001F300-\U0001FAFF⭐✅❌⚠\U0001F512]')
left = [n.get(k) for n in walk(c['phases']) if isinstance(n, dict) for k in ('label', 'value', 'desc', 'placeholder')
        if isinstance(n.get(k), str) and bad.search(n[k])]
assert not left, left
print('✅ ยามผ่าน: ไม่เหลือเงื่อนไขค่าเก่า · ไม่เหลือ emoji บนหน้าจอ')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
