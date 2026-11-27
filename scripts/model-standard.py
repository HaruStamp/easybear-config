#!/usr/bin/env python3
"""model-standard.py — มาตรฐานโมเดลทุกแอป easybear (ต้นฉบับเดียวของ "บล็อกตั้งค่าโมเดล" · 27 พ.ย. 2569)
คำพี่หมี 27 พ.ย.:
  "ทำให้ทุกตัว รองรับ การเลือก omni flash 1.2 และ 360p มาตร และ โมเดลภาพ ฐานเดียวกัน"
  "ฝากทำต่อให้เสร็จ ทำให้ ทุกตัว มาตรฐานเดียวกัน โดน omni flash 1.1. ก็รองรับ 360p"
  "omni flash 1.1 แบบ 360p 10วิ จะใช้ 7 เครดิต"
  "ทำ ux/ui ตั้งค่าโมเดล วีดีโอ ความละเอียด แบบมาตรฐานเดียวกัน ให้สวย layout ข้อความใกล้เคียงกัน ใช้ pattern คล้ายๆกัน"

บล็อกเดียวกันทุกแอป (วางต่อจาก "ความยาวคลิป" ในส่วนการผลิต):
  โมเดลภาพ   — ปุ่ม 3 ช่องแถวเดียว Pro "ดีสุด" / 2.1 "มาตรฐาน" / 2 Lite "ประหยัด" + บรรทัด "มีข้อความไทย ใช้ Pro อัตโนมัติ"
  โมเดลวิดีโอ — ปุ่ม 2 ช่อง Omni 1.1 Flash / Omni 1.2 Flash (hardsell + Veo 3.1 Lite 2 ปุ่ม แบบเดียวกัน)
  ความละเอียด — ปุ่ม 2 ช่อง 720p / 360p (ทั้ง Omni 1.1 และ 1.2) + หมายเหตุเฉพาะแอป
  บรรทัดสรุป "ใช้ X เครดิต ต่อคลิป · รุ่น · ความละเอียด · ความยาว" คิดจากรุ่น+ความละเอียด+ความยาวจริง
  เครดิต/10 วิ: Omni 1.1 720p 15 · 360p 7 · Omni 1.2 720p 30 · 360p 10
กติกา: ค่า/คีย์/ค่าเริ่มเดิมทุกตัว (ตัวขาย Omni 1.1 · dev ตามเดิม) ⇒ คำขอที่ค่าเริ่มเท่าเดิมทุกไบต์ (พิสูจน์ model-standard-proof.ts)
       · Omni 1.2 ไม่เป็นค่าเริ่มตัวขายจนพี่หมีกำหนดวัน · ไม่แตะราคาขาย/ข้อความขาย
       · Veo 3.1 Fast/Quality (Flow เลิก 5 ธ.ค.) ถอดจากตัวเลือก ค่าเก่าที่เซฟไว้แปลงเป็น Veo 3.1 - Lite ตอนส่ง (ท่า flowModelPatch)

ใช้:  python3 scripts/model-standard.py <app> <ไฟล์ config>   (แก้ในที่ · app = minimal|fashion|hardsell|showhow|podcast|petdance|parody)
      build-podcast/petdance/parody/fashion เรียก apply(app, c) ท้าย build (ต้นฉบับเดียว)
"""
import copy, json, re, sys

V11, V12 = 'Omni 1.1 Flash', 'Omni 1.2 Flash'
PRO, NB21, LITE = '🍌 Nano Banana Pro', '🍌 Nano Banana 2.1', '🍌 Nano Banana 2 Lite'
IMG_ORDER = [PRO, NB21, LITE]
VEO_LITE, VEO_LITE_LP, VEO_FAST, VEO_Q = 'Veo 3.1 - Lite', 'Veo 3.1 - Lite [Lower Priority]', 'Veo 3.1 - Fast', 'Veo 3.1 - Quality'
PRICE = {V11: {'720p': 15, '360p': 7}, V12: {'720p': 30, '360p': 10}}
TEXT_NONE = 'ไม่มีข้อความ'
HINT_IMG = 'มีข้อความไทย ใช้ Pro อัตโนมัติ'   # พี่หมี 27 พ.ย.: "ปรับคำอธิบาย โมเดล nano banana pro ให้สั้นกระชับกว่านี้"


