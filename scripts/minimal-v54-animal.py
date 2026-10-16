#!/usr/bin/env python3
"""minimal v54 — หัวข้อ "ตัวละครในคลิป" แบบ showhow: เห็นแค่ไหน × เป็นอะไร × ตัวละคร (ลูกค้าขอสัตว์จริง · พี่หมีสั่ง 2026-10-16 "เอาแบบ showhow เป๊ะ ๆ")

UI (โครงเดียวกับ showhow `people` / `castKind` / `peopleSrc`):
  ① ผู้แสดงเห็นแค่ไหน = field เดิม `svChar` ขยายจาก 2 → 4 ตัวเลือก (พี่หมีตัด "เห็นตัว ไม่เห็นหน้า" กับ "หลายคน" ของ showhow ออก)
       อัตโนมัติ · เห็นแค่มือ · เห็นเต็มตัว (= ค่าเดิม "มีพรีเซนเตอร์ไทย 1 คนในคลิป") · ไม่มีผู้แสดง (= ค่าเดิม "ไม่มีคนในคลิป …")
       ⇒ ค่าเดิม 2 ตัวยังเป็นสตริงเดิม ไฟล์เซฟเก่าเข้าที่ถูกเอง · ค่าปริยายยังเป็น "ไม่มีผู้แสดง"
  ② ผู้แสดงเป็นอะไร = `svCast` ใหม่ (โผล่เมื่อไม่ใช่ "ไม่มีผู้แสดง") · อัตโนมัติ · คน ('' = ค่าปริยาย = พฤติกรรมเดิม) · สัตว์จริง · สัตว์ทำตัวเหมือนคน · สัตว์เลี้ยง + เจ้าของ
  ③ ตัวละคร = `svCharSrc` เดิม (โผล่เมื่อเห็นเต็มตัว) · สุ่ม / ใช้รูป · แผงคนเดิม หรือแผงสัตว์ (ป้ายใหม่) ตามข้อ ② · ช่อง "ชนิด / สายพันธุ์" (`charAnimal`) โผล่เมื่อเป็นสัตว์

prompt (ถ้อยคำปรับจาก showhow ให้เป็นโฆษณาสินค้า — showhow เป็น "ผู้ลงมือทำงาน ห้ามมองกล้อง" แต่ minimal เป็นพรีเซนเตอร์/สินค้าเด่น):
  · ตาราง charPlan/charBoard/charVideoEN เพิ่มแถวของระดับการเห็นใหม่ 2 ตัว
  · เห็นเต็มตัว + สัตว์ → แทนแถวคนทั้งแถวด้วย charPlanPet/charBoardPet/charVideoPetEN (key = {svCast}|{svCharSrc}) — ไม่ใช้ "ทับกฎคน" เพราะแถวคนเต็มตัวพูดถึงพรีเซนเตอร์ไทยแรงเกินจะทับ
  · ระดับอื่น + สัตว์ → แถวระดับการเห็นเดิม + ต่อท้าย castPlan/castBoard/castVideoEN ("★ ทับกฎคนด้านบน" แบบ showhow)
  · ผู้แสดงเป็นอะไร = อัตโนมัติ → ต่อท้าย castPlan บรรทัดเดียว (บอร์ด/วิดีโอตามบท)
  🛡 svCast ว่าง/ไม่มี (ไฟล์เซฟเก่า) + ค่า svChar เดิม 2 ตัว = prompt เดิมทุกไบต์ (ยาม: scratch verify.ts resolve จริงเทียบ)
  🛡 ห่อด้วย block ในตำแหน่งเดิม ไม่แทรก part ใหม่ ⇒ ดัชนี part ไม่เลื่อน
  🪤 ความยาวแถวสัตว์ ≤ แถวคน (ยาม ② push-minimal) · ตารางเก็บข้อความนิ่ง ห้ามใส่ {values.*}
รันซ้ำได้ (เจอ svCast แล้ว = ข้าม)
"""
import json, os, copy

PATH = os.path.join(os.path.dirname(__file__), '..', 'minimal-dev.json')
cfg = json.load(open(PATH, encoding='utf-8'))

