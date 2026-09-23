#!/usr/bin/env python3
"""showhow-v85 — "ผู้แสดงเป็นอะไร" (คน / สัตว์จริง / สัตว์ทำตัวเหมือนคน / สัตว์การ์ตูน)

พี่หมีสั่งให้ทำแบบเดียวกับ flim · ทีม flim ให้แนวทางมาครบ (อ่านจาก `easybear-flim/src/services/castKind.ts`)
🪤 flim **ไม่ได้รันบน EasyBear Engine** ⇒ ไม่มี config ให้ก๊อป ต้องทำเป็น config เอง แต่ใช้ชื่อ/คีย์ให้ตรงกัน

## ทำไมต้องมี override ไม่ใช่แค่เพิ่มบล็อก (บทเรียนที่ flim จ่ายไปแล้ว)
ของเรามีคำที่ **ดึงตัวละครกลับเป็นคน** ฝังอยู่ในโหมด "คนเดียวเต็มตัว":
    charPlan     "มีผู้ลงมือ 1 คน (คนไทย) …"
    charVideoEN  "one Thai worker … face consistent and natural"
⇒ เลือก "สัตว์" แล้วไม่ทับ = ได้ **"คนหัวสัตว์"** (อาการที่ flim เจอจริงและเสียเวลาไล่ 3 ชั้นกว่าจะเจอราก)
⇒ ★ ต้องมี **3 ชิ้น** ไม่ใช่ชิ้นเดียว: ① บล็อกบอกว่าเป็นสัตว์แบบไหน ② override ทับคำที่พูดถึงคน ③ negative ห้ามรูปทรงคนหัวสัตว์

## ที่ต่างจาก flim โดยตั้งใจ
flim ตัดสิน **รายตัวละคร** (`Character.kind`) เพราะเรื่องหนึ่งมีทั้งเด็กและหมาได้
showhow มีผู้ลงมือ **คนเดียว/ชุดเดียว** ต่อคลิป ⇒ ตัดสิน **รายงาน** พอ — ง่ายกว่าและตรงกับโครงที่มีอยู่
⇒ ถ้าวันหน้าต้องมีหลายตัวละครในคลิปเดียว ค่อยยกท่า `Character.kind` ของ flim มา

## ประหยัดเพดาน prompt (3,900)
ทุกบล็อกใหม่ gate ด้วย `castKind` ⇒ **โหมดคนปกติไม่ยาวขึ้นเลยสักตัวอักษร**

ใช้: python3 scripts/showhow-v85-cast-kind.py
"""
import json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))

KINDS = ['auto', 'human', 'animalReal', 'animalAnthro', 'animalToon']
ANIMAL = ['animalReal', 'animalAnthro', 'animalToon']
P_NONE = 'ไม่มีคน'


def walk(n, parent=None, key=None):
    yield n, parent, key
    if isinstance(n, dict):
        for k, v in n.items(): yield from walk(v, n, k)
    elif isinstance(n, list):
        for i, v in enumerate(n): yield from walk(v, n, i)


# ── ① field + spawn ───────────────────────────────────────────────────────────
pf = c['collections']['products']['fields']
tf = c['collections']['tasks']['fields']
if isinstance(pf, dict): pf.setdefault('castKind', '')
elif 'castKind' not in pf: pf.append('castKind')
if 'castKind' not in tf: tf.append('castKind')
c['collections']['products']['addDefaults'].setdefault('castKind', 'auto')
q = next(o for o in c['ops'] if o['id'] == 'mnQueue')
q['spawn']['fields']['castKind'] = '{parent.fields.castKind}'
print('① field castKind (products + tasks + spawn) · ค่าตั้งต้น auto')

