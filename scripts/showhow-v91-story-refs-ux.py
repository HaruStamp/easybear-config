#!/usr/bin/env python3
"""showhow-v91 — จัดหน้างานใหม่ตามที่พี่หมีทัก 3 เรื่อง + บั๊กที่เจอระหว่างไล่

① ภาพเปิด/จบ "งง" (พี่หมี) → ย้ายไปอยู่ **ในส่วน "เรื่อง" ใต้ช่อง "ตอนนี้" / "อยากให้จบ"**
   เดิม (v90) เป็นกล่องพับลอย ๆ ในส่วน "ฉาก" ชื่อ "อยากให้เปิด–จบฉากประมาณไหน" — นามธรรม ไม่รู้ว่าผูกกับอะไร
   ใหม่: ใต้ "ตอนนี้สภาพเป็นยังไง" = "หรือใส่รูปตอนเริ่ม" · ใต้ "อยากให้จบแบบไหน" = "หรือใส่รูปตัวอย่างตอนจบ"
   ⇒ ผู้ใช้เข้าใจเองว่า "เล่าด้วยคำ หรือด้วยรูป ก็ได้" · ไม่ต้องอธิบายคำว่า "อ้างอิง"
   **โชว์เฉพาะเรื่องแบบที่มีตอนเริ่ม→ตอนจบชัด**: ก่อน→ลงมือ→หลัง · ปัญหา→แก้แล้ว · ทีละขั้น · ไทม์แลปส์
   ซ่อนเมื่อ อัตโนมัติ / ทัวร์จุดเด่น (ไม่มีก่อน-หลังให้เทียบ)
   🔑 ซ่อนแล้ว **ต้องไม่ถูกใช้ด้วย** — ผู้ใช้ใส่รูปไว้แล้วเปลี่ยนเรื่องแบบทีหลัง รูปยังค้างใน slot
      ⇒ บท/บอร์ด/คำสั่งทุกจุด gate ด้วยเรื่องแบบเดียวกับ UI (`ARC_OK`) · รายการรูปของบทใช้ `cond` (คืนค่าดิบ · engine ≥1.13)

② "ผู้แสดงเป็นอะไร" เปิดมาไม่มีอะไรถูกเลือก (พี่หมี) — รากเดียวกับ people ใน v83
   ค่าตั้งต้น `auto` ใช้กับงานที่สร้าง **หลัง** v85 เท่านั้น · งานเก่าค่าเป็น '' ⇒ ไม่มีปุ่มไหนตรง
   แก้: ตัวเลือกแรกเป็น value `''` ป้าย **"อัตโนมัติ"** (ทรงเดียวกับ เล่าเรื่องแบบไหน / มุมกล้อง / เห็นคนแค่ไหน)
   + คำอธิบายทุกตัวเลือกเขียนใหม่ให้สั้น ภาษาคน

③ "ทีมช่าง (เบลอ)" → **"ทีมงาน"** (พี่หมี) — ทีมตามประเภทงาน: ครัว = เชฟ/ผู้ช่วย · ทำความสะอาด = แม่บ้าน · สวน = คนสวน
   🪤 value `ทีมช่างเบลอเคลื่อนไหวเร็ว` **ไม่แตะ** (เป็น key ของ charPlan/charBoard/charVideoEN + when หลายจุด)
   🪤 ไทม์แลปส์ไม่มีกฎ "คนเบลอ" แยก — พึ่งตัวเลือกนี้อย่างเดียว ⇒ ถ้อยคำใหม่ต้องคง "ไทม์แลปส์ = เงาเคลื่อนไหวเร็ว" ไว้ในตัว

④ 🐛 บั๊กของ v84 เอง (เจอระหว่างไล่): งาน **ไม่มีสินค้า** เห็น "เล่าเรื่องแบบไหน" **2 ชุดซ้อนกัน**
   v84 ถอด when ของกล่องแรกออกทั้งกล่องเพื่อให้ มุมกล้อง/คน โผล่ — ช่องเลือกเรื่องแบบ "มีสินค้า" (มีทัวร์) เลยโผล่ติดมาด้วย
   แก้: gate เฉพาะป้าย+ช่องเลือกเรื่องแบบในกล่องแรกด้วย `hasProduct != ไม่มี` · และสลับให้กล่องเรื่องแบบ "ไม่มีสินค้า" มาก่อน
   (ไม่งั้นงานไม่มีสินค้าจะเห็น มุมกล้อง → คน → แล้วค่อยเลือกเรื่อง ซึ่งกลับหัว — ไทม์แลปส์ล็อกกล้อง ต้องเลือกเรื่องก่อน)

ใช้: python3 scripts/showhow-v91-story-refs-ux.py
"""
import copy, json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
TL = 'ไทม์แลปส์กล้องนิ่ง'
CREW = 'ทีมช่างเบลอเคลื่อนไหวเร็ว'
ARC_OK = {'op': 'not', 'a': {'op': 'or', 'list': [
    {'op': 'eq', 'a': '{item.arc}', 'b': ''},
    {'op': 'eq', 'a': '{item.arc}', 'b': 'ทัวร์จุดเด่น'},
]}}


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


