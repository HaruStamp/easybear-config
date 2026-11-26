# hardsell-dev v25: เลือกคลิป 10 วิ ได้ (เฉพาะ Omni) — เจ้าของสั่ง 26 พ.ย. ข้อ B
# เดิม: svSec มีแค่ 8/16 · mnVideo durationSeconds 8 ตายตัว · lookups คีย์ 8/16 · tplVidLead "about 8 seconds"
# แก้:
#   - lookups ทุกตารางที่คีย์ด้วย {values.svSec} เพิ่มคีย์ 10 (5 ฉาก ฉากละ 2 วิ · บทพูด ≤32 ตัว/ฉาก รวม ≤160)
#   - mnVideo.durationSeconds = cond(svSec=10 และโมเดล Omni → 10 · อื่น → 8) · บทพูดช่วงเดียวรวม vo5 เมื่อ 10 วิ
#   - tplVidLead ถอด "about 8 seconds" → ความยาวมาจาก lookup clipSecEN ตาม svSec (mnVideo/mnVideo2)
#   - UI: ปุ่มความยาว 2 ชุดตามโมเดล (Omni = 8/10/16 · Veo = 8/16 แบบ fashion) · dropdown วิดีโอ ปิด Veo ตอนเลือก 10 วิ
#   - 360p (คลิปช่วงเดียว) ใช้ได้กับ 8 และ 10 วิ (เดิม eq 8 → lte 10) · ฉาก 5 โชว์เมื่อ >8 วิ · validate ฉาก 6-8 เฉพาะ >10 วิ
#   - 20 วิ ยังไม่ทำ: el.segments.trimEndIfNext / tailTrim เป็นเลขตายตัว และยาม ④ ล็อก 8 − tailTrim (ดูรายงาน)
#   - ⚠️ el.segments / tailTrim ไม่แตะ — 10 วิ เป็นคลิปช่วงเดียว ไม่มีการต่อ
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F))
L = d['lookups']
SEC = '{values.svSec}'
OMNI = {'op': 'contains', 'a': '{values.videoModel}', 'b': 'Omni'}

# ── 1. lookups คีย์ 10 ────────────────────────────────────────────
L['lenSys']['10'] = ('คุณคือผู้กำกับคลิปขายของสไตล์ TikTok ของพี่หมีแว่น (แนวขายดุ — ฮุคแรง โน้มน้าวไว ปิดการขายชัด) — ออกแบบคลิปแนวตั้ง 9:16 ยาว 10 วินาที เป็นช็อตเดียวต่อเนื่อง เดินผ่าน 5 ฉากคงที่ตามลำดับนี้เสมอ:\n'
    '1. ฮุคแรง 0-2s — หยุดนิ้วคนดูตั้งแต่วินาทีแรก ด้วยประโยคหรือภาพที่คนดูต้องหยุดดู\n'
    '2. ปัญหาที่เจอ 2-4s — ปัญหาที่คนดูเจออยู่จริง\n'
    '3. จุดเด่นที่ชัดที่สุด 4-6s — จุดขายหลัก 1 อย่างของสินค้า\n'
    '4. ใช้จริงให้ดู 6-8s — โชว์สินค้าตอนใช้งานจริง ให้เห็นผลกับตา\n'
    '5. ปิดการขาย 8-10s — ชวนซื้อตอนนี้เลย จบที่คน ไม่ใช่การ์ดปิด')
L['lenVo']['10'] = ('กฎความยาวบทพูด (ต้องพูดต่อเนื่องเต็มความยาว ห้ามมีช่วงเงียบ):\n'
    '- คลิปนี้ยาว 10 วินาที มี 5 ฉาก ฉากละ 2 วินาที — vo1 ถึง vo5 ต้องมีบทพูดครบทุกฉาก ห้ามเว้นว่างแม้แต่ฉากเดียว\n'
    '- นับเป็นตัวอักษรไทย ไม่ใช่จำนวนคำ: ฉากละไม่เกิน 32 ตัวอักษร รวมทั้งคลิปไม่เกิน 160 ตัวอักษร\n'
    '  (นับทุกตัวอักษรรวมสระและวรรณยุกต์ เว้นวรรคไม่ต้องนับ) — เกินเมื่อไหร่เสียงจะพูดรัวจนฟังไม่ทัน\n'
    '- เขียนให้ vo1 ถึง vo5 ต่อกันเป็นย่อหน้าเดียวที่อ่านรวดเดียวจบพอดี 10 วินาที ไม่ใช่วลีสั้นที่จบห้วนแยกกัน\n'
    '- ภาษาพูดแบบคนรีวิวจริง ไม่ใช่ภาษาโฆษณาอ่านสคริปต์')
