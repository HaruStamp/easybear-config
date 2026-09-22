#!/usr/bin/env python3
# hardsell-v7-row-important.py — ใส่ `!` ให้คลาสที่ "ชนกับของที่ engine เติมให้" (ท่าของ minimal v41)
#
# 🔑 ที่มา: `el:'row'` ของ engine เติม **`flex gap-2 flex-wrap items-center`** ให้เสมอ (atoms-cases-a2.tsx)
#    ⇒ คลาสที่เราเขียนใน `className` จะ **อยู่ในกล่องเดียวกับของ engine** ไม่ใช่ทับมัน
#    ⇒ คู่ที่ชนกันจริงของแถวเรา 2 คู่: `flex` ↔ `grid` · `items-center` ↔ `items-stretch`
#    ⇒ ตัวที่ชนะตัดสินจาก **ลำดับใน stylesheet ของ Tailwind** ไม่ใช่ลำดับที่เราเขียน
#       (วันนี้ `.grid` และ `.items-stretch` ออกทีหลัง เลยชนะพอดี = **ถูกโดยบังเอิญ**)
#    ⇒ ถ้า build เรียง utility ใหม่เมื่อไหร่ เลย์เอาต์เปลี่ยนเงียบ ๆ โดยไม่มีใครแก้อะไรเลย
# ✅ ทางที่ deterministic: ใส่ `!` (important) เฉพาะ 2 ตัวที่ชนจริง ⇒ ชนะด้วย specificity ไม่ใช่ลำดับ
#
# 🪤 ทำไมไม่เลือกท่า "กลับไป flex + `!flex-1 !basis-0` บนปุ่ม" (ซึ่งสะอาดกว่าและ engine v1.12.0 รองรับแล้ว):
#    ท่านั้น **ต้องการ engine ≥ v1.12.0** · แต่ `hardsell-dev.json` จะถูกคัดลอกทั้งดุ้นไป `hardsell-public.json`
#    ตอนปล่อยรุ่น ⇒ ถ้าวันไหนตัวขายไปอยู่บน engine เก่ากว่าที่คิด (remix จาก Backup เก่า) **ผลจะต่างโดยไม่มีอะไรฟ้อง**
#    ⇒ เลือกทางที่ได้ผลกับ engine ทุกเวอร์ชัน (เหตุผลเดียวกับที่ minimal เลือก · เขาเจอเคสนี้มาแล้วตอน v2.0.0 ของเขา)
#
# 🪤 คู่ `align-items` อันตรายกว่าคู่ `display`: display ชนกันแล้วเลย์เอาต์พังทั้งแถว (เห็นทันที)
#    แต่ align-items ชนกันแล้ว "ปุ่มสูงไม่เท่ากันนิดเดียว" ซึ่งมองข้ามได้ทั้งรอบ ⇒ ใส่ `!` ให้ **ทั้ง 2 แถว**
#    (แถวหน้าคลังคลิปไม่มีปุ่มเมนู จึงไม่ต้องแตะ display แต่คู่ align-items ชนเหมือนกัน)
# ⚠️ ของที่ทำวันนี้ไม่เปลี่ยนหน้าตาที่เห็นอยู่ — บังคับให้ผลลัพธ์ **เดิม** เกิดขึ้นด้วยเหตุผลที่ควบคุมได้แทนความบังเอิญ
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW_MENU_OLD = 'w-full grid grid-flow-col auto-cols-fr gap-2 items-stretch'
ROW_MENU_NEW = 'w-full !grid grid-flow-col auto-cols-fr gap-2 !items-stretch'
ROW_PLAIN_OLD = 'w-full flex-wrap gap-2 items-stretch'
ROW_PLAIN_NEW = 'w-full flex-wrap gap-2 !items-stretch'


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
    if ROW_MENU_NEW in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    menu_rows, plain_rows = [], []

    def collect(n):
        if n.get('el') == 'row' and n.get('className') == ROW_MENU_OLD:
            menu_rows.append(n)
        elif n.get('el') == 'row' and n.get('className') == ROW_PLAIN_OLD:
            plain_rows.append(n)

    walk(cfg, collect)
    assert len(menu_rows) == 1, 'แถวปุ่มเมนู (grid) ต้องเจอ 1 แถว (เจอ %d)' % len(menu_rows)
    assert len(plain_rows) == 1, 'แถวหน้าคลังคลิปต้องเจอ 1 แถว (เจอ %d)' % len(plain_rows)

    menu_rows[0]['className'] = ROW_MENU_NEW
    plain_rows[0]['className'] = ROW_PLAIN_NEW

    # ── ยาม ──
    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    # แถวเมนู: display + align-items ต้องเป็น important ทั้งคู่
    assert '!grid' in menu_rows[0]['className'] and '!items-stretch' in menu_rows[0]['className']
    # ห้ามเผลอใส่ ! ให้คลาสที่ไม่ได้ชนกับของ engine (เช่น grid-flow-col/auto-cols-fr/gap-2 ไม่มีคู่ชน)
    for cls in ('!grid-flow-col', '!auto-cols-fr', '!gap-2', '!w-full'):
        assert cls not in menu_rows[0]['className'], 'ใส่ ! เกินจำเป็นที่ %s (ไม่มีคู่ชนกับ engine)' % cls
    # แถวธรรมดา: ต้องไม่ถูกเปลี่ยน display (ไม่มีปุ่มเมนู = ไม่มีอาการ)
    assert 'grid' not in plain_rows[0]['className'], 'แถวหน้าคลังคลิปไม่ควรถูกเปลี่ยนเป็น grid'
    assert '!items-stretch' in plain_rows[0]['className']
    assert not any(isinstance(k, dict) and k.get('menu') for k in plain_rows[0].get('card', [])), 'แถวหน้าคลังคลิปไม่ควรมีปุ่มเมนู'
    # ปุ่มเมนูทั้ง 5 ตัวยังอยู่ครบ + ธง aux/where เดิมไม่ถูกแตะ
    menus = []
    walk(cfg, lambda n: menus.append(n) if n.get('menu') else None)
    assert len(menus) == 5, 'ปุ่มเมนูต้องมี 5 ตัว (เจอ %d)' % len(menus)
    ops = {o['id']: o for o in cfg['ops']}
    assert ops['mnTrans'].get('aux') is True
    for i in range(1, 9):
        assert ops['mnTrA%d' % i]['setFields'].get('where') == 'data.trans.s%den!=' % i

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v7 ลงแล้ว — %s' % os.path.basename(src))
    print('   แถวปุ่มหน้าดูคลิป: `!grid` + `!items-stretch` (ชนะ `flex`/`items-center` ที่ engine เติม ด้วย specificity)')
    print('   แถวหน้าคลังคลิป: `!items-stretch` (คู่ชน align-items เหมือนกัน แต่ไม่ต้องแตะ display)')
    print('   ⇒ หน้าตาเหมือนเดิมทุกอย่าง แต่เลิกแขวนอยู่กับลำดับใน stylesheet ของ Tailwind')


main()
