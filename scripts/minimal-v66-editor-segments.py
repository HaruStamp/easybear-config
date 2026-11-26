#!/usr/bin/env python3
# minimal-dev v66: หน้าตัดต่อรับครบทุกช่วงของคลิป (ปิดอัปเดตใหญ่ 27 พ.ย. · ท่าเดียวกับ podcast 683cc2c)
#   อาการ: คลิป 20/30 วิ (video+video2+video3) กด "ไปตัดต่อคลิป" เห็นแค่ช่วงแรก ⇒ Export ได้คลิปไม่ครบ
#   ราก: editor.map.segments มีแค่ video ขณะที่ปุ่มดาวน์โหลด/พรีวิว/zip (el.segments 9 จุด) รวม video..video3
#   แก้: editor.map.segments = ลิสต์เดียวกับ el.segments ของปุ่มดาวน์โหลดทุกไบต์ (ไม่มี trim · ทางดาวน์โหลดก็ต่อเต็มคลิป)
# ใช้: python3 scripts/minimal-v66-editor-segments.py [minimal-dev.json]   (รันซ้ำได้)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json'
s0 = open(F, encoding='utf-8').read(); d = json.loads(s0)
assert json.dumps(d, ensure_ascii=False, indent=2) == s0, 'รูปแบบไฟล์ไม่ใช่ indent 2'
segs = []
def walk(o):
    if isinstance(o, dict):
        if isinstance(o.get('segments'), list) and o.get('el'): segs.append(o['segments'])
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(d['phases']); walk(d.get('chrome', {})); walk(d.get('components', {}))
assert segs and all(s == segs[0] for s in segs), 'el.segments ไม่ตรงกันทุกจุด'
want = json.loads(json.dumps(segs[0]))
assert [s['slot'] for s in want] == ['video', 'video2', 'video3'] and all(set(s) == {'slot'} for s in want), want
m = d['editor']['map']
if m['segments'] == want: print('v66: ทำไปแล้ว — ไม่แตะ'); sys.exit(0)
assert m['segments'] == [{'slot': 'video'}], m['segments']
m['segments'] = want
open(F, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2))
print(f'v66: editor.map.segments video → {len(want)} ช่วง (= el.segments {len(segs)} จุด)')
