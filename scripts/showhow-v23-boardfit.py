#!/usr/bin/env python3
# showhow-v23-boardfit.py — บีบ prompt บอร์ดให้ลงใต้เพดาน 3,900 อีกครั้ง (2026-09-21)
# ที่มา: ตัววัดเดิมใช้ค่า svText ที่ค้างจากยุคก่อน v13 (สั้นกว่าของจริง 59 ตัวอักษร) ⇒ ตัวเลข headroom ที่เคยรายงานสูงเกินจริง
#        วัดใหม่ด้วยค่าตั้งต้นจริง: **ทะลุ 6/10,800 สูงสุด 3,914** (บอร์ดช่วง 1 · โหมดหัวเรื่อง · คนเดียวเต็มตัว · มีรูป)
# ที่ตัด = คำฟุ่มเฟือยล้วน ไม่แตะคำสั่งเลย์เอาต์ / บรรทัดสินค้า / กติกาต่อเนื่อง (ทั้งสามอย่างพิสูจน์แล้วว่าบีบไม่ได้)
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
TRIM = [
    ('แผ่นภาพสตอรีบอร์ดแนวตั้ง ภาพล้วน ไม่มีตารางข้อความ ของคลิป "ทำให้ดู" เรื่อง',
     'แผ่นภาพสตอรีบอร์ดแนวตั้ง ภาพล้วน ไม่มีตารางข้อความ เรื่อง'),
    ('(ถ้าสไตล์ไม่ได้ระบุสี ให้ใช้หัวข้อตัวอักษรสีเข้มที่เข้ากับโทนสีของคลิป)',
     '(ไม่ระบุสี = หัวข้อตัวอักษรสีเข้มที่เข้ากับโทนสีของคลิป)'),          # ★ยาม starter เช็ควลีในวงเล็บ ห้ามแตะ
    ('ใช้ข้อความที่บทให้ไว้ของช่องนั้นเท่านั้น', 'ใช้ข้อความที่บทให้ของช่องนั้นเท่านั้น'),
    ('ระยะภาพตรงตามมุมกล้องของฉากนั้น', 'ระยะภาพตามมุมกล้องของฉากนั้น'),
    ('ช่องภาพเรียงตามลำดับ (เลขในวงกลม = เลขหน้าบรรทัด):', 'ช่องภาพตามลำดับ (เลขในวงกลม = เลขหน้าบรรทัด):'),
    ('บรรทัดนี้เป็นข้อมูลกำกับ ห้ามพิมพ์ลงบนภาพ', 'บรรทัดนี้เป็นข้อมูลกำกับ ห้ามพิมพ์ลงภาพ'),
    ('มีคนลงมือทำ 1 คน (ไทย) คนเดียวกันทุกช่อง', 'มีคนลงมือทำ 1 คน (ไทย) คนเดิมทุกช่อง'),
]
STYLE = {   # ค่าสไตล์ข้อความ (อังกฤษล้วนตั้งแต่ v21) — เขียนสั้นลงโดยคงฟอนต์/สี/การตกแต่งครบ
    'bold dark Thai text on a white rounded-corner card with even padding and a soft drop shadow':
        'bold dark Thai text on a white rounded card, even padding, soft shadow',
    'very bold Thai text, two lines, white with a thin dark outline, one key word in bright yellow or orange':
        'very bold Thai text, 2 lines, white, thin dark outline, one key word in bright yellow',
    'bold dark Thai text with a bright hand-drawn highlighter stroke behind the key word':
        'bold dark Thai text, bright hand-drawn highlighter stroke behind the key word',
    'bold Thai sans-serif, white fill, thick dark outline, soft drop shadow':
        'bold Thai sans-serif, white fill, thick dark outline, soft shadow',
    'clean thin Thai sans-serif, wide letter spacing, white, very soft shadow':
        'thin clean Thai sans-serif, wide letter spacing, white, very soft shadow',
}
raw = open(P, encoding='utf-8').read()
d = json.loads(raw)

def sub(node, old, new, box):
    """แทนข้อความในทุก string ของต้นไม้ (ไม่ใช้ json.dumps เพราะฟันหนูในข้อความจะกลายเป็น \\" แล้วหาไม่เจอ)"""
    if isinstance(node, dict):
        return {k: sub(v, old, new, box) for k, v in node.items()}
    if isinstance(node, list):
        return [sub(v, old, new, box) for v in node]
    if isinstance(node, str) and old in node:
        box[0] += node.count(old); return node.replace(old, new)
    return node

saved = 0
for old, new in TRIM:
    box = [0]; d = sub(d, old, new, box)
    if not box[0]: sys.exit(f'✗ ไม่เจอ "{old[:40]}…" — ข้อความเปลี่ยนไปแล้ว ห้ามเดา')
    saved += (len(old) - len(new))
    print(f'  -{len(old)-len(new):>2} × {box[0]:>2} จุด · {old[:38]}…')
for old, new in STYLE.items():
    box = [0]; d = sub(d, old, new, box)
    if not box[0]: sys.exit(f'✗ ไม่เจอค่าสไตล์ "{old[:40]}…"')
    print(f'  สไตล์ -{len(old)-len(new)} × {box[0]} จุด')
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print(f'✓ v23 boardfit · ลดต่อบอร์ดรวม ~{saved} ตัวอักษร (+สไตล์) ·', os.path.getsize(P), 'bytes')
