#!/usr/bin/env python3
# hardsell-v8-lightbox-labels.py — เช็กลิสต์ ⑧⑨ ของมาตรฐานหลายช่วง (minimal · พี่หมีทักของเขา 3 รอบกว่าจะครบ)
#
# ⑧ แถบปุ่มในหน้าดูสื่อเต็มจอ (lightboxActions) ต้องครบทุกมุมมอง · ดาวน์โหลดขวาสุด · ทุกปุ่มกว้างเท่ากัน
#    ที่ hardsell เป็นอยู่ (ตรวจแล้ว ไม่ได้เดา):
#      · มุมมองกริด `card[8]` วิดีโอ → มีแถบปุ่ม ✅ (ดาวน์โหลดขวาสุดอยู่แล้ว)
#      · **มุมมองรายการ `card[7]` วิดีโอ → ไม่มีแถบปุ่มเลย** 🔴 (อาการเดียวกับที่พี่หมีทัก minimal)
#      · หน้าคลังคลิป `form[4]` → มี แต่ **ดาวน์โหลดอยู่ซ้ายสุด** 🔴
# ⑨ ถ้อยคำ: ห้ามมี 2 ปุ่มชื่อซ้ำในแถวเดียวกัน · แยก "Gen วิดีโอใหม่" / "Gen บอร์ดใหม่"
#    · ปุ่มที่ทำงานกับ **บอร์ด** ใช้คำว่า "บอร์ด" ไม่ใช่ "ภาพ" — เพราะ hardsell มีคำว่า "ภาพ" 2 ความหมายจริง
#      ("เลือกภาพ" 14 ปุ่ม = บอร์ด 8 + รูปสินค้า/ใบหน้า 6) ⇒ ผู้ใช้แยกไม่ออกว่าปุ่มไหนทำอะไร
#    🪤 **ห้ามกรองด้วย label** (กับดักที่ minimal เตือน) — ต้องกรองด้วย "ปุ่มนี้ชี้ slot บอร์ดหรือเปล่า"
#       ไม่งั้นไปโดนปุ่มเลือกรูปสินค้า/ใบหน้า ซึ่งคนละความหมายและต้องคงคำว่า "ภาพ" ไว้
# ⚠️ ไม่แตะข้อความบรรยาย (เช่น "ยังไม่มีภาพ — ต้อง Gen ภาพก่อน") — เป็นถ้อยคำที่พี่หมีเป็นเจ้าของ
#    จดไว้ถามแทน (ถ้าเปลี่ยนปุ่มเป็น "บอร์ด" แล้วข้อความรอบ ๆ ยังพูดว่า "ภาพ" จะไม่ตรงกัน)
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD_SLOT = '{item.slots.board}'


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
    if 'Gen บอร์ดใหม่' in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    root = cfg['phases'][0]['form'][3]['card'][0]['card']
    cards_view, grid_view = root[7], root[8]

    # ── ⑧-1 ยกแถบปุ่มจากมุมมองกริดไปมุมมองรายการ ──
    def video_slot(node):
        out = []
        walk(node, lambda n: out.append(n) if n.get('el') == 'media-slot' and n.get('src') == '{item.slots.video}' else None)
        return out

    g_vid, c_vid = video_slot(grid_view), video_slot(cards_view)
    assert len(g_vid) == 1 and len(c_vid) == 1, 'ต้องเจอ media-slot วิดีโอฝั่งละ 1 ตัว (กริด %d · รายการ %d)' % (len(g_vid), len(c_vid))
    assert g_vid[0].get('lightboxActions'), 'มุมมองกริดต้องมีแถบปุ่มอยู่แล้ว'
    assert not c_vid[0].get('lightboxActions'), 'มุมมองรายการมีแถบปุ่มอยู่แล้ว — ตรวจใหม่ก่อนแก้'
    c_vid[0]['lightboxActions'] = json.loads(json.dumps(g_vid[0]['lightboxActions']))

    # ── ⑨ ป้ายปุ่มในแถบ: แยก "Gen วิดีโอใหม่" / "Gen บอร์ดใหม่" (ห้ามชื่อซ้ำในแถวเดียวกัน) ──
    renamed = []
    for slot in (g_vid[0], c_vid[0]):
        for b in slot['lightboxActions'][0]['card']:
            if b.get('label') != 'Gen ใหม่':
                continue
            b['label'] = 'Gen วิดีโอใหม่' if b.get('menu') else 'Gen บอร์ดใหม่'
            renamed.append(b['label'])
    assert len(renamed) == 4, 'ต้องเปลี่ยนป้าย "Gen ใหม่" 4 ปุ่ม (2 แถบ × 2) เจอ %d' % len(renamed)

    # ── ⑧-2 หน้าคลังคลิป: ดาวน์โหลดต้องขวาสุด ──
    gal = []
    walk(cfg['phases'][0]['form'][4], lambda n: gal.append(n) if isinstance(n.get('lightboxActions'), list) else None)
    assert len(gal) == 1, 'หน้าคลังคลิปต้องมีแถบปุ่ม 1 จุด (เจอ %d)' % len(gal)
    row = gal[0]['lightboxActions'][0]['card']
    dl = [i for i, b in enumerate(row) if b.get('el') == 'download-button']
    assert len(dl) == 1, 'แถบนี้ต้องมีปุ่มดาวน์โหลด 1 ปุ่ม'
    if dl[0] != len(row) - 1:
        row.append(row.pop(dl[0]))

    # ── ⑨ ปุ่มที่ทำงานกับบอร์ด: "ภาพ" → "บอร์ด" (กรองด้วย slot ไม่ใช่ label) ──
    board_renamed = []

    def relabel(n):
        el, lab = n.get('el'), n.get('label')
        if not isinstance(lab, str):
            return
        targets_board = (n.get('into') == BOARD_SLOT) or (n.get('chain') == ['mnBoard']) or (n.get('op') == 'mnBoard')
        if not targets_board:
            return
        new = {'Gen ภาพ': 'Gen บอร์ด', 'Gen ภาพใหม่': 'Gen บอร์ดใหม่', 'เลือกภาพ': 'เลือกบอร์ด'}.get(lab)
        if new:
            n['label'] = new
            board_renamed.append((el, lab, new))

    walk(cfg, relabel)

    # ── ยาม ──
    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    # ห้ามมีป้ายซ้ำในแถบปุ่มเดียวกัน
    for slot in (g_vid[0], c_vid[0]):
        labs = [b.get('label') for b in slot['lightboxActions'][0]['card'] if isinstance(b.get('label'), str)]
        assert len(labs) == len(set(labs)), 'แถบปุ่มมีป้ายซ้ำ: %s' % labs
    # ปุ่มเลือกรูปสินค้า/ใบหน้า ต้องยังเป็น "เลือกภาพ" (ห้ามโดนลูกหลง)
    keep = []
    walk(cfg, lambda n: keep.append(n.get('into')) if n.get('el') == 'pick-button' and n.get('label') == 'เลือกภาพ' else None)
    assert keep and all(k != BOARD_SLOT for k in keep), 'ปุ่ม "เลือกภาพ" ที่เหลือต้องไม่ใช่ปุ่มบอร์ด: %s' % keep
    assert len(keep) == 6, 'ปุ่มเลือกรูปสินค้า/ใบหน้าต้องเหลือ 6 ปุ่ม (เจอ %d)' % len(keep)
    # ดาวน์โหลดขวาสุดทั้ง 3 แถบ
    bars = []
    walk(cfg, lambda n: bars.append(n['lightboxActions'][0]['card']) if isinstance(n.get('lightboxActions'), list) else None)
    assert len(bars) == 3, 'ต้องมีแถบปุ่ม 3 จุด (กริด · รายการ · คลังคลิป) เจอ %d' % len(bars)
    for bar in bars:
        dls = [i for i, b in enumerate(bar) if b.get('el') == 'download-button']
        assert dls and dls[0] == len(bar) - 1, 'ปุ่มดาวน์โหลดต้องอยู่ขวาสุดทุกแถบ'
    # เมนูยังครบ 5 + ธง aux เดิม
    menus = []
    walk(cfg, lambda n: menus.append(n) if n.get('menu') else None)
    assert len(menus) == 6, 'ปุ่มเมนูต้องเป็น 6 ตัวหลังยกแถบไปมุมมองรายการ (เดิม 5 + สำเนา 1) เจอ %d' % len(menus)
    ops = {o['id']: o for o in cfg['ops']}
    assert ops['mnTrans'].get('aux') is True

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v8 ลงแล้ว — %s' % os.path.basename(src))
    print('   ⑧ ยกแถบปุ่มไปมุมมองรายการ (เดิมไม่มีเลย) · ดาวน์โหลดขวาสุดครบ 3 แถบ')
    print('   ⑨ แยกป้าย "Gen วิดีโอใหม่" / "Gen บอร์ดใหม่" (ห้ามซ้ำในแถวเดียว) · ปุ่มบอร์ด %d ปุ่ม "ภาพ"→"บอร์ด"' % len(board_renamed))
    print('   🪤 ปุ่มเลือกรูปสินค้า/ใบหน้า 6 ปุ่ม ยังเป็น "เลือกภาพ" ตามเดิม (กรองด้วย slot ไม่ใช่ label)')


main()
