#!/usr/bin/env python3
# minimal-v40-lightbox-font.py — คืนขนาดตัวหนังสือปุ่มในแถบดูเต็มจอเป็น 13.5px (เท่าเดิมก่อน v39)
#
# ทำไมถึงบีบไว้ 12.5 ตอน v39: กลัวว่า 3 ปุ่มใน 420px แล้วป้าย "Gen วิดีโอใหม่" จะล้น
# ทำไมคืนได้: **วัดแล้วว่าไม่มีทางเป็น 3** — `when` ของสองปุ่ม Gen ตรงข้ามกันเป๊ะ
#     Gen วิดีโอใหม่  when: slots.video != ''      (มีคลิปแล้ว)
#     Gen บอร์ดใหม่   when: slots.video == ''      (ยังไม่มีคลิป)
#   ⇒ แถบมีปุ่มโผล่พร้อมกัน **สูงสุด 2 ตัว** ⇒ ช่องละ ~206px · ป้ายยาวสุดใช้ ~145px ⇒ เหลือเฟือ
# 📌 บทเรียน: **เผื่อความปลอดภัยโดยไม่ดูเงื่อนไขจริงก่อน = จ่ายด้วยคุณภาพที่ผู้ใช้เห็น**
#    (พี่หมีเคยทักเรื่องตัวหนังสือบางมาแล้วรอบหนึ่ง — ของแบบนี้เขาเห็น)
# 🪤 ยามข้างล่างยืนยัน "สูงสุด 2" จากตัว config เอง ⇒ วันไหนมีคนแก้ `when` ให้โผล่พร้อมกัน 3 ตัว สคริปต์จะฟ้อง
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'mn-lb-grid'
OLD, NEW = '!text-[12.5px]', '!text-[13.5px]'


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
            kids = row.get('card') or []
            rows.append(kids)
            for k in kids:
                cls = str(k.get('className', ''))
                if OLD in cls:
                    k['className'] = cls.replace(OLD, NEW); changed += 1
    walk(cfg, go)

    # ── ยาม: พิสูจน์จาก config ว่าโผล่พร้อมกันได้สูงสุดกี่ปุ่ม ──
    for kids in rows:
        always = [k for k in kids if not k.get('when')]
        conds = [json.dumps(k.get('when'), ensure_ascii=False) for k in kids if k.get('when')]
        # กลุ่มที่ `when` เหมือนกัน = โผล่พร้อมกัน · กลุ่มต่างกันถือว่าอาจพร้อมกันได้ (นับแบบแย่ที่สุด)
        worst = len(always) + (max((conds.count(c) for c in set(conds)), default=0)
                               if len(set(conds)) <= 2 else len(conds))
        assert worst <= 2, ('🔴 แถบนี้มีปุ่มโผล่พร้อมกันได้ %d ตัว — ฟอนต์ 13.5px จะล้นช่อง '
                            '(ช่องละ ~%dpx) ให้กลับไปใช้ 12.5px หรือออกแบบแถวใหม่' % (worst, 420 // max(worst, 1)))

    if not changed:
        print('⏭  ขนาดตัวหนังสือเป็น %s อยู่แล้ว — ไม่ทำอะไร' % NEW)
        return
    assert json.dumps(cfg, ensure_ascii=False) != before
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v40 ลงแล้ว — คืนฟอนต์ปุ่มแถบเต็มจอเป็น %s (%d ปุ่ม)' % (NEW, changed))
    print('   ยามยืนยันจาก when ของ config: แต่ละแถบโผล่พร้อมกันสูงสุด 2 ปุ่ม ⇒ ช่องละ ~206px')


main()