NONE = 'ไม่มีคนในคลิป — โฟกัสสินค้าล้วน'
HUMAN = 'มีพรีเซนเตอร์ไทย 1 คนในคลิป'
AUTO_V = 'ให้ AI เลือกว่าจะเห็นผู้แสดงแค่ไหน'
HANDS = 'เห็นแต่มือ ไม่เห็นหน้า'
AI = 'AI เลือกนาย/นางแบบให้เหมาะกับสินค้า'
PHOTO = 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'
C_AUTO, C_REAL, C_ANTHRO, C_PET = 'อัตโนมัติ', 'สัตว์จริง', 'สัตว์ทำตัวเหมือนคน', 'สัตว์เลี้ยง + เจ้าของ'
ANIMALS = (C_REAL, C_ANTHRO, C_PET)


def eq(f, v): return {'op': 'eq', 'a': '{values.%s}' % f, 'b': v}
def NOT(x): return {'op': 'not', 'a': x}
def AND(*x): return {'op': 'and', 'list': list(x)}
def OR(*x): return {'op': 'or', 'list': list(x)}

SHOWN = NOT(eq('svChar', NONE))
ANIMAL_CAST = OR(*[eq('svCast', c) for c in ANIMALS])
PET_ACTIVE = AND(SHOWN, ANIMAL_CAST)
PET_FULL = AND(eq('svChar', HUMAN), ANIMAL_CAST)
PET_PART = AND(PET_ACTIVE, NOT(eq('svChar', HUMAN)))
AUTO_CAST = AND(SHOWN, eq('svCast', C_AUTO))

# ── ระดับการเห็นใหม่ (ทั้ง 2 key ของ svCharSrc ได้แถวเดียวกัน — รูปใช้เฉพาะเห็นเต็มตัว)
VIS_PLAN = {
    AUTO_V: 'กฎพรีเซนเตอร์: เลือกเองว่าจะให้เห็นผู้แสดงแค่ไหนให้เข้ากับสินค้า (ไม่มีคน / เห็นแต่มือ / พรีเซนเตอร์ 1 คน) — สินค้าที่ต้องสาธิตให้เห็นมือใช้งาน · สินค้าแฟชั่น/บิวตี้มีพรีเซนเตอร์ได้ · เลือกแล้วใช้แบบเดียวกันทุกฉากทุกคลิป · สินค้ายังเป็นจุดโฟกัสหลัก',
    HANDS: 'กฎพรีเซนเตอร์: เห็นแต่มือและแขนของผู้แสดง ห้ามเห็นหน้า ศีรษะ ไหล่ หรือตัวเต็ม — มือถือ/ใช้/สาธิตสินค้าอย่างเป็นธรรมชาติ (ฉากโชว์สินค้าเดี่ยวไม่มีมือได้) · ห้ามมุม over-the-shoulder หรือมุมที่ติดศีรษะ · s*en เขียนว่า hands only ห้ามใช้คำ woman/man/person (คลิปจริง S4: "woman\'s hands" + over-the-shoulder = ได้หน้าคนเต็ม ๆ)',
}
VIS_BOARD = {
    AUTO_V: 'ผู้แสดงในภาพตามบท แบบเดียวกันทุกช่อง สินค้าเด่นกว่าคนเสมอ',
    HANDS: 'เห็นแต่มือ/แขนที่ถือหรือใช้สินค้า ห้ามมีใบหน้า ศีรษะ ไหล่ หรือตัวเต็มในทุกช่อง',
}
VIS_VIDEO = {
    AUTO_V: 'People: exactly as written in each scene, identical across every shot; the product stays the focus.',
    HANDS: "Hands only: hands and forearms holding or using the product; never a face, head, shoulders or body; natural hands, correct fingers.",
}

