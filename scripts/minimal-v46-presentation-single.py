#!/usr/bin/env python3
"""minimal v46 — ตัดการ์ด "มุมกล้อง & การนำเสนอ รายฉาก (ขั้นสูง)" ออกจากหน้าตั้งค่า (พี่หมีเคาะ 2026-09-25)

มาตรฐานเดียวกับ showhow v82 (`easybear-showhow/docs/SETTINGS-MOVE-SPEC.md`):
  · มุมกล้อง  → ตัดหมดจากหน้าตั้งค่า · แก้รายฉากในหน้าผลิต (ช่อง cam1-15 ของ task มีอยู่แล้ว ตัวเลือก 12 ตัวเดียวกัน)
  · การนำเสนอ → ยุบ 5 ช่อง (svPres1-5) เหลือช่องเดียว = การ์ดปกติระดับเดียวกับ "โทนสีคลิป"
                  ใช้ชื่อ field `svPres1` เดิม ⇒ ไฟล์เซฟเก่าที่ตั้งองก์ 1 ไว้ ค่าจะติดมาเอง

ของที่ไม่แตะ: prompt บอร์ด/วิดีโอ (อ่าน item.camN อยู่แล้ว ไม่เคยอ่าน svCam) · ป้ายองก์ lenAct (บอก AI ว่าองก์ไหนกินฉากไหน)
รันซ้ำได้ — รอบที่ 2 จะบอกว่าแพตช์แล้วแล้วออก
"""
import json, re, sys, copy, os

PATH = os.path.join(os.path.dirname(__file__), '..', 'minimal-dev.json')
cfg = json.load(open(PATH, encoding='utf-8'))
orig = copy.deepcopy(cfg)

def refs(n, pat=re.compile(r'sv(Cam|Pres)\d')):
    out = []
    def w(x, p):
        if isinstance(x, dict):
            for k, v in x.items():
                if pat.search(k): out.append(p + '/' + k)
                w(v, p + '/' + k)
        elif isinstance(x, list):
            for i, v in enumerate(x): w(v, p + '/%d' % i)
        elif isinstance(x, str) and pat.search(x): out.append(p)
    w(n, ''); return out

cards = cfg['phases'][0]['form'][0]['card'][0]['card'][2]['card']
adv = cards[4]
if 'มุมกล้อง & การนำเสนอ รายฉาก' not in json.dumps(adv, ensure_ascii=False):
    if any(r.startswith('/values/svCam') for r in refs(cfg)):
        sys.exit('🔴 การ์ด [4] ไม่ใช่การ์ดขั้นสูง แต่ยังมี svCam ค้าง — โครงเปลี่ยน ต้องดูด้วยตา')
    print('✓ แพตช์แล้ว (v46) — ไม่มีอะไรต้องทำ'); sys.exit(0)

before = refs(cfg)
assert len(before) == 25, 'คาด svCam/svPres 25 จุด (values 10 + prompt 5 + UI 10) เจอ %d' % len(before)

# ── ① UI: แทนการ์ดขั้นสูงด้วยการ์ดปกติ 1 ช่อง ─────────────────────────────
tpl = cards[1]                                  # การ์ดปกติที่มี mt-2 (ตัวละคร) — ยืม className หัวการ์ด
row_tpl, desc_tpl = tpl['card'][0], tpl['card'][1]
assert row_tpl['el'] == 'row' and desc_tpl['el'] == 'text'
pres = None
def find(x):
    global pres
    if isinstance(x, dict):
        if x.get('field') == 'svPres1': pres = x
        for v in x.values(): find(v)
    elif isinstance(x, list):
        for v in x: find(v)
find(adv)
assert pres and len(pres['options']) == 11, 'ต้องเจอ dropdown svPres1 ตัวเลือก 11 ตัว'

