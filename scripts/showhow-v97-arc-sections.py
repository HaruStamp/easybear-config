#!/usr/bin/env python3
"""showhow-v97 — โชว์ "ฉากตอนจบ" / "ลูกเล่นตอนท้าย" ตามเรื่องแบบ (พี่หมีทัก 2026-09-24: บางเรื่องแบบยังโชว์ทั้งที่ไม่ควร)

| เล่าเรื่องแบบไหน      | ฉากตอนจบ | ลูกเล่นตอนท้าย |
| อัตโนมัติ             | ซ่อน     | ซ่อน   ← หมีคิดให้ทั้งหมด
| ก่อน→หลัง · ปัญหา→แก้ · ทีละขั้น | โชว์ | โชว์
| ทัวร์จุดเด่น          | ซ่อน     | โชว์   ← ไม่มีก่อน-หลัง แต่มีการใช้งานแถมได้
| ไทม์แลปส์             | โชว์     | ซ่อน   ← กล้องนิ่ง คนเป็นเงาเบลอ ลูกเล่นมองไม่เห็น

🔑 ซ่อนแล้วต้องไม่ถูกใช้: บทอ่าน {item.goal} ต้องผ่านเงื่อนไขเรื่องแบบด้วย (เดิมเช็คแค่ endMode) · {item.idea} gate ด้วยเงื่อนไขเดียวกับ UI
   (ภาพจบเช็คเรื่องแบบอยู่แล้วตั้งแต่ v91)
ใช้: python3 scripts/showhow-v97-arc-sections.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ARC = '{item.arc}'
eq = lambda v: {'op': 'eq', 'a': ARC, 'b': v}
END_OK = {'op': 'not', 'a': {'op': 'or', 'list': [eq(''), eq('ทัวร์จุดเด่น')]}}          # = ARC_OK ของ v91
IDEA_OK = {'op': 'not', 'a': {'op': 'or', 'list': [eq(''), eq('ไทม์แลปส์กล้องนิ่ง')]}}
EC = {'op': 'eq', 'a': '{item.endMode}', 'b': 'custom'}


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


def J(x): return json.dumps(x, ensure_ascii=False)


job = c['phases'][0]['form'][2]['card'][0]['card'][0]
story = next(x for x in job['card'] if '"field": "sceneMode"' in J(x))
end = next(x for x in story['card'] if '"field": "goal"' in J(x))
idea = next(x for x in story['card'] if '"field": "idea"' in J(x))
end['when'] = END_OK
idea['when'] = IDEA_OK

plan = next(o for o in c['ops'] if o['id'] == 'mnPlan')
n_goal = 0
for n in walk(plan['prompt']):
    if isinstance(n, dict) and n.get('when') == EC and n.get('value') == '{item.goal}':
        n['when'] = {'op': 'and', 'list': [EC, END_OK]}; n_goal += 1
assert n_goal == 1
hit = None
for n in walk(plan['prompt']):
    if isinstance(n, list):
        for i, x in enumerate(n):
            if isinstance(x, str) and '{item.idea}' in x:
                hit = (n, i, x)
assert hit
lst, i, s = hit
a, b = s.split('{item.idea}', 1)
lst[i:i + 1] = [a, {'op': 'block', 'sep': '', 'parts': [{'when': IDEA_OK, 'value': '{item.idea}'}]}, b]

sj = J(story)
assert J(END_OK) in J(end.get('when')) and J(IDEA_OK) in J(idea.get('when'))
assert '{item.idea}' in J(plan['prompt']) and J(IDEA_OK) in J(plan['prompt'])
print('ฉากตอนจบ: ซ่อนเมื่อ อัตโนมัติ/ทัวร์ · ลูกเล่นตอนท้าย: ซ่อนเมื่อ อัตโนมัติ/ไทม์แลปส์ · บทไม่อ่านของที่ซ่อน')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
