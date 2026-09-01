#!/usr/bin/env python3
# story-v3: ปุ่มความยาวคลิป → แถบเต็มการ์ด (grid-select contained)
import json, os
P = '/Users/tammaster/Desktop/Dev/bear-clan/easybear-config/story.json'
cfg = json.load(open(P, encoding='utf-8'))
PROD = cfg['phases'][0]['form'][0]['card'][0]['card'][3]

box = PROD['card'][1]
head = [el for el in box['card'] if el.get('el') in ('row', 'text') and 'grid-select' not in json.dumps(el, ensure_ascii=False)][:2]

box['card'] = head + [
    # แถวบน: อัตโนมัติ — เต็มความกว้าง แนวนอน (ไอคอน + ข้อความ)
    {'el': 'grid-select', 'field': 'clipsPerProduct', 'cols': 1, 'contained': True, 'horizontal': True,
     'options': [{'value': '', 'label': 'อัตโนมัติ', 'icon': 'auto_awesome',
                  'desc': 'หมีเลือกความยาวให้พอดีเนื้อหาของแต่ละงาน'}]},
    # แถวล่าง: 6 ความยาว — 3 คอลัมน์เท่ากัน เต็มการ์ด
    {'el': 'grid-select', 'field': 'clipsPerProduct', 'cols': 3, 'contained': True,
     'label': 'หรือกำหนดเอง',
     'options': [{'value': str(n), 'label': '%d วินาที' % (n * 10), 'desc': '%d ฉาก' % n} for n in range(1, 7)]},
    {'el': 'text',
     'value': 'ยิ่งยาวยิ่งใช้โควตา — 1 ฉาก = ภาพ 1 + วิดีโอ 1 · 60 วินาที = 12 ครั้ง gen ต่อ 1 งาน',
     'className': '!text-[13px] min-[640px]:!text-[12px] opacity-50 mt-1'},
]
json.dump(cfg, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✓ length selector → contained →', os.path.getsize(P), 'bytes')
