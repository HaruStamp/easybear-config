#!/usr/bin/env python3
"""showhow-v84 — ① ช่องของงานต้องเห็นทุกกรณี (พี่หมีจับได้) ② คำว่า "รายการสินค้า" → "รายการงาน"

① 🔴 บั๊กที่พี่หมีจับได้
   กล่องที่ครอบ "เล่าเรื่องแบบไหน" มี `when = item.hasProduct != ไม่มี`
   ⇒ เลือก **"ไม่มีสินค้า"** แล้ว **หายหมด 4 ช่อง**: เล่าเรื่องแบบไหน · มุมกล้อง · เห็นคนแค่ไหน · ตัวละคร
   🪤 และ `arc` ถูกซ่อนแบบนี้ **มาตั้งแต่ก่อน v82** ⇒ งานไม่มีสินค้าเลือกโครงเรื่องไม่ได้เลยมาตลอด
      (ผมไม่เจอเพราะทดสอบผ่านคำสั่ง ไม่ได้ผ่านหน้าจอ — คำสั่งไม่สนใจ `when` ของ UI)
   ⇒ งานที่ไม่มีสินค้า = สอนทำอาหาร · ไทม์แลปส์สร้างบ้าน · จัดบ้าน — **เป็นกลุ่มที่ต้องตั้งค่าพวกนี้มากที่สุด**
   แก้: ถอด `when` นั้นออกจากกล่อง ⇒ เห็นทุกกรณี

② การ์ดตอนเซฟ/โหลดโปรเจกต์เขียนว่า "รายการสินค้า" — ของจริงคือ "งาน"
   หน้าอื่นเรียก "งาน" หมดแล้ว (จัดการงาน · เพิ่มงาน · งานของฉัน) ⇒ ให้ตรงกัน

ใช้: python3 scripts/showhow-v84-job-fields-always.py
"""
import json

P = 'showhow-dev.json'
GATE = 'item.hasProduct!=ไม่มี'
c = json.load(open(P, encoding='utf-8'))


def walk(n, parent=None, key=None):
    yield n, parent, key
    if isinstance(n, dict):
        for k, v in n.items(): yield from walk(v, n, k)
    elif isinstance(n, list):
        for i, v in enumerate(n): yield from walk(v, n, i)


# ── ① ถอด gate ออกจากกล่องที่ครอบ arc ─────────────────────────────────────────
box = None
for n, p, k in walk(c):
    if not (isinstance(n, dict) and n.get('when') == GATE):
        continue
    t = json.dumps(n, ensure_ascii=False)
    if '"field": "arc"' in t:
        box = n
        break
assert box is not None, f'หากล่องที่ครอบ arc ด้วย when={GATE!r} ไม่เจอ'
for f in ('arc', 'camMode', 'people', 'peopleSrc'):
    assert '"field": "%s"' % f in json.dumps(box, ensure_ascii=False), f'กล่องนี้ควรมี {f} อยู่ข้างใน'
del box['when']
print('① ถอด when "hasProduct != ไม่มี" ออกจากกล่อง "เล่าเรื่องแบบไหน"')
print('   ⇒ เล่าเรื่องแบบไหน · มุมกล้อง · เห็นคนแค่ไหน · ตัวละคร เห็นทุกกรณีแล้ว')

# ยาม: ต้องไม่มีช่องของ 4 ตัวนี้เหลืออยู่ใต้ gate เดิมอีก
for n, p, k in walk(c):
    if isinstance(n, dict) and n.get('when') == GATE:
        t = json.dumps(n, ensure_ascii=False)
        for f in ('arc', 'camMode', 'people', 'peopleSrc'):
            assert '"field": "%s"' % f not in t, f'{f} ยังอยู่ใต้ gate hasProduct'

# ── ② คำในการ์ดเซฟ/โหลด ──────────────────────────────────────────────────────
sg = c['saveGroups']
hit = 0
for g in sg:
    if g.get('label') == 'รายการสินค้า':
        g['label'] = 'รายการงาน'
        g.setdefault('desc', 'งานที่เพิ่มไว้ พร้อมรูปและรายละเอียด')
        hit += 1
assert hit == 1, f'ควรเจอ label "รายการสินค้า" 1 ที่ · เจอ {hit}'
print('② การ์ดเซฟ/โหลด: "รายการสินค้า" → "รายการงาน" (ให้ตรงกับหน้าจัดการงาน)')

s = json.dumps(c, ensure_ascii=False)
assert 'รายการสินค้า' not in s, 'ยังเหลือคำว่า "รายการสินค้า"'
assert 'รายการงาน' in s
print('✅ ยามผ่าน')

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nเขียน {P} แล้ว')
