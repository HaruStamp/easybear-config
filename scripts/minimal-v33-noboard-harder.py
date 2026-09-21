#!/usr/bin/env python3
# minimal-v33-noboard-harder.py — บอร์ดยังหลุดเข้าคลิปแม้ v28 แล้ว → เสริมกฎ/Negative (พี่หมีเคาะข้อ ค · 2026-09-21)
# หลักฐานรอบนี้: คลิป 20 วิ ของจริง — 1 ช็อตมี "แถบลายเส้นกรอบสี่เหลี่ยมทับครึ่งบนของเฟรม + ภาพจริงครึ่งล่าง"
#   = โมเดลลอก "หน้าตาแผ่นบอร์ด" ที่เราแนบเป็นภาพอ้างอิง ไม่ใช่ลอกเนื้อหาในบอร์ด
# 🔬 วัดก่อนแก้ (eb_render_op ของจริง · Dev v3.1.0 · golden v1.8.0):
#     prompt 2,400 ตัวอักษร · willClamp=false · กฎบอร์ดอยู่ตำแหน่ง 1,662 · Negative มี "no split screen" อยู่แล้ว
#   ⇒ **กฎไปถึงโมเดลครบ ไม่ได้ถูกตัด** — ปัญหาคือโมเดลไม่เชื่อฟัง ไม่ใช่ prompt หาย
#   ⇒ ทางที่แน่นอนกว่าคือ "ไม่ส่งแผ่นบอร์ดเข้าโมเดลเลย" แต่พี่หมีเลือกเสริมถ้อยคำก่อน (ข้อ ค) — ทำตามนั้น
# 🪤 เพดาน: เคสชั้นตัดสินยาวสุดของวิดีโอ = 3,865 / 3,900 ⇒ **เหลือที่ 35 ตัวอักษร**
#   ⇒ ห้ามเติมคำลอย ๆ ต้องเขียนกฎเดิมใหม่ให้สั้นลงเพื่อแลกที่ว่าง · สคริปต์ assert ว่า net delta ต้อง ≤ 40 ตัวอักษร
# เปลี่ยน 2 ชิ้นในทุก op วิดีโอ (mnVideo/2/3):
#   ① กฎบอร์ด: เพิ่มประโยคเชิงบวก "ทุกเฟรมเป็นภาพถ่ายจริง" + ชื่อสิ่งที่เห็นในคลิปที่หลุด (line art/paper/panel border)
#      🔑 เดิมบอกแต่ว่า "ห้ามให้บอร์ดโผล่" (เชิงห้าม) — ไม่ได้บอกว่า "แล้วเฟรมต้องเป็นอะไร" (เชิงสั่ง)
#   ② Negative: เติมคำที่ตรงกับของที่เห็นจริง (line art · sketch · drawing · paper page · framed panel · band บน/ล่าง · picture-in-picture)
# 🛡 วลีที่ยาม prompt-clamp-matrix เฝ้า ต้องอัปตามในรอบเดียวกัน (ไม่งั้นยามเฝ้าข้อความที่ไม่มีแล้ว = ยามหลับชนิด ④)
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'live-action photography'
OPS = {'mnVideo': 'board', 'mnVideo2': 'board2', 'mnVideo3': 'board3'}

OLD_RULE_KEY = 'LAST reference image is this clip storyboard sheet'
OLD_NEG_KEY = 'Negative: no storyboard sheet'

# 🪤 ถ้อยคำผ่านการบีบ 1 รอบเพราะยามข้างล่างเด้ง (+122 เกินที่ว่าง 35) — ฉบับนี้ +32 ต่อ op
NEW_RULE = ('\n\nThe LAST reference image is this clip storyboard sheet; the others are real product photos. '
            'Silent look guide only — it must NEVER appear on screen. Every frame is live-action photography, '
            'never line art, sketch, paper or panel border, not even one frame.')
NEW_NEG = ('\n\nNegative: no storyboard sheet, no line art, no sketch, no paper page, no framed panel, '
           'no band across top or bottom, no grid, no split screen, no distorted or non-Thai text, '
           'no warped or morphing product, no extra fingers.')


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)
    if MARK in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return
    assert OLD_RULE_KEY in before, 'ต้องรัน v28 ก่อน (ยังไม่มีกฎบอร์ดรุ่นใหม่)'

    delta = 0
    for oid, board_slot in OPS.items():
        op = [o for o in cfg['ops'] if o['id'] == oid][0]
        parts = op['prompt']['parts']
        hit_rule = [i for i, p in enumerate(parts) if isinstance(p, str) and OLD_RULE_KEY in p]
        hit_neg = [i for i, p in enumerate(parts) if isinstance(p, str) and p.lstrip().startswith('Negative:')]
        assert len(hit_rule) == 1 and len(hit_neg) == 1, '%s: หาชิ้นกฎ/Negative ไม่เจอหรือเจอซ้ำ' % oid
        delta += (len(NEW_RULE) - len(parts[hit_rule[0]])) + (len(NEW_NEG) - len(parts[hit_neg[0]]))
        parts[hit_rule[0]] = NEW_RULE
        parts[hit_neg[0]] = NEW_NEG
        # บอร์ดต้องยังเป็นภาพอ้างอิงตัวสุดท้ายเหมือน v28 (พี่หมีเลือกยังส่งบอร์ดต่อ)
        assert op['refs']['slot'] == 'image', '%s: ภาพที่ 1 ต้องเป็นรูปสินค้า' % oid
        assert op['refs']['also'][-1]['slot'] == board_slot, '%s: บอร์ดต้องเป็นภาพสุดท้าย' % oid

    per_op = delta // len(OPS)
    print('   ความยาวที่เปลี่ยนต่อ op = %+d ตัวอักษร' % per_op)
    assert per_op <= 40, 'ยาวขึ้นเกิน 40 ตัวอักษรต่อ op — เคสชั้นตัดสินเหลือที่แค่ 35 (3,865/3,900) ต้องบีบก่อน'

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    for oid in OPS:
        blob = json.dumps([o for o in cfg['ops'] if o['id'] == oid][0]['prompt'], ensure_ascii=False)
        assert MARK in blob, '%s: ไม่มีประโยคเชิงสั่ง (live-action photography)' % oid
        assert 'no line art' in blob and 'no band across top or bottom' in blob, '%s: Negative ไม่ครบ' % oid
        assert OLD_RULE_KEY in blob and OLD_NEG_KEY in blob, '%s: วลีที่ยามเฝ้าหาย' % oid

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v33 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① กฎบอร์ดเพิ่มประโยค "ทุกเฟรมเป็นภาพถ่ายจริง" + ชื่อของที่หลุดจริง (line art/paper/panel border)')
    print('   ② Negative เติม line art · sketch · drawing · paper page · framed panel · band บน/ล่าง · picture-in-picture')
    print('   🪤 ยังส่งแผ่นบอร์ดเข้าโมเดลเหมือนเดิม (พี่หมีเลือกข้อ ค) ⇒ ลดโอกาส ไม่ใช่ปิดทาง')


main()