def eq(a, b): return {'op': 'eq', 'a': a, 'b': b}
def NOT(x): return {'op': 'not', 'a': x}
def AND(*xs): return {'op': 'and', 'list': list(xs)}
def OR(*xs): return {'op': 'or', 'list': list(xs)}
def cond(w, t, e): return {'op': 'cond', 'when': w, 'then': t, 'else': e}
def D(x): return copy.deepcopy(x)
IS12 = eq('{values.svModel}', V12)
IS360 = eq('{values.svRes}', '360p')


def walk_lists(o, fn):
    if isinstance(o, dict):
        for v in o.values(): walk_lists(v, fn)
    elif isinstance(o, list):
        for i, v in enumerate(list(o)):
            if isinstance(v, dict): fn(o, i, v)
            walk_lists(v, fn)


def find_all(o, pred):
    out = []
    walk_lists(o, lambda L, i, n: out.append((L, n)) if pred(n) else None)
    return out


def parent_of(root, node):
    hit = []
    walk_lists(root, lambda L, i, n: hit.append(L) if n is node else None)
    assert len(hit) == 1, len(hit)
    return hit[0]


def box_holding(root, node):
    hit = find_all(root, lambda n: isinstance(n.get('card'), list) and any(x is node for x in n['card']))
    assert len(hit) == 1, len(hit)
    return hit[0][1]


def idx(L, node): return next(k for k, x in enumerate(L) if x is node)
def remove(root, node): L = parent_of(root, node); del L[idx(L, node)]
def grids(root, field): return [n for _, n in find_all(root, lambda x: x.get('el') in ('grid-select', 'dropdown') and x.get('field') == field)]
def remove_boxes(root, field):
    bs = []
    for g in grids(root, field):
        b = box_holding(root, g)
        if not any(x is b for x in bs): bs.append(b)
    for b in bs: remove(root, b)
    return len(bs)


def video_ops(c): return [o for o in c['ops'] if o.get('type') == 'video']


def setup(c):
    """หน้าตั้งค่า = phases[0].form[0] (ทุกแอป engine)"""
    return c['phases'][0]['form'][0]


def save_value(c, key):
    g = [x for x in c.get('saveGroups', []) if x.get('id') == 'setup']
    assert len(g) == 1
    vals = g[0]['values']
    if key in vals or any(v.endswith('*') and key.startswith(v[:-1]) for v in vals): return
    vals.append(key)


# ───────────────────────── บล็อกมาตรฐาน (หน้าตาเดียวกันทุกแอป) ─────────────────────────
HEAD_ROW = 'items-center !gap-1.5 px-0.5'
HEAD_ICON = '!text-[var(--ev-accent)] leading-none flex items-center justify-center opacity-80 shrink-0'
HEAD_TEXT = '!text-[13px] @[640px]:!text-[12.5px] !text-[var(--ev-text)] opacity-65 uppercase tracking-[0.14em] font-black px-0.5 !px-0'
# ปุ่ม: เลือก = เติมสีหลักของแอป (engine) · ไม่เลือก = เส้นขอบ · ชื่อตัวหนา + บรรทัดย่อย 1 บรรทัด
GRID_CLS = '!min-h-[48px] @[420px]:!min-h-0 [&_button]:border [&_button]:border-[var(--ev-border)] [&_button>span:first-of-type]:font-bold [&_button>span:first-of-type]:!text-[15px]'
NOTE_CLS = '!text-[12.5px] leading-snug opacity-60 px-0.5'
WARN_CLS = '!text-[12.5px] leading-snug !text-amber-600 px-0.5'


def head(icon, label):
    return {'el': 'row', 'className': HEAD_ROW, 'style': {'flexWrap': 'nowrap'}, 'card': [
        {'el': 'icon', 'icon': icon, 'textSize': 'text-[16px]', 'className': HEAD_ICON},
        {'el': 'text', 'value': label, 'className': HEAD_TEXT}]}


def grid(field, options, cols):
    return {'el': 'grid-select', 'field': field, 'cols': cols, 'mobile': {'cols': cols}, 'contained': True, 'className': GRID_CLS, 'options': options}


def note(text, when=None, warn=False):
    n = {'el': 'text', 'value': text, 'icon': 'warning' if warn else 'info', 'className': WARN_CLS if warn else NOTE_CLS}
    if when is not None: n['when'] = when
    return n


