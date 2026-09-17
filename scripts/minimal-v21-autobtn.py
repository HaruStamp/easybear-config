#!/usr/bin/env python3
# minimal-v21-autobtn.py — โหมดออโต้ต้องมีปุ่มเดียว + เลขบนปุ่มต้องตรงกับหัวการ์ด (2026-09-13 · พี่หมีเจอกับของจริง)
#
# อาการ (ภาพหน้าจอ · ออโต้ · 20 วิ · โหลดเซฟที่มีงานค้างรอวาดภาพ):
#   หัวการ์ด  "0 /2 คลิป"
#   ปุ่ม      [ทำต่อให้ครบ · เหลือ 1 คลิป]  +  [Gen ภาพทั้งหมด · เหลือ 1 คลิป]   ← 2 ปุ่มในโหมดออโต้ + เลขผิดทั้งคู่
#
# 🔑 ราก 2 ข้อ คนละเรื่องกัน:
#   A. เลขบนปุ่ม "ทำต่อ" = เป้าหมาย − จำนวน task ที่มีใน store  ⇒ ตอบว่า "ยังไม่ได้สั่งอีกกี่คลิป"
#      แต่หัวการ์ดตอบว่า "ทำเสร็จกี่คลิปจากที่สั่ง" (นับจาก slot video) ⇒ 2 ตัวในกล่องเดียวกันตอบคนละคำถาม**อีกครั้ง**
#      ⇒ เปลี่ยนเป็น  max(คิวที่มี, เป้าหมาย) − คลิปที่มีวิดีโอแล้ว  = ตัวเดียวกับที่หัวการ์ด/แถบใช้
#   B. ปุ่ม "Gen ภาพทั้งหมด/Gen วิดีโอทั้งหมด" ไม่เคยมีประตูโหมด ⇒ โผล่ในโหมดออโต้ด้วยมาตลอด
#      (เดิมไม่มีใครเห็นเพราะออโต้ไม่มีปุ่มอื่นมาอยู่ข้าง ๆ · พอ v19 เพิ่มปุ่ม "ทำต่อ" เข้าไปเลยเห็นเป็นคู่)
#      ⇒ ใส่ประตู mode == manual · **และต้องแก้คู่กับ C ไม่งั้นออโต้จะไม่มีปุ่มเลยในบางสถานะ**
#   C. ปุ่มออโต้ต้องโผล่ทุกสถานะที่ "ยังไม่จบ" ไม่ใช่เฉพาะตอน "คิวยังไม่ครบ"
#      🔴 ไม่มีข้อนี้ = สถานะ "คิวครบแล้วแต่ภาพ/วิดีโอยังไม่ครบ" จะไม่มีปุ่มอะไรให้กดเลยในโหมดออโต้ (ผู้ใช้ตัน)
# รันซ้ำได้ (idempotent)
import json, sys, pathlib, copy

