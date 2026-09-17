#!/usr/bin/env python3
"""v23 — prompt วิดีโอของ minimal ต้องไม่เกินเพดานที่ engine ตัดเงียบ (execLeaf MAX_PROMPT = 3900)

ปัญหา (วัด 2026-09-15 · 216 คู่ผสมปุ่ม × บทยาวสูงสุดจากไฟล์เซฟจริง 22 คลิป / 110 ฉาก):
  เกินเพดาน 216/216 · ยาวสุด 5,922 ⇒ ท้าย prompt หายเงียบทุกคลิป ไม่มี error
  ของที่หายจริง: VOICE LOCK / AUDIO LOCK · กฎ "ข้อความเดียวที่อนุญาต" · กฎพรีเซนเตอร์ · Negative
  และโหมด 10 วิ **บทพากย์ฉาก 4-5 ถูกตัดด้วย** (บทพากย์อยู่ในบล็อก Audio ช่วงท้าย)
  🪤 dry-run ทุกตัวอ่าน prompt ก่อนจุดที่ตัด ⇒ เขียวหลอกมาตลอด

ทางแก้ (config ล้วน · ความหมายของกฎคงเดิม):
  1) บีบถ้อยคำ — ตัดคำซ้ำ/ประโยคที่ซ้ำกันระหว่างบล็อก
     ★วลีที่ยามเฝ้าอยู่ (minimal-knobs · minimal-camera-en · minimal-cliplen) คงไว้ตรงตัวทุกวลี — เป็นบทเรียนจากบั๊กจริง
  2) เรียงใหม่ ของสำคัญขึ้นหน้า ⇒ ถ้าวันหน้าบทยาวจนโดนตัดอีก ส่วนที่หายคือท้ายฉากสุดท้าย ไม่ใช่กฎ
     lead → PRODUCT LOCK → พรีเซนเตอร์ → VOICE/AUDIO LOCK → Audio(+บทพากย์) → กฎข้อความ → CONTINUATION → storyboard + Negative → ฉาก 1-5
  3) ทำกับ mnVideo / mnVideo2 / mnVideo3 ด้วยฟังก์ชันเดียวกัน (ช่วง 2/3 = สำเนาที่เลื่อนดัชนีของช่วง 1)
  🪤 ข้อความเดิม "White text with a soft shadow … doodles" ซ้ำกับ svText ค่าตั้งต้น ⇒ ตัดทิ้ง ให้ svText (สไตล์ที่ผู้ใช้เลือก) เป็นตัวกำหนดตัวเดียว
     ผลข้างเคียงที่ตั้งใจ: เลือกสไตล์ซานเซอริฟ/ตัวหนา จะไม่ถูกบังคับให้มีเงา+doodle อีก (ของเดิมขัดกับที่ผู้ใช้เลือก)

usage: python3 scripts/minimal-v23-video-prompt-fit.py [src.json] [dst.json]   (ค่าตั้งต้น = แก้ minimal-lab.json ในที่)
"""
import json, re, sys, copy, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'minimal-lab.json'
DST = Path(sys.argv[2]) if len(sys.argv) > 2 else SRC
VIDEO_OPS = ('mnVideo', 'mnVideo2', 'mnVideo3')
LOOKUPS = ('voiceVideoEN', 'voiceLockEN', 'charVideoEN')

