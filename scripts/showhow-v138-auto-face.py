#!/usr/bin/env python3
"""showhow-v138 — ล็อกหน้าตัวละครอัตโนมัติ (เจ้าของสั่ง 26 พ.ย. · ลอกท่า fashion fsModel)
อาการ: "คนเดียวเต็มตัว" + "AI เลือกนาย/นางแบบ" ไม่ส่งรูปหน้าเลย ⇒ หน้าต่างกันทุกบอร์ด/ทุกช่วงวิดีโอ
แก้:
- op ใหม่ mnFace (image · over tasks · out face) วาดรูปหน้าตัวละคร 1 ใบต่อคลิป ก่อนบอร์ด — **ไม่ใช่ aux** อยู่ใน stages + auto.productLoop.gens
  (ต่างจาก fashion ที่เป็นปุ่มเสริม) · where ราย task: people=คนเดียวเต็มตัว · ไม่ได้เลือกใช้รูปหน้าที่แนบ · ไม่ใช่ไทม์แลปส์ · ไม่ใช่โหมดสัตว์จริง/สัตว์ทำตัวเป็นคน/เจ้าของสัตว์
  ⇒ คลิปที่ไม่เข้าเงื่อนไข productLoop ข้ามเอง (loopGenApplies) ไม่นับเป็นพัง
- tasks.slots += face · แนบ tasks.face ต่อจากช่อง face ของตัวละคร ใน mnBoard · mnBoard2 · mnVideo (เพดานยาม G12/G18 — ดูหมายเหตุในโค้ด)
- ถ้อยคำคน (PEOPLE ของวิดีโอ / คน: ของบอร์ด) โหมดนี้ = ประโยค FACE LOCK แทนประโยคเดิม (วิดีโอสั้นกว่าเดิม ⇒ prompt ไม่ยาวขึ้น)
  op ที่แนบรูปหน้า = 'คนในรูปหน้าที่แนบ' · op ที่ไม่แนบ = 'คนเดียวกับในสตอรีบอร์ดที่แนบ'
- บท (charPlan คนเดียวเต็มตัว ไม่มีรูปหน้า): ให้เขียน look อังกฤษ 8-12 คำ — ใช้วาดรูปหน้าให้เข้ากับงาน
- ปุ่มผลิตบอร์ดทั้งชุด (chain/ops ที่มี mnBoard ครบชุด · ไม่ force): เติม mnFace นำหน้า (ข้ามเองเมื่อไม่เข้าเงื่อนไข/มีรูปแล้ว)
  เมนู 'Gen บอร์ดใหม่ · ทั้งหมด' (force) ไม่เติม ⇒ ทำบอร์ดใหม่ได้คนเดิม (หน้าตรงกับวิดีโอเก่า)
ใช้: python3 scripts/showhow-v138-auto-face.py  (รันบน v137)
"""
import json
P = 'showhow-dev.json'
s0 = open(P, encoding='utf-8').read()
c = json.loads(s0)
assert json.dumps(c, ensure_ascii=False, indent=1) + '\n' == s0
ops = {o['id']: o for o in c['ops']}
assert 'mnFace' not in ops, 'รันซ้ำ'
L = c['lookups']
ATT = 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'
AIP = 'AI เลือกนาย/นางแบบให้เหมาะกับสินค้า'
SOLO = 'คนเดียวเต็มตัว'

