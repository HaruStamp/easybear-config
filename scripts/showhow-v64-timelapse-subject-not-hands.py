#!/usr/bin/env python3
# showhow v64 — ไทม์แลปส์: ห้ามให้ "มือ" เป็นประธานของประโยคฉาก (นี่คือสิ่งที่ทำให้วิดีโอเข้าโคลสอัพ)
#
# หลักฐานจากเคสที่ดินจริงของพี่หมี (30 วิ · arc=ไทม์แลปส์ · มีรูปห้อง):
#   camN = "กว้างนิ่ง" 15/15 → แปลงเป็น "Camera: static locked-off shot, camera never moves" ครบทุกฉาก
#   แต่คลิปยังโคลสอัพครึ่งคลิป เพราะ s*en เขียนว่า
#       "Close-up of a hand hammering a wooden survey stake"   ← ฝ่าฝืนคำสั่งห้ามของ v63 ตรง ๆ
#       "Hands using a shovel to dig..." · "Hand laying red bricks..." · "Hand rolling white paint..."
#   ⇒ **ประโยคบรรยายฉากชนะคำสั่งกล้องเสมอ** · ประธาน = มือ แปลว่าโคลสอัพโดยปริยาย
#
# บทเรียน: v63 เป็น "ข้อห้าม" (ห้ามเขียนคำว่า close-up) แต่ไม่ได้บอกว่าให้เขียนแบบไหนแทน
#   ⇒ v64 เปลี่ยนเป็น **คำสั่งเชิงบวกที่ตรวจเองได้**: ประธานของประโยคต้องเป็นคน/เครื่องจักร/ตัวงาน "ในระยะไกล"
#     พร้อมตัวอย่างคู่ ผิด→ถูก ให้ลอกรูปประโยค
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ARC = 'ไทม์แลปส์กล้องนิ่ง'
ap = c['lookups']['arcPlan']
old = ap[ARC]
assert 'ห้ามเขียนคำว่า close-up' in old, 'ข้อความ v63 เปลี่ยนไปแล้ว — หยุด'

ap[ARC] = ('โครงเรื่องที่ผู้ใช้เลือก: ไทม์แลปส์กล้องนิ่ง — กล้องตั้งนิ่งมุมเดียวทั้งคลิป เห็นทั้งพื้นที่ตลอด '
           '🔴 **s*en ทุกฉากต้องเป็นภาพระยะไกลจากกรอบเดียวกัน**: ประธานของประโยคต้องเป็น "พื้นที่ / ตัวงาน / คนทั้งตัวที่อยู่ไกล ๆ" '
           '**ห้ามให้มือหรือเครื่องมือเป็นประธาน** และห้ามใช้คำว่า close-up / macro / pan / zoom / tilt / handheld เด็ดขาด — '
           'ผิด: "Hand laying red bricks on a beam" · ถูก: "Same wide shot, two workers lay the brick wall along the left edge of the plot" · '
           'ผิด: "Close-up of a hand hammering a stake" · ถูก: "Same wide shot, a worker hammers boundary stakes near the front of the plot" · '
           'ทุกฉากขึ้นต้นด้วย "Same wide shot, " (ฉากแรกใช้ "Fixed wide shot of …" · ฉากสุดท้ายใช้ "Same wide shot as scene 1, ") · '
           'camN ทุกฉาก = "กว้างนิ่ง" · s*th ทุกฉากขึ้นต้นว่า "มุมกว้างเดิม" เพราะสตอรีบอร์ดอ่านช่องนี้ · '
           'ฉากติดกันห่างกันแค่ **ขั้นเดียว** ของงาน ห้ามข้ามขั้น · สิ่งที่ทำไปแล้วต้องสะสมค้างอยู่ในเฟรมทุกฉากถัดไป · '
           'ฉากสุดท้าย = กรอบเดียวกับฉากแรก เห็นผลลัพธ์เต็มพื้นที่')

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'v64 ok · arcPlan[ไทม์แลปส์] {len(old)} → {len(ap[ARC])}')
