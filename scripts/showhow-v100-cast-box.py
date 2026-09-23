#!/usr/bin/env python3
"""showhow-v100 — ส่วน "ตัวละคร" หน้าตาเดียวกับกล่องกำหนดเองของ ฉาก / ฉากตอนจบ / ลูกเล่นตอนท้าย (พี่หมีสั่ง 2026-09-24)

เดิม: ป้าย "ตัวละคร" → กล่องพื้นทึบ (bg-ev-bg · p-4) ที่มีตัวเลือกแหล่งหน้าอยู่ข้างใน
      ป้ายช่องเป็นตัวพิมพ์ใหญ่ห่าง ๆ · ช่องรูปหน้ากว้างเต็มแถว + การ์ดเตือนสีเหลือง/เขียว
ใหม่: ป้าย "ตัวละคร" → ตัวเลือก (อยู่นอกกล่อง เหมือนหัวข้ออื่น) → กล่องเส้นขอบ ไม่มีพื้น p-3 (คลาสเดียวกับกล่องฉาก)
      ป้ายช่องใช้สไตล์ป้ายเดียวกับกล่องฉาก · รูปหน้าใช้ส่วนรูปแบบเดียวกับ "รูปฉาก" (ไอคอน+ป้าย · คำอธิบาย · ช่องสี่เหลี่ยม 124px)
ไม่แตะ field / when / value ใด ๆ — เปลี่ยนแค่โครงและคลาส
ใช้: python3 scripts/showhow-v100-cast-box.py
"""
import copy, json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
J = lambda x: json.dumps(x, ensure_ascii=False)
SUB = '!text-[13px] @[640px]:!text-[12.5px] font-bold opacity-70 px-0.5'
HINT = '!text-[13px] @[640px]:!text-[12.5px] opacity-50 px-0.5 leading-snug'
BOX = 'flex flex-col gap-2 rounded-2xl border border-[var(--ev-border)] p-3 mt-1'


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


job = c['phases'][0]['form'][2]['card'][0]['card'][0]
story = next(x for x in job['card'] if '"field": "people"' in J(x))
col = next(x for x in story['card'] if '"field": "peopleSrc"' in J(x))
i = next(k for k, x in enumerate(col['card']) if x.get('el') == 'box' and '"field": "peopleSrc"' in J(x))
box = col['card'][i]
assert box['card'][0]['field'] == 'peopleSrc' and 'bg-[var(--ev-bg)]' in box['className']
sc_box = next(n for n in walk(story) if isinstance(n, dict) and n.get('className') == BOX and n.get('when', {}).get('b') == 'custom')
assert sc_box['card'][0]['className'] == SUB

# ① ตัวเลือกแหล่งหน้าออกมานอกกล่อง · กล่องใช้คลาสของกล่องฉาก
grid = box['card'].pop(0)
grid['className'] = '!min-h-[44px] @[420px]:!min-h-0'
box['className'] = BOX
col['card'].insert(i, grid)

# ② ป้ายช่องทั้งหมดในกล่อง = สไตล์ป้ายกล่องฉาก
for n in walk(box):
    if isinstance(n, dict) and n.get('el') == 'text' and 'uppercase' in str(n.get('className')):
        n['className'] = SUB; n.pop('icon', None)
hint = next(n for n in box['card'] if n.get('el') == 'text' and 'บอกใบ้' in n.get('value', ''))
hint['value'] = 'บอกใบ้เพิ่มได้ (ไม่บังคับ)'; hint['className'] = SUB

# ③ รูปใบหน้า = ส่วนรูปแบบเดียวกับ "รูปฉาก"
face = next(n for n in box['card'] if '"coll": "characters"' in J(n))
rep = next(n for n in walk(face) if isinstance(n, dict) and n.get('el') == 'repeat')
room_tile = next(n for n in walk(sc_box) if isinstance(n, dict) and n.get('el') == 'box' and n.get('className') == 'shrink-0')
FULL = room_tile['card'][0]['className']; EMPTY = room_tile['card'][1]['className']
node = lambda el, extra=None: next(n for n in walk(rep) if isinstance(n, dict) and n.get('el') == el and (extra is None or n.get('fn') == extra))
up, pk, md, cl = (copy.deepcopy(node('upload')), copy.deepcopy(node('pick-button')),
                  copy.deepcopy(node('media-slot')), copy.deepcopy(node('button', 'clearSlot')))
r_up = next(n for n in walk(room_tile) if isinstance(n, dict) and n.get('el') == 'upload')
r_pk = next(n for n in walk(room_tile) if isinstance(n, dict) and n.get('el') == 'pick-button')
r_cl = next(n for n in walk(room_tile) if isinstance(n, dict) and n.get('fn') == 'clearSlot')
up['className'] = r_up['className']; pk['className'] = r_pk['className']; cl['className'] = r_cl['className']
rep['card'] = [{'el': 'box', 'className': 'flex flex-row flex-wrap gap-2.5 mt-0.5', 'card': [{'el': 'box', 'className': 'shrink-0', 'card': [
    {'el': 'box', 'className': FULL, 'when': 'item.slots.face!=', 'card': [md, cl]},
    {'el': 'box', 'className': EMPTY, 'when': 'item.slots.face=', 'card': [up, pk]},
]}]}]
face['className'] = 'flex flex-col gap-1.5 mb-1'
face['card'] = [
    {'el': 'row', 'className': '!gap-1.5 !flex-nowrap items-center', 'card': [
        {'el': 'icon', 'icon': 'add_photo_alternate', 'textSize': 'text-[17px]',
         'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center shrink-0'},
        {'el': 'text', 'value': 'รูปใบหน้า 1 รูป', 'className': SUB}]},
    {'el': 'text', 'value': 'หน้าตรง เห็นใบหน้าชัด — ล็อกหน้าเป็นคนเดิมทุกช็อต ทุกคลิป', 'className': HINT},
    rep,
]
print('ตัวละคร: ตัวเลือกออกนอกกล่อง · กล่องเส้นขอบแบบกล่องฉาก · ป้ายสไตล์เดียวกัน · รูปหน้าช่อง 124px แบบรูปฉาก')

# ── ยาม ──
sj = J(story)
assert sj.count('"into": "face"') == 2 and sj.count('"to": "face"') == 1
assert sj.count('"field": "peopleSrc"') == 1
for f in ('charName', 'charLook', 'charGender', 'charAge'): assert sj.count('"field": "%s"' % f) == 1, f
assert not any('uppercase' in str(n.get('className')) for n in walk(box) if isinstance(n, dict) and n.get('el') == 'text')
assert 'bg-[var(--ev-bg)]' not in J(box)
for w in ('sm:', 'md:', 'min-['): assert w not in J(box)
print('✅ ยามผ่าน: ทุก field/ช่องรูปอยู่ครบที่เดียว · ไม่เหลือสไตล์เก่า')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
