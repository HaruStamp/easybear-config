#!/usr/bin/env python3
# showhow-v25-title-once.py — หัวเรื่องถูกพิมพ์ซ้ำ 2 บรรทัด (เจอจากคลิปจริงบนบัญชีที่ 2 · 2026-09-21)
# อาการ: คลิปขึ้น "ขัดคราบหินปูนง่ายๆ" **สองบรรทัดข้อความเดียวกัน** (บรรทัดบนเน้นคำเหลือง บรรทัดล่างขาวล้วน) ทั้งช่วง 1 และ 2
# ราก 2 ชั้น:
#   ① ค่าสไตล์ตั้งต้นเขียนว่า "2 lines" — เป็นคำอธิบาย *ทรง* ของสไตล์ (หัวเรื่องยาวให้ตัด 2 บรรทัด)
#      แต่พอหัวเรื่องสั้น โมเดลทำตามตัวอักษรโดยการ **พิมพ์ข้อความเดิมซ้ำอีกบรรทัด** ⇒ ตัดเลขบรรทัดออกจากสไตล์ ปล่อยให้ตัดบรรทัดเอง
#   ② โหมดหัวเรื่องมีคำสั่งเรื่องหัวเรื่อง 2 ที่ (บล็อก ON-SCREEN TEXT + บรรทัด Thai overlay/TITLE) ⇒ เติมคำสั่งชัดว่า "พิมพ์ครั้งเดียว ห้ามซ้ำ"
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)

def sub(node, old, new, box):
    if isinstance(node, dict): return {k: sub(v, old, new, box) for k, v in node.items()}
    if isinstance(node, list): return [sub(v, old, new, box) for v in node]
    if isinstance(node, str) and old in node: box[0] += node.count(old); return node.replace(old, new)
    return node

PAIRS = [
    # ① เลขบรรทัดออกจากสไตล์
    ('very bold Thai text, 2 lines, white, thin dark outline, one key word in bright yellow',
     'very bold Thai text, white, thin dark outline, one key word in bright yellow'),
    # ② ย้ำ "ครั้งเดียว" ในบล็อกหัวเรื่องของโหมดค้างทั้งคลิป + โหมดปกติ
    ('ON-SCREEN TEXT: one fixed Thai title overlay only —',
     'ON-SCREEN TEXT: exactly ONE fixed Thai title overlay, rendered once only, never repeat the same words on a second line —'),
    ('ON-SCREEN TEXT: only the quoted Thai overlays below may appear —',
     'ON-SCREEN TEXT: only the quoted Thai overlays below may appear, each rendered once only, never repeated on a second line —'),
]
for old, new in PAIRS:
    box = [0]; d = sub(d, old, new, box)
    if not box[0]: sys.exit(f'✗ ไม่เจอ "{old[:50]}…"')
    print(f'  {box[0]} จุด · {"+" if len(new)>len(old) else ""}{len(new)-len(old)} ตัวอักษร · {old[:46]}…')
v = d['values'].get('svText', '')
if '2 lines' in v: d['values']['svText'] = v.replace('2 lines, ', ''); print('  ค่าตั้งต้น svText อัปเดตแล้ว')
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print('✓ v25 ·', os.path.getsize(P), 'bytes')
