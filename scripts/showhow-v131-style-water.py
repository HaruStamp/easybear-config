#!/usr/bin/env python3
"""showhow-v131 — สไตล์ภาพที่ 9 "สีน้ำ" (คีย์ `water`) · ตัวเลือกบนจอครบ 10 (รวมอัตโนมัติ) · พี่หมีสั่ง 2026-10-13

กติกาเดิมของสไตล์ (v121-v125): ยาวไม่เกินประโยคสมจริง — บอร์ด ≤ 86 · วิดีโอ ≤ 50 · วิดีโอเป็นอังกฤษล้วน (บทเรียน v21)
สไตล์วาด = บอกว่า "ทุกช่องทุกสิ่ง" + ห้ามเป็นภาพถ่ายจริง (v122) + styleNegEN ท้าย Negative
คีย์เดียวกับ podcast (แจ้ง podcast เพิ่ม `water` ให้ตรง)
ใช้: python3 scripts/showhow-v131-style-water.py  (รันบน v130)
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
L = c['lookups']
assert 'water' not in L['styleBoard']
L['styleBoard']['water'] = 'ภาพวาดสีน้ำแบบนิทานภาพ สีซึมนุ่ม เห็นเนื้อกระดาษ ทุกช่องทุกสิ่ง ห้ามเป็นภาพถ่ายจริง'
L['styleVideoEN']['water'] = 'watercolor storybook art, soft washes, paper grain'
L['stylePlan']['water'] = 'ภาพวาดสีน้ำแบบนิทานภาพ สีอ่อนนุ่ม ทุกอย่างในฉากเป็นภาพวาด'
L['styleNegEN']['water'] = L['styleNegEN']['anime']
assert len(L['styleBoard']['water']) <= len(L['styleBoard']['real']), len(L['styleBoard']['water'])
assert len(L['styleVideoEN']['water']) <= len(L['styleVideoEN']['real']), len(L['styleVideoEN']['water'])
assert all(ord(ch) < 128 for ch in L['styleVideoEN']['water'])
n = 0
def walk(x):
    global n
    if isinstance(x, dict):
        if x.get('field') == 'svStyle' and isinstance(x.get('options'), list):
            assert not any(o['value'] == 'water' for o in x['options'])
            x['options'].append({'value': 'water', 'label': 'สีน้ำ', 'desc': 'นิทานภาพ สีนุ่ม', 'icon': 'palette'}); n += 1
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
walk(c)
assert n == 1, n
opts = set()
def grab(x):
    if isinstance(x, dict):
        if x.get('field') == 'svStyle' and isinstance(x.get('options'), list): opts.update(o['value'] for o in x['options'])
        for v in x.values(): grab(v)
    elif isinstance(x, list):
        for v in x: grab(v)
grab(c)
assert opts == set(L['styleBoard']) == set(L['styleVideoEN']) == set(L['styleNegEN']), opts ^ set(L['styleBoard'])
assert opts - {'', 'real'} == set(L['stylePlan'])
print(f'✅ v131: สไตล์ {len(opts)} ตัวเลือก · บอร์ด {len(L["styleBoard"]["water"])} · วิดีโอ {len(L["styleVideoEN"]["water"])}')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
