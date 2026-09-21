#!/usr/bin/env python3
# showhow-v31-autoloop-board-order.py — 🔴 บั๊กใหญ่: ลำดับวาดบอร์ดใน "ปุ่มเริ่มผลิต" ยังเป็น 6→1 (พบ 2026-09-22)
# เจอยังไง: ยิงผลิตคลิป 60 วิ ของจริงครั้งแรกผ่าน `run` (เส้นเดียวกับปุ่มของผู้ใช้) แล้ว log ขึ้น
#          "กำลังวาดสตอรีบอร์ดช่วงที่ 6" เป็นใบแรก ⇒ ตรงข้ามกับที่ v11 ตั้งใจ
# ราก: v11 (2026-09-20) สลับลำดับใน `stages` อย่างเดียว — แต่ **ปุ่มเริ่มผลิตเดิน `auto.productLoop.gens`** ซึ่งยังเป็นของเดิม
#      ⇒ งานทดสอบทั้งหมดของเราเรียก `run-op` ทีละช่วงเอง (1→6) จึงไม่เคยเห็นอาการ · ผู้ใช้จริงกดปุ่มเดียว = ได้ลำดับผิดทุกครั้ง
# ผลเสีย: ฉากปิดลอกมุมจากบอร์ดช่วง 1 ไม่ได้ (ยังไม่เกิด) · บอร์ดช่วง K อ้างบอร์ดช่วงก่อนหน้าที่ยังไม่มี ⇒ ความต่อเนื่องพัง
# แก้: เรียง gens ของบอร์ดเป็น 1→6 · **วิดีโอคงเดิม 6→1** (ทั้งแอปตัดสิน "คลิปเสร็จ" จาก slots.video ของช่วงแรก)
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)
gens = d['auto']['productLoop']['gens']
boards = [g for g in gens if g.startswith('mnBoard')]
videos = [g for g in gens if g.startswith('mnVideo')]
others = [g for g in gens if not (g.startswith('mnBoard') or g.startswith('mnVideo'))]
want_b = ['mnBoard'] + [f'mnBoard{k}' for k in range(2, 7)]
want_v = [f'mnVideo{k}' for k in range(6, 1, -1)] + ['mnVideo']
assert sorted(boards) == sorted(want_b) and sorted(videos) == sorted(want_v), (boards, videos)
if boards == want_b: sys.exit('⏭ ลำดับบอร์ดถูกอยู่แล้ว ข้าม')
print('  บอร์ดเดิม:', boards, '→', want_b)
print('  วิดีโอ  :', videos, '(คงเดิม)')
d['auto']['productLoop']['gens'] = others + want_b + want_v
# ยาม: ลำดับใน stages กับ gens ต้องตรงกันเรื่องบอร์ด (กันพลาดซ้ำ)
st = [s.get('op') for s in d['stages'] if str(s.get('op','')).startswith('mnBoard')]
assert st == want_b, f'stages ยังเป็น {st}'
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print('✓ v31 ·', os.path.getsize(P), 'bytes')
