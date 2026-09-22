#!/usr/bin/env python3
# showhow v67 — ไทม์แลปส์ต้องเป็น "ช็อตเดียวยาว ไม่มีรอยตัด" (long take) ตามที่พี่หมีระบุ
#
# ที่ผมแก้มาทั้งคืน (v61-v66) แก้แค่ "กล้องนิ่ง" — แต่ prompt ยังสั่งเป็น **5 ฉากแยกกัน**
#   "Scene 1 (0-2s): … Scene 2 (2-4s): …" ⇒ โมเดลตัดภาพทุก 2 วินาทีโดยธรรมชาติ
#   ⇒ ได้ "กล้องนิ่งแต่ตัดสลับ" ไม่ใช่ไทม์แลปส์แบบถ่ายยาวช็อตเดียว
#
# v67: โหมดไทม์แลปส์ เปลี่ยน **โครงของ prompt** ไม่ใช่ถ้อยคำ
#   - ไม่มีป้าย "Scene N (a-b s):" และไม่มีคำสั่งกล้องรายฉาก
#   - เขียนเป็นหัวข้อเดียว "ONE CONTINUOUS LOCKED TAKE" แล้วไล่การเปลี่ยนแปลงเป็นลำดับในเฟรมเดียว
#   - โหมดอื่นไม่ขยับสักไบต์ (ทุกจุดห่อด้วย when)
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ARC = 'ไทม์แลปส์กล้องนิ่ง'
IS_TL = {'op': 'eq', 'a': '{item.arc}', 'b': ARC}
NOT_TL = {'op': 'not', 'a': IS_TL}
HEAD = ('\n\nONE CONTINUOUS LOCKED TAKE — the entire 10 s is a single unbroken shot from one fixed camera: '
        'no cuts, no transitions, no scene changes, the framing never moves. '
        'Inside that one frame the work advances continuously in this order, each change growing out of the previous one:')

done = 0
for op in c['ops']:
    if not op['id'].startswith('mnVideo'):
        continue
    parts = op['prompt']['parts']
    idx = [i for i, p in enumerate(parts) if isinstance(p, dict) and p.get('op') == 'concat'
           and 'sceneEN' in json.dumps(p, ensure_ascii=False)]
    assert len(idx) == 5, f'{op["id"]}: คาด 5 ฉาก เจอ {len(idx)}'
    # เลขฉากแรกของช่วงนี้ (mnVideo=1 · mnVideo2=6 · …)
    k = int(op['id'].replace('mnVideo', '') or '1')
    first = (k - 1) * 5 + 1
    for j, i in enumerate(idx):
        orig = parts[i]
        n = first + j
        tl = {'op': 'concat', 'parts': [('\n— ' if j else '\n'), '{item.s%den}' % n]}   # ไม่มีป้ายฉาก ไม่มีเวลา ไม่มีกล้อง
        parts[i] = {'op': 'block', 'sep': '', 'parts': [{'when': NOT_TL, 'value': orig},
                                                        {'when': IS_TL, 'value': tl}]}
    # หัวข้อ long take — แทรกก่อนฉากแรก
    parts.insert(idx[0], {'op': 'block', 'sep': '', 'parts': [{'when': IS_TL, 'value': HEAD}]})
    done += 1

assert done == 6, done
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'v67 ok · {done} op วิดีโอ · โหมดไทม์แลปส์ = ช็อตเดียวไม่มีป้ายฉาก · โหมดอื่นไม่ขยับ')
