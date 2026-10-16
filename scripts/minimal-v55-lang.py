#!/usr/bin/env python3
"""minimal v55 — ภาษา [ไทย / อังกฤษ] (พี่หมีสั่ง 2026-10-16: "เลือกอังกฤษ เสียงพากย์และข้อความจะเป็นอังกฤษหมด")

ต่างจาก showhow `svLang` (ของเขาเปลี่ยนแค่เสียงพากย์) — minimal เปลี่ยนทั้ง vo (เสียงพากย์) และ ov (ข้อความบนภาพ)
ส่วนที่ "ยังเป็นไทย" โดยตั้งใจ: s*th (บทภาพในสตอรีบอร์ดให้ผู้ใช้อ่าน) · synopsis · camN (ป้ายมุมกล้องในบอร์ด) · UI ทั้งหมด

แก้ (config ล้วน · ไม่แตะ engine):
  ① values.svLang ('ไทย' ปริยาย) · UI หัวข้อใหม่ "ภาษาเสียงพากย์และข้อความ" ก่อนหัวข้อข้อความบนคลิป
  ② ทุกชิ้นของ prompt (บท/บอร์ด/วิดีโอ) ที่ผูกกับภาษาไทย ห่อด้วย block 2 ทาง: ไม่ใช่ English = ของเดิมทุกตัวอักษร · English = ฉบับอังกฤษ
       ชิ้นข้อความ → แทนคำตามตาราง REPL (ห้ามแทนแบบ substring ลอย ๆ — แต่ละคู่ assert ว่าเจอจริง)
       lookup ที่มีกฎภาษา → ตาราง *EN คู่กัน (voicePlan/voiceVideoEN/voiceLockEN/lenVo/lenOut)
       {brain.mn.sys} → {brain.mn.sysEN} (แก้เฉพาะบรรทัดกฎ ov/vo)
       {values.svText} (คำบรรยายฟอนต์ไทย) → lookup svTextEN
  ③ ท้าย sys เพิ่มบรรทัดย้ำภาษา (เฉพาะ English)
  🛡 svLang ว่าง/ไทย/ไฟล์เซฟเก่า = prompt เดิมทุกไบต์ (ยาม: scratch verify-lang.ts resolve จริงเทียบ)
รันซ้ำได้ (เจอ svLang แล้ว = ข้าม) · ต้องรันหลัง v54
"""
import json, os, re, copy

PATH = os.path.join(os.path.dirname(__file__), '..', 'minimal-dev.json')
cfg = json.load(open(PATH, encoding='utf-8'))
if 'svLang' in cfg['values']:
    print('⏭ v55 แพตช์ไปแล้ว — ไม่ทำซ้ำ'); raise SystemExit(0)
assert 'svCast' in cfg['values'], 'ต้องรัน v54 ก่อน'

EN_V = 'English'
EN = {'op': 'eq', 'a': '{values.svLang}', 'b': EN_V}
TH = {'op': 'not', 'a': EN}
L = cfg['lookups']

# ── ตารางคำแทน (ชิ้นข้อความใน prompt) · ตัวนับยืนยันว่าทุกคู่ถูกใช้จริง
REPL = [
    (' Thai overlay: "', ' Overlay: "'),
    # 'the Thai narration' / 'warm friendly Thai ' อยู่ใน fallback ของ lookup เสียง — แปลงผ่าน TABLE_EN
    ('Voice-over script (Thai):', 'Voice-over script (English):'),
    ('max 5 Thai words', 'max 5 English words'),
    ("each scene's quoted Thai overlay", "each scene's quoted English overlay"),
    ('non-Thai text', 'misspelled text'),
    ('(4) บทพูด VO ภาษาไทย', '(4) บทพูด VO ภาษาอังกฤษ'),
    ('ข้อความในคอลัมน์ (3) และ (4) ต้องเป็นภาษาไทยตามบทที่ให้ ห้ามแปลเป็นภาษาอังกฤษ',
     'ข้อความคอลัมน์ (3) เป็นภาษาไทย · คอลัมน์ (4) และ Overlay เป็นภาษาอังกฤษตามบทที่ให้ ห้ามแปล'),
    ('ไม่เกิน 5 คำไทยต่อช่อง', 'ไม่เกิน 5 คำอังกฤษต่อช่อง'),
    ('ตัวหนังสือ overlay ภาษาไทยต้อง', 'ตัวหนังสือ overlay ภาษาอังกฤษต้อง'),
    ('ห้ามพิมพ์ชื่อหัวข้อภาษาอังกฤษหรือบรรทัดบอกสไตล์ลงในภาพ', 'ห้ามพิมพ์ชื่อหัวข้อหรือบรรทัดบอกสไตล์ลงในภาพ'),
    ('{brain.mn.sys}', '{brain.mn.sysEN}'),
    ('ย้ำเรื่องคำลงท้าย: ครับ / ค่ะ / คะ ใช้ได้อย่างมาก 2 ครั้งต่อคลิป (แนะนำครั้งเดียวที่ vo5) — vo2-vo4 จบห้วนไม่มีคำลงท้าย',
     'ย้ำเรื่องภาษา: ov และ vo ทุกฉากเป็นภาษาอังกฤษ ห้ามมีอักษรไทย ไม่มีคำลงท้าย ครับ/ค่ะ'),
]
used = {a: 0 for a, _ in REPL}

