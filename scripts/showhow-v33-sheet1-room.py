#!/usr/bin/env python3
# showhow-v33-sheet1-room.py — แผ่นบอร์ดของช่วงตัวเอง ต้องเป็นตัวตัดสิน "ห้อง" ไม่ใช่แค่ "กรอบภาพ/แสง" (พบ 2026-09-22)
# อาการ: คลิป 60 วิ ที่ผลิตจริง — **วิดีโอช่วง 1 เป็นคนละห้องกับบอร์ดช่วง 1** (บอร์ด = มุมอาบน้ำกระเบื้องลายอิฐ · วิดีโอ = โถส้วม+พื้นกระเบื้องใหญ่)
# ราก (อ่าน prompt ที่ยิงจริงด้วย render-op · ไม่ได้เดา): ถ้อยคำของเราสั่งกลับด้าน
#   "image 1 = this part's 5 scenes (follow each panel's **framing and lighting**)"      ← แผ่นของตัวเอง = แค่กรอบภาพ/แสง
#   "other sheets = other parts: **keep their room layout**, light and objects"           ← แผ่นของช่วงอื่น = ห้อง!
#   ⇒ โมเดลไม่เคยถูกสั่งให้ยึดห้องจากแผ่นของช่วงตัวเอง · บทฉากเขียนกว้าง ("ภาพกว้างห้องน้ำ") ⇒ มันคิดห้องเองได้
# แก้: ให้แผ่นที่ 1 เป็นตัวล็อกห้อง/สุขภัณฑ์/กรอบภาพ/แสง · แผ่นอื่น = "ห้องเดียวกัน" (ไม่ใช่ต้นแบบห้อง)
# 🪤 เบาะแสมาจากทีม minimal (เขาชี้ว่าคำว่า keep their room layout ของแผ่นอื่นอาจดึงห้อง) — ไล่ prompt จริงแล้วเจอว่าเป็นคนละจุดแต่ตระกูลเดียวกัน
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
OLD = ("Attached storyboard sheets are the plan: image 1 = this part's 5 scenes (follow each panel's framing and lighting); "
       "other sheets = other parts: keep their room layout, light and objects. Never copy a sheet or show one on screen.")
NEW = ("Attached storyboard sheets are the plan: image 1 = this part's 5 scenes — copy its room, fixtures, surfaces, framing and lighting; "
       "other sheets = other parts of the same room, same light. Never copy a sheet or show one on screen.")
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)
def sub(node, box):
    if isinstance(node, dict): return {k: sub(v, box) for k, v in node.items()}
    if isinstance(node, list): return [sub(v, box) for v in node]
    if isinstance(node, str) and OLD in node: box[0] += node.count(OLD); return node.replace(OLD, NEW)
    return node
box = [0]; d = sub(d, box)
assert box[0] == 6, f'เจอกฎแผ่นบอร์ด {box[0]} จุด (คาด 6 = วิดีโอ 6 ช่วง)'
print(f'  แก้ {box[0]} จุด · {len(NEW)-len(OLD):+d} ตัวอักษร/ช่วง')
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print('✓ v33 ·', os.path.getsize(P), 'bytes')
