#!/usr/bin/env python3
# hardsell-v17-no-buy-button.py — คืนคำห้าม "ปุ่มซื้อบนจอ" ที่ v10 ตัดไป (หลักฐานจากคลิปจริง 2026-09-28)
#   ทดสอบ D (วิธีภาพเฟรมแรก · บัญชีสำรอง): 3 วิสุดท้ายของช่วง 2 มีปุ่ม "BUY NOW" + ตัวหนังสือเล็กโผล่ใต้จอ
#   ต้นเหตุ: v10 ตัด "on-screen buy prompts, buttons" + "never shown on screen" ออกเพื่อประหยัดตัวอักษร (ตอนนั้น 2 ตัวอักษรสุดท้าย)
#   ตอนนี้ v16 ตัดบล็อกแผ่นบอร์ดออกแล้ว prompt วิดีโอเหลือ 3,464 ⇒ มีที่พอคืน · 🪤 ห้ามตัดคำนี้อีก (ยาม ② เฝ้าแล้ว)
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OLD_ASK = 'The ask to buy is spoken only; the clip ends on the person, not a card.'
NEW_ASK = 'The ask to buy is spoken only, never shown on screen; the clip ends on the person, not a card.'
OLD_NEG = 'Negative: no end card, closing title, price or discount graphics,'
NEW_NEG = 'Negative: no end card, closing title, buy buttons, shopping UI, on-screen buy prompts, price or discount graphics,'


def main():
    src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json'))
    cfg = json.load(open(src, encoding='utf-8'))
    if 'buy buttons, shopping UI' in json.dumps(cfg, ensure_ascii=False):
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร'); return
    n = 0
    for o in cfg['ops']:
        if o['id'] not in ('mnVideo', 'mnVideo2'): continue
        parts = o['prompt']['parts']
        hit = [i for i, x in enumerate(parts) if isinstance(x, str) and OLD_ASK in x and OLD_NEG in x]
        assert len(hit) == 1, '%s: ประโยคปิดการขาย+negative เจอ %d' % (o['id'], len(hit))
        parts[hit[0]] = parts[hit[0]].replace(OLD_ASK, NEW_ASK).replace(OLD_NEG, NEW_NEG); n += 1
    assert n == 2
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v17 ลงแล้ว — คืนคำห้ามปุ่มซื้อ/หน้าร้านบนจอ ใน mnVideo + mnVideo2')


main()
