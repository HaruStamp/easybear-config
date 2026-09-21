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
    ('ป้ายการ์ดขาว', 'สะอาด อ่านง่าย แบบคลิปสอนในเพจ',
     'ตัวอักษรไทยหนาสีเข้ม วางบนการ์ดสีขาวมุมมนโค้งมาก ขอบการ์ดเว้นรอบข้อความเท่ากัน มีเงานุ่มใต้การ์ด (bold dark Thai text on a white rounded-corner card with even padding and a soft drop shadow)'),
    ('เน้นคำสำคัญ', 'เด่นแบบคลิปไวรัล',
     'ตัวอักษรไทยหนามาก 2 บรรทัด สีขาว มีขอบเข้มบาง · คำสำคัญที่สุดเปลี่ยนเป็นสีเหลืองสดหรือส้มสด 1 คำ (very bold Thai text, two lines, white with thin dark outline, one key word in bright yellow or orange)'),
    ('แถบสีทึบ', 'แนวสปอร์ต สะดุดตาสุด',
     'ตัวอักษรไทยหนาสีขาว วางบนแถบสีทึบเข้ม แถบละบรรทัด (ข้อความมีกี่บรรทัดก็มีแถบเท่านั้น ห้ามแต่งข้อความเพิ่มให้ครบแถบ) แถบเหลื่อมกันเล็กน้อย กว้างพอดีข้อความแต่ละบรรทัด (bold white Thai text on solid dark colour bars, one bar per line of the given text, slightly offset, sized to each line)'),
    ('ไฮไลต์ปากกา', 'สดใส เป็นกันเอง',
     'ตัวอักษรไทยหนาสีเข้ม มีแถบสีสดแบบปากกาไฮไลต์ลากทับใต้คำสำคัญ ปลายแถบไม่เรียบเหมือนลากด้วยมือ (bold dark Thai text with a bright hand-drawn highlighter stroke behind the key word)'),
    ('ตัวหนาขอบหนา', 'เรียบง่าย ใช้ได้ทุกพื้นหลัง',
     'ตัวอักษรไทยหนาใหญ่ สีขาว มีขอบสีเข้มหนารอบตัวอักษรและเงาตกนุ่ม (bold Thai sans-serif, white fill, thick dark outline, soft drop shadow)'),
    ('บางมินิมอล', 'เรียบหรู ดูแพง',
     'ตัวอักษรไทยเส้นบางเรียบ เว้นช่องไฟกว้าง สีขาว เงาบางมาก (clean thin Thai sans-serif, wide letter spacing, white, very soft shadow)'),
]
DEFAULT = STYLES[0][2]   # ป้ายการ์ดขาว

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