LEAD_OLD_HEAD = 'A single continuous 9:16 vertical minimal commercial, approximately 10 seconds'
LEAD_NEW = (
    'A minimal commercial of approximately 10 seconds as one single continuous full-bleed 9:16 shot: Scandinavian '
    'pastel look, soft natural light, 4K, moving smoothly through the 5 scenes below in order.'
    '\n\nPRODUCT LOCK (outranks all style): the product is the exact real object in the attached product photos — same '
    'colour, shape, proportions, size, material, texture, label, logo, lettering and number of parts; never redraw, '
    'restyle or cartoonify it. Styling applies to the set and light, never to the product itself. For angles the '
    'photos lack, use the closest shown one; never invent details.'
)
STORYBOARD = (
    '\n\nReference image 1 is the storyboard sheet for THIS clip (one stacked panel per scene). Follow each '
    'panel as the look for its matching scene, but never draw its panel borders, numbers, labels, timings or split '
    'layout, and never copy the sheet as a whole image.'
)
NEG_OLD = '\n\nNegative: no grid, no table, no split screen, no distorted or non-Thai text, no warped product, no extra fingers, no morphing.'
NEG_NEW = '\n\nNegative: no grid, no table, no split screen, no distorted or non-Thai text, no warped or morphing product, no extra fingers.'
PRES_HDR_OLD, PRES_HDR_NEW = '\n\nPRESENTER MODE: ', '\n\n'   # ค่าใน charVideoEN มีหัวข้อของตัวเองอยู่แล้ว
# ข้อความเดิม → ข้อความใหม่ (ต้องเจอครบตามจำนวนที่คาด ไม่งั้น assert)
EXACT = {
    '\n\nAudio: The narration must run continuously for the whole clip — start speaking at 0.0s and keep speaking until the last second. No silent gap at the start, between scenes, or at the end. ':
        '\n\nAudio: ',
    '\n\nAudio: NO voice-over and no narration at all — natural ambient sound only (soft room tone, gentle real product and environment sounds), optional soft minimal background music. No spoken words in any language, no lip-sync.':
        '\n\nAudio: NO voice-over and no narration — natural ambient sound only (soft room tone, gentle real product and environment sounds), optional soft minimal music. No spoken words in any language, no lip-sync.',
    '\n\nAudio: ASMR style audio — NO narration and no spoken words. Close-mic, crisp, satisfying real product sounds matched to the on-screen action (gentle taps, fabric rustle, liquid pouring, cap twisting, cream squeezing, soft brush strokes) plus subtle room tone. No music, or only a very faint ambient pad. Never add a human voice.':
        '\n\nAudio: ASMR style audio — NO narration or spoken words. Close-mic, crisp, satisfying real product sounds matched to the action (gentle taps, fabric rustle, liquid pouring, cap twisting, cream squeezing, soft brush strokes) plus subtle room tone. No music, or only a very faint ambient pad. Never add a human voice.',
    '\n\nON-SCREEN TEXT STYLE: All Thai overlays use this style — {values.svText}. White text with a soft shadow, single line, max 5 Thai words per shot, decorated with tiny hand-drawn doodles (hearts, sparkles, stars, arrows). Never cover the product. Render Thai glyphs accurately. The ONLY text allowed anywhere in the video is the Thai overlay quoted for each scene above (plus text physically printed on the product packaging) — no camera directions, no scene names, no timings, no English words from this prompt.':
        "\n\nON-SCREEN TEXT STYLE: {values.svText}; one line, max 5 Thai words, never covering the product, crisp and correctly spelled. The ONLY text allowed anywhere in the video is each scene's quoted Thai overlay (plus text printed on the product). Camera directions, scene labels and timings are instructions — never draw them.",
    '\n\nNO ON-SCREEN TEXT: This commercial has NO text overlays at all — no Thai captions, no subtitles, no titles, no typography, no watermarks and no hand-drawn text doodles in any frame. The only readable text allowed is the text physically printed on the product packaging itself. Ignore any mention of on-screen text in the scene descriptions. Tell the story with visuals and the voice-over only.':
        '\n\nNO ON-SCREEN TEXT: no captions, subtitles, titles, typography, watermarks or text doodles in any frame; only text printed on the product may be readable. Ignore any on-screen text in the scenes or storyboard; tell the story with visuals and the voice-over only. Camera directions, scene labels and timings are instructions — never draw them.',
    '\n\nAUDIO LOCK: This video has NO spoken narration. Do not add any human voice, dialogue, singing or lip-sync. Any speech is a wrong result.':
        '\n\nAUDIO LOCK: NO spoken narration. Do not add any human voice, dialogue, singing or lip-sync; any speech is a wrong result.',
}
VOICE_DESC = {
    'warm friendly Thai FEMALE voice-over — an adult woman speaking natural Thai with a soft feminine timbre (never a male voice)':
        'warm friendly Thai FEMALE voice-over (adult woman)',
    'warm friendly Thai MALE voice-over — an adult man speaking natural Thai with a warm masculine timbre (never a female voice)':
        'warm friendly Thai MALE voice-over (adult man)',
}
VOICE_LOCK = {
    '\n\nVOICE LOCK: The Thai voice-over narration MUST be performed by a FEMALE (adult woman) voice. A male narrator is a wrong result.':
        '\n\nVOICE LOCK: the Thai narration MUST be performed by a FEMALE (adult woman) voice — a male narrator is wrong.',
    '\n\nVOICE LOCK: The Thai voice-over narration MUST be performed by a MALE (adult man) voice. A female narrator is a wrong result.':
        '\n\nVOICE LOCK: the Thai narration MUST be performed by a MALE (adult man) voice — a female narrator is wrong.',
}
CHAR = {
    'มีพรีเซนเตอร์ไทย 1 คนในคลิป|AI เลือกนาย/นางแบบให้เหมาะกับสินค้า':
        'MAIN CHARACTER: one attractive Thai-looking presenter (gender and age to suit the product and audience), friendly and natural, with eye contact, smiles and real hand use of the product; same person in every scene, product stays the focus.',
    'มีพรีเซนเตอร์ไทย 1 คนในคลิป|ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต':
        'CHARACTER CONSISTENCY (HIGHEST PRIORITY): the exact person from the attached face image in every shot (same face, hairstyle, hair colour, skin tone, body type, age, identity) — never another person or a changed gender, age or ethnicity; only clothing, pose, angle and expression may change. Product stays the focus.',
}
# ผลของ matchTable มุมกล้อง (อังกฤษ) — ย่อ ความหมายเดิม · คงคำที่ minimal-camera-en เฝ้า (low camera angle · 45 degrees · macro · top-down · pan · zoom-out · tracking)
CAMERA = {
    'extreme macro close-up on the product surface and texture': 'extreme macro close-up on the product texture',
    'top-down flat lay view straight above the product': 'top-down flat lay above the product',
    'high camera angle looking down at roughly 45 degrees': 'high angle looking down about 45 degrees',
    'low camera angle looking up so the product feels grand and heroic': 'low camera angle, product looks heroic',
    'slow smooth zoom-out revealing the wider scene': 'slow zoom-out revealing the scene',
    'slow smooth horizontal camera pan across the scene': 'slow pan across the scene',
    'tracking shot following the hands using the product': 'tracking shot following the hands',
    'smooth cinematic camera movement that suits the scene': 'smooth cinematic camera move',
}
VO_TAIL_OLD = ', short, must not exceed clip length. Voice-over script (Thai): '
VO_TAIL_NEW = ', from 0.0s to the end within the clip length. No silent gap. Voice-over script (Thai): '
CONT_RE = re.compile(r'^CONTINUATION SHOT — this is part (\d) of a single longer commercial\. It continues directly from the previous 10 seconds, same story, same take\. Same product, same set, same background, same lighting, same colour palette and the same person as before\. Do NOT re-introduce the product, do NOT restart the story, do NOT add an ending unless these are the final scenes\. Start exactly where the previous part left off\.\n\n$')
CONT_NEW = ('\n\nCONTINUATION SHOT — part {n}: continue exactly where the previous 10 seconds ended (same take, story, product, set, '
            'light, palette, person). Do NOT re-introduce the product, restart the story or add an ending before the final scenes.')