SRC = pathlib.Path(__file__).resolve().parent.parent / (sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json')
c = json.loads(SRC.read_text(encoding='utf-8'))
log = []

EXPECTED = {'op': 'mul', 'a': {'op': 'count', 'from': 'products', 'where': 'enabled=true'}, 'b': '{values.clipsPerProduct}'}
TOTAL = {'op': 'max', 'a': {'op': 'count', 'from': 'tasks'}, 'b': copy.deepcopy(EXPECTED)}          # ★ก้อนเดียวกับตัวหารของแถบความคืบหน้า
REMAIN_OLD = {'op': 'sub', 'a': copy.deepcopy(EXPECTED), 'b': {'op': 'count', 'from': 'tasks'}}
REMAIN_NEW = {'op': 'sub', 'a': copy.deepcopy(TOTAL), 'b': {'op': 'count', 'from': 'tasks', 'slot': 'video'}}
ORDERED_FULLY = {'op': 'gte', 'a': {'op': 'count', 'from': 'tasks'}, 'b': copy.deepcopy(EXPECTED)}
QL = [{'op': 'gt', 'a': {'op': 'count', 'from': 'tasks'}, 'b': 0},
      {'op': 'eq', 'a': {'op': 'count', 'from': 'tasks', 'slot': 'video'}, 'b': {'op': 'count', 'from': 'tasks'}},
      {'op': 'eq', 'a': {'op': 'count', 'from': 'tasks', 'slot': 'board'}, 'b': {'op': 'count', 'from': 'tasks'}}]
ALL_DONE = {'op': 'and', 'list': QL + [copy.deepcopy(ORDERED_FULLY)]}
IS_MANUAL = {'op': 'eq', 'a': '{values.mode}', 'b': 'manual'}

BTN = {'button', 'gen-button', 'gen-phase', 'run-button', 'retry-button', 'next-button', 'confirm-button'}
def walk(n, hits):
    if isinstance(n, dict):
        if n.get('el') in BTN: hits.append(n)
        for v in n.values(): walk(v, hits)
    elif isinstance(n, list):
        for v in n: walk(v, hits)

produce = c['phases'][0]['form'][3]
btns = []; walk(produce, btns)
def lab(b): return json.dumps(b.get('label'), ensure_ascii=False)

# ── A. เลขบนปุ่มทำต่อ = คลิปที่ยังไม่เสร็จ (ตรงกับหัวการ์ด) ───────────────
na = 0
for b in btns:
    if 'ทำต่อให้ครบ' in lab(b) or 'เขียนบทต่อ' in lab(b):
        parts = b.get('label', {}).get('parts') or []
        for i, p in enumerate(parts):
            if p == REMAIN_OLD: parts[i] = copy.deepcopy(REMAIN_NEW); na += 1
if na: log.append('A. เลขบนปุ่มทำต่อ → "คลิปที่ยังไม่เสร็จ" %d ปุ่ม' % na)

# ── B. Gen ภาพ/วิดีโอ ทั้งหมด = ของโหมดทีละขั้นเท่านั้น ─────────────────
nb = 0
for b in btns:
    if b.get('el') != 'gen-phase': continue
    if 'ทั้งหมด' not in lab(b) or 'ลองใหม่' in lab(b): continue
    w = b.get('when')
    if not (isinstance(w, dict) and w.get('op') == 'and' and isinstance(w.get('list'), list)): continue
    if IS_MANUAL in w['list']: continue
    w['list'].append(copy.deepcopy(IS_MANUAL)); nb += 1
if nb: log.append('B. ใส่ประตู "โหมดทีละขั้น" ให้ปุ่ม Gen …ทั้งหมด %d ปุ่ม' % nb)

# ── C. ปุ่มออโต้ครอบทุกสถานะที่ยังไม่จบ ───────────────────────────────
nc = 0
for b in btns:
    if 'ทำต่อให้ครบ' not in lab(b): continue
    lst = b['when']['list']
    for i, x in enumerate(lst):
        if x == {'op': 'not', 'a': copy.deepcopy(ORDERED_FULLY)}:
            lst[i] = {'op': 'not', 'a': copy.deepcopy(ALL_DONE)}; nc += 1
if nc: log.append('C. ปุ่มออโต้โผล่ทุกสถานะที่ยังไม่จบ (ไม่ใช่เฉพาะตอนคิวไม่ครบ)')

# ── ยามของสคริปต์เอง ────────────────────────────────────────────────
auto = [b for b in btns if 'ทำต่อให้ครบ' in lab(b)]
man = [b for b in btns if 'เขียนบทต่อ' in lab(b)]
assert len(auto) == 1 and len(man) == 1, 'ปุ่มทำต่อต้องมีโหมดละ 1 ปุ่ม (ออโต้ %d · ทีละขั้น %d)' % (len(auto), len(man))
assert auto[0]['el'] == 'run-button' and man[0]['el'] == 'gen-phase', 'ชนิดปุ่มเปลี่ยนไป'
gens = [b for b in btns if b.get('el') == 'gen-phase' and 'ทั้งหมด' in lab(b) and 'ลองใหม่' not in lab(b)]
assert len(gens) == 2, 'คาดว่ามีปุ่ม Gen …ทั้งหมด 2 ปุ่ม แต่เจอ %d' % len(gens)
for g in gens: assert IS_MANUAL in g['when']['list'], 'ปุ่ม %s ยังไม่มีประตูโหมด' % lab(g)
# 🔴 ปุ่ม "ลองใหม่ที่พลาด" ต้องไม่ถูกใส่ประตูโหมด (ออโต้พังแล้วต้องกู้ได้)
retry = [b for b in btns if 'ลองใหม่ที่พลาด' in lab(b)]
def has_mode_gate(w):
    """🧲 ★เทียบบนโครงสร้าง ห้ามเทียบบนสตริงที่ dump แล้ว (ฟันหนูโดน escape = ไม่มีวันแมตช์)"""
    if isinstance(w, dict):
        if w == IS_MANUAL: return True
        return any(has_mode_gate(v) for v in w.values())
    if isinstance(w, list): return any(has_mode_gate(v) for v in w)
    return False
assert retry and not any(has_mode_gate(b.get('when')) for b in retry), 'ปุ่มลองใหม่ห้ามผูกโหมด'
assert json.dumps(c, ensure_ascii=False).count('"ทำต่อให้ครบ · เหลือ "') == 1

SRC.write_text(json.dumps(c, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('✅ %s' % SRC.name)
for l in log: print('  ·', l)
if not log: print('  · ไม่มีอะไรเปลี่ยน (รันซ้ำ)')
