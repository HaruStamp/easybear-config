#!/usr/bin/env python3
"""pro-label-short.py — คำอธิบาย Nano Banana Pro สั้นลง (พี่หมี 27 พ.ย. 2569: "ปรับคำอธิบาย โมเดล nano banana pro ให้สั้นกระชับกว่านี้")
  ปุ่ม Pro          'ดีสุด · เขียนไทยได้'                          → 'ดีสุด'   (คู่ 2.1 'มาตรฐาน' · 2 Lite 'ประหยัด')
  บรรทัดใต้ปุ่ม     'ภาพที่มีตัวหนังสือไทย ระบบใช้ Pro ให้อัตโนมัติ'     → 'มีข้อความไทย ใช้ Pro อัตโนมัติ'
  ตั้งค่ารายสินค้า   'มีข้อความบนภาพ ระบบใช้ Nano Banana Pro ให้อัตโนมัติ' → 'มีข้อความไทย ใช้ Pro อัตโนมัติ'   (minimal · hardsell)
แตะเฉพาะข้อความ UI ใน phases (desc ของปุ่ม / value ของ el:text) · ops/prompt ไม่แตะ (ยาม: ops ก่อน=หลังทุกไบต์ + model-standard-proof.ts ต่าง 0)
ต้นฉบับบล็อก = model-standard.py (แก้คู่กัน · podcast/petdance/parody/fashion dev ได้จาก build ของแอป)
ใช้: python3 scripts/pro-label-short.py <ไฟล์ config>…   (แก้ในที่ · รันซ้ำได้ = ไม่เปลี่ยน)
"""
import json, sys

NEW_HINT = 'มีข้อความไทย ใช้ Pro อัตโนมัติ'
REP = {('desc', 'ดีสุด · เขียนไทยได้'): 'ดีสุด',
       ('value', 'ภาพที่มีตัวหนังสือไทย ระบบใช้ Pro ให้อัตโนมัติ'): NEW_HINT,
       ('value', 'มีข้อความบนภาพ ระบบใช้ Nano Banana Pro ให้อัตโนมัติ'): NEW_HINT}


def walk(o, n):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and (k, v) in REP: o[k] = REP[(k, v)]; n[(k, v)] = n.get((k, v), 0) + 1
            else: walk(v, n)
    elif isinstance(o, list):
        for v in o: walk(v, n)


for F in sys.argv[1:]:
    raw = open(F, encoding='utf-8').read()
    indent = 2 if raw.startswith('{\n  "') else 1
    c = json.loads(raw)
    ops0 = json.dumps(c['ops'], ensure_ascii=False)
    n = {}
    walk(c['phases'], n)
    assert json.dumps(c['ops'], ensure_ascii=False) == ops0
    out = json.dumps(c, ensure_ascii=False, indent=indent) + ('\n' if raw.endswith('\n') else '')
    s = json.dumps(c, ensure_ascii=False)
    for (k, v) in REP: assert v not in s, (F, v)   # ไม่เหลือข้อความเก่าที่ไหนเลย (รวม ops)
    open(F, 'w', encoding='utf-8').write(out)
    print(F, 'แก้', sum(n.values()), {v[:12]: x for (k, v), x in n.items()})