SVTEXT_EN = {
    'ตัวอักษรลายมือภาษาไทยเส้นโค้งนุ่มหัวกลม (cute Thai handwritten script) สีขาว มีเงานุ่มรองรับ (soft shadow) + doodle ลายเส้นวาดมือเล็กๆ':
        'cute rounded handwritten English script, white with a soft shadow + small hand-drawn doodles',
    'ตัวอักษรซานเซอริฟเส้นบางเรียบสะอาด (clean thin sans-serif)': 'clean thin sans-serif English lettering',
    'ตัวอักษรหนาใหญ่ชัดเจน (bold modern typography)': 'bold modern English typography',
}
svtext_opts = []
def find_opts(x):
    if isinstance(x, dict):
        if x.get('field') == 'svText': svtext_opts.extend(o['value'] for o in x['options'])
        for v in x.values(): find_opts(v)
    elif isinstance(x, list):
        for v in x: find_opts(v)
find_opts(cfg['phases'])
assert sorted(svtext_opts) == sorted(SVTEXT_EN), svtext_opts
L['svTextEN'] = SVTEXT_EN
SVTEXT_LK = {'op': 'lookup', 'table': 'svTextEN', 'key': '{values.svText}', 'fallback': SVTEXT_EN[svtext_opts[0]]}


def en_text(s):
    """ข้อความ → ฉบับอังกฤษ (str หรือ concat ถ้ามี {values.svText})"""
    t = s
    for a, b in REPL:
        if a in t:
            used[a] += 1; t = t.replace(a, b)
    if '{values.svText}' in t:
        bits = t.split('{values.svText}')
        parts = []
        for i, b in enumerate(bits):
            if b: parts.append(b)
            if i < len(bits) - 1: parts.append(copy.deepcopy(SVTEXT_LK))
        return {'op': 'concat', 'parts': parts}
    return t


def fork(old, new):
    return {'op': 'block', 'sep': '', 'parts': [{'when': TH, 'value': old}, {'when': EN, 'value': new}]}


# ── ตาราง *EN
def lenvo_en(v):
    def r(m):
        lo, hi = int(m.group(1)), int(m.group(2))
        n = lo // 5   # จำนวนฉาก (5-7 คำ/ฉาก)
        return 'ฉากละ 4-6 คำภาษาอังกฤษ รวมทั้งคลิป %d-%d คำ' % (4 * n, 6 * n)
    out, k = re.subn(r'ฉากละ 5-7 คำไทย รวมทั้งคลิป (\d+)-(\d+) คำ', r, v)
    assert k == 1, v[:120]
    return out
def lenout_en(v):
    out, k = re.subn(r'ovN ทุกตัวเป็นภาษาไทย', 'ovN ทุกตัวเป็นภาษาอังกฤษ ห้ามมีอักษรไทย', v)
    assert k == 1, v[:120]
    return out
