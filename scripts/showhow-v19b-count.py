#!/usr/bin/env python3
# showhow-v19b-count.py — ตัดคำว่า "จำนวน" ออกจากรายการห้ามเปลี่ยนของบอร์ด (2026-09-21)
# ราก: บรรทัดสินค้าขัดกันเอง — "ห้ามเปลี่ยนสี ทรง สัดส่วน ฉลาก โลโก้ **จำนวน**" (ห้ามเปลี่ยนจำนวนตามรูป = 2 ขวด)
#      ชนกับ "ถ้ารูปเป็นแพ็กหลายชิ้น … ให้วาดชิ้นเดียว" ⇒ ช่องโชว์ของวาดขวดคู่ทั้งชุด -f และ -h (รูปต้นทางเป็นแพ็กคู่จริง)
# แก้: เอา "จำนวน" ออกอย่างเดียว เหลือ สี ทรง สัดส่วน ฉลาก โลโก้ — กฎ "วาดชิ้นเดียว" จึงไม่มีคู่แข่ง (+ได้ที่ว่าง 8 ตัวอักษร)
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
OLD = 'ห้ามเปลี่ยนสี ทรง สัดส่วน ฉลาก โลโก้ จำนวน ห้ามวาดใหม่หรือเป็นการ์ตูน'
NEW = 'ห้ามเปลี่ยนสี ทรง สัดส่วน ฉลาก โลโก้ ห้ามวาดใหม่หรือเป็นการ์ตูน'
raw = open(P, encoding='utf-8').read()
if NEW in raw and OLD not in raw: print('· มี v19b แล้ว ข้าม'); sys.exit(0)
s = json.dumps(json.loads(raw), ensure_ascii=False)
n = s.count(OLD); assert n == 6, f'เจอ {n} จุด (คาด 6)'
open(P, 'w', encoding='utf-8').write(json.dumps(json.loads(s.replace(OLD, NEW)), ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
G = os.path.join(HERE, 'showhow-v9-board-collage.py'); g = open(G, encoding='utf-8').read()
assert g.count(OLD) == 1
open(G, 'w', encoding='utf-8').write(g.replace(OLD, NEW))
print('✓ v19b ·', n, 'จุด ·', os.path.getsize(P), 'bytes')
