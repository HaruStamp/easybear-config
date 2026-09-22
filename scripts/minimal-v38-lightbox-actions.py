#!/usr/bin/env python3
# minimal-v38-lightbox-actions.py — แถบปุ่มตอนดูสื่อเต็มจอ (พี่หมีสั่ง 2026-09-22 รอบที่ 2)
#
# คำสั่งพี่หมี: *"หน้าดูวีดีโอเต็มจอ ของทั้งหน้าผลิตและคลังคลิป ให้ปุ่มกว้างเท่า ๆ กัน
#                แล้วปุ่มดาวน์โหลดอยู่ขวาแทนอยู่ซ้าย · และในมุมมองลิสต์ ถ้ากดดูวิดีโอเต็มจอ ให้แสดงปุ่มด้วย
#                ตอนนี้ปุ่มแสดงแค่ในมุมมองกริด"*
#
# ที่เป็นอยู่ก่อนแก้:
#   กริด (หน้าผลิต)  [ดาวน์โหลด flex-1] [Gen วิดีโอใหม่ **w-full**] [Gen บอร์ดใหม่ flex-1]   ← ความกว้างไม่เท่ากัน
#   คลังคลิป         [ดาวน์โหลด flex-1] [ตัดต่อ flex-1]                                      ← เท่ากันแล้ว แต่ดาวน์โหลดอยู่ซ้าย
#   มุมมองรายการ     **ไม่มีแถบปุ่มเลย** ← กดดูวิดีโอเต็มจอแล้วไม่มีอะไรให้กด
#
# 🪤 ตัว `w-full` บนปุ่ม Gen วิดีโอใหม่ = ของที่ผมใส่เองตอนพี่หมีบอกว่า "ปุ่มแคบไป" (รอบก่อน)
#    พอมาขอ "กว้างเท่ากัน" ⇒ ต้องถอด w-full ออก ไม่ใช่ไปทำตัวอื่นให้เต็มตาม
#    📌 คำสั่ง UI 2 รอบอาจขัดกันเอง — ต้องอ่านว่าอันหลังแทนอันแรก ไม่ใช่เพิ่มเข้าไป
# 🪤 ดาวน์โหลดไปขวา = ย้ายไป **ท้ายแถว** (แถวเรียงซ้าย→ขวา) — รอบที่แล้วผมย้ายไปซ้ายตามที่เข้าใจผิด
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'mn-lb-eq'
EQ = ('justify-center !h-10 !rounded-xl !text-[13.5px] font-bold !flex-1 !basis-0 !min-w-[132px] '
      '!min-h-[48px] @[420px]:!min-h-0 ' + MARK)


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def norm_row(row):
    """ปุ่มกว้างเท่ากันทุกตัว + ดาวน์โหลดไปอยู่ขวาสุด · คงสีเดิมของแต่ละปุ่มไว้"""
    kids = row.get('card') or []
    for k in kids:
        old = str(k.get('className', ''))
        colour = ' '.join(w for w in old.split()
                          if w.startswith(('!bg-', '!text-', '!from-', '!to-', 'border', '!border', 'backdrop'))
                          and 'text-[1' not in w)          # เก็บเฉพาะคลาสสี/ขอบ ทิ้งคลาสขนาดทั้งหมด
        k['className'] = (EQ + ' ' + colour).strip()
    dl = [k for k in kids if k.get('el') == 'download-button']
    if dl:
        row['card'] = [k for k in kids if k is not dl[0]] + dl      # ดาวน์โหลดท้ายแถว = ขวาสุด
    row['className'] = 'w-full flex-wrap gap-2 items-stretch ' + MARK
    return len(row['card'])


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)
    if MARK in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    # ── ① เก็บแถบของกริดไว้เป็นต้นแบบ (มีปุ่มครบที่สุด) ก่อนแก้ ──
    proto = []
    def grab(n):
        arr = n.get('lightboxActions')
        if isinstance(arr, list) and arr and any(
                k.get('label') == 'Gen วิดีโอใหม่' for k in (arr[0].get('card') or [])):
            proto.append(arr)
    walk(cfg, grab)
    assert proto, 'หาแถบปุ่มต้นแบบ (ที่มี Gen วิดีโอใหม่) ไม่เจอ'
    tpl = json.loads(json.dumps(proto[0], ensure_ascii=False))

    # ── ② ปรับทุกแถบที่มีอยู่: กว้างเท่ากัน + ดาวน์โหลดขวาสุด ──
    rows = []
    def fix(n):
        arr = n.get('lightboxActions')
        if isinstance(arr, list):
            for row in arr:
                rows.append(norm_row(row))
    walk(cfg, fix)
    assert len(rows) == 2, 'ควรมีแถบปุ่มเดิม 2 ชุด (กริด + คลังคลิป) เจอ %d' % len(rows)

    # ── ③ ใส่แถบปุ่มให้ media-slot วิดีโอของ "มุมมองรายการ" ที่ยังไม่มี ──
    added = []
    def add(n):
        if n.get('el') != 'media-slot':
            return
        if not isinstance(n.get('segments'), list):
            return                                            # เอาเฉพาะช่องวิดีโอ (คลิปรวมหลายช่วง)
        if n.get('lightboxActions'):
            return
        row = json.loads(json.dumps(tpl, ensure_ascii=False))
        norm_row(row[0])
        n['lightboxActions'] = row
        added.append(str(n.get('src')))
    walk(cfg, add)
    assert len(added) == 1, 'ควรเติมแถบปุ่มให้ช่องวิดีโอของมุมมองรายการ 1 จุด (เจอ %d: %s)' % (len(added), added)

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before

    # ── ยาม ──
    checked = []
    def chk(n):
        arr = n.get('lightboxActions')
        if not isinstance(arr, list):
            return
        for row in arr:
            kids = row.get('card') or []
            checked.append(len(kids))
            assert all(MARK in str(k.get('className', '')) for k in kids), 'ปุ่มในแถบยังไม่ถูกปรับครบ'
            assert all('!flex-1' in str(k.get('className', '')) for k in kids), 'ปุ่มต้องกว้างเท่ากันทุกตัว'
            assert not any('w-full' in str(k.get('className', '')).split() for k in kids), \
                '🔴 ยังมีปุ่ม w-full อยู่ — จะกว้างไม่เท่าตัวอื่น'
            dl = [i for i, k in enumerate(kids) if k.get('el') == 'download-button']
            if dl:
                assert dl[0] == len(kids) - 1, '🔴 ปุ่มดาวน์โหลดต้องอยู่ขวาสุด (ตัวท้ายของแถว)'
    walk(cfg, chk)
    assert len(checked) == 3, 'ต้องมีแถบปุ่ม 3 ชุด (รายการ + กริด + คลังคลิป) เจอ %d' % len(checked)

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v38 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① ปุ่มในแถบกว้างเท่ากันทุกตัว (ถอด w-full ที่ทำให้ตัวหนึ่งกินเต็มแถว)')
    print('   ② ดาวน์โหลดย้ายไปขวาสุดทุกแถบ')
    print('   ③ มุมมองรายการได้แถบปุ่มตอนดูวิดีโอเต็มจอแล้ว (เดิมไม่มีเลย) — รวมเป็น %d ชุด · ปุ่มต่อแถว %s' % (len(checked), checked))


main()
