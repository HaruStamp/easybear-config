#!/usr/bin/env python3
# hardsell-dev v33: ตั้งค่าเฉพาะสินค้า (เจ้าของสั่ง 26 พ.ย. ข้อ 5/15 · ลอกท่า fashion E20 `own` + cond item/values)
#   ค่ากลาง = หน้าตั้งค่าเหมือนเดิม · หน้าแก้ไขสินค้ามีสวิตช์ "ตั้งค่าเฉพาะสินค้านี้" (products.own = "true")
#   เปิดสวิตช์ + เลือกค่า (ว่าง = ตามค่ากลาง) → สินค้านี้ใช้ค่าของตัวเอง 6 อย่าง:
#     เทมเพลต templateId · โทน toneId · ความยาว svSec · ฉากหลัง svBg · ท่า svPose · โมเดลรูป imageModel
#   ทางไหลของค่า (บทเรียนห้อง: ตัวเลือกที่ต้องถึงคลิปย่อย = ฟิลด์สินค้า + spawn {parent.fields.X} + tasks.fields)
#     - mnPlan (over products): ทุก {values.X} → cond(own=true และ ownX≠'' → {item.ownX} · อื่น → {values.X})
#     - mnQueue spawn เขียนลงงานย่อย: eSec = ความยาวจริง ณ ตอนจัดคิว (เสมอ — บทถูกเขียนตามความยาวนี้แล้ว)
#       eTpl/eTone/eBg/ePose/eImg = ค่าของสินค้าเมื่อเปิดสวิตช์ · ไม่เปิด = '' (งานย่อยตามค่ากลางสด เหมือนเดิมทุกไบต์)
#     - op งานย่อย (mnBoard/mnVideo/mnVideo2/mnCover) + การ์ดหน้าผลิต: {values.X} → cond(item.eX='' → {values.X} · อื่น → {item.eX})
#     - mnVideo2 เดิม when 'values.svSec>10' (ระดับ op ไม่มี item) → where ['s5en!=', 'eSec>10'] (ตัดสินรายคลิป แบบ fashion secAt)
#       🪤 งานย่อยที่จัดคิวก่อน v33 ไม่มี eSec ⇒ ช่วง 2 ไม่รัน — คิดบทใหม่/จัดคิวใหม่ (dev เท่านั้น)
#   ความยาว 10/20 ใช้ได้เฉพาะ Omni: สินค้าตั้ง 10/20 แต่ตอนนี้เลือก Veo = กลับไปใช้ค่ากลาง
#   products.fields ไม่แตะ (ยาม cross-app-load บังคับให้ตรง minimal-dev ทุกไบต์ · ช่องที่ฟอร์มใช้ engine นับเป็น usedFields อยู่แล้ว)
# ใช้: python3 scripts/hardsell-v33-per-product.py [hardsell-dev.json]   (รันบน v32 · รันซ้ำ = ไม่ทำอะไร)
import json, re, sys, copy
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F, encoding='utf-8'))
L = d['lookups']
ops = {o['id']: o for o in d['ops']}
T = d['collections']['tasks']
if 'eSec' in T['fields']:
    print('v33: ทำไปแล้ว — ไม่แตะ'); sys.exit(0)

#        values key    ฟิลด์สินค้า   ฟิลด์งานย่อย
MAP = {'templateId': ('ownTpl', 'eTpl'), 'toneId': ('ownTone', 'eTone'), 'svSec': ('ownSec', 'eSec'),
       'svBg': ('ownBg', 'eBg'), 'svPose': ('ownPose', 'ePose'), 'imageModel': ('ownImg', 'eImg')}
eq = lambda a, b: {'op': 'eq', 'a': a, 'b': b}
ne = lambda a, b: {'op': 'not', 'a': eq(a, b)}
AND = lambda *x: {'op': 'and', 'list': list(x)}
OR = lambda *x: {'op': 'or', 'list': list(x)}
OMNI = {'op': 'contains', 'a': '{values.videoModel}', 'b': 'Omni'}

def own_ok(k, src):   # src = 'item' (สินค้า) | 'parent.fields' (ตอน spawn)
    f = '{%s.%s}' % (src, MAP[k][0])
    c = [eq('{%s.own}' % src, 'true'), ne(f, '')]
    if k == 'svSec': c.append(OR(OMNI, eq(f, '8'), eq(f, '16')))
    return AND(*c)
