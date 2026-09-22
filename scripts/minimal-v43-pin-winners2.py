#!/usr/bin/env python3
# minimal-v43-pin-winners2.py — ปัก `!` ให้คลาสที่ "ชนะอยู่แล้ว" ในแถว el:'row' · **0 พิกเซลขยับ**
#
# ที่มา: `el:'row'` เติม `flex gap-2 flex-wrap items-center` ให้เสมอ ⇒ คลาสตระกูลเดียวกันที่เราเขียนจะชนกัน
#   ผู้ชนะตัดสินด้วย **ลำดับ utility ใน stylesheet** ซึ่งเราไม่ได้คุม
# 🆕 v43 = ใช้ตารางที่ starter **วัดรอบ 2** (52 คลาส · MISSING 0) ⇒ ครอบ gap-3.5/gap-4 ที่ v42 ไม่ยอมเดา
#     ⇒ 18 จุดที่ v42 เว้นไว้ ตอนนี้มีหลักฐานว่าชนะ (gap-3.5@87 · gap-4@88 > gap-2@84) ⇒ ปักได้ · ยัง 0 พิกเซลขยับ
#     🪤 starter เตือน 2 ตัวที่สวนสัญชาตญาณ (ไม่กระทบ el:'row' แต่จดไว้): `grow-0` ชนะ `grow` · `flex-row` ชนะ `flex-col`
# starter วัดลำดับจริงมาแล้ว (เดิน document.styleSheets บน tool จริง · 2026-09-22 · **n=1 หน้าเดียว ไม่รู้รุ่น**):
#   flex@45 grid@46 hidden@47 inline-flex@48 · flex-nowrap@55 flex-wrap@56
#   items-baseline@57 items-center@58 items-start@59 items-stretch@60
#   gap-1@63 gap-1.5@64 gap-2@65 gap-2.5@66 gap-3@67
#   🔑 ในตระกูลเดียวกัน **เรียงตามตัวอักษร/ตัวเลข ไม่ใช่ตามความหมาย** (baseline < center < start < stretch)
#
# สคริปต์นี้แตะ **เฉพาะตัวที่วัดแล้วว่าชนะ** ⇒ ใส่ `!` แล้วผลลัพธ์ **เท่าเดิมทุกพิกเซลวันนี้**
#   กำไรคือ: วันไหน Flow เปลี่ยน host แล้วลำดับกลับด้าน **ของเราจะไม่เลื่อนเงียบ ๆ**
# 🔴 **ไม่แตะ 2 กลุ่มนี้เด็ดขาด**
#   ① ตัวที่วัดแล้ว **แพ้** (gap-1 · gap-1.5 · items-baseline · flex-nowrap) — ใส่ `!` = **เปลี่ยนหน้าตาที่พี่หมีอนุมัติแล้ว** ⇒ ต้องให้เขาเคาะ
#   ② ตัวที่ **ไม่มีในตารางที่วัดมา** (gap-3.5 · gap-4) — เดาว่าชนะตามกฎตัวเลขได้ แต่ **การเดาคือสิ่งที่ทำให้ 2 ทีมพลาดมาแล้ววันนี้**
# 🪤 ท่านี้ยืมจาก showhow (v48 ของเขา) — เขาปัก !items-start ด้วยเหตุผลเดียวกัน
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
IDX = {'block': 44, 'flex': 45, 'grid': 46, 'hidden': 47, 'inline-flex': 48,
       'flex-nowrap': 67, 'flex-wrap': 68,
       'items-baseline': 69, 'items-center': 70, 'items-end': 71, 'items-start': 72, 'items-stretch': 73,
       'gap-0': 80, 'gap-0.5': 81, 'gap-1': 82, 'gap-1.5': 83, 'gap-2': 84, 'gap-2.5': 85,
       'gap-3': 86, 'gap-3.5': 87, 'gap-4': 88, 'gap-5': 89, 'gap-6': 90, 'gap-8': 91}
RIVAL = {'display': 'flex', 'gap': 'gap-2', 'wrap': 'flex-wrap', 'align': 'items-center'}


def fam(c):
    if c in ('flex', 'grid', 'inline-flex', 'block', 'hidden', 'inline-grid'): return 'display'
    if c.startswith('gap-') and not c.startswith(('gap-x-', 'gap-y-')): return 'gap'
    if c in ('flex-wrap', 'flex-nowrap', 'flex-wrap-reverse'): return 'wrap'
    if c.startswith('items-'): return 'align'
    return None


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'minimal-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)

    pinned, skipped_lose, skipped_unknown = [], [], []

    def walk(n):
        if isinstance(n, dict):
            if n.get('el') == 'row':
                toks = str(n.get('className', '')).split()
                out = []
                for t in toks:
                    f = fam(t) if (not t.startswith('!') and ':' not in t) else None
                    if not f or t == RIVAL[f]:
                        out.append(t); continue
                    if t not in IDX:
                        skipped_unknown.append(t); out.append(t); continue
                    if IDX[t] > IDX[RIVAL[f]]:
                        out.append('!' + t); pinned.append(t)      # ชนะอยู่แล้ว → ปักให้แน่นอน
                    else:
                        skipped_lose.append(t); out.append(t)      # แพ้ → ห้ามแตะ (เปลี่ยน UI)
                if out != toks:
                    n['className'] = ' '.join(out)
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(cfg)

    from collections import Counter
    if not pinned:
        print('⏭  ปักครบแล้ว — ไม่ทำอะไร')
        return
    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before

    # ── ยาม: ห้ามเผลอปักตัวที่แพ้ ──
    def recheck(n, bad):
        if isinstance(n, dict):
            if n.get('el') == 'row':
                for t in str(n.get('className', '')).split():
                    if t.startswith('!') and ':' not in t:
                        raw = t[1:]
                        f = fam(raw)
                        if f and raw in IDX and IDX[raw] < IDX[RIVAL[f]]:
                            bad.append(raw)
            for v in n.values():
                recheck(v, bad)
        elif isinstance(n, list):
            for v in n:
                recheck(v, bad)
    bad = []
    recheck(cfg, bad)
    assert not bad, '🔴 เผลอปัก ! ให้ตัวที่แพ้ = เปลี่ยนหน้าตา: %s' % sorted(set(bad))

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ v43 ลงแล้ว — ปัก ! ให้ตัวที่ "วัดแล้วว่าชนะ" %d จุด · **0 พิกเซลขยับ**' % len(pinned))
    print('   ปัก       : %s' % dict(Counter(pinned)))
    print('   ไม่แตะ(แพ้) : %s  ← เปลี่ยน = เปลี่ยนหน้าตา ต้องให้พี่หมีเคาะ' % dict(Counter(skipped_lose)))
    print('   ไม่แตะ(ไม่รู้): %s  ← ไม่มีในตารางที่วัดมา ไม่เดา' % dict(Counter(skipped_unknown)))


main()
