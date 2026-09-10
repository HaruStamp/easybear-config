#!/usr/bin/env python3
# minimal v10 — แยก "กำลังทำจริง" ออกจาก "รอคิว" บนการ์ดหน้าผลิต (2026-09-10 · คำสั่งพี่หมี จากภาพหน้าจอ Android)
#
# อาการที่พี่หมีเจอ (โหมดออโต้ · การ์ดที่ยังไม่ถึงคิว):
#   ① เห็นไอคอน 2 ตัวพร้อมกัน — นาฬิกา (รอคิว) + ไอคอนของงาน (ภาพ/วิดีโอ)  ⇒ อ่านไม่ออกว่าใบไหนกำลังทำ
#   ② ข้อความบอกว่า "กำลังวาดสตอรีบอร์ด" ทั้งที่ยังไม่ถึงคิว   ⇒ **การ์ดโกหก** (ตระกูลเดียวกับ "ช่องมีของ ≠ งานเสร็จ")
#   ③ แถวล่างการ์ดผีเขียน `ชื่อ [N คลิป] คลิปที่ N` ไม่เหมือนการ์ดจริงที่เป็น `ชื่อ … [คลิปที่ n/n]`
#
# 🔑 กฎเดียวที่ตัดสินทั้งไฟล์: **สาขา "กำลังทำ" ต้องโผล่ตอนที่สาขา "รอคิว" ไม่โผล่ เป๊ะ ๆ**
#    ⇒ ไม่ได้เขียนเงื่อนไขใหม่ให้สาขากำลังทำ แต่เอา `when` ของสาขารอคิวมา **not()** ตรง ๆ
#    ⇒ ① สองสาขาไม่มีวันโผล่พร้อมกัน และไม่มีวันหายพร้อมกัน (พิสูจน์ได้จากรูปทรง ไม่ต้องรัน)
#      ② **โหมดทำทีละขั้นไม่ขยับสักพิกเซล** — เพราะ `when` ของนาฬิกาในกริดมี `mode=auto` อยู่แล้ว
#         not() ของมันจึงเป็นจริงเสมอในโหมดมือ = เห็นเหมือนเดิมทุกอย่าง
#
# 🪤 ห้ามเขียนเงื่อนไข "กำลังทำ" ขึ้นมาใหม่เอง (เช่น or(running,retrying)) — กล่องแต่ละใบมีเงื่อนไขรอคิวไม่เหมือนกัน
#    (กริดมี mode=auto พ่วง · กล่องวิดีโอในลิสต์มี not(error) พ่วง) เขียนใหม่ = สองสาขาเหลื่อมกันเงียบ ๆ
#
# รันซ้ำได้ (idempotent) — ตรวจก่อนแก้ทุกจุด
import json, sys, copy, os

WAIT_BOARD = 'รอคิววาดสตอรีบอร์ด'
WAIT_VIDEO = 'รอคิวสร้างวิดีโอ'
BEAT = 'animate-evbeat'          # ★ต้องมี @keyframes evbeat ใน framework/app-css.ts ไม่งั้นคลาสนี้ประกาศแล้วไม่มีผล
REAL_BADGE = 'คลิปที่ {item.clipIndex}/{values.clipsPerProduct}'   # ป้ายบนการ์ดจริง = ต้นแบบของป้ายบนการ์ดผี
WRAP_TOKENS = ['!whitespace-normal', '@[420px]:!whitespace-nowrap']   # ยกมาจากชื่อสินค้าบนการ์ดจริง


def boxes(n, path='$'):
    if isinstance(n, dict):
        if isinstance(n.get('card'), list):
            yield path, n
        for k, v in n.items():
            yield from boxes(v, path + '.' + k)
    elif isinstance(n, list):
        for i, v in enumerate(n):
            yield from boxes(v, path + '[%d]' % i)


def is_opicon(c):
    return c.get('el') == 'icon' and isinstance(c.get('icon'), dict) and c['icon'].get('table') == 'opIcons'


def has_opnames(c):
    return c.get('el') == 'text' and 'opNames' in json.dumps(c.get('value', ''), ensure_ascii=False)


