#!/usr/bin/env python3
"""showhow v41 — ปุ่มที่แตะสื่อหลายช่วง เปลี่ยนเป็น `el.menu` (engine v1.10.0) ตาม design ที่พี่หมีเคาะ

design (ข้อความกลางที่ทีม minimal ส่งต่อมา):
  ปุ่ม "ทำใหม่" (retry · force)   10 วิ → กดแล้วทำเลย ไม่มีเมนู · 20 วิ+ → เมนู [ทั้งหมด] [ช่วง 1] [ช่วง 2] …
  ปุ่ม "เลือกไฟล์เอง" (pick)      10 วิ → เลือกไฟล์เลย      · 20 วิ+ → เมนู [ใส่เป็นช่วง 1] [ช่วง 2] …
  ปุ่ม "ทำของที่ยังไม่มี" (gen)    ไม่มีเมนู ไม่แตะเลย (มันข้ามช่องที่เต็มแล้วอยู่แล้ว)
🔑 กติกาที่ทำให้ design นี้เป็นจริง: **ทุกเมนูต้องมีข้อที่ไม่มี `when` พอดี 1 ข้อ**
   ⇒ ที่ความยาวต่ำสุดเหลือ 1 ข้อ · engine ยิงเลยไม่เปิดกล่อง (ยามข้อนี้ทีม minimal แนะนำให้ใส่ที่สุด)

ของที่ **ไม่** แตะรอบนี้ (ถอดทีหลังตามที่ตกลงกับ minimal — ต่อเมนูให้ทำงานก่อน):
  · ปุ่ม "วาดบอร์ดช่วง N ใหม่" 12 ตัว (v27)   · ปุ่มแปลบท 30 ตัว (v28)   · pick รูปสินค้า/ห้อง/หน้า (ไม่ใช่ช่วง)

🆕 แถม: chain ของปุ่มบอร์ดยังเป็น 6→1 (ซากจากยุคก่อน v11) — บอร์ดต้องวาด **1→6** เพราะช่วง K อ้างบอร์ดช่วง 1 และ K-1
   เป็นบั๊กตัวเดียวกับที่ยาม G8 จับใน `auto.productLoop.gens` แต่ยามยังไม่ครอบ "chain ของปุ่ม" ⇒ แก้ที่นี่ + ขยายยาม

🪤 บทเรียนจาก minimal ที่ใช้ในสคริปต์นี้: หาเป้าด้วย**โครง** (el + chain) ไม่ใช่ marker · เก็บเป้าให้ครบก่อนค่อยแก้ ·
   ลบเป้าเดิมออกจากตัวปุ่มให้หมดก่อนใส่ menu (validator ฟ้องตอน boot ถ้ามีทั้งคู่ = แอปไม่ขึ้น)
"""
import json, pathlib

P = pathlib.Path(__file__).resolve().parent.parent / 'showhow-dev.json'
d = json.loads(P.read_text(encoding='utf-8'))

BOARD_OPS = ['mnBoard'] + [f'mnBoard{k}' for k in range(2, 7)]          # 1 → 6 (ลำดับที่ถูก)
VIDEO_OPS = [f'mnVideo{k}' for k in range(6, 1, -1)] + ['mnVideo']      # 6 → 1 (ตั้งใจ · ประตู "เสร็จ" อ่าน slots.video)
BOARD_OLD = list(reversed(BOARD_OPS))                                   # 6 → 1 (ของเดิมที่ผิด)
TARGET_KEYS = ('op', 'ops', 'chain', 'into', 'action', 'to', 'value', 'force')
SPAN = lambda k: f'{(k-1)*10}-{k*10} วิ'
GT = lambda n: {'op': 'gt', 'a': '{values.svSec}', 'b': n}              # ช่วง k โผล่เมื่อคลิปยาวพอจะมีช่วงนั้น


def part_when(k):
    """ช่วง 1 ใช้เกณฑ์เดียวกับช่วง 2 (>10) — ที่ 10 วิ มีช่วงเดียว ข้อ 'ทั้งหมด' ทำงานแทนอยู่แล้ว
       ถ้าปล่อยช่วง 1 ไม่มี when จะเหลือ 2 ข้อที่ให้ผลเหมือนกันเป๊ะที่ 10 วิ = เมนูเปิดทั้งที่ไม่มีอะไรให้เลือก"""
    return GT(10 if k <= 2 else 10 * (k - 1))


