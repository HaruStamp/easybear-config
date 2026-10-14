#!/usr/bin/env python3
"""showhow-v133 — สไตล์ภาพ "หนังลึกลับ" (`noir`) + "ฟิล์มย้อนยุค" (`retro`) ให้ตรง podcast · ตัวเลือกบนจอ 12 (รวมอัตโนมัติ) · พี่หมีสั่ง 2026-10-14

คีย์/ป้าย/ไอคอน = ของ podcast (dcf7562) · ถ้อยคำวิดีโอของ podcast ยาว 77/66 เกินงบเรา (≤ 50) ⇒ ย่อ (podcast รับทราบ · คง "low-key")
ทั้งคู่เป็นภาพสมจริง ⇒ styleNegEN = '' (เหมือน real/thai/clean/cyber)
ใช้: python3 scripts/showhow-v133-style-noir-retro.py  (รันบน v132)
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
L = c['lookups']
NEW = {
 'noir': dict(board='ภาพสมจริงแบบหนังลึกลับ แสงต่ำ เงาเข้ม คอนทราสต์สูง ทุกช่อง',
              video='cinematic noir look, low-key light, deep shadows',
              plan='สมจริงแบบหนังลึกลับ แสงต่ำ เงาเข้ม คอนทราสต์สูง',
              ui={'value': 'noir', 'label': 'หนังลึกลับ', 'desc': 'แสงต่ำ เงาเข้ม', 'icon': 'movie'}),
 'retro': dict(board='ภาพสมจริงแบบฟิล์มย้อนยุค 70-80 สีซีดอุ่น เม็ดฟิล์ม ทุกช่อง',
               video='1970s film look, faded warm colors, film grain',
               plan='สมจริงแบบฟิล์มย้อนยุค 70-80 สีซีดอุ่น เม็ดฟิล์มบาง ๆ',
               ui={'value': 'retro', 'label': 'ฟิล์มย้อนยุค', 'desc': 'สีซีดอุ่น เม็ดฟิล์ม', 'icon': 'camera_roll'}),
}
for k, v in NEW.items():
    assert k not in L['styleBoard'], k
    L['styleBoard'][k] = v['board']; L['styleVideoEN'][k] = v['video']; L['stylePlan'][k] = v['plan']; L['styleNegEN'][k] = ''
    assert len(v['board']) <= len(L['styleBoard']['real']), (k, len(v['board']))
    assert len(v['video']) <= len(L['styleVideoEN']['real']), (k, len(v['video']))
    assert all(ord(ch) < 128 for ch in v['video'])
n = 0
def walk(x):
    global n
    if isinstance(x, dict):
        if x.get('field') == 'svStyle' and isinstance(x.get('options'), list):
            vals = [o['value'] for o in x['options']]
            assert 'noir' not in vals and 'ink' in vals
            i = vals.index('ink') + 1  # ต่อท้าย ink แบบ podcast (สีน้ำอยู่ท้ายสุดเหมือนเขา)
            x['options'][i:i] = [NEW['noir']['ui'], NEW['retro']['ui']]; n += 1
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
walk(c)
assert n == 1, n
opts = []
def grab(x):
    if isinstance(x, dict):
        if x.get('field') == 'svStyle' and isinstance(x.get('options'), list): opts.extend(o['value'] for o in x['options'])
        for v in x.values(): grab(v)
    elif isinstance(x, list):
        for v in x: grab(v)
grab(c)
assert set(opts) == set(L['styleBoard']) == set(L['styleVideoEN']) == set(L['styleNegEN']), set(opts) ^ set(L['styleBoard'])
assert set(opts) - {'', 'real'} == set(L['stylePlan'])
print(f'✅ v133: สไตล์ {len(opts)} ตัวเลือก {opts} · บอร์ด {[len(NEW[k]["board"]) for k in NEW]} · วิดีโอ {[len(NEW[k]["video"]) for k in NEW]}')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
