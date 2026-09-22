#!/usr/bin/env python3
"""showhow v47 — แถบปุ่มใน lightbox: ดาวน์โหลดขวาสุด + ปุ่มกว้างเท่ากันจริง (มาตรฐานร่วม §④-ค ⑧ ข้อ ข/ค)

มาตรฐานที่เป็นของกลางจริงมี 3 ข้อ (ทีม minimal แก้เอกสารให้ชัดหลังพบว่าเขียนกำกวม):
  (ก) มุมมองลิสต์กับกริดของ **หน้าเดียวกัน** ต้องมีแถบเหมือนกัน   ← ของเราใช้ lightboxActions ชุดเดียวต่อหน้า ผ่านอยู่แล้ว
  (ข) ดาวน์โหลดขวาสุด                                          ← 🔴 คลังคลิปของเราอยู่ซ้าย
  (ค) ปุ่มกว้างเท่ากัน                                          ← 🔴 ใช้ flex-1 ซึ่งไม่การันตี
  ("หน้าไหนมีปุ่มอะไร" **ไม่ใช่มาตรฐาน** — คลังคลิปไม่ต้องมีเมนู Gen ทั้ง minimal และเราตั้งใจไม่ใส่
   เหตุผล: คลังคลิป = ที่ดูผลงานที่เสร็จแล้ว ยัดปุ่ม Gen = ชวนให้เผาเครดิตจากหน้าที่กำลังชื่นชมผลงาน)

ท่าทำให้กว้างเท่ากัน (ยืมจาก minimal · ผ่านสนามแล้ว):
  แถว   `w-full !grid grid-flow-col auto-cols-fr gap-2 !items-stretch`
  ลูก    `!w-full !min-w-0`
🔑 `auto-cols-fr` ทำให้ **ช่องกว้างเท่ากันไม่ว่าลูกจะเป็น el อะไรหรือคุมคลาสได้แค่ไหน** ⇒ แก้ปัญหา "ตัวห่อของปุ่มเมนู" ให้เองในตัว
   (`!flex-1` ต้องไปลงที่ flex item จริง ๆ ซึ่งปุ่มเมนูคือตัวห่อ ⇒ ใช้ไม่ได้ก่อน engine 1.12.0)
🪤 **grid ไม่ wrap** ⇒ ต้องถอด `!min-w-[132px]` ออก ไม่งั้น 3 ช่อง × 132px + gap ล้นจอมือถือ (hardsell วัดกับ 398px มาแล้ว)
🪤 เก็บกวาด: className เดิมมี token `!` เดี่ยว ๆ ลอยอยู่ (ขยะจากการต่อสตริงรอบก่อน) — ลบทิ้งด้วย
"""
import json, pathlib, re

P = pathlib.Path(__file__).resolve().parent.parent / 'showhow-dev.json'
d = json.loads(P.read_text(encoding='utf-8'))

ROW = 'w-full !grid grid-flow-col auto-cols-fr gap-2 !items-stretch'
rows = []
def find(n):
    if isinstance(n, dict):
        if 'lightboxActions' in n:
            for r in n['lightboxActions']:
                if isinstance(r, dict) and r.get('el') == 'row': rows.append(r)
        for v in n.values(): find(v)
    elif isinstance(n, list):
        for v in n: find(v)
find(d.get('phases'))
assert len(rows) == 2, f'เจอแถว lightbox {len(rows)} แถว (คาด 2 = หน้าผลิต + คลังคลิป)'

def clean(cn):
    cn = re.sub(r'(?<![\w!-])!(?=\s|$)', ' ', cn)              # token `!` เดี่ยว ๆ
    cn = re.sub(r'!?min-w-\[132px\]\s*', '', cn)               # grid ไม่ wrap ⇒ ถอดความกว้างขั้นต่ำ
    cn = re.sub(r'!?flex-1\s*', '', cn)                        # ไม่ใช้ flex แล้ว
    cn = re.sub(r'\s+', ' ', cn).strip()
    return ('!w-full !min-w-0 ' + cn) if '!w-full' not in cn else cn

moved = 0
for r in rows:
    r['className'] = ROW
    kids = r.get('card') or []
    for k in kids:
        if isinstance(k, dict) and k.get('className'): k['className'] = clean(k['className'])
    # (ข) ดาวน์โหลดต้องอยู่ขวาสุด
    dl = [i for i, k in enumerate(kids) if isinstance(k, dict) and k.get('el') == 'download-button']
    if dl and dl[0] != len(kids) - 1:
        kids.append(kids.pop(dl[0])); moved += 1

# ยามท้ายไฟล์
for r in rows:
    kids = [k for k in (r.get('card') or []) if isinstance(k, dict)]
    assert r['className'] == ROW, 'className ของแถวไม่ตรงมาตรฐาน'
    assert kids[-1].get('el') == 'download-button', f'ดาวน์โหลดไม่ได้อยู่ขวาสุด: {[k.get("el") for k in kids]}'
    for k in kids:
        cn = k.get('className', '')
        assert '!w-full' in cn and '!min-w-0' in cn, f'{k.get("label")}: ขาด !w-full/!min-w-0'
        assert 'min-w-[132px]' not in cn, f'{k.get("label")}: ยังมี min-w-[132px] (grid ไม่ wrap จะล้นจอแคบ)'
        assert not re.search(r'(?<![\w!-])!(?=\s|$)', cn), f'{k.get("label")}: ยังมี token ! เดี่ยว'

P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'แก้ 2 แถว · ย้ายปุ่มดาวน์โหลดไปขวาสุด {moved} แถว')
for r in rows:
    print('  ', [f"{k.get('el')}:{k.get('label')}" for k in r['card'] if isinstance(k, dict)])
