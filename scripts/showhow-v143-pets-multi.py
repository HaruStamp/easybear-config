#!/usr/bin/env python3
"""showhow-v143 — ใส่ตัวละครและสัตว์เลี้ยง (หลายตัว) (อัปเดตใหญ่ พี่หมี 26 พ.ย. ข้อ 2 · ท่าเดียวกับ minimal-v62)
ของเดิม: ตัวละคร = รูปใบหน้า 1 รูป (characters ch1 slot face) · สัตว์ = แค่ "ผู้แสดงเป็นอะไร" ไม่มีรูป
ใหม่:
 - รูปสัตว์เลี้ยง 3 ช่อง เก็บที่ characters ch1 (pet1..pet3 · อัปครั้งเดียวใช้ทุกงาน เหมือนรูปหน้า)
 - จำนวนเป็นค่ากลาง values.svPets = '' / 1 / 2 / 3 + svPetDesc (ชื่อ/พันธุ์ ไม่บังคับ) ที่หน้าตั้งค่า (เหมือน minimal-v62)
   🪤 ไม่ทำเป็นค่ารายงาน: ยาม all-apps-safe ของ engine นับ ref ที่ gate ด้วย item.* = ติดมาเสมอ ⇒ ทางเดียวที่ "สัตว์ k ตัว แลกกับมุมเสริม k ใบ"
      นับได้จริงคือ gate ด้วย values (ยามไล่ค่า values ให้) · ค่ารายงานจะทำให้บอร์ด static 13 > 10 แดง
 - ใช้ร่วมกับตัวละคร/ล็อกหน้าอัตโนมัติ (mnFace) ได้ — รูปหน้า + รูปสัตว์ส่งคู่กัน
 ref (เพดาน: ภาพ 10 · Omni 7 · startFrame ทิ้ง refs) — showhow ให้ "บอร์ด = image 1" (prompt วิดีโอเขียนตามนี้ · Omni ตัดท้าย ⇒ บอร์ดต้องอยู่หน้า):
   บอร์ด : [บอร์ด] → สินค้า → ห้อง → หน้า → สัตว์ 1-3 → ภาพจบ  · มีสัตว์ k ตัว = ถอดรูปสินค้ามุมเสริมจากท้าย k ใบ (image5/4/3 · บอร์ด 2 ใบไม่มี image5 ⇒ ถอด image4/3/2)
   วิดีโอ: บอร์ด(+บอร์ดก่อน) → สินค้า → ห้อง → หน้า → สัตว์ 1-3 → มุมเสริม (โดนตัดที่ 7 ก่อน) · สัตว์ 3 ตัวในช่วง 2-6 = ถอดบอร์ดช่วงก่อน (ให้สัตว์ครบใน 7)
   ปก   : บอร์ด → สินค้า → หน้า → สัตว์ 1-3
 prompt (สั้นที่สุด — วิดีโอเหลือที่ ~105 ตัว): 1 ประโยคต่อท้ายบล็อกผู้แสดง (วิดีโอ EN · บอร์ด TH · ปก EN) + บรรทัดบท mnPlan
ใช้: python3 scripts/showhow-v143-pets-multi.py  (รันบน v142 · รันซ้ำ = ไม่ทำอะไร)
"""
import json, sys, copy
P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
s0 = open(P, encoding='utf-8').read()
c = json.loads(s0)
assert json.dumps(c, ensure_ascii=False, indent=1) + '\n' == s0
C = c['collections']; L = c['lookups']; O = {o['id']: o for o in c['ops']}
if 'svPets' in c['values']:
    print('v143: ทำไปแล้ว — ไม่แตะ'); sys.exit(0)
def eq(a, b): return {'op': 'eq', 'a': a, 'b': b}
def NOT(x): return {'op': 'not', 'a': x}
def AND(*x): return {'op': 'and', 'list': list(x)}
def OR(*x): return {'op': 'or', 'list': list(x)}
PETS = '{values.svPets}'
ON = {1: NOT(eq(PETS, '')), 2: OR(eq(PETS, '2'), eq(PETS, '3')), 3: eq(PETS, '3')}
FEWER = {1: eq(PETS, ''), 2: OR(eq(PETS, ''), eq(PETS, '1')), 3: NOT(eq(PETS, '3'))}   # มุมเสริมใบที่ k จากท้าย อยู่ได้เมื่อสัตว์ < k ตัว

# ── ข้อมูล ──
for k in (1, 2, 3):
    if 'pet%d' % k not in C['characters']['slots']: C['characters']['slots'].append('pet%d' % k)
c['values'].update({'svPets': '', 'svPetDesc': ''})

