#!/usr/bin/env python3
"""minimal v47 — dropdown "การนำเสนอสินค้า" มีคำอธิบายสั้นใต้ชื่อทุกตัวเลือก (พี่หมีสั่ง 2026-09-26)

engine รองรับอยู่แล้ว: `style.dropdown = "custom"` ⇒ `CustomDropdown` แสดง `option.desc` ในรายการ
และ `el.showDesc` ⇒ แสดง desc ของตัวที่เลือกใต้ชื่อในกล่อง (atoms-base.tsx · CustomDropdown)
🪤 desc ถูก `truncate` บรรทัดเดียว 11px ⇒ ต้องสั้น (ยาม: ≤ 34 ตัวอักษร)
แตะเฉพาะ desc + showDesc — `value` (ที่เข้า prompt) ไม่ขยับ · รันซ้ำได้
"""
import json, os, sys, copy

PATH = os.path.join(os.path.dirname(__file__), '..', 'minimal-dev.json')
cfg = json.load(open(PATH, encoding='utf-8'))
orig = copy.deepcopy(cfg)

DESC = {
    '': 'หมีเลือกให้เข้ากับสินค้าแต่ละตัว',
    'สินค้าเดี่ยวบนพื้นเรียบ': 'ตั้งเดี่ยว พื้นโล่ง เห็นสินค้าชัด',
    'มือคนถือสินค้า': 'มือหยิบจับ เห็นขนาดจริงของสินค้า',
    'มีพร็อพมินิมอลประกอบ': 'ของแต่งเรียบ ๆ วางข้างให้มีสไตล์',
    'บรรยากาศการใช้งานจริง': 'อยู่ในบ้าน ตอนใช้ในชีวิตประจำวัน',
    'โชว์เนื้อสัมผัส เท็กซ์เจอร์': 'ซูมใกล้ เห็นผิว เนื้อ และวัสดุ',
    'จัดวางหลายชิ้นเป็นแพทเทิร์น': 'เรียงหลายชิ้นเป็นลวดลายสวยงาม',
    'สินค้าลอยกลางอากาศ (floating)': 'สินค้าลอยนิ่งกลางเฟรม ดูโดดเด่น',
    'พร็อพธรรมชาติ ใบไม้ หิน แสงเงา': 'ใบไม้ หิน แสงเงา ดูเป็นธรรมชาติ',
    'เทียบก่อน-หลังใช้ (before-after)': 'โชว์ผลต่างก่อนและหลังใช้',
    'แกะกล่องเปิดสินค้า (unboxing)': 'เปิดกล่องเผยสินค้าครั้งแรก',
}

found = []
def walk(x):
    if isinstance(x, dict):
        if x.get('field') == 'svPres1' and isinstance(x.get('options'), list): found.append(x)
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
walk(cfg['phases'])
assert len(found) == 1, 'ต้องเจอ dropdown svPres1 ตัวเดียว เจอ %d' % len(found)
dd = found[0]
vals = [o['value'] for o in dd['options']]
assert sorted(vals) == sorted(DESC), 'ตัวเลือกไม่ตรงชุดที่คาด: %r' % vals

if dd.get('showDesc') is True and all(o.get('desc') == DESC[o['value']] for o in dd['options']):
    print('✓ แพตช์แล้ว (v47) — ไม่มีอะไรต้องทำ'); sys.exit(0)

for o in dd['options']:
    o['desc'] = DESC[o['value']]
dd['showDesc'] = True

# ── ยาม
assert all(len(d) <= 34 for d in DESC.values()), [d for d in DESC.values() if len(d) > 34]
assert [o['value'] for o in dd['options']] == vals            # value/ลำดับเดิม
o2, c2 = copy.deepcopy(orig), copy.deepcopy(cfg)
def strip(x):
    if isinstance(x, dict):
        if x.get('field') == 'svPres1':
            x.pop('showDesc', None)
            for o in x.get('options', []): o.pop('desc', None)
        for v in x.values(): strip(v)
    elif isinstance(x, list):
        for v in x: strip(v)
strip(o2); strip(c2)
assert o2 == c2, 'มีส่วนอื่นขยับนอกจาก desc/showDesc'

json.dump(cfg, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('✅ v47 เขียนแล้ว · desc %d ตัวเลือก · showDesc=true · ยาวสุด %d ตัวอักษร' % (len(DESC), max(map(len, DESC.values()))))
