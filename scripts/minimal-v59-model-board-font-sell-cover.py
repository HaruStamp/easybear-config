#!/usr/bin/env python3
# minimal-v59-model-board-font-sell-cover.py — เจ้าของสั่ง 26 พ.ย. 2569 (5 ข้อ · แก้ minimal-dev.json อย่างเดียว · รันซ้ำได้)
#  A. เลือกโมเดลรูปได้ 3 ตัว (values.imageModel + dropdown ข้างโมเดลวิดีโอ) · ทุก op ภาพ (mnBoard* + mnCover) ใช้
#     model = cond(มีข้อความบนภาพ → Nano Banana Pro · ไม่มี → imageModel · ว่าง/เซฟเก่า → Pro) — ลอกแบบ hardsell
#     ค่าเริ่ม = Pro (= ค่าที่ล็อกอยู่เดิม) ⇒ ลูกค้าเดิมได้ผลเหมือนเดิม · เซฟ/โหลดค่าด้วย (เติมเข้า saveGroups.setup)
#  B. วิดีโออิงบอร์ดมากขึ้น: บอร์ดย้ายจาก ref ใบสุดท้าย → ใบแรก (refs.slot หลัก) แบบ showhow · ข้อความ prompt
#     "The LAST reference image…" → "Reference image 1 is this clip's storyboard sheet… follow its 5 panels scene by scene
#     (pose, framing, camera angle, product placement)" · ประโยครูปสถานที่ "(just before the storyboard)" → "(the last image)"
#     ไม่ใช้ startFrame (ทิ้ง refs ทั้งชุด) · จำนวน ref เท่าเดิม (≤7)
#  C. ล็อกสไตล์ตัวอักษรเหมือนกันทั้งคลิป: บอร์ด + วิดีโอสั่ง "ฟอนต์ ขนาด สี ขอบ ตำแหน่งเดียวกันทุกฉาก"
#     + โหมดไทยแบบ "จัดฉากคุมโทน" เดิมส่ง {values.svText} (ไทย) เข้า prompt อังกฤษ → ใช้ lookup svTextEN
#     + svTextEN ตัดคำ "English" ออก (โหมดไทยเคยได้ "handwritten English script" ทั้งที่ต้องเขียนไทย · ภาษาบอกอยู่แล้วที่ "max 5 Thai/English words")
#  D. สไตล์การขาย svSell (grid-select ใต้ "การนำเสนอสินค้า") → บรรทัดสั้นใน sys ของ mnPlan · ค่าเริ่ม อัตโนมัติ = ไม่ส่งอะไร (พฤติกรรมเดิม)
#  E. ปก + แคปชัน: mnPlan ออก caption/hashtags (ภาษาตาม svLang) → mnQueue ยกเข้า tasks · op ปก mnCover (aux ไม่อยู่ใน gens/stages)
#     · slot cover · การ์ดหน้าผลิต (มุมมองการ์ด): กล่องแคปชัน + ปุ่มคัดลอก · กล่องปก + สร้าง/สร้างใหม่/โหลดปก
#  พื้นที่ prompt (เพดาน 3,900 ตึง): ไม่บีบรายละเอียดบท — ได้ที่ว่างจากคำสั่งที่ซ้ำ: Negative รวม "no" ซ้ำ ·
#     PRODUCT LOCK ย่อ "restyle" + "Styling applies to the set and light…" เหลือ "Style applies to the set, never to the product itself." (ยาม cliplen ล็อกท่อนนี้)
import json, sys, copy

P = sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json'
raw = open(P, encoding='utf-8').read()
c = json.loads(raw)
ops = {o['id']: o for o in c['ops']}
L = c['lookups']
PRO = '🍌 Nano Banana Pro'
IMG_MODELS = ['🍌 Nano Banana Pro', '🍌 Nano Banana 2.1', '🍌 Nano Banana 2 Lite']
TEXT_ON = {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svTextOn}', 'b': 'ไม่มีข้อความ'}}
MODEL = {'op': 'cond', 'when': TEXT_ON, 'then': PRO,
         'else': {'op': 'cond', 'when': {'op': 'eq', 'a': '{values.imageModel}', 'b': ''}, 'then': PRO, 'else': '{values.imageModel}'}}
