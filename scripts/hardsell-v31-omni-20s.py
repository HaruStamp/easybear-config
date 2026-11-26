# hardsell-dev v31: คลิป 20 วิ = mnVideo 10 วิ + mnVideo2 10 วิ (เฉพาะ Omni) — เจ้าของสั่ง 26 พ.ย. (งานต่อจาก v25)
# ปลดล็อกโดย engine mirror f912508: el.segments[].trimTailIfNext = ตัดท้ายกี่วิจากความยาวจริง (ชนะ trimEndIfNext · อ่านไม่ได้ถอยไป trimEndIfNext)
#   - ทุก el.segments ช่วงแรก: คง trimEndIfNext 7 (Flow รุ่นเก่ายังอ่านแค่ตัวนี้ = ถูกสำหรับ 16 วิ) + เพิ่ม trimTailIfNext 1 (= tailTrim)
#   - 20 วิ = 8 ฉาก ฉากละ 2.5 วิ (โครงเดียวกับ 16 วิ: ช่วง 1 = ฉาก 1-4 · ช่วง 2 = ฉาก 5-8) ⇒ ไม่ต้องแตะ spawn/validate/การ์ดฉาก
#   - mnVideo/mnVideo2.durationSeconds = 10 เมื่อ 20 วิ + Omni · mnVideo2.when svSec=16 → svSec>10
#   - รอยต่อเสียง (v26) 20 วิ: ช่วง 1 พูดจบก่อน 8.5 วิ แล้วเงียบ ปากปิด ถึงจุดตัด 9 วิ · lenVo 20 ช่วงแรก ≤128 ตัว ช่วงสอง ≤160 ตัว
#   - UI: ปุ่มความยาว Omni = 8/10/16/20 · Veo = 8/16 · Veo ถูกปิดตอนเลือก 10/20 · เวลาบนการ์ดฉากตามความยาว (lookup sceneTime)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F))
L = d['lookups']
SEC = '{values.svSec}'
OMNI = {'op': 'contains', 'a': '{values.videoModel}', 'b': 'Omni'}
TEN = {'op': 'or', 'list': [{'op': 'eq', 'a': SEC, 'b': '10'}, {'op': 'eq', 'a': SEC, 'b': '20'}]}
ops = {o['id']: o for o in d['ops']}
assert 'clipSecEN' in L and 'audioSpan' in L, 'ต้องรัน v25/v26 ก่อน'

# ── lookups คีย์ 20 ──
L['lenSys']['20'] = ('คุณคือผู้กำกับคลิปขายของสไตล์ TikTok ของพี่หมีแว่น (แนวขายดุ — ฮุคแรง โน้มน้าวไว ปิดการขายชัด) — ออกแบบคลิปแนวตั้ง 9:16 ยาว 20 วินาที แบ่ง 2 ช่วง ช่วงละ 10 วินาทีต่อกันเป็นเรื่องเดียว (ช่วงที่ 2 เริ่มจากเฟรมสุดท้ายของช่วงแรก) เดินผ่าน 8 ฉากคงที่ตามลำดับนี้เสมอ:\n'
    '1. ฮุคแรง 0-2.5s — หยุดนิ้วคนดูตั้งแต่วินาทีแรก\n2. ปัญหาที่เจอ 2.5-5s — ปัญหาที่คนดูเจออยู่จริง\n3. แนะนำสินค้า 5-7.5s — เปิดตัวสินค้าเป็นทางออก\n4. จุดเด่นที่ชัดที่สุด 7.5-10s — จุดขายหลัก 1 อย่าง\n'
    '5. ใช้จริงให้ดู 10-12.5s — โชว์ตอนใช้งานจริง\n6. ผลลัพธ์ที่ได้ 12.5-15s — ให้เห็นผลกับตา\n7. ข้อเสนอพิเศษ 15-17.5s — ราคา/โปรที่ผู้ใช้ให้มา (ถ้าไม่มี ให้เน้นความคุ้ม)\n8. ปิดการขาย 17.5-20s — ชวนซื้อตอนนี้เลย จบที่คน ไม่ใช่การ์ดปิด\n'
    'สำคัญ: ฉาก 4 คือเฟรมสุดท้ายของช่วงแรก และฉาก 5 เริ่มช่วงที่ 2 จากท่าและตำแหน่งเดียวกัน — ห้ามให้ฉาก 4 เป็นตอนจบ ห้ามให้ฉาก 5 เปิดเรื่องใหม่หรือแนะนำสินค้าซ้ำ')
