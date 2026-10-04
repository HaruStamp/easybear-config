#!/usr/bin/env python3
"""showhow-v120 (พี่หมีสั่ง "แก้เลย" 2026-10-04) — mnPlan: ย้ายกฎตามตัวเลือกจาก prompt ไปท้าย systemInstruction

ต้นเหตุ: Flow.generate.text ล้มหลอก "Text generation service unavailable" เมื่อ prompt ≥ ~4,000 ตัวอักษร
(systemInstruction ไม่ติด · podcast พบ · engine ไม่ clamp prompt ของ llm op) · วัดแล้ว: เลือกตัวเลือกพิเศษหลายอย่าง = สูงสุด 4,817
แก้: prompt เหลือ "ข้อมูลจากผู้ใช้" · กฎที่โผล่ตามตัวเลือก (กล้อง · ย้ำสไตล์ · โหมดคน · เสียงพากย์ · ข้อความบนคลิป · ผู้แสดง)
     ย้ายไปต่อท้าย systemInstruction ใต้หัวข้อเดียว — เนื้อกฎเดิมทุกตัวอักษร · sys resolve ด้วย ctx เดียวกับ prompt (engine-exec.ts:57) ⇒ {item.*} ใช้ได้
ใช้: python3 scripts/showhow-v120-plan-rules-to-sys.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
op = next(o for o in c['ops'] if o['id'] == 'mnPlan')
pr = op['prompt']; p0 = pr['parts'][0]['parts']
s = lambda x: json.dumps(x, ensure_ascii=False)
# ── ยืนยันโครงก่อนแตะ (โครงเปลี่ยน = ล้มดัง) ──
assert 'item.camMode' in s(p0[11]) and 'ย้ำ: สไตล์ภาพ' in s(p0[12]), 'p0.11/p0.12 ไม่ใช่กล้อง/ย้ำสไตล์'
assert 'โหมดคนในคลิป' in s(pr['parts'][1]) and 'charPlan' in s(pr['parts'][2]) and s(pr['parts'][3]) == '"\\n"'
assert 'ข้อมูลคนในคลิปจากผู้ใช้' in s(pr['parts'][4])
assert 'voicePlan' in s(pr['parts'][5]) and 'textPlan' in s(pr['parts'][7]) and 'castPlan' in s(pr['parts'][8]) and 'castOverrideTH' in s(pr['parts'][9])
assert len(pr['parts']) == 10 and len(p0) == 13
moved = [p0[11], p0[12], pr['parts'][1], pr['parts'][2], pr['parts'][3], pr['parts'][5], pr['parts'][6], pr['parts'][7], pr['parts'][8], pr['parts'][9]]
before = len(s(pr))
# prompt ใหม่: ข้อมูลผู้ใช้ทั้งหมด (p0.0-p0.10) + ข้อมูลคนในคลิปจากผู้ใช้ (p4)
pr['parts'][0]['parts'] = p0[:11]
pr['parts'] = [pr['parts'][0], pr['parts'][4]]
# sys ใหม่: ของเดิม + หัวข้อ + กฎที่ย้ายมา
head = '\n\n══ กฎเฉพาะงานนี้ (มาจากตัวเลือกที่ผู้ใช้เลือก — ใช้ร่วมกับข้อมูลงานในข้อความผู้ใช้) ══\n'
sys0 = op['systemInstruction']
op['systemInstruction'] = {'op': 'concat', 'parts': [sys0, head] + moved}
after = len(s(pr))
txt = s(op['prompt'])
for k in ('charPlan', 'voicePlan', 'textPlan', 'castPlan', 'castOverrideTH', 'item.camMode'):
    assert k not in txt, k + ' ยังอยู่ใน prompt'
    assert k in s(op['systemInstruction']), k + ' ไม่ได้ไป sys'
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'v120: ย้ายกฎ {len(moved)} ก้อน · prompt template {before} → {after} ตัวอักษร (JSON)')
