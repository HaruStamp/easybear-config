#!/usr/bin/env python3
"""showhow-v116 — เงื่อนไขแบบข้อความที่ซ้อนใน and/or/not "จริงเสมอ" → แปลงเป็น object (podcast ทัก · ยืนยันจากซอร์ส engine 2026-09-28)

engine-bind.ts:254 `and`/`or`/`not` ส่งลูกแต่ละตัวเข้า resolveValue → สตริง 'item.data.plan.0.s1th!=' ถูกอ่านเป็น
ข้อความธรรมดา (ไม่ว่าง = truthy) ⇒ **จริงเสมอ** · ข้อความเงื่อนไขถูกแปลเป็นเงื่อนไขเฉพาะตอนเป็น `when` ชั้นบนสุดเท่านั้น
ผล: ① validate ของ mnPlan เช็คได้แค่ "จำนวนคลิป" — ฉากขาดก็ผ่าน ไม่ retry (1,640 จุด)
    ② หน้าผลิต/คลังคลิป 65 จุด 'values.svSec<=N OR ครบช่วง N+1' ⇒ "คลิปเสร็จ" ตัดสินจากช่วง 1 อย่างเดียว
       (ปกติยังถูกเพราะช่วง 1 ทำสุดท้าย · ผิดเฉพาะเคสช่วงกลางล้ม)
แก้: แปลงทุกสตริงเงื่อนไขที่ซ้อนอยู่ เป็น object ที่ engine ประเมินจริง (ความหมายเดิมทุกตัว)
   'X!='   → {not:{eq:'{X}',''}}     'X=v' → {eq:'{X}','v'}     'X!=v' → {not:{eq}}
   'X<=n'  → {lte}  'X>=n' → {gte}  'X<n' → {lt}  'X>n' → {not:{lte}}
ใช้: python3 scripts/showhow-v116-nested-string-preds.py
"""
import json, re
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
PRED = re.compile(r'^([A-Za-z_][A-Za-z0-9_.]*)\s*(!=|>=|<=|=|<|>)(.*)$')
n = 0


def conv(s):
    m = PRED.match(s)
    f, op, v = m.group(1), m.group(2), m.group(3)
    ref = '{' + f + '}'
    if op == '=':  return {'op': 'eq', 'a': ref, 'b': v}
    if op == '!=': return {'op': 'not', 'a': {'op': 'eq', 'a': ref, 'b': v}}
    if op == '<=': return {'op': 'lte', 'a': ref, 'b': v}
    if op == '>=': return {'op': 'gte', 'a': ref, 'b': v}
    if op == '<':  return {'op': 'lt', 'a': ref, 'b': v}
    if op == '>':  return {'op': 'not', 'a': {'op': 'lte', 'a': ref, 'b': v}}


def walk(x):
    global n
    if isinstance(x, dict):
        if x.get('op') in ('and', 'or', 'not'):
            if isinstance(x.get('list'), list):
                for i, k in enumerate(x['list']):
                    if isinstance(k, str) and PRED.match(k): x['list'][i] = conv(k); n += 1
            for key in ('a', 'b'):
                if isinstance(x.get(key), str) and PRED.match(x[key]): x[key] = conv(x[key]); n += 1
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)


walk(c)
print('แปลงเงื่อนไขซ้อน', n, 'จุด')
# ยาม: ไม่เหลือสตริงเงื่อนไขซ้อน · ไม่มีตัวดำเนินการ ~ @ ที่แปลงไม่ได้
left = []
def chk(x):
    if isinstance(x, dict):
        if x.get('op') in ('and', 'or', 'not'):
            for k in (x.get('list') or []) + [x.get('a'), x.get('b')]:
                if isinstance(k, str) and re.match(r'^[A-Za-z_][A-Za-z0-9_.]*\s*(!=|=|~|@|>=|<=|>|<)', k): left.append(k)
        for v in x.values(): chk(v)
    elif isinstance(x, list):
        for v in x: chk(v)
chk(c)
assert not left and n == 1705, (n, left[:3])
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✅ ไม่เหลือสตริงเงื่อนไขซ้อน')
