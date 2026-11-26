#!/usr/bin/env python3
"""showhow-v137 — เลือกโมเดลรูปได้ 3 ตัว (เจ้าของสั่ง 26 พ.ย.) · ลอกแบบ hardsell-dev (values.imageModel + ตัวเลือก + model แบบ cond)
- values.imageModel = '🍌 Nano Banana 2.1' (ค่าเดิมที่บอร์ดใช้อยู่)
- หน้าตั้งค่า (phases[0].form[0].card[0].card[4]) ใต้ 'ความละเอียด': ตัวเลือก 'โมเดลสร้างภาพ' 3 ตัว + ข้อความเล็ก 'มีข้อความบนภาพ ใช้ Pro อัตโนมัติ'
- op ภาพ: มีข้อความบนภาพ → '🍌 Nano Banana Pro' · ไม่มี → {values.imageModel}
    mnBoard  : มีข้อความเมื่อ svTextOn != ไม่มีข้อความ (หัวเรื่องอยู่ช่องแรกของบอร์ดช่วง 1)
    mnBoard2-6: มีข้อความเฉพาะ svTextOn = ซับไตเติ้ลรายฉาก (โหมดหัวเรื่อง บอร์ดช่วง 2+ ภาพล้วน)
- ป้ายตัวเลือกไม่ใส่ emoji (กฎ UI showhow: material symbols ห้าม emoji) · ค่า value สะกดตรงชื่อโมเดล Flow
ใช้: python3 scripts/showhow-v137-image-model.py  (รันที่ราก easybear-config · บน showhow-dev ก่อน v137)
"""
import json
P = 'showhow-dev.json'
s0 = open(P, encoding='utf-8').read()
c = json.loads(s0)
assert json.dumps(c, ensure_ascii=False, indent=1) + '\n' == s0, 'รูปแบบไฟล์ไม่ตรง indent=1 + newline ท้าย'
PRO, DEF = '🍌 Nano Banana Pro', '🍌 Nano Banana 2.1'
MODELS = [PRO, DEF, '🍌 Nano Banana 2 Lite']
assert 'imageModel' not in c['values'], 'รันซ้ำ'
c['values']['imageModel'] = DEF

# ── UI ──
box = c['phases'][0]['form'][0]['card'][0]['card'][4]
res = box['card'][2]
assert any(x.get('field') == 'svRes' for x in res['card']), 'ตำแหน่งการ์ดความละเอียดเปลี่ยน'
row = json.loads(json.dumps(res['card'][0]))
row['card'][0]['icon'] = 'image'
row['card'][1]['value'] = 'โมเดลสร้างภาพ'
ui = {
 'el': 'box', 'className': res['className'],
 'card': [
  row,
  {'el': 'grid-select', 'field': 'imageModel', 'cols': 3, 'contained': True,
   'options': [
    {'value': MODELS[0], 'label': 'Nano Banana Pro', 'desc': 'สวยละเอียดสุด เขียนตัวไทยได้ · ช้ากว่า'},
    {'value': MODELS[1], 'label': 'Nano Banana 2.1', 'desc': 'ค่าเริ่ม · สมดุลทั้งคุณภาพและเวลา'},
    {'value': MODELS[2], 'label': 'Nano Banana 2 Lite', 'desc': 'เร็วสุด · รายละเอียดน้อยกว่า'},
   ],
   'className': res['card'][1]['className'], 'mobile': {'cols': 1}},
  {'el': 'text', 'value': 'มีข้อความบนภาพ ระบบใช้ Nano Banana Pro ให้ภาพที่มีตัวหนังสืออัตโนมัติ เพราะเขียนตัวไทยได้',
   'className': res['card'][2]['className'],
   'when': {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svTextOn}', 'b': 'ไม่มีข้อความ'}}},
 ]}
box['card'].insert(3, ui)

# ── ops ──
def cond(text_when):
    return {'op': 'cond', 'when': text_when, 'then': PRO, 'else': '{values.imageModel}'}
HAS_TEXT_1 = {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svTextOn}', 'b': 'ไม่มีข้อความ'}}
HAS_TEXT_K = {'op': 'eq', 'a': '{values.svTextOn}', 'b': 'ซับไตเติ้ลรายฉาก'}
n = 0
for o in c['ops']:
    if o.get('type') != 'image': continue
    assert o['model'] == DEF, (o['id'], o['model'])
    o['model'] = cond(HAS_TEXT_1 if o['id'] == 'mnBoard' else HAS_TEXT_K)
    n += 1
assert n == 6, n
print(f'✅ v137: op ภาพ {n} ตัว · ตัวเลือกโมเดล 3 ตัว · ค่าเริ่ม {DEF}')
open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
