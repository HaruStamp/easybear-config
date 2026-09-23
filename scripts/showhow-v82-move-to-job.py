#!/usr/bin/env python3
"""showhow-v82-move-to-job.py — ย้ายตัวเลือกที่ "เปลี่ยนตามงาน" เข้าไปในงาน (พี่หมีเคาะ 2026-09-23)

สเปกเต็ม: easybear-showhow/docs/SETTINGS-MOVE-SPEC.md

หลักการเดียว: อะไรที่เปลี่ยนตามงาน → อยู่ในงาน · อะไรที่เหมือนทุกงาน → อยู่หน้าหลัก
หลักฐาน: 3 งานจริงวันนี้ (ไทม์แลปส์สร้างบ้าน · สอนซูชิแมว · ทัวร์กาแฟ) โครงเรื่อง/กล้อง/คน เปลี่ยนพร้อมกันหมด

ทำ 5 อย่าง
  ① ตัด svCam1-5 + svPres1-5 (มุมกล้อง/การนำเสนอรายองก์ 10 ช่อง) ทิ้งทั้งหมด
     — ซ้ำกับ dropdown รายฉาก cam1-30 ในหน้าผลิต ซึ่งละเอียดกว่า แยกตามงานจริง และเป็นตัวที่ใช้จริงตอนทำวิดีโอ
     🪤 ป้ายเดิมเขียน "ฉาก 1 · 0-2 วิ" ตายตัว ทั้งที่ 1 ช่อง = 1 องก์ (60 วิ = 6 ฉาก) ⇒ บอกน้อยกว่าจริง 6 เท่า
  ② ย้าย svCamMode → products.camMode · svChar → products.people · svCharSrc → products.peopleSrc
  ③ ส่งลง task ผ่าน mnQueue.spawn ด้วย {parent.fields.*} (engine ≥1.9.0 รองรับ — arc ใช้ท่านี้อยู่แล้ว)
  ④ เปลี่ยน key ของ lookup ทุกตัวจาก {values.sv*} → {item.*}
  ⑤ UI ในหน้างาน: ล็อก/เตือน/ซ่อน ตามเมทริกซ์

ใช้: python3 scripts/showhow-v82-move-to-job.py   (แก้ showhow-dev.json ในที่)
"""
import json, sys, copy

P = 'showhow-dev.json'
TL = 'ไทม์แลปส์กล้องนิ่ง'
STEP = 'ทีละขั้นให้ทำตาม'
CAM_STILL = 'ตั้งนิ่งเห็นทั้งพื้นที่'
CAM_VLOG = 'ตามคน ตามมือ แบบ vlog'
P_SOLO = 'คนเดียวเต็มตัว'
P_HANDS = 'เห็นแต่มือ ไม่เห็นหน้า'
P_CREW = 'ทีมช่างเบลอเคลื่อนไหวเร็ว'
P_NONE = 'ไม่มีคน'
SRC_AI = 'AI เลือกนาย/นางแบบให้เหมาะกับสินค้า'
SRC_FACE = 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'

c = json.load(open(P, encoding='utf-8'))
before = json.dumps(c, ensure_ascii=False)


def walk(n, parent=None, key=None):
    yield n, parent, key
    if isinstance(n, dict):
        for k, v in list(n.items()):
            yield from walk(v, n, k)
    elif isinstance(n, list):
        for i, v in enumerate(list(n)):
            yield from walk(v, n, i)


def drop_where(pred):
    """ลบ node ที่ตรง pred ออกจาก list แม่ — คืนจำนวนที่ลบ"""
    n = 0
    changed = True
    while changed:
        changed = False
        for node, parent, key in walk(c):
            if isinstance(parent, list) and isinstance(node, dict) and pred(node):
                parent.pop(key); n += 1; changed = True; break
    return n


# ── ① ตัด svCam1-5 / svPres1-5 ────────────────────────────────────────────────
PER_ACT = {f'sv{p}{i}' for p in ('Cam', 'Pres') for i in range(1, 6)}

