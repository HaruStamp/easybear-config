#!/usr/bin/env python3
# minimal-v62-pets-multi.py — พี่หมีสั่ง 26 พ.ย. 2569 (อัปเดตใหญ่ ข้อ 4 "ใส่ภาพตัวละครและสัตว์เลี้ยง (หลายตัว)") · แก้ minimal-dev.json อย่างเดียว · รันซ้ำได้
#  ของเดิม: ตัวละครหลัก 1 รูป (characters ch1 slot face = คน หรือ สัตว์ ตาม svCast) — แนบสัตว์เพิ่มไม่ได้
#  ใหม่: "สัตว์เลี้ยงร่วมแสดง" แนบรูปได้สูงสุด 3 ตัว (ch1 slot pet1..pet3 · values.svPets = ''/1/2/3) ใช้ร่วมกับตัวละครหลักได้ทุกโหมด (ยกเว้น "ไม่มีผู้แสดง")
#  ref (เพดาน: ภาพ 10 · Omni 7 · startFrame ทิ้ง refs ทั้งชุด — minimal ไม่ใช้ startFrame):
#    วิดีโอ : สินค้า → หน้าตัวละคร → สัตว์ 1-3 → สถานที่ → บอร์ด (ใบสุดท้ายเสมอ · บทเรียน v28)
#    บอร์ด  : สินค้า → หน้าตัวละคร → สัตว์ 1-3 → สถานที่ → บอร์ดช่วงอื่น (ต่อเนื่อง · ท้ายเหมือนเดิม)
#    ปก     : บอร์ด → สินค้า 3 → หน้าตัวละคร → สัตว์ 1-3 (สูงสุด 8)
#    เกินเพดาน = ตัดรูปสินค้ามุมเสริมจากท้าย (image5 → image4 → image3 → image2) · รูปสินค้าหลัก + ตัวละคร + สัตว์ + สถานที่ + บอร์ด ไม่ถูกตัด
#    นับจากตัวเลือก (values · ให้ยาม all-apps-safe นับเพดานได้) ⇒ เลือก 3 ตัวแต่แนบรูป 1 = ยังกันที่ไว้ 3
#  prompt: 1 ประโยคต่อท้ายบล็อกตัวละคร (วิดีโอ EN · บอร์ด TH · ปก EN) + กฎใน sys ของ mnPlan + ส่งรูปสัตว์เข้า mnPlan ให้บทบรรยายน้องถูกตัว
#    ที่ว่าง prompt (เพดาน 3,900 ตึง): ไม่บีบบท — ย่อคำสั่งที่ซ้ำ (ดูท้ายไฟล์ ROOM)
import json, sys, copy

P = sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json'
c = json.load(open(P, encoding='utf-8'))
ops = {o['id']: o for o in c['ops']}
L = c['lookups']
NONE = 'ไม่มีคนในคลิป — โฟกัสสินค้าล้วน'
def eq(a, b): return {'op': 'eq', 'a': a, 'b': b}
def NOT(x): return {'op': 'not', 'a': x}
def AND(*xs): return {'op': 'and', 'list': list(xs)}
def gte(a, b): return {'op': 'gte', 'a': a, 'b': b}
def cond(w, t, e): return {'op': 'cond', 'when': w, 'then': t, 'else': e}
def add(*xs):
    out = xs[0]
    for x in xs[1:]: out = {'op': 'add', 'a': out, 'b': x}
    return out
def cnt(coll, cid, slot): return {'op': 'count', 'from': coll, 'where': 'id=' + cid, 'slot': slot}
def PET_ON(k): return AND(NOT(eq('{values.svChar}', NONE)), gte('{values.svPets}', k))
PETS_ANY = PET_ON(1)
PET_REF = lambda k: {'from': 'characters', 'by': '{values.charId}', 'slot': 'pet%d' % k, 'when': PET_ON(k)}

# ───────── ข้อมูล ─────────
ch = c['collections']['characters']
for k in (1, 2, 3):
    if 'pet%d' % k not in ch['slots']: ch['slots'].append('pet%d' % k)
