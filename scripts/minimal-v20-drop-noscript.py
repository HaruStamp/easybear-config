#!/usr/bin/env python3
# minimal-v20-drop-noscript.py — ถอดการ์ด "ยังไม่มีบท" ออกจากหน้าผลิต (2026-09-13 · คำสั่งพี่หมี)
#
# ของเดิม: กล่องเส้นประกลางหน้าผลิต — ไอคอน edit_note + "ยังไม่มีบท"
#          + "กลับหน้าตั้งค่าแล้วกด \"เริ่ม\" อีกครั้ง — บทจะโผล่เป็นการ์ดให้แก้ได้ทีละช่อง"
#          when = count(tasks)==0 ∧ ไม่ได้กำลังรัน/ลองใหม่
# พี่หมีสั่ง: "เอา card นี้ ออกเลย"
#
# 🪤 ถอด el ออกจากหน้า ต้องเช็คเสมอว่าไม่ได้ทำให้หน้านั้นว่างเปล่า (ตระกูลจอขาว)
#    วัดแล้ว: สถานะ tasks=0 ยังมีหัวหน้า · แถบขั้นตอน · การ์ดสถานะ · รายการสินค้า · ปุ่มรีเซ็ต ⇒ ไม่ว่าง
# รันซ้ำได้ (idempotent)
import json, sys, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / (sys.argv[1] if len(sys.argv) > 1 else 'minimal-lab.json')
c = json.loads(SRC.read_text(encoding='utf-8'))

TITLE = 'ยังไม่มีบท'
BODY_HEAD = 'กลับหน้าตั้งค่าแล้วกด'

def is_card(n):
    """กล่องที่ถือข้อความ 2 บรรทัดนั้นเป็น **ลูกตรง ๆ** เท่านั้น
       🧲 ★ห้ามใช้ json.dumps ทั้งก้อน — จะจับ ancestor แล้วลบทั้งหน้า (โดนมาแล้วรอบ v18)"""
    if not isinstance(n, dict) or n.get('el') != 'box':
        return False
    kids = n.get('card') or []
    vals = [k.get('value') for k in kids if isinstance(k, dict) and k.get('el') == 'text']
    return any(v == TITLE for v in vals) and any(isinstance(v, str) and v.startswith(BODY_HEAD) for v in vals)

produce = c['phases'][0]['form'][3]

# เก็บรายชื่อ (พ่อ, index) ให้ครบก่อนแก้ แล้วลบจากท้ายมาหน้า
targets = []
def rec(n):
    if isinstance(n, dict):
        kids = n.get('card')
        if isinstance(kids, list):
            for i, k in enumerate(kids):
                if is_card(k): targets.append((kids, i))
        for v in n.values(): rec(v)
    elif isinstance(n, list):
        for v in n: rec(v)
rec(produce)

for kids, i in sorted(targets, key=lambda t: -t[1]):
    del kids[i]

# ── ยามของสคริปต์เอง ─────────────────────────────────────────────
left = []
def rec2(n):
    if isinstance(n, dict):
        if is_card(n): left.append(1)
        for v in n.values(): rec2(v)
    elif isinstance(n, list):
        for v in n: rec2(v)
rec2(c)
assert not left, 'ยังเหลือการ์ด "ยังไม่มีบท" อยู่ %d จุด' % len(left)
whole = json.dumps(c, ensure_ascii=False)
assert TITLE not in whole, 'ข้อความ "%s" ยังตกค้างอยู่ที่อื่น' % TITLE
assert BODY_HEAD not in whole, 'ข้อความชวนกลับหน้าตั้งค่ายังตกค้าง'
# 🪤 ห้ามลบเกิน — หน้าผลิตต้องยังมีของครบ
assert len(produce['card'][0]['card']) >= 9, 'ลูกของหน้าผลิตหายเกินที่สั่ง (เหลือ %d)' % len(produce['card'][0]['card'])
assert any(json.dumps(x, ensure_ascii=False).find('"repeat"') >= 0 for x in produce['card'][0]['card']), 'ลิสต์การ์ดคลิป/สินค้าหายไป'

SRC.write_text(json.dumps(c, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('✅ %s — ลบการ์ด "ยังไม่มีบท" %d จุด%s' % (SRC.name, len(targets), '' if targets else ' (รันซ้ำ ไม่มีอะไรเปลี่ยน)'))
