#!/usr/bin/env python3
# minimal-v26-board-retry-one.py — ปุ่ม "วาดบอร์ดนี้ใหม่" ใต้ไทล์บอร์ด (วาดใหม่เฉพาะช่วงที่กำลังดู)
# ที่มา: พี่หมี 2026-09-21 — คลิป 30 วิ บอร์ด 2 เพี้ยน อยากวาดใหม่เฉพาะใบนั้น
#   ของเดิม: ทุกปุ่มบอร์ดสั่ง chain [mnBoard3, mnBoard2, mnBoard] ⇒ "Gen ภาพใหม่" = ทำใหม่ทั้ง 3 ใบ (เผาเครดิต 3)
#            ส่วน "ลองใหม่"/"Gen ภาพ" (ไม่ force) ข้ามช่องที่มีภาพแล้ว ⇒ ใบที่เพี้ยนไม่มีวันถูกวาดใหม่
#   ของใหม่: ปุ่มเดียวใต้ไทล์ · ผูกกับใบที่ผู้ใช้กำลังดู ({item.bview}) · force เฉพาะ op ของช่วงนั้น
# 🪤 ปุ่มเป็น retry-button + chain ที่มี op เดียว ⇒ force เฉพาะช่วงนั้น ไม่แตะช่วงอื่น
# 🪤 โชว์เฉพาะ svSec > 10 (คลิป 10 วิ มีใบเดียว — "Gen ภาพใหม่" เดิมทำงานถูกอยู่แล้ว)
# รันซ้ำได้: ตรวจ marker `mn-board-retry-one` ก่อนเติม
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'mn-board-retry-one'
# ตำแหน่งกล่องไทล์บอร์ด (list view) — media-slot board/board2/board3 + แถวชิป
TILE_BOX = '/phases[0]/form[3]/card[0]/card[6]/card[0]/card[0]/card[0]/card[0]/card[0]/card[0]/card[4]'

BTN_CLASS = ('w-full justify-center !h-10 !rounded-xl !text-[13px] @[640px]:!text-[12px] font-bold '
             'border border-[var(--ev-border)] !bg-[var(--ev-surface)] !min-h-[48px] @[420px]:!min-h-0 ' + MARK)


def get(node, path):
    for part in path.strip('/').split('/'):
        if '[' in part:
            k, i = part[:-1].split('[')
            node = node[k][int(i)]
        else:
            node = node[part]
    return node


def bview_is(n):
    """เงื่อนไขเดียวกับที่ไทล์ใช้เลือกใบ — ใบ 1 = ไม่ใช่ 2 และไม่ใช่ 3"""
    eq = lambda v: {'op': 'eq', 'a': {'op': 'max', 'a': {'op': 'concat', 'parts': ['{item.bview}']}, 'b': 1}, 'b': v}
    if n == 1:
        return {'op': 'not', 'a': {'op': 'or', 'list': [eq(2), eq(3)]}}
    return eq(n)


def button(n, op):
    # โชว์เมื่อ: กำลังดูใบนี้ ∧ คลิปยาวกว่า 10 วิ ∧ ไม่ได้กำลังรันอยู่ (กติกาเดียวกับปุ่ม "ลองใหม่")
    return {
        'el': 'retry-button', 'op': op, 'chain': [op],
        'label': 'วาดบอร์ดนี้ใหม่', 'icon': 'replay', 'variant': 'ghost',
        'className': BTN_CLASS,
        'when': {'op': 'and', 'list': [
            bview_is(n),
            {'op': 'gt', 'a': '{values.svSec}', 'b': 10},
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

    box = get(cfg, TILE_BOX)
    kids = box['card']
    # ยาม ①: ต้องเป็นกล่องไทล์จริง (media-slot 3 ใบ board/board2/board3)
    slots = [k.get('src') for k in kids if k.get('el') == 'media-slot']
    assert slots == ['{item.slots.board}', '{item.slots.board2}', '{item.slots.board3}'], \
        'ไม่ใช่กล่องไทล์บอร์ดที่คาด — โครง config เปลี่ยน ยกเลิก (slots=%s)' % slots

    if MARK in json.dumps(kids, ensure_ascii=False):
        print('⏭  มีปุ่มนี้อยู่แล้ว (marker %s) — ไม่ทำอะไร' % MARK)
        return

    row = {'el': 'row', 'className': 'w-full mt-1.5 @[420px]:mt-1', 'card': [button(n, op) for n, op in
           ((1, 'mnBoard'), (2, 'mnBoard2'), (3, 'mnBoard3'))]}
    kids.append(row)

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before, 'ไฟล์ไม่เปลี่ยน — แพตช์ไม่ทำงาน'
    # ยาม ②: ต้องเติมปุ่ม 3 ตัว และแต่ละตัวสั่ง op เดียว
    added = [c for c in row['card']]
    assert len(added) == 3 and all(len(c['chain']) == 1 for c in added), 'ปุ่มต้องสั่ง op เดียวต่อตัว'
    assert [c['op'] for c in added] == ['mnBoard', 'mnBoard2', 'mnBoard3']

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ เติมปุ่ม "วาดบอร์ดนี้ใหม่" 3 ตัว (ใบ 1/2/3) ลง %s' % os.path.basename(src))
    print('   แต่ละตัว force เฉพาะ op ของช่วงนั้น · โชว์เฉพาะคลิป > 10 วิ · ผูกกับใบที่กำลังดู {item.bview}')


main()
