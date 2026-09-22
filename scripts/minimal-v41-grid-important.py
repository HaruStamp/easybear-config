#!/usr/bin/env python3
# minimal-v41-grid-important.py — ปิดช่องที่ทีม hardsell ชี้: `grid` ของเราชนะ `flex` ของ engine "เพราะลำดับใน stylesheet"
#
# ที่มา: `el:'row'` ของ engine เขียน  className={'flex gap-2 flex-wrap items-center ' + el.className}
#   ⇒ กล่องเดียวกันมีทั้ง `flex` (ของ engine) และ `grid` (ของเรา) · และมีทั้ง `items-center` และ `items-stretch`
#   ⇒ ผู้ชนะตัดสินด้วย **ลำดับใน stylesheet ของ Tailwind** ไม่ใช่ลำดับคำใน attribute
#      (ลำดับมาตรฐาน: .flex … .grid ⇒ grid ชนะ · items-center … items-stretch ⇒ stretch ชนะ) = ตรงกับที่เห็นบนจอ
#   🪤 แต่ **ถ้าวันหลังลำดับ utility เปลี่ยน ปุ่มจะกลับไปกว้างไม่เท่ากันเงียบ ๆ โดยไม่มีใครแก้อะไรเลย**
#      โรคเดียวกับที่ CLAUDE.md จดไว้แล้วเรื่อง `!important` ① "ชนกันเอง — ผู้ชนะตัดสินด้วยลำดับ stylesheet"
#      รอบนี้ต่างตรงที่คู่ชนไม่ได้มาจาก config แต่ **engine เติมมาให้ก่อนแล้ว** ⇒ อ่าน config อย่างเดียวมองไม่เห็นคู่ชน
#
# แก้: ใส่ `!` ให้ 2 ตัวที่ชนกับของ engine → `!grid` · `!items-stretch`
#   ✅ ได้ผลกับ engine **ทุกเวอร์ชัน** (ไม่ต้องรอ/ไม่ต้องพึ่ง v1.12.0) และไม่แขวนอยู่กับลำดับ CSS อีก
#   🪤 ทางเลือกของ hardsell (กลับไปใช้ flex + `!flex-1` บนปุ่มเมนู) ใช้ได้เฉพาะ engine ≥ v1.12.0
#      — เราเลือกทางนี้เพราะ config ไฟล์เดียวกันนี้จะถูกคัดลอกไป `minimal-public.json` ตอนปล่อยรุ่น
#        และไม่อยากให้ผลลัพธ์ผูกกับว่า tool ตัวไหนอยู่บน engine อะไร
#   🪤 `!` มีแค่บน 2 property ที่ชนจริง — ไม่หว่าน (CLAUDE.md: อย่ารับกฎกว้าง "ทุก ! ต้องมีคู่แข่ง")
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'mn-lb-grid'
PAIRS = [('grid', '!grid'), ('items-stretch', '!items-stretch')]
ENGINE_ROW_ADDS = ['flex', 'gap-2', 'flex-wrap', 'items-center']   # สิ่งที่ engine เติมให้ทุกแถว el:'row'


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
    assert MARK in before, '🔴 ต้องรัน v39 ก่อน'

    rows, changed = [], 0

    def go(n):
        nonlocal changed
        arr = n.get('lightboxActions')
        if not isinstance(arr, list):
            return
        for row in arr:
            assert row.get('el') == 'row', 'แถบปุ่มต้องเป็น el:row (เจอ %r) — ถ้าเปลี่ยนชนิด ต้องคิดคู่ชนใหม่' % row.get('el')
            cls = str(row.get('className', '')).split()
            for old, new in PAIRS:
                if old in cls:
                    cls[cls.index(old)] = new; changed += 1
            row['className'] = ' '.join(cls)
            rows.append(cls)
    walk(cfg, go)

    if not changed:
        print('⏭  ใส่ ! ไปแล้ว — ไม่ทำอะไร')
        return
    assert len(rows) == 3, 'ต้องมีแถบปุ่ม 3 ชุด เจอ %d' % len(rows)
    assert json.dumps(cfg, ensure_ascii=False) != before

    # ── ยาม: ทุก property ที่ engine เติมให้แถว ถ้าเราตั้งใจทับ ต้องทับด้วย ! ──
    for cls in rows:
        assert '!grid' in cls, '🔴 ต้องเป็น !grid — ไม่งั้นแพ้/ชนะ `flex` ของ engine ตามลำดับ stylesheet'
        assert 'grid' not in cls, '🔴 ยังมี grid ที่ไม่มี ! ค้าง'
        assert '!items-stretch' in cls, '🔴 ต้องเป็น !items-stretch (ชนกับ items-center ของ engine)'
        assert 'items-center' not in cls, 'แถวไม่ควรเขียน items-center เอง (engine เติมให้แล้ว)'
        # ของที่ engine เติมแล้วเราไม่ได้ตั้งใจทับ ต้องไม่ไปเขียนซ้ำแบบไม่มี !
        assert 'flex' not in cls, '🔴 ห้ามเขียน flex เองในแถวที่เป็น grid'

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v41 ลงแล้ว — แก้ %d คลาสใน %d แถบ' % (changed, len(rows)))
    print('   engine เติมให้ทุกแถว el:row = %s' % ' '.join(ENGINE_ROW_ADDS))
    print('   เราทับ 2 ตัวด้วย ! ⇒ display:grid และ align-items:stretch ชนะแน่นอน ไม่ขึ้นกับลำดับ stylesheet')


main()
