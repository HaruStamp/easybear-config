#!/usr/bin/env python3
# minimal-v31-translate-btn-inline.py — ปุ่มแปลย้ายขึ้นไปอยู่แถวเดียวกับป้าย "บทภาพ" (ชิดขวา) + เปลี่ยนคำ
# พี่หมี 2026-09-21: "ปุ่มอยากจะอยู่แถวเดียวกับ label บทภาพ ด้านขวา แล้วใช้คำว่า แปลงเป็นบทวิดีโอ"
#   v30 วางปุ่มไว้ท้ายกล่อง (ใต้ช่องบทวิดีโอ) ⇒ อยู่ไกลจากบทไทยที่เพิ่งแก้ · กินความสูงเพิ่มอีก 1 แถว
#   ใหม่: [🖼 บทภาพ (คำสั่งวาด)] ————— [🔤 แปลงเป็นบทวิดีโอ]   ← แถวเดียวกัน ปุ่มชิดขวา
# 🪤 ห้ามแตะ `when`/`ops` ของปุ่มเดิม — ย้ายตำแหน่ง+เปลี่ยนป้ายเท่านั้น (ตรรกะ per-scene ของ v30 พิสูจน์แล้ว)
# 🪤 ป้ายเดิมเป็น el:text มี icon ⇒ ห่อด้วย row justify-between ไม่ใช่สร้างป้ายใหม่ (กัน drift ของข้อความ/ไอคอน)
# รันซ้ำได้: ตรวจ marker mn-tr-inline
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'mn-tr-inline'
OLD_MARK = 'mn-tr-scene'
NEW_LABEL = 'แปลงเป็นบทวิดีโอ'
BTN_CLASS = ('shrink-0 justify-center !gap-1 !h-8 !min-h-0 !px-2.5 !rounded-lg !text-[11.5px] font-bold '
             'border border-[var(--ev-border)] !bg-[var(--ev-surface2)] !text-[var(--ev-text)] ' + MARK)


def walk(node, fn, path=''):
    if isinstance(node, dict):
        fn(node, path)
        for k, v in node.items():
            walk(v, fn, path + '/' + k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, fn, path + '[%d]' % i)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)
    # 🪤 ต้องเช็ค "ทำแล้วหรือยัง" ก่อนเช็ค precondition — ไม่งั้นรันซ้ำจะฟ้องว่า "ยังไม่ได้รัน v30"
    #    (เพราะ v31 ลบ marker ของ v30 ทิ้งตอนย้ายปุ่ม) — เจอจริงตอนรันซ้ำครั้งแรก
    if MARK in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return
    assert OLD_MARK in before, 'ต้องรัน v30 ก่อน (ยังไม่มีปุ่มแปลรายฉาก)'

    moved = []

    def fix(n, p):
        kids = n.get('card')
        if not isinstance(kids, list):
            return
        # หาปุ่มแปลของ v30 ในกล่องนี้
        bi = next((i for i, k in enumerate(kids)
                   if isinstance(k, dict) and OLD_MARK in str(k.get('className', ''))), None)
        if bi is None:
            return
        btn = kids[bi]
        scene = int(re.match(r'mnTrA(\d+)$', btn['ops'][1]).group(1))
        # ป้าย "บทภาพ (คำสั่งวาด)" ของกล่องเดียวกัน
        li = next((i for i, k in enumerate(kids)
                   if isinstance(k, dict) and k.get('el') == 'text' and str(k.get('value', '')).startswith('บทภาพ')), None)
        assert li is not None, 'ฉาก %d: หาป้าย "บทภาพ" ไม่เจอ' % scene
        assert li < bi, 'ฉาก %d: ลำดับผิดคาด' % scene
        btn['label'] = NEW_LABEL
        btn['className'] = BTN_CLASS
        row = {'el': 'row', 'style': {'flexWrap': 'nowrap'},
               'className': 'w-full items-center justify-between gap-2',
               'card': [kids[li], btn]}
        kids.pop(bi)              # เอาปุ่มออกจากท้ายกล่องก่อน (index ปุ่มมากกว่าป้ายเสมอ)
        kids[li] = row            # แล้วแทนป้ายด้วยแถว [ป้าย][ปุ่ม]
        moved.append(scene)

    walk(cfg, fix)
    assert sorted(moved) == list(range(1, 16)), 'ต้องย้ายครบ 15 ฉาก (ได้ %s)' % sorted(moved)

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    assert OLD_MARK not in after, 'ยังมีปุ่มรุ่นเก่าค้าง'
    assert after.count(NEW_LABEL) == 15, 'ป้ายปุ่มต้องมี 15 จุด'
    # ยาม: ปุ่มยังต้องคู่กับ op ของฉากตัวเอง และยังไม่เข้า auto/stages
    pairs = []
    def chk(n, p):
        if isinstance(n, dict) and MARK in str(n.get('className', '')):
            pairs.append((n['ops'][1], n.get('label')))
    walk(cfg, chk)
    assert sorted(int(re.match(r'mnTrA(\d+)$', a).group(1)) for a, _ in pairs) == list(range(1, 16))
    assert 'mnTrA1' not in json.dumps(cfg.get('auto'), ensure_ascii=False)
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v31 ลงแล้ว — %s' % os.path.basename(src))
    print('   ปุ่ม 15 ตัวย้ายขึ้นไปอยู่แถวเดียวกับป้าย "บทภาพ (คำสั่งวาด)" ชิดขวา · เปลี่ยนคำเป็น "%s"' % NEW_LABEL)
    print('   ตรรกะ per-scene ของ v30 คงเดิมทุกตัวอักษร (ops/when ไม่ถูกแตะ)')


main()
