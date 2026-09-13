#!/usr/bin/env python3
# minimal-v17-savegroups.py — เซฟ/โหลดโปรเจกต์แบบ "เลือกเฉพาะส่วน" (2026-09-12)
#
# ที่มา (พี่หมีสั่ง): ของเดิมมีปุ่มเดียวคือ "เซฟสินค้า" (scope=products) ⇒ ได้แค่สินค้า+บท
#   ไม่ได้คลิป ไม่ได้การตั้งค่า ไม่ได้ความคืบหน้า ⇒ โหลดกลับมาต้องตั้งค่าใหม่และผลิตใหม่ทั้งหมด
#   และ `saveContent` ที่เขียนไว้สวยงามไม่เคยถูกเรียกเลย เพราะไม่มีปุ่มไหนตั้ง scope=parts
# ⇒ ประกาศ saveGroups + เพิ่มปุ่มเซฟ/โหลดโปรเจกต์ · ผู้ใช้ติ๊กได้ว่าจะเอาส่วนไหน
#   กฎที่พี่หมีวาง: ติ๊ก "ความคืบหน้า" = ลากการตั้งค่า+รายการสินค้ามาบังคับ · ติ๊กอย่างอื่น = อิสระ
#
# 🔴 ต้องใช้กับ engine ที่มี saveGroups แล้วเท่านั้น (golden ≥ v0.13.0) — ยังไม่ deploy = ปุ่มเซฟจะตกไปทางเดิม
# รันซ้ำได้ (idempotent)
import json, sys, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / (sys.argv[1] if len(sys.argv) > 1 else 'minimal-lab.json')
c = json.loads(SRC.read_text(encoding='utf-8'))
changed = []

# ── ① กลุ่มเซฟ ────────────────────────────────────────────────
#   🪤 พี่หมียุบกลุ่ม 2026-09-12 ดึก (หลังเห็นของจริงบนมือถือ): **มินิมอลแยกแค่ "การตั้งค่า" กับ "รายการสินค้า"**
#     สไตล์คลิป (sv*) + ตัวละคร (char*, characters) รวมเข้า "การตั้งค่า" ให้หมด
#     เหตุผล: 5 การ์ดบนจอมือถือ = ต้องเลื่อนหาทั้งที่ผู้ใช้มินิมอลไม่เคยอยากโหลด "สไตล์อย่างเดียว"
#     ⇒ engine ยังรองรับแยกละเอียดเท่าไหร่ก็ได้ (film ใช้ 8 กลุ่ม) — **จำนวนกลุ่มเป็นเรื่องของ config ไม่ใช่ engine**
#   🪤 requireField ของ prog = __tdone ซึ่งอยู่ใน item.data ⇒ ยังไม่กดเริ่ม = ไม่เขียนก้อนนี้ = ไม่มีการ์ดให้ติ๊ก
GROUPS = [
    {"id": "setup", "label": "การตั้งค่า", "icon": "tune", "rank": 1,
     "desc": "การตั้งค่า · สไตล์คลิป · การผลิต",
     "colls": ["characters"],
     # 🔴 absorbs = id กลุ่มรุ่นเก่าที่ยุบเข้ามา — ไฟล์เซฟที่ทำตอนยังแยก 5 กลุ่ม จะถูกนับเป็นของ "การตั้งค่า"
     #    ไม่มีบรรทัดนี้ = เปิดไฟล์เก่าแล้วเห็นการ์ด "สไตล์คลิป"/"ตัวละคร" แปลกปลอม
     #    และ **ติ๊ก "การตั้งค่า" แล้วไม่ได้ค่า sv- / char- มาด้วย โดยไม่มีอะไรเตือน** (พี่หมีเจอจริง 2026-09-13)
     "absorbs": ["style", "cast"],
     "values": ["mode", "clipsPerProduct", "viewMode", "batchDelay", "retryDelay", "sv*", "char*"]},
    {"id": "items", "label": "รายการสินค้า", "icon": "inventory_2", "rank": 4,
     "colls": ["products"]},
    # 🪤 เคยตั้ง tone:"muted" (สีจาง) — **สวนทางกับความสำคัญ** พี่หมีทัก 2026-09-12
    #    ใบนี้เป็นใบเดียวที่ "กดแล้วลากใบอื่นมาด้วย" ⇒ ต้องเด่นที่สุด ไม่ใช่จางที่สุด
    {"id": "prog", "label": "ความคืบหน้างาน", "icon": "donut_large", "rank": 9,
     "desc": "งานที่สั่งผลิต",
     "colls": ["control", "tasks"], "cursor": True, "requireField": "__tdone",
     # 🔴 "บท" ที่ mnPlan เขียนลง products[].data.plan เป็นงานที่เกิดหลังกด "เริ่ม" = ของกลุ่มนี้ ไม่ใช่ของสินค้า
     #    ไม่ย้าย = โหลดเฉพาะ "รายการสินค้า" แล้วบทครึ่ง ๆ ติดมาด้วย → แอปขึ้นเตือน "บทที่ได้มาไม่สมบูรณ์"
     #    (พี่หมีเจอจริง 2026-09-13) · ★data.plan เป็นหมุด "mnPlan เสร็จแล้ว" ในตัวมันเอง
     #    ⇒ ตัดออกแล้วกด "เริ่ม" จะคิดบทใหม่ให้เอง ไม่ติดตาย
     "dataOf": [{"coll": "products", "keys": ["plan"]}],
     "needs": ["items", "setup"]},
]
if c.get('saveGroups') != GROUPS:
    c['saveGroups'] = GROUPS
    changed.append('① saveGroups 3 กลุ่ม — ตั้งค่า(รวมสไตล์+ตัวละคร) · รายการสินค้า · ความคืบหน้า(ลาก 2 ตัวแรกมาด้วย)')

