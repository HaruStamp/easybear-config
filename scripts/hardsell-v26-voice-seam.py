# hardsell-dev v26: เสียงพูดไม่ต่อเนื่องระหว่าง 2 ช่วงของคลิป 16 วิ (เจ้าของสั่ง 26 พ.ย. ข้อ C)
# ต้นเหตุ: เสียงแต่ละช่วงเจนแยกกัน · ล็อกเสียงมีแค่เพศ + "Voice continuity: same take as part 1"
#   · ช่วง 1 ถูกตัดที่ 7 วิ (el.segments trimEndIfNext 7 · ช่วง 2 เริ่มจากเฟรมวินาทีที่ 7) แต่บทช่วง 1 เขียนให้พูดเต็ม 8 วิ
#     ⇒ คำท้ายช่วง 1 ถูกตัดทิ้ง/ค้างครึ่งคำ แล้วช่วง 2 ทวนหรือพูดต่อกลางประโยค
# แก้:
#   1. voiceLockEN (+fallback ใน op) เพิ่ม "Voice identity" ตายตัวตามเพศ — ข้อความเดียวกันเป๊ะทั้ง 2 ช่วง
#   2. mnVideo (16 วิ): บทพูดจบภายใน 6.5 วิ แล้วเงียบ ปากปิด ท่าเดิม ถึงจบช่วง (จุดตัด 7 วิ) — lookup audioSpan ตาม svSec
#   3. mnVideo2: เริ่มพูดที่ 0.0 วิ ด้วยประโยคใหม่ ห้ามทวนคำจากช่วง 1
#   4. lenVo 16: ช่วงแรก vo1-vo4 ≤100 ตัว และ vo4 จบประโยค · vo5 เริ่มประโยคใหม่ ไม่ทวน
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F))
L = d['lookups']
ops = {o['id']: o for o in d['ops']}

ID_F = ' Voice identity, identical in every part: one adult Thai woman, warm mid-pitched clear timbre, standard central-Thai accent, steady medium-fast pace.'
ID_M = ' Voice identity, identical in every part: one adult Thai man, warm mid-low clear timbre, standard central-Thai accent, steady medium-fast pace.'
OLD_F = L['voiceLockEN']['เสียงผู้หญิง']; OLD_M = L['voiceLockEN']['เสียงผู้ชาย']
if 'Voice identity' not in OLD_F:
    L['voiceLockEN']['เสียงผู้หญิง'] = OLD_F + ID_F
    L['voiceLockEN']['เสียงผู้ชาย'] = OLD_M + ID_M
NEW_F = L['voiceLockEN']['เสียงผู้หญิง']
nf = 0
def fb(x):
    global nf
    if isinstance(x, dict):
        if x.get('table') == 'voiceLockEN' and x.get('fallback') == OLD_F: x['fallback'] = NEW_F; nf += 1
        for v in x.values(): fb(v)
    elif isinstance(x, list):
        for v in x: fb(v)
fb(ops['mnVideo']); fb(ops['mnVideo2'])
assert nf in (0, 4), nf

# 2. ช่วง 1 ของ 16 วิ: จบพูดก่อนจุดตัด
SPAN = 'from 0.0s to the end, no silent gaps'
L['audioSpan'] = {'8': SPAN, '10': SPAN,
    '16': 'from 0.0s, no gaps, last sentence done by 6.5s; then silent to the end, lips closed, same pose (the clip is cut at 7s)'}
A1 = '\n\nAudio: continuous Thai narration from 0.0s to the end, no silent gaps. Tone: '
na = 0
def span(parts):
    global na
    for i, p in enumerate(parts):
        if p == A1:
            parts[i:i + 1] = ['\n\nAudio: continuous Thai narration ', {'op': 'lookup', 'table': 'audioSpan', 'key': '{values.svSec}', 'fallback': SPAN}, '. Tone: ']
            na += 1; return
        if isinstance(p, dict):
            for v in p.values():
                if isinstance(v, list): span(v)
span(ops['mnVideo']['prompt']['parts'])
assert na == 1, na

# 3. ช่วง 2: ประโยคใหม่ ไม่ทวน
VC = '\n\nVoice continuity: same take as part 1 — keep the exact same voice (gender, pitch, timbre, accent, pace); no other speaker.'
VC2 = VC + ' Start speaking at 0.0s with the new sentence of this script; never repeat words already said in part 1.'
nv = 0
def vc(parts):
    global nv
    for i, p in enumerate(parts):
        if p == VC: parts[i] = VC2; nv += 1
        elif isinstance(p, dict):
            for v in p.values():
                if isinstance(v, list): vc(v)
vc(ops['mnVideo2']['prompt']['parts'])
assert nv == 1 or VC2 in json.dumps(ops['mnVideo2'], ensure_ascii=False), nv

# 4. บท 16 วิ
L['lenVo']['16'] = ('กฎความยาวบทพูด (ต้องพูดต่อเนื่อง ห้ามมีช่วงเงียบกลางประโยค):\n'
    '- คลิปนี้ยาว 16 วินาที มี 8 ฉาก แบ่ง 2 ช่วงที่สร้างเสียงแยกกัน — vo1 ถึง vo8 ต้องมีบทพูดครบทุกฉาก ห้ามเว้นว่างแม้แต่ฉากเดียว\n'
    '- นับเป็นตัวอักษรไทย ไม่ใช่จำนวนคำ (นับทุกตัวอักษรรวมสระและวรรณยุกต์ เว้นวรรคไม่ต้องนับ) — เกินเมื่อไหร่เสียงจะพูดรัวจนฟังไม่ทัน\n'
    '- ช่วงแรก vo1 ถึง vo4: ฉากละไม่เกิน 28 ตัวอักษร รวมไม่เกิน 100 ตัวอักษร เพราะช่วงแรกถูกตัดที่วินาทีที่ 7 — vo4 ต้องจบประโยคสมบูรณ์ ห้ามค้างครึ่งประโยคไปต่อใน vo5\n'
    '- ช่วงสอง vo5 ถึง vo8: ฉากละไม่เกิน 32 ตัวอักษร รวมไม่เกิน 128 ตัวอักษร · vo5 เริ่มประโยคใหม่ ห้ามทวนคำหรือวลีของ vo4 ห้ามทักทายหรือแนะนำสินค้าซ้ำ\n'
    '- ในแต่ละช่วงเขียนให้ต่อกันเป็นย่อหน้าเดียวที่อ่านรวดเดียวจบ ไม่ใช่วลีสั้นที่จบห้วนแยกกัน\n'
    '- ภาษาพูดแบบคนรีวิวจริง ไม่ใช่ภาษาโฆษณาอ่านสคริปต์')
print('v26: voice fallback', nf, '· audioSpan', na, '· continuity', nv)
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))