GENDER_PRES = {
    'เสียงผู้หญิง': ' · ถ้าโหมดมีพรีเซนเตอร์และผู้ใช้ไม่ได้ระบุเพศพรีเซนเตอร์ ให้พรีเซนเตอร์เป็นผู้หญิงเพื่อให้ตรงกับเสียง · ใส่ค่า "หญิง" ในฟิลด์ voice ของทุกคลิป',
    'เสียงผู้ชาย': ' · ถ้าโหมดมีพรีเซนเตอร์และผู้ใช้ไม่ได้ระบุเพศพรีเซนเตอร์ ให้พรีเซนเตอร์เป็นผู้ชายเพื่อให้ตรงกับเสียง · ใส่ค่า "ชาย" ในฟิลด์ voice ของทุกคลิป',
}
VOICEPLAN_EN = {
    'เสียงผู้หญิง': 'เสียงพากย์ของคลิปนี้เป็น "ผู้หญิง" พูดภาษาอังกฤษ — vo ทุกฉากเขียนเป็นภาษาอังกฤษ ไม่มีคำลงท้ายภาษาไทย' + GENDER_PRES['เสียงผู้หญิง'],
    'เสียงผู้ชาย': 'เสียงพากย์ของคลิปนี้เป็น "ผู้ชาย" พูดภาษาอังกฤษ — vo ทุกฉากเขียนเป็นภาษาอังกฤษ ไม่มีคำลงท้ายภาษาไทย' + GENDER_PRES['เสียงผู้ชาย'],
    'สุ่มตามสินค้า': 'ผู้ใช้ให้คุณเลือกเพศเสียงพากย์เอง — พิจารณาจากหมวดสินค้าและกลุ่มลูกค้าเป้าหมาย แล้วเขียนผลลงฟิลด์ voice เป็นคำว่า "หญิง" หรือ "ชาย" เท่านั้น · vo เป็นภาษาอังกฤษ ไม่มีคำลงท้ายภาษาไทย · ในคลิปหนึ่งต้องเพศเดียวตลอด · ถ้าโหมดมีพรีเซนเตอร์และผู้ใช้ไม่ได้ระบุเพศพรีเซนเตอร์ ให้พรีเซนเตอร์เป็นเพศเดียวกับเสียงที่เลือก',
}
assert sorted(VOICEPLAN_EN) == sorted(L['voicePlan'])
for k in VOICEPLAN_EN:   # ท่อนท้ายต้องยกมาจากของเดิมจริง
    if k in GENDER_PRES: assert GENDER_PRES[k].split(' · ', 1)[1] in L['voicePlan'][k], k
L['voicePlanEN'] = VOICEPLAN_EN
L['voiceVideoEN_EN'] = {k: v.replace('Thai ', 'English ') for k, v in L['voiceVideoEN'].items()}
L['voiceLockEN_EN'] = {k: v.replace('the Thai narration', 'the English narration') for k, v in L['voiceLockEN'].items()}
for t in ('voiceVideoEN_EN', 'voiceLockEN_EN'):
    assert all('Thai' not in v and 'English' in v for v in L[t].values()), t
L['lenVoEN'] = {k: lenvo_en(v) for k, v in L['lenVo'].items()}
L['lenOutEN'] = {k: lenout_en(v) for k, v in L['lenOut'].items()}
TABLE_EN = {'voicePlan': ('voicePlanEN', lambda fb: VOICEPLAN_EN['เสียงผู้หญิง']),
            'voiceVideoEN': ('voiceVideoEN_EN', lambda fb: fb.replace('Thai ', 'English ')),
            'voiceLockEN': ('voiceLockEN_EN', lambda fb: fb.replace('the Thai narration', 'the English narration')),
            'lenVo': ('lenVoEN', lenvo_en), 'lenOut': ('lenOutEN', lenout_en)}
n_lk = {t: 0 for t in TABLE_EN}

# ── brain
b = cfg['brain']['mn']['sys'].split('\n')
assert b[13] == '- 2-6 คำไทยต่อฉาก สั้น กระชับ เน้น benefit'
assert b[15].startswith('- ห้าม emoji · ห้ามภาษาอังกฤษปน')
assert b[20].startswith('- คำลงท้ายและสรรพนาม') and b[21].startswith('- คำลงท้าย (ครับ') and b[22].startswith('- ประโยคที่ไม่มีคำลงท้าย')
assert b[23].startswith('- ฟิลด์ voice = เพศเสียงพากย์')
e = list(b)
e[13] = '- 2-6 คำภาษาอังกฤษต่อฉาก สั้น กระชับ เน้น benefit'
e[15] = '- ห้าม emoji · ov1-ov5 เขียนเป็นภาษาอังกฤษทั้งหมด ห้ามมีอักษรไทย (ชื่อสินค้าภาษาไทยให้ทับศัพท์หรือแปลเป็นอังกฤษ)'
e[20] = '- vo เขียนเป็นภาษาอังกฤษที่เป็นธรรมชาติทั้งหมด ห้ามมีอักษรไทย ไม่มีคำลงท้าย ครับ/ค่ะ · ประโยคสั้นกระชับแบบโฆษณา'
e[23] = '- ฟิลด์ voice = เพศเสียงพากย์ของคลิปนั้น เขียนว่า "หญิง" หรือ "ชาย" เท่านั้น'
del e[21:23]
cfg['brain']['mn']['sysEN'] = '\n'.join(e)