# ── ข้อความ ──
L['petVideoEN'] = {'1': ' PET: the animal in the pet photo, exact (breed, fur, markings).',
                   '2': ' PETS: only the 2 animals in the pet photos, each exact (breed, fur, markings).',
                   '3': ' PETS: only the 3 animals in the pet photos, each exact (breed, fur, markings).'}
L['petBoard'] = {'1': ' · สัตว์เลี้ยง 1 ตัวตามรูปสัตว์ที่แนบ ตรงพันธุ์ สีขน ลาย',
                 '2': ' · สัตว์เลี้ยง 2 ตัวตามรูปสัตว์ที่แนบเท่านั้น แต่ละตัวตรงพันธุ์ สีขน ลาย',
                 '3': ' · สัตว์เลี้ยง 3 ตัวตามรูปสัตว์ที่แนบเท่านั้น แต่ละตัวตรงพันธุ์ สีขน ลาย'}
L['petCoverEN'] = {'1': 'Include the pet from the pet photo, exactly as photographed. ',
                   '2': 'Include the 2 pets from the pet photos, each exactly as photographed. ',
                   '3': 'Include the 3 pets from the pet photos, each exactly as photographed. '}
def blk(table): return {'op': 'block', 'sep': '', 'parts': [{'when': ON[1], 'value': {'op': 'lookup', 'table': table, 'key': PETS, 'fallback': ''}}]}
MIC = ' Collar clip-on mic.'
nv = nb = 0
for o in c['ops']:
    pr = o.get('prompt'); ps = pr.get('parts') if isinstance(pr, dict) else None
    if not ps: continue
    if o['id'].startswith('mnVideo'):
        i = next(i for i, p in enumerate(ps) if MIC in json.dumps(p, ensure_ascii=False))
        ps.insert(i + 1, blk('petVideoEN')); nv += 1
    elif o['id'].startswith('mnBoard'):
        i = ps.index('\nตัวหนังสือบนภาพ: ')
        ps.insert(i, blk('petBoard')); nb += 1
assert nv == 6 and nb == 6, (nv, nb)
cv = O['mnCover']['prompt']['parts']
cv.insert(next(i for i, p in enumerate(cv) if p == 'Look: '), blk('petCoverEN'))
# บท: บอกจำนวน + คำผู้ใช้ (บทไม่เห็นรูปสัตว์ — ไม่ส่งรูปเข้า mnPlan กัน "รูปสุดท้าย = หน้า" เพี้ยน)
pl = O['mnPlan']['prompt']['parts']
i = next(i for i, p in enumerate(pl) if '{item.charLook}' in json.dumps(p, ensure_ascii=False))
pl.insert(i + 1, {'op': 'block', 'sep': '', 'parts': [{'when': ON[1], 'value': {'op': 'concat', 'parts': [
    '\nสัตว์เลี้ยงร่วมแสดง {values.svPets} ตัว (ผู้ใช้แนบรูปให้ขั้นวาดภาพแล้ว', {'op': 'block', 'sep': '', 'parts': [{'when': 'values.svPetDesc!=', 'value': ' · ผู้ใช้บอก: {values.svPetDesc}'}]},
    ') — ทุกคลิปมีน้องครบ {values.svPets} ตัวในฉากที่เหมาะ อยู่คู่กับงาน/ผู้แสดงอย่างเป็นธรรมชาติ ไม่บังงาน · s*en ที่มีน้องเรียก "the pet(s) from the photo" ห้ามแต่งพันธุ์/สีเอง · ทับกฎ "สัตว์ตัวเดียว" เฉพาะน้องจากรูป ห้ามเพิ่มสัตว์อื่น']}}]})

# ── ref ──
PET = lambda k: {'from': 'characters', 'by': '{values.charId}', 'slot': 'pet%d' % k, 'when': ON[k]}
def strpred(w):   # when แบบข้อความซ้อนใน and = จริงเสมอ (ยาม G21) ⇒ แปลงเป็น object ก่อนห่อ
    if not isinstance(w, str): return w
    assert w == 'values.svSec>10', w
    return {'op': 'not', 'a': {'op': 'lte', 'a': '{values.svSec}', 'b': '10'}}
def gate(a, w):
    a['when'] = AND(strpred(a['when']), w) if a.get('when') else w
for o in c['ops']:
    r = o.get('refs')
    if not (isinstance(r, dict) and r.get('op') == 'lookupRefs'): continue
    al = r['also']
    if o['id'].startswith('mnBoard') or o['id'].startswith('mnVideo'):
        last_face = max(i for i, a in enumerate(al) if a['slot'] == 'face')
        for k in (3, 2, 1): al.insert(last_face + 1, PET(k))
    if o['id'].startswith('mnBoard'):
        imgs = [a for a in al if a['from'] == 'products' and a['slot'] in ('image2', 'image3', 'image4', 'image5')]
        for k, a in zip((1, 2, 3), reversed(imgs)): gate(a, FEWER[k])
    if o['id'] in ('mnVideo2', 'mnVideo3', 'mnVideo4', 'mnVideo5', 'mnVideo6'):
        prev = al[0]; assert prev['from'] == 'tasks' and prev['slot'].startswith('board'), prev
        gate(prev, FEWER[3])
    if o['id'] == 'mnCover':
        for k in (1, 2, 3): al.append(PET(k))

