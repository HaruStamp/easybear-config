#!/usr/bin/env python3
"""showhow-v98 — "ลูกเล่นตอนท้าย" เป็น อัตโนมัติ / กำหนดเอง แบบเดียวกับ ฉาก และ ฉากตอนจบ (พี่หมีถาม 2026-09-24)

ทุกหัวข้อในส่วนเรื่องเป็นทรงเดียวกันครบแล้ว: ป้าย → ตัวเลือก (อัตโนมัติตัวแรก) → รายละเอียดโผล่เฉพาะกำหนดเอง
  อัตโนมัติ = หมีใส่ลูกเล่นเองถ้าเหมาะกับงาน (กฎข้อ 9 "มุกปิดท้าย = การใช้งานแถม" ในบทมีอยู่แล้ว)
  กำหนดเอง = กล่อง "อยากให้มีอะไรพิเศษหลังงานเสร็จ (ไม่บังคับ)" + ช่องพิมพ์
· ไอคอนกำหนดเองใช้ `edit_note` (ไม่ใช่รูปภาพเหมือนฉาก/ฉากตอนจบ — กล่องนี้ไม่มีช่องใส่รูป ใช้ไอคอนรูปจะเข้าใจผิด)
· ซ่อนแล้วไม่ถูกใช้: บทอ่าน {item.idea} เฉพาะ ideaMode=custom (+ เรื่องแบบที่โชว์ส่วนนี้ ตาม v97)
· `idea` ใช้แค่ในบท (ระดับงาน) ⇒ ไม่ต้องส่งลง task
ใช้: python3 scripts/showhow-v98-idea-toggle.py
"""
import copy, json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
IC = {'op': 'eq', 'a': '{item.ideaMode}', 'b': 'custom'}
SUB = '!text-[13px] @[640px]:!text-[12.5px] font-bold opacity-70 px-0.5'
DETAIL = 'flex flex-col gap-2 rounded-2xl border border-[var(--ev-border)] p-3 mt-1'


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


def J(x): return json.dumps(x, ensure_ascii=False)


pf = c['collections']['products']['fields']
if isinstance(pf, dict): pf.setdefault('ideaMode', '')
elif 'ideaMode' not in pf: pf.append('ideaMode')
c['collections']['products']['addDefaults']['ideaMode'] = ''

job = c['phases'][0]['form'][2]['card'][0]['card'][0]
story = next(x for x in job['card'] if '"field": "sceneMode"' in J(x))
end = next(x for x in story['card'] if '"field": "goal"' in J(x))
idea = next(x for x in story['card'] if '"field": "idea"' in J(x))
lab = next(n for n in walk(idea) if isinstance(n, dict) and n.get('el') == 'text' and n.get('value') == 'ลูกเล่นตอนท้าย (ไม่บังคับ)')
ta = next(n for n in walk(idea) if isinstance(n, dict) and n.get('field') == 'idea')
end_grid = next(x for x in end['card'] if x.get('field') == 'endMode')
lab['value'] = 'ลูกเล่นตอนท้าย'
grid = copy.deepcopy(end_grid)
grid['field'] = 'ideaMode'
grid['options'] = [
    {'value': '', 'label': 'อัตโนมัติ', 'desc': 'หมีใส่ให้ถ้าเหมาะกับงาน', 'icon': 'auto_awesome'},
    {'value': 'custom', 'label': 'กำหนดเอง', 'desc': 'บอกเองว่าอยากได้ลูกเล่นอะไร', 'icon': 'edit_note'},
]
idea['card'] = [lab, grid, {'el': 'box', 'when': IC, 'className': DETAIL, 'card': [
    {'el': 'text', 'value': 'อยากให้มีอะไรพิเศษหลังงานเสร็จ (ไม่บังคับ)', 'className': SUB}, ta]}]

plan = next(o for o in c['ops'] if o['id'] == 'mnPlan')
n = 0
for x in walk(plan['prompt']):
    if isinstance(x, dict) and x.get('value') == '{item.idea}' and isinstance(x.get('when'), dict):
        x['when'] = {'op': 'and', 'list': [x['when'], IC]}; n += 1
assert n == 1

sj = J(story)
assert sj.count('"field": "idea"') == 1 and '"field": "ideaMode"' in sj
assert J(IC) in J(plan['prompt'])
for w in ('sm:', 'md:', 'min-['):
    assert w not in J(idea)
print('ลูกเล่นตอนท้าย: อัตโนมัติ / กำหนดเอง · ช่องพิมพ์โผล่เฉพาะกำหนดเอง · บทอ่าน idea เฉพาะกำหนดเอง')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
