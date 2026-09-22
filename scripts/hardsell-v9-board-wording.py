#!/usr/bin/env python3
# hardsell-v9-board-wording.py — ถ้อยคำ "ภาพ" → "บอร์ด" เฉพาะที่หมายถึงสตอรีบอร์ด (พี่หมีเคาะ 2026-09-22 ผ่าน minimal)
#
# 🔴 กติกาที่ทำให้ไม่พัง (ท่าที่ตกลงกัน 3 ทีม):
#   ① **ห้าม find-replace คำว่า "ภาพ"** — แทนที่ **ทั้งข้อความแบบ exact match** เท่านั้น
#      เหตุผล: "ภาพ" ในแอปนี้หมายถึงของ 3 อย่าง — สตอรีบอร์ด (เปลี่ยน) · รูปสินค้า/ใบหน้าที่ผู้ใช้อัปเอง (ห้ามแตะ) · ภาพในคลิป/บทภาพ (ห้ามแตะ)
#   ② **นับก่อนแก้** — จำนวนต้องตรงที่ยื่นใบเคาะ ไม่งั้นหยุด (config อาจขยับหลังยื่น)
#   ③ **นับกอง B/C ก่อน-หลัง ต้องเท่ากันเป๊ะ** — ยามจับทันทีถ้าเผลอไปโดนของที่ห้ามแตะ
# ⭐ คำศัพท์กลางของตระกูลแอป (ต้องตรงกันทุกตัวอักษรทั้ง 3 ทีม): `ต้อง Gen ภาพก่อน` → `ต้อง Gen บอร์ดก่อน`
# ⏳ ไม่รวม A-2 (2 ข้อความที่ต้องอ่านบริบท) — ร่างส่ง minimal รวมยื่นพี่หมีก่อน ห้าม push เอง
import json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))

# (ข้อความเดิม, ข้อความใหม่, จำนวนที่ต้องเจอพอดี)
A1 = [
    ('ต้อง Gen ภาพก่อน', 'ต้อง Gen บอร์ดก่อน', 4),          # ⭐ คำศัพท์กลาง — hardsell/minimal/showhow ใช้ตัวเดียวกัน
    ('วาดภาพไม่สำเร็จ', 'วาดบอร์ดไม่สำเร็จ', 2),
    ('วาดภาพไม่สำเร็จ — กดลองใหม่', 'วาดบอร์ดไม่สำเร็จ — กดลองใหม่', 1),
    ('รอวาดภาพ', 'รอวาดบอร์ด', 2),
    ('รอภาพก่อน', 'รอบอร์ดก่อน', 1),
    ('ยังไม่มีภาพ', 'ยังไม่มีบอร์ด', 1),
    ('ได้ภาพแล้ว — รอวิดีโอ', 'ได้บอร์ดแล้ว — รอวิดีโอ', 2),
    ('แก้ภาพของคลิปนี้', 'แก้บอร์ดของคลิปนี้', 2),
    ('ยังไม่มีภาพ — ต้อง Gen ภาพก่อน ถึงจะ Gen วิดีโอได้', 'ยังไม่มีบอร์ด — ต้อง Gen บอร์ดก่อน ถึงจะ Gen วิดีโอได้', 1),
    ('ภาพโอเคแล้ว?', 'บอร์ดโอเคแล้ว?', 1),
    ('ภาพยังไม่ถูกใจ?', 'บอร์ดยังไม่ถูกใจ?', 1),
    ('แก้ภาพแล้ว สลับแท็บ “วิดีโอ” กด Gen วิดีโอใหม่ด้วย', 'แก้บอร์ดแล้ว สลับแท็บ “วิดีโอ” กด Gen วิดีโอใหม่ด้วย', 1),
]
# กอง B/C — ห้ามแตะ · นับก่อน-หลังต้องเท่ากัน
KEEP = ['เลือกภาพ', 'ต้องเลือกภาพอย่างน้อย 1 ภาพถึงจะผลิตได้', 'บทภาพ', 'บรรยายภาพฉากนี้เป็นภาษาไทย',
        'ข้อความบนภาพ', 'ข้อความสั้นบนภาพทุกฉาก', 'คลิปสะอาด ไม่มีข้อความบนภาพ', 'โมเดลสร้างภาพ']
