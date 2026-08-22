#!/usr/bin/env python3
# ⚠️⚠️ ONE-SHOT BOOTSTRAP — ห้ามรันซ้ำ ⚠️⚠️
# สคริปต์นี้ใช้ "ครั้งเดียว" ตอนคลอด story.json จาก minimal.json (2026-08-22)
# หลังจากนี้ story.json = source of truth ของตัวเอง — รันซ้ำ = ทับงานที่แก้ไปแล้วทั้งหมด
# เก็บไว้เป็นบันทึกว่า story ถอดมาจาก minimal ยังไง (แผนที่ op/field/UI)
# build-story.py — สร้าง story.json (หมีแว่น เล่าเรื่อง) จาก minimal.json  · รันซ้ำได้เสมอ
#
# สถาปัตยกรรม (ต่างจาก minimal):
#   products = "งาน 1 ชิ้น" (พื้นที่ + ของหลัก) → slots image..image5 (ของ) + room1,room2 (พื้นที่จริง) + full (คลิปเต็ม)
#   1 task   = 1 ฉาก 10 วิ (5 จังหวะ)          → N ฉากต่อเนื่อง (values.clipsPerProduct = จำนวนฉาก)
#   stFrame  = เฟรมเริ่มฉาก (photoreal 9:16)   → refs: เฟรมฉากก่อนหน้า (prevId) + พื้นที่ + ของ + หน้าคน
#   stVideo  = startFrame ชี้ slot board ของตัวเอง → frame-to-video (engine ละเว้น refs เมื่อมี startFrame)
#   stMerge  = merge over products from tasks  → slot 'full' = คลิปเต็มไฟล์เดียว
import json, os

ROOT = '/Users/tammaster/Desktop/Dev/bear-clan/easybear-config'
SRC, DST = os.path.join(ROOT, 'minimal.json'), os.path.join(ROOT, 'story.json')

# ── 0) rename op ids + brain namespace บนข้อความดิบ (ครอบ UI ที่อ้างถึงด้วย) ──
raw = open(SRC, encoding='utf-8').read()
for a, b in [('mnPlan', 'stPlan'), ('mnQueue', 'stQueue'), ('mnBoard', 'stFrame'),
             ('mnVideo', 'stVideo'), ('brain.mn', 'brain.st')]:
    raw = raw.replace(a, b)
cfg = json.loads(raw)
OPS = {o['id']: o for o in cfg['ops']}

ACCENT = '#0e9384'   # teal อบอุ่น — แยกจาก film/hardsell/minimal/flow

# ─────────────────────────── 1) identity / theme ───────────────────────────
cfg['title'] = 'หมีแว่น เล่าเรื่อง'
cfg['icon'] = 'auto_stories'
cfg['app'] = {'id': 'story', 'name': 'EasyBear Story'}
cfg['home'] = {
    'title': 'หมีแว่น เล่าเรื่อง',
    'tag': 'EasyBear Story',
    'description': 'หมีผู้ช่วยทำคลิปเล่าเรื่อง — แนบรูปพื้นที่จริงกับของที่จะใช้ แล้วให้หมีเล่าให้เห็นว่า "ก่อน" กลายเป็น "หลัง" ยังไง ยาว 10-30 วินาที',
    'cta': 'สร้างโปรเจกต์ใหม่', 'ctaContrast': True, 'loadLabel': 'โหลดโปรเจกต์เดิม',
    'footer': cfg['home']['footer'],
}

def repaint(n):
    if isinstance(n, dict):  return {k: repaint(v) for k, v in n.items()}
    if isinstance(n, list):  return [repaint(v) for v in n]
    if isinstance(n, str):   return n.replace('#2f7fe8', ACCENT).replace('#2F7FE8', ACCENT).replace('47,127,232', '14,147,132')
    return n
cfg['theme'] = repaint(cfg['theme'])

# ─────────────────────────── 2) values ───────────────────────────
V = cfg['values']
V['clipsPerProduct'] = '2'                    # จำนวนฉาก (10 วิ/ฉาก)
V['svTextOn'] = 'ไม่มีข้อความ'                 # bible §20
V['svChar'] = 'มีพรีเซนเตอร์ไทย 1 คนในคลิป'    # bible §9 ต้องมีคนลงมือทำ
V['svPace'] = 'ไทม์แลปส์'                      # bible §11
V['svLook'] = 'สมจริงแบบถ่ายจริง'              # bible §15/16
V['svCam1'] = 'ไวด์เห็นพื้นที่ทั้งหมด'
V['svCam2'] = 'มีเดียมเห็นคนกำลังทำ'
V['svCam3'] = 'โคลสอัพมือกับของ'
V['svCam4'] = 'มุม 45 องศา แทร็กกิ้งลื่นๆ'
V['svCam5'] = 'ไวด์ปิดท้ายเห็นผลลัพธ์'
for i in range(1, 6): V['svPres%d' % i] = ''

# ─────────────────────────── 3) collections ───────────────────────────
P = cfg['collections']['products']
for f in ['room', 'before', 'goal']:
    if f not in P['fields']: P['fields'].insert(P['fields'].index('info') + 1, f)
P['slots'] = ['image', 'image2', 'image3', 'image4', 'image5', 'room1', 'room2', 'full']

T = cfg['collections']['tasks']
for f in ['sceneRole', 'stateBefore', 'stateAfter', 'room']:
    if f not in T['fields']: T['fields'].insert(T['fields'].index('category') + 1, f)

