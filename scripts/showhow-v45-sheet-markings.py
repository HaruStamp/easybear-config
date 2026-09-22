#!/usr/bin/env python3
"""showhow v45 — เปลี่ยนกฎกันเลขบอร์ดจาก "ไล่ชื่อ" เป็น "นิยามหมวด"

ที่มา: ทีม minimal ทักว่า v44 (`Never copy a sheet or its numbered circles.`) ยังเป็นการไล่ชื่อของทีละอย่าง
  ⇒ รอบหน้าบอร์ดเพิ่มป้ายแบบใหม่ (เวลา · ชื่อฉาก · ลูกศร) กฎนี้จะหลับทันที
  = โรคเดียวกับที่เราสรุปเองทั้งวัน: **กฎห้ามที่ไม่ได้นิยามว่าอะไรนับเป็นของต้องห้าม**

แก้เป็นนิยามหมวด: **ทุกอย่างที่พิมพ์บนแผ่น = คำกำกับ ไม่ใช่เนื้อฉาก**
  `Never copy a sheet; its markings are annotation.`   (+5 ตัวอักษรจาก v44 · headroom เหลือ 22 ⇒ จ่ายไหว)
🪤 เลือกคำว่า `markings` แทนการไล่ (numbers/labels/times) เพราะครอบของที่ยังไม่มีด้วย และสั้นกว่า
🪤 ห้ามใช้ถ้อยคำทรง "ignore any on-screen text" ของ minimal ตรง ๆ — แอปเรามี **หัวเรื่อง/ซับที่ตั้งใจให้มี**
   ซึ่งโมเดลวาดจากบรรทัด `Thai overlay: "..."` ⇒ สั่งเมินข้อความทั้งหมดจะกลบของที่ต้องมี
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent.parent / 'showhow-dev.json'
s = P.read_text(encoding='utf-8')
OLD = 'Never copy a sheet or its numbered circles.'
NEW = 'Never copy a sheet; its markings are annotation.'
assert s.count(OLD) == 6, f'เจอ {s.count(OLD)} จุด (คาด 6) — รัน v44 ก่อน'
P.write_text(s.replace(OLD, NEW), encoding='utf-8')
print(f'แก้ 6 จุด · {len(NEW)-len(OLD):+d} ตัวอักษรต่อ prompt')
