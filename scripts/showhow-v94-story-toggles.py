#!/usr/bin/env python3
"""showhow-v94 — ส่วน "เรื่อง" ให้ลงตัว: ป้ายหน้าตาเดียวกัน · ฉาก/ฉากตอนจบเป็น อัตโนมัติ↔กำหนดเอง · ช่องพิมพ์มีป้ายนำ

พี่หมีทัก (2026-09-24):
  · ป้าย "ฉาก" / "ฉากตอนจบ (ไม่บังคับ)" หน้าตาไม่เหมือน "ผู้แสดงเห็นแค่ไหน" / "ผู้แสดงเป็นอะไร"
  · ช่องพิมพ์ "อยากได้ที่แบบไหน" ควรโชว์เฉพาะตอนเลือกกำหนดเองไหม · ฉากตอนจบด้วยไหม
  · ก่อนช่องพิมพ์ควรมีป้ายนำ

ออกแบบ — ทุกหัวข้อในส่วนเรื่องเป็นทรงเดียวกัน: ป้าย (สไตล์เดียว) → ตัวเลือก (อัตโนมัติเป็นตัวแรก) → รายละเอียดโผล่เฉพาะตอนกำหนดเอง
  ฉาก       [อัตโนมัติ · หมีคิดสถานที่ให้] [กำหนดเอง · ใส่รูปหรือเล่าสถานที่เอง]
            กำหนดเอง → กล่องรายละเอียด: "รูปสถานที่ (1-2 รูป)" + รูป · "เล่าสถานที่ (ไม่บังคับ)" + ช่องพิมพ์
  ฉากตอนจบ  [อัตโนมัติ · หมีคิดตอนจบให้] [กำหนดเอง · บอกเองว่าอยากได้แบบไหน]      (ซ่อนเมื่อทัวร์จุดเด่น)
            กำหนดเอง → กล่องรายละเอียด: "อยากให้ออกมาเป็นแบบไหน" + ช่องพิมพ์ · "หรือใส่รูปตัวอย่าง" (เฉพาะเรื่องแบบก่อน→หลัง)
  ลูกเล่นตอนท้าย (ไม่บังคับ) + ช่องพิมพ์  — ข้อความอิสระล้วน ไม่ต้องมีตัวเลือก
  · อัตโนมัติ = ไม่มีอะไรให้กรอกเลย (เดิม "ฉาก อัตโนมัติ" ยังมีช่องพิมพ์ = ไม่อัตโนมัติจริง)
  · เลิกเขียน "(ไม่บังคับ)" ที่หัวข้อที่มีตัวเลือกอัตโนมัติแล้ว — ตัวเลือกบอกเองว่าไม่ต้องกรอกก็ได้

🔑 ซ่อนแล้วต้องไม่ถูกใช้ — บทอ่าน `{item.room}` / `{item.goal}` ตรง ๆ
   ⇒ แยกบรรทัดในบทเป็นบล็อกที่ gate ด้วย sceneMode/endMode = custom · ภาพจบ (endRef) gate ด้วย endMode ด้วยทุกจุด
   ⇒ `endMode` ต้องส่งลง task (บอร์ดใช้ภาพจบที่ระดับ task)

ใช้: python3 scripts/showhow-v94-story-toggles.py
"""
import copy, json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
SC = {'op': 'eq', 'a': '{item.sceneMode}', 'b': 'custom'}
EC = {'op': 'eq', 'a': '{item.endMode}', 'b': 'custom'}
LABEL = '!text-[13px] @[640px]:!text-[12.5px] opacity-60 px-0.5 mt-1'         # = "ผู้แสดงเห็นแค่ไหน"
SUB = '!text-[13px] @[640px]:!text-[12.5px] font-bold opacity-70 px-0.5'
DETAIL = 'flex flex-col gap-2 rounded-2xl border border-[var(--ev-border)] p-3 mt-1'


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


def J(x):
    return json.dumps(x, ensure_ascii=False)


job = c['phases'][0]['form'][2]['card'][0]['card'][0]
story = next(x for x in job['card'] if '"field": "sceneMode"' in J(x))
people_label = next(n for n in walk(story) if isinstance(n, dict) and n.get('value') == 'ผู้แสดงเห็นแค่ไหน')
assert people_label['className'] == LABEL, 'สไตล์ป้ายอ้างอิงเปลี่ยน — ปรับ LABEL ก่อน'

# ── field endMode ─────────────────────────────────────────────────────────────
for f in (c['collections']['products']['fields'], c['collections']['tasks']['fields']):
    if isinstance(f, dict): f.setdefault('endMode', '')
    elif 'endMode' not in f: f.append('endMode')
