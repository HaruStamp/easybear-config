#!/usr/bin/env python3
# showhow v69 — end-frame chaining เฉพาะโหมดไทม์แลปส์ (พี่หมีสั่ง 2026-09-22)
#
# กลไกของ engine (อ่านจากซอร์ส execLeaf.ts:129 + engine-exec.ts:156):
#   op.startFrame ชี้ slot วิดีโอ → execLeaf ดึง "เฟรมก่อนท้ายคลิป" (tailTrim วิ) → firstFrameImageMediaId
#   ⇒ ช่วงถัดไปเริ่มจากเฟรมสุดท้ายของช่วงก่อน = รอยต่อเนียน
# 🪤 กับดักที่ engine เขียนกำกับไว้เอง: **มี startFrame แล้ว refs ทั้งชุดถูกทิ้ง** (else-if ใน execLeaf)
#    ⇒ ช่วงที่ต่อเฟรมจะไม่ได้เห็นบอร์ดของตัวเอง — ความต่อเนื่องมาจากเฟรมจริง + ข้อความแทน
# 🔴 ลำดับผลิตต้องเป็น 1→6 (ช่วง K ต้องรอช่วง K-1) ⇒ สลับ gens/stages
#    ทำได้เพราะ v68 เปลี่ยนประตู "คลิปเสร็จ" ให้ตรวจครบทุกช่วงแล้ว ไม่ได้เดาจากช่วงแรกอีก
# ⇒ startFrame ใส่แบบมีเงื่อนไข: โหมดอื่น resolve เป็นค่าว่าง → execLeaf ใช้ refs ตามเดิมทุกไบต์
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ARC = 'ไทม์แลปส์กล้องนิ่ง'
IS_TL = {'op': 'eq', 'a': '{item.arc}', 'b': ARC}

done = []
for op in c['ops']:
    if not op['id'].startswith('mnVideo'):
        continue
    k = int(op['id'].replace('mnVideo', '') or '1')
    if k < 2:
        continue
    assert 'startFrame' not in op, 'รันซ้ำ'
    prev = 'video' if k == 2 else f'video{k-1}'
    op['startFrame'] = {'op': 'block', 'sep': '', 'parts': [
        {'when': IS_TL, 'value': '{item.slots.%s}' % prev}]}
    op['tailTrim'] = 0.1          # ท้ายคลิปโมเดลมักค้าง/เบลอ → ถอยมา 0.1 วิ
    done.append((op['id'], prev))

assert len(done) == 5, done

# ลำดับผลิตวิดีโอ 6→1 → 1→6
NEW_V = ['mnVideo', 'mnVideo2', 'mnVideo3', 'mnVideo4', 'mnVideo5', 'mnVideo6']
g = c['auto']['productLoop']['gens']
vids = [x for x in g if x.startswith('mnVideo')]
assert vids == NEW_V[::-1], vids
c['auto']['productLoop']['gens'] = [x for x in g if not x.startswith('mnVideo')] + NEW_V

st = c['stages']
keep = [s for s in st if not str(s.get('op', '')).startswith('mnVideo')]
why = ('★วิดีโอเรียง 1→6 ตั้งแต่ v69 — โหมดไทม์แลปส์ต่อเฟรม (op.startFrame ชี้ slot ของช่วงก่อน) '
       'ช่วง K จึงต้องรอช่วง K-1 · ทำได้เพราะ v68 เปลี่ยนประตู "คลิปเสร็จ" ให้ตรวจครบทุกช่วงแล้ว '
       '(เดิมเรียง 6→1 เพราะประตูเดาจาก slots.video ของช่วงแรก)')
c['stages'] = keep + [{'op': v, **({'__why': why} if i == 0 else {})} for i, v in enumerate(NEW_V)]

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v69 ok · startFrame แบบมีเงื่อนไข', done, '· ลำดับวิดีโอ 1→6')
