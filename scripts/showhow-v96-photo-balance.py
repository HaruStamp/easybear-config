#!/usr/bin/env python3
"""showhow-v96 — กล่องกำหนดเองของ "ฉาก" กับ "ฉากตอนจบ" ให้เป็นมาตรฐานเดียวกัน (พี่หมีสั่ง 2026-09-24)

ทั้ง 2 กล่องเรียงเหมือนกันเป๊ะ:
   ป้ายช่องพิมพ์ (ไม่บังคับ)
   ช่องพิมพ์
   ส่วนรูป: [ไอคอน + ป้าย] · คำอธิบาย · ช่องรูปสี่เหลี่ยมขนาดเดียวกัน (อัพโหลด / เลือกภาพ ซ้อนบนล่าง)

ฉาก       "อยากให้ฉากเป็นแบบไหน (ไม่บังคับ)" (เดิม "เล่าสถานที่") → ช่องพิมพ์ → "รูปสถานที่ (1-2 รูป)" (เดิมอยู่บน · ย้ายลงล่าง)
ฉากตอนจบ  "อยากให้ออกมาเป็นแบบไหน (ไม่บังคับ)" → ช่องพิมพ์ → "หรือใส่รูปตัวอย่าง" (เฉพาะเรื่องแบบก่อน→หลัง เหมือนเดิม)

เดิม 2 ส่วนรูปหน้าตาคนละแบบ: ฉากใช้แถบประอัพโหลดเต็มความกว้าง (ปุ่มคู่แนวนอน) · ฉากตอนจบใช้ช่องสี่เหลี่ยม + ข้อความข้าง
⇒ ใช้ช่องสี่เหลี่ยม 124px แบบเดียวกันทั้งคู่ · รูปที่ 2 ของฉากโผล่เมื่อใส่รูปแรกแล้ว (ตรรกะเดิม)
ใช้: python3 scripts/showhow-v96-photo-balance.py
"""
import copy, json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
SC = {'op': 'eq', 'a': '{item.sceneMode}', 'b': 'custom'}
SUB = '!text-[13px] @[640px]:!text-[12.5px] font-bold opacity-70 px-0.5'
HINT = '!text-[13px] @[640px]:!text-[12.5px] opacity-50 px-0.5 leading-snug'


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
scene = next(x for x in story['card'] if '"field": "sceneMode"' in J(x))
sc_box = next(x for x in scene['card'] if x.get('when') == SC)
end = next(x for x in story['card'] if '"field": "goal"' in J(x))
en_box = end['card'][2]
ref_row = next(x for x in en_box['card'] if 'into": "endRef' in J(x))
ARC_OK = ref_row['when']

# แม่แบบช่องรูป = ของช่องรูปตัวอย่าง (ขนาดพอดีมือถือแล้วตั้งแต่ v91b)
up_t = next(n for n in walk(ref_row) if isinstance(n, dict) and n.get('el') == 'upload')
pk_t = next(n for n in walk(ref_row) if isinstance(n, dict) and n.get('el') == 'pick-button')
cl_t = next(n for n in walk(ref_row) if isinstance(n, dict) and n.get('fn') == 'clearSlot')
md_t = next(n for n in walk(ref_row) if isinstance(n, dict) and n.get('el') == 'media-slot')
empty_cls = next(n for n in walk(ref_row) if isinstance(n, dict) and n.get('el') == 'box' and 'border-dashed' in str(n.get('className')))['className']
full_cls = next(n for n in walk(ref_row) if isinstance(n, dict) and n.get('el') == 'box' and 'relative' in str(n.get('className')))['className']


def tile(slot, when=None):
    empty = {'op': 'eq', 'a': '{item.slots.%s}' % slot, 'b': ''}
    up = copy.deepcopy(up_t); up['into'] = slot
    pk = copy.deepcopy(pk_t); pk['into'] = slot
    md = copy.deepcopy(md_t); md['src'] = '{item.slots.%s}' % slot
    cl = copy.deepcopy(cl_t); cl['to'] = slot
    t = {'el': 'box', 'className': 'shrink-0', 'card': [
        {'el': 'box', 'className': full_cls, 'when': {'op': 'not', 'a': empty}, 'card': [md, cl]},
        {'el': 'box', 'className': empty_cls, 'when': empty, 'card': [up, pk]},
    ]}
    if when: t['when'] = when
    return t


