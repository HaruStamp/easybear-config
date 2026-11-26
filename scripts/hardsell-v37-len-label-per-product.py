#!/usr/bin/env python3
# hardsell-dev v37: ป้ายความยาว "N วิ / คลิป" หน้าผลิต + หน้าคลัง อ่านค่าจริงรายสินค้า (polish อัปเดตใหญ่ 27 พ.ย.)
#   เดิม = ค่ากลาง {values.svSec} เสมอ ⇒ สินค้าที่ตั้งเฉพาะ (v33 own → ownSec) 20 วิ ป้ายยังขึ้น "10 วิ / คลิป"
#   ใหม่ = มีงาน (tasks) ที่มี eSec แล้ว → รวมค่าที่ใช้จริงทุกงาน เรียงน้อย→มาก คั่น "/" (เช่น "10/20 วิ / คลิป")
#          ยังไม่มีงาน / งานเก่าไม่มี eSec → ป้ายเดิมทุกไบต์
# ใช้: python3 scripts/hardsell-v37-len-label-per-product.py [hardsell-dev.json]   (รันบน v33+ · รันซ้ำได้)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F, encoding='utf-8'))
OLD = {"op": "concat", "parts": [{"op": "lookup", "table": "lenSecs", "key": "{values.svSec}", "fallback": "10"}, " วิ / คลิป"]}
SECS = ['8', '10', '16', '20']
assert set(d['lookups']['lenSecs']) == set(SECS), d['lookups']['lenSecs']
cnt = lambda w: {"op": "count", "from": "tasks", "where": w}
has = lambda w: {"op": "gt", "a": cnt(w), "b": 0}
PER = {"op": "concat", "parts": [
    {"op": "cond", "when": has("eSec=" + s), "then": {"op": "concat", "parts": [{"op": "cond", "when": has("eSec<" + s), "then": "/", "else": ""}, s]}, "else": ""}
    for s in SECS] + [" วิ / คลิป"]}
NEW = {"op": "cond", "when": has("eSec!="), "then": PER, "else": OLD}
n = [0, 0]
def walk(o):
    if isinstance(o, dict):
        if o.get('el') == 'text' and o.get('value') == OLD: o['value'] = json.loads(json.dumps(NEW)); n[0] += 1; return
        if o.get('el') == 'text' and o.get('value') == NEW: n[1] += 1; return
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(d['phases'])
assert n[0] + n[1] == 2, n   # หน้าผลิต (หัว) + หน้าคลัง (แถบเสร็จ)
q = next(o for o in d['ops'] if o['id'] == 'mnQueue')['spawn']['fields']
assert 'eSec' in q, 'ต้องมี v33 (eSec ในงาน) ก่อน'
print(f'v37: ป้ายความยาวอ่านค่ารายสินค้า {n[0]} จุด (มีแล้ว {n[1]})')
open(F, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2))