def section(icon, label, body, when=None):
    s = {'el': 'box', 'className': 'flex flex-col gap-1.5', 'card': [head(icon, label)] + body}
    if when is not None: s['when'] = when
    return s


IMG_OPTS = [{'value': PRO, 'label': 'Pro', 'desc': 'ดีสุด', 'icon': 'auto_awesome'},
            {'value': NB21, 'label': '2.1', 'desc': 'มาตรฐาน', 'icon': 'image'},
            {'value': LITE, 'label': '2 Lite', 'desc': 'ประหยัด', 'icon': 'bolt'}]
VID_OPTS = [{'value': V11, 'label': 'Omni 1.1 Flash', 'desc': '15 เครดิต/10 วิ'},
            {'value': V12, 'label': 'Omni 1.2 Flash', 'desc': '30 เครดิต/10 วิ'}]
RES_OPTS = [{'value': '720p', 'label': '720p', 'desc': 'ชัด · ลง Shopee ได้'},
            {'value': '360p', 'label': '360p', 'desc': 'ประหยัด · Shopee ไม่รับ'}]


def summary(vfield, eff360, sec, omni=None):
    """บรรทัดสรุปเครดิต (กล่องเดียวกับ minimal) — คิดจากรุ่น + ความละเอียดที่ส่งจริง + ความยาว"""
    is12 = eq('{values.%s}' % vfield, V12)
    per10 = cond(D(eff360), cond(D(is12), PRICE[V12]['360p'], PRICE[V11]['360p']), cond(D(is12), PRICE[V12]['720p'], PRICE[V11]['720p']))
    n = {'op': 'round', 'value': {'op': 'mul', 'a': per10, 'b': {'op': 'div', 'a': D(sec), 'b': '10'}}}
    txt = {'op': 'concat', 'parts': ['ใช้ ', n, ' เครดิต ต่อคลิป · ', cond(D(is12), 'Omni 1.2', 'Omni 1.1'), ' · ',
                                     cond(D(eff360), '360p', '720p'), ' · ', D(sec), ' วิ']}
    box = {'el': 'box', 'className': 'flex flex-row items-center gap-2 rounded-2xl px-3 py-2.5 bg-[var(--ev-accent)]/[0.08] border border-[var(--ev-accent)]/25',
           'card': [{'el': 'icon', 'icon': 'toll', 'textSize': 'text-[18px]', 'className': '!text-[var(--ev-accent)] leading-none flex items-center shrink-0'},
                    {'el': 'text', 'className': '!text-[14px] leading-snug !text-[var(--ev-text)]', 'value': txt}]}
    if omni is not None: box['when'] = omni
    return box


def std_block(*, vfield='svModel', vid_opts=None, res_when=None, res_notes=(), eff360=None, sec='{values.svSec}', extra_summary=None, omni=None):
    eff360 = eff360 if eff360 is not None else D(IS360)
    card = [section('image', 'โมเดลภาพ', [grid('imageModel', D(IMG_OPTS), 3), note(HINT_IMG)]),
            section('movie', 'โมเดลวิดีโอ', [grid(vfield, D(vid_opts or VID_OPTS), 2)]),
            section('high_quality', 'ความละเอียด', [grid('svRes', D(RES_OPTS), 2)] + list(res_notes), when=res_when),
            summary(vfield, eff360, sec, omni)]
    if extra_summary: card.append(extra_summary)
    return {'el': 'box', 'className': 'flex flex-col gap-3 eb-model-std', 'card': card}   # eb-model-std = ป้ายให้ยามหาบล็อก (ไม่มีสไตล์)


SEC_CREDIT = re.compile(r'^(ใช้ \d+ เครดิต( \(360p \d+\))?|720p \d+ · 360p \d+ เครดิต)$')


def strip_sec_credits(c):
    """ป้ายใต้ปุ่มความยาวที่บอกเครดิต (เลขของรุ่นเดียว) → ย้ายไปบรรทัดสรุปของบล็อก"""
    n = 0
    for g in grids(setup(c), 'svSec'):
        if all(SEC_CREDIT.match(o.get('desc') or '') for o in g['options']):
            for o in g['options']: o.pop('desc'); n += 1
    return n


