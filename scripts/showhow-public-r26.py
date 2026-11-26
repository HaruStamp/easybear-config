#!/usr/bin/env python3
"""showhow-public r26 — ตัวขาย showhow รอบอัปเดตใหญ่ 26 พ.ย. (เฉพาะของที่เทสจริงบน Dev ผ่านแล้ว)
ฐาน = showhow-public.json ปัจจุบัน (939243c · Omni 1.1 Flash · บอร์ด Nano Banana Pro · ไม่มี 360p/ไทม์แลปส์ใหม่) — ไม่ยก dev ทั้งก้อน
ใส่:
  mic   ตัวเลือกไมค์ (dev 801ae19+1176a17) — ย้ายส่วนที่ dev เพิ่มมาวางบนตัวขาย (ยึดตำแหน่งด้วยของข้างเคียง)
  v137  โมเดลรูป 3 ตัว — ค่าเริ่มตัวขาย = 🍌 Nano Banana Pro (ค่าเดิมของตัวขาย · ไม่ใช่ 2.1 แบบ dev) ⇒ ค่าเริ่ม = prompt/model เดิม
  v138+v144  mnFace (ล็อกหน้า) แบบปลอดภัยบน engine 1.22: อยู่ใน stages/ปุ่มบอร์ดทั้งชุดเท่านั้น ไม่อยู่ใน productLoop.gens
  v139  วิดีโอตามช่องบอร์ด · v140 แคปชัน/แฮชแท็ก/ปก TikTok (aux) · v141 prompt วิดีโอ ≤3900 · v142 ปกหัวข้อไทยตรงตัว
ไม่ใส่ (ยังไม่เทสจริง): v143 สัตว์เลี้ยง · v145 ตั้งค่าเฉพาะงาน · v146 บอร์ด 6/8 ช่อง
ใช้: python3 scripts/showhow-public-r26.py [--check]   (รันที่ราก easybear-config · ต้องมี git history ของ 1176a17)
      --check = สร้างใหม่แล้วเทียบกับ showhow-public.json ในโฟลเดอร์ (ไม่เขียน)
"""
import json, os, subprocess, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC = os.path.join(ROOT, 'scripts')
OUT = os.path.join(ROOT, 'showhow-public.json')
BASE_COMMIT = '939243c'          # ตัวขายปัจจุบัน (ฐานของ candidate)
MIC_BASE, MIC_FEAT = '801ae19~1', '1176a17'
D = lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True)
dump = lambda c: json.dumps(c, ensure_ascii=False, indent=1) + '\n'
git = lambda ref: json.loads(subprocess.check_output(['git', '-C', ROOT, 'show', ref], text=True))


def port_mic(c):
    b, f = git(MIC_BASE + ':showhow-dev.json'), git(MIC_FEAT + ':showhow-dev.json')
    # 1) fields + addDefaults + spawn
    for coll in ('products', 'tasks'):
        bf, ff, cf = b['collections'][coll]['fields'], f['collections'][coll]['fields'], c['collections'][coll]['fields']
        assert [x for x in ff if x not in bf] == ['mic'] and 'mic' not in cf
        prev = ff[ff.index('mic') - 1]; cf.insert(cf.index(prev) + 1, 'mic')
    c['collections']['products'].setdefault('addDefaults', {})['mic'] = f['collections']['products']['addDefaults']['mic']
    co = {o['id']: o for o in c['ops']}; bo = {o['id']: o for o in b['ops']}; fo = {o['id']: o for o in f['ops']}
    co['mnQueue']['spawn']['fields']['mic'] = fo['mnQueue']['spawn']['fields']['mic']
    # 2) prompt บอร์ด/วิดีโอ: ส่วนที่ dev แทรก 1 ชิ้นต่อ op
    n = 0
    for k in ['', '2', '3', '4', '5', '6']:
        for oid in ('mnBoard' + k, 'mnVideo' + k):
            bp, fp, cp = bo[oid]['prompt']['parts'], fo[oid]['prompt']['parts'], co[oid]['prompt']['parts']
            assert len(fp) == len(bp) + 1
            i = next(i for i in range(len(fp)) if i >= len(bp) or D(fp[i]) != D(bp[i]))
            new = fp[i]; assert 'item.mic' in D(new)
            prev = [j for j, x in enumerate(cp) if D(x) == D(bp[i - 1])]
            if len(prev) == 1: at = prev[0] + 1                       # บอร์ด: ตัวขายมีส่วนต่างก่อนหน้า 1 ชิ้น → ยึดของข้างหน้า
            else:
                assert len(cp) == len(bp), (oid, len(cp), len(bp)); at = i   # วิดีโอ: โครงเท่ากัน → ตำแหน่งเดียวกัน
            cp.insert(at, json.loads(D(new))); n += 1
    assert n == 12, n
    # 3) UI: ป้าย + ตัวเลือก ในการ์ดงาน
    def at(x, path):
        for p in path: x = x[p]
        return x
    path = ['phases', None, 'form', 2, 'card', 0, 'card', 0, 'card', 4, 'card', 2, 'card']
    def resolve(cfg):
        ph = next(p for p in cfg['phases'] if p.get('id') == 'main')
        return at(ph, path[2:])
    bl, fl, cl = resolve(b), resolve(f), resolve(c)
    ins = [x for x in fl if D(x) not in {D(y) for y in bl}]
    assert len(ins) == 2 and len(fl) == len(bl) + 2
    i = next(i for i in range(len(fl)) if D(fl[i]) != D(bl[i]))
    j = [k for k, x in enumerate(cl) if D(x) == D(bl[i - 1])]; assert len(j) == 1, 'ตำแหน่ง UI ไมค์ในตัวขายไม่ตรง'
    cl[j[0] + 1:j[0] + 1] = json.loads(D(ins))
    print('✅ mic: fields 2 · spawn · prompt 12 op · UI 2 ชิ้น')


