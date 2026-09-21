#!/usr/bin/env python3
# hardsell-v3-aux-flag.py — ติดธง `aux: true` ให้ op แปล (mnTrans + mnTrA1..8) · ต้องใช้ engine ≥ v1.9.0
# ที่มา: op แปลอยู่นอก `stages`/`auto` (ถูกแล้ว — ไม่ควรวิ่งในรอบผลิต) แต่ `itemRunCounts` (engine-flow.ts:241)
#   นับ **ทุก op ที่ `over` ตรง** ⇒ คลิปที่ผลิตครบ board+video ไม่ถูกนับว่าเสร็จ ⇒ การ์ด/โมดัล "งานผลิตค้างอยู่" โกหก
#   วัดของ hardsell ไว้ก่อนแก้ (engine จริง · คลิป board+video เต็ม): มี op แปล done=0/1 ทั้งก่อนและหลังกดแปล · ถอด op แปลออก done=1/1
#   🪤 ยามของเราอยู่ที่ `op.setFields.where` ไม่ใช่ `op.where` ⇒ itemRunCounts (เช็ค o.where) มองไม่เห็น = mnTrA ทั้ง 8 นับเป็นงานค้างเสมอ
#   🪤 config แก้เองไม่ได้: `runOpPart` กรอง targets ด้วย `op.where` **ก่อน** `todo = targets.filter(it => opts.force || …)`
#      ⇒ ใส่ where หลอกตัวนับ = การแปลครั้งแรกไม่มีวันรัน ⇒ ต้องเป็นธงฝั่ง engine
# engine v1.9.0 เติม `op.aux` ให้แล้ว: itemRunCounts ข้าม (`!o.aux`) + computeProgress ข้าม (แม้ใครเผลอใส่ลง stages)
# 🔴 ห้ามรันแล้วขึ้น config ถ้า Dev ยังอยู่บน engine < v1.9.0 — รุ่นเก่าไม่รู้จักธงนี้ (ไม่พัง แต่ก็ไม่ช่วย)
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
N_SCENES = 8
AUX_OPS = ['mnTrans'] + ['mnTrA%d' % i for i in range(1, N_SCENES + 1)]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    ops = {o['id']: o for o in cfg['ops']}
    for n in AUX_OPS:
        assert n in ops, 'ไม่เจอ op %s (ต้องรัน hardsell-v1 ก่อน)' % n
    if all(ops[n].get('aux') is True for n in AUX_OPS):
        print('⏭  ติดธงครบแล้ว — ไม่ทำอะไร')
        return

    for n in AUX_OPS:
        ops[n]['aux'] = True

    # ── ยาม ──
    got = {o['id']: o for o in cfg['ops']}
    for n in AUX_OPS:
        assert got[n]['aux'] is True, 'ธง aux ของ %s ไม่ติด' % n
    # op ผลิตจริงต้องไม่ติดธงเด็ดขาด (ติดแล้วโมดัลจะบอกว่าเสร็จทั้งที่ยังไม่ได้ผลิต = ตรงข้ามกับบั๊กเดิม)
    for o in cfg['ops']:
        if o['id'] not in AUX_OPS:
            assert 'aux' not in o, 'op ผลิต %s ห้ามติดธง aux' % o['id']
    # ธงไม่เปลี่ยนเรื่องเดิม: op แปลยังต้องอยู่นอก auto/stages + ยาม where ยังอยู่
    auto_s = json.dumps(cfg.get('auto'), ensure_ascii=False)
    stages_s = json.dumps(cfg.get('stages'), ensure_ascii=False)
    for n in AUX_OPS:
        assert n not in auto_s and n not in stages_s, 'op แปล (%s) ต้องไม่เข้า auto/stages' % n
    for i in range(1, N_SCENES + 1):
        o = got['mnTrA%d' % i]
        assert o['setFields'].get('where') == 'data.trans.s%den!=' % i, 'ยาม where ของ mnTrA%d หาย' % i
        assert list(o['setFields']['fields']) == ['s%den' % i], 'mnTrA%d ต้องเขียนช่องเดียว' % i

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v3 ลงแล้ว — %s' % os.path.basename(src))
    print('   ติดธง aux:true ให้ %d op (mnTrans + mnTrA1..%d) ⇒ itemRunCounts/computeProgress ไม่นับ' % (len(AUX_OPS), N_SCENES))
    print('   🔴 ต้องใช้กับ Dev ที่อยู่บน engine ≥ v1.9.0 เท่านั้น')


main()