# ①a ตัดบล็อก "ข้อกำหนดรายฉากจากผู้ใช้" ออกจาก prompt ของ mnPlan
#    = lenActHead + (lenAct|N + สตริง " — มุมกล้อง: {svCamN} · การนำเสนอ: {svPresN}") ×5 + lenActTail
def is_peract_chunk(x):
    if isinstance(x, str):
        return 'svCam' in x and 'การนำเสนอ' in x
    if isinstance(x, dict) and x.get('op') == 'lookup':
        return x.get('table') in ('lenActHead', 'lenAct', 'lenActTail')
    return False

n_prompt = 0
for node, parent, key in list(walk(c)):
    if not isinstance(node, list):
        continue
    keep = [x for x in node if not is_peract_chunk(x)]
    if len(keep) != len(node):
        n_prompt += len(node) - len(keep)
        node[:] = keep
print(f'①a ตัดบล็อกข้อกำหนดรายองก์ออกจาก prompt: {n_prompt} ชิ้น')
# lookup ที่ไม่มีใครใช้แล้ว
for t in ('lenActHead', 'lenAct', 'lenActTail'):
    c['lookups'].pop(t, None)
print('   ลบ lookup lenActHead/lenAct/lenActTail (ไม่มีใครใช้แล้ว)')

n_el = drop_where(lambda d: d.get('field') in PER_ACT)
for f in PER_ACT:
    c.get('values', {}).pop(f, None)
assert n_el >= 10, f'ควรลบ element ได้ ≥10 · ได้ {n_el}'
s = json.dumps(c, ensure_ascii=False)
for f in PER_ACT:
    assert f not in s, f'ยังเหลือ {f} ใน config'
print(f'① ตัดมุมกล้อง/การนำเสนอรายองก์: ลบ element {n_el} ตัว · ล้าง values แล้ว')

# กล่องที่เหลือว่าง (หัวข้อ "ฉาก N" + เวลา) — ลบกล่องที่ไม่มี field เหลือเลย
def box_is_orphan(d):
    if not isinstance(d, dict) or d.get('el') != 'box':
        return False
    t = json.dumps(d, ensure_ascii=False)
    if '"field"' in t:
        return False
    # กล่องฉากเดิมมีทั้งเลขลำดับ + "ฉาก N" + "N-N วิ"
    return ('ฉาก ' in t and ' วิ' in t and t.count('"el"') <= 8)
n_box = drop_where(box_is_orphan)
print(f'   ลบกล่องฉากที่ว่างเปล่าอีก {n_box} กล่อง')


# ── ② ย้ายเป็น field ของงาน ───────────────────────────────────────────────────
MOVE = {'svCamMode': 'camMode', 'svChar': 'people', 'svCharSrc': 'peopleSrc'}
pf = c['collections']['products'].setdefault('fields', {})
if isinstance(pf, dict):
    for old, new in MOVE.items():
        pf.setdefault(new, '')
    pf.setdefault('camMode', '')
else:  # list
    for new in MOVE.values():
        if new not in pf:
            pf.append(new)
tf = c['collections']['tasks'].setdefault('fields', [])
for new in MOVE.values():
    if new not in tf:
        tf.append(new)
# ค่าตั้งต้นของงานใหม่
ad = c['collections']['products'].setdefault('addDefaults', {})
ad.setdefault('people', P_HANDS)
ad.setdefault('peopleSrc', SRC_AI)
ad.setdefault('camMode', '')
print(f'② เพิ่ม field ในงาน: {list(MOVE.values())} · addDefaults people={P_HANDS!r}')

# ── ③ spawn ส่งลง task ────────────────────────────────────────────────────────
q = next(o for o in c['ops'] if o['id'] == 'mnQueue')
sp = q['spawn']['fields']
assert sp.get('arc') == '{parent.fields.arc}', 'spawn ต้องมี arc จาก parent อยู่แล้ว (ท่ายืนยันว่า {parent.*} ใช้ได้)'
for new in MOVE.values():
    sp[new] = '{parent.fields.%s}' % new
print(f'③ spawn ส่งลง task: ' + ' · '.join(f'{k}=parent' for k in MOVE.values()))