# ── ถ้อยคำ ──
#   🪤 เพดานรูปตามยาม: G12 (วิดีโอ: รูปจาก tasks ≤ 2) + G18 (ภาพนิ่ง: นับทุก entry ≤ 10 แบบกรณีเลวร้ายสุด ไม่รู้ว่า face ตัวละคร/face ของ task ไม่มาพร้อมกัน)
#      ⇒ แนบรูปหน้าได้เฉพาะ บอร์ดช่วง 1-2 + วิดีโอช่วง 1 · บอร์ดช่วง 3-6 / วิดีโอช่วง 2-6 ล็อกหน้าผ่านแผ่นบอร์ดที่แนบ (วาดจากรูปหน้าแล้ว)
#      บอร์ดช่วง 2 ตัด image5 ออก (แบบเดียวกับบอร์ดช่วง 3-6 ที่ตัดอยู่แล้ว) ให้รูปหน้าลงในเพดาน 10
#   🪤 gate ถ้อยคำด้วย field ที่ตัววัดรู้จัก (people/peopleSrc · G16) ไม่ใช่ slot — เงื่อนไขเดียวกับ where ของ mnFace เป๊ะ
FACE_OPS = {'mnBoard', 'mnBoard2', 'mnVideo'}
old_v = L['charVideoEN'][SOLO + '|' + AIP]; old_b = L['charBoard'][SOLO + '|' + AIP]
TX = {
 ('charVideoEN', 1): 'FACE LOCK: the worker is the person in the attached face photo — same face, hair, skin, outfit every scene; absorbed in the task, never poses.',
 ('charVideoEN', 0): 'FACE LOCK: the worker is the same person shown in the sheets — same face, hair, skin, outfit every scene; absorbed in the task, never poses.',
 ('charBoard', 1): 'คนลงมือ 1 คน = คนในรูปหน้าที่แนบ เป๊ะทุกช่อง (หน้า ผม สีผิว ชุดเดิม) ห้ามสร้างหน้าใหม่ ไม่มองกล้อง ไม่โพสท่า',
 ('charBoard', 0): 'คนลงมือ 1 คน = คนเดียวกับในสตอรีบอร์ดที่แนบ เป๊ะทุกช่อง (หน้า ผม สีผิว ชุดเดิม) ห้ามสร้างหน้าใหม่ ไม่มองกล้อง ไม่โพสท่า',
}
for (t, a), v in TX.items():
    L[t]['ใบหน้าตัวละคร|' + ('รูปหน้า' if a else 'บอร์ด')] = v
    assert len(v) <= (len(old_v) if t == 'charVideoEN' else len(old_b) + 30), (t, a, len(v))   # วิดีโอห้ามยาวกว่าเดิม (p95 ชนเพดานอยู่แล้ว) · บอร์ดเหลือ ~320
LOOK = ' · ช่อง look ต้องบรรยายคนนี้เป็นอังกฤษ 8-12 คำ (เพศ ช่วงอายุ ทรงผม สีเสื้อ สีกางเกง) แม้ไม่มีรูปใบหน้า — ใช้วาดรูปหน้าตัวละคร'
for k in (SOLO + '|' + AIP, SOLO + '|'):
    assert 'ช่อง look' not in L['charPlan'][k]; L['charPlan'][k] += LOOK

AUTO = {'op': 'and', 'list': [{'op': 'eq', 'a': '{item.people}', 'b': SOLO}, {'op': 'not', 'a': {'op': 'eq', 'a': '{item.peopleSrc}', 'b': ATT}}]}
nP = 0
def swap(x, table, has):
    global nP
    if isinstance(x, dict):
        for k, v in list(x.items()):
            if isinstance(v, dict) and v.get('op') == 'lookup' and v.get('table') == table and v.get('key') == '{item.people}|{item.peopleSrc}':
                x[k] = {'op': 'cond', 'when': json.loads(json.dumps(AUTO)),
                        'then': {'op': 'lookup', 'table': table, 'key': 'ใบหน้าตัวละคร|' + ('รูปหน้า' if has else 'บอร์ด'), 'fallback': ''}, 'else': v}
                nP += 1
            else: swap(v, table, has)
    elif isinstance(x, list):
        for v in x: swap(v, table, has)
K = ['', '2', '3', '4', '5', '6']
for k in K:
    for oid, t in (('mnBoard' + k, 'charBoard'), ('mnVideo' + k, 'charVideoEN')):
        swap(ops[oid]['prompt'], t, oid in FACE_OPS)
assert nP == 12, nP

# ── refs: tasks.face ต่อจาก characters.face (เฉพาะ FACE_OPS) ──
TREF = {'from': 'tasks', 'by': '{item.id}', 'slot': 'face', 'when': AUTO}
for oid in sorted(FACE_OPS):
    also = ops[oid]['refs']['also']
    if oid == 'mnBoard2':
        j = next(j for j, r in enumerate(also) if r.get('slot') == 'image5'); del also[j]
    i = next(i for i, r in enumerate(also) if r.get('from') == 'characters' and r.get('slot') == 'face')
    also.insert(i + 1, json.loads(json.dumps(TREF)))
