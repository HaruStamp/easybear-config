#!/usr/bin/env python3
"""showhow-v90 — "อยากให้เปิด–จบฉากประมาณไหน" (ภาพอ้างอิงฉากเปิด / ฉากจบ · ไม่บังคับ)

ทีมเสนอ · พี่หมีชี้ชัด 2026-09-23: **ไม่ใช่เฟรมเริ่ม/จบเป๊ะ** — เป็นภาพอ้างอิง "ประมาณนี้"
(มุมกล้อง · การจัดวาง · สภาพ · บรรยากาศ) · ใส่ 0 / 1 / 2 รูปก็ได้

## ทำไมไม่ใช้ startFrame/endFrame ของ engine
- มี startFrame = refs ทั้งชุดถูกทิ้ง (บอร์ด · รูปสินค้า · รูปห้อง) — `execLeaf.ts` else-if (Flow แยกโหมดเฟรม/ส่วนผสม)
- endFrame ถูกส่งเฉพาะตอนมี startFrame ⇒ "ใส่แค่ภาพจบ" ถูกทิ้งเงียบ
⇒ ใช้เป็น **รูปอ้างอิงธรรมดา** แทน: ไม่ต้องขอ engine · ของเดิมส่งครบ

## ไหลผ่าน 2 ชั้น (ไม่แตะวิดีโอ — ตั้งใจ)
① **บท (mnPlan)** เห็นทั้งสองรูป → เขียนฉาก 1 / ฉากสุดท้ายให้เข้าทาง  ← คันโยกหลัก · ไม่ผ่านเพดาน 3,900
② **บอร์ด** ช่วงแรกแนบภาพเปิด · บอร์ดช่วงสุดท้าย (ตามความยาว) แนบภาพจบ
✗ **วิดีโอ ไม่แนบ** — Omni รับรูปอ้างอิงได้ 7 ใบ และช่วงวิดีโอเต็มอยู่แล้วในงานสินค้าหลายมุม
  (แนบเพิ่ม = รูปสินค้าตกเพดาน) · และเคยเจอ "แผ่นอ้างอิงที่ไม่เข้าคู่กับบทหลุดเข้าคลิป" (v73)
  ⇒ วิดีโอเดินตามบอร์ดอยู่แล้ว ได้ผลผ่านบอร์ดโดยไม่เสี่ยง

## ไม่ให้ตีกับรูปพื้นที่ (room1/room2)
รูปพื้นที่ = **ห้องนี้คือห้องไหน** (ชนะเรื่องสถานที่) · ภาพเปิด/จบ = **มุม · จัดวาง · สภาพ** (ชนะเรื่องมุม)
🪤 เคสที่ต้องกัน: ภาพจบจาก Pinterest (ห้องคนอื่น) → ทุกคำสั่งบอก "ห้องยังเป็นห้องเดิม ห้ามย้ายไปห้องในภาพ"
🪤 ไทม์แลปส์กล้องนิ่ง: ภาพจบให้แค่ "สภาพ" — กรอบภาพยังเดิมทั้งคลิป

## ลำดับรูป — ต่อท้ายสุดเสมอ
บอร์ดช่วง 3-6 ได้รูปครบเพดาน 10 อยู่แล้วเมื่อใส่รูปทุกช่อง ⇒ ต่อท้าย = ของเดิมไม่หลุดสักใบ
(กรณีเต็มจริง ภาพใหม่ยอมหลุดเอง และ capRefs ของ engine เตือนดัง)

## เพดาน prompt
คำสั่งใหม่ทุกชิ้นเปิดเฉพาะเมื่อมีรูปจริง ⇒ **คนไม่ใส่รูปยาวเท่าเดิมทุกตัวอักษร**
ฉากปิด = **แทนที่** บรรทัด "ช่องฉาก N = ฉากปิด…ภาพกว้างมุมเดียวกับฉากเปิด" เดิม (สั้นกว่าของเดิม)

ใช้: python3 scripts/showhow-v90-open-end-ref.py
"""
import copy, json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
TL = 'ไทม์แลปส์กล้องนิ่ง'
SLOTS = ('openRef', 'endRef')


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


def rf(slot):
    return {'op': 'refsFilled', 'key': 'prod', 'from': 'products', 'slot': slot}


