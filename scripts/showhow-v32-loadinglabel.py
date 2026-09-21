#!/usr/bin/env python3
# showhow-v32-loadinglabel.py — ใส่ `loadingLabel` ให้ปุ่ม retry ทุกตัว (engine v1.9.0 · มาตรฐานกลางของ minimal)
# ทำไม: v1.9.0 ให้ retry-button มี spinner ตอน item กำลัง gen และอ่าน `el.loadingLabel` มาทับข้อความปุ่ม
#       ⇒ ผู้ใช้เห็นว่า "กำลังทำอะไรอยู่" ระหว่างรอ (ก่อนหน้านี้ปุ่มแค่จางลงเฉย ๆ)
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)
def nodes(n):
    if isinstance(n, dict):
        yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n, list):
        for v in n: yield from nodes(v)
board = [x for x in nodes(d) if isinstance(x, dict) and 'sh-board-retry-one' in str(x.get('className', ''))]
trans = [x for x in nodes(d) if isinstance(x, dict) and 'sh-tr-inline' in str(x.get('className', ''))]
assert len(board) == 12 and len(trans) == 30, (len(board), len(trans))
if all(x.get('loadingLabel') for x in board + trans): sys.exit('⏭ มี loadingLabel แล้ว ข้าม')
for x in board: x['loadingLabel'] = 'กำลังวาดใหม่…'
for x in trans: x['loadingLabel'] = 'กำลังแปล…'
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print(f'✓ v32 · loadingLabel · ปุ่มบอร์ด {len(board)} · ปุ่มแปล {len(trans)} ·', os.path.getsize(P), 'bytes')