# ── ② lookup — ค่าเป็น key อังกฤษ ป้ายไทยอยู่แค่บนจอ ──────────────────────────
# 🔴 value อังกฤษล้วน: ของ showhow เคยโดนแล้ว — value ไทยถูกเสียบลง prompt แล้วโมเดล "พิมพ์คำนั้นลงบนจอ"
c['lookups']['castPlan'] = {
    'auto': '',
    'human': '',
    'animalReal': ('★ ผู้ลงมือในคลิปนี้เป็น **สัตว์จริง** ไม่ใช่คน — เดิน 4 ขา ท่าทางและสัดส่วนแบบสัตว์จริง '
                   'ไม่ใส่เสื้อผ้า ไม่ถือของด้วยอุ้งเท้า ทำตัวเหมือนสัตว์จริง ๆ · '
                   'เขียน s*th/s*en ให้ประธานเป็นตัวสัตว์ ห้ามเขียนว่ามีคนหรือมือคนในเฟรม'),
    'animalAnthro': ('★ ผู้ลงมือในคลิปนี้เป็น **สัตว์ที่ทำตัวเหมือนคน** ไม่ใช่คน — ยืน/นั่งตัวตรง ใช้อุ้งเท้าหน้าแทนมือ '
                     'ใส่เสื้อผ้า เล่นเป็นตัวละคร · ขนฟูน่ารัก ตากลมโต · '
                     'เขียน s*th/s*en ให้ประธานเป็นตัวสัตว์ ห้ามเขียนว่ามีคนในเฟรม'),
    'animalToon': ('★ ผู้ลงมือในคลิปนี้เป็น **ตัวการ์ตูนสัตว์แบบแอนิเมชัน** ไม่ใช่คน — รูปทรงสัตว์จริง (ปาก หู หาง อุ้งเท้า) '
                   'ตาโตแสดงอารมณ์ เส้นสะอาด สีสด · ยังคงเป็นสัตว์ ไม่ใช่คน · '
                   'เขียน s*th/s*en ให้ประธานเป็นตัวสัตว์ ห้ามเขียนว่ามีคนในเฟรม'),
}
c['lookups']['castBoard'] = {
    'auto': '', 'human': '',
    'animalReal': 'ผู้ลงมือเป็นสัตว์จริง เดิน 4 ขา ไม่ใส่เสื้อผ้า สัดส่วนแบบสัตว์จริง ห้ามวาดคนหรือมือคน',
    'animalAnthro': 'ผู้ลงมือเป็นสัตว์ที่ทำตัวเหมือนคน ยืนตัวตรง ใส่เสื้อผ้า ใช้อุ้งเท้าหน้าแทนมือ ขนฟู ตากลมโต ห้ามวาดคน',
    'animalToon': 'ผู้ลงมือเป็นตัวการ์ตูนสัตว์ รูปทรงสัตว์จริง ตาโต สีสด เส้นสะอาด ห้ามวาดคน',
}
c['lookups']['castVideoEN'] = {
    'auto': '', 'human': '',
    'animalReal': ('the worker is a REAL ANIMAL with true animal anatomy — four legs on the ground, natural animal '
                   'posture and proportions, no clothing, no accessories, behaving exactly like a real animal'),
    'animalAnthro': ('the worker is an adorable anthropomorphic animal acting like a person — standing upright, '
                     'front paws used as hands, wearing clothes, fluffy fur, big round expressive eyes'),
    'animalToon': ('the worker is an ANIMATED cartoon animal character — true animal anatomy (muzzle, ears, tail, paws), '
                   'big expressive eyes, clean bold shapes, bright colours, still an ANIMAL not a person'),
}
# ② override — ทับคำที่พูดถึงคนในบล็อกอื่น (flim: ถ้าไม่ทับ ช็อตสัตว์ถูกดึงกลับเป็นคนทุกครั้ง)
# 🔑 ไม่มี castOverrideEN สำหรับ board/video อีกแล้ว — ดู ③ (แทนที่บล็อกคน ไม่ใช่ทับ)
#    flim ต้อง "ทับ" เพราะเขาแก้ข้อความต้นทางไม่ได้ · ของเราเป็น config ⇒ **ปิดบล็อกคนไปเลย** ถูกกว่าและสั้นกว่า
c['lookups']['castOverrideTH'] = {k: '' for k in ('auto', 'human')}
for k in ANIMAL:
    c['lookups']['castOverrideTH'][k] = '★ ทับกฎคนด้านบน: ผู้ลงมือเป็นสัตว์ ไม่ใช่คน — คำที่พูดถึงคนไทย/ใบหน้าคน/มือคน ให้ข้ามทั้งหมด'