def retry_menu(kind):
    ops = BOARD_OPS if kind == 'board' else VIDEO_OPS
    icon = 'image' if kind == 'board' else 'movie'
    word = 'สตอรีบอร์ด' if kind == 'board' else 'คลิป'
    menu = [{'label': 'ทั้งหมด', 'desc': f'ทำ{word}ใหม่ทุกช่วง', 'icon': icon, 'chain': list(ops), 'force': True}]
    for k in range(1, 7):
        one = 'mnBoard' if (kind == 'board' and k == 1) else ('mnVideo' if (kind == 'video' and k == 1) else f'{"mnBoard" if kind=="board" else "mnVideo"}{k}')
        menu.append({'label': f'ช่วง {k} · {SPAN(k)}', 'desc': f'ทำเฉพาะ{word}ช่วงนี้ใหม่',
                     'icon': icon, 'chain': [one], 'force': True, 'when': part_when(k)})
    return menu


def pick_menu(kind):
    icon = 'image' if kind == 'board' else 'movie'
    word = 'ภาพ' if kind == 'board' else 'วิดีโอ'
    menu = []
    for k in range(1, 7):
        slot = kind if k == 1 else f'{kind}{k}'
        item = {'label': f'ใส่เป็นช่วง {k} · {SPAN(k)}', 'desc': f'แทน{word}ของช่วงนี้ด้วยไฟล์ที่เลือก',
                'icon': icon, 'into': slot}
        if k > 1: item['when'] = GT(10 * (k - 1))
        menu.append(item)
    return menu


targets = []                                                            # เก็บให้ครบก่อน แล้วค่อยแก้ (กัน RecursionError)
def walk(n):
    if isinstance(n, dict):
        el, chain, into = n.get('el'), n.get('chain'), n.get('into')
        if el == 'retry-button' and chain in (BOARD_OLD, BOARD_OPS):      targets.append((n, 'retry', 'board'))
        elif el == 'retry-button' and chain == VIDEO_OPS:                 targets.append((n, 'retry', 'video'))
        elif el == 'pick-button' and into == '{item.slots.board}':        targets.append((n, 'pick', 'board'))
        elif el == 'pick-button' and into == '{item.slots.video}':        targets.append((n, 'pick', 'video'))
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)

walk(d.get('phases'))
n_retry = sum(1 for _, kind, _ in targets if kind == 'retry')
n_pick = sum(1 for _, kind, _ in targets if kind == 'pick')
assert (n_retry, n_pick) == (7, 11), f'เจอ retry {n_retry} (คาด 7) · pick {n_pick} (คาด 11) — โครงเปลี่ยน หยุดก่อน'

for node, kind, media in targets:
    for k in TARGET_KEYS: node.pop(k, None)                              # ลบเป้าเดิมให้หมด ไม่งั้น validator ฟ้องตอน boot
    node['menu'] = retry_menu(media) if kind == 'retry' else pick_menu(media)

# ── ยามท้ายไฟล์ ────────────────────────────────────────────────────────
for node, kind, media in targets:
    assert not any(k in node for k in TARGET_KEYS), f'{node.get("label")}: ยังมีเป้าเดิมค้างที่ตัวปุ่ม'
    free = [m for m in node['menu'] if 'when' not in m]
    assert len(free) == 1, f'{node.get("label")}: มีข้อที่ไม่มี when {len(free)} ข้อ (ต้อง 1) — ที่ 10 วิ เมนูจะเปิดโดยไม่จำเป็น'
    for m in node['menu']:
        picked = [k for k in ('chain', 'op', 'ops', 'into', 'action') if k in m]
        assert len(picked) == 1, f'{node.get("label")} · {m["label"]}: เลือกเป้า {picked} (ต้อง 1 แบบ)'
        assert not any(ch.isdigit() for ch in str(m.get('desc', ''))), f'{m["label"]}: desc มีตัวเลข — engine นับสื่อให้เอง ห้ามเขียนเลขเอง'
# ยังมี chain บอร์ด 6→1 ค้างที่ปุ่ม gen (ตั้งใจไม่แตะรอบนี้) ⇒ ตรวจเฉพาะปุ่มที่เราแปลง
_old_json = json.dumps(BOARD_OLD, ensure_ascii=False)
for node, kind, media in targets:
    assert _old_json not in json.dumps(node['menu'], ensure_ascii=False), f'{node.get("label")}: เมนูยังมีลำดับบอร์ด 6→1'

P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'ใส่ menu: retry {n_retry} ปุ่ม (บอร์ด/วิดีโอ) · pick {n_pick} ปุ่ม · ข้อเมนูรวม {sum(len(t[0]["menu"]) for t in targets)}')
print('ลำดับบอร์ดในเมนู "ทั้งหมด" = 1→6 (แก้จากของเดิม 6→1) · วิดีโอ 6→1 ตามเดิม')
