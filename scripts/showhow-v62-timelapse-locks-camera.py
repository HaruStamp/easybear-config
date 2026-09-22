#!/usr/bin/env python3
# showhow v62 — ตัวเลือก "ไทม์แลปส์กล้องนิ่ง" ต้องล็อกกล้องจริง (ยิงบทจริงแล้วพบว่าไม่ล็อก)
#
# หลักฐาน (เคสทาสีห้อง 20 วิ · arc=ไทม์แลปส์ · มุมกล้อง=อัตโนมัติ):
#   camN ที่ได้ = แพนเข้าหาช้าๆ · ปานกลางแพนตามมือ · ปานกลางซูมออก
#   ฉากที่ขึ้นต้นว่า "Same wide shot" = **0/10** ทั้งที่ arcPlan สั่งไว้ชัด
# ราก: บล็อกมุมกล้องใน mnPlan เปิดเฉพาะ `values.svCamMode!=` ⇒ เลือกอัตโนมัติ = ไม่มีคำสั่งกล้องเลย
#   แล้วท้าย prompt ยังมีบรรทัด "ข้อกำหนดรายฉาก … ค่าว่าง = ออกแบบเองให้เหมาะกับงาน" ซึ่งมาทีหลัง = ชนะ
# ⇒ ตัวเลือกใหม่จึง "ชื่อบอกว่าล็อกกล้อง แต่ไม่ได้ล็อก"
#
# v62: เพิ่มบล็อกคู่ขนาน — ถ้าผู้ใช้ไม่ได้เลือกมุมกล้องเอง **และ** เลือกโครงเรื่องไทม์แลปส์
#      ให้ยัดคำสั่งกล้องนิ่งชุดเดียวกับที่ svCamMode=ตั้งนิ่ง ใช้
#      (อยู่ใน systemInstruction ของ mnPlan = ไม่กินเพดาน prompt ภาพ/วิดีโอ)
# + mnQueue ส่ง arc ลง task ด้วย เพื่อให้ชั้นบอร์ด/วิดีโอและการดีบักเห็นค่าเดียวกัน
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ARC = 'ไทม์แลปส์กล้องนิ่ง'
CAMKEY = 'ตั้งนิ่งเห็นทั้งพื้นที่'
assert CAMKEY in c['lookups']['camPlan']

op = [o for o in c['ops'] if o['id'] == 'mnPlan'][0]
blk = op['prompt']['parts'][0]['parts'][5]
assert blk.get('op') == 'block' and len(blk['parts']) == 1, 'โครงบล็อกมุมกล้องเปลี่ยน — หยุด'
assert blk['parts'][0]['when'] == 'values.svCamMode!=', blk['parts'][0]['when']

blk['parts'].append({
    'when': {'op': 'and',
             'a': {'op': 'eq', 'a': '{values.svCamMode}', 'b': ''},
             'b': {'op': 'eq', 'a': '{item.arc}', 'b': ARC}},
    'value': {'op': 'concat', 'parts': ['\n', {'op': 'lookup', 'table': 'camPlan', 'key': CAMKEY, 'fallback': ''}]},
})

# mnQueue: ส่ง arc ลง task
q = [o for o in c['ops'] if o['id'] == 'mnQueue'][0]['spawn']['fields']
assert 'arc' not in q
q['arc'] = '{parent.fields.arc}'          # v1.7.1: spawn mode B อ่าน field ของ product ได้ผ่าน {parent.*}
tf = c['collections']['tasks']['fields']
assert 'arc' not in tf
tf.append('arc')

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v62 ok · บล็อกมุมกล้องของ mnPlan มี 2 ทาง (เลือกเอง / ไทม์แลปส์+อัตโนมัติ) · mnQueue ส่ง arc ลง task')
