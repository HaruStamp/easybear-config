#!/usr/bin/env python3
"""showhow v44 — ห้ามลอก "วงกลมเลขฉาก" ของบอร์ดลงในวิดีโอ

หลักฐาน (2026-09-22 · คลิปทาสีห้องนอน 40 วิ · ทีมช่างเบลอ · engine 1.10.0 · config v43):
  วิดีโอช่วง 3 มีวงกลมขาวเลข **13** มุมซ้ายบนตลอดช่วง
  วิดีโอช่วง 4 ขึ้นเลข **17** แล้วเปลี่ยนเป็น **20** ตามฉาก ⇒ โมเดลวาดป้ายเลขฉากตามบอร์ดทีละช็อต
  (ช่วง 1-2 ไม่มี — วัดด้วยจำนวนพิกเซลขาวจัด/ดำจัดในกรอบมุมซ้ายบน: ช่วง 3/4 = 2,330/2,703 · ช่วง 1/2 = 0)

ราก: บอร์ดวาด "วงกลมทึบใส่เลขฉาก" ทุกช่องโดยตั้งใจ (เป็นหมุดให้คนอ่านบอร์ด)
  แต่คำสั่งฝั่งวิดีโอห้ามแค่ *"Never copy a sheet or show one on screen"* = ห้ามลอก**แผ่น**
  ⇒ โมเดลไม่ถือว่าวงกลมเลขเป็น "แผ่น" มันเป็นสิ่งที่อยู่ในช่องภาพที่สั่งให้ลอก ⇒ ลอกมาด้วย
📌 รูปแบบเดิมของวันนี้: **กฎห้ามที่ไม่ได้นิยามว่า "อะไรบ้างที่นับเป็นของต้องห้าม"**

🪤 ที่ว่างเหลือน้อยมาก (ชั้นตัดสินของ G9 เหลือ 11 ตัวอักษร) ⇒ จ่ายคืนด้วยการตัด "no morphing" ใน Negative
   (ซ้ำกับ "no warped objects" ที่อยู่บรรทัดเดียวกัน · ไม่ใช่กฎที่เคยแก้บั๊กจริงเหมือน no tripod)
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent.parent / 'showhow-dev.json'
s = P.read_text(encoding='utf-8')

OLD_SHEET = 'Never copy a sheet or show one on screen.'
NEW_SHEET = 'Never copy a sheet or its numbered circles.'   # ไม่ใส่ 'panel edges' — หัว prompt ห้าม panels/borders อยู่แล้ว
OLD_NEG = ', no morphing, no non-Thai text.'
NEW_NEG = ', no non-Thai text.'

assert s.count(OLD_SHEET) == 6, f'sheet line เจอ {s.count(OLD_SHEET)} จุด (คาด 6)'
assert s.count(OLD_NEG) == 6, f'negative เจอ {s.count(OLD_NEG)} จุด (คาด 6)'
s = s.replace(OLD_SHEET, NEW_SHEET).replace(OLD_NEG, NEW_NEG)
P.write_text(s, encoding='utf-8')
print(f'แก้ 6 จุด · สุทธิ {len(NEW_SHEET)-len(OLD_SHEET) + len(NEW_NEG)-len(OLD_NEG):+d} ตัวอักษรต่อ prompt')