# ── ป้ายจำนวนที่โชว์ใต้ชื่อการ์ด (engine รองรับ {n} ตั้งแต่ golden v0.13.4) ──────
#   🪤 ป้ายว่าง = ซ่อน collection นั้นจากบรรทัดนับ · control กับ characters ผู้ใช้ไม่ต้องรู้ว่ามีกี่ชิ้น
LABELS = {"products": "สินค้า {n} รายการ", "tasks": "{n} งาน", "characters": "", "control": "", "project": "ข้อมูลโปรเจกต์"}
sc = c.setdefault('saveContent', {})
if sc.get('collLabels') != LABELS:
    sc['collLabels'] = LABELS
    changed.append('① ป้ายนับ: สินค้า N รายการ · N งาน · ซ่อน control/characters')

# ── ยามก่อนเขียน: ทุกคีย์/ทุก collection ต้องมีกลุ่ม ────────────
import fnmatch
keys = [k for k in (c.get('values') or {}) if not k.startswith('__')]
colls = list((c.get('collections') or {}).keys())
def claimed(k):
    return any(any(fnmatch.fnmatchcase(k, p) for p in (g.get('values') or [])) for g in GROUPS)
miss_k = [k for k in keys if not claimed(k)]
miss_c = [x for x in colls if not any(x in (g.get('colls') or []) for g in GROUPS)]
assert not miss_k, 'คีย์ตั้งค่าไม่มีกลุ่ม: %s' % miss_k
assert not miss_c, 'collection ไม่มีกลุ่ม: %s' % miss_c

# ── ② ❌ ถอดออกแล้ว: กลุ่ม "เซฟ / โหลดโปรเจกต์" บนหน้าตั้งค่า ────────────
#   🪤 ผมเคยใส่กลุ่มนี้เข้าไป **ทั้งที่ engine มีปุ่มอยู่แล้ว** — พี่หมีทัก (2026-09-12)
#     NavBar มุมขวาบนเรียก on.save({scope:'parts'}) / on.load({mode:'replace'}) อยู่แล้ว
#     (app-render.tsx · โชว์เสมอเว้นแต่ config ตั้ง persistBar:false — minimal ไม่ได้ตั้ง)
#   ⇒ ปุ่มที่ผมเพิ่ม ทำงานเหมือนกันเป๊ะทุกอย่าง = UI ซ้ำซ้อนล้วน ๆ
#   🔑 ที่พลาดเพราะสแกนแต่ "ปุ่มที่ประกาศใน config" แล้วสรุปว่าไม่มีใครใช้ scope=parts
#      — จริงตามที่สแกน แต่ผิดตามความจริง เพราะทางนั้น engine เรียกเอง ไม่ผ่าน config
#      (โรคเดิม: อ่านที่เดียวแล้วสรุปทั้งระบบ · กฎที่มีอยู่แล้ว: ก่อนเติมของ ให้ไล่ของที่มีก่อนเสมอ)
#   ★ระบบ saveGroups (ข้อ ①) ยังอยู่ครบ — มันทำงานผ่านปุ่มมุมขวาบนนั่นแหละ
kids = c['phases'][0]['form'][0]['card'][0]['card']
_old = [i for i, k in enumerate(kids) if json.dumps(k, ensure_ascii=False).find('เซฟ / โหลดโปรเจกต์') >= 0]
for i in reversed(_old):
    kids.pop(i)
    changed.append('② ถอดกลุ่ม "เซฟ / โหลดโปรเจกต์" ออก (ซ้ำกับปุ่มมุมขวาบนที่ engine มีอยู่แล้ว)')

# ── ยามปิดท้าย: ปุ่มเดิมของหน้าสินค้าต้องไม่ถูกแตะ ──────────────
j = json.dumps(c, ensure_ascii=False)
assert j.count('"เซฟสินค้า"') == 1 and j.count('"โหลดสินค้า"') == 1, 'ปุ่มเดิมของหน้าสินค้าหาย/ซ้ำ'
assert j.count('"scope": "parts"') == 0, 'ไม่ควรมีปุ่ม scope=parts ใน config — engine มีปุ่มมุมขวาบนให้แล้ว'

SRC.write_text(json.dumps(c, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'— {SRC.name} —')
print('\n'.join('  ✔ ' + x for x in changed) if changed else '  (ไม่มีอะไรเปลี่ยน — รันซ้ำแล้วนิ่ง)')
