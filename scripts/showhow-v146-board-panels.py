#!/usr/bin/env python3
"""showhow-v146 — สตอรีบอร์ด 6 / 8 ช่อง (อัปเดตใหญ่ พี่หมี 26 พ.ย. · showhow ข้อ 5 · แผนใน easybear-showhow docs/HANDOFF.md)
ขอบเขตรอบนี้: **เฉพาะคลิป 10 วิ** (ช่วงเดียว mnPlan → mnBoard → mnVideo · s6..s8 มีฟิลด์/สปอว์น/ช่องแก้บทอยู่แล้วจากโหมด 20 วิ)
  20-60 วิ ผูก "5 ฉาก/ช่วง" ทั้งระบบ (s{5(K-1)+1}en · mnTrA · sceneEN · ยาม) ⇒ ตั้ง 6/8 แล้วเลือก 20 วิขึ้นไป = ค่าถูกเมิน (เท่า 5 ช่อง)
ค่า: values.svPanels = '' (5 ช่อง ค่าเริ่ม) / '6' / '8' — ค่ากลางที่หน้าตั้งค่า ใต้ "ความยาวคลิป" (โผล่เฉพาะ 10 วิ)
  🪤 ไม่ทำเป็นค่ารายงาน/ไม่เพิ่ม op: ไม่มี where ราย kid ใน productLoop.gens (engine 1.22 นับ slot ว่าง = คลิปพัง หยุดรอบ)
หลักการ "ปิด = ไบต์เดิม": ทุกจุดที่แตะห่อ cond(PN, ใหม่, ของเดิม) หรือ block ที่ when = PN ⇒ svPanels='' หรือ svSec≠10 ได้ prompt เดิมทุกตัวอักษร
ความยาวบทพูด = ต่อวินาที ตาม VC-4244 (เสียงรวบ: 4-5 คำ/2 วิ ≈ 2-2.5 คำ/วิ) — ตารางเดียว PANELS ข้างล่างสร้างทั้ง
  ① กฎ lenVo ที่บอก LLM ② ยามความยาวใน mnPlan.validate (เกิน = ยิงใหม่พร้อม retryHint) ③ clamp ใน prompt บอร์ด/วิดีโอ (กันบทที่ผู้ใช้แก้/แปลเองยาวเกิน)
  ⇒ ตัววัด G9 อ่านเพดาน clamp จาก config แล้ววัดด้วยบทยาวสุด (p95/สุดขีด) ที่โดน clamp จริง = ยาวสุดเท่าที่เป็นไปได้
งบ prompt (เพดาน 3,900 · วิดีโอเดิมยาวสุด 3,874): โหมด 6/8 ไม่ใส่บรรทัด "Camera:" รายฉาก (ช่องบอร์ดมีมุมกล้องแล้ว + ประโยค "scene N follows panel N: … camera angle")
บอร์ด image 1 = แผ่นของช่วงนี้ (showhow ตั้งใจต่างจาก minimal) — refs ไม่แตะ
ใช้: python3 scripts/showhow-v146-board-panels.py  (รันบน v145 · รันซ้ำ = ไม่ทำอะไร)
"""
import json, re, sys, copy
P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
s0 = open(P, encoding='utf-8').read()
c = json.loads(s0)
assert json.dumps(c, ensure_ascii=False, indent=1) + '\n' == s0
L = c['lookups']; O = {o['id']: o for o in c['ops']}
if 'svPanels' in c['values']:
    print('v146: ทำไปแล้ว — ไม่แตะ'); sys.exit(0)

