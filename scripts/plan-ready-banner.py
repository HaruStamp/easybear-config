#!/usr/bin/env python3
# plan-ready-banner — แก้ป้าย "บทที่ได้มาไม่สมบูรณ์" ที่ขึ้นผิดบนหน้าผลิต (ใบลูกค้า podcast 27 พ.ย. 2569 19:44)
#
# อาการ (เทสสดบัญชี Team · podcast v1.7.2 engine 1.25.2 · หลักฐาน easybear-podcast docs/qa/2026-11-27-incomplete-script.md):
#   กดปุ่มสมอง "คิดบทใหม่" ที่การ์ดเรื่อง (gen-button mnPlan = เขียนบทอย่างเดียว ไม่จัดคิว) → ได้บทครบ 10 ฉากผ่านเกณฑ์
#   → หน้าผลิตขึ้นป้ายเหลือง "บทที่ได้มาไม่สมบูรณ์ — กดปุ่มสมองที่เรื่องเพื่อคิดบทใหม่…" ทั้งที่บทสมบูรณ์
#   → และไม่มีปุ่มเริ่มบนหน้าผลิตเลย (ปุ่มทุกตัวบนการ์ดสถานะต้อง tasks > 0) ⇒ ลูกค้ากดสมองซ้ำ วนอยู่ที่เดิม
#   ระหว่างกดสมองซ้ำ ป้ายยังค้าง + การ์ดหมุน "กำลังเขียนบทพอดแคสต์ · คลิปที่ 1/1" = ภาพที่ลูกค้าส่งมา
# ราก: เงื่อนไขเดิม `tasks == 0 && some products data.plan!=` = "มีบทแต่ยังไม่จัดคิว" ซึ่งเป็นสถานะปกติหลังกดสมอง
#   บทเพี้ยนจริงไม่มีวันเข้าเงื่อนไขนี้ (planQueueOne/checkValid ลบ data.plan ทิ้งแล้วตั้ง status=error → การ์ดแดงแยกอยู่แล้ว)
#   — ข้อเดียวกับที่ minimal-v18-planfail.py จดไว้ตั้งแต่ ก.ย. แต่แก้แค่หน้าตั้งค่า ป้ายหน้าผลิตยังเป็นของเดิมทุกแอป
# แก้ (ข้อความ/ปุ่ม UI เท่านั้น · ops เท่าเดิมทุกไบต์ · ค่าเริ่มเดิม):
#   ① ป้ายนี้ = "บทพร้อมแล้ว" (โทนม่วง ไม่ใช่เตือน) โผล่เฉพาะตอนไม่มีงานวิ่ง (ระหว่างเขียนบทซ่อน — การ์ดสถานะบอกอยู่แล้ว)
#   ② ใส่ปุ่มในป้าย: ออโต้ = run-button (ทางเดียวกับปุ่ม "เริ่ม" หน้าตั้งค่า · บทที่มีอยู่ไม่ถูกเขียนซ้ำ — llm dedup)
#      ทีละขั้น = gen-phase [plan, queue] perProduct (จัดคิวจากบทเดิม ไม่ใช้สื่อ · ทางเดียวกับปุ่ม "เริ่มแบบทีละขั้น")
#   ③ (27 พ.ย. ค่ำ · ขยายทุกแอป) ป้ายเดิมที่อยู่ในรายการเดียวกับปุ่ม "เริ่ม" อยู่แล้ว (หน้าตั้งค่าของ hardsell) = ป้ายข้อความอย่างเดียว
#      ชี้ปุ่มเริ่มด้านล่าง (ไม่ใส่ปุ่มซ้ำ) · เงื่อนไขเดียวกับ ①
# ใช้: python3 scripts/plan-ready-banner.py <config.json>…   (รันซ้ำได้ — ไฟล์ที่แก้แล้วไม่เปลี่ยน)
import json, sys, copy

RUNNING = {'op': 'or', 'list': [{'op': 'eq', 'a': '{values.__runState}', 'b': s} for s in ('running', 'cooldown', 'retrying')]}
OLD_WHEN = {'op': 'and', 'a': {'op': 'eq', 'a': {'op': 'count', 'from': 'tasks'}, 'b': 0},
            'b': {'op': 'some', 'from': 'products', 'where': 'data.plan!='}}
NEW_WHEN = {'op': 'and', 'list': [OLD_WHEN['a'], OLD_WHEN['b'], {'op': 'not', 'a': RUNNING}]}
NEW_TEXT = 'บทพร้อมแล้ว — กดปุ่มด้านล่างเพื่อสร้างคลิปจากบทนี้ (ไม่ต้องคิดบทใหม่)'
NEW_TEXT_SETUP = 'บทพร้อมแล้ว — กดปุ่มเริ่มด้านล่างเพื่อสร้างคลิปจากบทนี้ (ไม่ต้องคิดบทใหม่)'
BTN_CLS = ('w-full justify-center !h-14 @[420px]:!h-12 !rounded-xl !text-[16px] @[420px]:!text-[15px] font-bold '
           '!bg-gradient-to-b !from-[#7c3aed] !to-[#6d28d9] !text-white !min-h-[48px] @[420px]:!min-h-0')
# ④ (27 พ.ย. ค่ำ · เทสสด hardsell) สีปุ่มในป้าย = สีปุ่ม "เริ่ม" หลักของแอปนั้น (hardsell ส้ม · minimal ฟ้า …) ไม่ใช่ม่วงของ podcast ทุกแอป
import re as _re
_GRAD = _re.compile(r'!from-\[#[0-9a-fA-F]{6}\] !to-\[#[0-9a-fA-F]{6}\]')


