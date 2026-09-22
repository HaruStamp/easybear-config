#!/usr/bin/env python3
# showhow v70 — ปิด end-frame chaining ชั่วคราว: Flow ปฏิเสธคำขอ frame-to-video (ต้องให้ starter ดู)
#
# หลักฐานแยกตัวแปรบนเครื่องจริง (2026-09-22 · engine 1.12.0 · บัญชีที่ 2):
#   mnVideo2 + startFrame → "Expected object response with media fields" **ล้ม 3/3 ครั้ง**
#   mnVideo2 ตัวเดิม เวลาเดียวกัน ปิด startFrame (เคลียร์ arc) → **สำเร็จทันทีครั้งแรก**
#   ⇒ ตัวแปรเดียวที่ต่างคือ startFrame · ไม่ใช่เครดิต ไม่ใช่ของชั่วคราว
#   (engine log ยืนยันว่าเข้าโหมดจริง: "ใช้โหมดต่อจากเฟรมเริ่มต้น — รูปอ้างอิง 3 ใบไม่ได้ถูกส่งไปด้วย")
#
# คงไว้: v68 ประตู "คลิปเสร็จ" ตรวจครบทุกช่วง (ดีกว่าเดิมไม่ว่าลำดับไหน) + ลำดับผลิต 1→6
#   ลำดับ 1→6 ผ่านของจริงแล้วในรอบนี้ (ช่วง 1 แล้วช่วง 2 ผลิตติดกันสำเร็จ)
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
n = 0
for op in c['ops']:
    if op['id'].startswith('mnVideo') and 'startFrame' in op:
        del op['startFrame']
        op.pop('tailTrim', None)
        n += 1
assert n == 5, f'คาด 5 op เจอ {n}'
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'v70 ok · ปิด startFrame {n} op · คง v68 (ประตูครบทุกช่วง) และลำดับ 1→6 ไว้')
