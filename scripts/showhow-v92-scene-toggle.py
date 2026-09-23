#!/usr/bin/env python3
"""showhow-v92 — จัดหน้างานใหม่ตามที่พี่หมีเคาะ: ฉาก "อัตโนมัติ / กำหนดเอง" อยู่ในส่วนเรื่อง · คำกลางสำหรับผู้แสดง

ที่มา (พี่หมี 2026-09-24): หน้างานถามเรื่อง "ตอนนี้ที่นี่เป็นยังไง" ซ้ำ 4 ที่ (รูปห้อง · บรรยายห้อง · ตอนนี้สภาพ · รูปตอนเริ่ม)
และ "อยากให้จบ" กับ "มุกปิดท้าย (…จบด้วย)" ฟังเป็นช่องเดียวกัน ⇒ ผู้ใช้ไม่รู้จะกรอกช่องไหน

① ฉาก → ย้ายเข้าส่วน "เรื่อง" เป็นตัวเลือก 2 ทาง (ทรงเดียวกับทุกตัวเลือกในแอปที่มี "อัตโนมัติ")
     [อัตโนมัติ · หมีคิดสถานที่ให้]  → ช่องพิมพ์ "อยากได้ที่แบบไหน" (ไม่บังคับ)
     [กำหนดเอง ⭐แนะนำ · ใส่รูปสถานที่] → รูป 1-2 รูป + "เล่าเพิ่ม" (ไม่บังคับ)
   · ลบส่วน "ฉาก" เดิม · ลบช่อง "ตอนนี้สภาพเป็นยังไง" และ "รูปตอนเริ่ม" (รูปสถานที่ = ฉากเริ่มอยู่แล้ว — บทสั่ง "ฉาก 1 = สภาพตามรูปนี้")
   · 🪤 รูปสถานที่ 1-2 รูปเท่าเดิม (ไม่ใช่ 3) — บอร์ดช่วงหลังเต็มเพดาน 10 อยู่แล้ว (G18)
   · 🔑 กดกลับเป็น "อัตโนมัติ" แล้ว **รูปที่ใส่ไว้ต้องไม่ถูกใช้** — ทุกจุดที่ใช้ room1/room2 (บท + บอร์ด 6 + วิดีโอ 6) gate ด้วย sceneMode=custom
     ⇒ ต้องส่ง sceneMode ลง task ด้วย (spawn) เพราะ LOCATION LOCK อยู่ใน prompt ระดับ task
② "อยากให้จบแบบไหน" → **"ฉากตอนจบ"** (ทำเสร็จอยากได้แบบไหน + รูปตัวอย่าง) · "ไอเดีย / มุกปิดท้าย" → **"ลูกเล่นตอนท้าย"**
   · ข้อความฉากตอนจบโชว์ทุกเรื่องแบบ ยกเว้นทัวร์จุดเด่น (อัตโนมัติคือค่าตั้งต้น — ถ้าซ่อน คนส่วนใหญ่จะไม่เห็นเลย)
   · รูปตัวอย่างตอนจบโชว์เฉพาะเรื่องแบบที่มีก่อน→หลังเหมือนเดิม (ARC_OK จาก v91)
③ "เห็นคนแค่ไหน" → **"ผู้แสดงเห็นแค่ไหน"** + ป้ายตัวเลือกเป็นคำกลาง (ผู้แสดงเป็นสัตว์ได้แล้ว) · value ไม่แตะ (เป็น key ของ lookup)
④ ตัวละคร (peopleSrc) เปิดมาไม่มีปุ่มถูกเลือก — งานที่ค่าว่าง ⇒ ตัวเลือกแรก value '' = **"สุ่มตัวละคร"** (ทรงเดียวกับ castKind v91)
   + lookup คีย์ "<people>|" ให้ค่าว่างทำงานเหมือนสุ่ม

ใช้: python3 scripts/showhow-v92-scene-toggle.py
"""
import copy, json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
SRC_AI = 'AI เลือกนาย/นางแบบให้เหมาะกับสินค้า'
CUSTOM = {'op': 'eq', 'a': '{item.sceneMode}', 'b': 'custom'}
NOT_TOUR = {'op': 'not', 'a': {'op': 'eq', 'a': '{item.arc}', 'b': 'ทัวร์จุดเด่น'}}


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


def J(x):
    return json.dumps(x, ensure_ascii=False)


def rf(slot):
    return {'op': 'refsFilled', 'key': 'prod', 'from': 'products', 'slot': slot}