L['lenVo']['20'] = ('กฎความยาวบทพูด (ต้องพูดต่อเนื่อง ห้ามมีช่วงเงียบกลางประโยค):\n'
    '- คลิปนี้ยาว 20 วินาที มี 8 ฉาก แบ่ง 2 ช่วงที่สร้างเสียงแยกกัน — vo1 ถึง vo8 ต้องมีบทพูดครบทุกฉาก ห้ามเว้นว่างแม้แต่ฉากเดียว\n'
    '- นับเป็นตัวอักษรไทย ไม่ใช่จำนวนคำ (นับทุกตัวอักษรรวมสระและวรรณยุกต์ เว้นวรรคไม่ต้องนับ) — เกินเมื่อไหร่เสียงจะพูดรัวจนฟังไม่ทัน\n'
    '- ช่วงแรก vo1 ถึง vo4: ฉากละไม่เกิน 32 ตัวอักษร รวมไม่เกิน 128 ตัวอักษร เพราะช่วงแรกถูกตัดที่วินาทีที่ 9 — vo4 ต้องจบประโยคสมบูรณ์ ห้ามค้างครึ่งประโยคไปต่อใน vo5\n'
    '- ช่วงสอง vo5 ถึง vo8: ฉากละไม่เกิน 40 ตัวอักษร รวมไม่เกิน 160 ตัวอักษร · vo5 เริ่มประโยคใหม่ ห้ามทวนคำหรือวลีของ vo4 ห้ามทักทายหรือแนะนำสินค้าซ้ำ\n'
    '- ในแต่ละช่วงเขียนให้ต่อกันเป็นย่อหน้าเดียวที่อ่านรวดเดียวจบ ไม่ใช่วลีสั้นที่จบห้วนแยกกัน\n'
    '- ภาษาพูดแบบคนรีวิวจริง ไม่ใช่ภาษาโฆษณาอ่านสคริปต์')
for t in ('lenOut', 'lenActHead', 'lenActTail', 'lenScenes'): L[t]['20'] = L[t]['16']
L['lenLabel']['20'] = '20 วินาที'; L['lenSecs']['20'] = '20'
L['clipSecEN']['20'] = ' About 10 seconds long.'; L['clipSecTH']['20'] = '10 วิ'
L['audioSpan']['20'] = 'from 0.0s, no gaps, last sentence done by 8.5s; then silent to the end, lips closed, same pose (the clip is cut at 9s)'
T20 = ['0-2.5', '2.5-5', '5-7.5', '7.5-10', '10-12.5', '12.5-15', '15-17.5', '17.5-20']
for i in range(1, 9):
    L['sceneAct']['20|%d' % i] = L['sceneAct']['16|%d' % i]
    L['sceneLab']['20|%d' % i] = L['sceneLab']['16|%d' % i].split(' [')[0] + ' [%ss]' % T20[i - 1]
    L['sceneEN']['20|%d' % i] = L['sceneEN']['16|%d' % i].replace(L['sceneEN']['16|%d' % i].split('(')[1].split(')')[0], T20[i - 1] + 's')
for i, t in enumerate(['0-5 วิ', '5-10 วิ', '10-15 วิ', '15-20 วิ'], 1):
    L['lenAct']['20|%d' % i] = L['lenAct']['16|%d' % i]; L['actName']['20|%d' % i] = L['actName']['16|%d' % i]; L['actTime']['20|%d' % i] = t
# เวลาบนการ์ดฉาก (เดิมเขียนตาย 0-2 … 14-16 วิ)
L['sceneTime'] = {}
for sec in ('8', '10', '16'):
    for i in range(1, 9): L['sceneTime']['%s|%d' % (sec, i)] = '%d-%d วิ' % (2 * i - 2, 2 * i)
for i in range(1, 9): L['sceneTime']['20|%d' % i] = T20[i - 1] + ' วิ'

# ── ops ──
v1, v2 = ops['mnVideo'], ops['mnVideo2']
v1['durationSeconds'] = {'op': 'cond', 'when': {'op': 'and', 'list': [TEN, OMNI]}, 'then': '10', 'else': '8'}
v2['durationSeconds'] = {'op': 'cond', 'when': {'op': 'and', 'list': [{'op': 'eq', 'a': SEC, 'b': '20'}, OMNI]}, 'then': '10', 'else': '8'}
assert v2['when'] in ('values.svSec=16', 'values.svSec>10'); v2['when'] = 'values.svSec>10'
v2['logRun'] = {'op': 'concat', 'parts': ['[{item.productName} คลิป {item.clipIndex}] กำลังสร้างวิดีโอช่วงที่ 2 (',
    {'op': 'lookup', 'table': 'clipSecTH', 'key': SEC, 'fallback': '8 วิ'}, ')']}