c['values'].setdefault('svPets', '')   # sv* อยู่ใน saveGroups.setup แล้ว (รูปอยู่ใน characters ที่ setup เก็บอยู่แล้ว)

L['petVideoEN'] = {
    '1': ' +1 pet from the pet photo, kept exact (breed, fur, markings); overrides any one-animal rule.',
    '2': ' +2 pets from the pet photos, each exact (breed, fur, markings); overrides any one-animal rule.',
    '3': ' +3 pets from the pet photos, each exact (breed, fur, markings); overrides any one-animal rule.',
}
L['petBoard'] = {
    '1': ' · มีสัตว์เลี้ยงจากรูปที่แนบเพิ่ม 1 ตัว ตรงพันธุ์ สีขน ลายตามรูป',
    '2': ' · มีสัตว์เลี้ยงจากรูปที่แนบเพิ่ม 2 ตัว ตรงพันธุ์ สีขน ลายตามรูป',
    '3': ' · มีสัตว์เลี้ยงจากรูปที่แนบเพิ่ม 3 ตัว ตรงพันธุ์ สีขน ลายตามรูป',
}
L['petPlan'] = {k: ('\n★ สัตว์เลี้ยงร่วมแสดง %s ตัว (ผู้ใช้แนบรูป — %s รูปท้ายสุดในชุดภาพที่แนบ ไม่ใช่สินค้า): ทุกคลิปมีน้องครบ %s ตัวในฉากที่เหมาะ '
                     'อยู่คู่กับสินค้า/ผู้แสดงอย่างเป็นธรรมชาติ ไม่บังสินค้า · ทุกฉากที่มีน้องให้ระบุชนิด สายพันธุ์ สีขน ลายของแต่ละตัวใน s*en ตรงรูปและเหมือนกันทุกฉาก '
                     '· ทับกฎ "สัตว์ 1 ตัว/ห้ามมีตัวที่สอง" ด้านบนเฉพาะน้องจากรูปเหล่านี้ (ตัวละครหลักยังเป็นตัวเดิม) ห้ามเพิ่มสัตว์อื่นนอกจากนี้') % (k, k, k)
                for k in ('1', '2', '3')}
L['petCoverEN'] = {'1': ' Also the pet from the pet photo, exactly as photographed.',
                   '2': ' Also the 2 pets from the pet photos, each exactly as photographed.',
                   '3': ' Also the 3 pets from the pet photos, each exactly as photographed.'}
PET_BLOCK_V = {'op': 'block', 'sep': '', 'parts': [{'when': PETS_ANY, 'value': {'op': 'lookup', 'table': 'petVideoEN', 'key': '{values.svPets}', 'fallback': ''}}]}
PET_BLOCK_B = {'op': 'block', 'sep': '', 'parts': [{'when': PETS_ANY, 'value': {'op': 'lookup', 'table': 'petBoard', 'key': '{values.svPets}', 'fallback': ''}}]}
PET_BLOCK_P = {'op': 'block', 'sep': '', 'parts': [{'when': PETS_ANY, 'value': {'op': 'lookup', 'table': 'petPlan', 'key': '{values.svPets}', 'fallback': ''}}]}
PET_BLOCK_C = {'op': 'block', 'sep': '', 'parts': [{'when': PETS_ANY, 'value': {'op': 'lookup', 'table': 'petCoverEN', 'key': '{values.svPets}', 'fallback': ''}}]}


def has_table(node, tables):
    s = json.dumps(node, ensure_ascii=False)
    return any('"table": "%s"' % t in s for t in tables)


