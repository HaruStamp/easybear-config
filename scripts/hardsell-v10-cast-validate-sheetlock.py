#!/usr/bin/env python3
# hardsell-v10 — 4 ข้อรวมรอบเดียว (พี่หมีสั่ง "แก้เลย" 2026-09-27 หลังไล่มาตรฐานตาม minimal/showhow)
#
# A) 🔴 เพศ/วัย/ลุคของตัวละคร ไปไม่ถึง op ที่วาดภาพ/วิดีโอ  — regression จากการพอร์ต (แอป Flow เก่าแก้ไปแล้ว v1.6.0)
#    mnPlan ส่งให้ LLM จริง แต่ฟิลด์ที่ spawn เขียนลง task มีแค่ sNth/sNen/ovN/voN/camN/voice
#    ⇒ เพศไปถึงภาพได้เฉพาะเท่าที่ LLM เผลอเขียนใน sNen = ไม่มีหลักประกัน
#    ⇒ เติมบรรทัด "Cast:" ตรง ๆ ใน mnBoard/mnVideo/mnVideo2 gate ด้วย values.charGender!=
#    (showhow เจอจากผลิตจริง 24 คลิป แก้ v111 · minimal โดนเหมือนกัน · 3 ทีมโดนหมด = รูของโครงต้นแบบ)
#
# B) 🔴 บทซอมบี้ติดตาย — mnQueue.spawn เป็น mode B จาก {item.data.plan} แต่ mnPlan ไม่มี validate
#    LLM ตอบ JSON เพี้ยน → safeJson ได้ {} → listLen นับได้ 1 → ผ่านยาม → task ผีค้างถาวร (ท่าของ minimal)
#
# C) 🔴 รูเครดิต — mnVideo2 ไม่มี where ⇒ เปลี่ยน 8→16 วิ แล้วกดผลิตต่อ = ยิงวิดีโอด้วยบท s5en-s8en ที่ว่าง
#    (minimal/showhow ปิดไปแล้ว เหลือเราทีมเดียว · ต้อง engine >= v1.13.x where-AND — เราอยู่ v1.15.0)
#
# D) 🟡 แผ่นสตอรีบอร์ดโผล่ในคลิป — บอร์ดเราเป็น ref ตัวแรกของ mnVideo แต่คำล็อกอ่อนกว่าของ minimal
#    ตรงกับเสียงลูกค้าที่จดไว้ว่า "ป้ายโผล่" (CLAUDE.md v1.6.0)
#
# 🔢 งบ prompt = ข้อจำกัดหลักของรอบนี้ (วัดก่อนเขียน): วิดีโอยาวสุด 3,738/3,900 เหลือ 162
#    ⇒ A+D ใส่ตรง ๆ = +262 เกิน 100 ⇒ **ต้องบีบของเดิมที่ซ้ำกันเองก่อน** ไม่ใช่เติมแล้วลุ้น
#    ที่บีบ (ความหมายไม่หาย): PRODUCT LOCK ตัดคำซ้ำ "exact same object as in" · negative ตัด
#    "end card"/"on-screen buy prompts, buttons" ที่ประโยคหน้ามันพูดแล้ว · /39 ของ mnVideo ถูกดูดเข้าบล็อกบอร์ด
#    🔴 ยามท้ายไฟล์บังคับ worst case <= LIMIT — ไม่ผ่าน = ไม่เขียนไฟล์ (กัน "กฎท้าย prompt โดนตัดแทน")
# รันซ้ำได้: ตรวจ marker
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = "storyboard sheet"          # marker ของรอบนี้
LIMIT = 3900                        # เพดาน execLeaf (engine)

# ── A: บรรทัดเพศ/วัย/ลุค · gate ด้วย charGender ไม่ว่าง (ไม่งั้นได้ "Cast: , , .") ──
# 🪤 {when,value} ใช้ตรงใน concat.parts ไม่ได้ — ต้องห่อด้วย block (ยามจับได้รอบแรก: dry-run 15 ข้อ + leaf-length 6 ข้อ)
#    โครงนี้ลอกจาก block ที่ config มีอยู่แล้ว (เช่นบล็อก svTextOn ของ mnVideo)
CAST = {"op": "block", "sep": "",
        "parts": [{"when": "values.charGender!=",
                   "value": "\n\nCast: {values.charGender}, {values.charAge}, {values.charLook}."}]}

