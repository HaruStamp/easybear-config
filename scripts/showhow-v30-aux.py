#!/usr/bin/env python3
# showhow-v30-aux.py — ติดธง `aux: true` ให้ op แปล 31 ตัว (engine v1.9.0 · starter ใส่ให้ตามที่ minimal ขอ)
# ทำไม: `itemRunCounts` นับทุก op ที่ over ตรง collection ⇒ op แปลของเราทำให้ตัวเลขใน **โมดัล "มีงานผลิตค้างอยู่"** ไม่มีวันขึ้นว่าเสร็จ
#       (ไล่ซอร์สแล้ว: ผู้เรียก itemRunCounts มีที่เดียวคือ app-render.tsx ⇒ กระทบแค่โมดัลนั้น · computeProgress เดินจาก stages จึงไม่กระทบ)
# `aux: true` = "op เสริมที่ผู้ใช้กดเอง" ⇒ engine ข้ามตอนนับงานเสร็จ/ความคืบหน้า
# 🪤 engine < v1.9.0 อ่านธงนี้ไม่ออก — ใส่ไว้ก่อนได้ (ไม่พัง) แต่จะมีผลจริงเมื่อ remix v1.9.0 แล้วเท่านั้น
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)
tr = [o for o in d['ops'] if o['id'] == 'mnTrans' or o['id'].startswith('mnTrA')]
assert len(tr) == 31, f'op แปลต้องมี 31 ตัว เจอ {len(tr)}'
if all(o.get('aux') is True for o in tr): sys.exit('⏭ ติดธง aux แล้ว ข้าม')
for o in tr: o['aux'] = True
# ยาม: ห้ามติด aux ให้ op ของสายผลิตจริง (ถ้าติด = งานหายจากตัวนับ)
prod = [o for o in d['ops'] if o.get('aux') and not (o['id'] == 'mnTrans' or o['id'].startswith('mnTrA'))]
assert not prod, f'aux ไปติด op สายผลิต: {[o["id"] for o in prod]}'
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print(f'✓ v30 · ติด aux ให้ {len(tr)} op (mnTrans + mnTrA1..30) ·', os.path.getsize(P), 'bytes')
