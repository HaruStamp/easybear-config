#!/usr/bin/env python3
# minimal-v63-own-product-settings.py — พี่หมีสั่ง 26 พ.ย. 2569 (อัปเดตใหญ่ ข้อ 7 "ตั้งค่าเฉพาะสินค้าเหมือนแอปแฟชั่น") · แก้ minimal-dev.json อย่างเดียว · รันซ้ำได้
#  แบบ fashion E20: สวิตช์ "ตั้งค่าเฉพาะสินค้านี้" (products.own = "true") ในหน้าเพิ่ม/แก้สินค้า · ปิด = ค่ากลางหน้าตั้งค่า (พฤติกรรมเดิมทุกไบต์)
#  เปิด = เลือกได้ 4 อย่าง (ว่าง = ตามค่ากลาง):
#    pSell  สไตล์การขาย (svSell)   → sys ของ mnPlan
#    pPres  การนำเสนอ (svPres1)    → prompt+sys ของ mnPlan · "auto" = อัตโนมัติ (ค่าว่างของ svPres1)
#    pImgModel โมเดลภาพ (imageModel) → model ของ mnBoard*/mnCover (ผ่าน tasks.pImgModel)
#    pVidModel โมเดลวิดีโอ (svModel)  → model + resolution ของ mnVideo* (ผ่าน tasks.pVidModel)
#  ไม่ทำรายสินค้า (ตั้งใจ): ความยาวคลิป/แนวคลิป/เสียง/ข้อความ = อยู่ใน prompt วิดีโอ+บอร์ด ที่ต้อง gate ด้วย values ล้วน (ยาม ④ + ตัววัด 3,900)
#    และผังช่วง 2/3 (where svSec) · จำนวนคลิป = ทั้งหน้าคำนวณ สินค้า×clipsPerProduct (นับความคืบหน้า/เสร็จ) → ต้องรื้อหลายสิบจุด
#  ⚠ ไม่เพิ่มคีย์ใน collections.products.fields (ยาม cross-app-load: products ต้องตรง hardsell-dev ทุกไบต์ · ห้อง hardsell กำลังแก้อยู่)
#    engine ไม่กรองฟิลด์ที่ไม่ประกาศ (ฟอร์ม/เซฟ/โหลด/spawn ใช้ได้) — ข้อเสียเดียว: eb_item_update ของ gateway ปฏิเสธฟิลด์นี้ (ทดสอบผ่าน UI)
#    tasks.fields เพิ่ม pImgModel/pVidModel + spawn {parent.fields.X} (บทเรียนห้อง: ไม่งั้นค่าหายเงียบ)
#  ใช้ block ไม่ใช้ cond ใน prompt (ยาม clamp/leaf-length รัน engine เปล่าที่ไม่รู้จัก cond)
import json, sys, copy

P = sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json'
c = json.load(open(P, encoding='utf-8'))
ops = {o['id']: o for o in c['ops']}
def eq(a, b): return {'op': 'eq', 'a': a, 'b': b}
def NOT(x): return {'op': 'not', 'a': x}
def AND(*xs): return {'op': 'and', 'list': list(xs)}
def blk(*pairs): return {'op': 'block', 'sep': '', 'parts': [{'when': w, 'value': v} for w, v in pairs]}
OWN = eq('{item.own}', 'true')
POWN = eq('{parent.fields.own}', 'true')

# ── บริบทสินค้า (mnPlan · item = สินค้า) ──
def EFF(f, v, auto=False):
    if not auto:
        on = AND(OWN, NOT(eq('{item.%s}' % f, '')))
        return blk((on, '{item.%s}' % f), (NOT(on), '{values.%s}' % v))
    on = AND(OWN, NOT(eq('{item.%s}' % f, '')), NOT(eq('{item.%s}' % f, 'auto')))
    au = AND(OWN, eq('{item.%s}' % f, 'auto'))
    return blk((on, '{item.%s}' % f), (au, ''), (AND(NOT(on), NOT(au)), '{values.%s}' % v))
PLAN_MAP = {'{values.svSell}': EFF('pSell', 'svSell'), '{values.svPres1}': EFF('pPres', 'svPres1', auto=True)}

def pieces(s):
    out, i = [], 0
    while True:
        hits = [(s.find(t, i), t) for t in PLAN_MAP if s.find(t, i) >= 0]
        if not hits: break
        j, t = min(hits)
        if j > i: out.append(s[i:j])
        out.append(copy.deepcopy(PLAN_MAP[t])); i = j + len(t)
    if i < len(s): out.append(s[i:])
    return out
