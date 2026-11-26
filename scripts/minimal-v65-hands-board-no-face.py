#!/usr/bin/env python3
# minimal-dev v65: โหมด "เห็นแต่มือ ไม่เห็นหน้า" — บอร์ดห้ามวาดหน้าทุกช่อง (polish อัปเดตใหญ่ 27 พ.ย.)
#   เทสสดรอบ 2 (สัตว์ 3 ตัว + เห็นแค่มือ): บอร์ดช่อง 4 วาดหน้าผู้หญิง ทั้งที่กฎ charBoard มีอยู่ต้น prompt
#   ⇒ ย้ำกฎท้าย prompt บอร์ดทุกแผ่น (โมเดลภาพให้น้ำหนักท้าย prompt) + ฉากที่บทเขียนถึงสีหน้า/รีแอ็กชัน ให้เล่าผ่านมือ/สินค้า/สัตว์
#   โหมดอื่น prompt เดิมทุกไบต์ (block มี when)
# ใช้: python3 scripts/minimal-v65-hands-board-no-face.py [minimal-dev.json]   (รันซ้ำได้)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json'
d = json.load(open(F, encoding='utf-8'))
HANDS = "เห็นแต่มือ ไม่เห็นหน้า"
TXT = "\n\nย้ำ: ทุกช่องห้ามมีหน้า ศีรษะ ไหล่ ตัวคน — รีแอ็กชันใช้มือ/สัตว์"
# ที่ว่าง: บอร์ด 20 วิ โหมดมือ+เจ้าของ+สัตว์ 3 ตัว ชนเพดาน 3900 ⇒ ย้ายส่วน "ห้าม" ของกฎต้น prompt (charBoard โหมดมือ) ไปท้ายแทน (สุทธิ +20 ตัว)
CB_OLD = "เห็นแต่มือ/แขนที่ถือหรือใช้สินค้า ห้ามมีใบหน้า ศีรษะ ไหล่ หรือตัวเต็มในทุกช่อง"
CB_NEW = "เห็นแต่มือ/แขนที่ถือหรือใช้สินค้า"
BLK = {"op": "block", "sep": "", "parts": [{"when": {"op": "eq", "a": "{values.svChar}", "b": HANDS}, "value": TXT}]}
_cb = [k for k in d['lookups']['charBoard'] if k.startswith(HANDS + '|')]
assert len(_cb) == 4 and all(d['lookups']['charBoard'][k] in (CB_OLD, CB_NEW) for k in _cb), _cb
for k in _cb: d['lookups']['charBoard'][k] = CB_NEW
n = [0, 0]
for o in d['ops']:
    if o['id'] not in ('mnBoard', 'mnBoard2', 'mnBoard3'): continue
    pp = o['prompt']['parts']
    if pp[-1] == BLK: n[1] += 1; continue
    pp.append(json.loads(json.dumps(BLK))); n[0] += 1
assert n[0] + n[1] == 3, n
print(f'v65: บอร์ดโหมดเห็นแต่มือ ย้ำห้ามหน้าท้าย prompt {n[0]} op (มีแล้ว {n[1]})')
open(F, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2))
