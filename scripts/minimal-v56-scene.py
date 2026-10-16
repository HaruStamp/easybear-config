#!/usr/bin/env python3
"""minimal v56 — ฉากในคลิป [จัดฉากคุมโทน (เดิม) / ฉากชีวิตจริง / กำหนดฉากเอง] (พี่หมีสั่ง 2026-10-16)

ที่มา: ลูกค้าเจนคลิปไฟโซล่าเซลล์เองใน Flow (prompt UGC 8 ช็อต) แล้วบอกว่าดีกว่าคลิปจาก minimal
  → รอบแรกทำเป็น "แนวคลิป: รีวิวแบบเพื่อนเล่า" · ทดสอบจริง 2 คลิป (ไฟโซล่า / กระทะ) ผ่าน
  → พี่หมีเคาะชื่อ "ฉากในคลิป: จัดฉากคุมโทน / ฉากชีวิตจริง" (ทุกแบบยังเป็นมินิมอล ต่างที่การจัดฉาก+วิธีเล่า) + เพิ่ม "กำหนดฉากเอง" แบบ showhow
ตัวเลือก (values.svVibe — ค่าเก็บเดิม '' / 'รีวิวแบบเพื่อนเล่า' ไม่เปลี่ยน · เปลี่ยนแค่ป้าย):
  'อัตโนมัติ'        ค่าเริ่มต้น (พี่หมีเคาะ) — บทเลือก คุมโทน/ชีวิตจริง ตามสินค้า · วิดีโอหัวกลาง ๆ ตามที่ฉากบอก
  ''               จัดฉากคุมโทน — prompt เดิมทุกไบต์
  'รีวิวแบบเพื่อนเล่า' ฉากชีวิตจริง — ฉาก Pinterest/MUJI/IKEA · ลงมือทุกฉาก · โชว์ผลจริง + โทนเพื่อนเล่า
  'กำหนดฉากเอง'      ผู้ใช้พิมพ์ฉาก (svScene · เข้าเฉพาะบท ไม่เข้า prompt วิดีโอ — ไทยในวิดีโอถูกวาดเป็นตัวหนังสือ + ความยาวคุมไม่ได้)
                     + รูปสถานที่ 1 รูป (collection scenes/sc1.room1 → refs บอร์ด/วิดีโอ + LOCATION LOCK) + วิธีเล่า svVoTone [แบบโฆษณา / แบบเพื่อนเล่า]
แก้จากผลทดสอบจริง (ใช้กับโหมดใหม่เท่านั้น):
  ① V6 ปุ่มซื้อปลอม+เมาส์โผล่ฉากท้าย ⇒ ห้ามคำว่า ตะกร้า/ปุ่มซื้อ/ราคา ใน s*th/s*en (ใช้ได้แค่ ov/vo)
  ③ V3 "five ninety" ไม่บอกสกุล ⇒ English: ราคาต้องมีคำว่า baht
  ④ V1/V4 สัตว์ขึ้นเคาน์เตอร์ครัว ⇒ สัตว์อยู่บนพื้น/โซฟา/ข้างโต๊ะ ห้ามขึ้นเคาน์เตอร์ครัวหรือเตา
🪤 รูปอ้างอิงวิดีโอ Omni สูงสุด 7 ใบ (ตัดท้าย = บอร์ดหาย) ⇒ กำหนดฉากเอง: รูปฉากเข้าแทน image5 (สินค้า 4 + หน้า + ฉาก + บอร์ด = 7)
🪤 ความยาว: แนวเดิมยาวสุด 3,893/3,900 ⇒ โหมดใหม่ชดเชยด้วยคำบรรยายฟอนต์สั้น + "Overlay" · โทนเพื่อนเล่าย้ายบทพูดเข้ารายฉากแทนบทรวม
🛡 svVibe ว่าง ('' = จัดฉากคุมโทน) = prompt เดิมทุกไบต์ · ⚠️ ไฟล์เซฟเก่า/ค่าเริ่มต้น = อัตโนมัติ (ไม่ใช่แบบเดิม — ตั้งใจ) · ห่อของเดิมด้วย block ในตำแหน่งเดิม
รันซ้ำได้ (เจอ svVibe แล้ว = ข้าม) · ต้องรันหลัง v55
"""
import json, os, re, copy

PATH = os.path.join(os.path.dirname(__file__), '..', 'minimal-dev.json')
cfg = json.load(open(PATH, encoding='utf-8'))
if 'svVibe' in cfg['values']:
    print('⏭ v56 แพตช์ไปแล้ว — ไม่ทำซ้ำ'); raise SystemExit(0)