n_plan = 0
def wrap(n):
    global n_plan
    if isinstance(n, dict):
        for k, v in list(n.items()):
            if isinstance(v, str) and any(t in v for t in PLAN_MAP):
                ps = pieces(v); n[k] = ps[0] if len(ps) == 1 else {'op': 'concat', 'parts': ps}; n_plan += 1
            elif k == 'parts' and isinstance(v, list) and n.get('op') == 'concat':
                nl = []
                for x in v:
                    if isinstance(x, str) and any(t in x for t in PLAN_MAP): nl += pieces(x); n_plan += 1
                    else: wrap(x); nl.append(x)
                n[k] = nl
            else: wrap(v)
    elif isinstance(n, list):
        for i, x in enumerate(n):
            if isinstance(x, str) and any(t in x for t in PLAN_MAP):
                ps = pieces(x); n[i] = ps[0] if len(ps) == 1 else {'op': 'concat', 'parts': ps}; n_plan += 1
            else: wrap(x)
DONE_PLAN = '{item.pSell}' in json.dumps(ops['mnPlan'], ensure_ascii=False)   # รันซ้ำ = ข้าม (ไม่ห่อซ้ำ)
if not DONE_PLAN: wrap(ops['mnPlan'])
left = [t for t in PLAN_MAP if json.dumps(ops['mnPlan'], ensure_ascii=False).count('"%s"' % t) > json.dumps(ops['mnPlan'], ensure_ascii=False).count('"value": "%s"' % t)]
assert not left, ('mnPlan ยังอ่านค่ากลางตรง ๆ', left)

# ── งานคลิป (tasks) ──
T = c['collections']['tasks']
for f in ('pImgModel', 'pVidModel'):
    if f not in T['fields']: T['fields'].append(f)
sp = ops['mnQueue']['spawn']['fields']
for f in ('pImgModel', 'pVidModel'):
    on = AND(POWN, NOT(eq('{parent.fields.%s}' % f, '')))
    sp[f] = blk((on, '{parent.fields.%s}' % f))
def EFFT(f, v):
    on = NOT(eq('{item.%s}' % f, ''))
    return blk((on, '{item.%s}' % f), (NOT(on), '{values.%s}' % v))
n_task = 0
def sub(n, tok, rep):
    global n_task
    if isinstance(n, dict):
        for k, v in list(n.items()):
            if v == tok: n[k] = copy.deepcopy(rep); n_task += 1
            else: sub(v, tok, rep)
    elif isinstance(n, list):
        for i, v in enumerate(n):
            if v == tok: n[i] = copy.deepcopy(rep); n_task += 1
            else: sub(v, tok, rep)
for o in ('mnBoard', 'mnBoard2', 'mnBoard3', 'mnCover'):
    if 'pImgModel' in json.dumps(ops[o]['model']): continue
    sub(ops[o]['model'], '{values.imageModel}', EFFT('pImgModel', 'imageModel'))
for o in ('mnVideo', 'mnVideo2', 'mnVideo3'):
    if 'pVidModel' in json.dumps(ops[o]['model']): continue
    sub(ops[o]['model'], '{values.svModel}', EFFT('pVidModel', 'svModel'))
    sub(ops[o].get('resolution'), '{values.svModel}', EFFT('pVidModel', 'svModel'))
for o in ('mnBoard', 'mnBoard2', 'mnBoard3', 'mnCover', 'mnVideo', 'mnVideo2', 'mnVideo3'):
    s = json.dumps({k: ops[o].get(k) for k in ('model', 'resolution')}, ensure_ascii=False)
    assert '"{values.imageModel}"' not in s.replace('"value": "{values.imageModel}"', '') and '"{values.svModel}"' not in s.replace('"value": "{values.svModel}"', ''), o
print('mnPlan', n_plan, 'จุด · model/resolution', n_task, 'จุด')

# ── UI: การ์ด "ตั้งค่าเฉพาะสินค้านี้" ในหน้าเพิ่ม/แก้สินค้า (ก่อนแถวปุ่มล่าง) ──
def find_field(n, f):
    if isinstance(n, dict):
        if n.get('field') == f: return n
        for v in n.values():
            r = find_field(v, f)
            if r: return r
    elif isinstance(n, list):
        for v in n:
            r = find_field(v, f)
            if r: return r
