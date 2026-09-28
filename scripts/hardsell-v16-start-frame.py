#!/usr/bin/env python3
# hardsell-v16-start-frame.py — เลิกใช้บอร์ด 4 ช่อง กลับไปวิธี hardsell เก่า (พี่หมีสั่ง 2026-09-28):
#   "ไม่ต้องทำบอร์ด ทำแค่ภาพ start frame · เจนภาพเฟรมแรกเอามาขยับ · ถ้าจะต่อฉาก แคปภาพเฟรมจบมาต่อ"
#
# ① mnBoard (slot `board` ชื่อเดิม — UI/segments/ยามผูกอยู่) = ภาพนิ่ง 1 ภาพ 9:16 = เฟรมแรกของคลิป (ฉาก 1 + สินค้า + พรีเซนเตอร์)
#    ข้อความ (ถ้าเปิด): วาดหัวข้อ ov1 ลงในภาพนี้เลย = วิธีแอปเก่า (H1 บนภาพ) — โมเดลภาพเขียนไทยถูก (บอร์ดทดสอบ A อ่านได้ทุกคำ)
#    ส่วน Veo วาดไทยเพี้ยนทุกฉาก (ทดสอบ A: "สักลัลเช้งเกผีเมี") ⇒ วิดีโอสั่งให้ "คงข้อความเดิม ห้ามเขียนใหม่"
# ② mnVideo: เลิก refs (บอร์ด+สินค้า+หน้า) → startFrame = {item.slots.board} (frame-to-video แบบแอปเก่า)
#    ⚠️ engine ทิ้ง refs ทั้งชุดเมื่อมี startFrame ⇒ ความตรงของสินค้า/หน้า มาจากภาพเฟรมแรก (ซึ่งสร้างจากรูปสินค้า+หน้าที่แนบ)
#    PRODUCT LOCK อ้าง "first frame" แทน "attached photo" · ตัดบล็อกล็อกแผ่นบอร์ด + คำตระกูลแผ่นบอร์ดใน negative (ไม่มีแผ่นบอร์ดแล้ว)
# ③ ข้อความบนจอในวิดีโอ (mnVideo+mnVideo2): เลิกสั่งให้ Veo วาดข้อความรายฉาก → คงเฉพาะหัวข้อที่อยู่ในเฟรมแรก
# ④ ถ้อยคำ "สตอรีบอร์ด" บนจอ/log → "ภาพ"
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'เฟรมแรกของคลิปโฆษณาสินค้า'


def rep_str(n, old, new):
    c = 0
    if isinstance(n, dict):
        for k, v in n.items():
            if isinstance(v, str) and old in v: n[k] = v.replace(old, new); c += 1
            else: c += rep_str(v, old, new)
    elif isinstance(n, list):
        for i, v in enumerate(n):
            if isinstance(v, str) and old in v: n[i] = v.replace(old, new); c += 1
            else: c += rep_str(v, old, new)
    return c


