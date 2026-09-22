#!/usr/bin/env python3
"""showhow v50 — ถ้อยคำกอง A-2 ข้อ 2/3/4 (อยู่ในขอบเขตที่พี่หมีเคาะ "ภาพ→บอร์ด หมดแล้ว")

พี่หมียืนยันเฉพาะเจาะจงว่า **showhow ต้องใช้ "บอร์ด" เพราะใช้ระบบ storyboard** (hardsell กลับไปใช้ "ภาพ")
⇒ คำศัพท์กลางเหลือ **minimal + showhow**

🔑 กฎแยกกองที่คมขึ้นจากรอบนี้ (ทีม hardsell คิดได้ตอนแก้ข้อเสนอตัวเอง · minimal ส่งต่อ):
   *"คำถามที่ถูกไม่ใช่ **ประโยคนี้พูดถึงของ 2 อย่างไหม** แต่คือ **ของ 2 อย่างนั้นใช้คำเดียวกันหรือเปล่า**"*
   ⇒ ข้อ 4 ("รูปนี้" = รูปที่ผู้ใช้อัป · "วาดภาพ" = วาดบอร์ด) ปนกันจริง **แต่ใช้คนละคำอยู่แล้ว** ⇒ เปลี่ยนคำล้วน ปลอดภัย
🔺 **ข้อ 1 ไม่อยู่ในสคริปต์นี้** — `ใต้ภาพ` → `ด้านล่าง` เป็น **คำใหม่ที่ไม่ได้อยู่ในคำสั่ง "เปลี่ยนภาพเป็นบอร์ด"**
   ⇒ ออกนอกขอบเขตที่เคาะ · minimal ยื่นถามพี่หมีเป็นคำถามบรรทัดเดียวให้แล้ว
"""
import json, pathlib

P = pathlib.Path(__file__).resolve().parent.parent / 'showhow-dev.json'
d = json.loads(P.read_text(encoding='utf-8'))

A2 = {
    'ยังไม่มีภาพ — ต้อง Gen ภาพก่อน ถึงจะ Gen วิดีโอได้':
        ('ยังไม่มีบอร์ด — ต้อง Gen บอร์ดก่อน ถึงจะ Gen วิดีโอได้', 1),   # "ภาพ" 2 ตัว บอร์ดทั้งคู่ · ครึ่งหลัง = คำศัพท์กลาง
    'บ้านจริงมีสีของมันเอง — คุมได้แค่แสง · มีผลทั้งภาพบอร์ดและวิดีโอจริง':
        ('บ้านจริงมีสีของมันเอง — คุมได้แค่แสง · มีผลทั้งบอร์ดและวิดีโอจริง', 1),   # "ภาพบอร์ด" ซ้ำซ้อน ⇒ ตัด "ภาพ"
    'ระบบแนบรูปนี้ให้ตอนวาดภาพและทำวิดีโอ เป็นคนเดิมทุกช็อต ทุกคลิป ทุกรอบผลิต':
        ('ระบบแนบรูปนี้ให้ตอนวาดบอร์ดและทำวิดีโอ เป็นคนเดิมทุกช็อต ทุกคลิป ทุกรอบผลิต', 1),   # "รูปนี้" คงไว้ (กอง B)
}
KEEP = {'เลือกภาพ': 13, 'บรรยายภาพฉากนี้เป็นภาษาไทย': 30, 'ข้อความบนภาพ': 30,
        'ภาพกว้างเห็นทั้งพื้นที่': 10, 'ไม่สำเร็จ ภาพที่ ': 2, 'ตอนนี้สภาพเป็นยังไง (ไม่บังคับ)': 1}
HOLD = 'ภาพโอเคแล้ว? สลับแท็บ “วิดีโอ” ใต้ภาพ เพื่อสั่งวิดีโอ'   # ข้อ 1 · ต้องยังอยู่ครบหลังรอบนี้

def count(node, t):
    if isinstance(node, dict): return sum(count(v, t) for v in node.values())
    if isinstance(node, list): return sum(count(v, t) for v in node)
    return 1 if isinstance(node, str) and node == t else 0

def repl(node, old, new):
    if isinstance(node, dict):
        return {k: (new if (isinstance(v, str) and v == old) else repl(v, old, new)) for k, v in node.items()}
    if isinstance(node, list):
        return [(new if (isinstance(v, str) and v == old) else repl(v, old, new)) for v in node]
    return node

before = {k: count(d['phases'], k) for k in KEEP}
for k, want in KEEP.items():
    assert before[k] == want, f'กอง B/C "{k}" = {before[k]} (คาด {want}) — config ขยับ หยุด'
assert count(d['phases'], HOLD) == 1, 'ข้อ 1 ที่ต้องพักไว้ หายไปแล้ว?'

n = 0
for old, (new, want) in A2.items():
    got = count(d['phases'], old)
    assert got == want, f'"{old[:34]}…" = {got} จุด (คาด {want}) — หยุด'
    d['phases'] = repl(d['phases'], old, new)
    assert count(d['phases'], old) == 0 and count(d['phases'], new) == want
    n += want

assert {k: count(d['phases'], k) for k in KEEP} == before, 'กอง B/C ขยับ!'
assert count(d['phases'], HOLD) == 1, 'ข้อ 1 โดนแตะโดยไม่ตั้งใจ'
P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'A-2 ข้อ 2/3/4 · {n} จุด · กอง B/C คงที่ · ข้อ 1 ยังอยู่ครบ (รอพี่หมีเคาะ)')