job = c['phases'][0]['form'][2]['card'][0]['card'][0]
scene, story = job['card'][4], job['card'][5]
assert 'into": "room1' in J(scene) and '"field": "arc"' in J(story), 'โครงหน้างานเปลี่ยน — หาใหม่ก่อน'

# ── ① field sceneMode ─────────────────────────────────────────────────────────
pf, tf = c['collections']['products']['fields'], c['collections']['tasks']['fields']
for f in (pf, tf):
    if isinstance(f, dict): f.setdefault('sceneMode', '')
    elif 'sceneMode' not in f: f.append('sceneMode')
c['collections']['products']['addDefaults']['sceneMode'] = ''
q = next(o for o in c['ops'] if o['id'] == 'mnQueue')
q['spawn']['fields']['sceneMode'] = '{parent.fields.sceneMode}'

# ── ① UI: บล็อกฉากในส่วนเรื่อง ────────────────────────────────────────────────
label_tpl = next(x for x in story['card'][2]['card'] if x.get('value') == 'เล่าเรื่องแบบไหน')      # ป้ายหัวข้อ
grid_tpl = next(x for x in story['card'][2]['card'] if x.get('field') == 'camMode')                 # grid-select 2 คอลัมน์
room_tiles = scene['card'][1]
room_box = scene['card'][2]
room_ta = next(n for n in walk(room_box) if isinstance(n, dict) and n.get('field') == 'room')
lab = copy.deepcopy(label_tpl); lab['value'] = 'ฉาก'; lab.pop('when', None)
grid = copy.deepcopy(grid_tpl); grid.pop('when', None)
grid.update({'field': 'sceneMode', 'options': [
    {'value': '', 'label': 'อัตโนมัติ', 'desc': 'หมีคิดสถานที่ให้', 'icon': 'auto_awesome'},
    {'value': 'custom', 'label': 'กำหนดเอง ⭐แนะนำ', 'desc': 'ใส่รูปสถานที่ของคุณ', 'icon': 'add_photo_alternate'},
]})
ta_auto = copy.deepcopy(room_ta); ta_auto['placeholder'] = 'อยากได้ที่แบบไหน (ไม่บังคับ) เช่น ครัวโทนอุ่น เคาน์เตอร์ไม้'
ta_custom = copy.deepcopy(room_ta); ta_custom['placeholder'] = 'เล่าเพิ่ม (ไม่บังคับ) เช่น คราบเหลืองตรงมุม แสงเข้าทางซ้าย'
scene_block = {'el': 'box', 'className': 'flex flex-col gap-1.5', 'card': [
    lab, grid,
    {'el': 'box', 'when': {'op': 'not', 'a': CUSTOM}, 'className': 'flex flex-col gap-1.5 mt-1', 'card': [ta_auto]},
    {'el': 'box', 'when': CUSTOM, 'className': 'flex flex-col gap-2 mt-1', 'card': [
        {'el': 'text', 'value': 'รูปสถานที่ 1-2 รูป · ใช้เป็นฉากเริ่ม และห้องจะไม่เปลี่ยนระหว่างคลิป',
         'className': '!text-[14px] @[640px]:!text-[13px] opacity-60 px-0.5'},
        copy.deepcopy(room_tiles), ta_custom]},
]}
job['card'].pop(4)                                                            # ลบส่วนฉากเดิมทั้งส่วน
box_before = next(x for x in story['card'] if '"field": "before"' in J(x))
i_before = story['card'].index(box_before)
story['card'][i_before] = scene_block                                         # ฉากเข้าแทนที่ "ตอนนี้สภาพเป็นยังไง" (+ รูปตอนเริ่ม)
print('① ฉาก: ย้ายเข้าส่วนเรื่อง เป็น อัตโนมัติ / กำหนดเอง ⭐แนะนำ · ลบส่วนฉากเดิม · ลบ "ตอนนี้สภาพ" และ "รูปตอนเริ่ม"')

# ── ① (ต่อ) กำหนดเองเท่านั้นที่ใช้รูปสถานที่ ─────────────────────────────────
ops = {o['id']: o for o in c['ops']}
plan = ops['mnPlan']
n_img = 0
for i, b in enumerate(plan['images']):
    if b in ('{item.slots.room1}', '{item.slots.room2}'):
        plan['images'][i] = {'op': 'cond', 'when': CUSTOM, 'then': b}; n_img += 1
assert n_img == 2
n_note = 0
for n in walk(plan['prompt']):
    if isinstance(n, dict) and n.get('when') == 'item.slots.room1!=':
        n['when'] = {'op': 'and', 'list': [{'op': 'not', 'a': {'op': 'eq', 'a': '{item.slots.room1}', 'b': ''}}, CUSTOM]}; n_note += 1