def sec_eq(n):
    return {'op': 'eq', 'a': '{values.svSec}', 'b': str(n)}


# ── ① slot ของงาน ─────────────────────────────────────────────────────────────
ps = c['collections']['products']['slots']
for s in SLOTS:
    assert s not in ps, f'{s} มีอยู่แล้ว'
    ps.append(s)
print(f'① products.slots += {SLOTS}')

# ── ② UI — กล่องพับในส่วน "ฉาก" ใต้คำบรรยายพื้นที่ ──────────────────────────────
job = c['phases'][0]['form'][2]['card'][0]['card'][0]
scene = job['card'][4]
assert 'into": "room1' in json.dumps(scene, ensure_ascii=False), 'ส่วน "ฉาก" ย้ายที่แล้ว — หาใหม่ก่อน'
assert '"field": "room"' in json.dumps(scene, ensure_ascii=False)
# ลอกคลาสปุ่มจากช่องรูปพื้นที่ของจริง (ไม่พิมพ์เอง = หน้าตาเหมือนกันเป๊ะ)
room_row = scene['card'][1]
up_tpl = next(n for n in walk(room_row) if isinstance(n, dict) and n.get('el') == 'upload')
pick_tpl = next(n for n in walk(room_row) if isinstance(n, dict) and n.get('el') == 'pick-button')
clear_tpl = next(n for n in walk(room_row) if isinstance(n, dict) and n.get('fn') == 'clearSlot')
media_tpl = next(n for n in walk(room_row) if isinstance(n, dict) and n.get('el') == 'media-slot')
sell_group = next(n for n in walk(job) if isinstance(n, dict) and n.get('el') == 'group'
                  and 'ถ้าขาย' in json.dumps(n.get('head'), ensure_ascii=False))


def tile(slot, label, icon):
    empty = {'op': 'eq', 'a': '{item.slots.%s}' % slot, 'b': ''}
    up = copy.deepcopy(up_tpl); up['into'] = slot
    pk = copy.deepcopy(pick_tpl); pk['into'] = slot
    for b in (up, pk):   # ช่องเล็กกว่ารูปพื้นที่ (2 ช่องต่อแถว) ⇒ ปุ่มเต็มความกว้างของช่อง
        b['className'] = b['className'].replace('flex-1 @[560px]:flex-none @[560px]:w-full', 'w-full')
    md = copy.deepcopy(media_tpl); md['src'] = '{item.slots.%s}' % slot
    cl = copy.deepcopy(clear_tpl); cl['to'] = slot
    return {'el': 'box', 'className': 'flex flex-col gap-1.5 w-[calc((100%-0.75rem)/2)] @[560px]:w-[170px] shrink-0', 'card': [
        {'el': 'row', 'className': '!gap-1.5 !flex-nowrap items-center px-0.5', 'card': [
            {'el': 'icon', 'icon': icon, 'textSize': 'text-[17px]',
             'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center shrink-0'},
            {'el': 'text', 'value': label, 'className': '!text-[15px] @[640px]:!text-[14px] font-black !text-[var(--ev-text)]'}]},
        {'el': 'box', 'className': 'relative w-full', 'when': {'op': 'not', 'a': empty}, 'card': [md, cl]},
        {'el': 'box', 'when': empty,
         'className': 'w-full aspect-square rounded-2xl border-2 border-dashed border-[var(--ev-border)] bg-black/40 flex flex-col gap-2 p-2 justify-center',
         'card': [up, pk]},
    ]}