def rf(slot):
    return {'op': 'refsFilled', 'key': 'prod', 'from': 'products', 'slot': slot}


def J(x):
    return json.dumps(x, ensure_ascii=False)


job = c['phases'][0]['form'][2]['card'][0]['card'][0]
scene, story = job['card'][4], job['card'][5]
assert 'into": "room1' in J(scene) and '"field": "before"' in J(story), 'โครงหน้างานเปลี่ยน — หาใหม่ก่อน'

# ── ④ ช่องเลือกเรื่องแบบซ้อน 2 ชุด ────────────────────────────────────────────
box_prod, box_noprod = story['card'][1], story['card'][2]
assert box_noprod.get('when') == 'item.hasProduct=ไม่มี' and '"field": "arc"' in J(box_noprod)
assert box_prod['card'][1].get('field') == 'arc' and box_prod['card'][0].get('value') == 'เล่าเรื่องแบบไหน'
for k in (0, 1):
    assert box_prod['card'][k].get('when') is None
    box_prod['card'][k]['when'] = 'item.hasProduct!=ไม่มี'
story['card'][1], story['card'][2] = box_noprod, box_prod
print('④ งานไม่มีสินค้า: เหลือช่อง "เล่าเรื่องแบบไหน" ชุดเดียว · เลือกเรื่องแบบก่อน แล้วค่อยมุมกล้อง/คน')

# ── ① ย้ายภาพเปิด/จบ ──────────────────────────────────────────────────────────
gi = next(i for i, x in enumerate(scene['card']) if isinstance(x, dict) and x.get('el') == 'group'
          and 'อยากให้เปิด' in J(x.get('head')))
old_group = scene['card'].pop(gi)
up_tpl = next(n for n in walk(old_group) if isinstance(n, dict) and n.get('el') == 'upload')
pick_tpl = next(n for n in walk(old_group) if isinstance(n, dict) and n.get('el') == 'pick-button')
clear_tpl = next(n for n in walk(old_group) if isinstance(n, dict) and n.get('fn') == 'clearSlot')
media_tpl = next(n for n in walk(old_group) if isinstance(n, dict) and n.get('el') == 'media-slot')


def ref_row(slot, label, hint):
    empty = {'op': 'eq', 'a': '{item.slots.%s}' % slot, 'b': ''}
    up = copy.deepcopy(up_tpl); up['into'] = slot
    pk = copy.deepcopy(pick_tpl); pk['into'] = slot
    md = copy.deepcopy(media_tpl); md['src'] = '{item.slots.%s}' % slot
    cl = copy.deepcopy(clear_tpl); cl['to'] = slot
    return {'el': 'box', 'when': ARC_OK, 'className': 'flex flex-row items-start gap-3 mt-1', 'card': [
        {'el': 'box', 'className': 'relative w-[112px] shrink-0', 'when': {'op': 'not', 'a': empty}, 'card': [md, cl]},
        {'el': 'box', 'when': empty,
         'className': 'w-[112px] aspect-square shrink-0 rounded-2xl border-2 border-dashed border-[var(--ev-border)] bg-black/40 flex flex-col gap-1.5 p-1.5 justify-center',
         'card': [up, pk]},
        {'el': 'box', 'className': 'flex flex-col gap-1 min-w-0 pt-1', 'card': [
            {'el': 'row', 'className': '!gap-1.5 !flex-nowrap items-center', 'card': [
                {'el': 'icon', 'icon': 'add_photo_alternate', 'textSize': 'text-[18px]',
                 'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center shrink-0'},
                {'el': 'text', 'value': label, 'className': '!text-[15px] @[640px]:!text-[14px] font-black !text-[var(--ev-text)]'}]},
            {'el': 'text', 'value': hint, 'className': '!text-[13.5px] @[640px]:!text-[13px] opacity-55 leading-snug'},
        ]},
    ]}


box_before = next(x for x in story['card'] if '"field": "before"' in J(x))
box_goal = next(x for x in story['card'] if '"field": "goal"' in J(x))
box_before['card'].append(ref_row('openRef', 'หรือใส่รูปตอนเริ่ม', 'ไม่บังคับ · หมีจะเปิดคลิปให้ใกล้ภาพนี้'))
box_goal['card'].append(ref_row('endRef', 'หรือใส่รูปตัวอย่างตอนจบ',
                                'ไม่บังคับ · ใช้รูปจากที่อื่นได้ ห้องยังเป็นห้องของงานนี้'))
