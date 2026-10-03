#!/usr/bin/env python3
"""showhow-v118 (พี่หมีสั่ง 2026-10-03) — 2 เรื่อง
① มาตรฐานเพดานเวลารอผลทุกโปรแกรม (starter ประกาศ): ภาพ 180 วิ · วิดีโอ 300 วิ — ตั้ง timeoutMs ชัดบน mnBoard..6 / mnVideo..6
   (ค่ากลาง engine เดิม ภาพ 90 / วิดีโอ 180 วิ · ใส่ใน config = ตัวขายได้ทันทีไม่ต้อง remix)
② หน้าจัดการงาน แถบ [ค้นหา][ใช้/ปิดทั้งหมด][+เพิ่มงาน] — ปุ่ม "เพิ่มงาน" ล้นขวาที่ iframe 421-650px
   (starter วัด · podcast แก้แบบเดียวกัน) ⇒ เลิกตัดบรรทัดที่ 720px แทน 420px · แตะแถวนี้แถวเดียว
ใช้: python3 scripts/showhow-v118-timeouts-addbtn.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ops = {o['id']: o for o in c['ops']}
n = 0
for k in [''] + [str(i) for i in range(2, 7)]:
    ops['mnBoard' + k]['timeoutMs'] = 180000; ops['mnVideo' + k]['timeoutMs'] = 300000; n += 2
assert n == 12 and all(ops['mnBoard' + k]['type'] == 'image' and ops['mnVideo' + k]['type'] == 'video' for k in [''] + [str(i) for i in range(2, 7)])
row = c['phases'][0]['form'][1]['card'][2]['card'][0]
kids = [k.get('label') or k.get('placeholder') for k in row['card']]
assert kids[0] == 'ค้นหางาน…' and kids[-1] == 'เพิ่มงาน', kids
assert row['className'] == 'items-center gap-2.5 flex-wrap @[420px]:flex-nowrap'
row['className'] = 'items-center gap-2.5 flex-wrap @[720px]:flex-nowrap'
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v118: timeoutMs 12 op · แถบเพิ่มงาน @[720px]')
