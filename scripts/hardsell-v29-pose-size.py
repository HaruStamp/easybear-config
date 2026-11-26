# hardsell-dev v29: นางแบบไม่ต้องถือสินค้า ยืนข้าง/ชี้นำเสนอได้ + โหมดสินค้าขนาดใหญ่ + ช่องขนาดสินค้า (เจ้าของสั่ง 26 พ.ย. ข้อ F)
#   - ค่าใหม่ svPose: อัตโนมัติ (ตามขนาด) · ถือสินค้า · ยืนข้างสินค้า (ชี้/ผายมือนำเสนอ) · สินค้าใหญ่ (ยืนข้าง + กล้องถอยเห็นทั้งชิ้น)
#     ใช้เฉพาะเทมเพลตที่มีคน (tplChar = yes) · ฉีด mnPlan/mnBoard (poseTH) · mnVideo/mnVideo2 (poseEN — ช่วง 2 ต้องมีด้วย
#     เพราะ tplSceneEN หลายตัวสั่ง holding ⇒ ไม่ย้ำ = ช่วง 2 หยิบสินค้าขึ้นมาถือ)
#   - กฎบท mnPlan "ท่าฉากปิดการขาย: พรีเซนเตอร์ถือสินค้าไว้ข้างหน้า" → lookup poseClose ตาม svPose
#   - ช่องขนาดสินค้า sizeInfo ที่สินค้า (แบบ fashion) → mnPlan · mnQueue ส่งต่อ task → mnBoard/mnVideo (ตัด ≤80/60 ตัว)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F))
L = d['lookups']
ops = {o['id']: o for o in d['ops']}
AUTO = 'อัตโนมัติ'
L['poseTH'] = {
  'ถือสินค้า': 'ท่าพรีเซนเตอร์ (ผู้ใช้เลือก): ถือสินค้าในมือทุกฉาก ยกใกล้กล้องให้เห็นชัด',
  'ยืนข้างสินค้า': 'ท่าพรีเซนเตอร์ (ผู้ใช้เลือก): ไม่ถือสินค้า — สินค้าวางบนโต๊ะ ชั้น หรือพื้นข้างตัว พรีเซนเตอร์ยืนข้าง ผายมือหรือชี้นำเสนอ แตะได้แต่ไม่ยก',
  'สินค้าใหญ่': 'โหมดสินค้าขนาดใหญ่ (ผู้ใช้เลือก): สินค้าคงขนาดจริงวางกับพื้น พรีเซนเตอร์ยืนข้าง ผายมือหรือชี้นำเสนอ ห้ามถือหรือยก · กล้องถอยให้เห็นสินค้าทั้งชิ้นพร้อมคนในเฟรมเดียว เทียบขนาดได้ชัด',
}
L['poseEN'] = {
  'ถือสินค้า': 'Pose: the presenter holds the product in hand throughout, close to camera.',
  'ยืนข้างสินค้า': 'Pose override: the presenter never holds the product — it rests on a table, shelf or floor beside them; they stand next to it presenting with an open hand or pointing.',
  'สินค้าใหญ่': 'Pose override (large product): it stays full size on the floor; the presenter stands beside it with an open hand, never holding or lifting it; camera pulled back so the whole product and person fit at true scale.',
}
CLOSE_OLD = 'ท่าฉากปิดการขาย (ฉากสุดท้าย): พรีเซนเตอร์ถือสินค้าไว้ข้างหน้า มองกล้อง ยิ้ม แล้วพูดคำชวนซื้อ'
L['poseClose'] = {
  AUTO: 'พรีเซนเตอร์ถือสินค้าไว้ข้างหน้า (ชิ้นใหญ่ เช่น เฟอร์นิเจอร์ เครื่องใช้ไฟฟ้า ให้ยืนข้างสินค้าแทน ห้ามยก)',
  'ถือสินค้า': 'พรีเซนเตอร์ถือสินค้าไว้ข้างหน้า',
  'ยืนข้างสินค้า': 'พรีเซนเตอร์ยืนข้างสินค้า ผายมือไปที่สินค้า (ไม่ถือ)',
  'สินค้าใหญ่': 'พรีเซนเตอร์ยืนข้างสินค้าชิ้นใหญ่ ผายมือไปที่สินค้า (ไม่ถือ ไม่ยก) กล้องเห็นสินค้าทั้งชิ้น',
}
POSE_ON = {'op': 'and', 'list': [
  {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svPose}', 'b': AUTO}},
  {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svPose}', 'b': ''}},
  {'op': 'eq', 'a': {'op': 'lookup', 'table': 'tplChar', 'key': '{values.templateId}', 'fallback': ''}, 'b': 'yes'}]}
