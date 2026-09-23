#!/usr/bin/env python3
# showhow v81 — โหมดล็อกหน้า: ให้ LLM "บรรยายคนจากรูป" แทนการหวังให้โมเดลภาพลอกรูป (พี่หมีสั่งแก้ 2026-09-23)
#
# 🔎 ที่มา — พิสูจน์แล้วว่ากลไกฝั่งเราถูกหมด แต่ผลไม่ตรง:
#    · `scripts/lab/refs-probe.ts` (เขียนใหม่วันนี้ เรียก resolveValue ของ engine ตรง ๆ):
#        ล็อกหน้า ไม่มีรูปสินค้า → แนบ **1 ใบ** (รูปหน้า) ✓ · ล็อกหน้า+สินค้า → 2 ใบ ✓
#        กลุ่มควบคุม "AI เลือกเอง" → 1 ใบ (สินค้าอย่างเดียว · face ไม่ถูกแนบ) ✓
#    · prompt มีคำสั่งครบ: บอร์ด "ใช้บุคคลจากภาพใบหน้าที่แนบมา…ล็อกหน้าตา 100%" · วิดีโอ "CHARACTER LOCK (highest priority)"
#    · engine ไม่เตือนว่าทิ้ง refs
#    ⇒ **โมเดลภาพได้รูปหน้าไปแล้วแต่ไม่ทำ identity transfer** (รูปผู้หญิง → ได้ผู้ชาย)
#
# ⇒ เปลี่ยนวิธี: ใช้ท่าเดียวกับ `palette` (แสง) ที่ได้ผลมาแล้ว —
#    **ให้ LLM ที่เห็นรูป เขียนคำบรรยายออกมาเป็นข้อความ แล้วเสียบเข้า prompt**
#    โมเดลภาพทำตาม "คำบรรยาย" ได้ดีกว่า "ลอกรูป" มาก (เห็นจาก palette/PRODUCT LOCK ที่ทำงาน)
#
# 🪤 ทำไมเสียบใน lookup ไม่ได้: `lookup` คืนค่าจากตาราง **ไม่ resolve ต่อ** ⇒ `{item.look}` ใน charBoard จะไม่ถูกแทนค่า
#    (บทเรียนเดียวกับตอน cond) ⇒ ต้องเสียบเป็นบล็อกแยกใน prompt ของ op
# 🪤 ไวยากรณ์ `when` มี 2 แบบ ห้ามสับสน (ผมพลาดตรงนี้รอบแรก):
#    · `op.where`   ใช้ matchWhere  → เขียนชื่อ field ตรง ๆ        เช่น 'arc!=ไทม์แลปส์กล้องนิ่ง'
#    · `when` ในบล็อก ใช้ whenMet   → **ต้องมี `item.` นำหน้า**   เช่น 'item.look!='
#      ('look!=' แบบไม่มี item. = ไปหาตัวแปร global ที่ไม่มีอยู่ ⇒ เงื่อนไขไม่เป็นจริงตลอดกาล เงียบ ๆ)
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
FACE_SRC = 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'
# 🪤 ต้องกัน "ไทม์แลปส์" ออกด้วย — v66 บังคับให้โหมดไทม์แลปส์ใช้โหมดคน "ช่างเบลอ" เสมอ
#    ถ้าไม่กัน จะได้ข้อความช่างเบลอ **บวก** คำบรรยายหน้าซ้อนกัน = ยาวเกินเพดาน (เจอจากยาม G9: เคสที่ตกคือ
#    `คนเดียวเต็มตัว + ไทม์แลปส์` ทั้ง 16 เคส) · ผมบีบข้อความผิดที่ไป 3 รอบก่อนจะไปดูว่า "เคสไหนตก"
IS_FACE = {'op': 'and',
           'a': {'op': 'and',
                 'a': {'op': 'eq', 'a': '{values.svChar}', 'b': 'คนเดียวเต็มตัว'},
                 'b': {'op': 'eq', 'a': '{values.svCharSrc}', 'b': FACE_SRC}},
           'b': {'op': 'not', 'a': {'op': 'eq', 'a': '{item.arc}', 'b': 'ไทม์แลปส์กล้องนิ่ง'}}}

# ① mnPlan เห็นรูปหน้าด้วย
plan = [o for o in c['ops'] if o['id'] == 'mnPlan'][0]
FACE_REF = '{characters[ch1].slots.face}'      # ✅ พิสูจน์แล้วว่า resolve เป็น MediaRef ได้ (id คงที่ · charId = ch1 เสมอ)
assert FACE_REF not in plan['images'], 'รันซ้ำ'
plan['images'].append(FACE_REF)