def insert_after_char_block(prompt, tables, block):
    """แทรก block หลังบล็อกตัวละคร (block ที่มี lookup ตารางตัวละคร) — ในรายการ parts ที่ลึกที่สุดที่ถือบล็อกนั้น"""
    if 'petVideoEN' in json.dumps(prompt, ensure_ascii=False) or 'petBoard' in json.dumps(prompt, ensure_ascii=False): return 0
    def rec(n):
        if isinstance(n, dict):
            parts = n.get('parts')
            if isinstance(parts, list):
                for i, x in enumerate(parts):
                    if isinstance(x, dict) and x.get('op') == 'block' and has_table(x, tables) and all(not has_table(y.get('value'), ['opNames']) for y in x.get('parts', []) if isinstance(y, dict)):
                        # บล็อกตัวละคร = block ที่ parts ทุกตัวเป็น lookup/concat ตาราง char*/cast*
                        if all(isinstance(y, dict) and has_table(y.get('value'), tables) for y in x['parts']):
                            parts.insert(i + 1, copy.deepcopy(block)); return 1
                for x in parts:
                    r = rec(x)
                    if r: return r
            for k, v in n.items():
                if k != 'parts':
                    r = rec(v)
                    if r: return r
        elif isinstance(n, list):
            for x in n:
                r = rec(x)
                if r: return r
        return 0
    return rec(prompt)


n_ins = 0
for oid in ('mnVideo', 'mnVideo2', 'mnVideo3'):
    n_ins += insert_after_char_block(ops[oid]['prompt'], ['charVideoEN', 'charVideoPetEN', 'castVideoEN'], PET_BLOCK_V)
for oid in ('mnBoard', 'mnBoard2', 'mnBoard3'):
    n_ins += insert_after_char_block(ops[oid]['prompt'], ['charBoard', 'charBoardPet', 'castBoard'], PET_BLOCK_B)
cv = ops['mnCover']['prompt']['parts']
if 'petCoverEN' not in json.dumps(cv, ensure_ascii=False):
    assert isinstance(cv[0], str) and 'PRODUCT LOCK' in cv[0]
    cv[0] = cv[0].replace(" (plus the presenter's face if attached).", " (plus the presenter's face if attached, then pet photos if any).")
    cv.insert(1, copy.deepcopy(PET_BLOCK_C)); cv.insert(2, '\n'); n_ins += 1
    # ประโยคสัตว์ต่อท้ายบรรทัด PRODUCT LOCK ⇒ ตัด \n ท้าย cv[0] ไปไว้หลัง block
    cv[0] = cv[0].rstrip('\n')
# mnPlan: กฎใน sys (ต่อท้ายบล็อกตัวละคร/สัตว์) + รูปสัตว์เข้า images (ท้ายรูปสินค้า)
pl = ops['mnPlan']
si = pl['systemInstruction']['parts']
if 'petPlan' not in json.dumps(si, ensure_ascii=False):
    last = max(i for i, x in enumerate(si) if has_table(x, ['charPlan', 'charPlanPet', 'castPlan']))
    si.insert(last + 1, copy.deepcopy(PET_BLOCK_P)); n_ins += 1
for k in (1, 2, 3):
    tok = '{characters[ch1].slots.pet%d}' % k
    if tok not in json.dumps(pl['images'], ensure_ascii=False):
        pl['images'].append(cond(PET_ON(k), tok, ''))
print('แทรกประโยคสัตว์:', n_ins, 'จุด')

# ───────── refs ─────────
FACE_W = None
def face_gate(also):
    for a in also:
        if a['from'] == 'characters' and a['slot'] == 'face': return a.get('when')
    raise AssertionError('ไม่เจอ ref หน้า')

def extra_count(also):
    """จำนวนรูปที่ไม่ใช่สินค้า = หน้า + สัตว์ + สถานที่ + บอร์ด — นับจาก "ตัวเลือก" (values) ไม่ใช่ slot ที่มีรูปจริง
    เพราะยามกลาง all-apps-safe นับเพดานจาก values ล้วน (store ว่าง) · ใช้ block ไม่ใช้ cond (engine เปล่าในยามไม่รู้จัก cond)
    ผล: เลือก 3 ตัวแต่แนบรูป 1 = กันที่ไว้ 3 (รูปสินค้ามุมเสริมน้อยกว่าที่ใส่ได้ — ปลอดภัยฝั่งไม่เกินเพดาน)"""
    parts = []
    for a in also:
        if a['from'] == 'products': continue
        parts.append({'op': 'block', 'sep': '', 'parts': [{'when': a['when'], 'value': '1'}]} if 'when' in a else 1)
    return add(*parts)

