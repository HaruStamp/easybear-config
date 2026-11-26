#!/usr/bin/env python3
"""showhow-v147 — คืน mnFace เข้า auto.productLoop.gens (Dev ขึ้น engine v1.25 แล้ว · มี loopGenApplies ตั้งแต่ 1.23)
v144 ถอดออกเพราะ engine 1.22 นับ slot face ว่าง (where ราย kid ไม่ตรง) = พัง → รอบหยุด
ตอนนี้ Dev 6eb190f0 = engine 1.25.0 ⇒ ใส่กลับหน้าบอร์ด (ตำแหน่งเดิมของ v138) · ประโยครูปหน้าของ v144 (ต้องมีรูปจริง) คงไว้
ใช้: python3 scripts/showhow-v147-face-gens-engine125.py [showhow-dev.json]  (รันซ้ำ = ไม่ทำอะไร)
⚠ ห้ามใช้กับ config ที่ tool ยังเป็น engine < 1.23
"""
import json, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
s0 = open(P, encoding='utf-8').read()
c = json.loads(s0)
assert json.dumps(c, ensure_ascii=False, indent=1) + '\n' == s0
g = c['auto']['productLoop']['gens']
if 'mnFace' in g:
    print('v147: ทำไปแล้ว — ไม่แตะ'); sys.exit(0)
assert g[0] == 'mnBoard', g
assert any(s.get('op') == 'mnFace' for s in c['stages'])
g.insert(0, 'mnFace')
open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
print('✅ v147: mnFace กลับเข้า productLoop.gens (หน้า mnBoard)')
