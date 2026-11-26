# hardsell-dev v28: เลือกฉากหลังได้ + ฉากสมจริง สัดส่วนจริง (เจ้าของสั่ง 26 พ.ย. ข้อ E)
#   - ค่าใหม่ svBg (อัตโนมัติ · โกดังสินค้า · ห้างสรรพสินค้า · ตลาดนัดเปิดท้ายขายของ · บ้าน · ร้านค้า)
#     ใช้กับเทมเพลตที่ฉากไม่ตายตัว (tplBgOk = yes: มือ POV · ซูมสินค้า · รีวิว · สาธิต · ก่อน-หลัง · ความรู้สึก · แนะนำ · สินค้าอย่างเดียว · Lifestyle)
#     เทมเพลตที่ฉากตายตัว (ไลฟ์ · โกดัง · โรงงาน · ห้าง · ตลาด · สตูดิโอ · viral · 3D) ไม่โชว์ตัวเลือก และไม่ฉีด
#   - ฉีด: mnPlan (bgTH) · mnBoard (bgTH) · mnVideo (bgEN) — mnVideo2 ไม่ฉีด (เริ่มจากเฟรมท้ายช่วง 1 ฉากติดมาแล้ว · ประหยัดเพดาน 3900)
#   - ทุกฉากมีกฎขนาดจริงเทียบของรอบตัว · ป้ายไม่มีตัวหนังสือที่อ่านได้
#   - แก้ tplScene/tplSceneEN ugc-warehouse/ugc-mall ที่สั่ง "holding the product" → ชิ้นใหญ่ยืนข้าง ไม่ถูกย่อ (แบบ ugc-hand 48ad933/3a17fe6)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F))
L = d['lookups']
ops = {o['id']: o for o in d['ops']}
AUTO = 'อัตโนมัติ'
OK = ['ugc-hand', 'ugc-closeup', 'ugc-review', 'ugc-using', 'ugc-compare', 'ugc-feeling', 'ugc-recommend', 'product-only', 'lifestyle']
L['tplBgOk'] = {k: ('yes' if k in OK else 'no') for k in L['tplScene']}
L['bgTH'] = {
  'โกดังสินค้า': 'โกดังกระจายสินค้าจริง — ชั้นวางเหล็กสูงหลายชั้น (racking) พาเลทไม้ห่อฟิล์มใส พื้นปูนขัดมันมีเส้นเหลือง ไฟเพดานสูงแบบโกดัง ป้ายไม่มีตัวหนังสือ',
  'ห้างสรรพสินค้า': 'ทางเดินในห้างสรรพสินค้าจริง — พื้นหินขัดเงาสะท้อนไฟ ไฟดาวน์ไลท์เพดาน หน้าร้านกระจกและคนเดินเบลออยู่ไกลๆ ป้ายร้านไม่มีตัวหนังสือหรือโลโก้',
  'ตลาดนัดเปิดท้ายขายของ': 'ตลาดนัดเปิดท้ายขายของตอนเย็น — ท้ายรถกระบะหรือ SUV เปิดอยู่ สินค้าวางเรียงบนผ้าปูและโต๊ะพับ ไฟหลอดแขวนสีส้ม รถคันอื่นและคนเดินเบลอด้านหลัง ป้ายไม่มีตัวหนังสือ',
  'บ้าน': 'ในบ้านคนไทยจริง — ห้องที่ตรงกับการใช้สินค้า (ห้องนั่งเล่น ห้องนอน ห้องครัว ห้องน้ำ) ของใช้จริงวางเป็นธรรมชาติ แสงธรรมชาติจากหน้าต่าง',
  'ร้านค้า': 'ร้านค้าปลีกเล็กๆ จริง — ชั้นวางสินค้าเรียบร้อย เคาน์เตอร์ ไฟร้านสว่าง ป้ายและฉลากบนชั้นไม่มีตัวหนังสือที่อ่านได้',
}
L['bgEN'] = {
  'โกดังสินค้า': 'Setting: a real distribution warehouse — tall steel pallet racking, film-wrapped pallets, polished concrete floor with yellow lines, high-bay ceiling lights; signs carry no readable text.',
  'ห้างสรรพสินค้า': 'Setting: a real shopping-mall walkway — glossy stone floor reflecting downlights, blurred glass shopfronts and distant shoppers; no readable signs or logos.',
  'ตลาดนัดเปิดท้ายขายของ': 'Setting: an evening car-boot market — an open pickup or SUV tailgate, goods laid on cloth and folding tables, warm hanging bulbs, blurred cars and shoppers; no readable signs.',
  'บ้าน': 'Setting: a real lived-in Thai home room that fits how the product is used, natural window light.',
  'ร้านค้า': 'Setting: a real small retail shop — tidy stocked shelves, a counter, bright shop lighting; no readable labels or signs.',
}
BG_ON = {'op': 'and', 'list': [
  {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svBg}', 'b': AUTO}},
  {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svBg}', 'b': ''}},
  {'op': 'eq', 'a': {'op': 'lookup', 'table': 'tplBgOk', 'key': '{values.templateId}', 'fallback': 'no'}, 'b': 'yes'}]}
SIZE_TH = ' · สินค้าคงขนาดจริงเทียบกับชั้นวาง โต๊ะ มือ และคนรอบข้าง ห้ามย่อหรือขยาย'
def blk(head, table, tail):
    return {'op': 'block', 'sep': '', 'parts': [{'when': BG_ON, 'value': {'op': 'concat', 'parts': [head, {'op': 'lookup', 'table': table, 'key': '{values.svBg}', 'fallback': ''}, tail]}}]}
d['values'].setdefault('svBg', AUTO)