# ── ต่อท้าย (ระดับการเห็นอื่นที่ไม่ใช่เต็มตัว + สัตว์ · หรือ อัตโนมัติ)
CAST_PLAN = {
    C_AUTO: '★ ผู้แสดงเป็นคนหรือสัตว์: เลือกเองให้เข้ากับสินค้า (สินค้าสัตว์เลี้ยง = สัตว์เลี้ยง · อื่น ๆ = คน) เลือกแล้วใช้แบบเดียวทุกฉากทุกคลิป',
    C_REAL: '★ ทับกฎคนด้านบน: ผู้แสดงเป็นสัตว์จริง 1 ตัว ไม่ใช่คน — เดิน 4 ขา ไม่ใส่เสื้อผ้า ไม่พูด "มือ" = อุ้งเท้า · คำที่พูดถึงคนไทย/ใบหน้าคน/มือคน ให้ข้ามทั้งหมด · ระบุชนิดและสีของน้องให้ตรงกันทุกฉาก',
    C_ANTHRO: '★ ทับกฎคนด้านบน: ผู้แสดงเป็นสัตว์ที่ทำตัวเหมือนคน 1 ตัว — ยืน/นั่งตัวตรง ใช้อุ้งเท้าหน้าแทนมือ ใส่เสื้อผ้า ขนฟู ตากลมโต · คำที่พูดถึงคนไทย/ใบหน้าคน/มือคน ให้ข้ามทั้งหมด · ระบุชนิดและสีให้ตรงกันทุกฉาก',
    C_PET: '★ ทับกฎคนด้านบน: ตัวเอกเป็นสัตว์เลี้ยง 1 ตัว ตัวเดิมทุกฉาก · คนในคลิปมีแค่เจ้าของ 1 คนที่ใช้สินค้ากับน้อง (เห็นแค่ระดับที่กำหนดด้านบน) · ฉากปิดเป็นน้องคู่กับสินค้า',
}
CAST_BOARD = {
    C_REAL: 'ผู้แสดงเป็นสัตว์จริงตัวเดิมทุกช่อง เดิน 4 ขา ไม่ใส่เสื้อผ้า มือ = อุ้งเท้า ห้ามวาดคน',
    C_ANTHRO: 'ผู้แสดงเป็นสัตว์ทำตัวเหมือนคนตัวเดิมทุกช่อง ยืนตัวตรง ใส่เสื้อผ้า ห้ามวาดคน',
    C_PET: 'ตัวเอกเป็นสัตว์เลี้ยงตัวเดิมทุกช่อง เจ้าของใช้สินค้ากับน้อง',
}
CAST_VIDEO = {
    C_REAL: 'The performer is ONE real animal, not a person (overrides any person wording): four legs, no clothes, paws for hands, never talks.',
    C_ANTHRO: 'The performer is ONE animal acting like a person (overrides any person wording): upright, clothed, front paws as hands, big round eyes.',
    C_PET: 'ONE pet is the star, the same one every scene, with cute clear reactions; its owner uses the product on it; no second pet.',
}