c['collections']['products']['addDefaults']['endMode'] = ''
next(o for o in c['ops'] if o['id'] == 'mnQueue')['spawn']['fields']['endMode'] = '{parent.fields.endMode}'

# ── ① ป้ายทุกหัวข้อในส่วนเรื่อง = สไตล์เดียว ─────────────────────────────────
n_lab = 0
for n in walk(story):
    if isinstance(n, dict) and n.get('el') == 'text' and n.get('value') in ('เล่าเรื่องแบบไหน', 'ฉาก', 'ฉากตอนจบ (ไม่บังคับ)', 'ลูกเล่นตอนท้าย (ไม่บังคับ)'):
        n['className'] = LABEL; n_lab += 1
        if n['value'] == 'ฉากตอนจบ (ไม่บังคับ)': n['value'] = 'ฉากตอนจบ'
assert n_lab == 5, n_lab                       # เล่าเรื่องแบบไหน ×2 (มี/ไม่มีสินค้า) · ฉาก · ฉากตอนจบ · ลูกเล่นตอนท้าย
print('① ป้ายหัวข้อในส่วนเรื่องใช้สไตล์เดียวกับ "ผู้แสดงเห็นแค่ไหน" ทั้งหมด (5 ป้าย)')

# ── ② ฉาก: อัตโนมัติไม่มีอะไรให้กรอก · กำหนดเองได้กล่องรายละเอียด ─────────────
scene = next(x for x in story['card'] if '"field": "sceneMode"' in J(x))
grid = next(x for x in scene['card'] if x.get('field') == 'sceneMode')
next(o for o in grid['options'] if o['value'] == 'custom')['desc'] = 'ใส่รูปหรือเล่าสถานที่เอง'
auto_box = next(x for x in scene['card'] if x.get('when') == {'op': 'not', 'a': SC})
cust_box = next(x for x in scene['card'] if x.get('when') == SC)
tiles = next(x for x in cust_box['card'] if 'into": "room1' in J(x))
ta = next(x for x in cust_box['card'] if x.get('field') == 'room')
ta['placeholder'] = 'เช่น ห้องน้ำเล็ก กระเบื้องขาว คราบเหลืองตรงมุม แสงเข้าทางซ้าย'
scene['card'].remove(auto_box)
cust_box['className'] = DETAIL
cust_box['card'] = [
    {'el': 'text', 'value': 'รูปสถานที่ (1-2 รูป)', 'className': SUB},
    {'el': 'text', 'value': 'ใช้เป็นฉากเริ่ม และห้องจะไม่เปลี่ยนระหว่างคลิป', 'className': '!text-[13px] @[640px]:!text-[12.5px] opacity-50 px-0.5 -mt-1'},
    tiles,
    {'el': 'text', 'value': 'เล่าสถานที่ (ไม่บังคับ)', 'className': SUB + ' mt-1'},
    ta,
]
print('② ฉาก: อัตโนมัติ = ไม่มีช่องให้กรอก · กำหนดเอง = กล่อง "รูปสถานที่" + "เล่าสถานที่" มีป้ายนำ')

# ── ③ ฉากตอนจบ: ตัวเลือกเหมือนฉาก ───────────────────────────────────────────
end = next(x for x in story['card'] if '"field": "goal"' in J(x))
end_lab = next(x for x in end['card'] if x.get('el') == 'text' and x.get('value') == 'ฉากตอนจบ')
goal_ta = next(x for x in end['card'] if x.get('field') == 'goal')
ref_row = next(x for x in end['card'] if 'into": "endRef' in J(x))
goal_ta['placeholder'] = 'เช่น เคาน์เตอร์โล่ง ของเข้าที่ หยิบใช้ง่าย'
for n in walk(ref_row):
    if isinstance(n, dict) and n.get('value') == 'หรือใส่รูปตัวอย่าง':
        pass
end_grid = copy.deepcopy(grid)
end_grid['field'] = 'endMode'
end_grid['options'] = [
    {'value': '', 'label': 'อัตโนมัติ', 'desc': 'หมีคิดตอนจบให้', 'icon': 'auto_awesome'},
    {'value': 'custom', 'label': 'กำหนดเอง', 'desc': 'บอกเองว่าอยากได้แบบไหน', 'icon': 'flag'},
]
end['card'] = [end_lab, end_grid, {'el': 'box', 'when': EC, 'className': DETAIL, 'card': [
    {'el': 'text', 'value': 'อยากให้ออกมาเป็นแบบไหน', 'className': SUB},
    goal_ta,
    ref_row,
]}]
print('③ ฉากตอนจบ: อัตโนมัติ / กำหนดเอง · กำหนดเอง = กล่อง "อยากให้ออกมาเป็นแบบไหน" + รูปตัวอย่าง')

