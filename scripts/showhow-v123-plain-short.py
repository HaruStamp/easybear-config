#!/usr/bin/env python3
"""showhow-v123 — prompt บอร์ด/วิดีโอ สั้นลง เป็นภาษาคนง่าย ๆ (พี่หมีสั่ง 2026-10-13)

เทคนิคของพี่หมี: "Flow ไม่ชอบ prompt ยาว ๆ เอาเน้น ๆ ที่จำเป็น เขียนแบบภาษาคนง่าย ๆ จะทำได้ตรง"
เคสที่เห็น: v121 การ์ตูน 3D — คำว่า 3D มีบรรทัดเดียวจมในกฎเลย์เอาต์ยาว ๆ ⇒ บอร์ดช่วง 1 ออกมาสมจริง

ทำ: เขียนข้อความคงที่ใน mnBoard1-6 / mnVideo1-6 ใหม่ให้สั้น (gate/lookup/ตัวแปรเดิมทุกตัว ไม่แตะโครง)
ไม่แตะ (มีบทเรียนจริง):
  · บรรทัดสินค้าของบอร์ด + PRODUCT LOCK วิดีโอ — v18b ยุบให้สั้นแล้วขวดเปลี่ยนสี/ทรงทันที
  · คำบังคับเลย์เอาต์ที่ audit R6 เช็ค (ตาราง 2 คอลัมน์ · ช่องติดกันสนิท · ไม่มีขอบสีขาวรอบแผ่น · วงกลมทึบ · ห้ามมีคอลัมน์ข้อความ
    · ห้ามมีคำบรรยายใต้ภาพ · ฉาก N เป็นช่องเดียวกินเต็มความกว้าง) — คงคำเดิม ตัดแค่คำขยายซ้ำ
  · ค่าเสียง/ภาษา (lookup) · Negative · บรรทัดฉาก
ใช้: python3 scripts/showhow-v123-plain-short.py  (รันบน v122)
"""
import json, re
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))

NUM = r'(\d+)'
R = []  # (ชื่อ, regex, ฟังก์ชันแทน) — regex ต้องจับทั้งสตริง (fullmatch) ยกเว้นที่ระบุ prefix


def rule(name, pat, rep, prefix=False):
    R.append((name, re.compile(pat, re.S), rep, prefix))


# ══ บอร์ด ══
rule('B-head', r'แผ่นภาพสตอรีบอร์ดแนวตั้ง ภาพล้วน ไม่มีตารางข้อความ เรื่อง "\{item\.productName\}"',
     lambda m: 'สตอรีบอร์ดแนวตั้ง ภาพล้วน เรื่อง "{item.productName}"')


def layout(m):
    a, e = int(m.group(1)), int(m.group(4))
    d = e - 1
    no1 = '' if a == 1 else ' ห้ามเริ่มที่ 1'
    return (' (บรรทัดนี้ห้ามพิมพ์ลงภาพ)\n'
            f'เลย์เอาต์: ตาราง 2 คอลัมน์ ช่องละ 1 ฉาก เรียงซ้ายไปขวา · ฉาก {a} ถึง {d} ช่องทรงตั้งขนาดเท่ากัน · '
            f'ฉาก {e} เป็นช่องเดียวกินเต็มความกว้างแถวล่างสุด · ช่องติดกันสนิท ไม่มีเส้นคั่น ไม่มีขอบสีขาวรอบแผ่น ภาพเต็มแผ่น · '
            f'มุมซ้ายบนทุกช่องมีวงกลมทึบใส่เลขฉาก {a} ถึง {e}{no1} · ห้ามมีคอลัมน์ข้อความ ห้ามมีคำบรรยายใต้ภาพ ห้ามมีแถบหัวเรื่อง\n'
            'ภาพทุกช่อง: ')


rule('B-layout', r' \(บรรทัดนี้เป็นข้อมูลกำกับ ห้ามพิมพ์ลงภาพ\)\nบังคับเลย์เอาต์: ตาราง 2 คอลัมน์ ช่องละ 1 ฉาก เรียงซ้าย→ขวา แล้วลงแถวถัดไป ครบ (\d+)-(\d+) · ฉาก (\d+) ถึง \d+ อยู่ในช่องทรงตั้ง .*?· ฉาก (\d+) เป็นช่องเดียวกินเต็มความกว้างที่แถวล่างสุด .*ภาพทุกช่อง: ',
     layout)


