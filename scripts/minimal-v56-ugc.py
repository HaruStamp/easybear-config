#!/usr/bin/env python3
"""minimal v56 — แนวคลิป [โฆษณามินิมอล (เดิม) / รีวิวแบบเพื่อนเล่า] (พี่หมีสั่ง 2026-10-16 "เอา prompt ที่ลูกค้าเจนมือมาปรับใช้")

ที่มา: ลูกค้าเจนคลิปไฟโซล่าเซลล์เองใน Flow (prompt UGC 8 ช็อต) แล้วบอกว่าดีกว่าคลิปจาก minimal
สิ่งที่ยกมา (เฉพาะแนว "รีวิวแบบเพื่อนเล่า" — แนวเดิมไม่ขยับสักไบต์):
  ① ฉาก = สถานที่ใช้งานจริงแบบมินิมอลอบอุ่น (Pinterest / MUJI / IKEA) ไม่ใช่สตูดิโอพื้นเรียบ
  ② ทุกฉากลงมือทำกับสินค้า · อย่างน้อย 1 ฉากโชว์ผลการทำงานจริง (ไฟสว่างตอนค่ำ / ก่อน-หลัง)
  ③ บทพูดโทนเพื่อนแนะนำเพื่อน เร็วนิด ๆ ไม่ขายแรง · ปิดด้วยประโยคชวนแบบเพื่อน
  ④ บทพูดผูกรายฉาก (Narration ใต้แต่ละฉาก) ให้ปากพูดตรงภาพ
  ⑤ ฉากปิด มือชี้ลงแทนการชวนกดตะกร้า · ห้าม UI ร้านค้า/ตะกร้า/ราคา · Negative มือเพี้ยน นิ้วเกิน
  ⑥ ov ขึ้นต้นด้วยอีโมจิ 1 ตัวได้
ไม่ยกมา (รอบนี้): 8 ช็อต ช็อตละ 1.2 วิ — ต้องรื้อโครงบท 5 ฉาก/ช่วง ทั้งแอป
🛡 svVibe ว่าง/ไฟล์เซฟเก่า = prompt เดิมทุกไบต์ · ห่อของเดิมด้วย block ในตำแหน่งเดิม ไม่แทรก part
รันซ้ำได้ (เจอ svVibe แล้ว = ข้าม) · ต้องรันหลัง v55
"""
import json, os, re, copy

PATH = os.path.join(os.path.dirname(__file__), '..', 'minimal-dev.json')
cfg = json.load(open(PATH, encoding='utf-8'))
if 'svVibe' in cfg['values']:
    print('⏭ v56 แพตช์ไปแล้ว — ไม่ทำซ้ำ'); raise SystemExit(0)
assert 'svLang' in cfg['values'], 'ต้องรัน v55 ก่อน'

