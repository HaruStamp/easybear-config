#!/usr/bin/env python3
"""showhow-v102 — เรื่อง "อัตโนมัติ" เห็น ลูกเล่นตอนท้าย + ช่องพิมพ์ฉากตอนจบ (พี่หมีเคาะตามตาราง 2026-09-24)

                     อัตโนมัติ  ก่อน→หลัง  ปัญหา→แก้  ทัวร์  ทีละขั้น  ไทม์แลปส์
ลูกเล่นตอนท้าย          ✅(ใหม่)     ✅        ✅       ✅      ✅        ❌
ฉากตอนจบ (ช่องพิมพ์)     ✅(ใหม่)     ✅        ✅       ❌      ✅        ✅
รูปตัวอย่างฉากจบ          ❌         ✅        ✅       ❌      ✅        ✅   ← ไม่แตะ (เหมือนเดิม)

เหตุผล: อัตโนมัติ = ค่าตั้งต้น ⇒ เดิมผู้ใช้ส่วนใหญ่ไม่เคยเห็น 2 ส่วนนี้ · อัตโนมัติไม่เคยเดาเป็นไทม์แลปส์ ⇒ ลูกเล่นไม่ชน
แก้คู่กัน 2 ฝั่ง (กฎ "ซ่อน = ไม่ใช้"): wrapper บนหน้างาน + เงื่อนไขในบท mnPlan · บอร์ด/วิดีโอไม่เกี่ยว (goal/idea ไปแค่บท)
+ ป้ายช่องพิมพ์ลูกเล่น: "อยากให้มีอะไรพิเศษหลังงานเสร็จ" → "อยากปิดท้ายคลิปด้วยอะไร" (ทัวร์ไม่มี "งาน" ให้เสร็จ)
ใช้: python3 scripts/showhow-v102-auto-end-idea.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
J = lambda x: json.dumps(x, ensure_ascii=False)
ARC = lambda v: {'op': 'eq', 'a': '{item.arc}', 'b': v}
OLD_TL = {'op': 'not', 'a': {'op': 'or', 'list': [ARC(''), ARC('ไทม์แลปส์กล้องนิ่ง')]}}
OLD_TU = {'op': 'not', 'a': {'op': 'or', 'list': [ARC(''), ARC('ทัวร์จุดเด่น')]}}
NEW_TL = {'op': 'not', 'a': ARC('ไทม์แลปส์กล้องนิ่ง')}
NEW_TU = {'op': 'not', 'a': ARC('ทัวร์จุดเด่น')}


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


story = next(x for x in c['phases'][0]['form'][2]['card'][0]['card'][0]['card'] if '"field": "ideaMode"' in J(x))
end = next(x for x in story['card'] if '"field": "endMode"' in J(x))
gag = next(x for x in story['card'] if '"field": "ideaMode"' in J(x))
assert end['when'] == OLD_TU and gag['when'] == OLD_TL
end['when'] = NEW_TU
gag['when'] = NEW_TL
lab = next(n for n in walk(gag) if isinstance(n, dict) and n.get('el') == 'text' and 'หลังงานเสร็จ' in str(n.get('value')))
lab['value'] = 'อยากปิดท้ายคลิปด้วยอะไร (ไม่บังคับ)'
photo = next(n for n in walk(end) if isinstance(n, dict) and n.get('when') == OLD_TU)   # รูปตัวอย่าง: ไม่แตะ
print('UI: ฉากตอนจบ ซ่อนเฉพาะทัวร์ · ลูกเล่น ซ่อนเฉพาะไทม์แลปส์ · รูปตัวอย่างเงื่อนไขเดิม · ป้ายลูกเล่นใหม่')

plan = next(o for o in c['ops'] if o['id'] == 'mnPlan')
n_goal = n_idea = 0
for n in walk(plan['prompt']):
    if not (isinstance(n, dict) and isinstance(n.get('when'), dict) and n['when'].get('op') == 'and' and 'list' in n['when']): continue
    L = n['when']['list']; v = J(n.get('value'))
    if '{item.goal}' in v and OLD_TU in L and not any('endRef' in J(x) for x in L):
        L[L.index(OLD_TU)] = NEW_TU; n_goal += 1
    if '{item.idea}' in v and OLD_TL in L:
        L[L.index(OLD_TL)] = NEW_TL; n_idea += 1
assert n_goal == 1 and n_idea == 1, (n_goal, n_idea)
print('mnPlan: ข้อความฉากตอนจบ + ลูกเล่น ใช้ในโหมดอัตโนมัติด้วย (ภาพจบเงื่อนไขเดิม)')

# ── ยาม ──
s = J(c)
assert s.count(J(OLD_TL)) == 0, 'ยังมีเงื่อนไขลูกเล่นแบบเก่าหลงเหลือ'
assert J(photo['when']) == J(OLD_TU)
for o in c['ops']:
    if o['id'].startswith(('mnBoard', 'mnVideo')):
        assert '{item.goal}' not in J(o) and '{item.idea}' not in J(o), o['id']
print('✅ ยามผ่าน: UI กับบทเงื่อนไขตรงกัน · ภาพจบ/บอร์ด/วิดีโอไม่ถูกแตะ')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
