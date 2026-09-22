#!/usr/bin/env python3
# showhow v75 — ย้อน "หมุดมุมเปิด" ของ v73 (แผ่นที่ 2 ของ mnVideo3-6 กลับเป็นบอร์ดช่วงก่อน)
#
# ทำไม: v73 แก้ห้องในฉากปิดได้จริง (บอร์ดช่อง 20 = ครัวขาวใบเดียวกับช่อง 1 · วิดีโอช่วง 4 ก็ห้องถูก)
#       แต่ **แผ่นสตอรีบอร์ดหลุดเข้าคลิป** ซึ่งร้ายแรงกว่า:
#         · วิดีโอช่วง 3 — 2 เฟรมแรกมีอินเซ็ตช่องบอร์ด + วงกลมเลข 11
#         · วิดีโอช่วง 4 — t=2.4 วิ มีวงกลมเลข 17 · t=8.6 วิ ทั้งเฟรมเป็นคอลัมน์ช่อง 16/18/20
# หลักฐานที่ทำให้เชื่อว่าเป็นผลของ v73 ไม่ใช่ความบังเอิญ (บทเดียวกัน brief เดียวกัน):
#         · op ที่ v73 แก้ = mnVideo3, mnVideo4 → **หลุดทั้งคู่**
#         · op ที่ไม่ได้แตะ = mnVideo2 → **สะอาด**
#         · คลิปรอบก่อน v73 (docs/qa/2026-09-22-regress40/) ช่วง 3 และ 4 → **สะอาดทั้งคู่**
#       🪤 เป็นการสังเกตจาก 1 รอบผลิต (เครดิตหมดก่อนได้รอบยืนยัน) — เลือกทางที่ปลอดภัยไว้ก่อน
# กลไกที่น่าจะเป็น: บอร์ดช่วง 1 มีเลขช่อง 1-5 แต่ prompt ของช่วง 4 พูดถึงฉาก 16-20
#       ⇒ แผ่นที่ "ไม่เข้าคู่กับบทตรงหน้า" ถูกโมเดลตีความว่าเป็นของให้วาด ไม่ใช่ของให้ดูเฉย ๆ
# เรื่องห้องในฉากปิด: เคสนี้เป็นงาน **ไม่มีรูปห้องเลย** ⇒ ไม่มี LOCATION LOCK
#       เคสที่แนบรูปห้องจริง (docs/qa/2026-09-22-garden40-v51/ · บ้านพี่หมี) ล็อกห้องได้ครบ 4 ช่วงอยู่แล้ว
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))

back = []
for op in c['ops']:
    if op['id'] not in ('mnVideo3', 'mnVideo4', 'mnVideo5', 'mnVideo6'):
        continue
    k = int(op['id'].replace('mnVideo', ''))
    also = op['refs']['also']
    assert also[0]['from'] == 'tasks' and also[0]['slot'] == 'board', (op['id'], also[0])
    prev = {'from': 'tasks', 'by': '{item.id}', 'slot': 'board%d' % (k - 1)}
    if k == 3:
        prev['when'] = 'values.svSec>10'      # ของเดิมก่อน v73 — board2 มีเฉพาะเมื่อยาวกว่า 10 วิ
    also[0] = prev
    back.append((op['id'], 'board%d' % (k - 1)))
assert len(back) == 4, back

for op in c['ops']:
    if op['id'].startswith('mnVideo'):
        r = op['refs']
        sheets = [r['slot']] + [a['slot'] for a in r['also'] if a['from'] == 'tasks']
        assert len(sheets) <= 2 and len(set(sheets)) == len(sheets), (op['id'], sheets)

json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v75 ok · คืนแผ่นที่ 2 เป็นบอร์ดช่วงก่อน:', back)
