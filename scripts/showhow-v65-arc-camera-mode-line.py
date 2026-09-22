#!/usr/bin/env python3
# showhow v65 — ให้เส้นทาง arc=ไทม์แลปส์ ได้บรรทัด CAMERA MODE เหมือนเส้นทาง svCamMode (และแลกที่ให้พอดีเพดาน)
#
# ทำไม: ไล่แก้ด้วย "คำสั่งในบท" มา 4 รอบ (v61-v64) แล้วยังล็อกกล้องไม่ได้ —
#   camN = กว้างนิ่ง 15/15 · Camera: static locked-off shot ครบทุกฉาก · แต่วิดีโอยังโคลสอัพ
#   และ LLM ยังเขียน "Close up of a hand…" ทั้งที่ห้ามไว้ชัด (v63/v64) ⇒ **สั่งอย่างเดียวไม่พอ**
# 🔑 หลักฐานว่าอะไรได้ผลจริง: คลิปแรกของพี่หมีที่ตั้ง svCamMode=ตั้งนิ่ง **กล้องนิ่งทั้งคลิป**
#   ต่างกันตรงเดียวคือเส้นทางนั้นมีบรรทัด `CAMERA MODE:` อยู่ใน prompt วิดีโอ
#
# v65 (เชิงกลไก ไม่ใช่เชิงขอร้อง):
#   ① arc = ไทม์แลปส์ → บรรทัด CAMERA MODE เป็นกล้องนิ่งเสมอ (ทับค่ามุมกล้องที่ผู้ใช้เลือก)
#   ② เมื่ออยู่ในโหมดนั้น **ตัดคำสั่งกล้องรายฉาก ("Camera: …") ออก** เพราะซ้ำซ้อนกับบรรทัดเดียวข้างบน
#      ⇒ ได้ที่คืนมามากกว่าที่ใช้ไป (5 ฉาก × ~47 ตัวอักษร) จึงไม่ทะลุเพดาน 3,900
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ARC = 'ไทม์แลปส์กล้องนิ่ง'
CAMKEY = 'ตั้งนิ่งเห็นทั้งพื้นที่'
# 🔴 พี่หมีเคาะ: "ถ้า timelapse กล้องต้องนิ่ง" — ไม่มีเงื่อนไข ไม่ขึ้นกับว่าผู้ใช้ตั้งมุมกล้องอะไรไว้
#    (เดิมผมกั้นด้วย svCamMode='' ซึ่งยังเปิดช่องให้เลือกไทม์แลปส์ + กล้องตามคนแบบ vlog = ขัดกันเอง)
WHEN_TL = {'op': 'eq', 'a': '{item.arc}', 'b': ARC}
WHEN_NOT_TL = {'op': 'not', 'a': WHEN_TL}

added = cut = 0
for op in c['ops']:
    if not op['id'].startswith('mnVideo'):
        continue

    def walk(n):
        global added, cut
        if isinstance(n, dict):
            # ① บล็อกของ camVideoEN — เติมทางที่สอง
            if n.get('op') == 'block' and len(n.get('parts', [])) == 1:
                p0 = n['parts'][0]
                v = p0.get('value')
                if p0.get('when') == 'values.svCamMode!=' and isinstance(v, dict) and v.get('table') == 'camVideoEN':
                    p0['when'] = {'op': 'and', 'a': {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svCamMode}', 'b': ''}},
                                  'b': WHEN_NOT_TL}          # เลือกมุมกล้องเอง **และไม่ใช่ไทม์แลปส์**
                    n['parts'].append({'when': WHEN_TL,
                                       'value': {'op': 'lookup', 'table': 'camVideoEN', 'key': CAMKEY, 'fallback': ''}})
                    added += 1
                    return n
            # ② คำสั่งกล้องรายฉาก — ปิดเมื่ออยู่โหมดไทม์แลปส์
            if n.get('op') == 'concat' and n.get('parts') and n['parts'][0] == 'Camera: ':
                cut += 1
                return {'op': 'block', 'sep': '', 'parts': [{'when': WHEN_NOT_TL, 'value': n}]}
            return {k: walk(v) for k, v in n.items()}
        if isinstance(n, list):
            return [walk(x) for x in n]
        return n

    op['prompt'] = walk(op['prompt'])

assert added == 6, f'คาดเติม CAMERA MODE 6 op เจอ {added}'
assert cut == 30, f'คาดห่อคำสั่งกล้องรายฉาก 30 จุด เจอ {cut}'
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'v65 ok · เติมบรรทัด CAMERA MODE {added} op · ห่อคำสั่งกล้องรายฉาก {cut} จุด')
