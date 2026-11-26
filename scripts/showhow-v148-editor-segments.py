#!/usr/bin/env python3
"""showhow-v148 — หน้าตัดต่อรับครบทุกช่วงของคลิป (ปิดอัปเดตใหญ่ 27 พ.ย. · ท่าเดียวกับ podcast 683cc2c)
อาการ: คลิป 20/30 วิ (video..video6) กด "ไปตัดต่อคลิป" เห็นแค่ช่วงแรก ⇒ Export ได้คลิปไม่ครบ
ราก: editor.map.segments มีแค่ video ขณะที่ปุ่มดาวน์โหลด/พรีวิว/zip (el.segments) รวม video..video6
แก้: editor.map.segments = ลิสต์เดียวกับ el.segments ทุกไบต์ (ไม่มี trim · ทางดาวน์โหลดก็ต่อเต็มคลิป · tailTrim 0.1 ใช้แค่ดึงเฟรมต่อฉาก)
ใช้: python3 scripts/showhow-v148-editor-segments.py [showhow-dev.json]  (รันซ้ำ = ไม่ทำอะไร)
"""
import json, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
s0 = open(P, encoding='utf-8').read()
c = json.loads(s0)
assert json.dumps(c, ensure_ascii=False, indent=1) + '\n' == s0
segs = []
def walk(o):
    if isinstance(o, dict):
        if isinstance(o.get('segments'), list) and o.get('el'): segs.append(o['segments'])
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(c['phases']); walk(c.get('chrome', {})); walk(c.get('components', {}))
assert segs and all(s == segs[0] for s in segs), 'el.segments ไม่ตรงกันทุกจุด'
want = json.loads(json.dumps(segs[0]))
assert [s['slot'] for s in want] == ['video'] + [f'video{k}' for k in range(2, 7)] and all(set(s) == {'slot'} for s in want), want
m = c['editor']['map']
if m['segments'] == want:
    print('v148: ทำไปแล้ว — ไม่แตะ'); sys.exit(0)
assert m['segments'] == [{'slot': 'video'}], m['segments']
m['segments'] = want
open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
print(f'✅ v148: editor.map.segments video → {len(want)} ช่วง (= el.segments {len(segs)} จุด)')
