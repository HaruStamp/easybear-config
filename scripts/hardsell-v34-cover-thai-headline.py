#!/usr/bin/env python3
# hardsell-dev v34: ปก TikTok — หัวข้อไทยห้ามแปล (บทเรียนเจนจริง minimal mnCover 26 พ.ย.: โมเดลแปลหัวข้อไทยเป็นอังกฤษ + แปะแคปชันทั้งย่อหน้า)
#   - หัวข้อ = ov1 (ว่าง = ชื่อสินค้า) ตัดเหลือ ≤32 ตัว (clamp กันล้นเท่านั้น — ov1 ตามกฎบท ≤5 คำอยู่แล้ว · ตัดสั้นกว่านี้ = ตัดกลางคำไทย เห็นในเทส) · ไม่ส่ง caption เข้า prompt ปก (v32 ไม่ส่งอยู่แล้ว — ยามกันกลับมา)
#   - สั่งชัด: อักษรไทยคัดลอกทีละตัว ห้ามแปล/ถอดเป็นอังกฤษ · ห้ามมีข้อความอื่นนอกจากหัวข้อนี้
# ใช้: python3 scripts/hardsell-v34-cover-thai-headline.py [hardsell-dev.json]   (รันบน v33 · รันซ้ำได้)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F, encoding='utf-8'))
cov = next(o for o in d['ops'] if o['id'] == 'mnCover')
pp = cov['prompt']['parts']
OLD_A = 'HEADLINE text in Thai, spelled exactly: "'
NEW_A = 'HEADLINE (the only text on the cover), written in THAI SCRIPT, copied character by character exactly as given — never translate it to English, never transliterate, never add words: "'
OLD_B = '" — one or two short lines in the upper third'
if OLD_A in pp[0]:
    pp[0] = pp[0].replace(OLD_A, NEW_A)
    i = next(i for i, p in enumerate(pp) if isinstance(p, dict) and p.get('op') == 'cond')
    pp[i] = {'op': 'clamp', 'max': 32, 'value': pp[i]}
    assert pp[i + 1].startswith(OLD_B)
s = json.dumps(cov, ensure_ascii=False)
assert 'item.caption' not in s and 'item.hashtags' not in s and NEW_A in pp[0] and '"op": "clamp", "max": 32' in s
assert cov['model'] == '🍌 Nano Banana Pro' and cov['aux'] is True
print('v34: หัวข้อปกไทยห้ามแปล ≤32 ตัว')
open(F, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2))
