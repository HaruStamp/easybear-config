#!/usr/bin/env python3
# minimal-v36-el-menu.py — ย้ายไปใช้ `el.menu` ของ engine v1.10.0 (design ที่พี่หมีเคาะ 2026-09-22)
#
# design (เอกสารกลาง docs/STANDARD-multipart-2026-09-22.md §④):
#   ปุ่ม "ทำใหม่"       10 วิ → กดแล้วทำเลย ไม่มีเมนู · 20/30 วิ → เมนู [ทั้งหมด] [ช่วง 1] [ช่วง 2] [ช่วง 3*]
#   ปุ่ม "เลือกไฟล์เอง"  10 วิ → เลือกไฟล์เลย       · 20/30 วิ → เมนู [ใส่เป็นช่วง 1] [ช่วง 2] [ช่วง 3*]
#   ปุ่ม "ทำของที่ยังไม่มี" (gen-button chain 3 ช่วง) — **ไม่แตะ** มันข้ามช่องที่เต็มแล้วอยู่ดี
#
# 🔑 กลไกที่ทำให้ "10 วิ ไม่มีเมนู" เกิดเอง — engine ยิงทันทีเมื่อ `when` กรองแล้วเหลือ 1 ข้อ
#    ⇒ ข้อ "ทั้งหมด" ไม่มี `when` · ข้อ "ช่วง 1" ต้องมี `when: svSec>10`
#      ไม่งั้นตอน 10 วิ จะเหลือ 2 ข้อที่ให้ผลเหมือนกันเป๊ะ แล้วเมนูจะเปิดโดยไม่จำเป็น
#
# 🪤 สเปก engine: ปุ่มที่มี `menu` **ห้ามมี op/ops/chain/into/action ที่ตัวปุ่ม** (validator ฟ้องตอน boot)
# 🪤 เก็บเป้าหมายให้ครบก่อนแล้วค่อยแทน — แก้ระหว่าง walk = RecursionError (เจอจริงตอน v35)
# 🪤 **ยังไม่ถอดของเดิม (v26 ปุ่มใต้ไทล์ · v27 ไอคอน ↺)** — ถอดรอบถัดไปหลังยืนยันว่าเมนูทำงานจริง
#    กฎของทีม: ต่อของใหม่ให้ทำงานก่อน ค่อยถอดของเดิม · ถอดก่อนแล้วเจอปัญหา ผู้ใช้จะไม่เหลืออะไรให้กด
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'mn-menu'
OLD_VID_MARK = 'mn-vid-part'        # กล่องเมนูชั่วคราวของ v35 (action:setField + item.vpick)
VID_CHAIN = ['mnVideo3', 'mnVideo2', 'mnVideo']
BRD_CHAIN = ['mnBoard3', 'mnBoard2', 'mnBoard']


def gt(n):
    return {'op': 'gt', 'a': '{values.svSec}', 'b': n}


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def redo_menu(kind):
    """เมนู 'ทำใหม่' — ทั้งหมด / ช่วง 1 / ช่วง 2 / ช่วง 3"""
    op1, op2, op3 = ('mnVideo', 'mnVideo2', 'mnVideo3') if kind == 'video' else ('mnBoard', 'mnBoard2', 'mnBoard3')
    full = VID_CHAIN if kind == 'video' else BRD_CHAIN
    unit = 'คลิป' if kind == 'video' else 'บอร์ด'
    icon = 'movie' if kind == 'video' else 'image'
    return [
        {'label': 'ทั้งหมด', 'desc': 'ทำใหม่ทุกช่วง', 'icon': icon, 'chain': full},
        {'label': 'ช่วง 1 · 0-10 วิ', 'desc': '%s ช่วงแรก' % unit, 'icon': icon, 'chain': [op1], 'when': gt(10)},
        {'label': 'ช่วง 2 · 10-20 วิ', 'desc': '%s ช่วงกลาง' % unit, 'icon': icon, 'chain': [op2], 'when': gt(10)},
        {'label': 'ช่วง 3 · 20-30 วิ', 'desc': '%s ช่วงท้าย' % unit, 'icon': icon, 'chain': [op3], 'when': gt(20)},
    ]


def pick_menu(kind):
    """เมนู 'เลือกไฟล์เอง' — ใส่เป็นช่วงไหน"""
    s1, s2, s3 = ('video', 'video2', 'video3') if kind == 'video' else ('board', 'board2', 'board3')
    icon = 'movie' if kind == 'video' else 'photo_library'
    return [
        {'label': 'ใส่เป็นช่วง 1 · 0-10 วิ', 'icon': icon, 'into': '{item.slots.%s}' % s1},
        {'label': 'ใส่เป็นช่วง 2 · 10-20 วิ', 'icon': icon, 'into': '{item.slots.%s}' % s2, 'when': gt(10)},
        {'label': 'ใส่เป็นช่วง 3 · 20-30 วิ', 'icon': icon, 'into': '{item.slots.%s}' % s3, 'when': gt(20)},
    ]


