#!/usr/bin/env python3
# hardsell-meta-from-dev.py — สร้าง hardsell-meta-dev.json จาก hardsell-dev.json (EasyBear Meta · คลิปช่วงละ 10 วิคงที่)
# ใช้: python3 scripts/hardsell-meta-from-dev.py   (รันซ้ำได้ทุกครั้งที่ hardsell-dev.json เปลี่ยน · ห้ามแก้ไฟล์ meta ด้วยมือ)
# งานจากพี่หมีผ่าน metabear-starter 2026-10-10: โหมด 10/20 วิ แทน 8/16 · hardsell-dev.json ของ Flow ไม่แตะ (Flow ยังใช้ Veo 8 วิ)
# สิ่งที่เปลี่ยน:
#   ① ค่า svSec 8/16 เป็น 10/20 ทุกที่ (ค่าตั้งต้น · ตัวเลือก · คีย์ตาราง lookups · เงื่อนไข lte/eq · fallback)
#      เงื่อนไขเดิมจากโครง minimal (gt 10 = มีช่วง 2 · div 10 = จำนวนช่วง) ถูกกับ 10/20 อยู่แล้ว ไม่แตะ
#   ② วิดีโอ durationSeconds 8 เป็น 10 · ตัด trimEndIfNext + tailTrim ทิ้ง (Meta ต่อเต็มคลิป ไม่ตัดท้าย · ช่วง 2 เริ่มจากเฟรมท้ายจริง)
#   ③ ข้อความบท: ฉากละ 2 วิ เป็น 2.5 วิ (4 ฉาก/ช่วง เท่าเดิม) · ช่วงเวลา 0-2s เป็น 0-2.5s · บทพูดฉากละ 32 เป็น 40 ตัวอักษร
#      (อัตราเดิม 16 ตัวอักษร/วิ) · รวม 128/256 เป็น 160/320 · about 8 seconds เป็น 10
#   ④ หน้าจอ: ตัดหมวด โมเดล AI (dropdown imageModel/videoModel · Meta เลือกโมเดลไม่ได้) · ชิปที่โชว์ {values.videoModel} เป็นข้อความคงที่ Meta AI
#      (ขอเพิ่มโดย metabear-starter 2026-10-10 · ops ยังอ้าง values.*Model ตามเดิม — ทีม metabear map ชื่อโมเดลเองตอน build)
#   ชื่อโมเดล/เวลารอผล = ทีม metabear ปรับเองตอน build (meta-config.mjs) ไม่ทำที่นี่
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, DST = ROOT / 'hardsell-dev.json', ROOT / 'hardsell-meta-dev.json'
SEC = {'8': '10', '16': '20'}
log = []

def fmt(x):
    return str(int(x)) if x == int(x) else str(x)

def scale_range(m):
    a, b = int(m.group(1)), int(m.group(2))
    if a % 2 or b % 2 or b > 16 or a >= b:
        return m.group(0)
    return f'{fmt(a * 1.25)}-{fmt(b * 1.25)}{m.group(3)}'

TEXT_RULES = [
    (re.compile(r'(?<![\d.])(\d+)-(\d+)(s\b|\]| วิ(?!น))'), scale_range),            # 0-2s · [0-2s] · 0-4 วิ
    (re.compile(r'(?<![\d.])8 วินาที'), '10 วินาที'),
    (re.compile(r'(?<![\d.])16 วินาที'), '20 วินาที'),
    (re.compile(r'(?<![\d.])8 วิ(?!น)'), '10 วิ'),
    (re.compile(r'ฉากละ 2 วินาที'), 'ฉากละ 2.5 วินาที'),
    (re.compile(r'ฉากละไม่เกิน 32 ตัวอักษร'), 'ฉากละไม่เกิน 40 ตัวอักษร'),
    (re.compile(r'ไม่เกิน 128 ตัวอักษร'), 'ไม่เกิน 160 ตัวอักษร'),
    (re.compile(r'ไม่เกิน 256 ตัวอักษร'), 'ไม่เกิน 320 ตัวอักษร'),
    (re.compile(r'about 8 seconds'), 'about 10 seconds'),
]
TEXT_SCOPES = ('/lookups/sceneLab/', '/lookups/sceneEN/', '/lookups/lenSys/', '/lookups/lenVo/', '/lookups/lenLabel/',
               '/lookups/actTime/', '/lookups/tplVidLead/', '/ops/', '/phases/')

def text(s, path):
    if not any(path.startswith(p) for p in TEXT_SCOPES):
        return s
    out = s
    for rx, rep in TEXT_RULES:
        out = rx.sub(rep, out)
    if out != s:
        log.append(('text', path))
    return out