def cont(m):
    ref = m.group(1).replace('**', '')
    return (' · แสง {item.palette} · ทุกช่องที่เดียวกัน ของที่ไม่ได้ทำคงที่ · ห้ามมีเส้นหรือคำเอฟเฟกต์\n'
            f'บอร์ดช่วงก่อนหน้าที่แนบมา ({ref}): คลิปเดียวกัน ห้องเดิม — พื้น ผนัง เฟอร์นิเจอร์ ประตูหน้าต่าง และชุดของคนทำเหมือนเดิม · ห้ามลอกภาพในช่อง')


rule('B-cont', r' ห้ามมีเส้นเอฟเฟกต์หรือคำเอฟเฟกต์ · แสง \{item\.palette\} · .*?\nบอร์ดช่วงก่อนหน้าที่แนบมา \((.*?)\): เป็นคลิปเดียวกัน .*ห้ามลอกภาพในช่อง', cont)

PROD_TAIL = ' · ถ้ามีสินค้าในเฟรม ต้องตรงรูปที่แนบ'
rule('B-end-open1', r'\nช่องฉาก (\d+) = ฉากปิดของคลิป ต้องเป็นภาพกว้างเห็นทั้งพื้นที่ .*\(ดูช่องแรกของแผ่นนี้\).*',
     lambda m: f'\nช่องฉาก {m.group(1)} = ฉากปิดของคลิป: ภาพกว้าง มุมกล้องเดียวกับช่องแรกของแผ่นนี้ เปลี่ยนแค่สภาพที่ทำเสร็จ' + PROD_TAIL)
rule('B-end-openK', r'\nช่องฉาก (\d+) = ฉากปิดของคลิป ต้องเป็นภาพกว้างเห็นทั้งพื้นที่ .*\(\*\*รูปแรกที่แนบ = บอร์ดช่วงที่ 1\*\*.*',
     lambda m: f'\nช่องฉาก {m.group(1)} = ฉากปิดของคลิป: ภาพกว้าง ลอกมุมกล้องจากช่องแรกของรูปแรกที่แนบ (บอร์ดช่วงที่ 1) ห้องเดิม เปลี่ยนแค่สภาพที่ทำเสร็จ' + PROD_TAIL)
rule('B-end-ref', r'\nช่องฉาก (\d+) = ฉากปิดของคลิป: มุมกล้อง การจัดวาง และสภาพตามภาพอ้างอิงฉากจบ .*',
     lambda m: f'\nช่องฉาก {m.group(1)} = ฉากปิดของคลิป: มุมกล้องและสภาพตามภาพฉากจบ (รูปสุดท้ายที่แนบ) แต่ยังเป็นห้องเดิม' + PROD_TAIL)
rule('B-end-tl', r'\nช่องฉาก (\d+) = ฉากปิดของคลิป: กรอบภาพเดิมทุกช่อง .*',
     lambda m: f'\nช่องฉาก {m.group(1)} = ฉากปิดของคลิป: กรอบภาพเดิม เปลี่ยนแค่สภาพให้ตรงภาพฉากจบ (รูปสุดท้ายที่แนบ)' + PROD_TAIL)
rule('B-room', r'\nสถานที่ = ห้องตามรูปที่แนบ \(ผนัง พื้น เฟอร์นิเจอร์ หน้าต่าง ทิศแสง\) เปลี่ยนได้เฉพาะผลของงาน · ช่องแรก = สภาพตามรูป',
     lambda m: '\nสถานที่ = ห้องตามรูปที่แนบ (ผนัง พื้น เฟอร์นิเจอร์ หน้าต่าง แสง) · ช่องแรก = สภาพตามรูป')
rule('B-sub', r'ใช้ข้อความที่บทให้ของช่องนั้นเท่านั้น .*ไม่ทับจุดที่กำลังทำ',
     lambda m: 'ใช้เฉพาะข้อความที่บทให้ (ช่องไหนไม่มี = ภาพล้วน) บรรทัดเดียว ฟอนต์ {values.svText} (ไม่ระบุสี = สีเข้มเข้ากับคลิป) ไม่ทับจุดที่กำลังทำ')
