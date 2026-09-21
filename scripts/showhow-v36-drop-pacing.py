#!/usr/bin/env python3
"""showhow v36 — ถอดบรรทัด PACING ออกจาก mnVideo* ทั้ง 6 ช่วง (คืน 88 ตัวอักษรต่อ prompt)

หลักฐานว่ามันไม่ทำงาน (2026-09-22 · วัดจากคลิปจริงด้วย ffmpeg scene-detect):
  t_pd_job_0-video6.mp4 (ช่วงท้ายของคลิป 60 วิ) ตัดที่ 2.0 / 4.0 / 6.0 / 8.0 วิ = 5 ช็อต ช็อตละ 2 วิเป๊ะ
  video3 เหมือนกันทุกจุด ⇒ Omni ตัดตามจำนวนช่องบอร์ด (5 ช่อง/ช่วง) ตายตัว **ช็อตสุดท้ายไม่ได้ยาวกว่าใคร**
⇒ ข้อความ "hold the last scene about 1 s longer" กินที่ prompt ฟรี ๆ · ถ้าอยากได้ฉากปิดค้างนานจริงต้องแก้เชิงโครงสร้าง (ช่วงท้ายใช้ 4 ช่อง)

ทำไมต้องคืนที่ตรงนี้: ตัววัดในเครื่อง (scripts/lab/prompt-clamp-matrix.ts · ยืนยันตรงกับ engine v1.9.0 ทุกไบต์)
  ชั้นตัดสิน p95 พบ mnVideo* ทะลุเพดานสูงสุด 4,043/3,900 ในคู่ผสม (มีเสียงพากย์ + ซับไตเติ้ลรายฉาก + มีรูป)
"""
import json, pathlib

P = pathlib.Path(__file__).resolve().parent.parent / 'showhow-dev.json'
d = json.loads(P.read_text(encoding='utf-8'))
LINE = '\n\nPACING: hold the last scene about 1 s longer than the others and end on a still frame.'

def strip(node):
    """คืน node ที่ถอดบล็อก PACING ออก (นับจำนวนที่ถอด)"""
    if isinstance(node, list):
        out = []
        for x in node:
            if isinstance(x, dict) and x.get('op') == 'block':
                parts = [p for p in x.get('parts', []) if p.get('value') != LINE]
                if not parts:
                    strip.n += 1
                    continue
                x = {**x, 'parts': parts}
            out.append(strip(x))
        return out
    if isinstance(node, dict):
        return {k: strip(v) for k, v in node.items()}
    return node

strip.n = 0
d['ops'] = strip(d['ops'])
assert strip.n == 6, f'ถอดได้ {strip.n} บล็อก (คาด 6 = mnVideo 1-6) — หยุด'
assert 'PACING' not in json.dumps(d, ensure_ascii=False), 'ยังมี PACING ค้าง'
P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'ถอด PACING {strip.n} บล็อก · คืน {len(LINE)} ตัวอักษรต่อ prompt วิดีโอ')