def strip_targets(el):
    """สเปก engine: ปุ่มที่มี menu ห้ามมีเป้าที่ตัวปุ่มเอง"""
    for k in ('op', 'ops', 'chain', 'into', 'action', 'to', 'value', 'force'):
        el.pop(k, None)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)
    if MARK in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    done = {'vid_redo': 0, 'brd_redo': 0, 'pick_img': 0, 'pick_vid': 0}

    # ── ① กล่องเมนูชั่วคราวของ v35 → retry-button + menu ตัวเดียว ──
    boxes = []
    def find_box(n):
        kids = n.get('card')
        if not isinstance(kids, list):
            return
        for i, k in enumerate(kids):
            # 🪤 marker ของ v35 อยู่ทั้งกล่องนอกและกล่องเมนูข้างใน ⇒ ต้องเจาะจงด้วย "โครง" ไม่ใช่แค่ marker
            #    กล่องนอก = ลูกตัวแรกเป็นปุ่มเดิม (retry-button chain 3 ช่วง) ตามที่ v35 สร้างไว้
            if (isinstance(k, dict) and k.get('el') == 'box' and OLD_VID_MARK in str(k.get('className', ''))
                    and isinstance(k.get('card'), list) and len(k['card']) == 3
                    and k['card'][0].get('el') == 'retry-button' and k['card'][0].get('chain') == VID_CHAIN):
                boxes.append((kids, i, k))
    walk(cfg, find_box)
    assert len(boxes) == 2, 'ต้องเจอกล่อง v35 พอดี 2 จุด (เจอ %d)' % len(boxes)
    for kids, i, box in boxes:
        keep = box['card'][0]                      # ปุ่มเดิม (retry-button chain 3 ช่วง) — เอา className/label/icon มาใช้
        btn = {k: v for k, v in keep.items() if k in ('el', 'label', 'icon', 'variant', 'className', 'loadingLabel')}
        btn['className'] = str(btn.get('className', '')).replace(OLD_VID_MARK, '').strip() + ' ' + MARK
        btn['el'] = 'retry-button'
        btn['menu'] = redo_menu('video')
        if keep.get('when'):
            btn['when'] = keep['when']
        kids[i] = btn
        done['vid_redo'] += 1

    # ── ② ปุ่ม "ทำใหม่" ของบอร์ด (retry-button chain 3 ช่วง) → menu ──
    # ── ③ ปุ่มเลือกไฟล์ (pick-button into ช่องแรก) → menu ──
    targets = []
    def find_btn(n):
        el = n.get('el')
        if el == 'retry-button' and n.get('chain') == BRD_CHAIN:
            targets.append(('brd_redo', n))
        elif el == 'pick-button' and n.get('into') == '{item.slots.board}':
            targets.append(('pick_img', n))
        elif el == 'pick-button' and n.get('into') == '{item.slots.video}':
            targets.append(('pick_vid', n))
    walk(cfg, find_btn)
    for kind, el in targets:
        strip_targets(el)
        el['menu'] = redo_menu('board') if kind == 'brd_redo' else pick_menu('board' if kind == 'pick_img' else 'video')
        el['className'] = (str(el.get('className', '')).strip() + ' ' + MARK).strip()
        done[kind] += 1

    assert done['vid_redo'] == 2, done
    assert done['brd_redo'] == 5, 'ปุ่มทำใหม่ของบอร์ดต้องมี 5 จุด (เจอ %d)' % done['brd_redo']
    assert done['pick_img'] == 8, 'ปุ่มเลือกภาพต้องมี 8 จุด (เจอ %d)' % done['pick_img']
    assert done['pick_vid'] == 3, 'ปุ่มเลือกวิดีโอต้องมี 3 จุด (เจอ %d)' % done['pick_vid']

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    assert OLD_VID_MARK not in after, 'กล่องชั่วคราวของ v35 ยังค้าง'
    assert 'vpick' not in after, 'field vpick ของ v35 ยังถูกอ้างอยู่'

    # ── ยามหลังแก้ ──
    menus = []
    def chk(n):
        if isinstance(n.get('menu'), list):
            menus.append(n)
    walk(cfg, chk)
    assert len(menus) == 18, 'ปุ่มที่มีเมนูต้องมี 18 ตัว (2+5+8+3) เจอ %d' % len(menus)
    for m in menus:
        assert m['el'] in ('retry-button', 'pick-button'), 'ชนิดปุ่มผิด: %s' % m['el']
        for k in ('op', 'ops', 'chain', 'into', 'action'):
            assert k not in m, '🔴 ปุ่มที่มี menu ห้ามมี %s ที่ตัวปุ่ม (validator ของ engine ฟ้องตอน boot)' % k
        items = m['menu']
        assert items, 'เมนูว่าง = engine ฟ้อง'
        # ทุกข้อต้องมีเป้าเดียว
        for it in items:
            tg = [k for k in ('chain', 'op', 'ops', 'into', 'action') if k in it]
            assert len(tg) == 1, 'ข้อ "%s" ต้องมีเป้าเดียว (เจอ %s)' % (it.get('label'), tg)
            assert it.get('label'), 'ทุกข้อต้องมี label'
        # 🔑 หัวใจของ design: ตอน 10 วิ ต้องเหลือ "ข้อเดียว" เพื่อให้ engine ยิงทันทีไม่เปิดเมนู
        no_when = [it for it in items if 'when' not in it]
        assert len(no_when) == 1, ('ปุ่ม "%s": ต้องมีข้อที่ไม่มี when พอดี 1 ข้อ (เจอ %d) '
                                   'ไม่งั้นตอน 10 วิ เมนูจะเปิดทั้งที่มีตัวเลือกเดียวที่ใช้ได้'
                                   % (m.get('label'), len(no_when)))

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v36 ลงแล้ว — %s' % os.path.basename(src))
    print('   ปุ่มทำใหม่ วิดีโอ %d · บอร์ด %d · ปุ่มเลือกภาพ %d · เลือกวิดีโอ %d = เมนูรวม %d ปุ่ม'
          % (done['vid_redo'], done['brd_redo'], done['pick_img'], done['pick_vid'], len(menus)))
    print('   10 วิ = เหลือข้อเดียว ⇒ engine ยิงทันที ไม่เปิดเมนู (พฤติกรรมเดิมเป๊ะ)')
    print('   🪤 ยังไม่ถอดปุ่มเดิมของ v26/v27 — ถอดรอบถัดไปหลังยืนยันว่าเมนูทำงานจริง')


main()