VIDS = ['mnVideo', 'mnVideo2', 'mnVideo3']
BOARDS = ['mnBoard', 'mnBoard2', 'mnBoard3']


def walk_str(x, fn):
    if isinstance(x, str): return fn(x)
    if isinstance(x, list): return [walk_str(i, fn) for i in x]
    if isinstance(x, dict): return {k: walk_str(v, fn) for k, v in x.items()}
    return x


def replace_all(x, repl, hits):
    def fn(s):
        for a, b in repl:
            if a in s:
                hits[a] = hits.get(a, 0) + s.count(a); s = s.replace(a, b)
        return s
    return walk_str(x, fn)


def find(node, pred, out=None):
    out = [] if out is None else out
    if isinstance(node, dict):
        if pred(node): out.append(node)
        for v in node.values(): find(v, pred, out)
    elif isinstance(node, list):
        for v in node: find(v, pred, out)
    return out


# ───────── A. โมเดลรูป ─────────
c['values']['imageModel'] = c['values'].get('imageModel') or PRO
setup = next(g for g in c['saveGroups'] if g['id'] == 'setup')
if 'imageModel' not in setup['values']: setup['values'].append('imageModel')
for b in BOARDS:
    assert ops[b]['model'] in (PRO, MODEL), (b, ops[b]['model'])
    ops[b]['model'] = copy.deepcopy(MODEL)

prodbox = c['phases'][0]['form'][0]['card'][0]['card'][3]['card'][1]
assert any(x.get('field') == 'svModel' for x in prodbox['card']), 'กล่องโมเดลวิดีโอย้ายที่แล้ว — ปรับสคริปต์ก่อน'
if not any(x.get('field') == 'imageModel' for x in prodbox['card']):
    vrow = prodbox['card'][0]
    assert vrow['el'] == 'row' and vrow['card'][1]['value'] == 'โมเดลวิดีโอ', vrow
    irow = copy.deepcopy(vrow); irow['card'][0]['icon'] = 'image'; irow['card'][1]['value'] = 'โมเดลภาพ (สตอรีบอร์ด · ปก)'
    dd = {'el': 'dropdown', 'field': 'imageModel', 'label': '',
          'options': [{'value': m, 'label': m, 'icon': ic} for m, ic in zip(IMG_MODELS, ['auto_awesome', 'image', 'bolt'])],
          'className': '!min-h-[48px] @[420px]:!min-h-0'}
    hint = {'el': 'text', 'value': 'มีข้อความบนภาพ ระบบใช้ Nano Banana Pro ให้อัตโนมัติ', 'icon': 'info',
            'className': '!text-[12.5px] leading-snug opacity-60 px-0.5 mb-1', 'when': 'values.svTextOn!=ไม่มีข้อความ'}
    prodbox['card'][0:0] = [irow, dd, hint]