print('① ภาพเปิด/จบ: ย้ายจากกล่องพับในส่วน "ฉาก" → ใต้ "ตอนนี้" / "อยากให้จบ" ในส่วน "เรื่อง"')
print('   โชว์เฉพาะ ก่อน→หลัง · ปัญหา→แก้แล้ว · ทีละขั้น · ไทม์แลปส์ (ซ่อนเมื่ออัตโนมัติ/ทัวร์)')

# ── ① (ต่อ) ซ่อนแล้วต้องไม่ถูกใช้ — gate บท/บอร์ดด้วยเงื่อนไขเดียวกับ UI ────────
ops = {o['id']: o for o in c['ops']}
plan = ops['mnPlan']
assert plan['images'][-2:] == ['{item.slots.openRef}', '{item.slots.endRef}']
plan['images'][-2] = {'op': 'cond', 'when': ARC_OK, 'then': '{item.slots.openRef}'}
plan['images'][-1] = {'op': 'cond', 'when': ARC_OK, 'then': '{item.slots.endRef}'}
n_note = 0
for n in walk(plan['prompt']):
    if isinstance(n, dict) and n.get('when') in ('item.slots.openRef!=', 'item.slots.endRef!='):
        slot = 'openRef' if 'openRef' in n['when'] else 'endRef'
        n['when'] = {'op': 'and', 'list': [{'op': 'not', 'a': {'op': 'eq', 'a': '{item.slots.%s}' % slot, 'b': ''}}, ARC_OK]}
        n_note += 1
assert n_note == 2

for K in range(1, 7):
    op = ops['mnBoard' if K == 1 else f'mnBoard{K}']
    for a in op['refs']['also']:
        if a.get('slot') == 'openRef':
            a['when'] = ARC_OK
        elif a.get('slot') == 'endRef':
            a['when'] = {'op': 'and', 'list': [a['when'], ARC_OK]}
    for n in walk(op['prompt']):
        if not (isinstance(n, dict) and isinstance(n.get('when'), dict)):
            continue
        w = n['when']
        if w == rf('openRef'):                                   # บรรทัด "ช่องฉาก 1 = ตามภาพเปิด"
            n['when'] = {'op': 'and', 'list': [rf('openRef'), ARC_OK]}
        elif w.get('op') == 'and' and rf('endRef') in w.get('list', []):          # ทางใหม่ 2 ทาง (มีภาพจบ)
            w['list'].append(ARC_OK)
        elif w.get('op') == 'and' and {'op': 'not', 'a': rf('endRef')} in w.get('list', []):   # ทางเดิม (ไม่มีภาพจบ)
            i = w['list'].index({'op': 'not', 'a': rf('endRef')})
            w['list'][i] = {'op': 'not', 'a': {'op': 'and', 'list': [rf('endRef'), ARC_OK]}}
print('   บท/บอร์ด/คำสั่งทุกจุด gate ด้วยเรื่องแบบเดียวกับ UI — รูปที่ค้างใน slot ไม่รั่วเข้าเรื่องแบบที่ซ่อน')

# ── ② ผู้แสดงเป็นอะไร: ค่าว่าง = อัตโนมัติ ────────────────────────────────────
cast = next(n for n in walk(job) if isinstance(n, dict) and n.get('field') == 'castKind' and n.get('options'))
NEW_CAST = {
    'auto': ('', 'อัตโนมัติ', 'หมีเลือกให้ตามงาน'),
    'human': ('human', 'คน', 'คนจริงลงมือทำ'),
    'animalReal': ('animalReal', 'สัตว์จริง', 'เดิน 4 ขา แบบสัตว์จริง'),
    'animalAnthro': ('animalAnthro', 'สัตว์ทำตัวเหมือนคน', 'ยืน 2 ขา ใส่เสื้อผ้า'),
    'animalToon': ('animalToon', 'สัตว์การ์ตูน', 'แบบการ์ตูนแอนิเมชัน'),
}
for o in cast['options']:
    v, l, d = NEW_CAST[o['value']]
    o['value'], o['label'], o['desc'] = v, l, d
c['collections']['products']['addDefaults']['castKind'] = ''
for t in ('castPlan', 'castBoard', 'castVideoEN', 'castOverrideTH', 'castNegEN'):
    c['lookups'][t][''] = c['lookups'][t]['auto']          # = '' · คง 'auto' ไว้ให้งานที่สร้างช่วง v85-v90
print('② ผู้แสดงเป็นอะไร: ตัวแรก = "อัตโนมัติ" (value ว่าง) · งานเก่า/งานใหม่ถูกเลือกไว้เสมอ · คำอธิบายใหม่ 5 ตัว')