def insert_after(c, anchor, node):
    L = parent_of(setup(c), anchor); L.insert(idx(L, anchor) + 1, node)


def head_rows(root, labels):
    return [n for _, n in find_all(root, lambda x: x.get('el') == 'row' and any(isinstance(t, dict) and t.get('el') == 'text' and t.get('value') in labels for t in x.get('card', [])))]


# ───────────────────────── op: เลือกรุ่นวิดีโอ / ภาพ ─────────────────────────
def fixed_video_model(c):
    ms = {o['model'] for o in video_ops(c) if isinstance(o.get('model'), str)}
    assert len(ms) == 1 and ms <= {V11, V12} and all(isinstance(o.get('model'), str) for o in video_ops(c)), ms
    return ms.pop()


def add_video_model(c):
    cur = fixed_video_model(c)
    assert 'svModel' not in c['values']
    c['values']['svModel'] = cur
    for o in video_ops(c): o['model'] = cond(D(IS12), V12, V11)
    return cur


def image_ops_pick(c, ids_pick, ids_text, default):
    """ids_pick = ภาพไม่มีตัวหนังสือ → ตามที่เลือก · ids_text = บอร์ดที่อาจมีข้อความ → มีข้อความ = Pro"""
    assert 'imageModel' not in c['values']; c['values']['imageModel'] = default
    pick = {'op': 'coalesce', 'parts': ['{values.imageModel}'], 'default': default}
    for o in c['ops']:
        if o.get('type') != 'image': continue
        if o['id'] in ids_pick: o['model'] = D(pick)
        elif o['id'] in ids_text: o['model'] = cond(NOT(eq('{values.svTextOn}', TEXT_NONE)), PRO, D(pick))
    save_value(c, 'imageModel')


# ───────────────────────── สูตรรายแอป ─────────────────────────
def sec_box(c):
    g = grids(setup(c), 'svSec'); assert len(g) >= 1
    return box_holding(setup(c), g[0])


def std_podcast(c):
    S = setup(c)
    add_video_model(c)
    for o in video_ops(c): assert o.get('resolution') == '{values.svRes}', o['id']
    for f in ('svRes', 'imageModel'): remove_boxes(S, f)
    # ข้อความตอนยาว "ใช้ราว N เครดิต (360p ราว M)" = 60 วิ/คลิป ⇒ ×6
    hit = [n for _, n in find_all(c['phases'], lambda x: x.get('el') == 'text' and isinstance(x.get('value'), dict) and ' เครดิต (360p ราว ' in json.dumps(x['value'], ensure_ascii=False))]
    assert len(hit) == 1
    muls = [p for p in hit[0]['value']['parts'] if isinstance(p, dict) and p.get('op') == 'mul']
    assert len(muls) == 2 and muls[0]['b'] in (90, 180) and muls[1]['b'] in (42, 60), [m['b'] for m in muls]
    for m, r in zip(muls, ('720p', '360p')): m['b'] = cond(D(IS12), PRICE[V12][r] * 6, PRICE[V11][r] * 6)
    n = strip_sec_credits(c)
    insert_after(c, sec_box(c), std_block())
    return {'secDesc': n}


def std_parody(c):
    S = setup(c)
    add_video_model(c)
    for o in video_ops(c): assert o.get('resolution') == '{values.svRes}', o['id']
    remove_boxes(S, 'svRes')
    imgs = {o['id'] for o in c['ops'] if o.get('type') == 'image'}
    assert imgs == {'pdMaster', 'pyDraw1', 'pyDraw2'} | {f'mnBoard{k}' for k in ['', 2, 3, 4, 5, 6]}, imgs
    # pdMaster มีป้ายไทย "ล้อเลียน · AI" ทุกเฟรม = Pro คงเดิม · ค่าเริ่ม Pro = ตัวขาย (dev เดิม pyDraw 2.1 → ตามที่เลือก)
    assert next(o for o in c['ops'] if o['id'] == 'pdMaster')['model'] == PRO
    image_ops_pick(c, {'pyDraw1', 'pyDraw2'}, {f'mnBoard{k}' for k in ['', 2, 3, 4, 5, 6]}, PRO)
    insert_after(c, sec_box(c), std_block())
    return {}


