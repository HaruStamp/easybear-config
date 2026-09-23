#!/usr/bin/env python3
"""showhow-v99 — ไอคอนกำหนดเอง = ดินสอ ทุกหัวข้อ · เพิ่มตัวเลือกมุมกล้อง + ผู้แสดงเห็นแค่ไหน อย่างละ 1 (พี่หมีสั่ง 2026-09-24)

① ฉาก / ฉากตอนจบ · กำหนดเอง: ไอคอน add_photo_alternate → edit_note (เหมือนลูกเล่นตอนท้าย)
② มุมกล้อง +1 = **มองจากด้านบน** (ท็อปดาวน์) — เดิม 3 ตัว → 4 (กริด 2×2 พอดี)
   เหมาะกับงานบนโต๊ะ: ทำอาหาร งานฝีมือ จัดของ · ฉากปิดถอยกว้างเห็นผลงานได้
③ ผู้แสดงเห็นแค่ไหน +1 = **เห็นตัว ไม่เห็นหน้า** (ครอปใต้คาง) — เดิม 5 → 6 (กริด 2×3 พอดี)
   ต่างจาก "เห็นแค่มือ" (เห็นแค่มือ/แขน) และ "เห็นเต็มตัว" (เห็นหน้า) — แนวคลิปที่ไม่โชว์หน้า

กติกา:
- value ใช้เป็น **คีย์ lookup + เงื่อนไขเท่านั้น** (ตรวจแล้ว ไม่ถูกเสียบลง prompt ตรง ๆ) ⇒ ไทยได้
- ข้อความกฎใหม่ **ไม่ยาวกว่าของเดิมที่ยาวสุด** ในแต่ละตาราง (เพดาน prompt · บอร์ดเหลือ 13)
- คำในกฎกล้องห้ามมีชื่ออุปกรณ์ถ่ายทำ (บทเรียน tripod) — "top-down view" ไม่ใช่ "overhead rig"
- ⚠️ ตัววัดความยาว (`prompt-clamp-matrix.ts`) มีรายการโหมดคนแบบพิมพ์มือ ⇒ ต้องเติมโหมดใหม่ที่นั่นด้วย ไม่งั้นไม่ถูกวัด
ใช้: python3 scripts/showhow-v99-more-options.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
L = c['lookups']
SRC_AI = 'AI เลือกนาย/นางแบบให้เหมาะกับสินค้า'
SRC_FACE = 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'
CAM = 'มองจากด้านบน'
PEO = 'เห็นตัว ไม่เห็นหน้า'


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


def grid(field):
    return next(n for n in walk(c['phases']) if isinstance(n, dict) and n.get('field') == field and n.get('options'))


# ① ไอคอน
for f in ('sceneMode', 'endMode'):
    o = next(o for o in grid(f)['options'] if o['value'] == 'custom'); o['icon'] = 'edit_note'
assert next(o for o in grid('ideaMode')['options'] if o['value'] == 'custom')['icon'] == 'edit_note'
print('① กำหนดเองของ ฉาก / ฉากตอนจบ → ไอคอนดินสอ (edit_note) เหมือนลูกเล่นตอนท้าย')

# ② มุมกล้อง
cam = grid('camMode')
assert [o['value'] for o in cam['options']] == ['', 'ตั้งนิ่งเห็นทั้งพื้นที่', 'ตามคน ตามมือ แบบ vlog']
cam['options'].append({'value': CAM, 'label': 'มองจากด้านบน', 'desc': 'เห็นมือทำบนโต๊ะ แบบคลิปสูตร', 'icon': 'arrow_downward'})
L['camPlan'][CAM] = ('มุมกล้องหลัก: มองจากด้านบนลงมาตรง ๆ (ท็อปดาวน์) เห็นพื้นโต๊ะ/พื้นที่ทำงานกับมือที่กำลังทำ — '
                     'camN ทุกฉากเป็นมุมบนลงล่าง ยกเว้นฉากปิดถอยกว้างเห็นผลงานได้ · เหมาะกับงานบนโต๊ะ ทำอาหาร งานฝีมือ จัดของ')
L['camVideoEN'][CAM] = ('CAMERA MODE: top-down view looking straight down at the work surface; '
                        'hands and the work fill the frame; framing stays steady. ')
for t in ('camPlan', 'camVideoEN'):
    others = max(len(v) for k, v in L[t].items() if k != CAM)
    assert len(L[t][CAM]) <= others, f'{t} ยาวเกินของเดิม {len(L[t][CAM])} > {others}'
assert not any(w in L['camVideoEN'][CAM].lower() for w in ('tripod', 'rig', 'crane', 'gimbal', 'dolly', 'overhead rig'))
print(f'② มุมกล้อง +1 "{CAM}" (4 ตัว) · กฎบท {len(L["camPlan"][CAM])} · กฎวิดีโอ {len(L["camVideoEN"][CAM])} ตัวอักษร')

# ③ ผู้แสดงเห็นแค่ไหน
peo = grid('people')
assert len(peo['options']) == 5
peo['options'].insert(2, {'value': PEO, 'label': 'เห็นตัว ไม่เห็นหน้า', 'desc': 'ครอปใต้คาง ไม่โชว์หน้า', 'icon': 'accessibility_new'})
TXT = {
    'charPlan': ('กฎคนในคลิป: เห็นตัวผู้ลงมือตั้งแต่คอลงมา (ครอปใต้คาง) ห้ามเห็นหน้าเด็ดขาด — ลำตัว แขน มือกำลังทำงานจริง '
                 'ชุดเดิมทุกฉาก · ห้ามมองกล้อง ห้ามโพสท่า · เขียน s*th/s*en ให้ชัดว่าเห็นแค่ช่วงตัว'),
    'charBoard': 'เห็นตัวคนทำงานตั้งแต่คอลงมา ครอปใต้คาง ห้ามเห็นหน้า ชุดเดิมทุกช่อง',
    'charVideoEN': ('the worker is framed from the neck down — body, arms and hands at work, never the face; '
                    'same outfit in every scene, never posing.'),
}
for t, txt in TXT.items():
    others = max(len(v) for v in L[t].values())
    assert len(txt) <= others, f'{t} ยาวเกินของเดิม {len(txt)} > {others}'
    for src in ('', SRC_AI, SRC_FACE):
        k = PEO + '|' + src
        assert k not in L[t]; L[t][k] = txt
print(f'③ ผู้แสดงเห็นแค่ไหน +1 "{PEO}" (6 ตัว) · กฎ 3 ตาราง × 3 แหล่งหน้า')

# ── ยาม ───────────────────────────────────────────────────────────────────────
assert len(cam['options']) == 4 and len(peo['options']) == 6
for t in ('charPlan', 'charBoard', 'charVideoEN'):
    for o in peo['options']:
        for src in ('', SRC_AI, SRC_FACE):
            if o['value'] == '' and src == '': continue
            assert (o['value'] + '|' + src) in L[t] or o['value'] == '', f'{t} ขาด {o["value"]}|{src[:10]}'
print('✅ ยามผ่าน: มุมกล้อง 4 · ผู้แสดง 6 · lookup ครบทุกคีย์ · ข้อความไม่ยาวกว่าของเดิม · ไม่มีชื่ออุปกรณ์ถ่ายทำ')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
