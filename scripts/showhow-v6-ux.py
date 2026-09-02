#!/usr/bin/env python3
# showhow-v6-ux.py — ออกแบบหน้า "เพิ่มงาน" ใหม่ + ปลดกฎบังคับรูปสินค้าที่เป็นมรดกจาก minimal
#   ลำดับใหม่เล่าเป็นเรื่อง: ① งานนี้ทำอะไร → ② พื้นที่ → ③ ก่อน→หลัง → ④ ของที่จะใช้ (ไม่บังคับ) → ⑤ ขั้นสูง
import json, os, copy

P = '/Users/tammaster/Desktop/Dev/bear-clan/easybear-config/showhow.json'
cfg = json.load(open(P, encoding='utf-8'))
PE = cfg['phases'][0]['form'][2]

def find_list(root, probe):
    if isinstance(root, dict):
        for k, v in root.items():
            if isinstance(v, list) and len(v) >= 4 and any(probe in json.dumps(c, ensure_ascii=False) for c in v):
                return root, k
            r = find_list(v, probe)
            if r: return r
    elif isinstance(root, list):
        for c in root:
            r = find_list(c, probe)
            if r: return r
    return None

node, key = find_list(PE, '{item.slots.image}')
OLD = node[key]
header, prodGal, roomBlk, nameRow, descBlk, advGrp, footer = OLD[0], OLD[1], OLD[2], OLD[3], OLD[4], OLD[5], OLD[6]

# ── ชิ้นส่วนที่เอากลับมาใช้ ──
prodTiles = prodGal['card'][1]                       # แถวไทล์รูปของหลัก (progressive 5 ช่อง)
roomTiles = [c for c in roomBlk['card'] if c.get('className', '').startswith('flex flex-row flex-wrap')][0]
def field_of(blk, f):                                 # ดึงกล่อง label+input ของฟิลด์นั้นออกมา
    out = []
    def w(n):
        if isinstance(n, dict):
            if n.get('field') == f: out.append(n)
            for v in n.values(): w(v)
        elif isinstance(n, list):
            for v in n: w(v)
    w(blk); return out[0] if out else None

f_name, f_price = field_of(nameRow, 'name'), field_of(nameRow, 'price')
f_desc = field_of(descBlk, 'description')
f_room, f_before, f_goal = field_of(roomBlk, 'room'), field_of(roomBlk, 'before'), field_of(roomBlk, 'goal')

LBL = ('!text-[13.5px] min-[640px]:!text-[13px] !text-[var(--ev-text)] opacity-65 '
       'uppercase tracking-[0.14em] font-black px-0.5 mb-2')
BOX = 'bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-2xl p-4 min-[640px]:p-5 flex flex-col gap-3.5'

def chip(text, tone):
    c = {'req': '!bg-[var(--ev-accent)] !text-white',
         'rec': '!bg-[var(--ev-accent)]/[0.14] !text-[var(--ev-accent)]',
         'opt': '!bg-[var(--ev-text)]/[0.08] opacity-70'}[tone]
    return {'el': 'text', 'value': text,
            'className': '!text-[12px] font-black px-2.5 py-1 rounded-full shrink-0 whitespace-nowrap ' + c}

def head(num, title, sub, tag):
    return {'el': 'row', 'className': 'items-center gap-3 mb-1', 'style': {'flexWrap': 'nowrap'}, 'card': [
        {'el': 'box',
         'className': 'w-[34px] h-[34px] rounded-full flex items-center justify-center shrink-0 ring-4 ring-[var(--ev-accent)]/15',
         'style': {'background': 'linear-gradient(135deg, var(--ev-accent), color-mix(in srgb, var(--ev-accent) 72%, #1e3a8a))'},
         'card': [{'el': 'text', 'value': num, 'className': '!text-[18px] font-black !text-white'}]},
        {'el': 'box', 'className': 'flex-1 min-w-0 flex flex-col gap-0.5', 'card': [
            {'el': 'row', 'className': 'items-center gap-2', 'style': {'flexWrap': 'nowrap'}, 'card': [
                {'el': 'text', 'value': title,
                 'className': '!text-[20px] min-[640px]:!text-[19px] font-black !text-[var(--ev-text)] leading-tight'},
                tag]},
            {'el': 'text', 'value': sub,
             'className': '!text-[14px] min-[640px]:!text-[13px] opacity-60 leading-relaxed'}]}]}