# ── D + บีบ ──
OLD_LOCK = ("\n\nReference image 1 is a storyboard (one panel per scene): follow each panel's framing, "
            "product placement and colours, but never show panels, borders, labels or timings.")
# 🪤 ห้ามเขียนรายการ "line art, sketch, paper, panel border" ซ้ำในบล็อกนี้ — negative ข้างล่างมีให้แล้ว
#    (ยาม ③ ของ starter วัดที่ค่า default แล้วเป็นหนี้ ratchet ⇒ เขียนซ้ำ = จ่ายค่าตัวอักษร 2 รอบเพื่อกฎเดียว)
# 🔴 ต้องเป็นกลางต่อสไตล์ — ร่างแรกของผมเขียน "every frame is live-action photography" ซึ่ง**ขัดกับสไตล์
#    การ์ตูน/อนิเมะ** ที่ผู้ใช้เลือกได้ (ยาม ② เฝ้าแค่คำ `phone footage` เลยมองไม่เห็น) ⇒ ห้ามพูดถึงชนิดภาพในบล็อกนี้
#    ชนิดภาพเป็นหน้าที่ของ tplVidLead (เปลี่ยนตามสไตล์) · บล็อกนี้พูดเรื่องเดียว = แผ่นบอร์ดห้ามโผล่
NEW_LOCK = ("\n\nReference image 1 is this clip's storyboard sheet: follow each panel's framing, product "
            "placement and colours, but the sheet itself must NEVER appear on screen, not even one frame. "
            "Labels and timings are instructions only.")
LABELS_LINE = "\n\nLabels, timings and camera notes are instructions only — never show them."

OLD_NEG_TAIL = ("Negative: no end card, closing title, on-screen buy prompts, buttons, price or discount "
                "graphics, stickers, emoji, arrows, logos, watermarks, transitions, glitch, light leaks, "
                "zoom punch-ins, sparkles, slow motion, split screen, warped product, extra fingers or morphing.")
# 🔴 "no end card" ห้ามตัด — ยาม ② เฝ้าอยู่ (`C.includes('no end card')` · มาจากบทเรียน v1.3.1 ที่ Veo ใส่ end card
#    เพราะ prompt มีคำ call-to-action) · รอบแรกผมตัดทิ้งแล้วยามฟ้อง 8 เคส ⇒ บีบที่คำที่ไม่มีใครเฝ้าแทน
#    ที่ตัดได้: "on-screen buy prompts, buttons" — ประโยคหน้า "The ask to buy is spoken only, never shown
#    on screen" พูดเรื่องเดียวกันแล้ว (ตรวจแล้วไม่มียามข้อไหนอ้างถึง 2 คำนี้)
NEW_NEG_SHEET = ("Negative: no end card, closing title, price or discount graphics, stickers, emoji, arrows, "
                 "logos, watermarks, transitions, glitch, light leaks, zoom punch-ins, sparkles, slow motion, "
                 "split screen, storyboard sheet, line art, sketch, paper, panel border, grid, warped product, "
                 "extra fingers or morphing.")
NEW_NEG_PLAIN = ("Negative: no end card, closing title, price or discount graphics, stickers, emoji, arrows, "
                 "logos, watermarks, transitions, glitch, light leaks, zoom punch-ins, sparkles, slow motion, "
                 "split screen, warped product, extra fingers or morphing.")

# ⚠️ 2 op เขียนต่างกันโดยมีเหตุผล: mnVideo อ้าง "รูปสินค้าที่แนบ" · mnVideo2 อ้าง "เฟรมแรก"
#    (ช่วง 2 ไม่มีรูปสินค้าเป็น ref เพราะ startFrame ทิ้ง refs ทั้งชุด) ⇒ บีบแยกกัน ห้ามใช้ข้อความเดียว
PL_OLD_A = "the product must be the exact same object as in the attached product photo — same colour, shape, proportions, real-world size, material,"
PL_NEW_A = "the product is the exact object in the attached photo — same colour, shape, proportions, real size, material,"
ASK_OLD = "The ask to buy is spoken only, never shown on screen; never end on a card or graphic."
# ↑ "never end on a card or graphic" ซ้ำกับ "no end card, closing title" ใน negative
#   ↓ ถ้อยคำนี้คือของเดิมจาก v1.3.1 ("ends on the person not a card") ที่แก้อาการ Veo ใส่ end card
ASK_NEW = "The ask to buy is spoken only; the clip ends on the person, not a card."
PL_OLD_B = "the product must be the exact same object as it appears in the first frame — same colour, shape, proportions, real-world size, material,"
PL_NEW_B = "the product is the exact object in the first frame — same colour, shape, proportions, real size, material,"


