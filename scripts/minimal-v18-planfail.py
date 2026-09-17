#!/usr/bin/env python3
# minimal-v18-planfail.py — UX ตอน "คิดบทไม่สำเร็จ" (2026-09-13 · พี่หมีเจอกับของจริง)
#
# อาการที่เจอ: 2 สินค้า → กดเริ่ม → คิดบทพลาดทั้งคู่ → เด้งกลับหน้าตั้งค่า
#   ① ข้อความ "เขียนบทไม่สำเร็จ" + ปุ่ม "คิดบทใหม่" โผล่ **แค่สินค้าตัวแรก** (when มี index==0)
#   ② ข้อความยาวเกิน → การ์ดรายการสินค้าเละ
#   ③ หน้าผลิต: สินค้า 1 ตัว 4 คลิป พอพลาด **ยุบเหลือการ์ดใบเดียว** (index==0 อีกที)
#
# สิ่งที่ทำ (config ล้วน):
#   A. หน้าตั้งค่า — ถอดกล่อง error + ปุ่มคิดบทใหม่ ออกจากการ์ดสินค้า
#   B. หน้าตั้งค่า — การ์ดเตือนใบเดียวเหนือปุ่ม "เริ่ม" บอกให้กดเริ่มอีกครั้ง
#   C. หน้าผลิต — การ์ด "เขียนบทไม่สำเร็จ" แสดงครบทุกคลิป (index < clipsPerProduct)
#   D. หน้าผลิต — ปุ่มคิดบทใหม่เปลี่ยนเป็น gen-phase [mnPlan,mnQueue] perProduct
#      ⇒ คิดบทใหม่แล้ว **เข้าคิวต่อเอง** + ตัวนับด้านบนอัปเดต (planQueueOne ทำให้ครบในตัว)
#      🔑 ทำไมไม่ใช้ chain: runChain ยึด over ของ op ตัวแรก ⇒ mnQueue (over=control) จะถูกข้าม**เงียบ**
# รันซ้ำได้ (idempotent)
import json, sys, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / (sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json')
c = json.loads(SRC.read_text(encoding='utf-8'))
changed = []

ERR_TITLE = 'เขียนบทไม่สำเร็จ — {item.name}'
RETRY_BTN = {'el': 'gen-button', 'op': 'mnPlan', 'force': True, 'label': 'คิดบทใหม่'}
NEW_BTN = {'el': 'gen-phase', 'ops': ['mnPlan', 'mnQueue'], 'perProduct': True,
           'label': 'คิดบทใหม่', 'icon': 'psychology', 'variant': 'solid', 'className': 'mt-1'}

def walk(n, fn, path=''):
    """เก็บรายชื่อโหนดให้ครบก่อนแก้ — เดินแก้ระหว่าง walk = RecursionError (บทเรียนเดิม)"""
    hits = []
    def rec(n, path):
        if isinstance(n, dict):
            if fn(n): hits.append((n, path))
            for k, v in n.items(): rec(v, path + '.' + str(k))
        elif isinstance(n, list):
            for i, v in enumerate(n): rec(v, path + '[%d]' % i)
    rec(n, path)
    return hits

def page(i):
    return c['phases'][0]['form'][i]

# ── A. หน้าตั้งค่า: ถอดกล่อง error + ปุ่มคิดบทใหม่ ออกจากการ์ดสินค้า ─────────────
setup = page(0)
def is_errbox(n):
    # 🔴 ต้องจับ "กล่องที่ถือข้อความนั้นเป็นลูกตรง ๆ" เท่านั้น
    #    ใช้ substring บน json.dumps ทั้งก้อน = จับ **ancestor** ไปด้วย ⇒ รอบแรกลบทั้งแถวสินค้าทิ้ง
    #    (repeat products เหลือลูกว่าง = หน้าตั้งค่าไม่มีรายการสินค้าเลย) — mutation ตอนเขียนยามเป็นคนจับได้
    return n.get('el') == 'box' and isinstance(n.get('card'), list) and any(
        isinstance(x, dict) and x.get('el') == 'text' and x.get('value') == ERR_TITLE for x in n['card'])
def is_brain(n):
    return n.get('el') == 'gen-button' and n.get('op') == 'mnPlan' and n.get('iconOnly')

removed = 0
for holder, _ in walk(setup, lambda n: isinstance(n.get('card'), list)):
    keep = [x for x in holder['card'] if not (is_errbox(x) or is_brain(x))]
    if len(keep) != len(holder['card']):
        removed += len(holder['card']) - len(keep)
        holder['card'] = keep
if removed: changed.append('A ถอดกล่อง error + ปุ่มคิดบทใหม่ ออกจากหน้าตั้งค่า (%d ชิ้น)' % removed)

# ── B. การ์ดเตือนใบเดียวเหนือปุ่ม "เริ่ม" ───────────────────────────────────────
NEW_WHEN = {'op': 'gt', 'a': {'op': 'count', 'from': 'products', 'where': 'status=error'}, 'b': 0}
NEW_TEXT = 'เขียนบทไม่สำเร็จบางสินค้า — กด "เริ่ม" อีกครั้งเพื่อลองเขียนใหม่'
for n, _ in walk(setup, lambda n: n.get('el') == 'text' and 'บทที่ได้มาไม่สมบูรณ์' in str(n.get('value', ''))):
    if n['value'] != NEW_TEXT:
        n['value'] = NEW_TEXT
        changed.append('B ข้อความการ์ดเตือนหน้าตั้งค่า → "กดเริ่มอีกครั้ง"')
# 🔴 เงื่อนไขเดิม (tasks==0 && some products มี data.plan) **ไม่มีวันติดตอนคิดบทพลาด**
#    เพราะ planQueueOne ลบ data.plan ทิ้งเมื่อบทเพี้ยน ⇒ การ์ดจะไม่โผล่เลย = ใส่ไปก็เปล่าประโยชน์
# 🪤 ห้ามหาโหนดด้วย `NEW_TEXT in json.dumps(...)` — ฟันหนูถูก escape (พลาดมาแล้วรอบนี้) ⇒ เทียบค่าตรง ๆ
for holder, _ in walk(setup, lambda n: isinstance(n.get('card'), list) and any(
        isinstance(x, dict) and x.get('el') == 'text' and x.get('value') == NEW_TEXT for x in n['card'])):
    if holder.get('when') != NEW_WHEN:
        holder['when'] = NEW_WHEN
        changed.append('B เงื่อนไขการ์ดเตือน → มีสินค้าที่คิดบทพลาด (ของเดิมไม่มีวันติด)')

# ── C+D. หน้าผลิต: การ์ดพลาดต้องครบทุกคลิป + ปุ่มเข้าคิวต่อเอง ──────────────────
IDX0 = {'op': 'eq', 'a': {'op': 'index'}, 'b': 0}
IDXN = {'op': 'lt', 'a': {'op': 'index'}, 'b': '{values.clipsPerProduct}'}
produce = page(3)
nfix = nbtn = 0
for n, _ in walk(produce, lambda n: ERR_TITLE in json.dumps(n, ensure_ascii=False) and n.get('el') == 'box'):
    w = n.get('when') or {}
    lst = w.get('list') if isinstance(w, dict) else None
    if isinstance(lst, list) and IDX0 in lst:
        n['when']['list'] = [IDXN if x == IDX0 else x for x in lst]
        nfix += 1
    for i, ch in enumerate(n.get('card', [])):
        if isinstance(ch, dict) and ch.get('el') == 'gen-button' and ch.get('op') == 'mnPlan' and ch.get('force'):
            n['card'][i] = dict(NEW_BTN); nbtn += 1
if nfix: changed.append('C การ์ด "เขียนบทไม่สำเร็จ" หน้าผลิตแสดงครบทุกคลิป (%d จุด)' % nfix)
if nbtn: changed.append('D ปุ่มคิดบทใหม่หน้าผลิต → gen-phase [mnPlan,mnQueue] perProduct (%d จุด)' % nbtn)

# ── ยามก่อนเขียน ────────────────────────────────────────────────────────────────
j = json.dumps(c, ensure_ascii=False)
s_setup = json.dumps(page(0), ensure_ascii=False)
assert ERR_TITLE not in s_setup, 'หน้าตั้งค่ายังมีกล่อง error อยู่'
assert '"op": "mnPlan"' not in s_setup, 'หน้าตั้งค่ายังมีปุ่มคิดบทใหม่อยู่'
s_prod = json.dumps(page(3), ensure_ascii=False)
assert json.dumps(IDX0, ensure_ascii=False) not in json.dumps(
    [n for n, _ in walk(page(3), lambda n: ERR_TITLE in json.dumps(n, ensure_ascii=False))], ensure_ascii=False), 'หน้าผลิตยังยุบเหลือใบเดียว'
# 🪤 ห้ามเทียบสตริงที่มีฟันหนูกับผลของ json.dumps — มันถูก escape เป็น \\" แล้ว (assert นี้เคยแดงหลอก)
texts = [n.get('value') for n, _ in walk(page(0), lambda n: n.get('el') == 'text')]
assert NEW_TEXT in texts, 'ไม่มีการ์ดบอกให้กดเริ่มอีกครั้ง'
# 🔴 ยามกันตัวเองลบเกิน: รายการสินค้าในหน้าตั้งค่าต้องยังมีเนื้อ (รอบแรกลบทั้งแถวไปโดยไม่มีใครรู้)
reps = [n for n, _ in walk(page(0), lambda n: n.get('el') == 'repeat' and n.get('coll') == 'products')]
assert reps and all(len(r.get('card') or []) > 0 for r in reps), 'แถวสินค้าในหน้าตั้งค่าถูกลบเกลี้ยง'
holders = [n for n, _ in walk(page(0), lambda n: isinstance(n.get('card'), list) and any(
    isinstance(x, dict) and x.get('el') == 'text' and x.get('value') == NEW_TEXT for x in n['card']))]
assert holders and all(h.get('when') == NEW_WHEN for h in holders), 'การ์ดเตือนยังใช้เงื่อนไขเดิมที่ไม่มีวันติด'
assert s_prod.count('"perProduct": true') >= 2, 'ปุ่มคิดบทใหม่หน้าผลิตยังไม่ต่อคิว'

if changed:
    SRC.write_text(json.dumps(c, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('— %s —' % SRC.name)
for x in changed: print('  ✔ ' + x)
if not changed: print('  (ไม่มีอะไรเปลี่ยน — แพตช์ลงไปแล้ว)')