def relabel(node, label, placeholder=None):
    n = copy.deepcopy(node)
    if placeholder is not None and 'placeholder' in n: n['placeholder'] = placeholder
    return {'el': 'box', 'className': 'flex flex-col gap-2', 'card': [
        {'el': 'text', 'value': label, 'className': LBL}, n]}

# ═══ ① งานนี้ทำอะไร ═══
S1 = {'el': 'box', 'className': BOX, 'card': [
    head('1', 'งานนี้ทำอะไร', 'บอกสั้น ๆ ว่าจะทำอะไรกับพื้นที่ไหน — หมีใช้ประโยคนี้ตั้งต้นทั้งเรื่อง', chip('บังคับ', 'req')),
    copy.deepcopy(f_name) | {'placeholder': 'เช่น จัดครัวใหม่ · ล้างแอร์ · ถางหญ้าหน้าบ้าน · ปลูกผักสลัดในระเบียง'},
]}

# ═══ ② พื้นที่ ═══
S2 = {'el': 'box', 'className': BOX, 'card': [
    head('2', 'พื้นที่ที่จะถ่าย', 'แนบรูปจริงได้ = หมีล็อกให้เป็นที่เดิมทุกฉาก · ไม่มีรูปก็ได้ หมีสร้างให้จากคำบรรยาย', chip('แนะนำอย่างยิ่ง', 'rec')),
    roomTiles,
    relabel(f_room, 'พื้นที่นี้หน้าตาเป็นยังไง', 'เช่น ครัวเล็กผนังขาว ตู้ไม้อ่อน หน้าต่างบานใหญ่ทางซ้าย'),
]}

# ═══ ③ ก่อน → หลัง ═══
S3 = {'el': 'box', 'className': BOX, 'card': [
    head('3', 'ก่อน → หลัง', 'หัวใจของคลิป — ยิ่งบอก "ก่อน" ชัด คนดูยิ่งเห็นการเปลี่ยนแปลงชัด', chip('แนะนำอย่างยิ่ง', 'rec')),
    relabel(f_before, 'ตอนนี้สภาพเป็นยังไง', 'เช่น เคาน์เตอร์รก จานชามกองรวมกัน พื้นยังไม่ได้ทำความสะอาด'),
    relabel(f_goal, 'อยากให้จบแบบไหน', 'เช่น ครัวโล่ง หยิบของง่าย ดูสบายตา'),
]}

# ═══ ④ ของที่จะใช้ (ไม่บังคับ) ═══
S4 = {'el': 'box', 'className': BOX, 'card': [
    head('4', 'ของที่จะใช้', 'ชั้นวาง กล่อง ต้นไม้ อุปกรณ์ — แนบรูปแล้วหมีล็อกให้เหมือนของจริง 100%', chip('ไม่บังคับ', 'opt')),
    {'el': 'text',
     'value': 'งานที่ไม่มีของหลัก (ล้างบ้าน · ถางหญ้า · ขัดพื้น · ทาสี) ข้ามหัวข้อนี้ไปได้เลย',
     'className': '!text-[13.5px] min-[640px]:!text-[13px] opacity-55 leading-relaxed -mt-1'},
    prodTiles,
    relabel(f_desc, 'ของชิ้นนี้คืออะไร — จุดเด่น / ขนาด / วัสดุ',
            'เช่น ชั้นเหล็กพ่นสีขาว 4 ชั้น รับน้ำหนักชั้นละ 8 กก. ประกอบเองได้'),
]}

