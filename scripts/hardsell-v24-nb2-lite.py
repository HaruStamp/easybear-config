# hardsell-dev v24: โมเดลรูป 3 ตัว — dropdown imageModel มีแค่ 2.1/Pro → เพิ่ม "🍌 Nano Banana 2 Lite" (เจ้าของสั่ง 26 พ.ย.)
# mnBoard.model = cond(มีข้อความ → Pro · ไม่มี → {values.imageModel}) ⇒ Lite ใช้ได้เฉพาะไม่มีข้อความ เหมือน 2.1 (ไม่แตะ)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F))
LITE = '🍌 Nano Banana 2 Lite'
n = 0
def walk(x):
    global n
    if isinstance(x, dict):
        if x.get('el') == 'dropdown' and x.get('field') == 'imageModel':
            opts = x['options']
            if not any(o.get('value') == LITE for o in opts):
                i = next(i for i, o in enumerate(opts) if o.get('value') == '🍌 Nano Banana 2.1')
                opts.insert(i + 1, {'value': LITE, 'label': LITE, 'icon': 'bolt'})
            n += 1
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
walk(d['phases'])
assert n == 1, n
print('imageModel dropdown แก้แล้ว', n, 'จุด')
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))
