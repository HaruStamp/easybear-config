#!/usr/bin/env python3
# showhow-v11-board-order.py — สลับลำดับวาดบอร์ดเป็น 1 → 6 แล้วให้ทุกช่วงอ้างอิง "บอร์ดช่วงที่ 1" (พี่หมีสั่ง 2026-09-20)
# ปัญหา: บอร์ดเดิมวาดจากช่วงท้ายมาหน้า ⇒ ตอนวาดฉากปิด ภาพฉากเปิดยังไม่เกิด ⇒ กฎ "ฉากปิดมุมเดียวกับฉากเปิด" ทำไม่ได้เลยในทางกลไก
# ปลอดภัยไหม: เงื่อนไข "คลิปเสร็จ" ของทั้งแอปนับจาก slots.video (ยังเรียง 6→1 เหมือนเดิม) · การ์ดสรุปหน้าผลิตเช็ค video ครบคู่กับ board ครบ ⇒ สลับเฉพาะบอร์ดไม่กระทบ
# refs ใหม่ของ mnBoardK (K≥2): บอร์ดช่วง 1 (หมุดมุมเปิด) + บอร์ดช่วง K-1 (ช่วงก่อนหน้า) — รวม ≤10 refs เท่าเดิม
# ลำดับรัน: base → showhow-v9-board-collage.py → showhow-v10-endshot.py → ไฟล์นี้
import json, os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'showhow-dev.json')
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)

WHY = ('★บอร์ดเรียง 1→6 ตั้งใจ — ช่วงแรกต้องเสร็จก่อน เพราะฉากปิดของคลิปต้องลอกมุมกล้องจากฉากเปิด (บอร์ดช่วง 1) '
       'ส่วนวิดีโอยังเรียง 6→1 เหมือนเดิม ห้ามสลับ เพราะทั้งแอปตัดสิน "คลิปเสร็จหรือยัง" จาก slots.video ของช่วงแรก')

# ── ① สลับลำดับ stage ของบอร์ด ──
stages = d['stages']
board_idx = [i for i, s in enumerate(stages) if str(s.get('op', '')).startswith('mnBoard')]
assert board_idx == list(range(board_idx[0], board_idx[0] + 6)), board_idx
ordered = ['mnBoard'] + [f'mnBoard{k}' for k in range(2, 7)]
old = [stages[i]['op'] for i in board_idx]
for pos, op in zip(board_idx, ordered):
    stages[pos] = {'op': op}
stages[board_idx[0]]['__why'] = WHY
print('stage บอร์ด:', old, '→', ordered)

# ── ② เขียน refs ของบอร์ดใหม่ ──
def board_ref(slot, when=None):
    r = {'from': 'tasks', 'by': '{item.id}', 'slot': slot}
    if when: r['when'] = when
    return r

def find_ops(node):
    if isinstance(node, dict):
        if str(node.get('id', '')).startswith('mnBoard') and node.get('type') == 'image': yield node
        for v in node.values(): yield from find_ops(v)
    elif isinstance(node, list):
        for v in node: yield from find_ops(v)

n = 0
for op in find_ops(d):
    k = 1 if op['id'] == 'mnBoard' else int(op['id'][len('mnBoard'):])
    also = [a for a in op['refs']['also'] if not (a.get('from') == 'tasks' and str(a.get('slot', '')).startswith('board'))]
    if k >= 2:
        # 🔑 v16: บอร์ดช่วง 1 ต้องเป็น "รูปอ้างอิงใบแรก" ของช่วง 2+ — โมเดลภาพให้น้ำหนักรูปแรกมากสุด
        #     เดิมบอร์ดอยู่ท้ายสุด (หลังรูปสินค้า/ห้อง) ⇒ ช่วงท้ายที่ฉากสะอาดหมดแล้วหลุดไปวาดห้องสต็อก
        prev = [board_ref(f'board{k - 1}')] if k >= 3 else []
        main_old = {'from': op['refs'].get('from'), 'by': op['refs'].get('by'), 'slot': op['refs']['slot']}   # products/image เดิม ห้ามหาย
        op['refs'] = {'op': 'lookupRefs', 'from': 'tasks', 'by': '{item.id}', 'slot': 'board',
                      'also': prev + [main_old] + [dict(a) for a in also]}
    else:
        op['refs']['also'] = also
    n += 1
    print(f"  {op['id']}: board refs =", [a['slot'] for a in also if a.get('from') == 'tasks'] or '—', '· refs รวม', 1 + len(also))

open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print(f'✓ v11 board-order · แก้ {n} op ·', os.path.getsize(P), 'bytes')