# ③ negative — ห้ามรูปทรง "คนหัวสัตว์" (flim บอกว่าของเดิมไม่มี = ต้นตอบั๊ก)
c['lookups']['castNegEN'] = {k: '' for k in ('auto', 'human')}
for k in ANIMAL:
    c['lookups']['castNegEN'][k] = ' no human face, no human hands, no animal head on a human body, no mascot suit'
c['lookups']['castNegEN']['animalReal'] += ', no clothes on the animal'
print('② lookup 5 ตัว: castPlan · castBoard · castVideoEN · castOverrideTH · castNegEN (value = key อังกฤษ)')

# ── ③ เสียบเข้า ops — gate ด้วย castKind ⇒ โหมดคนไม่ยาวขึ้น ────────────────────
def lk(table, fb=''):
    return {'op': 'lookup', 'table': table, 'key': '{item.castKind}', 'fallback': fb}

# ── ③ เสียบเข้า ops — **แทนที่บล็อกคน** ไม่ใช่ต่อท้าย ─────────────────────────
# 🔴 บทเรียนรอบนี้ (วัดแล้วถึงรู้): เพดาน 3,900 **ไม่เหลือที่ให้ต่อท้ายอะไรอีกแล้ว**
#    ของเดิม (ก่อน v85) บอร์ดเหลือ 22 ตัวอักษร · วิดีโอกินบรรทัด Negative อยู่แล้ว
#    ต่อกฎสัตว์ท้าย prompt = บอร์ดทะลุ 2,918 เคส ⇒ กฎหายเงียบ = ได้คนหัวสัตว์ทั้งที่ config ถูก
# ⇒ โหมดสัตว์ **ปิดบล็อกคนทิ้งแล้ววางกฎสัตว์แทนที่เดิม** — ยาวเท่าเดิม ไม่มีข้อความขัดกันเองให้โมเดลเลือกข้าง
#    (flim ต้องใช้วิธี "ทับ" เพราะแก้ข้อความต้นทางไม่ได้ · ของเราเป็น config จึงปิดได้ตรง ๆ = ถูกกว่าและชัดกว่า)
IS_ANIMAL = {'op': 'not', 'a': {'op': 'or', 'list': [
    {'op': 'eq', 'a': '{item.castKind}', 'b': 'auto'},
    {'op': 'eq', 'a': '{item.castKind}', 'b': 'human'},
    {'op': 'eq', 'a': '{item.castKind}', 'b': ''},
]}}
NOT_ANIMAL = {'op': 'not', 'a': IS_ANIMAL}


def gate(when, value):
    return {'op': 'block', 'sep': '', 'parts': [{'when': when, 'value': value}]}


def swap_people(parts, i_first, n, table):
    """ห่อบล็อกคน n ชิ้นตั้งแต่ index i_first ด้วย 'ไม่ใช่สัตว์' แล้ววางกฎสัตว์ต่อท้ายทันที"""
    for j in range(i_first, i_first + n):
        parts[j] = gate(NOT_ANIMAL, parts[j])
    parts.insert(i_first + n, gate(IS_ANIMAL, lk(table)))


