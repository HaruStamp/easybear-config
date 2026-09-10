#!/usr/bin/env python3
# minimal v12 — แถบล่างการ์ด: ชื่อสินค้ากับป้าย "คลิปที่ n/n" ต้องอยู่ **บรรทัดเดียวกัน** (2026-09-10 · พี่หมีแก้ให้)
#
# รูปที่ต้องได้:
#                                   [▣ 3]     ← ป้ายจำนวนบอร์ด แถวบน ชิดขวา (เฉพาะคลิปยาว)
#   [Hoka รองเท้า..] ......... [คลิปที่ 1/3]  ← ชื่อตัดด้วยจุดไข่ปลา · ป้ายคลิปชิดขวา · บรรทัดเดียว
#
# 📌 **แก้ที่ผมทำพลาดมา 2 รอบ ไม่ใช่บั๊กของใคร:**
#   v10 ผมเติม `!whitespace-normal` ให้ชื่อสินค้าเอง (อนุมานว่า "ตัดบรรทัดได้ = อ่านง่ายกว่า")
#       ⇒ พี่หมีเห็นของจริงแล้วบอกว่าไม่เอา ให้ตัดด้วยจุดไข่ปลาแทน — **ของที่ผมอนุมานเอง ไม่ใช่ของที่สั่ง**
#   v11 ผมยุบป้าย 2 ใบเป็นคอลัมน์แล้ววางคู่กับชื่อ ⇒ ชื่อกับป้ายคลิป**หลุดจากบรรทัดเดียวกัน**
#       ⇒ โจทย์จริงคือ "ป้ายบอร์ดขึ้นไปแถวบน" ไม่ใช่ "ป้ายคลิปตามขึ้นไปด้วย"
#
# 🔑 โครงที่ใช้: แถบเดิมเป็น flex-row อยู่แล้ว ⇒ **ไม่แตะ el/className ของแถบ** (กันโรค flex-row ปะทะ flex-col
#    ที่ผู้ชนะตัดสินด้วยลำดับใน stylesheet) · ใส่ลูกตัวเดียวเป็นกล่องคอลัมน์เต็มความกว้างแทน
#      แถบ(row) → [ box(w-full flex-col) → [ แถวป้ายบอร์ด(self-end) , แถวชื่อ+ป้ายคลิป(nowrap) ] ]
#
# 🪤 `min-w-0` ต้องมีทั้งกล่องคอลัมน์และแถวใน — ไม่งั้น `truncate` ของชื่อไม่ทำงาน
#    (flex item มี min-width:auto เป็นค่าเริ่มต้น = ไม่ยอมหดต่ำกว่าเนื้อหา แล้วมันดันล้นแทนที่จะตัด)
#
# รันซ้ำได้ (idempotent) · รับได้ทั้งโครง v11 (คอลัมน์) และโครงเดิม (เรียงในแถว)
import json, sys, os

REAL_BADGE = 'คลิปที่ {item.clipIndex}/{values.clipsPerProduct}'
V11_COL = 'ml-auto shrink-0 flex flex-col items-end gap-1'
STACK = 'w-full min-w-0 flex flex-col gap-1'
INNER = 'w-full min-w-0 items-center gap-1.5'
WRAP_TOKENS = ['!whitespace-normal', '@[420px]:!whitespace-nowrap']   # ★v10 เติมไว้เอง — พี่หมีสั่งเอาออก


def nodes(n, path='$'):
    if isinstance(n, dict):
        yield path, n
        for k, v in n.items():
            yield from nodes(v, path + '.' + k)
    elif isinstance(n, list):
        for i, v in enumerate(n):
            yield from nodes(v, path + '[%d]' % i)


def is_clip(c):
    v = c.get('value')
    return c.get('el') == 'text' and (v == REAL_BADGE
        or (isinstance(v, dict) and v.get('op') == 'concat' and (v.get('parts') or [''])[0] == 'คลิปที่ '))


def is_name(c):
    return c.get('el') == 'text' and c.get('value') in ('{item.productName}', '{item.name}')


def is_board(c):
    return c.get('el') == 'row' and any(isinstance(d, dict) and d.get('icon') == 'burst_mode'
                                        for d in (c.get('card') or []))


def find(strip, pred):
    """เดินหาลูกที่ตรงเงื่อนไข ลึกเท่าไหร่ก็ได้ (โครง v11 ฝังลึก 1 ชั้น)"""
    out = []
    def w(n):
        for c in (n.get('card') or []):
            if isinstance(c, dict):
                if pred(c): out.append(c)
                w(c)
    w(strip)
    return out


def cls_del(node, tokens):
    keep = [t for t in (node.get('className') or '').split() if t not in tokens]
    node['className'] = ' '.join(keep)


def cls_add(node, token):
    if token not in (node.get('className') or '').split():
        node['className'] = ((node.get('className') or '') + ' ' + token).strip()


def patch(cfg):
    log = []
    for path, n in list(nodes(cfg)):
        if not isinstance(n, dict) or not isinstance(n.get('card'), list): continue
        if 'absolute bottom-0' not in (n.get('className') or ''): continue
        clip = find(n, is_clip)
        name = find(n, is_name)
        if len(clip) != 1 or len(name) != 1: continue
        clip, name = clip[0], name[0]
        board = find(n, is_board)
        board = board[0] if board else None

        before = json.dumps(n, ensure_ascii=False, sort_keys=True)

        # ① ชื่อสินค้า = บรรทัดเดียว ตัดด้วยจุดไข่ปลา (ถอดของที่ v10 เติมไว้เอง)
        cls_del(name, WRAP_TOKENS)
        cls_add(name, 'truncate')
        # ② ป้ายคลิปชิดขวาเสมอ (ทั้งการ์ดที่รอคิวและที่วาดแล้ว = วางที่เดียวกัน)
        cls_add(clip, 'ml-auto')

        if board is None:
            n['card'] = [name, clip]                       # การ์ดที่ยังไม่วาด: แถวเดียว 2 ชิ้น
        else:
            cls_del(board, ['ml-auto'])                    # ★ml-auto อยู่ที่ป้ายคลิปแล้ว ห้ามซ้ำ
            cls_add(board, 'self-end')                     # ชิดขวาในคอลัมน์
            n['card'] = [{
                "el": "box", "className": STACK,
                "card": [board,
                         {"el": "row", "style": {"flexWrap": "nowrap"}, "className": INNER,
                          "card": [name, clip]}],
            }]
        if json.dumps(n, ensure_ascii=False, sort_keys=True) != before:
            log.append('  · %s @%s' % ('ป้ายบอร์ดขึ้นแถวบน + ชื่อ/คลิปบรรทัดเดียว' if board else 'ชื่อ/คลิปบรรทัดเดียว', path[-40:]))
    return log


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = sys.argv[1:] or [os.path.join(here, 'minimal-lab.json'), os.path.join(here, 'minimal.json')]
    for f in files:
        cfg = json.load(open(f, encoding='utf-8'))
        before = json.dumps(cfg, ensure_ascii=False, sort_keys=True)
        print('══', os.path.basename(f))
        for line in patch(cfg): print(line)
        if json.dumps(cfg, ensure_ascii=False, sort_keys=True) == before:
            print('  (ไม่มีอะไรเปลี่ยน — แพตช์ลงไปแล้ว)')
        else:
            json.dump(cfg, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('  ✅ เขียนแล้ว')


if __name__ == '__main__':
    main()
