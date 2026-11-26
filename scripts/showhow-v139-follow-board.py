#!/usr/bin/env python3
"""showhow-v139 — วิดีโอตามช่องสตอรีบอร์ดทีละฉาก (เจ้าของสั่ง 26 พ.ย.: "นักเรียนดูบอร์ดก่อนแล้วค่อยเจน")
เดิม: 'image 1 = this part's 5 scenes — copy its room, fixtures, surfaces, framing, lighting' = ลอกแค่ห้อง/แสง ไม่ได้สั่งให้ฉาก N ตามช่อง N
ใหม่: ฉาก N ตามช่อง N — ท่า องค์ประกอบ มุมกล้อง ตำแหน่งสินค้า (+ห้อง ของในห้อง แสง)
- แก้ประโยคเดียวกันทั้ง 6 op วิดีโอ (ช่วงไทม์แลปส์ต่อเฟรมไม่มีประโยคนี้อยู่แล้ว — ไม่แตะ)
- คงประโยคกัน 'แผ่นบอร์ดขึ้นจอ' ทุกตัวอักษร (Sheets, panels and number marks must NEVER appear on screen; frame 1 is already a live scene.)
- ยาวขึ้น +29 ตัว (ตัด 'surfaces' · 'same light' ซ้ำ) — วัดด้วย G9 แล้ว
ใช้: python3 scripts/showhow-v139-follow-board.py  (รันบน v138)
"""
import json
P = 'showhow-dev.json'
s0 = open(P, encoding='utf-8').read()
c = json.loads(s0)
assert json.dumps(c, ensure_ascii=False, indent=1) + '\n' == s0
OLD = "\n\nAttached sheets are a silent guide: image 1 = this part's 5 scenes — copy its room, fixtures, surfaces, framing, lighting; others = same room, same light. Sheets, panels and number marks must NEVER appear on screen; frame 1 is already a live scene."
NEW = "\n\nAttached sheets are a silent guide: image 1 = this part's 5 scenes — scene N follows panel N: pose, framing, camera angle, product position, room, fixtures, light; others = same room. Sheets, panels and number marks must NEVER appear on screen; frame 1 is already a live scene."
n = 0
def walk(x):
    global n
    if isinstance(x, dict):
        for k, v in x.items():
            if v == OLD: x[k] = NEW; n += 1
            else: walk(v)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            if v == OLD: x[i] = NEW; n += 1
            else: walk(v)
for o in c['ops']:
    if o['id'].startswith('mnVideo'): walk(o['prompt'])
assert n == 6, n
print(f'✅ v139: {n} op วิดีโอ · +{len(NEW) - len(OLD)} ตัว')
open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
