# hardsell-public r26-b = dev v25 (คลิป 10 วิ เฉพาะ Omni) แบบตัวขาย — ตัวขายไม่มี svRes/360p (dev v22.5)
#   ⇒ รันสคริปต์ dev v25 ตัวเดิม (ต้นฉบับเดียว) แต่ผ่อน assert ส่วน 360p: เงื่อนไข eq 8 ใน mnVideo = 0 · UI ความละเอียด = 0
#   ส่วนอื่น (lookups คีย์ 10 · durationSeconds · vo5 · validate · ปุ่ม 8/10/16 · ปิด Veo ตอน 10 วิ) เหมือน dev ทุกไบต์
# ใช้: python3 scripts/hardsell-public-r26-b-omni-10s.py hardsell-public.json   (ห้ามรันซ้ำ — dev v25 เองก็รันครั้งเดียว)
import os, sys
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hardsell-v25-omni-10s.py')).read()
for a, b in [("assert n360 == 8, n360", "assert n360 == 0, n360   # ตัวขายไม่มี 360p"),
             ("assert done == {'sec': 1, 'vm': 1, 'res': 4, 'scene': 4}, done", "assert done == {'sec': 1, 'vm': 1, 'res': 0, 'scene': 4}, done   # ตัวขายไม่มี svRes")]:
    assert src.count(a) == 1, a
    src = src.replace(a, b)
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else 'hardsell-public.json']
exec(compile(src, 'hardsell-v25-omni-10s.py(public)', 'exec'))