# ─────────────────────────── 4) brain ───────────────────────────
cfg['brain'] = {'st': {
 'imgNote': 'รูปที่แนบ = ของจริงของผู้ใช้ · รูปพื้นที่ = สถานที่จริงของคลิป (ทุกฉากต้องเป็นที่เดียวกัน) · รูปสินค้า = ต้นแบบเป๊ะ ห้ามดัดแปลง',
 'sys': """คุณคือผู้กำกับคลิปสั้นแนวตั้งสาย "เล่าให้เห็นการเปลี่ยนแปลง" ของพี่หมีแว่น — ออกแบบคลิป 9:16 ที่พาคนดูจาก "สภาพก่อน" ไปสู่ "ผลลัพธ์หลัง" อย่างเข้าใจง่ายและน่าดูจนจบ

กฎทอง — ทุกคลิปต้องตอบ 5 ข้อนี้ได้ชัด:
1. BEFORE พื้นที่/สถานการณ์ตอนเริ่มเป็นอย่างไร
2. MAIN OBJECT ของหรือองค์ประกอบหลักที่เข้ามาเปลี่ยนพื้นที่คืออะไร
3. ACTION คนในคลิปกำลังทำอะไร
4. PROGRESS จัด/ทำไปทีละขั้นอย่างไร
5. AFTER ผลลัพธ์สุดท้ายเป็นอย่างไร

โครงเรื่องมาตรฐาน 6 จังหวะ: เห็นพื้นที่ก่อน → นำของเข้ามา → วางตำแหน่ง → ลงมือจัด/ทำ → เก็บรายละเอียด → เผยผลลัพธ์

การแบ่งฉาก (1 ฉาก = 10 วินาที):
- ขอ 1 ฉาก: ยัดครบทั้ง 6 จังหวะในฉากเดียว
- ขอ 2 ฉาก: ฉาก 1 = เห็นพื้นที่ + นำของเข้ามา + วางตำแหน่ง · ฉาก 2 = ลงมือจัด + เก็บรายละเอียด + เผยผลลัพธ์
- ขอ 3 ฉาก: ฉาก 1 จัดเตรียม (เห็นพื้นที่ + นำของเข้ามา) · ฉาก 2 ลงมือทำ (จัด แยกประเภท จัดตำแหน่ง) · ฉาก 3 เก็บงาน (เก็บรายละเอียด + เผยผลลัพธ์)
ห้ามเล่าเหตุการณ์เดิมซ้ำข้ามฉากเด็ดขาด — แต่ละฉากต้องเดินเรื่องต่อจากฉากก่อนหน้า

ภายใน 1 ฉาก แบ่งเป็น 5 จังหวะย่อย จังหวะละ 2 วินาที:
- จังหวะ 1 (0-2 วิ) เห็นพื้นที่/สถานการณ์ตั้งต้นของฉากนี้ — ไวด์
- จังหวะ 2 (2-4 วิ) คนลงมือ: ยก วาง เปิด หยิบ — มีเดียม
- จังหวะ 3 (4-6 วิ) โคลสอัพมือกับของ ให้เห็นว่าใช้งานได้จริง
- จังหวะ 4 (6-8 วิ) ความคืบหน้าของงาน — มุม 45 องศา / แทร็กกิ้ง / ท็อปดาวน์
- จังหวะ 5 (8-10 วิ) ปิดฉากด้วยภาพที่สวยที่สุดของฉากนั้น

กฎเหล็กของแอ็กชัน: หนึ่งจังหวะ = หนึ่งแอ็กชันหลักเท่านั้น
ผิด: "เธอยกชั้นวาง เปิดตู้ จัดจาน แล้วตกแต่งครัว"
ถูก: "เธอวางชั้นวางลงข้างเคาน์เตอร์อย่างเป็นธรรมชาติ"

ความต่อเนื่อง (ห้ามพลาด): ทุกฉากคือ "ที่เดิม คนเดิม ของเดิม" — ผนัง ประตู หน้าต่าง เฟอร์นิเจอร์ ทิศแสง ใบหน้า ทรงผม เสื้อผ้า และตัวสินค้า ต้องเหมือนกันทุกฉาก สิ่งเดียวที่เปลี่ยนได้คือสภาพของงานที่คืบหน้าขึ้น
- stateBefore ของฉากถัดไป ต้องเท่ากับ stateAfter ของฉากก่อนหน้าเสมอ
- ฉากแรก stateBefore = สภาพก่อนเริ่มที่ผู้ใช้ระบุ (ว่างไว้ = อนุมานจากรูปพื้นที่ที่แนบมา)
- ฟิลด์ room ต้องเป็นข้อความ "เดียวกันทุกฉาก" คำต่อคำ

ใช้ข้อมูลจริงเท่านั้น: ห้ามแต่งสรรพคุณ ราคา ส่วนลด สถิติ หรือรายละเอียดของที่ผู้ใช้ไม่ได้ให้มา · ของหลักต้องตรงตามรูปที่แนบ 100% ห้ามเปลี่ยนรูปทรง สี วัสดุ จำนวนชั้น จำนวนช่อง หรือดีไซน์

กฎคำอธิบายภาพ:
- s1th-s5th: ภาษาไทย ไม่เกิน 14 คำต่อจังหวะ สำหรับให้ผู้ใช้อ่านและแก้
- s1en-s5en: ภาษาอังกฤษ 1-2 ประโยคต่อจังหวะ บรรยายแบบถ่ายจริง (มุมกล้อง แสง องค์ประกอบ การเคลื่อนไหวของคนและของ) — ต้องเป็นการเคลื่อนไหวที่เป็นไปได้จริงทางฟิสิกส์ มือและนิ้วถูกกายวิภาค ของมีน้ำหนักจริง
- camN: มุมกล้องของจังหวะนั้น เป็นวลีไทยสั้น · จังหวะที่ผู้ใช้ล็อกมุมกล้องไว้ ต้องใช้ตามที่ล็อกทุกฉาก

กฎ Overlay (ข้อความบนภาพ ov1-ov5):
- 2-6 คำไทยต่อจังหวะ สั้น เน้นประโยชน์ที่คนดูได้
- ห้าม emoji · ห้ามภาษาอังกฤษปน ยกเว้นตัวเลข/หน่วยจากข้อมูลที่ผู้ใช้ให้
- ชื่อของหลักปรากฏได้ครั้งเดียวทั้งคลิป

กฎบทพูด VO (vo1-vo5):
- ทั้งฉากรวม 18-26 คำไทย เฉลี่ย 4-5 คำต่อจังหวะ น้ำเสียงอบอุ่นเป็นกันเอง เหมือนเล่าให้เพื่อนฟัง
- คำลงท้ายและสรรพนามต้องตรงกับเพศเสียงพากย์ที่ระบุท้ายคำสั่ง (หญิง = ค่ะ/คะ · ชาย = ครับ) ห้ามผสมเด็ดขาด
- ฟิลด์ voice = "หญิง" หรือ "ชาย" เท่านั้น ต้องตรงกับคำลงท้ายที่ใช้จริง
- ห้ามพูดสิ่งที่ผู้ใช้ไม่ได้ระบุ

Output: ตอบเป็น JSON array ล้วน ห้ามมี markdown ห้ามมีข้อความอื่นนอก JSON · จำนวน object = จำนวนฉากที่ขอ เรียงตามลำดับเวลา รูปแบบแต่ละ object:
{"productName":"ชื่องาน/ของหลัก คัดลอกตรงตามที่ให้มา","category":"ประเภทพื้นที่ เช่น ห้องครัว ห้องนอน ระเบียง แปลงผัก หน้าร้าน","room":"คำบรรยายพื้นที่สั้นๆ ที่คงที่ทุกฉาก เช่น ครัวเล็กผนังขาว ตู้ไม้อ่อน หน้าต่างบานใหญ่ทางซ้าย","palette":"บรรยากาศแสงและโทนสีของงานนี้ เช่น แสงธรรมชาติช่วงสาย โทนไม้อุ่น","sceneRole":"บทบาทของฉากนี้ เช่น จัดเตรียม / ลงมือทำ / เก็บงานและเผยผลลัพธ์","stateBefore":"สภาพพื้นที่ตอนฉากนี้เริ่ม","stateAfter":"สภาพพื้นที่ตอนฉากนี้จบ","synopsis":"สรุปฉากนี้ 1 ประโยคภาษาไทย","voice":"หญิง หรือ ชาย","s1th":"...","s1en":"...","ov1":"...","vo1":"...","cam1":"...","s2th":"...","s2en":"...","ov2":"...","vo2":"...","cam2":"...","s3th":"...","s3en":"...","ov3":"...","vo3":"...","cam3":"...","s4th":"...","s4en":"...","ov4":"...","vo4":"...","cam4":"...","s5th":"...","s5en":"...","ov5":"...","vo5":"...","cam5":"..."}

กฎ overlay เพิ่มเติม: ovN ทุกตัวเป็นภาษาไทย บรรทัดเดียว ไม่เกิน 5 คำ ห้ามใส่เลขฉาก/ลิสต์"""}}

# ─────────────────────────── 5) lookups ───────────────────────────
cfg['lookups']['opNames'] = {
    'stPlan': 'กำลังเขียนบท', 'stQueue': 'กำลังจัดคิวฉาก',
    'stFrame': 'กำลังวาดเฟรมเริ่มฉาก', 'stVideo': 'กำลังสร้างวิดีโอ', 'stMerge': 'กำลังต่อฉากเป็นคลิปเดียว',
}
cfg['lookups']['paceEN'] = {
    'ไทม์แลปส์': 'Fast but readable timelapse motion — accelerated yet every object interaction stays clearly legible, satisfying rhythm.',
    'ความเร็วปกติ': 'Natural real-time pacing, smooth deliberate movement.',
}
cfg['lookups']['lookEN'] = {
    'สมจริงแบบถ่ายจริง': 'Photorealistic, natural daylight, soft shadows, ultra-realistic materials, commercial-quality footage.',
    'อบอุ่นโทนไม้': 'Photorealistic with warm wood tones, cozy golden natural light, soft shadows, tactile natural materials.',
    'สว่างสะอาดมินิมอล': 'Photorealistic, bright airy white space, clean minimal composition, crisp soft daylight.',
}

# ─────────────────────────── 6) ops ───────────────────────────
CAMLINES = '\n'.join(
    'จังหวะ %d (%d-%d วิ) — มุมกล้อง: {values.svCam%d} · การนำเสนอ: {values.svPres%d}' % (i, (i-1)*2, i*2, i, i)
    for i in range(1, 6))

