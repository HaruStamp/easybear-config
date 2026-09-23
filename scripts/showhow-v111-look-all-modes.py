#!/usr/bin/env python3
"""showhow-v111 — 🐛 ลุคผู้แสดง (เพศ/วัย/ชุด) ไม่ถึงบอร์ด/วิดีโอ ยกเว้นโหมด "ใช้รูปตัวละคร" (ผลิตจริงคืน 2026-09-24)

เคส V2: เสียงผู้หญิง + บท look "Thai woman early 20s ponytail" → บนจอเป็นผู้ชายทั้งคลิป
เคส B2: คนเปลี่ยนเพศกลางคลิป · เคส B1: เสื้อเปลี่ยนตอนจบ
สาเหตุ: บล็อก " | {item.look}" (บอร์ด) / " | PERSON: {item.look}" (วิดีโอ) gate ด้วย people=เต็มตัว AND peopleSrc=ใช้รูปใบหน้า
   ⇒ ค่าตั้งต้น "สุ่มตัวละคร" + โหมดเห็นตัวไม่เห็นหน้า ไม่เคยได้ look ⇒ เพศ/ชุดที่ผู้ใช้เลือก (charGender) ไม่ถึงภาพเลย
แก้: gate = people ∈ {เต็มตัว, เห็นตัวไม่เห็นหน้า} (ไม่ดูแหล่งหน้า) · ไม่ใช่ไทม์แลปส์ (เดิม)
ใช้: python3 scripts/showhow-v111-look-all-modes.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
J = lambda x: json.dumps(x, ensure_ascii=False)
FACE = 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'
TL = {'op': 'not', 'a': {'op': 'eq', 'a': '{item.arc}', 'b': 'ไทม์แลปส์กล้องนิ่ง'}}
OLD = {'op': 'and', 'a': {'op': 'and', 'a': {'op': 'eq', 'a': '{item.people}', 'b': 'คนเดียวเต็มตัว'},
                          'b': {'op': 'eq', 'a': '{item.peopleSrc}', 'b': FACE}}, 'b': TL}
NEW = {'op': 'and', 'a': {'op': 'or', 'a': {'op': 'eq', 'a': '{item.people}', 'b': 'คนเดียวเต็มตัว'},
                          'b': {'op': 'eq', 'a': '{item.people}', 'b': 'เห็นตัว ไม่เห็นหน้า'}}, 'b': TL}


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


n = 0
for o in c['ops']:
    if not o['id'].startswith(('mnBoard', 'mnVideo')): continue
    for x in walk(o['prompt']):
        if isinstance(x, dict) and x.get('when') == OLD and '{item.look}' in J(x.get('value')):
            x['when'] = NEW; n += 1
assert n == 12, n
print(f'ลุคผู้แสดงถึงบอร์ด/วิดีโอทุกโหมดที่เห็นตัว: {n} จุด (บอร์ด 6 + วิดีโอ 6)')

# ── ชดเชยความยาว (แทนที่ ไม่ต่อท้าย): PERSON: {look} บอกตัวตนแล้ว ⇒ ตัดคำที่ซ้ำในกฎคนของวิดีโอ ──
L = c['lookups']['charVideoEN']
OLD_FULL = 'one Thai worker, the same person in every scene, absorbed in the task; never looks at, poses for or smiles at the camera; face consistent and natural; the work stays the focus.'
NEW_FULL = 'one Thai worker as in PERSON, the same person every scene, absorbed in the task; never looks at or poses for the camera; the work is the focus.'
OLD_BODY = 'the worker is framed from the neck down — body, arms and hands at work, never the face; same outfit in every scene, never posing.'
NEW_BODY = 'framed from the neck down — body, arms, hands at work, never the face; same outfit every scene.'
m = 0
for k, v in list(L.items()):
    if v == OLD_FULL: L[k] = NEW_FULL; m += 1
    elif v == OLD_BODY: L[k] = NEW_BODY; m += 1
assert m == 5, m
print(f'กฎคนในวิดีโอสั้นลง {m} คีย์ (เต็มตัว -{len(OLD_FULL)-len(NEW_FULL)} · ไม่เห็นหน้า -{len(OLD_BODY)-len(NEW_BODY)})')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