def flat(n):
    out = []
    def w(x):
        if isinstance(x, str): out.append(x)
        elif isinstance(x, dict):
            for v in x.values(): w(v)
        elif isinstance(x, list):
            for v in x: w(v)
    w(n); return '\n'.join(out)

def placeholders(n):
    return collections.Counter(re.findall(r'\{(?:item|values)\.[a-zA-Z0-9_.]+\}', json.dumps(n, ensure_ascii=False)))

def whens(n):
    out = []
    def w(x):
        if isinstance(x, dict):
            if 'when' in x: out.append(json.dumps(x['when'], ensure_ascii=False, sort_keys=True))
            for v in x.values(): w(v)
        elif isinstance(x, list):
            for v in x: w(v)
    w(n); return collections.Counter(out)

hits = collections.Counter()
def replace_strings(n, table):
    items = n.items() if isinstance(n, dict) else enumerate(n) if isinstance(n, list) else []
    for k, v in list(items):
        if isinstance(v, str):
            if v in table: n[k] = table[v]; hits[v] += 1
            elif v.startswith(VO_TAIL_OLD): n[k] = VO_TAIL_NEW + v[len(VO_TAIL_OLD):]; hits[VO_TAIL_OLD] += 1
        else:
            replace_strings(v, table)

def restructure(op):
    parts = op['prompt']['parts']
    cont = [p for p in parts if isinstance(p, str) and p.startswith('CONTINUATION SHOT')]
    lead = [p for p in parts if isinstance(p, dict) and LEAD_OLD_HEAD in flat(p)]
    audio = [p for p in parts if isinstance(p, dict) and '\n\nAudio: ' in flat(p)]
    neg = [p for p in parts if p == NEG_OLD]
    text = [p for p in parts if isinstance(p, dict) and 'ON-SCREEN TEXT' in flat(p)]
    hdr = [p for p in parts if p == PRES_HDR_OLD]
    pres = [p for p in parts if isinstance(p, dict) and p.get('table') == 'charVideoEN']
    lock = [p for p in parts if isinstance(p, dict) and 'LOCK:' in flat(p) and 'Audio:' not in flat(p) and LEAD_OLD_HEAD not in flat(p)]
    assert [len(x) for x in (lead, audio, neg, text, hdr, pres, lock)] == [1] * 7, op['id']
    assert len(cont) == (0 if op['id'] == 'mnVideo' else 1), op['id']
    first = lead[0]['parts'][0]['parts']
    assert isinstance(first[0], str) and first[0].startswith(LEAD_OLD_HEAD) and first[0].endswith('full-bleed 9:16 shot.\n\n'), op['id']
    first[0] = '\n'   # เหลือแต่หัวฉาก 1 · กฎทั้งหมดย้ายขึ้นหน้า
    special = set(map(id, cont + lead + audio + neg + text + hdr + pres + lock))
    scenes = [p for p in parts if id(p) not in special]   # overlay ฉาก 1 + ฉาก 2-5 + overlay ตามลำดับเดิม
    assert len(scenes) == 9, (op['id'], len(scenes))
    new = [LEAD_NEW, PRES_HDR_NEW, pres[0], lock[0], audio[0], text[0]]
    if cont:
        m = CONT_RE.match(cont[0]); assert m, op['id']
        new.append(CONT_NEW.format(n=m.group(1)))
    new += [STORYBOARD, NEG_NEW, lead[0]] + scenes
    op['prompt']['parts'] = new