def v137_public(c):
    """= scripts/showhow-v137-image-model.py แต่ค่าเริ่ม = Pro (ค่าเดิมตัวขาย) และวางตัวเลือกใต้ 'ความยาวคลิป' (ตัวขายไม่มีการ์ดความละเอียด)"""
    PRO = '🍌 Nano Banana Pro'
    MODELS = [PRO, '🍌 Nano Banana 2.1', '🍌 Nano Banana 2 Lite']
    assert 'imageModel' not in c['values']
    c['values']['imageModel'] = PRO
    box = c['phases'][0]['form'][0]['card'][0]['card'][4]
    sec = box['card'][1]
    assert any(x.get('field') == 'svSec' for x in sec['card']), 'ตำแหน่งการ์ดความยาวเปลี่ยน'
    row = json.loads(D(sec['card'][0])); row['card'][0]['icon'] = 'image'; row['card'][1]['value'] = 'โมเดลสร้างภาพ'
    row['className'] = row['className'].replace('gap-1.5', '!gap-1.5')   # ยาม G10: gap บน el:row ต้องมี ! (แบบการ์ดความละเอียดของ dev)
    ui = {'el': 'box', 'className': sec['className'], 'card': [
        row,
        {'el': 'grid-select', 'field': 'imageModel', 'cols': 3, 'contained': True, 'options': [
            {'value': MODELS[0], 'label': 'Nano Banana Pro', 'desc': 'ค่าเริ่ม · สวยละเอียดสุด เขียนตัวไทยได้'},
            {'value': MODELS[1], 'label': 'Nano Banana 2.1', 'desc': 'สมดุลทั้งคุณภาพและเวลา'},
            {'value': MODELS[2], 'label': 'Nano Banana 2 Lite', 'desc': 'เร็วสุด · รายละเอียดน้อยกว่า'}],
         'className': '!min-h-[48px] @[420px]:!min-h-0 [&_button>span:first-of-type]:font-bold', 'mobile': {'cols': 1}},
        {'el': 'text', 'value': 'มีข้อความบนภาพ ระบบใช้ Nano Banana Pro ให้ภาพที่มีตัวหนังสืออัตโนมัติ เพราะเขียนตัวไทยได้',
         'className': '!text-[13.5px] @[640px]:!text-[13px] opacity-55 px-0.5 leading-snug',
         'when': {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svTextOn}', 'b': 'ไม่มีข้อความ'}}}]}
    box['card'].insert(2, ui)
    H1 = {'op': 'not', 'a': {'op': 'eq', 'a': '{values.svTextOn}', 'b': 'ไม่มีข้อความ'}}
    HK = {'op': 'eq', 'a': '{values.svTextOn}', 'b': 'ซับไตเติ้ลรายฉาก'}
    n = 0
    for o in c['ops']:
        if o.get('type') != 'image': continue
        assert o['model'] == PRO, (o['id'], o['model'])
        o['model'] = {'op': 'cond', 'when': H1 if o['id'] == 'mnBoard' else HK, 'then': PRO, 'else': '{values.imageModel}'}
        n += 1
    assert n == 6, n
    print(f'✅ v137(public): op ภาพ {n} · ค่าเริ่ม {PRO}')


def run_script(name, path, argv=True):
    src = os.path.join(SC, name)
    if argv:
        subprocess.check_call([sys.executable, src, path])
    else:   # สคริปต์รุ่นแรกอ่าน 'showhow-dev.json' ใน cwd ตายตัว → รันในโฟลเดอร์ชั่วคราวที่ตั้งชื่อนั้น
        d = os.path.dirname(path); assert os.path.basename(path) == 'showhow-dev.json'
        subprocess.check_call([sys.executable, src], cwd=d)


def build():
    c = git(BASE_COMMIT + ':showhow-public.json')
    port_mic(c)
    v137_public(c)
    tmp = tempfile.mkdtemp(); p = os.path.join(tmp, 'showhow-dev.json')   # ชื่อไฟล์ชั่วคราวเท่านั้น — เนื้อหา = ตัวขาย
    open(p, 'w', encoding='utf-8').write(dump(c))
    for nm, av in (('showhow-v138-auto-face.py', False), ('showhow-v139-follow-board.py', False),
                   ('showhow-v140-tiktok-cover.py', False), ('showhow-v141-video-trim.py', True),
                   ('showhow-v142-cover-headline.py', True), ('showhow-v144-face-engine122.py', True)):
        run_script(nm, p, av)
    s = open(p, encoding='utf-8').read(); shutil.rmtree(tmp)
    c = json.loads(s)
    # ยืนยันขอบเขต
    assert 'mnFace' not in c['auto']['productLoop']['gens'] and any(x.get('op') == 'mnFace' for x in c['stages'])
    for k in ('svPets', 'svPetDesc', 'svPanels', 'svRes'): assert k not in c['values'], k
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