nR = len(FACE_OPS)

# ── slot + op ──
c['collections']['tasks']['slots'].append('face')
NE = lambda f, v: {'op': 'not', 'a': {'op': 'eq', 'a': '{values.%s}' % f if f.startswith('sv') else '{item.%s}' % f, 'b': v}}
face = {
 'id': 'mnFace', 'type': 'image', 'over': 'tasks', 'out': 'face',
 'model': '{values.imageModel}', 'aspectRatio': '9:16',
 'prompt': {'op': 'concat', 'parts': [
  'Character reference photo for a Thai how-to video series about "{item.productName}": ONE ordinary Thai adult who fits this job',
  {'op': 'block', 'sep': '', 'parts': [{'when': 'item.look!=', 'value': ', look: {item.look}'}]},
  '. Waist-up portrait facing the camera, face fully visible and sharp, relaxed natural expression, arms relaxed, simple work clothes that suit the job (keep the outfit in the look if given). Ordinary non-famous everyday face with its own small quirks, never a celebrity look-alike. Plain soft light-grey background, even soft daylight. ',
  {'op': 'block', 'sep': '', 'parts': [
   {'when': {'op': 'or', 'a': {'op': 'eq', 'a': '{values.svStyle}', 'b': ''}, 'b': {'op': 'eq', 'a': '{values.svStyle}', 'b': 'real'}},
    'value': 'Real smartphone photo, real skin texture, natural colours, true-white balance — NOT AI-looking, NOT CGI, NOT plastic skin'},
   {'when': {'op': 'and', 'a': NE('svStyle', ''), 'b': NE('svStyle', 'real')},
    'value': {'op': 'concat', 'parts': ['Draw the person in this look: ', {'op': 'lookup', 'table': 'styleVideoEN', 'key': '{values.svStyle}', 'fallback': ''}]}}]},
  '. No text, no logos, no watermark, no other people.']},
 'where': ['people=' + SOLO, 'peopleSrc!=' + ATT, 'arc!=ไทม์แลปส์กล้องนิ่ง', 'castKind!=animalReal', 'castKind!=animalAnthro', 'castKind!=petOwner'],   # = เงื่อนไขที่ PEOPLE ใช้ประโยค FACE LOCK (ไทม์แลปส์/โหมดสัตว์ ใช้ประโยคอื่น)
 'logRun': '[{item.productName} คลิป {item.clipIndex}] กำลังวาดหน้าตัวละคร (ใช้ล็อกหน้าทุกบอร์ดและวิดีโอ)',
 'logDone': '[{item.productName} คลิป {item.clipIndex}] วาดหน้าตัวละครเสร็จแล้ว',
 'timeoutMs': 180000,
}
qi = next(i for i, o in enumerate(c['ops']) if o['id'] == 'mnQueue')
c['ops'].insert(qi + 1, face)
st = c['stages']; si = next(i for i, s in enumerate(st) if s.get('op') == 'mnQueue'); st.insert(si + 1, {'op': 'mnFace'})
g = c['auto']['productLoop']['gens']; assert g[0] == 'mnBoard'; g.insert(0, 'mnFace')

# ── ปุ่มผลิตบอร์ดทั้งชุด ──
FULL = {'mnBoard', 'mnBoard2', 'mnBoard3', 'mnBoard4', 'mnBoard5', 'mnBoard6'}
nB = 0
def btn(x):
    global nB
    if isinstance(x, dict):
        for key in ('chain', 'ops'):
            v = x.get(key)
            if isinstance(v, list) and FULL <= set(v) and 'mnFace' not in v and x.get('force') is not True:   # เมนู 'ทำใหม่ทั้งหมด' (force) ไม่วาดหน้าใหม่ — คนเดิมทั้งคลิปแม้ทำบอร์ดใหม่
                x[key] = ['mnFace'] + v; nB += 1
        for v in x.values(): btn(v)
    elif isinstance(x, list):
        for v in x: btn(v)
btn(c['phases'])
print(f'✅ v138: PEOPLE {nP} · refs {nR} op · ปุ่ม {nB} · op mnFace ใน stages+gens')
open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
