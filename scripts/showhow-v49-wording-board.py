#!/usr/bin/env python3
"""showhow v49 — ถ้อยคำ "ภาพ → บอร์ด" กอง A-1 (พี่หมีเคาะ "ภาพ→บอร์ด หมดแล้ว" · ทีม minimal ส่งต่อ)

⭐ **คำศัพท์กลาง 3 ทีม — ห้ามเปลี่ยนสำนวน**: `ต้อง Gen ภาพก่อน` → `ต้อง Gen บอร์ดก่อน`
   (showhow 4 · hardsell 4 · minimal 4 จุด · minimal ใช้ไปแล้ว ⇒ เปลี่ยนสำนวน = ได้ 3 แอปที่พูดเกือบเหมือนกัน
    ซึ่งแย่กว่าตอนที่ทุกแอปพูดผิดเหมือนกัน)

ท่าที่ใช้ (ตามที่ minimal แนะ · ของเราเสี่ยงกว่าเขามากเพราะกอง B/C มี 86 จุด):
  ① **exact match ทั้งสตริง ห้าม find-replace** — 'Gen ภาพ' เป็นสตริงย่อยของอีก 3 ข้อความ
  ② assert จำนวนก่อนแก้ทุกข้อความ ⇒ ถ้า config ขยับไปจากตอนยื่นใบเคาะ สคริปต์หยุด ไม่ใช่แก้ไปเรื่อย ๆ
  ③ 🛡 **นับกอง B/C ก่อน-หลัง ต้องเท่ากันเป๊ะ** — ยามที่สำคัญที่สุดของงานนี้
     (B = รูปที่ผู้ใช้อัปเอง · C = ภาพในคลิป/เฟรม/บท — ทั้งสองกองห้ามแตะ)

🪤 `ภาพยังไม่ถูกใจ?` / `ภาพโอเคแล้ว?` ผมเคยใส่กอง D (ไม่แน่ใจ) · hardsell ใส่ A-1 · พี่หมีตอบ "หมดแล้ว"
   ⇒ เปลี่ยนตามที่เคาะ · ถ้าเห็นบนจอจริงแล้วไม่ชอบค่อยถอย (ถอยทีหลังถูกกว่าค้างไว้แล้ว 2 แอปพูดคนละคำ)
🪤 **A-2 4 ข้อความไม่อยู่ในสคริปต์นี้** — รับปากพี่หมีผ่าน minimal ว่าจะร่างประโยคใหม่ให้ดูก่อน ไม่เขียนเองเงียบ ๆ
"""
import json, pathlib

P = pathlib.Path(__file__).resolve().parent.parent / 'showhow-dev.json'
raw = P.read_text(encoding='utf-8')
d = json.loads(raw)

A1 = {   # ข้อความเดิม → ข้อความใหม่ : จำนวนจุดที่คาด
    'แทนภาพของช่วงนี้ด้วยไฟล์ที่เลือก': ('แทนบอร์ดของช่วงนี้ด้วยไฟล์ที่เลือก', 48),
    'บทภาพ (คำสั่งวาด)': ('บทบอร์ด (คำสั่งวาด)', 30),
    'ต้อง Gen ภาพก่อน': ('ต้อง Gen บอร์ดก่อน', 4),          # ⭐ คำศัพท์กลาง
    'Gen ภาพ': ('Gen บอร์ด', 3),
    'วาดภาพไม่สำเร็จ': ('วาดบอร์ดไม่สำเร็จ', 2),
    'รอวาดภาพ': ('รอวาดบอร์ด', 2),
    'ได้ภาพแล้ว — รอวิดีโอ': ('ได้บอร์ดแล้ว — รอวิดีโอ', 2),
    'แก้ภาพของคลิปนี้': ('แก้บอร์ดของคลิปนี้', 2),
    'Gen ภาพทั้งหมด · เหลือ ': ('Gen บอร์ดทั้งหมด · เหลือ ', 1),
    'รอภาพก่อน': ('รอบอร์ดก่อน', 1),
    'ยังไม่มีภาพ': ('ยังไม่มีบอร์ด', 1),
    'วาดภาพไม่สำเร็จ — กดลองใหม่': ('วาดบอร์ดไม่สำเร็จ — กดลองใหม่', 1),
    'เขียนบท → ตรวจ → สร้างภาพ → วิดีโอ': ('เขียนบท → ตรวจ → สร้างบอร์ด → วิดีโอ', 1),
    'ภาพยังไม่ถูกใจ?': ('บอร์ดยังไม่ถูกใจ?', 1),            # เดิมกอง D · พี่หมีเคาะว่าเข้าข่าย A
    'ภาพโอเคแล้ว?': ('บอร์ดโอเคแล้ว?', 1),
}
KEEP = {   # กอง B (รูปที่ผู้ใช้อัป) + กอง C (ภาพในคลิป/บท) — ห้ามขยับแม้แต่จุดเดียว
    'เลือกภาพ': 13, 'บรรยายภาพฉากนี้เป็นภาษาไทย': 30, 'ข้อความบนภาพ': 30,
    'ภาพกว้างเห็นทั้งพื้นที่': 10, 'ไม่สำเร็จ ภาพที่ ': 2, 'ตอนนี้สภาพเป็นยังไง (ไม่บังคับ)': 1,
}

def count_exact(node, target):
    n = 0
    if isinstance(node, dict):
        for v in node.values(): n += count_exact(v, target)
    elif isinstance(node, list):
        for v in node: n += count_exact(v, target)
    elif isinstance(node, str) and node == target: n = 1
    return n

def replace_exact(node, old, new):
    if isinstance(node, dict):
        return {k: (new if (isinstance(v, str) and v == old) else replace_exact(v, old, new)) for k, v in node.items()}
    if isinstance(node, list):
        return [(new if (isinstance(v, str) and v == old) else replace_exact(v, old, new)) for v in node]
    return node

before_keep = {k: count_exact(d['phases'], k) for k in KEEP}
for k, want in KEEP.items():
    assert before_keep[k] == want, f'กอง B/C "{k}" มี {before_keep[k]} จุด (คาด {want}) — config ขยับไปแล้ว หยุด'

total = 0
for old, (new, want) in A1.items():
    got = count_exact(d['phases'], old)
    assert got == want, f'"{old}" มี {got} จุด (คาด {want}) — config ขยับไปจากตอนยื่นใบเคาะ หยุด'
    d['phases'] = replace_exact(d['phases'], old, new)
    assert count_exact(d['phases'], old) == 0, f'"{old}" ยังเหลืออยู่'
    assert count_exact(d['phases'], new) == want, f'"{new}" ได้ไม่ครบ {want}'
    total += want

# 🛡 ยามที่สำคัญที่สุด: กอง B/C ต้องไม่ขยับแม้แต่จุดเดียว
after_keep = {k: count_exact(d['phases'], k) for k in KEEP}
assert after_keep == before_keep, f'กอง B/C ขยับ! ก่อน {before_keep} → หลัง {after_keep}'

P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'เปลี่ยน {len(A1)} ข้อความ · {total} จุด · กอง B/C คงที่ทุกตัว {after_keep}')