assert 'svLang' in cfg['values'], 'ต้องรัน v55 ก่อน'

REAL_V, CUST_V, FRIEND_V, AUTO_V = 'รีวิวแบบเพื่อนเล่า', 'กำหนดฉากเอง', 'แบบเพื่อนเล่า', 'อัตโนมัติ'
def eq(f, v): return {'op': 'eq', 'a': '{values.%s}' % f, 'b': v}
def NOT(x): return {'op': 'not', 'a': x}
def AND(*x): return {'op': 'and', 'list': list(x)}
def OR(*x): return {'op': 'or', 'list': list(x)}
S_REAL, S_CUST, S_AUTO = eq('svVibe', REAL_V), eq('svVibe', CUST_V), eq('svVibe', AUTO_V)
NEW = OR(S_REAL, S_CUST, S_AUTO)
FRIEND = OR(S_REAL, AND(S_CUST, eq('svVoTone', FRIEND_V)))
VOICE_ON = AND(NOT(eq('svAudio', 'ไม่มีเสียงพากย์')), NOT(eq('svAudio', 'ASMR')))
H = 'มีพรีเซนเตอร์ไทย 1 คนในคลิป'; NONE = 'ไม่มีคนในคลิป — โฟกัสสินค้าล้วน'
PET_ACTIVE = AND(NOT(eq('svChar', NONE)), OR(*[eq('svCast', c) for c in ('สัตว์จริง', 'สัตว์ทำตัวเหมือนคน', 'สัตว์เลี้ยง + เจ้าของ')]))

def only(cond, v): return {'op': 'block', 'sep': '', 'parts': [{'when': cond, 'value': v}]}
def plus(old, *tails):
    """ของเดิม + ท้ายตามเงื่อนไข (เดิมไม่ขยับเมื่อทุกเงื่อนไขเท็จ)"""
    return {'op': 'concat', 'parts': [old] + [only(c, t) for c, t in tails]}
def pick(old, *alts):
    """ของเดิมเมื่อไม่เข้าเงื่อนไขใด · ไม่งั้นทางที่ตรง (เงื่อนไขต้องไม่ซ้อนกัน)"""
    conds = [c for c, _ in alts]
    return {'op': 'block', 'sep': '', 'parts': [{'when': NOT(OR(*conds)), 'value': old}] + [{'when': c, 'value': v} for c, v in alts]}

ops = {o['id']: o for o in cfg['ops']}

# ── บท (mnPlan sys) — ต่อท้ายบล็อกภาษา v55
PLAN_REAL = ('\n\n★ ฉากในคลิป: ฉากชีวิตจริง — ทับกฎสไตล์ด้านบนเฉพาะเรื่องต่อไปนี้:'
             '\n- ฉากเป็นสถานที่ใช้งานจริงที่เรียบโล่ง อบอุ่น (บ้าน ห้อง ครัว ระเบียง สวน — ไม้ธรรมชาติ ของแต่งโทนครีม ต้นไม้ แบบ Pinterest / MUJI / IKEA) ไม่ใช่สตูดิโอพื้นเรียบ · แสงธรรมชาติ'
             '\n- ทุกฉากมีการลงมือทำกับสินค้าจริง (หยิบ แกะ คลี่ ติดตั้ง กด ทา ใช้) ตามระดับผู้แสดงที่ตั้งไว้ · ต้องมีอย่างน้อย 1 ฉากโชว์ผลการทำงานจริงของสินค้า (เช่น ไฟสว่างตอนค่ำ ก่อน-หลังใช้ ผลลัพธ์หลังใช้)')
PLAN_CUST = ('\n\n★ ฉากในคลิป: ผู้ใช้กำหนดสถานที่เอง — ทับกฎฉาก/สไตล์ภาพด้านบนเฉพาะเรื่องสถานที่: {values.svScene}'
             '\n- ทุกฉากทุกคลิปอยู่ในสถานที่นี้ (ปรับมุมกล้องและระยะได้) · ถ้าผู้ใช้เว้นว่าง ให้เลือกสถานที่เรียบโล่งที่เข้ากับสินค้าเองแล้วใช้ที่เดิมทุกฉาก'
             '\n- s*en ทุกฉากระบุสถานที่นี้เป็นภาษาอังกฤษ (ระบบแนบรูปสถานที่ให้ตอนวาดภาพและทำวิดีโอ ถ้าผู้ใช้ใส่รูปไว้)')
