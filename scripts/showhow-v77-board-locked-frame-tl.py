#!/usr/bin/env python3
# showhow v77 — โหมดไทม์แลปส์: บอร์ดต้องล็อกกรอบ "ทุกช่อง" ไม่ใช่แค่ช่องปิดท้าย (2026-09-22 ดึกมาก)
#
# หลักฐาน: docs/qa/2026-09-22-v76-land-timelapse/ (สร้างบ้าน 30 วิ · ที่ดินจริงของพี่หมี)
#   ภายในช่วง = long take จริง ภูเขาไม่ขยับทั้ง 10 เฟรม ✓
#   แต่ **ข้ามช่วงแล้วมุมกล้องเปลี่ยนจริงจัง** — ช่วง 1 ทุ่งกว้างภูเขาชัด · ช่วง 2 ใกล้พื้นสแลบ ภูเขามีหมอก · ช่วง 3 เปลี่ยนอีก
#
# 🔎 รากอยู่ที่ "บอร์ด" ไม่ใช่ "วิดีโอ" — นับบล็อกที่ gate ด้วย arc=ไทม์แลปส์:
#     mnVideo* = 20 จุด (v65 CAMERA MODE · v66 โหมดคน · v67 long take)
#     mnBoard* = **2 จุด** และทั้งคู่เป็นแค่ "โหมดคนเป็นช่างเบลอ" — ไม่มีคำสั่งล็อกกรอบเลยสักคำ
#   ⇒ บอร์ดแต่ละใบวาดมุมกว้างตามใจตัวเอง แล้ววิดีโอลอกบอร์ดมาอีกที
#   🪤 กฎล็อกกรอบมีอยู่แล้วแต่ gate ด้วย `values.svSec=<ความยาวที่แผ่นนี้เป็นใบสุดท้าย>` ⇒ ครอบแค่ช่องปิดของคลิป
#
# 🛡️ เรื่องความยาว — รอบแรกผมเขียน 185/215 ตัวอักษร **แล้วยามเขียว** เพราะตัววัด G9 ไม่รู้จักฟิลด์ `arc` เลย
#    (วัดด้วย arc ว่างตลอด ⇒ โหมดไทม์แลปส์ไม่เคยถูกวัดสักครั้ง) · เพิ่มมิติ arc เข้าไปแล้วยามแดงทันที 220 เคส สูงสุด 4,005
#    วัดใหม่เฉพาะโหมดไทม์แลปส์: บอร์ดยาวสุด **3,789 ⇒ เหลือ 111 ตัวอักษร** ⇒ ข้อความต้องไม่เกินนั้น
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
TL = 'ไทม์แลปส์กล้องนิ่ง'
IS_TL = {'op': 'eq', 'a': '{item.arc}', 'b': TL}
BUDGET = 111

FIRST = '\nไทม์แลปส์: ทุกช่องกรอบเดียวกัน จุดยืน ความสูง ระยะ ฉากหลังตรงกัน เปลี่ยนเฉพาะความคืบหน้า'
LATER = '\nไทม์แลปส์: ทุกช่องกรอบเดียวกับช่องแรกของรูปที่แนบใบแรก จุดยืน ความสูง ระยะ ฉากหลังตรงกัน'
# 🪤 ตัด "เปลี่ยนเฉพาะงาน" ออกเพื่อเอา headroom คืน (8 → 22 ตัวอักษร) — ความหมายนั้นมีอยู่แล้วใน arcPlan
#    ("สิ่งที่ทำไปแล้วต้องสะสมค้างอยู่ในเฟรมทุกฉาก") จึงไม่ได้หายไปจากบท
assert len(FIRST) <= BUDGET and len(LATER) <= BUDGET, (len(FIRST), len(LATER))

done = []
for op in c['ops']:
    oid = op['id']
    if not oid.startswith('mnBoard'):
        continue
    parts = op['prompt']['parts']
    assert 'ไทม์แลปส์: ทุกช่องกรอบเดียวกัน' not in json.dumps(parts, ensure_ascii=False), 'รันซ้ำ'
    idx = None
    for i, x in enumerate(parts):
        if 'ช่องภาพตามลำดับ' in json.dumps(x, ensure_ascii=False):
            idx = i
            break
    assert idx is not None, oid
    parts.insert(idx, {'op': 'block', 'sep': '', 'parts': [
        {'when': IS_TL, 'value': FIRST if oid == 'mnBoard' else LATER}]})
    done.append(oid)

assert len(done) == 6, done
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v77 ok ·', done, '· ยาว', len(FIRST), '/', len(LATER), 'ตัวอักษร (งบ', BUDGET, ')')
