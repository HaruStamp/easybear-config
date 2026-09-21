#!/usr/bin/env python3
# minimal-v35-video-part-menu.py — "Gen วิดีโอใหม่" ของคลิป 20/30 วิ กดแล้วเลือกช่วงก่อน (พี่หมีสั่ง 2026-09-21)
# ที่มา: คลิป 20/30 วิ = วิดีโอ 2-3 ช่วงต่อกัน · ถ้าช่วง 2 เสีย เดิม**ซ่อมเฉพาะช่วงนั้นไม่ได้เลย**
#   ปุ่ม "Gen วิดีโอใหม่" (retry force) สั่ง chain [mnVideo3, mnVideo2, mnVideo] ⇒ ทำใหม่ทั้ง 3 ช่วง = เผาเครดิตวิดีโอ 3 ชิ้น
#   ปุ่ม "ลองใหม่" (gen ไม่ force) ข้ามช่องที่มีวิดีโอแล้ว ⇒ ช่วงที่เสีย (แต่มีไฟล์) ถูกข้าม = กดแล้วไม่มีอะไรเกิดขึ้น
# คำสั่งพี่หมี: "ไม่ต้องเพิ่มปุ่ม ใช้ UX เดิม — กดปุ่ม gen ใหม่ของวิดีโอแล้วให้เลือกก่อนว่าจะทำใหม่ทั้งหมด/ช่วง 1/2/3"
# 🔑 ท่าที่ engine รองรับอยู่แล้ว (ไม่ต้องรอ golden ใหม่): `action:'setField'` บนปุ่มในการ์ด
#    (app-handlers-b.tsx:122 — คอมเมนต์ของ engine เขียนเองว่า "state ต่อการ์ด … (เปิด/ปิด modal ผ่าน when)")
#    ⇒ กดปุ่มเดิม = เขียน field `vpick` ของคลิปนั้น → ตัวเลือกโผล่แทนที่ปุ่ม → กดเลือก → ยิง chain ช่วงเดียว
# 🪤 ไม่ใช่ popup ลอยทับ — engine ยังไม่มี popup ให้ config เรียก · แจ้งพี่หมีแล้วว่าต่างตรงนี้
# 🪤 `vpick` ไม่ต้องประกาศใน collections.fields — `bview` ของ v9 ก็ไม่ได้ประกาศและใช้งานได้ (readItem คืน '' เมื่อไม่มี)
# 🪤 10 วิ = ปุ่มเดิมทำงานเหมือนเดิมทุกประการ (ไม่มีเมนู) — ช่วงเดียวไม่มีอะไรให้เลือก
# 🪤 ทำเฉพาะปุ่มตระกูล "ทำใหม่" (retry force) 2 จุด — ปุ่ม "Gen วิดีโอ"/"ลองใหม่" (gen ไม่ force) ไม่แตะ
#    เพราะมันแปลว่า "ทำของที่ยังไม่มี" ซึ่งข้ามช่องที่เต็มอยู่แล้ว ไม่ต้องเลือกช่วง
# รันซ้ำได้: ตรวจ marker mn-vid-part
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'mn-vid-part'
FULL_CHAIN = ['mnVideo3', 'mnVideo2', 'mnVideo']

CLS_LIGHT = ('!flex-1 !min-w-[118px] justify-center !h-10 !rounded-xl !text-[12.5px] font-bold '
             'border border-[var(--ev-border)] !bg-[var(--ev-surface)] !min-h-[48px] @[420px]:!min-h-0 ' + MARK)
CLS_DARK = ('!flex-1 !min-w-[118px] justify-center !h-10 !rounded-xl !text-[12.5px] font-bold '
            '!bg-white/15 !text-white border border-white/35 backdrop-blur-sm !min-h-[48px] @[420px]:!min-h-0 ' + MARK)


def gt(key, n):
    return {'op': 'gt', 'a': '{values.%s}' % key, 'b': n}


def eq(a, b):
    return {'op': 'eq', 'a': a, 'b': b}


