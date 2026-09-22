#!/usr/bin/env python3
# minimal-v39-lightbox-grid.py — ปุ่มในแถบดูเต็มจอ "กว้างเท่ากันจริง" (พี่หมีทัก 2026-09-22 รอบที่ 3)
#
# คำสั่งพี่หมี: *"ทดสอบแล้วผ่านหมด แต่ติดตรง ปุ่ม gen ใหม่ กับ ดาวน์โหลด กว้างไม่เท่ากัน"*
#
# 🔴🔴 ทำไม v38 ไม่ได้ผล ทั้งที่ทุกปุ่มได้ `!flex-1 !basis-0` เหมือนกันเป๊ะ — **2 ชั้นซ้อนกัน**
#   ① `box` ของ engine = `<div className={el.className}>` เปล่า ๆ **ไม่มี `flex` ให้เอง**
#      v38 ตั้งแถวเป็น `w-full flex-wrap gap-2` ⇒ มี flex-wrap แต่**ไม่มี `flex`** ⇒ ไม่ใช่ flex container
#      ⇒ `flex-1` / `basis-0` ของลูกทุกตัว **ไม่มีผลอะไรเลย** (คุณสมบัติ flex ใช้ได้เฉพาะลูกของ flex container)
#      📌 บทเรียน: `flex-wrap`/`items-stretch`/`gap` **ไม่ได้แปลว่าเป็น flex** — ตาเห็นแล้วเหมือนถูก เพราะ gap ทำงานกับ grid/flex เท่านั้นแต่ตัวอื่นดูเข้าท่า
#   ② ปุ่มที่มี `menu` ถูก engine ห่ออีกชั้น (`atoms-menu.tsx`):
#         <div className="relative inline-flex items-center">   ← ตัวนี้ต่างหากที่เป็นลูกของแถว
#           <Btn el={{...el, className: el.className}} />       ← className ของเราไปลงชั้นใน
#      ⇒ ต่อให้แถวเป็น flex จริง ตัวห่อ `inline-flex` ก็กว้างตามเนื้อหา — **สั่งขนาดปุ่มเมนูจาก config ไม่ได้เลย**
#      (ปุ่มดาวน์โหลดไม่มีเมนู = เป็น `Btn` ตรง ๆ ได้ className เต็ม ⇒ คู่นี้จึงไม่มีทางเท่ากัน)
#
# ✅ ท่าที่ใช้: **grid ที่ทุกคอลัมน์กว้างเท่ากัน** (`grid grid-flow-col auto-cols-fr`)
#    - grid **blockify ลูกทุกตัว** ⇒ ตัวห่อ `inline-flex` กลายเป็น `flex` ธรรมดาและถูกยืดเต็มช่อง (default `justify-self: stretch`)
#      ⇒ แก้ชั้น ② ได้โดย **ไม่ต้องรอ engine** (ชั้น ② ยังเป็นบั๊กของ engine อยู่ — แจ้ง starter แยก เพราะ showhow/hardsell จะเจอตอนรับ el.menu ไปใช้)
#    - `auto-cols-fr` = ทุกคอลัมน์ 1fr เท่ากัน **โดยไม่ต้องรู้ล่วงหน้าว่ามีกี่ปุ่ม** (สำคัญ: บางปุ่มมี `when` โผล่/หายตามสถานะ
#      ⇒ ใช้ `grid-cols-3` ตายตัวไม่ได้ จะเหลือช่องว่างตอนปุ่มหาย)
#    - ลูกต้อง `!w-full !min-w-0` — `w-full` ให้ปุ่มชั้นในเต็มตัวห่อ · `min-w-0` ปลดพื้น min-content ไม่ให้ดันจนล้นแถว
# 🪤 ถอด `!flex-1 !basis-0 !min-w-[132px]` ทิ้งให้หมด — ของที่ไม่ทำงานแต่ดูเหมือนทำงาน อันตรายกว่าไม่มี
# 🪤 ถ้าวันหลัง engine แก้ให้ตัวห่อรับคลาสขนาด ของชุดนี้ยังถูก (grid ไม่สน flex-*)
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OLD = 'mn-lb-eq'
MARK = 'mn-lb-grid'
ROW = 'w-full grid grid-flow-col auto-cols-fr gap-2 items-stretch ' + MARK
# ปุ่ม: เต็มช่องของตัวเอง · ยอมให้บีบได้ · ตัวหนังสือไม่ตกบรรทัด (สูงคงที่ 40px ตกบรรทัดแล้วโดนตัดหัวท้าย)
BTN = ('justify-center !h-10 !rounded-xl !text-[12.5px] font-bold !w-full !min-w-0 '
       'whitespace-nowrap overflow-hidden !px-2.5 !min-h-[48px] @[420px]:!min-h-0 ' + MARK)