# ── ④ เปลี่ยน {values.sv*} → {item.*} ทั้ง config (ops + UI) ───────────────────
s = json.dumps(c, ensure_ascii=False)
hits = {old: s.count('{values.%s}' % old) for old in MOVE}
# 🪤 ต้องแทน svCharSrc ก่อน svChar (ไม่งั้น "svCharSrc" จะโดน prefix "svChar" กินไปครึ่งหนึ่ง)
for old, new in sorted(MOVE.items(), key=lambda kv: -len(kv[0])):
    s = s.replace('{values.%s}' % old, '{item.%s}' % new)       # การอ้างค่า
    s = s.replace('"field": "%s"' % old, '"field": "%s"' % new)  # ชื่อ field ของ element
c = json.loads(s)
for old, new in MOVE.items():
    print(f'④ {old:<12} → item.{new:<10} แทน {hits[old]} จุด (ops + UI)')

# ── ⑤ UI: ย้ายของเดิมเข้าหน้างาน ──────────────────────────────────────────────
# ⑤a ตัดบล็อกตัวละครทั้งก้อนออกจากหน้าตั้งค่า (มีอัปโหลดรูป + charName/charLook/charGender/charAge)
char_block = None
for node, parent, key in list(walk(c)):
    if (isinstance(node, dict) and isinstance(parent, list)
            and json.dumps(node.get('when'), ensure_ascii=False) == json.dumps(
                {'op': 'eq', 'a': '{item.people}', 'b': P_SOLO}, ensure_ascii=False)
            and '"field": "peopleSrc"' in json.dumps(node, ensure_ascii=False)):
        char_block = parent.pop(key)
        break
assert char_block is not None, 'หาบล็อกตัวละครในหน้าตั้งค่าไม่เจอ'
assert '"el": "upload"' in json.dumps(char_block, ensure_ascii=False), 'บล็อกตัวละครต้องมีช่องอัปโหลดรูป'
print('⑤a ย้ายบล็อกตัวละครทั้งก้อน (อัปโหลดรูป + 4 ช่องบอกใบ้) ออกจากหน้าตั้งค่า')

# ⑤b ลบช่อง camMode/people ที่เหลือในหน้าตั้งค่า
n_old = drop_where(lambda d: d.get('field') in ('camMode', 'people'))
print(f'⑤b ลบช่อง มุมกล้อง/เห็นคนแค่ไหน จากหน้าตั้งค่า {n_old} ตัว')

# หา element arc ในหน้างาน เพื่อแทรกต่อ
arc_parent = arc_idx = None
for node, parent, key in walk(c):
    if isinstance(node, dict) and node.get('field') == 'arc' and isinstance(parent, list):
        arc_parent, arc_idx = parent, key
        break
assert arc_parent is not None, 'หา element arc ในหน้างานไม่เจอ'

IS_TL = {'op': 'eq', 'a': '{item.arc}', 'b': TL}
NOT_TL = {'op': 'not', 'a': IS_TL}
IS_STEP = {'op': 'eq', 'a': '{item.arc}', 'b': STEP}
LBL = '!text-[13px] @[640px]:!text-[12.5px] opacity-60 px-0.5 mt-1'
WARN = '!text-[13px] @[640px]:!text-[12.5px] px-0.5 !text-[#a16207] dark:!text-[#fbbf24]'
OK = '!text-[13px] @[640px]:!text-[12.5px] px-0.5 !text-[#15803d] dark:!text-[#4ade80]'

def eq(f, v): return {'op': 'eq', 'a': '{item.%s}' % f, 'b': v}
def both(a, b): return {'op': 'and', 'a': a, 'b': b}

