#!/usr/bin/env python3
# hardsell-v15-seam-labels-logs.py — แก้ 3 เรื่องที่เจอจากการผลิตคลิปจริงครั้งแรกบน engine (บัญชีสำรอง UltraFamily3 · 2026-09-28)
#
# ① รอยต่อ 16 วิ ภาพกระโดดย้อน — หลักฐานจากคลิปจริง (docs/qa/2026-09-28-prod/A-16s/seam-compare.jpg):
#    เฟรมแรกของช่วง 2 == เฟรมวินาทีที่ 7.0 ของช่วง 1 (mnVideo2.tailTrim = 1 ⇒ ต่อจาก 8-1) แต่ตอนรวมเอาช่วง 1 เต็ม 8 วิ
#    ⇒ เห็นท่าวินาที 7-8 แล้วกระโดดกลับไปท่าวินาที 7 · จำลองรวมแบบตัดที่ 7 = ต่อเนียนสนิท
#    สาเหตุในโค้ด engine: จุดตัดอัตโนมัติ (`data.__segTrim`) เขียนเฉพาะ op ที่ใช้ `parts` (engine-parts.ts:196-203)
#    hardsell ใช้ 2 op แยก (mnVideo/mnVideo2) ⇒ ไม่มีใครตั้ง ⇒ ต้องตั้ง `trimEndIfNext` ที่ el.segments เอง (§③ ข้อ 13 ทาง A)
#    7 = 8 วิ − tailTrim 1 ของ mnVideo2 · ตั้งเฉพาะ slot `video` (ช่วง 1) — `video2` ตัดเฉพาะเมื่อมีช่วง 3 ซึ่ง hardsell ไม่มี
# ② ป้ายชื่อโมเดลวิดีโอ 3 จุด เขียนตายตัว "Omni 1.1 Flash" (ติดจากโครง minimal ที่ล็อก Omni) — ยิงจริงใช้ {values.videoModel}
#    ⇒ ผู้ใช้เลือก Veo แต่หน้าจอบอก Omni (ทดสอบ A = Veo 3.1 Fast สำเร็จ ทั้งที่ป้ายบอก Omni)
# ③ log เขียนตายตัว "สตอรีบอร์ด 5 ช่อง" / "วิดีโอ 10 วิ" (minimal) — hardsell = 4 ช่อง / 8 วิ ต่อช่วง (ไฟล์จริง 8.000 วิ)
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TRIM = 7


def main():
    src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json'))
    cfg = json.load(open(src, encoding='utf-8'))
    s0 = json.dumps(cfg, ensure_ascii=False)
    if '"trimEndIfNext": %d' % TRIM in s0:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร'); return
    ops = {o['id']: o for o in cfg['ops']}
    assert ops['mnVideo2'].get('tailTrim') == 1 and not ops['mnVideo'].get('tailTrim'), 'tailTrim เปลี่ยน — ทบทวนค่า 7 ก่อน'

    # ① segments
    segs = []
    def walk(n):
        if isinstance(n, dict):
            if isinstance(n.get('segments'), list): segs.append(n['segments'])
            for v in n.values(): walk(v)
        elif isinstance(n, list):
            for v in n: walk(v)
    walk(cfg)
    assert len(segs) == 10, 'segments %d จุด (ตรวจไว้ 10)' % len(segs)
    for sg in segs:
        first = sg[0]
        assert first == {'slot': 'video'}, 'ช่วงแรกไม่ใช่ {slot: video} เดี่ยว ๆ: %r' % first
        first['trimEndIfNext'] = TRIM

    # ② ป้ายโมเดล
    n_label = 0
    def lab(n):
        nonlocal n_label
        if isinstance(n, dict):
            if n.get('el') == 'text' and n.get('value') == 'Omni 1.1 Flash':
                n['value'] = '{values.videoModel}'; n_label += 1
            v = n.get('value')
            if n.get('el') == 'text' and isinstance(v, dict) and v.get('op') == 'concat' and v['parts'][:1] == ['Omni 1.1 Flash · ']:
                v['parts'][0] = '{values.videoModel} · '; n_label += 1
                for p in v['parts']:
                    if isinstance(p, dict) and p.get('table') == 'lenSecs' and p.get('fallback') == '10': p['fallback'] = '8'
            for x in n.values(): lab(x)
        elif isinstance(n, list):
            for x in n: lab(x)
    lab(cfg['phases'])
    assert n_label == 3, 'ป้ายโมเดล %d จุด (ตรวจไว้ 3)' % n_label

    # ③ log
    for oid, old, new in (('mnBoard', 'สตอรีบอร์ด 5 ช่อง', 'สตอรีบอร์ด 4 ช่อง'),
                          ('mnVideo', 'สร้างวิดีโอ 10 วิ', 'สร้างวิดีโอ 8 วิ'),
                          ('mnVideo2', 'ช่วงที่ 2 (10 วิ)', 'ช่วงที่ 2 (8 วิ)')):
        assert old in ops[oid]['logRun'], '%s logRun ไม่มี %r' % (oid, old)
        ops[oid]['logRun'] = ops[oid]['logRun'].replace(old, new)

    s = json.dumps(cfg, ensure_ascii=False)
    assert 'Omni 1.1 Flash' in s  # ยังต้องมีในตัวเลือก dropdown (เป็นตัวเลือกจริงของผู้ใช้)
    assert s.count('"value": "Omni 1.1 Flash"') == 1, 'Omni ที่เหลือต้องเป็นตัวเลือก dropdown 1 จุดเท่านั้น'
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v15 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① trimEndIfNext=%d ที่ช่วงแรก 10 จุด (รวมคลิป 16 วิ ต่อเนียน · ได้ 15 วิ)' % TRIM)
    print('   ② ป้ายโมเดล 3 จุด → {values.videoModel} · ③ log 3 จุด → 4 ช่อง / 8 วิ')


main()