# ── ③ ทีมช่าง → ทีมงาน ────────────────────────────────────────────────────────
people = next(n for n in walk(job) if isinstance(n, dict) and n.get('field') == 'people' and n.get('options'))
crew = next(o for o in people['options'] if o['value'] == CREW)
crew['label'], crew['desc'] = 'ทีมงาน', 'หลายคน ตามงาน เช่น เชฟ แม่บ้าน คนสวน'
CREW_TXT = {
    'charPlan': ('กฎคนในคลิป: มีทีมงานหลายคน บทบาทตามประเภทงาน — ครัว = เชฟและผู้ช่วยเชฟ · ทำความสะอาด = แม่บ้าน/ทีมทำความสะอาด · '
                 'สวน = คนสวน · ก่อสร้าง/ซ่อม = ช่าง · ชุดทำงานเข้ากับงานเดียวกันทั้งทีม ไม่มองกล้อง ไม่โพสท่า งานเด่นกว่าคน · '
                 'โหมดไทม์แลปส์กล้องนิ่ง: เห็นเป็นเงาเคลื่อนไหวเร็ว ไม่เห็นหน้าชัด · เขียน s*en ให้ระบุบทบาททีมงานทุกฉากที่มีคน'),
    'charBoard': 'ทีมงานหลายคนตามงาน (เชฟ แม่บ้าน คนสวน ช่าง) ชุดเข้ากับงาน ไม่มองกล้อง · ไทม์แลปส์ = เงาเบลอเคลื่อนไหว',
    'charVideoEN': ('a small team whose roles fit the job (chefs, housekeepers, gardeners, builders) in matching work clothes, '
                    'never posing; in a time-lapse they blur as fast-moving figures.'),
}
for t, txt in CREW_TXT.items():
    ks = [k for k in c['lookups'][t] if k.startswith(CREW + '|')]
    assert len(ks) == 2, f'{t}: ควรมี 2 คีย์ของทีม'
    for k in ks:
        c['lookups'][t][k] = txt
# ป้าย/คำอธิบายบนจอที่พูดถึง "ทีมช่าง" (ไม่แตะ value/when/key)
n_ui = 0
for n in walk(c['phases']):
    if isinstance(n, dict) and n.get('el') == 'text' and isinstance(n.get('value'), str) and 'ทีมช่าง' in n['value']:
        n['value'] = n['value'].replace('ทีมช่าง', 'ทีมงาน'); n_ui += 1
print(f'③ "ทีมช่าง (เบลอ)" → "ทีมงาน" · กฎบท/บอร์ด/วิดีโอเขียนใหม่ตามประเภทงาน (คงเงาเบลอเฉพาะไทม์แลปส์) · ป้ายบนจอ {n_ui} จุด')

# ── ยาม ───────────────────────────────────────────────────────────────────────
assert 'อยากให้เปิด' not in J(c['phases']), 'กล่องเดิมยังค้าง'
assert J(c).count('"into": "openRef"') == 2 and J(c).count('"into": "endRef"') == 2, 'ช่องละ 2 ปุ่ม (อัพโหลด + เลือกภาพ) · มีที่เดียว'
arcs_shown_prod = [x for x in story['card'] if '"field": "arc"' in J(x)]
assert len(arcs_shown_prod) == 2 and story['card'][1].get('when') == 'item.hasProduct=ไม่มี'
for x in box_prod['card'][:2]:
    assert x['when'] == 'item.hasProduct!=ไม่มี'
assert [o['value'] for o in cast['options']][0] == '' and c['collections']['products']['addDefaults']['castKind'] == ''
assert all(o['value'].isascii() for o in cast['options'])
assert crew['value'] == CREW, 'value ของทีมห้ามแตะ'
assert 'ทีมช่าง' not in J([n.get('value') for n in walk(c['phases']) if isinstance(n, dict) and n.get('el') == 'text'])
for t in ('charBoard', 'charVideoEN'):
    old_max = max(len(v) for k, v in c['lookups'][t].items() if not k.startswith(CREW))
    assert len(CREW_TXT[t]) <= max(old_max, 176), f'{t} ทีมงานยาวเกินกฎคนตัวอื่น'
for K in range(1, 7):
    b = J(ops['mnBoard' if K == 1 else f'mnBoard{K}'])
    assert b.count('"op": "tuple"') == 0
    assert J(ARC_OK) in b, f'บอร์ดช่วง {K} ยังไม่ gate ด้วยเรื่องแบบ'
for w in ('sm:', 'md:', 'min-['):
    assert w not in J(story), f'UI ใหม่ห้ามใช้ {w}'
print('✅ ยามผ่าน: กล่องเดิมหาย · slot ละที่เดียว · เรื่องแบบไม่ซ้อน · castKind ว่าง=อัตโนมัติ · value ทีมไม่แตะ · gate ครบ 6 บอร์ด')

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nเขียน {P} แล้ว')
