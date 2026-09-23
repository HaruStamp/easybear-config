#!/usr/bin/env python3
"""showhow-v101 — เสียงพากย์เลือก "ภาษา" + "สำเนียง" ได้แบบ film (พี่หมีสั่ง 2026-09-24)

UI (หน้าตั้งค่า · กล่องที่โผล่เมื่อเลือก "มีเสียงพากย์"):
   เพศเสียงพากย์ (เดิม) → ภาษาพากย์ [ไทย | English] → สำเนียง (dropdown · เฉพาะภาษาไทย)
   สำเนียง 5 แบบของ film: มาตรฐาน · กรุงเทพ/วัยรุ่น · อีสาน · เหนือ · ใต้
   🚫 ไม่เอา "ดุดัน/ปากแสบ" กับ "หยาบคาย" ของ film — แอปนี้ขายของ/สาธิตงาน และคำหยาบเสี่ยงโดนตัวกรองของโมเดลวิดีโอ

prompt:
   mnPlan  (llm · ไม่โดนตัด): ต่อกฎภาษา/สำเนียงท้ายบล็อกเสียงพากย์ — English = เขียน vo เป็นอังกฤษ · สำเนียง = ใช้คำถิ่นพอให้รู้
   mnVideo* (เพดาน 3,900): 🔴 **แทนที่ ไม่ต่อท้าย** — คำว่า "Thai" ที่ฝังอยู่ 4 จุดในบล็อกเสียง ถูกยุบเหลือจุดเดียว
            ("continuous {ภาษา} narration") แล้วจุดนั้นเปลี่ยนตามภาษา/สำเนียง ⇒ ภาษาไทยมาตรฐานสั้นลง 31 ตัวอักษร
            สำเนียงที่ยาวสุดยาวกว่าเดิมไม่กี่ตัว (วัดด้วย G9)
value ใช้เป็นคีย์/เงื่อนไขเท่านั้น ไม่ถูกเสียบลง prompt ตรง ๆ
ใช้: python3 scripts/showhow-v101-voice-lang.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
J = lambda x: json.dumps(x, ensure_ascii=False)
L = c['lookups']
EN, STD = 'English', 'มาตรฐาน'


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


# ── values ──
c['values']['svLang'] = 'ไทย'
c['values']['svAccent'] = STD

# ── UI ──
box = next(n for n in walk(c['phases']) if isinstance(n, dict) and n.get('el') == 'box'
           and any(isinstance(x, dict) and x.get('field') == 'svVoice' for x in n.get('card', [])))
lab = box['card'][0]
assert lab['value'] == 'เพศเสียงพากย์'
gi = next(i for i, x in enumerate(box['card']) if x.get('field') == 'svVoice')
NOT_EN = {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svLang}', 'b': EN}}
box['card'][gi + 1:gi + 1] = [
    dict(lab, value='ภาษาพากย์', className=lab['className'] + ' mt-1'),
    {'el': 'grid-select', 'field': 'svLang', 'cols': 2, 'contained': True, 'options': [
        {'value': 'ไทย', 'label': 'ไทย', 'desc': 'พากย์ภาษาไทย', 'icon': 'forum'},
        {'value': EN, 'label': 'English', 'desc': 'พากย์ภาษาอังกฤษ', 'icon': 'translate'}],
     'className': '!min-h-[48px] @[420px]:!min-h-0'},
    dict(lab, value='สำเนียง', className=lab['className'] + ' mt-1', when=NOT_EN),
    {'el': 'dropdown', 'field': 'svAccent', 'when': NOT_EN, 'options': [
        {'value': STD, 'label': 'มาตรฐาน (สุภาพ)'},
        {'value': 'กรุงเทพ', 'label': 'กรุงเทพ / วัยรุ่น'},
        {'value': 'อีสาน', 'label': 'อีสาน'},
        {'value': 'เหนือ', 'label': 'เหนือ (คำเมือง)'},
        {'value': 'ใต้', 'label': 'ใต้'}],
     'className': '!min-h-[48px] @[420px]:!min-h-0'},
]
hint = box['card'][-1]
assert 'คิดบทใหม่' in hint['value']
hint['value'] = 'เปลี่ยนได้ทุกเมื่อ — ถ้าเปลี่ยนเพศ ภาษา หรือสำเนียงหลังคิดบทแล้ว ให้กด "คิดบทใหม่" ที่การ์ดงานก่อน · สำเนียงเห็นชัดที่คำพูดในบท ส่วนน้ำเสียงในวิดีโอขึ้นกับโมเดล'
print('UI: + ภาษาพากย์ (ไทย/English) · + สำเนียง 5 แบบ (เฉพาะไทย)')

# ── mnPlan: ต่อกฎภาษา/สำเนียง ──
L['accentPlan'] = {
    'กรุงเทพ': 'สำเนียงพากย์: กรุงเทพ/วัยรุ่น — เขียน vo แบบคนกรุงรุ่นใหม่คุยกับเพื่อน ภาษาพูดสบาย ๆ ใส่คำฮิตได้พอดี (เช่น ปังมาก ดีย์ เริ่ด) ห้ามหยาบ',
    'อีสาน': 'สำเนียงพากย์: อีสาน — เขียน vo เป็นภาษาไทยปนคำอีสานที่คนทั้งประเทศฟังเข้าใจ (เช่น บ่ หลาย แซบ เด้อ คือกัน) ไม่ต้องทุกคำ ให้ฟังออกว่าคนอีสานพูด',
    'เหนือ': 'สำเนียงพากย์: เหนือ (คำเมือง) — เขียน vo เป็นภาษาไทยปนคำเมืองที่คนทั่วไปฟังเข้าใจ (เช่น เจ้า ขนาด=มาก ลำ=อร่อย ก่อ) ไม่ต้องทุกคำ ให้ฟังออกว่าคนเหนือพูด',
    'ใต้': 'สำเนียงพากย์: ใต้ — เขียน vo เป็นภาษาไทยปนคำใต้ที่คนทั่วไปฟังเข้าใจ (เช่น หรอย จังหู้ ไม่หอ แหละ) ไม่ต้องทุกคำ ให้ฟังออกว่าคนใต้พูด',
}
LANG_EN = ('ภาษาพากย์: English — เขียน vo1-vo5 เป็นภาษาอังกฤษที่เป็นธรรมชาติ ราว 5 คำต่อฉาก 2 วินาที '
           '(กฎคำลงท้าย ค่ะ/ครับ ไม่ใช้ แต่เพศเสียงยังตามที่เลือก) · ฟิลด์อื่นเขียนตามเดิม')
plan = next(o for o in c['ops'] if o['id'] == 'mnPlan')
vb = next(n for n in walk(plan['prompt']) if isinstance(n, dict) and n.get('op') == 'concat'
          and isinstance(n.get('parts'), list) and n['parts'] and n['parts'][0] == '\n\nเสียงพากย์ของคลิป: {values.svVoice}\n')
vb['parts'].append({'op': 'block', 'sep': '', 'parts': [
    {'when': 'values.svLang=' + EN, 'value': '\n' + LANG_EN},
    {'when': {'op': 'and', 'list': [NOT_EN, {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svAccent}', 'b': STD}}]},
     'value': {'op': 'concat', 'parts': ['\n', {'op': 'lookup', 'table': 'accentPlan', 'key': '{values.svAccent}', 'fallback': ''}]}},
]})
print('mnPlan: + กฎภาษา English / สำเนียง 4 แบบ (มาตรฐาน = ไม่เพิ่มอะไร)')

# ── mnVideo*: ยุบ "Thai" 4 จุด → จุดเดียวที่เปลี่ยนตามภาษา ──
L['accentVideoEN'] = {STD: 'Thai', 'กรุงเทพ': 'casual youthful Bangkok Thai', 'อีสาน': 'Thai in a natural Isan accent',
                      'เหนือ': 'Thai in a natural Northern accent', 'ใต้': 'Thai in a natural Southern accent'}
LANG = {'op': 'block', 'sep': '', 'parts': [
    {'when': 'values.svLang=' + EN, 'value': 'English'},
    {'when': NOT_EN, 'value': {'op': 'lookup', 'table': 'accentVideoEN', 'key': '{values.svAccent}', 'fallback': 'Thai'}}]}
A0 = '\n\nAudio: continuous Thai narration for the whole clip — starts at 0.0s, no silent gaps between scenes or at the end. '
F_OLD = 'warm friendly Thai FEMALE voice-over — an adult woman speaking natural Thai with a soft feminine timbre (never a male voice)'
F_NEW = 'warm friendly FEMALE voice-over — an adult woman with a soft feminine timbre (never a male voice)'
n_audio = 0
for o in c['ops']:
    if not o['id'].startswith('mnVideo'): continue
    for n in walk(o['prompt']):
        if isinstance(n, dict) and n.get('op') == 'concat' and n.get('parts') and n['parts'][0] == A0:
            n['parts'][0:1] = ['\n\nAudio: continuous ', LANG, ' narration for the whole clip — starts at 0.0s, no silent gaps between scenes or at the end. ']
            n_audio += 1
    s = J(o['prompt'])
    s = s.replace(F_OLD, F_NEW).replace('The Thai voice-over narration MUST', 'The voice-over narration MUST') \
         .replace('. Voice-over script (Thai): ', '. Voice-over script: ')
    o['prompt'] = json.loads(s)
assert n_audio == 6, n_audio
L['voiceVideoEN'] = {k: v.replace('Thai ', '').replace(', natural Thai', '') for k, v in L['voiceVideoEN'].items()}
L['voiceLockEN'] = {k: v.replace('the Thai narration', 'the narration') for k, v in L['voiceLockEN'].items()}
print('mnVideo 1-6: "Thai" 4 จุด → จุดเดียวตามภาษา/สำเนียง')

# ── ยาม ──
for o in c['ops']:
    if o['id'].startswith('mnVideo'):
        s = J(o['prompt'])
        assert 'Thai narration' not in s and 'script (Thai)' not in s and F_OLD not in s and 'The Thai voice' not in s, o['id']
        assert s.count('accentVideoEN') == 1, o['id']
for t in ('voiceVideoEN', 'voiceLockEN'):
    assert not any('Thai' in v for v in L[t].values()), t
for k in ('กรุงเทพ', 'อีสาน', 'เหนือ', 'ใต้'):
    assert k in L['accentPlan'] and k in L['accentVideoEN']
for w in ('หยาบ', 'ดุดัน'):
    assert w not in J([o['value'] for o in box['card'][gi + 4]['options']])
print('✅ ยามผ่าน: ไม่เหลือ "Thai" ฝังในบล็อกเสียงของ video · lookup ครบทุกสำเนียง · ไม่มีตัวเลือกหยาบ')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
