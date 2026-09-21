#!/usr/bin/env python3
# showhow-v13-textstyle.py — สไตล์ข้อความบนคลิปให้ "สวย เด่น" เลือกได้จริง (พี่หมีสั่ง 2026-09-20)
# ปัญหาเดิม: ① มี 3 ตัวเลือก แต่เป็นแค่ "หน้าตาตัวอักษร" ไม่มีการตกแต่ง
#            ② prompt วิดีโอฮาร์ดโค้ด "white, soft shadow" ต่อท้าย {values.svText} · บอร์ดฮาร์ดโค้ด "ตัวอักษรสีเข้ม"
#               ⇒ เลือกสไตล์ไหนก็ออกมาเกือบเหมือนกัน และสองที่ขัดกันเอง (ขาว vs เข้ม)
# แก้: ตัวเลือก 6 แบบ แต่ละแบบพก ฟอนต์+สี+การตกแต่ง มาครบในสตริงเดียว · ถอดสี/เงาที่ฮาร์ดโค้ดออกจากทั้ง 2 ฝั่ง
#      · วลี "หัวข้อตัวอักษรสีเข้มที่เข้ากับโทนสีของคลิป" (ยาม dry-run-minimal ของ starter เช็คคำนี้) เปลี่ยนเป็นเงื่อนไข "ถ้าสไตล์ไม่ได้ระบุสี"
# ลำดับรัน: base → v9-board-collage → v10-endshot → v11-board-order → ไฟล์นี้
import json, os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'showhow-dev.json')
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)

# value = ข้อความที่ถูกแทนใน prompt ทั้งบอร์ดและวิดีโอ (ไทย + วงเล็บอังกฤษให้โมเดลวิดีโอจับได้)
STYLES = [
    ('ตัวหนาขอบหนา', 'อ่านง่ายที่สุด เด่นทุกพื้นหลัง',
     'ตัวอักษรไทยหนาใหญ่ สีขาว มีขอบสีเข้มหนารอบตัวอักษรและเงาตกนุ่ม (bold Thai sans-serif, white fill, thick dark outline, soft drop shadow)'),
    ('ตัวหนาบนแถบสี', 'แบบคลิปไวรัล สะดุดตา',
     'ตัวอักษรไทยหนาสีขาว วางบนแถบสีทึบสั้น ๆ กว้างพอดีข้อความ มุมมน อยู่ในกรอบภาพ (bold Thai sans-serif, white text on a short solid colour bar sized to the text, rounded corners)'),
    ('ลายมือ', 'อบอุ่นเป็นกันเอง',
     'ตัวอักษรลายมือภาษาไทยเส้นโค้งนุ่มหัวกลม สีขาว มีเงานุ่มรองรับ (cute Thai handwritten script, white, soft shadow)'),
    ('บางมินิมอล', 'เรียบหรู ดูแพง',
     'ตัวอักษรไทยเส้นบางเรียบ เว้นช่องไฟกว้าง สีขาว เงาบางมาก (clean thin Thai sans-serif, wide letter spacing, white, very soft shadow)'),
    ('ตัวใหญ่เรืองแสง', 'นุ่มตา ดูพรีเมียม',
     'ตัวอักษรไทยหนาใหญ่ สีขาว มีแสงเรืองนวลรอบตัวอักษร (bold Thai sans-serif, white, soft glow halo)'),
    ('ตัวเข้มบนพื้นสว่าง', 'เหมาะกับฉากสว่างมาก',
     'ตัวอักษรไทยหนาสีเข้มที่เข้ากับโทนสีของคลิป ไม่มีขอบ เงาบาง (bold Thai sans-serif in a dark tone matching the clip, no outline, light shadow)'),
]
DEFAULT = STYLES[0][2]

n = 0
def walk(node):
    global n
    if isinstance(node, dict):
        if node.get('field') == 'svText' and node.get('options'):
            node['options'] = [{'value': v, 'label': lab, 'desc': desc} for lab, desc, v in STYLES]; n += 1
        for v in node.values(): walk(v)
    elif isinstance(node, list):
        for v in node: walk(v)
walk(d)
assert n == 1, f'เจอ UI ของ svText {n} จุด (คาด 1)'
d['values']['svText'] = DEFAULT

# ── ถอดสี/เงาที่ฮาร์ดโค้ด ──
s = json.dumps(d, ensure_ascii=False)
OLD_BOARD = ' · หัวข้อตัวอักษรสีเข้มที่เข้ากับโทนสีของคลิป'
NEW_BOARD = ' (ถ้าสไตล์ไม่ได้ระบุสี ให้ใช้หัวข้อตัวอักษรสีเข้มที่เข้ากับโทนสีของคลิป)'   # ★ยาม starter เช็คคำว่า "หัวข้อตัวอักษรสีเข้มที่เข้ากับโทนสีของคลิป" — ต้องคงคำนี้ไว้
cb = s.count(OLD_BOARD); s = s.replace(OLD_BOARD, NEW_BOARD)
OLD_VID = 'style {values.svText}, white, soft shadow, one line'
NEW_VID = 'style {values.svText} — follow that style exactly for font, colour and treatment, one line'
cv = s.count(OLD_VID); s = s.replace(OLD_VID, NEW_VID)
assert cb and cv, (cb, cv)
d = json.loads(s)

open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print(f'✓ v13 textstyle · ตัวเลือก {len(STYLES)} แบบ · ถอดสีบอร์ด {cb} จุด · ถอด white/soft shadow ในวิดีโอ {cv} จุด ·', os.path.getsize(P), 'bytes')
