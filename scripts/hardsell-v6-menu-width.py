#!/usr/bin/env python3
# hardsell-v6-menu-width.py — แถวปุ่มในหน้าดูคลิปเต็มจอ: flex → grid เพื่อให้ปุ่มที่มี `el.menu` กว้างเท่าเพื่อน
#
# 🔴 บั๊ก engine (minimal เจอ · พี่หมีจับได้จากภาพหน้าจอ · แจ้ง starter แล้ว):
#    `atoms-menu.tsx` ห่อปุ่มด้วย `<div className="relative inline-flex items-center">` แล้วส่ง `el.className` ให้ `<Btn>` ชั้นใน
#    ⇒ ตัวที่แถว flex เห็นคือ **ตัวห่อ** ซึ่งไม่เคยได้ className ของเรา ⇒ `!flex-1` ไปไม่ถึง ⇒ กว้างตามเนื้อหาเสมอ
#    ⇒ วางคู่ปุ่มธรรมดาที่ได้ `!flex-1` เต็ม ๆ แล้ว **กว้างไม่เท่ากัน**
#
# ที่ของเราโดน = แถวเดียว: `lightboxActions` (ปุ่มในหน้าดูคลิปเต็มจอ) — `row` + ปุ่ม `!flex-1 !min-w-[132px]`
#    ส่วนอีก 4 ปุ่มเมนูอยู่ในกล่อง `flex flex-col` ⇒ flex item ถูก blockify + stretch เต็มความกว้างให้อยู่แล้ว (ไม่ต้องแก้)
#
# ทางเลี่ยงฝั่ง config (ท่าของ minimal · พิสูจน์กับของเขาแล้ว): แถวเป็น `grid grid-flow-col auto-cols-fr`
#    grid จะ blockify ตัวห่อ `inline-flex` แล้ว **ยืดเต็มช่องให้เอง** · `auto-cols-fr` ดีกว่า `grid-cols-N` ตายตัว
#    เพราะปุ่มบางตัวมี `when` โผล่/หาย (ของเรา: ปุ่มบอร์ด/ดาวน์โหลดมีเงื่อนไข)
# 🪤 ปุ่มในแถวต้องเปลี่ยน `!min-w-[132px]` → `!min-w-0` ด้วย ไม่งั้น 3 ช่องรวมกันล้นจอมือถือ 398px (grid ไม่ wrap ให้เหมือน flex-wrap)
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OLD_ROW = 'w-full flex-wrap gap-2 items-stretch'
NEW_ROW = 'w-full grid grid-flow-col auto-cols-fr gap-2 items-stretch'
OLD_BTN = '!flex-1 !min-w-[132px]'
NEW_BTN = '!w-full !min-w-0'


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
    if NEW_ROW in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    rows, btns = [], []

    def collect(n):
        # 🪤 className ชุดนี้ใช้ 2 แถว (หน้าดูคลิป + หน้าคลังคลิป) — เอาเฉพาะแถวที่ **มีปุ่มเมนู** เท่านั้น
        #    อีกแถวไม่มีปุ่มเมนู จึงไม่มีอาการ ⇒ ไม่แตะ (กฎ: อย่าแก้ของที่ไม่ได้พัง)
        if n.get('el') == 'row' and n.get('className') == OLD_ROW \
           and any(isinstance(k, dict) and k.get('menu') for k in n.get('card', [])):
            rows.append(n)
        if OLD_BTN in str(n.get('className', '')):
            btns.append(n)

    walk(cfg, collect)
    assert len(rows) == 1, 'แถวปุ่มหน้าดูคลิปเต็มจอต้องเจอ 1 แถว (เจอ %d)' % len(rows)
    # ปุ่มในแถวนั้นเท่านั้น (กันไปโดนปุ่มที่หน้าอื่นใช้ className ชุดเดียวกัน)
    inrow = [k for k in rows[0]['card'] if isinstance(k, dict) and OLD_BTN in str(k.get('className', ''))]
    assert len(inrow) == 3, 'ปุ่มในแถวต้องมี 3 ตัว (เจอ %d)' % len(inrow)
    assert len(btns) == 5, 'ทั้ง config ต้องมีปุ่มที่ใช้ min-w คงที่ 5 ตัว (แถวนี้ 3 + แถวหน้าคลังคลิป 2) เจอ %d' % len(btns)

    rows[0]['className'] = NEW_ROW
    for b in inrow:
        b['className'] = str(b['className']).replace(OLD_BTN, NEW_BTN)

    # ── ยาม ──
    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    left = []
    walk(cfg, lambda n: left.append(n.get('label')) if OLD_BTN in str(n.get('className', '')) else None)
    assert len(left) == 2, 'ปุ่มของแถวหน้าคลังคลิปต้องยังใช้ของเดิม 2 ตัว (เจอ %d)' % len(left)
    assert 'flex-wrap' not in rows[0]['className'], 'grid ไม่ควรมี flex-wrap ค้าง'
    # ปุ่มเมนูในแถวต้องยังเป็นปุ่มเมนูอยู่ (ไม่ได้ไปแตะโครงอื่น)
    menus_in_row = [k for k in rows[0]['card'] if isinstance(k, dict) and k.get('menu')]
    assert len(menus_in_row) == 1, 'แถวนี้ต้องมีปุ่มเมนู 1 ตัว (เจอ %d)' % len(menus_in_row)
    for b in inrow:
        assert '!w-full' in b['className'] and '!min-w-0' in b['className'], 'ปุ่มในแถวยังไม่ได้ w-full/min-w-0'
    # ปุ่มเมนูอีก 4 ตัวที่อยู่ใน flex-col ต้องไม่ถูกแตะ
    others = []
    walk(cfg, lambda n: others.append(n) if n.get('menu') and n not in menus_in_row else None)
    assert len(others) == 4, 'ปุ่มเมนูนอกแถวต้องมี 4 ตัวและไม่ถูกแตะ (เจอ %d)' % len(others)

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v6 ลงแล้ว — %s' % os.path.basename(src))
    print('   แถวปุ่มหน้าดูคลิปเต็มจอ: flex-wrap → grid grid-flow-col auto-cols-fr · ปุ่ม 3 ตัว → !w-full !min-w-0')
    print('   ⇒ ปุ่มที่มี el.menu กว้างเท่าปุ่มธรรมดาในแถวเดียวกัน (ตัวห่อ inline-flex ถูก grid ยืดให้)')


main()
