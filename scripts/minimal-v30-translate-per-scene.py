#!/usr/bin/env python3
# minimal-v30-translate-per-scene.py — ปุ่มแปลเป็น "ของฉากใครฉากมัน" (พี่หมีสั่ง 2026-09-21 · แก้จาก v29)
# v29 ทำปุ่มเดียวแปลทั้งคลิป → พี่หมีทักว่าควรเป็นปุ่มเล็กประจำฉาก เพราะ:
#   · แก้บทจริงมักแก้ทีละฉาก ⇒ ปุ่มรวมเขียนทับช่องอังกฤษของฉากอื่นที่อาจแก้มือไว้
#   · ปุ่มอยู่ไกลจากฉากที่แก้ ⇒ ต้องเลื่อนหา
# โครงใหม่: mnTrans (llm แปลทั้งคลิป 1 ครั้ง → data.trans) + mnTrA1..15 (setFields เขียน "ช่องเดียว")
#   ปุ่มฉาก N = gen-phase ops:[mnTrans, mnTrA{N}] ⇒ กดฉากไหน **เขียนทับเฉพาะช่องนั้น** ฉากอื่นไม่ขยับ
# 🔴 กันเคส "แปลไม่มา แล้วลบของเดิมทิ้ง": ทุก mnTrA{N} มี `setFields.where = 'data.trans.s{N}en!='`
#    ⇒ ถ้า LLM ไม่คืนคีย์นั้น (หรือคืนค่าว่าง) **ข้ามไปเลย ไม่เขียนทับ** — ยืนยันในโค้ด engine:
#       `matchWhere` ใช้ readItem(it, path.split('.')) ⇒ รองรับ path ซ้อน `data.trans.s1en` · `!=` กับ rhs ว่าง = "ต้องไม่ว่าง"
# ลบของ v29 ที่ถูกแทน: ปุ่มรวม (marker mn-translate-btn) + mnTransApply/2/3
# รันซ้ำได้: ตรวจ marker mn-tr-scene
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'mn-tr-scene'
N_SCENES = 15
BTN_CLASS = ('justify-center !gap-1 !h-8 !min-h-0 !px-2 !rounded-lg !text-[11.5px] font-bold '
             'border border-[var(--ev-border)] !bg-[var(--ev-surface2)] !text-[var(--ev-text)] ' + MARK)


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
    assert 'mnTrans' in before, 'ต้องรัน v29 ก่อน (ยังไม่มี op แปล)'
    if MARK in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    # ── ① ลบปุ่มรวมของ v29 ──
    removed_btn = 0
    def drop_btn(n, p):
        nonlocal removed_btn
        kids = n.get('card')
        if isinstance(kids, list):
            keep = [k for k in kids if not (isinstance(k, dict) and 'mn-translate-btn' in str(k.get('className', '')))]
            if len(keep) != len(kids):
                removed_btn += len(kids) - len(keep)
                n['card'] = keep
    walk(cfg, drop_btn)
    assert removed_btn == 1, 'ต้องเจอปุ่มรวมของ v29 พอดี 1 ปุ่ม (เจอ %d)' % removed_btn

    # ── ② เปลี่ยน op apply: 3 ตัวช่วงละ 5 ฉาก → 15 ตัว ฉากละ 1 ช่อง + ยามกันเขียนทับด้วยค่าว่าง ──
    ops = [o for o in cfg['ops'] if o['id'] not in ('mnTransApply', 'mnTransApply2', 'mnTransApply3')]
    assert len(cfg['ops']) - len(ops) == 3, 'ต้องเจอ apply เดิม 3 ตัว'
    new_apply = [{
        'id': 'mnTrA%d' % i, 'type': 'transform', 'over': 'tasks', 'out': '__trA%d' % i,
        'fn': 'setFields', 'pace': False,
        # 🪤 where = "ช่องต้นทางต้องไม่ว่าง" ⇒ แปลไม่มา = ไม่แตะของเดิม (ห้ามถอดออก)
        'setFields': {'where': 'data.trans.s%den!=' % i, 'fields': {'s%den' % i: '{item.data.trans.s%den}' % i}},
    } for i in range(1, N_SCENES + 1)]
    j = [o['id'] for o in ops].index('mnQueue')
    cfg['ops'] = ops[:j] + new_apply + ops[j:]

    # ── ③ ปุ่มเล็กประจำฉาก — วางท้ายกล่องบทของฉากนั้น (ใต้ช่องบทวิดีโอ) ──
    def btn(n):
        return {'el': 'gen-phase', 'ops': ['mnTrans', 'mnTrA%d' % n],
                'label': 'แปลฉากนี้', 'icon': 'translate', 'variant': 'ghost',
                'className': BTN_CLASS,
                'when': {'op': 'not', 'a': {'op': 'or', 'list': [
                    {'op': 'eq', 'a': '{item.status}', 'b': 'running'},
                    {'op': 'eq', 'a': '{item.meta.retrying}', 'b': '1'}]}}}

    placed = []
    def place(n, p):
        kids = n.get('card')
        if not isinstance(kids, list):
            return
        for k in kids:
            if isinstance(k, dict) and k.get('el') == 'textarea' and isinstance(k.get('field'), str):
                m = re.match(r's(\d+)en$', k['field'])
                if m and not any(isinstance(x, dict) and MARK in str(x.get('className', '')) for x in kids):
                    kids.append(btn(int(m.group(1))))
                    placed.append(int(m.group(1)))
                    return
    walk(cfg, place)
    assert sorted(placed) == list(range(1, N_SCENES + 1)), 'ต้องวางปุ่มครบ 15 ฉาก (ได้ %s)' % sorted(placed)

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    got = [o['id'] for o in cfg['ops']]
    assert all('mnTrA%d' % i in got for i in range(1, N_SCENES + 1)), 'op apply ไม่ครบ'
    assert not any(o.startswith('mnTransApply') for o in got), 'apply เดิมยังอยู่'
    assert 'mnTrA1' not in json.dumps(cfg.get('auto'), ensure_ascii=False) and 'mnTrA1' not in json.dumps(cfg.get('stages'), ensure_ascii=False), 'op แปลต้องไม่เข้า auto/stages'
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v30 ลงแล้ว — %s' % os.path.basename(src))
    print('   ปุ่ม "แปลฉากนี้" 15 ปุ่ม (ฉากละ 1 · ใต้ช่องบทวิดีโอของฉากนั้น) · ถอดปุ่มรวมของ v29 ออกแล้ว')
    print('   op: mnTrans (แปลทั้งคลิป 1 ครั้ง) + mnTrA1..15 (เขียนช่องเดียว · where กันเขียนทับด้วยค่าว่าง)')


main()