def PEFF(k, src='item'):
    return {'op': 'cond', 'when': own_ok(k, src), 'then': '{%s.%s}' % (src, MAP[k][0]), 'else': '{values.%s}' % k}
def TEFF(k):
    e = '{item.%s}' % MAP[k][1]
    return {'op': 'cond', 'when': eq(e, ''), 'then': '{values.%s}' % k, 'else': e}

TOK = re.compile(r'\{values\.(%s)\}' % '|'.join(MAP))
SCOND = re.compile(r'^values\.(%s)(!=|>=|<=|>|<|=)(.*)$' % '|'.join(MAP))
CMP = {'>': 'gt', '<': 'lt', '>=': 'gte', '<=': 'lte'}
n = {'tok': 0, 'cond': 0}

def pieces(s, eff):
    out, last = [], 0
    for m in TOK.finditer(s):
        if m.start() > last: out.append(s[last:m.start()])
        out.append(eff(m.group(1))); last = m.end()
    if last < len(s): out.append(s[last:])
    n['tok'] += 1
    return out
def scond(s, eff):
    m = SCOND.match(s); k, op, rhs = m.groups(); n['cond'] += 1
    if op == '=': return eq(eff(k), rhs)
    if op == '!=': return ne(eff(k), rhs)
    return {'op': CMP[op], 'a': eff(k), 'b': rhs}

def tr(o, eff, key=None):
    """คืน object ใหม่ · ไม่เดินเข้าไปในค่าที่เพิ่งแทน (กันห่อซ้ำ)"""
    if isinstance(o, str):
        if key in ('when', 'disabledWhen') and SCOND.match(o): return scond(o, eff)
        if TOK.search(o):
            ps = pieces(o, eff); return ps[0] if len(ps) == 1 else {'op': 'concat', 'parts': ps}
        return o
    if isinstance(o, list):
        return [tr(x, eff) for x in o]
    if isinstance(o, dict):
        out = {}
        for k_, v_ in o.items():
            if k_ == 'parts' and o.get('op') == 'concat' and isinstance(v_, list):
                nl = []
                for x in v_:
                    if isinstance(x, str) and TOK.search(x): nl += pieces(x, eff)
                    else: nl.append(tr(x, eff))
                out[k_] = nl
            else: out[k_] = tr(v_, eff, k_)
        return out
    return o

# ── op ──
v2 = ops['mnVideo2']
assert v2.get('when') == 'values.svSec>10' and v2.get('where') == 's5en!=', (v2.get('when'), v2.get('where'))
del v2['when']; v2['where'] = ['s5en!=', 'eSec>10']
for i, o in enumerate(d['ops']):
    if o['id'] == 'mnPlan': d['ops'][i] = tr(o, PEFF)
    elif o.get('over') == 'tasks': d['ops'][i] = tr(o, TEFF)
ops = {o['id']: o for o in d['ops']}

# ── spawn → งานย่อย ──
sp = ops['mnQueue']['spawn']['fields']
for k, (pf, tf) in MAP.items():
    sp[tf] = PEFF(k, 'parent.fields') if k == 'svSec' else {'op': 'cond', 'when': own_ok(k, 'parent.fields'), 'then': '{parent.fields.%s}' % pf, 'else': ''}
    if tf not in T['fields']: T['fields'].append(tf)

# ── UI: การ์ดงานย่อย (repeat tasks) ──
def ui(o):
    if isinstance(o, dict):
        if o.get('el') == 'repeat' and o.get('coll') == 'tasks':
            o['card'] = tr(o['card'], TEFF); return
        for v_ in o.values(): ui(v_)
    elif isinstance(o, list):
        for x in o: ui(x)
ui(d['phases'])

# ── UI: หน้าแก้ไขสินค้า — สวิตช์ + ตัวเลือก ──
S = d['phases'][0]['form'][0]['card'][0]   # หน้าตั้งค่า (ยืมตัวเลือก)
def find_field(root, field):
    hit = []
    def w(o):
        if isinstance(o, dict):
            if o.get('field') == field and o.get('options'): hit.append(o)
            for v_ in o.values(): w(v_)
        elif isinstance(o, list):
            for x in o: w(x)
    w(root); return hit
