#!/usr/bin/env python3
"""showhow-v144 — mnFace ปลอดภัยบน engine 1.22 (บั๊กเทสจริง Dev bc691528 26 พ.ย.)
อาการ: งาน people=อัตโนมัติ (บทเลือกไม่ใช่เต็มตัว) → หยุดหลัง mnQueue ไม่มีบอร์ด/วิดีโอ ไม่มี error
ต้นเหตุ (engine 1.22 runProductLoop ก่อน 4d5d9f6): gen ใน productLoop.gens ที่ where ราย kid ไม่ตรง → runOpPart กรองทิ้งเงียบ
  → slot ว่าง → `if (!slotFilled(kid, out)) { bad = true; break }` = คลิปนั้นหยุดทั้งสาย · loopItemDone ก็รอ slot นี้ตลอด
  mnBoard2..6/mnVideo2..6 รอดเพราะตัวกรองจริงอยู่ที่ op.when ระดับโปรเจกต์ (values.svSec>N → loopGens ตัดทิ้งก่อน)
  ส่วน where ราย kid (s6en!=) ตรงทุกคลิปเสมอเมื่อ when ผ่าน — mnFace เป็น gen ตัวเดียวที่ where ราย kid ไม่ตรงได้จริง
แก้:
  1. ถอด mnFace ออกจาก auto.productLoop.gens (คงใน stages = โหมดทีละขั้น · runOpPart กรองราย kid ได้ปกติ ไม่มี break)
     ⇒ โหมดออโต้บน 1.22 = ไม่วาดหน้าก่อน (เหมือนก่อน v138) · ใส่กลับได้เมื่อ Dev/ตัวขายขึ้น engine ≥1.23 (มี loopGenApplies)
  2. ประโยค "คนในรูปหน้าที่แนบ" (บอร์ด 1-2 · วิดีโอ 1 · ปก) ขึ้นเฉพาะเมื่อมีรูปหน้าจริง (tasks.face หรือรูปที่ผู้ใช้แนบ)
     ไม่มีรูป = กลับไปประโยคเดิมก่อน v138 — กัน "the attached face photo" ชี้ผิดรูป (โมเดลเอารูปสินค้าเป็นหน้า)
ใช้: python3 scripts/showhow-v144-face-engine122.py  (รันบน v143 · รันซ้ำ = ไม่ทำอะไร)
"""
import json, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
s0 = open(P, encoding='utf-8').read()
c = json.loads(s0)
assert json.dumps(c, ensure_ascii=False, indent=1) + '\n' == s0
g = c['auto']['productLoop']['gens']
if 'mnFace' not in g:
    print('v144: ทำไปแล้ว — ไม่แตะ'); sys.exit(0)
g.remove('mnFace')
assert any(s.get('op') == 'mnFace' for s in c['stages'])
HAS = {'op': 'not', 'a': {'op': 'eq', 'a': '{item.slots.face}', 'b': ''}}
n = 0
def walk(x):
    global n
    if isinstance(x, dict):
        t = x.get('then')
        if x.get('op') == 'cond' and isinstance(t, dict) and t.get('op') == 'lookup' and t.get('key') == 'ใบหน้าตัวละคร|รูปหน้า':
            w = x['when']; assert w.get('op') == 'and' and 'list' in w
            w['list'].append(HAS); n += 1
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
for o in c['ops']:
    if o['id'].startswith(('mnBoard', 'mnVideo')): walk(o['prompt'])
assert n >= 3, n
cv = next(o for o in c['ops'] if o['id'] == 'mnCover')['prompt']['parts']
fb = next(p for p in cv if isinstance(p, dict) and 'The attached face photo' in json.dumps(p, ensure_ascii=False))
w0 = fb['parts'][0]['when']
fb['parts'][0]['when'] = {'op': 'and', 'list': [w0, {'op': 'or', 'list': [HAS, {'op': 'eq', 'a': '{item.peopleSrc}', 'b': 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'}]}]}
print(f'✅ v144: mnFace ออกจาก productLoop.gens · ประโยครูปหน้าต้องมีรูปจริง {n} จุด + ปก')
open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