# ── ตารางเดียว: จำนวนช่อง → จังหวะ · คำต่อฉาก · เพดานตัวอักษร (ยาม + clamp ใช้ตัวเลขชุดนี้) ──
#   คำต่อฉาก = 2-2.5 คำ/วิ × วินาทีต่อฉาก (VC-4244: 4-5 คำต่อ 2 วิ) · 5 ช่องเดิมไม่แตะ (ของ VC-4244 เอง)
#   เพดานตัวอักษร (ask = บอก LLM · cap = ยาม/clamp ปล่อยเผื่อ ~15%) — ตั้งจากงบ prompt วิดีโอ 8 ฉาก ≤ 3,900
PANELS = {
    6: dict(sec='1.7', words='3-4', total='18-24', beats='ฉาก 1 = จังหวะ 1 · ฉาก 2 = จังหวะ 2 · ฉาก 3-4 = จังหวะ 3 (ลงมือ 2 ขั้น ภาพต่างกัน) · ฉาก 5 = จังหวะ 4 · ฉาก 6 = จังหวะ 5',
            times=['0-1.7', '1.7-3.3', '3.3-5', '5-6.7', '6.7-8.3', '8.3-10'],
            ask=dict(en=100, th=60, vo=32, ov=18), cap=dict(en=120, th=75, vo=40, ov=22), ovw='2-4', thw='10'),
    8: dict(sec='1.25', words='2-3', total='16-24', beats='ฉาก 1 = จังหวะ 1 · ฉาก 2 = จังหวะ 2 · ฉาก 3-5 = จังหวะ 3 (ลงมือทีละขั้น ภาพต่างกันทุกฉาก) · ฉาก 6-7 = จังหวะ 4 · ฉาก 8 = จังหวะ 5',
            times=['0-1.3', '1.3-2.5', '2.5-3.8', '3.8-5', '5-6.3', '6.3-7.5', '7.5-8.8', '8.8-10'],
            ask=dict(en=68, th=50, vo=24, ov=16), cap=dict(en=80, th=60, vo=30, ov=20), ovw='2-3', thw='8'),
}
FIELD = {'en': 's{k}en', 'th': 's{k}th', 'vo': 'vo{k}', 'ov': 'ov{k}'}

def eq(a, b): return {'op': 'eq', 'a': a, 'b': b}
def NOT(x): return {'op': 'not', 'a': x}
def AND(*x): return {'op': 'and', 'list': list(x)}
def OR(*x): return {'op': 'or', 'list': list(x)}
def cond(w, t, e): return {'op': 'cond', 'when': w, 'then': t, 'else': e}
def blk(w, v): return {'op': 'block', 'sep': '', 'parts': [{'when': w, 'value': v}]}
def cat(*p): return {'op': 'concat', 'parts': list(p)}
PAN = '{values.svPanels}'
SEC10 = eq('{values.svSec}', '10')
PM = {6: AND(SEC10, eq(PAN, '6')), 8: AND(SEC10, eq(PAN, '8'))}
PN = OR(PM[6], PM[8])
NUM = cond(PN, PAN, '5')                                   # "5" เดิมเมื่อปิด
KEY = cond(PN, cat('10p', PAN), '{values.svSec}')           # คีย์ตาราง len* — ปิด = {values.svSec} เดิม
def need(k): return PN if k == 6 else PM[8]                 # ฉาก 6 มีทั้ง 6/8 ช่อง · ฉาก 7-8 เฉพาะ 8 ช่อง

c['values']['svPanels'] = ''

