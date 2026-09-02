#!/usr/bin/env python3
# showhow-v6b.py — เก็บรายละเอียดหน้า "เพิ่มงาน" หลังดูจริงบนจอ (รันต่อจาก v6)
import json, os
P = '/Users/tammaster/Desktop/Dev/bear-clan/easybear-config/showhow.json'
cfg = json.load(open(P, encoding='utf-8'))
LBL = ('!text-[13.5px] min-[640px]:!text-[13px] !text-[var(--ev-text)] opacity-65 '
       'uppercase tracking-[0.14em] font-black px-0.5 mb-2')

def find_list(root, probe):
    if isinstance(root, dict):
        for k, v in root.items():
            if isinstance(v, list) and len(v) >= 4 and any(probe in json.dumps(c, ensure_ascii=False) for c in v):
                return root, k
            r = find_list(v, probe)
            if r: return r
    elif isinstance(root, list):
        for c in root:
            r = find_list(c, probe)
            if r: return r
    return None

node, key = find_list(cfg['phases'][0]['form'][2], '{item.slots.image}')
CARD = node[key]
assert len(CARD) == 7, f'คาดว่า 7 บล็อก แต่เจอ {len(CARD)} — v6 ยังไม่ถูกรัน?'
S2, S4 = CARD[2], CARD[4]

def tiles_of(sec):
    for blk in sec['card']:
        if isinstance(blk, dict) and 'flex flex-row flex-wrap' in str(blk.get('className', '')):
            return blk
    return None

# ① ถอดการ์ดเตือนเหลืองออกจากหัวข้อ 4 (หัวข้อบอก "ไม่บังคับ" แต่มีการ์ดเตือน = ขัดกันเอง)
t4 = tiles_of(S4); amber = None
for i, c in enumerate(t4['card']):
    if 'amber' in json.dumps(c, ensure_ascii=False):
        amber = t4['card'].pop(i); break

# ② ย้ายไปหัวข้อ 2 ในโทน "คำแนะนำ" ไม่ใช่ "เตือน" + ผูกกับ room1
if amber:
    a = (json.dumps(amber, ensure_ascii=False)
         .replace('amber-500', '[var(--ev-accent)]').replace('amber-600', '[var(--ev-accent)]')
         .replace('"icon": "warning"', '"icon": "lightbulb"')
         .replace('{item.slots.image}', '{item.slots.room1}')
         .replace('ยังไม่ได้แนบรูป', 'ยังไม่ได้แนบรูปพื้นที่')
         .replace('ไม่บังคับ — แต่แนบรูปจริงแล้วผลลัพธ์ตรงกว่ามาก',
                  'ไม่มีรูปก็ผลิตได้ — หมีจะจินตนาการพื้นที่จากคำบรรยาย แต่แนบรูปจริงแล้วตรงบ้านกว่ามาก'))
    tiles_of(S2)['card'].append(json.loads(a))

# ③ ป้ายบอกจำนวนรูปเหนือแถวไทล์
for sec, text in [(S2, 'รูปพื้นที่จริง (สูงสุด 2 รูป)'), (S4, 'รูปของ (สูงสุด 5 มุม)')]:
    for i, blk in enumerate(sec['card']):
        if isinstance(blk, dict) and 'flex flex-row flex-wrap' in str(blk.get('className', '')):
            sec['card'].insert(i, {'el': 'text', 'value': text, 'className': LBL}); break

json.dump(cfg, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'✓ v6b → {os.path.getsize(P)} bytes · ถอดการ์ดเตือนจากหัวข้อ 4 · ย้ายเป็นคำแนะนำหัวข้อ 2 · เพิ่มป้ายจำนวนรูป')