def patch_refs(oid, cap):
    r = ops[oid]['refs']; al = r['also']
    assert r['from'] == 'products' and r['slot'] == 'image', (oid, r['slot'])
    if not any(a['slot'] == 'pet1' for a in al):
        fi = next(i for i, a in enumerate(al) if a['from'] == 'characters' and a['slot'] == 'face')
        al[fi + 1:fi + 1] = [PET_REF(k) for k in (1, 2, 3)]
    EX = extra_count(al)
    for a in al:
        if a['from'] == 'products' and a['slot'] in ('image2', 'image3', 'image4', 'image5'):
            k = int(a['slot'][-1])
            a['when'] = {'op': 'lte', 'a': EX, 'b': cap - k}   # รูปสินค้าใบที่ k ใช้ได้เมื่อ (รูปอื่น) + k ≤ เพดาน
    # ลำดับ: บอร์ดของช่วง (วิดีโอ) ต้องเป็นใบสุดท้าย
    if oid.startswith('mnVideo'):
        assert al[-1]['from'] == 'tasks' and al[-1]['slot'].startswith('board') and 'when' not in al[-1], (oid, al[-1])

for oid in ('mnVideo', 'mnVideo2', 'mnVideo3'): patch_refs(oid, 7)
for oid in ('mnBoard', 'mnBoard2', 'mnBoard3'): patch_refs(oid, 10)
cr = ops['mnCover']['refs']['also']
if not any(a['slot'] == 'pet1' for a in cr):
    fi = next(i for i, a in enumerate(cr) if a['from'] == 'characters' and a['slot'] == 'face')
    cr[fi + 1:fi + 1] = [PET_REF(k) for k in (1, 2, 3)]