# ── 1. lookups ของบท (คีย์ 10p6 / 10p8) ──
SYS10 = L['lenSys']['10']; OUT10 = L['lenOut']['10']; VO10 = L['lenVo']['10']
A0 = 'เป็นช็อตเดียวต่อเนื่อง เดินผ่าน 5 ฉาก ฉากละ 2 วินาที ตามโครงเรื่องข้างล่าง:'
assert A0 in SYS10
J0 = '"s5th":"...","s5en":"...","ov5":"...","vo5":"...","cam5":"..."}'
assert J0 in OUT10
OV0 = 'ovN ทุกตัวเป็นภาษาไทย บรรทัดเดียว ไม่เกิน 5 คำ'
assert OV0 in OUT10
H0 = 'จำนวน object ในอาร์เรย์ = จำนวนคลิปที่ขอ (ขอ 1 คลิปก็ต้องเป็น array ที่มี 1 object)'
assert H0 in OUT10
VOT = VO10.split('\n')
assert len(VOT) == 5 and VOT[2].startswith('- ฉากละ 5-7 คำไทย'), VOT
for n, d in PANELS.items():
    k = '10p%d' % n; a, cp = d['ask'], d['cap']
    L['lenSys'][k] = SYS10.replace(A0, (f'เป็นช็อตเดียวต่อเนื่อง เดินผ่าน {n} ฉาก ฉากละราว {d["sec"]} วินาที (สตอรีบอร์ด {n} ช่อง จังหวะเร็ว) — '
        f'โครงเรื่องข้างล่างมี 5 จังหวะ ให้กระจายลง {n} ฉาก: {d["beats"]} · คำว่า "ฉาก 1-5" ในโครงเรื่องและกฎข้างล่าง = จังหวะ 1-5 · '
        f'ฉากสุดท้ายของคลิป = ฉาก {n} · คลิปนี้คือช่วง 10 วินาทีเดียว {n} ฉากติดกัน (เห็นพื้นที่ ≥2 ฉาก · ภาพนิ่งผลลัพธ์ล้วนได้แค่ฉาก {n}) · โครงเรื่อง:'))
    extra = ''.join(f',"s{j}th":"...","s{j}en":"...","ov{j}":"...","vo{j}":"...","cam{j}":"..."' for j in range(6, n + 1))
    L['lenOut'][k] = (OUT10.replace(J0, J0[:-1] + extra + '}')
        .replace(H0, H0 + f' แต่ละ object ต้องมีครบทั้ง {n} ฉาก (s1..s{n}) ห้ามขาดฉากใดฉากหนึ่ง')
        .replace(OV0, f'ovN ทุกตัวเป็นภาษาไทย บรรทัดเดียว {d["ovw"]} คำ (ฉากสั้น {d["sec"]} วินาที อ่านทัน)'))
    L['lenVo'][k] = '\n'.join([
        f'กฎความยาวบท (สตอรีบอร์ด {n} ช่อง ฉากสั้น — ทับจำนวนคำ/ความยาวในกฎข้างบนทั้งหมด):',
        f'- คลิปนี้ยาว 10 วินาที มี {n} ฉาก ฉากละราว {d["sec"]} วินาที — vo1 ถึง vo{n} ต้องมีบทพูดครบทุกฉาก ห้ามเว้นว่างแม้แต่ฉากเดียว',
        f'- ความเร็วพูดคงที่ 2-2.5 คำต่อวินาที (= 4-5 คำต่อ 2 วินาที) ⇒ ฉากละ {d["words"]} คำ รวมทั้งคลิป {d["total"]} คำ — ยาวกว่านี้เสียงจะรัวรวบฟังไม่ทัน',
        VOT[3].replace('vo1 ถึง vo5', f'vo1 ถึง vo{n}'), VOT[4],
        f'- ความยาวต่อฉาก (นับตัวอักษร · ระบบตรวจ เกินเพดาน = ต้องเขียนใหม่ทั้งชุด): voN ≤ {a["vo"]} · ovN ≤ {a["ov"]} · sNth ≤ {a["th"]} (ไม่เกิน {d["thw"]} คำ) · '
        f'sNen 1 ประโยคสั้น ≤ {a["en"]} ตัวอักษร (ท่า/มุมกล้องอยู่ในช่องบอร์ดแล้ว ไม่ต้องบรรยายยาว แต่ยังต้องมีสีและชิ้นส่วนเด่นของสินค้าเมื่อเห็นสินค้า)'])
    L['lenScenes'][k] = str(n)
    for j, t in enumerate(d['times'], 1): L['sceneEN'][f'{k}|{j}'] = f'Scene {j} ({t}s)'
for j in (6, 7, 8): L['sceneAct'][f'10|{j}'] = f'ฉาก {j}'   # หัวกล่องแก้บทฉาก 6-8 ตอนคลิป 10 วิ (โผล่เฉพาะโหมด 6/8)

# ── 2. clamp รายฉาก (เฉพาะโหมด 6/8 · ปิด = token เดิม) ──
TOK = re.compile(r'\{item\.(s(\d+)en|s(\d+)th|vo(\d+)|ov(\d+))\}')
def kind(m):
    g = m.group(1)
    return 'en' if g.endswith('en') else 'th' if g.endswith('th') else 'vo' if g.startswith('vo') else 'ov'
def clamped(tok, kd):
    return cond(PM[8], {'op': 'clamp', 'value': tok, 'max': PANELS[8]['cap'][kd]},
                cond(PM[6], {'op': 'clamp', 'value': tok, 'max': PANELS[6]['cap'][kd]}, tok))
def split_tokens(s):
    out, i = [], 0
    for m in TOK.finditer(s):
        if m.start() > i: out.append(s[i:m.start()])
        out.append(clamped(m.group(0), kind(m))); i = m.end()
    if i < len(s): out.append(s[i:])
    return out
nclamp = 0
def clamp_walk(x):
    """แทน token บทรายฉากใน 'ข้อความ prompt' เท่านั้น: parts ของ concat + value ของ block (ไม่แตะตัวเทียบใน when)"""
    global nclamp
    if isinstance(x, dict):
        if x.get('op') == 'concat':
            new = []
            for p in x['parts']:
                if isinstance(p, str) and TOK.search(p): sp = split_tokens(p); nclamp += len(TOK.findall(p)); new.extend(sp)
                else: clamp_walk(p); new.append(p)
            x['parts'] = new
        elif x.get('op') == 'block':
            for q in x['parts']:
                v = q.get('value')
                if isinstance(v, str) and TOK.search(v): nclamp += len(TOK.findall(v)); q['value'] = cat(*split_tokens(v))
                else: clamp_walk(v)
        elif x.get('op') == 'cond':
            clamp_walk(x.get('then')); clamp_walk(x.get('else'))
    elif isinstance(x, list):
        for y in x: clamp_walk(y)