def key(k):
    m = re.fullmatch(r'(8|16)(\|\d+)?', k)
    return SEC[m.group(1)] + (m.group(2) or '') if m else k

def is_sv(v):
    return isinstance(v, str) and v.startswith('{values.svSec}')

MODEL_FIELDS = {'imageModel', 'videoModel'}
def ui_fields(x, acc):
    if isinstance(x, dict):
        if isinstance(x.get('field'), str): acc.add(x['field'])
        if 'action' in x or 'chain' in x: acc.add('<action>')
        for v in x.values(): ui_fields(v, acc)
    elif isinstance(x, list):
        for v in x: ui_fields(v, acc)
    return acc

def model_only(x):   # กล่องที่มีแต่ตัวเลือกโมเดล (ไม่มีช่องอื่น/ปุ่ม) = ตัดทั้งกล่อง
    if not isinstance(x, dict) or 'el' not in x: return False
    f = ui_fields(x, set())
    return bool(f) and f <= MODEL_FIELDS

def walk(o, path):
    if isinstance(o, list):
        if path.startswith('/phases/'):
            keep = []
            for i, v in enumerate(o):
                if model_only(v): log.append(('model-ui-drop', f'{path}/{i}')); continue
                keep.append(walk(v, f'{path}/{i}'))
            return keep
        return [walk(v, f'{path}/{i}') for i, v in enumerate(o)]
    if isinstance(o, str) and path.startswith('/phases/') and o.startswith('{values.videoModel}'):
        log.append(('model-chip', path)); return 'Meta AI' + o[len('{values.videoModel}'):]
    if not isinstance(o, dict):
        return text(o, path) if isinstance(o, str) else o
    out = {}
    in_lookups = path.startswith('/lookups/') and path.count('/') == 2
    for k, v in o.items():
        p = f'{path}/{k}'
        if k in ('trimEndIfNext', 'tailTrim'):   # ต่อเต็มคลิป: ช่วง 2 เริ่มจากเฟรมสุดท้ายจริง · รวมคลิปไม่ตัดท้ายช่วงแรก
            log.append(('trim-drop', p)); continue
        nk = key(k) if in_lookups else k
        if nk != k: log.append(('key', p))
        if k == 'durationSeconds' and v == 8:
            out[nk] = 10; log.append(('dur', p)); continue
        out[nk] = walk(v, p)
    # เงื่อนไข/ตัวเลือกที่ผูกค่า svSec
    if o.get('op') in ('lte', 'eq') and is_sv(o.get('a')) and o.get('b') in SEC:
        out['b'] = SEC[o['b']]; log.append(('cmp', path))
    if o.get('op') == 'lookup' and is_sv(o.get('key')) and isinstance(o.get('fallback'), str):
        fb = o['fallback']
        out['fallback'] = SEC.get(fb, out['fallback']); log.append(('fallback', path))
    if o.get('field') == 'svSec' and isinstance(o.get('options'), list):
        for opt in out['options']:
            if opt.get('value') in SEC:
                opt['value'] = SEC[opt['value']]; log.append(('option', path))
    if isinstance(o.get('when'), str) and o['when'].startswith('values.svSec='):
        n = o['when'].split('=', 1)[1]
        if n in SEC: out['when'] = 'values.svSec=' + SEC[n]; log.append(('when', path))
    return out

d = json.loads(SRC.read_text())
m = walk(d, '')
m['lookups']['lenSecs'] = {k: SEC.get(v, v) for k, v in m['lookups']['lenSecs'].items()}; log.append(('lenSecs', '/lookups/lenSecs'))
if m.get('values', {}).get('svSec') in SEC:
    m['values']['svSec'] = SEC[m['values']['svSec']]; log.append(('default', '/values/svSec'))

# ยาม: ห้ามเหลือ 8/16 ที่ผูก svSec
s = json.dumps(m, ensure_ascii=False)
left = [x for x in ('values.svSec=16', '"trimEndIfNext"', '"tailTrim"', '"durationSeconds": 8', 'about 8 seconds') if x in s]
ph = json.dumps(m['phases'], ensure_ascii=False)
left += [x for x in ('{values.videoModel}', '{values.imageModel}', '"field": "videoModel"', '"field": "imageModel"') if x in ph]
left += [k for t in m['lookups'].values() if isinstance(t, dict) for k in t if re.fullmatch(r'(8|16)(\|\d+)?', k)]
if left:
    sys.exit(f'🔴 ยังเหลือของ 8/16: {left}')
DST.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n')
from collections import Counter
print('✓', DST.name, len(DST.read_bytes()), 'B ·', dict(Counter(k for k, _ in log)))
