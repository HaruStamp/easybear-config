#!/usr/bin/env python3
# minimal-v22-stopstay.py — กดหยุดตอนเขียนบทแล้วต้องอยู่หน้าผลิต ไม่เด้งไปหน้าตั้งค่า (2026-09-14 · พี่หมีเจอ)
#
# อาการ: กดเริ่ม → กดหยุดจังหวะเขียนบท → การ์ด "กำลังหยุด" สีเหลืองแวบนึง → **เด้งไปหน้าตั้งค่า**
#
# 🔑 ราก (วัดด้วย runProductLoop + markRunEnd ของจริง):
#   หลังหยุดตอน mnPlan ยังไม่ได้ task สักใบ  ⇒  tasks = 0
#   หน้าตั้งค่า when = __page=='' ∧ tasks==0 ∧ ไม่ได้กำลังรัน   ⇒ **เข้าเงื่อนไขพอดี** = ยึดหน้าไป
#   🪤 `__runState` หลัง markRunEnd กลายเป็น **'idle'** (ไม่ใช่ 'paused') ⇒ เช็ค runState ไม่ช่วยเลย
#   ✅ ค่าที่บอกความจริงคือ `__runLoopLeft` = "2" (ลูปหยุดทั้งที่ยังเหลือสินค้าให้ทำ)
#
# แก้ (config ล้วน):
#   A. หน้าผลิต — เพิ่มสาขา "ยังมีงานค้างในลูป" (`__page=='' ∧ __runLoopLeft > 0`)
#   B. หน้าตั้งค่า — สาขา derived ต้องไม่ยึดหน้าเมื่อลูปยังค้าง
#   ★ A ต้องมาก่อน B เสมอในแง่ความหมาย: สถานะนี้ถูกย้ายเจ้าของ ไม่ใช่ถูกปล่อยว่าง (กันจอขาว)
# รันซ้ำได้ (idempotent)
import json, sys, pathlib, copy

SRC = pathlib.Path(__file__).resolve().parent.parent / (sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json')
c = json.loads(SRC.read_text(encoding='utf-8'))
log = []

LOOP_LEFT = {'op': 'gt', 'a': '{values.__runLoopLeft}', 'b': 0}
AT_ROOT = {'op': 'eq', 'a': '{values.__page}', 'b': ''}
PRODUCE_BRANCH = {'op': 'and', 'list': [copy.deepcopy(AT_ROOT), copy.deepcopy(LOOP_LEFT)]}
NOT_LOOP_LEFT = {'op': 'not', 'a': copy.deepcopy(LOOP_LEFT)}

forms = c['phases'][0]['form']

# ── A. หน้าผลิตรับสถานะ "ลูปหยุดทั้งที่ยังเหลืองาน" ──────────────────
w3 = forms[3]['when']
assert w3.get('op') == 'or' and isinstance(w3.get('list'), list), 'โครง when ของหน้าผลิตเปลี่ยนไป'
if PRODUCE_BRANCH not in w3['list']:
    w3['list'].append(copy.deepcopy(PRODUCE_BRANCH))
    log.append('A. หน้าผลิตรับสถานะ "หยุดแล้วยังเหลืองาน" (__runLoopLeft > 0)')

# ── B. หน้าตั้งค่าเลิกยึดหน้าตอนลูปยังค้าง ────────────────────────────
w0 = forms[0]['when']
assert w0.get('op') == 'or' and isinstance(w0.get('list'), list), 'โครง when ของหน้าตั้งค่าเปลี่ยนไป'
derived = [b for b in w0['list'] if isinstance(b, dict) and b.get('op') == 'and'
           and any(x == AT_ROOT for x in (b.get('list') or []))]
assert len(derived) == 1, 'หาสาขา derived ของหน้าตั้งค่าไม่เจอ (เจอ %d)' % len(derived)
if NOT_LOOP_LEFT not in derived[0]['list']:
    derived[0]['list'].append(copy.deepcopy(NOT_LOOP_LEFT))
    log.append('B. หน้าตั้งค่าไม่ยึดหน้าเมื่อลูปยังเหลืองาน')

# ── ยามของสคริปต์เอง ─────────────────────────────────────────────────
assert PRODUCE_BRANCH in forms[3]['when']['list'], 'สาขาใหม่ของหน้าผลิตหาย'
assert NOT_LOOP_LEFT in derived[0]['list'], 'ประตูใหม่ของหน้าตั้งค่าหาย'
# 🔴 ห้ามแตะหน้าอื่น
for i in (1, 2, 4):
    assert 'runLoopLeft' not in json.dumps(forms[i].get('when'), ensure_ascii=False), 'หน้า %d ไม่ควรถูกแตะ' % i
# 🔴 หน้าคลังคลิปต้องไม่โดนแย่ง: ถ้าลูปเหลือ 0 พฤติกรรมเดิมทุกอย่าง
assert json.dumps(forms[4]['when'], ensure_ascii=False).count('__runLoopLeft') == 0

SRC.write_text(json.dumps(c, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('✅ %s' % SRC.name)
for l in log: print('  ·', l)
if not log: print('  · ไม่มีอะไรเปลี่ยน (รันซ้ำ)')