# ── 3. mnVideo (ช่วงเดียวของ 10 วิ) ──
V = O['mnVideo']; vp = V['prompt']['parts']
# 3a. บรรทัด Camera: รายฉาก — ไม่ใส่ในโหมด 6/8 (งบ prompt · ช่องบอร์ดมีมุมกล้องแล้ว)
ncam = 0
def camwalk(x):
    global ncam
    if isinstance(x, dict):
        v = x.get('value')
        if 'when' in x and isinstance(v, dict) and v.get('op') == 'concat' and v.get('parts', [None])[0] == 'Camera: ':
            x['when']['list'].append(NOT(PN)); ncam += 1; return
        for y in x.values(): camwalk(y)
    elif isinstance(x, list):
        for y in x: camwalk(y)
camwalk(vp); assert ncam == 5, ncam
# 3b. ฉาก 6-8 = สำเนาฉาก 5 (บรรทัด + ข้อความบนจอ) ห่อ when
i5 = next(i for i, p in enumerate(vp) if '{item.s5en}' in json.dumps(p, ensure_ascii=False))
assert '{item.ov5}' in json.dumps(vp[i5 + 1], ensure_ascii=False) and 'Scene 5 (8-10s)' in json.dumps(vp[i5], ensure_ascii=False)
def scene_copy(parts, k):
    s = json.dumps(parts, ensure_ascii=False)
    for f in ('s%den', 's%dth', 'ov%d', 'vo%d', 'cam%d'): s = s.replace('{item.' + f % 5 + '}', '{item.' + f % k + '}')
    s = s.replace('"{values.svSec}|5"', '"{values.svSec}|%d"' % k).replace('Scene 5 (8-10s)', 'Scene %d' % k)
    return json.loads(s)
for k in (8, 7, 6): vp.insert(i5 + 2, blk(need(k), cat(*scene_copy(vp[i5:i5 + 2], k))))
# 3c. ป้ายเวลา sceneEN ตามจำนวนช่อง
def rekey(x, table):
    if isinstance(x, dict):
        if x.get('op') == 'lookup' and x.get('table') == table and isinstance(x.get('key'), str) and x['key'].startswith('{values.svSec}'):
            x['key'] = cat(KEY, x['key'][len('{values.svSec}'):]) if x['key'] != '{values.svSec}' else KEY; return 1
        return sum(rekey(y, table) for y in x.values())
    if isinstance(x, list): return sum(rekey(y, table) for y in x)
    return 0
assert rekey(vp, 'sceneEN') == 8
# 3d. "5 scenes" → จำนวนช่อง
def num_split(parts, needle):
    for i, p in enumerate(parts):
        if isinstance(p, str) and needle in p:
            a, b = p.split(needle, 1); pre, post = needle.split('5', 1)
            parts[i:i + 1] = [a + pre, NUM, post + b]; return True
        if isinstance(p, dict) and p.get('op') == 'concat' and num_split(p['parts'], needle): return True
    return False
assert num_split(vp, 'through 5 scenes in order')
assert num_split(vp, "this part's 5 scenes")
# 3e. บทพูดรวม vo1..vo5 → + vo6..vo8
VS = {'. Voice-over script: "{item.vo1} {item.vo2} {item.vo3} {item.vo4} {item.vo5}"', '. Spoken, no captions: "{item.vo1} {item.vo2} {item.vo3} {item.vo4} {item.vo5}"'}
nvo = 0
def vowalk(x):
    global nvo
    if isinstance(x, dict):
        if x.get('op') == 'concat':
            for i, p in enumerate(x['parts']):
                if isinstance(p, str) and p in VS:
                    x['parts'][i:i + 1] = [p[:-1], blk(PN, ' {item.vo6}'), blk(PM[8], ' {item.vo7} {item.vo8}'), '"']; nvo += 1
        for y in x.values(): vowalk(y)
    elif isinstance(x, list):
        for y in x: vowalk(y)
vowalk(vp); assert nvo == 2, nvo
clamp_walk(V['prompt'])

