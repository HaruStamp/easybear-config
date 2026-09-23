#!/usr/bin/env python3
"""showhow-v86 — ปิดรูที่ v82 ทิ้งไว้: mnPlan ยัง gate ด้วย `values.svChar` ที่ตายไปแล้ว

v82 ย้าย "เห็นคนแค่ไหน" จาก `values.svChar` → `item.people` (ตั้งค่าในงาน)
สคริปต์นั้นแทนชื่อให้ทุกที่ **ยกเว้นบล็อกที่เขียน `when` แบบ predicate string** (`"when": "values.svChar=..."`)
เพราะตัวแทนที่ไล่จาก `{values.svChar}` (มีปีกกา) กับ `"field": "svChar"` เท่านั้น

ผลที่เกิดจริง (ไม่มีใครเห็น เพราะไม่มี error):
  บล็อกใน mnPlan ที่ส่ง **ข้อมูลตัวละครที่ผู้ใช้กรอก** — ชื่อเล่น · เพศ · ช่วงวัย · ลุค/สไตล์
  ⇒ ไม่เคยเข้าบทอีกเลยตั้งแต่ v82 · ผู้ใช้กรอกไปก็ไม่มีผล (AI เลือกเองทุกครั้ง)

🪤 ทำไมยามไม่จับ: ยาม G16 ดู `{item.*}` ที่ gate prompt ของ **op สื่อ** เท่านั้น
   ของนี้เป็น `values.*` ที่ **ไม่มีอยู่แล้ว** ใน op llm ⇒ ต้องใช้ยามคนละข้อ (เพิ่ม G17 ในรอบนี้)

ใช้: python3 scripts/showhow-v86-dead-gate-svchar.py
"""
import json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
OLD, NEW = 'values.svChar=คนเดียวเต็มตัว', 'item.people=คนเดียวเต็มตัว'


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


hit = 0
for n in walk(c):
    if isinstance(n, dict) and n.get('when') == OLD:
        assert 'charName' in json.dumps(n, ensure_ascii=False), 'บล็อกที่เจอไม่ใช่บล็อกข้อมูลตัวละคร — หยุดก่อน'
        n['when'] = NEW
        hit += 1
assert hit == 1, f'ควรเจอ 1 ที่ · เจอ {hit}'
print(f'① mnPlan: when "{OLD}" → "{NEW}"')
print('   ⇒ ชื่อเล่น/เพศ/ช่วงวัย/ลุค ที่ผู้ใช้กรอกในงาน กลับเข้าบทแล้ว')

# ── ยาม: ต้องไม่เหลือชื่อฟิลด์ที่ย้ายไปแล้วในไฟล์อีกเลย ─────────────────────────
s = json.dumps(c, ensure_ascii=False)
for dead in ('svChar', 'svCharSrc', 'svCamMode'):
    assert dead not in s, f'ยังเหลือ {dead} ที่ย้ายไป item แล้ว'
assert '{item.charName}' in s and NEW in s
print('✅ ยามผ่าน: ไม่เหลือ svChar / svCharSrc / svCamMode ในไฟล์อีกเลย')

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nเขียน {P} แล้ว')
