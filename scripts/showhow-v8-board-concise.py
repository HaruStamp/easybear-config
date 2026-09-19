#!/usr/bin/env python3
# showhow-v8-board-concise.py — เขียน prompt สตอรีบอร์ด mnBoard..mnBoard6 ใหม่จากแม่แบบเดียว "สั้นแต่ครบ" (พี่หมีสั่ง 2026-09-19)
# ที่มา: audit 11,610 prompt (easybear-showhow/docs/qa/2026-09-19-board-audit) ถูกตามแบบ 100% แต่อ่านด้วยตาเจอ 4 จุด:
#   ① บอร์ด 3-5 ไม่มีกติกาต่อเนื่อง/ห้ามลอกช่อง ทั้งที่ได้บอร์ดอื่นเป็น ref (40-60 วิ)
#   ② "ท้ายทุกภาพ: \"Realistic Home Documentary, 4K…\"" กำกวม — อาจถูกวาดเป็นป้ายอังกฤษบนแผง
#   ③ โหมด ASMR/ไม่มีพากย์ ข้อความเสียงซ้ำ 5 แถว (~225 ตัว) ไม่ได้ข้อมูลเพิ่ม
#   ④ ซับว่าง → `Overlay: ""` (สลับโหมดซับหลังสร้างบท)
# หลักการเขียน: ของสำคัญก่อน · 1 เรื่อง 1 บรรทัด · ไม่ซ้ำ · ไม่มีข้อความที่โมเดลต้องเดาว่าจะวาดหรือไม่ · กฎเงื่อนไขทุกข้อยังผูกกับตัวเลือก/รูปจริงเหมือนเดิม
import json, os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'showhow-dev.json')
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)

def eq(a, b): return {'op': 'eq', 'a': a, 'b': b}
def neq(a, b): return {'op': 'not', 'a': eq(a, b)}
def AND(*xs): return {'op': 'and', 'list': list(xs)}
def block(*pairs): return {'op': 'block', 'sep': '', 'parts': [{'when': w, 'value': v} for w, v in pairs]}
SUB, TITLE, NOTEXT = 'ซับไตเติ้ลรายฉาก', 'หัวเรื่องตอนเปิด', 'ไม่มีข้อความ'
VO_ON = AND(neq('{values.svAudio}', 'ไม่มีเสียงพากย์'), neq('{values.svAudio}', 'ASMR'))

