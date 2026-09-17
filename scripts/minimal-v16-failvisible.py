#!/usr/bin/env python3
# minimal-v16-failvisible.py — "งานที่สั่งไว้" ต้องมองเห็น แม้ของยังไม่เกิด  (2026-09-11)
#
# ราก (พี่หมีเจอสด LIVE-QA): ทุกตัวเลข/ทุกประตูบนจอ นับจาก `tasks` ที่ "มีอยู่"
#   ⇒ สินค้าที่เขียนบทไม่สำเร็จ ไม่เคยเกิด task ⇒ ของที่หายไม่มีตัวตนให้นับ ⇒ ทุกเงื่อนไขผ่าน = บอกว่าเสร็จ
# ⇒ ทุกที่ต้องเทียบกับ EXPECT = สินค้าที่เปิดใช้ × คลิปต่อสินค้า
#
# รันซ้ำได้ (idempotent) · assert ทุกจุดก่อนเขียนทับ
import json, sys, copy, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / (sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json')
c = json.loads(SRC.read_text(encoding='utf-8'))
changed = []

EXPECT = {"op": "mul",
          "a": {"op": "count", "from": "products", "where": "enabled=true"},
          "b": "{values.clipsPerProduct}"}

# ─────────────────────────────────────────────────────────────
# ① mnPlan: บทไม่ครบ = ยังไม่สำเร็จ ⇒ engine ล้างผล + ตี invalid + retry ตาม run.maxAttempts
#    🪤 listLen ทำงานกับสตริง ⇒ จับ "บทเป็น {} เปล่า" ไม่ได้ตอน clipsPerProduct=1 (จับได้ตั้งแต่ 2 ขึ้นไป)
#       เคสนั้น planQueueOne ของ engine ดักไว้อยู่แล้ว แค่ไม่ retry — ไม่ได้แย่ลงกว่าเดิม
op = next(o for o in c['ops'] if o['id'] == 'mnPlan')
want_validate = {"op": "gte",
                 "a": {"op": "listLen", "value": "{item.data.plan}"},
                 "b": "{values.clipsPerProduct}"}
want_msg = 'เขียนบทได้ไม่ครบจำนวนคลิปที่ตั้งไว้ — ระบบจะสั่งอีกครั้งให้เอง ถ้ายังไม่ผ่าน ให้กดปุ่มคิดบทใหม่ที่การ์ดสินค้า'
if op.get('validate') != want_validate or op.get('validateMsg') != want_msg:
    op['validate'] = want_validate
    op['validateMsg'] = want_msg
    changed.append('① mnPlan.validate — บทไม่ครบ = retry อัตโนมัติ')

form = c['phases'][0]['form']

# ─────────────────────────────────────────────────────────────
# ④a ประตูคลังคลิป: เพิ่ม 2 คำถามที่ไม่มีใครถาม
gal = form[4]['when']['list'][1]
inner = gal['list'][1]['list']          # [count>0, video==tasks, error==0]
add_a = {"op": "eq", "a": {"op": "count", "from": "products", "where": "status=error"}, "b": 0}
add_b = {"op": "gte", "a": {"op": "count", "from": "tasks"}, "b": copy.deepcopy(EXPECT)}
assert len(inner) >= 3, 'โครงประตูคลังคลิปเปลี่ยนไป — หยุดก่อนเขียนทับ'
if add_a not in inner:
    inner.append(add_a); changed.append('④a คลังคลิป: ต้องไม่มีสินค้าที่พัง')
if add_b not in inner:
    inner.append(add_b); changed.append('④a คลังคลิป: task ต้องไม่น้อยกว่างานที่สั่ง')

# ─────────────────────────────────────────────────────────────
# ④b ตัวนับบนสุด: พูดเป็น "คลิป" เสมอ ทุกขั้น (เดิมตอนเขียนบทมันพูดเป็น "สินค้า" แต่ติดป้ายว่าคลิป)
done_clips0 = {"op": "count", "from": "tasks", "slot": "video"}
g = form[3]['card'][0]['card'][5]['card'][0]['card'][4]['card'][0]['card'][0]['card']
assert g[0]['value'] in ('{values.__runDone}', done_clips0), 'ตัวเศษตอนรันไม่ใช่ค่าที่รู้จัก — โครงเปลี่ยน'
done_clips = {"op": "count", "from": "tasks", "slot": "video"}
if g[0]['value'] != done_clips:
    g[0]['value'] = copy.deepcopy(done_clips); changed.append('④b ตัวเศษตอนรัน → นับคลิปที่เสร็จจริง')
# 🪤 ผูกกับ "รูปแบบของตัวส่วน" ไม่ใช่เลข index — ยาม ㉑ จับได้ว่ารุ่นแรกผมแก้ตกไป 1 จุด
den_n = 0
def fix_den(o):
    global den_n
    v = o.get('value')
    if not (isinstance(v, dict) and v.get('op') == 'concat'): return
    ps = v.get('parts') or []
    if len(ps) < 3 or ps[0] != '/' or ' คลิป' not in str(ps[-1]): return
    if ps[1] != EXPECT:
        ps[1] = copy.deepcopy(EXPECT); den_n += 1
def walk_den(o):
    if isinstance(o, dict):
        if o.get('el') in ('text', 'md'): fix_den(o)
        for x in o.values(): walk_den(x)
    elif isinstance(o, list):
        for x in o: walk_den(x)
walk_den(form)
if den_n: changed.append(f'④b ตัวส่วน {den_n} จุด → งานที่สั่งไว้')

# ─────────────────────────────────────────────────────────────
# ⑤ badge เอาเลขออก · ข้อความกลางเติม n/n n%
SEG_TOTAL = {"op": "div", "a": "{values.svSec}", "b": 10}
def is_opnames(v):
    return isinstance(v, dict) and v.get('op') == 'lookup' and v.get('table') == 'opNames'
badge_n = center_n = 0
def patch_text(node):
    global badge_n, center_n
    v = node.get('value')
    if not isinstance(v, dict): return
    # 🪤 โหนดเส้น 10 วิ เก็บ value เป็น `lookup` เดี่ยว ไม่ใช่ `concat` ⇒ ถูกกรองทิ้งตั้งแต่บรรทัดนี้
    #    นี่คือเหตุผลที่รอบก่อนแพตช์ไม่โดนมันเลย ทั้งที่ผมเขียนสาขารองรับไว้แล้ว — ตัวกรองทางเข้าฆ่าก่อนถึง
    if v.get('op') == 'lookup':
        parts = [v]
    elif v.get('op') == 'concat':
        parts = v.get('parts') or []
    elif v.get('op') == 'block':
        return                                   # แพตช์ไปแล้ว
    else:
        return
    if not parts or not is_opnames(parts[0]): return
    cn = str(node.get('className', ''))
    if '!text-white' in cn:                      # badge — เหลือแค่ชื่อขั้น + … (badge กริดมี truncate ⇒ เลขยาวถูกตัดจนอ่านไม่รู้เรื่อง)
        want = [copy.deepcopy(parts[0])]         # ★พี่หมีสั่งเอา … ออกหลังเห็นของจริงบนจอ — badge เอาแค่ชื่อขั้น
        if v['parts'] != want:
            v['parts'] = want; badge_n += 1
    elif 'text-center' in cn:                    # กลาง — ชื่อขั้น N/ทั้งหมด + % ของ "การเจนรอบนั้น"
        num = next((p for p in parts[1:] if isinstance(p, dict) and p.get('op') == 'min'), None)
        # 🪤 เส้น 10 วิ (ช่วงเดียว) ไม่มี n/n — แต่ **ต้องมี %** เหมือนกัน
        #    ไม่งั้น overlay บอก "กำลังวาดสตอรีบอร์ด 45%" ส่วนกล่องรอเจนบอกแค่ "กำลังวาดสตอรีบอร์ด"
        #    = สองที่บนจอเดียวกันบอกคนละอย่าง · รอบก่อนผมแก้เฉพาะสาขาที่มีเลข แล้วลืมสาขานี้ (พี่หมีทักเอง)
        if num is None:
            want1 = {"op": "block", "sep": " ", "parts": [
                {"value": copy.deepcopy(parts[0])},
                {"when": {"op": "not", "a": {"op": "eq", "a": "{item.meta.progress}", "b": ""}},
                 "value": {"op": "concat", "parts": ["{item.meta.progress}", "%"]}},
            ]}
            if node.get('value') != want1:
                node['value'] = want1; center_n += 1
            return
        # 🔴 % ที่ถูกคือ {item.meta.progress} = ความคืบหน้าของการเจนใบนั้น 0→100 แล้วรีเซ็ตทุกใบ
        #    ไม่ใช่ N/ทั้งหมด*100 (33/67) ซึ่ง "ค้างตามใบที่เสร็จ" ไม่ได้บอกว่าใบที่กำลังทำไปถึงไหน — พี่หมีทักเอง
        new = {"op": "block", "sep": " ", "parts": [
            {"value": copy.deepcopy(parts[0])},
            {"value": {"op": "concat", "parts": [copy.deepcopy(num), "/", copy.deepcopy(SEG_TOTAL)]}},
            {"when": {"op": "not", "a": {"op": "eq", "a": "{item.meta.progress}", "b": ""}},
             "value": {"op": "concat", "parts": ["{item.meta.progress}", "%"]}},
        ]}
        if node.get('value') != new:
            node['value'] = new; center_n += 1
def walk(o):
    if isinstance(o, dict):
        if o.get('el') in ('text', 'md'): patch_text(o)
        for x in o.values(): walk(x)
    elif isinstance(o, list):
        for x in o: walk(x)
walk(form[3])
if badge_n: changed.append(f'⑤ badge เอาเลขออก {badge_n} จุด')
if center_n: changed.append(f'⑤ ข้อความกลางเติม n/n n% {center_n} จุด')

# ─────────────────────────────────────────────────────────────
# ③ สินค้าที่เขียนบทไม่ผ่าน ต้องมีปุ่มให้กดที่หน้าผลิต
#    เดิมปุ่ม "คิดบทใหม่" มีที่หน้า setup หน้าเดียว ⇒ ตอนพังผู้ใช้อยู่หน้าผลิต = ไม่มีปุ่ม เหลือทาง "เริ่มใหม่" ซึ่งล้างทั้งชุด
#    🪤 repeat ชั้นในวน 10 รอบ ⇒ การ์ดพังต้องกัน index==0 ไม่งั้นโผล่ 10 ใบ
# 🪤 รอบแรกผมชี้ path ตายตัว card[7] = **โหมดการ์ดอย่างเดียว** ⇒ คนที่อยู่โหมดกริดเห็นข้อความชี้ไปที่ปุ่มที่ไม่มีอยู่
#    (พี่หมีเจอเอง — ถามว่า "ปุ่มอยู่ตรงไหน") ⇒ ไล่หา repeat products ทุกที่ในหน้าผลิตแทน
IS_ERR = {"op": "eq", "a": "{item.status}", "b": "error"}
NOT_ERR = {"op": "not", "a": dict(IS_ERR)}
def FAIL_CARD():
    return {
      "el": "box",
      "when": {"op": "and", "list": [copy.deepcopy(IS_ERR), {"op": "eq", "a": {"op": "index"}, "b": 0}]},
      "className": "rounded-[26px] border-2 border-dashed border-red-400/50 bg-red-500/[0.05] py-10 px-3 @[420px]:px-6 flex flex-col items-center justify-center gap-2.5",
      "card": [
        {"el": "icon", "icon": "edit_note", "textSize": "text-[22px]", "className": "!text-red-400 leading-none flex items-center justify-center"},
        {"el": "text", "value": "เขียนบทไม่สำเร็จ — {item.name}", "className": "!text-[15px] font-bold !text-red-400 text-center px-2"},
        {"el": "text", "value": "สินค้าตัวอื่นทำต่อไปแล้ว — ตัวนี้กดคิดบทใหม่ได้เลย", "className": "!text-[12.5px] opacity-70 text-center px-2"},
        {"el": "gen-button", "op": "mnPlan", "force": True, "label": "คิดบทใหม่", "icon": "psychology", "variant": "solid", "className": "mt-1"},
      ]}
rep_n = 0
def add_fail_card(o):
    global rep_n
    if not (o.get('el') == 'repeat' and o.get('coll') == 'products'): return
    inner = (o.get('card') or [{}])[0]
    kids = inner.get('card')
    if not isinstance(kids, list) or not kids: return
    skel = kids[0]
    if isinstance(skel.get('when'), dict) and isinstance(skel['when'].get('list'), list):
        if NOT_ERR not in skel['when']['list']:
            skel['when']['list'].append(copy.deepcopy(NOT_ERR)); rep_n += 1
    # 🪤 `when` เป็นได้ทั้ง object และสตริง ("path=value") — เช็คชนิดก่อน ไม่งั้นพังตอนเจอทรงสตริง
    def _is_fail(k):
        w = k.get('when') if isinstance(k, dict) else None
        return isinstance(w, dict) and isinstance(w.get('list'), list) and w['list'] and w['list'][0] == IS_ERR
    already = any(_is_fail(k) for k in kids)
    if not already:
        kids.insert(1, FAIL_CARD()); rep_n += 1
def walk_rep(o):
    if isinstance(o, dict):
        add_fail_card(o)
        for x in o.values(): walk_rep(x)
    elif isinstance(o, list):
        for x in o: walk_rep(x)
walk_rep(form)
if rep_n: changed.append(f'③ การ์ดเขียนบทไม่สำเร็จ + ปุ่มคิดบทใหม่ — ทุกโหมดการแสดงผล ({rep_n} จุด)')

# ─────────────────────────────────────────────────────────────
# ⑥ ดาวน์โหลด zip: iPhone ขั้นต่ำ 5 คลิป/ก้อน (พี่หมีขอ) + เพดานแข็งกันคลิปยาวลากชุดโต
#    ★ไม่ตั้ง capMB = ใช้ค่าเดิมของ engine (มือถือ 40MB) ⇒ ขยับเฉพาะ "จำนวนชิ้นขั้นต่ำ" ไม่ไปยุ่งกับเพดานที่ยังไม่มีใครวัด
zip_n = 0
def fix_zip(o):
    global zip_n
    if o.get('el') != 'zip-export': return
    # 🔑 พี่หมีชี้ (2026-09-11) ว่า "นับจำนวนชิ้น" ใช้ไม่ได้ — คลิป 10 วิ ด้วยกันเองขนาดยังไม่เท่ากัน · 30 วิ ยิ่งต่าง
    #    ⇒ การแบ่งด้วย "ไบต์" คือของที่ถูกอยู่แล้ว · สิ่งที่ควรขยับคือ "เพดาน" ไม่ใช่เปลี่ยนหน่วยวัด
    #    ⇒ ถอด minPerPart/hardCapMB ออก เหลือ capMB อย่างเดียว (engine ยังรองรับ 2 ตัวนั้นอยู่ แต่ไม่มี config ไหนใช้)
    #    🪤 50 ยังไม่ใช่เลขที่วัดว่า "เกินแล้วพัง" — เป็นก้าวทดลองจาก 40 · ตัวที่ต้องวัดจริงคือพีคแรมตอนเข้ารหัส base64
    if o.get('capMB') != 50 or 'minPerPart' in o or 'hardCapMB' in o:
        o['capMB'] = 50
        o.pop('minPerPart', None); o.pop('hardCapMB', None)
        zip_n += 1
def walk_zip(o):
    if isinstance(o, dict):
        fix_zip(o)
        for x in o.values(): walk_zip(x)
    elif isinstance(o, list):
        for x in o: walk_zip(x)
walk_zip(c)
if zip_n: changed.append(f'⑥ zip-export {zip_n} ปุ่ม → เพดาน 50MB/ก้อน (เดิม 40 · แบ่งด้วยไบต์เหมือนเดิม)')

# ─────────────────────────────────────────────────────────────
# ⑦ overlay บนช่องสื่อตอนกำลังสร้าง — เดิม engine ฮาร์ดโค้ด "กำลังสร้าง...N%" (ไม่บอกว่าสร้างอะไร ช่วงไหน)
#    ⇒ ให้ config สั่งข้อความเองผ่าน el.busyLabel · engine เติม % ต่อท้ายให้
#    🪤 ใช้ block+when เพื่อให้ 10 วิ (ช่วงเดียว) ไม่ขึ้น "1/1" ซึ่งอ่านแล้วงง
SEG_TOTAL2 = {"op": "div", "a": "{values.svSec}", "b": 10}
def _filled(slots):
    e = None
    for sl in slots:
        t = {"op": "not", "a": {"op": "eq", "a": "{item.slots." + sl + "}", "b": ""}}
        e = t if e is None else {"op": "add", "a": e, "b": t}
    return e
def busy_label(kind):
    slots = ['board', 'board2', 'board3'] if kind == 'board' else ['video', 'video2', 'video3']
    n = {"op": "min", "a": {"op": "add", "a": _filled(slots), "b": 1}, "b": copy.deepcopy(SEG_TOTAL2)}
    return {"op": "block", "sep": " ", "parts": [
        {"value": {"op": "lookup", "table": "opNames", "key": "{values.__runStage}", "fallback": "กำลังทำ"}},
        {"when": {"op": "gt", "a": "{values.svSec}", "b": 10},
         "value": {"op": "concat", "parts": [n, "/", copy.deepcopy(SEG_TOTAL2)]}},
    ]}
busy_n = 0
def fix_busy(o):
    global busy_n
    if o.get('el') != 'media-slot': return
    src = str(o.get('src', ''))
    kind = 'video' if 'video' in src else 'board' if 'board' in src else ''
    if not kind: return
    want = busy_label(kind)
    if o.get('busyLabel') != want:
        o['busyLabel'] = want; busy_n += 1
def walk_busy(o):
    if isinstance(o, dict):
        fix_busy(o)
        for x in o.values(): walk_busy(x)
    elif isinstance(o, list):
        for x in o: walk_busy(x)
walk_busy(form)
if busy_n: changed.append(f'⑦ overlay ช่องสื่อ {busy_n} จุด → บอกว่าสร้างอะไร ช่วงไหน')

# ─────────────────────────────────────────────────────────────
# ⑧ เอา … ออกจาก fallback ของ opNames ด้วย (พี่หมีสั่ง: badge/overlay ไม่ต้องมีจุดต่อท้าย)
#    🪤 รอบก่อนผมแก้เฉพาะ "ค่าปกติ" ลืม fallback ⇒ พอ __runStage ไม่ตรงคีย์ จุดกลับมาโผล่
#       = ตระกูล "แก้ทางหลักแล้วเชื่อว่าครบ" เดียวกับที่แก้ข้อความกลางแล้วลืม overlay
dot_n = 0
def fix_dots(o):
    global dot_n
    if o.get('op') == 'lookup' and o.get('table') == 'opNames':
        fb = o.get('fallback')
        if isinstance(fb, str) and (fb.endswith('…') or fb.endswith('...')):
            o['fallback'] = fb.rstrip('.…'); dot_n += 1
def fix_lit(o):
    # ★ข้อความตรง ๆ ที่บอกความคืบหน้า ก็ห้ามมีจุดต่อท้ายเหมือนกัน (เจอ 1 จุดที่หลุดจาก fallback)
    global dot_n
    v = o.get('value')
    if isinstance(v, str) and v.rstrip('.…') != v and any(k in v for k in ('กำลังเขียนบท', 'กำลังวาด', 'กำลังสร้าง', 'กำลังทำ')):
        o['value'] = v.rstrip('.…'); dot_n += 1
def walk_dots(o):
    if isinstance(o, dict):
        fix_dots(o); fix_lit(o)
        for x in o.values(): walk_dots(x)
    elif isinstance(o, list):
        for x in o: walk_dots(x)
walk_dots(c)
if dot_n: changed.append(f'⑧ fallback ของ opNames เอา … ออก {dot_n} จุด')

# ─────────────────────────────────────────────────────────────
# ⑨ ไอคอนตอนกำลังทำ = วงหมุน (เหมือน overlay ของ engine ตอนสร้างวิดีโอ) — พี่หมีสั่ง
#    เดิมกล่องรอเจนใช้ไอคอนตามขั้น + animate-evbeat (เต้น) ⇒ คนละภาษากับ overlay ที่เป็นวงหมุน
#    🪤 แตะเฉพาะไอคอนที่อยู่ "กล่องเดียวกับข้อความความคืบหน้า" — ไอคอนสถานะอื่น (นาฬิการอคิว) ห้ามแตะ
spin_n = 0
def fix_spin(box):
    global spin_n
    kids = box.get('card')
    if not isinstance(kids, list): return
    has_busy = any(k.get('el') in ('text','md') and 'opNames' in json.dumps(k.get('value',''),ensure_ascii=False)
                   and 'text-center' in str(k.get('className','')) for k in kids if isinstance(k,dict))
    if not has_busy: return
    for k in kids:
        if isinstance(k,dict) and k.get('el')=='icon' and 'opIcons' in json.dumps(k.get('icon',''),ensure_ascii=False):
            if k.get('icon')!='progress_activity':
                k['icon']='progress_activity'
                cn=str(k.get('className',''))
                k['className']=cn.replace('animate-evbeat','animate-spin') if 'animate-evbeat' in cn else (cn+' animate-spin').strip()
                spin_n += 1
def walk_spin(o):
    if isinstance(o, dict):
        fix_spin(o)
        for x in o.values(): walk_spin(x)
    elif isinstance(o, list):
        for x in o: walk_spin(x)
walk_spin(form)
if spin_n: changed.append(f'⑨ ไอคอนกล่องรอเจน {spin_n} จุด → วงหมุนเหมือน overlay')

# ─────────────────────────────────────────────────────────────
# ⑩ 3 จุดที่พี่หมีเจอบนเครื่องจริง (2026-09-12)
fix_n = []

# ① ไอคอนหมุน "แกว่งเหมือนจุดศูนย์กลางเบี้ยว"
#    ราก: กล่องไอคอนไม่เป็นจัตุรัส — `textSize` ให้ line-height ของขนาดหนึ่ง แต่ `!text-[24px]` เปลี่ยนแค่ font-size
#         ⇒ กล่องสูงไม่เท่ากว้าง ⇒ หมุนรอบจุดกลางกล่องแล้วเห็นเป็นแกว่ง
#    🔑 การ์ดแดงในหน้าเดียวกันไม่เบี้ยว เพราะมี `leading-none flex items-center justify-center` อยู่แล้ว = เฉลยอยู่ในไฟล์เดียวกัน
def fix_spin_box(o):
    if o.get('el') != 'icon' or 'animate-spin' not in str(o.get('className', '')): return
    cn = str(o.get('className', ''))
    need = [c for c in ('leading-none', 'flex', 'items-center', 'justify-center') if c not in cn]
    if need:
        o['className'] = (cn + ' ' + ' '.join(need)).strip()
        fix_n.append('①')

# ② การ์ดแดง "คิดบทไม่สำเร็จ" บอกให้กด เริ่ม ทั้งที่ระบบยังทำงานอยู่
#    🔴 ผิดจริง: ตอนรันอยู่ ผู้ใช้กด เริ่ม ไม่ได้ (ปุ่มเป็น หยุดพัก) ⇒ บอกทางที่ทำตามไม่ได้ = แย่กว่าไม่บอก
#    ⇒ แยก 2 ถ้อยคำตามสถานะ: รันอยู่ = รายงานเฉย ๆ · หยุดแล้ว = ค่อยบอกวิธีทำต่อ
RUNNING = {"op": "or", "list": [{"op": "eq", "a": "{values.__runState}", "b": "running"},
                                {"op": "eq", "a": "{values.__runState}", "b": "cooldown"},
                                {"op": "eq", "a": "{values.__runState}", "b": "retrying"}]}
def fix_red(o):
    if o.get('el') != 'text': return
    v = o.get('value')
    if not (isinstance(v, dict) and 'คิดบทไม่สำเร็จ' in json.dumps(v, ensure_ascii=False)): return
    if v.get('op') == 'block': return          # ★แพตช์ไปแล้ว — ไม่งั้นรันซ้ำจะรายงานว่าเปลี่ยนทุกรอบ = เสียคุณสมบัติที่ใช้จับ drift
    cnt = {"op": "count", "from": "products", "where": "status=error"}
    o['value'] = {"op": "block", "sep": "", "parts": [
        {"value": {"op": "concat", "parts": ["คิดบทไม่สำเร็จ ", copy.deepcopy(cnt), " สินค้า"]}},
        {"when": copy.deepcopy(RUNNING), "value": " — ระบบกำลังทำสินค้าตัวที่เหลือต่ออยู่ ตัวที่พลาดกดคิดบทใหม่ได้ที่การ์ดข้างล่าง"},
        {"when": {"op": "not", "a": copy.deepcopy(RUNNING)},
         "value": " — กดปุ่มคิดบทใหม่ที่การ์ดสินค้าด้านล่าง หรือกดเริ่มอีกครั้งเพื่อเขียนใหม่เฉพาะตัวที่พลาด"},
    ]}
    fix_n.append('②')

# ③ การ์ดเหลือง "กำลังหยุด" — ไอคอนชิดบน + วงหมุนสื่อผิด (ตอนนี้คือ "รอ" ไม่ใช่ "กำลังทำ")
def fix_amber(o):
    kids = o.get('card')
    if not isinstance(kids, list): return
    if 'กำลังหยุด' not in json.dumps(o, ensure_ascii=False): return
    if 'items-start' in str(o.get('className', '')):
        o['className'] = str(o['className']).replace('items-start', 'items-center')   # ไอคอนอยู่กึ่งกลางแนวตั้งของการ์ด
        fix_n.append('③')
    for i, k in enumerate(kids):
        if isinstance(k, dict) and k.get('el') == 'spinner':
            # 🔑 สถานะนี้คือ "รอให้ของที่ค้างอยู่จบ" ไม่ใช่ "กำลังลงมือทำ" ⇒ วงหมุนสื่อผิด
            # 🪤 เลือก `pending` ไม่ใช่ `hourglass_top` เพราะยาม ⑲ ห้ามนาฬิกาทราย/พู่กันทั้ง config
            #    — และพอคิดตามจริง `pending` ตรงกว่าด้วย: นาฬิกาทรายบอกเป็นนัยว่า "รู้ว่าอีกนานเท่าไหร่" ซึ่งเราไม่รู้
            #    ★ไม่ผ่อนยามให้เข้าทางตัวเอง — ยามห้ามไอคอนนั้นทั้งไฟล์ ก็เลี่ยงไอคอนนั้น
            kids[i] = {"el": "icon", "icon": "pending", "textSize": "text-[18px]",
                       "className": "!text-amber-600 leading-none flex items-center justify-center animate-pulse shrink-0"}
            fix_n.append('③')

def walk_ui(o):
    if isinstance(o, dict):
        fix_spin_box(o); fix_red(o); fix_amber(o)
        for x in o.values(): walk_ui(x)
    elif isinstance(o, list):
        for x in o: walk_ui(x)
walk_ui(form)
if fix_n:
    from collections import Counter
    cc = Counter(fix_n)
    changed.append('⑩ ' + ' · '.join(f'{k}×{n}' for k, n in sorted(cc.items())) +
                   ' (ไอคอนหมุนไม่แกว่ง · การ์ดแดงไม่บอกให้กดปุ่มที่กดไม่ได้ · การ์ดเหลืองกึ่งกลาง+ไอคอนรอ)')

# ─────────────────────────────────────────────────────────────
# ⑪ แถบแดงตอน "ยังรันอยู่" ห้ามบอกให้กดปุ่มที่ตอนนั้นกดไม่ได้  (พี่หมีถาม LIVE-QA: "กดคิดบทใหม่ตอนไหน ตรงไหน")
#    ราก: `gen-button` ปิดตัวเองด้วย `itemBusy` ซึ่งอ่าน `on.busy` = ธงของทั้งรอบ (atoms-cases-a2.tsx · atoms-parts.tsx)
#      ⇒ ระหว่างรัน ปุ่ม "คิดบทใหม่" เป็นสีจาง กดไม่ติด แต่ข้อความบอกให้กด
#    🪤 นี่คือบั๊กตัวเดิมที่พี่หมีทักรอบแรก (ตอนนั้นข้อความบอกให้กด "เริ่ม") — ย้ายปุ่มแล้วแต่โรคไม่หาย
#    ★แก้ที่ "ข้อความ" ไม่ใช่ที่ engine — ปลดปุ่มให้กดได้ตอนรันเป็นการแตะจุดที่ใช้ร่วมกับปุ่ม gen ทุกตัวของทุกแอป
#      (engine มีทางเข้าคิวรออยู่แล้วที่ genGate แต่ปุ่มถูกปิดก่อน ⇒ ทางนั้นไม่มีวันถูกเรียก · เป็นหนี้ที่จดไว้)
# 🪤 ข้อความตอนรันอยู่ **ห้ามเอ่ยชื่อปุ่มเลย** ไม่ใช่แค่ห้ามสั่งให้กด —
#    เขียนว่า "รอจบรอบแล้วค่อยกดคิดบทใหม่" ยังกำกวม (ผู้ใช้เห็นชื่อปุ่มแล้วไปกด เจอปุ่มสีจาง)
#    และยามที่จะเฝ้าเรื่องนี้ แยก "กดตอนนี้" กับ "เดี๋ยวค่อยกด" ด้วยสตริงภาษาไทยไม่ได้จริง
#    ⇒ กฎที่ตรวจได้จริง: **ข้อความที่เอ่ยชื่อปุ่ม ต้องโผล่เฉพาะตอนที่ปุ่มนั้นกดได้**
OLD11 = [' — ระบบกำลังทำสินค้าตัวที่เหลือต่ออยู่ ตัวที่พลาดกดคิดบทใหม่ได้ที่การ์ดข้างล่าง',
         ' — ระบบกำลังทำสินค้าตัวที่เหลือต่ออยู่ รอรอบนี้จบก่อน แล้วค่อยกดคิดบทใหม่ที่การ์ดข้างล่าง']
NEW11 = ' — ระบบกำลังทำสินค้าตัวที่เหลือต่ออยู่ รอจนจบรอบก่อน แล้วค่อยแก้ตัวที่พลาดได้'
hit11 = []
def walk11(o):
    if isinstance(o, dict):
        if o.get('value') in OLD11:
            o['value'] = NEW11; hit11.append(1)
        for x in o.values(): walk11(x)
    elif isinstance(o, list):
        for x in o: walk11(x)
walk11(c['phases'])
if hit11:
    changed.append('⑪ แถบแดงตอนรันอยู่ → เลิกเอ่ยชื่อปุ่มที่ตอนนั้นกดไม่ได้')
_j11 = json.dumps(c, ensure_ascii=False)
for _o in OLD11:
    assert _o not in _j11, 'ยังมีข้อความเก่าตกค้าง'
assert NEW11 in json.dumps(c, ensure_ascii=False), 'ไม่พบข้อความใหม่ — โครงแถบแดงเปลี่ยนไปแล้ว ให้ไปดูก่อนแก้'

SRC.write_text(json.dumps(c, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'— {SRC.name} —')
print('\n'.join('  ✔ ' + x for x in changed) if changed else '  (ไม่มีอะไรเปลี่ยน — รันซ้ำแล้วนิ่ง)')
