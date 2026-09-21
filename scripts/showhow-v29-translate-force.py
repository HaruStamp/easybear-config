#!/usr/bin/env python3
# showhow-v29-translate-force.py — ปุ่มแปลต้องกดซ้ำได้ (ทีม minimal เจอกับพี่หมี 2026-09-21)
# อาการ: กดปุ่มแปลครั้งที่ 2 ไม่มีอะไรเกิดขึ้น (ปุ่ม disable แวบเดียวเหมือนทำงาน)
# ราก (engine-run.ts:122): `gen-phase` → genPhase = **ไม่ force** ⇒ llm ที่มี out ใน data แล้ว = ข้าม · transform ที่มี __tdone แล้ว = ข้าม
#       ⇒ แก้บทไทยใหม่แล้วกดแปลซ้ำ ได้คำแปลเดิม (หรือไม่ได้อะไรเลย)
# แก้: เปลี่ยนเป็น `retry-button` + `chain:[mnTrans, mnTrA{N}]` + `op:'mnTrA{N}'` ⇒ UI เรียก chainItem(el, item, **true**) = force
#      และถอด `when` ที่ซ่อนปุ่มตอนรันออก — retry-button disable ราย item ให้เองอยู่แล้ว
# 🪤 บน engine v1.7.0 bridge ยังส่งปุ่มที่มี chain เข้า genPhase (ไม่ force) ⇒ **ทดสอบผ่าน eb_ui ไม่ได้จนกว่าจะ remix v1.8.0**
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
MARK = 'sh-tr-inline'; N = 30
raw = open(P, encoding='utf-8').read(); cfg = json.loads(raw)
def nodes(n):
    if isinstance(n, dict):
        yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n, list):
        for v in n: yield from nodes(v)
btns = [x for x in nodes(cfg) if isinstance(x, dict) and MARK in str(x.get('className', ''))]
assert len(btns) == N, f'เจอปุ่มแปล {len(btns)} ตัว (คาด {N}) — ต้องรัน v28 ก่อน'
if all(b.get('el') == 'retry-button' for b in btns): sys.exit('⏭ เป็น retry-button อยู่แล้ว ข้าม')
for b in btns:
    scene = int(re.fullmatch(r'mnTrA(\d+)', b['ops'][1]).group(1))
    b['el'] = 'retry-button'
    b['chain'] = b.pop('ops')                 # chain = [mnTrans, mnTrA{N}] (ลำดับเดิม)
    b['op'] = f'mnTrA{scene}'                 # op = ตัวสุดท้ายของสาย (เกณฑ์ media/สถานะของ engine อ่านตัวนี้)
    b.pop('when', None)                       # retry-button disable ราย item ให้เอง
after = [x for x in nodes(cfg) if isinstance(x, dict) and MARK in str(x.get('className', ''))]
assert all(x.get('el') == 'retry-button' and x.get('chain') and x.get('op') and 'when' not in x for x in after), 'แปลงปุ่มไม่ครบ'
assert all(x['chain'][0] == 'mnTrans' for x in after), 'ลำดับ chain เพี้ยน'
open(P, 'w', encoding='utf-8').write(json.dumps(cfg, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print(f'✓ v29 · เปลี่ยนปุ่มแปล {len(after)} ตัวเป็น retry-button (force) ·', os.path.getsize(P), 'bytes')