def std_petdance(c):
    S = setup(c)
    vids = video_ops(c)
    R = AND(D(IS360), eq('{values.svSec}', '10'))   # 360p เฉพาะคลิป 10 วิ · 360p ไม่ส่ง startFrame (Flow 360p+startFrame ล้ม) ใช้บอร์ดใน refs
    if 'svRes' not in c['values']:
        c['values']['svRes'] = '720p'
        for o in vids:
            sf = o.get('startFrame')
            assert o.get('resolution') == '720p' and isinstance(sf, dict) and sf['when'] == eq('{item.clipStyle}', 'selfie'), o['id']
            o['resolution'] = cond(D(R), '360p', '720p')
            sf['when'] = AND(sf['when'], NOT(D(R)))
    else:
        for o in vids: assert o['resolution'] == cond(D(R), '360p', '720p'), o['id']
        remove_boxes(S, 'svRes')   # dev: กล่องความละเอียดเดิมในกล่องความยาว
    add_video_model(c)
    ms = {o['model'] for o in c['ops'] if o.get('type') == 'image'}
    assert len(ms) == 1 and ms <= {PRO, NB21}, ms   # น้อง + บอร์ด ห้ามมีตัวอักษร (E15) ⇒ ทุกภาพตามที่เลือก
    image_ops_pick(c, {o['id'] for o in c['ops'] if o.get('type') == 'image'}, set(), ms.pop())
    n = strip_sec_credits(c)
    insert_after(c, sec_box(c), std_block(eff360=D(R), res_notes=[
        note('360p ใช้ได้กับคลิป 10 วิเท่านั้น คลิปยาวกว่านี้จะทำที่ 720p', AND(D(IS360), NOT(eq('{values.svSec}', '10'))), warn=True)]))
    return {'secDesc': n}


TL, BA = 'ไทม์แลปส์กล้องนิ่ง', 'ก่อน → ลงมือ → หลัง'
def _arc(ref): return cond(AND(eq(ref, TL), D(IS360)), BA, ref)


def std_showhow(c):
    S = setup(c)
    vids = video_ops(c)
    n = {}
    if 'svRes' not in c['values']:
        # 360p ใช้ไทม์แลปส์ไม่ได้ (ต่อช่วงด้วย startFrame) ⇒ โครงเรื่องที่ใช้จริง = ก่อน → ลงมือ → หลัง (= dev ทุกไบต์)
        c['values']['svRes'] = '720p'
        cnt = {'arc': 0, 'parent': 0, 'sf': 0}
        def rw(o):
            it = o.items() if isinstance(o, dict) else enumerate(o) if isinstance(o, list) else ()
            for k, v in list(it):
                if v == '{item.arc}': o[k] = _arc('{item.arc}'); cnt['arc'] += 1
                elif v == '{parent.fields.arc}': o[k] = _arc('{parent.fields.arc}'); cnt['parent'] += 1
                else: rw(v)
        rw(c['ops'])
        for o in vids:
            sf = o.get('startFrame')
            if sf is not None:
                assert sf['when'] == eq(_arc('{item.arc}'), TL), o['id']
                sf['when'] = AND(sf['when'], NOT(D(IS360))); cnt['sf'] += 1
            assert 'resolution' not in o
            # ไม่ตั้ง = Flow เลือกเอง (ตัวขายเดิม) · 360p ส่งจริง · Omni 1.2 720p ส่ง 720p (แบบ minimal)
            o['resolution'] = cond(D(IS360), '360p', cond(D(IS12), '720p', ''))
        n['arc360'] = cnt
    else:
        for o in vids: assert o.get('resolution') == '{values.svRes}', o['id']
        remove_boxes(S, 'svRes')
    add_video_model(c)
    remove_boxes(S, 'imageModel')
    n['secDesc'] = strip_sec_credits(c)
    insert_after(c, sec_box(c), std_block(res_notes=[
        note('360p: ไทม์แลปส์ใช้ได้เฉพาะ 720p — งานที่ตั้งเป็นไทม์แลปส์จะทำแบบ ก่อน → ลงมือ → หลัง แทน', D(IS360))]))
    return n


