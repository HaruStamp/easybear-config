#!/usr/bin/env python3
# showhow-v5.py — รอบเก็บของที่เหลือจากเอกสารมาตรฐาน (อ่านครบ 247 หัวข้อแล้ว)
#   เติม: ACTION INVENTORY · STATE→ACTION→NEW STATE · VIDEO RHYTHM · ACTION PHASES ·
#         SATISFYING PATTERNS · HAND-OBJECT 6 ข้อ · DECORATION RESTRAINT · NEGATIVE SPACE ·
#         STYLE BALANCE · LIGHTING CONTINUITY · STORAGE PRODUCT PATTERN · VIDEO END RULE
import json, os

P = '/Users/tammaster/Desktop/Dev/bear-clan/easybear-config/showhow.json'
cfg = json.load(open(P, encoding='utf-8'))
OPS = {o['id']: o for o in cfg['ops']}
sys = cfg['brain']['sh']['sys']

# ═══════ A) วิธีคิดก่อนแบ่งฉาก (§109/§110/§111) — แทรกก่อน "ชั้นที่ 1" ═══════
METHOD = """
═══ ขั้นที่ 0 · วิธีคิดก่อนลงมือเขียน (ทำในหัว ห้ามพิมพ์ออกมา) ═══

**1. ลิสต์แอ็กชันทั้งหมดก่อน** — ไล่ว่างานนี้ต้องทำอะไรบ้างตั้งแต่ต้นจนจบ เป็นข้อ ๆ
   ตัวอย่าง: เก็บของออกจากเคาน์เตอร์ · ยกชั้นเข้ามา · วางชั้น · ปรับให้ตรง · ยกไมโครเวฟ · วางไมโครเวฟ · ใส่จาน · ใส่ชาม · เรียงแก้ว · เช็ดเคาน์เตอร์ · เผยผลลัพธ์
**2. จับกลุ่มแอ็กชันตาม "เป้าหมายการเปลี่ยนแปลง"** — 1 กลุ่ม = 1 ฉาก
   ตัวอย่าง: [ติดตั้งชั้น] [วางเครื่องใช้ไฟฟ้า] [จัดจานและเก็บงาน]
**3. เขียนแต่ละฉากเป็นสคริปต์การกระทำ** `สภาพเดิม → การกระทำ → สภาพใหม่`
   ตัวอย่าง: เคาน์เตอร์โล่ง → วางชั้นเข้าที่ → มีโครงเก็บของแล้ว
**4. ถ้าแตกหน่วยที่ไม่ซ้ำกันได้ไม่ถึงจำนวนฉากที่ขอ ให้ลดจำนวนฉากลง** อย่ายืดเรื่อง
"""
sys = sys.replace("═══ ชั้นที่ 1 · อาร์คของเรื่อง ═══", METHOD.strip() + "\n\n═══ ชั้นที่ 1 · อาร์คของเรื่อง ═══", 1)

# ═══════ B) จังหวะ 5 beat + เฟสการเคลื่อนไหว (§59/§58) — เสริมในชั้นที่ 3 ═══════
RHYTHM = """
**จังหวะมาตรฐานของ 5 จังหวะในหนึ่งฉาก** (ใช้เป็นค่าตั้งต้น):
`แอ็กชันใหญ่ → แอ็กชันกลาง → ดีเทลเล็ก → ดีเทลเล็ก → ปิดด้วยผลของฉากนั้น`
ตัวอย่าง: ยกชั้นเข้ามา → วางไมโครเวฟ → ใส่แก้วเข้าช่อง → จัดช้อนให้ตรงแนว → เห็นมุมที่เพิ่งจัดเสร็จ

**เฟสของการเคลื่อนไหวที่ต้องเห็นครบ** (ห้ามข้ามไปเป็นวาร์ป):
`ตั้งท่า → เอื้อมเข้าไป → สัมผัสของ → เคลื่อนย้าย → วางลง → ปล่อยมือ`

**แพตเทิร์นที่ทำให้ดูแล้วสะใจ** — เลือกใช้ให้เข้ากับงาน: รก→เข้าแถว · ว่าง→เต็ม · เปิด→ใส่→ปิด · กระจัดกระจาย→แยกหมวด · สกปรก→สะอาด · ยับ→เรียบ

**ช็อตโคลสอัพมือ ต้องบอกครบ 6 อย่างใน s*en**: มือไหนทำ · แตะตรงไหนของของ · มืออีกข้างทำอะไร · เคลื่อนไหวยังไง · ของไปจบที่ไหน · ปล่อยมือเมื่อไหร่
ตัวอย่าง: "Her left hand steadies the rack while her right hand lifts one plate and slides it vertically into an empty slot, releasing only after the rack fully supports it."
"""
sys = sys.replace("═══ ท่าเปิดคลิป (hook)", RHYTHM.strip() + "\n\n═══ ท่าเปิดคลิป (hook)", 1)

