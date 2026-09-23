#!/usr/bin/env python3
"""showhow-v88 — กฎสัตว์ต้องมี "ตัวเดียว ตัวเดิมทุกฉาก" (ข้อที่หล่นหายตอน v85 แทนที่บล็อกคน)

เจอจากคลิปจริง 2026-09-23 (`docs/qa/2026-09-23-castkind/` เคสของเล่นแมว · animalReal):
  วินาที 0-6 มีแมว **1 ตัว** · วินาที 8 กลายเป็น **2 ตัว**
  บทจาก LLM เขียน "the cat" ตัวเดียวทุกฉาก ⇒ ไม่ใช่ความผิดของบท — โมเดลวิดีโองอกตัวที่ 2 เอง

🔴 รากของปัญหาคือการออกแบบของ v85 เอง:
   กฎคนเดิม (`charVideoEN`) มี 3 ข้อผูกไว้ — ① one … **the same person in every scene**
   ② never looks at / poses for the camera  ③ the work stays the focus
   v85 เอากฎสัตว์ไป **แทนที่ทั้งบล็อก** แต่เขียนแค่ "เป็นสัตว์แบบไหน" ⇒ **ทั้ง 3 ข้อหายไปพร้อมกัน**
   ⇒ บทเรียน: "แทนที่" ต้องแทนให้ครบทุกข้อที่ของเดิมแบกไว้ ไม่ใช่แค่เรื่องที่เรากำลังสนใจ

แก้: เขียนกฎสัตว์ใหม่ทั้ง 3 โหมด ให้ครบ 3 ข้อเดิม + เรื่องสัตว์ · คุมความยาวไม่ให้เกินของเดิมมาก
     castPlan (เข้า LLM · ไม่ถูกตัด) ก็ย้ำ "ตัวเดียวตัวเดิม" ด้วย — กันตั้งแต่ชั้นบท

ใช้: python3 scripts/showhow-v88-one-animal.py
"""
import json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))

# 🪤 ความยาวคือข้อจำกัดจริง ไม่ใช่ถ้อยคำ — วัดแล้วเพดานของบล็อกนี้อยู่ที่ประมาณความยาวของกฎคนเดิม (176)
#    ร่างแรกของ v88 เขียนครบดี แต่ยาว 217-229 ⇒ G9 ตกทันที (คลิปกินเข้าไปในบรรทัด Negative จนกฎ "no storyboard sheet" หาย)
#    ⇒ เขียนใหม่ให้ครบ 3 ข้อในความยาวเท่าของเดิม
VIDEO = {
    'animalReal': ('ONE real animal, the same one in every scene — four legs down, natural animal anatomy, no '
                   'clothing; absorbed in the task, never poses for the camera; the work stays the focus.'),
    'animalAnthro': ('ONE animal acting like a person, the same one in every scene — upright, front paws as hands, '
                     'clothes, fluffy fur, big round eyes; never poses for the camera; the work stays the focus.'),
    'animalToon': ('ONE cartoon animal, the same one in every scene — animal anatomy (muzzle, ears, tail, paws), '
                   'big eyes, bold shapes, bright colours, an ANIMAL not a person; never poses for the camera.'),
}
BOARD = {
    'animalReal': 'ผู้ลงมือเป็นสัตว์จริง ตัวเดียว ตัวเดิมทุกช่อง เดิน 4 ขา ไม่ใส่เสื้อผ้า ห้ามวาดคนหรือมือคน',
    'animalAnthro': 'ผู้ลงมือเป็นสัตว์ทำตัวเหมือนคน ตัวเดียว ตัวเดิมทุกช่อง ยืนตัวตรง ใส่เสื้อผ้า ใช้อุ้งเท้าแทนมือ ห้ามวาดคน',
    'animalToon': 'ผู้ลงมือเป็นตัวการ์ตูนสัตว์ ตัวเดียว ตัวเดิมทุกช่อง รูปทรงสัตว์จริง ตาโต สีสด ห้ามวาดคน',
}
ONE_TH = 'ตัวเดียว ตัวเดิมทุกฉากทุกช่วง ห้ามมีตัวที่สองโผล่ · '

for tbl, new in (('castVideoEN', VIDEO), ('castBoard', BOARD)):
    lk = c['lookups'][tbl]
    for k, v in new.items():
        old = lk[k]
        assert old, f'{tbl}.{k} ว่าง — โครงเปลี่ยน'
        lk[k] = v
        print(f'  {tbl}.{k}: {len(old)} → {len(v)} ตัวอักษร ({len(v)-len(old):+d})')
    assert set(lk) == {'auto', 'human', 'animalReal', 'animalAnthro', 'animalToon'}

# castPlan — กันตั้งแต่ชั้นบท (mnPlan ไม่ถูกตัด ใส่ได้ไม่ต้องกลัวเพดาน)
cp = c['lookups']['castPlan']
for k in ('animalReal', 'animalAnthro', 'animalToon'):
    assert ONE_TH not in cp[k]
    cp[k] = cp[k].replace('★ ผู้ลงมือในคลิปนี้เป็น', '★ ผู้ลงมือในคลิปนี้ ' + ONE_TH + 'เป็น')
print('① castPlan: ย้ำ "ตัวเดียว ตัวเดิมทุกฉากทุกช่วง ห้ามมีตัวที่สองโผล่" ทั้ง 3 โหมด')

# ── ยาม: ทุกโหมดสัตว์ต้องมีครบ 3 ข้อที่กฎคนเดิมแบกไว้ ─────────────────────────
for k in ('animalReal', 'animalAnthro', 'animalToon'):
    v = c['lookups']['castVideoEN'][k]
    assert v.startswith('ONE '), f'castVideoEN.{k} ต้องเริ่มด้วยจำนวน (ONE)'
    assert 'the same one in every scene' in v, \
        f'castVideoEN.{k} ขาดข้อ "ตัวเดิมทุกฉาก" — ข้อที่ทำให้แมวงอกเป็น 2 ตัว'
    assert 'camera' in v, f'castVideoEN.{k} ขาดข้อ "ห้ามมองกล้อง/โพสท่า"'
    b = c['lookups']['castBoard'][k]
    assert 'ตัวเดียว' in b and 'ตัวเดิมทุกช่อง' in b, f'castBoard.{k} ขาดข้อ "ตัวเดียว ตัวเดิมทุกช่อง"'
HUMAN = max(len(v) for v in c['lookups']['charVideoEN'].values())
for k in ('animalReal', 'animalAnthro', 'animalToon'):
    n = len(c['lookups']['castVideoEN'][k])
    assert n <= HUMAN + 10, (f'castVideoEN.{k} ยาว {n} — กฎคนที่มันไปแทนยาวสุด {HUMAN} '
                             f'· ยาวกว่านี้ = คลิปกินเข้าไปในบรรทัด Negative (G9 ตก)')
HB = max(len(v) for v in c['lookups']['charBoard'].values())
for k in ('animalReal', 'animalAnthro', 'animalToon'):
    n = len(c['lookups']['castBoard'][k])
    assert n <= HB, f'castBoard.{k} ยาว {n} — กฎคนของบอร์ดยาวสุด {HB} (บอร์ดเหลือ headroom หลักสิบ)'
print('✅ ยามผ่าน: ทุกโหมดสัตว์มีครบ — จำนวน · ตัวเดิมทุกฉาก · ห้ามมองกล้อง · และไม่ยาวกว่ากฎคนที่ไปแทน')

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nเขียน {P} แล้ว')
