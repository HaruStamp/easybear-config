#!/usr/bin/env python3
"""showhow v51 — ตัดแผ่นบอร์ดที่ "ไม่มีข้อมูลความต่อเนื่องให้" ออกจาก ref ของวิดีโอ

หลักฐาน (พี่หมีทดสอบ 40 วิ · คลิป "รีโนเวทสวนหน้าบ้าน" · config v50 · engine 1.12.0):
  วินาทีที่ ~9 (ท้ายช่วง 1) **วิดีโอวาดแผ่นบอร์ดออกมาทั้งแผ่น** — 3 ช่องซ้อนกันพร้อมวงกลมเลข 2 · 5 · 11
  เลข 2,5 = ช่องของบอร์ดช่วง 1 · เลข 11 = ช่องของบอร์ดช่วง 3
  ⇒ **ตรงกับจำนวนแผ่นที่เราแนบให้ op นั้นพอดี** (mnVideo ที่ 40 วิ แนบ board + board2 + board3)
  ⇒ โมเดลเอาแผ่นที่แนบมาต่อกันเป็นภาพเดียว ไม่ใช่ "เผลอวาดเลข" แบบที่เจอเมื่อวาน (v44/v45)

🔑 ทำไมกฎห้ามอย่างเดียวไม่พอ: หัว prompt สั่งห้าม `no grid, split-screen, panels or borders` อยู่แล้ว
   และ v45 สั่ง `Never copy a sheet; its markings are annotation.` — **ทั้งคู่ถูกเมินในเคสนี้**
   ⇒ ลดโอกาสด้วยการ **ไม่ยื่นของที่ไม่จำเป็นให้โมเดลตั้งแต่แรก** ได้ผลกว่าการเติมคำสั่งห้าม

ตัดเฉพาะแผ่นที่ **ไม่มีข้อมูลความต่อเนื่องให้ช่วงนั้นเลย** (ปลอดภัยโดยนิยาม):
  mnVideo  (ช่วง 1)  ตัด board2 + board3  ← ช่วงแรกเป็นคนตั้งต้นห้องเอง ไม่มีอะไรให้สืบทอด
  mnVideo2 (ช่วง 2)  ตัด board3           ← ช่วง 3 เป็น "อนาคต" ของช่วง 2
  mnVideo3 (ช่วง 3)  คงไว้ (board = หมุด · board2 = ช่วงก่อนหน้า)
  mnVideo4/5/6       คงไว้ (board = หมุด · board K-1 = ช่วงก่อนหน้า)
⇒ ช่วง 1 เหลือแผ่นเดียว (ของตัวเอง) · ช่วง 2 เหลือ 2 แผ่น · ที่เหลือเท่าเดิม
🪤 ไม่แตะ mnBoard* — บอร์ดต้องเห็นบอร์ดช่วงก่อนหน้าเพื่อคุมห้อง (คนละเรื่องกับวิดีโอ)
"""
import json, pathlib

P = pathlib.Path(__file__).resolve().parent.parent / 'showhow-dev.json'
d = json.loads(P.read_text(encoding='utf-8'))
DROP = {'mnVideo': {'board2', 'board3'}, 'mnVideo2': {'board3'}}
n = 0
for op in d['ops']:
    drop = DROP.get(op['id'])
    if not drop: continue
    also = op['refs']['also']
    before = len(also)
    op['refs']['also'] = [a for a in also if not (a.get('from') == 'tasks' and a.get('slot') in drop)]
    n += before - len(op['refs']['also'])

assert n == 3, f'ตัดได้ {n} รายการ (คาด 3) — โครงเปลี่ยน หยุด'
for op in d['ops']:
    if op['id'].startswith('mnVideo'):
        boards = [a['slot'] for a in op['refs']['also'] if a.get('from') == 'tasks']
        k = 1 if op['id'] == 'mnVideo' else int(op['id'][-1])
        want = [] if k == 1 else (['board'] if k == 2 else ['board', f'board{k-1}'])
        assert boards == want, f'{op["id"]}: แนบบอร์ด {boards} (คาด {want})'
        assert op['refs']['slot'] == ('board' if k == 1 else f'board{k}'), f'{op["id"]}: บอร์ดของตัวเองเปลี่ยน'

P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'ตัดแผ่นบอร์ดออก {n} รายการ · ช่วง 1 เหลือแผ่นเดียว · ช่วง 2 เหลือ 2 แผ่น')
