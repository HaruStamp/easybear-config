#!/usr/bin/env python3
# hardsell-v5-el-menu.py — แปลงปุ่มวิดีโอเป็น `el.menu` (engine ≥ v1.10.0 · มาตรฐานหลายช่วง §④)
# สายงานที่พี่หมีวาง: starter ออก engine → minimal แปลงก่อน → ส่งท่าให้ hardsell/showhow (ท่าอ้างอิง: minimal-v36-el-menu.py)
#
# 🔴 **เมนูของ hardsell ต่างจาก minimal/showhow โดยตั้งใจ** — ของเรา `mnVideo2.startFrame = '{item.slots.video}'`
#    (16 วิ = ช่วง 2 ต่อเฟรมจากช่วง 1) ⇒ **ห้ามมีข้อ "ช่วง 1 อย่างเดียว"**: สร้างช่วง 1 ใหม่โดยไม่แตะช่วง 2
#    = เผาเครดิต 1 ชิ้นแล้วได้คลิปที่รอยต่อไม่ตรง ซึ่งแย่กว่าไม่ทำอะไรเลย (minimal ยืนยันข้อนี้ให้แล้ว)
#    ⇒ เมนูมี 2 ข้อพอ: [ทั้งคลิป] · [เฉพาะช่วงท้าย]
#
# ทำอะไร:
#   ① ปุ่ม **retry-button** ที่ chain = ['mnVideo','mnVideo2'] (= ปุ่ม "ทำใหม่" 2 ตัว) → ใส่ menu 2 ข้อ
#   ② ปุ่ม **pick-button** ที่ into = '{item.slots.video}' (3 ตัว) → ใส่ menu [ใส่เป็นช่วง 1] / [ใส่เป็นช่วง 2]
#   🚫 ไม่แตะ **gen-button** ('Gen วิดีโอ' · 'ลองใหม่') — กฎกลาง: ปุ่ม "ทำของที่ยังไม่มี" ไม่มีเมนู
#   🚫 ไม่แตะปุ่มบอร์ด — hardsell มีบอร์ดช่องเดียวต่อคลิป (`mnBoard → board` ตัวเดียว) ไม่ใช่งานหลายช่วง
#
# 🪤 ท่าที่ minimal เสียเวลาไปก่อนแล้ว (ลอกมาใช้):
#   · หาเป้าด้วย **โครง** (el + chain/into) ไม่ใช่ className/marker — className ไม่ใช่ตัวระบุตัวตนของปุ่ม
#   · **เก็บเป้าให้ครบก่อน แล้วค่อยแทน** — แก้ระหว่าง walk = RecursionError
#   · ลบ op/ops/chain/into/action ออกจากตัวปุ่มให้หมดก่อนใส่ menu — validator ของ engine ฟ้องตอน boot (แอปไม่ขึ้น)
#   · **ห้ามเขียนจำนวนสื่อใน desc** — engine นับชิป "N ภาพ · N คลิป" ให้เอง
# 🔑 ยามสำคัญสุด: ทุกเมนูต้องมีข้อที่ **ไม่มี `when` พอดี 1 ข้อ** ⇒ โหมด 8 วิ เหลือ 1 ข้อ ⇒ engine ยิงเลยไม่เปิดเมนู
#    (= design ของพี่หมี "10 วิ ปุ่มทำงานเหมือนเดิม")
# รันซ้ำได้: ตรวจว่ามี menu แล้วหรือยัง
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VID_CHAIN = ['mnVideo', 'mnVideo2']
PICK_INTO = '{item.slots.video}'
HAS_SEG2 = {'op': 'gt', 'a': '{values.svSec}', 'b': 10}   # 16 วิ เท่านั้นที่มีช่วง 2 (ค่าที่เป็นไปได้ = 8 / 16 · สไตล์เดียวกับ when อื่นในไฟล์)