row = copy.deepcopy(row_tpl)
icon = next(e for e in row['card'] if e['el'] == 'icon'); icon['icon'] = 'auto_awesome_mosaic'
title = next(e for e in row['card'] if e['el'] == 'text'); title['value'] = 'การนำเสนอสินค้า'
row['card'] = [icon, title]
desc = copy.deepcopy(desc_tpl)
desc['value'] = 'แนวการนำเสนอหลักของทุกคลิป — มุมกล้องหมีเลือกให้รายฉาก แล้วปรับเองได้ทีละฉากในหน้าผลิต'
foot = {'el': 'text', 'value': 'ไม่เลือก = หมีเลือกให้เข้ากับสินค้า',
        'className': cards[0]['card'][-1]['className']}
assert cards[0]['card'][-1]['el'] == 'text'
cards[4] = {'el': 'box', 'className': 'flex flex-col gap-2 mt-2',
            'card': [row, desc, copy.deepcopy(pres), foot]}

# ── ② mnPlan: ป้ายองก์คงไว้ · ตัดท่อนมุมกล้อง/การนำเสนอรายองก์ · เพิ่มบรรทัดการนำเสนอหลัก (มีเมื่อเลือก) ──
mn = next(o for o in cfg['ops'] if o['id'] == 'mnPlan')
ps = mn['prompt']['parts'][0]['parts']
assert ps[1].get('table') == 'lenActHead' and ps[12].get('table') == 'lenActTail'
for n, i in enumerate((3, 5, 7, 9, 11), 1):
    assert ps[i] == ' — มุมกล้อง: {values.svCam%d} · การนำเสนอ: {values.svPres%d}\n' % (n, n), ps[i]
    ps[i] = '\n'
HEAD10 = '\n\nโครง 5 ฉาก (มุมกล้องและการจัดภาพของแต่ละฉาก ออกแบบเองให้เข้ากับสินค้า):\n'
HEADN = '\n\nโครง 5 องก์ (มุมกล้องและการจัดภาพของแต่ละฉาก ออกแบบเองให้เข้ากับสินค้า):\n'
ps[1]['fallback'] = HEAD10
ps.insert(12, {'op': 'block', 'sep': '', 'parts': [{
    'when': {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svPres1}', 'b': ''}},
    'value': 'แนวการนำเสนอหลักที่ผู้ใช้เลือก (ใช้กับทุกคลิป): {values.svPres1} — ใช้เป็นแกนของทุกฉาก แต่ปรับให้เข้ากับหน้าที่ของแต่ละฉาก\n'}]})

lk = cfg['lookups']
lk['lenActHead'] = {'10': HEAD10, '20': HEADN, '30': HEADN}
TAIL = 'ฉากในองก์เดียวกันต้องเล่าต่อเนื่องกัน แต่เปลี่ยนมุมกล้อง ระยะ การเคลื่อนไหว และองค์ประกอบให้ไม่ซ้ำกัน\n'
assert 'ผู้ใช้ล็อกไว้' in lk['lenActTail']['20']
lk['lenActTail'] = {'10': '', '20': TAIL, '30': TAIL}

