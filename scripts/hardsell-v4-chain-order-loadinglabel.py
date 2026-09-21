#!/usr/bin/env python3
# hardsell-v4 — ① แก้ลำดับ chain ของปุ่มวิดีโอ (ช่วง 2 ถูกสร้างก่อนช่วง 1) ② เติม loadingLabel บนปุ่มแปล
#
# ① 🔴 **บั๊กจริงเฉพาะ hardsell** (เจอ 2026-09-22 ตอนเช็กมาตรฐานหลายช่วงของ minimal):
#    ปุ่มวิดีโอทุกตัวใช้ `chain: ['mnVideo2','mnVideo']` แต่ `runChain` (engine-flow.ts) เดิน op **ตามลำดับใน array**
#    ของ hardsell ช่วงวิดีโอ **ต่อเนื่องกัน**: `mnVideo2.startFrame = '{item.slots.video}'` (16 วิ = ต่อเฟรมสุดท้ายของช่วง 1)
#      ⇒ ลำดับปัจจุบัน = สร้างช่วง 2 จากช่วง 1 **ของเก่า** แล้วค่อยสร้างช่วง 1 ใหม่ทับ ⇒ รอยต่อไม่ตรง + เผาเครดิตฟรี
#      ⇒ คลิปใหม่เอี่ยม (ยังไม่มี video) ยิ่งหนัก: ช่วง 2 ถูกสร้างจาก startFrame ว่าง
#    🪤 ทำไมของ minimal/showhow ไม่เจ็บ: `startFrame: None` ทั้งคู่ = แต่ละช่วงอิสระ ⇒ สลับลำดับไม่มีผล
#      (ผมลอกลำดับ chain มาจากโครงของเขาโดยไม่ได้ดูว่าแอปเราช่วงต่อเนื่องกัน)
#    แก้: chain → ['mnVideo','mnVideo2'] ให้ตรงกับ `stages` และ `auto.productLoop.gens` (ซึ่งถูกอยู่แล้ว)
#    ยามกันซ้ำ: `scripts/lab/check-gens-order.py` (hardsell) ตรวจ chain ของปุ่มเทียบ stages แล้วบล็อก push
#
# ② `loadingLabel: 'กำลังแปล...'` บนปุ่ม "แปลงเป็นบทวิดีโอ" (engine ≥ v1.9.0) — ไม่งั้นขึ้น "กำลังสร้าง..." ซึ่งไม่ตรงบริบท
# รันซ้ำได้: ตรวจสภาพก่อนแก้
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BAD, GOOD = ['mnVideo2', 'mnVideo'], ['mnVideo', 'mnVideo2']
BTN_MARK = 'hs-tr-force'
LOADING = 'กำลังแปล...'


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

    fixed_chain, fixed_label = [], []

    def fix(n):
        if n.get('chain') == BAD:
            n['chain'] = list(GOOD)
            fixed_chain.append(n.get('label') if isinstance(n.get('label'), str) else '(dyn)')
        if BTN_MARK in str(n.get('className', '')) and n.get('loadingLabel') != LOADING:
            n['loadingLabel'] = LOADING
            fixed_label.append(n['ops'][1] if n.get('ops') else n.get('op'))

    walk(cfg, fix)
    if not fixed_chain and not fixed_label:
        print('⏭  ทำไปแล้วทั้ง 2 ข้อ — ไม่ทำอะไร')
        return

    # ── ยาม ──
    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    assert '"chain": ["mnVideo2", "mnVideo"]' not in after.replace(', ', ', '), 'ยังมี chain ลำดับเก่าค้าง'
    left = []
    walk(cfg, lambda n: left.append(n) if n.get('chain') == BAD else None)
    assert not left, 'ยังมี chain สลับลำดับเหลือ %d จุด' % len(left)
    # ปุ่มแปลต้องได้ loadingLabel ครบ 8 และยังเป็น retry-button + chain เดิม
    btns = []
    walk(cfg, lambda n: btns.append(n) if BTN_MARK in str(n.get('className', '')) else None)
    assert len(btns) == 8, 'ปุ่มแปลต้องมี 8 ปุ่ม (เจอ %d)' % len(btns)
    for b in btns:
        assert b.get('loadingLabel') == LOADING, 'loadingLabel ไม่ครบ'
        assert b.get('el') == 'retry-button' and b.get('chain') and b.get('chain')[0] == 'mnTrans', 'ปุ่มแปลเสียรูป'
    # ธง aux + ยาม where ต้องไม่ถูกแตะ
    ops = {o['id']: o for o in cfg['ops']}
    for i in range(1, 9):
        assert ops['mnTrA%d' % i].get('aux') is True, 'ธง aux ของ mnTrA%d หาย' % i
        assert ops['mnTrA%d' % i]['setFields'].get('where') == 'data.trans.s%den!=' % i, 'ยาม where หาย'
    assert ops['mnTrans'].get('aux') is True, 'ธง aux ของ mnTrans หาย'

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v4 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① แก้ลำดับ chain %d ปุ่ม: %s → %s' % (len(fixed_chain), ' → '.join(BAD), ' → '.join(GOOD)))
    print('   ② loadingLabel "%s" บนปุ่มแปล %d ปุ่ม' % (LOADING, len(fixed_label)))


main()
