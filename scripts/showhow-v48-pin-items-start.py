#!/usr/bin/env python3
"""showhow v48 — ปัก `!items-start` 3 จุด ให้เลิกแขวนอยู่กับลำดับตัวอักษรของ Tailwind (ไม่เปลี่ยนหน้าตา)

ที่มา: `el:'row'` ของ engine เติม `items-center` ให้ทุกแถว ⇒ ของเราชนะหรือแพ้ตาม **ลำดับ utility ใน stylesheet**
starter วัดจริงบน tool (เดิน `document.styleSheets`) ได้ลำดับ **เรียงตามตัวอักษร ไม่ใช่ตามความหมาย**:
    flex-nowrap@55 · flex-wrap@56 · items-baseline@57 · items-center@58 · items-start@59 · items-stretch@60
    gap-1@63 · gap-1.5@64 · gap-2@65 · gap-2.5@66 · gap-3@67
⇒ `items-start` (59) มาหลัง `items-center` (58) ⇒ **ชนะอยู่แล้ว ทำงานมาตลอด**

🪤 ผมกับทีม minimal **เดาผิดทั้งคู่** ว่ามันตาย เพราะอนุมานลำดับจาก "ความหมาย" (start ควรมาก่อน center)
   ตามลำดับ plugin มาตรฐานของ Tailwind — ซึ่งไม่ใช่ลำดับของบิลด์ที่ Flow ฉีด
   📌 **ห้ามอนุมานลำดับ CSS จากเหตุผลเชิงความหมาย — ต้องวัดจาก stylesheet จริง**

ทำไมยังต้องปัก `!` ทั้งที่ชนะอยู่แล้ว: เลขชุดนี้ **n=1 วัดครั้งเดียว ไม่รู้รุ่น Tailwind** ⇒ ถ้า Flow เปลี่ยน host
เมื่อไหร่ ลำดับอาจกลับด้านแล้ว **ไอคอนเลื่อนไปกลางกล่องแบบเงียบ ๆ** · ใส่ `!` = ผลลัพธ์เท่าเดิมวันนี้ + ไม่ผูกกับโชค
🔴 **ไม่แตะ `gap-1.5` 32 จุด** — ตัวนั้นแพ้จริง (64 < 65) ⇒ ใส่ `!` = **เปลี่ยนระยะห่างที่พี่หมีอนุมัติไปแล้ว** ต้องให้เขาเคาะก่อน
"""
import json, pathlib

P = pathlib.Path(__file__).resolve().parent.parent / 'showhow-dev.json'
d = json.loads(P.read_text(encoding='utf-8'))
n = 0
def walk(x):
    global n
    if isinstance(x, dict):
        if x.get('el') == 'row':
            cn = str(x.get('className') or '')
            if 'items-start' in cn and '!items-start' not in cn:
                x['className'] = cn.replace('items-start', '!items-start', 1); n += 1
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
walk(d.get('phases'))
assert n == 3, f'ปักได้ {n} จุด (คาด 3) — โครงเปลี่ยน หยุดก่อน'

s = json.dumps(d, ensure_ascii=False)
import re
assert not re.search(r'"[^"]*(?<![!\w-])items-start(?![\w-])[^"]*"', s.replace('!items-start', '!X')), 'ยังเหลือ items-start ที่ไม่ได้ปัก'
P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'ปัก !items-start {n} จุด · หน้าตาเท่าเดิมทุกพิกเซล (ชนะอยู่แล้วตามลำดับที่วัดได้)')