c = json.loads(SRC.read_text(encoding='utf-8'))
ops = {o['id']: o for o in c['ops']}
if all(ops[k]['prompt']['parts'][0] == LEAD_NEW for k in VIDEO_OPS):
    print('✓ แพตช์แล้ว — ไม่ต้องทำซ้ำ'); sys.exit(0)

before = copy.deepcopy(c)
for k in VIDEO_OPS:
    replace_strings(ops[k]['prompt'], {**EXACT, **VOICE_DESC, **VOICE_LOCK, **CAMERA})
for o in EXACT: assert hits[o] == 3, ('EXACT', o[:50], hits[o])
assert hits[VO_TAIL_OLD] == 3, hits[VO_TAIL_OLD]
for o in CAMERA: assert hits[o] == 15, ('camera', o, hits[o])       # 5 ฉาก × 3 op
for o in VOICE_DESC: assert hits[o] in (0, 6), ('voice desc fallback', o[:30], hits[o])   # fallback อยู่ใน op 6 ที่ (ฝั่งหญิง)
for o in VOICE_LOCK: assert hits[o] in (0, 6), ('voice lock fallback', o[:30], hits[o])
for k in VIDEO_OPS: restructure(ops[k])
lk = c['lookups']
for key, val in list(lk['voiceVideoEN'].items()): lk['voiceVideoEN'][key] = VOICE_DESC[val]
for key, val in list(lk['voiceLockEN'].items()): lk['voiceLockEN'][key] = VOICE_LOCK[val]
for key, val in CHAR.items(): assert key in lk['charVideoEN']; lk['charVideoEN'][key] = val

# ── ยาม: ไม่มีอะไรนอกขอบเขตขยับ ─────────────────────────────────
for k in c:
    if k not in ('ops', 'lookups'): assert c[k] == before[k], ('แตะก้อนนอกขอบเขต', k)
for ob, oa in zip(before['ops'], c['ops']):
    if ob['id'] in VIDEO_OPS:
        assert {x: ob[x] for x in ob if x != 'prompt'} == {x: oa[x] for x in oa if x != 'prompt'}, ('op field อื่นขยับ', ob['id'])
        assert placeholders(ob['prompt']) == placeholders(oa['prompt']), ('ตัวแปรในบทหาย/งอก', ob['id'])
        assert whens(ob['prompt']) == whens(oa['prompt']), ('เงื่อนไข when ขยับ', ob['id'])
    else:
        assert ob == oa, ('op อื่นขยับ', ob['id'])
for t in lk:
    if t not in LOOKUPS: assert lk[t] == before['lookups'][t], ('lookup อื่นขยับ', t)
    else: assert set(lk[t]) == set(before['lookups'][t]), ('คีย์ lookup ขยับ', t)

DST.write_text(json.dumps(c, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'✓ เขียน {DST.name} · ops {", ".join(VIDEO_OPS)} · lookups {", ".join(LOOKUPS)}')
