#!/usr/bin/env python3
# showhow v79 — ไทม์แลปส์: เลิกวาดบอร์ดที่ไม่ได้ใช้ + บอกโมเดลว่าเฟรมแรกถูกกำหนดมาแล้ว (พี่หมีสั่ง 2026-09-23)
#
# 🔎 ที่มา: พี่หมีดูคลิปไทม์แลปส์ 30 วิ แล้วชี้ว่า "วิ 10 ต่อเนียนมาก แต่ วิ 20 หลุด"
#    ตรวจแล้วพี่หมีถูก — ผมตรวจไม่ครบเอง:
#      เฟรมแรกของช่วง 3 ตรงกับเฟรมท้ายช่วง 2 เป๊ะ (t=0.0) แต่ **t=0.5 กระโดดไปคนละช็อตทันที**
#    ⇒ chaining การันตีแค่ "เฟรมแรก" ไม่ได้การันตี "ทั้งช่วง"
#    ทำไมช่วง 2 รอด แต่ช่วง 3 ไม่รอด: บทช่วง 2 (ตั้งเสา→เชื่อมโครง→มุงหลังคา) ต่อจากเฟรมเริ่มต้นได้ตรง ๆ
#      ส่วนช่วง 3 (ติดกระจก→จัดสวน→บ้านเสร็จ) ห่างจากเฟรมเริ่มต้นมาก โมเดลเลยทิ้งเฟรมแล้วตัดไปช็อตใหม่
#
# ① **เลิกวาดบอร์ดช่วง 2+ ในโหมดไทม์แลปส์** (ข้อเสนอของพี่หมี — ถูกต้องและประหยัดจริง)
#    เพราะพอมี startFrame แล้ว **refs ทั้งชุดถูกทิ้ง** ⇒ บอร์ดช่วง 2+ ถูกวาดแล้วไม่มีใครใช้
#      30 วิ: บอร์ด 3 → 1 (ประหยัด 2 ใบ) · 60 วิ: 6 → 1 (ประหยัด 5 ใบ)
#    🔑 ทำได้ด้วย `op.where` ซึ่ง **ประเมินกับ item จริง** (engine-run.ts:115 `matchWhereAll(it, op.where, …)`)
#       ต่างจาก `op.when` ที่ประเมินโดยไม่มี item (engine-run.ts:111) — จุดที่เคยทำให้ผมคิดว่าแตกสาขารายงานไม่ได้
#
# ② **บอกโมเดลว่าเฟรมแรกเป็นของที่ถูกกำหนดมาแล้ว** — prompt เดิมไม่เคยบอกเลย
#    🔑 ได้ที่ฟรี: ช่วงที่ต่อเฟรม **ไม่มีรูปอ้างอิงสักใบ** แต่ prompt ยังพูดถึง "แผ่นที่แนบมา" อยู่ 250 ตัวอักษร
#       ⇒ สลับย่อหน้านั้นเป็นคำสั่งต่อเนื่อง = ได้ที่ฟรี + ตัดคำสั่งที่ขัดกับความจริงออกด้วย
#    🪤 ผลข้างเคียงที่ยอมรับ: ช่วงที่ต่อเฟรมจะไม่มีประโยค "แผ่นห้ามโผล่บนจอ" แล้ว
#       — รับได้เพราะช่วงนั้นไม่มีแผ่นแนบไปเลย และบรรทัด Negative ยังมี "no storyboard sheet" อยู่
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ARC = 'ไทม์แลปส์กล้องนิ่ง'
IS_TL = {'op': 'eq', 'a': '{item.arc}', 'b': ARC}
NOT_TL = {'op': 'not', 'a': IS_TL}
CHAINED = ['mnVideo2', 'mnVideo3', 'mnVideo4', 'mnVideo5', 'mnVideo6']

# ① บอร์ดช่วง 2+ : ข้ามงานที่เป็นไทม์แลปส์
boards = []
for op in c['ops']:
    if not op['id'].startswith('mnBoard') or op['id'] == 'mnBoard':
        continue
    assert 'where' not in op, (op['id'], op.get('where'))
    op['where'] = 'arc!=' + ARC
    boards.append(op['id'])
assert len(boards) == 5, boards

# ② สลับย่อหน้า "แผ่นที่แนบมา" เป็นคำสั่งต่อเนื่อง เฉพาะช่วงที่ต่อเฟรม
# 🪤 ห้ามขึ้นต้นว่า "frame 1 is …" — ชนแพตเทิร์นของยาม G11 ที่เฝ้ากฎคนละเรื่อง
#    (G11 ค้นประโยคขึ้นต้น `frame 1 is` แล้วบังคับว่าต้องมี `live scene` = กฎห้ามวาดแผ่นบอร์ด)
CONT = ('\n\nCONTINUATION: the opening frame is supplied — start from exactly that image and carry on from that state. '
        'Same camera position and framing throughout; never re-frame, never cut, '
        'and never jump ahead to a more finished stage of the work.')
swapped = []
for op in c['ops']:
    if op['id'] not in CHAINED:
        continue
    parts = op['prompt']['parts']
    hit = [i for i, x in enumerate(parts) if isinstance(x, str) and 'Attached sheets' in x]
    assert len(hit) == 1, (op['id'], hit)
    i = hit[0]
    sheet = parts[i]
    parts[i] = {'op': 'block', 'sep': '', 'parts': [
        {'when': NOT_TL, 'value': sheet},
        {'when': IS_TL, 'value': CONT},
    ]}
    swapped.append((op['id'], len(sheet), len(CONT)))
assert len(swapped) == 5, swapped

# ---- sanity ----
s = json.dumps(c, ensure_ascii=False)
assert s.count('"where": "arc!=' + ARC + '"') == 5
assert s.count('CONTINUATION: the opening frame is supplied') == 5
# ประโยคแผ่นบอร์ดต้องยังอยู่ในไฟล์ (ยาม G11 หาเจอ) และช่วงแรกต้องไม่ถูกแตะ
assert s.count('Attached sheets are a silent guide') >= 6
first = [o for o in c['ops'] if o['id'] == 'mnVideo'][0]
assert any(isinstance(x, str) and 'Attached sheets' in x for x in first['prompt']['parts']), 'ช่วงแรกต้องคงเดิม (มีบอร์ดจริง)'
assert 'where' not in first and 'where' not in [o for o in c['ops'] if o['id'] == 'mnBoard'][0]

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v79 ok')
print('  ① บอร์ดข้ามไทม์แลปส์:', boards)
print('  ② สลับย่อหน้าในช่วงต่อเฟรม:', [(a, f'{b}→{d}') for a, b, d in swapped], f'(สุทธิ {CONT.__len__()-swapped[0][1]:+d} ตัวอักษร)')