def photo_area(label, hint, tiles, when=None):
    a = {'el': 'box', 'className': 'flex flex-col gap-1.5 mt-1', 'card': [
        {'el': 'row', 'className': '!gap-1.5 !flex-nowrap items-center', 'card': [
            {'el': 'icon', 'icon': 'add_photo_alternate', 'textSize': 'text-[17px]',
             'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center shrink-0'},
            {'el': 'text', 'value': label, 'className': SUB}]},
        {'el': 'text', 'value': hint, 'className': HINT},
        {'el': 'box', 'className': 'flex flex-row flex-wrap gap-2.5 mt-0.5', 'card': tiles},
    ]}
    if when: a['when'] = when
    return a


room_ta = next(x for x in sc_box['card'] if x.get('field') == 'room')
goal_ta = next(x for x in en_box['card'] if x.get('field') == 'goal')
room1_filled = {'op': 'not', 'a': {'op': 'eq', 'a': '{item.slots.room1}', 'b': ''}}
sc_box['card'] = [
    {'el': 'text', 'value': 'อยากให้ฉากเป็นแบบไหน (ไม่บังคับ)', 'className': SUB},
    room_ta,
    photo_area('รูปสถานที่ (1-2 รูป)', 'ไม่บังคับ · ใช้เป็นฉากเริ่ม และห้องจะไม่เปลี่ยนระหว่างคลิป',
               [tile('room1'), tile('room2', when=room1_filled)]),
]
en_box['card'] = [
    {'el': 'text', 'value': 'อยากให้ออกมาเป็นแบบไหน (ไม่บังคับ)', 'className': SUB},
    goal_ta,
    photo_area('หรือใส่รูปตัวอย่าง', 'ไม่บังคับ · ใช้รูปจากที่อื่นได้ ห้องยังเป็นห้องของงานนี้', [tile('endRef')], when=ARC_OK),
]
print('ฉาก: ป้าย "อยากให้ฉากเป็นแบบไหน (ไม่บังคับ)" → ช่องพิมพ์ → รูปสถานที่ (ย้ายลงล่าง)')
print('ฉากตอนจบ: "อยากให้ออกมาเป็นแบบไหน (ไม่บังคับ)" → ช่องพิมพ์ → รูปตัวอย่าง')
print('ส่วนรูปทั้ง 2 กล่องใช้แบบเดียวกัน: ไอคอน+ป้าย · คำอธิบาย · ช่องสี่เหลี่ยมขนาดเดียวกัน')

# ── ยาม ───────────────────────────────────────────────────────────────────────
sj = J(story)
for s in ('room1', 'room2', 'endRef'):
    assert sj.count('"into": "%s"' % s) == 2, f'{s}: ต้องมีปุ่มอัพโหลด+เลือกภาพ ที่เดียว'
assert 'เล่าสถานที่' not in J([n.get('value') for n in walk(story) if isinstance(n, dict) and n.get('el') == 'text'])
a_sc, a_en = sc_box['card'][2], en_box['card'][2]
strip = lambda a: J({k: v for k, v in a.items() if k != 'when'}).replace('room1', 'X').replace('room2', 'X').replace('endRef', 'X')
assert a_sc['className'] == a_en['className'] and a_sc['card'][0]['className'] == a_en['card'][0]['className']
assert sc_box['card'][0]['className'] == en_box['card'][0]['className'] == SUB
for w in ('sm:', 'md:', 'min-['):
    assert w not in sj
print('✅ ยามผ่าน: ช่องรูปแต่ละช่องมีที่เดียว · 2 กล่องโครงเดียวกัน · ไม่เหลือ "เล่าสถานที่"')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