# ── เดิน prompt
SKIP = {'when', 'key', 'table', 'op', 'any', 'fallback'}
def visit(node):
    """คืน node ใหม่ (ห่อ fork ถ้าภาษามีผล) · แก้ลูกในที่"""
    if isinstance(node, str):
        new = en_text(node)
        return node if new == node else fork(node, new)
    if isinstance(node, list):
        return [visit(x) for x in node]
    if not isinstance(node, dict):
        return node
    if node.get('op') == 'lookup' and node['table'] in TABLE_EN:
        t2, fbf = TABLE_EN[node['table']]; n_lk[node['table']] += 1
        en = dict(node, table=t2, fallback=fbf(node.get('fallback', '')))
        return fork(node, en)
    if node.get('op') == 'matchTable':   # ค่าใน table เป็น key ของ lookup ชั้นใน — ห้ามแตะ
        return node
    out = {}
    for k, v in node.items():
        out[k] = v if k in SKIP else visit(v)
    return out

ops = {o['id']: o for o in cfg['ops']}
ops['mnPlan']['systemInstruction'] = visit(ops['mnPlan']['systemInstruction'])
ops['mnPlan']['prompt'] = visit(ops['mnPlan']['prompt'])
for oid in ('mnBoard', 'mnBoard2', 'mnBoard3', 'mnVideo', 'mnVideo2', 'mnVideo3'):
    ops[oid]['prompt'] = visit(ops[oid]['prompt'])
missing = [a for a, n in used.items() if not n]
assert not missing, missing
assert all(n_lk.values()), n_lk
ops['mnPlan']['systemInstruction']['parts'].append(
    {'op': 'block', 'sep': '', 'parts': [{'when': EN, 'value': '\n\nภาษาของคลิป: English — ov และ vo ทุกฉากเป็นภาษาอังกฤษที่เป็นธรรมชาติ ห้ามมีอักษรไทย · synopsis, s*th และ camN ยังเป็นภาษาไทยตามเดิม · s*en เป็นภาษาอังกฤษตามเดิม'}]})

# ── UI
area = cfg['phases'][0]['form'][0]['card'][0]['card'][2]['card']
ovsec = area[2]
assert any(c.get('field') == 'svTextOn' for c in ovsec['card']), 'ตำแหน่งหัวข้อข้อความบนคลิปเปลี่ยน'
lang = copy.deepcopy(ovsec)
lang['card'] = copy.deepcopy(ovsec['card'][:2])
lang['card'][0]['card'][0]['icon'] = 'translate'
lang['card'][0]['card'][1]['value'] = 'ภาษาเสียงพากย์และข้อความ'
lang['card'][1]['value'] = 'เลือกอังกฤษ = เสียงพากย์และข้อความบนคลิปเป็นภาษาอังกฤษทั้งหมด (บทภาพในสตอรีบอร์ดยังเป็นไทย)'
sel = copy.deepcopy(next(c for c in ovsec['card'] if c.get('field') == 'svTextOn'))
sel.update(field='svLang', options=[{'value': 'ไทย', 'label': 'ไทย', 'desc': 'พากย์และข้อความภาษาไทย', 'icon': 'forum'},
                                    {'value': EN_V, 'label': 'อังกฤษ', 'desc': 'English voice-over & text', 'icon': 'translate'}])
lang['card'].append(sel)
area.insert(2, lang)
cfg['values']['svLang'] = 'ไทย'

json.dump(cfg, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('✅ v55 · ภาษา ไทย/อังกฤษ · คำแทน %d คู่ (ใช้ %d ครั้ง) · lookup EN %s' % (len(REPL), sum(used.values()), n_lk))