# ───────── UI: กล่อง "สัตว์เลี้ยงร่วมแสดง" ใต้กล่องตัวละคร ─────────
cast = c['phases'][0]['form'][0]['card'][0]['card'][2]['card'][2]
assert cast['card'][0]['card'][1]['value'] == 'ตัวละครในคลิป', 'กล่องตัวละครย้ายที่แล้ว — ปรับสคริปต์ก่อน'
if not any(x.get('id') == 'mnPets' for x in cast['card']):
    face_box = cast['card'][7]
    assert face_box['card'][0]['value'] == 'ตัวละคร', face_box['card'][0]
    FILL = 'w-full justify-center !h-[44px] !rounded-xl !border-0 font-black !text-[15px] uppercase'
    def tile(k):
        sl = 'pet%d' % k
        return {'el': 'box', 'className': 'flex flex-col gap-1.5 w-[calc((100%-0.75rem)/2)] @[560px]:w-[140px]', 'when': 'values.svPets>=%d' % k, 'card': [
            {'el': 'text', 'value': 'น้องตัวที่ %d' % k, 'icon': 'pets', 'className': '!text-[12.5px] @[640px]:!text-[12px] font-bold opacity-60'},
            {'el': 'box', 'className': 'relative', 'when': 'item.slots.%s!=' % sl, 'card': [
                {'el': 'media-slot', 'src': '{item.slots.%s}' % sl, 'aspect': '1:1', 'style': {'borderRadius': '16px'}, 'className': 'ring-1 ring-[var(--ev-border)]'},
                {'el': 'button', 'action': 'hook', 'fn': 'clearSlot', 'to': sl, 'label': '', 'icon': 'close', 'variant': 'ghost',
                 'className': '!absolute !top-1.5 !right-1.5 z-10 justify-center !gap-0 !w-11 !h-11 @[640px]:!w-8 @[640px]:!h-8 !rounded-full !px-0 !aspect-square !bg-white/95 !text-red-500 !border-0 !min-h-0 !shrink-0'}]},
            {'el': 'box', 'className': 'aspect-square rounded-2xl border-2 border-dashed border-[var(--ev-border)] bg-black/40 flex flex-col justify-center gap-2 p-2', 'when': 'item.slots.%s=' % sl, 'card': [
                {'el': 'upload', 'label': '', 'placeholder': 'อัพโหลด', 'icon': 'upload', 'into': sl, 'resize': {'maxPx': 512, 'quality': 0.8}, 'className': FILL + ' !bg-[var(--ev-text)] !text-[var(--ev-bg)]'},
                {'el': 'pick-button', 'label': 'เลือกภาพ', 'icon': 'photo_library', 'filter': 'image', 'into': sl, 'resize': {'maxPx': 512, 'quality': 0.8}, 'className': FILL + ' !bg-white !text-[#17253a]'}]},
        ]}
    pets_box = {'el': 'box', 'id': 'mnPets', 'className': 'flex flex-col gap-3 p-3 @[420px]:p-4 rounded-2xl bg-[var(--ev-bg)] border border-[var(--ev-border)]',
                'when': NOT(eq('{values.svChar}', NONE)), 'card': [
        {'el': 'text', 'value': 'สัตว์เลี้ยงร่วมแสดง (ไม่บังคับ)', 'icon': 'pets', 'className': '!text-[14px] @[640px]:!text-[13px] opacity-60'},
        {'el': 'text', 'value': 'แนบรูปน้องของคุณได้สูงสุด 3 ตัว — อยู่ในคลิปพร้อมตัวละครด้านบน ระบบล็อกพันธุ์ สีขน ลาย ตามรูปทุกช็อต',
         'className': '!text-[13px] @[640px]:!text-[12.5px] opacity-60 leading-relaxed'},
        {'el': 'grid-select', 'field': 'svPets', 'cols': 4, 'mobile': {'cols': 2}, 'contained': True, 'className': '!min-h-[48px] @[420px]:!min-h-0', 'options': [
            {'value': '', 'label': 'ไม่มี', 'desc': 'ไม่แนบสัตว์เพิ่ม', 'icon': 'block'},
            {'value': '1', 'label': '1 ตัว', 'desc': 'แนบ 1 รูป', 'icon': 'pets'},
            {'value': '2', 'label': '2 ตัว', 'desc': 'แนบ 2 รูป', 'icon': 'pets'},
            {'value': '3', 'label': '3 ตัว', 'desc': 'แนบ 3 รูป', 'icon': 'pets'}]},
        {'el': 'repeat', 'coll': 'characters', 'where': 'id=ch1', 'when': 'values.svPets>=1', 'card': [
            {'el': 'box', 'className': 'flex flex-row flex-wrap gap-3 items-start', 'card': [tile(1), tile(2), tile(3)]}]},
        {'el': 'text', 'when': 'values.svPets>=1', 'icon': 'info',
         'value': 'รูปละ 1 ตัว เห็นหน้าและลำตัวชัด · วิดีโอรับรูปอ้างอิงได้ 7 รูป — ยิ่งเลือกจำนวนสัตว์มาก ระบบยิ่งใช้รูปสินค้ามุมเสริมน้อยลง (รูปสินค้าหลักใช้ทุกครั้ง)',
         'className': '!text-[12.5px] leading-snug opacity-60 px-0.5'},
    ]}
    cast['card'].insert(8, pets_box)