o8 = L['lenOut']['8']
tail4 = '"s4th":"...","s4en":"...","ov4":"...","vo4":"...","cam4":"..."'
assert tail4 in o8
L['lenOut']['10'] = o8.replace(tail4, tail4 + ',"s5th":"...","s5en":"...","ov5":"...","vo5":"...","cam5":"..."')
L['lenActHead']['10'] = L['lenActHead']['8']
L['lenActTail']['10'] = L['lenActTail']['16']   # องก์ 3 มี 2 ฉาก (3-4) → ใช้กติกา "ฉากในองก์เดียวกัน" ของ 16 วิ
L['lenLabel']['10'] = '10 วินาที'
L['lenSecs']['10'] = '10'
L['lenScenes']['10'] = '5'
acts = [('ฉาก 1 ฮุคแรง', 'ฮุคแรง', '0-2 วิ'), ('ฉาก 2 ปัญหาที่เจอ', 'ปัญหาที่เจอ', '2-4 วิ'),
        ('ฉาก 3-4 จุดเด่น + ใช้จริง', 'จุดเด่น + ใช้จริง', '4-8 วิ'), ('ฉาก 5 ปิดการขาย', 'ปิดการขาย', '8-10 วิ')]
for i, (a, n, t) in enumerate(acts, 1):
    L['lenAct']['10|%d' % i] = a; L['actName']['10|%d' % i] = n; L['actTime']['10|%d' % i] = t
scenes = [('ฮุคแรง', 'Hook'), ('ปัญหาที่เจอ', 'The problem'), ('จุดเด่นที่ชัดที่สุด', 'Strongest benefit'),
          ('ใช้จริงให้ดู', 'Demo in real use'), ('ปิดการขาย', 'Closing (spoken ask to buy)')]
for i, (th, en) in enumerate(scenes, 1):
    t = '%d-%ds' % (2 * i - 2, 2 * i)
    L['sceneLab']['10|%d' % i] = '%d. %s [%s]' % (i, th, t)
    L['sceneEN']['10|%d' % i] = 'Scene %d (%s) — %s' % (i, t, en)
    L['sceneAct']['10|%d' % i] = th
for i in (6, 7, 8): L['sceneAct']['10|%d' % i] = ''   # การ์ดฉาก 6-8 ซ่อนตอน 10 วิ (แค่ให้ตารางครบ)
# ความยาวคลิปต่อช่วง (ภาษาอังกฤษ/ไทย) — แทน "about 8 seconds" ที่ฝังใน tplVidLead
L['clipSecEN'] = {'8': ' About 8 seconds long.', '10': ' About 10 seconds long.', '16': ' About 8 seconds long.'}
L['clipSecTH'] = {'8': '8 วิ', '10': '10 วิ', '16': '8 วิ'}
for k, v in L['tplVidLead'].items():
    nv = v.replace(', about 8 seconds, one continuous shot.', ', one continuous shot.').replace(', 9:16 vertical, about 8 seconds.', ', 9:16 vertical.')
    assert nv != v and 'about 8' not in nv, k
    L['tplVidLead'][k] = nv

# ── 2. ops ────────────────────────────────────────────────────────
ops = {o['id']: o for o in d['ops']}
def is_eq8(x):
    return isinstance(x, dict) and x.get('op') == 'eq' and x.get('a') == SEC and x.get('b') == '8'
def fix_eq8(x):   # 360p (ช่วงเดียว) 8 → ≤10
    n = 0
    if isinstance(x, dict):
        for k, v in list(x.items()):
            if is_eq8(v): x[k] = {'op': 'lte', 'a': SEC, 'b': 10}; n += 1
            else: n += fix_eq8(v)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            if is_eq8(v): x[i] = {'op': 'lte', 'a': SEC, 'b': 10}; n += 1
            else: n += fix_eq8(v)
    return n
n360 = fix_eq8(ops['mnVideo']) + fix_eq8(ops['mnVideo2'])
assert n360 == 8, n360

