#!/usr/bin/env python3
"""minimal v48 — ไอคอนหน้ากล่อง dropdown "การนำเสนอสินค้า" ตามตัวเลือกที่เลือก (พี่หมีทดสอบ 2026-09-29)

อาการ: เลือก "ลอยกลางอากาศ" แล้วไอคอนหน้ากล่องยังเป็นไม้กายสิทธิ์
ราก: CustomDropdown ใช้ `(icon || sel?.icon)` — `el.icon` ตายตัว 'auto_fix_high' (ติดมาจากการ์ดขั้นสูงตอน v46) ชนะไอคอนของตัวเลือกเสมอ
แก้: ถอด `el.icon` · ตัวเลือกค่าว่าง ("อัตโนมัติ") มีไอคอน auto_fix_high ของตัวเองอยู่แล้ว ⇒ ตอนยังไม่เลือกหน้าตาเดิม
รันซ้ำได้
"""
import json, os, sys, copy

PATH = os.path.join(os.path.dirname(__file__), '..', 'minimal-dev.json')
cfg = json.load(open(PATH, encoding='utf-8'))
orig = copy.deepcopy(cfg)

found = []
def walk(x):
    if isinstance(x, dict):
        if x.get('field') == 'svPres1' and isinstance(x.get('options'), list): found.append(x)
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
walk(cfg['phases'])
assert len(found) == 1
dd = found[0]
if 'icon' not in dd:
    print('✓ แพตช์แล้ว (v48)'); sys.exit(0)
assert dd['icon'] == 'auto_fix_high'
auto = next(o for o in dd['options'] if o['value'] == '')
assert auto.get('icon') == 'auto_fix_high', 'ตัวเลือกอัตโนมัติต้องมีไอคอนของตัวเอง ไม่งั้นตอนยังไม่เลือกจะไม่มีไอคอน'
assert all(o.get('icon') for o in dd['options']), 'ทุกตัวเลือกต้องมีไอคอน'
del dd['icon']

o2, c2 = copy.deepcopy(orig), copy.deepcopy(cfg)
def strip(x):
    if isinstance(x, dict):
        if x.get('field') == 'svPres1': x.pop('icon', None)
        for v in x.values(): strip(v)
    elif isinstance(x, list):
        for v in x: strip(v)
strip(o2); strip(c2)
assert o2 == c2, 'มีส่วนอื่นขยับ'
json.dump(cfg, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('✅ v48 ถอด el.icon ของ dropdown svPres1 · ไอคอนหน้ากล่องตามตัวเลือก')