form0 = c['phases'][0]['form'][0]
SAME = {'value': '', 'label': 'ตามค่ากลาง', 'desc': 'ใช้ค่าหน้าตั้งค่า', 'icon': 'sync'}
LBL = '!text-[13.5px] @[640px]:!text-[13px] font-bold opacity-70'
HINT = '!text-[12.5px] leading-snug opacity-60'
sell = copy.deepcopy(find_field(form0, 'svSell')); sell['field'] = 'pSell'; sell['options'] = [SAME] + sell['options']
pres = copy.deepcopy(find_field(form0, 'svPres1')); pres['field'] = 'pPres'; pres['placeholder'] = 'ตามค่ากลาง'
assert pres['options'][0]['value'] == ''
pres['options'] = [dict(SAME), dict(pres['options'][0], value='auto')] + pres['options'][1:]
imgm = copy.deepcopy(find_field(form0, 'imageModel')); imgm['field'] = 'pImgModel'; imgm['options'] = [dict(SAME)] + imgm['options']; imgm['placeholder'] = 'ตามค่ากลาง'
vidm = copy.deepcopy(find_field(form0, 'svModel')); vidm['field'] = 'pVidModel'; vidm['options'] = [dict(SAME)] + vidm['options']; vidm['cols'] = 3; vidm['mobile'] = {'cols': 1}
def sec(title, icon, el, hint=None):
    card = [{'el': 'text', 'value': title, 'icon': icon, 'className': LBL}, el]
    if hint: card.append({'el': 'text', 'value': hint, 'className': HINT})
    return {'el': 'box', 'className': 'flex flex-col gap-1.5', 'card': card}
CUR = {'op': 'concat', 'parts': ['ตอนนี้ใช้ค่ากลาง: สไตล์การขาย ', '{values.svSell}', ' · การนำเสนอ ',
                                 blk((eq('{values.svPres1}', ''), 'อัตโนมัติ'), (NOT(eq('{values.svPres1}', '')), '{values.svPres1}')),
                                 ' · ภาพ ', '{values.imageModel}', ' · วิดีโอ ', '{values.svModel}']}
OWN_CARD = {'el': 'box', 'id': 'mnOwn', 'className': 'bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-2xl p-3 @[420px]:p-4 @[640px]:p-5 flex flex-col gap-3.5', 'card': [
    {'el': 'switch', 'field': 'own', 'icon': 'tune', 'label': 'ตั้งค่าเฉพาะสินค้านี้', 'placeholder': 'สไตล์การขาย · การนำเสนอ · โมเดลภาพ · โมเดลวิดีโอ'},
    {'el': 'text', 'value': CUR, 'className': HINT, 'when': 'item.own!=true'},
    {'el': 'box', 'className': 'flex flex-col gap-3.5', 'when': 'item.own=true', 'card': [
        {'el': 'text', 'value': 'ค่าด้านล่างใช้กับสินค้านี้ตัวเดียว — เว้น "ตามค่ากลาง" = ใช้ค่าหน้าตั้งค่า · สินค้าอื่นไม่เปลี่ยน', 'className': HINT},
        sec('สไตล์การขาย', 'campaign', sell),
        sec('การนำเสนอสินค้า', 'view_in_ar', pres),
        sec('โมเดลภาพ (สตอรีบอร์ด · ปก)', 'image', imgm, 'มีข้อความบนภาพ ระบบใช้ Nano Banana Pro ให้อัตโนมัติ'),
        sec('โมเดลวิดีโอ', 'movie', vidm),
        {'el': 'text', 'value': 'ความยาวคลิป จำนวนคลิป ตัวละคร เสียง ข้อความ ตั้งที่หน้าตั้งค่า (ใช้กับทุกสินค้า) · เปลี่ยนค่าหลังเขียนบทแล้ว ให้กดคิดบทใหม่ของสินค้านี้', 'icon': 'info', 'className': HINT},
    ]},
]}
inner = c['phases'][0]['form'][2]['card'][0]['card'][0]
if not any(x.get('id') == 'mnOwn' for x in inner['card']):
    assert inner['card'][-1]['el'] == 'row' and inner['card'][-2]['el'] == 'group', 'หน้าแก้สินค้าเปลี่ยนผัง — ปรับสคริปต์ก่อน'
    inner['card'].insert(len(inner['card']) - 1, OWN_CARD)

open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=2))
print('ok', P)
