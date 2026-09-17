#!/usr/bin/env python3
# minimal v15 — ปุ่มเลือกความยาวคลิป: บรรทัดบน (10 วิ / 20 วิ / 30 วิ) เป็นตัวหนา (2026-09-10 · พี่หมีสั่ง)
#   บรรทัดล่าง ("ใช้ 15 เครดิต") คงเดิมทุกอย่าง
#
# 🔑 **ทำฝั่ง config ล้วน ไม่แตะ engine** — ทั้งที่คลาสอยู่ใน `atoms-cases-a2.tsx` เพราะ:
#   ① `case 'grid-select'` เป็น **บรรทัดเดียวยาว ~1.5KB** = ทรงที่ CLAUDE.md ห้ามสั่ง agent แก้
#      (agent ต้อง regenerate ทั้งบรรทัด แล้วมันลากทั้งฟังก์ชันไปด้วย · ไฟล์ตระกูลนี้เคย spiral 6 รอบ)
#   ② ถ้าใส่ `font-bold` ลง engine ตรง ๆ = **grid-select ทุกจุดในทุกแอปหนาตามหมด** โดยไม่มีใครขอ
#      (minimal เองก็มีหลายจุด: การ์ดเลือกโหมด · สไตล์ตัวอักษร) ⇒ blast radius เกินคำสั่ง
#   ⇒ ใช้ arbitrary variant ยิงเฉพาะโหนดนี้ — ท่าที่แอปนี้ใช้อยู่แล้ว 4 จุด (เช่น segmented `[&>div:last-child]:`)
#
# 🪤 **ใช้ `span:first-of-type` ไม่ใช่ `span:first-child`** — engine เรนเดอร์ `<img>` ก่อน span ได้ถ้า option มี image
#    (ตัวนี้ไม่มี แต่ผูกกับ *กฎ* ดีกว่าผูกกับ *สภาพวันนี้*)
# 🪤 **ห้ามใช้ `[&_button]:font-bold`** — จะไปโดนบรรทัด "ใช้ N เครดิต" ด้วย ซึ่งพี่หมีสั่งให้คงเดิม
# 🪤 คลาสนี้จะ **ตายเงียบ** ถ้า engine เปลี่ยนโครง markup ⇒ ยาม ⑧ ใน minimal-queue-ui เรนเดอร์ของจริงมาเฝ้า
import json, sys, os

BOLD = '[&_button>span:first-of-type]:font-bold'


def nodes(n):
    if isinstance(n, dict):
        yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n, list):
        for v in n: yield from nodes(v)


def patch(cfg):
    log = []
    for n in list(nodes(cfg)):
        if not isinstance(n, dict) or n.get('el') != 'grid-select' or n.get('field') != 'svSec':
            continue
        cls = n.get('className') or ''
        if BOLD in cls.split():
            continue
        n['className'] = (cls + ' ' + BOLD).strip()
        log.append('  · ทำบรรทัดบนของปุ่มความยาวคลิปเป็นตัวหนา')
    return log


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for f in (sys.argv[1:] or [os.path.join(here, 'minimal-dev.json'), os.path.join(here, 'minimal.json')]):
        cfg = json.load(open(f, encoding='utf-8'))
        before = json.dumps(cfg, ensure_ascii=False, sort_keys=True)
        print('══', os.path.basename(f))
        for l in patch(cfg): print(l)
        if json.dumps(cfg, ensure_ascii=False, sort_keys=True) == before:
            print('  (ไม่มีอะไรเปลี่ยน — แพตช์ลงไปแล้ว)')
        else:
            json.dump(cfg, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('  ✅ เขียนแล้ว')


if __name__ == '__main__':
    main()
