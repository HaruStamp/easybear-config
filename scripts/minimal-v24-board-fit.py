#!/usr/bin/env python3
"""v24 — prompt สตอรีบอร์ดของ minimal: ย้ายกฎพรีเซนเตอร์ขึ้นหน้า + ยุบบรรทัดปิดท้ายที่ซ้ำกับบรรทัดสไตล์

ปัญหา (ยาม scripts/lab/prompt-clamp-matrix.ts จับได้ 2026-09-15):
  prompt บอร์ดยาวเกินเพดาน 3900 ในคู่ผสม 30 วิ + ใช้รูปใบหน้า + ชื่อสินค้ายาว (วัดได้ 3,934)
  ⇒ ส่วนที่ถูกตัดคือ **บรรทัดสุดท้าย = กฎพรีเซนเตอร์** (ล็อกหน้า/สินค้าเด่นกว่าคน) — กฎหาย ไม่ใช่แค่บทหาย
  🪤 บอร์ดไม่ได้ถูกแก้ใน v23 ⇒ ตัวขาย v2 ที่ live อยู่ก็เป็นแบบนี้มาตลอด

ทางแก้ (พี่หมีเลือกข้อ ก · 2026-09-16) — **ห้ามลดรายละเอียดบท/สตอรีบอร์ด**:
  ① ย้าย "พรีเซนเตอร์: …" + lookup charBoard จากท้าย prompt ขึ้นไปต่อจากกติกาเหล็ก (ก่อนบล็อก Overlay/5 แถว)
     ⇒ ถ้าวันหน้าโดนตัดอีก ส่วนที่หายคือท้ายบทฉากสุดท้าย ไม่ใช่กฎ
  ② ยุบบรรทัด 'ปิดท้ายทุกภาพด้วย: "Scandinavian Minimal, Soft Natural Light, 4K, Clean Layout"'
     เข้ากับบรรทัด "สไตล์ภาพรวม:" ที่พูดเรื่องเดียวกัน — คำอังกฤษที่โมเดลภาพใช้ยังอยู่ครบทุกคำ

usage: python3 scripts/minimal-v24-board-fit.py [src.json] [dst.json]   (ค่าตั้งต้น = แก้ minimal-lab.json ในที่)
"""
import json, sys, copy, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'minimal-lab.json'
DST = Path(sys.argv[2]) if len(sys.argv) > 2 else SRC
BOARD_OPS = ('mnBoard', 'mnBoard2', 'mnBoard3')

CLOSING = '\n\nปิดท้ายทุกภาพด้วย: "Scandinavian Minimal, Soft Natural Light, 4K, Clean Layout"'
PRES_HDR_OLD = '\n\nพรีเซนเตอร์: {values.svChar} — '
PRES_HDR_NEW = 'พรีเซนเตอร์: {values.svChar} — '
STYLE_OLD = 'หัวข้อตัวอักษรสีเข้มที่เข้ากับโทนสีของคลิป (เลือกให้เอง), เส้นสายเรียบง่าย'
STYLE_NEW = 'หัวข้อตัวอักษรสีเข้มที่เข้ากับโทนสีของคลิป (เลือกให้เอง), เส้นสายเรียบง่าย (Clean Layout), แสงธรรมชาตินุ่ม (Soft Natural Light), 4K'

def placeholders(n):
    return collections.Counter(re.findall(r'\{(?:item|values)\.[a-zA-Z0-9_.]+\}', json.dumps(n, ensure_ascii=False)))

def whens(n):
    out = []
    def w(x):
        if isinstance(x, dict):
            if 'when' in x: out.append(json.dumps(x['when'], ensure_ascii=False, sort_keys=True))
            for v in x.values(): w(v)
        elif isinstance(x, list):
            for v in x: w(v)
    w(n); return collections.Counter(out)

