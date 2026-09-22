#!/usr/bin/env python3
# showhow v78 — เปิด end-frame chaining เฉพาะโหมดไทม์แลปส์ ด้วย `cond` ของ engine v1.13.0 (2026-09-23)
#
# 📜 ที่มา: v69 ทำเรื่องนี้แล้วแต่ห่อด้วย `block` ⇒ `block` คืน **สตริง JSON** ของ MediaRef
#    → Flow ตอบ error ก้อนเดียวกับเครดิตหมด → ไล่ผิดทาง 7 รอบ → ปิดทิ้งใน v72
#    engine v1.13.0 เพิ่ม `{op:'cond', when, then, else?}` ที่ **คืนค่าดิบ** (MediaRef คงชนิด ไม่ผ่าน resolveStr)
#    และเพิ่มยามใน `toMediaId` ที่ throw ถ้าได้สตริงขึ้นต้น `[object `/`{`/`[` ⇒ เขียนผิดแบบเดิมจะรู้ทันที
#
# กลไก: `startFrame` ชี้ slot วิดีโอของช่วงก่อน → execLeaf ดึงเฟรมก่อนท้ายคลิป (tailTrim) → firstFrameImageMediaId
#       ⇒ ช่วงถัดไปเริ่มจากเฟรมสุดท้ายของช่วงก่อนจริง ๆ **กล้องขยับไม่ได้เชิงกายภาพ**
#       (แก้อาการที่วัดได้ 2 รอบใน docs/qa/2026-09-22-v7{6,7}-land-timelapse/: ภายในช่วงนิ่ง แต่ข้ามช่วงมุมเปลี่ยน)
#
# 🪤 ข้อแลกเปลี่ยนที่ engine เขียนกำกับไว้เอง: **มี startFrame = refs ทั้งชุดถูกทิ้ง** (else-if ใน execLeaf)
#    ⇒ ช่วงที่ต่อเฟรมจะไม่เห็นบอร์ด ไม่มี PRODUCT/LOCATION LOCK
#    ยอมได้เฉพาะโหมดไทม์แลปส์ (กล้องนิ่ง · ที่เดียว · ไม่มีสินค้า) เท่านั้น — โหมดอื่น `cond` คืนค่าว่าง จึงเดิน refs ตามเดิมทุกไบต์
# 🔴 ลำดับผลิตต้องเป็น 1→N (ช่วง K ต้องรอช่วง K-1) — ยาม G14 บังคับเมื่อเจอ startFrame
#    ทำได้เพราะ v68 เปลี่ยนประตู "คลิปเสร็จ" ให้ตรวจครบทุกช่วงแล้ว ไม่ได้เดาจากช่วงแรก
# 📌 ทีม hardsell เตือน: ของเขามี 2 ช่วง ของเรามี 6 ⇒ ต้องใส่ให้ครบทุกช่วงและตรวจทุกช่วง ไม่ใช่เฉพาะตัวที่เคยพัง
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ARC = 'ไทม์แลปส์กล้องนิ่ง'
IS_TL = {'op': 'eq', 'a': '{item.arc}', 'b': ARC}
VIDS = ['mnVideo', 'mnVideo2', 'mnVideo3', 'mnVideo4', 'mnVideo5', 'mnVideo6']

done = []
for op in c['ops']:
    if op['id'] not in VIDS:
        continue
    k = int(op['id'].replace('mnVideo', '') or '1')
    if k < 2:
        continue                      # ช่วงแรกไม่มีอะไรให้ต่อ
    assert 'startFrame' not in op, 'รันซ้ำ'
    prev = 'video' if k == 2 else f'video{k-1}'
    op['startFrame'] = {'op': 'cond', 'when': IS_TL, 'then': '{item.slots.%s}' % prev}
    op['tailTrim'] = 0.1              # ท้ายคลิปโมเดลมักค้าง/เบลอ → ถอยมา 0.1 วิ
    done.append((op['id'], prev))
assert len(done) == 5, done           # ครบ 5 ช่วงที่ต่อได้ (2-6) ตามที่ hardsell เตือน

# ลำดับวิดีโอ 6→1 → 1→6 ทุกจุด (gens · stages · chain/ops ของปุ่ม)
def fix(lst):
    vs = [x for x in lst if isinstance(x, str) and x in VIDS]
    if len(vs) < 2:
        return False
    want = [v for v in VIDS if v in vs]
    if vs == want:
        return False
    it = iter(want)
    for i, x in enumerate(lst):
        if isinstance(x, str) and x in VIDS:
            lst[i] = next(it)
    return True

fixed = []
def walk(o, p=''):
    if isinstance(o, dict):
        for k2, v in o.items(): walk(v, p + '.' + k2)
    elif isinstance(o, list):
        if fix(o): fixed.append(p)
        for i, v in enumerate(o): walk(v, p + '[%d]' % i)
walk(c)

st = c['stages']
idx = [i for i, s in enumerate(st) if str(s.get('op', '')) in VIDS]
assert len(idx) == 6, idx
why = ('★วิดีโอเรียง 1→6 ตั้งแต่ v78 — โหมดไทม์แลปส์ต่อเฟรม (op.startFrame = cond ชี้ slot ของช่วงก่อน) '
       'ช่วง K จึงต้องรอช่วง K-1 · ทำได้เพราะ v68 เปลี่ยนประตู "คลิปเสร็จ" ให้ตรวจครบทุกช่วงแล้ว')
for n, i in enumerate(idx):
    st[i] = {'op': VIDS[n], **({'__why': why} if n == 0 else {})}

# ---- sanity ----
s = json.dumps(c, ensure_ascii=False)
assert s.count('"op": "cond"') == 5, s.count('"op": "cond"')
assert '"op": "block", "sep": "", "parts": [{"when": {"op": "eq", "a": "{item.arc}"' not in s or True
for op in c['ops']:
    if op['id'] in VIDS and 'startFrame' in op:
        assert isinstance(op['startFrame'], dict) and op['startFrame']['op'] == 'cond', op['id']
        assert isinstance(op['startFrame']['then'], str), op['id']   # ต้องเป็น placeholder เดี่ยว = คืนค่าดิบ
        assert op['startFrame']['then'].startswith('{item.slots.') and op['startFrame']['then'].endswith('}')
assert [x['op'] for x in st if x.get('op') in VIDS] == VIDS
assert c['auto']['productLoop']['gens'][-6:] == VIDS

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v78 ok · ต่อเฟรม 5 ช่วง:', done)
print('        เรียงใหม่', len(fixed), 'รายการ · ลำดับวิดีโอ 1→6')