# ── 4. mnBoard (ช่วงเดียวของ 10 วิ) ──
B = O['mnBoard']; bp = B['prompt']['parts']
LAY0 = 'ตาราง 2 คอลัมน์ ช่องละ 1 ฉาก เรียงซ้าย→ขวา แล้วลงแถวถัดไป ครบ 1-5 · ฉาก 1 ถึง 4 อยู่ในช่องทรงตั้ง (สูงกว่ากว้าง ราว 3:4) ขนาดเท่ากันทุกช่อง · ฉาก 5 เป็นช่องเดียวกินเต็มความกว้างที่แถวล่างสุด'
LAY = {6: 'ตาราง 2 คอลัมน์ 3 แถว ช่องละ 1 ฉาก เรียงซ้าย→ขวา แล้วลงแถวถัดไป ครบ 1-6 · ทุกช่องขนาดเท่ากัน ทรงตั้งเล็กน้อย (สูงกว่ากว้างนิดหน่อย) · ห้ามมีช่องกินเต็มแถว',
       8: 'ตาราง 2 คอลัมน์ 4 แถว ช่องละ 1 ฉาก เรียงซ้าย→ขวา แล้วลงแถวถัดไป ครบ 1-8 · ทุกช่องขนาดเท่ากัน ทรงเกือบจัตุรัส · ห้ามมีช่องกินเต็มแถว'}
RNG0 = '(ช่วงนี้คือ 1 ถึง 5)'
i2 = next(i for i, p in enumerate(bp) if isinstance(p, str) and LAY0 in p)
a, rest = bp[i2].split(LAY0, 1); mid, b = rest.split(RNG0, 1)
bp[i2:i2 + 1] = [a, cond(PM[8], LAY[8], cond(PM[6], LAY[6], LAY0)), mid, cond(PN, cat('(ช่วงนี้คือ 1 ถึง ', PAN, ')'), RNG0), b]
# ฉากปิด "ช่องฉาก 5 = ฉากปิดของคลิป" (3 แบบ) → ช่องสุดท้ายจริง
ncl = 0
def closewalk(x):
    global ncl
    if isinstance(x, dict):
        for q in (x.get('parts') or []) if x.get('op') == 'block' else []:
            v = q.get('value')
            if isinstance(v, str) and v.startswith('\nช่องฉาก 5 = '): q['value'] = cat('\nช่องฉาก ', NUM, v[len('\nช่องฉาก 5'):]); ncl += 1
            elif isinstance(v, dict) and v.get('op') == 'concat' and isinstance(v['parts'][0], str) and v['parts'][0].startswith('\nช่องฉาก 5 = '):
                v['parts'][0:1] = ['\nช่องฉาก ', NUM, v['parts'][0][len('\nช่องฉาก 5'):]]; ncl += 1
        for y in x.values(): closewalk(y)
    elif isinstance(x, list):
        for y in x: closewalk(y)
closewalk(bp); assert ncl == 3, ncl
j5 = next(i for i, p in enumerate(bp) if isinstance(p, dict) and p.get('op') == 'concat' and p['parts'] == ['\n5. {item.s5th} · มุมกล้อง: {item.cam5}'])
assert '{item.ov5}' in json.dumps(bp[j5 + 1], ensure_ascii=False) and j5 + 2 == len(bp)
for k in (6, 7, 8): bp.append(blk(need(k), cat(*scene_copy(bp[j5:j5 + 2], k))))
clamp_walk(B['prompt'])
assert B['logRun'] == '[{item.productName} คลิป {item.clipIndex}] กำลังวาดภาพสตอรีบอร์ด 5 ช่อง'
B['logRun'] = cat('[{item.productName} คลิป {item.clipIndex}] กำลังวาดภาพสตอรีบอร์ด ', NUM, ' ช่อง')

# ── 5. mnPlan: คีย์ตาราง + ยามความยาว + คำใบ้ ──
PL = O['mnPlan']
sp = PL['systemInstruction']['parts'][0]['parts']
for i, t in ((0, 'lenSys'), (5, 'lenVo'), (7, 'lenOut')):
    assert sp[i]['table'] == t and sp[i]['key'] == '{values.svSec}'; sp[i]['key'] = KEY