# ── ④ ซ่อนแล้วต้องไม่ถูกใช้ ──────────────────────────────────────────────────
ops = {o['id']: o for o in c['ops']}
plan = ops['mnPlan']
OLD = None
for n in walk(plan['prompt']):
    if isinstance(n, list):
        for i, x in enumerate(n):
            if isinstance(x, str) and '{item.room}' in x and '{item.goal}' in x:
                OLD = (n, i, x)
assert OLD, 'หาบรรทัด room/goal ในบทไม่เจอ'
lst, i, s = OLD
a, rest = s.split('{item.room}', 1)
b, rest2 = rest.split('{item.goal}', 1)
lst[i:i + 1] = [a, {'op': 'block', 'sep': '', 'parts': [{'when': SC, 'value': '{item.room}'}]},
                b, {'op': 'block', 'sep': '', 'parts': [{'when': EC, 'value': '{item.goal}'}]}, rest2]
# ภาพจบ: บท (รูป + คำอธิบาย) · บอร์ด (refs + บรรทัดฉากปิด) — เพิ่ม endMode
n_e = 0
for k, b in enumerate(plan['images']):
    if 'endRef' in J(b):
        b['when'] = {'op': 'and', 'list': [b['when'], EC]}; n_e += 1
for n in walk(plan['prompt']):
    if isinstance(n, dict) and isinstance(n.get('when'), dict) and '{item.slots.endRef}' in J(n['when']):
        n['when']['list'].append(EC); n_e += 1
for K in range(1, 7):
    o = ops['mnBoard' if K == 1 else f'mnBoard{K}']
    for a_ in o['refs']['also']:
        if a_.get('slot') == 'endRef':
            a_['when']['list'].append(EC); n_e += 1
    for n in walk(o['prompt']):
        if isinstance(n, dict) and isinstance(n.get('when'), dict):
            w = n['when']
            if w.get('op') == 'and' and any('endRef' in J(x) for x in w.get('list', [])):
                for j, x in enumerate(w['list']):
                    if x == {'op': 'refsFilled', 'key': 'prod', 'from': 'products', 'slot': 'endRef'}:
                        w['list'][j] = {'op': 'and', 'list': [x, EC]}; n_e += 1
                    elif isinstance(x, dict) and x.get('op') == 'not' and 'endRef' in J(x):
                        x['a']['list'].append(EC); n_e += 1
print(f'④ บทอ่านคำบรรยายสถานที่เฉพาะฉากกำหนดเอง · ผลลัพธ์ตอนจบ+ภาพจบเฉพาะตอนจบกำหนดเอง ({n_e} จุด)')

# ── ยาม ───────────────────────────────────────────────────────────────────────
sj = J(story)
assert sj.count('"field": "room"') == 1 and sj.count('"field": "goal"') == 1, 'ช่องพิมพ์ต้องมีที่เดียว'
assert '(ไม่บังคับ)"' not in J([n.get('value') for n in walk(story) if isinstance(n, dict) and n.get('className') == LABEL
                              and n.get('value') in ('ฉาก', 'ฉากตอนจบ')])
labs = [n for n in walk(story) if isinstance(n, dict) and n.get('el') == 'text' and n.get('value') in
        ('เล่าเรื่องแบบไหน', 'มุมกล้อง', 'ผู้แสดงเห็นแค่ไหน', 'ผู้แสดงเป็นอะไร', 'ตัวละคร', 'ฉาก', 'ฉากตอนจบ', 'ลูกเล่นตอนท้าย (ไม่บังคับ)')]
assert all(n['className'] == LABEL for n in labs), 'ป้ายยังไม่เป็นสไตล์เดียว'
ps = J(plan['prompt'])
assert '{item.room}' in ps and '{item.goal}' in ps and J(SC) in ps and J(EC) in ps
for K in range(1, 7):
    o = ops['mnBoard' if K == 1 else f'mnBoard{K}']
    for a_ in o['refs']['also']:
        if a_.get('slot') == 'endRef': assert J(EC) in J(a_['when'])
    assert J(o['prompt']).count(J(EC)) >= 3, f"{o['id']}: บรรทัดฉากปิด 3 ทางต้องรู้จัก endMode"
for w in ('sm:', 'md:', 'min-['):
    assert w not in sj
print('✅ ยามผ่าน: ช่องพิมพ์ที่เดียว · ป้ายสไตล์เดียว · ซ่อนแล้วบท/บอร์ดไม่ใช้')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nเขียน {P} แล้ว')