KEEP_PREFIX = ('!bg-', '!text-', '!from-', '!to-', 'border', '!border', 'backdrop')


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)
    if MARK in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return
    assert OLD in before, '🔴 ต้องรัน v38 ก่อน (ไม่เจอ marker %s)' % OLD

    rows = []

    def fix(n):
        arr = n.get('lightboxActions')
        if not isinstance(arr, list):
            return
        for row in arr:
            kids = row.get('card') or []
            for k in kids:
                old = str(k.get('className', ''))
                colour = ' '.join(w for w in old.split()
                                  if w.startswith(KEEP_PREFIX) and 'text-[1' not in w)
                k['className'] = (BTN + ' ' + colour).strip()
            row['className'] = ROW
            rows.append(len(kids))
    walk(cfg, fix)

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    assert len(rows) == 3, 'ต้องมีแถบปุ่ม 3 ชุด (รายการ + กริด + คลังคลิป) เจอ %d' % len(rows)

    # ── ยาม ──
    seen = []

    def chk(n):
        arr = n.get('lightboxActions')
        if not isinstance(arr, list):
            return
        for row in arr:
            rc = str(row.get('className', ''))
            assert 'grid' in rc.split(), '🔴 แถวต้องเป็น grid จริง (เจอ: %s)' % rc
            assert 'auto-cols-fr' in rc.split(), '🔴 ขาด auto-cols-fr = คอลัมน์ไม่เท่ากัน'
            kids = row.get('card') or []
            seen.append(len(kids))
            for k in kids:
                cls = str(k.get('className', '')).split()
                assert '!w-full' in cls, '🔴 ปุ่มต้อง !w-full ไม่งั้นตัวที่มีเมนูจะไม่เต็มช่อง'
                assert '!min-w-0' in cls, '🔴 ปุ่มต้อง !min-w-0 ไม่งั้นดันจนล้นแถว'
                assert not any(c.startswith(('!flex-1', '!basis-', '!min-w-[')) for c in cls), \
                    '🔴 ยังมีคลาส flex/min-w เดิมค้าง — ของที่ไม่ทำงานแต่ดูเหมือนทำงาน'
                assert 'w-full' not in [c for c in cls if c == 'w-full'], 'ห้ามมี w-full ไม่ติด ! (โดน default ทับ)'
            dl = [i for i, k in enumerate(kids) if k.get('el') == 'download-button']
            if dl:
                assert dl[0] == len(kids) - 1, '🔴 ปุ่มดาวน์โหลดต้องอยู่ขวาสุด (ตัวท้ายของแถว)'
    walk(cfg, chk)
    assert OLD not in json.dumps(cfg, ensure_ascii=False), 'marker เก่ายังค้าง'
    assert len(seen) == 3

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v39 ลงแล้ว — %s' % os.path.basename(src))
    print('   แถบปุ่ม %d ชุด (ปุ่มต่อแถว %s) → grid คอลัมน์เท่ากัน ทุกปุ่มเต็มช่อง' % (len(seen), seen))
    print('   ⇒ ปุ่มที่มีเมนู (ถูก engine ห่อ inline-flex) ถูก grid ยืดเต็มช่องแล้ว = กว้างเท่าดาวน์โหลด')


main()
