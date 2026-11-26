#!/usr/bin/env python3
"""showhow-public r27 — อัปเดตใหญ่ รอบ 2 (27 พ.ย. 2569) = r26 + ของที่เทสสดผ่านบน Dev 6eb190f0 (engine 1.25) รอบ 2
ฐาน = showhow-public-r26.build() (ตัวขาย r26 c154baa ทุกไบต์)
ใส่เพิ่ม (สคริปต์ dev ตัวเดิม ลำดับเดียวกับ dev):
  v143 สัตว์เลี้ยงร่วมแสดง 1-3 ตัว (ตัวห่อ public-r27-v143: ค้นช่องรูปหน้าแทน index ตายตัว) · v145 ตั้งค่าเฉพาะงาน · v146 สตอรีบอร์ด 6/8 ช่อง (คลิป 10 วิ · ตัวห่อ public-r27-v146: หัวการ์ดลอกการ์ดโมเดลภาพ เพราะตัวขายไม่มีการ์ดความละเอียด)
  v147 mnFace กลับเข้า productLoop.gens (ตัวขาย v1.10.0 2901b15c = engine 1.25 มี loopGenApplies แล้ว)
ค่าเริ่มคงเดิม: วิดีโอ Omni 1.1 Flash · ภาพ 🍌 Nano Banana Pro · ไม่มี 360p
หลักฐานเทส: easybear/apps/showhow/docs/qa/2026-11-27-round2/README.md
ใช้: python3 scripts/showhow-public-r27.py [--check]   (รันที่ราก easybear-config)
"""
import importlib.util, json, os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('r26', os.path.join(HERE, 'showhow-public-r26.py'))
r26 = importlib.util.module_from_spec(spec); spec.loader.exec_module(r26)
OUT = r26.OUT



def build():
    s = r26.build()
    tmp = tempfile.mkdtemp(); p = os.path.join(tmp, 'showhow-public.json')
    open(p, 'w', encoding='utf-8').write(s)
    for nm in ('showhow-public-r27-v143-pets.py', 'showhow-v145-per-product.py', 'showhow-public-r27-v146-panels.py',
               'showhow-v147-face-gens-engine125.py'):
        subprocess.check_call([sys.executable, os.path.join(HERE, nm), p])
    s = open(p, encoding='utf-8').read(); shutil.rmtree(tmp)
    c = json.loads(s)
    assert 'mnFace' in c['auto']['productLoop']['gens']
    assert 'svRes' not in c['values']
    assert {o['model'] for o in c['ops'] if o['type'] == 'video'} == {'Omni 1.1 Flash'}
    assert c['values']['imageModel'] == '🍌 Nano Banana Pro'
    return s


if __name__ == '__main__':
    s = build()
    if '--check' in sys.argv:
        ok = open(OUT, encoding='utf-8').read() == s
        print('check:', 'ตรงทุกไบต์' if ok else 'ไม่ตรง'); sys.exit(0 if ok else 1)
    open(OUT, 'w', encoding='utf-8').write(s)
    print('เขียน', OUT, len(s))