CAT = {'ugc': 'UGC', 'style': 'สไตล์', 'd3': '3D'}
tpl_opts = []
for g in find_field(S, 'templateId'):
    cat = re.match(r'^values\.styleCat=(\w+)$', g.get('when', '')).group(1)
    tpl_opts += [{'value': x['value'], 'label': CAT[cat] + ' · ' + x['label']} for x in g['options']]
assert len(tpl_opts) == len(L['tplScene']) == len({x['value'] for x in tpl_opts}), (len(tpl_opts), len(L['tplScene']))
def plain(field):
    return [{k: x[k] for k in ('value', 'label', 'desc', 'icon') if k in x} for x in find_field(S, field)[0]['options']]
CENTRAL = {'value': '', 'label': 'ตามหน้าตั้งค่า', 'desc': 'ค่ากลาง', 'icon': 'settings'}
sec_omni = [x for x in find_field(S, 'svSec') if 'Omni' in json.dumps(x.get('when'))][0]['options']
LBL = '!text-[13.5px] @[640px]:!text-[13px] !text-[var(--ev-text)] opacity-65 uppercase tracking-[0.14em] font-black px-0.5'
HINT = '!text-[13px] @[640px]:!text-[12.5px] opacity-55 px-0.5 leading-snug'
GRID = '!min-h-[48px] @[420px]:!min-h-0'
def fld(label, el):
    return {'el': 'box', 'className': 'flex flex-col gap-2', 'card': [{'el': 'text', 'value': label, 'className': LBL}, el]}
def dd(field, opts):
    return {'el': 'dropdown', 'field': field, 'options': [{'value': '', 'label': 'ตามหน้าตั้งค่า'}] + opts, 'className': GRID}
def gs(field, opts, cols=3, mcols=2, when=None):
    g = {'el': 'grid-select', 'field': field, 'cols': cols, 'mobile': {'cols': mcols}, 'contained': True, 'className': GRID, 'options': [CENTRAL] + opts}
    if when is not None: g['when'] = when
    return g
OWN = eq('{item.own}', 'true')
TPL_P = PEFF('templateId')
LOOK = lambda tb: {'op': 'lookup', 'table': tb, 'key': copy.deepcopy(TPL_P), 'fallback': 'no'}
central_line = {'op': 'concat', 'parts': [
    'ตอนนี้ใช้ค่ากลางจากหน้าตั้งค่า: ', {'op': 'lookup', 'table': 'tplName', 'key': '{values.templateId}', 'fallback': '{values.templateId}'},
    ' · ', {'op': 'lookup', 'table': 'toneName', 'key': '{values.toneId}', 'fallback': '{values.toneId}'},
    ' · {values.svSec} วิ · {values.imageModel}']}
