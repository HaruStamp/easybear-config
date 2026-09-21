#!/usr/bin/env python3
# hardsell-v1-video-script-translate.py — ป้าย "บทวิดีโอ" + ไอคอน movie + ปุ่มแปลไทย→บทวิดีโอ "รายฉาก"
# ที่มา: คำสั่งพี่หมี 2026-09-21 (สั่งในห้อง minimal · minimal ส่งต่อให้ hardsell/showhow ใช้มาตรฐานเดียวกัน)
#   ปัญหาเดิม: แก้บท 1 ฉาก ต้องแก้ 2 ช่อง (ไทยสำหรับบอร์ด · อังกฤษสำหรับโมเดลวิดีโอ) แล้วป้าย "บทอังกฤษ" ทำให้คนอ่านนึกว่าซ้ำซ้อน
#   ⚠️ ตัดช่องอังกฤษทิ้งไม่ได้ — ส่งบทไทยเข้าโมเดลวิดีโอตรง ๆ แล้วโมเดล "วาด" ตัวหนังสือไทยลงบนคลิป (บั๊กเก่าเคสมุมกล้องไทย)
#   ⇒ ทางออก: ทำให้เติมช่องอังกฤษเป็น "กดปุ่มครั้งเดียว" แทนการพิมพ์เอง + เปลี่ยนชื่อช่องให้ตรงหน้าที่
#
# ทำ 3 อย่าง (= ผลลัพธ์สุดท้ายของ minimal v29+v30+v31 รวบเป็นรอบเดียว — hardsell ไม่ต้องเดินประวัติซ้ำ):
#   ① ป้าย 8 จุด: "บทอังกฤษ — ใช้ส่งเข้าโมเดลวิดีโอ (แก้คู่กับบทไทย)" → "บทวิดีโอ" + icon movie
#      🪤 ใช้ `movie` ไม่ใช่ `videocam` — `videocam` เป็นไอคอนของ "มุมกล้อง" อยู่แล้วในกล่องเดียวกัน ซ้ำแล้วอ่านสับสน
#   ② textarea อังกฤษ 8 ช่อง ได้ placeholder บอกหน้าที่
#   ③ ปุ่มแปล **รายฉาก** 8 ปุ่ม อยู่แถวเดียวกับป้าย "บทภาพ (คำสั่งวาด)" ชิดขวา
#      op: mnTrans (llm แปลทั้งคลิปครั้งเดียว → data.trans) + mnTrA1..8 (setFields เขียน "ช่องเดียว")
#      ปุ่มฉาก N = gen-phase ops:['mnTrans','mnTrA{N}'] ⇒ กดฉากไหนเขียนทับเฉพาะช่องนั้น ฉากอื่นที่แก้มือไว้ไม่ขยับ
#
# 🔴 ยามที่ห้ามถอด — ทุก mnTrA{N} ต้องมี setFields.where = 'data.trans.s{N}en!='
#    (engine `matchWhere` อ่าน path ซ้อนผ่าน readItem · `!=` กับ rhs ว่าง = "ต้องไม่ว่าง")
#    ถ้าไม่มี: LLM ไม่คืนคีย์นั้น/คืนค่าว่าง = ลบบทอังกฤษเดิมทิ้งเงียบ ๆ (ผู้ใช้ที่แก้มือไว้เสียของ)
# 🪤 ห้ามใช้ setFields ก้อนเดียวเขียนหลายฉากรวด — setFields ไม่มี `when` รายฟิลด์ ฉากที่ว่างจะถูกล้าง
# 🪤 op ใหม่ต้องไม่เข้า `auto.productLoop.gens` และ `stages` ⇒ ทำงานเฉพาะตอนกดปุ่ม ไม่วิ่งในรอบผลิตอัตโนมัติ
# รันซ้ำได้: ตรวจ marker
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = 'hs-tr-inline'
N_SCENES = 8
OLD_LABEL = 'บทอังกฤษ — ใช้ส่งเข้าโมเดลวิดีโอ (แก้คู่กับบทไทย)'
NEW_LABEL = 'บทวิดีโอ'
PLACEHOLDER = 'ภาษาอังกฤษ — ช่องนี้คือตัวที่ส่งเข้าโมเดลวิดีโอ'
BTN_LABEL = 'แปลงเป็นบทวิดีโอ'
BTN_CLASS = ('shrink-0 justify-center !gap-1 !h-8 !min-h-0 !px-2.5 !rounded-lg !text-[11.5px] font-bold '
             'border border-[var(--ev-border)] !bg-[var(--ev-surface2)] !text-[var(--ev-text)] ' + MARK)


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json')
    src = os.path.abspath(src)
    cfg = json.load(open(src, encoding='utf-8'))
    before = json.dumps(cfg, ensure_ascii=False)
    if MARK in before:
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร')
        return

    # ── ①②③ เดินกล่องบทของแต่ละฉาก (ลูกของกล่องคือ [ป้ายบทภาพ, sNth, ป้ายบทอังกฤษ, sNen]) ──
    done = []

    def btn(n):
        return {'el': 'gen-phase', 'ops': ['mnTrans', 'mnTrA%d' % n],
                'label': BTN_LABEL, 'icon': 'translate', 'variant': 'ghost',
                'className': BTN_CLASS,
                'when': {'op': 'not', 'a': {'op': 'or', 'list': [
                    {'op': 'eq', 'a': '{item.status}', 'b': 'running'},
                    {'op': 'eq', 'a': '{item.meta.retrying}', 'b': '1'}]}}}

    def fix(node):
        kids = node.get('card')
        if not isinstance(kids, list):
            return
        ai = next((i for i, k in enumerate(kids)
                   if isinstance(k, dict) and k.get('el') == 'textarea'
                   and isinstance(k.get('field'), str) and re.match(r's\d+en$', k['field'])), None)
        if ai is None:
            return
        scene = int(re.match(r's(\d+)en$', kids[ai]['field']).group(1))
        li = next((i for i, k in enumerate(kids)
                   if isinstance(k, dict) and k.get('el') == 'text' and k.get('value') == OLD_LABEL), None)
        assert li is not None, 'ฉาก %d: หาป้ายบทอังกฤษไม่เจอ' % scene
        di = next((i for i, k in enumerate(kids)
                   if isinstance(k, dict) and k.get('el') == 'text'
                   and str(k.get('value', '')).startswith('บทภาพ')), None)
        assert di is not None, 'ฉาก %d: หาป้าย "บทภาพ" ไม่เจอ' % scene
        # ① ป้ายบทวิดีโอ + ไอคอน · ② placeholder
        kids[li]['value'] = NEW_LABEL
        kids[li]['icon'] = 'movie'
        kids[ai]['placeholder'] = PLACEHOLDER
        # ③ [ป้าย บทภาพ] ————— [ปุ่มแปลงเป็นบทวิดีโอ]  (ห่อป้ายเดิม ไม่สร้างป้ายใหม่ กัน drift ข้อความ/ไอคอน)
        kids[di] = {'el': 'row', 'style': {'flexWrap': 'nowrap'},
                    'className': 'w-full items-center justify-between gap-2',
                    'card': [kids[di], btn(scene)]}
        done.append(scene)

    walk(cfg, fix)
    assert sorted(done) == list(range(1, N_SCENES + 1)), 'ต้องทำครบ %d ฉาก (ได้ %s)' % (N_SCENES, sorted(done))

    # ── op แปล ──
    ops = cfg['ops']
    ids = [o['id'] for o in ops]
    assert 'mnQueue' in ids, 'ไม่เจอ mnQueue'
    th_lines = '\n'.join('ฉาก %d: {item.s%dth}' % (i, i) for i in range(1, N_SCENES + 1))
    trans = {
        'id': 'mnTrans', 'type': 'llm', 'over': 'tasks', 'out': 'trans', 'parse': 'json',
        'systemInstruction': ('You translate Thai storyboard shot descriptions into English prompts for a video model. '
                             'Keep the same camera action, subject and setting. Do not invent new objects, brands or text. '
                             'Do not translate Thai on-screen text or voice-over — only the visual description.'),
        'prompt': {'op': 'block', 'sep': '', 'parts': [
            'แปลบทภาพแต่ละฉากเป็นภาษาอังกฤษ สำหรับส่งเข้าโมเดลวิดีโอ\n\n',
            th_lines,
            ('\n\nตอบเป็น JSON object เท่านั้น key = s1en ถึง s%den · value = คำบรรยายภาพภาษาอังกฤษของฉากนั้น\n'
             'ฉากที่บทไทยว่าง ให้ value เป็นสตริงว่าง · ห้ามใส่ข้อความอื่นนอก JSON' % N_SCENES),
        ]},
        'logRun': 'กำลังแปลบทเป็นบทวิดีโอ…', 'logDone': 'แปลบทวิดีโอแล้ว',
    }
    apply_ops = [{
        'id': 'mnTrA%d' % i, 'type': 'transform', 'over': 'tasks', 'out': '__trA%d' % i,
        'fn': 'setFields', 'pace': False,
        # 🔴 where = "ช่องต้นทางต้องไม่ว่าง" ⇒ แปลไม่มา = ไม่แตะของเดิม (ห้ามถอด)
        'setFields': {'where': 'data.trans.s%den!=' % i, 'fields': {'s%den' % i: '{item.data.trans.s%den}' % i}},
    } for i in range(1, N_SCENES + 1)]
    j = ids.index('mnQueue')
    cfg['ops'] = ops[:j] + [trans] + apply_ops + ops[j:]

    # ── ยามก่อนเขียน ──
    after = json.dumps(cfg, ensure_ascii=False)
    assert after != before
    got = [o['id'] for o in cfg['ops']]
    assert len(got) == len(set(got)), 'op id ซ้ำ'
    assert all('mnTrA%d' % i in got for i in range(1, N_SCENES + 1)), 'op apply ไม่ครบ'
    assert OLD_LABEL not in after, 'ยังมีป้ายเก่าค้าง'
    # 🪤 นับจาก node จริง ไม่ใช่ substring — คำว่า "บทวิดีโอ" อยู่ในป้ายปุ่ม/ข้อความ log ด้วย
    n_label = n_btn = 0
    def count(n):
        nonlocal n_label, n_btn
        if n.get('el') == 'text' and n.get('value') == NEW_LABEL: n_label += 1
        if n.get('el') == 'gen-phase' and n.get('label') == BTN_LABEL: n_btn += 1
    walk(cfg, count)
    assert n_label == N_SCENES, 'ป้าย "%s" ต้องมี %d จุด (ได้ %d)' % (NEW_LABEL, N_SCENES, n_label)
    assert n_btn == N_SCENES, 'ปุ่มต้องมี %d จุด (ได้ %d)' % (N_SCENES, n_btn)
    auto_s = json.dumps(cfg.get('auto'), ensure_ascii=False)
    stages_s = json.dumps(cfg.get('stages'), ensure_ascii=False)
    for n in ['mnTrans'] + ['mnTrA%d' % i for i in range(1, N_SCENES + 1)]:
        assert n not in auto_s and n not in stages_s, 'op แปล (%s) ต้องไม่เข้า auto/stages' % n
    pairs = []
    walk(cfg, lambda n: pairs.append((n['ops'][1], n.get('setFields'))) if MARK in str(n.get('className', '')) else None)
    assert sorted(int(re.match(r'mnTrA(\d+)$', a).group(1)) for a, _ in pairs) == list(range(1, N_SCENES + 1)), 'ปุ่มไม่ได้คู่กับ op ของฉากตัวเอง'
    for o in cfg['ops']:
        if o['id'].startswith('mnTrA'):
            i = int(o['id'][5:])
            assert o['setFields'].get('where') == 'data.trans.s%den!=' % i, 'ยาม where ของ %s หาย' % o['id']
            assert list(o['setFields']['fields']) == ['s%den' % i], '%s ต้องเขียนช่องเดียว' % o['id']

    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v1 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① ป้าย %d จุด → "%s" + icon movie · ② placeholder %d ช่อง' % (N_SCENES, NEW_LABEL, N_SCENES))
    print('   ③ ปุ่ม "%s" %d ปุ่ม (แถวเดียวกับป้ายบทภาพ ชิดขวา) + op mnTrans + mnTrA1..%d' % (BTN_LABEL, N_SCENES, N_SCENES))
    print('   🔴 ทุก mnTrA{N} มี where กันเขียนทับด้วยค่าว่าง · op ใหม่ไม่อยู่ใน auto/stages')


main()