def main():
    src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json'))
    cfg = json.load(open(src, encoding='utf-8'))
    if MARK in json.dumps(cfg, ensure_ascii=False):
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร'); return
    ops = {o['id']: o for o in cfg['ops']}
    B, V1, V2 = ops['mnBoard'], ops['mnVideo'], ops['mnVideo2']
    bp = B['prompt']['parts']

    # ── ① ภาพเฟรมแรก — หยิบชิ้นเดิมที่ใช้ได้มาใช้ต่อ (lead · ฉากเทมเพลต · อารมณ์ · ล็อกสินค้า · พรีเซนเตอร์ · Cast · ปิดท้าย)
    def find(pred, what):
        h = [x for x in bp if pred(x)]; assert len(h) == 1, '%s เจอ %d' % (what, len(h)); return h[0]
    lk = lambda t: find(lambda x: isinstance(x, dict) and x.get('op') == 'lookup' and x.get('table') == t, t)
    lock = find(lambda x: isinstance(x, str) and 'กติกาเหล็กสินค้า' in x, 'ล็อกสินค้า')
    cast = find(lambda x: isinstance(x, dict) and 'พรีเซนเตอร์ตามที่ผู้ใช้ระบุ' in json.dumps(x, ensure_ascii=False), 'Cast')
    lock = lock.replace('สินค้าทุกช่องต้องเป็น', 'สินค้าในภาพต้องเป็น').replace('ห้ามมีเด็กหรือทารกทุกช่อง', 'ห้ามมีเด็กหรือทารกในภาพ')
    assert 'ทุกช่อง' not in lock
    txt_style = {'op': 'lookup', 'table': 'txtStyle', 'key': '{values.textStyleId}', 'fallback': ''}
    text_block = {'op': 'block', 'sep': '', 'parts': [
        {'when': 'values.svTextOn!=ไม่มีข้อความ', 'value': {'op': 'concat', 'parts': [
            '\n\nข้อความบนภาพ (หัวคลิปสไตล์ TikTok วางบนสุดของเฟรม ไม่บังหน้าและสินค้า): "{item.ov1}" · สไตล์: ', txt_style,
            ' · บรรทัดเดียว สะกดถูกทุกตัว คมชัด ห้าม emoji ห้ามพิมพ์ชื่อสไตล์ลงภาพ · นอกจากข้อความนี้และฉลากจริงบนสินค้า '
            'ห้ามมีตัวหนังสืออื่น — ห้ามราคา สัญลักษณ์เงิน % ส่วนลด ป้ายร้าน โปสเตอร์ สติกเกอร์ โลโก้ ตัวหนังสือบนเสื้อผ้า']}},
        {'when': 'values.svTextOn=ไม่มีข้อความ',
         'value': '\n\nไม่มีข้อความบนภาพ: ภาพต้องสะอาด ห้ามตัวหนังสือ ป้าย ซับไตเติล หรือ doodle (ยกเว้นฉลากจริงบนสินค้า)'}]}
    B['prompt']['parts'] = [
        'สร้างภาพนิ่ง 1 ภาพ แนวตั้ง 9:16 = เฟรมแรกของคลิปโฆษณาสินค้า "{item.productName}" จากภาพที่แนบ (ภาพนี้จะถูกนำไปขยับเป็นวิดีโอต่อ)\n'
        'ภาพเดี่ยวเต็มเฟรมเท่านั้น — ห้ามแบ่งช่อง ห้ามทำเป็นสตอรีบอร์ด คอลลาจ ตาราง หรือกรอบหลายภาพ\n\n',
        lk('tplImgLead'),
        'ฉากของภาพนี้ (ฉากแรกของคลิป): {item.s1th} · มุมกล้อง: {item.cam1}\nสไตล์ภาพรวม (ตามเทมเพลตที่ผู้ใช้เลือก): ',
        lk('tplScene'), ' · อารมณ์และสีหน้า: ', lk('toneVisual'),
        '\nองค์ประกอบ 9:16: ตัวแบบอยู่ค่อนลงล่างเล็กน้อย เว้นที่ว่างด้านบน · ถือสินค้าใกล้กล้องให้เห็นชัด ไม่ถูกบัง โฟกัสคม',
        lock, text_block,
        '\n\nพรีเซนเตอร์: ', lk('tplCharMode'), ' — ', lk('charBoardT'), cast,
        '\n\nปิดท้ายภาพด้วย: "', lk('tplImgClose'), '"']
    B['logRun'] = '[{item.productName} คลิป {item.clipIndex}] กำลังวาดภาพเฟรมแรก'
    B['logDone'] = '[{item.productName} คลิป {item.clipIndex}] ภาพเฟรมแรกเสร็จแล้ว'
    # ตาราง charBoardT เขียนแบบหลายช่อง ("ทุกช่อง") → ภาพเดียว
    n_cb = (rep_str(cfg['lookups']['charBoardT'], 'ทุกช่อง', 'ในภาพ') + rep_str(cfg['lookups']['charBoardT'], 'ช่องสาธิต', 'ฉากสาธิต')
            + rep_str(cfg['lookups']['charBoardT'], 'ในภาพของแผงนี้', 'ในภาพนี้'))
    assert not any(w in v for v in cfg['lookups']['charBoardT'].values() for w in ('แผง', 'ช่อง')), 'charBoardT ยังมีคำแบบหลายช่อง'

    # ── ② mnVideo = frame-to-video จากภาพเฟรมแรก
    assert 'refs' in V1 and 'startFrame' not in V1
    del V1['refs']
    V1['startFrame'] = '{item.slots.board}'
    vp = V1['prompt']['parts']
    PL_A = 'the product is the exact object in the attached photo'
    assert rep_str(vp, PL_A, 'the product is the exact object in the first frame') == 1
    SHEET = ("\n\nReference image 1 is this clip's storyboard sheet: follow each panel's framing, product placement and colours, "
             "but the sheet itself must NEVER appear on screen, not even one frame. Labels and timings are instructions only.")
    i = [k for k, x in enumerate(vp) if x == SHEET]; assert len(i) == 1, 'บล็อกแผ่นบอร์ด %d' % len(i)
    vp[i[0]] = ('\n\nThe first frame is given: animate forward from it — the same person, outfit, place, light and product; '
                'no cut, no new layout, no split screen.')
    assert rep_str(vp, 'split screen, storyboard sheet, line art, sketch, paper, panel border, grid, ', 'split screen, ') == 1

    # ── ③ ข้อความบนจอในวิดีโอ: คงหัวข้อที่อยู่ในเฟรมแรก ห้าม Veo วาดใหม่
    KEEP = ("\n\nOn-screen text: keep ONLY the Thai headline already in the first frame, unchanged and in the same place for the whole clip, "
            "plus text printed on the packaging; never add, change or animate any other text.")
    for oid, o in (('mnVideo', V1), ('mnVideo2', V2)):
        parts = o['prompt']['parts']
        # บล็อก svTextOn: เปลี่ยน value ของกิ่ง "มีข้อความ" · กิ่ง "ไม่มีข้อความ" คงเดิม
        hit = 0
        for x in parts:
            if isinstance(x, dict) and x.get('op') == 'block':
                for br in x.get('parts', []):
                    if isinstance(br, dict) and br.get('when') == 'values.svTextOn!=ไม่มีข้อความ' and "ONLY each scene's quoted Thai overlay" in json.dumps(br, ensure_ascii=False):
                        br['value'] = KEEP; hit += 1
        assert hit == 1, '%s: กฎข้อความ (มีข้อความ) เจอ %d' % (oid, hit)
        # ลบ " Thai overlay: \"{item.ovN}\"" รายฉาก (บล็อกที่มีแต่กิ่งนั้น)
        before = len(parts)
        # 🪤 เทียบกับสตริง value ตรง ๆ — รอบแรกผมค้นใน json.dumps แล้วเจอ 0 เพราะฟันหนูถูก escape เป็น \\"
        o['prompt']['parts'] = [x for x in parts if not (isinstance(x, dict) and x.get('op') == 'block' and len(x.get('parts', [])) == 1
                                and isinstance(x['parts'][0], dict) and 'Thai overlay: "{item.ov' in str(x['parts'][0].get('value', '')))]
        assert before - len(o['prompt']['parts']) == 4, '%s: overlay รายฉากลบได้ %d' % (oid, before - len(o['prompt']['parts']))

    # ── ④ ถ้อยคำบนจอ/log
    n_ui = rep_str(cfg['phases'], 'รอคิววาดสตอรีบอร์ด', 'รอคิววาดภาพ') + rep_str(cfg['phases'], 'กำลังวาดสตอรีบอร์ด', 'กำลังวาดภาพ')
    ops['mnQueue']['logDone'] = ops['mnQueue']['logDone'].replace('พร้อมวาดสตอรีบอร์ด', 'พร้อมวาดภาพเฟรมแรก')
    n_br = rep_str(cfg['brain'], 'สำหรับแสดงในสตอรีบอร์ด', 'สำหรับแสดงในรายการฉาก')

    # ── ยาม
    s = json.dumps(cfg, ensure_ascii=False)
    assert 'storyboard sheet' not in s and "quoted Thai overlay" not in s and 'Thai overlay: \\"{item.ov' not in s
    assert json.dumps(V1['prompt'], ensure_ascii=False).count('first frame') >= 2
    assert V2.get('startFrame') == '{item.slots.video}' and V2.get('tailTrim') == 1
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v16 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① mnBoard = ภาพเฟรมแรก 1 ภาพ (หัวข้อ ov1 วาดในภาพ) · charBoardT แก้คำหลายช่อง %d จุด' % n_cb)
    print('   ② mnVideo = startFrame จากภาพ (ตัด refs + บล็อกแผ่นบอร์ด) · ③ วิดีโอคงข้อความเดิม ไม่วาดใหม่ (2 op · ลบ overlay รายฉาก 8)')
    print('   ④ UI %d · brain %d · log ภาพเฟรมแรก' % (n_ui, n_br))


main()
