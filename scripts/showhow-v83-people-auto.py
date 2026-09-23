#!/usr/bin/env python3
"""showhow-v83-people-auto.py — "เห็นคนแค่ไหน" ต้องมีตัวเลือกที่ถูกเลือกเสมอ (พี่หมีเห็นของจริงแล้วทัก)

อาการ: เปิดหน้าตั้งค่างานแล้ว "เห็นคนแค่ไหน" **ไม่มีตัวเลือกไหนถูกเลือกไว้เลย**

สาเหตุ (2 ชั้น · ชั้นที่ 2 หนักกว่าที่ตาเห็น)
  ① `addDefaults.people` ใช้กับ **งานที่สร้างใหม่หลัง v82** เท่านั้น
     ⇒ งานเก่าที่สร้างก่อนหน้านั้น field `people` เป็นค่าว่าง
  ② `people` เป็น grid-select ที่ **ไม่มี option ค่าว่าง** (ต่างจาก `arc` และ `camMode` ที่มี "อัตโนมัติ")
     ⇒ ค่าว่าง = ไม่มีปุ่มไหนตรง = ไม่มีอะไรถูกไฮไลต์
  🔴 และที่หนักกว่าคือ **`charPlan` ไม่มีคีย์สำหรับค่าว่าง** ⇒ lookup ตก fallback `''`
     ⇒ งานเก่าจะผลิตคลิป **โดยไม่มีกฎคนในคลิปเลยสักบรรทัด** — โมเดลเดาเอาเอง ไม่ใช่แค่ปุ่มไม่ไฮไลต์

แก้
  ① เพิ่ม option `''` = "อัตโนมัติ" ให้ `people` (ทรงเดียวกับ `arc`/`camMode`)
  ② เพิ่มคีย์ค่าว่างใน charPlan / charBoard / charVideoEN — ให้ "อัตโนมัติ" มีกฎจริง ไม่ใช่ช่องว่าง
  ③ งานใหม่ยังได้ "เห็นแต่มือ" เป็นค่าตั้งต้นเหมือนเดิม (ค่าที่ใช้บ่อยที่สุด ใช้ได้ทันทีโดยไม่ต้องเลือก)

ใช้: python3 scripts/showhow-v83-people-auto.py
"""
import json

P = 'showhow-dev.json'
SRC_AI = 'AI เลือกนาย/นางแบบให้เหมาะกับสินค้า'
SRC_FACE = 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'

c = json.load(open(P, encoding='utf-8'))


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


# ── ① option "อัตโนมัติ" ──────────────────────────────────────────────────────
hit = 0
for n in walk(c):
    if isinstance(n, dict) and n.get('field') == 'people' and n.get('options'):
        vals = [o.get('value') for o in n['options']]
        if '' in vals:
            continue
        n['options'].insert(0, {'value': '', 'label': 'อัตโนมัติ',
                                'desc': 'หมีเลือกให้เข้ากับงาน', 'icon': 'auto_awesome'})
        hit += 1
assert hit == 1, f'ควรเจอ grid-select ของ people 1 ตัว · เจอ {hit}'
print('① เพิ่ม option "อัตโนมัติ" ให้ "เห็นคนแค่ไหน" (ทรงเดียวกับ เล่าเรื่องแบบไหน / มุมกล้อง)')

# ── ② คีย์ค่าว่างใน lookup ทั้ง 3 ตัว ──────────────────────────────────────────
AUTO = {
    'charPlan': ('กฎคนในคลิป: เลือกเองว่าจะให้เห็นคนแค่ไหนให้เข้ากับงานนี้ '
                 '(เห็นแต่มือ / คนเดียวเต็มตัว / ทีมช่างเบลอ / ไม่มีคน) '
                 '— งานที่ต้องสอนทำตามให้เห็นมือลงมือชัด · งานไทม์แลปส์ให้คนอยู่ไกลหรือเบลอ · '
                 'งานโชว์ของอย่างเดียวไม่ต้องมีคนก็ได้ · เลือกแล้วต้องเป็นแบบเดียวกันทุกฉากทุกคลิป '
                 'และสะท้อนใน s*th/s*en ทุกฉากที่มีคน · ห้ามเป็นพรีเซนเตอร์ ห้ามมองกล้อง'),
    'charBoard': 'คนในภาพ: ให้เข้ากับงาน และต้องเป็นแบบเดียวกันทุกช่อง · ห้ามมองกล้อง ห้ามโพสท่า',
    'charVideoEN': ('people: match the job — keep it identical across every shot; '
                    'never look at camera, never pose'),
}
for tbl, txt in AUTO.items():
    lk = c['lookups'][tbl]
    for src in (SRC_AI, SRC_FACE):
        k = '|' + src
        assert k not in lk, f'{tbl} มีคีย์ {k} อยู่แล้ว'
        lk[k] = txt
    print(f'② {tbl}: เพิ่มคีย์ค่าว่าง 2 คีย์ (คู่กับ "สุ่ม" และ "ใช้รูป")')

# ── ③ ค่าตั้งต้นของงานใหม่ยังเป็น "เห็นแต่มือ" ─────────────────────────────────
ad = c['collections']['products']['addDefaults']
assert ad.get('people') == 'เห็นแต่มือ ไม่เห็นหน้า', 'addDefaults.people ต้องเป็น "เห็นแต่มือ ไม่เห็นหน้า"'
print('③ งานใหม่ยังได้ "เห็นแต่มือ" เป็นค่าตั้งต้น (ไม่เปลี่ยน)')

# ── ยาม ───────────────────────────────────────────────────────────────────────
for n in walk(c):
    if isinstance(n, dict) and n.get('field') in ('arc', 'camMode', 'people') and n.get('options'):
        vals = [o.get('value') for o in n['options']]
        assert '' in vals, f'{n["field"]} ต้องมี option ค่าว่างเพื่อให้ค่าว่างยังมีปุ่มที่ถูกเลือก'
for tbl in AUTO:
    lk = c['lookups'][tbl]
    for src in (SRC_AI, SRC_FACE):
        assert lk.get('|' + src), f'{tbl} ขาดคีย์ค่าว่างสำหรับ {src[:20]}'
    assert len(lk) == 10, f'{tbl} ควรมี 10 คีย์ (4 โหมด + อัตโนมัติ) × 2 แหล่ง · มี {len(lk)}'
print('✅ ยามผ่าน: ทั้ง 3 ช่องมี option ค่าว่าง · lookup ครบ 10 คีย์ทุกตัว')

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nเขียน {P} แล้ว')
