#!/usr/bin/env python3
# showhow-v26-no-sheet-onscreen.py — ห้ามโชว์แผ่นสตอรีบอร์ดบนจอ (minimal เจอของจริง 2026-09-21)
# ที่มา: ทีม minimal เจอคลิปจริงที่ **หน้าสตอรีบอร์ดโผล่เต็มจอ 2 วินาทีตอนหัวช่วงที่ 3** (เขาแก้ด้วย v28: ย้ายบอร์ดไปเป็น ref ตัวท้าย + ห้ามโชว์)
# ของเรา: prompt วิดีโอมีแค่ "Never copy a sheet." = ห้ามลอก **แต่ไม่ได้ห้ามโชว์** · และบอร์ดเป็น ref ใบแรก (ตั้งใจ เพื่อให้ยึดแผนของช่วงนั้น)
# ⇒ เลือกแก้แบบถูกที่สุด: เปลี่ยนประโยคเดิมให้ครอบ "ห้ามโชว์" ด้วย โดยไม่ขยับลำดับ ref (ลำดับปัจจุบันพิสูจน์แล้ววันนี้ว่าคุมความต่อเนื่องได้)
# 🪤 headroom วิดีโอเหลือ 38 ตัวอักษร ⇒ ต้องตัดคำฟุ่มเฟือยในประโยคเดียวกันมาแลก
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)
def sub(node, old, new, box):
    if isinstance(node, dict): return {k: sub(v, old, new, box) for k, v in node.items()}
    if isinstance(node, list): return [sub(v, old, new, box) for v in node]
    if isinstance(node, str) and old in node: box[0] += node.count(old); return node.replace(old, new)
    return node
PAIRS = [
    ('Never copy a sheet.', 'Never copy a sheet or show one on screen.'),          # +21
    ('other sheets = other parts of the same clip:', 'other sheets = other parts:'),  # -17
]
for old, new in PAIRS:
    box = [0]; d = sub(d, old, new, box)
    if not box[0]: sys.exit(f'✗ ไม่เจอ "{old[:40]}…"')
    print(f'  {box[0]} จุด · {len(new)-len(old):+d} ตัวอักษร · {old[:44]}')
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print('✓ v26 ·', os.path.getsize(P), 'bytes')
