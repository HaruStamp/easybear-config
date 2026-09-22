#!/usr/bin/env python3
# showhow v71 — เปิด end-frame chaining กลับ (ที่ล้มคือ transient ไม่ใช่กลไก) + ตั้ง resolution 720p ทุก video op
#
# 🪤 บทเรียนของผมเอง: v70 ปิดกลไกนี้เพราะ "แยกตัวแปรพิสูจน์แล้ว" ซึ่ง **ผิด**
#   ที่ทำจริง: เทียบ "มี startFrame → ล้ม 3 ครั้ง" กับ "ไม่มี startFrame → ผ่าน 1 ครั้ง"
#   ที่ขาด: **ไม่เคยยิงชุดที่มี startFrame ซ้ำอีกเลย** ⇒ ช่วงที่ Flow ล่มชั่วคราวอธิบายได้ทั้งหมด
#   พอยิงกลุ่มควบคุม (zzE = ชุดที่ล้มเดิมเป๊ะ) → **ผ่าน** · zzA/zzC ก็ผ่าน ⇒ กลไกไม่เคยพัง
#   📌 กฎ: เทียบ A กับ B ในสภาพแวดล้อมที่ล้มเป็นช่วง ๆ ต้องยิง A ซ้ำหลังเจอ B ผ่าน ไม่งั้นแยกไม่ออกจาก "จังหวะ"
#
# + resolution: engine ส่งคีย์นี้เฉพาะเมื่อ config ตั้ง · ของเราไม่เคยตั้ง = พึ่ง default ของ Flow
#   วัดคลิปจริง 3 ตัววันนี้ได้ 720×1280 (ไม่ใช่ 360p ที่ hardsell เคยเจอ) — แต่ตั้งให้ชัดกัน default เปลี่ยนเงียบ
import json, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ARC = 'ไทม์แลปส์กล้องนิ่ง'
IS_TL = {'op': 'eq', 'a': '{item.arc}', 'b': ARC}
c['ops'] = [o for o in c['ops'] if not o['id'].startswith('zz')]     # ลบ op ทดสอบ
chain = res = 0
for op in c['ops']:
    if not op['id'].startswith('mnVideo'):
        continue
    if op.get('resolution') != '720p':
        op['resolution'] = '720p'; res += 1
    k = int(op['id'].replace('mnVideo', '') or '1')
    if k < 2:
        continue
    prev = 'video' if k == 2 else f'video{k-1}'
    op['startFrame'] = {'op': 'block', 'sep': '', 'parts': [{'when': IS_TL, 'value': '{item.slots.%s}' % prev}]}
    op['tailTrim'] = 1.0      # zzC ผ่านที่ 1.0 · ถอยจากท้ายคลิปมากกว่า 0.1 = เฟรมมีเนื้อแน่นอนกว่า
    chain += 1
assert chain == 5 and res == 6, (chain, res)
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'v71 ok · เปิด startFrame {chain} op (tailTrim 1.0) · ตั้ง resolution 720p {res} op · ลบ op ทดสอบแล้ว')