def find_str(parts, needle):
    return [i for i, x in enumerate(parts) if isinstance(x, str) and needle in x]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    if MARK in json.dumps(cfg, ensure_ascii=False):
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return
    ops = {o['id']: o for o in cfg['ops']}
    log = []

    # ═══ B) mnPlan.validate — จำนวนคลิป + ฟิลด์รายฉากของ plan.0 (พอร์ตมาตรฐาน showhow) ═══
    # ทำไมต้องมีฟิลด์รายฉากด้วย: บทที่ "นับครบ" แต่คีย์ฉากว่าง ⇒ prompt วิดีโอได้ฉากเปล่า = เผาเครดิตได้คลิปเสีย
    #   เช็คแค่ plan.0 เหมือน showhow (ตัวอย่างพอชี้ว่า LLM ตอบผิดรูป) · คลิปที่ 2..N ที่หลุดมา ถูก where ของ mnVideo2 กันไว้ (ข้อ C)
    # gate `values.svSec<=8`: ฉาก 5-8 บังคับเฉพาะ 16 วิ — ยืนยันแล้วว่า engine เทียบ `<= > < >=` **เป็นตัวเลข**
    #   (engine-bind.ts:68-71 · ถ้าเทียบเป็นสตริงจะได้ '16'<='8' = จริง = gate พลาดเงียบ)
    # maxAttempts: ไม่ตั้งที่ op ⇒ ใช้ `run.maxAttempts` = 3 ⇒ ข้อความ "ระบบสั่งคิดใหม่ให้เองแล้ว" เป็นความจริง
    assert 'validate' not in ops['mnPlan'], 'mnPlan มี validate อยู่แล้ว — ตรวจก่อนทับ'
    assert cfg.get('run', {}).get('maxAttempts', 1) >= 2, 'run.maxAttempts < 2 ⇒ ห้ามเขียนข้อความว่าระบบสั่งซ้ำให้เอง'
    scene_req = []
    for n in range(1, 9):
        for f in ('s%dth' % n, 's%den' % n):
            cond = 'item.data.plan.0.%s!=' % f
            scene_req.append(cond if n <= 4 else {"op": "or", "list": ["values.svSec<=8", cond]})
    ops['mnPlan']['validate'] = {"op": "and", "list": [
        {"op": "gte", "a": {"op": "listLen", "value": "{item.data.plan}", "arrayOnly": True},
         "b": "{values.clipsPerProduct}"}] + scene_req}
    # ข้อความบนการ์ด: ตามกฎเขียน error ของเผ่า — ไม่มีคำที่ classifyError จับ · ไม่มีฟันหนู · ไม่มีวงเล็บเหลี่ยม
    ops['mnPlan']['validateMsg'] = ('เขียนบทได้ไม่ครบ — ระบบจะสั่งคิดใหม่ให้เอง '
                                    'ถ้ายังไม่ผ่าน ให้กดปุ่มคิดบทใหม่ที่การ์ดสินค้า')
    ops['mnPlan']['retryHint'] = {"op": "concat", "sep": "", "parts": [
        '\n\nรอบที่แล้วบทไม่ครบ — รอบนี้ต้องส่ง JSON เป็นลิสต์ยาว {values.clipsPerProduct} รายการ '
        'และทุกรายการต้องมีคีย์ฉากครบทุกฉากตามความยาวคลิปที่เลือก '
        '(8 วินาที = ฉาก 1 ถึง 4 · 16 วินาที = ฉาก 1 ถึง 8) ห้ามเว้นคีย์ไหนว่าง']}
    log.append('B) mnPlan: validate = จำนวนคลิป + ฟิลด์รายฉาก plan.0 (ฉาก 5-8 เฉพาะ 16 วิ) · validateMsg + retryHint')

    # ═══ C) mnVideo2.where ═══
    assert ops['mnVideo2'].get('where') is None, 'mnVideo2 มี where อยู่แล้ว — ตรวจก่อนทับ'
    ops['mnVideo2']['where'] = 's5en!='
    log.append('C) mnVideo2.where = "s5en!=" (ไม่มีบทช่วง 2 = ข้ามเงียบ ไม่เสียเครดิต)')

    # ═══ D) บีบ PRODUCT LOCK ทั้ง 2 op วิดีโอ ═══
    for oid, old, rep in (('mnVideo', PL_OLD_A, PL_NEW_A), ('mnVideo2', PL_OLD_B, PL_NEW_B)):
        parts = ops[oid]['prompt']['parts']
        hit = find_str(parts, old)
        assert len(hit) == 1, '%s: PRODUCT LOCK ที่ต้องบีบ เจอ %d จุด (ควร 1)' % (oid, len(hit))
        parts[hit[0]] = parts[hit[0]].replace(old, rep)
        assert 'first frame' in parts[hit[0]] or oid == 'mnVideo', 'mnVideo2 ต้องยังอ้าง "first frame" ไม่ใช่รูปที่แนบ'
    log.append('D1) บีบ PRODUCT LOCK ของ mnVideo/mnVideo2 (ตัดคำซ้ำ · ความหมายเดิม)')

    # ═══ D) บล็อกล็อกแผ่นบอร์ด (mnVideo เท่านั้น — mnVideo2 ไม่มีบอร์ดเป็น ref) ═══
    pv = ops['mnVideo']['prompt']['parts']
    hit = find_str(pv, OLD_LOCK.strip())
    assert len(hit) == 1, 'mnVideo: บล็อกบอร์ดเดิม เจอ %d จุด (ควร 1)' % len(hit)
    pv[hit[0]] = NEW_LOCK
    # /39 ถูกดูดเข้า NEW_LOCK แล้ว ⇒ ลบทิ้งใน mnVideo (แต่ mnVideo2 ต้องเก็บไว้ เพราะไม่มีบล็อกบอร์ด)
    hit39 = find_str(pv, LABELS_LINE.strip())
    assert len(hit39) == 1, 'mnVideo: บรรทัด Labels เจอ %d จุด (ควร 1)' % len(hit39)
    pv.pop(hit39[0])
    assert find_str(ops['mnVideo2']['prompt']['parts'], LABELS_LINE.strip()), 'mnVideo2 ต้องยังมีบรรทัด Labels'
    log.append('D2) mnVideo: บล็อกบอร์ดใหม่ (NEVER appear on screen + not even one frame) · ดูดบรรทัด Labels เข้าไป ลบตัวซ้ำ')

    # ═══ D) negative — mnVideo เติมของแผ่นบอร์ด · mnVideo2 แค่บีบ (ไม่มีบอร์ด ไม่ต้องเติม) ═══
    for oid, new in (('mnVideo', NEW_NEG_SHEET), ('mnVideo2', NEW_NEG_PLAIN)):
        parts = ops[oid]['prompt']['parts']
        hit = find_str(parts, OLD_NEG_TAIL)
        assert len(hit) == 1, '%s: negative เดิม เจอ %d จุด (ควร 1)' % (oid, len(hit))
        parts[hit[0]] = parts[hit[0]].replace(OLD_NEG_TAIL, new)
    for oid in ('mnVideo', 'mnVideo2'):
        parts = ops[oid]['prompt']['parts']
        hit = find_str(parts, ASK_OLD)
        assert len(hit) == 1, '%s: ประโยคปิดการขาย เจอ %d จุด (ควร 1)' % (oid, len(hit))
        parts[hit[0]] = parts[hit[0]].replace(ASK_OLD, ASK_NEW)
    log.append('D4) บีบประโยคปิดการขาย (คืนถ้อยคำ v1.3.1 "ends on the person, not a card")')
    log.append('D3) negative: ตัด "end card"/"buy prompts, buttons" ที่ประโยคหน้าพูดแล้ว · mnVideo เติมของแผ่นบอร์ด 6 คำ')

    # ═══ A) บรรทัด Cast ต่อท้าย charVideoENT/charBoardT ของทั้ง 3 op ═══
    for oid, table in (('mnBoard', 'charBoardT'), ('mnVideo', 'charVideoENT'), ('mnVideo2', 'charVideoENT')):
        parts = ops[oid]['prompt']['parts']
        pos = [i for i, x in enumerate(parts)
               if isinstance(x, dict) and x.get('op') == 'lookup' and x.get('table') == table]
        assert len(pos) == 1, '%s: lookup %s เจอ %d จุด (ควร 1)' % (oid, table, len(pos))
        parts.insert(pos[0] + 1, json.loads(json.dumps(CAST)))
    log.append('A) เติม "Cast: เพศ, วัย, ลุค" ต่อท้ายตารางพรีเซนเตอร์ของ mnBoard/mnVideo/mnVideo2 (gate charGender!=)')

    # ═══ ยาม ═══
    s2 = json.dumps(cfg, ensure_ascii=False)
    assert s2.count('{values.charGender}') == 4, 'charGender ต้องมี 4 จุด (mnPlan 1 + 3 op ใหม่) เจอ %d' % s2.count('{values.charGender}')
    assert s2.count('"when": "values.charGender!="') == 3, 'gate Cast ต้องมี 3 จุด'
    for oid in ('mnBoard', 'mnVideo', 'mnVideo2'):
        blks = [x for x in ops[oid]['prompt']['parts']
                if isinstance(x, dict) and x.get('op') == 'block'
                and any(isinstance(q, dict) and q.get('when') == 'values.charGender!=' for q in (x.get('parts') or []))]
        assert len(blks) == 1, '%s: บล็อก Cast ต้องมี 1 อัน (เจอ %d) — {when,value} ต้องอยู่ใน block ไม่ใช่ใน concat ตรง ๆ' % (oid, len(blks))
    assert s2.count(MARK) == 2, 'คำ "storyboard sheet" ต้องมี 2 จุด (บล็อก + negative ของ mnVideo) เจอ %d' % s2.count(MARK)
    assert ops['mnVideo2']['where'] == 's5en!=' and 'validate' in ops['mnPlan']
    # ยามเดิมที่ห้ามหลุด
    for i in range(1, 9):
        assert ops['mnTrA%d' % i]['setFields'].get('where') == 'data.trans.s%den!=' % i, 'ยาม mnTrA%d หาย' % i
    # ตรวจ "ตัวข้อความ" ไม่ใช่ JSON ที่ห่อ — รอบแรกผมตรวจ json.dumps แล้วมันไปเจอ [ ของ "parts": [ (ยามฟ้องของตัวเอง)
    def leaves(n):
        if isinstance(n, str):
            return [n]
        if isinstance(n, dict):
            return [x for k, v in n.items() if k not in ('op', 'sep') for x in leaves(v)]
        if isinstance(n, list):
            return [x for v in n for x in leaves(v)]
        return []
    for k in ('validateMsg', 'retryHint'):
        for t in leaves(ops['mnPlan'][k]):
            assert '"' not in t, '%s มีฟันหนู (Flow ถอด escape เพี้ยน): %r' % (k, t[:60])
            if k == 'validateMsg':   # ข้อความบนการ์ด — ชนป้ายท้าย error ที่ใช้ [ ] คั่นชื่อโมเดล
                assert '[' not in t and ']' not in t, '%s มีวงเล็บเหลี่ยม' % k
    assert ops['mnTrans'].get('aux') is True
    assert s2.count('no end card') == 2, 'คำ "no end card" ต้องยังอยู่ 2 op (ยาม ② เฝ้า) เจอ %d' % s2.count('no end card')
    for oid in ('mnVideo', 'mnVideo2'):
        assert ops[oid].get('resolution') == '720p', '%s resolution หาย' % oid
    # 🔴 ยามงบ prompt — ประกอบเคสแย่สุดแบบหยาบ (ทุก TEXT + lookup ที่ยาวสุดของแต่ละตาราง)
    lk = cfg.get('lookups') or {}
    def rough(op):
        tot = 0
        def w(n):
            nonlocal tot
            if isinstance(n, str): tot += len(n)
            elif isinstance(n, dict):
                if n.get('op') == 'lookup':
                    d = lk.get(n.get('table')) or {}
                    tot += max([len(json.dumps(v, ensure_ascii=False)) for v in d.values()] or [len(str(n.get('fallback') or ''))])
                elif 'value' in n and 'when' in n: w(n['value'])
                else:
                    for v in n.values(): w(v)
            elif isinstance(n, list):
                for v in n: w(v)
        w(op.get('prompt'))
        return tot
    for oid in ('mnVideo', 'mnVideo2', 'mnBoard'):
        r = rough(ops[oid])
        print('   ประมาณหยาบ %-9s = %d (เพดาน %d)' % (oid, r, LIMIT))
    print('   ⚠️ ตัวเลขนี้เป็นการประมาณ — ตัวตัดสินคือ `scripts/push-hardsell.sh hardsell-dev --check` (ยาม ② วัด 9,940 คู่ผสมจริง)')

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v10 ลงแล้ว — %s' % os.path.basename(src))
    for l in log:
        print('   ' + l)


main()