def _gate_off_12(o):
    """minimal/fashion: เงื่อนไข 360p เดิมผูก Omni 1.2 → 360p ใช้ได้ทั้ง 1.1 และ 1.2 (พี่หมี 27 พ.ย.)"""
    if isinstance(o, dict):
        if o.get('op') == 'and' and isinstance(o.get('list'), list) and D(IS12) in o['list'] and any(x == D(IS360) for x in o['list']):
            o['list'] = [x for x in o['list'] if x != D(IS12)]
            if len(o['list']) == 1: v = o['list'][0]; o.clear(); o.update(v)
        for v in o.values(): _gate_off_12(v)
    elif isinstance(o, list):
        for v in o: _gate_off_12(v)


def _sec_grids_360(c, box, at, opts, note_text):
    """ความยาวคลิป (minimal/fashion): 360p ทำได้แค่ 10 วิ — ปุ่มชุดเดียว 2 แบบ (720p = ทุกความยาว · 360p = 10 วิ)"""
    for g in grids(box, 'svSec'): box['card'].remove(g)
    base = {'el': 'grid-select', 'field': 'svSec', 'contained': True, 'className': '!min-h-[48px] @[420px]:!min-h-0 [&_button>span:first-of-type]:font-bold'}
    a = {**D(base), 'cols': len(opts), 'options': [{'value': v, 'label': f'{v} วิ'} for v in opts], 'when': NOT(D(IS360))}
    b = {**D(base), 'cols': 1, 'options': [{'value': '10', 'label': '10 วิ', 'desc': note_text}], 'when': D(IS360)}
    box['card'][at:at] = [a, b]


def std_minimal(c):
    S = setup(c)
    for o in video_ops(c):   # resolution: เดิม 1.2 เท่านั้นที่ส่ง 360p ⇒ 360p+10 วิ ส่ง 360p ทั้ง 2 รุ่น · 720p เดิมทุกไบต์
        r = o['resolution']
        assert r['op'] == 'cond' and r['else'] == '' and r['then']['then'] == '360p' and r['then']['else'] == '720p', o['id']
        o['resolution'] = cond(D(r['then']['when']), '360p', cond(D(r['when']), '720p', ''))
    g_img, g_vid = grids(S, 'imageModel'), grids(S, 'svModel')
    assert len(g_img) == 1 and len(g_vid) == 1 and len(grids(S, 'svRes')) == 2
    box = box_holding(S, g_vid[0])
    drop = [g_img[0], g_vid[0]] + grids(S, 'svRes') + head_rows(box, {'โมเดลภาพ (สตอรีบอร์ด · ปก)', 'โมเดลวิดีโอ', 'ความละเอียด'})
    drop += [x for x in box['card'] if x.get('el') == 'text' and str(x.get('value', '')).startswith('มีข้อความบนภาพ')]
    drop += [x for x in box['card'] if x.get('el') == 'box' and any(i.get('icon') == 'toll' for i in x.get('card', []))]
    assert len(drop) == 9, len(drop)
    for x in drop: box['card'].remove(x)
    sh = head_rows(box, {'ความยาวคลิป'}); assert len(sh) == 1
    _sec_grids_360(c, box, idx(box['card'], sh[0]) + 1, ['10', '20', '30'], '360p ทำได้แค่ 10 วิ')
    nt = [x for x in box['card'] if x.get('el') == 'text' and str(x.get('value', '')).startswith('360p ทำได้แค่คลิป 10 วิ')]
    assert len(nt) == 1
    nt[0]['when'] = AND(D(IS360), NOT(eq('{values.svSec}', '10')))
    _gate_off_12(c['phases'])
    box['card'].append(std_block(eff360=AND(D(IS360), eq('{values.svSec}', '10'))))
    return {}


