#!/usr/bin/env python3
# showhow v60 — งาน "ไม่มีสินค้า" ก็เลือกวิธีเล่าเรื่องได้ + เพิ่มโครงเรื่อง "ไทม์แลปส์" (พี่หมีเสนอ 2026-09-22)
#
# ทำไมเดิมไม่มี: บล็อก "เล่าเรื่องแบบไหน" ถูกกั้นด้วย when = item.hasProduct!=ไม่มี
#   เพราะ 2 ใน 3 โครงเรื่องเดิมผูกกับสินค้า (ปัญหา→แก้แล้ว = ของที่ติดแล้วจบ · ทัวร์จุดเด่น = โชว์ของทำงาน)
#   ⇒ สายไม่มีสินค้าเลยถูกบังคับเป็น "ก่อน → ลงมือ → หลัง" อัตโนมัติเสมอ
# 🪤 ผลข้างเคียงที่เพิ่งเจอ: คนอยากได้ "ไทม์แลปส์" ต้องไปเดาเองว่าต้องเข้า ▸ ขั้นสูง แล้วเลือกมุมกล้อง "ตั้งนิ่ง"
#   (เคสสร้างบ้านของพี่หมี) — ซึ่งไม่มีทางรู้จากหน้าจอ
#
# v60:
#   ① เพิ่มโครงเรื่อง "ไทม์แลปส์กล้องนิ่ง" ให้สายมีสินค้า (5 ตัวเลือก)
#   ② เพิ่มบล็อกคู่ขนานสำหรับสาย "ไม่มีสินค้า" — 4 ตัวเลือก (ไม่มีทัวร์จุดเด่น เพราะต้องมีของให้ทัวร์)
#      🪤 ต้องแยกเป็น 2 บล็อก เพราะ grid-select ของ engine **ไม่รองรับ when ราย option** (normOptions ไม่อ่าน)
#   ③ arcPlan เพิ่มคีย์ใหม่ (อยู่ใน systemInstruction ของ mnPlan = ไม่กินเพดาน prompt ภาพ/วิดีโอ)
import json, sys, copy

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ARC = 'ไทม์แลปส์กล้องนิ่ง'

blk = c['phases'][0]['form'][2]['card'][0]['card'][0]['card'][5]
assert blk['card'][1]['when'] == 'item.hasProduct!=ไม่มี', 'โครงเปลี่ยน — หยุด'
gs = blk['card'][1]['card'][1]
assert gs['field'] == 'arc' and len(gs['options']) == 4

NEW_OPT = {'value': ARC, 'label': 'ไทม์แลปส์', 'desc': 'กล้องนิ่งมุมเดียว เห็นงานค่อย ๆ คืบหน้า', 'icon': 'timelapse'}
assert all(o['value'] != ARC for o in gs['options']), 'รันซ้ำ'
gs['options'].append(NEW_OPT)

# ② บล็อกของสาย "ไม่มีสินค้า" — ตัดทัวร์จุดเด่นออก
nb = copy.deepcopy(blk['card'][1])
nb['when'] = 'item.hasProduct=ไม่มี'
nb['card'][1]['options'] = [o for o in copy.deepcopy(gs['options']) if o['value'] != 'ทัวร์จุดเด่น']
assert len(nb['card'][1]['options']) == 4
blk['card'].insert(2, nb)

# ③ arcPlan
ap = c['lookups']['arcPlan']
assert ARC not in ap
ap[ARC] = ('โครงเรื่องที่ผู้ใช้เลือก: ไทม์แลปส์กล้องนิ่ง — กล้องตั้งนิ่งมุมเดียวทั้งคลิป '
           'ทุกฉากต้องเป็นกรอบภาพเดียวกัน (ขึ้นต้น s*en ว่า "Same wide shot") และ camN ทุกฉากเป็นมุมเดิม · '
           'ฉากติดกันห่างกันแค่ **ขั้นเดียว** ของงาน ห้ามข้ามขั้น · สิ่งที่ทำไปแล้วต้องสะสมค้างอยู่ในเฟรมทุกฉากถัดไป · '
           'ฉากสุดท้าย = กรอบเดียวกับฉากแรก เห็นผลลัพธ์เต็มพื้นที่ · เหมาะกับงานที่พื้นที่ค่อย ๆ เปลี่ยนทั้งผืน เช่น สร้าง/ต่อเติม/จัดสวน/ทาสี')

# sanity: ทุก option.value ต้องมีคีย์ใน arcPlan (ยกเว้นค่าว่าง = อัตโนมัติ)
for block in (gs, nb['card'][1]):
    for o in block['options']:
        assert o['value'] == '' or o['value'] in ap, f'option "{o["value"]}" ไม่มีใน arcPlan'

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'v60 ok · สายมีสินค้า {len(gs["options"])} ตัวเลือก · สายไม่มีสินค้า {len(nb["card"][1]["options"])} ตัวเลือก · arcPlan {len(ap)} คีย์')