def add_clip_sec(op):
    parts = op['prompt']['parts']
    i = next(i for i, p in enumerate(parts) if isinstance(p, dict) and p.get('table') == 'tplVidLead')
    if not (isinstance(parts[i + 1], dict) and parts[i + 1].get('table') == 'clipSecEN'):
        parts.insert(i + 1, {'op': 'lookup', 'table': 'clipSecEN', 'key': SEC, 'fallback': ' About 8 seconds long.'})
add_clip_sec(ops['mnVideo']); add_clip_sec(ops['mnVideo2'])

v1 = ops['mnVideo']
v1['durationSeconds'] = {'op': 'cond', 'when': {'op': 'and', 'list': [{'op': 'eq', 'a': SEC, 'b': '10'}, OMNI]}, 'then': '10', 'else': '8'}
v1['logRun'] = {'op': 'concat', 'parts': ['[{item.productName} คลิป {item.clipIndex}] กำลังสร้างวิดีโอ ',
    {'op': 'lookup', 'table': 'clipSecTH', 'key': SEC, 'fallback': '8 วิ'}, ' (ช็อตเดียวต่อเนื่อง)']}
# บทพูดช่วง 1: 10 วิ ต้องรวม vo5 ด้วย
OLD = '. Natural Thai pronunciation and speed, no English. No music or sound effects — only the voice. Script (Thai): "{item.vo1} {item.vo2} {item.vo3} {item.vo4}"'
hit = 0
def fix_script(parts):
    global hit
    for i, p in enumerate(parts):
        if p == OLD:
            parts[i:i + 1] = [OLD[:-1], {'op': 'block', 'sep': '', 'parts': [{'when': 'values.svSec=10', 'value': ' {item.vo5}'}]}, '"']
            hit += 1; return True
        if isinstance(p, dict):
            for v in p.values():
                if isinstance(v, list) and fix_script(v): return True
    return False
fix_script(v1['prompt']['parts'])
assert hit == 1, hit

# mnPlan: validate ฉาก 6-8 บังคับเฉพาะ >10 วิ (ฉาก 5 บังคับ >8 วิ เหมือนเดิม) · retryHint บอก 10 วิ
pl = ops['mnPlan']
nv = 0
for c in pl['validate']['list']:
    if c.get('op') == 'or' and len(c.get('list', [])) == 2 and c['list'][0].get('op') == 'lte':
        key = json.dumps(c['list'][1])
        if any('plan.0.s%d' % k in key for k in (6, 7, 8)):
            c['list'][0]['b'] = '10'; nv += 1
assert nv == 6, nv
rh = pl['retryHint']['parts']
rh[0] = rh[0].replace('(8 วินาที = ฉาก 1 ถึง 4 · 16 วินาที = ฉาก 1 ถึง 8)', '(8 วินาที = ฉาก 1 ถึง 4 · 10 วินาที = ฉาก 1 ถึง 5 · 16 วินาที = ฉาก 1 ถึง 8)')
assert '10 วินาที = ฉาก 1 ถึง 5' in rh[0]