# ② ให้ LLM คืนฟิลด์ look
# 🪤 schema JSON ไม่ได้อยู่ใน mnPlan.prompt — อยู่ใน lookup `lenOut` ทั้ง 6 ความยาว + fallback ของ systemInstruction
#    (หาโดยไล่ทุก string ใน op ไม่ใช่เดาว่าอยู่ที่ prompt — สคริปต์รอบแรกล้มตรงนี้เพราะเดา)
OLD = '"palette":"lighting and mood in English 3-6 words e.g. soft morning window light"'
NEW = (OLD + ',"look":"มีรูปใบหน้าแนบมาเป็นรูปสุดท้าย = บรรยายคนในรูปนั้นเป็นอังกฤษ **4-6 คำ สั้นที่สุด** '
       '(เพศ ช่วงอายุ ทรงผม) เช่น Thai woman late 20s brown bob '
       '· ไม่มีรูปใบหน้า = ส่งค่าว่าง"')
hits = 0
for k, v in c['lookups']['lenOut'].items():
    assert '"look"' not in v, 'รันซ้ำ'
    assert OLD in v, ('ไม่เจอ schema ใน lenOut[%s]' % k)
    c['lookups']['lenOut'][k] = v.replace(OLD, NEW, 1); hits += 1
node = plan['systemInstruction']['parts'][7]
assert node.get('table') == 'lenOut' and OLD in node['fallback'], 'โครง systemInstruction เปลี่ยน'
node['fallback'] = node['fallback'].replace(OLD, NEW, 1); hits += 1
assert hits == 7, hits

# ③ ส่ง look ลง task + ประกาศ field
q = [o for o in c['ops'] if o['id'] == 'mnQueue'][0]
assert 'look' not in q['spawn']['fields']
q['spawn']['fields']['look'] = '{item.fields.look}'
if 'look' not in c['collections']['tasks']['fields']:
    c['collections']['tasks']['fields'].append('look')

# ④ เสียบคำบรรยายเข้า prompt ของบอร์ด/วิดีโอ เฉพาะโหมดล็อกหน้า และเฉพาะเมื่อ look ไม่ว่าง
BOARD = {'op': 'block', 'sep': '', 'parts': [
    {'when': IS_FACE, 'value': {'op': 'block', 'sep': '', 'parts': [
        {'when': 'item.look!=', 'value': '\n{item.look}'}]}}]}
VIDEO = {'op': 'block', 'sep': '', 'parts': [
    {'when': IS_FACE, 'value': {'op': 'block', 'sep': '', 'parts': [
        {'when': 'item.look!=', 'value': '\nPERSON: {item.look}'}]}}]}
touched = []
for op in c['ops']:
    oid = op['id']
    if not (oid.startswith('mnBoard') or oid.startswith('mnVideo')):
        continue
    parts = op['prompt']['parts']
    key = 'หน้าตาคนในคลิป' if oid.startswith('mnBoard') else 'PERSON: {item.look}'
    assert key not in json.dumps(parts, ensure_ascii=False), ('รันซ้ำ', oid)
    # วางต่อท้ายบล็อกกติกาคน (parts[7] คือบล็อก charBoard/charVideoEN ตามที่ไล่โครงแล้ว)
    idx = None
    for i, x in enumerate(parts):
        s = json.dumps(x, ensure_ascii=False)
        if 'charBoard' in s or 'charVideoEN' in s:
            idx = i + 1
            break
    assert idx is not None, oid
    parts.insert(idx, json.loads(json.dumps(BOARD if oid.startswith('mnBoard') else VIDEO, ensure_ascii=False)))
    touched.append(oid)
assert len(touched) == 12, touched


# ⑤ แลกที่: เขียน charBoard/charVideoEN ของโหมดล็อกหน้าใหม่ให้สั้นลง
#    เดิมเป็นคำสั่ง "ลอกหน้าจากรูปที่แนบ 100%" ซึ่ง **พิสูจน์แล้วว่าโมเดลไม่ทำตาม** ⇒ ไม่ต้องจ่ายที่ให้มันอีก
#    เก็บเฉพาะใจความที่ยังจำเป็น: คนเดิมทุกช็อต · ห้ามเปลี่ยนคน · เป็นผู้ลงมือไม่ใช่พรีเซนเตอร์
K = 'คนเดียวเต็มตัว|' + FACE_SRC
NEW_BOARD = 'คนเดียวกันทุกช่อง เปลี่ยนได้แค่เสื้อผ้า'
NEW_VIDEO = ('CHARACTER LOCK: the same person in every shot; '
             'vary only clothing and angle; a worker, never a presenter — no eye contact, no posing.')
saved = 0
for tbl, new in (('charBoard', NEW_BOARD), ('charVideoEN', NEW_VIDEO)):
    old = c['lookups'][tbl][K]
    assert 'character reference' in old or 'the attached face photo' in old, (tbl, 'รันซ้ำ?')
    saved += len(old) - len(new)
    c['lookups'][tbl][K] = new
print('        แลกที่คืนจาก lookup:', saved, 'ตัวอักษร')

s = json.dumps(c, ensure_ascii=False)
assert s.count('{item.look}') == 12
assert s.count(FACE_REF) == 1
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v81 ok · mnPlan เห็นรูปหน้าแล้ว · เพิ่มฟิลด์ look · เสียบเข้า', len(touched), 'op')