def prompt_for(k):
    first, last = 5 * (k - 1) + 1, 5 * k
    head = 'ภาพเดียว = เอกสารสตอรีบอร์ดดิจิทัลแนวตั้ง ของคลิป "ทำให้ดู" เรื่อง "{item.productName}"'
    parts = [head]
    if k == 1:
        parts.append(block(('values.svSec>10', ' · ช่วงที่ 1 ของคลิป — ฉาก 1 ถึง 5')))
    else:
        parts.append(f' · ช่วงที่ {k} ของคลิป — ฉาก {first} ถึง {last}')
    # v8.7: A/C/F ใส่หัวเรื่องเหนือตารางเอง (สะกดไทยเพี้ยน) · B แปลมุมกล้องเป็นอังกฤษ ⇒ แถวหัวคอลัมน์บนสุด ไม่มีหัวเรื่อง · มุมกล้องภาษาไทยตามบท
    # v8.6 (วาดจริง 11 use case): หัวคอลัมน์หลุดอังกฤษ/"(เล็ก)"/เลข ①-④ กลายเป็นเลขแถว · ตารางในกรอบแท็บเล็ต · ภาพซ้ำหลายคอลัมน์ · กล้องนิ่งกลายเป็นโคลสอัพ · ช่องเสียง ASMR เป็นคำมั่ว
    #   ⇒ บอกคำหัวคอลัมน์ตรง ๆ · ไม่มีสัญลักษณ์ ①-④ · ห้ามกรอบอุปกรณ์ · ภาพอยู่คอลัมน์ภาพเท่านั้น · ระยะภาพตามมุมกล้อง · บอกว่าช่องเสียงเขียนอะไร
    parts.append(f'\nบังคับเลย์เอาต์: ตาราง 5 แถว × 4 คอลัมน์ เต็มภาพชิดขอบ เส้นแบ่งชัด (ไม่ใช่ภาพถ่ายกระดาษ/สมุด ไม่มีกรอบแท็บเล็ตหรือมือถือรอบนอก) · แถวหัวคอลัมน์อยู่บนสุด ไม่มีหัวเรื่องเหนือตาราง · 1 แถว = 1 ฉาก เรียงบนลงล่าง ครบ {first}-{last} · ภาพถ่ายอยู่คอลัมน์ "ภาพ" ช่องละ 1 ภาพเท่านั้น คอลัมน์อื่นเป็นตัวหนังสือล้วน'
                 '\nหัวคอลัมน์พิมพ์ 4 คำนี้เท่านั้น: "ฉาก" · "ภาพ" · "มุมกล้อง" · "')
    parts.append(block((VO_ON, 'บทพากย์'), (eq('{values.svAudio}', 'ASMR'), 'เสียงในฉาก'),
                       (eq('{values.svAudio}', 'ไม่มีเสียงพากย์'), 'เสียงบรรยากาศ')))
    parts.append('" · คอลัมน์ฉาก = ป้ายต้นบรรทัดของแถวนั้นคัดเป๊ะ · คอลัมน์มุมกล้อง = มุมกล้องของแถว (ภาษาไทยตามบท) · คอลัมน์เสียง = ')
    parts.append(block((VO_ON, 'บทพากย์ของแถว (แถวไหนไม่มี เว้นว่าง)'), (neq('{values.svAudio}', 'มีเสียงพากย์'), 'เสียงสั้น 2-4 คำจากแอ็กชันของแถว ไม่มีบทพูด')))
    parts.append(' · ตัวหนังสือทุกช่องเป็นภาษาไทย'
                 '\nภาพในคอลัมน์ภาพ: ภาพถ่ายสมจริงสไตล์สารคดีในบ้าน แสง {item.palette} · ระยะภาพตรงตามมุมกล้องของแถว (มุมกว้าง = เห็นทั้งพื้นที่) · ทุกช่องสถานที่เดียวกัน ของที่งานไม่ได้แตะคงที่'
                 '\nถ้ามีบอร์ดช่วงอื่นแนบมา (รูปท้าย ๆ): ใช้โทน แสง ฉากหลัง ฟอนต์ชุดเดียวกัน แต่ห้ามลอกภาพในช่อง')
    parts.append(block(({'op': 'refsFilled', 'key': 'prod', 'from': 'products', 'slot': 'image'},
                        '\nสินค้า = ของจริงตามรูปที่แนบ (หลายชิ้น = ชิ้นละรูป): ห้ามเปลี่ยนสี ทรง สัดส่วน ฉลาก โลโก้ จำนวน ห้ามวาดใหม่หรือเป็นการ์ตูน · มุมที่รูปไม่มีให้ใช้มุมใกล้สุด · เอาเฉพาะตัวสินค้า ห้ามลอกฉากหลัง ของประกอบ หรือข้อความโฆษณาจากรูป')))
    parts.append(block(({'op': 'refsFilled', 'key': 'prod', 'from': 'products', 'slot': 'room1'},
                        '\nสถานที่ = ห้องตามรูปที่แนบ (ผนัง พื้น เฟอร์นิเจอร์ หน้าต่าง ทิศแสง) เปลี่ยนได้เฉพาะผลของงาน · ช่องแรก = สภาพตามรูป')))
    parts.append('\nคน: ')
    parts.append({'op': 'lookup', 'table': 'charBoard', 'key': '{values.svChar}|{values.svCharSrc}', 'fallback': ''})
    COLOR = ' · หัวข้อตัวอักษรสีเข้มที่เข้ากับโทนสีของคลิป'
    title_txt = 'เฉพาะแถวแรกตามข้อความที่บทให้ (หัวเรื่อง) บรรทัดเดียว ฟอนต์ {values.svText}' + COLOR + ' · แถวอื่นภาพล้วน' if k == 1 else 'ไม่มี — ภาพล้วนทุกช่อง'
    parts.append('\nตัวหนังสือบนภาพ: ')
    parts.append(block((f'values.svTextOn={SUB}', 'ใช้ข้อความที่บทให้ไว้ในแต่ละแถวเท่านั้น (แถวไหนไม่มี = ภาพล้วน ห้ามแต่งเอง) บรรทัดเดียว ฟอนต์ {values.svText}' + COLOR + ' ไม่ทับจุดที่กำลังทำ'),
                       (f'values.svTextOn={TITLE}', title_txt),
                       (f'values.svTextOn={NOTEXT}', 'ไม่มี — ภาพล้วนทุกช่อง (ยกเว้นฉลากจริงบนสินค้า)')))
    parts.append(' · ห้ามพิมพ์ภาษาอังกฤษ ชื่อสไตล์ แบรนด์ที่ไม่ได้แนบ หรือ emoji ลงบนแผง\n\nรายการแถว (ป้ายฉากต้นบรรทัดคัดเป็นภาษาไทยตามนี้ ห้ามแปล):')
    for n in range(first, last + 1):
        parts.append({'op': 'concat', 'parts': ['\n', {'op': 'lookup', 'table': 'sceneLab', 'key': '{values.svSec}|' + str(n), 'fallback': f'{n}. ฉาก {n}'},
                                                 ' — {item.s%dth} · มุมกล้อง: {item.cam%d}' % (n, n)]})
        ov_mode = eq('{values.svTextOn}', SUB) if not (k == 1 and n == 1) else neq('{values.svTextOn}', NOTEXT)
        parts.append(block((AND(ov_mode, neq('{item.ov%d}' % n, '')), ' · ข้อความ: "{item.ov%d}"' % n)))
        parts.append(block((AND(VO_ON, neq('{item.vo%d}' % n, '')), ' · พากย์: "{item.vo%d}"' % n)))
    return {'op': 'concat', 'parts': parts}

boards = {}
def walk(n):
    if isinstance(n, dict):
        if str(n.get('id', '')).startswith('mnBoard') and n.get('type') == 'image': boards[n['id']] = n
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)
walk(d)
assert sorted(boards) == ['mnBoard'] + [f'mnBoard{k}' for k in range(2, 7)], sorted(boards)
for k in range(1, 7):
    boards['mnBoard' if k == 1 else f'mnBoard{k}']['prompt'] = prompt_for(k)
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print('✓ v8 board-concise · เขียน prompt ใหม่ 6 บอร์ด ·', os.path.getsize(P), 'bytes')
