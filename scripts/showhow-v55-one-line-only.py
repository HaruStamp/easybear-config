#!/usr/bin/env python3
# showhow v55 — ห้ามโมเดล "แต่งบรรทัดที่ 2 ขึ้นมาเอง" บนคลิป
#
# อาการจริง (คลิปขัดห้องน้ำ 30 วิ · 2026-09-22): ov1 = "ขัดหินปูนห้องน้ำ" 16 ตัวอักษร บรรทัดเดียว
#   แต่วิดีโอพิมพ์ 2 บรรทัด: **"ขัดหืวย์"** (คำมั่ว ไม่มีในบท) อยู่บรรทัดบน แล้วตามด้วยหัวเรื่องจริง
# ราก: กฎเดิมเขียนว่า "never repeat the same words on a second line" = ห้ามเฉพาะ **คำเดิมซ้ำ**
#      ⇒ คำที่โมเดลแต่งขึ้นใหม่ไม่เข้าข่าย · v25 เคยแก้เคส "พิมพ์ซ้ำ 2 บรรทัด" จึงเขียนไว้แบบนั้น
# แก้: เปลี่ยนเป็น "one line only — no second line, no extra or invented words"
#      = ห้ามทั้งคำซ้ำและคำที่ไม่ได้อยู่ในบท · คุมความยาวให้ไม่ยาวกว่าเดิม (วิดีโอเหลือ headroom แค่ 17 ตัวอักษร)
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
raw = open(P, encoding='utf-8').read()
c = json.loads(raw)

PAIRS = [
    # (ของเดิม, ของใหม่, จำนวนที่ต้องเจอ)
    ('rendered once only, never repeat the same words on a second line',
     'one line only — no second line, no extra or invented words', 6),
    ('each rendered once only, never repeated on a second line',
     'each on one line only — no second line or invented words', 6),
]
ops = json.dumps(c['ops'], ensure_ascii=False)
for old, new, n in PAIRS:
    got = ops.count(old)
    assert got == n, f'คาด {n} จุด เจอ {got} · "{old[:40]}…"'
    assert new not in ops, 'รันซ้ำ'
    ops = ops.replace(old, new)
c['ops'] = json.loads(ops)

# ต้องไม่แตะอย่างอื่นนอก ops
before = json.loads(raw)
for k in before:
    if k != 'ops':
        assert json.dumps(before[k], ensure_ascii=False) == json.dumps(c[k], ensure_ascii=False), f'v55 แตะ {k} โดยไม่ตั้งใจ'

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
d = sum((len(n) - len(o)) * cnt for o, n, cnt in PAIRS)
print(f'v55 ok · แทน 12 จุด · ความยาวรวมเปลี่ยน {d:+d} ตัวอักษร (ต่อ prompt ที่มีบล็อกนั้น)')
