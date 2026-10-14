#!/usr/bin/env python3
"""showhow-v135 — ตัวเอกพูดเอง: ย้ำให้ปากขยับทุกคำ (รวมสัตว์)
ผลจริง v134 (docs/qa/2026-10-14-star-speaks-v134): เสียงเป็นคำพูดตัวเองแล้ว แต่ปากน้องหมาแทบไม่ขยับ ⇒ ใช้ที่ว่างที่เหลือ (ทางตัวเองยังต้อง ≤ ทางคนเล่าเรื่อง)
ใช้: python3 scripts/showhow-v135-star-mouth.py  (รันบน v134)
"""
import json
P = 'showhow-dev.json'
OLD = ' speech by the main character on screen, lip-synced, 0.0s to the end. '
NEW = ' speech: the main character talks on camera, mouth moving with each word, even a pet. '
s = open(P, encoding='utf-8').read()
c = json.loads(s)
n = 0
def walk(x):
    global n
    if isinstance(x, list):
        for i, v in enumerate(x):
            if v == OLD: x[i] = NEW; n += 1
            else: walk(v)
    elif isinstance(x, dict):
        for v in x.values(): walk(v)
walk(c['ops'])
assert n == 6, n
L = c['lookups']
for g in ['เสียงผู้หญิง', 'เสียงผู้ชาย']:
    old = len(' narration from 0.0s to the end, no silent gaps. ') + len(L['voiceVideoEN'][g]) + len('. Voice-over script: "')
    new = len(NEW) + len(L['voiceStarEN'][g]) + len('. Lines: "')
    assert new <= old, (g, new, old)
print(f'✅ v135: {n} จุด · ทางตัวเอกยังสั้นกว่า/เท่าทางคนเล่าเรื่อง')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
