#!/usr/bin/env python3
# minimal-v19-orderdone.py — "งานในคิวเสร็จ" ≠ "งานที่สั่งเสร็จ" (2026-09-13 · พี่หมีเจอกับของจริง)
#
# อาการ: โหลดเซฟที่มีงานค้าง (2 ใน 4 คลิป) → ไปหน้าผลิต → ระบบกำลังเขียนบทของงานที่ค้าง
#        → กด "หยุดพัก" → การ์ดบนสุดขึ้น "ครบทุกคลิปแล้ว — ไปดูผลงานที่คลังคลิปได้เลย" + ปุ่ม "ไปคลังคลิป"
#        ทั้งที่หัวการ์ดข้าง ๆ กันเขียนว่า "2 /4 คลิป"
#
# 🔑 ราก: เงื่อนไข "เสร็จ" ของการ์ดบนสุดถามว่า
#        count(tasks slot=video) == count(tasks)   →  "ของที่อยู่ในคิว ทำครบหมดแล้ว"
#     ซึ่ง **เป็นจริง** ตอนมี task แค่ 2 ใบ ทั้งที่ผู้ใช้สั่งไว้ 4 คลิป
#     ⇒ ตระกูลเดียวกับ "ช่องมีของ ≠ งานเสร็จ" · คราวนี้คือ "คิวครบ ≠ สั่งครบ"
#     หัวการ์ด กับ gallery.when รู้เป้าหมายที่ถูกอยู่แล้ว (products(enabled) × clipsPerProduct)
#     แต่เงื่อนไขในการ์ดไม่เคยถาม ⇒ ตอบคนละคำถามกันเองมาตลอด
#     ({values.__runLoopLeft} ที่วางไว้กันเคสนี้ **ใช้ไม่ได้หลังโหลดเซฟ** เพราะเป็นค่าที่ run เป็นคนประกาศ)
#
# สิ่งที่ทำ (config ล้วน ไม่แตะ engine):
#   A. เติมเงื่อนไข "คิวครบตามที่สั่ง" (gte count(tasks) ≥ เป้าหมาย) เข้าไปในนิพจน์ "เสร็จ" 9 จุด
#      🔴 ยกเว้นปุ่ม gen-phase "Gen วิดีโอทั้งหมด · เหลือ N" — **ตั้งใจไม่แตะ**
#         มันตอบคนละคำถาม ("ของในคิวเหลือกี่ใบ") ถ้าแตะจะโผล่ปุ่ม "เหลือ 0" ให้กดฟรี
#   B. แถบความคืบหน้าใช้ตัวหารเป็น max(คิวที่มี, เป้าหมาย) — ไม่งั้น 2/2 = 100% ทั้งที่สั่ง 4
#   C. เพิ่มปุ่ม "ทำต่อ" (ออโต้ = run-button · ทีละขั้น = gen-phase [mnPlan,mnQueue] perProduct)
#      🔴 ข้อนี้จำเป็น ไม่ใช่ของแถม — ทำแค่ A แล้วสถานะนี้จะ **ไม่มีปุ่มอะไรให้กดเลย**
#         ทั้งที่ข้อความข้าง ๆ เขียนว่า "กดปุ่มด้านขวา" (= สร้างบั๊ก "บอกอย่าง เห็นอีกอย่าง" ตัวใหม่)
#
# 🛡 ทางเข้ากันเคสเก่า: clipsPerProduct ว่าง/สินค้าเปิด 0 ตัว ⇒ เป้าหมาย = 0 ⇒ gte เป็นจริงเสมอ
#    ⇒ พฤติกรรมเดิมทุกตัวอักษร (ไฟล์เซฟรุ่นเก่าไม่สะดุด)
# รันซ้ำได้ (idempotent)
import json, sys, pathlib, copy