# ───────── B + C. prompt วิดีโอ ─────────
OLD_SHEET = "\n\nThe LAST reference image is this clip storyboard sheet; the others are real product photos. Silent look guide only — it must NEVER appear on screen. Every frame is live-action photography."
NEW_SHEET = "\n\nReference image 1 is this clip's storyboard sheet, a silent guide: follow each scene's panel (pose, framing, angle, product). The sheet must NEVER appear on screen. Every frame is live-action photography."
FONT_EN = '; same font, size, colour, outline, position in all scenes'
VREPL = [
    (OLD_SHEET, NEW_SHEET),
    ('If a location photo is attached (just before the storyboard), use that exact place.', 'If a location photo is attached (the last image), use that exact place.'),
    ('never redraw, restyle or cartoonify it. Styling applies to the set and light, never to the product itself.', 'never redraw or cartoonify it. Style applies to the set, never to the product itself.'),
    ('no storyboard sheet, no line art, no sketch, no paper page, no framed panel, no band across top or bottom, no grid, no split screen, no distorted or non-Thai text, no warped or morphing product, no extra fingers.',
     'no storyboard sheet, line art, sketch, paper page, framed panel, top/bottom band, grid, split screen, distorted or non-Thai text, warped or morphing product or extra fingers.'),
    ('no storyboard sheet, no line art, no sketch, no paper page, no framed panel, no band across top or bottom, no grid, no split screen, no distorted or misspelled text, no warped or morphing product, no extra fingers.',
     'no storyboard sheet, line art, sketch, paper page, framed panel, top/bottom band, grid, split screen, distorted or misspelled text, warped or morphing product or extra fingers.'),
    ('; one line, max 5 Thai words, never covering the product', FONT_EN + '; one line, max 5 Thai words, never covering the product'),
    ('; one line, max 5 English words, never covering the product', FONT_EN + '; one line, max 5 English words, never covering the product'),
]
already = all(NEW_SHEET.strip() in json.dumps(ops[v]['prompt'], ensure_ascii=False) for v in VIDS)
if not already:
    for v in VIDS:
        hits = {}
        ops[v]['prompt'] = replace_all(ops[v]['prompt'], VREPL, hits)
        miss = [a[:50] for a, _ in VREPL if not hits.get(a)]
        assert not miss, (v, miss)
        # โหมดไทย + จัดฉากคุมโทน: {values.svText} ดิบ (ไทย) → lookup อังกฤษ
        for node in find(ops[v]['prompt'], lambda n: isinstance(n.get('value'), str) and n['value'].startswith('\n\nON-SCREEN TEXT STYLE: {values.svText}')):
            tail = node['value'][len('\n\nON-SCREEN TEXT STYLE: {values.svText}'):]
            node['value'] = {'op': 'concat', 'parts': ['\n\nON-SCREEN TEXT STYLE: ', {'op': 'lookup', 'table': 'svTextEN', 'key': '{values.svText}', 'fallback': ''}, tail]}
        # B: บอร์ดขึ้นเป็นรูปแรก
        r = ops[v]['refs']; also = r['also']
        last = also[-1]
        assert last['from'] == 'tasks' and last['slot'].startswith('board') and 'when' not in last, (v, last)
        main = {k: r[k] for k in ('from', 'by', 'slot')}
        ops[v]['refs'] = {'op': 'lookupRefs', 'from': last['from'], 'by': last['by'], 'slot': last['slot'], 'also': [main] + also[:-1]}
for v in VIDS:
    s = json.dumps(ops[v]['prompt'], ensure_ascii=False)
    assert 'LAST reference image' not in s and 'just before the storyboard' not in s and 'STYLE: {values.svText}' not in s, v
    assert ops[v]['refs']['slot'].startswith('board') and 'startFrame' not in ops[v], v

# C: svTextEN ไม่ระบุภาษา (ภาษาอยู่ที่ "max 5 Thai/English words" แล้ว) + fallback เดียวกันทุกจุด
NEUTRAL = {'cute rounded handwritten English script, white with a soft shadow + small hand-drawn doodles': 'cute rounded handwritten script, white with a soft shadow + small hand-drawn doodles',
           'clean thin sans-serif English lettering': 'clean thin sans-serif lettering',
           'bold modern English typography': 'bold modern typography'}
for k, val in list(L['svTextEN'].items()):
    L['svTextEN'][k] = NEUTRAL.get(val, val)
DEF_EN = 'cute rounded handwritten script, white with a soft shadow + small hand-drawn doodles'
for o in c['ops']:
    for n in find(o.get('prompt'), lambda n: n.get('op') == 'lookup' and n.get('table') == 'svTextEN'):
        n['fallback'] = DEF_EN

# C: บอร์ด — ประโยค "เรนเดอร์เป็นฟอนต์สไตล์ที่กำหนด" กลายเป็นล็อกทั้งชุด
BREPL = [('ตัวหนังสือ overlay ภาษาไทยต้องเรนเดอร์เป็นฟอนต์สไตล์ที่กำหนดจริงๆ ให้เห็นชัดเจน',
          'ตัวหนังสือ overlay ภาษาไทยใช้ฟอนต์สไตล์ที่กำหนดจริง ขนาด สี ขอบ ตำแหน่งเดียวกันทุกช่อง'),
         ('doodle ต้องเป็นลายเส้นวาดมือเท่านั้น ห้ามใช้ emoji', 'doodle ห้ามเป็น emoji'),
         ('ตัวหนังสือ overlay ภาษาอังกฤษต้องเรนเดอร์เป็นฟอนต์สไตล์ที่กำหนดจริงๆ ให้เห็นชัดเจน',
          'ตัวหนังสือ overlay ภาษาอังกฤษใช้ฟอนต์สไตล์ที่กำหนดจริง ขนาด สี ขอบ ตำแหน่งเดียวกันทุกช่อง')]
