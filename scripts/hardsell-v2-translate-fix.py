#!/usr/bin/env python3
# hardsell-v2-translate-fix.py — แก้ปุ่มแปล 4 ข้อ ตามที่ minimal เจอกับพี่หมี (2026-09-21 · ของเขา = minimal v32 `99161ea`)
#   ① ป้าย "บทวิดีโอ" ใช้ className ชุดเดียวกับป้าย "บทภาพ" (v1 เปลี่ยนแต่ข้อความ+ไอคอน ⇒ ยังเป็นสไตล์ป้ายเก่าที่ตั้งใจให้จาง)
#   ② "บทภาพ (คำสั่งวาด)" → "บทภาพ" (พี่หมีสั่งตัดวงเล็บ · บนมือถือตกเป็น 2 บรรทัด)
#   ③ ไอคอนปุ่ม translate → sync_alt (สื่อ "แปลง" ไม่ใช่ "ภาษา")
#   ④ 🔴🔴 บั๊กจริง: กดซ้ำแล้วบทวิดีโอไม่เปลี่ยน — ปุ่มหายแวบหนึ่งเหมือนทำงาน แต่ไม่มีอะไรเกิดขึ้น
#      ราก (ยืนยันในโค้ด golden ทั้ง 2 ชั้น · minimal ไล่ให้แล้ว):
#        · atoms-cases-a2.tsx  `gen-phase` → on.genPhase(el)          ⇒ **ไม่ส่ง force**
#                              `retry-button` + chain → on.chainItem(el, item, **true**) ⇒ force
#        · engine-run.ts:122   todo = targets.filter(it => opts.force || status==='stale' ||
#                                llm ? !(data && out in data) : transform ? !__tdone.includes(id) : …)
#      ⇒ กดครั้งที่ 2: mnTrans มี data.trans แล้ว = ข้าม · mnTrA{N} มี __tdone แล้ว = ข้าม ⇒ ทั้งสายไม่ยิงอะไรเลย
#      แก้: `gen-phase` → `retry-button` + `chain:['mnTrans','mnTrA{N}']` + `op:'mnTrA{N}'`
#      🪤 ปุ่มนี้ความหมายคือ "ทำใหม่" ไม่ใช่ "ทำของที่ยังไม่มี" ⇒ ต้องเป็น retry-button ตั้งแต่แรก
#   ⑤ ปุ่มไม่หายตอนทำงาน → ถอด `when` ออก (retry-button มี disabled={itemBusy} ในตัวแล้ว)
# ⏳ ที่ยังทำไม่ได้ด้วย config: ไอคอนหมุนตอนทำงาน — engine ให้ `loading:true` เฉพาะ `gen-button` (minimal ขอ starter ไปแล้ว)
# รันซ้ำได้: ตรวจ marker hs-tr-force
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'hs-tr-force'
OLD_MARK = 'hs-tr-inline'
OLD_BOARD_LABEL = 'บทภาพ (คำสั่งวาด)'
NEW_BOARD_LABEL = 'บทภาพ'
VID_LABEL = 'บทวิดีโอ'
NEW_ICON = 'sync_alt'
N_SCENES = 8


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)
    if MARK in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return
    assert OLD_MARK in before, 'ต้องรัน hardsell-v1 ก่อน (ยังไม่มีปุ่มแปล)'

    # ── ① เก็บ className ของป้าย "บทภาพ" ไว้ใช้กับป้าย "บทวิดีโอ" ──
    board_cls = []
    walk(cfg, lambda n: board_cls.append(n.get('className'))
         if n.get('el') == 'text' and n.get('value') == OLD_BOARD_LABEL else None)
    assert len(board_cls) == N_SCENES, 'ป้าย "บทภาพ" ต้องมี %d จุด เจอ %d' % (N_SCENES, len(board_cls))
    assert len(set(board_cls)) == 1, 'ป้าย "บทภาพ" className ไม่เหมือนกันทุกจุด — ยกเลิก'
    CLS = board_cls[0]
    assert 'font-bold' in CLS, 'className ของป้ายบทภาพไม่ใช่ชุดที่คาด: %s' % CLS

    fixed_board, fixed_vid, fixed_btn = [], [], []

    def fix(n):
        if n.get('el') == 'text' and n.get('value') == OLD_BOARD_LABEL:
            n['value'] = NEW_BOARD_LABEL                 # ②
            fixed_board.append(1)
        elif n.get('el') == 'text' and n.get('value') == VID_LABEL:
            n['className'] = CLS                         # ① สไตล์เดียวกับป้ายบทภาพ
            fixed_vid.append(1)
        elif OLD_MARK in str(n.get('className', '')):
            ops = n.get('ops') or []
            assert len(ops) == 2 and ops[0] == 'mnTrans' and re.match(r'mnTrA\d+$', ops[1]), \
                'ปุ่มแปลโครงไม่ตรงที่คาด: %s' % ops
            n.pop('ops', None)
            n.pop('when', None)                          # ⑤ ปุ่มไม่หายตอนทำงาน
            n['el'] = 'retry-button'                     # ④ force
            n['op'] = ops[1]                             # retry-button ต้องมี op (สาขาที่ไม่มี chain) — chain ชนะเมื่อมี
            n['chain'] = ['mnTrans', ops[1]]
            n['icon'] = NEW_ICON                         # ③
            n['className'] = str(n['className']).replace(OLD_MARK, MARK)
            fixed_btn.append(int(ops[1][5:]))

    walk(cfg, fix)
    assert len(fixed_board) == N_SCENES, 'ป้ายบทภาพต้องแก้ %d จุด (ได้ %d)' % (N_SCENES, len(fixed_board))
    assert len(fixed_vid) == N_SCENES, 'ป้ายบทวิดีโอต้องแก้ %d จุด (ได้ %d)' % (N_SCENES, len(fixed_vid))
    assert sorted(fixed_btn) == list(range(1, N_SCENES + 1)), 'ปุ่มต้องแก้ครบ %d (ได้ %s)' % (N_SCENES, sorted(fixed_btn))

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    assert OLD_MARK not in after, 'ยังมีปุ่มรุ่นเก่าค้าง'
    assert OLD_BOARD_LABEL not in after, 'ยังมีป้าย "บทภาพ (คำสั่งวาด)" ค้าง'
    # 🪤 นับจาก node ไม่ใช่ substring (กฎที่แลกกับ minimal 2026-09-21 — "บทวิดีโอ" อยู่ในป้ายปุ่ม/log ด้วย)
    n_btn = n_vid = 0
    def chk(n):
        nonlocal n_btn, n_vid
        if MARK in str(n.get('className', '')):
            assert n.get('el') == 'retry-button' and n.get('chain') and n.get('op'), 'ปุ่มไม่ครบรูป: %s' % n.get('el')
            assert 'when' not in n, 'ปุ่มยังมี when'
            n_btn += 1
        if n.get('el') == 'text' and n.get('value') == VID_LABEL and n.get('className') == CLS:
            n_vid += 1
    walk(cfg, chk)
    assert n_btn == N_SCENES and n_vid == N_SCENES, 'ยามนับไม่ครบ (ปุ่ม %d · ป้าย %d)' % (n_btn, n_vid)
    # op ต้องยังอยู่ครบและยังไม่เข้า auto/stages
    got = [o['id'] for o in cfg['ops']]
    auto_s = json.dumps(cfg.get('auto'), ensure_ascii=False)
    stages_s = json.dumps(cfg.get('stages'), ensure_ascii=False)
    for nm in ['mnTrans'] + ['mnTrA%d' % i for i in range(1, N_SCENES + 1)]:
        assert nm in got, 'op %s หาย' % nm
        assert nm not in auto_s and nm not in stages_s, 'op แปล (%s) ต้องไม่เข้า auto/stages' % nm
    for o in cfg['ops']:
        if o['id'].startswith('mnTrA'):
            i = int(o['id'][5:])
            assert o['setFields'].get('where') == 'data.trans.s%den!=' % i, 'ยาม where ของ %s หาย' % o['id']

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v2 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① ป้าย "บทวิดีโอ" %d จุด ใช้สไตล์เดียวกับป้ายบทภาพ · ② "บทภาพ (คำสั่งวาด)" → "บทภาพ"' % N_SCENES)
    print('   ③ ไอคอนปุ่ม → %s · ④ gen-phase → retry-button + chain (force) · ⑤ ถอด when (ปุ่มไม่หายตอนทำงาน)' % NEW_ICON)


main()
