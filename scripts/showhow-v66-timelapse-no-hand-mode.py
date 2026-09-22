#!/usr/bin/env python3
# showhow v66 — ไทม์แลปส์: โหมดคนต้องไม่ใช่ "เห็นแต่มือ" (ชิ้นสุดท้ายที่ทำให้กล้องไม่นิ่งจริง)
#
# หลักฐานจากเคสที่ดินของพี่หมี บน v65 (ซึ่งมีบรรทัด CAMERA MODE แล้ว):
#   บททำตามเป๊ะ — 13/15 ฉากขึ้นต้น "Same wide angle" · camN = มุมกว้างตั้งนิ่ง ทุกฉาก
#   แต่ประโยคเขียนว่า "a pair of male hands holds a blueprint **in front of the camera**"
#                    "hands are seen at the bottom of the frame hammering…"
#   ⇒ โมเดลตีความว่า "กว้างเดิม + มือทำงาน" = ถ่ายกว้างแต่เอามือมาไว้หน้ากล้อง = ดูเป็นโคลสอัพ
# 🔑 ต้นเหตุ: ค่าตั้งต้นของ "เห็นคนแค่ไหน" คือ **"เห็นแต่มือ ไม่เห็นหน้า"** ซึ่งแปลว่า *ต้องเห็นมือ*
#   ⇒ ขัดกับไทม์แลปส์โดยธรรมชาติ · คลิปแรกของพี่หมีที่กล้องนิ่งสวย ตั้งเป็น "ทีมช่างเบลอเคลื่อนไหวเร็ว"
#
# v66 (เชิงกลไกเหมือน v65): arc = ไทม์แลปส์ → ใช้โหมดคน "ทีมช่างเบลอเคลื่อนไหวเร็ว" เสมอ
#   ทั้ง 3 ชั้น (บท mnPlan · บอร์ด · วิดีโอ) ทับค่าที่ผู้ใช้เลือกไว้ — เพราะกล้องนิ่งกับมือหน้ากล้องอยู่ด้วยกันไม่ได้
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ARC = 'ไทม์แลปส์กล้องนิ่ง'
CREW = 'ทีมช่างเบลอเคลื่อนไหวเร็ว|AI เลือกนาย/นางแบบให้เหมาะกับสินค้า'
for t in ('charPlan', 'charBoard', 'charVideoEN'):
    assert CREW in c['lookups'][t], t
IS_TL = {'op': 'eq', 'a': '{item.arc}', 'b': ARC}
NOT_TL = {'op': 'not', 'a': IS_TL}

wrapped = 0
def walk(n):
    global wrapped
    if isinstance(n, dict):
        if n.get('op') == 'lookup' and n.get('table') in ('charPlan', 'charBoard', 'charVideoEN'):
            wrapped += 1
            fixed = dict(n); fixed['key'] = CREW          # ไทม์แลปส์ = ทีมช่างเบลอเสมอ
            return {'op': 'block', 'sep': '', 'parts': [
                {'when': NOT_TL, 'value': n},
                {'when': IS_TL, 'value': fixed},
            ]}
        return {k: walk(v) for k, v in n.items()}
    if isinstance(n, list):
        return [walk(x) for x in n]
    return n

for op in c['ops']:
    if op['id'] == 'mnPlan' or op['id'].startswith('mnBoard') or op['id'].startswith('mnVideo'):
        op['prompt'] = walk(op['prompt'])

assert wrapped >= 13, f'คาดห่อ lookup โหมดคนอย่างน้อย 13 จุด เจอ {wrapped}'
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'v66 ok · ห่อ lookup โหมดคน {wrapped} จุด (mnPlan + บอร์ด 6 + วิดีโอ 6)')