for b in BOARDS:
    hits = {}
    ops[b]['prompt'] = replace_all(ops[b]['prompt'], BREPL, hits)
    s = json.dumps(ops[b]['prompt'], ensure_ascii=False)
    assert 'ตำแหน่งเดียวกันทุกช่อง' in s and 'เรนเดอร์เป็นฟอนต์' not in s and 'doodle ห้ามเป็น emoji' in s, b

# ───────── D. สไตล์การขาย ─────────
SELL = [('อัตโนมัติ', 'อัตโนมัติ', 'หมีเลือกให้เข้ากับสินค้า', 'auto_awesome'),
        ('สินค้าแก้ปัญหา', 'สินค้าแก้ปัญหา', 'เปิดด้วยปัญหา แล้วโชว์ทางแก้', 'lightbulb'),
        ('เพื่อนแนะนำเพื่อน', 'เพื่อนแนะนำเพื่อน', 'บอกต่อของดีแบบคนสนิท', 'group'),
        ('รีวิวจริงใจ', 'รีวิวจริงใจ', 'เล่าข้อดีตรง ๆ ไม่โอเวอร์', 'thumb_up'),
        ('เปรียบเทียบก่อน-หลัง', 'ก่อน-หลังใช้', 'ชีวิตก่อนมี vs หลังมีสินค้า', 'compare'),
        ('ขายดุ เร่งปิด', 'ขายดุ เร่งปิด', 'จังหวะเร็ว ชวนซื้อชัด', 'bolt'),
        ('เล่าเรื่องสั้น', 'เล่าเรื่องสั้น', 'มีเรื่องราว ต้น-กลาง-จบ', 'auto_stories')]
L['sellPlan'] = {
    'สินค้าแก้ปัญหา': 'สไตล์การขาย: สินค้าแก้ปัญหา — เปิดด้วยปัญหาที่คนกลุ่มนี้เจอจริง แล้วฉากต่อไปโชว์ว่าสินค้าแก้ยังไง ปิดด้วยผลที่ได้ + ชวนซื้อ',
    'เพื่อนแนะนำเพื่อน': 'สไตล์การขาย: เพื่อนแนะนำเพื่อน — ov/vo เหมือนบอกต่อของดีให้คนสนิท เป็นกันเอง เล่าเหตุผลที่อยากให้ลอง (ห้ามขึ้นต้นด้วยคำเรียกเพื่อน)',
    'รีวิวจริงใจ': 'สไตล์การขาย: รีวิวจริงใจ — เล่าเหมือนคนที่ใช้มาแล้ว บอกข้อดีตรง ๆ ไม่โอเวอร์ ไม่อ้างเกินจริง',
    'เปรียบเทียบก่อน-หลัง': 'สไตล์การขาย: เปรียบเทียบก่อน-หลัง — ช่วงแรกเล่าสภาพก่อนมีสินค้า ช่วงหลังโชว์ความต่างหลังใช้ (ห้ามแต่งตัวเลขผลลัพธ์ที่ผู้ใช้ไม่ได้ให้)',
    'ขายดุ เร่งปิด': 'สไตล์การขาย: ขายดุ เร่งปิด — ประโยคสั้น กระชับ บอกเหตุผลให้ซื้อตอนนี้ ชวนซื้อชัด (ห้ามแต่งโปร ราคา ของใกล้หมด หรือเวลาจำกัดเอง ใช้ได้เฉพาะที่ผู้ใช้ให้)',
    'เล่าเรื่องสั้น': 'สไตล์การขาย: เล่าเรื่องสั้น — ทั้งคลิปเป็นเรื่องเล็ก ๆ มีต้น กลาง จบ สินค้าเป็นตัวช่วยของเรื่อง จบด้วยชวนซื้อ',
}
SELL_TAIL = ' · ใช้กับลำดับเรื่องและถ้อยคำใน synopsis/ov/vo เท่านั้น — โครงฉาก ฉาก มุมกล้อง และน้ำเสียงยังตามค่าที่ตั้งไว้'
c['values'].setdefault('svSell', 'อัตโนมัติ')
sysP = ops['mnPlan']['systemInstruction']['parts']
if not any('sellPlan' in json.dumps(x, ensure_ascii=False) for x in sysP):
    i = next(i for i, x in enumerate(sysP) if isinstance(x, dict) and x.get('table') == 'lenActTail')
    sysP.insert(i + 1, {'op': 'block', 'sep': '', 'parts': [{
        'when': {'op': 'not', 'a': {'op': 'or', 'list': [{'op': 'eq', 'a': '{values.svSell}', 'b': 'อัตโนมัติ'}, {'op': 'eq', 'a': '{values.svSell}', 'b': ''}]}},
        'value': {'op': 'concat', 'parts': [{'op': 'lookup', 'table': 'sellPlan', 'key': '{values.svSell}', 'fallback': ''}, SELL_TAIL, '\n']}}]})
