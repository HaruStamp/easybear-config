#!/usr/bin/env python3
"""showhow-v89 — ช่วงที่ยังไม่มีบท ห้ามวาด (กันเครดิตไหลตอนผู้ใช้เพิ่มความยาวทีหลัง)

เจอจริง 2026-09-23: งานที่ผลิตคลิป 10 วิ ไปแล้ว พอเปลี่ยนความยาวเป็น 50 วิ แล้วกดผลิต
  → `plan.media = 8` ทันที (ช่วง 2-5 ของ **task เดิม**)
  → แต่ task เดิมมีบทแค่ 5 ฉาก · product เป็น done แล้ว ⇒ **mnPlan ไม่รันใหม่**
  ⇒ ช่วง 2-5 จะถูกวาดจาก **ฟิลด์บทที่ว่างเปล่า** = ภาพมั่ว + เสียเครดิต 8 ชิ้น (~120 เครดิต) เงียบ ๆ

แก้: `op.where` ให้ mnBoardK/mnVideoK (K≥2) เช็คว่า **ฉากแรกของช่วงนั้นมีบทจริง**
     (engine v1.15.0 รองรับ where-AND ใน productLoop แล้ว ⇒ ใส่ได้โดยไม่ชนกับ where ของ loop)
     ไม่มีบท = ข้ามเงียบ ๆ ไม่วาด ไม่เสียเครดิต · ผู้ใช้กด "คิดบทใหม่" แล้วค่อยวาดครบ

🪤 ห้ามใส่ที่ mnBoard/mnVideo (ช่วง 1) — ช่วงแรกคือช่วงที่ต้องวาดเสมอ และประตู "คลิปเสร็จ" นับจาก slots.video ของช่วง 1

ใช้: python3 scripts/showhow-v89-part-needs-script.py
"""
import json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))

n = 0
for op in c['ops']:
    oid = op['id']
    for base in ('mnBoard', 'mnVideo'):
        if oid.startswith(base) and oid != base:
            k = int(oid[len(base):])
            first = 5 * (k - 1) + 1              # ช่วง 2 → ฉาก 6 · ช่วง 3 → ฉาก 11 …
            assert op.get('where') is None, f'{oid} มี where อยู่แล้ว: {op["where"]!r}'
            op['where'] = f's{first}en!='
            n += 1
            print(f'  {oid}: where = "s{first}en!=" (ช่วงนี้เริ่มที่ฉาก {first})')
assert n == 10, f'ควรใส่ 10 op (บอร์ด 2-6 + วิดีโอ 2-6) · ใส่ {n}'

# ── ยาม ───────────────────────────────────────────────────────────────────────
for op in c['ops']:
    oid = op['id']
    if oid in ('mnBoard', 'mnVideo'):
        assert op.get('where') is None, f'{oid} (ช่วงแรก) ห้ามมี where — ต้องวาดเสมอ'
    if oid.startswith(('mnBoard', 'mnVideo')) and oid not in ('mnBoard', 'mnVideo'):
        w = op['where']
        assert w.endswith('en!='), f'{oid}: where ต้องเช็ค "ฉากแรกของช่วงมีบทอังกฤษ" · ได้ {w!r}'
        # ต้องตรงกับเลขฉากที่ prompt ของ op นั้นพูดถึงจริง (กันคัดลอกเลขผิด)
        scene = w[1:w.index('en')]
        assert '{item.s%sen}' % scene in json.dumps(op['prompt'], ensure_ascii=False) or \
               '{item.s%sth}' % scene in json.dumps(op['prompt'], ensure_ascii=False), \
            f'{oid}: where เช็คฉาก {scene} แต่ prompt ไม่ได้พูดถึงฉากนั้น'
print(f'✅ ยามผ่าน: {n} op มี where ตรงกับเลขฉากใน prompt ของตัวเอง · ช่วงแรกไม่มี where')

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nเขียน {P} แล้ว')
