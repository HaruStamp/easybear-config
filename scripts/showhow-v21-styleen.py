#!/usr/bin/env python3
# showhow-v21-styleen.py — ค่าสไตล์ข้อความต้องเป็น "อังกฤษล้วน" (พี่หมีเจอจากวิดีโอจริง 2026-09-21)
# อาการ: วิดีโอช่วง 1 พิมพ์หัวเรื่องเป็น 2 บรรทัด — บรรทัดบน "ตัวอักษร ไทยหนามาก" (= คำขึ้นต้นของ *คำอธิบายสไตล์*) บรรทัดล่างเป็นหัวเรื่องจริง
# ราก: option.value ของ svText เขียนเป็นไทย แล้วถูกเสียบลง prompt (`style {values.svText}`) ⇒ โมเดลเข้าใจว่าเป็นข้อความที่ต้องพิมพ์ลงจอ
# แก้: value = อังกฤษล้วน (ไทยอยู่ที่ label/desc ซึ่งเป็น UI เท่านั้น) · svText ไม่ใช่คีย์ของ lookup ใด ๆ จึงเปลี่ยนค่าได้ปลอดภัย
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
EN = {
 'ป้ายการ์ดขาว': 'bold dark Thai text on a white rounded-corner card with even padding and a soft drop shadow',
 'เน้นคำสำคัญ': 'very bold Thai text, two lines, white with a thin dark outline, one key word in bright yellow or orange',
 'ไฮไลต์ปากกา': 'bold dark Thai text with a bright hand-drawn highlighter stroke behind the key word',
 'ตัวหนาขอบหนา': 'bold Thai sans-serif, white fill, thick dark outline, soft drop shadow',
 'บางมินิมอล': 'clean thin Thai sans-serif, wide letter spacing, white, very soft shadow',
}
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)
old_by_label = {}
def walk(n):
    if isinstance(n, dict):
        if n.get('field') == 'svText' and n.get('options'):
            for o in n['options']:
                old_by_label[o['label']] = o['value']; o['value'] = EN[o['label']]
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)
walk(d)
assert set(old_by_label) == set(EN), old_by_label.keys()
d['values']['svText'] = EN['เน้นคำสำคัญ']            # ค่าตั้งต้นเดิม (พี่หมีเลือก)
s = json.dumps(d, ensure_ascii=False)
for lab, old in old_by_label.items():                 # กันค่าไทยค้างที่อื่น (when/eq/values)
    assert old not in s, f'ยังมีค่าไทยของสไตล์ "{lab}" ค้างอยู่'
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
G = os.path.join(HERE, 'showhow-v13-textstyle.py')     # generator: เปลี่ยน value ของ STYLES ให้ตรงกัน
g = open(G, encoding='utf-8').read()
for lab, old in old_by_label.items():
    if old in g: g = g.replace(old, EN[lab])
open(G, 'w', encoding='utf-8').write(g)
print('✓ v21 · สไตล์ 5 แบบเป็นอังกฤษล้วน ·', os.path.getsize(P), 'bytes')
