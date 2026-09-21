#!/usr/bin/env python3
# minimal-v28-no-storyboard-leak.py — กันโมเดลวิดีโอวาด "แผ่นสตอรีบอร์ด" ลงคลิป
# ที่มา: พี่หมีส่งคลิป 30 วิ ของจริง (VISTRA Q10 · 2026-09-21) — ช่วง 20.2→22.0 วิ = หน้าบอร์ดเต็มจอ
#   (เห็นแถว Scene 11/12/14/15 + คอลัมน์ Camera/Visual Info · Voiceover ครบ) แล้ว 22.2 วิ กลับเป็นภาพจริง
#   ⇒ หลุดที่ "2 วินาทีแรกของช่วงที่ 3" พอดี = ฉากแรกของช่วงที่ไม่มีภาพเริ่มต้นให้ยึด
# วัดแล้วว่า *ไม่ใช่* กฎหาย: ยิง eb_render_op จริง กฎ "never copy the sheet" อยู่ตำแหน่ง 1,646 / เพดาน 3,900
#   ⇒ ปัญหาคือ "น้ำหนัก" — บอร์ดเป็นภาพอ้างอิงที่ 1 + ประโยคสั่งให้ยึดแต่ละช่อง ⇒ พอไม่มีอะไรยึด โมเดลหยิบมาวาด
# แก้ 2 ชั้นพร้อมกัน (พี่หมีเลือกข้อ ค):
#   ① ย้ายแผ่นบอร์ดไปเป็น "ภาพสุดท้าย" · รูปสินค้าขึ้นเป็นภาพที่ 1 (ท่าเดียวกับฝั่งสร้างบอร์ดที่รูปสินค้ามาก่อนเสมอ)
#   ② เขียนกฎใหม่: อ้างอิงด้วยเนื้อหา ไม่ใช่เลขภาพ + ห้ามโชว์แม้เสี้ยววินาที/เฟรมแรก/ช่วงเปลี่ยนฉาก + เติม Negative
# 🪤 lookupRefs: ตัวหลัก (from/by/slot) มาก่อน also[] เสมอ ⇒ "ย้ายบอร์ดไปท้าย" = สลับให้ products.image เป็นตัวหลัก
#    แล้วผลัก board ไปเป็น also ตัวสุดท้าย (ยังคง when ของ face ไว้ตรงตัว)
# 🪤 คลิปยังเป็น 1 task = หลาย slot ⇒ ต้องทำครบทั้ง mnVideo / mnVideo2 / mnVideo3 ไม่งั้นช่วงที่ลืมยังหลุด
# รันซ้ำได้: ตรวจ marker ในข้อความกฎ
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'appear on screen'   # ตัวชี้ว่าแพตช์ลงแล้ว (ระวังตัวพิมพ์ — ข้อความจริงเขียน NEVER ตัวใหญ่)
OPS = {'mnVideo': 'board', 'mnVideo2': 'board2', 'mnVideo3': 'board3'}

NEW_RULE = ('\n\nThe LAST reference image is this clip storyboard sheet; the others are real product photos. '
            'Use it only as a silent look guide — it must NEVER appear on screen: not whole, not a panel, not the '
            'first frame, not a transition. Never draw panel borders, numbers, labels, timings or split layout.')
NEW_NEG = ('\n\nNegative: no storyboard sheet, no document page, no grid, no split screen, no distorted or '
           'non-Thai text, no warped or morphing product, no extra fingers.')


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)
    if MARK in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    done = []
    for oid, board_slot in OPS.items():
        op = [o for o in cfg['ops'] if o['id'] == oid][0]

        # ① สลับลำดับภาพอ้างอิง — บอร์ดไปท้ายสุด
        refs = op['refs']
        assert refs.get('slot') == board_slot and refs.get('from') == 'tasks', \
            '%s: ตัวหลักของ refs ไม่ใช่บอร์ดตามที่คาด (%s)' % (oid, refs.get('slot'))
        also = refs['also']
        first = also[0]
        assert first.get('from') == 'products' and first.get('slot') == 'image', \
            '%s: also ตัวแรกไม่ใช่รูปสินค้าหลัก' % oid
        board_ref = {'from': 'tasks', 'by': refs['by'], 'slot': board_slot}
        refs['from'], refs['by'], refs['slot'] = first['from'], first['by'], first['slot']
        refs['also'] = also[1:] + [board_ref]          # สินค้า 2-5 · face · แล้วบอร์ดท้ายสุด

        # ② เขียนกฎใหม่ (แทนทั้งชิ้น ไม่แก้คำในชิ้น — ตามกฎ "แทนทั้งบรรทัด verbatim")
        parts = op['prompt']['parts'] if isinstance(op.get('prompt'), dict) else None
        assert parts is not None, '%s: prompt ไม่ใช่ block/parts' % oid
        hit_rule = [i for i, p in enumerate(parts) if isinstance(p, str) and 'Reference image 1 is the storyboard' in p]
        hit_neg = [i for i, p in enumerate(parts) if isinstance(p, str) and p.lstrip().startswith('Negative:')]
        assert len(hit_rule) == 1 and len(hit_neg) == 1, '%s: หาชิ้นกฎ/Negative ไม่เจอหรือเจอซ้ำ' % oid
        parts[hit_rule[0]] = NEW_RULE
        parts[hit_neg[0]] = NEW_NEG
        done.append(oid)

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before, 'ไฟล์ไม่เปลี่ยน'
    # ยาม: ทุก op ต้องได้ทั้ง 2 ชั้น และบอร์ดต้องเป็น ref ตัวสุดท้ายจริง
    for oid, board_slot in OPS.items():
        op = [o for o in cfg['ops'] if o['id'] == oid][0]
        assert op['refs']['slot'] == 'image', '%s: ภาพที่ 1 ต้องเป็นรูปสินค้า' % oid
        assert op['refs']['also'][-1]['slot'] == board_slot, '%s: บอร์ดต้องเป็นภาพสุดท้าย' % oid
        blob = json.dumps(op['prompt'], ensure_ascii=False)
        assert MARK in blob and 'no storyboard sheet' in blob, '%s: กฎใหม่ไม่ครบ' % oid
        assert 'Reference image 1 is the storyboard' not in blob, '%s: ข้อความเก่ายังอยู่' % oid

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ แพตช์ %s แล้ว — %s' % (', '.join(done), os.path.basename(src)))
    print('   ① รูปสินค้าเป็นภาพอ้างอิงที่ 1 · แผ่นบอร์ดย้ายไปท้ายสุด')
    print('   ② กฎใหม่: ห้ามแผ่นบอร์ดโผล่บนจอแม้เฟรมเดียว/เฟรมแรก/ช่วงเปลี่ยนฉาก + Negative เติม storyboard/หน้ากระดาษ')


main()
