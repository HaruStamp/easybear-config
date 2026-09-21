#!/usr/bin/env python3
# showhow-v28-video-script-translate.py — "บทวิดีโอ" + ปุ่มแปลรายฉาก (มาตรฐานกลาง · พี่หมีสั่งผ่านทีม minimal 2026-09-21)
# ที่มา: ผู้ใช้ต้องแก้บท 2 จุดต่อฉาก (ไทย + อังกฤษ) · ของเรามี 30 ฉาก ⇒ หนักกว่า minimal 2 เท่า
#        ตัดช่องอังกฤษทิ้งไม่ได้ (บทไทยส่งเข้าโมเดลวิดีโอตรง ๆ = โมเดล "วาด" ตัวหนังสือไทยลงคลิป)
#        ⇒ ทำให้การเติมช่องอังกฤษเป็น "กดปุ่มครั้งเดียว" แทนการพิมพ์เอง + เลิกเรียกว่า "บทอังกฤษ"
# ทำ 3 อย่าง (config ล้วน · ไม่แตะ engine · ลอกหลักการจาก minimal-v29/30/31 แต่เขียนของเราเอง 30 ฉาก):
#   ① ป้าย "บทอังกฤษ — …" → **"บทวิดีโอ"** + icon movie  (🪤 ห้ามใช้ videocam — ชนไอคอนมุมกล้อง)
#   ② placeholder ช่องอังกฤษ → "ภาษาอังกฤษ — ช่องนี้คือตัวที่ส่งเข้าโมเดลวิดีโอ"
#   ③ ปุ่ม "แปลงเป็นบทวิดีโอ" รายฉาก อยู่แถวเดียวกับป้าย "บทภาพ" ชิดขวา
#      โครง: mnTrans (llm แปลทั้งคลิป 1 ครั้ง → data.trans) + mnTrA1..30 (setFields เขียน "ช่องเดียว")
# 🔴 ยามห้ามถอด: ทุก mnTrA{N} มี setFields.where = 'data.trans.s{N}en!=' ⇒ LLM ไม่คืนคีย์นั้น = **ไม่แตะของเดิม**
# 🪤 op แปลห้ามเข้า auto.productLoop / stages (ทำงานเฉพาะตอนกดปุ่ม) — assert ท้ายไฟล์
# 🪤 JSON ของ showhow ใช้ indent=1 (ของ minimal ใช้ 2) — เขียนผิดชั้น diff พังทั้งไฟล์
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
MARK = 'sh-tr-inline'
N = 30
OLD_LABEL = 'บทอังกฤษ — ใช้ส่งเข้าโมเดลวิดีโอ (แก้คู่กับบทไทย)'
NEW_LABEL = 'บทวิดีโอ'
PLACEHOLDER = 'ภาษาอังกฤษ — ช่องนี้คือตัวที่ส่งเข้าโมเดลวิดีโอ'
BTN_LABEL = 'แปลงเป็นบทวิดีโอ'
BTN_CLASS = ('shrink-0 justify-center !gap-1 !h-8 !min-h-0 !px-2.5 !rounded-lg !text-[11.5px] font-bold '
             'border border-[var(--ev-border)] !bg-[var(--ev-surface2)] !text-[var(--ev-text)] ' + MARK)

raw = open(P, encoding='utf-8').read(); cfg = json.loads(raw)
if MARK in raw: sys.exit('⏭ แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')

def walk(node, fn, path=''):
    if isinstance(node, dict):
        fn(node, path)
        for k, v in node.items(): walk(v, fn, f'{path}/{k}')
    elif isinstance(node, list):
        for i, v in enumerate(node): walk(v, fn, f'{path}[{i}]')

# ── ① ② ป้าย + placeholder ──────────────────────────────────────────────
labels, areas = [], []
def visit(n, p):
    if n.get('el') == 'text' and n.get('value') == OLD_LABEL: labels.append(n)
    f = n.get('field')
    if n.get('el') == 'textarea' and isinstance(f, str) and re.fullmatch(r's\d+en', f): areas.append(n)
walk(cfg, visit)
assert len(labels) == N, f'ป้ายบทอังกฤษต้องมี {N} จุด เจอ {len(labels)}'
assert len(areas) == N, f'ช่องบทอังกฤษต้องมี {N} ช่อง เจอ {len(areas)}'
for n in labels: n['value'] = NEW_LABEL; n['icon'] = 'movie'
for n in areas: n['placeholder'] = PLACEHOLDER

