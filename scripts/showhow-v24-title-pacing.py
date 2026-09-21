#!/usr/bin/env python3
# showhow-v24-title-pacing.py — 2 อย่างที่ทำได้ใน config โดยไม่ต้องรอ engine (พี่หมีสั่ง 2026-09-21)
#  ① โหมดข้อความใหม่ "หัวเรื่องค้างทั้งคลิป" — หัวเรื่องเดิมอยู่บนจอตลอดคลิป ไม่ใช่แค่ฉากแรก
#     (ของเดิม "หัวเรื่องตอนเปิด" = ov1 โผล่เฉพาะช่วงแรก ⇒ คลิป 20-60 วิ พอขึ้นช่วง 2 หัวเรื่องหายไปเลย)
#     ทำที่ prompt วิดีโอทุกช่วง: ช่วง 1 สั่งให้ค้างทั้ง 10 วิ · ช่วง 2+ สั่งให้คงหัวเรื่องเดิมจากช่วงแรก (ข้อความ/ฟอนต์/ตำแหน่งเดียวกัน)
#     🪤 ไม่แตะบอร์ด — บอร์ดเป็นภาพอ้างอิง ไม่ใช่ของที่ผู้ชมเห็น และ headroom บอร์ดเหลือ 47 ตัวอักษร
#  ② จังหวะฉากปิด — ช่วงสุดท้ายของคลิป (svSec = 10k) ให้ค้างฉากสุดท้ายนานกว่าฉากอื่นราว 1 วินาที แล้วจบนิ่ง
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, '..', 'showhow-dev.json')
NEW = 'หัวเรื่องค้างทั้งคลิป'
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)
if NEW in raw: sys.exit('· มี v24 อยู่แล้ว ข้าม')

# ── ① UI: เพิ่มตัวเลือกที่ 4 ────────────────────────────────────────────
def walk(n):
    if isinstance(n, dict):
        yield n
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)
ui = [n for n in walk(d) if n.get('field') == 'svTextOn' and n.get('options')]
assert len(ui) == 1, len(ui)
ui[0]['options'].append({'value': NEW, 'label': 'หัวเรื่องค้างทั้งคลิป', 'desc': 'หัวเรื่องเดิมอยู่ตลอดคลิป', 'icon': 'sticky_note_2'})
ui[0]['cols'] = 2                                     # 4 ตัวเลือก → 2 คอลัมน์ (เดิม 3 ช่องพอดีแถวเดียว)

# ── ② บทของ mnPlan: กฎโหมดใหม่ (ลอกของ "หัวเรื่องตอนเปิด" แล้วบอกว่าค้างทั้งคลิป) ──
tp = d['lookups']['textPlan']
base = tp['หัวเรื่องตอนเปิด']
tp[NEW] = (base.replace('โหมดข้อความ "หัวเรื่องตอนเปิด" — มีตัวหนังสือบนภาพเฉพาะฉากแรก (ov1)',
                        'โหมดข้อความ "หัวเรื่องค้างทั้งคลิป" — มีตัวหนังสือบนภาพชุดเดียวคือ ov1 ที่ค้างอยู่ตลอดคลิป')
           + ' · ov1 ต้องสั้นพอที่จะอ่านได้ตลอดคลิปโดยไม่บังงาน')
assert tp[NEW] != base

# ── ③ บอร์ดช่วง 2+ : โหมดใหม่ = ไม่มีตัวหนังสือบนบอร์ด (เหมือนโหมดหัวเรื่องตอนเปิด) ──
n_board = 0
for n in walk(d):
    if isinstance(n.get('parts'), list):
        for i, part in enumerate(list(n['parts'])):
            if isinstance(part, dict) and part.get('when') == 'values.svTextOn=หัวเรื่องตอนเปิด':
                n['parts'].insert(i + 1, {'when': f'values.svTextOn={NEW}', 'value': part['value']}); n_board += 1
                break

# ── ④ วิดีโอ: หัวเรื่องค้าง ──────────────────────────────────────────────
OST = ('\n\nON-SCREEN TEXT: one fixed Thai title overlay only — style {values.svText} — follow that style exactly for font, colour and treatment,'
       ' one line, accurate Thai glyphs, same wording, size and position in every single frame from first to last, upper area, never covering the work.')
KEEP = '\n\nTITLE: keep the exact same fixed title overlay as the earlier parts, same wording, font, size and position, on screen the whole time: "{item.ov1}"'
PACE = '\n\nPACING: hold the last scene about 1 s longer than the others and end on a still frame.'
ops = {o['id']: o for o in d['ops']}
for k in range(1, 7):
    op = ops['mnVideo' if k == 1 else f'mnVideo{k}']
    parts = op['prompt']['parts']
    ost_at = next(i for i, p in enumerate(parts)
                  if isinstance(p, dict) and p.get('op') == 'block'
                  and any(isinstance(q, dict) and 'ON-SCREEN TEXT' in str(q.get('value', '')) for q in p.get('parts', [])))
    parts[ost_at]['parts'].insert(0, {'when': f'values.svTextOn={NEW}', 'value': OST if k == 1 else OST + KEEP})
    assert isinstance(parts[-1], str) and 'Negative:' in parts[-1], parts[-1][:40]
    parts.insert(len(parts) - 1, {'op': 'block', 'sep': '', 'parts': [{'when': f'values.svSec={10 * k}', 'value': PACE}]})
print(f'  วิดีโอ 6 op · บอร์ด {n_board} จุด · textPlan +1 คีย์')

open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print('✓ v24 ·', os.path.getsize(P), 'bytes')