# ── 3. UI ─────────────────────────────────────────────────────────
done = {'sec': 0, 'vm': 0, 'res': 0, 'scene': 0}
def ui(x, parent=None, idx=None):
    if isinstance(x, dict):
        # ปุ่มความยาว: 2 ชุดตามโมเดล
        if x.get('el') == 'grid-select' and x.get('field') == 'svSec' and not x.get('__v25'):
            base = {k: v for k, v in x.items()}
            omni = dict(base, cols=3, options=[
                {'value': '8', 'label': '8 วินาที', 'desc': '1 ช่วง · 4 ฉาก'},
                {'value': '10', 'label': '10 วินาที', 'desc': '1 ช่วง · 5 ฉาก'},
                {'value': '16', 'label': '16 วินาที', 'desc': '2 ช่วงต่อฉาก · 8 ฉาก'}], when=OMNI)
            veo = dict(base, when={'op': 'not', 'a': OMNI})
            parent[idx:idx + 1] = [omni, veo,
                {'el': 'text', 'value': 'คลิป 10 วิ ใช้ได้เฉพาะ Omni — Veo ทำได้ 8 / 16 วิ',
                 'className': '!text-[13px] @[640px]:!text-[12.5px] opacity-55 px-0.5 leading-snug', 'when': {'op': 'not', 'a': OMNI}},
                {'el': 'text', 'value': 'ตอนนี้ตั้งความยาว 10 วิ แต่ Veo ทำไม่ได้ — เลือก 8 หรือ 16 วินาทีใหม่ก่อนเริ่ม',
                 'className': '!text-[13px] @[640px]:!text-[12.5px] font-bold !text-[var(--ev-accent)] px-0.5 leading-snug',
                 'when': {'op': 'and', 'list': [{'op': 'not', 'a': OMNI}, {'op': 'eq', 'a': SEC, 'b': '10'}]}}]
            done['sec'] += 1; return 'restart'
        if x.get('el') == 'dropdown' and x.get('field') == 'videoModel':
            for o in x['options']:
                if 'Omni' not in o['value']:
                    o['disabledWhen'] = {'op': 'eq', 'a': SEC, 'b': '10'}; o['reason'] = 'ทำได้แค่ 8 / 16 วิ'
            done['vm'] += 1
        if x.get('el') == 'grid-select' and x.get('field') == 'svRes':
            w = x.get('when')
            if w == {'op': 'not', 'a': {'op': 'eq', 'a': SEC, 'b': '16'}}:
                x['when'] = {'op': 'not', 'a': {'op': 'gt', 'a': SEC, 'b': 10}}
                x['options'][0]['desc'] = '24 เครดิต / 8 วิ · 30 / 10 วิ · ภาพคม ลง Shopee ได้'
                x['options'][1]['desc'] = '8 เครดิต / 8 วิ · 10 / 10 วิ · ภาพไม่คม'
                done['res'] += 1
            elif w == {'op': 'eq', 'a': SEC, 'b': '16'}:
                x['when'] = {'op': 'gt', 'a': SEC, 'b': 10}
                x['options'][1]['desc'] = 'ใช้ได้กับคลิป 8 / 10 วิ เท่านั้น · ตอนนี้ 16 วิ จะใช้ 720p 48 เครดิต'
                done['res'] += 1
        if x.get('el') == 'text' and isinstance(x.get('value'), str) and x['value'].startswith('360p'):
            w = json.dumps(x.get('when'))
            if '"b": "8"' in w:
                fix_eq8(x)
                x['value'] = '360p: ทำได้เฉพาะคลิปช่วงเดียว (8 / 10 วิ) · ใช้ภาพเฟรมแรกเป็นภาพอ้างอิงแทนการขยับจากภาพนั้นตรงๆ — เปิดคลิปอาจไม่ตรงภาพเฟรมแรกเป๊ะ'
                done['res'] += 1
            elif '"b": "16"' in w:
                x['when']['list'][1] = {'op': 'gt', 'a': SEC, 'b': 10}
                x['value'] = '360p ทำได้เฉพาะคลิปช่วงเดียว — ตอนนี้ตั้งความยาว 16 วิ คลิปจะใช้ 720p · ถ้าจะประหยัดด้วย 360p ให้เลือก 8 หรือ 10 วินาที'
                done['res'] += 1
        # การ์ดฉาก 5-8: เดิม values.svSec=16
        if x.get('when') == 'values.svSec=16' and x.get('el') == 'box':
            s = json.dumps(x, ensure_ascii=False)
            x['when'] = {'op': 'gt', 'a': SEC, 'b': 8} if '"field": "s5th"' in s else {'op': 'gt', 'a': SEC, 'b': 10}
            done['scene'] += 1
        for k, v in list(x.items()):
            if k == 'when': continue
            ui(v)
    elif isinstance(x, list):
        i = 0
        while i < len(x):
            r = ui(x[i], x, i)
            i += 4 if r == 'restart' else 1
ui(d['phases'])
assert done == {'sec': 1, 'vm': 1, 'res': 4, 'scene': 4}, done

# ── 4. ตรวจ: ทุก lookup ที่คีย์ด้วย svSec มีคีย์ 10 ครบ ────────────
miss = []
def chk(x):
    if isinstance(x, dict):
        if x.get('op') == 'lookup' and isinstance(x.get('key'), str) and x['key'].startswith(SEC):
            t = x['table']; k = x['key'].replace(SEC, '10')
            if k not in L.get(t, {}): miss.append((t, k))
        for v in x.values(): chk(v)
    elif isinstance(x, list):
        for v in x: chk(v)
chk(d['ops']); chk(d['phases'])
assert not miss, miss
print('v25: 360p conds', n360, '· validate', nv, '· UI', done)
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))
