#!/usr/bin/env python3
# minimal-v45-gate-and-4k.py — 2 เรื่องในรอบเดียว (พี่หมีเคาะ 2026-09-23)
#
# ① ประตูกันวาดจากบทว่าง (รูเครดิต · showhow เจอ · 3/3 ทีมโดน)
#    เส้นทาง: ผลิต 10 วิ จนเสร็จ → เปลี่ยน svSec เป็น 20/30 → กดผลิต
#      mnPlan out='plan' ⇒ product ที่มี plan แล้วถูกข้าม ไม่คิดบทใหม่
#      mnQueue reset=False ⇒ task เดิม (บท 5 ฉาก) อยู่ต่อ
#      mnBoard2/3 · mnVideo2/3 ไม่มี where ⇒ วาดจาก s6th/s11th ที่ว่าง = เสียเครดิตทุกคลิป ไม่มี error
#    lookups.lenScenes = {10:5, 20:10, 30:15} ⇒ ที่ 10 วิ s6-s15 **ว่าง 100%** ไม่ใช่ "อาจว่าง"
#    🔴 ต้องใช้ engine >= v1.13.x (productLoop AND op.where กับ where ของ loop · commit fa20ed2)
#       engine เก่ากว่านั้น where ของ op ถูก **แทนทั้งดุ้น** ⇒ ใส่แล้วพังหนักกว่าเดิม
#
# ② ตัดคำ "4K" ออกจาก prompt (showhow เจอโมเดลวาดเป็น UI กล้องลงเฟรม: "4K" ซ้ายบน · "30 —" ขวาบน · แถบตารางล่าง)
#    🪤 ตัดคำทิ้งเฉย ๆ **ไม่เพิ่มบรรทัด Negative** — Negative อยู่ท้ายสุด = โดนตัดก่อนเมื่อชนเพดาน 3,900 ⇒ พึ่งไม่ได้
#    ⚠️ n=1 ทั้งก่อนและหลัง · คลิปอื่นวันเดียวกันที่มีคำเดียวกันไม่แสดงอาการ
#       ⇒ เหตุผลคือ "ตัดคำที่ไม่ได้ช่วยอะไรอยู่แล้ว เพื่อลดโอกาส" ไม่ใช่ "แก้บั๊กที่พิสูจน์แล้ว"
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATES = {'mnBoard2': 's6en!=', 'mnVideo2': 's6en!=', 'mnBoard3': 's11en!=', 'mnVideo3': 's11en!='}


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)

    ops = {o['id']: o for o in cfg['ops']}
    for k in GATES:
        assert k in ops, 'ไม่เจอ op %s' % k

    if all(ops[k].get('where') == v for k, v in GATES.items()) and '4K' not in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    # ── ① ประตู ──
    gated = []
    for k, w in GATES.items():
        o = ops[k]
        assert o.get('where') in (None, w), '%s มี where อยู่แล้วและไม่ตรงที่คาด: %r' % (k, o.get('where'))
        if o.get('where') != w:
            o['where'] = w
            gated.append('%s(%s)' % (k, w))

    # ── ② ตัดคำ 4K ──
    cut = []
    def walk(n, path=''):
        if isinstance(n, dict):
            for k, v in list(n.items()):
                if isinstance(v, str) and '4K' in v:
                    new = v.replace(', 4K,', ',').replace(', 4K', '').replace('4K, ', '').replace('4K', '')
                    n[k] = new; cut.append(path + '/' + str(k))
                else: walk(v, path + '/' + str(k))
        elif isinstance(n, list):
            for i, v in enumerate(n):
                if isinstance(v, str) and '4K' in v:
                    new = v.replace(', 4K,', ',').replace(', 4K', '').replace('4K, ', '').replace('4K', '')
                    n[i] = new; cut.append(path + '/' + str(i))
                else: walk(v, path + '/' + str(i))
    walk(cfg)

    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before, 'ไฟล์ไม่เปลี่ยนเลย'

    # ── ยาม ──
    assert '4K' not in after, '🔴 ยังเหลือคำว่า 4K'
    ops2 = {o['id']: o for o in cfg['ops']}
    for k, w in GATES.items():
        assert ops2[k].get('where') == w, '🔴 %s ไม่มีประตู' % k
    for k in ('mnBoard', 'mnVideo'):
        assert ops2[k].get('where') is None, '🔴 ช่วง 1 ต้องไม่มีประตู (%s)' % k
    # ฟิลด์ประตูต้องมีจริงใน tasks
    tf = {f['key'] if isinstance(f, dict) else f for f in cfg['collections']['tasks'].get('fields', [])}
    for w in set(GATES.values()):
        assert w.split('!')[0] in tf, '🔴 ฟิลด์ %s ไม่มีใน tasks.fields' % w
    # จำนวน op ต้องไม่ขยับ
    assert len(cfg['ops']) == len(json.loads(before)['ops']), '🔴 จำนวน op เปลี่ยน'

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v45 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① ประตู %d จุด: %s' % (len(gated), ', '.join(gated) or '(มีอยู่แล้ว)'))
    print('   ② ตัดคำ 4K %d จุด: %s' % (len(cut), ' '.join(cut)))


main()
