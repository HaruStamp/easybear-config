# hardsell-public r27-v31 = dev v31 (คลิป 20 วิ Omni · trimTailIfNext) แบบตัวขาย — ตัวขายไม่มี svRes/360p
#   ⇒ รันสคริปต์ dev v31 ตัวเดิม (ต้นฉบับเดียว) แต่ผ่อน assert ส่วน 360p: UI ความละเอียด res = 0 (ข้อความเตือน 360p + การ์ด svRes ไม่มีในตัวขาย)
#   ต้องใช้ engine ≥ v1.25 (trimTailIfNext) — ตัวขาย v2.8.0 889a6b53 = engine 1.25.0 แล้ว
# ใช้: python3 scripts/hardsell-public-r27-v31-omni-20s.py hardsell-public.json   (รันบน r26 · ครั้งเดียว)
import os, sys
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hardsell-v31-omni-20s.py')).read()
a = "assert done['sec'] == 1 and done['vm'] == 1 and done['warn'] == 2 and done['res'] == 2 and done['time'] in (0, 8), done"
b = "assert done['sec'] == 1 and done['vm'] == 1 and done['warn'] == 2 and done['res'] == 0 and done['time'] in (0, 8), done   # ตัวขายไม่มี svRes/360p"
assert src.count(a) == 1, a
src = src.replace(a, b)
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else 'hardsell-public.json']
exec(compile(src, 'hardsell-v31-omni-20s.py(public)', 'exec'))