group = {
    'el': 'group', 'collapsible': True,
    'className': sell_group['className'], 'bodyClass': 'pt-2 gap-3', 'chevClass': sell_group['chevClass'],
    'head': [
        {'el': 'icon', 'icon': 'compare', 'textSize': 'text-[19px]',
         'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center shrink-0'},
        {'el': 'text', 'value': 'อยากให้เปิด–จบฉากประมาณไหน',
         'className': '!text-[16px] @[640px]:!text-[15px] font-black !text-[var(--ev-text)] whitespace-nowrap'},
        {'el': 'text', 'value': 'ภาพตัวอย่าง (ไม่บังคับ)', 'className': '!text-[13px] opacity-40 truncate min-w-0'},
    ],
    'card': [
        {'el': 'text', 'value': 'ให้หมีดูเป็นแนว — มุมกล้อง การจัดวาง สภาพ บรรยากาศ ไม่ต้องเป๊ะ · ใส่รูปเดียวก็ได้\n'
                               'ห้องยังเป็นห้องจากรูปพื้นที่เสมอ ใช้รูปจากที่อื่นเป็นตัวอย่างได้',
         'className': '!text-[14px] @[640px]:!text-[13px] opacity-60 px-0.5 whitespace-pre-line'},
        {'el': 'box', 'className': 'flex flex-row gap-3 items-start', 'card': [
            tile('openRef', 'เปิดฉากประมาณนี้', 'first_page'),
            tile('endRef', 'จบฉากประมาณนี้', 'last_page'),
        ]},
    ],
}
scene['card'].insert(3, group)
print('② UI: กล่องพับ "อยากให้เปิด–จบฉากประมาณไหน" ในส่วนฉาก (ใต้คำบรรยายพื้นที่) · 2 ช่อง ลอกทรงจากช่องรูปพื้นที่')

# ── ③ บท — mnPlan เห็นรูป + คำอธิบาย ─────────────────────────────────────────
ops = {o['id']: o for o in c['ops']}
plan = ops['mnPlan']
plan['images'] += ['{item.slots.openRef}', '{item.slots.endRef}']   # ท้ายสุดเสมอ ⇒ ตำแหน่งชี้ได้แน่นอน
host = next(n for n in walk(plan['prompt']) if isinstance(n, list)
            and any(isinstance(x, dict) and x.get('when') == 'item.slots.room1!=' for x in n))
k = next(i for i, x in enumerate(host) if isinstance(x, dict) and x.get('when') == 'item.slots.room1!=')
PLAN_OPEN = ('มีภาพอ้างอิงฉากเปิดแนบมา (อยู่ท้ายรูปทั้งหมด ก่อนภาพจบถ้ามี) — ฉาก 1 จัดมุมกล้อง การจัดวาง และสภาพให้ใกล้ภาพนี้ '
             'แล้วบรรยายใน s1th/s1en ให้เห็นภาพชัด · สถานที่ยังเป็นพื้นที่ตามรูปพื้นที่ (ถ้ามี) ไม่ใช่ห้องในภาพนี้\n')
PLAN_END = ('มีภาพอ้างอิงฉากจบแนบมา (รูปสุดท้ายที่แนบ) — ฉากสุดท้ายของคลิปจัดการวางและสภาพให้ใกล้ภาพนี้ '
            '(ใช้แทนกฎ "ฉากสุดท้ายมุมเดียวกับฉากแรก") แล้วบรรยายให้เห็นภาพชัด · สถานที่ยังเป็นพื้นที่เดิม ห้ามย้ายไปห้องในภาพ · '
            'โหมดไทม์แลปส์กล้องนิ่ง: เอาแค่สภาพจากภาพจบ มุมกล้องยังเดิมทั้งคลิป\n')
host.insert(k + 1, {'when': 'item.slots.openRef!=', 'value': PLAN_OPEN})
host.insert(k + 2, {'when': 'item.slots.endRef!=', 'value': PLAN_END})
print('③ mnPlan: เห็นภาพเปิด/จบ (ต่อท้ายรายการรูป) + คำอธิบาย 2 บล็อก เปิดเฉพาะเมื่อมีรูป')