def busy_only_box(b):
    """กล่องที่ตัวเองถูกล็อกว่า status=running อยู่แล้ว (ป้าย pill) — ไม่ต้องแตะ"""
    return json.dumps(b.get('when'), ensure_ascii=False) == json.dumps(
        {"op": "eq", "a": "{item.status}", "b": "running"}, ensure_ascii=False)


def negate(w):
    """not(w) — ถ้า w เป็น not(x) อยู่แล้วให้คลายออกแทนการซ้อน (อ่านง่ายและเทียบได้)"""
    if isinstance(w, dict) and w.get('op') == 'not' and 'a' in w and len(w) == 2:
        return w['a']
    return {"op": "not", "a": copy.deepcopy(w)}


def and_with(existing, extra):
    if existing is None:
        return copy.deepcopy(extra)
    return {"op": "and", "a": copy.deepcopy(existing), "b": copy.deepcopy(extra)}


def patch(cfg):
    log = []

    # ── P1 · แยกสาขา กำลังทำ / รอคิว ในทุกกล่องที่มีไอคอน opIcons ────────────
    for path, b in list(boxes(cfg)):
        kids = [c for c in b['card'] if isinstance(c, dict)]
        oi = [c for c in kids if is_opicon(c)]
        if not oi or busy_only_box(b):
            continue
        # ไอคอน "รอคิว" = ไอคอนตัวอื่นในกล่องเดียวกันที่มี when (นาฬิกา/หนัง)
        qicon = next((c for c in kids
                      if c.get('el') == 'icon' and not is_opicon(c) and c.get('when') is not None), None)
        if qicon is None:
            log.append('  ⚠️  ข้าม %s — ไม่มีไอคอนรอคิวให้ยึด' % path[-46:])
            continue
        QW = qicon['when']
        BUSY = negate(QW)

        for c in oi:
            if json.dumps(c.get('when'), ensure_ascii=False) != json.dumps(BUSY, ensure_ascii=False):
                c['when'] = copy.deepcopy(BUSY)
                log.append('  · gate ไอคอนงาน @%s' % path[-46:])
            cls = c.get('className', '')
            if BEAT not in cls:
                c['className'] = (cls + ' ' + BEAT).strip()
                log.append('  · เติม %s @%s' % (BEAT, path[-46:]))

        for c in kids:
            if not has_opnames(c):
                continue
            w = c.get('when')
            bj = json.dumps(BUSY, ensure_ascii=False)
            # gate ไว้แล้วหรือยัง — เทียบ "ตัวที่ AND เข้าไป" ตรง ๆ ไม่ใช่เดาจากสตริงบางส่วน (รันซ้ำต้องนิ่ง)
            if json.dumps(w, ensure_ascii=False) == bj or (
                    isinstance(w, dict) and w.get('op') == 'and'
                    and json.dumps(w.get('b'), ensure_ascii=False) == bj):
                continue
            c['when'] = and_with(w, BUSY)
            log.append('  · gate ข้อความ "กำลัง…" @%s' % path[-46:])

        # กล่องไหนมีไอคอนรอคิวแต่ไม่มี "ข้อความ" รอคิว = ไอคอนโดด ไม่มีคำอธิบาย → เติมให้
        qj = json.dumps(QW, ensure_ascii=False)
        if not any(c.get('el') == 'text' and json.dumps(c.get('when'), ensure_ascii=False) == qj for c in kids):
            bw = json.dumps(b.get('when'), ensure_ascii=False)
            wait = WAIT_VIDEO if '{item.slots.video}' in bw and '{item.slots.board}' not in bw else WAIT_BOARD
            node = {"el": "text", "value": wait, "when": copy.deepcopy(QW),
                    "className": "!text-[12.5px] font-bold opacity-45 text-center px-2"}
            b['card'].insert(b['card'].index(qicon) + 1, node)
            log.append('  · เติมข้อความ "%s" @%s' % (wait, path[-46:]))

    # ── P2 · ถ้อยคำสาขารอคิว ต้องขึ้นต้น "รอคิว" ──────────────────────────
    for _, b in list(boxes(cfg)):
        for c in b['card']:
            if isinstance(c, dict) and c.get('el') == 'text':
                if c.get('value') == 'รอวาดภาพ' and 'text-center' not in (c.get('className') or '') \
                        and '!text-[13px]' in (c.get('className') or '') and 'text-white' not in (c.get('className') or ''):
                    c['value'] = WAIT_BOARD
                    log.append('  · ถ้อยคำ รอวาดภาพ → %s' % WAIT_BOARD)
                elif c.get('value') == 'รอสร้างวิดีโอ':
                    c['value'] = WAIT_VIDEO
                    log.append('  · ถ้อยคำ รอสร้างวิดีโอ → %s' % WAIT_VIDEO)

    # ── P3 · แถวล่างการ์ดผี (กริด) ให้เป็นมาตรฐานเดียวกับการ์ดจริง ──────────
    # 🪤 **ลอก className มาจากการ์ดจริงใน config ตัวเดียวกัน ห้ามฮาร์ดโค้ด** — minimal.json กับ
    #    minimal-lab.json ป้ายคนละสไตล์ (lab ผ่านงาน v9 มาแล้ว) ⇒ ค่าคงที่เดียวจะทำให้ตัวหนึ่งเพี้ยน
    badge_cls = None
    for _, bb in boxes(cfg):
        for c in bb['card']:
            if isinstance(c, dict) and c.get('el') == 'text' and c.get('value') == REAL_BADGE:
                badge_cls = c.get('className') or ''
    if badge_cls is None:
        log.append('  ⚠️  ไม่เจอป้ายบนการ์ดจริง — ข้าม P3 (ห้ามเดา className เอง)')
    BADGE_CLS = ((badge_cls or '') + ' ml-auto').strip() if badge_cls is not None else None

    for path, b in (list(boxes(cfg)) if BADGE_CLS else []):
        kids = [c for c in b['card'] if isinstance(c, dict)]
        chip = next((c for c in kids if c.get('el') == 'text'
                     and c.get('value') == '[{values.clipsPerProduct} คลิป]'), None)
        idx = next((c for c in kids if c.get('el') == 'text' and isinstance(c.get('value'), dict)
                    and c['value'].get('op') == 'concat'
                    and c['value'].get('parts', [None])[0] == 'คลิปที่ '), None)
        if chip is None and idx is None:
            continue
        if chip is not None:
            b['card'].remove(chip)
            log.append('  · เอาชิป [N คลิป] ออก @%s' % path[-46:])
        # ชื่อสินค้า: การ์ดจริงตัดบรรทัดได้บนมือถือ (ภาพที่พี่หมีชี้เป็นแบบนั้น) การ์ดผีตัดด้วย … ⇒ ให้เหมือนกัน
        #   🪤 ลอกเฉพาะ "โทเคนเรื่องการตัดบรรทัด" ห้ามลอกทั้งชุด — การ์ดจริงมี !text-white เพราะนั่งบนแถบไล่สีเข้ม
        nm = next((c for c in kids if c.get('el') == 'text' and c.get('value') == '{item.name}'), None)
        if nm is not None:
            for tok in WRAP_TOKENS:
                if tok not in (nm.get('className') or ''):
                    nm['className'] = ((nm.get('className') or '') + ' ' + tok).strip()
                    log.append('  · ชื่อสินค้าตัดบรรทัดได้เหมือนการ์ดจริง (%s)' % tok)
        if idx is not None and not (len(idx['value'].get('parts', [])) == 4 and idx.get('className') == BADGE_CLS):
            idx['value'] = {"op": "concat", "parts": ["คลิปที่ ",
                                                     {"op": "add", "a": {"op": "index"}, "b": 1},
                                                     "/", "{values.clipsPerProduct}"]}
            idx['className'] = BADGE_CLS
            log.append('  · badge คลิปที่ n/n @%s' % path[-46:])
    return log


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = sys.argv[1:] or [os.path.join(here, 'minimal-lab.json'), os.path.join(here, 'minimal.json')]
    for f in files:
        cfg = json.load(open(f, encoding='utf-8'))
        before = json.dumps(cfg, ensure_ascii=False, sort_keys=True)
        print('══', os.path.basename(f))
        for line in patch(cfg):
            print(line)
        after = json.dumps(cfg, ensure_ascii=False, sort_keys=True)
        if before == after:
            print('  (ไม่มีอะไรเปลี่ยน — แพตช์ลงไปแล้ว)')
        else:
            json.dump(cfg, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('  ✅ เขียนแล้ว')


if __name__ == '__main__':
    main()
