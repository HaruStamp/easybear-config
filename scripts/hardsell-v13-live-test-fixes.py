#!/usr/bin/env python3
# hardsell-v13-live-test-fixes.py — แก้ 6 เรื่องที่เจอจากการให้ AI เขียนบทจริงบนแอป (รอบ 22 · พี่หมีสั่ง "แก้ให้เรียบร้อย" 2026-09-28)
#   ยามเดิมทุกตัวตรวจ "คำสั่ง" จึงมองไม่เห็นเรื่องเหล่านี้ — เจอเพราะดู "คำตอบของ AI" + prompt ที่ประกอบจากบทจริง
#
# A. CTA ตายตัว "ฉาก 5" + "คำลงท้ายแนะนำที่ vo5" (ติดมาจากโครง minimal) — hardsell 8 วิ ไม่มีฉาก 5 · 16 วิ ปิดการขายที่ฉาก 8
#    ของจริง: 16 วิ AI ใส่ "รีบกดตะกร้าเลย" กลางคลิป ⇒ เปลี่ยนเป็น "ฉากปิดการขาย (ฉากสุดท้าย)" ใช้ได้ทั้ง 2 ความยาว
# B. ราคา/โปร/คำชวนซื้อขึ้นเป็นข้อความบนจอ แต่ negative วิดีโอห้าม "price or discount graphics" = สั่งขัดกันเอง
#    ⇒ ยึดตามแอปเดิม (PRICE_LOCK: ห้ามราคาบนจอ) — พูดในบทพากย์เท่านั้น · 🔁 ถ้าพี่หมีอยากให้ขึ้นจอ = ถอด 2 ประโยคนี้ + ลบ "price or discount graphics"
# C. มุมกล้องที่ AI เลือก ถูกแปลเป็น "…on the product" เสมอ แม้ฉากนั้นเป็นหน้าคน ⇒ ตัดคำชี้วัตถุ 3 ค่าที่ใช้กับคนได้ (ฉากบอกเองว่าถ่ายอะไร)
# D. Cast เป็นภาษาไทยกลาง prompt อังกฤษ + ขึ้นในเทมเพลตที่ไม่มีคน ⇒ วิดีโอเป็นอังกฤษ · บอร์ดเป็นไทย (prompt บอร์ดเป็นไทย) · gate เฉพาะเทมเพลตที่มีคน
#    + ไม่ทิ้ง ", ," เมื่อผู้ใช้เว้นวัย/ลุค
# E. `..` ซ้อนท้ายฉาก — sNen ของ AI จบด้วยจุดอยู่แล้ว แต่ template เติมจุดซ้ำ ⇒ template ไม่เติม + บอก AI ให้จบด้วยจุดเสมอ
# F. สาย 3D ขัดกันทั้งเส้น: ฉากบอก "ตัวการ์ตูน 3D แสดงท่า" แต่ บท/บอร์ด/วิดีโอ บอก "ไม่มีคน สินค้าเป็นพระเอกล้วน"
#    ⇒ ไม่มีคนจริง แต่ตัวการ์ตูนตามเทมเพลตเป็นตัวเดินเรื่อง (ตัวเดิมทุกฉาก) · สินค้าจริงยังเป็นจุดโฟกัส
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'ฉากปิดการขาย (ฉากสุดท้าย)'


def strings(n, fn):
    """เรียก fn กับทุกสตริงใน n (แก้ในที่) · คืนจำนวนสตริงที่เปลี่ยน"""
    c = 0
    if isinstance(n, dict):
        for k, v in list(n.items()):
            if isinstance(v, str):
                nv = fn(v)
                if nv != v: n[k] = nv; c += 1
            else:
                c += strings(v, fn)
    elif isinstance(n, list):
        for i, v in enumerate(n):
            if isinstance(v, str):
                nv = fn(v)
                if nv != v: n[i] = nv; c += 1
            else:
                c += strings(v, fn)
    return c


def rep(node, old, new, want, label):
    got = json.dumps(node, ensure_ascii=False).count(json.dumps(old, ensure_ascii=False)[1:-1])
    assert got == want, '%s: ข้อความเดิมเจอ %d จุด (ควร %d)' % (label, got, want)
    strings(node, lambda s: s.replace(old, new))
    # ตรวจ "ข้อความใหม่ขึ้นครบ" — ไม่ใช่ "ข้อความเดิมหายหมด" (ข้อที่เป็นการเติมต่อท้าย ข้อความใหม่มีข้อความเดิมอยู่ข้างใน)
    after = json.dumps(node, ensure_ascii=False).count(json.dumps(new, ensure_ascii=False)[1:-1])
    assert after == want, '%s: ข้อความใหม่ขึ้น %d จุด (ควร %d)' % (label, after, want)