# ═══ ⑤ ขั้นสูง ═══
adv_children = [c for c in advGrp.get('card', [])]
extra = []
for f, lab, ph in [('idea', 'ไอเดียเพิ่มเติมที่อยากให้มี', 'เช่น ฟีลเช้าวันหยุด · เน้นมุมริมหน้าต่าง'),
                   ('tone', 'โทน/บรรยากาศของงานนี้', 'เช่น โทนไม้อุ่น · ขาวสะอาด (ว่าง = ใช้ของโปรเจกต์)'),
                   ('price', 'ราคา', '฿390')]:
    src = f_price if f == 'price' else None
    base = copy.deepcopy(src) if src else {'el': 'input', 'field': f,
                                           'className': '!h-14 !px-4 !rounded-xl !text-[19px] min-[640px]:!text-[18px]'}
    base['field'] = f
    extra.append(relabel(base, lab, ph))
S5 = {'el': 'group', 'collapsible': True, 'startOpen': False,
      'className': '!rounded-2xl !p-4 min-[640px]:!p-5 bg-[var(--ev-surface)] !border-[var(--ev-border)]',
      'head': [{'el': 'icon', 'icon': 'tune', 'textSize': 'text-[18px]',
                'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center'},
               {'el': 'text', 'value': 'ขั้นสูง — ไอเดีย · โทน · ราคา · โปรโมชั่น · CTA',
                'className': '!text-[17px] min-[640px]:!text-[16px] font-black !text-[var(--ev-text)]'}],
      'card': extra + adv_children}

node[key] = [header, S1, S2, S3, S4, S5, footer]

# ═══ ปลดกฎ "บังคับรูปของหลัก" (มรดกจาก minimal ที่เป็นแอปขายของ) ═══
HARD = {'op': 'or', 'list': [
    {'op': 'eq', 'a': {'op': 'count', 'from': 'products', 'where': 'enabled=true'}, 'b': 0},
    {'op': 'not', 'a': {'op': 'eq',
                        'a': {'op': 'count', 'from': 'products', 'where': 'enabled=true'},
                        'b': {'op': 'count', 'from': 'products', 'where': 'enabled=true', 'slot': 'image'}}}]}
SOFT = {'op': 'eq', 'a': {'op': 'count', 'from': 'products', 'where': 'enabled=true'}, 'b': 0}
n_gate = 0
def ungate(n):
    global n_gate
    if isinstance(n, dict):
        for k, v in list(n.items()):
            if v == HARD: n[k] = copy.deepcopy(SOFT); n_gate += 1
            else: ungate(v)
        if n.get('reason') in ('ทุกงานที่ใช้ต้องมีรูปของหลักก่อน', 'เพิ่ม/ติ๊กใช้งาน + ใส่รูปของหลักให้ครบก่อน'):
            n['reason'] = 'เพิ่มงานอย่างน้อย 1 งาน แล้วติ๊ก "ใช้" ก่อน'
    elif isinstance(n, list):
        for v in n: ungate(v)
ungate(cfg['phases'])

# การ์ดเตือน: จากบังคับ → คำแนะนำนุ่ม ๆ และย้ายไปดู "รูปพื้นที่" แทน
def soften(n):
    if isinstance(n, dict):
        for k, v in list(n.items()):
            if isinstance(v, str):
                n[k] = (v.replace('มีงานที่เลือกใช้แต่ยังไม่มีรูป — ใส่รูปของหลักก่อน (สูตรล็อกหน้าตาของตามรูปจริง)',
                                  'บางงานยังไม่มีรูปพื้นที่ — หมีจะสร้างพื้นที่ให้เอง ผลอาจไม่ตรงบ้านจริง (แนบรูปได้ที่หัวข้อ 2)')
                          .replace('ยังไม่มีรูปของหลักที่จะใช้', 'ยังไม่ได้แนบรูป')
                          .replace('ต้องเลือกภาพอย่างน้อย 1 ภาพถึงจะผลิตได้',
                                   'ไม่บังคับ — แต่แนบรูปจริงแล้วผลลัพธ์ตรงกว่ามาก'))
            else: soften(v)
    elif isinstance(n, list):
        for v in n: soften(v)
