#!/usr/bin/env python3
# minimal-v44-board-wording.py — คำว่า "ภาพ" → "บอร์ด" เฉพาะที่หมายถึงสตอรีบอร์ด (พี่หมีเคาะ 2026-09-22: "หมดแล้ว")
#
# ที่มา: พี่หมีสั่งเปลี่ยนคำบนปุ่มเป็น "บอร์ด" (v37) แต่ข้อความรอบ ๆ ยังพูด "ภาพ"
#   ⇒ ยื่นใบเคาะรวม 3 ทีม (`bear-clan/docs/DECIDE-wording-board-2026-09-22.md`) · พี่หมีตอบ "หมดแล้ว" = เอากอง A ทั้งหมด
#
# 🔴🔴 **แทนคำทั้งแอปไม่ได้เด็ดขาด** — "ภาพ" ในแอปนี้หมายถึงของ 3 อย่างที่ต่างกันจริง:
#   A  สตอรีบอร์ด                     → เปลี่ยน (ไฟล์นี้)
#   B  รูปสินค้า/รูปใบหน้าที่ผู้ใช้อัปเอง  → **ห้ามแตะ** (`เลือกภาพ` ×6 · ชี้ slot face/image1-5)
#   C  ภาพในคลิป / บทภาพ / เฟรม        → **ห้ามแตะ** (`บรรยายภาพฉากนี้…` ×15 · `ข้อความสั้นบนภาพทุกฉาก` ฯลฯ)
#   ⇒ จึงใช้ **exact match ทั้งสตริง** ไม่ใช่ replace คำ · ทุกทีมยืนยันตรงกันว่า B/C ห้ามแตะ
#
# ⭐ `ต้อง Gen ภาพก่อน` = **ข้อความร่วมของทั้ง 3 แอป** (hardsell 4 · minimal 4 · showhow 4 จุด · ตรงกันทุกตัวอักษรโดยไม่ได้ลอกกัน)
#    ⇒ คำที่เคาะรอบนี้กลายเป็น **คำศัพท์กลางของตระกูลแอป** — ทีมอื่นต้องใช้คำเดียวกันเป๊ะ
# รันซ้ำได้: ตรวจว่าเหลือของเก่าไหม
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = {
    'ต้อง Gen ภาพก่อน': 'ต้อง Gen บอร์ดก่อน',
    'เขียนบท → ตรวจ → สร้างภาพ → วิดีโอ': 'เขียนบท → ตรวจ → สร้างบอร์ด → วิดีโอ',
}
EXPECT = {'ต้อง Gen ภาพก่อน': 4, 'เขียนบท → ตรวจ → สร้างภาพ → วิดีโอ': 1}
# ของกอง B/C ที่ต้อง "ไม่ขยับ" หลังรัน — ยามเช็กจำนวนกลับ
KEEP = {'เลือกภาพ': 6, 'บรรยายภาพฉากนี้เป็นภาษาไทย': 15,
        'ข้อความสั้นบนภาพทุกฉาก': 1, 'คลิปสะอาด ไม่มีข้อความบนภาพ': 1,
        'เน้นภาพสินค้าโดยตรง ไม่มีคนในคลิป': 1}
TXT = {'label', 'text', 'title', 'subtitle', 'desc', 'placeholder', 'hint', 'reason',
       'emptyText', 'loadingLabel', 'note', 'value'}


def count(cfg, s):
    n = 0

    def w(x):
        nonlocal n
        if isinstance(x, dict):
            for k, v in x.items():
                if k in TXT and v == s:
                    n += 1
                w(v)
        elif isinstance(x, list):
            for v in x:
                w(v)
    w(cfg)
    return n


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)

    if all(count(cfg, o) == 0 for o in MAP):
        print('⏭  เปลี่ยนไปแล้ว — ไม่ทำอะไร')
        return
    for o, want in EXPECT.items():
        got = count(cfg, o)
        assert got == want, '🔴 "%s" ควรมี %d จุด เจอ %d — config เปลี่ยนไปจากตอนยื่นใบเคาะ ต้องตรวจใหม่ก่อนแก้' % (o, want, got)
    keep_before = {s: count(cfg, s) for s in KEEP}
    assert keep_before == KEEP, '🔴 จำนวนข้อความกอง B/C ไม่ตรงกับที่ยื่นไว้: %s' % keep_before

    changed = 0

    def w(x):
        nonlocal changed
        if isinstance(x, dict):
            for k, v in list(x.items()):
                if k in TXT and isinstance(v, str) and v in MAP:
                    x[k] = MAP[v]; changed += 1
                else:
                    w(v)
        elif isinstance(x, list):
            for v in x:
                w(v)
    w(cfg)

    assert changed == sum(EXPECT.values()), 'เปลี่ยน %d จุด (ควร %d)' % (changed, sum(EXPECT.values()))
    assert json.dumps(cfg, ensure_ascii=False) != before

    # ── ยาม: กอง B/C ต้องไม่ขยับแม้แต่จุดเดียว ──
    keep_after = {s: count(cfg, s) for s in KEEP}
    assert keep_after == KEEP, '🔴 ไปแตะกอง B/C เข้า: ก่อน %s → หลัง %s' % (KEEP, keep_after)
    for o in MAP:
        assert count(cfg, o) == 0, 'ยังเหลือข้อความเก่า: %s' % o
    for n_ in MAP.values():
        assert count(cfg, n_) > 0, 'ไม่พบข้อความใหม่: %s' % n_

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v44 ลงแล้ว — เปลี่ยน %d จุด (กอง A เท่านั้น)' % changed)
    for o, n_ in MAP.items():
        print('   "%s" → "%s"  ×%d' % (o, n_, EXPECT[o]))
    print('   🛡 กอง B/C ไม่ขยับ: %s' % keep_after)


main()