assert n_note == 1
n_ref = n_lock = 0
for o in c['ops']:
    if not o['id'].startswith(('mnBoard', 'mnVideo')): continue
    for a in o['refs'].get('also', []):
        if a.get('slot') in ('room1', 'room2'):
            a['when'] = {'op': 'and', 'list': [a['when'], CUSTOM]} if a.get('when') else CUSTOM; n_ref += 1
    for n in walk(o['prompt']):
        if isinstance(n, dict) and n.get('when') == rf('room1'):
            n['when'] = {'op': 'and', 'list': [rf('room1'), CUSTOM]}; n_lock += 1
assert n_ref == 24 and n_lock >= 12, (n_ref, n_lock)
print(f'   รูปสถานที่ใช้เฉพาะ "กำหนดเอง": บท (รูป 2 + คำอธิบาย 1) · refs {n_ref} จุด · LOCATION LOCK {n_lock} บล็อก')

# ภาพเปิด (openRef) — ช่องถูกลบแล้ว ⇒ ถอดการใช้งานทุกจุด (slot คงไว้ ไม่ทำให้ของเก่าพัง)
plan['images'] = [b for b in plan['images'] if 'openRef' not in J(b)]
for n in list(walk(plan['prompt'])):
    if isinstance(n, list):
        n[:] = [x for x in n if not (isinstance(x, dict) and 'item.slots.openRef' in J(x.get('when')))]
for K in range(1, 7):
    o = ops['mnBoard' if K == 1 else f'mnBoard{K}']
    o['refs']['also'] = [a for a in o['refs']['also'] if a.get('slot') != 'openRef']
    parts = o['prompt']['parts']
    o['prompt']['parts'] = [x for x in parts if not (isinstance(x, dict) and 'ภาพอ้างอิงฉากเปิด' in J(x))]
assert 'openRef' not in J(c['ops']) and 'ภาพอ้างอิงฉากเปิด' not in J(c['ops'])
print('   ถอดภาพเปิด (openRef) ออกจากบท/บอร์ดทุกจุด')

# ── ② ฉากตอนจบ · ลูกเล่นตอนท้าย ─────────────────────────────────────────────
box_goal = next(x for x in story['card'] if '"field": "goal"' in J(x))
box_goal['when'] = NOT_TOUR
gl = next(x for x in box_goal['card'] if x.get('el') == 'text')
gl['value'] = 'ฉากตอนจบ (ไม่บังคับ)'
gta = next(x for x in box_goal['card'] if x.get('field') == 'goal')
gta['placeholder'] = 'ทำเสร็จอยากได้แบบไหน เช่น เคาน์เตอร์โล่ง ของเข้าที่ หยิบใช้ง่าย'
for n in walk(box_goal):
    if isinstance(n, dict) and n.get('value') == 'หรือใส่รูปตัวอย่างตอนจบ':
        n['value'] = 'หรือใส่รูปตัวอย่าง'
box_idea = next(x for x in story['card'] if '"field": "idea"' in J(x))
for n in walk(box_idea):
    if isinstance(n, dict) and n.get('el') == 'text' and isinstance(n.get('value'), str):
        if 'มุกปิดท้าย' in n['value']: n['value'] = 'ลูกเล่นตอนท้าย (ไม่บังคับ)'
        elif 'จบด้วย' in n['value']: n['value'] = 'อยากให้มีอะไรพิเศษหลังงานเสร็จ'
    if isinstance(n, dict) and n.get('field') == 'idea':
        n['placeholder'] = 'เช่น ลองใช้จริง · เปิดไฟดูตอนกลางคืน · แมวเดินมาเล่น'
print('② "อยากให้จบ" → "ฉากตอนจบ" (ซ่อนเฉพาะทัวร์) · "ไอเดีย / มุกปิดท้าย" → "ลูกเล่นตอนท้าย"')

# ── ③ คำกลางสำหรับผู้แสดง ────────────────────────────────────────────────────
people = next(n for n in walk(job) if isinstance(n, dict) and n.get('field') == 'people' and n.get('options'))
NEW_PEOPLE = {
    '': ('อัตโนมัติ', 'หมีเลือกให้เข้ากับงาน'),
    'เห็นแต่มือ ไม่เห็นหน้า': ('เห็นแค่มือ', 'มือหรืออุ้งเท้า · ไม่เห็นหน้า'),
    'คนเดียวเต็มตัว': ('เห็นเต็มตัว', 'ผู้แสดง 1 คนหรือ 1 ตัว'),
    'ทีมช่างเบลอเคลื่อนไหวเร็ว': ('ทีมงาน', 'หลายคน/หลายตัว ตามงาน เช่น เชฟ แม่บ้าน'),
    'ไม่มีคน': ('ไม่มีผู้แสดง', 'เห็นแต่พื้นที่และของ'),
}
for o in people['options']:
    o['label'], o['desc'] = NEW_PEOPLE[o['value']]
