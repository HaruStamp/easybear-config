#!/usr/bin/env python3
"""showhow-v91b — ช่องรูปตอนเริ่ม/ตอนจบ: ปุ่มแน่นเกินที่ความกว้างไอโฟน (390)

เห็นจาก UI Lab ที่ 390px: ปุ่ม "เลือกภาพ" ขึ้น 2 บรรทัด ปุ่มล้นกรอบ
สาเหตุ: v91 ลอกคลาสปุ่มจากช่องรูปพื้นที่ (กว้างกว่า · ตัวอักษร 18px · สูง 52px) มาใส่ช่องกว้าง 112px
แก้: ช่องกว้าง 124px · ปุ่มสูง 42px · ตัวอักษร 15/14px · ห้ามตัดบรรทัด
ใช้: python3 scripts/showhow-v91b-ref-tile-fit.py
"""
import json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


story = c['phases'][0]['form'][2]['card'][0]['card'][0]['card'][5]
n = 0
for x in walk(story):
    if not isinstance(x, dict):
        continue
    if x.get('into') in ('openRef', 'endRef') and x.get('el') in ('upload', 'pick-button'):
        cls = x['className']
        for a, b in (('!h-[52px]', '!h-[42px]'), ('!text-[18px]', '!text-[15px]'), ('@[640px]:!text-[17px]', '@[640px]:!text-[14px]')):
            assert a in cls, f'{x["into"]}: ไม่เจอ {a}'
            cls = cls.replace(a, b)
        x['className'] = cls + ' whitespace-nowrap !px-2 !gap-1'
        n += 1
    if isinstance(x.get('className'), str) and 'w-[112px]' in x['className']:
        x['className'] = x['className'].replace('w-[112px]', 'w-[124px]'); n += 100
assert n == 4 + 400, f'ควรแก้ปุ่ม 4 ตัว + ช่อง 4 กล่อง · ได้ {n}'
print('ช่องรูปตอนเริ่ม/จบ: กว้าง 124px · ปุ่มสูง 42 · ตัวอักษร 15/14 · ไม่ตัดบรรทัด')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