UGC_V = 'รีวิวแบบเพื่อนเล่า'
UGC = {'op': 'eq', 'a': '{values.svVibe}', 'b': UGC_V}
NOT_UGC = {'op': 'not', 'a': UGC}
VOICE_ON = {'op': 'and', 'list': [{'op': 'not', 'a': {'op': 'eq', 'a': '{values.svAudio}', 'b': 'ไม่มีเสียงพากย์'}},
                                  {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svAudio}', 'b': 'ASMR'}}]}

def fork(old, new):
    return {'op': 'block', 'sep': '', 'parts': [{'when': NOT_UGC, 'value': old}, {'when': UGC, 'value': new}]}
def plus(old, tail):
    """ของเดิม + ท้าย (เฉพาะ UGC)"""
    return {'op': 'concat', 'parts': [old, {'op': 'block', 'sep': '', 'parts': [{'when': UGC, 'value': tail}]}]}

ops = {o['id']: o for o in cfg['ops']}

# ── บท (mnPlan sys) — ต่อท้ายบล็อกกฎแนว UGC
UGC_PLAN = ('\n\n★ แนวคลิป: รีวิวแบบเพื่อนเล่า (UGC) — ทับกฎสไตล์ด้านบนเฉพาะเรื่องต่อไปนี้:'
            '\n- ฉากเป็นสถานที่ใช้งานจริงแบบมินิมอลอบอุ่น (บ้าน ห้อง ครัว ระเบียง สวน — ไม้ธรรมชาติ ของแต่งโทนครีม ต้นไม้ แบบ Pinterest / MUJI / IKEA) ไม่ใช่สตูดิโอพื้นเรียบ · แสงธรรมชาติ'
            '\n- ทุกฉากมีการลงมือทำกับสินค้าจริง (หยิบ แกะ คลี่ ติดตั้ง กด ทา ใช้) ตามระดับผู้แสดงที่ตั้งไว้ · ต้องมีอย่างน้อย 1 ฉากโชว์ผลการทำงานจริงของสินค้า (เช่น ไฟสว่างตอนค่ำ ก่อน-หลังใช้ ผลลัพธ์หลังใช้)'
            '\n- ฉากสุดท้าย: สินค้าเด่นสวย มือชี้ลงด้านล่างเบา ๆ แทนการชวนกดตะกร้า — ห้ามมีหน้าจอร้านค้า ปุ่มซื้อ ไอคอนตะกร้า หรือราคาในภาพ'
            '\n- vo: ภาษาพูดแบบเพื่อนแนะนำเพื่อน เป็นกันเอง เร็วนิด ๆ ไม่ขายแรง เหมือนคนใช้จริงเล่า (เปิดได้แบบ "แก ...อันนี้ดีมาก" · ปิดแบบชวนเพื่อน เช่น "แปะตะกร้าไว้ให้แล้ว") · ถ้าภาษาเป็น English ใช้ภาษาพูดอังกฤษโทนเดียวกัน · กฎคำลงท้ายและเพศเสียงยังใช้ตามเดิม'
            '\n- ov: ขึ้นต้นได้ด้วยอีโมจิ 1 ตัวที่เข้ากับข้อความ (ข้อยกเว้นของกฎห้าม emoji) · ov1 เป็นชื่อสินค้าแบบสั้น')
sp = ops['mnPlan']['systemInstruction']['parts']
last = sp[-1]
assert isinstance(last, dict) and 'ภาษาของคลิป: English' in json.dumps(last, ensure_ascii=False), 'ท้าย sys ไม่ใช่บล็อกภาษา v55'
sp[-1] = plus(last, UGC_PLAN)

# ── บอร์ด — ต่อท้ายส่วนตัวละคร (part 6)
UGC_BOARD = ' · แนวรีวิว: ฉากจริงในบ้าน/สวนแบบมินิมอลอบอุ่น ไม่ใช่สตูดิโอ · ห้ามวาดหน้าจอร้านค้า/ตะกร้า/ราคา'
for oid in ('mnBoard', 'mnBoard2', 'mnBoard3'):
    p = ops[oid]['prompt']['parts']
    assert 'charBoard' in json.dumps(p[6]), oid
    p[6] = plus(p[6], UGC_BOARD)

# ── วิดีโอ
OLD_LEAD = 'A minimal commercial of approximately 10 seconds as one single continuous full-bleed 9:16 shot: Scandinavian pastel look, soft natural light, moving smoothly through the 5 scenes below in order.'
NEW_LEAD = ('A UGC-style product review, ~10 s, vertical full-bleed 9:16, 5 clean-cut shots below: '
            'photorealistic cozy lived-in minimal home/garden (Pinterest/MUJI/IKEA), natural daylight.')
UGC_VOICE = ' Tone: casual friend-to-friend, not salesy.'
UGC_NEG = ' Also avoid: shopping UI, cart, price.'

SCRIPT_RX = re.compile(r' ?Voice-over script \((?:Thai|English)\): "[^"]*"')
def strip_script(x):
    if isinstance(x, str): return SCRIPT_RX.sub('', x)
    if isinstance(x, list): return [strip_script(v) for v in x]
    if isinstance(x, dict): return {k: (v if k in ('when', 'key', 'table', 'op') else strip_script(v)) for k, v in x.items()}
    return x

# UGC ต้องยาวไม่เกินแนวเดิม (ยาม ② : แนวเดิมยาวสุด 3,893 / 3,900) ⇒ ชดเชยด้วยคำบรรยายฟอนต์ฉบับสั้น + "Overlay" แทน "Thai overlay"
def short_text(x):
    if isinstance(x, str):
        x = x.replace(' Thai overlay: "', ' Overlay: "')
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
    p = ops[oid]['prompt']['parts']
    assert isinstance(p[0], str) and p[0].startswith(OLD_LEAD), oid
    p[0] = fork(p[0], p[0].replace(OLD_LEAD, NEW_LEAD, 1))
    iv = [i for i, x in enumerate(p) if 'Voice-over script' in json.dumps(x, ensure_ascii=False)]
    ineg = [i for i, x in enumerate(p) if 'Negative:' in json.dumps(x, ensure_ascii=False)]
    assert len(iv) == 1 and len(ineg) == 1, (oid, iv, ineg)   # ช่วง 2/3 มีบล็อก CONTINUATION แทรก ⇒ ดัชนีไม่ตายตัว
    # UGC: บทพูดไปอยู่ใต้แต่ละฉาก (Narration) ⇒ ตัดบทรวม "Voice-over script (…)" ออก ไม่งั้นบทซ้ำ 2 ที่ prompt เกิน 3,900 (ยาม ② วัดได้ 4,209)
    noscript = strip_script(copy.deepcopy(p[iv[0]]))
    assert json.dumps(noscript) != json.dumps(p[iv[0]]), (oid, 'ตัดบทรวมไม่ได้')
    p[iv[0]] = fork(p[iv[0]], {'op': 'concat', 'parts': [noscript, {'op': 'block', 'sep': '', 'parts': [{'when': VOICE_ON, 'value': UGC_VOICE}]}]})
    p[ineg[0]] = plus(p[ineg[0]], UGC_NEG)
    its = [i for i, x in enumerate(p) if 'ON-SCREEN TEXT STYLE' in json.dumps(x, ensure_ascii=False)]
    assert len(its) == 1, (oid, its)
    p[its[0]] = fork(p[its[0]], short_text(copy.deepcopy(p[its[0]])))
    for i, part in enumerate(p):
        m = re.search(r'\{item\.ov(\d+)\}', json.dumps(part)) if isinstance(part, dict) and i > ineg[0] else None
        if m:
            k = m.group(1)
            p[i] = fork(part, {'op': 'concat', 'parts': [short_text(copy.deepcopy(part)),
                     {'op': 'block', 'sep': '', 'parts': [{'when': VOICE_ON, 'value': ' VO: "{item.vo%s}"' % k}]}]})
            n_nar += 1
assert n_nar == 15, n_nar   # ช่วง 1/2/3 × 5 ฉาก

# ── UI — หัวข้อ "แนวคลิป" ต่อจากโทนสีคลิป · โครงยกจากหัวข้อภาษา (v55)
area = cfg['phases'][0]['form'][0]['card'][0]['card'][2]['card']
lang = next(c for c in area if any(x.get('field') == 'svLang' for x in c.get('card', []) if isinstance(x, dict)))
vibe = copy.deepcopy(lang)
vibe['card'][0]['card'][0]['icon'] = 'movie_filter'
vibe['card'][0]['card'][1]['value'] = 'แนวคลิป'
vibe['card'][1]['value'] = 'รีวิวแบบเพื่อนเล่า = ใช้สินค้าจริงในบ้าน/สวน เห็นมือลงมือทำ เสียงพากย์แบบเพื่อนแนะนำ (เข้าคู่กับ "เห็นแค่มือ")'
sel = vibe['card'][2]; assert sel['field'] == 'svLang'
sel.update(field='svVibe', options=[
    {'value': '', 'label': 'โฆษณามินิมอล', 'desc': 'สตูดิโอพื้นเรียบ เสียงโฆษณา (แบบเดิม)', 'icon': 'auto_awesome'},
    {'value': UGC_V, 'label': 'รีวิวแบบเพื่อนเล่า', 'desc': 'ใช้จริงในบ้าน · เพื่อนแนะนำเพื่อน', 'icon': 'record_voice_over'}])
area.insert(1, vibe)
cfg['values']['svVibe'] = ''

json.dump(cfg, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('✅ v56 · แนวคลิป UGC · บท +1 บล็อก · บอร์ด ×3 · วิดีโอ ×3 (หัว/เสียง/Negative) · Narration รายฉาก %d' % n_nar)