def ins_after(parts, pred, item):
    s = json.dumps(parts, ensure_ascii=False)
    if '"table": "bg' in s: return 0
    for i, p in enumerate(parts):
        if pred(p): parts.insert(i + 1, item); return 1
        if isinstance(p, dict) and isinstance(p.get('parts'), list) and ins_after(p['parts'], pred, item): return 1
    return 0
LINE = '\n(อารมณ์ของบทและตัวละครทั้งคลิปต้องเป็นไปตามโทนการขายนี้'
n = 0
n += ins_after(ops['mnPlan']['prompt']['parts'], lambda p: isinstance(p, str) and p.startswith(LINE),
               blk('\nฉากหลังที่ผู้ใช้เลือก (ใช้ทุกฉาก แทนสถานที่ในเทมเพลต — สะท้อนใน sNth และ sNen): ', 'bgTH', SIZE_TH))
n += ins_after(ops['mnBoard']['prompt']['parts'], lambda p: isinstance(p, dict) and p.get('table') == 'toneVisual',
               blk('\nฉากหลังที่ผู้ใช้เลือก (ชนะสถานที่ในสไตล์ภาพ): ', 'bgTH', SIZE_TH))
n += ins_after(ops['mnVideo']['prompt']['parts'], lambda p: p == '.',
               blk('\n\n', 'bgEN', ' The product keeps its true real-world size against the surroundings.'))
assert n in (0, 3), n

# tplScene: โกดัง/ห้าง ชิ้นใหญ่ห้ามถูกย่อให้ถือ
TRUE = ' at its true real-world size — a small item held up; a large item (furniture, appliance, big box) stays full size on the floor or display while the reviewer stands beside it and gestures, never shrunk to be held.'
L['tplScene']['ugc-warehouse'] = ('Inside a real distribution warehouse: tall steel pallet racking stacked with many identical units of the product, film-wrapped pallets, concrete floor, high-bay ceiling lights. '
    'The reviewer stands beside the racking presenting one unit' + TRUE + ' No price tags, no readable signs, no closed parcel boxes hiding the product.')
L['tplScene']['ugc-mall'] = ('Inside a bright premium shopping-mall store: clean stocked shelves, glossy floor, bright LED retail lighting. '
    'The reviewer presents the product in the aisle with a delighted expression' + TRUE + ' No store logos or readable signs.')
L['tplSceneEN']['ugc-warehouse'] = 'The reviewer presents the product among the warehouse racking at its true size (a large item stays on the floor, never lifted), gesturing back at the huge stock behind them, energetic "shipped straight from the warehouse" vibe.'
L['tplSceneEN']['ugc-mall'] = 'The reviewer presents the product in the retail aisle — a small item picked from the shelf and shown to camera, a large item shown in place at true size — with delight, premium shopping atmosphere around.'

# UI: ตัวเลือกฉากหลัง (ใต้กล่องเลือกเทมเพลต) — โชว์เฉพาะเทมเพลตที่ฉากไม่ตายตัว
sett = d['phases'][0]['form'][0]['card'][0]['card'][2]['card']
assert any(isinstance(c, dict) and 'templateId' in json.dumps(c) for c in sett[:1])
if not any('"field": "svBg"' in json.dumps(c, ensure_ascii=False) for c in sett):
    sett.insert(1, {'el': 'box', 'className': 'flex flex-col gap-2 mt-2',
      'when': {'op': 'eq', 'a': {'op': 'lookup', 'table': 'tplBgOk', 'key': '{values.templateId}', 'fallback': 'no'}, 'b': 'yes'},
      'card': [
        {'el': 'row', 'className': 'items-center gap-2 mt-1', 'style': {'flexWrap': 'nowrap'}, 'card': [
          {'el': 'icon', 'icon': 'landscape', 'textSize': 'text-[18px]', 'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center'},
          {'el': 'text', 'value': 'ฉากหลัง', 'className': '!text-[17px] @[640px]:!text-[16px] font-black !text-[var(--ev-text)]'}]},
        {'el': 'text', 'value': 'เลือกสถานที่ของคลิป — สินค้าคงขนาดจริงเทียบกับของรอบตัว · อัตโนมัติ = AI เลือกให้เหมาะกับสินค้า', 'className': '!text-[14px] @[640px]:!text-[13px] opacity-60 leading-relaxed mb-1'},
        {'el': 'grid-select', 'field': 'svBg', 'cols': 3, 'mobile': {'cols': 2}, 'contained': True, 'className': '!min-h-[48px] @[420px]:!min-h-0', 'options': [
          {'value': AUTO, 'label': 'อัตโนมัติ', 'desc': 'AI เลือกให้', 'icon': 'auto_fix_high'},
          {'value': 'โกดังสินค้า', 'label': 'โกดังสินค้า', 'desc': 'ชั้นวางเหล็ก พาเลท', 'icon': 'warehouse'},
          {'value': 'ห้างสรรพสินค้า', 'label': 'ห้างฯ', 'desc': 'ทางเดินห้าง ไฟสว่าง', 'icon': 'storefront'},
          {'value': 'ตลาดนัดเปิดท้ายขายของ', 'label': 'ตลาดนัดเปิดท้าย', 'desc': 'เทของจากท้ายรถ', 'icon': 'local_shipping'},
          {'value': 'บ้าน', 'label': 'บ้าน', 'desc': 'ห้องที่ใช้สินค้าจริง', 'icon': 'home'},
          {'value': 'ร้านค้า', 'label': 'ร้านค้า', 'desc': 'ชั้นวาง เคาน์เตอร์', 'icon': 'store'}]}]})
print('v28: inject', n)
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))
