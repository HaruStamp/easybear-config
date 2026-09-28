#!/usr/bin/env python3
# hardsell-v14-validate-op-predicates.py — ตัวตรวจบทรายฉาก (v10) ไม่เคยทำงาน: แปลงเงื่อนไขแบบข้อความใน and/or/not เป็น op
#
# ที่มา: podcast แจ้ง 2026-09-28 (พิสูจน์บน engine v1.15.0 · แจ้ง starter แล้ว) — สตริงเงื่อนไขอย่าง
#   'item.data.plan.0.s1th!=' / 'values.svSec<=8' ที่อยู่ใน list/a/b ของ op and/or/not ถูก resolveValue อ่านเป็น
#   "สตริงไม่ว่าง" = จริงเสมอ ⇒ validate ของเราเช็คได้แค่จำนวนคลิป · ผมวัดซ้ำเอง: บท 16 วิ ขาด s6en / มีแค่ 4 ฉาก /
#   8 วิ ขาด s3en — ผ่านหมดทั้ง 5 กรณี · กับดักตระกูลเดียวกับ §⑤ ข้อ 36 ที่ผมเพิ่งเจอกับ Cast (v13)
#   🪤 dry-run สถานการณ์ E ผ่านมาตลอดเพราะมันทดสอบ "จำนวนคลิปขาด" ซึ่งเป็นส่วนเดียวที่ทำงาน · ไม่มีเคส "ฉากขาด"
# วิธี: สตริงเงื่อนไขเฉพาะที่อยู่ใน list/a/b ของ op and/or/not → op จริง (`when`/`where` ระดับบนสุดที่เป็นสตริงเดี่ยวทำงานถูก ไม่แตะ)
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PRED = re.compile(r'^\s*([\w.]+)\s*(!=|>=|<=|>|<|=)\s*(.*?)\s*$')
OPS = {'<=': 'lte', '>=': 'gte', '<': 'lt', '>': 'gt'}


def to_op(s):
    path, cmp, rhs = PRED.match(s).groups()
    a = '{%s}' % path
    if cmp == '=': return {'op': 'eq', 'a': a, 'b': rhs}
    if cmp == '!=': return {'op': 'not', 'a': {'op': 'eq', 'a': a, 'b': rhs}}
    return {'op': OPS[cmp], 'a': a, 'b': rhs}


def fix(n, inop=False, stat=None):
    if isinstance(n, dict):
        isop = n.get('op') in ('and', 'or', 'not')
        for k in list(n):
            v = n[k]
            if isop and k in ('list', 'a', 'b') and isinstance(v, str) and PRED.match(v) and not v.startswith('{'):
                n[k] = to_op(v); stat.append(v)
            else:
                fix(v, isop and k in ('list', 'a', 'b'), stat)
    elif isinstance(n, list):
        for i, v in enumerate(n):
            if inop and isinstance(v, str) and PRED.match(v) and not v.startswith('{'):
                n[i] = to_op(v); stat.append(v)
            else:
                fix(v, False, stat)


def main():
    src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json'))
    cfg = json.load(open(src, encoding='utf-8'))
    stat = []
    fix(cfg, False, stat)
    if not stat:
        print('⏭  ไม่มีเงื่อนไขแบบข้อความใน and/or/not แล้ว — ไม่ทำอะไร'); return
    assert len(stat) == 24, 'เจอ %d จุด (ตรวจไว้ 24 จุด ทั้งหมดอยู่ใน mnPlan.validate) — config ขยับ หยุดก่อน' % len(stat)
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v14 ลงแล้ว — แปลงเงื่อนไข %d จุดใน mnPlan.validate เป็น op (%s …)' % (len(stat), ', '.join(sorted(set(stat))[:3])))


main()