# ── UI: หน้าตั้งค่า ต่อจากการ์ดเสียง (ค่ากลาง) ──
box = c['phases'][0]['form'][2]['card'][0]['card'][0]['card'][4]['card'][2]
face_box = box['card'][20]
assert face_box['card'][0]['card'][2]['el'] == 'repeat'
slot_tpl = face_box['card'][0]['card'][2]['card'][0]['card'][0]   # กล่อง 1 ช่องรูป (มีรูป/ปุ่มอัป)
def slot_box(k):
    s = json.dumps(slot_tpl, ensure_ascii=False).replace('item.slots.face', 'item.slots.pet%d' % k).replace('"to": "face"', '"to": "pet%d"' % k).replace('"into": "face"', '"into": "pet%d"' % k)
    return json.loads(s)
SET = c['phases'][0]['form'][0]['card'][0]['card'][3]
audio_card = next(x for x in SET['card'] if '"svAudio"' in json.dumps(x, ensure_ascii=False))
pet_card = copy.deepcopy(audio_card)   # ใช้กรอบ+หัวการ์ดเดียวกับการ์ดเสียง
head = pet_card['card'][0]
hs = json.dumps(head, ensure_ascii=False)
LBL = "!text-[13px] @[640px]:!text-[12.5px] opacity-60 px-0.5 mt-1"
HINT = "!text-[13px] @[640px]:!text-[12.5px] opacity-50 px-0.5 leading-snug"
def retitle(n):
    if isinstance(n, dict):
        if n.get('el') == 'icon': n['icon'] = 'pets'
        if n.get('el') == 'text' and isinstance(n.get('value'), str): n['value'] = '' 
        for v in n.values(): retitle(v)
    elif isinstance(n, list):
        for v in n: retitle(v)
retitle(head)
texts = []
def collect(n):
    if isinstance(n, dict):
        if n.get('el') == 'text': texts.append(n)
        for v in n.values(): collect(v)
    elif isinstance(n, list):
        for v in n: collect(v)
collect(head)
texts[0]['value'] = 'สัตว์เลี้ยงร่วมแสดง'
for t in texts[1:]: t['value'] = 'ไม่บังคับ'
pet_card['card'] = [head,
    {'el': 'text', 'value': 'ใส่น้องจากรูปจริงได้สูงสุด 3 ตัว ใช้กับทุกงาน · ใช้คู่กับรูปใบหน้าตัวละครได้ · มีน้องกี่ตัว รูปสินค้ามุมเสริมบนบอร์ดลดลงเท่านั้น (รูปหลักยังอยู่)', 'className': HINT},
    {'el': 'grid-select', 'field': 'svPets', 'cols': 4, 'mobile': {'cols': 2}, 'contained': True, 'className': '!min-h-[44px] @[420px]:!min-h-0', 'options': [
        {'value': '', 'label': 'ไม่มี', 'icon': 'block'}, {'value': '1', 'label': '1 ตัว', 'icon': 'pets'},
        {'value': '2', 'label': '2 ตัว', 'icon': 'pets'}, {'value': '3', 'label': '3 ตัว', 'icon': 'pets'}]},
    {'el': 'box', 'className': 'flex flex-col gap-2', 'when': NOT(eq('{values.svPets}', '')), 'card': [
        {'el': 'text', 'value': 'แนบรูปน้องตามจำนวนที่เลือก (เรียงช่อง 1 → 3)', 'className': LBL},
        {'el': 'repeat', 'coll': 'characters', 'where': 'id={values.charId}', 'card': [{'el': 'box', 'className': 'flex flex-row flex-wrap gap-2.5 mt-0.5', 'card': [slot_box(k) for k in (1, 2, 3)]}]},
        {'el': 'input', 'field': 'svPetDesc', 'placeholder': 'ชื่อ/พันธุ์ (ไม่บังคับ) เช่น แมวส้มชื่อส้มโอ + หมาชิบะ',
         'className': '!text-[16px] @[640px]:!text-[15px] !rounded-xl !px-3.5 !py-3 @[640px]:!py-2.5 border-[var(--ev-border)] !min-h-[48px] @[420px]:!min-h-0'}]}]
SET['card'].insert(SET['card'].index(audio_card) + 1, pet_card)
print(f'✅ v143: สัตว์ 3 ช่อง · วิดีโอ {nv} · บอร์ด {nb} · ปก · บท · UI')
open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
