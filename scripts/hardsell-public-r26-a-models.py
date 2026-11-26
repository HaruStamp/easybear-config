# hardsell-public r26-a (ฐานก่อนยก dev v24): โมเดลรูป 3 ตัว + ค่าเริ่มวิดีโอ Veo 3.1 - Lite (26 พ.ย. 2569 · อัปเดตใหญ่)
#   ตัวขายเดิม (v22.4) dropdown รูป = Pro · "Nano Banana 2" · "Imagen 4" — ชื่อเก่า ไม่ใช่ชุดที่เทสสดผ่าน 26 พ.ย.
#   ⇒ ตั้งเป็น Pro (ค่าเริ่มเดิม ไม่เปลี่ยน) · 2.1 แล้วให้ dev v24 เติม 2 Lite ต่อท้าย 2.1
#   + mnBoard.model: มีข้อความบนภาพ = Pro อัตโนมัติ (ของ dev v22.8 · v24 พึ่งข้อนี้ — Lite/2.1 เขียนไทยไม่ได้) + ข้อความบอกใต้ dropdown
#   + videoModel ค่าเริ่ม Veo 3.1 - Fast → Veo 3.1 - Lite (BOARD: hardsell/flow ค่าเริ่ม Lite ก่อน 5 ธ.ค.) · ตัวเลือกวิดีโอไม่แตะ (Omni ยัง 1.1 · 1.2 ห้ามเป็นค่าเริ่ม)
#   ⚠️ ไม่ยก svRes/360p/Omni 1.2 ของ dev v22.5-v22.8 (ยังไม่สั่งขึ้นตัวขาย)
# ใช้: python3 scripts/hardsell-public-r26-a-models.py hardsell-public.json   (รันซ้ำได้ ไบต์เท่าเดิม)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-public.json'
d = json.load(open(F))
PRO, NB21 = '🍌 Nano Banana Pro', '🍌 Nano Banana 2.1'
TEXT_ON = {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svTextOn}', 'b': 'ไม่มีข้อความ'}}
HINT = {'el': 'text', 'value': 'มีข้อความบนภาพ ระบบใช้ Nano Banana Pro ให้อัตโนมัติ เพราะเขียนตัวไทยได้',
        'className': '!text-[13px] @[640px]:!text-[12.5px] opacity-55 px-0.5 leading-snug', 'when': TEXT_ON}
n = 0
def walk(x):
    global n
    if isinstance(x, dict):
        for k in ('card',):
            cs = x.get(k)
            if isinstance(cs, list):
                for i, c in enumerate(cs):
                    if isinstance(c, dict) and c.get('el') == 'dropdown' and c.get('field') == 'imageModel':
                        keep = [o for o in c['options'] if o['value'] in (PRO, NB21, '🍌 Nano Banana 2 Lite')]
                        if not any(o['value'] == NB21 for o in keep):
                            keep.insert(1, {'value': NB21, 'label': NB21, 'icon': 'image'})
                        c['options'] = keep
                        if not (i + 1 < len(cs) and cs[i + 1] == HINT): cs.insert(i + 1, HINT)
                        n += 1
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
walk(d['phases'])
assert n == 1, n
b = next(o for o in d['ops'] if o['id'] == 'mnBoard')
assert b['model'] in ('{values.imageModel}', {'op': 'cond', 'when': TEXT_ON, 'then': PRO, 'else': '{values.imageModel}'}), b['model']
b['model'] = {'op': 'cond', 'when': TEXT_ON, 'then': PRO, 'else': '{values.imageModel}'}
assert d['values']['imageModel'] == PRO   # ค่าเริ่มรูปคงเดิม
assert d['values']['videoModel'] in ('Veo 3.1 - Fast', 'Veo 3.1 - Lite')
d['values']['videoModel'] = 'Veo 3.1 - Lite'
print('r26-a: imageModel dropdown', n, '· mnBoard Pro เมื่อมีข้อความ · videoModel ค่าเริ่ม', d['values']['videoModel'])
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))