# ── เห็นเต็มตัว + สัตว์ (แทนแถวคนทั้งแถว)
def pp(core, extra): return core + ' · ' + extra
PAI = 'ชนิดสัตว์: ถ้าผู้ใช้ไม่ระบุ ให้เลือกให้เข้ากับสินค้าและกลุ่มเป้าหมาย (เช่น แมว สุนัข กระต่าย) เลือกแล้วใช้ตัวเดิมทุกคลิป'
PPH = 'ใช้น้องจากรูปที่แนบเป็นตัวเดิมทุกฉากทุกคลิป ห้ามเปลี่ยนตัว ห้ามเปลี่ยนชนิด สี หรือลายขน'
CORE = {
    C_REAL: ('กฎตัวละคร: ตัวละครคือ **สัตว์จริง 1 ตัว** ตัวเดิมทุกฉากทุกคลิป ห้ามมีตัวที่สอง — เดิน 4 ขา ท่าทางและสัดส่วนแบบสัตว์จริง ไม่ใส่เสื้อผ้า ไม่ยืน 2 ขา ไม่ถือของด้วยอุ้งเท้า ไม่พูด · '
             'น้องอยู่คู่กับสินค้าอย่างเป็นธรรมชาติ (ดม เดินผ่าน นั่งข้าง นอนบน เล่นใกล้ ๆ) สินค้ายังเป็นจุดโฟกัสหลัก ห้ามบังหรือทำให้สินค้าผิดรูป · ไม่มีคนในคลิป (มือคนโผล่สั้น ๆ ได้เฉพาะฉากสาธิตที่จำเป็น) · '
             'บทพากย์ vo เป็นผู้บรรยาย ไม่ใช่เสียงสัตว์ · s*th/s*en ทุกฉากระบุชนิดและสีของน้องให้ตรงกัน'),
    C_ANTHRO: ('กฎตัวละคร: ตัวละครคือ **สัตว์ที่ทำตัวเหมือนคน 1 ตัว** ตัวเดิมทุกฉากทุกคลิป ห้ามมีตัวที่สอง — ยืน/นั่งตัวตรง ใช้อุ้งเท้าหน้าแทนมือ ใส่เสื้อผ้า ขนฟู ตากลมโต เป็นพรีเซนเตอร์ถือ/ใช้/รีวิวสินค้าได้ มองกล้องได้ · '
               'สินค้ายังเป็นจุดโฟกัสหลัก ห้ามทำให้สินค้าผิดรูป · ไม่มีคนในคลิป · บทพากย์ vo เป็นผู้บรรยาย ปากไม่ขยับตามบท · s*th/s*en ทุกฉากระบุชนิด สี และชุดให้ตรงกัน'),
    C_PET: ('กฎตัวละคร: ตัวเอกคือ **สัตว์เลี้ยง 1 ตัว** ตัวเดิมทุกฉากทุกคลิป — ขนฟู ตากลมโต ทำหน้าทำตาตอบสนองชัด มองกล้องได้ · คนลงมือคือ **เจ้าของ 1 คน** ใช้สินค้ากับน้อง เห็นมือ/ลำตัว ไม่ต้องเห็นหน้าชัด · '
            'เล่า: น้องมีปัญหา/อยากได้ → เจ้าของใช้สินค้า → น้องสบาย มีความสุข · ฉากปิดเป็นน้องคู่กับสินค้า · s*th/s*en ทุกฉากให้น้องเป็นจุดสนใจ ระบุชนิดและสีให้ตรงกัน'),
}
PLAN_PET = {c + '|' + AI: pp(CORE[c], PAI) for c in ANIMALS}
PLAN_PET.update({c + '|' + PHOTO: pp(CORE[c], PPH) for c in ANIMALS})
BOARD_PET = {
    C_REAL + '|' + AI: 'สัตว์จริง 1 ตัวตามบท ตัวเดียวกันทุกช่อง เดิน 4 ขา ไม่ใส่เสื้อผ้า ห้ามวาดคน สินค้าเด่นกว่าสัตว์เสมอ',
    C_REAL + '|' + PHOTO: 'ใช้สัตว์จากภาพที่แนบมา (character reference) ตัวเดียวกันทุกช่อง — ล็อกชนิด สายพันธุ์ สีและลายขน 100% เดิน 4 ขา ไม่ใส่เสื้อผ้า ห้ามวาดคน สินค้าเด่นกว่าสัตว์เสมอ',
    C_ANTHRO + '|' + AI: 'สัตว์ทำตัวเหมือนคน 1 ตัวตามบท ตัวเดียวกันทุกช่อง ยืนตัวตรง ใส่เสื้อผ้า ห้ามวาดคน สินค้าเด่นเสมอ',
    C_ANTHRO + '|' + PHOTO: 'ใช้สัตว์จากภาพที่แนบมา (character reference) ตัวเดียวกันทุกช่อง — ล็อกชนิด สีและลายขน 100% ยืนตัวตรง ใส่เสื้อผ้า ใช้อุ้งเท้าแทนมือ ห้ามวาดคน สินค้าเด่นเสมอ',
    C_PET + '|' + AI: 'สัตว์เลี้ยง 1 ตัวเป็นตัวเอก ตัวเดียวกันทุกช่อง · เจ้าของ 1 คนเห็นมือ/ลำตัว ไม่เน้นหน้า',
    C_PET + '|' + PHOTO: 'ใช้สัตว์เลี้ยงจากภาพที่แนบมา (character reference) ตัวเดียวกันทุกช่อง ล็อกชนิด สีและลายขน 100% · เจ้าของ 1 คนเห็นมือ/ลำตัว ไม่เน้นหน้า',
}
VC = 'natural four-legged anatomy, no clothes, never upright or talking; no people; product stays the focus.'
VIDEO_PET = {
    C_REAL + '|' + AI: 'MAIN CHARACTER: ONE real animal, the same one in every scene, interacting naturally with the product and never hiding it; ' + VC,
    C_REAL + '|' + PHOTO: 'CHARACTER CONSISTENCY (HIGHEST PRIORITY): the exact animal from the attached reference image in every shot (same species, breed, fur colour, markings), never another animal; ' + VC,
    C_ANTHRO + '|' + AI: 'MAIN CHARACTER: ONE animal acting like a person, the same one in every scene: upright, clothed, front paws as hands, big round eyes, presenting the product; no people.',
    C_ANTHRO + '|' + PHOTO: 'CHARACTER CONSISTENCY (HIGHEST PRIORITY): the exact animal from the attached reference image in every shot (same species, fur colour, markings), acting like a person: upright, clothed, paws as hands; no people.',
    C_PET + '|' + AI: 'MAIN CHARACTER: ONE pet, the same one in every scene, cute clear reactions, may look at camera; its owner (hands/torso, face not the focus) uses the product on it.',
    C_PET + '|' + PHOTO: 'CHARACTER CONSISTENCY (HIGHEST PRIORITY): the exact pet from the attached reference image in every shot (same species, fur colour, markings); its owner (hands/torso only) uses the product on it.',
}

