#!/usr/bin/env python3
# showhow v61 — เพิ่มโครงเรื่อง "ทีละขั้นให้ทำตาม" + เขียนคำอธิบายของสายไม่มีสินค้าใหม่ (พี่หมีเคาะ 2026-09-22)
#
# ① ที่ขาดจริง: งานสาย "ตัวขั้นตอนคือพระเอก" (ทำอาหาร · พับผ้าแบบสอน · ซ่อม/ประกอบของ)
#    ตอนนี้ถูกเหมาเป็น "ก่อน → ลงมือ → หลัง" ซึ่งให้ฉากแบบ วัตถุดิบ → ผัด → จานเสร็จ
#    แต่คนดูคลิปสอนอยากได้ **ทุกขั้นเป็นฉากของตัวเอง + โคลสอัพของที่เปลี่ยนทุกขั้น**
#    ⇒ ใส่ทั้ง 2 สาย (มีสินค้าก็ใช้ได้ เช่น สอนผัดด้วยกระทะเคลือบ)
# ② แก้ของที่ v60 ทำพลาด: บล็อกสายไม่มีสินค้าก๊อป desc มาทั้งดุ้น เลยยังพูดถึง "ของ/สินค้า"
#    ในหน้าที่ไม่มีสินค้า ("หมีเลือกจากชื่องานและของ" · "ของที่ติดแล้วจบ — กันฝน กันแมลง ชั้นวาง")
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ARC = 'ทีละขั้นให้ทำตาม'
NEW_OPT = {'value': ARC, 'label': 'ทีละขั้นให้ทำตาม', 'desc': 'สูตร/วิธีทำ — ทำอาหาร พับผ้า ซ่อมของ', 'icon': 'format_list_numbered'}

blk = c['phases'][0]['form'][2]['card'][0]['card'][0]['card'][5]
blocks = [b for b in blk['card'] if b.get('el') == 'box' and b.get('when')]
assert len(blocks) == 2, f'คาด 2 บล็อก เจอ {len(blocks)}'
withp = [b for b in blocks if b['when'] == 'item.hasProduct!=ไม่มี'][0]['card'][1]
nop   = [b for b in blocks if b['when'] == 'item.hasProduct=ไม่มี'][0]['card'][1]

# ① เพิ่มตัวเลือกใหม่ทั้ง 2 สาย (วางก่อน "ไทม์แลปส์" เพราะเป็นทรงเล่าเรื่อง ไม่ใช่ทรงถ่าย)
for gs in (withp, nop):
    assert all(o['value'] != ARC for o in gs['options']), 'รันซ้ำ'
    i = next(i for i, o in enumerate(gs['options']) if o['value'] == 'ไทม์แลปส์กล้องนิ่ง')
    gs['options'].insert(i, dict(NEW_OPT))

# ② คำอธิบายของสายไม่มีสินค้า — ห้ามพูดถึง "ของ/สินค้า"
NODESC = {
    '': 'หมีเลือกให้จากชื่องานและสภาพก่อน/หลัง',
    'ก่อน → ลงมือ → หลัง': 'จัดบ้าน จัดสวน ทำของ รีโนเวท',
    'ปัญหา → แก้แล้ว': 'คราบ รก ของเสีย — เปิดด้วยจุดที่เจ็บตา',
}
for o in nop['options']:
    if o['value'] in NODESC:
        o['desc'] = NODESC[o['value']]
bad = [o for o in nop['options'] if any(w in o.get('desc', '') for w in ('สินค้า', 'ของที่ติด', 'และของ', 'โชว์ของ'))]
assert not bad, f'ยังมี desc ที่พูดถึงสินค้าในสายไม่มีสินค้า: {bad}'

# ③ arcPlan
ap = c['lookups']['arcPlan']
assert ARC not in ap
ap[ARC] = ('โครงเรื่องที่ผู้ใช้เลือก: ทีละขั้นให้ทำตาม — **1 ฉาก = 1 ขั้นตอนจริง** เรียงตามลำดับที่ต้องทำ '
           'ห้ามข้ามขั้นและห้ามยุบ 2 ขั้นไว้ฉากเดียว · ทุกฉากต้องเห็น **ของที่กำลังเปลี่ยน** ชัด ๆ (มือกำลังทำ + ตัวงานใกล้ ๆ) '
           'ไม่ใช่ภาพบรรยากาศ · ของที่ทำไปแล้วต้องยังอยู่ในฉากถัดไป · '
           'ฉากสุดท้าย = ผลลัพธ์ที่เสร็จแล้วเต็มเฟรม พร้อมใช้/พร้อมเสิร์ฟ · เหมาะกับ ทำอาหาร สูตร วิธีพับ วิธีซ่อม วิธีประกอบ')

for gs in (withp, nop):
    for o in gs['options']:
        assert o['value'] == '' or o['value'] in ap, f'option "{o["value"]}" ไม่มีใน arcPlan'

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'v61 ok · มีสินค้า {len(withp["options"])} ตัวเลือก · ไม่มีสินค้า {len(nop["options"])} · arcPlan {len(ap)} คีย์')
