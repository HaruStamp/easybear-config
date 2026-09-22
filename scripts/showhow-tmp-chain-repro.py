#!/usr/bin/env python3
# ชั่วคราว (ลบหลังปิดเคส) — repro หาสาเหตุ frame-to-video ถูกปฏิเสธ
# ชุดที่ล้ม = Omni 1.1 Flash · durationSeconds 10 · tailTrim 0.1 · ไม่ส่ง resolution
# แผนของ starter+hardsell: **เปลี่ยนทีละ 1 ตัวแปร** (ชุดแรกที่เปลี่ยน 3 ตัวพร้อมกันตีความไม่ได้)
import json, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
base = [o for o in c['ops'] if o['id'] == 'mnVideo2'][0]
c['ops'] = [o for o in c['ops'] if not o['id'].startswith('zz')]
#     id      model            dur  tailTrim  resolution   อะไรเปลี่ยนจากชุดที่ล้ม
CASES = [
    ('zzA', 'Omni 1.1 Flash', 8,  0.1, None,   'ความยาว 10→8'),
    ('zzC', 'Omni 1.1 Flash', 10, 1.0, None,   'tailTrim 0.1→1.0'),
    ('zzD', 'Omni 1.1 Flash', 10, 0.1, '720p', 'เพิ่ม resolution 720p'),
    ('zzB', 'Veo 3.1 Fast',   8,  0.1, None,   'โมเดล+ความยาว (Veo clamp 8 อยู่แล้ว)'),
]
for oid, model, dur, tt, res, why in CASES:
    o = json.loads(json.dumps(base, ensure_ascii=False))
    o.update({'id': oid, 'out': 'video6', 'model': model, 'durationSeconds': dur, 'tailTrim': tt,
              'startFrame': '{item.slots.video}',
              'logRun': f'[repro {oid}] {why} · {model}/{dur}s/tt{tt}/res{res or "-"}',
              'logDone': f'[repro {oid}] ✅ ผ่าน — {why}'})
    if res: o['resolution'] = res
    o.pop('when', None)
    c['ops'].append(o)
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('repro ops:', [x[0] + ' = ' + x[5] for x in CASES])
