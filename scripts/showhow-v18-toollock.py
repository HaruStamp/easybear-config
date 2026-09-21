#!/usr/bin/env python3
# showhow-v18-toollock.py — "อุปกรณ์ต้องเป็นรุ่นเดียวกับรูปทุกช่อง" (พี่หมีเจอจากบอร์ด 6 ช่วง 2026-09-21)
# อาการ: สินค้าหลัก (ขวด) เป๊ะทุกช่วง แต่ **อุปกรณ์ชิ้นที่ 2 (แปรง 4in1 ด้ามยาว) ถูกย่อเป็นแปรงมือ**
#        ช่วง 2 ที่บทโฟกัสตัวแปรงวาดถูก (ด้ามยาว+ยางปาดเหลือง) · ช่วง 1/3/4/5 วาดเป็นแปรงมือด้ามสั้น
#        แล้วบานปลาย เพราะช่วง K ลอก "ของติดตาย" จากบอร์ดช่วง K-1 ที่ผิดไปแล้ว
# ราก: PRODUCT LOCK พูดถึง "ทรง/สี/ฉลาก" ซึ่งโมเดลตีว่าเป็นเรื่องของ *ขวด* — ไม่มีคำสั่งเรื่อง **ด้าม/ขนาดเทียบมือ**
# แก้: เติมประโยคเดียวต่อท้ายบรรทัดสินค้าของบอร์ดทุกช่วง (แก้ทั้ง JSON และ generator v9 ให้ตรงกัน)
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..', 'showhow-dev.json')
ANCHOR = '(ห้ามเปลี่ยนเป็นขวดหรือแปรงทรงอื่น)'
ADD = (' · **อุปกรณ์ทุกชิ้นต้องเป็นรุ่นเดียวกับรูปทุกช่อง รวมด้าม ความยาวด้าม ทรงหัว สีขนแปรง'
       ' — ในรูปมีด้ามยาวต้องมีด้ามยาวทุกช่อง ห้ามย่อเป็นแปรงมือ**')

raw = open(P, encoding='utf-8').read()
if ADD in raw:
    print('· JSON มี v18 อยู่แล้ว ข้าม'); sys.exit(0)
d = json.loads(raw)
s = json.dumps(d, ensure_ascii=False)
n = s.count(ANCHOR)
assert n == 6, f'เจอหมุดสินค้า {n} จุด (คาด 6 = บอร์ด 6 ช่วง)'
s = s.replace(ANCHOR, ANCHOR + ADD)
open(P, 'w', encoding='utf-8').write(json.dumps(json.loads(s), ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))

# mirror เข้า generator เพื่อไม่ให้หายเมื่อสร้างใหม่จากฐาน
G = os.path.join(HERE, 'showhow-v9-board-collage.py')
g = open(G, encoding='utf-8').read()
if ADD not in g:
    assert g.count(ANCHOR) == 1, g.count(ANCHOR)
    open(G, 'w', encoding='utf-8').write(g.replace(ANCHOR, ANCHOR + ADD))
    print('✓ mirror เข้า showhow-v9-board-collage.py')
print('✓ v18 toollock ·', n, 'จุด ·', os.path.getsize(P), 'bytes')