style = c['phases'][0]['form'][0]['card'][0]['card'][2]
if not any(x.get('field') == 'svSell' for x in find(style, lambda n: 'field' in n)):
    pres = next(i for i, x in enumerate(style['card']) if 'svPres1' in json.dumps(x, ensure_ascii=False))
    tpl = style['card'][pres]
    head = copy.deepcopy(tpl['card'][0]); head['card'][0]['icon'] = 'campaign'; head['card'][1]['value'] = 'สไตล์การขาย'
    desc = copy.deepcopy(tpl['card'][1]); desc['value'] = 'วิธีเล่าเพื่อขายของ — มีผลกับบทพูดและข้อความ ส่วนฉากยังตาม "ฉากในคลิป"'
    gs = {'el': 'grid-select', 'field': 'svSell', 'cols': 2, 'contained': True,
          'options': [{'value': v, 'label': lb, 'desc': d, 'icon': ic} for v, lb, d, ic in SELL],
          'className': '!min-h-[48px] @[420px]:!min-h-0'}
    style['card'].insert(pres + 1, {'el': 'box', 'className': tpl['className'], 'card': [head, desc, gs]})

# ───────── E. แคปชัน + ปก ─────────
T = c['collections']['tasks']
for f in ('caption', 'hashtags'):
    if f not in T['fields']: T['fields'].append(f)
if 'cover' not in T['slots']: T['slots'].append('cover')
sp = ops['mnQueue']['spawn']['fields']
sp.setdefault('caption', '{item.fields.caption}'); sp.setdefault('hashtags', '{item.fields.hashtags}')
CAP_TH = ('\n\nเพิ่มอีก 2 คีย์ในทุก object: "caption":"แคปชันโพสต์ TikTok/Facebook ภาษาไทย 1-2 ประโยค ไม่เกิน 150 ตัวอักษร '
          'พูดถึงสินค้าและประโยชน์ ไม่มี emoji ไม่แต่งราคา/โปรที่ผู้ใช้ไม่ได้ให้ ห้ามใช้คำสไตล์ภาพตามกฎคำสไตล์ข้างต้น",'
          '"hashtags":"แฮชแท็ก 5-7 อัน คั่นด้วยเว้นวรรค ไทยปนอังกฤษ ไม่มีชื่อร้าน"')
CAP_EN = ('\n\nเพิ่มอีก 2 คีย์ในทุก object: "caption":"แคปชันโพสต์ TikTok/Facebook เป็นภาษาอังกฤษ 1-2 ประโยค ไม่เกิน 150 ตัวอักษร ห้ามมีอักษรไทย '
          'พูดถึงสินค้าและประโยชน์ ไม่มี emoji ไม่แต่งราคา/โปรที่ผู้ใช้ไม่ได้ให้ ห้ามใช้คำสไตล์ภาพตามกฎคำสไตล์ข้างต้น",'
          '"hashtags":"แฮชแท็กภาษาอังกฤษ 5-7 อัน คั่นด้วยเว้นวรรค ไม่มีชื่อร้าน"')
