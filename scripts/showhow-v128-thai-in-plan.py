#!/usr/bin/env python3
"""showhow-v128 — สไตล์ "ไทยท้องถิ่น" ยังออกเป็นบ้านทั่วไป (ทดสอบ v127 บทสด 2026-10-13)

ราก: บทที่ LLM เขียน (s1th-s5th) ไม่มีของไทยเลย ("โต๊ะไม้รก…" "โต๊ะเรียบร้อย…") — บอร์ดวาดตามบรรทัดฉาก
  คำสไตล์บรรทัดเดียวสู้บรรทัดฉาก 5 บรรทัดไม่ได้
แก้: stylePlan thai สั่งให้ "เขียนของไทยลงในบทภาพทุกฉาก" (ฉากเป็นตัวที่บอร์ด/วิดีโอวาดจริง)
  + styleVideoEN thai ระบุของให้ชัดขึ้น (≤ 50 = ประโยคสมจริงเดิม)
  stylePlan อยู่ใน mnPlan (llm · ไม่ผ่าน clamp 3,900) · board/video ไม่ยาวขึ้น
ใช้: python3 scripts/showhow-v128-thai-in-plan.py  (รันบน v127)
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
L = c['lookups']
L['stylePlan']['thai'] = ('สมจริง บ้านไทยท้องถิ่น · s*th และ s*en ทุกฉากต้องเขียนของไทยที่เห็นในฉาก ≥1 อย่าง '
                          '(เช่น พื้นไม้ ผนังไม้ หน้าต่างบานเกล็ด เสื่อ ผ้าขาวม้า พัดลมตั้งพื้น ปิ่นโต) เปลี่ยนของไปตามฉากได้')
L['styleVideoEN']['thai'] = 'real Thai home: teak wood, louvre windows, fan'
assert len(L['styleVideoEN']['thai']) <= len(L['styleVideoEN']['real']), len(L['styleVideoEN']['thai'])
assert all(ord(ch) < 128 for ch in L['styleVideoEN']['thai'])
print('✅ v128: stylePlan thai สั่งของไทยลงบททุกฉาก · styleVideoEN thai', len(L['styleVideoEN']['thai']))
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
