# showhow-public r27-v146 = dev v146 (สตอรีบอร์ด 6/8 ช่อง · คลิป 10 วิ) แบบตัวขาย — ตัวขายไม่มีการ์ด "ความละเอียด" (svRes/360p)
#   ⇒ รันสคริปต์ dev v146 ตัวเดิม แต่หัวการ์ด/คลาสของการ์ดใหม่ลอกจากการ์ด "โมเดลภาพ" (prod['card'][2] ของตัวขาย · โครงเดียวกัน หัว+grid-select+คำใบ้) แทนการ์ดความละเอียด
#   ส่วนอื่น (ตาราง 10p6/10p8 · บอร์ด/วิดีโอ/บท · ยามความยาว · กล่องแก้บทฉาก 6-8) เหมือน dev
# ใช้: python3 scripts/showhow-public-r27-v146-panels.py showhow-public.json
import os, sys
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'showhow-v146-board-panels.py')).read()
a = "head = copy.deepcopy(res['card'][0]); assert head['card'][1]['value'] == 'ความละเอียด'"
b = "head = copy.deepcopy(res['card'][0]); assert res['card'][1]['field'] == 'imageModel' and head['card'][0]['el'] == 'icon' and head['card'][1]['el'] == 'text'   # ตัวขาย: ลอกหัวการ์ดโมเดลภาพ"
assert src.count(a) == 1
src = src.replace(a, b)
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else 'showhow-public.json']
exec(compile(src, 'showhow-v146-board-panels.py(public)', 'exec'))