GEN_MENU = [
    {'label': 'ทั้งคลิป', 'desc': 'ทำใหม่ทุกช่วง รอยต่อตรงกันแน่นอน', 'icon': 'movie', 'chain': list(VID_CHAIN)},
    {'label': 'เฉพาะช่วงท้าย', 'desc': 'เก็บช่วงแรกไว้ ทำใหม่เฉพาะช่วงที่ต่อจากมัน', 'icon': 'skip_next',
     'chain': ['mnVideo2'], 'when': dict(HAS_SEG2)},
]
PICK_MENU = [
    {'label': 'ใส่เป็นช่วงแรก', 'desc': 'ไฟล์ของคุณแทนช่วงแรก', 'icon': 'looks_one', 'into': '{item.slots.video}'},
    {'label': 'ใส่เป็นช่วงท้าย', 'desc': 'ไฟล์ของคุณแทนช่วงท้าย', 'icon': 'looks_two',
     'into': '{item.slots.video2}', 'when': dict(HAS_SEG2)},
]
STRIP = ('op', 'ops', 'chain', 'into', 'action', 'to', 'value')


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)
    if '"menu"' in before:
        print('⏭  มี menu อยู่แล้ว — ไม่ทำอะไร')
        return

    # ── ① เก็บเป้าให้ครบก่อน (ห้ามแก้ระหว่างเดิน) ──
    gen_targets, pick_targets = [], []

    def collect(n):
        if n.get('el') == 'retry-button' and n.get('chain') == VID_CHAIN:
            gen_targets.append(n)
        elif n.get('el') == 'pick-button' and n.get('into') == PICK_INTO:
            pick_targets.append(n)

    walk(cfg, collect)
    assert len(gen_targets) == 2, 'ปุ่ม "ทำใหม่" วิดีโอต้องมี 2 ตัว (เจอ %d)' % len(gen_targets)
    assert len(pick_targets) == 3, 'ปุ่มเลือกวิดีโอต้องมี 3 ตัว (เจอ %d)' % len(pick_targets)

    # ── ② แทนที่ ──
    for n in gen_targets:
        for k in STRIP:
            n.pop(k, None)
        n['menu'] = json.loads(json.dumps(GEN_MENU))
    for n in pick_targets:
        for k in STRIP:
            n.pop(k, None)
        n['menu'] = json.loads(json.dumps(PICK_MENU))

    # ── ยาม ──
    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    menus = []
    walk(cfg, lambda n: menus.append(n) if n.get('menu') else None)
    assert len(menus) == 5, 'ต้องมีปุ่มเมนู 5 ตัว (เจอ %d)' % len(menus)
    for n in menus:
        # validator ของ engine: ปุ่มที่มี menu ห้ามมีเป้าที่ตัวปุ่ม (ไม่งั้นแอปไม่ขึ้น)
        for k in STRIP:
            assert k not in n, 'ปุ่มเมนูยังมี %s ติดอยู่ (validator จะฟ้องตอน boot)' % k
        # 🔑 ต้องมีข้อที่ไม่มี when พอดี 1 ข้อ ⇒ โหมด 8 วิ เหลือ 1 ข้อ = ยิงเลยไม่เปิดเมนู
        nowhen = [c for c in n['menu'] if 'when' not in c]
        assert len(nowhen) == 1, 'เมนูของปุ่ม "%s" ต้องมีข้อที่ไม่มี when พอดี 1 ข้อ (เจอ %d)' % (n.get('label'), len(nowhen))
        for c in n['menu']:
            assert ('chain' in c) ^ ('into' in c), 'แต่ละข้อต้องมี chain หรือ into อย่างใดอย่างหนึ่ง'
            # 🪤 desc ห้ามมีตัวเลขเลย — จำนวนสื่อ engine นับชิปให้ · จำนวนช่วงก็ล้าสมัยได้ถ้าวันหลังเพิ่มช่วง
            assert not any(ch.isdigit() for ch in str(c.get('desc', ''))), \
                'desc ห้ามมีตัวเลข (engine นับชิปสื่อให้ · เลขช่วงล้าสมัยง่าย) — เจอ: %s' % c.get('desc')
        # 🔴 กฎเฉพาะ hardsell: ห้ามมีข้อที่สร้างช่วง 1 ใหม่โดยไม่แตะช่วง 2
        for c in n['menu']:
            ch = c.get('chain')
            assert ch != ['mnVideo'], 'ห้ามมีข้อ "ช่วง 1 อย่างเดียว" — ช่วง 2 ต่อเฟรมจากช่วง 1 (รอยต่อจะผิด)'
    # ปุ่ม gen เดิมต้องไม่ถูกแตะ + บอร์ดไม่ถูกแตะ
    gens = []
    walk(cfg, lambda n: gens.append(n) if n.get('el') == 'gen-button' and n.get('chain') == VID_CHAIN else None)
    assert len(gens) == 5, 'ปุ่ม gen วิดีโอเดิมต้องยังอยู่ 5 ตัวและไม่มีเมนู (เจอ %d)' % len(gens)   # ลองใหม่ 2 + Gen วิดีโอ 3
    assert all('menu' not in g for g in gens), 'ปุ่ม gen ต้องไม่มีเมนู'
    boards = []
    walk(cfg, lambda n: boards.append(n) if n.get('chain') == ['mnBoard'] else None)
    assert len(boards) == 10 and all('menu' not in b for b in boards), 'ปุ่มบอร์ดต้องไม่ถูกแตะ (10 ตัว)'
    # ธง aux + ยาม where ต้องไม่ถูกแตะ
    ops = {o['id']: o for o in cfg['ops']}
    assert ops['mnTrans'].get('aux') is True
    for i in range(1, 9):
        assert ops['mnTrA%d' % i].get('aux') is True
        assert ops['mnTrA%d' % i]['setFields'].get('where') == 'data.trans.s%den!=' % i

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v5 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① ปุ่ม "ทำใหม่" วิดีโอ 2 ตัว → เมนู [ทั้งคลิป] · [เฉพาะช่วงท้าย] (gate svSec>10)')
    print('   ② ปุ่มเลือกวิดีโอ 3 ตัว → เมนู [ใส่เป็นช่วงแรก] · [ใส่เป็นช่วงท้าย] (gate svSec>10)')
    print('   🚫 ไม่แตะปุ่ม gen (ทำของที่ยังไม่มี) และปุ่มบอร์ด · 🔑 โหมด 8 วิ เหลือ 1 ข้อ = ยิงเลยไม่เปิดเมนู')


main()
