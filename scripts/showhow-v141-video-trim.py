#!/usr/bin/env python3
"""showhow-v141 — prompt วิดีโอลงใต้เพดาน 3,900 (อัปเดตใหญ่ พี่หมี 26 พ.ย. · ข้อแก้ก่อน: p95 4066 ท้าย/Negative โดนตัด)
ต้นเหตุ 2 ชั้น:
 ① ตัววัดวนคีย์ camVideoEN 'ไทม์แลปส์' เป็น "ตัวเลือกกล้อง" ทั้งที่บนจอไม่มีปุ่มนี้ (มาทาง arc เท่านั้น) ⇒ 4066 = เคสที่กดไม่ได้
    (แก้ที่ตัววัด easybear-showhow scripts/lab/prompt-clamp-matrix.ts) · เคสจริงยาวสุด = 3923 ยังเกิน
 ② ของซ้ำ/ขัดกันใน prompt (ตัดตรงนี้ ไม่แตะบท ไม่แตะคำห้ามเฉพาะอาการ):
    a. กล้องโหมดนิ่ง (ตั้งนิ่งเห็นทั้งพื้นที่ · มองจากด้านบน) มีบรรทัด CAMERA MODE "กล้องไม่ขยับ" อยู่แล้ว
       แต่ทุกฉากยังสั่ง "Camera: <ท่ากล้องเคลื่อน>" สวนกัน ⇒ โหมดนิ่ง 2 แบบนี้ไม่ใส่บรรทัดกล้องรายฉาก (30 จุด · 6 op)
    b. voiceVideoEN ซ้ำกับ VOICE LOCK (ขึ้นคู่กันเสมอ) — ตัดวงเล็บ "(adult man, never a female voice)" ที่ซ้ำ · คง MALE/FEMALE
    c. PRODUCT LOCK เกลาไวยากรณ์ (ทุกคำห้ามคงครบ: colour transparency shape size material label logo lettering parts
       redraw restyle cartoonify · unseen angles · invent nothing · props background ad text)
ใช้: python3 scripts/showhow-v141-video-trim.py  (รันบน v140 · รันซ้ำ = ไม่ทำอะไร)
"""
import json, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
s0 = open(P, encoding='utf-8').read()
c = json.loads(s0)
assert json.dumps(c, ensure_ascii=False, indent=1) + '\n' == s0
L = c['lookups']
if L['voiceVideoEN'].get('เสียงผู้ชาย') == 'warm friendly MALE voice-over':
    print('v141: ทำไปแล้ว — ไม่แตะ'); sys.exit(0)

FIXED = ['ตั้งนิ่งเห็นทั้งพื้นที่', 'มองจากด้านบน']
NOT_FIXED = [{'op': 'not', 'a': {'op': 'eq', 'a': '{item.camMode}', 'b': m}} for m in FIXED]
for m in FIXED: assert m in L['camVideoEN'], m

# a. บรรทัดกล้องรายฉาก
na = 0
def walk(x):
    global na
    if isinstance(x, dict):
        v = x.get('value')
        if 'when' in x and isinstance(v, dict) and v.get('op') == 'concat' and v.get('parts', [None])[0] == 'Camera: ':
            x['when'] = {'op': 'and', 'list': [x['when'], *NOT_FIXED]}; na += 1; return
        for y in x.values(): walk(y)
    elif isinstance(x, list):
        for y in x: walk(y)
for o in c['ops']:
    if o['id'].startswith('mnVideo'): walk(o['prompt'])
assert na == 30, na

# b. เสียงซ้ำ VOICE LOCK
VV = {'เสียงผู้หญิง': ('warm friendly FEMALE voice-over (adult woman, never a male voice)', 'warm friendly FEMALE voice-over'),
      'เสียงผู้ชาย': ('warm friendly MALE voice-over (adult man, never a female voice)', 'warm friendly MALE voice-over')}
for k, (old, new) in VV.items():
    assert L['voiceVideoEN'][k] == old, (k, L['voiceVideoEN'][k]); L['voiceVideoEN'][k] = new
    assert k in L['voiceLockEN']

# c. PRODUCT LOCK
OLD = "PRODUCT LOCK (overrides style): every product must be the exact object in the attached reference photo(s), each matching its own photo — never change colour, transparency, shape, size, material, label, logo, lettering or parts; never redraw, restyle or cartoonify; unseen angles = closest angle shown, invent nothing; copy only the product itself, never the props, background or ad text in its photo. "
NEW = "PRODUCT LOCK (overrides style): each product = the exact object in its own attached photo — never change colour, transparency, shape, size, material, label, logo, lettering or parts; never redraw, restyle or cartoonify; unseen angles = closest angle shown, invent nothing; copy only the product, never its photo's props, background or ad text. "
nc = 0
def walk2(x):
    global nc
    if isinstance(x, dict):
        for k, v in x.items():
            if v == OLD: x[k] = NEW; nc += 1
            else: walk2(v)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            if v == OLD: x[i] = NEW; nc += 1
            else: walk2(v)
for o in c['ops']:
    if o['id'].startswith('mnVideo'): walk2(o['prompt'])
assert nc == 6, nc
print(f'✅ v141: กล้องรายฉาก {na} จุด · เสียงซ้ำ 2 · PRODUCT LOCK {nc} op ({len(NEW) - len(OLD)} ตัว)')
open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