# ── ④ บอร์ด — แนบรูป + คำสั่ง ────────────────────────────────────────────────
BOARD_OPEN = '\nช่องฉาก 1 = มุม การจัดวาง และสภาพตามภาพอ้างอิงฉากเปิดที่แนบ แต่ห้องยังเป็นห้องเดิม'
n_end = 0
for K in range(1, 7):
    oid = 'mnBoard' if K == 1 else f'mnBoard{K}'
    op = ops[oid]
    also = op['refs'].setdefault('also', [])
    if K == 1:
        also.append({'from': 'products', 'by': '{item.refs.prod}', 'slot': 'openRef'})
    # ภาพจบ → เฉพาะบอร์ดที่มีฉากสุดท้ายของคลิป (ช่วง K สุดท้ายเมื่อ svSec = 10K)
    also.append({'from': 'products', 'by': '{item.refs.prod}', 'slot': 'endRef', 'when': sec_eq(10 * K)})

    parts = op['prompt']['parts']
    i = next(i for i, x in enumerate(parts) if isinstance(x, dict) and x.get('op') == 'block'
             and any(isinstance(p, dict) and p.get('when') == f'values.svSec={10 * K}' and 'ฉากปิดของคลิป' in str(p.get('value'))
                     for p in x.get('parts', [])))
    blk = parts[i]['parts'][0]
    last = 5 * K
    blk['when'] = {'op': 'and', 'list': [sec_eq(10 * K), {'op': 'not', 'a': rf('endRef')}]}
    tail = ' · ถ้าวางสินค้าไว้ในเฟรมด้วย ต้องเป็นสินค้าตามรูปที่แนบเท่านั้น'
    parts[i]['parts'] += [
        {'when': {'op': 'and', 'list': [sec_eq(10 * K), rf('endRef'), {'op': 'not', 'a': {'op': 'eq', 'a': '{item.arc}', 'b': TL}}]},
         'value': f'\nช่องฉาก {last} = ฉากปิดของคลิป: มุมกล้อง การจัดวาง และสภาพตามภาพอ้างอิงฉากจบ (รูปสุดท้ายที่แนบ) '
                  f'แต่ห้องยังเป็นห้องเดิม ห้ามย้ายไปห้องในภาพนั้น' + tail},
        {'when': {'op': 'and', 'list': [sec_eq(10 * K), rf('endRef'), {'op': 'eq', 'a': '{item.arc}', 'b': TL}]},
         'value': f'\nช่องฉาก {last} = ฉากปิดของคลิป: กรอบภาพเดิมทุกช่อง เปลี่ยนแค่สภาพให้ตรงภาพอ้างอิงฉากจบ (รูปสุดท้ายที่แนบ)' + tail},
    ]
    n_end += 1
    if K == 1:
        parts.insert(i + 1, {'op': 'block', 'sep': '', 'parts': [{'when': rf('openRef'), 'value': BOARD_OPEN}]})
print(f'④ บอร์ด: ช่วงแรกแนบภาพเปิด · ภาพจบแนบเฉพาะบอร์ดช่วงสุดท้ายตามความยาว ({n_end} op) · '
      'บรรทัดฉากปิดสลับ 3 ทาง (ไม่มีภาพจบ / มีภาพจบ / มีภาพจบ+ไทม์แลปส์)')

# ── ยาม ───────────────────────────────────────────────────────────────────────
s = json.dumps(c, ensure_ascii=False)
assert all(sl in c['collections']['products']['slots'] for sl in SLOTS)
assert plan['images'][-2:] == ['{item.slots.openRef}', '{item.slots.endRef}'], 'ภาพเปิด/จบต้องอยู่ท้ายรายการรูปของบท'
for K in range(1, 7):
    oid = 'mnBoard' if K == 1 else f'mnBoard{K}'
    sl = [a['slot'] for a in ops[oid]['refs']['also']]
    assert sl[-1] == 'endRef', f'{oid}: endRef ต้องอยู่ท้ายสุด (ของเดิมห้ามหลุดเพดาน)'
    blob = json.dumps(ops[oid]['prompt'], ensure_ascii=False)
    assert blob.count('ฉากปิดของคลิป') == 3, f'{oid}: บรรทัดฉากปิดควรมี 3 ทาง'
for o in c['ops']:
    if o['id'].startswith('mnVideo'):
        assert 'openRef' not in json.dumps(o, ensure_ascii=False) and 'endRef' not in json.dumps(o, ensure_ascii=False), \
            f"{o['id']}: วิดีโอห้ามแนบภาพเปิด/จบ (ตั้งใจ — Omni รับ 7 ใบ · เสี่ยงแผ่นหลุดเข้าคลิป)"
for w in ('sm:', 'md:', 'min-['):
    assert w not in json.dumps(group, ensure_ascii=False), f'UI ใหม่ห้ามใช้ {w} (ใช้ container query @[Npx]: เท่านั้น)'
print('✅ ยามผ่าน: slot ครบ · รูปต่อท้ายสุดทุกที่ · ฉากปิด 3 ทางครบ 6 บอร์ด · วิดีโอไม่แตะ · UI ใช้ container query ล้วน')

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nเขียน {P} แล้ว')
