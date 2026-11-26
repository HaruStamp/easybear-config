# hardsell-dev v23: สไตล์ 3D (สัตว์/คน/ผลไม้/ของ/รถ/อวัยวะ) บทออกมาเศร้า/เบื่อทั้งคลิป ไม่ว่าเลือกโทนขายดุหรือตลก
# ต้นเหตุ: tplScene d3-* สั่งตัวการ์ตูน "sad/troubled/wilted/tired" เป็นภาพหลัก → ส่งเข้า mnPlan + mnBoard ก่อนโทน → ชนะโทน
# แก้: ตัวการ์ตูนมีพลังตามโทนที่เลือก · ปัญหาโผล่แวบเดียวแบบตลก · mnPlan เพิ่ม 1 บรรทัด "อารมณ์ตามโทนตลอดคลิป"
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F))
L = d['lookups']
BASE = 'Pixar-style 3D animated cartoon, vibrant colors, soft cinematic lighting: '
TAIL = ' The real product appears prominently and must stay photorealistic exactly as the reference.'
MOOD = ' Overall mood is upbeat and energetic, matching the chosen sales tone — the problem is shown only as a quick comic beat, never as sadness or boredom.'
scene = {
  'd3-person': BASE + 'a cute 3D cartoon Thai person, bright and expressive, excitedly presenting the real product with a playful exaggerated reaction.' + MOOD + TAIL,
  'd3-animal': BASE + 'an adorable 3D cartoon animal, lively and expressive, excitedly showing off the real product with bouncy cartoon energy.' + MOOD + TAIL,
  'd3-fruit':  BASE + 'a cute 3D cartoon fruit or vegetable character, fresh and cheerful, proudly showing the real product with squashy cartoon energy.' + MOOD + TAIL,
  'd3-object': BASE + 'a cute 3D cartoon everyday object character, lively and expressive, eagerly presenting the real product.' + MOOD + TAIL,
  'd3-car':    'Pixar Cars-style 3D animated cartoon, vibrant colors, soft cinematic lighting: a cute 3D cartoon car with expressive eyes, revved up and excited, showing off the real product.' + MOOD + TAIL,
  'd3-organ':  BASE + "a cute 3D cartoon body-organ character (matching the product's benefit), energetic and cheerful, presenting the real product." + MOOD + TAIL,
}
sceneEN = {
  'd3-person': 'The cute 3D cartoon person does a quick comic reaction to the problem, then lights up with joy as the product saves the day — bouncy cartoon motion, expressive face, energy matching the sales tone throughout.',
  'd3-animal': 'The adorable 3D cartoon animal does a quick comic reaction to the problem, then bounces with happiness as the product fixes everything — playful cartoon motion, energy matching the sales tone throughout.',
  'd3-fruit':  'The cartoon fruit/vegetable character does a quick comic droop, then plumps up fresh and glowing thanks to the product — squashy bouncy cartoon motion, energy matching the sales tone throughout.',
  'd3-object': 'The cartoon object character does a quick comic reaction to the problem, then gets revived sparkling-new thanks to the product — charming lively cartoon motion, energy matching the sales tone throughout.',
  'd3-car':    'The cartoon car does a quick comic sputter, then revs up shiny and happy thanks to the product — fun automotive cartoon motion, energy matching the sales tone throughout.',
  'd3-organ':  'The cute organ character does a quick comic wobble, then glows healthy and energetic thanks to the product — uplifting cartoon motion, energy matching the sales tone throughout.',
}
TAIL_EN = ' The real product stays photorealistic exactly as the reference.'
for k in scene:
    assert k in L['tplScene'] and k in L['tplSceneEN'], k
    L['tplScene'][k] = scene[k]
    L['tplSceneEN'][k] = sceneEN[k] + TAIL_EN
# mnPlan: บรรทัดโทน → อารมณ์ตามโทนตลอดคลิป
LINE = '\n(อารมณ์ของบทและตัวละครทั้งคลิปต้องเป็นไปตามโทนการขายนี้ ห้ามเศร้า เบื่อ หมดแรงเป็นอารมณ์หลัก · ปัญหาเล่าสั้นแวบเดียวแล้วเข้าทางแก้)'
n = 0
for o in d['ops']:
    if o.get('id') != 'mnPlan': continue
    def fix(parts):
        global n
        for i, p in enumerate(parts):
            if isinstance(p, dict) and p.get('op') == 'lookup' and p.get('table') == 'toneSpeech' and i + 1 < len(parts) and parts[i+1] == '':
                if LINE not in json.dumps(parts, ensure_ascii=False):
                    parts[i+1] = LINE; n += 1
            if isinstance(p, dict):
                for v in p.values():
                    if isinstance(v, list): fix(v)
    def walk(x):
        if isinstance(x, dict):
            for v in x.values(): walk(v)
            if isinstance(x.get('parts'), list): fix(x['parts'])
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(o)
print('mnPlan tone line inserted:', n)
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))