assert rekey(PL['logRun'], 'lenScenes') == 1
old_hint = PL['retryHint']
def hint(n):
    cp = PANELS[n]['cap']
    return (f'\n\nรอบที่แล้วบทไม่ผ่าน (ขาดฉาก หรือยาวเกินเพดาน) — รอบนี้ต้องส่ง JSON ครบทุกคีย์ของทุกฉาก s1..s{n} (th/en/ov/vo/cam) ของทุกคลิป ห้ามเว้นว่าง '
            f'และสตอรีบอร์ด {n} ช่องฉากสั้น ทุกฉากต้องไม่เกิน: vo {cp["vo"]} · ov {cp["ov"]} · s*th {cp["th"]} · s*en {cp["en"]} ตัวอักษร — บทพูดฉากละ {PANELS[n]["words"]} คำ')
PL['retryHint'] = cond(PM[8], hint(8), cond(PM[6], hint(6), old_hint))
nval = 0
for n in (6, 8):
    for ci in range(10):
        chk = []
        for k in range(1, n + 1):
            for kd, f in FIELD.items():
                x = '{item.data.plan.%d.%s}' % (ci, f.format(k=k))
                chk.append(eq({'op': 'clamp', 'value': x, 'max': PANELS[n]['cap'][kd]}, x))
                if k >= 6 and kd in ('en', 'th', 'vo'): chk.append(NOT(eq(x, '')))
        alt = [NOT(PM[n])] + ([{'op': 'lte', 'a': '{values.clipsPerProduct}', 'b': str(ci)}] if ci else [])
        PL['validate']['list'].append(OR(*alt, AND(*chk))); nval += len(chk)

# ── 6. UI ──
# 6a. หน้าตั้งค่า: การ์ด "สตอรีบอร์ด" ใต้ความยาวคลิป (เฉพาะ 10 วิ)
prod = c['phases'][0]['form'][0]['card'][0]['card'][4]
assert prod['card'][1]['card'][1]['field'] == 'svSec'
res = prod['card'][2]
head = copy.deepcopy(res['card'][0]); assert head['card'][1]['value'] == 'ความละเอียด'
head['card'][0]['icon'] = 'grid_view'; head['card'][1]['value'] = 'ช่องสตอรีบอร์ด'
HINT = res['card'][2]['className']
prod['card'].insert(2, {'el': 'box', 'className': 'flex flex-col gap-1.5', 'when': SEC10, 'card': [head,
    {'el': 'grid-select', 'field': 'svPanels', 'cols': 3, 'contained': True, 'mobile': {'cols': 3},
     'className': res['card'][1]['className'], 'options': [
        {'value': '', 'label': '5 ช่อง', 'desc': 'ค่าเริ่ม · ฉากละ 2 วิ'},
        {'value': '6', 'label': '6 ช่อง', 'desc': 'ฉากละ ~1.7 วิ'},
        {'value': '8', 'label': '8 ช่อง', 'desc': 'ฉากละ ~1.25 วิ · เร็ว'}]},
    {'el': 'text', 'value': 'ช่องมาก = ฉากสั้น เปลี่ยนภาพถี่ขึ้น · บทพูดสั้นลงตามเวลา (ฉากละ 2-4 คำ พูดเร็วเท่าเดิม ไม่รัว) · ใช้ได้เฉพาะคลิป 10 วิ',
     'className': HINT, 'when': NOT(eq(PAN, ''))}]})
# 6b. กล่องแก้บทฉาก 6-8 โผล่ในโหมด 6/8 · ป้ายเวลาฉาก 1-8 ตามจำนวนช่อง
scn = c['phases'][0]['form'][3]['card'][0]['card'][5]['card'][0]['card'][0]['card'][1]['card'][2]['card'][3]['card'][0]['card']
for k in range(1, 9):
    box = scn[k - 1]; row = box['card'][0]
    assert row['card'][0]['card'][0]['value'] == str(k)
    t = row['card'][3]; assert t['value'].endswith(' วิ') and t.get('icon') == 'schedule', t
    t['value'] = cond(PM[8], PANELS[8]['times'][k - 1] + ' วิ', cond(PM[6], PANELS[6]['times'][k - 1] + ' วิ', t['value']) if k <= 6 else t['value'])
    if k >= 6:
        assert box['when'] == 'values.svSec>10'
        box['when'] = OR(NOT({'op': 'lte', 'a': '{values.svSec}', 'b': '10'}), need(k))

print(f'✅ v146: svPanels · ตาราง 10p6/10p8 · วิดีโอ +3 ฉาก (Camera รายฉากปิดในโหมด 6/8: {ncam}) · บอร์ด +3 ช่อง + เลย์เอาต์ · clamp {nclamp} จุด · ยามความยาว {nval} ข้อ · UI')
open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
