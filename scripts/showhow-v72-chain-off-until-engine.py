#!/usr/bin/env python3
# showhow v72 — ปิด end-frame chaining + คืนสภาพที่ผ่านการทดสอบจริงมาแล้วทั้งหมด (2026-09-22 ดึก)
#
# 🔴 ทำไมต้องปิด — ไม่ใช่เพราะ engine พัง แต่เพราะ **config เขียนแบบมีเงื่อนไขไม่ได้**
#    engine: `startFrame: op.startFrame ? resolveValue(op.startFrame, ctx) : undefined`  (engine-exec.ts:156)
#            ต้องได้ **MediaRef ดิบ** แล้ว execLeaf จึง `toMediaId` → firstFrameImageMediaId (execLeaf.ts:129)
#    v69 ห่อด้วย `block` เพื่อให้มีเงื่อนไข → `block` จบด้วย `out.join()` หลัง resolveStr ทุกชิ้น (engine-bind.ts:298)
#            ⇒ MediaRef กลายเป็นสตริง "[object Object]" → ส่งเข้า Flow เป็น mediaId → ตอบ error ก้อนเดียวกับเครดิตหมด
#    พิสูจน์: เปลี่ยนเป็นสตริงตรง `'{item.slots.video}'` → ผ่านครั้งแรกทันที (ล้มมาก่อนหน้า 7/7)
# 🪤 ไล่ครบทุกทางแล้วว่า **config ล้วนทำไม่ได้**:
#    · ไม่มี combinator ตัวไหนคืน "ค่าดิบแบบมีเงื่อนไข" (lookup/matchTable คืนค่าจากตารางแต่ไม่ resolve ต่อ)
#    · lookupRefs คืน array → toMediaId คืน undefined ทั้งเปิดและปิด
#    · op.when ก็ไม่ช่วย — ประเมินด้วย ctx ที่ **ไม่มี item** (engine-run.ts:111) ⇒ แตกสาขาราย "งาน" ไม่ได้
#    ⇒ ขอ engine: combinator `cond` ที่คืนค่าดิบ  (ขอไปที่ starter แล้ว)
# ⇒ v72 คืนทุกอย่างกลับเป็นสภาพเดียวกับคลิปที่ยืนยันแล้ว (bath1/desk1/aircon50/regress40):
#    1) ถอด startFrame + tailTrim ทุก mnVideo*
#    2) ถอด resolution '720p' ที่ v71 ใส่ — minimal (ฐานของเรา) ไม่ตั้ง ปล่อย Flow เลือก · คลิปที่ผ่าน QA ทุกตัวไม่มีคีย์นี้
#    3) คืนลำดับวิดีโอเป็น 6→1 ทุกจุด (gens/stages/chain/ops) — 1→6 มีไว้รับ chaining เท่านั้น และยังไม่เคยผลิตคลิปปกติจนจบสักคลิป
#       (ประตู "คลิปเสร็จ" ของ v68 ที่ตรวจครบทุกช่วง **คงไว้** — ดีกว่าเดิมและไม่ผูกกับลำดับ)
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
VIDS = ['mnVideo', 'mnVideo2', 'mnVideo3', 'mnVideo4', 'mnVideo5', 'mnVideo6']
DESC = VIDS[::-1]

# 1+2 — ถอดคีย์ที่ใส่เพิ่มในรอบ v69/v71
removed = []
for op in c['ops']:
    if not op['id'].startswith('mnVideo'):
        continue
    for k in ('startFrame', 'tailTrim', 'resolution'):
        if k in op:
            op.pop(k)
            removed.append(op['id'] + '.' + k)

# 3 — ลำดับ 6→1 ทุกที่ที่มีรายชื่อ op วิดีโอเรียงกัน
fixed = []
def fix_list(lst, path):
    vs = [x for x in lst if isinstance(x, str) and x in VIDS]
    if len(vs) < 2:
        return
    want = [v for v in DESC if v in vs]
    if vs == want:
        return
    it = iter(want)
    for i, x in enumerate(lst):
        if isinstance(x, str) and x in VIDS:
            lst[i] = next(it)
    fixed.append(path)

def walk(o, p=''):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, p + '.' + k)
    elif isinstance(o, list):
        fix_list(o, p)
        for i, v in enumerate(o):
            walk(v, p + '[%d]' % i)
walk(c)

# stages: เรียงลำดับวิดีโอใหม่ในตำแหน่งเดิม
st = c['stages']
idx = [i for i, s in enumerate(st) if str(s.get('op', '')) in VIDS]
assert len(idx) == 6, idx
why = ('★วิดีโอเรียง 6→1 (ของ minimal) — คืนลำดับเดิมใน v72 หลังปิด end-frame chaining '
       '· ประตู "คลิปเสร็จ" ของ v68 ที่ตรวจครบทุกช่วงยังอยู่ จึงไม่ผูกกับลำดับอีกแล้ว')
for n, i in enumerate(idx):
    st[i] = {'op': DESC[n], **({'__why': why} if n == 0 else {})}

# ---- sanity ----
s = json.dumps(c, ensure_ascii=False)
assert '"startFrame"' not in s, 'ยังมี startFrame หลงเหลือ'
assert '"tailTrim"' not in s, 'ยังมี tailTrim หลงเหลือ'
for op in c['ops']:
    if op.get('type') == 'video':
        assert 'resolution' not in op, op['id']
assert [s['op'] for s in st if s.get('op') in VIDS] == DESC
assert c['auto']['productLoop']['gens'][-6:] == DESC, c['auto']['productLoop']['gens'][-6:]

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v72 ok · ถอด', len(removed), 'คีย์:', removed)
print('        เรียงใหม่', len(fixed), 'รายการ:', fixed)
