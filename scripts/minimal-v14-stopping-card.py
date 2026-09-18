#!/usr/bin/env python3
# minimal v14 — ข้อความ "กำลังหยุด…" ตอนกดหยุดพัก → การ์ดเตือน (2026-09-10 · พี่หมีเห็นบน iPhone)
#
# อาการ: เป็นแถวเปล่า ๆ (spinner + ข้อความยาว 1 บรรทัด) วางลอยใต้ปุ่ม
#   "กำลังหยุด… รอขั้นที่ค้างอยู่จบก่อน (ช่วงเขียนบทอาจใช้เวลาถึง 1 นาที)"  = 66 ตัวอักษร
#   ⇒ บนจอ ~390px มันตัดบรรทัดกลางวงเล็บ ไม่มีพื้นหลัง ไม่มีขอบ = อ่านยากและดูเหมือนของหลุด
#
# แก้: ห่อเป็นการ์ดเตือนสีอำพัน + แบ่งข้อความเป็น 2 บรรทัด
#   ┌─────────────────────────────────────┐
#   │ ◌  กำลังหยุด… รอขั้นที่ค้างอยู่จบก่อน   │   ← ตัวหนา
#   │    ช่วงเขียนบทอาจใช้เวลาถึง 1 นาที      │   ← เล็กลง จางลง
#   └─────────────────────────────────────┘
#
# 🔑 **แบ่งตามจุดตัดที่ข้อความมีอยู่แล้ว (วงเล็บ) ไม่แต่งคำใหม่** —
#    รอบนี้ผมโดนพี่หมีแก้ทิศมา 2 ครั้งเพราะไปอนุมานถ้อยคำ/เลย์เอาต์เอง ⇒ ตัดตรงที่ผู้เขียนเดิมตั้งใจแบ่งไว้
#    (วงเล็บ = ข้อมูลรอง อยู่แล้วโดยธรรมชาติ) ⇒ ความหมายไม่เปลี่ยนสักตัวอักษร
#
# 🪤 ขอบ ไม่ใช้เงา (กฎสไตล์ของแอปนี้ — className ห้ามมี shadow-*)
# 🪤 `items-start` + `min-w-0` ที่คอลัมน์ข้อความ — ไม่งั้นบรรทัดยาวดันขอบการ์ดแทนที่จะตัดบรรทัดในกรอบ
#
# รันซ้ำได้ (idempotent)
import json, sys, os

OLD = 'กำลังหยุด… รอขั้นที่ค้างอยู่จบก่อน (ช่วงเขียนบทอาจใช้เวลาถึง 1 นาที)'
L1 = 'กำลังหยุด… รอขั้นที่ค้างอยู่จบก่อน'
L2 = 'ช่วงเขียนบทอาจใช้เวลาถึง 1 นาที'
CARD_CLS = ('w-full items-start gap-2.5 rounded-xl border border-amber-500/35 '
            'bg-amber-500/10 px-3 py-2.5 @[420px]:px-3.5')


def nodes(n):
    if isinstance(n, dict):
        yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n, list):
        for v in n: yield from nodes(v)


def patch(cfg):
    log = []
    for n in list(nodes(cfg)):
        if not isinstance(n, dict) or not isinstance(n.get('card'), list): continue
        kids = [c for c in n['card'] if isinstance(c, dict)]
        old = next((c for c in kids if c.get('el') == 'text' and c.get('value') == OLD), None)
        if old is None: continue
        spin = next((c for c in kids if c.get('el') == 'spinner'), None)
        n['className'] = CARD_CLS
        col = {"el": "box", "className": "flex flex-col gap-0.5 min-w-0",
               "card": [
                   {"el": "text", "value": L1,
                    "className": "!text-[13.5px] font-bold !text-amber-600 leading-snug"},
                   {"el": "text", "value": L2,
                    "className": "!text-[12px] font-medium !text-amber-600 opacity-75 leading-snug"},
               ]}
        n['card'] = ([spin] if spin else []) + [col]
        log.append('  · ทำการ์ดเตือน + แบ่ง 2 บรรทัด')
    return log


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for f in (sys.argv[1:] or [os.path.join(here, 'minimal-dev.json')]   # 2026-09-18: minimal.json ปลดระวางแล้ว (ลบจาก GCS+รีโป)):
        cfg = json.load(open(f, encoding='utf-8'))
        before = json.dumps(cfg, ensure_ascii=False, sort_keys=True)
        print('══', os.path.basename(f))
        for l in patch(cfg): print(l)
        if json.dumps(cfg, ensure_ascii=False, sort_keys=True) == before:
            print('  (ไม่มีอะไรเปลี่ยน — แพตช์ลงไปแล้ว)')
        else:
            json.dump(cfg, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('  ✅ เขียนแล้ว')


if __name__ == '__main__':
    main()