rule('B-title', r'พิมพ์ทับลงบนภาพถ่ายในช่องแรกเท่านั้น .*ช่องอื่นภาพล้วน',
     lambda m: 'พิมพ์บนช่องแรกเท่านั้น (หัวเรื่องตามบท) ตัวใหญ่เด่น ชิดซ้าย ครึ่งบนของช่อง อยู่ในกรอบช่องแรก ไม่ทับจุดที่กำลังทำ · ฟอนต์ {values.svText} (ไม่ระบุสี = สีเข้มเข้ากับคลิป) · ช่องอื่นภาพล้วน')
rule('B-tail', r' · ห้ามพิมพ์ตัวหนังสืออื่นบนแผ่น .*\n\nช่องภาพตามลำดับ \(เลขในวงกลม = เลขหน้าบรรทัด\):',
     lambda m: ' · ห้ามมีตัวหนังสืออื่น ชื่อสไตล์ แบรนด์ที่ไม่ได้แนบ หรือ emoji\n\nช่องภาพ (เลขในวงกลม = เลขหน้าบรรทัด):')

# ══ วิดีโอ ══
rule('V-head', r'Single continuous 9:16 vertical how-to clip, ~10 s, ', lambda m: 'One 9:16 vertical how-to clip, ~10 s, ')
rule('V-light', r'\. Lighting/mood: \{item\.palette\}\. One continuous shot through 5 scenes in order — no grid, split-screen, panels or borders\. ',
     lambda m: '. Light: {item.palette}. One continuous shot through 5 scenes in order — no split-screen or panels. ')
rule('V-loc', r'LOCATION LOCK: the attached room photo is the real location — .*scene 1 = as photographed\. ',
     lambda m: 'LOCATION LOCK: the attached room photo is the real place — same walls, floor, furniture, window and light in every scene; scene 1 = as photographed. ')
rule('V-audiolock', r'\n\nAUDIO LOCK: no spoken narration, .*any speech is a wrong result\.',
     lambda m: '\n\nAUDIO LOCK: no speech, no human voice, no lip-sync.')
rule('V-title', r'\n\nON-SCREEN TEXT: exactly ONE fixed Thai title overlay, .*?upper area, never covering the work\.',
     lambda m: '\n\nON-SCREEN TEXT: one fixed Thai title, one line, style {values.svText}, exact Thai letters, same words, size and place in every frame, upper area, not covering the work.', prefix=True)
rule('V-subs', r'\n\nON-SCREEN TEXT: only the quoted Thai overlays below may appear, .*never render directions or labels\.',
     lambda m: '\n\nON-SCREEN TEXT: show only the quoted Thai lines below, one line each, style {values.svText}, exact Thai letters, not covering the work. No other words or labels.')
rule('V-notext', r'\n\nNO ON-SCREEN TEXT: no captions, titles or subtitles in any frame; .*',
     lambda m: '\n\nNO ON-SCREEN TEXT: no captions or titles; only text printed on real objects.')
rule('V-sheet', r'\n\nAttached sheets are a silent guide: image 1 = this part\'s 5 scenes — .*frame 1 is already a live scene\.',
     lambda m: "\n\nThe attached sheet (image 1) is a silent guide to this part's 5 scenes; other images = same room. Copy its room, framing and light. Never show sheets, panels or numbers — the first frame already shows the scene itself.")
rule('V-locked', r'\n\nONE CONTINUOUS LOCKED TAKE — the entire 10 s .*each change growing out of the previous one:',
     lambda m: '\n\nONE LOCKED TAKE: a fixed camera for the whole 10 s — no cuts, no moves. The work moves forward in this order:')
rule('V-asmr', r'\n\nAudio: ASMR — no narration, no spoken words\. .*Never add a human voice\.',
     lambda m: '\n\nAudio: ASMR — no speech. Close, crisp real sounds of the work (scrubbing, pouring, wiping, tapping) plus room tone; no music or a faint pad.')
