#!/usr/bin/env python3
# minimal-v27-grid-board-bar.py — มุมมองกริด (= โหมดออโต้) ได้แถบเลื่อนบอร์ด + ไอคอน "วาดใบนี้ใหม่"
# ที่มา: พี่หมี 2026-09-21 ถามว่า v26 มีในโหมดออโต้ไหม → ตรวจแล้วพบ 2 เรื่อง
#   ① กล่องมุมมองรายการถูกกั้น `viewMode=='cards' OR (viewMode=='' AND mode!='auto')`
#      ⇒ โหมดออโต้ได้มุมมองกริดเสมอ และปุ่มสลับมุมมองก็ถูกซ่อนในโหมดออโต้ ⇒ เข้าไม่ถึง v26 เลย
#   ② 🔴 กริด **ไม่มีแถบ ‹ บอร์ด n/m ›** — ตัวควบคุม bview มีแค่ 2 ตัวและอยู่ฝั่งรายการทั้งคู่
#      ⇒ คนใช้โหมดออโต้ "เลื่อนดูบอร์ดใบ 2/3 ในการ์ดไม่ได้เลย" (เห็นได้ทางเดียวคือเปิดภาพเต็มจอ)
# แก้: ยกแถบจากฝั่งรายการมาวางในกล่องไทล์ของกริด + เติมปุ่มไอคอน ↺ ท้ายแถบ (force op ของใบที่ดูอยู่)
# 🪤 แถบวางเป็นลูกของกล่องไทล์ (className `relative`) ต่อจาก overlay ⇒ อยู่ใต้ภาพ ไม่ทับเนื้อบอร์ด
# 🪤 ปุ่ม ↺ 3 ตัว (ใบ 1/2/3) โชว์ทีละตัวตาม {item.bview} — เงื่อนไขชุดเดียวกับที่ไทล์ใช้เลือกใบ
# รันซ้ำได้: ตรวจ marker `mn-grid-board-bar`
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'mn-grid-board-bar'
GRID_TILES = '/phases[0]/form[3]/card[0]/card[7]/card[0]/card[0]/card[2]'
LIST_BAR = '/phases[0]/form[3]/card[0]/card[6]/card[0]/card[0]/card[0]/card[0]/card[0]/card[0]/card[4]/card[3]'
ICON_CLASS = ('justify-center !gap-0 !w-11 !h-11 @[420px]:!w-8 @[420px]:!h-8 !min-h-0 !p-0 !rounded-lg '
              '!bg-[var(--ev-surface2)] !text-[var(--ev-text)] !border-0 ' + MARK)


def get(node, path):
    for part in path.strip('/').split('/'):
        if '[' in part:
            k, i = part[:-1].split('[')
            node = node[k][int(i)]
        else:
            node = node[part]
    return node


def bview_is(n):
    eq = lambda v: {'op': 'eq', 'a': {'op': 'max', 'a': {'op': 'concat', 'parts': ['{item.bview}']}, 'b': 1}, 'b': v}
    return {'op': 'not', 'a': {'op': 'or', 'list': [eq(2), eq(3)]}} if n == 1 else eq(n)


def redo_icon(n, op):
    return {
        'el': 'retry-button', 'op': op, 'chain': [op],
        'label': '', 'icon': 'replay', 'variant': 'ghost',
        'className': ICON_CLASS,
        'when': {'op': 'and', 'list': [
            bview_is(n),
            {'op': 'not', 'a': {'op': 'or', 'list': [
                {'op': 'eq', 'a': '{item.status}', 'b': 'running'},
                {'op': 'eq', 'a': '{item.meta.retrying}', 'b': '1'},
            ]}},
        ]},
    }


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)

    tiles = get(cfg, GRID_TILES)
    slots = [k.get('src') for k in tiles['card'] if k.get('el') == 'media-slot']
    assert slots == ['{item.slots.board}', '{item.slots.board2}', '{item.slots.board3}'], \
        'ไม่ใช่กล่องไทล์บอร์ดของกริด — โครงเปลี่ยน ยกเลิก (slots=%s)' % slots
    if MARK in json.dumps(tiles, ensure_ascii=False):
        print('⏭  กริดมีแถบนี้อยู่แล้ว — ไม่ทำอะไร')
        return

    bar = json.loads(json.dumps(get(cfg, LIST_BAR), ensure_ascii=False))   # ยกมาทั้งดุ้น (ปุ่ม ‹ ›, ป้าย บอร์ด n/m, when svSec>10)
    assert bar['el'] == 'row' and len(bar['card']) == 3, 'แม่แบบแถบฝั่งรายการเปลี่ยนโครง ยกเลิก'
    # กริดเป็นกล่อง absolute/relative ⇒ แถบต้องเป็นชั้นบนสุดของกล่อง และกดได้
    bar['className'] = (bar['className'].replace('w-full mt-2 @[420px]:mt-1.5', 'w-full mt-2')
                        + ' relative z-20 ' + MARK)
    bar['card'] = [bar['card'][0], bar['card'][1], bar['card'][2]] + [redo_icon(n, op) for n, op in
                                                                     ((1, 'mnBoard'), (2, 'mnBoard2'), (3, 'mnBoard3'))]
    # วางไว้นอกกล่องภาพ (ต่อท้ายกล่องไทล์) — ไม่ทับเนื้อบอร์ด
    tiles['card'].append(bar)

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before, 'ไฟล์ไม่เปลี่ยน — แพตช์ไม่ทำงาน'
    icons = [c for c in bar['card'] if c.get('el') == 'retry-button']
    assert len(icons) == 3 and [c['op'] for c in icons] == ['mnBoard', 'mnBoard2', 'mnBoard3']
    assert all(len(c['chain']) == 1 for c in icons), 'ไอคอนต้องสั่ง op เดียว'
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ กริดได้แถบ ‹ บอร์ด n/m › + ไอคอน ↺ (วาดใบที่ดูอยู่ใหม่) แล้ว — %s' % os.path.basename(src))
    print('   ⇒ โหมดออโต้เลื่อนดูบอร์ดใบ 2/3 ได้ และวาดใหม่ทีละใบได้ (ของเดิมทำไม่ได้ทั้งคู่)')


main()
