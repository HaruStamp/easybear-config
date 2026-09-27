#!/usr/bin/env python3
# hardsell-v12-fix-output-example.py — แก้ตัวอย่างรูปแบบคำตอบ JSON ของตัวเขียนบท (ตาราง lenOut) ให้ครบทุกฉาก
#
# ที่มา (เจอตอนพี่หมีสั่งตรวจละเอียด 2026-09-28): `lenOut` ผิดทั้ง 2 ค่า **ตั้งแต่ยกโครง minimal (`8b14752` · 2026-09-14)**
#   8 วิ  = ฉาก 1-4 แล้วมีก้อนขยะซ้ำ `s4th s5en ov4 vo4 cam4`
#   16 วิ = ฉาก 1-4 แล้วกระโดดไปฉาก 8 **ข้ามฉาก 5-7 ทั้งหมด** + ฉาก 8 ใช้ `s5en` แทน `s8en`
# 🔴 ทำไมต้องแก้ตอนนี้: แพตช์ v10 ใส่ `mnPlan.validate` บังคับฟิลด์ฉาก 5-8 ของคลิป 16 วิ
#   ⇒ ถ้า AI ทำตามตัวอย่างที่ผิด = โดนตีกลับครบ 3 รอบแล้วขึ้นพลาด (เดิมแค่ได้ฉากว่าง) · งานของผมทำให้รูเดิมกลายเป็นตัวบล็อก
# วิธี: สร้างรายการช่องใหม่จากจำนวนฉากจริง (8 วิ = 4 · 16 วิ = 8) แทนที่เฉพาะสายตัวอย่างในแต่ละค่า — ข้อความรอบ ๆ ไม่แตะ
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = {'8': 4, '16': 8}
FIELDS = ('th', 'en', 'ov', 'vo', 'cam')
# สายตัวอย่างเดิม = ตั้งแต่ "s1th" จนถึงช่องสุดท้ายก่อน } ปิด object
PAT = re.compile(r'"s1th":"\.\.\.",(?:"[a-z0-9]+":"\.\.\.",?)+(?=\})')


def example(n):
    out = []
    for k in range(1, n + 1):
        out += ['"s%dth":"..."' % k, '"s%den":"..."' % k, '"ov%d":"..."' % k, '"vo%d":"..."' % k, '"cam%d":"..."' % k]
    return ','.join(out)


def keys(txt):
    return re.findall(r'"((?:s\d+(?:th|en))|ov\d+|vo\d+|cam\d+)":"\.\.\."', txt)


def want(n):
    return [f % k for k in range(1, n + 1) for f in ('s%dth', 's%den', 'ov%d', 'vo%d', 'cam%d')]


def main():
    src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json'))
    cfg = json.load(open(src, encoding='utf-8'))
    tb = cfg['lookups']['lenOut']
    if all(keys(tb[k]) == want(n) for k, n in SCENES.items()):
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร'); return
    assert sorted(tb) == sorted(SCENES), 'lenOut มีคีย์อื่นนอกจาก 8/16: %s' % list(tb)
    for k, n in SCENES.items():
        hits = PAT.findall(tb[k])
        assert len(hits) == 1, 'lenOut[%s]: เจอสายตัวอย่าง %d จุด (ควร 1)' % (k, len(hits))
        tb[k] = PAT.sub(example(n), tb[k])
        assert keys(tb[k]) == want(n), 'lenOut[%s]: ช่องหลังแก้ไม่ครบ' % k
    # fallback ของ lookup (ใช้เมื่อ svSec ไม่ใช่ 8/16) — ถือเป็นแบบ 8 วิ ตามค่าเริ่มต้นของแอป
    fixed_fb = 0
    def walk(n):
        nonlocal fixed_fb
        if isinstance(n, dict):
            if n.get('op') == 'lookup' and n.get('table') == 'lenOut' and isinstance(n.get('fallback'), str) and PAT.search(n['fallback']):
                n['fallback'] = PAT.sub(example(SCENES['8']), n['fallback']); fixed_fb += 1
                assert keys(n['fallback']) == want(4)
            for v in n.values(): walk(v)
        elif isinstance(n, list):
            for v in n: walk(v)
    walk(cfg['ops'])
    assert cfg['values'].get('svSec') == '8', 'fallback ถือเป็น 8 วิ เพราะค่าเริ่มต้นเป็น 8 — ถ้าเปลี่ยนต้องทบทวน'
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v12 ลงแล้ว — %s' % os.path.basename(src))
    print('   lenOut[8]  = ฉาก 1-4 ครบ %d ช่อง (ตัดก้อนขยะซ้ำ) · lenOut[16] = ฉาก 1-8 ครบ %d ช่อง (เดิมขาดฉาก 5-7)' % (len(want(4)), len(want(8))))
    print('   fallback ของ lookup แก้ %d จุด' % fixed_fb)


main()
