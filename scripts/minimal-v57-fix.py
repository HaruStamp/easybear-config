#!/usr/bin/env python3
# minimal-v57-fix.py — แก้ 3 เรื่องจากคลิปจริง 2026-10-16 (รันซ้ำได้)
#  ① เสียงผู้ชายโทนสูง (f0 160-184 Hz ใน V2/V3/S3) → แถวผู้ชายสั่ง deep / low-pitched + ห้ามเสียงสูง
#  ② ข้อความบนจอค้างซ้อนข้ามฉาก (S1/S4) → overlay ขึ้นเฉพาะฉากของมัน แล้วหาย · ห้ามขึ้น 2 อันพร้อมกัน
#  ③ ข้อความไทยเพี้ยน → "correctly spelled" (ชวนโมเดลสะกดเอง) เป็น "copied letter by letter from the quote"
#  ที่ว่าง: ตัด "within the clip length" (ซ้ำกับ to the end) · ตัดประโยค live-action ที่ซ้ำกับ Negative (no line art/sketch/paper/panel ยังอยู่ใน Negative)
import json, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json'
c = json.load(open(P))
L = c['lookups']

def setrow(tbl, key, val):
    assert tbl in L and key in L[tbl], (tbl, key)
    L[tbl][key] = val

setrow('voiceVideoEN', 'เสียงผู้ชาย', 'deep warm Thai MALE voice-over (adult man, low pitch)')
setrow('voiceLockEN', 'เสียงผู้ชาย', '\n\nVOICE LOCK: the Thai narration MUST be performed by a MALE (adult man) voice, deep and low-pitched — never female or high.')
for t in ('voiceVideoEN_EN', 'voiceLockEN_EN'):
    assert t in L, t
setrow('voiceVideoEN_EN', 'เสียงผู้ชาย', 'deep warm English MALE voice-over (adult man, low pitch)')
setrow('voiceLockEN_EN', 'เสียงผู้ชาย', '\n\nVOICE LOCK: the English narration MUST be performed by a MALE (adult man) voice, deep and low-pitched — never female or high.')

REPL = [
  (", from 0.0s to the end within the clip length.", ", from 0.0s to the end."),
  ("Every frame is live-action photography, never line art, sketch, paper or panel border, not even one frame.",
   "Every frame is live-action photography."),
  ("crisp and correctly spelled. The ONLY text allowed anywhere in the video is each scene's quoted Thai overlay (plus text printed on the product).",
   "crisp, copied exactly from the quote. The ONLY text allowed anywhere in the video is each scene's quoted Thai overlay (plus text printed on the product), only in its own scene, then gone; never two at once."),
  ("crisp and correctly spelled. The ONLY text allowed anywhere in the video is each scene's quoted English overlay (plus text printed on the product).",
   "crisp, copied exactly from the quote. The ONLY text allowed anywhere in the video is each scene's quoted English overlay (plus text printed on the product), only in its own scene, then gone; never two at once."),
]
hits = {a: 0 for a, _ in REPL}
def walk(x):
    if isinstance(x, str):
        for a, b in REPL:
            if a in x: hits[a] += x.count(a); x = x.replace(a, b)
        return x
    if isinstance(x, list): return [walk(i) for i in x]
    if isinstance(x, dict): return {k: walk(v) for k, v in x.items()}
    return x
vids = [o for o in c['ops'] if o['id'] in ('mnVideo', 'mnVideo2', 'mnVideo3')]
assert len(vids) == 3
for o in vids: o['prompt'] = walk(o['prompt'])
done_before = all(v == 0 for v in hits.values())
print({a[:40]: n for a, n in hits.items()})
if done_before:
    s = json.dumps([o['prompt'] for o in vids], ensure_ascii=False)
    assert 'never two at once' in s, 'ไม่เจอทั้งของเก่าและของใหม่'
    print('แพตช์แล้วก่อนหน้า (เขียนแถวเสียงซ้ำอย่างเดียว)')
else:
    assert all(v > 0 for v in hits.values()), hits
json.dump(c, open(P, 'w'), ensure_ascii=False, indent=2)
print('ok', P)
