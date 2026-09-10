#!/usr/bin/env python3
# minimal v13 — เอาป้าย "จำนวนบอร์ด" (▣ N) ออกจากแถบชื่อ (2026-09-10 · พี่หมีถามว่าทำยังไงให้ลงตัว หรือไม่ต้องมี)
#
# 🔑 เหตุผลที่เอาออก ไม่ใช่ "ไม่สวย" แต่เพราะ **มันไม่มีข้อมูลต่อการ์ดเลย** (วัดจากค่าที่มันแสดงจริง):
#     ค่า = {op:'div', a:'{values.svSec}', b:10}   ← ไม่มี {item.*} สักตัว
#     ⇒ ทุกการ์ดในรอบเดียวกันขึ้นเลขเดียวกันเสมอ = พิมพ์ค่ากลางซ้ำ N ใบ
#     ⇒ และหัวหน้าผลิตมีชิป "⏱ 30 วิ / คลิป" บอกค่าเดียวกันนี้อยู่แล้ว
#     ⇒ ซ้ำร้าย ถ้าผู้ใช้เปลี่ยน svSec กลางคัน การ์ดเก่าจะโชว์เลขใหม่ทั้งที่บอร์ดเป็นของเดิม = **ป้ายที่โกหก**
#        (ตระกูลเดียวกับบทเรียน "ป้ายที่ฮาร์ดโค้ด = เครื่องมือวินิจฉัยที่เสีย")
#   เลขที่เป็นความจริงต่อการ์ดยังอยู่ครบ: ตัวนับตอนผลิต "กำลังวาดสตอรีบอร์ด 2/3" (อ่านจาก slot จริง)
#
# ↩️ อยากได้กลับ: `git revert` คอมมิตนี้ หรือรัน minimal-v11-badge-stack.py ใหม่หลังคืนป้าย
import json, sys, os


def nodes(n):
    if isinstance(n, dict):
        yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n, list):
        for v in n: yield from nodes(v)


is_board = lambda c: isinstance(c, dict) and c.get('el') == 'row' and any(
    isinstance(d, dict) and d.get('icon') == 'burst_mode' for d in (c.get('card') or []))


def patch(cfg):
    log = []
    for n in list(nodes(cfg)):
        if not isinstance(n.get('card'), list): continue
        gone = [c for c in n['card'] if is_board(c)]
        for c in gone:
            n['card'].remove(c)
            log.append('  · เอาป้าย ▣ N ออก')
    # กล่องที่เหลือลูกตัวเดียว → ยุบจนแบน ให้แถบกลับเป็น "แถวเดียว ลูก 2 ชิ้น" เหมือนแถบพี่น้องทุกใบ
    # 🪤 ยุบชั้นเดียวไม่พอ — จะเหลือ row ซ้อนใน row ซึ่งเรนเดอร์ได้ แต่ **หน้าตา config ไม่เหมือนแถบอื่น**
    #    วันหลังใครมาเทียบจะนึกว่าเป็นของคนละแบบ ⇒ วนยุบจนไม่มีอะไรให้ยุบ
    WRAPPERS = ('w-full min-w-0 flex flex-col gap-1', 'w-full min-w-0 items-center gap-1.5')
    for _ in range(4):
        moved = False
        for n in list(nodes(cfg)):
            if not isinstance(n.get('card'), list): continue
            if 'absolute bottom-0' not in (n.get('className') or ''): continue
            kids = [x for x in n['card'] if isinstance(x, dict)]
            if len(kids) == 1 and isinstance(kids[0].get('card'), list) and kids[0].get('className') in WRAPPERS:
                n['card'] = list(kids[0]['card'])
                log.append('  · ยุบกล่องที่เหลือลูกตัวเดียว (แถบแบนเท่ากันทุกใบ)')
                moved = True
        if not moved: break
    return log


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for f in (sys.argv[1:] or [os.path.join(here, 'minimal-lab.json'), os.path.join(here, 'minimal.json')]):
        cfg = json.load(open(f, encoding='utf-8'))
        before = json.dumps(cfg, ensure_ascii=False, sort_keys=True)
        print('══', os.path.basename(f))
        for l in patch(cfg): print(l)
        if json.dumps(cfg, ensure_ascii=False, sort_keys=True) == before:
            print('  (ไม่มีอะไรเปลี่ยน)')
        else:
            json.dump(cfg, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('  ✅ เขียนแล้ว')


if __name__ == '__main__':
    main()