n_txt = 0
for n in walk(c['phases']):
    if isinstance(n, dict) and n.get('el') == 'text' and isinstance(n.get('value'), str):
        v = n['value']
        v2 = v.replace('เห็นคนแค่ไหน', 'ผู้แสดงเห็นแค่ไหน').replace('"ไม่มีคน"', '"ไม่มีผู้แสดง"')
        if v2 != v: n['value'] = v2; n_txt += 1
print(f'③ "เห็นคนแค่ไหน" → "ผู้แสดงเห็นแค่ไหน" + ป้ายตัวเลือก 5 ตัวเป็นคำกลาง · ข้อความบนจอ {n_txt} จุด · value ไม่แตะ')

# ── ④ ตัวละคร: ค่าว่าง = สุ่ม ──────────────────────────────────────────────────
src = next(n for n in walk(job) if isinstance(n, dict) and n.get('field') == 'peopleSrc' and n.get('options'))
ai = next(o for o in src['options'] if o['value'] == SRC_AI)
ai['value'], ai['desc'] = '', 'หมีสร้างผู้แสดงให้เหมาะกับงาน'
face = next(o for o in src['options'] if o['value'] != '')
face['desc'] = 'ล็อกหน้าจากรูปที่แนบ — ตัวเดิมทุกช็อต'
c['collections']['products']['addDefaults']['peopleSrc'] = ''
n_key = 0
for t in ('charPlan', 'charBoard', 'charVideoEN'):
    lk = c['lookups'][t]
    for k in list(lk):
        if k.endswith('|' + SRC_AI):
            lk[k[: -len(SRC_AI)]] = lk[k]; n_key += 1              # "<people>|" = เหมือนสุ่ม · คงคีย์เดิมไว้ให้งานเก่า
print(f'④ ตัวละคร: ตัวแรก = "สุ่มตัวละคร" (value ว่าง) · lookup คีย์ใหม่ {n_key} ตัว')

# ── ยาม ───────────────────────────────────────────────────────────────────────
s = J(c)
assert 'into": "room1' in J(story) and J(job).count('"into": "room1"') == 2, 'ช่องรูปสถานที่ต้องอยู่ในส่วนเรื่องที่เดียว'
assert '"field": "before"' not in J(job) and '"into": "openRef"' not in J(job)
assert J(job).count('"field": "room"') == 2                                   # 2 ทาง (อัตโนมัติ/กำหนดเอง) · โชว์ทีละทาง
assert [o['value'] for o in grid['options']] == ['', 'custom']
assert [o['value'] for o in src['options']][0] == '' and c['collections']['products']['addDefaults']['peopleSrc'] == ''
assert all(o['value'] in NEW_PEOPLE for o in people['options'])
assert 'เห็นคนแค่ไหน' not in J(c['phases'])
for t in ('charPlan', 'charBoard', 'charVideoEN'):
    for pv in NEW_PEOPLE:
        assert (pv + '|') in c['lookups'][t], f'{t} ขาดคีย์ "{pv}|"'
for o in c['ops']:
    if o['id'].startswith(('mnBoard', 'mnVideo')):
        for a in o['refs'].get('also', []):
            if a.get('slot') in ('room1', 'room2'):
                assert 'sceneMode' in J(a.get('when')), f"{o['id']}: {a['slot']} ยังไม่ gate"
        for n in walk(o['prompt']):
            if isinstance(n, dict) and isinstance(n.get('when'), dict) and rf('room1') in (n['when'].get('list') or []):
                assert CUSTOM in n['when']['list'], f"{o['id']}: LOCATION LOCK ไม่มีเงื่อนไขกำหนดเอง"
            assert not (isinstance(n, dict) and n.get('when') == rf('room1')), f"{o['id']}: LOCATION LOCK ยังไม่ gate"
for w in ('sm:', 'md:', 'min-['):
    assert w not in J(scene_block), f'UI ใหม่ห้ามใช้ {w}'
print('✅ ยามผ่าน: รูปสถานที่ที่เดียว · ไม่มีช่องซ้ำ · รูปห้องใช้เฉพาะกำหนดเองทุกจุด · ค่าว่าง = อัตโนมัติ/สุ่ม · value ไม่แตะ')

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nเขียน {P} แล้ว')