PLAN_AUTO = ('\n\n★ ฉากในคลิป: อัตโนมัติ — เลือกเองว่าคลิปนี้จะเป็นแบบไหน แล้วใช้แบบเดียวทั้งคลิป:'
             '\n- (ก) จัดฉากคุมโทน: สตูดิโอ/พื้นเรียบโทนพาสเทล สินค้าเด่น เสียงพากย์แบบโฆษณา — เหมาะกับสินค้าที่ขายความสวยหรือภาพลักษณ์ (บิวตี้ แฟชั่น เครื่องประดับ ของพรีเมียม)'
             '\n- (ข) ฉากชีวิตจริง: สถานที่ใช้งานจริงที่เรียบโล่ง อบอุ่น (Pinterest / MUJI / IKEA) ลงมือใช้สินค้าทุกฉาก มีฉากโชว์ผลการทำงานจริง เสียงพากย์แบบเพื่อนแนะนำเพื่อน — เหมาะกับสินค้าที่ต้องใช้ ติดตั้ง หรือเห็นผลจากการใช้ (ของใช้ในบ้าน ไฟ เครื่องครัว ทำความสะอาด สัตว์เลี้ยง)'
             '\n- s*en ทุกฉากบอกสถานที่/พื้นหลังให้ชัด (สตูดิโอพื้นเรียบ หรือห้อง/ระเบียง/สวนที่ระบุ) · ห้ามเขียนคำว่า ตะกร้า ปุ่มซื้อ หน้าจอ หรือราคา ลงใน s*th และ s*en')
PLAN_FRIEND = ('\n\n★ วิธีเล่า: แบบเพื่อนเล่า'
               '\n- vo: ภาษาพูดแบบเพื่อนแนะนำเพื่อน เป็นกันเอง เร็วนิด ๆ ไม่ขายแรง เหมือนคนใช้จริงเล่า (เปิดได้แบบ "แก ...อันนี้ดีมาก" · ปิดแบบชวนเพื่อน เช่น "แปะตะกร้าไว้ให้แล้ว") · ถ้าภาษาเป็น English ใช้ภาษาพูดอังกฤษโทนเดียวกัน · กฎคำลงท้ายและเพศเสียงยังใช้ตามเดิม'
               '\n- ov: ขึ้นต้นได้ด้วยอีโมจิ 1 ตัวที่เข้ากับข้อความ (ข้อยกเว้นของกฎห้าม emoji) · ov1 เป็นชื่อสินค้าแบบสั้น'
               '\n- ฉากสุดท้าย: สินค้าเด่นสวย มือชี้ลงด้านล่างเบา ๆ — ห้ามเขียนคำว่า ตะกร้า ปุ่มซื้อ หน้าจอ หรือราคา ลงใน s*th และ s*en (คำพวกนี้ใช้ได้แค่ใน ov/vo) ไม่งั้นโมเดลวาด UI ร้านค้าลงในภาพ')
PLAN_EN_PRICE = '\n- (English) ถ้าพูดหรือเขียนราคา ต้องมีคำว่า baht เช่น "590 baht" ห้ามอ่านเลขลอย ๆ'
PLAN_PET = '\n- ตัวละครสัตว์อยู่บนพื้น โซฟา หรือข้างโต๊ะ ห้ามขึ้นเคาน์เตอร์ครัว โต๊ะทำอาหาร หรือเตา'
sp = ops['mnPlan']['systemInstruction']['parts']
assert isinstance(sp[-1], dict) and 'ภาษาของคลิป: English' in json.dumps(sp[-1], ensure_ascii=False), 'ท้าย sys ไม่ใช่บล็อกภาษา v55'
sp[-1] = plus(sp[-1], (S_AUTO, PLAN_AUTO), (S_REAL, PLAN_REAL), (S_CUST, PLAN_CUST), (FRIEND, PLAN_FRIEND),
              (AND(NEW, eq('svLang', 'English')), PLAN_EN_PRICE), (AND(NEW, PET_ACTIVE), PLAN_PET))

