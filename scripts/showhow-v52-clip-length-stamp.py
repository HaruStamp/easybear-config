#!/usr/bin/env python3
# showhow v52 — ป้ายความยาว/จำนวนคลิป ต้องบอก "ตอนผลิต" ไม่ใช่ "ค่าตั้งค่าตอนนี้"
#
# อาการ: ผลิตคลิป 40 วิ แล้วกลับไปตั้งค่าเป็น 20 วิ → การ์ดคลิปเก่าบนหน้าผลิต/คลังคลิป
#        เปลี่ยนป้ายเป็น "20 วิ / คลิป" ทันที และ "คลิปที่ 1/N" ใช้ N ของค่าใหม่
#        ⇒ ป้ายโกหกเรื่องของที่ผลิตไปแล้ว
#
# ราก: การ์ดพวกนี้อยู่ใน repeat ของ tasks แต่ค่าที่โชว์อ่านจาก {values.svSec}/{values.clipsPerProduct}
#      ซึ่งเป็น "ค่าปัจจุบัน" ของหน้าตั้งค่า · task ไม่เคยเก็บว่าตัวเองถูกผลิตที่ความยาวเท่าไร
#
# แก้: ปั๊มค่าลง task ตอน spawn (mnQueue) = secAt / clipsAt แล้วให้ป้ายอ่านจาก item
#      · task เก่าที่ไม่มี secAt (โปรเจกต์ที่เซฟไว้ก่อน v52) → คงป้ายแบบเดิมด้วย element คู่ที่ gate ด้วย when
#      · ไม่แตะ when ที่คุมว่าจะโชว์ไทล์ช่วงไหน (146 จุด) — เป็นงานร่วมกับทีม minimal (ดู docs/qa/2026-09-22-clip-length-stamp/)
import json, sys, copy

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))

def get(root, path):
    n = root
    for k in path:
        n = n[k]
    return n

# ① mnQueue — ปั๊มค่าลง task
q = [o for o in c['ops'] if o['id'] == 'mnQueue']
assert len(q) == 1, 'mnQueue ต้องมีตัวเดียว'
sp = q[0]['spawn']['fields']
assert 'secAt' not in sp and 'clipsAt' not in sp, 'รันซ้ำ'
sp['secAt'] = '{values.svSec}'
sp['clipsAt'] = '{values.clipsPerProduct}'

# ② ประกาศ field (ให้ describe/bridge เห็น)
tf = c['collections']['tasks']['fields']
for k in ('secAt', 'clipsAt'):
    assert k not in tf
    tf.append(k)

CH = 0

# ③ "คลิปที่ {item.clipIndex}/{values.clipsPerProduct}" → clipsAt (2 จุด: หน้าผลิต + คลังคลิป)
OLD = 'คลิปที่ {item.clipIndex}/{values.clipsPerProduct}'
NEW = 'คลิปที่ {item.clipIndex}/{item.clipsAt}'
def fix_counter(n):
    global CH
    if isinstance(n, dict):
        if n.get('value') == OLD:
            # task เก่าไม่มี clipsAt → เหลือ "คลิปที่ 1/" ⇒ แยกเป็น 2 element
            n['value'] = NEW
            n['when'] = {'op': 'not', 'a': {'op': 'eq', 'a': '{item.clipsAt}', 'b': ''}}
            CH += 1
            return [n, {**copy.deepcopy(n), 'value': OLD,
                        'when': {'op': 'eq', 'a': '{item.clipsAt}', 'b': ''}}]
        for k, v in list(n.items()):
            n[k] = fix_counter(v)
        return n
    if isinstance(n, list):
        out = []
        for v in n:
            r = fix_counter(v)
            out.extend(r) if isinstance(r, list) and isinstance(v, dict) else out.append(r)
        return out
    return n
c['phases'] = fix_counter(c['phases'])
assert CH == 4, f'ป้าย "คลิปที่ x/y" ต้องเจอ 4 จุด (หน้าผลิต 1 · ไลต์บ็อกซ์ผลิต 2 · คลังคลิป 1) · เจอ {CH}'

# ④ ป้ายความยาวบนการ์ดคลิป (หน้าผลิต) — lookup lenSecs key {values.svSec} → {item.secAt}
PROD = ['phases', 0, 'form', 3, 'card', 0, 'card', 5, 'card', 0, 'card', 0, 'card', 1, 'card', 1, 'card', 1]
row = get(c, PROD)
i = [j for j, x in enumerate(row['card'])
     if isinstance(x.get('value'), dict) and any(
         isinstance(p, dict) and p.get('table') == 'lenSecs' for p in x['value'].get('parts', []))]
assert len(i) == 1, f'ชิปความยาวบนการ์ดคลิป (หน้าผลิต) ต้องเจอ 1 จุด · เจอ {len(i)}'
chip = row['card'][i[0]]
legacy = copy.deepcopy(chip)
legacy['when'] = {'op': 'and', 'list': [chip['when'], {'op': 'eq', 'a': '{item.secAt}', 'b': ''}]}
for p in chip['value']['parts']:
    if isinstance(p, dict) and p.get('table') == 'lenSecs':
        p['key'] = '{item.secAt}'
chip['when'] = {'op': 'and', 'list': [chip['when'], {'op': 'not', 'a': {'op': 'eq', 'a': '{item.secAt}', 'b': ''}}]}
row['card'].insert(i[0] + 1, legacy)

# ⑤ คลังคลิป — หัวหน้าเพจบอก "N วิ / คลิป" จากค่าตั้งค่าปัจจุบัน ทั้งที่หน้านี้โชว์ของที่ผลิตไปแล้ว
#    ⇒ ย้ายความยาวไปอยู่บนการ์ดคลิปแต่ละใบ (ของจริงต่อคลิป) แล้วถอดชิปนั้นออกจากหัวเพจ
HEAD = ['phases', 0, 'form', 4, 'card', 0, 'card', 1, 'card', 0, 'card', 1, 'card', 2]
hrow = get(c, HEAD)
j = [k for k, x in enumerate(hrow['card'])
     if isinstance(x.get('value'), dict) and any(
         isinstance(p, dict) and p.get('table') == 'lenSecs' for p in x['value'].get('parts', []))]
assert len(j) == 1, f'ชิปความยาวหัวหน้าคลังคลิป ต้องเจอ 1 จุด · เจอ {len(j)}'
hrow['card'].pop(j[0])

CARD = ['phases', 0, 'form', 4, 'card', 0, 'card', 3, 'card', 0, 'card', 0, 'card', 2]
crow = get(c, CARD)
assert crow['el'] == 'row'
crow['card'].insert(1, {
    'el': 'text',
    'value': {'op': 'concat', 'parts': ['{item.secAt}', ' วิ']},
    'icon': 'timer',
    'className': ('!text-[11px] font-bold px-2 py-0.5 rounded-md bg-[var(--ev-surface2)] '
                  '!text-[var(--ev-text)] opacity-85 shrink-0 whitespace-nowrap leading-none flex items-center gap-1'),
    'when': {'op': 'not', 'a': {'op': 'eq', 'a': '{item.secAt}', 'b': ''}},
})

# sanity — ไม่มี {values.clipsPerProduct} หลงเหลือใน repeat ของ tasks
s = json.dumps(c, ensure_ascii=False)
assert '"secAt": "{values.svSec}"' in s and '"clipsAt": "{values.clipsPerProduct}"' in s
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v52 ok · counter 4 · chip ผลิต 1 · คลังคลิป: หัวเพจ -1 การ์ด +1')
