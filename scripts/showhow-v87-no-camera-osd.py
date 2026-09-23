#!/usr/bin/env python3
"""showhow-v87 — ตัดคำ "4K" ออกจาก prompt วิดีโอ (คำกลายเป็นตัวหนังสือบนจอ)

เจอจากคลิปจริง 2026-09-23 (`docs/qa/2026-09-23-castkind/` เคสของเล่นแมว · 10 วิ · กล้องนิ่ง):
  มุมซ้ายบนของทุกเฟรมมีตัวหนังสือ **"4K"** · มุมขวาบนมี **"30 —"** (= เฟรมเรต) + แถบตารางที่ขอบล่าง
  ⇒ โมเดลตีความว่าเป็น **UI ของกล้อง/เทมเพลตวิดีโอรีวิว** แล้ววาดลงเฟรมจริง

🪤 ตระกูลเดียวกับบั๊ก "tripod" (คลิปแรก 2026-09-15): **คำบรรยายเทคนิคในprompt กลายเป็นวัตถุ/ตัวหนังสือในภาพ**
   ทางแก้ที่ได้ผลคือ **ตัดคำต้นตอทิ้ง** ไม่ใช่เพิ่มบรรทัด Negative
   (Negative อยู่ท้ายสุด = ตัวแรกที่โดนตัดเมื่อชนเพดาน ⇒ พึ่งไม่ได้ · และ "no non-Thai text" ก็มีอยู่แล้วแต่ไม่กัน)

ที่ตัด: `, 4K` ท้ายประโยคนำของ mnVideo1-6 — ความคมชัดมาจากโมเดลอยู่แล้ว ไม่ได้มาจากคำนี้
ได้เพดานคืน 4 ตัวอักษร/op ด้วย

ใช้: python3 scripts/showhow-v87-no-camera-osd.py
"""
import json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
OLD, NEW = 'of a real lived-in home, 4K.', 'of a real lived-in home.'

hit = 0
for op in c['ops']:
    if not op['id'].startswith('mnVideo'): continue
    # 🪤 ช่วง 2-6 มีบรรทัด CONTINUATION นำหน้า ⇒ ประโยคนำไม่ได้อยู่ชิ้นแรกเสมอ — ไล่หาเอง
    n = 0
    def fix(node):
        global n
        if isinstance(node, str): 
            return node.replace(OLD, NEW) if OLD in node else node
        if isinstance(node, dict):
            return {k: fix(v) for k, v in node.items()}
        if isinstance(node, list):
            return [fix(v) for v in node]
        return node
    before = json.dumps(op['prompt'], ensure_ascii=False)
    assert OLD in before, f"{op['id']}: ไม่เจอประโยคนำที่มี 4K"
    op['prompt'] = fix(op['prompt'])
    assert OLD not in json.dumps(op['prompt'], ensure_ascii=False)
    hit += 1
assert hit == 6, f'ควรแก้ 6 op · แก้ {hit}'
print(f'① ตัด "4K" ออกจากประโยคนำของ mnVideo 6 ตัว')

s = json.dumps(c, ensure_ascii=False)
assert '4K' not in s, 'ยังเหลือคำว่า 4K'
for bad in ('1080', '60fps', '30fps', 'fps'):
    assert bad not in s, f'มีคำบอกสเปกกล้องอีก: {bad} — เสี่ยงกลายเป็นตัวหนังสือบนจอ'
print('✅ ยามผ่าน: ไม่เหลือคำบอกสเปกภาพ/เฟรมเรตใน prompt เลย')

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nเขียน {P} แล้ว')
