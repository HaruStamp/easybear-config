#!/usr/bin/env python3
# minimal-v25-planfail-one-card.py — หน้าตั้งค่าเหลือการ์ดเตือน "เขียนบทไม่สำเร็จ" ใบเดียว (2026-09-17 · พี่หมีเคาะ: เก็บใบเหลือง v18)
#
# อาการ: สินค้าเขียนบทพลาด · tasks 0 · หยุดแล้ว ⇒ หน้าตั้งค่าโชว์การ์ดเตือน 2 ใบซ้อนกัน
#   ใบเหลือง (v18 B)  "เขียนบทไม่สำเร็จบางสินค้า — กด "เริ่ม" อีกครั้งเพื่อลองเขียนใหม่"   when count(error)>0
#   ใบแดง (ของเดิม bf769ec)  "เขียนบทไม่สำเร็จ N สินค้า — ยังไม่ได้เริ่มผลิต" + วิธีแก้     when not running ∧ tasks=0 ∧ count(error)>0
#   v18 B ตั้งใจให้เหลือ "การ์ดเตือนใบเดียว" แต่ไม่ได้ถอดใบแดง ⇒ ถอดใบแดงออก
#
# หาด้วยความหมาย ไม่ใช้ index · assert ก่อนเขียนทับ · รันซ้ำได้ (idempotent)
import json, sys, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / (sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json')
c = json.loads(SRC.read_text(encoding='utf-8'))
J = lambda o: json.dumps(o, ensure_ascii=False)

YELLOW = 'เขียนบทไม่สำเร็จบางสินค้า — กด "เริ่ม" อีกครั้งเพื่อลองเขียนใหม่'
COUNT_ERR = {'op': 'count', 'from': 'products', 'where': 'status=error'}

forms = c['phases'][0]['form']
setup = [f for f in forms if '"setup"' in J(f.get('when'))]
assert len(setup) == 1, 'หาหน้าตั้งค่าไม่เจอ/เจอหลายหน้า: %d' % len(setup)
setup = setup[0]

def is_red(n):
    """กล่องที่มี when และลูกหลานมีข้อความ concat 'เขียนบทไม่สำเร็จ ' + count(error) + ' สินค้า — ยังไม่ได้เริ่มผลิต'"""
    if not (isinstance(n, dict) and n.get('when') is not None and isinstance(n.get('card'), list)): return False
    hit = []
    def w(o):
        if isinstance(o, dict):
            v = o.get('value')
            if o.get('el') == 'text' and isinstance(v, dict) and v.get('op') == 'concat' and COUNT_ERR in v.get('parts', []) \
               and any(isinstance(p, str) and 'ยังไม่ได้เริ่มผลิต' in p for p in v.get('parts', [])):
                hit.append(o)
            for x in o.values(): w(x)
        elif isinstance(o, list):
            for x in o: w(x)
    w(n)
    return bool(hit)

holders = []   # (list ที่ถือการ์ด, การ์ด) — เก็บให้ครบก่อนแก้
def walk(o):
    if isinstance(o, dict):
        if isinstance(o.get('card'), list):
            for ch in o['card']:
                if is_red(ch) and not any(is_red(g) for g in (ch.get('card') or []) if isinstance(g, dict)):
                    holders.append((o['card'], ch))
        for x in o.values(): walk(x)
    elif isinstance(o, list):
        for x in o: walk(x)
walk(setup)

yellow_n = J(setup).count(J(YELLOW)[1:-1])
assert yellow_n == 1, 'ใบเหลือง v18 ต้องมี 1 ใบพอดี (เจอ %d) — ห้ามถอดใบแดงถ้าไม่มีใบที่มาแทน' % yellow_n

changed = []
assert len(holders) <= 1, 'เจอใบแดงมากกว่า 1 ใบ (%d) — หยุดก่อน ตรวจด้วยตา' % len(holders)
for lst, card in holders:
    lst.remove(card)
    changed.append('ถอดการ์ดแดง "เขียนบทไม่สำเร็จ N สินค้า" ออกจากหน้าตั้งค่า (เหลือใบเหลือง v18)')

if changed:
    SRC.write_text(json.dumps(c, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('✅ ' + SRC.name + ': ' + ' · '.join(changed))
else:
    print('— ' + SRC.name + ': แพตช์แล้ว ไม่มีอะไรเปลี่ยน')
