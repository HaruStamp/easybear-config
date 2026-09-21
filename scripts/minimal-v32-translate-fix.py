#!/usr/bin/env python3
# minimal-v32-translate-fix.py — 4 ข้อที่พี่หมีแจ้งหลังลองของจริงบนมือถือ (2026-09-21)
#   ① ป้าย "บทวิดีโอ" ตัวบาง/ตกบรรทัด/ไม่อยู่ระดับเดียวกับไอคอน → ใช้ className ชุดเดียวกับป้าย "บทภาพ"
#      (v29 เปลี่ยนแต่ข้อความ+ไอคอน ลืมเปลี่ยน className ⇒ ยังเป็นสไตล์ของป้ายเก่า "บทอังกฤษ — …" ที่ตั้งใจให้จาง)
#   ② ป้าย "บทภาพ (คำสั่งวาด)" → "บทภาพ" (พี่หมีสั่งตัดวงเล็บออก · บนมือถือมันตกเป็น 2 บรรทัดด้วย)
#   ③ ไอคอนปุ่มแปล translate → sync_alt (สื่อ "แปลง" ไม่ใช่ "ภาษา")
#   ④ 🔴🔴 **บั๊กจริง: กดซ้ำแล้วบทวิดีโอไม่เปลี่ยน** — ปุ่มหายไปแวบหนึ่งเหมือนทำงาน แต่ไม่มีอะไรเกิดขึ้น
#      ราก (ยืนยันในโค้ด golden v1.7.0 ทั้ง 2 ชั้น):
#        · atoms-cases-a2.tsx  `gen-phase` → on.genPhase(el)            ⇒ **ไม่ส่ง force**
#          (ตรงข้ามกับ `retry-button` + chain → on.chainItem(el, item, **true**) ⇒ force)
#        · engine-run.ts:122   todo = targets.filter(it => opts.force || it.status === 'stale' ||
#                                 op.type === 'llm'       ? !(it.data && op.out in it.data)
#                               : op.type === 'transform' ? !(__tdone.includes(op.id)) : …)
#      ⇒ กดครั้งที่ 2: mnTrans มี data.trans แล้ว = ถูกข้าม · mnTrA{N} มี __tdone แล้ว = ถูกข้าม
#        ⇒ **ทั้งสายไม่ยิงอะไรเลย** แต่ปุ่มยัง disable ชั่วครู่ (busy flag) = อาการที่พี่หมีเห็นเป๊ะ
#      แก้: ปุ่มเปลี่ยนเป็น `retry-button` + `chain` ⇒ force ⇒ mnTrans แปลใหม่จากบทไทยล่าสุดทุกครั้ง
#      🪤 นี่คือกฎเดิมของแอปนี้ที่เคยจดไว้แล้ว: "gen-button ไม่ force · retry-button force" (v8 · ปุ่มรายคลิป 17 ปุ่ม)
#         ผมเผลอใช้ gen-phase เพราะมันรับ `ops` หลายตัวได้ — แต่ปุ่มนี้ความหมายคือ "ทำใหม่" ไม่ใช่ "ทำของที่ยังไม่มี"
#   ⑤ ปุ่มต้องไม่หายตอนทำงาน (พี่หมีสั่ง) → ถอด `when` ที่ซ่อนปุ่มตอน running ออก
#      `retry-button` มี `disabled={itemBusy(on, item)}` ในตัวอยู่แล้ว ⇒ ปุ่มอยู่ที่เดิมแต่กดไม่ได้
#      ⚠️ ไอคอนหมุนยังไม่ได้ในรอบนี้ — engine ให้ `loading:true` เฉพาะ `gen-button` (atoms-cases-a2.tsx)
#         `retry-button` ไม่มีบรรทัดนั้น และ Btn อ่าน `el.loading === true` แบบ strict (config ตั้งเองไม่ได้)
#         ⇒ ต้องให้ starter เติม 1 บรรทัด — แจ้งไปแล้ว · ไม่ใช่ของที่ config ทำได้เอง
# รันซ้ำได้: ตรวจ marker mn-tr-force
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'mn-tr-force'
OLD_MARK = 'mn-tr-inline'
OLD_BOARD_LABEL = 'บทภาพ (คำสั่งวาด)'
NEW_BOARD_LABEL = 'บทภาพ'
VID_LABEL = 'บทวิดีโอ'
NEW_ICON = 'sync_alt'
N_SCENES = 15


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)
    if MARK in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return
    assert OLD_MARK in before, 'ต้องรัน v31 ก่อน'

    # ── ① + ② ป้าย: เก็บ className ของป้ายบทภาพไว้ใช้กับป้ายบทวิดีโอ ──
    board_cls = []
    def grab(n):
        if n.get('el') == 'text' and n.get('value') == OLD_BOARD_LABEL:
            board_cls.append(n.get('className'))
    walk(cfg, grab)
    assert len(board_cls) == N_SCENES, 'ป้าย "บทภาพ" ต้องมี 15 จุด เจอ %d' % len(board_cls)
    assert len(set(board_cls)) == 1, 'ป้าย "บทภาพ" className ไม่เหมือนกันทุกจุด — ยกเลิก'
    CLS = board_cls[0]
    assert 'items-center' in CLS and 'font-bold' in CLS, 'className ของป้ายบทภาพไม่ใช่ชุดที่คาด'

    fixed_board, fixed_vid, fixed_btn = [], [], []

    def fix(n):
        if n.get('el') == 'text' and n.get('value') == OLD_BOARD_LABEL:
            n['value'] = NEW_BOARD_LABEL          # ② ตัด "(คำสั่งวาด)" ออก
            fixed_board.append(1)
        elif n.get('el') == 'text' and n.get('value') == VID_LABEL:
            n['className'] = CLS                  # ① ใช้สไตล์เดียวกับป้ายบทภาพ (หนา · ไอคอนอยู่ระดับเดียวกับข้อความ)
            fixed_vid.append(1)
        elif OLD_MARK in str(n.get('className', '')):
            # ③ ④ ⑤ ปุ่มแปล
            ops = n.get('ops') or []
            assert len(ops) == 2 and ops[0] == 'mnTrans' and re.match(r'mnTrA\d+$', ops[1]), 'ปุ่มแปลโครงไม่ตรงที่คาด: %s' % ops
            n.pop('ops', None)
            n.pop('when', None)                   # ⑤ ปุ่มไม่หายตอนทำงาน (retry-button disable ให้เองราย item)
            n['el'] = 'retry-button'              # ④ force — ไม่งั้นกดซ้ำแล้วทั้งสายถูกข้าม
            n['op'] = ops[1]                      # retry-button ต้องมี op (สาขาที่ไม่มี chain) — chain ชนะเมื่อมี
            n['chain'] = ['mnTrans', ops[1]]
            n['icon'] = NEW_ICON                  # ③
            n['className'] = str(n['className']).replace(OLD_MARK, MARK)
            fixed_btn.append(int(ops[1][5:]))

    walk(cfg, fix)
    assert len(fixed_board) == N_SCENES, 'ป้ายบทภาพต้องแก้ 15 จุด (ได้ %d)' % len(fixed_board)
    assert len(fixed_vid) == N_SCENES, 'ป้ายบทวิดีโอต้องแก้ 15 จุด (ได้ %d)' % len(fixed_vid)
    assert sorted(fixed_btn) == list(range(1, N_SCENES + 1)), 'ปุ่มต้องแก้ครบ 15 (ได้ %s)' % sorted(fixed_btn)

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    assert OLD_MARK not in after, 'marker เก่ายังค้าง'
    assert OLD_BOARD_LABEL not in after, 'ป้าย "บทภาพ (คำสั่งวาด)" ยังเหลืออยู่'

    # ── ยามหลังแก้ (นับจาก node ห้ามนับ substring — บทเรียนจาก hardsell 2026-09-21) ──
    labels_board, labels_vid, btns = [], [], []
    def chk(n):
        if n.get('el') == 'text' and n.get('value') == NEW_BOARD_LABEL: labels_board.append(n.get('className'))
        if n.get('el') == 'text' and n.get('value') == VID_LABEL: labels_vid.append(n.get('className'))
        if MARK in str(n.get('className', '')): btns.append(n)
    walk(cfg, chk)
    assert len(labels_board) == N_SCENES and len(labels_vid) == N_SCENES, 'จำนวนป้ายเพี้ยน'
    assert set(labels_board) == set(labels_vid) == {CLS}, 'ป้าย 2 ชนิดต้องใช้ className ชุดเดียวกัน'
    assert len(btns) == N_SCENES
    for b in btns:
        assert b['el'] == 'retry-button', 'ปุ่มต้องเป็น retry-button (ตัวที่ส่ง force)'
        assert b['chain'][0] == 'mnTrans' and b['chain'][1] == b['op'], 'chain ต้องเป็น [mnTrans, mnTrA{N}] และ op = ตัวท้าย'
        assert 'ops' not in b and 'when' not in b, 'ต้องไม่เหลือ ops/when ของ gen-phase'
        assert b['icon'] == NEW_ICON and b['label'] == 'แปลงเป็นบทวิดีโอ'
    assert sorted(int(b['op'][5:]) for b in btns) == list(range(1, N_SCENES + 1)), 'ปุ่มต้องคู่กับ op ของฉากตัวเอง'
    # op แปลยังต้องไม่หลุดเข้ารอบผลิตอัตโนมัติ
    assert 'mnTrA1' not in json.dumps(cfg.get('auto'), ensure_ascii=False)
    assert 'mnTrA1' not in json.dumps(cfg.get('stages'), ensure_ascii=False)
    # ยาม where กันเขียนทับด้วยค่าว่าง ต้องอยู่ครบทุกตัว (v30)
    for i in range(1, N_SCENES + 1):
        o = [o for o in cfg['ops'] if o['id'] == 'mnTrA%d' % i][0]
        assert o['setFields']['where'] == 'data.trans.s%den!=' % i, 'ยาม where ของ mnTrA%d หาย' % i

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v32 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① ป้าย "บทวิดีโอ" ใช้สไตล์เดียวกับ "บทภาพ" (หนา · ไอคอนกับข้อความอยู่ระดับเดียวกัน · ไม่ตกบรรทัด)')
    print('   ② "บทภาพ (คำสั่งวาด)" → "บทภาพ"')
    print('   ③ ไอคอนปุ่ม translate → %s' % NEW_ICON)
    print('   ④ gen-phase → retry-button + chain ⇒ **ส่ง force** ⇒ กดซ้ำแล้วแปลใหม่จริง (บั๊กที่พี่หมีเจอ)')
    print('   ⑤ ถอด when ที่ซ่อนปุ่มตอนทำงาน — ปุ่มอยู่ที่เดิม กดไม่ได้ระหว่างรัน')
    print('   ⏳ ไอคอนหมุนต้องรอ engine (retry-button ไม่มี loading:true — แจ้ง starter แล้ว)')


main()