own_card = {'el': 'box', 'className': 'bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-2xl p-3 @[420px]:p-4 @[640px]:p-5 flex flex-col gap-3.5', 'card': [
    {'el': 'row', 'className': 'items-center gap-2 px-0.5', 'style': {'flexWrap': 'nowrap'}, 'card': [
        {'el': 'icon', 'icon': 'tune', 'textSize': 'text-[19px]', 'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center'},
        {'el': 'text', 'value': 'ตั้งค่าเฉพาะสินค้านี้', 'className': '!text-[18px] @[640px]:!text-[17px] font-black !text-[var(--ev-text)] leading-tight'},
        {'el': 'text', 'value': 'ไม่บังคับ', 'className': '!text-[12.5px] opacity-50 font-bold ml-auto whitespace-nowrap'}]},
    {'el': 'switch', 'field': 'own', 'label': 'ใช้ค่าของสินค้านี้แทนค่ากลาง', 'placeholder': 'เทมเพลต · โทน · ความยาว · ฉากหลัง · ท่า · โมเดลรูป'},
    {'el': 'text', 'value': central_line, 'className': HINT, 'when': ne('{item.own}', 'true')},
    {'el': 'box', 'className': 'flex flex-col gap-3', 'when': OWN, 'card': [
        {'el': 'text', 'value': 'ค่าด้านล่างใช้กับสินค้านี้ตัวเดียว · "ตามหน้าตั้งค่า" = ใช้ค่ากลาง · มีผลตอนคิดบทครั้งถัดไป (คลิปที่จัดคิวแล้วไม่เปลี่ยน)', 'className': HINT},
        fld('เทมเพลตคลิป', dd('ownTpl', tpl_opts)),
        fld('โทนการขาย', dd('ownTone', plain('toneId'))),
        fld('ความยาวคลิป', {'el': 'box', 'className': 'flex flex-col gap-1.5', 'card': [
            gs('ownSec', [{k: x[k] for k in ('value', 'label', 'desc') if k in x} for x in sec_omni], cols=5, mcols=2, when=OMNI),
            gs('ownSec', [{k: x[k] for k in ('value', 'label', 'desc') if k in x} for x in sec_omni if x['value'] in ('8', '16')], cols=3, mcols=3, when={'op': 'not', 'a': OMNI}),
            {'el': 'text', 'value': 'ตอนนี้เลือก Veo — สินค้าที่ตั้ง 10 / 20 วิ จะใช้ความยาวกลางแทน', 'className': HINT + ' font-bold !text-[var(--ev-accent)]',
             'when': AND({'op': 'not', 'a': OMNI}, OR(eq('{item.ownSec}', '10'), eq('{item.ownSec}', '20')))}]}),
        {'el': 'box', 'className': 'flex flex-col gap-2', 'when': eq(LOOK('tplBgOk'), 'yes'), 'card': [
            {'el': 'text', 'value': 'ฉากหลัง', 'className': LBL}, dd('ownBg', plain('svBg'))]},
        {'el': 'box', 'className': 'flex flex-col gap-2', 'when': eq(LOOK('tplChar'), 'yes'), 'card': [
            {'el': 'text', 'value': 'ท่านำเสนอสินค้า', 'className': LBL}, dd('ownPose', plain('svPose'))]},
        fld('โมเดลสร้างภาพ', dd('ownImg', plain('imageModel'))),
        {'el': 'text', 'value': 'มีข้อความบนภาพ ระบบใช้ Nano Banana Pro ให้อัตโนมัติ', 'className': HINT, 'when': ne('{values.svTextOn}', 'ไม่มีข้อความ')}]}]}
prod = d['phases'][0]['form'][2]['card'][0]['card'][0]['card']
foot = next(i for i, x in enumerate(prod) if x.get('el') == 'row' and 'edit-cancel' in json.dumps(x) and 'ยกเลิก' in json.dumps(x, ensure_ascii=False))
prod.insert(foot, own_card)

# ── UI: รายการสินค้า — ป้าย "ตั้งค่าเฉพาะ" ──
lst = d['phases'][0]['form'][1]['card'][2]['card'][2]['card'][1]
assert lst.get('el') == 'repeat' and lst.get('coll') == 'products'
namerow = lst['card'][0]['card'][2]['card'][0]
assert '{item.name}' in json.dumps(namerow, ensure_ascii=False)
namerow['card'].append({'el': 'text', 'value': 'ตั้งค่าเฉพาะ', 'icon': 'tune', 'when': 'item.own=true',
    'className': 'flex items-center gap-1 shrink-0 !text-[12px] @[640px]:!text-[11px] font-bold px-2 py-0.5 rounded-full bg-[var(--ev-surface2)] !text-[var(--ev-accent)] !whitespace-nowrap'})

# ── ตรวจปิดท้าย ──
def raw(o):   # {values.X} ที่ไม่ได้อยู่ใน else/then ของ cond ที่เราห่อ
    if isinstance(o, dict):
        if o.get('op') == 'cond' and isinstance(o.get('when'), dict):
            w = json.dumps(o['when'], ensure_ascii=False)
            if '.own}' in w or re.search(r'\{item\.e(Tpl|Tone|Sec|Bg|Pose|Img)\}', w): return 0
        return sum(raw(v_) for v_ in o.values())
    if isinstance(o, list): return sum(raw(x) for x in o)
    return 1 if isinstance(o, str) and (TOK.search(o) or SCOND.match(o)) else 0
for o in d['ops']:
    if o['id'] == 'mnPlan' or o.get('over') == 'tasks':
        assert raw(o) == 0, ('ยังอ่านค่ากลางตรง', o['id'])
print('v33: แทน', n['tok'], 'จุด · เงื่อนไขข้อความ', n['cond'], 'จุด · spawn 6 ช่อง · การ์ดตั้งค่าเฉพาะสินค้า')
open(F, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2))
