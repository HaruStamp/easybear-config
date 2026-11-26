#!/usr/bin/env python3
# minimal-v64-cover-thai-headline.py — แก้ปก (mnCover) จากเทสสดบน Dev 26 พ.ย. 2569 (svLang ไทย · มีข้อความ · สินค้า "ที่แขวนหูฟังใต้โต๊ะ") · minimal-dev.json อย่างเดียว · รันซ้ำได้
#  ① หัวข้อถูกแปลเป็นอังกฤษ ("Under-desk headphone hanger") — prompt ไม่ได้บอกภาษา ⇒ ไทย: "Thai script, copy every character exactly, never translate" · English: ตาม svLang
#  ② "Optional one tiny label taken only from this caption: {item.caption}" ⇒ โมเดลแปะแคปชันทั้งย่อหน้า (เป็นอังกฤษ) ใต้หัวข้อ
#     → ป้ายเล็กใช้ข้อความ overlay ฉาก 2 ({item.ov2} · ≤5 คำ ภาษาเดียวกับคลิปอยู่แล้ว) ห้ามแปล · แคปชันไม่เข้า prompt ปกอีก
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json'
c = json.load(open(P, encoding='utf-8'))
cov = next(o for o in c['ops'] if o['id'] == 'mnCover')
def eq(a, b): return {'op': 'eq', 'a': a, 'b': b}
def NOT(x): return {'op': 'not', 'a': x}
OLD_H = 'HEADLINE text, spelled exactly: "{item.productName}" — one short line in the top area, '
OLD_T = ', the same lettering style as the clip overlays, never covering the product. Optional one tiny label taken only from this caption: "{item.caption}".\n'
NEW_T = ', the same lettering style as the clip overlays, never covering the product. Optional tiny sub-label under it, copied exactly: "{item.ov2}" — nothing else, no caption or paragraph.\n'
HEAD = {'op': 'block', 'sep': '', 'parts': [
    {'when': NOT(eq('{values.svLang}', 'English')), 'value': 'HEADLINE in THAI SCRIPT (ภาษาไทย), copy every character exactly, never translate or romanize: "{item.productName}" — one short line in the top area, '},
    {'when': eq('{values.svLang}', 'English'), 'value': 'HEADLINE in English, spelled exactly: "{item.productName}" — one short line in the top area, '},
]}
n = 0
def walk(x):
    global n
    if isinstance(x, dict):
        if x.get('op') == 'concat' and isinstance(x.get('parts'), list):
            ps = x['parts']
            for i, p in enumerate(ps):
                if p == OLD_H: ps[i] = HEAD; n += 1
                elif p == OLD_T: ps[i] = NEW_T; n += 1
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
walk(cov['prompt'])
s = json.dumps(cov['prompt'], ensure_ascii=False)
assert '{item.caption}' not in s and 'never translate or romanize' in s and '{item.ov2}' in s, 'ผัง prompt ปกเปลี่ยน — ปรับสคริปต์ก่อน'
# กฎท้าย: ห้ามแปลข้อความใด ๆ
R = cov['prompt']['parts'][-1]
if isinstance(R, str) and 'never translate' not in R:
    cov['prompt']['parts'][-1] = R.replace('text spelled exactly, never mirrored;', 'text spelled exactly in the clip language, never translated or mirrored;'); n += 1
open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=2))
print('ปก แก้', n, 'จุด ·', P)
