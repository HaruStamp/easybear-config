# hardsell-dev v35: ugc-lips (ปากทาลิป) ต้องโคลสอัปปากทั้งคลิป ทุกช่วง (เทสสด 26 พ.ย. · engine v1.25 · Omni 1.2 · 20 วิ)
#   อาการ: ช่วง 1 ปากล้วน สีอิฐคงที่ ✅ · ช่วง 2 กล้องถอยออก ท้ายคลิปเห็นทั้งหน้า (เห็นตา) ❌
#   ต้นเหตุ (mnVideo2 ข้อความกลางทุกเทมเพลต):
#     ① "closing with rising energy and a confident nod that invites the viewer to buy" — nod = ต้องเห็นศีรษะ ⇒ ถอยกล้อง
#     ② "the clip ends on the person, not a card" (ทั้ง 2 ช่วง) — จบที่ "คน" ⇒ โมเดลเผยทั้งตัว/หน้า
#     ③ หัวช่วง 2 "same person, outfit, place" — ไม่มีคำล็อกระยะกล้อง · ล็อกปากอยู่ท้าย prompt บรรทัด Presenter เท่านั้น
#     ④ tplSceneEN ugc-lips จบด้วย "then a soft smile" (ช่วง 2 ได้ฉากเดิมซ้ำ = ยิ้ม ⇒ ถอยให้เห็นหน้า)
#     ⑤ mnPlan ฉากปิด "มองกล้อง ยิ้ม แล้วพูดคำชวนซื้อ" + lenActTail "เปลี่ยนระยะ" (บท s5-s8 ไปถึงวิดีโอเมื่อผู้ใช้แก้ฉาก)
#   แก้ (ตาราง lookup ใหม่ มีค่าเฉพาะ ugc-lips · fallback = ข้อความเดิม ⇒ เทมเพลตอื่นได้ prompt เดิมทุกไบต์):
#     - tplFrameEN: FRAMING LOCK ทุกช่วง แทรกหลัง Scene/Motion (ก่อน PRODUCT LOCK — ไม่โดนตัด 3900)
#     - tplEndEN: "ends on <the person>" → ugc-lips "the lips and the lipstick"
#     - tplP2CloseEN: ปิดช่วง 2 ด้วยปาก/เสียง/มือ+แท่งลิป ไม่ nod ไม่เผยหน้า
#     - tplSameEN: หัวช่วง 2 "same <person, outfit>" → ugc-lips "lips-only close-up framing, lip colour"
#     - tplCloseTH: mnPlan ฉากปิด ugc-lips ไม่มองกล้อง ยังโคลสอัปปาก
#     - tplSceneEN / charVideoENT / charPlanT ugc-lips: ย้ำ "ทุกช่วง จนเฟรมสุดท้าย" · คง COLOUR LOCK
#   ใช้ได้ทั้ง dev (key cond own/eTpl) และ public r26 (key {values.templateId}) — ยืม key จาก lookup ข้างเคียงใน op เดียวกัน
import json, sys, copy
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F))
L = d['lookups']
K = 'ugc-lips'
AIS = 'AI เลือกนาย/นางแบบให้เหมาะกับสินค้า'; FACE = 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'
assert K in L['tplSceneEN'], 'ต้องรัน v30 ก่อน'
ops = {o['id']: o for o in d['ops']}

L['tplFrameEN'] = {K: '\n\nFRAMING LOCK (every part, to the last frame): macro close-up of the lips only, nose tip to chin; the eyes and full face never enter the frame; the camera never pulls back, zooms out or tilts up.'}
L['tplEndEN'] = {K: 'the lips and the lipstick'}
L['tplP2CloseEN'] = {K: 'closing on the same lips close-up: a soft lip smile, lipstick beside the mouth, while the voice invites the viewer to buy — no nod, no face reveal'}
L['tplSameEN'] = {K: 'lips-only close-up framing, lip colour'}
L['tplCloseTH'] = {K: ' — ข้อนี้ไม่ใช้กับเทมเพลตปากทาลิป: ฉากสุดท้ายยังโคลสอัปปากระยะเดิม ไม่มองกล้อง ไม่เห็นตา/ทั้งหน้า — ยิ้มที่ปาก ถือแท่งลิปข้างปาก ชวนซื้อด้วยเสียงพากย์'}
L['tplSceneEN'][K] = ('Macro beauty shot of the lips only: the hand glides the lipstick bullet across the lips in one smooth stroke, the lips press together and part to show even full colour, then a soft lip smile with the lipstick held beside the lips. '
    'COLOUR LOCK: the colour on the lips matches the lipstick bullet in the first frame exactly — same hue, depth, undertone and finish — and never shifts under any light. '
    'An unseen narrator speaks; voice-over only, the lips do not lip-sync.')