# ── บอร์ด — ต่อท้ายส่วนตัวละคร + รูปฉาก
BOARD_REAL = ' · ฉากชีวิตจริง: บ้าน/สวนแบบมินิมอลอบอุ่น ไม่ใช่สตูดิโอ · ห้ามวาดหน้าจอร้านค้า/ตะกร้า/ราคา'
BOARD_AUTO = ' · ฉาก: ตามบท (จัดฉากคุมโทนหรือฉากชีวิตจริงตามที่บทเลือก) · ห้ามวาดหน้าจอร้านค้า/ตะกร้า/ราคา'
BOARD_CUST = ' · ฉาก: สถานที่ตามบท (ผู้ใช้กำหนด) · ถ้ามีรูปสถานที่แนบ ทุกช่องเป็นที่นั้น'
SCENE_REF = {'from': 'scenes', 'by': 'sc1', 'slot': 'room1', 'when': S_CUST}
for oid in ('mnBoard', 'mnBoard2', 'mnBoard3'):
    o = ops[oid]; p = o['prompt']['parts']
    assert 'charBoard' in json.dumps(p[6]), oid
    p[6] = plus(p[6], (S_AUTO, BOARD_AUTO), (S_REAL, BOARD_REAL), (S_CUST, BOARD_CUST))
    also = o['refs']['also']
    i_face = next(i for i, r in enumerate(also) if r.get('slot') == 'face')
    also.insert(i_face + 1, copy.deepcopy(SCENE_REF))

# ── วิดีโอ
OLD_LEAD = 'A minimal commercial of approximately 10 seconds as one single continuous full-bleed 9:16 shot: Scandinavian pastel look, soft natural light, moving smoothly through the 5 scenes below in order.'
REAL_LEAD = ('A UGC-style product review, ~10 s, full-bleed 9:16, 5 clean-cut shots below: '
             'cozy lived-in minimal home/garden (Pinterest/MUJI/IKEA), natural daylight.')   # live-action มีบรรทัด "Every frame is live-action photography" อยู่แล้ว
CUST_LEAD = ('A minimal product video, ~10 s, vertical full-bleed 9:16, 5 clean-cut shots below, all in the location each scene names. '
             'If a location photo is attached (just before the storyboard), use that exact place.')
AUTO_LEAD = ('A minimal commercial, ~10 s, as one single continuous full-bleed 9:16 shot through the 5 scenes below, each set as its scene describes: '
             'clean pastel studio or cozy lived-in home.')   # ค่าเริ่มต้น ⇒ คงกฎล็อกช็อตเดียว (ยาม minimal-cliplen)
FRIEND_VOICE = ' Tone: casual friend-to-friend, not salesy.'
FRIEND_NEG = ' Also avoid: shopping UI, cart, price.'
SCRIPT_RX = re.compile(r' ?Voice-over script \((?:Thai|English)\): "[^"]*"')
def strip_script(x):
    if isinstance(x, str): return SCRIPT_RX.sub('', x)
    if isinstance(x, list): return [strip_script(v) for v in x]
    if isinstance(x, dict): return {k: (v if k in ('when', 'key', 'table', 'op') else strip_script(v)) for k, v in x.items()}
    return x
def short_text(x):   # ชดเชยความยาว: คำบรรยายฟอนต์ฉบับสั้น ("Thai overlay" ต้องคงไว้ — ยาม camera-en)
    if isinstance(x, str):
        if '{values.svText}' in x:
            bits = x.split('{values.svText}'); parts = []
            for i, b in enumerate(bits):
                if b: parts.append(b)
                if i < len(bits) - 1: parts.append({'op': 'lookup', 'table': 'svTextEN', 'key': '{values.svText}', 'fallback': ''})
            return {'op': 'concat', 'parts': parts}
        return x
    if isinstance(x, list): return [short_text(v) for v in x]
    if isinstance(x, dict): return {k: (v if k in ('when', 'key', 'table', 'op', 'fallback') else short_text(v)) for k, v in x.items()}
    return x
