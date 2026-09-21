#!/usr/bin/env python3
# showhow-v20-anchor.py — ปิด 2 รอยรั่วความต่อเนื่องที่เจอจากการวาดจริง 3 ชุด × 6 ช่วง (2026-09-21)
# ① ถุงมือเปลี่ยนสี (น้ำเงิน→เหลือง) ตั้งแต่ช่วง 2 แล้วช่วง 3-6 ลอกสีผิดต่อ
#    ราก: "เสื้อผ้าและถุงมือ…สีเดิม" อยู่ **นอก** วงเล็บตัวหนาของรายการ "ของติดตาย" ⇒ น้ำหนักต่ำกว่าเพื่อนร่วมประโยค
#    แก้: ย้ายเข้าไปอยู่ในกลุ่มตัวหนาเดียวกัน (ความยาวเท่าเดิม)
# ② ช่วงที่บทเขียนเป็นโคลสอัพสินค้าล้วนทั้ง 5 ฉาก = ไม่มีหลักยึดของห้องในภาพเลย ⇒ โมเดลไปหยิบห้องสต็อก/ถุงมือสต็อก
#    แก้ที่ต้นทาง (บท): ทุกช่วง 10 วิ ต้องมีอย่างน้อย 2 ฉากที่เห็นพื้นที่จริงเป็นฉากหลัง — ได้ทั้งความต่อเนื่องและคลิปไม่น่าเบื่อ
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)

OLD_G = 'ตำแหน่งประตูหน้าต่าง** · เสื้อผ้าและถุงมือของคนทำต้องเป็นชุดเดิมสีเดิม'
NEW_G = 'ตำแหน่งประตูหน้าต่าง · เสื้อผ้าและถุงมือของคนทำ (ชุดเดิมสีเดิม)**'
s = json.dumps(d, ensure_ascii=False)
n = s.count(OLD_G); assert n == 6, f'ถุงมือ {n} จุด (คาด 6)'
d = json.loads(s.replace(OLD_G, NEW_G))

OLD_S = '- สถานที่เดียวกันทุกฉาก:'
ADD_S = ('- ทุกช่วง 10 วินาที (5 ฉากติดกัน) ต้องมีอย่างน้อย 2 ฉากที่เห็นพื้นที่จริงเป็นฉากหลัง (ภาพกว้างหรือปานกลาง)'
         ' — ห้ามมีช่วงใดเป็นโคลสอัพสินค้าหรือมือล้วนครบทั้ง 5 ฉาก\n')
sys_ = d['brain']['mn']['sys']; assert OLD_S in sys_ and ADD_S not in sys_
d['brain']['mn']['sys'] = sys_.replace(OLD_S, ADD_S + OLD_S)

open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
G = os.path.join(HERE, 'showhow-v9-board-collage.py'); g = open(G, encoding='utf-8').read()
assert g.count(OLD_G) == 1
open(G, 'w', encoding='utf-8').write(g.replace(OLD_G, NEW_G))
print('✓ v20 · ถุงมือเข้ากลุ่มตัวหนา 6 จุด · กฎหลักยึดพื้นที่ในบท (+%d ตัวอักษรใน sys) · %d bytes' % (len(ADD_S), os.path.getsize(P)))
