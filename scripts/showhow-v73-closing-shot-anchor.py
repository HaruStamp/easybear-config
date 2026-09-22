#!/usr/bin/env python3
# showhow v73 — คลิปยาว: ช่วงท้ายกลับไปห้องเดิม + หัวเรื่องมีโอกาสซ้ำน้อยลง (2026-09-22 ดึก)
#
# หลักฐาน: docs/qa/2026-09-22-regress40/full40.jpg (คลิป 40 วิ · ล้างครัว)
#   ① ฉากปิดของช่วง 4 เป็น **ครัวไม้คนละห้อง** ทั้งที่ทั้งคลิปเป็นครัวขาว
#      กฎในบทบอก "ฉากสุดท้ายมุมเดียวกับฉากแรก" แต่ v59 ถอดบอร์ดช่วง 1 ออกจาก mnVideo3-6
#      ⇒ ช่วงท้าย **ไม่เห็นฉากเปิดเลยสักใบ** จะลอกมุมเปิดได้ยังไง
#      แก้: แผ่นที่ 2 ของ mnVideo3-6 เปลี่ยนจาก "บอร์ดช่วงก่อน" → **"บอร์ดช่วง 1" (หมุดมุมเปิด)**
#      เสียอะไรไหม: ไม่ — บอร์ดช่วง K เองก็ ref บอร์ดช่วง K-1 อยู่แล้ว (v11) ความต่อเนื่องช่วงติดกันจึงอยู่ในบอร์ดแล้ว
#      ยังคง **≤2 แผ่นต่อ op** ตามยาม G12 (3 แผ่น = สตอรีบอร์ดหลุดเข้าคลิป)
#   ② หัวเรื่องถูกพิมพ์ 2 บรรทัด — **บรรทัดบนขาวล้วน บรรทัดล่างมีคำเน้นสีเหลือง**
#      = โมเดลอ่านค่าสไตล์ตั้งต้น 'very bold Thai text, white, ... one key word in bright yellow'
#        เป็น "สองการเรนเดอร์" แล้ววาดทั้งคู่ ไม่ใช่การตัดบรรทัดยาวเกิน
#      ⇒ ค่าตั้งต้นเปลี่ยนเป็นสไตล์ที่บรรยาย **การเรนเดอร์เดียว** (ตัวเลือกสีเหลืองยังเลือกได้อยู่)
#      🪤 ไม่ใช่การ "ฟิกซ์" — เป็นการลดความเสี่ยงของค่าตั้งต้น · อาการนี้แก้ด้วยถ้อยคำมาแล้ว 2 รอบ (v25, v55) ไม่หาย
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))

# ① หมุดมุมเปิดกลับเข้า mnVideo3-6
swapped = []
for op in c['ops']:
    if op['id'] not in ('mnVideo3', 'mnVideo4', 'mnVideo5', 'mnVideo6'):
        continue
    k = int(op['id'].replace('mnVideo', ''))
    also = op['refs']['also']
    first = also[0]
    assert first['from'] == 'tasks' and first['slot'] == 'board%d' % (k - 1), (op['id'], first)
    also[0] = {'from': 'tasks', 'by': '{item.id}', 'slot': 'board'}
    swapped.append((op['id'], 'board%d' % (k - 1), 'board'))
assert len(swapped) == 4, swapped

# เช็คว่ายังไม่เกิน 2 แผ่นบอร์ดต่อ op (เกณฑ์ G12)
for op in c['ops']:
    if op['id'].startswith('mnVideo'):
        r = op['refs']
        sheets = [r['slot']] + [a['slot'] for a in r['also'] if a['from'] == 'tasks']
        assert len(sheets) <= 2, (op['id'], sheets)
        assert len(set(sheets)) == len(sheets), (op['id'], sheets)

# ② ค่าตั้งต้นของสไตล์ข้อความ
SAFE = 'bold Thai sans-serif, white fill, thick dark outline, soft shadow'
old = c['values']['svText']
assert old != SAFE, 'รันซ้ำ'
vals = []
def opts(node):
    if isinstance(node, dict):
        if node.get('field') == 'svText' and 'options' in node:
            vals.extend(o.get('value') for o in node['options'])
        for v in node.values(): opts(v)
    elif isinstance(node, list):
        for v in node: opts(v)
opts(c)
assert SAFE in vals, 'ค่าใหม่ต้องเป็นตัวเลือกที่มีจริง'
c['values']['svText'] = SAFE

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v73 ok · หมุดมุมเปิด:', swapped)
print('        svText ตั้งต้น:', repr(old), '→', repr(SAFE))