n_nar = 0
for oid in ('mnVideo', 'mnVideo2', 'mnVideo3'):
    o = ops[oid]; p = o['prompt']['parts']
    assert isinstance(p[0], str) and p[0].startswith(OLD_LEAD), oid
    p[0] = pick(p[0], (S_AUTO, p[0].replace(OLD_LEAD, AUTO_LEAD, 1)), (S_REAL, p[0].replace(OLD_LEAD, REAL_LEAD, 1)), (S_CUST, p[0].replace(OLD_LEAD, CUST_LEAD, 1)))
    iv = [i for i, x in enumerate(p) if 'Voice-over script' in json.dumps(x, ensure_ascii=False)]
    ineg = [i for i, x in enumerate(p) if 'Negative:' in json.dumps(x, ensure_ascii=False)]
    its = [i for i, x in enumerate(p) if 'ON-SCREEN TEXT STYLE' in json.dumps(x, ensure_ascii=False)]
    assert len(iv) == 1 and len(ineg) == 1 and len(its) == 1, (oid, iv, ineg, its)   # ช่วง 2/3 มีบล็อก CONTINUATION แทรก ⇒ ดัชนีไม่ตายตัว
    noscript = strip_script(copy.deepcopy(p[iv[0]]))
    assert json.dumps(noscript) != json.dumps(p[iv[0]]), (oid, 'ตัดบทรวมไม่ได้')
    p[iv[0]] = pick(p[iv[0]], (FRIEND, {'op': 'concat', 'parts': [noscript, only(VOICE_ON, FRIEND_VOICE)]}))
    p[ineg[0]] = plus(p[ineg[0]], (OR(FRIEND, S_AUTO), FRIEND_NEG))
    p[its[0]] = pick(p[its[0]], (NEW, short_text(copy.deepcopy(p[its[0]]))))
    for i, part in enumerate(p):
        m = re.search(r'\{item\.ov(\d+)\}', json.dumps(part)) if isinstance(part, dict) and i > ineg[0] else None
        if m:
            k = m.group(1)
            p[i] = pick(part, (NEW, {'op': 'concat', 'parts': [short_text(copy.deepcopy(part)),
                                                              only(AND(FRIEND, VOICE_ON), ' VO: "{item.vo%s}"' % k)]}))
            n_nar += 1
    also = o['refs']['also']
    i5 = next(i for i, r in enumerate(also) if r.get('slot') == 'image5')
    assert 'when' not in also[i5]
    also[i5]['when'] = NOT(S_CUST)        # Omni รับ 7 ใบ: กำหนดฉากเอง = รูปฉากเข้าแทน image5 (บอร์ดท้ายสุดต้องไม่โดนตัด)
    i_face = next(i for i, r in enumerate(also) if r.get('slot') == 'face')
    also.insert(i_face + 1, copy.deepcopy(SCENE_REF))
    assert also[-1]['slot'].startswith('board'), oid
assert n_nar == 15, n_nar

# ── collection รูปฉาก (แบบ characters/ch1)
cfg['collections']['scenes'] = {'fields': [], 'slots': ['room1'], 'idPrefix': 'sc'}
cfg['seed']['scenes'] = [{'id': 'sc1'}]
g = next(x for x in cfg['saveGroups'] if x['id'] == 'setup')
g['colls'].append('scenes')

# ── UI — หัวข้อ "ฉากในคลิป" ต่อจากโทนสีคลิป · โครงยกจากหัวข้อภาษา (v55)
area = cfg['phases'][0]['form'][0]['card'][0]['card'][2]['card']
lang = next(c for c in area if any(x.get('field') == 'svLang' for x in c.get('card', []) if isinstance(x, dict)))
charsec = next(c for c in area if 'ตัวละครในคลิป' in json.dumps(c.get('card', [])[:1], ensure_ascii=False))
lbl_cls = next(x for x in json.loads(json.dumps(charsec))['card'] if x.get('el') == 'text' and x.get('value') == 'ผู้แสดงเห็นแค่ไหน')['className']
vibe = copy.deepcopy(lang)
vibe['card'][0]['card'][0]['icon'] = 'movie_filter'
vibe['card'][0]['card'][1]['value'] = 'ฉากในคลิป'
vibe['card'][1]['value'] = 'ทุกแบบยังเป็นมินิมอล — ต่างที่การจัดฉากและวิธีเล่า'
sel = vibe['card'][2]; assert sel['field'] == 'svLang'
sel.update(field='svVibe', options=[
    {'value': AUTO_V, 'label': 'อัตโนมัติ', 'desc': 'หมีเลือกฉากให้เข้ากับสินค้า', 'icon': 'auto_awesome'},
    {'value': '', 'label': 'จัดฉากคุมโทน', 'desc': 'สะอาด โทนเดียวทั้งคลิป เสียงโฆษณา', 'icon': 'palette'},
    {'value': REAL_V, 'label': 'ฉากชีวิตจริง', 'desc': 'เหมือนคนใช้จริงถ่ายเอง เสียงเพื่อนเล่า', 'icon': 'home'},
    {'value': CUST_V, 'label': 'กำหนดฉาก', 'desc': 'พิมพ์หรือใส่รูปสถานที่เอง', 'icon': 'edit_note'}])
