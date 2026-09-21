#!/usr/bin/env python3
# showhow-v24b-ost-exclusive.py — โหมด "หัวเรื่องค้างทั้งคลิป" ต้องไม่ซ้อนกับบล็อก ON-SCREEN TEXT เดิม (2026-09-21)
# อาการ (จับได้จาก render-op ของจริง): ช่วง 1 ได้ ON-SCREEN TEXT **2 ชุด** — ชุดใหม่ "one fixed Thai title overlay only"
#   กับชุดเดิม "only the quoted Thai overlays below may appear" (when = svTextOn != ไม่มีข้อความ ซึ่งคลุมโหมดใหม่ด้วย)
#   ⇒ คำสั่งขัดกันเองในคำสั่งเดียว · แก้: กันโหมดใหม่ออกจากเงื่อนไขเดิม
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
NEW = 'หัวเรื่องค้างทั้งคลิป'
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)
ops = {o['id']: o for o in d['ops']}
op = ops['mnVideo']; hit = 0
for part in op['prompt']['parts']:
    if isinstance(part, dict) and part.get('op') == 'block':
        for q in part.get('parts', []):
            if isinstance(q, dict) and q.get('when') == 'values.svTextOn!=ไม่มีข้อความ' and 'ON-SCREEN TEXT' in str(q.get('value', '')):
                q['when'] = {'op': 'and', 'list': [{'op': 'not', 'a': {'op': 'eq', 'a': '{values.svTextOn}', 'b': 'ไม่มีข้อความ'}},
                                                   {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svTextOn}', 'b': NEW}}]}
                hit += 1
assert hit == 1, f'เจอบล็อก ON-SCREEN TEXT เดิมของ mnVideo {hit} จุด (คาด 1)'
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print('✓ v24b ·', os.path.getsize(P), 'bytes')
