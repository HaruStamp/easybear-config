#!/usr/bin/env python3
"""showhow-v134 — "ตัวเอกพูดเอง" ให้ตัวละครพูดในคลิปจริง (ลูกค้าแจ้ง 2026-10-14: เลือกตัวเอกพูดเองแล้วยังได้เสียงบรรยาย ตัวละครไม่ขยับปาก)

ราก: v121 ทำ `values.svVoiceBy=star` แก้แค่บท (speakerPlan ใน mnPlan) · prompt วิดีโอยังสั่ง "narration … voice-over … Voice-over script" ทุกโหมด
แก้: ใน mnVideo* แยกบล็อกเสียงพากย์เป็น 2 ทาง — คนเล่าเรื่อง = ของเดิมทุกตัวอักษร · ตัวเอกพูดเอง = ตัวละครบนจอพูดเอง ขยับปาก
     ทางตัวเอกต้องสั้นกว่าหรือเท่าของเดิม (เพดาน 3,900 · p95 วิดีโอเหลือ 26) ⇒ ใช้ lookup เสียงสั้น `voiceStarEN`
ใช้: python3 scripts/showhow-v134-star-speaks.py  (รันบน v133)
"""
import copy, json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
L = c['lookups']
assert 'voiceStarEN' not in L
L['voiceStarEN'] = {'เสียงผู้หญิง': 'FEMALE voice, never a male voice', 'เสียงผู้ชาย': 'MALE voice, never a female voice'}
OLD_A = ' narration from 0.0s to the end, no silent gaps. '
NEW_A = ' speech by the main character on screen, lip-synced, 0.0s to the end. '
OLD_S = '. Voice-over script: "'
NEW_S = '. Lines: "'
STAR = {'op': 'eq', 'a': '{values.svVoiceBy}', 'b': 'star'}

def is_vo(p):
    v = p.get('value') if isinstance(p, dict) else None
    return isinstance(v, dict) and v.get('op') == 'concat' and v['parts'][:1] == ['\n\nAudio: continuous '] and OLD_A in v['parts']

def starify(x):
    if isinstance(x, dict):
        if x.get('table') == 'voiceVideoEN': x['table'] = 'voiceStarEN'
        if isinstance(x.get('fallback'), str) and 'voice-over' in x['fallback']: x['fallback'] = L['voiceStarEN']['เสียงผู้หญิง']
        for k, v in x.items():
            if isinstance(v, str): x[k] = v.replace(OLD_A, NEW_A).replace(OLD_S, NEW_S)
            else: starify(v)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            if isinstance(v, str): x[i] = v.replace(OLD_A, NEW_A).replace(OLD_S, NEW_S)
            else: starify(v)

hits = []
for op in c['ops']:
    if not str(op.get('id', '')).startswith('mnVideo'): continue
    def walk(x):
        if isinstance(x, dict):
            if x.get('op') == 'block' and isinstance(x.get('parts'), list):
                for i, p in enumerate(list(x['parts'])):
                    if is_vo(p):
                        star = copy.deepcopy(p); starify(star['value'])
                        assert OLD_A not in json.dumps(star, ensure_ascii=False) and 'Voice-over script' not in json.dumps(star, ensure_ascii=False)
                        base = p['when']
                        p['when'] = {'op': 'and', 'list': [base, {'op': 'not', 'a': STAR}]}
                        star['when'] = {'op': 'and', 'list': [copy.deepcopy(base), STAR]}
                        x['parts'].insert(i + 1, star); hits.append(op['id']); return
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(op['prompt'])
assert len(hits) == 6, hits
# ทางตัวเอกสั้นกว่าหรือเท่าทางเดิมทุกคู่เสียง
for g in ['เสียงผู้หญิง', 'เสียงผู้ชาย']:
    old = len(OLD_A) + len(L['voiceVideoEN'][g]) + len(OLD_S)
    new = len(NEW_A) + len(L['voiceStarEN'][g]) + len(NEW_S)
    assert new <= old, (g, new, old)
print(f'✅ v134: แยกเสียงตัวเอกพูดเอง {len(hits)} op {sorted(hits)} · ทางตัวเอกสั้นกว่าเดิม {old - new} ตัวอักษร')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