if not any('เพิ่มอีก 2 คีย์ในทุก object' in json.dumps(x, ensure_ascii=False) for x in sysP):
    i = next(i for i, x in enumerate(sysP) if 'lenOut' in json.dumps(x, ensure_ascii=False))
    sysP.insert(i + 1, {'op': 'block', 'sep': '', 'parts': [
        {'when': {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svLang}', 'b': 'English'}}, 'value': CAP_TH},
        {'when': {'op': 'eq', 'a': '{values.svLang}', 'b': 'English'}, 'value': CAP_EN}]})

COVER = {
    'id': 'mnCover', 'type': 'image', 'over': 'tasks', 'out': 'cover', 'model': copy.deepcopy(MODEL), 'aspectRatio': '9:16',
    'where': 'slots.board!=',
    'refs': {'op': 'lookupRefs', 'from': 'tasks', 'by': '{item.id}', 'slot': 'board', 'also': [
        {'from': 'products', 'by': '{item.refs.prod}', 'slot': 'image'},
        {'from': 'products', 'by': '{item.refs.prod}', 'slot': 'image2'},
        {'from': 'products', 'by': '{item.refs.prod}', 'slot': 'image3'},
        {'from': 'characters', 'by': '{values.charId}', 'slot': 'face', 'when': {'op': 'and',
            'a': {'op': 'eq', 'a': '{values.svChar}', 'b': 'มีพรีเซนเตอร์ไทย 1 คนในคลิป'},
            'b': {'op': 'eq', 'a': '{values.svCharSrc}', 'b': 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'}}}]},
    'prompt': {'op': 'concat', 'parts': [
        'Design one scroll-stopping vertical 9:16 COVER photo (thumbnail) for this product clip: clean Scandinavian minimal look, soft natural light, uncluttered. '
        'Reference image 1 is this clip\'s storyboard sheet: borrow only its set, light, palette and presenter (if any) — never copy the sheet, its panels, rows, number marks or notes. '
        'The other images are real photos of the product (plus the presenter\'s face if attached).\n'
        'PRODUCT LOCK: the product is the hero, large and sharp, exactly as photographed — same colour, shape, proportions, material, label, logo and lettering; never redraw or restyle it.\n',
        {'op': 'block', 'sep': '', 'parts': [
            {'when': TEXT_ON, 'value': {'op': 'concat', 'parts': [
                'HEADLINE text, spelled exactly: "{item.productName}" — one short line in the top area, ',
                {'op': 'lookup', 'table': 'svTextEN', 'key': '{values.svText}', 'fallback': DEF_EN},
                ', the same lettering style as the clip overlays, never covering the product. Optional one tiny label taken only from this caption: "{item.caption}".\n']}},
            {'when': 'values.svTextOn=ไม่มีข้อความ', 'value': 'NO TEXT on the cover: no headline, captions or labels; only text printed on the product may be readable.\n'}]},
        'RULES: one single full-bleed photo, no grid, no split screen, no collage; text spelled exactly, never mirrored; never invent prices, discounts, free shipping or stock claims; no shopping UI, no emoji, no watermark.']},
    'logRun': '[{item.productName} คลิป {item.clipIndex}] กำลังสร้างปก',
    'logDone': '[{item.productName} คลิป {item.clipIndex}] ปกเสร็จแล้ว',
    'timeoutMs': 180000,
}
if 'mnCover' in ops: c['ops'][[o['id'] for o in c['ops']].index('mnCover')] = COVER
else: c['ops'].append(COVER)
L['opNames']['mnCover'] = 'กำลังสร้างปก'; L['opIcons']['mnCover'] = 'image'

# การ์ดหน้าผลิต (มุมมองการ์ด) — คอลัมน์ข้อมูล ต่อจากกล่องเรื่องย่อ
card = c['phases'][0]['form'][3]['card'][0]['card'][6]['card'][0]['card'][0]
info = card['card'][1]
syn_i = next(i for i, x in enumerate(info['card']) if 'item.synopsis' in json.dumps(x, ensure_ascii=False))
BTN = 'w-full justify-center !h-12 !rounded-xl !text-[15px] @[640px]:!text-[14px] font-bold'
BTN_SOLID = BTN + ' !bg-gradient-to-b !from-[#3f8ef0] !to-[#2571dd] !text-white'
BTN_GHOST = BTN + ' border border-[var(--ev-border)] !bg-[var(--ev-surface)]'
HEAD = lambda icon, txt: {'el': 'row', 'className': 'items-center !gap-1.5 px-0.5', 'style': {'flexWrap': 'nowrap'}, 'card': [
    {'el': 'icon', 'icon': icon, 'textSize': 'text-[16px]', 'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center opacity-80 shrink-0'},
    {'el': 'text', 'value': txt, 'className': '!text-[13px] @[640px]:!text-[12.5px] !text-[var(--ev-text)] opacity-65 uppercase tracking-[0.14em] font-black'}]}
BOXCLS = 'flex flex-col gap-2 rounded-2xl border border-[var(--ev-border)] bg-[var(--ev-bg)]/60 p-3'
cap_box = {'el': 'box', '__v59': 'caption', 'className': BOXCLS, 'when': 'item.caption!=', 'card': [
    HEAD('chat', 'แคปชันพร้อมโพสต์'),
    {'el': 'text', 'value': '{item.caption}', 'className': '!text-[15px] @[640px]:!text-[14px] leading-relaxed whitespace-pre-line'},
    {'el': 'text', 'value': '{item.hashtags}', 'className': '!text-[14px] @[640px]:!text-[13px] leading-relaxed font-bold !text-[var(--ev-accent)] break-words', 'when': 'item.hashtags!='},
    {'el': 'copy-button', 'value': '{item.caption}\n\n{item.hashtags}', 'label': 'คัดลอกแคปชัน + แฮชแท็ก', 'icon': 'content_copy', 'variant': 'ghost', 'className': BTN_GHOST}]}
NOT_RUN = {'op': 'not', 'a': {'op': 'eq', 'a': '{item.status}', 'b': 'running'}}
HAS_COVER = {'op': 'not', 'a': {'op': 'eq', 'a': '{item.slots.cover}', 'b': ''}}
cov_box = {'el': 'box', '__v59': 'cover', 'className': BOXCLS, 'when': {'op': 'not', 'a': {'op': 'eq', 'a': '{item.slots.board}', 'b': ''}}, 'card': [
    HEAD('photo', 'ปกคลิป'),
    {'el': 'box', 'className': 'w-[140px]', 'when': HAS_COVER, 'card': [
        {'el': 'media-slot', 'src': '{item.slots.cover}', 'aspect': '9:16', 'style': {'borderRadius': '14px'}, 'className': 'ring-1 ring-[var(--ev-border)]'}]},
    {'el': 'text', 'value': 'ภาพปก 9:16 จากสตอรีบอร์ดและรูปสินค้าของคลิปนี้ — สร้างเมื่อไหร่ก็ได้', 'className': '!text-[13px] @[640px]:!text-[12px] opacity-55 leading-snug', 'when': {'op': 'eq', 'a': '{item.slots.cover}', 'b': ''}},
    {'el': 'gen-button', 'op': 'mnCover', 'label': 'สร้างปก', 'icon': 'auto_awesome', 'variant': 'solid', 'className': BTN_SOLID,
     'when': {'op': 'and', 'list': [{'op': 'eq', 'a': '{item.slots.cover}', 'b': ''}, NOT_RUN]}},
    {'el': 'box', 'className': 'grid grid-cols-1 @[420px]:grid-cols-2 gap-2', 'when': HAS_COVER, 'card': [
        {'el': 'download-button', 'to': '{item.slots.cover}', 'label': 'โหลดปก', 'icon': 'download', 'variant': 'solid', 'className': BTN_SOLID},
        {'el': 'retry-button', 'op': 'mnCover', 'label': 'สร้างปกใหม่', 'icon': 'refresh', 'variant': 'ghost', 'className': BTN_GHOST, 'when': NOT_RUN}]}]}
for b in (cap_box, cov_box): b.pop('__v59')
if not any('{item.slots.cover}' in json.dumps(x, ensure_ascii=False) for x in info['card']):
    info['card'][syn_i + 1:syn_i + 1] = [cap_box, cov_box]

# ───────── ตรวจปิดท้าย ─────────
assert 'mnCover' not in c['auto']['productLoop']['gens'] and all(s.get('op') != 'mnCover' for s in c['stages'])
assert all(ops[b]['model'] == MODEL for b in BOARDS) and c['values']['imageModel'] == PRO
out = json.dumps(c, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else '')
open(P, 'w', encoding='utf-8').write(out)
print('ok', P)