if 'svCast' in cfg['values']:
    print('⏭ v54 แพตช์ไปแล้ว — ไม่ทำซ้ำ'); raise SystemExit(0)

L = cfg['lookups']
for v in VIS_PLAN:
    for s in (AI, PHOTO):
        L['charPlan'][v + '|' + s] = VIS_PLAN[v]
        L['charBoard'][v + '|' + s] = VIS_BOARD[v]
        L['charVideoEN'][v + '|' + s] = VIS_VIDEO[v]
L['castPlan'], L['castBoard'], L['castVideoEN'] = CAST_PLAN, CAST_BOARD, CAST_VIDEO
L['charPlanPet'], L['charBoardPet'], L['charVideoPetEN'] = PLAN_PET, BOARD_PET, VIDEO_PET
for c in ANIMALS:   # สัตว์เต็มตัวต้องไม่ยาวกว่าคนเต็มตัว
    for s in (AI, PHOTO):
        assert len(BOARD_PET[c + '|' + s]) <= len(L['charBoard'][HUMAN + '|' + s]), ('board', c, s, len(BOARD_PET[c + '|' + s]))
        assert len(VIDEO_PET[c + '|' + s]) <= len(L['charVideoEN'][HUMAN + '|' + s]), ('video', c, s, len(VIDEO_PET[c + '|' + s]))
for v in VIS_VIDEO:   # ระดับอื่น + สัตว์ (แถว + ต่อท้าย) ต้องไม่ยาวกว่าคนแบบใช้รูป
    for c in ANIMALS:
        assert len(VIS_VIDEO[v]) + 1 + len(CAST_VIDEO[c]) <= len(L['charVideoEN'][HUMAN + '|' + PHOTO]), ('video+cast', v, c)
        assert len(VIS_BOARD[v]) + 3 + len(CAST_BOARD[c]) <= len(L['charBoard'][HUMAN + '|' + PHOTO]), ('board+cast', v, c)


def lk(t, key): return {'op': 'lookup', 'table': t, 'key': key, 'fallback': ''}
OLDKEY = '{values.svChar}|{values.svCharSrc}'
PETKEY = '{values.svCast}|{values.svCharSrc}'


def chooser(old, pet, tail=None, auto_tail=None):
    parts = [{'when': NOT(PET_FULL), 'value': old}, {'when': PET_FULL, 'value': pet}]
    if tail: parts.append({'when': PET_PART, 'value': tail})
    if auto_tail: parts.append({'when': AUTO_CAST, 'value': auto_tail})
    return {'op': 'block', 'sep': '', 'parts': parts}

