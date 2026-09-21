#!/usr/bin/env python3
# minimal-v34-aux-loadinglabel.py — ใช้ของใหม่จาก golden v1.9.0 (2026-09-21)
#   ① `"aux": true` บน mnTrans + mnTrA1..15
#      แก้บั๊กที่ v29 ของเราทำไว้: `itemRunCounts` (engine-flow.ts:244) นับ **ทุก op ที่ over ตรง collection**
#      ไม่ได้ดูว่าอยู่ใน stages ไหม ⇒ op แปล (เครื่องมือที่ผู้ใช้กดเอง) ถูกนับเป็นงานของทุกคลิป ⇒ คลิปไม่มีวัน done
#      ⇒ เลข "เสร็จ/ค้าง" ในโมดัล "มีงานผลิตค้างอยู่" ผิดตลอดกาล (ผู้เรียกที่เดียว = app-render.tsx:117)
#      วัดพร้อมกลุ่มควบคุมแล้ว: ยาม blank-page ตก 6 · ถอด op แปลออก = 121/121
#   ② `loadingLabel` บนปุ่มแปล — engine ให้ retry-button ขึ้นสปินเนอร์แล้ว (v1.9.0) แต่ข้อความปริยายคือ "กำลังสร้าง..."
#      ซึ่งไม่ตรงบริบท ⇒ ตั้งเป็น "กำลังแปล..." (พี่หมีสั่งเรื่องสปินเนอร์ไว้ตอน v32: "กดแล้วปุ่มไม่หาย แต่ disable + ไอคอนหมุน")
# 🪤 engine ที่ต่ำกว่า v1.9.0 อ่าน 2 คีย์นี้ไม่ออก — ไม่พัง แต่ไม่มีผล ⇒ config นี้ต้องคู่กับ Dev v3.2.0 ขึ้นไป
# 🪤 ห้ามใส่ aux ให้ op ผลิต (mnPlan/mnQueue/mnBoard*/mnVideo*) เด็ดขาด — พวกนั้น *คือ* งานที่ต้องนับ
# รันซ้ำได้: ตรวจ marker
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUX_OPS = re.compile(r'^(mnTrans|mnTrA\d+)$')
PROD_OPS = ('mnPlan', 'mnQueue', 'mnBoard', 'mnBoard2', 'mnBoard3', 'mnVideo', 'mnVideo2', 'mnVideo3')
BTN_MARK = 'mn-tr-force'
LOADING_LABEL = 'กำลังแปล...'


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
    if '"aux"' in before or LOADING_LABEL in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    # ① aux
    marked = []
    for op in cfg['ops']:
        if AUX_OPS.match(op['id']):
            op['aux'] = True
            marked.append(op['id'])
    assert len(marked) == 16, 'ต้องมี op แปล 16 ตัว (mnTrans + mnTrA1..15) เจอ %d: %s' % (len(marked), marked)
    for op in cfg['ops']:
        if op['id'] in PROD_OPS:
            assert 'aux' not in op, '🔴 op ผลิต %s ห้ามมี aux' % op['id']

    # ② loadingLabel บนปุ่มแปล
    btns = []
    def fix(n):
        if BTN_MARK in str(n.get('className', '')):
            n['loadingLabel'] = LOADING_LABEL
            btns.append(n)
    walk(cfg, fix)
    assert len(btns) == 15, 'ปุ่มแปลต้องมี 15 ตัว เจอ %d' % len(btns)
    for b in btns:
        assert b['el'] == 'retry-button', 'ปุ่มแปลต้องเป็น retry-button (ตัวที่ engine ให้สปินเนอร์)'

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    assert after.count('"aux": true') == 16, 'จำนวน aux ไม่ตรง'
    assert after.count(LOADING_LABEL) == 15
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v34 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① aux: true บน %s' % ', '.join(marked[:3] + ['…', marked[-1]]))
    print('   ② loadingLabel "%s" บนปุ่มแปล 15 ตัว' % LOADING_LABEL)
    print('   🪤 ต้องใช้กับ engine v1.9.0 ขึ้นไป (ต่ำกว่านั้นอ่านคีย์ไม่ออก · ไม่พัง แต่ไม่มีผล)')


main()