def std_fashion(c):
    """fashion: op (360p ทั้ง 2 รุ่น) ทำใน build-fashion.py E46 · ตรงนี้ = หน้าตั้งค่า"""
    S = setup(c)
    g_img, g_vid = grids(S, 'imageModel'), grids(S, 'svModel')
    assert len(g_img) == 1 and len(g_vid) == 1
    top = box_holding(S, box_holding(S, g_vid[0]))
    res_box = box_holding(S, grids(S, 'svRes')[0])
    res_notes = [x for x in res_box['card'] if x.get('el') == 'text' and str(x.get('value', '')).startswith('360p')]
    for x in res_notes:
        x.pop('when', None); x.update({'className': NOTE_CLS, 'icon': 'info'}); x['when'] = D(IS360)
    for g in (g_img[0], g_vid[0]): top['card'].remove(box_holding(S, g))
    top['card'].remove(res_box)
    top['card'] = [x for x in top['card'] if not (x.get('el') == 'box' and any(i.get('icon') == 'toll' for i in x.get('card', [])))]
    sh = head_rows(top, {'ความยาวคลิป'}); assert len(sh) == 1
    _sec_grids_360(c, top, idx(top['card'], sh[0]) + 1, ['10', '20', '30'], '360p ทำได้แค่ 10 วิ')
    nt = [x for x in top['card'] if x.get('el') == 'text' and str(x.get('value', '')).startswith('ความยาว 10 วิ — 360p')]
    assert len(nt) == 1; nt[0]['when'] = D(IS360)
    _gate_off_12(c['phases'])
    top['card'].append(std_block(res_notes=res_notes, sec=cond(D(IS360), '10', '{values.svSec}')))
    return {}


# hardsell: dropdown videoModel เดิม → ปุ่มแบบเดียวกัน · Omni 1.1/1.2 + Veo 3.1 Lite 2 แบบ · ถอด Veo Fast/Quality
HS_SEC = cond(eq('{item.eSec}', ''), '{values.svSec}', '{item.eSec}')
HS_IS_OMNI = {'op': 'contains', 'a': '{values.videoModel}', 'b': 'Omni'}
HS_R360 = AND(D(IS360), D(HS_IS_OMNI), {'op': 'lte', 'a': HS_SEC, 'b': 10})
HS_360_LINE = {
    'mnVideo': "\n\n360p mode: no frame is supplied — attached image 1 is the opening shot; start the clip looking exactly like it (same person, outfit, place, light, product and headline). Every mention of the first frame means that image.",
    'mnVideo2': "\n\n360p mode: no frame is supplied — attached image 1 is the opening shot of part 1; continue the same take with the same person, outfit, place, light and product. Every mention of the first frame means that image."}
HS_VM_SEND = cond(OR(eq('{values.videoModel}', VEO_FAST), eq('{values.videoModel}', VEO_Q)), VEO_LITE, '{values.videoModel}')
HS_VEO_DIS = OR(eq('{values.svSec}', '10'), eq('{values.svSec}', '20'))