def all_of(*conds):
    lst = [c for c in conds if c is not None]
    return lst[0] if len(lst) == 1 else {'op': 'and', 'list': lst}


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def build(orig):
    """คืน box ที่แทนปุ่มเดิม: [ปุ่มเดิม (10 วิ)] · [ปุ่มเปิดเมนู (20/30 วิ)] · [เมนูเลือกช่วง]"""
    dark = 'bg-white/15' in str(orig.get('className', ''))
    cls = CLS_DARK if dark else CLS_LIGHT
    ow = orig.get('when')
    open_menu = eq('{item.vpick}', '1')
    not_open = {'op': 'not', 'a': open_menu}

    keep = json.loads(json.dumps(orig, ensure_ascii=False))          # ปุ่มเดิม — ใช้ตอน 10 วิ
    keep['when'] = all_of(ow, {'op': 'not', 'a': gt('svSec', 10)})

    opener = {k: v for k, v in orig.items() if k in ('label', 'icon', 'variant', 'className')}
    opener.update({'el': 'button', 'action': 'setField', 'to': 'vpick', 'value': '1',
                   'when': all_of(ow, gt('svSec', 10), not_open)})

    def pick(label, chain, extra=None):
        return {'el': 'retry-button', 'op': chain[-1], 'chain': chain, 'label': label,
                'icon': 'movie', 'variant': 'ghost', 'className': cls,
                'loadingLabel': 'กำลังสร้างวิดีโอ...',
                'when': all_of(extra) if extra else None}

    picks = [pick('ทั้งหมด', FULL_CHAIN),
             pick('ช่วง 1 · 0-10 วิ', ['mnVideo']),
             pick('ช่วง 2 · 10-20 วิ', ['mnVideo2']),
             pick('ช่วง 3 · 20-30 วิ', ['mnVideo3'], gt('svSec', 20))]
    for p in picks:
        if p['when'] is None:
            del p['when']

    close = {'el': 'button', 'action': 'setField', 'to': 'vpick', 'value': '', 'label': '',
             'icon': 'close', 'iconOnly': True, 'variant': 'ghost',
             'className': ('shrink-0 justify-center !gap-0 !w-10 !h-10 !min-h-0 !p-0 !rounded-xl '
                           + ('!bg-white/15 !text-white border border-white/35 ' if dark else
                              'border border-[var(--ev-border)] !bg-[var(--ev-surface)] ') + MARK)}

    menu = {'el': 'box', 'className': 'w-full flex flex-col gap-1.5 ' + MARK,
            'when': all_of(ow, gt('svSec', 10), open_menu),
            'card': [
                {'el': 'text', 'value': 'เลือกช่วงที่จะทำใหม่ (กินเครดิตช่วงละ 1 คลิป)',
                 'className': ('!text-[11.5px] font-bold opacity-70 px-0.5 '
                               + ('!text-white ' if dark else '')) + MARK},
                {'el': 'row', 'className': 'w-full flex-wrap items-center gap-1.5',
                 'card': picks + [close]},
            ]}

    return {'el': 'box', 'className': 'w-full ' + MARK, 'card': [keep, opener, menu]}


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)
    if MARK in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    done = []
    targets = []

    # 🪤 เก็บเป้าหมายให้ครบ "ก่อน" แก้ — แก้ระหว่าง walk = RecursionError
    #    (กล่องใหม่มีปุ่มเดิมที่ chain เหมือนกันอยู่ข้างใน ⇒ walk เดินเข้าไปเจอแล้วแทนซ้ำไม่รู้จบ · เจอจริงรอบแรก)
    def scan(n):
        kids = n.get('card')
        if not isinstance(kids, list):
            return
        for i, k in enumerate(kids):
            if (isinstance(k, dict) and k.get('el') == 'retry-button'
                    and k.get('chain') == FULL_CHAIN):
                targets.append((kids, i, k))

    walk(cfg, scan)   # lightboxActions[n] เป็น dict ที่มีคีย์ 'card' ⇒ walk เดินถึงเองอยู่แล้ว
    for kids, i, k in targets:
        kids[i] = build(k)
        done.append(k.get('label'))
    assert sorted(done) == ['Gen วิดีโอใหม่', 'Gen ใหม่'], 'ต้องเจอปุ่มทำใหม่วิดีโอ 2 จุดพอดี (เจอ %s)' % done

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    # ยาม: chain ของแต่ละตัวเลือกต้องเป็นช่วงเดียว และครบ 3 ช่วง + ตัวเลือก "ทั้งหมด"
    boxes = []
    def chk(n):
        if n.get('el') == 'box' and MARK in str(n.get('className', '')) and n.get('card'):
            if any(isinstance(c, dict) and c.get('el') == 'retry-button' for c in n['card']):
                boxes.append(n)
    walk(cfg, chk)
    assert len(boxes) == 2, 'ต้องได้ 2 กล่อง (เจอ %d)' % len(boxes)
    for b in boxes:
        menu = b['card'][2]
        rows = menu['card'][1]['card']
        chains = [c['chain'] for c in rows if c.get('el') == 'retry-button']
        assert chains == [FULL_CHAIN, ['mnVideo'], ['mnVideo2'], ['mnVideo3']], 'ตัวเลือกช่วงผิด: %s' % chains
        p3 = [c for c in rows if c.get('chain') == ['mnVideo3']][0]
        assert p3['when'] == gt('svSec', 20), 'ช่วง 3 ต้องโผล่เฉพาะ 30 วิ'
        assert b['card'][0]['el'] == 'retry-button' and b['card'][0]['chain'] == FULL_CHAIN, 'ปุ่มเดิมของ 10 วิ หาย'
        assert b['card'][1]['action'] == 'setField' and b['card'][1]['to'] == 'vpick', 'ปุ่มเปิดเมนูผิด'
        closes = [c for c in rows if c.get('action') == 'setField' and c.get('value') == '']
        assert len(closes) == 1, 'ต้องมีปุ่มปิดเมนู 1 ตัว'

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v35 ลงแล้ว — %s' % os.path.basename(src))
    print('   ปุ่ม "Gen วิดีโอใหม่" (การ์ด) + "Gen ใหม่" (ดูเต็มจอ) → 20/30 วิ กดแล้วเลือกช่วงก่อน')
    print('   ตัวเลือก: ทั้งหมด · ช่วง 1 · ช่วง 2 · ช่วง 3 (เฉพาะ 30 วิ) · ปุ่มปิด')
    print('   10 วิ = พฤติกรรมเดิมทุกตัวอักษร (ปุ่มเดียว ไม่มีเมนู)')


main()