new_blocks = [
    {'el': 'text', 'value': 'มุมกล้อง', 'className': LBL},
    {'el': 'text', 'value': '🔒 กล้องนิ่งมุมเดียวทั้งคลิป — โครงเรื่องนี้กำหนดไว้แล้ว',
     'className': '!text-[13.5px] @[640px]:!text-[13px] px-0.5 opacity-75', 'when': IS_TL},
    {'el': 'grid-select', 'field': 'camMode', 'cols': 2, 'contained': True, 'when': NOT_TL,
     'className': '!min-h-[44px] @[420px]:!min-h-0',
     'options': [
         {'value': '', 'label': 'อัตโนมัติ', 'desc': 'หมีเลือกให้เข้ากับเรื่อง', 'icon': 'auto_awesome'},
         {'value': CAM_STILL, 'label': 'ตั้งนิ่งเห็นทั้งพื้นที่', 'desc': 'มุมเดิมทั้งคลิป', 'icon': 'crop_free'},
         {'value': CAM_VLOG, 'label': 'ตามคน ตามมือ', 'desc': 'ใกล้ชิด แบบ vlog', 'icon': 'directions_walk'},
     ]},
    {'el': 'text', 'value': '⚠️ โครงเรื่องนี้ต้องเห็นมือทำใกล้ ๆ ทุกขั้น — ถ่ายไกลจะดูไม่ออกว่าทำอะไร',
     'className': WARN, 'when': both(IS_STEP, eq('camMode', CAM_STILL))},

    {'el': 'text', 'value': 'เห็นคนแค่ไหน', 'className': LBL},
    {'el': 'grid-select', 'field': 'people', 'cols': 2, 'contained': True,
     'className': '!min-h-[44px] @[420px]:!min-h-0',
     'options': [
         {'value': P_HANDS, 'label': 'เห็นแต่มือ', 'desc': 'ไม่เห็นหน้า', 'icon': 'back_hand'},
         {'value': P_SOLO, 'label': 'คนเดียวเต็มตัว', 'desc': 'ผู้ลงมือทำ', 'icon': 'person'},
         {'value': P_CREW, 'label': 'ทีมช่าง (เบลอ)', 'desc': 'หลายคน เคลื่อนไหวเร็ว', 'icon': 'groups'},
         {'value': P_NONE, 'label': 'ไม่มีคน', 'desc': 'เห็นแต่พื้นที่และของ', 'icon': 'no_accounts'},
     ]},
    {'el': 'text', 'value': '✅ เข้ากับไทม์แลปส์พอดี', 'className': OK,
     'when': both(IS_TL, eq('people', P_CREW))},
    {'el': 'text', 'value': '⚠️ ไทม์แลปส์ห้ามให้มือเป็นประธานของภาพ — อาจได้ผลไม่ตรงที่ตั้งใจ',
     'className': WARN, 'when': both(IS_TL, eq('people', P_HANDS))},
    {'el': 'text', 'value': '⚠️ สอนทำตามต้องเห็นมือชัดทุกขั้น — คนเบลอจะดูไม่ออกว่าทำอะไร',
     'className': WARN, 'when': both(IS_STEP, eq('people', P_CREW))},
    {'el': 'text', 'value': '⚠️ สอนทำตามต้องมีมือลงมือทุกฉาก — "ไม่มีคน" จะขัดกับโครงเรื่อง',
     'className': WARN, 'when': both(IS_STEP, eq('people', P_NONE))},
    {'el': 'text', 'value': 'ตัวละคร', 'className': LBL, 'when': eq('people', P_SOLO)},
    char_block,   # ← บล็อกเดิมทั้งก้อน (when = people คนเดียวเต็มตัว อยู่แล้ว)
]
for i, b in enumerate(new_blocks):
    arc_parent.insert(arc_idx + 1 + i, b)
print(f'⑤c แทรกในหน้างาน {len(new_blocks)} ชิ้น (มุมกล้อง + เห็นคนแค่ไหน + คำเตือน + บล็อกตัวละครเดิม)')

# ── ยาม ───────────────────────────────────────────────────────────────────────
s = json.dumps(c, ensure_ascii=False)
for f in list(PER_ACT) + list(MOVE):
    assert '"field": "%s"' % f not in s, f'ยังมี element ของ {f} หลงเหลือ'
    assert '{values.%s}' % f not in s, f'ยังมีการอ้าง {{values.{f}}} หลงเหลือ'
for new in MOVE.values():
    assert '{item.%s}' % new in s, f'ไม่พบการใช้ {{item.{new}}}'
    assert '{parent.fields.%s}' % new in s, f'spawn ไม่ได้ส่ง {new}'
