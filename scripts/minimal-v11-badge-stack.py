#!/usr/bin/env python3
# minimal v11 — ป้าย "จำนวนบอร์ด" ย้ายไปซ้อนเหนือป้าย "คลิปที่ n/n" (2026-09-10 · คำสั่งพี่หมี จากภาพหน้าจอ)
#
# อาการ: แถวล่างของการ์ดที่วาดบอร์ดแล้วมีของ 3 ชิ้นเรียงกันในแถวเดียว
#   [ชื่อสินค้า] [คลิปที่ 1/3] [▣ 3]     ← style.flexWrap = nowrap
#   ⇒ ชื่อสินค้าถูกบีบจนแตกเป็น 3 บรรทัด ("Ho… / รอ… / วิ่ง") บนมือถือ
#   ⇒ และป้าย "คลิปที่ n/n" ไปลอยอยู่กลางแถว ไม่ชิดขวาเหมือนการ์ดที่ยังรอคิว = สองสถานะวางของคนละที่
#
# แก้: ยุบป้าย 2 ใบเป็น **คอลัมน์เดียวชิดขวา** (บอร์ดอยู่บน · คลิปอยู่ล่าง)
#   [ชื่อสินค้า] ................ [▣ 3]
#                                [คลิปที่ 1/3]
#   ⇒ แถวเหลือลูก 2 ชิ้น ชื่อสินค้าได้ความกว้างคืน · ป้ายคลิปชิดขวาตรงกับการ์ดที่รอคิวเป๊ะ
#
# 🔑 ทำไมป้ายคลิปถึงชิดขวาได้เอง: `ml-auto` ย้ายจากป้ายบอร์ดไปอยู่ที่ "คอลัมน์" แทน
#    ⇒ ตอน 10 วิ (ป้ายบอร์ดถูก `when` ปิด) คอลัมน์เหลือป้ายคลิปใบเดียว **ยังชิดขวาเหมือนเดิม**
#    ⇒ ไม่ต้องเขียนเงื่อนไขแยกสำหรับ 10 วิ เลยสักบรรทัด
#
# 🪤 ห้ามใส่ `ml-auto` ทั้งที่คอลัมน์และที่ป้ายข้างใน — ป้ายข้างในจะดัน `items-end` เพี้ยน
#    (โรคเดียวกับ `flex-1` ทับ `basis-full` · ผู้ชนะตัดสินด้วยลำดับใน stylesheet ไม่ใช่ลำดับใน class)
#
# รันซ้ำได้ (idempotent)
import json, sys, os, copy

REAL_BADGE = 'คลิปที่ {item.clipIndex}/{values.clipsPerProduct}'
COL_CLS = 'ml-auto shrink-0 flex flex-col items-end gap-1'


def boxes(n, path='$'):
    if isinstance(n, dict):
        if isinstance(n.get('card'), list):
            yield path, n
        for k, v in n.items():
            yield from boxes(v, path + '.' + k)
    elif isinstance(n, list):
        for i, v in enumerate(n):
            yield from boxes(v, path + '[%d]' % i)


def is_board_badge(c):
    """แถวป้ายจำนวนบอร์ด = row ที่มีไอคอน burst_mode"""
    return c.get('el') == 'row' and any(
        isinstance(d, dict) and d.get('icon') == 'burst_mode' for d in (c.get('card') or []))


def patch(cfg):
    log = []
    for path, b in list(boxes(cfg)):
        kids = [c for c in b['card'] if isinstance(c, dict)]
        clip = next((c for c in kids if c.get('el') == 'text' and c.get('value') == REAL_BADGE), None)
        board = next((c for c in kids if is_board_badge(c)), None)
        if clip is None or board is None:
            continue                      # แถวที่ไม่มีป้ายบอร์ด (เช่นการ์ดที่ยังไม่วาด) ไม่ต้องแตะ
        # รันซ้ำ: ถ้าทั้งคู่อยู่ในคอลัมน์เดียวกันแล้ว = เสร็จแล้ว
        if b.get('className') == COL_CLS:
            continue

        i = min(b['card'].index(clip), b['card'].index(board))
        b['card'].remove(clip)
        b['card'].remove(board)
        # ★ml-auto ต้องอยู่ที่คอลัมน์ที่เดียว — ถอดออกจากป้ายบอร์ดก่อน ไม่งั้นชนกันเอง
        board['className'] = ' '.join(t for t in (board.get('className') or '').split() if t != 'ml-auto')
        col = {"el": "box", "className": COL_CLS, "card": [board, clip]}   # บอร์ดอยู่บน · คลิปอยู่ล่าง
        b['card'].insert(i, col)
        log.append('  · ยุบป้าย 2 ใบเป็นคอลัมน์ชิดขวา @%s' % path[-42:])
    return log


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = sys.argv[1:] or [os.path.join(here, 'minimal-dev.json'), os.path.join(here, 'minimal.json')]
    for f in files:
        cfg = json.load(open(f, encoding='utf-8'))
        before = json.dumps(cfg, ensure_ascii=False, sort_keys=True)
        print('══', os.path.basename(f))
        for line in patch(cfg):
            print(line)
        if json.dumps(cfg, ensure_ascii=False, sort_keys=True) == before:
            print('  (ไม่มีอะไรเปลี่ยน — แพตช์ลงไปแล้ว)')
        else:
            json.dump(cfg, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('  ✅ เขียนแล้ว')


if __name__ == '__main__':
    main()
