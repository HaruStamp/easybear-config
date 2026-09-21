#!/usr/bin/env python3
# minimal-v29-video-script-label-translate.py — ป้าย "บทวิดีโอ" + ไอคอน + ปุ่มแปลไทย→บทวิดีโอ
# ที่มา: พี่หมี 2026-09-21 — "ใช้คำว่าบทอังกฤษ เป็นบทวิดีโอไปเลยดีกว่าไหม + มีไอคอนวิดีโอหน้า label + เพิ่มปุ่มแปล"
#   ปัญหาเดิม: แก้บท 1 ฉาก ต้องแก้ 2 ช่อง (ไทยสำหรับสตอรีบอร์ด · อังกฤษสำหรับโมเดลวิดีโอ)
#   ⚠️ ส่งบทไทยเข้าโมเดลวิดีโอตรง ๆ ไม่ได้ — บั๊กเก่า: ไทยในคำสั่งวิดีโอถูกวาดเป็นตัวหนังสือบนคลิป (เคสมุมกล้องไทย)
#      ⇒ ต้องมี 2 ช่องต่อไป แต่ทำให้ "เติมช่องอังกฤษ" เป็นการกดปุ่มครั้งเดียวแทนการพิมพ์เอง
# ทำ 3 อย่าง:
#   ① ป้าย 15 จุด: "บทอังกฤษ — ใช้ส่งเข้าโมเดลวิดีโอ (แก้คู่กับบทไทย)" → "บทวิดีโอ" + icon movie
#      🪤 ใช้ `movie` ไม่ใช่ `videocam` — `videocam` ถูกใช้เป็นไอคอนของ "มุมกล้อง" อยู่แล้ว ถ้าซ้ำจะอ่านสับสน
#   ② textarea อังกฤษได้ placeholder บอกหน้าที่ (ภาษาอังกฤษ · ตัวที่ส่งเข้าโมเดลวิดีโอ)
#   ③ op ใหม่ 4 ตัว + ปุ่ม "แปลบทไทย → บทวิดีโอ"
#      mnTrans      = llm over tasks → data.trans (JSON s1en..s15en)
#      mnTransApply / 2 / 3 = transform fn:setFields คัดจาก data.trans ลง fields (ช่วงละ 5 ฉาก · gate ด้วย svSec)
#      🪤 ต้องแยก 3 ตัวตาม svSec — setFields ไม่มี when รายฟิลด์ ถ้าเขียนรวดเดียว ฉากที่ไม่มีในบทจะถูกล้างเป็นค่าว่าง
#      🪤 op ใหม่ไม่เข้า auto: `auto.productLoop.gens` และ `stages` ระบุรายชื่อ op ไว้ชัด ⇒ ของใหม่รันเมื่อกดปุ่มเท่านั้น
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'mnTrans'
OLD_LABEL = 'บทอังกฤษ — ใช้ส่งเข้าโมเดลวิดีโอ (แก้คู่กับบทไทย)'
NEW_LABEL = 'บทวิดีโอ'
PLACEHOLDER = 'ภาษาอังกฤษ — ช่องนี้คือตัวที่ส่งเข้าโมเดลวิดีโอ'