# ───────── ROOM: ที่ว่าง prompt สำหรับประโยคสัตว์ — เฉพาะตอนแนบสัตว์ (ไม่แนบ = prompt เดิมทุกไบต์) · ไม่บีบบท ─────────
#  ① วิดีโอ: ตัด "For angles the photos lack…" ใน PRODUCT LOCK — กฎมุมที่รูปไม่มีอยู่ในบอร์ดแล้ว และวิดีโอเดินตามช่องบอร์ด
#  ② ตารางตัวละคร (วิดีโอ+บอร์ด) อ่านคีย์ "<เดิม>|pets" ตอนแนบสัตว์ · ค่าเริ่ม = ข้อความเดิม · ตัวยาว (ใช้รูปหน้า) ย่อคำซ้ำ (คงคำล็อกตัวตน)
ANG = ' For angles the photos lack, use the closest shown one; never invent details.'
def split_angle(n):
    hits = 0
    if isinstance(n, dict):
        for k_, v_ in list(n.items()):
            if isinstance(v_, str) and ANG in v_ and v_ != ANG:
                a_, b_ = v_.split(ANG, 1)
                n[k_] = {'op': 'concat', 'parts': [a_, {'op': 'block', 'sep': '', 'parts': [{'when': NOT(PETS_ANY), 'value': ANG}]}, b_]}; hits += 1
            else: hits += split_angle(v_)
    elif isinstance(n, list):
        for i_, v_ in enumerate(n):
            if isinstance(v_, str) and ANG in v_ and v_ != ANG:
                a_, b_ = v_.split(ANG, 1)
                n[i_:i_ + 1] = [a_, {'op': 'block', 'sep': '', 'parts': [{'when': NOT(PETS_ANY), 'value': ANG}]}, b_]; hits += 1
            else: hits += split_angle(v_)
    return hits
n_ang = sum(split_angle(ops[o]['prompt']) for o in ('mnVideo', 'mnVideo2', 'mnVideo3'))
FACE = 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'
SHORT = {
    ('charVideoEN', 'มีพรีเซนเตอร์ไทย 1 คนในคลิป|' + FACE): 'CHARACTER CONSISTENCY (HIGHEST PRIORITY): the exact person from the attached face image in every shot (same face, hair, skin tone, body, age, identity, outfit), never another person; only pose, angle, expression change. Product stays the focus.',
    ('charVideoPetEN', 'สัตว์จริง|' + FACE): 'CHARACTER CONSISTENCY (HIGHEST PRIORITY): the exact animal from the attached reference image in every shot (same species, breed, fur, markings); four-legged, no clothes, never upright or talking; no people; product stays the focus.',
    ('charVideoPetEN', 'สัตว์ทำตัวเหมือนคน|' + FACE): 'CHARACTER CONSISTENCY (HIGHEST PRIORITY): the exact animal from the attached reference image in every shot (same species, fur, markings), acting like a person: upright, clothed, paws as hands; no people; voice-over is an off-screen narrator.',
    ('charBoard', 'มีพรีเซนเตอร์ไทย 1 คนในคลิป|' + FACE): 'ใช้บุคคลจากภาพใบหน้าที่แนบ เป็นคนเดียวกันทุกช่อง ล็อกหน้าตา ทรงผม สีผิว 100% ชุดเดิม ปรับได้แค่ท่าทาง/มุมกล้อง สินค้าเด่นกว่าคนเสมอ',
}
PSUF = {'op': 'block', 'sep': '', 'parts': [{'when': PETS_ANY, 'value': '|pets'}]}   # block ไม่ใช่ cond — ยาม clamp (engine เปล่า) ไม่รู้จัก cond
n_key = 0
for t in ('charVideoEN', 'charVideoPetEN', 'charBoard', 'charBoardPet'):
    for k_ in [k for k in L[t] if not k.endswith('|pets')]:
        L[t][k_ + '|pets'] = SHORT.get((t, k_), L[t][k_])
def key_suffix(n, t):
    global n_key
    if isinstance(n, dict):
        if n.get('op') == 'lookup' and n.get('table') == t and isinstance(n.get('key'), str):
            n['key'] = {'op': 'concat', 'parts': [n['key'], PSUF]}; n_key += 1; return
        for v_ in n.values(): key_suffix(v_, t)
    elif isinstance(n, list):
        for v_ in n: key_suffix(v_, t)
for o in ('mnVideo', 'mnVideo2', 'mnVideo3', 'mnBoard', 'mnBoard2', 'mnBoard3'):
    for t in ('charVideoEN', 'charVideoPetEN', 'charBoard', 'charBoardPet'): key_suffix(ops[o]['prompt'], t)
for (t, k_), v_ in SHORT.items(): assert len(v_) < len(L[t][k_]), (t, k_)
print('ที่ว่าง: ตัดประโยคมุม', n_ang, 'จุด · คีย์ |pets', n_key, 'จุด')

open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=2))
print('ok', P)
