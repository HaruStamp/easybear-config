#!/usr/bin/env python3
# minimal-v37-menu-fixes.py — 4 ข้อที่พี่หมีเจอหลังกดใช้เมนูจริง (2026-09-22) · ข้อที่ 5 เป็นของ engine (เมนูโดน clip)
#
# 🔴🔴 ① **บั๊กของผมเองใน v36: ปุ่ม "Gen วิดีโอใหม่" หายตอน 20/30 วิ**
#     v35 สร้างกล่อง [ปุ่มเดิม(when: ไม่เกิน 10 วิ) · ปุ่มเปิดเมนู · เมนู] — `when` นั้นแปลว่า
#     "โชว์ปุ่มเดิมเฉพาะตอน 10 วิ" เพราะ 20/30 วิ ใช้ปุ่มเปิดเมนูแทน
#     v36 ยกคุณสมบัติจาก "ปุ่มเดิม" มาทำปุ่มเมนู **แล้วลอก `when` ติดมาด้วย** ⇒ ปุ่มใหม่โชว์เฉพาะ 10 วิ
#     = ตรงข้ามกับที่ควรเป็น (เมนูมีไว้สำหรับ 20/30 วิ!) · พี่หมีเห็นการ์ดที่ไม่มีปุ่ม Gen วิดีโอใหม่เลย
#     📌 บทเรียน: **เวลารวมปุ่ม 2 ตัวเป็นตัวเดียว `when` ของแต่ละตัวมีความหมายคนละอย่าง — ห้ามลอกมาเฉย ๆ**
#        ของที่ต้องเก็บคือ `when` ที่เป็น "เงื่อนไขของสถานะงาน" (เช่น มีวิดีโอแล้วหรือยัง)
#        ของที่ต้องทิ้งคือ `when` ที่เป็น "เงื่อนไขว่าจะโชว์ปุ่มไหนในคู่" (ซึ่งเมนูมาแทนแล้ว)
# ② ปุ่ม "Gen วิดีโอใหม่" ต้องมีในการ์ดสถานะ "มีวิดีโอแล้วบางส่วน" ด้วย (เดิมมีแต่ใน "ครบแล้ว")
# ③ คำในปุ่ม: ภาพ → บอร์ด (Gen บอร์ดใหม่ · เลือกบอร์ด · Gen บอร์ด) — เฉพาะปุ่มที่ทำงานกับบอร์ดจริง
#    🪤 ปุ่ม "เลือกภาพ" ของรูปสินค้า/รูปใบหน้า **ห้ามแตะ** (คนละความหมาย) ⇒ กรองด้วย "เมนูชี้ slot บอร์ดไหม"
# ④ ป้ายในเมนูเลือกไฟล์: "ใส่เป็นช่วง N" → "ช่วง N" (พี่หมีสั่ง — สั้นกว่า อ่านเร็วกว่า)
# ⑤ แถบปุ่มตอนดูเต็มจอ: เรียง [ดาวน์โหลด] ก่อน แล้วค่อย [Gen …ใหม่] ให้เหมือนหน้าคลังคลิป
#    + แยกป้าย "Gen ใหม่" 2 ตัวที่ซ้ำกันให้รู้ว่าอันไหนวิดีโอ อันไหนบอร์ด
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'Gen บอร์ดใหม่'          # ป้ายใหม่ = ตัวชี้ว่าแพตช์ลงแล้ว
LEFTOVER = {'op': 'not', 'a': {'op': 'gt', 'a': '{values.svSec}', 'b': 10}}
BRD_OPS = {'mnBoard', 'mnBoard2', 'mnBoard3'}


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def menu_kind(el):
    """ปุ่มนี้ทำงานกับบอร์ดหรือวิดีโอ — ดูจากเป้าของข้อแรกในเมนู"""
    it = (el.get('menu') or [{}])[0]
    tgt = it.get('chain') or ([it['op']] if it.get('op') else []) or []
    if tgt:
        return 'board' if set(tgt) & BRD_OPS else 'video'
    into = str(it.get('into') or '')
    return 'board' if 'board' in into else 'video'


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)
    if MARK in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    # ── ① ถอด `when` ที่ตกค้างจาก v35 ──
    stripped = []
    def fix_when(n):
        if not n.get('menu') or not n.get('when'):
            return
        w = n['when']
        if w == LEFTOVER:                                  # when มีแต่ของตกค้าง → ถอดทิ้งทั้งก้อน
            del n['when']; stripped.append(n.get('label'))
        elif w.get('op') == 'and' and isinstance(w.get('list'), list) and LEFTOVER in w['list']:
            rest = [x for x in w['list'] if x != LEFTOVER]  # เหลือเงื่อนไขสถานะงานไว้
            n['when'] = rest[0] if len(rest) == 1 else {'op': 'and', 'list': rest}
            stripped.append(n.get('label'))
    walk(cfg, fix_when)
    assert len(stripped) == 2, 'ต้องถอด when ตกค้าง 2 ปุ่ม (เจอ %d: %s)' % (len(stripped), stripped)

    # ── ④ ป้ายในเมนูเลือกไฟล์ ──
    renamed_items = 0
    def fix_items(n):
        nonlocal renamed_items
        for it in (n.get('menu') or []):
            lb = it.get('label', '')
            if lb.startswith('ใส่เป็นช่วง '):
                it['label'] = lb.replace('ใส่เป็นช่วง ', 'ช่วง ', 1); renamed_items += 1
    walk(cfg, fix_items)
    assert renamed_items == 33, 'ป้ายในเมนูเลือกไฟล์ต้องมี 33 ข้อ (11 ปุ่ม × 3) เจอ %d' % renamed_items

    # ── ③ คำในปุ่ม: ภาพ → บอร์ด (เฉพาะปุ่มที่ทำงานกับบอร์ด) ──
    LABEL_MAP = {'Gen ภาพใหม่': 'Gen บอร์ดใหม่', 'เลือกภาพ': 'เลือกบอร์ด', 'Gen ภาพ': 'Gen บอร์ด'}
    renamed_btn = []
    def fix_label(n):
        lb = n.get('label')
        if not isinstance(lb, str) or lb not in LABEL_MAP:
            return
        if n.get('menu'):
            if menu_kind(n) != 'board':
                return
        elif n.get('el') == 'gen-button':
            ch = n.get('chain') or []
            if not (set(ch) & BRD_OPS):
                return                                      # ปุ่มรูปสินค้า/ใบหน้า = ไม่มี chain บอร์ด ⇒ ไม่แตะ
        else:
            return
        n['label'] = LABEL_MAP[lb]; renamed_btn.append(lb)
    walk(cfg, fix_label)

    # ── ⑤ แถบปุ่มตอนดูเต็มจอ: ดาวน์โหลดขึ้นก่อน + แยกป้าย "Gen ใหม่" ──
    fixed_lb = 0
    def fix_lightbox(n):
        nonlocal fixed_lb
        arr = n.get('lightboxActions')
        if not isinstance(arr, list):
            return
        for row in arr:
            kids = row.get('card')
            if not isinstance(kids, list) or len(kids) < 2:
                continue
            for k in kids:
                if k.get('label') == 'Gen ใหม่' and k.get('menu'):
                    k['label'] = 'Gen วิดีโอใหม่' if menu_kind(k) == 'video' else 'Gen บอร์ดใหม่'
            dl = [k for k in kids if k.get('el') == 'download-button']
            if dl:                                          # ดาวน์โหลดขึ้นเป็นตัวแรก (เหมือนหน้าคลังคลิป)
                rest = [k for k in kids if k is not dl[0]]
                row['card'] = dl + rest
                fixed_lb += 1
    walk(cfg, fix_lightbox)

    # ── ② เพิ่มปุ่ม "Gen วิดีโอใหม่" ในการ์ดสถานะที่ยังไม่มี ──
    added = 0
    proto = []
    def grab(n):
        if n.get('label') == 'Gen วิดีโอใหม่' and n.get('menu'):
            proto.append(n)
    walk(cfg, grab)
    assert proto, 'หาปุ่ม Gen วิดีโอใหม่ ต้นแบบไม่เจอ'
    tpl = proto[0]
    def add_btn(n):
        nonlocal added
        kids = n.get('card')
        if not isinstance(kids, list):
            return
        i_pick = next((i for i, k in enumerate(kids)
                       if isinstance(k, dict) and k.get('label') == 'เลือกวิดีโอ' and k.get('menu')), None)
        if i_pick is None:
            return
        if any(isinstance(k, dict) and k.get('label') == 'Gen วิดีโอใหม่' for k in kids):
            return                                          # การ์ดนี้มีอยู่แล้ว
        btn = json.loads(json.dumps(tpl, ensure_ascii=False))
        btn.pop('when', None)
        kids.insert(i_pick, btn); added += 1
    walk(cfg, add_btn)

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    assert json.dumps(LEFTOVER, ensure_ascii=False) not in json.dumps(
        [n for n in []], ensure_ascii=False) or True
    # ยาม: ห้ามเหลือปุ่มเมนูที่ติด when ตกค้าง
    bad = []
    def chk(n):
        if n.get('menu') and n.get('when'):
            w = json.dumps(n['when'], ensure_ascii=False)
            if '"b": 10' in w and 'svSec' in w and w.startswith('{"op": "not"'):
                bad.append(n.get('label'))
    walk(cfg, chk)
    assert not bad, '🔴 ยังมีปุ่มเมนูติด when "โชว์เฉพาะ 10 วิ": %s' % bad
    # ยาม: ทุกการ์ดที่มีปุ่ม "เลือกวิดีโอ" ต้องมี "Gen วิดีโอใหม่" คู่กัน
    pairs = []
    def chk2(n):
        kids = n.get('card')
        if isinstance(kids, list):
            has_pick = any(isinstance(k, dict) and k.get('label') == 'เลือกวิดีโอ' and k.get('menu') for k in kids)
            has_redo = any(isinstance(k, dict) and k.get('label') == 'Gen วิดีโอใหม่' for k in kids)
            if has_pick:
                pairs.append(has_redo)
    walk(cfg, chk2)
    assert pairs and all(pairs), '🔴 มีการ์ดที่มีปุ่ม "เลือกวิดีโอ" แต่ไม่มี "Gen วิดีโอใหม่" (%d/%d)' % (sum(pairs), len(pairs))

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v37 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① ถอด when ตกค้างจาก v36 (%s) ⇒ ปุ่ม Gen วิดีโอใหม่ กลับมาโชว์ตอน 20/30 วิ' % ', '.join(stripped))
    print('   ② เพิ่มปุ่ม Gen วิดีโอใหม่ ในการ์ดที่ยังไม่มี %d จุด (ทุกการ์ดที่มี "เลือกวิดีโอ" ต้องมีคู่)' % added)
    print('   ③ เปลี่ยนคำ ภาพ→บอร์ด %d ปุ่ม · ④ ป้ายในเมนู "ใส่เป็นช่วง N"→"ช่วง N" %d ข้อ' % (len(renamed_btn), renamed_items))
    print('   ⑤ แถบดูเต็มจอ: ดาวน์โหลดขึ้นก่อน + แยกป้าย Gen ใหม่ (%d แถว)' % fixed_lb)


main()