n_plan = n_board = n_vid = 0
for op in c['ops']:
    oid = op['id']
    if not (oid == 'mnPlan' or oid.startswith('mnBoard') or oid.startswith('mnVideo')):
        continue
    parts = op['prompt']['parts']
    J = lambda x: json.dumps(x, ensure_ascii=False)
    if oid == 'mnPlan':
        # mnPlan เป็น llm ไม่ผ่าน execLeaf ⇒ ไม่ถูกตัด · ที่นี่ "ทับ" พอ (ถูกกว่าการรื้อบล็อกบท)
        parts.append(lk('castPlan'))
        parts.append(lk('castOverrideTH'))
        n_plan += 1
    elif oid.startswith('mnBoard'):
        i = next(k for k, x in enumerate(parts) if 'คน: ' in J(x))
        assert 'charBoard' in J(parts[i + 1]), f'{oid}: หลัง "คน: " ควรเป็นกฎคนของบอร์ด'
        assert '{item.people}' in J(parts[i + 2]), f'{oid}: ชิ้นถัดไปควรเป็นบล็อกล็อกหน้า'
        swap_people(parts, i + 1, 2, 'castBoard')
        n_board += 1
    else:
        i = next(k for k, x in enumerate(parts) if 'PEOPLE: ' in J(x))
        # ชิ้นนี้เป็น concat ["\n\nPEOPLE: ", <บล็อกกฎคน>] — ต้องเข้าไปสลับ "ข้างใน" ไม่งั้นหัวข้อ PEOPLE หายไปด้วย
        inner = parts[i]['parts']
        k_people = next(k for k, x in enumerate(inner) if 'charVideoEN' in J(x))
        inner[k_people] = gate(NOT_ANIMAL, inner[k_people])
        inner.insert(k_people + 1, gate(IS_ANIMAL, lk('castVideoEN')))
        assert '{item.people}' in J(parts[i + 1]), f'{oid}: ชิ้นถัดจาก PEOPLE ควรเป็นบล็อกล็อกหน้า'
        parts[i + 1] = gate(NOT_ANIMAL, parts[i + 1])      # ล็อกหน้าคนจากรูป = ใช้กับสัตว์ไม่ได้
        neg = next(k for k, x in enumerate(parts) if isinstance(x, str) and x.startswith('\n\nNegative:'))
        parts.insert(neg + 1, lk('castNegEN'))             # ต่อท้ายบรรทัด Negative โดยตั้งใจ (เป็นเนื้อเดียวกัน)
        n_vid += 1
print(f'③ แทนที่บล็อกคนด้วยกฎสัตว์: mnPlan {n_plan} · mnBoard {n_board} · mnVideo {n_vid} (โหมดคนยาวเท่าเดิมทุกตัวอักษร)')

# ── ④ UI — ต่อจาก "เห็นคนแค่ไหน" · ซ่อนเมื่อ "ไม่มีคน" ────────────────────────
anchor = None
for n, p, k in walk(c):
    if isinstance(n, dict) and n.get('field') == 'people' and isinstance(p, list):
        anchor = (p, k); break
assert anchor, 'หา grid-select ของ people ไม่เจอ'
p, k = anchor
NOT_NONE = {'op': 'not', 'a': {'op': 'eq', 'a': '{item.people}', 'b': P_NONE}}
blocks = [
    {'el': 'text', 'value': 'ผู้แสดงเป็นอะไร', 'when': NOT_NONE,
     'className': '!text-[13px] @[640px]:!text-[12.5px] opacity-60 px-0.5 mt-1'},
    {'el': 'grid-select', 'field': 'castKind', 'cols': 2, 'contained': True, 'when': NOT_NONE,
     'className': '!min-h-[44px] @[420px]:!min-h-0',
     'options': [
         {'value': 'auto', 'label': 'ดูจากงานเอง', 'desc': 'งานบอกว่าเป็นสัตว์ก็เป็นสัตว์', 'icon': 'auto_awesome'},
         {'value': 'human', 'label': 'คนล้วน', 'desc': 'เป็นมนุษย์เสมอ', 'icon': 'person'},
         {'value': 'animalReal', 'label': 'สัตว์จริง', 'desc': 'เดิน 4 ขา ไม่ใส่เสื้อผ้า', 'icon': 'pets'},
         {'value': 'animalAnthro', 'label': 'สัตว์ทำตัวเหมือนคน', 'desc': 'ยืน 2 ขา ใส่เสื้อผ้า', 'icon': 'emoji_nature'},
         {'value': 'animalToon', 'label': 'สัตว์การ์ตูน', 'desc': 'แอนิเมชัน ตาโต สีสด', 'icon': 'animation'},
     ]},
]
for i, b in enumerate(blocks):
    p.insert(k + 1 + i, b)
