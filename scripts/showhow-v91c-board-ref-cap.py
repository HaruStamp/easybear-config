#!/usr/bin/env python3
"""showhow-v91c — บอร์ดช่วง 3-6 รูปอ้างอิงเกินเพดาน 10 (บั๊กของ v90 · ยาม all-apps-safe ของ starter จับได้)

v90 ต่อ endRef ท้าย `also` ของทุกบอร์ด โดยคิดว่า "เต็มจริงก็แค่ภาพจบหลุดเอง"
❌ คิดผิด: บอร์ดช่วง 3-6 = pin + บอร์ดก่อนหน้า + image..image5 + room1-2 + face + endRef = **11**
   engine ตัดใบที่ 11 ทิ้ง = ภาพจบหาย · แต่ prompt ยังบอกว่า "รูปสุดท้ายที่แนบ = ภาพอ้างอิงฉากจบ"
   ⇒ โมเดลไปลอก **รูปหน้า/รูปห้อง** มาเป็นฉากจบแทน — แย่กว่าแค่หายเงียบ
   (เกิดเฉพาะเคสใส่รูปครบทุกช่อง แต่เป็นไปได้จริง)
แก้: ถอด image5 (มุมที่ 5 ของสินค้า) ออกจากบอร์ดช่วง 3-6 — ใบที่ถูกใช้น้อยสุด และช่วง 3-6 เห็นบอร์ดก่อนหน้าที่วาดสินค้าไว้แล้ว
     ⇒ ทุกบอร์ด ≤ 10 ทางโครงสร้าง (ยามของ starter นับ entry ที่ gate ด้วย item.* เป็น "ติดมาเสมอ" = กรณีเลวร้ายสุด)
ใช้: python3 scripts/showhow-v91c-board-ref-cap.py
"""
import json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
for o in c['ops']:
    if o['id'] in ('mnBoard3', 'mnBoard4', 'mnBoard5', 'mnBoard6'):
        also = o['refs']['also']
        before = 1 + len(also)
        o['refs']['also'] = [a for a in also if a.get('slot') != 'image5']
        after = 1 + len(o['refs']['also'])
        assert before == 11 and after == 10, f"{o['id']}: {before} → {after}"
        assert o['refs']['also'][-1]['slot'] == 'endRef', 'ภาพจบต้องยังอยู่ท้ายสุด (prompt อ้าง "รูปสุดท้ายที่แนบ")'
        print(f"{o['id']}: รูปอ้างอิง {before} → {after} (ถอด image5)")
for o in c['ops']:
    if o['id'].startswith('mnBoard'):
        n = 1 + len(o['refs'].get('also', []))
        assert n <= 10, f"{o['id']} ยังมี {n} รูป"
print('✅ ทุกบอร์ด ≤ 10 รูป (นับกรณีเลวร้ายสุด) · ภาพจบอยู่ท้ายสุดจริงเสมอ')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