def walk(node, fn, path=''):
    if isinstance(node, dict):
        fn(node, path)
        for k, v in node.items():
            walk(v, fn, path + '/' + k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, fn, path + '[%d]' % i)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)
    if MARK in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    # ── ① + ② ป้าย/placeholder ──
    labels, areas = [], []
    def visit(n, p):
        if n.get('el') == 'text' and n.get('value') == OLD_LABEL:
            labels.append(n)
        f = n.get('field')
        if n.get('el') == 'textarea' and isinstance(f, str) and f.startswith('s') and f.endswith('en'):
            areas.append(n)
    walk(cfg, visit)
    assert len(labels) == 15, 'ป้ายบทอังกฤษต้องมี 15 จุด เจอ %d' % len(labels)
    assert len(areas) == 15, 'ช่องบทอังกฤษต้องมี 15 ช่อง เจอ %d' % len(areas)
    for n in labels:
        n['value'] = NEW_LABEL
        n['icon'] = 'movie'
    for n in areas:
        n['placeholder'] = PLACEHOLDER

    # ── ③ op แปล ──
    ops = cfg['ops']
    ids = [o['id'] for o in ops]
    assert 'mnPlan' in ids, 'ไม่เจอ mnPlan'

    th_lines = '\n'.join('ฉาก %d: {item.s%dth}' % (i, i) for i in range(1, 16))
    trans = {
        'id': 'mnTrans', 'type': 'llm', 'over': 'tasks', 'out': 'trans', 'parse': 'json',
        'systemInstruction': ('You translate Thai storyboard shot descriptions into English prompts for a video model. '
                              'Keep the same camera action, subject and setting. Do not invent new objects, brands or text. '
                              'Do not translate Thai on-screen text or voice-over — only the visual description.'),
        'prompt': {'op': 'block', 'sep': '', 'parts': [
            'แปลบทภาพแต่ละฉากเป็นภาษาอังกฤษ สำหรับส่งเข้าโมเดลวิดีโอ\n\n',
            th_lines,
            ('\n\nตอบเป็น JSON object เท่านั้น key = s1en ถึง s15en · value = คำบรรยายภาพภาษาอังกฤษของฉากนั้น\n'
             'ฉากที่บทไทยว่าง ให้ value เป็นสตริงว่าง · ห้ามใส่ข้อความอื่นนอก JSON'),
        ]},
        'logRun': 'กำลังแปลบทเป็นบทวิดีโอ…', 'logDone': 'แปลบทวิดีโอแล้ว',
    }

    def apply_op(n, lo, hi, when=None):
        o = {'id': n, 'type': 'transform', 'over': 'tasks', 'out': '__trans%s' % (n[-1] if n[-1].isdigit() else ''),
             'fn': 'setFields', 'pace': False,
             'setFields': {'fields': {'s%den' % i: '{item.data.trans.s%den}' % i for i in range(lo, hi + 1)}}}
        if when: o['when'] = when
        return o

    new_ops = [trans,
               apply_op('mnTransApply', 1, 5),
               apply_op('mnTransApply2', 6, 10, 'values.svSec>10'),
               apply_op('mnTransApply3', 11, 15, 'values.svSec>20')]
    # วางต่อท้าย mnPlan เพื่อให้อ่าน config แล้วเห็นกลุ่ม "งานข้อความ" อยู่ด้วยกัน
    i = ids.index('mnQueue')
    cfg['ops'] = ops[:i] + new_ops + ops[i:]

    # ── ปุ่ม: วางในกล่องเดียวกับหัวข้อบท (card[1] ของกล่องบท) ──
    btn = {'el': 'gen-phase', 'ops': ['mnTrans', 'mnTransApply', 'mnTransApply2', 'mnTransApply3'],
           'label': 'แปลบทไทย → บทวิดีโอ', 'icon': 'translate', 'variant': 'ghost',
           'className': ('w-full justify-center !h-10 !rounded-xl !text-[13px] @[640px]:!text-[12px] font-bold '
                         'border border-[var(--ev-border)] !bg-[var(--ev-surface)] !min-h-[48px] @[420px]:!min-h-0 mn-translate-btn'),
           'when': {'op': 'not', 'a': {'op': 'or', 'list': [
               {'op': 'eq', 'a': '{item.status}', 'b': 'running'},
               {'op': 'eq', 'a': '{item.meta.retrying}', 'b': '1'}]}}}
    holder = None
    def find_holder(n, p):
        nonlocal holder
        if holder is None and n.get('el') == 'box':
            kids = n.get('card') or []
            if any(isinstance(k, dict) and k.get('field') == 's1th' for k in kids):
                holder = n
    walk(cfg, find_holder)
    assert holder is not None, 'หากล่องบทฉาก 1 ไม่เจอ'
    holder['card'].append(btn)

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    got = [o['id'] for o in cfg['ops']]
    for n in ('mnTrans', 'mnTransApply', 'mnTransApply2', 'mnTransApply3'):
        assert n in got, 'ไม่ได้เติม op %s' % n
    assert 'mnTrans' not in json.dumps(cfg.get('auto'), ensure_ascii=False), 'op แปลต้องไม่เข้า auto'
    assert 'mnTrans' not in json.dumps(cfg.get('stages'), ensure_ascii=False), 'op แปลต้องไม่เข้า stages'
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v29 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① ป้าย 15 จุด → "บทวิดีโอ" + ไอคอน movie · ② placeholder บอกหน้าที่ 15 ช่อง')
    print('   ③ op ใหม่ 4 ตัว (mnTrans + Apply×3 gate ตามความยาว) + ปุ่ม "แปลบทไทย → บทวิดีโอ" ใต้ฉาก 1')
    print('   🪤 op ใหม่ไม่อยู่ใน auto/stages ⇒ ทำงานเมื่อกดปุ่มเท่านั้น')


main()