ops = {o['id']: o for o in cfg['ops']}
sp = ops['mnPlan']['systemInstruction']['parts']
assert sp[23] == '\n\nโหมดพรีเซนเตอร์: {values.svChar}\n' and sp[24] == lk('charPlan', OLDKEY), sp[23]
assert sp[26].startswith('ข้อมูลพรีเซนเตอร์จากผู้ใช้')
CAST_TAIL_PLAN = {'op': 'concat', 'parts': ['\n', lk('castPlan', '{values.svCast}')]}
sp[23] = chooser(sp[23], '\n\nตัวละครในคลิป: {values.svCast} 1 ตัว\n')
sp[24] = chooser(sp[24], lk('charPlanPet', PETKEY), CAST_TAIL_PLAN, CAST_TAIL_PLAN)
sp[26] = {'op': 'block', 'sep': '', 'parts': [{'when': NOT(PET_ACTIVE), 'value': sp[26]},
          {'when': PET_ACTIVE, 'value': 'ข้อมูลสัตว์จากผู้ใช้ (ค่าว่าง = AI เลือกให้): ชนิด/สายพันธุ์ {values.charAnimal}'}]}
for oid in ('mnBoard', 'mnBoard2', 'mnBoard3'):
    p = ops[oid]['prompt']['parts']
    assert p[5] == 'พรีเซนเตอร์: {values.svChar} — ' and p[6] == lk('charBoard', OLDKEY), oid
    p[5] = chooser(p[5], 'ตัวละคร: {values.svCast} 1 ตัว — ')
    p[6] = chooser(p[6], lk('charBoardPet', PETKEY), {'op': 'concat', 'parts': [' · ', lk('castBoard', '{values.svCast}')]})
for oid in ('mnVideo', 'mnVideo2', 'mnVideo3'):
    p = ops[oid]['prompt']['parts']
    assert p[2] == lk('charVideoEN', OLDKEY), oid
    p[2] = chooser(p[2], lk('charVideoPetEN', PETKEY), {'op': 'concat', 'parts': [' ', lk('castVideoEN', '{values.svCast}')]})

# ── UI
sec = cfg['phases'][0]['form'][0]['card'][0]['card'][2]['card'][1]
sel = sec['card'][2]
assert sel.get('field') == 'svChar' and [o['value'] for o in sel['options']] == [NONE, HUMAN]
human = sec['card'][3]
assert human['when'] == eq('svChar', HUMAN), human['when']
kids = human['card']
assert kids[0].get('field') == 'svCharSrc' and len(kids) == 4
lbl_cls = kids[2]['className']
def label(t, when=None):
    n = {'el': 'text', 'value': t, 'className': lbl_cls}
    if when: n['when'] = when
    return n

sec['card'][1]['value'] = 'ใครอยู่กับสินค้าในคลิป และเห็นแค่ไหน — มีผลทั้งภาพสตอรีบอร์ดและวิดีโอจริง'
sel['options'] = [
    {'value': AUTO_V, 'label': 'อัตโนมัติ', 'desc': 'หมีเลือกให้เข้ากับสินค้า', 'icon': 'auto_awesome'},
    {'value': HANDS, 'label': 'เห็นแค่มือ', 'desc': 'มือหรืออุ้งเท้า · ไม่เห็นหน้า', 'icon': 'back_hand'},
    {'value': HUMAN, 'label': 'เห็นเต็มตัว', 'desc': 'พรีเซนเตอร์ 1 คนหรือ 1 ตัว', 'icon': 'person'},
    {'value': NONE, 'label': 'ไม่มีผู้แสดง', 'desc': 'เห็นแต่สินค้า', 'icon': 'no_accounts'},
]
castSel = {'el': 'grid-select', 'field': 'svCast', 'cols': 2, 'contained': True, 'className': sel['className'], 'when': SHOWN,
           'options': [{'value': C_AUTO, 'label': 'อัตโนมัติ', 'desc': 'หมีเลือกให้ตามสินค้า', 'icon': 'auto_awesome'},
                       {'value': '', 'label': 'คน', 'desc': 'คนจริงถือ/ใช้สินค้า', 'icon': 'person'},
                       {'value': C_REAL, 'label': 'สัตว์จริง', 'desc': 'เดิน 4 ขา แบบสัตว์จริง', 'icon': 'pets'},
                       {'value': C_ANTHRO, 'label': 'สัตว์ทำตัวเหมือนคน', 'desc': 'ยืน 2 ขา ใส่เสื้อผ้า', 'icon': 'emoji_nature'},
                       {'value': C_PET, 'label': 'สัตว์เลี้ยง + เจ้าของ', 'desc': 'น้องเป็นตัวเอก เจ้าของใช้สินค้า', 'icon': 'volunteer_activism'}]}