SRC = pathlib.Path(__file__).resolve().parent.parent / (sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json')
c = json.loads(SRC.read_text(encoding='utf-8'))
log = []

# ── นิพจน์กลาง ──────────────────────────────────────────────────────────────
EXPECTED = {'op': 'mul',
            'a': {'op': 'count', 'from': 'products', 'where': 'enabled=true'},
            'b': '{values.clipsPerProduct}'}          # ★ก้อนเดียวกับที่หัวการ์ด/chrome.resume.total ใช้
ORDERED_FULLY = {'op': 'gte', 'a': {'op': 'count', 'from': 'tasks'}, 'b': copy.deepcopy(EXPECTED)}
REMAIN = {'op': 'sub', 'a': copy.deepcopy(EXPECTED), 'b': {'op': 'count', 'from': 'tasks'}}

QUEUE_DONE_LIST = [
    {'op': 'gt', 'a': {'op': 'count', 'from': 'tasks'}, 'b': 0},
    {'op': 'eq', 'a': {'op': 'count', 'from': 'tasks', 'slot': 'video'}, 'b': {'op': 'count', 'from': 'tasks'}},
    {'op': 'eq', 'a': {'op': 'count', 'from': 'tasks', 'slot': 'board'}, 'b': {'op': 'count', 'from': 'tasks'}},
]
QUEUE_DONE = {'op': 'and', 'list': QUEUE_DONE_LIST}
ALL_DONE = {'op': 'and', 'list': QUEUE_DONE_LIST + [copy.deepcopy(ORDERED_FULLY)]}

NOT_RUNNING = {'op': 'not', 'a': {'op': 'or', 'list': [
    {'op': 'eq', 'a': '{values.__runState}', 'b': 'running'},
    {'op': 'eq', 'a': '{values.__runState}', 'b': 'cooldown'},
    {'op': 'eq', 'a': '{values.__runState}', 'b': 'retrying'}]}}

SKIP_EL = {'gen-phase', 'gen-button', 'retry-button'}   # ★ตัวที่ถาม "คิวเหลือกี่ใบ" ไม่ใช่ "สั่งครบหรือยัง"

def nodes_with_when(root):
    out = []
    def rec(n):
        if isinstance(n, dict):
            if 'when' in n: out.append(n)
            for v in n.values(): rec(v)
        elif isinstance(n, list):
            for v in n: rec(v)
    rec(root)
    return out

def swap(node, old, new):
    """แทนก้อนที่ deep-equal old ด้วย new — คืนจำนวนที่แทน"""
    n = 0
    def rec(o):
        nonlocal n
        if isinstance(o, dict):
            for k, v in list(o.items()):
                if v == old: o[k] = copy.deepcopy(new); n += 1
                else: rec(v)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                if v == old: o[i] = copy.deepcopy(new); n += 1
                else: rec(v)
    rec(o=node)
    return n

def count_of(root, expr):
    n = 0
    def rec(o):
        nonlocal n
        if o == expr: n += 1; return
        if isinstance(o, dict):
            for v in o.values(): rec(v)
        elif isinstance(o, list):
            for v in o: rec(v)
    rec(root)
    return n

produce = c['phases'][0]['form'][3]

# ── A. เติม "คิวครบตามที่สั่ง" เข้าเงื่อนไขเสร็จ ───────────────────────────
before_q = count_of(produce, QUEUE_DONE)
before_a = count_of(produce, ALL_DONE)
assert before_q + before_a == 10, 'คาดว่ามีนิพจน์ "เสร็จ" 10 จุดในหน้าผลิต แต่เจอ %d (คิวเดิม %d · แก้แล้ว %d)' % (before_q + before_a, before_q, before_a)

patched = 0
skipped = []
for node in nodes_with_when(produce):
    if node.get('el') in SKIP_EL:
        if count_of(node['when'], QUEUE_DONE): skipped.append(node.get('el'))
        continue
    patched += swap(node['when'], QUEUE_DONE, ALL_DONE)
if patched: log.append('A. เติมเงื่อนไข "คิวครบตามที่สั่ง" %d จุด (ข้าม %s)' % (patched, skipped or 'ไม่มี'))

assert count_of(produce, ALL_DONE) == 9, 'ต้องได้ 9 จุด แต่ได้ %d' % count_of(produce, ALL_DONE)
assert count_of(produce, QUEUE_DONE) == 1, 'ปุ่ม Gen วิดีโอต้องเหลือนิพจน์เดิมไว้ 1 จุด แต่เหลือ %d' % count_of(produce, QUEUE_DONE)
assert skipped == ['gen-phase'] or not patched, 'จุดที่ข้ามต้องเป็น gen-phase เท่านั้น: %s' % skipped

# ── B. ตัวหารของแถบความคืบหน้า ────────────────────────────────────────────
OLD_DIV = {'op': 'div', 'a': {'op': 'count', 'from': 'tasks', 'slot': 'video'}, 'b': {'op': 'count', 'from': 'tasks'}}
NEW_DIV = {'op': 'div', 'a': {'op': 'count', 'from': 'tasks', 'slot': 'video'},
           'b': {'op': 'max', 'a': {'op': 'count', 'from': 'tasks'}, 'b': copy.deepcopy(EXPECTED)}}
bars = [n for n in nodes_with_when(produce) if n.get('el') == 'progress-bar']
nb = 0
for b in bars:
    if b.get('value') == {'op': 'mul', 'a': copy.deepcopy(OLD_DIV), 'b': 100}:
        b['value'] = {'op': 'mul', 'a': copy.deepcopy(NEW_DIV), 'b': 100}; nb += 1
if nb: log.append('B. แถบความคืบหน้าใช้ตัวหาร max(คิวที่มี, เป้าหมาย) %d จุด' % nb)
assert any(n.get('value') == {'op': 'mul', 'a': copy.deepcopy(NEW_DIV), 'b': 100} for n in bars), 'ไม่เจอแถบความคืบหน้าที่แก้แล้ว'

# ── C. ปุ่ม "ทำต่อ" ตอนคิวยังไม่ครบตามที่สั่ง ─────────────────────────────
CONT_BASE = [
    copy.deepcopy(NOT_RUNNING),
    {'op': 'not', 'a': {'op': 'gt', 'a': {'op': 'count', 'from': 'tasks', 'where': 'status=error'}, 'b': 0}},
    {'op': 'not', 'a': {'op': 'gt', 'a': '{values.__runLoopLeft}', 'b': 0}},
    {'op': 'gt', 'a': {'op': 'count', 'from': 'tasks'}, 'b': 0},
    {'op': 'not', 'a': copy.deepcopy(ORDERED_FULLY)},
]
BTN_CLS = ('justify-center !h-14 @[420px]:!h-12 !rounded-xl !text-[16px] @[420px]:!text-[15px] font-bold '
           '!bg-gradient-to-b !from-[#3f8ef0] !to-[#2571dd] transition-all hover:-translate-y-0.5 '
           'active:translate-y-0 !text-white px-4 shrink-0 whitespace-nowrap w-full')
CONT_AUTO = {'el': 'run-button', 'icon': 'bolt', 'variant': 'solid',
             'label': {'op': 'concat', 'parts': ['ทำต่อให้ครบ · เหลือ ', copy.deepcopy(REMAIN), ' คลิป']},
             'when': {'op': 'and', 'list': CONT_BASE + [{'op': 'eq', 'a': '{values.mode}', 'b': 'auto'}]},
             'className': BTN_CLS}
CONT_MANUAL = {'el': 'gen-phase', 'ops': ['mnPlan', 'mnQueue'], 'perProduct': True,
               'icon': 'edit_note', 'variant': 'solid',
               'label': {'op': 'concat', 'parts': ['เขียนบทต่อ · เหลือ ', copy.deepcopy(REMAIN), ' คลิป']},
               'when': {'op': 'and', 'list': CONT_BASE + [{'op': 'eq', 'a': '{values.mode}', 'b': 'manual'}]},
               'className': BTN_CLS}

col = produce['card'][0]['card'][5]['card'][0]['card'][5]
assert col.get('el') == 'box' and len(col['card']) >= 6, 'หาคอลัมน์ปุ่มของการ์ดสถานะไม่เจอ'
assert col['card'][2].get('el') == 'run-button', 'ลำดับปุ่มเปลี่ยนไป — ตรวจก่อนแทรก'
have = [json.dumps(x, ensure_ascii=False, sort_keys=True) for x in col['card']]
for i, btn in enumerate((CONT_AUTO, CONT_MANUAL)):
    key = json.dumps(btn, ensure_ascii=False, sort_keys=True)
    if key not in have:
        col['card'].insert(3 + i, copy.deepcopy(btn))
        log.append('C. เพิ่มปุ่ม "%s"' % ('ทำต่อให้ครบ (ออโต้)' if i == 0 else 'เขียนบทต่อ (ทีละขั้น)'))

# ── ยามของสคริปต์เอง ──────────────────────────────────────────────────────
assert c['values'].get('clipsPerProduct') not in (None, ''), 'clipsPerProduct ปริยายห้ามว่าง (whenMet อ่าน "" เป็น 0 ⇒ เป้าหมาย 0 ⇒ ยามนี้ตายเงียบ)'
# หน้า derived ต้องไม่ถูกแตะ (มันมีเงื่อนไขเป้าหมายอยู่ก่อนแล้วคนละทรง)
for fi in (3, 4):
    w = json.dumps(c['phases'][0]['form'][fi]['when'], ensure_ascii=False)
    assert '"gte"' in w and 'clipsPerProduct' in w, 'form[%d].when ต้องยังมีเงื่อนไขเป้าหมาย' % fi
# แถวสินค้า/การ์ดคลิปใน repeat ต้องไม่โดนลูกหลง
assert count_of(c['phases'][0]['form'][0], ALL_DONE) == 0, 'หน้าตั้งค่าไม่ควรถูกแตะ'

SRC.write_text(json.dumps(c, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('✅ %s' % SRC.name)
for l in log: print('  ·', l)
if not log: print('  · ไม่มีอะไรเปลี่ยน (รันซ้ำ)')
