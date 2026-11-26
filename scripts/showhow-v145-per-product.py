#!/usr/bin/env python3
"""showhow-v145 — ตั้งค่าเฉพาะสินค้า/งาน (อัปเดตใหญ่ พี่หมี 26 พ.ย. ข้อ 7 · ลอกท่า fashion E20 `own` + hardsell v33)
ค่ากลาง = หน้าตั้งค่าเหมือนเดิม · หน้าแก้งาน กลุ่ม "ปรับเฉพาะงานนี้" มีสวิตช์ "ใช้ค่าของงานนี้แทนค่ากลาง" (products.own = 'true')
เปิดสวิตช์ + เลือกค่า (ว่าง = ตามค่ากลาง) → งานนี้ใช้ค่าของตัวเอง 4 อย่าง: สไตล์ภาพ svStyle · ข้อความบนจอ svTextOn · เสียง svAudio · เสียงพากย์ svVoice
(ความยาว/ความละเอียดไม่ทำรายงาน — svSec/svRes คุมจำนวน op ทั้งสายระดับโปรเจกต์ (op.when) · engine 1.22 ไม่มี loopGenApplies ⇒ ทำรายงานไม่ได้อย่างปลอดภัย)
ทางไหลของค่า (บทเรียนห้อง: ตัวเลือกที่ต้องถึงคลิปย่อย = ฟิลด์สินค้า + spawn {parent.fields.X} + tasks.fields):
  - mnPlan (over products): {values.X} → cond(own=true และ ownX≠'' → {item.ownX} · อื่น → {values.X})
  - mnQueue spawn: eX = cond(own=true และ ownX≠'' → ownX · อื่น → '') ⇒ งานย่อยที่ไม่เปิดสวิตช์ = '' = อ่านค่ากลางสดเหมือนเดิมทุกไบต์
  - op งานย่อย (mnFace/mnBoard*/mnVideo*/mnCover · prompt/refs/model): {values.X} → cond(eX='' → {values.X} · อื่น → {item.eX})
    when แบบข้อความ "values.X=..." ในบล็อก → object eq (cond) · op.when ระดับโปรเจกต์ไม่แตะ
ใช้: python3 scripts/showhow-v145-per-product.py  (รันบน v144 · รันซ้ำ = ไม่ทำอะไร)
"""
import json, re, sys, copy
P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
s0 = open(P, encoding='utf-8').read()
c = json.loads(s0)
assert json.dumps(c, ensure_ascii=False, indent=1) + '\n' == s0
C = c['collections']; O = {o['id']: o for o in c['ops']}
if 'own' in C['products']['fields']:
    print('v145: ทำไปแล้ว — ไม่แตะ'); sys.exit(0)
MAP = {'svStyle': ('ownStyle', 'eStyle'), 'svTextOn': ('ownTextOn', 'eTextOn'), 'svAudio': ('ownAudio', 'eAudio'), 'svVoice': ('ownVoice', 'eVoice')}
eq = lambda a, b: {'op': 'eq', 'a': a, 'b': b}
NOT = lambda x: {'op': 'not', 'a': x}
AND = lambda *x: {'op': 'and', 'list': list(x)}
def own_ok(k, src): return AND(eq('{%s.own}' % src, 'true'), NOT(eq('{%s.%s}' % (src, MAP[k][0]), '')))
def PEFF(k): return {'op': 'cond', 'when': own_ok(k, 'item'), 'then': '{item.%s}' % MAP[k][0], 'else': '{values.%s}' % k}
def TEFF(k): return {'op': 'cond', 'when': eq('{item.%s}' % MAP[k][1], ''), 'then': '{values.%s}' % k, 'else': '{item.%s}' % MAP[k][1]}

C['products']['fields'] += ['own'] + [v[0] for v in MAP.values()]
C['products']['addDefaults']['own'] = ''
C['tasks']['fields'] += [v[1] for v in MAP.values()]
sp = O['mnQueue']['spawn']['fields']
for k, (pf, tf) in MAP.items():
    sp[tf] = {'op': 'cond', 'when': own_ok(k, 'parent.fields'), 'then': '{parent.fields.%s}' % pf, 'else': ''}

