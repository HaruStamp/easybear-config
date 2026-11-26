# hardsell-dev v36: mnPlan prompt เกิน 3900 = เขียนบทไม่ได้เลย (เทสสด 26 พ.ย. หลัง v35 · engine v1.25 · ugc-lips 20 วิ friendly)
#   log: "⚠ mnPlan: prompt 4017 ตัวอักษร เกิน 3900 — ย้ายก้อนข้อมูลไปท้าย systemInstruction" → "FAIL mnPlan: prompt-too-long 4017 (policy)"
#   engine-exec: llm prompt > MAX_PROMPT (3900) Flow ตอบหลอก service unavailable · systemInstruction ไม่ติดเพดานนี้
#   ต้นเหตุ: prompt ของ mnPlan แบกทั้งข้อมูลสินค้า (ยาวตามที่ผู้ใช้พิมพ์) + กฎคงที่ทุกก้อน (ย้ำชื่อเทมเพลต · คำลงท้าย · ท่าฉากปิด · โหมดพรีเซนเตอร์
#     + charPlanT · ข้อมูลพรีเซนเตอร์ · เสียงพากย์ · โหมดข้อความ) — v35 เพิ่มกฎปากทาลิป ~300 ตัว เลยล้น · สินค้าคำอธิบายยาวล้นตั้งแต่ก่อน v35 (วัดได้ 4611)
#   แก้: ย้ายก้อนกฎทั้งหมดไปท้าย systemInstruction (เนื้อความเดิมทุกตัวอักษร ลำดับเดิม) ใต้หัว "กฎเพิ่มเติมของคลิปนี้"
#     prompt เหลือ: ข้อมูลสินค้า · เทมเพลต · โทน · ฉากหลัง · ข้อกำหนดรายองก์ · ท่า · บรรทัด "ตอบเป็น JSON array เท่านั้น"
#   ใช้ได้ทั้ง dev และ public r26 (โครง mnPlan เดียวกัน: prompt concat 10 ชิ้น · ชิ้นแรก concat 21 ชิ้น)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F))
o = next(o for o in d['ops'] if o['id'] == 'mnPlan')
HEAD = '\n\nกฎเพิ่มเติมของคลิปนี้ (ตามที่ผู้ใช้ตั้งค่า — ใช้คู่กับข้อมูลสินค้าใน prompt):\n'
JSONL = '\n\nตอบเป็น JSON array เท่านั้น — token แรกของคำตอบต้องเป็น [ และ token สุดท้ายต้องเป็น ] ห้ามมีข้อความอื่นใดนอก JSON'
S = o['systemInstruction']
if HEAD.strip() in json.dumps(S, ensure_ascii=False):
    print('v36: ทำแล้ว ข้าม')
else:
    P = o['prompt']; assert P['op'] == 'concat' and 'sep' not in P and len(P['parts']) == 10, 'โครง prompt ไม่ตรง'
    P0 = P['parts'][0]; assert P0['op'] == 'concat' and 'sep' not in P0
    i = next(k for k, p in enumerate(P0['parts']) if isinstance(p, str) and p.startswith('ย้ำ: ชื่อเทมเพลต'))
    assert P0['parts'][i - 1] == '\n', repr(P0['parts'][i - 1])
    moved = P0['parts'][i:]
    last = moved[-1]; assert last['op'] == 'concat' and 'sep' not in last and isinstance(last['parts'][-1], str) and last['parts'][-1].endswith(JSONL)
    last['parts'][-1] = last['parts'][-1][:-len(JSONL)]
    pose = P['parts'][1]; assert pose['op'] == 'block' and 'poseTH' in json.dumps(pose, ensure_ascii=False)
    rest = P['parts'][2:]; assert rest[0] == '\n\nโหมดพรีเซนเตอร์: '
    P0['parts'] = P0['parts'][:i - 1]
    P['parts'] = [P0, pose, JSONL]
    assert S['op'] == 'concat' and 'sep' not in S
    S['parts'] += [HEAD] + moved + rest
    print('v36: ย้ายกฎ %d+%d ชิ้น ไปท้าย systemInstruction' % (len(moved), len(rest)))
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))