def std_hardsell(c):
    S = setup(c)
    vids = video_ops(c)
    assert sorted(o['id'] for o in vids) == ['mnVideo', 'mnVideo2']
    has360 = 'svRes' in c['values']
    for o in vids:
        assert o['model'] in ('{values.videoModel}', HS_VM_SEND), o['model']
        o['model'] = D(HS_VM_SEND)
        SF0 = {'mnVideo': '{item.slots.board}', 'mnVideo2': '{item.slots.video}'}[o['id']]
        res = cond(D(HS_R360), '360p', '720p')
        sf = {'op': 'cond', 'when': NOT(D(HS_R360)), 'then': SF0}
        refs = {'op': 'lookupRefs', 'from': 'tasks', 'by': '', 'slot': 'board', 'also': [{'from': 'tasks', 'by': '{item.id}', 'slot': 'board', 'when': D(HS_R360)}]}
        line = {'op': 'block', 'sep': '', 'parts': [{'when': D(HS_R360), 'value': HS_360_LINE[o['id']]}]}
        if has360:   # dev v22.5-v22.8: ต้องตรงของเดิมทุกไบต์
            assert o['resolution'] == res and o['startFrame'] == sf and o['refs'] == refs and o['prompt']['parts'][-1] == line, o['id']
        else:
            assert o['resolution'] == '720p' and o['startFrame'] == SF0 and 'refs' not in o and o['prompt'].get('op') == 'concat', o['id']
            o['resolution'], o['startFrame'], o['refs'] = res, sf, refs
            o['prompt']['parts'].append(line)
    if not has360: c['values']['svRes'] = '720p'
    dd = grids(S, 'videoModel'); assert len(dd) == 1
    assert {o['value'] for o in dd[0]['options']} <= {V11, V12, VEO_LITE, VEO_LITE_LP, VEO_FAST, VEO_Q}
    ai = box_holding(S, box_holding(S, box_holding(S, dd[0])))   # กล่อง "โมเดล AI"
    assert any(x.get('el') == 'text' and x.get('value') == 'โมเดล AI' for x in ai['card']), ai['card'][0]
    remove(S, ai)
    vopts = D(VID_OPTS) + [
        {'value': VEO_LITE, 'label': 'Veo 3.1 Lite', 'desc': '8 / 16 วิ · 720p', 'disabledWhen': D(HS_VEO_DIS), 'reason': 'ทำได้แค่ 8 / 16 วิ'},
        {'value': VEO_LITE_LP, 'label': 'Veo 3.1 Lite คิวช้า', 'desc': '8 / 16 วิ · 720p', 'disabledWhen': D(HS_VEO_DIS), 'reason': 'ทำได้แค่ 8 / 16 วิ'}]
    eff = AND(D(IS360), {'op': 'lte', 'a': '{values.svSec}', 'b': 10})
    veo_sum = summary('videoModel', {'op': 'eq', 'a': '1', 'b': '0'}, '{values.svSec}', NOT(D(HS_IS_OMNI)))
    veo_sum['card'][1]['value'] = {'op': 'concat', 'parts': [cond(eq('{values.videoModel}', VEO_LITE_LP), 'Veo 3.1 Lite คิวช้า', 'Veo 3.1 Lite'), ' · 720p · ', '{values.svSec}', ' วิ']}
    blk = std_block(vfield='videoModel', vid_opts=vopts, res_when=D(HS_IS_OMNI), eff360=eff, omni=D(HS_IS_OMNI), extra_summary=veo_sum, res_notes=[
        note('360p ทำได้เฉพาะคลิปช่วงเดียว (8 / 10 วิ) · ใช้ภาพเฟรมแรกเป็นภาพอ้างอิงแทน — เปิดคลิปอาจไม่ตรงภาพเฟรมแรกเป๊ะ', AND(D(IS360), {'op': 'lte', 'a': '{values.svSec}', 'b': 10})),
        note('ความยาว 16 / 20 วิ ใช้ 720p · อยากประหยัดด้วย 360p เลือก 8 หรือ 10 วิ', AND(D(IS360), {'op': 'gt', 'a': '{values.svSec}', 'b': 10}), warn=True)])
    insert_after(c, sec_box(c), blk)
    assert c['values']['videoModel'] in (VEO_LITE, V12), c['values']['videoModel']
    return {}


RECIPES = {'minimal': std_minimal, 'fashion': std_fashion, 'podcast': std_podcast, 'parody': std_parody,
           'petdance': std_petdance, 'showhow': std_showhow, 'hardsell': std_hardsell}


def check(app, c):
    """ยามบล็อก: มีบล็อกมาตรฐาน 1 ชุดในหน้าตั้งค่า · ไม่มีตัวเลือกโมเดล/ความละเอียดนอกบล็อก (นอกหน้าตั้งค่ารายสินค้า)"""
    S = setup(c)
    blks = [n for _, n in find_all(S, lambda x: 'eb-model-std' in str(x.get('className', '')))]
    assert len(blks) == 1, len(blks)
    for f in ('imageModel', 'svModel', 'videoModel', 'svRes'):
        out = [g for g in grids(S, f) if not find_all(blks[0], lambda x, g=g: x is g)]
        assert not out, (f, len(out))
    s = json.dumps(c, ensure_ascii=False)
    for bad in (VEO_FAST, VEO_Q): assert s.count(bad) == (2 if app == 'hardsell' else 0), (bad, s.count(bad))


def apply(app, c):
    before = {k: c['values'].get(k) for k in ('svModel', 'imageModel', 'svRes', 'videoModel')}
    n = RECIPES[app](c)
    check(app, c)
    after = {k: c['values'].get(k) for k in before}
    print(f'model-standard {app}: {n} · ค่าเริ่ม {before} → {after}')
    return c


if __name__ == '__main__':
    app, F = sys.argv[1], sys.argv[2]
    raw = open(F, encoding='utf-8').read()
    indent = 2 if raw.startswith('{\n  "') else 1
    c = apply(app, json.loads(raw))
    out = json.dumps(c, ensure_ascii=False, indent=indent) + ('\n' if raw.endswith('\n') else '')
    open(F, 'w', encoding='utf-8').write(out)
    print('เขียน', F, len(out.encode('utf-8')))