def pblk(head, table):
    return {'op': 'block', 'sep': '', 'parts': [{'when': POSE_ON, 'value': {'op': 'concat', 'parts': [head, {'op': 'lookup', 'table': table, 'key': '{values.svPose}', 'fallback': ''}]}}]}
def sblk(head, n, tail):
    return {'op': 'block', 'sep': '', 'parts': [{'when': 'item.sizeInfo!=', 'value': {'op': 'concat', 'parts': [head, {'op': 'clamp', 'max': n, 'value': '{item.sizeInfo}'}, tail]}}]}
d['values'].setdefault('svPose', AUTO)

def ins_after(parts, pred, item):
    for i, p in enumerate(parts):
        if pred(p): parts.insert(i + 1, item); return 1
        if isinstance(p, dict) and isinstance(p.get('parts'), list) and ins_after(p['parts'], pred, item): return 1
    return 0
has = lambda k: (lambda p: isinstance(p, dict) and k in json.dumps(p, ensure_ascii=False))
done = 'poseEN' in json.dumps(d['ops'], ensure_ascii=False)
n = 0
if not done:
    # mnPlan: ท่า + ขนาดจริง · ฉากปิดการขายตามท่า
    n += ins_after(ops['mnPlan']['prompt']['parts'], has('"bgTH"'), pblk('\n', 'poseTH'))
    pp = ops['mnPlan']['prompt']['parts'][0]['parts']
    i = next(i for i, p in enumerate(pp) if isinstance(p, str) and 'ราคา: {item.price}\n' in p)
    a, b = pp[i].split('ราคา: {item.price}\n', 1)
    pp[i:i + 1] = [a + 'ราคา: {item.price}\n',
                   {'op': 'block', 'sep': '', 'parts': [{'when': 'item.sizeInfo!=', 'value': 'ขนาดสินค้าจริง: {item.sizeInfo} (ใช้เทียบสัดส่วนกับมือ คน และของรอบตัวทุกฉาก)\n'}]}, b]
    k = next(k for k, p in enumerate(pp) if isinstance(p, str) and CLOSE_OLD in p)
    a, b = pp[k].split(CLOSE_OLD, 1)
    pp[k:k + 1] = [a + 'ท่าฉากปิดการขาย (ฉากสุดท้าย): ', {'op': 'lookup', 'table': 'poseClose', 'key': '{values.svPose}', 'fallback': L['poseClose'][AUTO]},
                   ' มองกล้อง ยิ้ม แล้วพูดคำชวนซื้อ' + b]
    n += 2
    # mnBoard
    n += ins_after(ops['mnBoard']['prompt']['parts'], has('"bgTH"'), pblk('\n', 'poseTH'))
    n += ins_after(ops['mnBoard']['prompt']['parts'], has('"poseTH"'), sblk('\nขนาดสินค้าจริง: ', 80, ' — วาดสัดส่วนให้ตรงขนาดนี้เทียบกับคน มือ และของรอบตัว'))
    # mnVideo / mnVideo2
    n += ins_after(ops['mnVideo']['prompt']['parts'], has('"bgEN"'), pblk('\n\n', 'poseEN'))
    n += ins_after(ops['mnVideo']['prompt']['parts'], has('"poseEN"'), sblk('\n\nReal product size: ', 60, ' — keep this scale next to people and objects.'))
    n += ins_after(ops['mnVideo2']['prompt']['parts'], lambda p: p == '.', pblk('\n\n', 'poseEN'))
    assert n == 8, n