soften(cfg['phases'])
# การ์ดเตือนหน้าตั้งค่า: เช็ค slot image → เปลี่ยนเป็น room1
s = json.dumps(cfg['phases'], ensure_ascii=False)
s = s.replace('"where": "enabled=true", "slot": "image"}}}]}, "className": "flex flex-row',
              '"where": "enabled=true", "slot": "room1"}}}]}, "className": "flex flex-row')
cfg['phases'] = json.loads(s)

json.dump(cfg, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'✓ v6 UX → {os.path.getsize(P)} bytes · ปลด hard-gate {n_gate} จุด · หน้าเพิ่มงาน = {len(node[key])} บล็อก')

# ═══════ v6b — เก็บรายละเอียดหลังดูจริงบนจอ ═══════
cfg = json.load(open(P, encoding='utf-8'))
node, key = find_list(cfg['phases'][0]['form'][2], '{item.slots.image}')
CARD = node[key]
S2, S4 = CARD[2], CARD[4]

def pull_amber(container):
    """ถอดการ์ดเตือนเหลืองออกจากแถวไทล์ แล้วคืนตัวที่ถอดออกมา"""
    for blk in container['card']:
        if isinstance(blk, dict) and isinstance(blk.get('card'), list):
            for i, c in enumerate(blk['card']):
                if 'amber' in json.dumps(c, ensure_ascii=False):
                    return blk['card'].pop(i)
    return None

amber = pull_amber(S4)          # ① หัวข้อ 4 บอก "ไม่บังคับ" → ห้ามมีการ์ดเตือน

# ② ย้ายไปหัวข้อ 2 (พื้นที่) ในโทน "ข้อมูล" ไม่ใช่ "เตือน" + ผูก when กับ room1
if amber:
    a = json.dumps(amber, ensure_ascii=False)
    a = (a.replace('amber-500', 'var(--ev-accent)').replace('amber-600', 'var(--ev-accent)')
           .replace('"icon": "warning"', '"icon": "lightbulb"')
           .replace('{item.slots.image}', '{item.slots.room1}')
           .replace('ยังไม่ได้แนบรูป', 'ยังไม่ได้แนบรูปพื้นที่')
           .replace('ไม่บังคับ — แต่แนบรูปจริงแล้วผลลัพธ์ตรงกว่ามาก',
                    'ไม่บังคับ — ไม่มีรูป หมีจะจินตนาการพื้นที่ให้จากคำบรรยาย แต่แนบรูปจริงแล้วตรงบ้านกว่ามาก'))
    amber = json.loads(a)
    for blk in S2['card']:
        if isinstance(blk, dict) and 'flex flex-row flex-wrap' in str(blk.get('className', '')):
            blk['card'].append(amber); break

# ③ ป้ายบอกจำนวนรูปเหนือแถวไทล์
def tile_label(sec, text):
    for i, blk in enumerate(sec['card']):
        if isinstance(blk, dict) and 'flex flex-row flex-wrap' in str(blk.get('className', '')):
            sec['card'].insert(i, {'el': 'text', 'value': text, 'className': LBL}); return
tile_label(S2, 'รูปพื้นที่จริง (สูงสุด 2 รูป)')
tile_label(S4, 'รูปของ (สูงสุด 5 มุม)')

json.dump(cfg, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✓ v6b → ถอดการ์ดเตือนออกจากหัวข้อ 4 · ย้ายเป็นคำแนะนำในหัวข้อ 2 · เพิ่มป้ายจำนวนรูป')