TOK = re.compile(r'\{values\.(%s)\}' % '|'.join(MAP))
SPRED = re.compile(r'^values\.(%s)\s*(!=|=)(.*)$' % '|'.join(MAP))
def conv(o, EFF, cnt):
    """แทน {values.X} ทุกที่ใน o (คืนค่าใหม่)"""
    if isinstance(o, str):
        if not TOK.search(o): return o
        cnt[0] += 1
        ps, last = [], 0
        for m in TOK.finditer(o):
            if m.start() > last: ps.append(o[last:m.start()])
            ps.append(EFF(m.group(1))); last = m.end()
        if last < len(o): ps.append(o[last:])
        return ps[0] if len(ps) == 1 else {'op': 'concat', 'parts': ps}
    if isinstance(o, list):
        out = []
        for x in o: out.append(conv(x, EFF, cnt))
        return out
    if isinstance(o, dict):
        n = {}
        for k, v in o.items():
            if k == 'when' and isinstance(v, str) and SPRED.match(v.strip()):
                m = SPRED.match(v.strip()); cnt[0] += 1
                e = eq(EFF(m.group(1)), m.group(3)); n[k] = e if m.group(2) == '=' else NOT(e)
            elif k == 'parts' and o.get('op') == 'concat' and isinstance(v, list):
                np_ = []
                for x in v:
                    y = conv(x, EFF, cnt)
                    if isinstance(y, dict) and y.get('op') == 'concat' and isinstance(x, str): np_ += y['parts']
                    else: np_.append(y)
                n[k] = np_
            else: n[k] = conv(v, EFF, cnt)
        return n
    return o
tot = {}
for o in c['ops']:
    if o['id'] == 'mnPlan': EFF = PEFF
    elif o.get('over') == 'tasks' and o.get('type') in ('image', 'video'): EFF = TEFF
    else: continue
    cnt = [0]
    for k in list(o.keys()):
        if k in ('id', 'when', 'where', 'over', 'type', 'out'): continue
        o[k] = conv(o[k], EFF, cnt)
    tot[o['id']] = cnt[0]
left = [o['id'] for o in c['ops'] if (o['id'] == 'mnPlan' or (o.get('over') == 'tasks' and o.get('type') in ('image', 'video')))
        and re.search(r'values\.(%s)\b' % '|'.join(MAP), json.dumps({k: v for k, v in o.items() if k not in ('when', 'where')}, ensure_ascii=False).replace('{values.', '§'))]
assert not left, left   # ไม่มี "values.X=..." แบบข้อความหลงเหลือ (ที่ยังอยู่ต้องอยู่ใน else ของ cond เป็น {values.X} เท่านั้น)

# ── UI: ต้นกลุ่ม "ปรับเฉพาะงานนี้" ──
F0 = c['phases'][0]['form'][0]['card'][0]['card'][3]
src = {}
def find(n):
    if isinstance(n, dict):
        if n.get('el') == 'grid-select' and n.get('field') in MAP and n['field'] not in src: src[n['field']] = n
        for v in n.values(): find(v)
    elif isinstance(n, list):
        for v in n: find(v)
find(F0); assert set(src) == set(MAP), src.keys()
LBL = "!text-[13px] @[640px]:!text-[12.5px] opacity-60 px-0.5 mt-1"
HINT = "!text-[13px] @[640px]:!text-[12.5px] opacity-50 px-0.5 leading-snug"
TITLE = {'svStyle': 'สไตล์ภาพ', 'svTextOn': 'ข้อความบนจอ', 'svAudio': 'เสียง', 'svVoice': 'เสียงพากย์'}
items = []
for k in MAP:
    g = copy.deepcopy(src[k]); g['field'] = MAP[k][0]; g.pop('when', None)
    g['options'] = [{'value': '', 'label': 'ตามค่ากลาง', 'desc': 'ใช้ค่าหน้าตั้งค่า', 'icon': 'sync'}] + [o for o in g['options'] if o.get('value') != '']
    items += [{'el': 'text', 'value': TITLE[k], 'className': LBL}, g]
    if k == 'svVoice': items[-2]['when'] = items[-1]['when'] = eq('{item.ownAudio}', 'มีเสียงพากย์')
group = c['phases'][0]['form'][2]['card'][0]['card'][0]['card'][6]
assert group['head'][1]['value'] == 'ปรับเฉพาะงานนี้'
own_box = {'el': 'box', 'className': 'flex flex-col gap-1.5 rounded-2xl border border-[var(--ev-border)] p-3', 'card': [
    {'el': 'switch', 'field': 'own', 'label': 'ใช้ค่าของงานนี้แทนค่ากลาง', 'placeholder': 'สไตล์ภาพ · ข้อความบนจอ · เสียง · เสียงพากย์'},
    {'el': 'text', 'value': 'ปิดอยู่ = งานนี้ใช้ค่าจากหน้าตั้งค่า · ความยาวคลิปและความละเอียดใช้ค่ากลางเสมอ', 'className': HINT, 'when': NOT(eq('{item.own}', 'true'))},
    {'el': 'box', 'className': 'flex flex-col gap-1.5', 'when': eq('{item.own}', 'true'), 'card': [
        {'el': 'text', 'value': 'ค่าด้านล่างใช้กับงานนี้งานเดียว — ว่าง = ตามค่ากลาง', 'className': HINT}, *items]}]}
group['card'].insert(0, own_box)
print('✅ v145: own + 4 ค่า ·', ' '.join(f'{k}:{v}' for k, v in tot.items() if v))
open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
