# hardsell-dev v30: สไตล์ใหม่ "เห็นแค่ปาก ทาลิปสติก" (ugc-lips) เน้นล็อกสีลิป (เจ้าของสั่ง 26 พ.ย. ข้อ G)
#   - ครบทุก lookup ที่เทมเพลตอื่นมี: tplName/tplScene/tplSceneEN/tplKind/tplChar/tplCharMode/tplVidLead/tplImgLead/tplImgClose/
#     charPlanT/charBoardT/charVideoENT (2 แหล่งตัวละคร) + tplBgOk (no — ฉากตายตัวเป็นโคลสอัป)
#   - ไม่มีคนเต็มตัว (tplChar no = ไม่ใช้รูปหน้า ไม่มีบรรทัด Cast) · เสียงพากย์เป็นเสียงบรรยาย ไม่ลิปซิงก์
#   - ภาพ: โคลสอัปริมฝีปาก ทาลิปจากแท่ง · COLOUR LOCK สีบนปาก = สีเนื้อลิปในรูปสินค้าเป๊ะ (เฉด ความเข้ม อันเดอร์โทน ผิวสัมผัส)
#   - ตัวเลือกใน grid-select templateId (หมวด UGC)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F))
L = d['lookups']
K = 'ugc-lips'
AIS = 'AI เลือกนาย/นางแบบให้เหมาะกับสินค้า'; FACE = 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'
L['tplName'][K] = 'ปากทาลิป'
L['tplScene'][K] = ('Extreme close-up beauty macro of a woman\'s lips only — no eyes, no full face; just the lips, a little chin and the lipstick bullet in hand. '
    'The lipstick from the reference is applied straight from the bullet in one smooth stroke. '
    'COLOUR LOCK: the shade on the lips must match the lipstick bullet colour in the product photo exactly — same hue, depth, undertone and finish (matte, satin or gloss); never shift it pinker, redder, lighter or darker. '
    'Real lip texture with fine natural lines, soft even beauty light, clean neutral background.')
L['tplSceneEN'][K] = ('Macro beauty shot of the lips only: the hand glides the lipstick bullet across the lips in one smooth stroke, the lips press together and part to show even full colour, then a soft smile with the lipstick held beside the lips. '
    'COLOUR LOCK: the colour on the lips matches the lipstick bullet in the first frame exactly — same hue, depth, undertone and finish — and never shifts under any light. '
    'An unseen narrator speaks; voice-over only, the lips do not lip-sync.')
L['tplKind'][K] = 'hands'
L['tplChar'][K] = 'no'
L['tplBgOk'][K] = 'no'
L['tplCharMode'][K] = 'ไม่มีคนเต็มตัวในคลิป — เห็นแค่ริมฝีปากและมือที่ทาลิปสติก (โคลสอัปปาก)'
L['tplVidLead'][K] = L['tplVidLead']['ugc-hand']
L['tplImgLead'][K] = ('A real photograph captured with a macro lens on a camera — not a 3D render, illustration or digital art. '
    'Real lip texture with fine natural lines, healthy smooth skin around the mouth, no blemishes; no beauty filter, airbrushing or waxy plastic look.')
L['tplImgClose'][K] = 'Shot on a modern phone camera, sharp and well exposed, macro beauty detail'
plan = ('กฎภาพ: ทุกฉากเห็นแค่ริมฝีปาก (และมือที่ถือแท่งลิป) ห้ามเห็นตาหรือทั้งหน้า — เขียน sNth/sNen เป็นโคลสอัปปาก: หมุนแท่งลิปให้เห็นเนื้อสี → ทาจากแท่งลงปาก → เม้มปากเกลี่ยสี → โชว์สีบนปากเต็มๆ → ยิ้มพร้อมแท่งลิปข้างปาก'
    ' · สีบนปากต้องตรงกับสีเนื้อลิปในรูปสินค้าเป๊ะ ห้ามบรรยายเป็นสีอื่น · เสียงพากย์เป็นเสียงบรรยาย ไม่ใช่ปากในภาพพูด')
board = 'เห็นแค่ริมฝีปากโคลสอัปและมือที่ถือแท่งลิปสติก ห้ามเห็นตาหรือทั้งใบหน้า · สีบนปาก = สีเนื้อลิปในรูปสินค้าเป๊ะ (เฉด ความเข้ม อันเดอร์โทน ความเงา/แมตต์)'
video = 'Only the lips and the hand holding the lipstick are visible — never the eyes or full face; the lip colour stays exactly the lipstick colour from the first frame.'
for src in (AIS, FACE):
    L['charPlanT'][K + '|' + src] = plan
    L['charBoardT'][K + '|' + src] = board
    L['charVideoENT'][K + '|' + src] = video
# ครบทุกตารางที่ ugc-hand มี
for t, v in L.items():
    if isinstance(v, dict) and 'ugc-hand' in v: assert K in v, t
    if isinstance(v, dict) and any(str(k).startswith('ugc-hand|') for k in v): assert all(K + '|' + s in v for s in (AIS, FACE)), t
# UI
n = 0
def walk(x):
    global n
    if isinstance(x, dict):
        if x.get('el') == 'grid-select' and x.get('field') == 'templateId' and x.get('when') == 'values.styleCat=ugc':
            if not any(o['value'] == K for o in x['options']):
                i = next(i for i, o in enumerate(x['options']) if o['value'] == 'ugc-closeup')
                x['options'].insert(i + 1, {'value': K, 'label': 'ปากทาลิป', 'desc': 'โคลสอัปปาก ล็อกสีลิป', 'icon': 'face_retouching_natural'})
            n += 1
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
walk(d['phases'])
assert n == 1, n
print('v30: ugc-lips ok')
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))