UI = {'label', 'value', 'placeholder', 'desc', 'reason', 'hint', 'title'}


def strings(cfg):
    """ทุกข้อความ UI (คืน list ของ (dict, key)) — แก้ผ่านตัวนี้เท่านั้น"""
    out = []

    def walk(n):
        if isinstance(n, dict):
            for k, v in n.items():
                if k in UI and isinstance(v, str):
                    out.append((n, k))
                else:
                    walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(cfg)
    return out


def count(cfg, text):
    return sum(1 for n, k in strings(cfg) if n[k] == text)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    if count(cfg, 'ต้อง Gen บอร์ดก่อน'):
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    # ② นับก่อนแก้ — ต้องตรงกับที่ยื่นใบเคาะทุกข้อ
    for old, new, want in A1:
        got = count(cfg, old)
        assert got == want, 'ข้อความ %r ต้องเจอ %d จุด แต่เจอ %d — config ขยับหลังยื่นใบเคาะ หยุดก่อน' % (old, want, got)
    before_keep = {t: count(cfg, t) for t in KEEP}
    assert all(v > 0 for v in before_keep.values()), 'กอง B/C บางข้อความหายไปแล้ว: %s' % before_keep

    # ① แทนที่ทั้งข้อความแบบ exact match เท่านั้น
    changed = Counter()
    for n, k in strings(cfg):
        for old, new, _ in A1:
            if n[k] == old:
                n[k] = new
                changed[old] += 1
                break

    # ── ยาม ──
    for old, new, want in A1:
        assert changed[old] == want, 'แทนที่ %r ได้ %d ครั้ง (ควร %d)' % (old, changed[old], want)
        assert count(cfg, old) == 0, 'ยังมีข้อความเดิม %r ค้าง' % old
        assert count(cfg, new) == want, 'ข้อความใหม่ %r ต้องมี %d จุด' % (new, want)
    # ③ กอง B/C ต้องไม่ขยับแม้แต่จุดเดียว
    after_keep = {t: count(cfg, t) for t in KEEP}
    assert after_keep == before_keep, 'กอง B/C ถูกแตะ! ก่อน=%s หลัง=%s' % (before_keep, after_keep)
    # A-2 ต้องยังไม่ถูกแตะ (รอพี่หมีเคาะถ้อยคำผ่าน minimal)
    for t in ('ภาพโอเคแล้ว? สลับแท็บ “วิดีโอ” ใต้ภาพ เพื่อสั่งวิดีโอ',
              'ระบบแนบรูปนี้ให้ตอนวาดภาพและทำวิดีโอ เป็นคนเดิมทุกช็อต ทุกคลิป ทุกรอบผลิต'):
        assert count(cfg, t) == 1, 'A-2 %r ต้องยังอยู่เดิม 1 จุด (ห้ามแก้เองก่อนพี่หมีเคาะถ้อยคำ)' % t[:40]

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v9 ลงแล้ว — %s' % os.path.basename(src))
    print('   A-1 เปลี่ยน %d ข้อความ / %d จุด (exact match ทั้งสตริง)' % (len(A1), sum(changed.values())))
    print('   ⭐ คำศัพท์กลาง: "ต้อง Gen บอร์ดก่อน" (ตรงกับ minimal/showhow ทุกตัวอักษร)')
    print('   🛡 กอง B/C %d ข้อความ ไม่ขยับแม้แต่จุดเดียว · A-2 2 ข้อความ ยังไม่แตะ (รอถ้อยคำที่พี่หมีเคาะ)' % len(KEEP))


main()
