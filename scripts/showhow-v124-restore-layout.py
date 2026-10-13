#!/usr/bin/env python3
"""showhow-v124 — ถอยคำสั่งเลย์เอาต์บอร์ดกลับเป็นของ v122 + ใส่ "บรรทัดเดียว" ในข้อความวิดีโอกลับ (ทดสอบ v123 จริง 2026-10-13)

ผลผลิตจริง v123 (docs/qa/2026-10-13-pet-3d-v123): บอร์ดช่วง 2 ได้ 5 ช่องแนวนอนเรียงคอลัมน์เดียว (ไม่ใช่ตาราง 2 คอลัมน์)
  = บทเรียน v8.4 ซ้ำ "ห้ามบีบคำสั่งเลย์เอาต์" (ที่ตัดไป: สูงกว่ากว้าง ราว 3:4 · ลงแถวถัดไป · ไม่มีช่องว่างสีขาว · มุมฉาก · ห้ามเริ่มนับใหม่)
  · ซับขึ้น 2 บรรทัดหลายฉาก — v123 ตัด "one line only — no second line" ออก
ที่เหลือของ v123 (ตัดคำซ้ำ/ภาษาง่าย) คงไว้
ใช้: python3 scripts/showhow-v124-restore-layout.py  (รันบน v123 · อ่านเลย์เอาต์เดิมจาก git show 23f13d5^.. = v122)
"""
import json, subprocess
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
old = json.loads(subprocess.check_output(['git', 'show', 'HEAD~1:showhow-dev.json']))   # v122
OLD = {o['id']: o for o in old['ops']}
n = 0
for o in c['ops']:
    if o['id'].startswith('mnBoard'):
        prev = OLD[o['id']]['prompt']['parts'][2]
        assert isinstance(prev, str) and 'บังคับเลย์เอาต์' in prev, o['id']
        cur = o['prompt']['parts'][2]
        assert isinstance(cur, str) and cur.startswith(' (บรรทัดนี้ห้ามพิมพ์ลงภาพ)\nเลย์เอาต์:'), o['id']
        o['prompt']['parts'][2] = prev; n += 1
assert n == 6
S = json.dumps(c, ensure_ascii=False)
A = 'ON-SCREEN TEXT: show only the quoted Thai lines below, one line each, style'
B = 'ON-SCREEN TEXT: show only the quoted Thai lines below, each on one line only — no second line, style'
C = 'ON-SCREEN TEXT: one fixed Thai title, one line, style'
D = 'ON-SCREEN TEXT: one fixed Thai title, one line only — no second line, style'
assert S.count(A) == 6 and S.count(C) == 6, (S.count(A), S.count(C))
S = S.replace(A, B).replace(C, D)
c = json.loads(S)
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✅ v124: เลย์เอาต์บอร์ดกลับเป็นของเดิม 6 op · ข้อความวิดีโอ บรรทัดเดียว 12 จุด')
