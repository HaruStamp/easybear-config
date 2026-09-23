#!/usr/bin/env python3
"""showhow-v93 — สไตล์ตัวอักษรตัวที่ 6 (พี่หมีสั่ง 2026-09-24 · ให้ครบ 6 = เต็ม 2 แถวของกริด 3 คอลัมน์)

ของเดิม 5 แบบไม่มีแบบ "พื้นเข้มรองหลัง" เลย (การ์ดขาว · เน้นคำเหลือง · ไฮไลต์ปากกา · ขอบหนา · บางมินิมอล)
⇒ เพิ่ม **"แถบดำโปร่ง"** — ตัวขาวบนแถบดำโปร่งแสง แบบซับของคลิปสั้น อ่านง่ายแม้พื้นหลังรก (ครัว · ห้องเก็บของ · สวน)

กติกาที่ต้องผ่าน:
- value **อังกฤษล้วน** (ยาม G6 · v21: ค่าไทยถูกพิมพ์ลงจอ)
- value **ไม่ยาวกว่าสไตล์ที่ยาวสุดเดิม (77)** — ถูกเสียบลง prompt ตรง ๆ · บอร์ดเหลือที่ว่าง 13 ตัวอักษรเมื่อวัดด้วยสไตล์ยาวสุด
- ไม่มีคำเทคนิคที่เคยกลายเป็นของบนจอ (4K · tripod · 2 lines · doodle)
ใช้: python3 scripts/showhow-v93-text-style-6.py
"""
import json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
NEW = {'value': 'bold white Thai text on a semi-transparent black rounded bar, even padding',
       'label': 'แถบดำโปร่ง', 'desc': 'อ่านง่ายทุกพื้นหลัง แบบซับคลิปสั้น'}


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


grids = [n for n in walk(c['phases']) if isinstance(n, dict) and n.get('field') == 'svText' and n.get('options')]
assert len(grids) == 1
opts = grids[0]['options']
assert len(opts) == 5, f'ควรมี 5 สไตล์ก่อนเพิ่ม · มี {len(opts)}'
longest = max(len(o['value']) for o in opts)
assert NEW['value'].isascii(), 'value ต้องอังกฤษล้วน'
assert len(NEW['value']) <= longest, f'ยาว {len(NEW["value"])} > สไตล์ยาวสุดเดิม {longest}'
for bad in ('4k', 'tripod', 'line', 'doodle', 'fps', 'frame', 'box'):
    assert bad not in NEW['value'].lower(), f'มีคำเสี่ยง "{bad}"'
assert NEW['value'] not in [o['value'] for o in opts]
opts.append(NEW)
# ── ② ปุ่ม "กำหนดเอง ⭐แนะนำ" → "กำหนดเอง" (พี่หมีสั่ง · และ emoji บนปุ่มผิดกฎของโปรเจกต์อยู่แล้ว — ใช้ได้แค่ material symbols)
sm = next(n for n in walk(c['phases']) if isinstance(n, dict) and n.get('field') == 'sceneMode' and n.get('options'))
cu = next(o for o in sm['options'] if o['value'] == 'custom')
assert cu['label'] == 'กำหนดเอง ⭐แนะนำ'
cu['label'] = 'กำหนดเอง'
import re
EMOJI = re.compile('[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2B55]')
for n in walk(c['phases']):
    if isinstance(n, dict):
        for k in ('label', 'desc'):
            if isinstance(n.get(k), str): assert not EMOJI.search(n[k]), f'emoji ใน {k}: {n[k]!r}'
    if isinstance(n, dict) and isinstance(n.get('options'), list):
        for o in n['options']:
            for k in ('label', 'desc'):
                assert not EMOJI.search(str(o.get(k, ''))), f'emoji ในตัวเลือก: {o.get(k)!r}'
print('② ปุ่มฉาก: "กำหนดเอง ⭐แนะนำ" → "กำหนดเอง" · ไม่มี emoji ในป้าย/ตัวเลือกไหนอีก')
print(f'เพิ่มสไตล์ที่ 6 "{NEW["label"]}" · value {len(NEW["value"])} ตัวอักษร (ยาวสุดเดิม {longest}) · รวม {len(opts)} แบบ')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
