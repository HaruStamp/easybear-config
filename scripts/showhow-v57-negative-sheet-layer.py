#!/usr/bin/env python3
# showhow v57 — เพิ่ม "ชั้นที่ 2" กันแผ่นบอร์ดโผล่: ใส่ไว้ใน Negative ของ prompt วิดีโอ (ท่าที่ทีม minimal ใช้)
#
# ทำไมต้อง 2 ชั้น: v56 คืนคำสั่งตรง ("Never copy or show a sheet") แล้ว แต่คำสั่งตรงเป็นประโยคกลาง prompt
#   ซึ่งเป็นจุดที่ถูกเขียนทับบ่อยที่สุด (เคสนี้เพิ่งโดนมาเอง) · Negative เป็นบรรทัดของตัวเอง ไม่มีใครไปยุบรวม
# 🔑 วางไว้ **หน้าสุดของ Negative** — เพราะ Negative คือบรรทัดท้ายสุดที่เกณฑ์ G9 ยอมให้โดนตัดได้
#   ถ้าวางท้าย มันจะเป็นตัวแรกที่หายเวลา prompt ยาวเกิน
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
raw = open(P, encoding='utf-8').read()
c = json.loads(raw)

# 🪤 รอบแรกเติมอย่างเดียว (+40) แล้ว p95 ของวิดีโอทะลุ 3,900 ไป 31 ⇒ ตัวที่โดนตัดคือ "ท้าย Negative"
#    ซึ่งแปลว่ากฎใหม่รอด แต่กฎเก่าท้ายแถวหายแทน = ย้ายปัญหา ไม่ได้แก้
# ⇒ แลกที่: ตัด "no warped objects" (กันของบิดเบี้ยว — ทั่วไป) ออกไป แล้วเอา "no storyboard sheet" มาแทนหน้าแถว
#    เพราะเราเพิ่งโดนแผ่นบอร์ดโผล่เต็มจอ 2 วินาทีจริง ๆ ส่วนของบิดเบี้ยวยังไม่เคยเป็นปัญหาในคลิปไหน
OLD = 'Negative: no tripod or camera gear in frame, no warped objects,'
NEW = 'Negative: no storyboard sheet, no tripod or camera gear in frame,'
ops = json.dumps(c['ops'], ensure_ascii=False)
n = ops.count(OLD)
assert n == 6, f'คาด Negative 6 จุด เจอ {n}'
assert 'no storyboard sheet' not in ops, 'รันซ้ำ'
c['ops'] = json.loads(ops.replace(OLD, NEW))

before = json.loads(raw)
for k in before:
    if k != 'ops':
        assert json.dumps(before[k], ensure_ascii=False) == json.dumps(c[k], ensure_ascii=False), f'v57 แตะ {k}'
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'v57 ok · Negative 6 จุด · +{len(NEW)-len(OLD)} ตัวอักษร (อยู่ท้าย prompt = ชั้นที่ยอมให้โดนตัดตามเกณฑ์ G9)')
