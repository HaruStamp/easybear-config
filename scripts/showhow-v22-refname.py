#!/usr/bin/env python3
# showhow-v22-refname.py — บอกให้ชัดว่า "รูปใบไหนคือบอร์ดช่วงก่อนหน้า" แยกตามช่วง (2026-09-21)
# ราก: กติกาต่อเนื่องเขียนเหมือนกันทุกช่วงว่า "รูปแรก ๆ ที่แนบ" — คลุมเครือ โดยเฉพาะช่วง 2 ที่แนบบอร์ดมาใบเดียว
#      แล้วตามด้วยรูปสินค้า 2 ใบ ⇒ โมเดลไม่รู้ว่าต้องยึดใบไหน · เคสไม่มีรูปห้อง (LOCATION LOCK ไม่โผล่) กติกานี้เป็นหลักยึดเดียวที่มี
#      อาการจริง: ช่วง 2 เปลี่ยนกระเบื้องผนังเป็นลายอิฐ เปลี่ยนรุ่นสุขภัณฑ์ แล้วช่วงถัดไปลอกผิดต่อ (เจอซ้ำหลายรอบ)
# แก้: ช่วง 2 → "**รูปแรกที่แนบ = บอร์ดช่วงที่ 1**" · ช่วง 3-6 → "**รูป 2 ใบแรกที่แนบ = บอร์ดช่วงที่ 1 และช่วงก่อนหน้า**"
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
OLD = 'บอร์ดช่วงก่อนหน้าที่แนบมา (**รูปแรก ๆ ที่แนบ**):'
NEW2 = 'บอร์ดช่วงก่อนหน้าที่แนบมา (**รูปแรกที่แนบ = บอร์ดช่วงที่ 1**):'
NEWK = 'บอร์ดช่วงก่อนหน้าที่แนบมา (**รูป 2 ใบแรกที่แนบ = บอร์ดช่วงที่ 1 และช่วงก่อนหน้า**):'
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)
def find_ops(n):
    if isinstance(n, dict):
        if str(n.get('id','')).startswith('mnBoard') and n.get('type') == 'image': yield n
        for v in n.values(): yield from find_ops(v)
    elif isinstance(n, list):
        for v in n: yield from find_ops(v)
hit = 0
for op in find_ops(d):
    k = 1 if op['id'] == 'mnBoard' else int(op['id'][len('mnBoard'):])
    if k == 1: continue
    s = json.dumps(op, ensure_ascii=False)
    if OLD not in s: sys.exit(f'✗ {op["id"]} ไม่เจอข้อความเดิม')
    op.clear(); op.update(json.loads(s.replace(OLD, NEW2 if k == 2 else NEWK))); hit += 1
assert hit == 5, hit
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
G = os.path.join(HERE, 'showhow-v9-board-collage.py'); g = open(G, encoding='utf-8').read()
if OLD in g:
    open(G, 'w', encoding='utf-8').write(g.replace(OLD, 'บอร์ดช่วงก่อนหน้าที่แนบมา (**' + "'รูปแรกที่แนบ = บอร์ดช่วงที่ 1' if k == 2 else 'รูป 2 ใบแรกที่แนบ = บอร์ดช่วงที่ 1 และช่วงก่อนหน้า'" + '**):'))
    print('🪤 generator v9 ยังเป็นข้อความเดียวทุกช่วง — แก้ในไฟล์นั้นด้วยมือถ้าจะสร้างใหม่จากฐาน')
print(f'✓ v22 · แก้ {hit} op ·', os.path.getsize(P), 'bytes')