print('④ UI: "ผู้แสดงเป็นอะไร" 5 ตัวเลือก ต่อจาก "เห็นคนแค่ไหน" · ซ่อนเมื่อเลือก "ไม่มีคน"')

# ── ยาม ───────────────────────────────────────────────────────────────────────
s = json.dumps(c, ensure_ascii=False)
for t in ('castPlan', 'castBoard', 'castVideoEN', 'castOverrideTH', 'castNegEN'):
    assert set(c['lookups'][t]) == set(KINDS), f'{t} คีย์ไม่ครบ 5 โหมด'
    assert c['lookups'][t]['human'] == '' and c['lookups'][t]['auto'] == '', f'{t}: human/auto ต้องว่าง (ไม่เพิ่มความยาวให้โหมดคน)'
for nd in [n for n, _, _ in walk(c) if isinstance(n, dict) and n.get('field') == 'castKind' and n.get('options')]:
    assert [o['value'] for o in nd['options']] == KINDS, 'ลำดับ/ค่า option ไม่ตรง'
    for o in nd['options']:
        assert o['value'].isascii(), f'option.value ต้องเป็นอังกฤษล้วน — เจอ {o["value"]!r}'
assert '{parent.fields.castKind}' in s and '{item.castKind}' in s
# 🛡️ ยามโครง: ทุก op สื่อต้องมี "ทางคน" และ "ทางสัตว์" ครบคู่ และต้องเป็นทางแยก (ไม่ใช่ต่อกัน)
for op in c['ops']:
    oid = op['id']
    if not oid.startswith(('mnBoard', 'mnVideo')): continue
    blob = json.dumps(op['prompt'], ensure_ascii=False)
    tbl = 'castBoard' if oid.startswith('mnBoard') else 'castVideoEN'
    assert blob.count('"table": "%s"' % tbl) == 1, f'{oid}: ต้องมีกฎสัตว์ 1 ที่'
    n_gate = blob.count(json.dumps(IS_ANIMAL, ensure_ascii=False))
    n_not = blob.count(json.dumps(NOT_ANIMAL, ensure_ascii=False))
    # 🪤 NOT_ANIMAL มี IS_ANIMAL อยู่ข้างใน ⇒ นับ IS_ANIMAL ได้ 1 (ทางสัตว์) + 2 (ที่ซ้อนใน NOT) = 3
    assert n_not == 2, f'{oid}: ประตู "ไม่ใช่สัตว์" ควรมี 2 ที่ (กฎคน + ล็อกหน้า) · มี {n_not}'
    assert n_gate == n_not + 1, f'{oid}: ประตู "เป็นสัตว์" ควรมี 1 ที่ · นับได้ {n_gate} (รวมที่ซ้อนใน not {n_not})'
    if oid.startswith('mnVideo'):
        parts = op['prompt']['parts']
        neg = next(k for k, x in enumerate(parts) if isinstance(x, str) and x.startswith('\n\nNegative:'))
        assert isinstance(parts[neg + 1], dict) and parts[neg + 1].get('table') == 'castNegEN', \
            f'{oid}: castNegEN ต้องต่อท้ายบรรทัด Negative พอดี'
assert 'castOverrideEN' not in s, 'castOverrideEN ไม่ควรเหลือแล้ว (เลิกใช้วิธีทับ)'
print('✅ ยามผ่าน: 5 lookup ครบ 5 โหมด · human/auto ว่าง · value อังกฤษล้วน · spawn ส่งครบ · ทางคน/ทางสัตว์เป็นทางแยกครบ 12 op')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nเขียน {P} แล้ว')
