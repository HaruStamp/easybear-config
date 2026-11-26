# showhow-public r27-v143 = dev v143 (สัตว์เลี้ยง 1-3 ตัว) แบบตัวขาย — ผังหน้าจอตัวขายไม่เท่า dev ⇒ index ตายตัว box['card'][20] ใช้ไม่ได้
#   ⇒ รันสคริปต์ dev v143 ตัวเดิม (ต้นฉบับเดียว) แต่หา "repeat ช่องรูปใบหน้า" ด้วยการค้น (repeat characters ที่มี slot face) แทน index
#   ส่วนอื่น (ref/prompt/การ์ดหน้าตั้งค่าใต้การ์ดเสียง) เหมือน dev
# ใช้: python3 scripts/showhow-public-r27-v143-pets.py showhow-public.json
import os, sys
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'showhow-v143-pets-multi.py')).read()
a = """box = c['phases'][0]['form'][2]['card'][0]['card'][0]['card'][4]['card'][2]
face_box = box['card'][20]
assert face_box['card'][0]['card'][2]['el'] == 'repeat'
slot_tpl = face_box['card'][0]['card'][2]['card'][0]['card'][0]   # กล่อง 1 ช่องรูป (มีรูป/ปุ่มอัป)"""
b = """_reps = []
def _find(n):
    if isinstance(n, dict):
        if n.get('el') == 'repeat' and n.get('coll') == 'characters' and '"to": "face"' in json.dumps(n, ensure_ascii=False): _reps.append(n)
        for v in n.values(): _find(v)
    elif isinstance(n, list):
        for v in n: _find(v)
_find(c['phases'])
assert _reps, 'ไม่เจอ repeat ช่องรูปใบหน้า'
slot_tpl = _reps[0]['card'][0]['card'][0]   # กล่อง 1 ช่องรูป (มีรูป/ปุ่มอัป) · ตัวขาย: ค้นแทน index"""
assert src.count(a) == 1
src = src.replace(a, b)
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else 'showhow-public.json']
exec(compile(src, 'showhow-v143-pets-multi.py(public)', 'exec'))
