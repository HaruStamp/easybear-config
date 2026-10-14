#!/usr/bin/env python3
"""showhow-v136 — ตัวเอกพูดเอง: คำพูดห้ามขึ้นเป็นซับบนจอ
ผลจริง v135 (docs/qa/2026-10-14-star-speaks-v134/S2-pet-v135): ปากน้องหมาขยับตามคำแล้ว แต่ประโยคพูดขึ้นเป็นซับทุกฉาก (ตั้ง "หัวเรื่องตอนเปิด")
แก้: ป้าย "Lines:" → "Spoken, no captions:" · ย่อเสียงให้พอที่ (ทางตัวเอกยังต้อง ≤ ทางคนเล่าเรื่อง)
ใช้: python3 scripts/showhow-v136-star-nocaption.py  (รันบน v135)
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
L = c['lookups']
L['voiceStarEN'] = {'เสียงผู้หญิง': 'FEMALE voice, never male', 'เสียงผู้ชาย': 'MALE voice, never female'}
OLD_S, NEW_S = '. Lines: "', '. Spoken, no captions: "'
n = 0
def walk(x):
    global n
    if isinstance(x, dict):
        if x.get('table') == 'voiceStarEN' and isinstance(x.get('fallback'), str): x['fallback'] = L['voiceStarEN']['เสียงผู้หญิง']
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            if isinstance(v, str) and v.startswith(OLD_S): x[i] = NEW_S + v[len(OLD_S):]; n += 1
            else: walk(v)
walk(c['ops'])
assert n == 6, n
A = ' speech: the main character talks on camera, mouth moving with each word, even a pet. '
for g in ['เสียงผู้หญิง', 'เสียงผู้ชาย']:
    old = len(' narration from 0.0s to the end, no silent gaps. ') + len(L['voiceVideoEN'][g]) + len('. Voice-over script: "')
    new = len(A) + len(L['voiceStarEN'][g]) + len(NEW_S)
    assert new <= old, (g, new, old)
print(f'✅ v136: {n} จุด')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