# ---- stPlan (llm) ----
plan = OPS['stPlan']
plan['images'] = ['{item.slots.room1}', '{item.slots.room2}', '{item.slots.image}',
                  '{item.slots.image2}', '{item.slots.image3}', '{item.slots.image4}', '{item.slots.image5}']
plan['logRun'] = '[{item.name}] หมีกำลังเขียนบท {values.clipsPerProduct} ฉาก (5 จังหวะ/ฉาก)'
plan['logDone'] = '[{item.name}] ได้บทครบทุกฉากแล้ว'
plan['prompt']['parts'] = ["""ออกแบบแผนคลิปเล่าเรื่อง "ก่อน → หลัง" จำนวน {values.clipsPerProduct} ฉาก (ฉากละ 10 วินาที · เรียงต่อกันเป็นคลิปเดียว) สำหรับงานนี้

ชื่องาน / ของหลักที่ใช้: {item.name}
รายละเอียด จุดเด่น: {item.description} {item.info}
พื้นที่ที่ถ่าย: {item.room}
สภาพก่อนเริ่ม: {item.before}
ผลลัพธ์ที่อยากได้: {item.goal}
ราคา: {item.price}
โปรโมชั่น: {item.promotion}
คำชวนปิดท้าย (CTA): {item.cta}
(ค่าว่าง = ไม่ต้องพูดถึง หรืออนุมานจากรูปที่แนบ · มีค่า = ต้องสะท้อนในบท)
ไอเดียเพิ่มเติมจากผู้ใช้: {item.idea}
โทน/บรรยากาศที่อยากได้: {item.tone} {values.svTone}
สไตล์ภาพ: {values.svLook} · จังหวะการเล่า: {values.svPace}

รูปที่แนบมา: รูปพื้นที่จริง (ถ้ามี) = สถานที่ของคลิปนี้ ต้องเป็นที่เดียวกันทุกฉาก · รูปของหลัก = ต้นแบบเป๊ะ ห้ามดัดแปลง

ข้อกำหนดมุมกล้องรายจังหวะจากผู้ใช้ (ค่าว่าง = ออกแบบเอง):
""" + CAMLINES + """

ตอบเป็น JSON array เท่านั้น — token แรกของคำตอบต้องเป็น [ และ token สุดท้ายต้องเป็น ] ห้ามมีข้อความอื่นใดนอก JSON · จำนวน object ในอาร์เรย์ = {values.clipsPerProduct}"""] + plan['prompt']['parts'][1:]

# ---- stQueue (transform spawn) : เพิ่มฟิลด์ใหม่เข้า mapping ----
sp = OPS['stQueue']['spawn']
for f in ['sceneRole', 'stateBefore', 'stateAfter', 'room']:
    sp['fields'][f] = '{item.fields.%s}' % f
OPS['stQueue']['logRun'] = 'จัดคิวฉากจากงานที่เลือกใช้'
OPS['stQueue']['logDone'] = 'จัดคิวแล้ว — พร้อมวาดเฟรมเริ่มฉาก'

