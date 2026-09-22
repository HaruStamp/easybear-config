#!/usr/bin/env python3
"""showhow v46 — ถ้อยคำปุ่มเมนูตามมาตรฐานร่วม 3 ทีม (STANDARD-multipart §④-ค ข้อ ⑨)

  "Gen ภาพใหม่"      → "Gen บอร์ดใหม่"      (ชัดว่าเป็นสตอรีบอร์ด ไม่ใช่รูปสินค้า)
  "เลือกภาพ"         → "เลือกบอร์ด"          (เฉพาะปุ่มที่ into = ช่อง board เท่านั้น)
  "ใส่เป็นช่วง N …"   → "ช่วง N …"            (ข้อในเมนู pick — สั้นลง อ่านเป็นตัวเลือกช่วง)
  "Gen ใหม่" 2 ปุ่มในแถวเดียวกัน → "Gen บอร์ดใหม่" / "Gen วิดีโอใหม่"

🪤 **ห้ามกรองด้วย label อย่างเดียว** (ทีม minimal เตือน): "เลือกภาพ" ใช้กับ **ปุ่มเลือกรูปสินค้า/รูปห้อง/รูปหน้า** ด้วย
   ซึ่งคนละความหมายกันสิ้นเชิง ⇒ กรองด้วย **การมี `menu` + เป้าหมายของข้อในเมนู** (into ขึ้นต้นด้วย board/video)
"""
import json, pathlib

P = pathlib.Path(__file__).resolve().parent.parent / 'showhow-dev.json'
d = json.loads(P.read_text(encoding='utf-8'))

def kind_of(node):
    """บอกว่าปุ่มเมนูนี้ทำงานกับบอร์ดหรือวิดีโอ — ดูจากเป้าของข้อในเมนู ไม่ใช่จาก label"""
    for m in node.get('menu') or []:
        t = m.get('into') or (m.get('chain') or [None])[0] or ''
        if str(t).startswith(('board', 'mnBoard')): return 'board'
        if str(t).startswith(('video', 'mnVideo')): return 'video'
    return None

hit = {'retry': 0, 'pick': 0, 'items': 0}
def walk(n):
    if isinstance(n, dict):
        if n.get('menu'):
            k = kind_of(n)
            lab = str(n.get('label') or '')
            if n.get('el') == 'retry-button' and k:
                new = f'Gen {"บอร์ด" if k=="board" else "วิดีโอ"}ใหม่'
                if lab != new: n['label'] = new; hit['retry'] += 1
            if n.get('el') == 'pick-button' and k:
                new = 'เลือกบอร์ด' if k == 'board' else 'เลือกวิดีโอ'
                if lab != new: n['label'] = new; hit['pick'] += 1
            for m in n['menu']:
                ml = str(m.get('label') or '')
                if ml.startswith('ใส่เป็นช่วง '):
                    m['label'] = ml.replace('ใส่เป็นช่วง ', 'ช่วง ', 1); hit['items'] += 1
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)

walk(d.get('phases'))
assert hit['retry'] and hit['pick'] and hit['items'], f'ไม่ได้แก้อะไรเลย: {hit}'

# ยาม: ห้ามเหลือ 2 ปุ่มเมนูชื่อเดียวกันในแถวเดียวกัน
def rows_with_dup(n, bad):
    if isinstance(n, dict):
        kids = n.get('card') if isinstance(n.get('card'), list) else None
        if n.get('el') == 'row' and kids:
            labs = [str(c.get('label')) for c in kids if isinstance(c, dict) and c.get('menu')]
            for l in set(labs):
                if labs.count(l) > 1: bad.append((l, labs))
        for v in n.values(): rows_with_dup(v, bad)
    elif isinstance(n, list):
        for v in n: rows_with_dup(v, bad)
bad = []; rows_with_dup(d.get('phases'), bad)
assert not bad, f'ยังมีปุ่มเมนูชื่อซ้ำในแถวเดียวกัน: {bad[:2]}'

# ยาม: ปุ่มเลือกรูปสินค้า/ห้อง/หน้า ต้องยังชื่อ "เลือกภาพ" เหมือนเดิม (ห้ามโดนลูกหลง)
s = json.dumps(d, ensure_ascii=False)
assert '"เลือกภาพ"' in s, 'ปุ่มเลือกรูปสินค้า/ใบหน้าโดนเปลี่ยนชื่อไปด้วย — ผิด'

P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f"เปลี่ยนชื่อ: retry {hit['retry']} ปุ่ม · pick {hit['pick']} ปุ่ม · ข้อในเมนู {hit['items']} ข้อ")