# สินค้า: ช่อง sizeInfo · task รับต่อ
pf = d['collections']['products']['fields']
if 'sizeInfo' not in pf: pf.insert(pf.index('price') + 1, 'sizeInfo')
tf = d['collections']['tasks']['fields']
if 'sizeInfo' not in tf: tf.append('sizeInfo')
ops['mnQueue']['spawn']['fields']['sizeInfo'] = '{parent.fields.sizeInfo}'

# UI: ช่องขนาดสินค้า (ใต้ราคา) · ตัวเลือกท่า (ใต้ฉากหลัง · เฉพาะเทมเพลตที่มีคน)
prod = d['phases'][0]['form'][2]['card'][0]['card'][0]['card']
if not any('"field": "sizeInfo"' in json.dumps(c) for c in prod):
    i = next(i for i, c in enumerate(prod) if '"field": "price"' in json.dumps(c))
    prod.insert(i + 1, {'el': 'box', 'className': 'flex flex-col gap-2', 'card': [
        {'el': 'text', 'value': 'ขนาดสินค้า (ไม่บังคับ)', 'className': '!text-[13.5px] @[640px]:!text-[13px] !text-[var(--ev-text)] opacity-65 uppercase tracking-[0.14em] font-black px-0.5 mb-2'},
        {'el': 'input', 'field': 'sizeInfo', 'placeholder': 'เช่น สูง 180 ซม. กว้าง 90 ซม. · หนัก 15 กก.', 'className': '!h-14 !px-4 !rounded-xl !text-[20px] @[640px]:!text-[19px]'},
        {'el': 'text', 'value': 'ช่วยให้ AI วาดสัดส่วนสินค้าเทียบกับคนได้ตรง — สำคัญกับสินค้าชิ้นใหญ่', 'className': '!text-[13px] @[640px]:!text-[12px] opacity-50 leading-relaxed px-0.5'}]})
sett = d['phases'][0]['form'][0]['card'][0]['card'][2]['card']
if not any('"field": "svPose"' in json.dumps(c) for c in sett):
    i = next(i for i, c in enumerate(sett) if '"field": "svBg"' in json.dumps(c))
    sett.insert(i + 1, {'el': 'box', 'className': 'flex flex-col gap-2 mt-2',
      'when': {'op': 'eq', 'a': {'op': 'lookup', 'table': 'tplChar', 'key': '{values.templateId}', 'fallback': ''}, 'b': 'yes'},
      'card': [
        {'el': 'row', 'className': 'items-center gap-2 mt-1', 'style': {'flexWrap': 'nowrap'}, 'card': [
          {'el': 'icon', 'icon': 'accessibility_new', 'textSize': 'text-[18px]', 'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center'},
          {'el': 'text', 'value': 'ท่านำเสนอสินค้า', 'className': '!text-[17px] @[640px]:!text-[16px] font-black !text-[var(--ev-text)]'}]},
        {'el': 'text', 'value': 'นาย/นางแบบถือสินค้า หรือยืนข้างแล้วชี้นำเสนอ · สินค้าใหญ่ = ยืนข้าง กล้องถอยให้เห็นทั้งชิ้น (ใส่ขนาดสินค้าในหน้าแก้ไขสินค้าด้วย)', 'className': '!text-[14px] @[640px]:!text-[13px] opacity-60 leading-relaxed mb-1'},
        {'el': 'grid-select', 'field': 'svPose', 'cols': 2, 'mobile': {'cols': 2}, 'contained': True, 'className': '!min-h-[48px] @[420px]:!min-h-0', 'options': [
          {'value': AUTO, 'label': 'อัตโนมัติ', 'desc': 'ชิ้นเล็กถือ · ชิ้นใหญ่ยืนข้าง', 'icon': 'auto_fix_high'},
          {'value': 'ถือสินค้า', 'label': 'ถือสินค้า', 'desc': 'ยกใกล้กล้อง', 'icon': 'back_hand'},
          {'value': 'ยืนข้างสินค้า', 'label': 'ยืนข้าง ชี้นำเสนอ', 'desc': 'ไม่ต้องถือ', 'icon': 'person_pin'},
          {'value': 'สินค้าใหญ่', 'label': 'สินค้าใหญ่', 'desc': 'ยืนข้าง เห็นทั้งชิ้น', 'icon': 'chair'}]}]})
print('v29: inject', n)
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))