rule('V-novo', r'\n\nAudio: no voice-over, no narration, no spoken words in any language — .*optional faint ambient music\.',
     lambda m: '\n\nAudio: no narration or speech — only natural room sounds of the work, optional soft music.')
rule('V-contframe', r'\n\nCONTINUATION: the opening frame is supplied — .*never jump ahead to a more finished stage of the work\.',
     lambda m: '\n\nCONTINUATION: start exactly from the supplied opening frame and carry on. Same camera and framing; no cuts, no jumping ahead.')
rule('V-contpart', r'CONTINUATION — part (\d+) of one longer clip: same take, room, light, objects and person; no restart, no re-introduction, no ending unless final\.',
     lambda m: f'CONTINUATION — part {m.group(1)} of one clip: same room, light, objects and people; no restart, no ending unless final.', prefix=True)
rule('V-narr', r' narration for the whole clip — starts at 0\.0s, no silent gaps between scenes or at the end\. ',
     lambda m: ' narration from 0.0s to the end, no silent gaps. ')

hits = {r[0]: 0 for r in R}


def fix(s):
    for name, pat, rep, prefix in R:
        if prefix:
            s2, n = pat.subn(rep, s, count=1)
            if n and s2 != s:
                hits[name] += 1; s = s2
        else:
            m = pat.fullmatch(s)
            if m:
                hits[name] += 1
                return rep(m)
    return s


def walk(n):
    if isinstance(n, dict):
        for k, v in n.items():
            if k in ('when', 'table', 'key', 'op'):
                continue
            if isinstance(v, str):
                n[k] = fix(v)
            else:
                walk(v)
    elif isinstance(n, list):
        for i, v in enumerate(n):
            if isinstance(v, str):
                n[i] = fix(v)
            else:
                walk(v)


before = {}
for o in c['ops']:
    if o['id'].startswith(('mnBoard', 'mnVideo')):
        before[o['id']] = len(json.dumps(o['prompt'], ensure_ascii=False))
        walk(o['prompt'])

print('จำนวนจุดที่แก้ต่อกติกา:', hits)
# board: head6 layout6 cont6 end-open1 1 + end-openK 5 + end-ref 6 + end-tl 6 room6 sub6 title2 tail6
WANT = {'B-head': 6, 'B-layout': 6, 'B-cont': 6, 'B-end-open1': 1, 'B-end-openK': 5, 'B-end-ref': 6, 'B-end-tl': 6,
        'B-room': 6, 'B-sub': 6, 'B-title': 2, 'B-tail': 6,
        'V-head': 6, 'V-light': 6, 'V-loc': 6, 'V-audiolock': 6, 'V-title': 6, 'V-subs': 6, 'V-notext': 6, 'V-sheet': 6,
        'V-locked': 6, 'V-asmr': 6, 'V-novo': 6, 'V-contframe': 5, 'V-contpart': 5, 'V-narr': 6}
bad = {k: (hits[k], v) for k, v in WANT.items() if hits[k] != v}
assert not bad, f'จำนวนจุดไม่ตรงที่คาด (ได้, คาด): {bad}'

J = json.dumps(c, ensure_ascii=False)
for gone in ('บังคับเลย์เอาต์', 'ชนิดและขนาดกระเบื้อง', 'Close-mic', 'Lighting/mood', 'live scene', 'jump ahead to a more finished'):
    assert gone not in J, gone
for keep in ('สินค้า = ของจริงตามรูปที่แนบ (หลายชิ้น = ชิ้นละรูป)', 'PRODUCT LOCK (overrides style)', 'Negative: no storyboard sheet'):
    assert keep in J, keep
for o in c['ops']:
    if o['id'].startswith(('mnBoard', 'mnVideo')):
        s = json.dumps(o['prompt'], ensure_ascii=False)
        assert '{item.' in s and 'แสง' in s or o['id'].startswith('mnVideo'), o['id']
after = {o['id']: len(json.dumps(o['prompt'], ensure_ascii=False)) for o in c['ops'] if o['id'] in before}
print('ขนาด template ก่อน→หลัง:', {k: f'{before[k]}→{after[k]}' for k in before})
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✅ v123 เขียนแล้ว')