def app_grad(cfg) -> str:
    found = []
    def w(o):
        if isinstance(o, dict):
            if o.get('el') == 'run-button' and 'จากบทนี้' not in str(o.get('label', '')):
                m = _GRAD.search(str(o.get('className', '')))
                if m: found.append(m.group(0))
            for v in o.values(): w(v)
        elif isinstance(o, list):
            for v in o: w(v)
    w(cfg.get('phases'))
    return found[0] if found else '!from-[#7c3aed] !to-[#6d28d9]'


def is_new(n) -> bool:
    return (isinstance(n, dict) and isinstance(n.get('card'), list) and n.get('when') is not None and any(
        isinstance(r, dict) and r.get('el') == 'row' and any(isinstance(t, dict) and t.get('el') == 'text' and str(t.get('value', '')).startswith('บทพร้อมแล้ว — ')
                                                            for t in (r.get('card') or [])) for r in n['card']))


def build(plan_op: str, queue_op: str, with_buttons: bool = True) -> dict:
    b = {
        'el': 'box',
        'className': 'flex flex-col gap-3 bg-[var(--ev-accent)]/[0.06] border border-[var(--ev-accent)]/25 rounded-2xl p-3 @[420px]:p-3.5',
        'card': [
            {'el': 'row', 'className': 'items-center gap-3.5', 'style': {'flexWrap': 'nowrap'}, 'card': [
                {'el': 'box', 'className': 'w-[40px] h-[40px] rounded-xl bg-[var(--ev-accent)]/[0.14] flex items-center justify-center shrink-0',
                 'card': [{'el': 'icon', 'icon': 'task_alt', 'textSize': 'text-[20px]',
                           'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center'}]},
                {'el': 'text', 'value': NEW_TEXT,
                 'className': '!text-[15px] @[640px]:!text-[14px] !text-[var(--ev-accent)] font-medium leading-relaxed flex-1 min-w-0'},
            ]},
            {'el': 'run-button', 'label': 'เริ่มสร้างคลิปจากบทนี้', 'to': '', 'icon': 'bolt', 'className': BTN_CLS,
             'when': {'op': 'eq', 'a': '{values.mode}', 'b': 'auto'}},
            {'el': 'gen-phase', 'ops': [plan_op, queue_op], 'perProduct': True, 'icon': 'playlist_add', 'variant': 'solid',
             'label': 'จัดคิวคลิปจากบทนี้', 'className': BTN_CLS,
             'when': {'op': 'eq', 'a': '{values.mode}', 'b': 'manual'}},
        ],
        'when': NEW_WHEN,
    }
    if not with_buttons:   # ③ มีปุ่มเริ่มในรายการเดียวกันอยู่แล้ว
        b['card'] = b['card'][:1]
        b['card'][0]['card'][1]['value'] = NEW_TEXT_SETUP
    return b


def is_old(n) -> bool:
    return (isinstance(n, dict) and isinstance(n.get('card'), list) and n.get('when') == OLD_WHEN and any(
        isinstance(x, dict) and x.get('el') == 'text' and 'บทที่ได้มาไม่สมบูรณ์' in str(x.get('value', '')) for x in n['card']))


def apply(cfg: dict) -> int:
    pl = (cfg.get('auto') or {}).get('productLoop') or {}
    plan_op, queue_op = pl.get('plan', 'mnPlan'), pl.get('queue', 'mnQueue')
    ids = {o.get('id') for o in cfg.get('ops', [])}
    assert plan_op in ids and queue_op in ids, (plan_op, queue_op)
    n = [0]

    def walk(o):
        if isinstance(o, list):
            has_start = any(isinstance(x, dict) and x.get('el') == 'run-button' for x in o)
            for i, x in enumerate(o):
                if is_old(x):
                    o[i] = build(plan_op, queue_op, not has_start); n[0] += 1
                else:
                    walk(x)
        elif isinstance(o, dict):
            for v in o.values(): walk(v)
    walk(cfg.get('phases'))
    grad = app_grad(cfg)   # ④ ป้ายใหม่ทุกจุด (รวมที่ทำไว้แล้ว) ใช้สีปุ่มของแอป · รันซ้ำไม่เปลี่ยน

    def paint(o):
        if isinstance(o, list):
            for x in o: paint(x)
        elif isinstance(o, dict):
            if is_new(o):
                for b in o['card']:
                    if isinstance(b, dict) and b.get('el') in ('run-button', 'gen-phase'):
                        b['className'] = _GRAD.sub(grad, b['className'])
                return
            for v in o.values(): paint(v)
    paint(cfg.get('phases'))
    return n[0]


if __name__ == '__main__':
    for f in sys.argv[1:]:
        raw = open(f, encoding='utf-8').read()
        indent = 2 if raw.startswith('{\n  "') else 1   # minimal/hardsell = 2 ช่อง · แอปอื่น 1 ช่อง (คงรูปเดิม ไม่จัดทั้งไฟล์ใหม่)
        cfg = json.loads(raw)
        k = apply(cfg)
        left = json.dumps(cfg['phases'], ensure_ascii=False).count('บทที่ได้มาไม่สมบูรณ์')
        nl = '\n' if raw.endswith('\n') else ''
        new = json.dumps(cfg, ensure_ascii=False, indent=indent) + nl
        if new != raw: open(f, 'w', encoding='utf-8').write(new)
        print(f'{f}: ป้ายบทพร้อม {k} จุด · ข้อความเดิมเหลือ {left}')