# ── ②ข brain.mn.sys: กฎ 3 ท่อนที่พูดถึง "ฉากที่ผู้ใช้ล็อกมุมกล้อง/การนำเสนอไว้" (ยามจับได้ตอนรันรอบแรก)
#    ปล่อยไว้ = AI ถูกสั่งให้ทำตามค่าที่ไม่มีใครส่งมาแล้ว · ถ้อยคำใหม่ยังบอกว่าแนวการนำเสนอหลักต้องเห็นจริงในบท
SYS_FIX = [
    ('ข้อกำหนดรายฉากจากผู้ใช้ (มุมกล้อง / การนำเสนอ): ถ้าผู้ใช้ระบุมา ต้องทำตามอย่างเคร่งครัดทุกคลิป และสะท้อนให้เห็นจริงใน s*th กับ s*en · ค่าว่าง = ออกแบบเองให้เหมาะกับสินค้า',
     'แนวการนำเสนอหลักจากผู้ใช้: ถ้าผู้ใช้ระบุมา ต้องสะท้อนให้เห็นจริงใน s*th กับ s*en ทุกคลิป · ค่าว่าง = ออกแบบเองให้เหมาะกับสินค้า'),
    ('(ยกเว้นฉากที่ผู้ใช้ล็อกมุมกล้อง/การนำเสนอไว้ ให้ทำตามที่ล็อกทุกคลิป แล้วสร้างความต่างจากรายละเอียดอื่น)',
     '(แนวการนำเสนอหลักที่ผู้ใช้เลือก ให้คงไว้ทุกคลิป แล้วสร้างความต่างจากรายละเอียดอื่น)'),
    (' — ฉากที่ผู้ใช้ล็อกมุมกล้องไว้ camN ต้องตรงกับที่ล็อกทุกคลิป ฉากที่ไม่ล็อกให้เลือกเองตามจังหวะเรื่อง',
     ' — เลือกเองตามจังหวะเรื่อง'),
]
sysmsg = cfg['brain']['mn']['sys']
for old, new in SYS_FIX:
    assert sysmsg.count(old) == 1, 'sys ไม่เจอท่อน: ' + old[:40]
    sysmsg = sysmsg.replace(old, new)
cfg['brain']['mn']['sys'] = sysmsg

# ── ③ values: เหลือ svPres1 ตัวเดียว ─────────────────────────────────────
for k in ['svCam%d' % n for n in range(1, 6)] + ['svPres%d' % n for n in range(2, 6)]:
    assert cfg['values'][k] == '', k
    del cfg['values'][k]

# ── ยาม ──────────────────────────────────────────────────────────────────
after = refs(cfg)
print('svCam/svPres ที่เหลือ:', len(after), 'จุด', after)
assert all('svPres1' in r or r.endswith('/field') or '/parts/' in r for r in after)
s = json.dumps(cfg, ensure_ascii=False)
assert 'svCam' not in s, 'ยังมี svCam ค้าง'
for n in range(2, 6): assert 'svPres%d' % n not in s
assert s.count('{values.svPres1}') == 2       # when + ข้อความ
assert s.count('"field": "svPres1"') == 1
assert 'ผู้ใช้ล็อกไว้' not in s and 'ข้อกำหนดราย' not in s and 'ล็อกมุมกล้อง' not in s and 'ล็อกไว้ camN' not in s
# ของที่ต้องไม่ขยับเลย: op อื่นทุกตัว + lookups อื่นทุกตัว + ป้ายองก์
for o_old, o_new in zip(orig['ops'], cfg['ops']):
    if o_old['id'] != 'mnPlan': assert o_old == o_new, 'op %s ขยับ' % o_old['id']
assert {k: v for k, v in orig['lookups'].items() if k not in ('lenActHead', 'lenActTail')} == \
       {k: v for k, v in cfg['lookups'].items() if k not in ('lenActHead', 'lenActTail')}
assert orig['lookups']['lenAct'] == cfg['lookups']['lenAct']
unchanged = [k for k in orig if k not in ('ops', 'lookups', 'values', 'phases', 'brain')]
assert orig['brain']['mn']['imgNote'] == cfg['brain']['mn']['imgNote'] and set(orig['brain']) == set(cfg['brain'])
assert all(orig[k] == cfg[k] for k in unchanged)
o2, c2 = copy.deepcopy(orig), copy.deepcopy(cfg)
o2['phases'][0]['form'][0]['card'][0]['card'][2]['card'][4] = None
c2['phases'][0]['form'][0]['card'][0]['card'][2]['card'][4] = None
assert o2['phases'] == c2['phases'], 'หน้าอื่นขยับ'

json.dump(cfg, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('✅ v46 เขียนแล้ว · ตัด svCam 15 จุด + svPres2-5 12 จุด · เหลือ svPres1 = UI 1 + prompt 2 (when+ข้อความ) + values 1')