c = json.loads(SRC.read_text(encoding='utf-8'))
ops = {o['id']: o for o in c['ops']}
# 🪤 เช็คแบบ substring ไม่ได้ — PRES_HDR_NEW เป็นสตริงย่อยของ PRES_HDR_OLD ⇒ ต้องเทียบ 'ทั้งชิ้น' ในลิสต์ parts
def patched(op):
    parts = op['prompt']['parts']
    return any(p == PRES_HDR_NEW for p in parts) and not any(p == CLOSING for p in parts)
if all(patched(ops[k]) for k in BOARD_OPS):
    print('✓ แพตช์แล้ว — ไม่ต้องทำซ้ำ'); sys.exit(0)

before = copy.deepcopy(c)
for k in BOARD_OPS:
    parts = ops[k]['prompt']['parts']
    # ① หา 3 ชิ้นท้าย: ปิดท้าย · หัวข้อพรีเซนเตอร์ · lookup charBoard
    i_close = next(i for i, p in enumerate(parts) if p == CLOSING)
    i_hdr = next(i for i, p in enumerate(parts) if p == PRES_HDR_OLD)
    i_look = next(i for i, p in enumerate(parts) if isinstance(p, dict) and p.get('table') == 'charBoard')
    assert i_close < i_hdr < i_look == len(parts) - 1, (k, i_close, i_hdr, i_look, len(parts))
    # ② จุดแทรก = หลังก้อนกติกาเหล็ก (ก้อนที่จบด้วย "ห้ามเดารายละเอียดด้านที่มองไม่เห็น")
    i_iron = next(i for i, p in enumerate(parts) if isinstance(p, str) and p.rstrip().endswith('ห้ามเดารายละเอียดด้านที่มองไม่เห็น'))
    assert i_iron < i_close, (k, i_iron)
    hdr, look = parts[i_hdr], parts[i_look]
    rest = [p for i, p in enumerate(parts) if i not in (i_close, i_hdr, i_look)]
    j = rest.index(parts[i_iron])
    new = rest[:j + 1] + [PRES_HDR_NEW, look, '\n\n'] + rest[j + 1:]
    # ③ ยุบบรรทัดปิดท้ายเข้าบรรทัดสไตล์
    assert sum(1 for p in new if isinstance(p, str) and STYLE_OLD in p) == 1, k
    new = [p.replace(STYLE_OLD, STYLE_NEW) if isinstance(p, str) and STYLE_OLD in p else p for p in new]
    ops[k]['prompt']['parts'] = new

# ── ยาม: ไม่มีอะไรนอกขอบเขตขยับ + ของในบอร์ดไม่หาย ─────────────
for key in c:
    if key != 'ops': assert c[key] == before[key], ('แตะก้อนนอกขอบเขต', key)
for ob, oa in zip(before['ops'], c['ops']):
    if ob['id'] in BOARD_OPS:
        assert {x: ob[x] for x in ob if x != 'prompt'} == {x: oa[x] for x in oa if x != 'prompt'}, ('op field อื่นขยับ', ob['id'])
        assert placeholders(ob['prompt']) == placeholders(oa['prompt']), ('ตัวแปรในบทหาย/งอก', ob['id'])
        assert whens(ob['prompt']) == whens(oa['prompt']), ('เงื่อนไข when ขยับ', ob['id'])
        # ถอดบรรทัดปิดท้าย 1 ชิ้น + เพิ่มตัวคั่น '\n\n' 1 ชิ้น ⇒ จำนวนชิ้นเท่าเดิม
        assert len(oa['prompt']['parts']) == len(ob['prompt']['parts']), ('จำนวนชิ้นผิด', ob['id'])
        for token in ['Scandinavian Minimal', 'Soft Natural Light', '4K', 'Clean Layout', 'พรีเซนเตอร์:', 'กติกาเหล็ก', 'รูปแบบเลย์เอาต์']:
            assert token in json.dumps(oa['prompt'], ensure_ascii=False), ('คำหาย', ob['id'], token)
    else:
        assert ob == oa, ('op อื่นขยับ', ob['id'])

DST.write_text(json.dumps(c, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'✓ เขียน {DST.name} · ops {", ".join(BOARD_OPS)}')