rh = ops['mnPlan']['retryHint']['parts']
if '20 วินาที' not in rh[0]:
    rh[0] = rh[0].replace('16 วินาที = ฉาก 1 ถึง 8)', '16 หรือ 20 วินาที = ฉาก 1 ถึง 8)'); assert '20 วินาที' in rh[0]

# ── segments: คง 7 + เพิ่ม trimTailIfNext = tailTrim ──
TT = v2['tailTrim']; assert TT == 1
ns = 0
def segs(x):
    global ns
    if isinstance(x, dict):
        if isinstance(x.get('segments'), list):
            s0 = x['segments'][0]; assert s0['slot'] == 'video' and s0.get('trimEndIfNext') == 8 - TT
            s0['trimTailIfNext'] = TT; ns += 1
        for v in x.values(): segs(v)
    elif isinstance(x, list):
        for v in x: segs(v)
segs(d)
assert ns == 10, ns

# ── UI ──
done = {'sec': 0, 'vm': 0, 'warn': 0, 'res': 0, 'time': 0}
def ui(x):
    if isinstance(x, dict):
        if x.get('el') == 'grid-select' and x.get('field') == 'svSec' and x.get('when') == OMNI:
            if not any(o['value'] == '20' for o in x['options']):
                x['options'].append({'value': '20', 'label': '20 วินาที', 'desc': '2 ช่วง ช่วงละ 10 วิ · 8 ฉาก'})
            x['cols'] = 4; x['mobile'] = {'cols': 2}; done['sec'] += 1
        if x.get('el') == 'dropdown' and x.get('field') == 'videoModel':
            for o in x['options']:
                if 'disabledWhen' in o: o['disabledWhen'] = TEN; o['reason'] = 'ทำได้แค่ 8 / 16 วิ'
            done['vm'] += 1
        if x.get('el') == 'text' and isinstance(x.get('value'), str):
            v = x['value']
            if v.startswith('คลิป 10 วิ ใช้ได้เฉพาะ Omni'):
                x['value'] = 'คลิป 10 / 20 วิ ใช้ได้เฉพาะ Omni — Veo ทำได้ 8 / 16 วิ'; done['warn'] += 1
            elif v.startswith('ตอนนี้ตั้งความยาว 10 วิ แต่ Veo'):
                x['value'] = 'ตอนนี้ตั้งความยาว 10 / 20 วิ แต่ Veo ทำไม่ได้ — เลือก 8 หรือ 16 วินาทีใหม่ก่อนเริ่ม'
                x['when']['list'][1] = TEN; done['warn'] += 1
            elif v.startswith('360p ทำได้เฉพาะคลิปช่วงเดียว — ตอนนี้ตั้งความยาว 16 วิ'):
                x['value'] = v.replace('ตอนนี้ตั้งความยาว 16 วิ คลิปจะใช้ 720p', 'ตอนนี้ตั้งความยาว 16 / 20 วิ คลิปจะใช้ 720p'); done['res'] += 1
            elif x.get('icon') == 'schedule' and v.endswith(' วิ') and '-' in v:
                a, b = v[:-3].split('-')
                if int(b) == int(a) + 2 and int(b) <= 16:
                    x['value'] = {'op': 'lookup', 'table': 'sceneTime', 'key': SEC + '|%d' % (int(b) // 2), 'fallback': v}; done['time'] += 1
        if x.get('el') == 'grid-select' and x.get('field') == 'svRes' and x.get('when') == {'op': 'gt', 'a': SEC, 'b': 10}:
            x['options'][0]['desc'] = '48 เครดิต / 16 วิ · 60 / 20 วิ · ภาพคม ลง Shopee ได้'
            x['options'][1]['desc'] = 'ใช้ได้กับคลิป 8 / 10 วิ เท่านั้น · 16 / 20 วิ จะใช้ 720p'; done['res'] += 1
        for k, v in x.items():
            if k != 'when': ui(v)
    elif isinstance(x, list):
        for v in x: ui(v)
ui(d['phases'])
assert done['sec'] == 1 and done['vm'] == 1 and done['warn'] == 2 and done['res'] == 2 and done['time'] in (0, 8), done

# ── ตรวจ: lookup ที่คีย์ด้วย svSec มีคีย์ 20 ครบ ──
miss = []
def chk(x):
    if isinstance(x, dict):
        if x.get('op') == 'lookup' and isinstance(x.get('key'), str) and x['key'].startswith(SEC):
            k = x['key'].replace(SEC, '20')
            if k not in L.get(x['table'], {}): miss.append((x['table'], k))
        for v in x.values(): chk(v)
    elif isinstance(x, list):
        for v in x: chk(v)
chk(d['ops']); chk(d['phases'])
assert not miss, miss
print('v31: segments', ns, '· UI', done)
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))