def main():
    src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json'))
    cfg = json.load(open(src, encoding='utf-8'))
    if MARK in json.dumps(cfg, ensure_ascii=False):
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร'); return
    ops = {o['id']: o for o in cfg['ops']}
    L = cfg['lookups']
    plan = ops['mnPlan']

    # ═══ A ═══
    rep(plan, 'คำชวนซื้อ (CTA) ที่ต้องใช้ในฉาก 5:', 'คำชวนซื้อ (CTA) ที่ต้องใช้ใน' + MARK + ':', 1, 'A1')
    rep(plan, '(แนะนำครั้งเดียวที่ vo5)', '(แนะนำครั้งเดียวที่ voN ของฉากปิดการขาย = ฉากสุดท้าย)', 1, 'A2')

    # ═══ B ═══
    rep(plan, 'มีค่า = ต้องสะท้อนในบท โดยเฉพาะฉากชวนซื้อ)',
        'มีค่า = ต้องพูดในบทพากย์ voN โดยเฉพาะฉากชวนซื้อ — ห้ามใส่ใน ovN)', 1, 'B1')
    # กฎ overlay/sNen อยู่ใน brain.mn.sys (คำสั่งระบบของตัวเขียนบท) ไม่ใช่ใน op — รอบแรกผมหาใน op แล้วยามหยุดก่อนเขียนไฟล์
    rep(cfg['brain'], '- 2-6 คำไทยต่อฉาก สั้น กระแทก เน้นประโยชน์หรือความเร่งด่วน\n',
        '- 2-6 คำไทยต่อฉาก สั้น กระแทก เน้นประโยชน์หรือความเร่งด่วน\n'
        '- ห้ามใส่ตัวเลขราคา ส่วนลด โปรโมชั่น หรือคำชวนซื้อ (เช่น กดตะกร้า สั่งเลย) ใน ovN — ของพวกนี้พูดในบทพากย์เท่านั้น '
        '(AI วิดีโอวาดตัวเลขบนจอเพี้ยนบ่อย ราคาผิดบนคลิปขายเสียหายกว่าไม่มี) · ตัวเลขสเปกสินค้า เช่น 15% SPF50 ใส่ได้\n', 1, 'B2')

    # ═══ C ═══ (mnVideo + mnVideo2 มีตารางมุมกล้องตัวละ 4 ฉาก = 8 จุดต่อค่า)
    for old, new in (('tight close-up on the product', 'tight close-up'),
                     ('slow smooth zoom-in toward the product', 'slow smooth zoom-in'),
                     ('eye-level view at product height', 'eye-level view')):
        for oid in ('mnVideo', 'mnVideo2'):
            rep(ops[oid], old, new, 4, 'C ' + oid + ' ' + new)

    # ═══ D ═══ Cast
    L['castGenderEN'] = {'หญิง': 'female', 'ชาย': 'male'}
    L['castAgeEN'] = {'วัยรุ่น': ' in their late teens', 'วัยทำงานตอนต้น': ' in their twenties', 'วัยผู้ใหญ่': ' in their thirties to forties'}
    has_person = {'op': 'eq', 'a': {'op': 'lookup', 'table': 'tplChar', 'key': '{values.templateId}', 'fallback': ''}, 'b': 'yes'}
    # 🪤 เงื่อนไขแบบข้อความ ('values.charGender!=') ใช้ได้เฉพาะเป็น when ตัวเดียว — ใส่ใน list ของ op and แล้วถูกอ่านเป็นสตริงไม่ว่าง = จริงเสมอ
    #    รอบแรกผมใส่แบบนั้น ⇒ ไม่กรอกเพศได้ "Cast: one Thai  presenter." เปล่า ๆ (ยาม ③ จับได้จากความยาวที่เพิ่ม 24)
    gender_set = {'op': 'not', 'a': {'op': 'eq', 'a': '{values.charGender}', 'b': ''}}
    gate = {'op': 'and', 'list': [gender_set, has_person]}
    cast_en = {'op': 'block', 'sep': '', 'parts': [{'when': gate, 'value': {'op': 'concat', 'sep': '', 'parts': [
        '\n\nCast: one Thai ', {'op': 'lookup', 'table': 'castGenderEN', 'key': '{values.charGender}', 'fallback': ''}, ' presenter',
        {'op': 'lookup', 'table': 'castAgeEN', 'key': '{values.charAge}', 'fallback': ''},
        {'op': 'block', 'sep': '', 'parts': [{'when': 'values.charLook!=', 'value': ', look: {values.charLook}'}]}, '.']}}]}
    cast_th = {'op': 'block', 'sep': '', 'parts': [{'when': gate, 'value': {'op': 'concat', 'sep': '', 'parts': [
        '\n\nพรีเซนเตอร์ตามที่ผู้ใช้ระบุ: เพศ{values.charGender}',
        {'op': 'block', 'sep': '', 'parts': [{'when': 'values.charAge!=', 'value': ' · {values.charAge}'}]},
        {'op': 'block', 'sep': '', 'parts': [{'when': 'values.charLook!=', 'value': ' · ลุค {values.charLook}'}]}]}}]}
    OLD_CAST = '\n\nCast: {values.charGender}, {values.charAge}, {values.charLook}.'
    for oid, new in (('mnBoard', cast_th), ('mnVideo', cast_en), ('mnVideo2', cast_en)):
        parts = ops[oid]['prompt']['parts']
        hit = [i for i, x in enumerate(parts) if OLD_CAST in json.dumps(x, ensure_ascii=False).replace('\\n', '\n')]
        assert len(hit) == 1, 'D %s: บล็อก Cast เดิมเจอ %d จุด' % (oid, len(hit))
        parts[hit[0]] = json.loads(json.dumps(new))

    # ═══ E ═══
    for oid in ('mnVideo', 'mnVideo2'):
        rep(ops[oid], '}. Camera: ', '} Camera: ', 4, 'E ' + oid)
    rep(cfg['brain'], '- sNen ทุกฉาก: ภาษาอังกฤษ 1 ประโยค ', '- sNen ทุกฉาก: ภาษาอังกฤษ 1 ประโยค จบด้วยจุด (.) เสมอ ', 1, 'E sNen rule')

    # ═══ F ═══ สาย 3D
    D3 = {
        'charVideoENT': ('No real people — the 3D cartoon character described in the scene is the presenter, the same character in every scene; '
                         'the real product stays photorealistic and in focus.'),
        'charBoardT': 'ไม่มีคนจริงในภาพ — ตัวการ์ตูน 3D ตามเทมเพลตเป็นตัวเดินเรื่อง ตัวเดิมทุกช่อง · สินค้าจริงคงความสมจริงและเป็นจุดโฟกัส',
        'charPlanT': ('กฎพรีเซนเตอร์: ไม่มีคนจริงในทุกฉาก — ตัวการ์ตูน 3D ตามเทมเพลตเป็นตัวเดินเรื่อง (ตัวเดิมทุกฉาก) สินค้าจริงเป็นจุดโฟกัส '
                      '— เขียนบท s*th/s*en ให้ตัวการ์ตูนตัวนี้เป็นผู้แสดง ไม่มีบุคคลจริง'),
        'tplCharMode': 'ไม่มีคนจริง — ตัวการ์ตูน 3D ตามเทมเพลตเป็นตัวเดินเรื่อง',
    }
    fixed3d = 0
    for t, txt in D3.items():
        ks = [k for k in L[t] if k.startswith('d3-')]
        assert len(ks) in (6, 12), 'F %s: คีย์ d3 %d ตัว' % (t, len(ks))
        for k in ks: L[t][k] = txt; fixed3d += 1

    # ── ยาม ──
    s = json.dumps(cfg, ensure_ascii=False)
    assert 'ที่ต้องใช้ในฉาก 5' not in s and 'ที่ vo5' not in s
    assert '}. Camera' not in s and 'Cast: {values.charGender}' not in s
    for oid in ('mnVideo', 'mnVideo2'):
        o = json.dumps(ops[oid], ensure_ascii=False)
        for w in ('tight close-up on the product', 'zoom-in toward the product', 'at product height'):
            assert w not in o, '%s ยังมี %s' % (oid, w)
    for t in D3:
        assert not any('ไม่มีคนในคลิป — โฟกัสสินค้าล้วน' == L[t][k] or 'product is the only hero' in L[t][k] for k in L[t] if k.startswith('d3-')), t
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v13 ลงแล้ว — %s' % os.path.basename(src))
    print('   A CTA/คำลงท้าย → ฉากปิดการขาย (ฉากสุดท้าย) · B ราคา/โปร/คำชวนซื้อ = พูดเท่านั้น ไม่ขึ้นจอ')
    print('   C มุมกล้อง 3 ค่าเลิกชี้สินค้า (x2 op x4 ฉาก) · D Cast: วิดีโออังกฤษ/บอร์ดไทย + เฉพาะเทมเพลตที่มีคน')
    print('   E เลิกเติมจุดซ้ำ (8 จุด) + สั่ง AI จบ sNen ด้วยจุด · F สาย 3D %d ค่า: ตัวการ์ตูนเป็นตัวเดินเรื่อง' % fixed3d)


main()
