#!/usr/bin/env python3
"""showhow-v126 — บอร์ดช่วง 1 ไม่มี "บอร์ดช่วงก่อนหน้า" ให้แนบ แต่ prompt บอกว่ามี (รูปแรก ๆ ที่แนบ … ห้ามลอกภาพในช่อง)
รูปแรกที่แนบจริงของช่วง 1 = รูปสินค้า ⇒ โมเดลถูกสั่ง "ห้ามลอก" รูปสินค้า · ทดสอบจริง 2026-10-13: กล่องใสกลายเป็นกล่องครีมทึบ 6/13 ใบ ทุกสไตล์
ซากจาก v11 (บอร์ดเรียง 1→6 · ช่วง 1 ไม่มีบอร์ดก่อนหน้า) — v22 แก้ถ้อยคำช่วง 2-6 แต่ช่วง 1 ยังเหลือ "รูปแรก ๆ ที่แนบ"
แก้: ตัดบรรทัดนี้ออกจาก mnBoard (ช่วง 1) เท่านั้น · ช่วง 2-6 ไม่แตะ
"""
import json, re
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
o = next(o for o in c['ops'] if o['id'] == 'mnBoard')
parts = o['prompt']['parts']
i = next(i for i, p in enumerate(parts) if isinstance(p, str) and '\nบอร์ดช่วงก่อนหน้าที่แนบมา (รูปแรก ๆ ที่แนบ)' in p)
new, n = re.subn(r'\nบอร์ดช่วงก่อนหน้าที่แนบมา \(รูปแรก ๆ ที่แนบ\):[^\n]*ห้ามลอกภาพในช่อง', '', parts[i])
assert n == 1, n
parts[i] = new
assert 'บอร์ดช่วงก่อนหน้า' not in json.dumps(o['prompt'], ensure_ascii=False)
for k in range(2, 7):
    assert 'บอร์ดช่วงก่อนหน้าที่แนบมา' in json.dumps(next(x for x in c['ops'] if x['id'] == f'mnBoard{k}')['prompt'], ensure_ascii=False), k
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✅ v126: ตัดบรรทัดบอร์ดก่อนหน้าออกจากบอร์ดช่วง 1 ·', repr(new[-80:]))
