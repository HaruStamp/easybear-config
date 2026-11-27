#!/usr/bin/env python3
"""minimal-v68 (ตัวขาย r32 · 27 พ.ย. 2569 · ห้อง easybear หลัง QA เด้งออก apps/minimal/docs/qa/2026-11-27-bounce-out.md)
  ① ปุ่ม "แปลงเป็นบทวิดีโอ" (mn-tr-force · 15 จุด) สูง 32px บนมือถือ → 44px (`!h-11 @[420px]:!h-8`) · จอใหญ่เท่าเดิม (ยาม minimal-mobile-tier ⑤)
  ② เลือก 20/30 วิ แล้วสลับเป็น 360p: UI บอก "360p ทำได้แค่ 10 วิ" + สรุปเครดิตคิด 720p ตามความยาวเดิม แต่คำขอ Omni 1.1 ไม่ส่งคีย์ ส่วน 1.2 ส่ง 720p
     ⇒ กรณีนี้ส่ง 720p ชัดทั้ง 2 รุ่น (ตรงกับบรรทัดสรุป · เครดิต 1.1 = 15 · 1.2 = 30 ต่อ 10 วิ) · ค่าเริ่ม 720p/Omni 1.1 ยังไม่ส่งคีย์เหมือนเดิมทุกไบต์
     แอปอื่นตรวจแล้วไม่มีช่องนี้: hardsell/petdance ส่ง 720p ชัดเสมอ · showhow/podcast/parody 360p ทุกความยาว · fashion 360p ใช้ความยาว 10 วิ (lookup svSec|svRes)
  ③ บรรทัดเตือนในหน้าผลิต (มีคลิปแล้ว): ระหว่างรอวิดีโออย่าสลับแอป/ล็อกจอ + บันทึกไว้ก่อน (รีโหลด = งานหาย ไม่มีบันทึกอัตโนมัติฝั่งลูกค้า)
  ใช้ของที่ engine 1.22 มีครบ (text + icon + when/count) — ตัวขายเก่าอ่าน minimal-public ตัวเดียวกัน
ใช้: python3 scripts/minimal-v68-tap-res-warn.py <ไฟล์ config>…   (แก้ในที่ · รันซ้ำ = ไม่เปลี่ยน)
"""
import json, sys

TR_OLD, TR_NEW = '!h-8 !min-h-0', '!h-11 @[420px]:!h-8 !min-h-0'
WARN = 'ระหว่างรอวิดีโอ อย่าสลับแอปหรือล็อกจอ · ได้บอร์ดครบแล้วกดบันทึกมุมขวาบนเก็บไว้ก่อน'
WARN_CLS = '!text-[12.5px] leading-snug opacity-60 px-0.5'
IS360 = {'op': 'eq', 'a': '{values.svRes}', 'b': '360p'}


def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in o.values(): walk(v, fn)
    elif isinstance(o, list):
        for v in o: walk(v, fn)


def fix_tap(c):
    n = [0]
    def f(o):
        cls = o.get('className')
        if isinstance(cls, str) and 'mn-tr-force' in cls and TR_OLD in cls and TR_NEW not in cls:
            o['className'] = cls.replace(TR_OLD, TR_NEW, 1); n[0] += 1
    walk(c['phases'], f)
    return n[0]


def fix_res(c):
    n = 0
    for o in c['ops']:
        if o.get('type') != 'video': continue
        r = o['resolution']
        assert r['op'] == 'cond' and r['then'] == '360p' and r['else']['op'] == 'cond' and r['else']['then'] == '720p' and r['else']['else'] == '', o['id']
        w = r['else']['when']
        if w.get('op') == 'or' and IS360 in w.get('list', []): continue   # ทำแล้ว
        r['else']['when'] = {'op': 'or', 'list': [w, dict(IS360)]}   # รุ่น 1.2 หรือ (เลือก 360p แต่ยาวเกิน 10 วิ) ⇒ 720p ชัด
        n += 1
    return n


def produce_box(c):
    """กล่องหน้าผลิต = กล่องที่มีการ์ดสถานะ (ปุ่ม gen-phase วิดีโอทั้งหมด) เป็นลูกตรง"""
    hit = []
    def has_vid_all(o):
        found = []
        walk(o, lambda x: found.append(1) if x.get('el') == 'gen-phase' and x.get('ops') == ['mnVideo3', 'mnVideo2', 'mnVideo'] else None)
        return bool(found)
    def f(o):
        card = o.get('card')
        if isinstance(card, list) and 'max-w-[1060px]' in str(o.get('className', '')):
            kids = [k for k in card if isinstance(k, dict) and has_vid_all(k)]
            if kids: hit.append((o, kids[0]))
    walk(c['phases'], f)
    assert len(hit) == 1, len(hit)
    return hit[0]


def add_warn(c):
    box, status = produce_box(c)   # ต่อท้ายการ์ดสถานะ (ไม่แทรกกลาง = path ของแถวอื่นไม่เลื่อน · ยาม row-collisions เทียบด้วย path)
    if any(isinstance(k, dict) and k.get('value') == WARN for k in status['card']): return 0
    status['card'].append({'el': 'text', 'value': WARN, 'icon': 'info', 'className': WARN_CLS,
                               'when': {'op': 'gt', 'a': {'op': 'count', 'from': 'tasks'}, 'b': 0}})
    return 1


for F in sys.argv[1:]:
    raw = open(F, encoding='utf-8').read()
    indent = 2 if raw.startswith('{\n  "') else 1
    c = json.loads(raw)
    n = {'tap': fix_tap(c), 'res': fix_res(c), 'warn': add_warn(c)}
    s = json.dumps(c, ensure_ascii=False)
    assert s.count(TR_NEW) == 15 and s.count('mn-tr-force') == 15, s.count(TR_NEW)
    assert s.count(WARN) == 1
    open(F, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=indent) + ('\n' if raw.endswith('\n') else ''))
    print(F, n)
