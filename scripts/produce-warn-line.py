#!/usr/bin/env python3
"""produce-warn-line — บรรทัดเตือนท้ายการ์ดสถานะหน้าผลิต (ทุกแอป engine · ต้นฉบับข้อความ = minimal-v68-tap-res-warn.py ③ · 27 พ.ย. 2569)

  ระหว่างรอวิดีโอ อย่าสลับแอปหรือล็อกจอ · ได้บอร์ดครบแล้วกดบันทึกมุมขวาบนเก็บไว้ก่อน
  เหตุ: รีโหลดแท็บ (มือถือสลับแอป/ล็อกจอ = แรมโดนคืน) = งานหาย · ฝั่งลูกค้าไม่มีบันทึกอัตโนมัติ (iframe เก็บของถาวรไม่ได้ · engine v1.25.2 release note §4)
  โผล่เมื่อมีคลิปในคิวแล้ว (count tasks > 0) เหมือน minimal r32 · ทุกแอปมีขั้นบอร์ด (mnBoard*) ⇒ ใช้ข้อความเดียวกันทุกแอป
  ตำแหน่ง: ต่อท้ายการ์ดสถานะ (ลูกตรงของกล่องหน้าผลิต max-w-[1060px] ที่มีปุ่ม gen-phase วิดีโอทั้งหมด = ops mnVideo* ล้วน)
    ไม่แทรกกลาง ⇒ path ของแถวอื่นไม่เลื่อน · ใช้ของที่ engine 1.22 มีครบ (text + icon + when/count) — ตัวขายเก่าอ่าน public ตัวเดียวกัน
ใช้: python3 scripts/produce-warn-line.py <ไฟล์ config>…   (แก้ในที่ · รันซ้ำ = ไม่เปลี่ยน · minimal มีแล้ว = 0 จุด)
"""
import json, sys

WARN = 'ระหว่างรอวิดีโอ อย่าสลับแอปหรือล็อกจอ · ได้บอร์ดครบแล้วกดบันทึกมุมขวาบนเก็บไว้ก่อน'
WARN_CLS = '!text-[12.5px] leading-snug opacity-60 px-0.5'


def walk(o, f):
    if isinstance(o, dict):
        f(o)
        for v in o.values(): walk(v, f)
    elif isinstance(o, list):
        for v in o: walk(v, f)


def is_vid_all(x) -> bool:
    ops = x.get('ops')
    return x.get('el') == 'gen-phase' and isinstance(ops, list) and len(ops) > 0 and all(isinstance(p, str) and p.startswith('mnVideo') for p in ops)


def status_card(c):
    hit = []
    def has_vid_all(o):
        found = []
        walk(o, lambda x: found.append(1) if is_vid_all(x) else None)
        return bool(found)
    def f(o):
        card = o.get('card')
        if isinstance(card, list) and 'max-w-[1060px]' in str(o.get('className', '')):
            kids = [k for k in card if isinstance(k, dict) and has_vid_all(k)]
            if kids: hit.append(kids)
    walk(c['phases'], f)
    assert len(hit) == 1 and len(hit[0]) == 1, [len(h) for h in hit]
    return hit[0][0]


def apply(c) -> int:
    st = status_card(c)
    if any(isinstance(k, dict) and k.get('value') == WARN for k in st['card']): return 0
    st['card'].append({'el': 'text', 'value': WARN, 'icon': 'info', 'className': WARN_CLS,
                       'when': {'op': 'gt', 'a': {'op': 'count', 'from': 'tasks'}, 'b': 0}})
    return 1


if __name__ == '__main__':
    for F in sys.argv[1:]:
        raw = open(F, encoding='utf-8').read()
        indent = 2 if raw.startswith('{\n  "') else 1
        c = json.loads(raw)
        k = apply(c)
        assert json.dumps(c, ensure_ascii=False).count(WARN) == 1
        if k: open(F, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=indent) + ('\n' if raw.endswith('\n') else ''))
        print(f'{F}: บรรทัดเตือนหน้าผลิต {k} จุด')
