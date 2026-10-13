#!/usr/bin/env python3
"""showhow-v132 — คลิป ASMR มีเสียงคนอ่านหัวเรื่องออกเสียงช่วง 0-2 วิ (ผลิตจริง W2 สีน้ำ v131 · whisper logprob −0.36 · 2026-10-13)

ราก: v123 ย่อ AUDIO LOCK จาก "no spoken narration, no human voice, no dialogue, no lip-sync — any speech is a wrong result."
  เหลือ "no speech, no human voice, no lip-sync." — คำห้ามเฉพาะอาการหลวม (บทเรียนเดียวกับ v124/v129/v130)
แก้: คืนถ้อยคำ v122 + ห้ามอ่านข้อความบนจอออกเสียง (อาการที่เจอจริง)
ใช้: python3 scripts/showhow-v132-audio-lock.py  (รันบน v131)
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
OLD = 'AUDIO LOCK: no speech, no human voice, no lip-sync.'
NEW = 'AUDIO LOCK: no spoken narration, no human voice, no dialogue, no lip-sync, on-screen text is never read aloud — any speech is a wrong result.'
n = 0
def walk(x):
    global n
    it = x.items() if isinstance(x, dict) else enumerate(x) if isinstance(x, list) else []
    for k, v in list(it):
        if isinstance(v, str):
            if OLD in v: x[k] = v.replace(OLD, NEW); n += 1
        else: walk(v)
for o in c['ops']:
    if o['id'].startswith('mnVideo'): walk(o['prompt'])
assert n == 6, n
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'✅ v132: AUDIO LOCK {n} op')