# แผงกำหนดเอง: ช่องพิมพ์ (โครงช่องลุคของตัวละคร) + รูปสถานที่ (โครงการ์ดรูปหน้าตัวละคร) + วิธีเล่า
human = next(x for x in charsec['card'] if x.get('el') == 'box' and 'svCharSrc' in json.dumps(x))
kids = next(x for x in human['card'] if x.get('el') == 'box' and 'svCharSrc' in json.dumps(x) and 'face' in json.dumps(x))['card']
photo = copy.deepcopy(next(k for k in kids if 'into' in json.dumps(k) and 'face' in json.dumps(k)))
photo.pop('when', None)
TEXTS = {'ยังไม่มีรูปใบหน้า': 'ยังไม่มีรูปสถานที่ (ไม่บังคับ)',
         'แนบรูปหน้าตรง เห็นใบหน้าชัด 1 รูป — ระบบล็อกหน้าให้เป็นคนเดิมทุกช็อต': 'แนบรูปห้องหรือสถานที่จริง 1 รูป — ทุกฉากจะอยู่ในที่นี้',
         'ได้ตัวละครแล้ว — ล็อกหน้าตามรูปนี้': 'ได้รูปสถานที่แล้ว — ทุกฉากอยู่ในที่นี้',
         'ระบบแนบรูปนี้ให้ตอนวาดภาพและทำวิดีโอ เป็นคนเดิมทุกช็อต ทุกคลิป ทุกรอบผลิต': 'ระบบแนบรูปนี้ให้ตอนวาดภาพและทำวิดีโอ ทุกคลิป ทุกรอบผลิต'}
hit = []
def fix(n):
    if isinstance(n, dict):
        if n.get('el') == 'repeat' and n.get('coll') == 'characters': n['coll'] = 'scenes'
        if n.get('into') == 'face': n['into'] = 'room1'
        if n.get('to') == 'face': n['to'] = 'room1'
        for k in ('when', 'src'):
            if isinstance(n.get(k), str): n[k] = n[k].replace('slots.face', 'slots.room1')
        if n.get('el') == 'text' and n.get('value') in TEXTS: hit.append(n['value']); n['value'] = TEXTS[n['value']]
        for v in n.values(): fix(v)
    elif isinstance(n, list):
        for v in n: fix(v)
fix(photo)
assert sorted(hit) == sorted(TEXTS), hit
assert 'face' not in json.dumps(photo) and 'characters' not in json.dumps(photo)
look = copy.deepcopy(next(x for x in kids[3]['card'] if 'charLook' in json.dumps(x)))
look['card'][0].update(value='อยากให้ฉากเป็นแบบไหน (ไม่บังคับ)', icon='location_on')
look['card'][1].update(el='textarea', field='svScene', placeholder='เช่น ห้องนั่งเล่นโทนไม้ โซฟาสีครีม แสงเช้าเข้าทางหน้าต่าง',
                       className='!text-[16px] @[640px]:!text-[15px] !rounded-xl !px-3.5 !py-3 @[640px]:!py-2.5 border-[var(--ev-border)] !min-h-[104px] @[420px]:!min-h-[64px]')   # ยาม mobile-tier ⑦: textarea สูง ≥100px บนมือถือ (คลาสเดียวกับช่องบท s*th)
tone = copy.deepcopy(sel)
tone.update(field='svVoTone', options=[
    {'value': '', 'label': 'แบบโฆษณา', 'desc': 'เสียงพากย์แบบโฆษณา', 'icon': 'campaign'},
    {'value': FRIEND_V, 'label': 'แบบเพื่อนเล่า', 'desc': 'ภาษาพูด เพื่อนแนะนำเพื่อน', 'icon': 'record_voice_over'}])
panel = copy.deepcopy(human)
panel['when'] = S_CUST
panel['card'] = [look, photo, {'el': 'text', 'value': 'วิธีเล่า', 'className': lbl_cls}, tone]
vibe['card'].append(panel)
area.insert(1, vibe)
cfg['values'].update(svVibe=AUTO_V, svScene='', svVoTone='')   # พี่หมีเคาะ 2026-10-16: ค่าเริ่มต้น = อัตโนมัติ (ไฟล์เซฟเก่าที่ไม่มี svVibe ได้อัตโนมัติด้วย · กด "จัดฉากคุมโทน" = prompt เดิมทุกไบต์)

json.dump(cfg, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('✅ v56 · ฉากในคลิป 3 แบบ (คุมโทน/ชีวิตจริง/กำหนดเอง) · รูปฉาก scenes/sc1 · VO รายฉาก %d' % n_nar)
