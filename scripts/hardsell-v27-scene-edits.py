# hardsell-dev v27: แก้บทฉากแล้วต้องมีผลกับวิดีโอ (เจ้าของสั่ง 26 พ.ย. ข้อ D)
# ต้นเหตุ: v22 (2026-10-18) ถอด "Scenes in order" (s1en-s4en) ออกจาก mnVideo/mnVideo2 เพราะ 4 ฉากใน 8 วิ
#   ทำให้สินค้าถูกจับเปิด/หมุนจนเพี้ยน (A/B docs/qa/2026-10-17-ab-v22 ยืนยันว่าฉากเดียวต่อเนื่องดีกว่า)
#   ⇒ ตั้งแต่นั้นวิดีโออ่านแค่ voN · ช่อง "บทวิดีโอ" (sNen) ในหน้าแก้บทเขียนว่า "ตัวที่ส่งเข้าโมเดลวิดีโอ" แต่ไม่ถูกส่ง
# แก้ (คงเจตนา v22): บทที่ AI เขียนเอง ยังไม่ส่งเข้าวิดีโอเหมือนเดิม · ส่งเฉพาะฉากที่ "ผู้ใช้แก้" เท่านั้น
#   - mnQueue เก็บต้นฉบับ oNen = sNen ตอนจัดคิว · ฉากที่ sNen ≠ oNen (และไม่ว่าง) = ผู้ใช้แก้ (พิมพ์เอง หรือกดแปลงจากบทไทย)
#   - mnVideo (ฉาก 1-4 · 10 วิ +ฉาก 5) / mnVideo2 (ฉาก 5-8) เติม "Shot notes" ของฉากที่แก้ ตัดรวม ≤240 ตัว (เพดาน 3900)
#     ย้ำในบรรทัดเดียวกันว่ายังเป็นเทคเดียว สินค้าไม่เปลี่ยน
#   - คิวเก่าที่ไม่มี oNen = ไม่ส่ง (พฤติกรรม v22 เดิม)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F))
ops = {o['id']: o for o in d['ops']}
CAP = 240

# 1. ต้นฉบับตอนจัดคิว
sp = ops['mnQueue']['spawn']['fields']
for n in range(1, 9): sp['o%den' % n] = '{item.fields.s%den}' % n
tf = d['collections']['tasks']['fields']
for n in range(1, 9):
    if 'o%den' % n not in tf: tf.append('o%den' % n)

def edited(n):
    return {'op': 'and', 'list': [
        {'op': 'not', 'a': {'op': 'eq', 'a': '{item.o%den}' % n, 'b': ''}},
        {'op': 'not', 'a': {'op': 'eq', 'a': '{item.s%den}' % n, 'b': ''}},
        {'op': 'not', 'a': {'op': 'eq', 'a': '{item.s%den}' % n, 'b': '{item.o%den}' % n}}]}
def note(n, extra=None):
    w = edited(n) if extra is None else {'op': 'and', 'list': [extra, edited(n)]}
    return {'when': w, 'value': '{item.s%den} ' % n}
TEN = {'op': 'eq', 'a': '{values.svSec}', 'b': '10'}
HEAD = '\n\nUser shot notes (same continuous take, product unchanged): '
def block(notes, conds):
    return {'op': 'block', 'sep': '', 'parts': [{'when': {'op': 'or', 'list': conds},
        'value': {'op': 'concat', 'parts': [HEAD, {'op': 'clamp', 'max': CAP, 'value': {'op': 'block', 'sep': '', 'parts': notes}}]}}]}
B1 = block([note(1), note(2), note(3), note(4), note(5, TEN)],
           [edited(1), edited(2), edited(3), edited(4), {'op': 'and', 'list': [TEN, edited(5)]}])
B2 = block([note(5), note(6), note(7), note(8)], [edited(5), edited(6), edited(7), edited(8)])

def insert(op, blk, anchor):
    parts = op['prompt']['parts']
    if 'User shot notes' in json.dumps(parts, ensure_ascii=False): return 0   # รันซ้ำไม่ซ้อน
    i = next(i for i, p in enumerate(parts) if isinstance(p, str) and p.startswith(anchor))
    parts.insert(i, blk); return 1
n1 = insert(ops['mnVideo'], B1, '\n\nOne continuous take with a single simple action from start to end')
n2 = insert(ops['mnVideo2'], B2, '\n\nOne continuous take with a single simple action: keep the same action')
# "follow the Scene above only" ขัดกับโน้ตที่ผู้ใช้แก้ → ตัดคำ only
for p_i, p in enumerate(ops['mnVideo']['prompt']['parts']):
    if isinstance(p, str) and 'follow the Scene above only' in p:
        ops['mnVideo']['prompt']['parts'][p_i] = p.replace('follow the Scene above only', 'follow the Scene above')
print('v27: notes block', n1, n2)
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))