video = 'Only the lips and the lipstick hand, in every part — never the eyes or full face; the lip colour stays exactly the lipstick colour from the first frame.'
plan = ('กฎภาพ: ทุกฉากเห็นแค่ริมฝีปาก (และมือที่ถือแท่งลิป) ห้ามเห็นตาหรือทั้งหน้า — เขียน sNth/sNen เป็นโคลสอัปปาก: หมุนแท่งลิปให้เห็นเนื้อสี → ทาจากแท่งลงปาก → เม้มปากเกลี่ยสี → โชว์สีบนปากเต็มๆ → ยิ้มพร้อมแท่งลิปข้างปาก'
    ' · ทุกฉาก (รวมฉาก 5-8 ของคลิปยาวและฉากปิดการขาย) กล้องอยู่ระยะโคลสอัปปากเท่าเดิม ห้ามถอยกล้อง/ซูมออก — เปลี่ยนได้แค่การกระทำของมือและปาก'
    ' · สีบนปากต้องตรงกับสีเนื้อลิปในรูปสินค้าเป๊ะ ห้ามบรรยายเป็นสีอื่น · เสียงพากย์เป็นเสียงบรรยาย ไม่ใช่ปากในภาพพูด')
for src in (AIS, FACE):
    L['charVideoENT'][K + '|' + src] = video
    L['charPlanT'][K + '|' + src] = plan

def key_of(op, table):
    st = [op['prompt']]
    while st:
        x = st.pop(0)
        if isinstance(x, dict):
            if x.get('op') == 'lookup' and x.get('table') == table: return copy.deepcopy(x['key'])
            st += list(x.values())
        elif isinstance(x, list): st += x
    raise SystemExit('ไม่เจอ lookup %s ใน %s' % (table, op['id']))
def lk(table, key, fb): return {'op': 'lookup', 'table': table, 'key': key, 'fallback': fb}
def has(op, table): return table in json.dumps(op['prompt'], ensure_ascii=False)

END_OLD = '; the clip ends on the person, not a card.'
for oid in ('mnVideo', 'mnVideo2'):
    o = ops[oid]; P = o['prompt']['parts']; key = key_of(o, 'tplSceneEN')
    # FRAMING LOCK หลัง "." ที่ปิด Scene/Motion
    if not has(o, 'tplFrameEN'):
        i = next(i for i, p in enumerate(P) if isinstance(p, dict) and p.get('table') == 'toneMotion')
        assert P[i + 1] == '.', (oid, P[i + 1])
        P.insert(i + 2, lk('tplFrameEN', copy.deepcopy(key), ''))
    # จบที่ใคร
    if not has(o, 'tplEndEN'):
        i = next(i for i, p in enumerate(P) if isinstance(p, str) and END_OLD in p)
        a, b = P[i].split(END_OLD)
        P[i:i + 1] = [{'op': 'concat', 'parts': [a + '; the clip ends on ', lk('tplEndEN', copy.deepcopy(key), 'the person'), ', not a card.' + b]}]

o = ops['mnVideo2']; P = o['prompt']['parts']; key = key_of(o, 'tplSceneEN')
NOD = 'closing with rising energy and a confident nod that invites the viewer to buy'
if not has(o, 'tplP2CloseEN'):
    i = next(i for i, p in enumerate(P) if isinstance(p, str) and NOD in p)
    a, b = P[i].split(NOD)
    P[i:i + 1] = [{'op': 'concat', 'parts': [a, lk('tplP2CloseEN', copy.deepcopy(key), NOD), b]}]
SAME = 'same person, outfit, place, light and product'
if not has(o, 'tplSameEN'):
    assert isinstance(P[0], str) and P[0].startswith('Part 2 of the same take') and SAME in P[0]
    a, b = P[0].split(SAME)
    P[0:1] = [{'op': 'concat', 'parts': [a + 'same ', lk('tplSameEN', copy.deepcopy(key), 'person, outfit'), ', place, light and product' + b]}]

o = ops['mnPlan']; key = key_of(o, 'tplName')
LOOK = ' มองกล้อง ยิ้ม แล้วพูดคำชวนซื้อ'
if not has(o, 'tplCloseTH'):
    n = 0
    def walk(x):
        global n
        if isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                if isinstance(v, str) and LOOK in v:
                    a, b = v.split(LOOK, 1)
                    x[i:i + 1] = [{'op': 'concat', 'parts': [a, lk('tplCloseTH', copy.deepcopy(key), LOOK), b]}]; n += 1
                else: walk(v)
    walk(o['prompt'])
    assert n == 1, n

print('v35: ugc-lips lips-only all parts ok')
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))