# ---- stFrame (image) : เฟรมเริ่มฉาก ภาพเดี่ยว 9:16 ----
fr = OPS['stFrame']
old_fr = fr['prompt']['parts']
fr['logRun'] = '[{item.productName} ฉาก {item.clipIndex}] กำลังวาดเฟรมเริ่มฉาก'
fr['logDone'] = '[{item.productName} ฉาก {item.clipIndex}] ได้เฟรมเริ่มฉากแล้ว'
fr['refs'] = {
    'op': 'lookupRefs', 'from': 'tasks',
    'by': {'op': 'prevId', 'from': 'tasks', 'by': 'prod'}, 'slot': 'board',
    'also': [
        {'from': 'products', 'by': '{item.refs.prod}', 'slot': 'room1'},
        {'from': 'products', 'by': '{item.refs.prod}', 'slot': 'room2'},
        {'from': 'products', 'by': '{item.refs.prod}', 'slot': 'image'},
        {'from': 'products', 'by': '{item.refs.prod}', 'slot': 'image2'},
        {'from': 'products', 'by': '{item.refs.prod}', 'slot': 'image3'},
        {'from': 'products', 'by': '{item.refs.prod}', 'slot': 'image4'},
        {'from': 'products', 'by': '{item.refs.prod}', 'slot': 'image5'},
        {'from': 'characters', 'by': '{values.charId}', 'slot': 'face',
         'when': {'op': 'and',
                  'a': {'op': 'eq', 'a': '{values.svChar}', 'b': 'มีพรีเซนเตอร์ไทย 1 คนในคลิป'},
                  'b': {'op': 'eq', 'a': '{values.svCharSrc}', 'b': 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'}}},
    ],
}
fr['prompt']['parts'] = ["""สร้างภาพนิ่ง "เฟรมแรกของฉากที่ {item.clipIndex}" สำหรับคลิป "{item.productName}"

⚠️ ต้องเป็นภาพเดียวเต็มเฟรม 9:16 เหมือนภาพถ่ายจริง — ห้ามเป็นแผงสตอรีบอร์ด กริด คอลลาจ ภาพซ้อน กรอบ หรือแบ่งช่องเด็ดขาด

สถานที่ (ต้องเหมือนกันทุกฉาก): {item.room}
สภาพพื้นที่ ณ ต้นฉากนี้: {item.stateBefore}
สิ่งที่ต้องเห็นในเฟรมนี้: {item.s1th}
มุมกล้อง: {item.cam1}
บรรยากาศแสงและโทน: {item.palette}
สไตล์ภาพ: {values.svLook} — แสงธรรมชาตินุ่ม เงาอ่อน วัสดุสมจริง สัดส่วนห้องสมจริง คุณภาพระดับงานโฆษณา 4K

ล็อกสถานที่: ถ้ามีภาพฉากก่อนหน้าหรือรูปพื้นที่จริงแนบมา ให้ถือเป็น "ห้องเดียวกัน" — ผนัง พื้น ประตู หน้าต่าง เฟอร์นิเจอร์ ตำแหน่ง ทิศแสง ต้องตรงกันทั้งหมด เปลี่ยนได้เฉพาะความคืบหน้าของงาน
ล็อกของหลัก: ใช้ของจากรูปที่แนบเป็นต้นแบบเป๊ะ คงรูปทรง สี วัสดุ สัดส่วน จำนวนชั้น จำนวนช่อง มือจับ ขา และรายละเอียดที่มองเห็นทุกจุด ห้ามออกแบบใหม่ ห้ามบิดเบี้ยว ห้ามมีชิ้นส่วนหาย
ล็อกคน: ถ้ามีคนในเฟรม ต้องเป็นคนเดิม หน้าเดิม ทรงผมเดิม เสื้อผ้าเดิมทุกฉาก · มือและนิ้วถูกต้องตามกายวิภาค ไม่มีนิ้วเกิน ไม่มีแขนซ้อน ของไม่ลอย ท่าทางเป็นไปได้จริง

""",
 {'op': 'block', 'sep': '', 'parts': [
   {'when': 'values.svTextOn!=ไม่มีข้อความ',
    'value': 'ข้อความบนภาพ: {values.svText} — ข้อความไทยบรรทัดเดียว ไม่เกิน 5 คำ ว่า "{item.ov1}" วางไม่ทับของหลัก สะกดถูก คมชัด · ห้ามใช้ emoji ห้ามพิมพ์หัวข้อภาษาอังกฤษหรือบรรทัดบอกสไตล์ลงในภาพ'},
   {'when': 'values.svTextOn=ไม่มีข้อความ',
    'value': 'ข้อความบนภาพ: ไม่มี — ภาพต้องสะอาดล้วน ห้ามมีตัวหนังสือ ป้าย ซับไตเติล ลายน้ำ หรือหน้าจอแอปใดๆ (ตัวอักษรเดียวที่มีได้คือฉลากจริงบนตัวของ)'},
 ]},
 old_fr[22], old_fr[23]]

# ---- stVideo (video) : frame-to-video จาก slot board ----
vd = OPS['stVideo']
old_vd = vd['prompt']['parts']
vd['startFrame'] = '{item.slots.board}'
vd.pop('refs', None)
vd['logRun'] = '[{item.productName} ฉาก {item.clipIndex}] กำลังสร้างวิดีโอฉากนี้ (10 วิ)'
vd['logDone'] = '[{item.productName} ฉาก {item.clipIndex}] วิดีโอฉากนี้เสร็จแล้ว'
BEAT = ['Beat 1 (0-2s) — establish', 'Beat 2 (2-4s) — action', 'Beat 3 (4-6s) — close-up interaction',
        'Beat 4 (6-8s) — progress', 'Beat 5 (8-10s) — reveal']
head = """A single continuous 10-second vertical 9:16 photorealistic video. Start immediately from the attached first frame — the real full-screen space. NEVER show a storyboard grid, collage, split screen, panel borders, phone UI or app interface.

Location (identical for the entire clip): {item.room}
State at the start of this scene: {item.stateBefore}
State at the end of this scene: {item.stateAfter}

Maintain strict visual continuity: same room layout and architecture, same door and window positions, same furniture placement, same lighting direction, same person identity, hairstyle and outfit, and the same product appearance throughout. Only the progress of the work changes.

Keep the product 100% identical to the first frame — same shape, color, material, proportions, components and visible details. No redesign, no distortion, no missing parts.

Realistic human motion, correct hand anatomy and fingers, physically plausible movement, believable object weight, natural body mechanics. One primary action per beat.

""" + BEAT[0] + ': {item.s1en}. Camera: {item.cam1}.'
newparts = [head, old_vd[1]]
for i in range(2, 6):
    newparts.append('\n' + BEAT[i-1] + ': {item.s%den}. Camera: {item.cam%d}.' % (i, i))
    newparts.append(old_vd[(i-1)*2 + 1])
newparts.append({'op': 'concat', 'parts': [
    '\n\nMotion: ', {'op': 'lookup', 'table': 'paceEN', 'key': '{values.svPace}',
                     'fallback': 'Fast but readable timelapse motion, satisfying rhythm.'},
    '\nVisual style: ', {'op': 'lookup', 'table': 'lookEN', 'key': '{values.svLook}',
                         'fallback': 'Photorealistic, natural daylight, soft shadows, ultra-realistic materials.'}]})
newparts.append(old_vd[10])          # audio / voice-over block (reuse verbatim)
newparts.append("""

Negative: no storyboard grid, no split screen, no panel borders, no on-screen UI or phone frame, no watermark, no floating objects, no duplicated products, no changing room layout or furniture, no extra fingers, no malformed hands, no duplicated limbs, no impossible physics, no random objects appearing, no inconsistent lighting.""")
newparts += [old_vd[12], old_vd[13], old_vd[14], old_vd[15]]
vd['prompt']['parts'] = newparts

# ---- stMerge (merge) : ต่อทุกฉากของงานนั้นเป็นคลิปเดียว ----
cfg['ops'].append({
    'id': 'stMerge', 'type': 'merge', 'over': 'products', 'where': 'enabled=true',
    'from': 'tasks', 'by': 'prod', 'slot': 'video', 'out': 'full',
    'logRun': '[{item.name}] กำลังต่อฉากทั้งหมดเป็นคลิปเดียว',
    'logDone': '[{item.name}] ได้คลิปเต็มแล้ว',
})

# ─────────────────────────── 7) stages / auto / editor ───────────────────────────
cfg['stages'] = [{'op': 'stPlan'}, {'op': 'stQueue'}, {'op': 'stFrame'}, {'op': 'stVideo'},
                 {'op': 'stMerge'}, {'checkpoint': 'main'}]
cfg['auto']['productLoop'] = {'source': 'products', 'where': 'enabled=true',
                              'plan': 'stPlan', 'queue': 'stQueue', 'gens': ['stFrame', 'stVideo'],
                              'childRef': 'prod', 'capDefault': 999}

json.dump(cfg, open(DST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✓ wrote', DST, os.path.getsize(DST), 'bytes')

# ═══════════════════════════════════════════════════════════════
# 8) UI — copy + ช่องกรอกใหม่ (พื้นที่) + ปุ่มความยาวคลิป
# ═══════════════════════════════════════════════════════════════
import copy, re

PH = cfg['phases']

# ---- 8.1 แทนคำเฉพาะ "คีย์ที่ปลอดภัย" เท่านั้น ----
# ⚠️ ห้ามแตะ option.value / when / field — พวกนั้นเป็น key ของ lookup (charPlan/voicePlan…) แตะแล้วกฎหาย
TXT = [
    ('บทที่ได้มาไม่สมบูรณ์ — กดปุ่มสมองที่สินค้าเพื่อคิดบทใหม่ แล้วกด "เริ่ม" อีกครั้ง',
     'บทที่ได้มาไม่สมบูรณ์ — กดปุ่มสมองที่งานนั้นเพื่อคิดบทใหม่ แล้วกด "เริ่ม" อีกครั้ง'),
    ('ยังไม่ได้เลือกใช้สินค้า — เข้า "จัดการสินค้า" (ข้อ 1) ก่อน',
     'ยังไม่ได้เลือกใช้งาน — เข้า "จัดการงาน" (ข้อ 1) ก่อน'),
    ('มีสินค้าที่เลือกใช้แต่ยังไม่มีรูป — ใส่รูปให้ครบก่อน (สูตรล็อกหน้าตาสินค้าตามรูปจริง)',
     'มีงานที่เลือกใช้แต่ยังไม่มีรูป — ใส่รูปของหลักก่อน (สูตรล็อกหน้าตาของตามรูปจริง)'),
    ('ยังไม่มีสินค้า — กด "จัดการสินค้า" เพื่อเพิ่ม', 'ยังไม่มีงาน — กด "จัดการงาน" เพื่อเพิ่ม'),
    ('คุมสีพื้นหลัง/บรรยากาศของทุกฉาก — มีผลทั้งภาพบอร์ดและวิดีโอจริง',
     'คุมบรรยากาศแสงของทุกฉาก — มีผลทั้งเฟรมเริ่มฉากและวิดีโอจริง'),
    ('สินค้าที่ตั้งโทนสีไว้เอง จะใช้ของสินค้าก่อนเสมอ', 'งานที่ตั้งโทนไว้เอง จะใช้ของงานนั้นก่อนเสมอ'),
    ('คลิปมีคนถือ/ใช้สินค้าไหม — มีผลทั้งภาพสตอรีบอร์ดและวิดีโอจริง',
     'คลิปนี้มีคนลงมือทำไหม — สูตรนี้แนะนำให้มีคน (เห็นมือทำงานจริง = ดูน่าเชื่อ)'),
    ('เน้นภาพสินค้าโดยตรง ไม่มีคนในคลิป', 'เห็นเฉพาะพื้นที่กับของ ไม่มีคน'),
    ('ไม่มีคนในคลิป — โฟกัสสินค้าล้วน', 'ไม่มีคน — เห็นแต่พื้นที่กับของ'),
    ('มีพรีเซนเตอร์ ถือ/ใช้/รีวิวสินค้า', 'มีคนลงมือจัด/ทำในพื้นที่จริง'),
    ('AI สร้างนาย/นางแบบที่เหมาะกับสินค้าให้', 'AI สร้างคนที่เข้ากับงานนี้ให้'),
    ('AI เลือกนาย/นางแบบให้เหมาะกับสินค้า', 'AI เลือกคนให้เหมาะกับงาน'),
    ('ระบบแนบรูปนี้ให้ตอนวาดภาพและทำวิดีโอ เป็นคนเดิมทุกช็อต ทุกคลิป ทุกรอบผลิต',
     'ระบบแนบรูปนี้ให้ทุกฉาก เป็นคนเดิมตลอดคลิป ทุกรอบผลิต'),
    ('เปิด/ปิดข้อความบนภาพได้ — เปิดแล้วเลือกฟอนต์ที่ใช้ทุกฉาก',
     'สูตรนี้แนะนำ "ไม่มีข้อความ" — ให้ภาพเล่าเอง · เปิดได้ถ้าอยากมีคำโปรย'),
    ('เลือกว่าคลิปมีคนพูดไหม — ถ้ามี ค่อยเลือกเพศเสียงข้างล่าง',
     'มีคนพูดบรรยาย / เงียบ / ASMR (เสียงจากการหยิบจับของ)'),
    ('ไม่ตั้ง = หมีเลือกให้เข้ากับสินค้า · ตั้งฉากไหน มีผลทุกคลิปของรอบนั้น',
     'ค่าเริ่มต้น = บันไดกล้องมาตรฐาน ไวด์ → มีเดียม → โคลสอัพ → มุมพลิ้ว → ปิดสวย · แก้ได้ทุกช่อง'),
    ('สไตล์มีผลตอน "คิดบท" — ถ้าเปลี่ยนหลังผลิตแล้ว ให้กดปุ่มสมองที่สินค้า แล้วกด เริ่มรอบใหม่',
     'สไตล์มีผลตอน "คิดบท" — ถ้าเปลี่ยนหลังผลิตแล้ว ให้กดปุ่มสมองที่งานนั้น แล้วกด เริ่มรอบใหม่'),
    ('ใช้เป็นชื่อไฟล์เซฟ · เว้นว่าง = หมีตั้งจากชื่อสินค้าตัวแรกให้เอง',
     'ใช้เป็นชื่อไฟล์เซฟ · เว้นว่าง = หมีตั้งจากชื่องานแรกให้เอง'),
    ('แต่ละคลิปได้บท/มุมกล้องต่างกัน · สูงสุด 10 คลิป',
     '1 ฉาก = 10 วินาที · ฉากต่อเนื่องกันเป็นเรื่องเดียว (สูงสุด 3 ฉาก = 30 วิ)'),
    ('รูปแรก = รูปหลัก — หมีล็อกรูปทรง สี ฉลาก ตามรูปทุกมุมที่แนบ',
     'รูปแรก = รูปหลัก — หมีล็อกรูปทรง สี วัสดุ ตามรูปที่แนบทุกมุม'),
    ('เช่น SPF50+ เนื้อบางเบา ไม่เหนียว โทนอัพผิว — ยิ่งละเอียด AI ยิ่งเขียนบทได้ตรง',
     'เช่น ชั้นเหล็กพ่นสีขาว 4 ชั้น รับน้ำหนักชั้นละ 8 กก. ประกอบเองได้ — ยิ่งละเอียด บทยิ่งตรง'),
    ('ข้อมูลสินค้า — จุดเด่น / คุณสมบัติ', 'ของหลักที่ใช้ — จุดเด่น / คุณสมบัติ'),
    ('เช่น ครีมกันแดด RACHI', 'เช่น ชั้นวางของ 4 ชั้น / ชุดปลูกผักสลัด'),
    ('เช่น สินค้าเข้าบ้าน ส.ค.', 'เช่น จัดครัวใหม่ ส.ค.'),
    ('เช่น สายมินิมอล เสื้อโทนครีม', 'เช่น สายมินิมอล เสื้อโทนครีม'),
    ('กดครั้งเดียวจบ — บอร์ด + วิดีโอต่อเนื่อง', 'กดครั้งเดียวจบ — เฟรม + วิดีโอทุกฉากต่อเนื่อง'),
    ('เขียนบท → ตรวจ → สร้างภาพ → วิดีโอ', 'เขียนบท → ตรวจ → เฟรมเริ่มฉาก → วิดีโอ'),
    ('ยืนยัน? การ์ด/บอร์ด/วิดีโอชุดนี้จะถูกล้าง', 'ยืนยัน? การ์ด/เฟรม/วิดีโอชุดนี้จะถูกล้าง'),
    ('คลิปที่ {item.clipIndex}/{values.clipsPerProduct}', 'ฉากที่ {item.clipIndex}/{values.clipsPerProduct}'),
    ('บรรยายภาพฉากนี้เป็นภาษาไทย', 'บรรยายภาพจังหวะนี้เป็นภาษาไทย'),
    ('แก้ภาพของคลิปนี้', 'แก้เฟรมเริ่มของฉากนี้'),
    ('ได้ภาพแล้ว — รอวิดีโอ', 'ได้เฟรมแล้ว — รอวิดีโอ'),
    ('บทภาพ (คำสั่งวาด)', 'บทภาพ (คำสั่งวาด)'),
    ('จำนวนคลิป/สินค้า', 'ความยาวคลิป'),
    ('ข้อความบนคลิป (Overlay)', 'ข้อความบนคลิป'),
    ('จัดการสินค้า', 'จัดการงาน'),
    ('บันทึกสินค้า', 'บันทึกงาน'),
    ('เพิ่มสินค้า', 'เพิ่มงาน'),
    ('แก้ไขสินค้า', 'แก้ไขงาน'),
    ('โหลดสินค้า', 'โหลดรายการงาน'),
    ('ชื่อสินค้า *', 'ชื่องาน / ของหลัก *'),
    ('ตัวละครในคลิป', 'คนในคลิป'),
    ('โทนสีคลิป', 'โทน & บรรยากาศแสง'),
    ('รูปสินค้า', 'รูปของหลักที่จะใช้'),
    ('10 วิ / คลิป', '10 วิ / ฉาก'),
    ('รอวาดภาพ', 'รอวาดเฟรม'),
    ('วาดภาพไม่สำเร็จ', 'วาดเฟรมไม่สำเร็จ'),
    ('Gen ภาพใหม่', 'Gen เฟรมใหม่'),
    ('Gen ภาพ', 'Gen เฟรม'),
    ('บอร์ด', 'เฟรม'),
]
SAFE_KEYS = {'label', 'placeholder', 'hint', 'title', 'subtitle', 'confirmText', 'cancelText', 'desc'}

def retext(n):
    """แทนข้อความเฉพาะคีย์ที่ปลอดภัย · 'value' แทนได้เฉพาะตอน el=='text' (option.value = key ของ lookup)"""
    if isinstance(n, dict):
        is_text = n.get('el') == 'text'
        out = {}
        for k, v in n.items():
            if isinstance(v, str) and (k in SAFE_KEYS or (k == 'value' and is_text)):
                for a, b in TXT: v = v.replace(a, b)
                out[k] = v
            else:
                out[k] = retext(v)
        return out
    if isinstance(n, list): return [retext(x) for x in n]
    return n

cfg['phases'] = retext(PH)
PH = cfg['phases']
SETUP, PRODEDIT = PH[0]['form'][0], PH[0]['form'][2]

# ---- 8.2 โทน/บรรยากาศแสง: เปลี่ยนตัวเลือกจากพาสเทล → บรรยากาศแสงจริง ----
STYLE = SETUP['card'][0]['card'][2]
for el in STYLE['card'][0]['card']:
    if el.get('field') == 'svTone':
        el['options'] = [
            {'value': '', 'label': 'อัตโนมัติ', 'icon': 'auto_fix_high'},
            {'value': 'แสงเช้านุ่มๆ', 'label': 'เช้านุ่ม', 'color': '#f2e2c9'},
            {'value': 'แสงสายสว่างสะอาด', 'label': 'สายสว่าง', 'color': '#eef3f6'},
            {'value': 'โทนไม้อุ่น', 'label': 'ไม้อุ่น', 'color': '#d8b98f'},
            {'value': 'ขาวมินิมอลสะอาดตา', 'label': 'ขาวสะอาด', 'color': '#f6f7f8'},
            {'value': 'เขียวธรรมชาติ', 'label': 'เขียวธรรมชาติ', 'color': '#a9c4a0'},
        ]

# ---- 8.3 บล็อกใหม่: สไตล์ภาพ & จังหวะ (svLook / svPace) — แทรกบนสุดของหมวดสไตล์ ----
def head(icon, title, sub):
    return [
        {'el': 'row', 'className': 'items-center gap-2 mt-1', 'style': {'flexWrap': 'nowrap'}, 'card': [
            {'el': 'icon', 'icon': icon, 'textSize': 'text-[18px]',
             'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center'},
            {'el': 'text', 'value': title, 'className': '!text-[17px] min-[640px]:!text-[16px] font-black !text-[var(--ev-text)]'}]},
        {'el': 'text', 'value': sub, 'className': '!text-[14px] min-[640px]:!text-[13px] opacity-60 leading-relaxed mb-1'},
    ]

STYLE['card'].insert(0, {'el': 'box', 'className': 'flex flex-col gap-2', 'card': head(
    'photo_camera_back', 'สไตล์ภาพ & จังหวะ', 'คลิปสายนี้เป็นภาพเหมือนถ่ายจริง — เลือกโทนวัสดุกับความเร็วการเล่า') + [
    {'el': 'grid-select', 'field': 'svLook', 'cols': 3, 'options': [
        {'value': 'สมจริงแบบถ่ายจริง', 'label': 'ถ่ายจริง', 'desc': 'ภาพเหมือนกล้องจริง แสงธรรมชาติ'},
        {'value': 'อบอุ่นโทนไม้', 'label': 'อบอุ่นโทนไม้', 'desc': 'ไม้ ผ้า แสงทองนุ่ม'},
        {'value': 'สว่างสะอาดมินิมอล', 'label': 'สว่างสะอาด', 'desc': 'ขาวโล่ง โปร่ง มินิมอล'}]},
    {'el': 'text', 'value': 'จังหวะการเล่า',
     'className': '!text-[13.5px] min-[640px]:!text-[13px] !text-[var(--ev-text)] opacity-65 uppercase tracking-[0.14em] font-black px-0.5 mt-2 mb-1'},
    {'el': 'grid-select', 'field': 'svPace', 'cols': 2, 'options': [
        {'value': 'ไทม์แลปส์', 'label': 'ไทม์แลปส์', 'desc': 'เร็วแต่ยังดูออกว่าทำอะไร (แนะนำ)'},
        {'value': 'ความเร็วปกติ', 'label': 'ความเร็วปกติ', 'desc': 'เนิบๆ เห็นทุกจังหวะ'}]},
]})

# ---- 8.4 productEdit: บล็อก "พื้นที่ที่จะถ่าย" (รูปพื้นที่ 2 รูป + คำบรรยาย + สภาพก่อน) ----
def find_list(root, probe):
    if isinstance(root, dict):
        for k, v in root.items():
            if isinstance(v, list) and len(v) >= 4 and any(probe in json.dumps(c, ensure_ascii=False) for c in v):
                return root, k
            r = find_list(v, probe)
            if r: return r
    elif isinstance(root, list):
        for c in root:
            r = find_list(c, probe)
            if r: return r
    return None

node, key = find_list(PRODEDIT, '{item.slots.image}')
CARD = node[key]                      # การ์ดหน้าแก้ไขงาน (6 ชิ้น)
gal  = CARD[1]['card'][1]['card']     # ไทล์รูปของหลัก [tile, upload, tile2, upload2, ...]

def reslot(n, new):
    """clone ไทล์/กล่องอัปโหลด แล้วเปลี่ยน slot เป้าหมาย (เฉพาะคีย์ที่ชี้ slot จริง)"""
    n = copy.deepcopy(n)
    def fix(x):
        if isinstance(x, dict):
            for k, v in list(x.items()):
                if k in ('src',) and isinstance(v, str) and v.startswith('{item.slots.'): x[k] = '{item.slots.%s}' % new
                elif k == 'into' and isinstance(v, str): x[k] = new
                elif k == 'to' and x.get('fn') == 'clearSlot': x[k] = new
                elif k == 'when':
                    x[k] = json.loads(re.sub(r'\{item\.slots\.[a-zA-Z0-9]+\}', '{item.slots.%s}' % new,
                                             json.dumps(v, ensure_ascii=False)))
                else: fix(v)
        elif isinstance(x, list):
            for c in x: fix(c)
    fix(n)
    return n

room_tiles = []
for slot, lab in [('room1', 'พื้นที่ 1'), ('room2', 'พื้นที่ 2')]:
    tile = reslot(gal[0], slot)
    tile['card'] = [c for c in tile['card'] if not (c.get('el') == 'box' and 'รูปหลัก' in json.dumps(c, ensure_ascii=False))]
    room_tiles += [tile, reslot(gal[1], slot)]

ROOMBLOCK = {'el': 'box',
    'className': 'bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-2xl p-4 min-[640px]:p-5 flex flex-col gap-3.5',
    'card': [
        {'el': 'row', 'className': 'items-center gap-3.5 mb-2', 'style': {'flexWrap': 'nowrap'}, 'card': [
            {'el': 'box', 'className': 'w-[46px] h-[46px] rounded-2xl bg-[var(--ev-accent)]/[0.12] flex items-center justify-center shrink-0',
             'card': [{'el': 'icon', 'icon': 'home_work', 'textSize': 'text-[22px]',
                       'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center'}]},
            {'el': 'box', 'className': 'flex-1 min-w-0 flex flex-col gap-0.5', 'card': [
                {'el': 'text', 'value': 'พื้นที่ที่จะถ่าย',
                 'className': '!text-[20px] min-[640px]:!text-[19px] font-black !text-[var(--ev-text)] leading-tight'},
                {'el': 'text', 'value': 'แนบรูปพื้นที่จริงได้ = หมีล็อกให้เป็นห้องเดิมทุกฉาก · ไม่มีรูปก็ได้ หมีสร้างพื้นที่ให้จากคำบรรยาย',
                 'className': '!text-[14px] min-[640px]:!text-[13px] opacity-60 leading-relaxed'}]}]},
        {'el': 'box', 'className': 'flex flex-row flex-wrap gap-3 items-stretch', 'card': room_tiles},
        {'el': 'box', 'className': 'flex flex-col gap-2 mt-1', 'card': [
            {'el': 'text', 'value': 'พื้นที่นี้หน้าตาเป็นยังไง',
             'className': '!text-[13.5px] min-[640px]:!text-[13px] !text-[var(--ev-text)] opacity-65 uppercase tracking-[0.14em] font-black px-0.5 mb-2'},
            {'el': 'input', 'field': 'room', 'placeholder': 'เช่น ครัวเล็กผนังขาว ตู้ไม้อ่อน หน้าต่างบานใหญ่ทางซ้าย',
             'className': '!h-14 !px-4 !rounded-xl !text-[19px] min-[640px]:!text-[18px]'}]},
        {'el': 'box', 'className': 'flex flex-col gap-2', 'card': [
            {'el': 'text', 'value': 'สภาพ "ก่อน" เริ่มทำ',
             'className': '!text-[13.5px] min-[640px]:!text-[13px] !text-[var(--ev-text)] opacity-65 uppercase tracking-[0.14em] font-black px-0.5 mb-2'},
            {'el': 'textarea', 'field': 'before', 'placeholder': 'เช่น เคาน์เตอร์ครัวรก จานชามกองรวมกัน ของวางเต็มโต๊ะ',
             'className': '!min-h-[96px] !p-4 !rounded-xl !text-[19px] min-[640px]:!text-[18px] !leading-relaxed'}]},
        {'el': 'box', 'className': 'flex flex-col gap-2', 'card': [
            {'el': 'text', 'value': 'ผลลัพธ์ "หลัง" ที่อยากได้ (ไม่บังคับ)',
             'className': '!text-[13.5px] min-[640px]:!text-[13px] !text-[var(--ev-text)] opacity-65 uppercase tracking-[0.14em] font-black px-0.5 mb-2'},
            {'el': 'input', 'field': 'goal', 'placeholder': 'เช่น ครัวโล่ง หยิบของง่าย ดูสบายตา',
             'className': '!h-14 !px-4 !rounded-xl !text-[19px] min-[640px]:!text-[18px]'}]},
    ]}
CARD.insert(2, ROOMBLOCK)

json.dump(cfg, open(DST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✓ UI pass done →', DST, os.path.getsize(DST), 'bytes')

# ═══════════════════════════════════════════════════════════════
# 9) UI pass 2 — คำที่หลุดรอบแรก (อยู่ใน concat / option label / reason) + ตัวเลือกกล้องสายเล่าเรื่อง
# ═══════════════════════════════════════════════════════════════
TXT2 = [
    ('ติ๊ก "ใช้" = สินค้าที่จะผลิตคลิป · ปิด = ข้าม · สินค้าต้องมีรูปจริงถึงเข้าคิวผลิต',
     'ติ๊ก "ใช้" = งานที่จะผลิตคลิป · ปิด = ข้าม · งานต้องมีรูปของหลักถึงเข้าคิวผลิต'),
    ('ต้องการลบ "{item.name}" ออกจากลิสต์สินค้าใช่ไหม? การลบนี้กู้คืนไม่ได้',
     'ต้องการลบ "{item.name}" ออกจากลิสต์งานใช่ไหม? การลบนี้กู้คืนไม่ได้'),
    ('ข้อมูลสินค้า (ช่องรุ่นเก่า — บทยังอ่านค่านี้อยู่ ย้ายข้อความไปช่องใหม่ได้เลย)',
     'ข้อมูลเพิ่มเติม (ช่องรุ่นเก่า — บทยังอ่านค่านี้อยู่ ย้ายข้อความไปช่องใหม่ได้เลย)'),
    ('เปลี่ยนได้ทุกเมื่อ — มีผลกับวิดีโอที่สร้างใหม่ · ถ้าบทเดิมลงท้ายไม่ตรงเสียง ให้กด "คิดบทใหม่" ที่การ์ดสินค้าก่อน',
     'เปลี่ยนได้ทุกเมื่อ — มีผลกับวิดีโอที่สร้างใหม่ · ถ้าบทเดิมลงท้ายไม่ตรงเสียง ให้กด "คิดบทใหม่" ที่การ์ดงานก่อน'),
    ('พร้อมผลิต — กดปุ่มด้านขวา หรือจัดการรายคลิปข้างล่าง', 'พร้อมผลิต — กดปุ่มด้านขวา หรือจัดการรายฉากข้างล่าง'),
    ('ครบทุกคลิปแล้ว — ไปดูผลงานที่คลังคลิปได้เลย', 'ครบทุกฉากแล้ว — ไปดูผลงานที่คลังคลิปได้เลย'),
    ('ยังไม่มีคลิปเสร็จ — กลับไปหน้าผลิตเพื่อสร้างวิดีโอ', 'ยังไม่มีคลิปเสร็จ — กลับไปหน้าผลิตเพื่อสร้างวิดีโอ'),
    ('เพิ่ม/ติ๊กใช้สินค้า + ใส่รูปให้ครบก่อน', 'เพิ่ม/ติ๊กใช้งาน + ใส่รูปของหลักให้ครบก่อน'),
    ('ทุกสินค้าที่ใช้ต้องมีรูปก่อน', 'ทุกงานที่ใช้ต้องมีรูปของหลักก่อน'),
    ('ยังไม่มีสินค้า — กดเพิ่มงานใหม่ข้างล่าง', 'ยังไม่มีงาน — กดเพิ่มงานใหม่ข้างล่าง'),
    ('ได้ตัวละครแล้ว — ล็อกหน้าตามรูปนี้', 'ได้คนในคลิปแล้ว — ล็อกหน้าตามรูปนี้'),
    (' สินค้า × {values.clipsPerProduct} คลิป', ' งาน × {values.clipsPerProduct} ฉาก'),
    ('[{values.clipsPerProduct} คลิป]', '[{values.clipsPerProduct} ฉาก]'),
    ('เลือกให้เหมาะกับสินค้า', 'เลือกให้เหมาะกับงาน'),
    ('สินค้าทั้งหมด', 'งานทั้งหมด'),
    ('ค้นหาสินค้า…', 'ค้นหางาน…'),
    ('ลบสินค้านี้?', 'ลบงานนี้?'),
    ('ใช้สินค้านี้', 'ใช้งานนี้'),
    ('เซฟสินค้า', 'เซฟงาน'),
    ('ไม่มีตัวละคร', 'ไม่มีคน'),
    ('มีตัวละคร', 'มีคนในคลิป'),
    ('สุ่มตัวละคร', 'ให้ AI เลือกคน'),
    ('ใช้รูปตัวละคร', 'ใช้รูปหน้าที่แนบ'),
    ('คลิป — ', 'ฉาก — '),
    ('สินค้า', 'งาน'),
]
SAFE2 = SAFE_KEYS | {'reason'}

def retext2(n, in_text=False):
    if isinstance(n, dict):
        is_text = n.get('el') == 'text'
        out = {}
        for k, v in n.items():
            if k == 'when' or k == 'field':                     # 🚫 predicate/lookup key — ห้ามแตะ
                out[k] = v
            elif isinstance(v, str) and (k in SAFE2 or (k == 'value' and (is_text or in_text))):
                for a, b in TXT2: v = v.replace(a, b)
                out[k] = v
            elif k in ('value', 'parts') and (is_text or in_text):
                out[k] = retext2(v, True)
            else:
                out[k] = retext2(v, in_text)
        return out
    if isinstance(n, list): return [retext2(x, in_text) for x in n]
    if isinstance(n, str) and in_text:
        for a, b in TXT2: n = n.replace(a, b)
    return n

cfg['phases'] = retext2(cfg['phases'])

# ---- 9.1 ตัวเลือกมุมกล้อง / การนำเสนอ = บันไดช็อตของ bible §5 (value = วลีที่ interpolate ลง prompt ตรง) ----
CAM_OPTS = [
    {'value': '', 'label': 'อัตโนมัติ — AI เลือกให้', 'icon': 'auto_awesome'},
    {'value': 'ไวด์เห็นพื้นที่ทั้งหมด (wide establishing)', 'label': 'ไวด์เห็นพื้นที่ทั้งหมด'},
    {'value': 'มีเดียมเห็นคนกำลังทำ (medium action)', 'label': 'มีเดียมเห็นคนกำลังทำ'},
    {'value': 'โคลสอัพมือกับของ (close-up hands)', 'label': 'โคลสอัพมือกับของ'},
    {'value': 'มุม 45 องศา (45-degree angle)', 'label': 'มุม 45 องศา'},
    {'value': 'แทร็กกิ้งเลื่อนตาม (tracking shot)', 'label': 'แทร็กกิ้งเลื่อนตาม'},
    {'value': 'ท็อปดาวน์มองจากด้านบน (overhead)', 'label': 'ท็อปดาวน์มองจากบน'},
    {'value': 'ดันเข้าใกล้ช้าๆ (slow push-in)', 'label': 'ดันเข้าใกล้ช้าๆ'},
    {'value': 'แพนช้าๆ (slow pan)', 'label': 'แพนช้าๆ'},
    {'value': 'มาโครใกล้มาก (extreme macro)', 'label': 'มาโครใกล้มาก'},
    {'value': 'ไวด์ปิดท้ายเห็นผลลัพธ์ (final beauty)', 'label': 'ไวด์ปิดท้ายเห็นผลลัพธ์'},
]
PRES_OPTS = [
    {'value': '', 'label': 'อัตโนมัติ — AI เลือกให้', 'icon': 'auto_awesome'},
    {'value': 'เห็นพื้นที่ทั้งหมดก่อนลงมือ', 'label': 'เห็นพื้นที่ก่อนลงมือ'},
    {'value': 'คนถือของเดินเข้ามาในเฟรม', 'label': 'คนถือของเดินเข้ามา'},
    {'value': 'มือกำลังจัด/วางของเข้าที่', 'label': 'มือกำลังจัดของเข้าที่'},
    {'value': 'โคลสอัพวัสดุและดีเทลของ', 'label': 'โคลสอัพวัสดุ/ดีเทล'},
    {'value': 'ของเข้าที่แล้ว เห็นความเป็นระเบียบ', 'label': 'ของเข้าที่ เป็นระเบียบ'},
    {'value': 'เห็นคนใช้งานพื้นที่ที่จัดเสร็จ', 'label': 'คนใช้งานพื้นที่ที่เสร็จ'},
]
def swap_opts(n):
    if isinstance(n, dict):
        f = n.get('field', '')
        if (f.startswith('svCam') or (f.startswith('cam') and f[3:].isdigit())) and 'options' in n:
            n['options'] = copy.deepcopy(CAM_OPTS)
        elif f.startswith('svPres') and 'options' in n: n['options'] = copy.deepcopy(PRES_OPTS)
        for v in n.values(): swap_opts(v)
    elif isinstance(n, list):
        for v in n: swap_opts(v)
swap_opts(cfg['phases'])

# default svCam ต้องตรง option value เป๊ะ ไม่งั้น dropdown โชว์ placeholder (กับดักที่ minimal เคยเจอ)
V['svCam1'] = 'ไวด์เห็นพื้นที่ทั้งหมด (wide establishing)'
V['svCam2'] = 'มีเดียมเห็นคนกำลังทำ (medium action)'
V['svCam3'] = 'โคลสอัพมือกับของ (close-up hands)'
V['svCam4'] = 'มุม 45 องศา (45-degree angle)'
V['svCam5'] = 'ไวด์ปิดท้ายเห็นผลลัพธ์ (final beauty)'

json.dump(cfg, open(DST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✓ UI pass 2 done →', DST, os.path.getsize(DST), 'bytes')

# ═══════════════════════════════════════════════════════════════
# 10) คลังคลิป — บล็อก "คลิปเต็ม" (ต่อทุกฉากเป็นไฟล์เดียวด้วย op merge)
# ═══════════════════════════════════════════════════════════════
TXT3 = [('Gen ภาพทั้งหมด', 'Gen เฟรมทั้งหมด'), ('ลองใหม่ที่พลาด · ', 'ลองใหม่ที่พลาด · '), (' คลิป', ' ฉาก')]
def retext3(n, in_text=False):
    if isinstance(n, dict):
        is_text = n.get('el') in ('text', 'md') or n.get('el', '').endswith('button') or n.get('el') == 'gen-phase'
        out = {}
        for k, v in n.items():
            if k in ('when', 'field', 'where'): out[k] = v
            elif k == 'label' and isinstance(v, str):
                for a, b in TXT3: v = v.replace(a, b)
                out[k] = v
            elif k in ('label', 'value', 'parts') and (is_text or in_text): out[k] = retext3(v, True)
            else: out[k] = retext3(v, in_text)
        return out
    if isinstance(n, list): return [retext3(x, in_text) for x in n]
    if isinstance(n, str) and in_text:
        for a, b in TXT3: n = n.replace(a, b)
    return n
cfg['phases'] = retext3(cfg['phases'])

GAL = cfg['phases'][0]['form'][4]
def find_parent_of(root, pred):
    if isinstance(root, dict):
        for k, v in root.items():
            if isinstance(v, list):
                for i, c in enumerate(v):
                    if isinstance(c, dict) and pred(c): return v, i
            r = find_parent_of(v, pred)
            if r: return r
    elif isinstance(root, list):
        for c in root:
            r = find_parent_of(c, pred)
            if r: return r
    return None

def has_task_repeat(x):
    return json.dumps(x, ensure_ascii=False).find('"coll": "tasks"') >= 0 and x.get('el') == 'box'
lst, idx = find_parent_of(GAL, has_task_repeat)

HAS_VIDEO = {'op': 'gt', 'a': {'op': 'count', 'from': 'tasks', 'slot': 'video'}, 'b': 0}
FULLBLOCK = {'el': 'box',
  'className': 'bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-2xl p-4 min-[640px]:p-5 flex flex-col gap-3.5 mb-4',
  'when': HAS_VIDEO,
  'card': [
    {'el': 'row', 'className': 'items-center gap-3.5', 'style': {'flexWrap': 'nowrap'}, 'card': [
        {'el': 'box', 'className': 'w-[46px] h-[46px] rounded-2xl bg-[var(--ev-accent)]/[0.12] flex items-center justify-center shrink-0',
         'card': [{'el': 'icon', 'icon': 'movie', 'textSize': 'text-[22px]',
                   'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center'}]},
        {'el': 'box', 'className': 'flex-1 min-w-0 flex flex-col gap-0.5', 'card': [
            {'el': 'text', 'value': 'คลิปเต็ม — ต่อทุกฉากแล้ว',
             'className': '!text-[20px] min-[640px]:!text-[19px] font-black !text-[var(--ev-text)] leading-tight'},
            {'el': 'text', 'value': 'กดปุ่มนี้เพื่อต่อฉากทั้งหมดของแต่ละงานเป็นไฟล์เดียว พร้อมโพสต์',
             'className': '!text-[14px] min-[640px]:!text-[13px] opacity-60 leading-relaxed'}]}]},
    {'el': 'gen-phase', 'ops': ['stMerge'], 'icon': 'call_merge', 'variant': 'solid',
     'label': 'ต่อฉากเป็นคลิปเดียว',
     'className': ('w-full justify-center !h-16 min-[640px]:!h-14 !rounded-2xl !text-[18px] min-[640px]:!text-[17px] '
                   'font-bold !bg-[var(--ev-accent)] !text-white transition-all hover:-translate-y-0.5 active:translate-y-0')},
    {'el': 'box', 'className': 'flex flex-row flex-wrap gap-3 items-stretch', 'card': [
      {'el': 'repeat', 'coll': 'products', 'where': 'slots.full!=', 'card': [
        {'el': 'box', 'className': 'relative group flex flex-col w-[150px] min-[560px]:w-[190px]', 'card': [
          {'el': 'media-slot', 'src': '{item.slots.full}', 'aspect': '9:16',
           'style': {'borderRadius': '18px'}, 'className': 'ring-1 ring-[var(--ev-border)]'},
          {'el': 'row', 'style': {'flexWrap': 'nowrap'},
           'className': ('absolute bottom-0 left-0 right-0 z-10 items-center gap-1.5 px-2.5 pb-2 pt-7 rounded-b-[18px] '
                         'bg-gradient-to-t from-black/70 to-transparent pointer-events-none'),
           'card': [{'el': 'text', 'value': '{item.name}',
                     'className': '!text-[12.5px] font-bold truncate !text-white shrink min-w-0'}]},
          {'el': 'box', 'className': ('absolute inset-0 z-20 rounded-[18px] bg-black/45 opacity-0 group-hover:opacity-100 '
                                      'transition flex flex-col justify-end gap-2 p-2.5 pointer-events-none'),
           'card': [{'el': 'download-button', 'to': '{item.slots.full}', 'label': 'ดาวน์โหลดคลิปเต็ม', 'icon': 'download',
                     'variant': 'solid',
                     'className': ('justify-center !h-10 !rounded-xl !text-[13px] font-bold w-full !pointer-events-auto '
                                   '!bg-[var(--ev-accent)] !text-white')}]}]}]}]},
  ]}
lst.insert(idx, FULLBLOCK)

json.dump(cfg, open(DST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✓ gallery full-clip block →', DST, os.path.getsize(DST), 'bytes')

# ── 11) หน่วยของ stepper: "คลิป" → "ฉาก" (text ยืนเดี่ยว รอบก่อนไม่โดน) ──
def fix_unit(n):
    if isinstance(n, dict):
        if n.get('el') == 'text' and n.get('value') == 'คลิป': n['value'] = 'ฉาก'
        for v in n.values(): fix_unit(v)
    elif isinstance(n, list):
        for v in n: fix_unit(v)
fix_unit(cfg['phases'])
json.dump(cfg, open(DST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✓ final →', DST, os.path.getsize(DST), 'bytes')