# ═══════ C) กฎภาพ/สไตล์ที่ยังขาด (§47/§48/§52/§54) + สูตรของหลักตามชนิด (§28-32) ═══════
STYLE = """
═══ กฎภาพที่ห้ามพลาด (ตัวคุมไม่ให้ AI ใส่ของมั่ว) ═══

**ห้ามเติมของแต่งเอง** — ต้นไม้ ดอกไม้ รูปแขวน โคมไฟ หมอน เทียน ของประดับ พรม **ห้ามใส่** ถ้าผู้ใช้ไม่ได้ระบุหรือมันไม่ได้ช่วยเล่าการเปลี่ยนแปลง · ของทุกชิ้นในเฟรมต้องมีเหตุผลว่าทำไมอยู่ตรงนั้น

**เว้นที่ว่าง** — ห้ามยัดของเต็มทุกชั้นทุกผิวหน้า · ต้องเหลือที่ว่างพอให้ของหลักอ่านออก แอ็กชันชัด และห้องดูแพง

**สมดุลของสไตล์** — ต้องเป็น "บ้านจริง + จัดเป็นระเบียบน่าอิจฉา + คุณภาพงานโฆษณา"
ห้ามเป็น: โชว์รูมหรูเกินจริง · สถาปัตยกรรมแฟนตาซี · เรนเดอร์ 3D แข็ง ๆ ว่างเปล่า · ภาพแคตตาล็อกจัดเกินจริง

**ล็อกทิศแสง** — กำหนดทิศแสงหลักครั้งเดียว (เช่น "หน้าต่างอยู่ซ้าย แสงเข้าจากซ้าย") แล้วต้องเหมือนกันทุกฉากทุกจังหวะ ห้ามสลับทิศ

**ความลึกของภาพ** — ใช้ ฉากหน้า → ตัวแบบ → ฉากหลัง เมื่อช่วยให้ภาพอ่านง่ายขึ้น (เช่น ฉากหน้า=ขอบเคาน์เตอร์ · ตัวแบบ=มือกำลังวางจาน · ฉากหลัง=ครัวที่จัดแล้ว)

**เฟรมสุดท้ายของคลิป** — กล้องนิ่ง · พื้นที่เสร็จสมบูรณ์ · เห็นของหลักชัด · แสงสมจริง · **ห้ามมีแอ็กชันใหญ่ใหม่**

═══ สูตรตามชนิดของหลัก (ถ้ามีของหลัก) ═══
โครงร่วม: นำของเข้ามา → วางให้เข้าที่ → เห็นโครงสร้างของมัน → ใส่ของที่เกี่ยวข้องลงไป → เผยว่ามันถูกใช้งานจริง
- **ชั้น/แร็ค/ราวแขวน** — ใส่ของที่ชั้นนั้นรับได้จริงเท่านั้น ห้ามเพิ่มฟังก์ชันที่ของไม่มี
- **ที่คว่ำจาน** — จาน ชาม แก้ว ช้อนส้อม ตามช่องที่มีจริงในรูป
- **ชั้นวางเครื่องใช้ไฟฟ้า** — ไมโครเวฟ หม้อหุงข้าว กาต้มน้ำ เครื่องชงกาแฟ เท่าที่พื้นที่จริงรับได้
- **ตู้** — เปิดตู้ → วางของ → จัดเรียง → ปิด/แง้ม → เผยผลลัพธ์
- **กล่องเก็บของ** — เห็นของที่ยังไม่แยก → แยกหมวด → เปิดกล่อง → ใส่ตามหมวด → จัดให้ตรง → ปิด/เลื่อนเก็บ
"""
sys = sys.replace("═══ กฎการเขียนแต่ละฟิลด์ ═══", STYLE.strip() + "\n\n═══ กฎการเขียนแต่ละฟิลด์ ═══", 1)
cfg['brain']['sh']['sys'] = sys

# ═══════ D) prompt วิดีโอ — เติมกฎภาพ + ปิดท้าย (§21/§22/§52/§53/§108) ═══════
vd = OPS['shVideo']['prompt']['parts']
vd[0] = vd[0].replace(
    'Realistic human motion, correct hand anatomy',
    'Lock the primary light direction for the whole clip — daylight must enter from the same side in every shot, never reversed.\n'
    'Use depth when useful: foreground / subject / background. Leave believable negative space — do not fill every surface.\n'
    'Do NOT add decorative objects that were not requested (plants, flowers, artwork, lamps, cushions, candles, ornaments, rugs).\n'
    'Style balance: a real lived-in home, aspirationally organized, with commercial polish — never a luxury showroom, never a sterile 3D render, never an over-decorated catalog shot.\n\n'
    'Realistic human motion, correct hand anatomy')
# กฎเฟรมสุดท้าย + เฟสการเคลื่อนไหว → ต่อท้ายบล็อก negative
for i, p in enumerate(vd):
    if isinstance(p, str) and p.lstrip().startswith('Negative:'):
        vd[i] = (p.rstrip() +
                 '\n\nPhysical actions must show their full phases — start pose, approach, contact, movement, placement, release. '
                 'Never replace movement with teleportation, never let objects fuse into hands or pass through each other.'
                 '\nEnd the clip on a stable camera showing the completed space with the hero object clearly visible — no new major action in the final seconds.')
        break

# ═══════ E) prompt เฟรม — decoration restraint + negative space + ทิศแสง ═══════
fr = OPS['shFrame']['prompt']['parts']
fr[0] = fr[0].replace(
    'ล็อกสถานที่:',
    'ห้ามเติมของแต่งที่ไม่ได้ระบุ (ต้นไม้ ดอกไม้ รูปแขวน โคมไฟ หมอน เทียน พรม ของประดับ) · เว้นที่ว่างให้พอ ห้ามยัดของเต็มทุกผิวหน้า · '
    'ทิศแสงต้องเหมือนกันทุกฉาก ห้ามสลับข้าง · เป็นบ้านจริงที่จัดเป็นระเบียบ ไม่ใช่โชว์รูมหรูหรือภาพเรนเดอร์แข็ง ๆ\n\n'
    'ล็อกสถานที่:')

json.dump(cfg, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
s2 = cfg['brain']['sh']['sys']
print('✓ v5 →', os.path.getsize(P), 'bytes · brain.sh.sys', len(s2), 'ตัวอักษร', len(s2.split('\n')), 'บรรทัด')