assert s.count('"field": "peopleSrc"') == 1, 'ช่องตัวละครต้องมีที่เดียว'
assert '"el": "upload"' in s, 'ต้องยังมีช่องอัปโหลดรูปตัวละคร'
print('✅ ยามผ่าน: ไม่มี sv* หลงเหลือ · item.* ใช้ครบ · spawn ส่งครบ')

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nเขียน {P} แล้ว ({len(before):,} → {len(json.dumps(c, ensure_ascii=False)):,} ตัวอักษร)')

# ── ⑥ เก็บกวาด: ย้าย charName/charLook/charGender/charAge เข้างานด้วย ──────────
#    (บล็อกตัวละครย้ายไปหน้างานแล้ว ⇒ ช่องบอกใบ้ต้องเป็นของงาน ไม่งั้นทุกงานใช้ชื่อตัวละครเดียวกัน)
HINTS = ['charName', 'charLook', 'charGender', 'charAge']
s = json.dumps(c, ensure_ascii=False)
for f in HINTS:
    s = s.replace('{values.%s}' % f, '{item.%s}' % f)
c = json.loads(s)
pf = c['collections']['products']['fields']
tf = c['collections']['tasks']['fields']
for f in HINTS:
    if isinstance(pf, dict): pf.setdefault(f, '')
    elif f not in pf: pf.append(f)
    if f not in tf: tf.append(f)
    c['ops'][[o['id'] for o in c['ops']].index('mnQueue')]['spawn']['fields'][f] = '{parent.fields.%s}' % f
# ล้าง values ที่ไม่มีใครใช้แล้ว
for f in list(MOVE) + HINTS:
    c['values'].pop(f, None)
s = json.dumps(c, ensure_ascii=False)
for f in list(MOVE) + HINTS:
    assert '{values.%s}' % f not in s, f'ยังอ้าง values.{f}'
for f in HINTS:   # ชื่อ sv* ตายไปแล้วตั้งแต่ ④ · ที่ต้องยังอยู่คือช่องบอกใบ้
    assert '"field": "%s"' % f in s, f'{f} หายไปหมดเลย'
    assert '{item.%s}' % f in s, f'{f} ไม่ถูกใช้ใน prompt'
print(f'⑥ ย้ายช่องบอกใบ้ตัวละคร {HINTS} เข้างาน + ล้าง values ที่ไม่ใช้แล้ว {len(MOVE)+len(HINTS)} ตัว')

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'เขียนซ้ำ {P} ({len(json.dumps(c, ensure_ascii=False)):,} ตัวอักษร)')

# ── ⑦ ลบการ์ด "มุมกล้อง & การนำเสนอ (ขั้นสูง)" ที่เหลือแต่หัวข้อ ─────────────────
#    (พี่หมีเห็นของจริงแล้วทัก: ข้างในไม่มีอะไรให้ตั้งค่าแล้ว แต่การ์ดยังอยู่)
setup = c['phases'][0]['form'][0]
target = None
for node, parent, key in list(walk(setup)):
    if not (isinstance(node, dict) and isinstance(parent, list)):
        continue
    t = json.dumps(node, ensure_ascii=False)
    if 'มุมกล้อง & การนำเสนอ' in t and '"field"' not in t:
        target = (parent, key); break
assert target, 'หาการ์ด "มุมกล้อง & การนำเสนอ" ที่ว่างเปล่าไม่เจอ'
parent, key = target
gone = parent.pop(key)
assert '"field"' not in json.dumps(gone, ensure_ascii=False), 'การ์ดที่ลบต้องไม่มีช่องให้กรอกเหลืออยู่'
print('⑦ ลบการ์ด "มุมกล้อง & การนำเสนอ (ขั้นสูง)" ที่เหลือแต่หัวข้อออกจากหน้าตั้งค่า')

s = json.dumps(c, ensure_ascii=False)
assert 'มุมกล้อง & การนำเสนอ' not in s, 'ยังเหลือหัวข้อการ์ดเดิม'
assert 'มุมกล้องหลักของคลิป' not in s, 'ยังเหลือป้ายเดิมในหน้าตั้งค่า'
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'เขียนซ้ำ {P} ({len(s):,} ตัวอักษร)')
