#!/usr/bin/env python3
# showhow-v27-board-retry-one.py — ปุ่ม "วาดบอร์ดนี้ใหม่" (วาดใหม่เฉพาะช่วงที่กำลังดู) · 6 ช่วง
# ที่มา: พี่หมีถาม 2026-09-21 ว่ามีระบบซ่อมบอร์ดเพี้ยนเหมือน minimal ไหม — ตรวจแล้ว showhow ไม่มี
#   ของเดิม: "Gen ภาพใหม่" = force ทั้ง chain ⇒ วาดใหม่ทุกช่วง (คลิป 60 วิ = เผา 6 เครดิตเพื่อซ่อม 1 ใบ)
#            "ลองใหม่" ไม่ force ⇒ ข้ามช่องที่มีภาพแล้ว ใบที่เพี้ยนไม่มีวันถูกวาดใหม่
#   ของใหม่: ปุ่มใต้ไทล์ · chain มี op เดียวของช่วงนั้น · เงื่อนไขการโชว์ **คัดลอกจากไทล์ที่ตาเห็น** มาทั้งดุ้น
# บทเรียนที่ minimal ส่งมา (เอามาใช้ครบ):
#   ① ไทล์ไม่ได้ถูกกั้นด้วย svSec ⇒ ลดความยาว (60→30) แล้ว bview ค้างที่ 4-6 · ปุ่มต้องกั้น "ช่วงนี้มีจริงที่ความยาวปัจจุบัน" = svSec > 10(k-1)
#   ② กันกดตอนกำลังรัน: not(status=running or meta.retrying=1)
#   ③ ใส่ให้ครบทุกมุมมอง (เขาพลาดรอบแรก ใส่แค่ list view แล้วโหมดออโต้มองไม่เห็น) ⇒ สคริปต์นี้หา **ทุกกล่อง** ที่มีไทล์บอร์ด ≥2 ใบ
#   ④ ห้ามใช้ป้ายว่าง (ยาม starter indexOf('') = 0 → จับผิดทุกข้อความ) ⇒ ปุ่มมีข้อความเสมอ
#   🪤 เก็บรายชื่อโหนดให้ครบก่อนค่อยแก้ (แก้ระหว่าง walk = RecursionError)
# รันซ้ำได้: ตรวจ marker `sh-board-retry-one`
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
MARK = 'sh-board-retry-one'
SLOT = re.compile(r'^\{item\.slots\.(board(\d*))\}$')
BTN_CLASS = ('w-full justify-center !h-10 !rounded-xl !text-[13px] @[640px]:!text-[12px] font-bold '
             'border border-[var(--ev-border)] !bg-[var(--ev-surface)] !min-h-[48px] @[420px]:!min-h-0 ' + MARK)

raw = open(P, encoding='utf-8').read(); d = json.loads(raw)
if MARK in raw: sys.exit(f'· มี {MARK} อยู่แล้ว ข้าม')

def walk(node, path=''):
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items(): yield from walk(v, f'{path}/{k}')
    elif isinstance(node, list):
        for i, v in enumerate(node): yield from walk(v, f'{path}[{i}]')

# ── ① หา "กล่องไทล์บอร์ด" ทุกกล่อง (ไม่ฮาร์ดโค้ด path) ──────────────────
targets = []
for path, node in walk(d):
    if not (isinstance(node, dict) and isinstance(node.get('card'), list)): continue
    tiles = [(c, SLOT.match(str(c.get('src', '')))) for c in node['card'] if isinstance(c, dict) and c.get('el') == 'media-slot']
    tiles = [(c, m.group(1), int(m.group(2) or 1)) for c, m in tiles if m]
    if len(tiles) >= 2: targets.append((path, node, tiles))
assert targets, '✗ ไม่เจอกล่องไทล์บอร์ดสักกล่อง — โครงหน้าผลิตเปลี่ยนไปแล้ว ห้ามเดา'
print(f'เจอกล่องไทล์บอร์ด {len(targets)} กล่อง (มุมมองละกล่อง):')

def op_of(k): return 'mnBoard' if k == 1 else f'mnBoard{k}'

added = 0
for path, node, tiles in targets:
    row = {'el': 'box', 'className': 'mt-2 grid grid-cols-1 gap-2', 'card': []}
    for tile, slot, k in sorted(tiles, key=lambda t: t[2]):
        when_parts = []
        if tile.get('when') is not None: when_parts.append(tile['when'])              # ★เงื่อนไข "ใบที่ตาเห็น" — ลอกจากไทล์
        when_parts.append({'op': 'gt', 'a': '{values.svSec}', 'b': 10 * (k - 1)})      # ① ช่วงนี้มีจริงที่ความยาวปัจจุบัน
        when_parts.append({'op': 'not', 'a': {'op': 'or', 'list': [                    # ② กันกดตอนกำลังรัน
            {'op': 'eq', 'a': '{item.status}', 'b': 'running'},
            {'op': 'eq', 'a': '{item.meta.retrying}', 'b': '1'}]}})
        row['card'].append({'el': 'retry-button', 'op': op_of(k), 'chain': [op_of(k)],
                            'label': f'วาดบอร์ดช่วง {k} ใหม่', 'icon': 'replay', 'variant': 'ghost',
                            'className': BTN_CLASS,
                            'when': {'op': 'and', 'list': when_parts}})
        added += 1
    node['card'].append(row)
    print(f'  + {len(row["card"])} ปุ่ม → {path}')

open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print(f'✓ v27 · ปุ่มรวม {added} ตัว ·', os.path.getsize(P), 'bytes')
