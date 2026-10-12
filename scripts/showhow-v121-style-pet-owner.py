#!/usr/bin/env python3
"""showhow-v121 — สไตล์ภาพหลายแบบ (แบบ podcast) + รองรับคลิปโฆษณาสัตว์เลี้ยง (พี่หมีสั่ง 2026-10-12)

ที่มา: นักเรียนอยากทำคลิปแนวโฆษณาของใช้สัตว์เลี้ยง (TikTok 5 คลิป) — น้องหมาเป็นตัวเอก มองกล้อง
พูดเองแบบ "หนู…ค่ะ แม่" · เจ้าของเป็นคนใช้สินค้ากับน้อง · ภาพมีทั้งสมจริงและ 3D แบบหนังการ์ตูน

1) สไตล์ภาพ `values.svStyle` (หน้าตั้งค่า §2 · ตัวเลือก/คีย์เดียวกับ podcast)
   '' อัตโนมัติ(=สมจริง) · real · pixar · anime · clay · thai · clean · cyber · ink
   mnBoard*/mnVideo* (เพดาน 3,900): 🔴 **แทนที่ ไม่ต่อท้าย** — ประโยคสไตล์เดิมกลายเป็น lookup
     ค่า '' / real = ข้อความเดิมทุกตัวอักษร · สไตล์อื่นต้อง **สั้นกว่าหรือเท่าของเดิม** (ยามท้ายไฟล์ assert)
   mnPlan (sys · ไม่โดนตัด): สไตล์ที่ไม่ใช่สมจริง = บรรทัดทับคำว่า "ภาพสมจริง" ของ lenSys
   PRODUCT LOCK ไม่แตะ — สินค้ายังต้องตรงรูปจริงในทุกสไตล์ (คลิปตัวอย่างก็เป็นแพ็กจริงในโลก 3D)

2) ผู้แสดง `item.castKind = petOwner` "สัตว์เลี้ยง + เจ้าของ"
   ใช้ท่าเดียวกับโหมดสัตว์ (v85): ค่าที่ไม่ใช่ ''/auto/human/animalToon = ปิดบล็อกคน แล้ววาง cast* แทน
   ⇒ ไม่ต้องแตะ gate ใน op เลย แค่เพิ่มคีย์ใน 5 ตาราง + ตัวเลือกบนจอ
   ต่างจากโหมดสัตว์: น้องมองกล้องได้ ทำหน้าทำตา · มีเจ้าของ 1 คนเป็นคนใช้สินค้ากับน้อง (ไม่เน้นหน้า)

3) ใครพูด `values.svVoiceBy`: '' คนเล่าเรื่อง (เดิม) · star ตัวเอกพูดเอง
   แก้แค่บท (mnPlan) — vo เป็นคำพูดบุรุษที่ 1 ของตัวเอก (สัตว์ = "หนู" เรียกเจ้าของ "แม่")
   วิดีโอไม่แตะ: คลิปตัวอย่างเป็นเสียงพากย์ทับภาพอยู่แล้ว ไม่ต้องขยับปาก ⇒ prompt วิดีโอยาวเท่าเดิม
ใช้: python3 scripts/showhow-v121-style-pet-owner.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
J = lambda x: json.dumps(x, ensure_ascii=False)
L = c['lookups']


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


# ══ 1) สไตล์ภาพ ══
B_OLD = 'ภาพถ่ายจริงจากกล้อง สไตล์สารคดีในบ้าน ห้ามเป็นภาพวาด การ์ตูน เวกเตอร์ หรือ 3D เรนเดอร์'
V_OLD = 'realistic documentary look of a real lived-in home'
L['styleBoard'] = {
    '': B_OLD, 'real': B_OLD,
    'pixar': 'การ์ตูน 3D แบบแอนิเมชันฉายโรง ผิวนุ่ม ตาโต แสงนวล ทั้งตัวละครและห้อง',
    'anime': 'อนิเมะ 2D เส้นสะอาด สีสด ทั้งตัวละครและห้อง ไม่ใช่ภาพถ่าย',
    'clay': 'ดินน้ำมันแบบสต็อปโมชัน พื้นผิวมีรอยนิ้ว ทั้งตัวละครและห้อง',
    'thai': 'ภาพถ่ายจริงในบ้านไทยท้องถิ่น ของประดับและสีแบบไทย ห้ามเป็นภาพวาดหรือการ์ตูน',
    'clean': 'ภาพถ่ายจริงแบบมินิมอล ของในฉากน้อย สีน้อย แสงขาวนวล',
    'cyber': 'ไซเบอร์พังก์ ไฟนีออนม่วง-ฟ้า คอนทราสต์สูง',
    'ink': 'ภาพวาดลายเส้นหมึกแบบนิยายภาพ ตัดเส้นดำหนา สีหม่นอุ่น ทั้งตัวละครและห้อง',
}
L['styleVideoEN'] = {
    '': V_OLD, 'real': V_OLD,
    'pixar': '3D animated-film look, soft shading, big cute eyes',
    'anime': '2D anime look, clean lines, vivid flat colours',
    'clay': 'claymation stop-motion look, fingerprint textures',
    'thai': 'realistic documentary look of a Thai local home',
    'clean': 'minimal realistic look, few props, soft light',
    'cyber': 'cyberpunk look, purple-blue neon, high contrast',
    'ink': 'inked graphic-novel art, bold lines, muted tones',
}
L['stylePlan'] = {
    'pixar': 'การ์ตูน 3D แบบแอนิเมชันฉายโรง ตัวละครตาโต ท่าทางน่ารักเกินจริงได้',
    'anime': 'อนิเมะ 2D เส้นสะอาด สีสด',
    'clay': 'ดินน้ำมัน/สต็อปโมชัน',
    'thai': 'สมจริง โทนบ้านไทยท้องถิ่น',
    'clean': 'สมจริงแบบมินิมอล ของในฉากน้อย',
    'cyber': 'ไซเบอร์พังก์ ไฟนีออนม่วง-ฟ้า',
    'ink': 'ภาพวาดลายเส้นหมึกแบบนิยายภาพ',
}
c['values']['svStyle'] = ''
ST_B = {'op': 'lookup', 'table': 'styleBoard', 'key': '{values.svStyle}', 'fallback': B_OLD}
ST_V = {'op': 'lookup', 'table': 'styleVideoEN', 'key': '{values.svStyle}', 'fallback': V_OLD}


def split_str(parent, idx, old, node):
    s = parent[idx]
    a, b = s.split(old, 1)
    parent[idx:idx + 1] = [x for x in (a, node, b) if x != '']


n_b = n_v = 0
for o in c['ops']:
    oid = o['id']
    if not (oid.startswith('mnBoard') or oid.startswith('mnVideo')): continue
    old, node = (B_OLD, ST_B) if oid.startswith('mnBoard') else (V_OLD, ST_V)
    for n in list(walk(o['prompt'])):
        if isinstance(n, dict) and isinstance(n.get('parts'), list):
            for i, s in enumerate(n['parts']):
                if isinstance(s, str) and old in s:
                    split_str(n['parts'], i, old, dict(node))
                    if oid.startswith('mnBoard'): n_b += 1
                    else: n_v += 1
                    break
    assert J(o['prompt']).count(old) == 1, f'{oid}: ประโยคสไตล์เดิมต้องเหลือแค่ใน fallback ของ lookup'
assert n_b == 6 and n_v == 6, (n_b, n_v)
print(f'mnBoard 1-6 / mnVideo 1-6: ประโยคสไตล์ → lookup ({n_b}+{n_v} จุด)')

plan = next(o for o in c['ops'] if o['id'] == 'mnPlan')
NOT_REAL = {'op': 'and', 'list': [{'op': 'not', 'a': {'op': 'eq', 'a': '{values.svStyle}', 'b': ''}},
                                  {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svStyle}', 'b': 'real'}}]}
plan['systemInstruction']['parts'].append({'op': 'block', 'sep': '', 'parts': [{'when': NOT_REAL, 'value': {'op': 'concat', 'parts': [
    '\n\n★ สไตล์ภาพของคลิปนี้: ', {'op': 'lookup', 'table': 'stylePlan', 'key': '{values.svStyle}', 'fallback': ''},
    ' — ทับคำว่า "ภาพสมจริง/ถ่ายในบ้านจริง" ด้านบน · ตัวละครและฉากเป็นสไตล์นี้ทั้งคลิป '
    '(สินค้ายังต้องหน้าตาตรงรูปจริง) · s*en ห้ามเขียน photo/realistic/real footage · ห้ามใส่ชื่อสไตล์ใน ov/vo']}}]})

# UI: กล่องใหม่ "สไตล์ภาพ" ต่อจากกล่องแสง (ทรงเดียวกัน)
grp = c['phases'][0]['form'][0]['card'][0]['card'][2]
tone_box = grp['card'][0]
assert any(isinstance(x, dict) and x.get('field') == 'svTone' for x in tone_box['card'])
row = json.loads(J(tone_box['card'][0]))
assert row['card'][1]['value'] == 'แสงและบรรยากาศ'
row['card'][0]['icon'] = 'palette'
row['card'][1]['value'] = 'สไตล์ภาพ'
hint = dict(tone_box['card'][1], value='มีผลทั้งบอร์ดและวิดีโอ · สินค้าที่แนบรูปยังหน้าตาตรงรูปจริงทุกสไตล์')
grid = dict(tone_box['card'][2], field='svStyle', options=[
    {'value': '', 'label': 'อัตโนมัติ', 'desc': 'ปกติ = สมจริง', 'icon': 'auto_awesome'},
    {'value': 'real', 'label': 'สมจริง', 'desc': 'เหมือนถ่ายจริง', 'icon': 'photo_camera'},
    {'value': 'pixar', 'label': 'การ์ตูน 3D', 'desc': 'แบบแอนิเมชันฉายโรง', 'icon': 'view_in_ar'},
    {'value': 'anime', 'label': 'อนิเมะ 2D', 'desc': 'เส้นสะอาด สีสด', 'icon': 'brush'},
    {'value': 'clay', 'label': 'ดินน้ำมัน', 'desc': 'สต็อปโมชัน', 'icon': 'gesture'},
    {'value': 'thai', 'label': 'ไทยท้องถิ่น', 'desc': 'บ้านแบบไทย', 'icon': 'temple_buddhist'},
    {'value': 'clean', 'label': 'มินิมอล', 'desc': 'ของน้อย สีน้อย', 'icon': 'crop_square'},
    {'value': 'cyber', 'label': 'ไซเบอร์พังก์', 'desc': 'นีออนม่วง-ฟ้า', 'icon': 'bolt'},
    {'value': 'ink', 'label': 'ลายเส้นหมึก', 'desc': 'นิยายภาพ ตัดเส้นหนา', 'icon': 'draw'}])
grp['card'].insert(1, {'el': 'box', 'className': 'flex flex-col gap-2 mt-2', 'card': [row, hint, grid]})
print('UI: + สไตล์ภาพ 9 แบบ (หน้าตั้งค่า ต่อจากแสง)')

# ══ 2) ผู้แสดง "สัตว์เลี้ยง + เจ้าของ" ══
PO = 'petOwner'
L['castPlan'][PO] = ('★ ตัวเอกของคลิปนี้คือ **สัตว์เลี้ยง 1 ตัว** ตัวเดิมทุกฉากทุกช่วง (ชนิด/สายพันธุ์ตามชื่องานหรือรูปที่แนบ) — '
                     'ขนฟู ตากลมโต ทำหน้าทำตาตอบสนองชัด มองกล้องได้ (ข้อยกเว้นของกฎ "ไม่ใช่พรีเซนเตอร์") · '
                     'คนลงมือคือ **เจ้าของ 1 คน** ใช้สินค้ากับน้อง (อาบน้ำ เช็ดตัว ป้อน ทา) เห็นมือ/ลำตัว ไม่ต้องเห็นหน้าชัด · '
                     'เล่า: น้องมีปัญหา/อยากได้ → เจ้าของใช้สินค้า → น้องสบาย มีความสุข · ฉากปิด = น้องคู่กับสินค้า '
                     '· เขียน s*th/s*en ให้น้องเป็นจุดสนใจของทุกฉาก')
L['castBoard'][PO] = 'ตัวเอกคือสัตว์เลี้ยงตัวเดียว ตัวเดิมทุกช่อง ตาโต มองกล้องได้ · เจ้าของ 1 คนเห็นมือ/ลำตัว ไม่เน้นหน้า'
L['castVideoEN'][PO] = ('ONE pet, the same one in every scene — the star: fluffy, big round eyes, clear cute reactions, may look at the camera; '
                        'its owner (hands/torso, face not the focus) uses the product on it.')
L['castOverrideTH'][PO] = '★ ทับกฎคนด้านบน: ตัวเอกเป็นสัตว์เลี้ยง · คนในคลิปมีแค่เจ้าของ 1 คนที่ลงมือกับน้อง'
L['castNegEN'][PO] = ' no animal head on a human body, no mascot suit, no second pet'
for t in ('castPlan', 'castBoard', 'castVideoEN', 'castOverrideTH', 'castNegEN'):
    assert PO in L[t], t
assert len(L['castBoard'][PO]) <= max(len(L['castBoard'][k]) for k in ('animalReal', 'animalAnthro')) + 5, len(L['castBoard'][PO])
ck = next(n for n in walk(c['phases']) if isinstance(n, dict) and n.get('field') == 'castKind' and n.get('el') == 'grid-select')
ck['options'].append({'value': PO, 'label': 'สัตว์เลี้ยง + เจ้าของ', 'desc': 'น้องเป็นตัวเอก เจ้าของลงมือ', 'icon': 'volunteer_activism'})
print('castKind: + สัตว์เลี้ยง + เจ้าของ (5 ตาราง + ตัวเลือกบนจอ)')

# ══ 3) ใครพูด ══
c['values']['svVoiceBy'] = ''
L['speakerPlan'] = {'star': (
    'ผู้พูด: **ตัวเอกในคลิปพูดเอง** เป็นบุรุษที่ 1 (★ ทับกฎสรรพนาม "เรา" ด้านบน) — ถ้าตัวเอกเป็นสัตว์ ให้น้องเล่าเอง '
    'แทนตัวว่า "หนู" เรียกเจ้าของว่า "แม่" น้ำเสียงน่ารัก ขี้อ้อน (เช่น "วันนี้ต้องอาบน้ำอีกแล้วหรอคะแม่") · '
    'ถ้าตัวเอกเป็นคน ให้คนในคลิปเล่างานของตัวเอง · เล่าความรู้สึกก่อน→หลังใช้ ฉากท้ายชวนซื้อสั้น ๆ ได้ถ้ามีสินค้า '
    '· คำลงท้ายตามเพศเสียงที่เลือก ใส่ได้บ่อยกว่ากฎ 2 ครั้ง เพราะเป็นคำพูดของตัวละคร')}
vb = next(n for n in walk(plan['systemInstruction']) if isinstance(n, dict) and n.get('op') == 'concat'
          and isinstance(n.get('parts'), list) and n['parts'] and n['parts'][0] == '\n\nเสียงพากย์ของคลิป: {values.svVoice}\n')
vb['parts'].append({'op': 'block', 'sep': '', 'parts': [
    {'when': 'values.svVoiceBy=star', 'value': {'op': 'concat', 'parts': ['\n', {'op': 'lookup', 'table': 'speakerPlan', 'key': 'star', 'fallback': ''}]}}]})
box = next(n for n in walk(c['phases']) if isinstance(n, dict) and n.get('el') == 'box'
           and any(isinstance(x, dict) and x.get('field') == 'svVoice' for x in n.get('card', [])))
lab = box['card'][0]
assert lab['value'] == 'เพศเสียงพากย์'
box['card'][0:0] = [
    dict(lab, value='ใครพูด'),
    {'el': 'grid-select', 'field': 'svVoiceBy', 'cols': 2, 'contained': True, 'options': [
        {'value': '', 'label': 'คนเล่าเรื่อง', 'desc': 'พากย์เล่าสิ่งที่ทำ', 'icon': 'record_voice_over'},
        {'value': 'star', 'label': 'ตัวเอกพูดเอง', 'desc': 'เช่น น้องหมาเล่าเอง "หนู…ค่ะ"', 'icon': 'pets'}],
     'className': '!min-h-[48px] @[420px]:!min-h-0'},
]
box['card'][2] = dict(lab, className=lab['className'] + ' mt-1')
hint = box['card'][-1]
assert 'คิดบทใหม่' in hint['value']
hint['value'] = hint['value'].replace('ถ้าเปลี่ยนเพศ ภาษา', 'ถ้าเปลี่ยนคนพูด เพศ ภาษา')
print('UI: + ใครพูด (คนเล่าเรื่อง / ตัวเอกพูดเอง) · mnPlan: + กฎบทพูดของตัวเอก')

# ══ ยาม ══
for t, old in (('styleBoard', B_OLD), ('styleVideoEN', V_OLD)):
    for k, v in L[t].items():
        assert len(v) <= len(old), f'{t}[{k}] ยาว {len(v)} > ของเดิม {len(old)} — เพดาน 3,900 ไม่มีที่ให้'
    assert L[t][''] == old and L[t]['real'] == old
opts = {o['value'] for o in grid['options']}
assert opts == set(L['styleBoard']) == set(L['styleVideoEN']), opts ^ set(L['styleBoard'])
assert opts - {'', 'real'} == set(L['stylePlan'])
for k, v in L['styleVideoEN'].items():
    assert all(ord(ch) < 128 for ch in v), f'styleVideoEN[{k}] ต้องเป็นอังกฤษล้วน (บทเรียน v21)'
for o in c['ops']:
    if o['id'].startswith(('mnBoard', 'mnVideo')):
        s = J(o['prompt'])
        assert s.count('"styleBoard"') + s.count('"styleVideoEN"') == 1, o['id']
print('✅ ยามผ่าน: สไตล์ทุกตัวสั้นกว่าหรือเท่าของเดิม · ตัวเลือก = คีย์ lookup ครบ · op ละ 1 จุด · วิดีโออังกฤษล้วน')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
