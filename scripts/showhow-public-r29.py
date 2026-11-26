#!/usr/bin/env python3
"""showhow-public r29 — ปิดอัปเดตใหญ่ (27 พ.ย. 2569) = r27 + v148 หน้าตัดต่อรับครบทุกช่วง video..video6 (คลิป 20-30 วิ)
ฐาน = showhow-public-r27.build() (ตัวขาย r27 b20ba81 ทุกไบต์ · รอบ r28 showhow ไม่ได้ปล่อย)
ค่าเริ่มคงเดิม: วิดีโอ Omni 1.1 Flash · ภาพ 🍌 Nano Banana Pro
หลักฐานเทส: easybear/apps/showhow/docs/qa/2026-11-27-editor-seg/README.md
ใช้: python3 scripts/showhow-public-r29.py [--check]   (รันที่ราก easybear-config)
"""
import importlib.util, json, os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('r27', os.path.join(HERE, 'showhow-public-r27.py'))
r27 = importlib.util.module_from_spec(spec); spec.loader.exec_module(r27)
OUT = r27.OUT


def build():
    s = r27.build()
    tmp = tempfile.mkdtemp(); p = os.path.join(tmp, 'showhow-public.json')
    open(p, 'w', encoding='utf-8').write(s)
    subprocess.check_call([sys.executable, os.path.join(HERE, 'showhow-v148-editor-segments.py'), p])
    s = open(p, encoding='utf-8').read(); shutil.rmtree(tmp)
    c = json.loads(s)
    assert len(c['editor']['map']['segments']) == 6
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