# ช่องชนิดสัตว์ (ทุกระดับที่เห็นสัตว์) — สำเนาโครงช่องชื่อเล่น
hints = kids[3]
nameBox = copy.deepcopy(hints['card'][0])
assert nameBox['card'][1]['field'] == 'charName'
nameBox['card'][0].update(value='ชนิด / สายพันธุ์ (ไม่บังคับ)', icon='pets')
nameBox['card'][1].update(field='charAnimal', placeholder='เช่น แมวส้ม · คอร์กี้ · กระต่ายขาว')
speciesBox = {'el': 'box', 'className': hints['className'], 'when': PET_ACTIVE, 'card': [nameBox]}

# แผงสัตว์ของ "ตัวละคร" (สุ่ม/ใช้รูป) — สำเนาแผงคน ป้ายใหม่ ไม่มีช่องบอกใบ้ของคน
pet = copy.deepcopy(kids[:2])
src = pet[0]
assert [o['value'] for o in src['options']] == [AI, PHOTO]
src['options'][0].update(label='สุ่มตัวละคร', desc='หมีสร้างน้องให้เหมาะกับสินค้า', icon='shuffle')
src['options'][1].update(label='ใช้รูปน้องของฉัน', desc='ล็อกตามรูปที่แนบ — ตัวเดิมทุกช็อต', icon='pets')
TEXTS = {
    'ยังไม่มีรูปใบหน้า': 'ยังไม่มีรูปน้อง',
    'แนบรูปหน้าตรง เห็นใบหน้าชัด 1 รูป — ระบบล็อกหน้าให้เป็นคนเดิมทุกช็อต': 'แนบรูปน้องเห็นหน้าและลำตัวชัด 1 รูป — ระบบล็อกให้เป็นตัวเดิมทุกช็อต',
    'ได้ตัวละครแล้ว — ล็อกหน้าตามรูปนี้': 'ได้รูปน้องแล้ว — ล็อกตามรูปนี้',
    'ระบบแนบรูปนี้ให้ตอนวาดภาพและทำวิดีโอ เป็นคนเดิมทุกช็อต ทุกคลิป ทุกรอบผลิต': 'ระบบแนบรูปนี้ให้ตอนวาดภาพและทำวิดีโอ เป็นตัวเดิมทุกช็อต ทุกคลิป ทุกรอบผลิต',
}
hit = []
def retext(n):
    if isinstance(n, dict):
        if n.get('el') == 'text' and n.get('value') in TEXTS:
            hit.append(n['value']); n['value'] = TEXTS[n['value']]
        for v in n.values(): retext(v)
    elif isinstance(n, list):
        for v in n: retext(v)
retext(pet[1])
assert sorted(hit) == sorted(TEXTS), hit

human['card'] = [
    label('ตัวละคร'),
    {'el': 'box', 'className': 'flex flex-col gap-3', 'when': NOT(ANIMAL_CAST), 'card': kids},
    {'el': 'box', 'className': 'flex flex-col gap-3', 'when': ANIMAL_CAST, 'card': pet},
]
sec['card'][2:4] = [label('ผู้แสดงเห็นแค่ไหน'), sel, label('ผู้แสดงเป็นอะไร', SHOWN), castSel, speciesBox, human]
cfg['values']['svCast'] = ''
cfg['values']['charAnimal'] = ''

json.dump(cfg, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('✅ v54 · showhow-style: เห็นแค่ไหน 4 · เป็นอะไร 5 · ตัวละคร (คน/สัตว์) · lookup +6 ตาราง')