# ── ③ op แปล ────────────────────────────────────────────────────────────
ops = cfg['ops']; ids = [o['id'] for o in ops]
assert 'mnPlan' in ids and 'mnQueue' in ids
th_lines = '\n'.join(f'ฉาก {i}: {{item.s{i}th}}' for i in range(1, N + 1))
trans = {
    'id': 'mnTrans', 'type': 'llm', 'over': 'tasks', 'out': 'trans', 'parse': 'json',
    'systemInstruction': ('You translate Thai storyboard shot descriptions into English prompts for a video model. '
                          'Keep the same camera action, subject and setting. Do not invent new objects, brands or text. '
                          'Do not translate Thai on-screen text or voice-over — only the visual description.'),
    'prompt': {'op': 'block', 'sep': '', 'parts': [
        'แปลบทภาพแต่ละฉากเป็นภาษาอังกฤษ สำหรับส่งเข้าโมเดลวิดีโอ\n\n', th_lines,
        (f'\n\nตอบเป็น JSON object เท่านั้น key = s1en ถึง s{N}en · value = คำบรรยายภาพภาษาอังกฤษของฉากนั้น\n'
         'ฉากที่บทไทยว่าง ให้ value เป็นสตริงว่าง · ห้ามใส่ข้อความอื่นนอก JSON'),
    ]},
    'logRun': 'กำลังแปลบทเป็นบทวิดีโอ…', 'logDone': 'แปลบทวิดีโอแล้ว',
}
apply_ops = [{
    'id': f'mnTrA{i}', 'type': 'transform', 'over': 'tasks', 'out': f'__trA{i}',
    'fn': 'setFields', 'pace': False,
    # 🪤 where = "ช่องต้นทางต้องไม่ว่าง" ⇒ แปลไม่มา = ไม่เขียนทับของเดิม (ห้ามถอด)
    'setFields': {'where': f'data.trans.s{i}en!=', 'fields': {f's{i}en': f'{{item.data.trans.s{i}en}}'}},
} for i in range(1, N + 1)]
j = ids.index('mnQueue')
cfg['ops'] = ops[:j] + [trans] + apply_ops + ops[j:]

# ── ④ ปุ่มรายฉาก แถวเดียวกับป้าย "บทภาพ" ชิดขวา ────────────────────────
def btn(n):
    return {'el': 'gen-phase', 'ops': ['mnTrans', f'mnTrA{n}'], 'label': BTN_LABEL, 'icon': 'translate',
            'variant': 'ghost', 'className': BTN_CLASS,
            'when': {'op': 'not', 'a': {'op': 'or', 'list': [
                {'op': 'eq', 'a': '{item.status}', 'b': 'running'},
                {'op': 'eq', 'a': '{item.meta.retrying}', 'b': '1'}]}}}
placed = []
def place(n, p):
    kids = n.get('card')
    if not isinstance(kids, list) or any(isinstance(k, dict) and MARK in str(k.get('className', '')) for k in kids): return
    ta = next((k for k in kids if isinstance(k, dict) and k.get('el') == 'textarea'
               and isinstance(k.get('field'), str) and re.fullmatch(r's\d+en', k['field'])), None)
    if not ta: return
    scene = int(re.fullmatch(r's(\d+)en', ta['field']).group(1))
    li = next((i for i, k in enumerate(kids) if isinstance(k, dict) and k.get('el') == 'text'
               and str(k.get('value', '')).startswith('บทภาพ')), None)
    assert li is not None, f'ฉาก {scene}: หาป้าย "บทภาพ" ในกล่องเดียวกันไม่เจอ'
    kids[li] = {'el': 'row', 'style': {'flexWrap': 'nowrap'},
                'className': 'w-full items-center justify-between gap-2', 'card': [kids[li], btn(scene)]}
    placed.append(scene)
walk(cfg, place)
assert sorted(placed) == list(range(1, N + 1)), f'ต้องวางปุ่มครบ {N} ฉาก (ได้ {sorted(placed)[:5]}… รวม {len(placed)})'

# 🪤 ยามต้องนับจาก **node** ไม่ใช่ substring (hardsell เจอ · minimal ยืนยัน): คำว่า "บทวิดีโอ" ไปโผล่ในป้ายปุ่มและข้อความ log ด้วย
#    ของเราวัดได้ substring 62 ครั้ง ทั้งที่ป้ายจริง 30 ⇒ นับด้วย count() = ยามหลอกตัวเอง
after = json.dumps(cfg, ensure_ascii=False)
def nodes(n):
    if isinstance(n, dict):
        yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n, list):
        for v in n: yield from nodes(v)
all_nodes = list(nodes(cfg))
n_label = sum(1 for x in all_nodes if x.get('el') == 'text' and x.get('value') == NEW_LABEL)
n_btn = sum(1 for x in all_nodes if x.get('el') == 'gen-phase' and x.get('label') == BTN_LABEL)
n_ph = sum(1 for x in all_nodes if x.get('el') == 'textarea' and x.get('placeholder') == PLACEHOLDER)
assert n_label == N and n_btn == N and n_ph == N, f'นับจาก node: ป้าย {n_label} · ปุ่ม {n_btn} · placeholder {n_ph} (ต้องได้ {N} ทั้งหมด)'
assert 'mnTrA1' not in json.dumps(cfg.get('auto'), ensure_ascii=False), 'op แปลหลุดเข้า auto'
assert 'mnTrA1' not in json.dumps(cfg.get('stages'), ensure_ascii=False), 'op แปลหลุดเข้า stages'
assert all(o['setFields'].get('where') for o in apply_ops), 'ยาม where หาย'
open(P, 'w', encoding='utf-8').write(json.dumps(cfg, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print(f'✓ v28 · (นับจาก node) ป้าย {n_label} · placeholder {n_ph} · ปุ่ม {n_btn} · op mnTrans + mnTrA1..{N} ·', os.path.getsize(P), 'bytes')
