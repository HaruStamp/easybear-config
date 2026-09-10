#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
minimal-v7-cliplen.py — เพิ่ม "ความยาวคลิป 10 / 20 / 30 วินาที" ให้ easybear-minimal (config ล้วน · ไม่แตะ engine)

──────────────────────────────────────────────────────────────────────────────
โจทย์จากพี่หมี:
  คลิปยาวกว่า 10 วิ ให้ **เขียนบทรอบเดียวยาว ๆ** แล้วสตอรีบอร์ดต่อกันเป็นเรื่องเดียวจบตามวินาทีที่เลือก
  เวลาสร้างวิดีโอ: ก้อนที่ 1 = ฉาก 1-5 · ก้อนที่ 2 = ฉาก 6-10 · เอาวิดีโอมาต่อกันตรง ๆ
  **ห้ามใช้เทคนิคแคปเฟรมท้ายมาต่อฉาก** — เพราะมินิมอลตัดภาพทุก 2 วิอยู่แล้ว รอยต่อจึงเนียนโดยธรรมชาติ

โครงที่เลือก (ทำไมถึงเลือกแบบนี้):
  ★ ไม่สร้าง collection ใหม่ · ไม่แตะ engine — ใช้ **หลายช่วงวิดีโอบน item เดียว** ที่ engine มีอยู่แล้ว
    (`el.segments` → app-handlers-a.mergeSegmentsPreview / downloadSegments · app-handlers-b zip · atoms-cases-a media-slot)
    ทีม hardsell ทำ 16 วิด้วยทางนี้มาก่อน ⇒ เส้นทางนี้ผ่านสนามจริงแล้ว
  ⇒ 1 task = 1 คลิปสุดท้ายเหมือนเดิม (การ์ด/แกลเลอรี/zip ไม่ต้องรื้อ)
    slots: board+video (ช่วง 1) · board2+video2 (ช่วง 2) · board3+video3 (ช่วง 3)
    ตอนดู/โหลด/แพ็ก engine รวมช่วงให้เอง (มี cache ต่อคลิป — ffmpeg ไม่รันซ้ำทุกคลิก)

  ★ โครงเรื่องยังเป็น **5 องก์คงที่** ตามสูตรมินิมอล — ความยาวแค่กำหนดว่า "องก์ละกี่ฉาก"
      10 วิ = องก์ละ 1 ฉาก (5 ฉาก)   20 วิ = องก์ละ 2 ฉาก (10 ฉาก)   30 วิ = องก์ละ 3 ฉาก (15 ฉาก)
    ⇒ ปุ่ม svCam1-5 / svPres1-5 ที่มีอยู่ยังใช้ได้เหมือนเดิม (คุมทั้งองก์) ไม่ต้องเพิ่มปุ่ม 15 ชุด

🪤 กติกาที่ยึดตลอดสคริปต์นี้ — **เส้นทาง 10 วิต้องได้ข้อความเดิมทุกตัวอักษร**
   ทุก lookup ที่เพิ่มมี `fallback` = ข้อความเดิมของ 10 วิ ⇒ ไฟล์เซฟเก่า (ไม่มี values.svSec) = พฤติกรรมเดิมเป๊ะ
   และ gate ใช้ `>` (whenMet แปลง '' เป็น 0) ⇒ ค่าหาย = 1 ช่วง ไม่ใช่ 3 ช่วง

รัน:  python3 scripts/minimal-v7-cliplen.py minimal-lab.json [minimal.json ...]
"""
import json, sys, copy, re, os

ACT_TH = ['Intro (Hero)', 'Feature', 'Lifestyle (การใช้จริง)', 'Versatility', 'CTA']
ACT_EN = ['Intro/Hero', 'Feature', 'Lifestyle', 'Versatility', 'CTA']
ACT_NAME_TH = ['เปิดตัว', 'จุดเด่น', 'ใช้จริง', 'หลากหลาย', 'ชวนซื้อ']
SUF_TH = ['', ' (ต่อ)', ' (ปิดองก์)']
SUF_EN = ['', ' (continued)', ' (closing beat)']
LENS = [10, 20, 30]


def scenes_of(sec):      return sec // 2          # 2 วิ/ฉาก เสมอ
def per_act(sec):        return sec // 10         # องก์ละกี่ฉาก
def segs_of(sec):        return sec // 10         # 1 ก้อนวิดีโอ = 10 วิ = 5 ฉาก


def lab_th(sec, n):
    """ป้ายแถวในสตอรีบอร์ด — เลขฉาก + ชื่อองก์ + ช่วงเวลา **ของทั้งคลิป** (บอร์ดคือเอกสาร ต้องเห็นเวลาจริง)"""
    k = per_act(sec)
    act, j = (n - 1) // k, (n - 1) % k
    return '%d. %s%s [%d-%ds]' % (n, ACT_TH[act], SUF_TH[j], (n - 1) * 2, n * 2)


def lab_en(sec, n):
    """ป้ายฉากใน prompt วิดีโอ — เวลานับใหม่ **ในก้อนของตัวเอง** (โมเดลสร้างทีละ 10 วิ ไทม์ไลน์ของมันเริ่ม 0 เสมอ)"""
    k = per_act(sec)
    act, j = (n - 1) // k, (n - 1) % k
    pos = (n - 1) % 5 + 1
    return 'Scene %d (%d-%ds) — %s%s' % (pos, (pos - 1) * 2, pos * 2, ACT_EN[act], SUF_EN[j])


# ─────────────────────────────────────────────────────────────────────────────
# helper: เดินทั้งต้นไม้ JSON แล้วแทนสตริง / ย้ายเลขฉาก
# ─────────────────────────────────────────────────────────────────────────────
RE_S = re.compile(r'\{item\.s(\d+)(th|en)\}')
RE_X = re.compile(r'\{item\.(ov|vo|cam)(\d+)\}')


def shift_scene_refs(node, off):
    """คัดลอกต้นไม้ prompt แล้วเลื่อนเลขฉากทุกที่ (s1th→s6th · ov1→ov6 · cam1→cam6 …)
       ★ทำแบบกลไกล้วน = ก้อนที่ 2/3 เป็น 'สำเนาที่เลื่อนดัชนี' ของก้อนที่ 1 เสมอ ไม่มีทางหลุดกันเอง
         (มีเทสประกอบใหม่แล้วเทียบว่าเป็นสำเนาจริง — ใครแก้ก้อน 1 อย่างเดียว เทสแดงทันที)"""
    if isinstance(node, str):
        node = RE_S.sub(lambda m: '{item.s%d%s}' % (int(m.group(1)) + off, m.group(2)), node)
        return RE_X.sub(lambda m: '{item.%s%d}' % (m.group(1), int(m.group(2)) + off), node)
    if isinstance(node, list):
        return [shift_scene_refs(x, off) for x in node]
    if isinstance(node, dict):
        return {k: shift_scene_refs(v, off) for k, v in node.items()}
    return node


def map_strings(node, fn):
    if isinstance(node, str):   return fn(node)
    if isinstance(node, list):  return [map_strings(x, fn) for x in node]
    if isinstance(node, dict):  return {k: map_strings(v, fn) for k, v in node.items()}
    return node


def find_op(cfg, oid):
    for o in cfg['ops']:
        if o['id'] == oid: return o
    raise SystemExit('ไม่เจอ op ' + oid)


def walk(node, path=''):
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items(): yield from walk(v, path + '.' + k)
    elif isinstance(node, list):
        for i, v in enumerate(node): yield from walk(v, '%s[%d]' % (path, i))


# ─────────────────────────────────────────────────────────────────────────────
def build_lookups(cfg):
    lk = cfg.setdefault('lookups', {})

    # ป้ายฉาก — key = "{svSec}|{n}" · ไม่เจอ key = fallback (ข้อความ 10 วิ เดิม) ⇒ ไฟล์เซฟเก่าไม่ขยับ
    lk['sceneLab'] = {'%d|%d' % (sec, n): lab_th(sec, n) for sec in LENS for n in range(1, scenes_of(sec) + 1)}
    lk['sceneEN'] = {'%d|%d' % (sec, n): lab_en(sec, n) for sec in LENS for n in range(1, scenes_of(sec) + 1)}

    # ── หัวคำสั่งระบบ (ส่วนที่ผูกกับความยาว) ────────────────────────────────
    head10 = ('คุณคือผู้กำกับโฆษณาสินค้าของพี่หมีแว่น ถ่ายทำด้วยสไตล์ภาพ "มินิมอลสแกนดิเนเวียน" '
              '(สไตล์นี้คือวิธีจัดภาพ แสง และองค์ประกอบ ไม่ใช่เนื้อหาของบทขาย) — '
              'ออกแบบคลิปโฆษณาสินค้าแนวตั้ง 9:16 ยาวประมาณ 10 วินาที เป็นช็อตเดียวต่อเนื่อง เดินผ่าน 5 ฉากคงที่ตามลำดับนี้เสมอ:\n'
              '1. Intro (Hero) 0-2s — โชว์สินค้าเป็นพระเอก องค์ประกอบสะอาดตา\n'
              '2. Feature 2-4s — close-up จุดเด่น 1 อย่างที่ผู้ใช้ระบุมา\n'
              '3. Lifestyle 4-6s — การใช้จริงในชีวิตประจำวัน\n'
              '4. Versatility 6-8s — ใช้ได้หลากหลายสถานการณ์\n'
              '5. CTA 8-10s — ปิดท้ายชวนซื้อ\n')

    def head_long(sec):
        k, ns = per_act(sec), scenes_of(sec)
        lines = []
        for a in range(5):
            first, last = a * k + 1, a * k + k
            lines.append('องก์ %d %s %d-%ds → ฉาก %d-%d — %s' % (
                a + 1, ACT_EN[a], a * k * 2, (a + 1) * k * 2, first, last,
                ['โชว์สินค้าเป็นพระเอก องค์ประกอบสะอาดตา',
                 'close-up จุดเด่นที่ผู้ใช้ระบุมา',
                 'การใช้จริงในชีวิตประจำวัน',
                 'ใช้ได้หลากหลายสถานการณ์',
                 'ปิดท้ายชวนซื้อ'][a]))
        cuts = ' · '.join('ก้อน %d = ฉาก %d-%d' % (i + 1, i * 5 + 1, i * 5 + 5) for i in range(segs_of(sec)))
        return ('คุณคือผู้กำกับโฆษณาสินค้าของพี่หมีแว่น ถ่ายทำด้วยสไตล์ภาพ "มินิมอลสแกนดิเนเวียน" '
                '(สไตล์นี้คือวิธีจัดภาพ แสง และองค์ประกอบ ไม่ใช่เนื้อหาของบทขาย) — '
                'ออกแบบคลิปโฆษณาสินค้าแนวตั้ง 9:16 ยาวประมาณ %d วินาที เป็นเรื่องเดียวต่อเนื่องจบในตัว '
                'เดินผ่าน 5 องก์คงที่ องก์ละ %d ฉาก ฉากละ 2 วินาที รวม %d ฉาก เรียงตามลำดับนี้เสมอ:\n%s\n'
                '★ เรื่องต้องจบสมบูรณ์ภายใน %d วินาที — ฉาก %d คือฉากปิด ห้ามค้างคาหรือเล่าไม่จบ\n'
                '★ ทุกฉากคือคลิปเดียวกัน เล่าต่อเนื่องกันไปข้างหน้า ห้ามเริ่มเรื่องใหม่กลางทาง '
                'ห้ามแนะนำสินค้าซ้ำ และห้ามใส่ฉากปิดชวนซื้อก่อนองก์ 5\n'
                '★ ตอนถ่ายจริงคลิปนี้จะถูกสร้างเป็น %d ก้อน ก้อนละ 5 ฉาก (%s) แล้วนำมาต่อกัน — '
                'ทุกก้อนต้องเป็นสถานที่เดียวกัน แสงเดียวกัน โทนสีเดียวกัน สินค้าชิ้นเดิม และคนคนเดิม\n'
                % (sec, k, ns, '\n'.join(lines), sec, ns, segs_of(sec), cuts))

    lk['lenSys'] = {'10': head10, '20': head_long(20), '30': head_long(30)}

    # ── รูปแบบ Output (คีย์ JSON ตามจำนวนฉาก) ───────────────────────────────
    def out_block(sec):
        ns = scenes_of(sec)
        keys = ''.join(',"s%dth":"...","s%den":"...","ov%d":"...","vo%d":"...","cam%d":"..."' % (n, n, n, n, n)
                       for n in range(1, ns + 1))
        # 🪤 ประโยคย้ำ "ครบทุกฉาก" ใส่เฉพาะ 20/30 วิ — ★10 วิ ต้องเหมือนของเดิมทุกตัวอักษร
        #    (คลิปสั้นไม่เคยมีปัญหาฉากขาด · เพิ่มคำใหม่เข้าไป = เส้นทางที่ลูกค้าใช้อยู่เปลี่ยนโดยไม่จำเป็น)
        insist = '' if sec == 10 else 'แต่ละ object ต้องมีครบทั้ง %d ฉาก ห้ามขาดฉากใดฉากหนึ่ง ' % ns
        return ('Output: ตอบเป็น JSON array ล้วน ห้ามมี markdown ห้ามมีข้อความอื่นนอก JSON · '
                'จำนวน object ในอาร์เรย์ = จำนวนคลิปที่ขอ (ขอ 1 คลิปก็ต้องเป็น array ที่มี 1 object) '
                + insist + 'รูปแบบแต่ละ object:\n'
                '{"productName":"ชื่อสินค้า คัดลอกตรงตามที่ให้มา","category":"หมวดสินค้า",'
                '"palette":"ชื่อโทนสีสั้นๆ เช่น ชมพู-ส้ม","synopsis":"เรื่องย่อคลิป 1-2 ประโยค ภาษาไทย",'
                '"voice":"หญิง หรือ ชาย — เพศเสียงพากย์ของคลิปนี้"%s}\n\n'
                'กฎ overlay เพิ่มเติม: ovN ทุกตัวเป็นภาษาไทย บรรทัดเดียว ไม่เกิน 5 คำ ห้ามใส่เลขฉาก/ลิสต์'
                % keys)
    lk['lenOut'] = {str(s): out_block(s) for s in LENS}

    # ── บล็อก "ข้อกำหนดรายองก์" ในคำสั่งงาน ─────────────────────────────────
    # 🔴 ค่าที่คืนจาก lookup **ไม่ถูก resolve ซ้ำ** — ใส่ {values.svCam1} ไว้ในตารางแล้วมันจะโผล่เป็นตัวหนังสือดิบ
    #    (เจอจริงตอนเขียนสคริปต์นี้ · เทสข้อ ① จับได้) ⇒ ตารางเก็บได้แค่ **ป้ายหัวแถว** ส่วน {values.*} ต้องอยู่นอกตาราง
    #    กติกาเดียวกับที่ CLAUDE.md เตือนไว้ว่า "เลี่ยง lookup ซ้อนใน string template"
    lk['lenActHead'] = {'10': '\n\nข้อกำหนดรายฉากจากผู้ใช้ (ค่าว่าง = ออกแบบเอง):\n'}
    lk['lenActTail'] = {'10': ''}
    for sec in (20, 30):
        lk['lenActHead'][str(sec)] = '\n\nข้อกำหนดรายองก์จากผู้ใช้ (ค่าว่าง = ออกแบบเอง) — ใช้กับทุกฉากในองก์นั้น:\n'
        lk['lenActTail'][str(sec)] = ('ฉากในองก์เดียวกันต้องใช้มุมกล้องที่ผู้ใช้ล็อกไว้เหมือนกัน '
                                      'แต่เปลี่ยนระยะ การเคลื่อนไหว และองค์ประกอบให้ไม่ซ้ำกัน\n')
    lk['lenAct'] = {}
    for a in range(5):
        lk['lenAct']['10|%d' % (a + 1)] = 'ฉาก %d %s' % (a + 1, ACT_NAME_TH[a])
        for sec in (20, 30):
            k = per_act(sec)
            lk['lenAct']['%d|%d' % (sec, a + 1)] = 'องก์ %d %s (ฉาก %d-%d)' % (a + 1, ACT_NAME_TH[a], a * k + 1, a * k + k)

    # ── ข้อความ UI ─────────────────────────────────────────────────────────
    lk['lenLabel'] = {'10': '10 วินาที', '20': '20 วินาที', '30': '30 วินาที'}
    lk['lenSecs'] = {str(x): str(x) for x in LENS}   # เลขล้วน ไว้ประกอบป้ายบนหน้าจอ
    lk['lenScenes'] = {str(s): str(scenes_of(s)) for s in LENS}
    return lk


# ─────────────────────────────────────────────────────────────────────────────
def patch_collections(cfg):
    t = cfg['collections']['tasks']
    want = []
    for n in range(1, 16): want += ['s%dth' % n, 's%den' % n]
    for pre in ('ov', 'vo', 'cam'):
        for n in range(1, 16): want.append('%s%d' % (pre, n))
    for f in want:
        if f not in t['fields']: t['fields'].append(f)
    for s in ('board2', 'board3', 'video2', 'video3'):
        if s not in t['slots']: t['slots'].append(s)


def patch_values(cfg):
    # 10 = ค่าเริ่มต้น · ไฟล์เซฟเก่าไม่มีคีย์นี้ → whenMet อ่านเป็น 0 → ทุก gate '>' เป็นเท็จ = 1 ช่วง (เหมือนเดิม)
    cfg.setdefault('values', {}).setdefault('svSec', '10')


def patch_queue(cfg):
    """mnQueue ต้องยกฟิลด์ฉาก 6-15 ตามมาด้วย — ฉากที่แผนไม่มี resolve เป็นค่าว่าง (ไม่พัง)"""
    q = find_op(cfg, 'mnQueue')
    f = q['spawn']['fields']
    for n in range(6, 16):
        for key in ('s%dth' % n, 's%den' % n, 'ov%d' % n, 'vo%d' % n, 'cam%d' % n):
            f.setdefault(key, '{item.fields.%s}' % key)


def patch_plan(cfg):
    """mnPlan: หัวคำสั่งระบบ + รูปแบบ Output + บล็อกรายองก์ → ผูกกับ values.svSec"""
    lk = cfg['lookups']
    op = find_op(cfg, 'mnPlan')
    sys_txt = cfg['brain']['mn']['sys']

    head_mark = '\n\nขั้นตอนคิด (ห้ามพิมพ์ขั้นตอนนี้ออกมา):'
    out_mark = '\n\nOutput: ตอบเป็น JSON array ล้วน'
    assert head_mark in sys_txt and out_mark in sys_txt, 'sys เปลี่ยนโครง — หาจุดตัดไม่เจอ'
    body = sys_txt.split(head_mark, 1)[1].split(out_mark, 1)[0]
    head_old = sys_txt.split(head_mark, 1)[0] + '\n'
    out_old = out_mark.lstrip('\n') + sys_txt.split(out_mark, 1)[1]
    assert head_old == lk['lenSys']['10'], 'ข้อความหัว 10 วิ ไม่ตรงของเดิม — เส้นทาง 10 วิ จะเปลี่ยน'
    assert out_old == lk['lenOut']['10'], 'ข้อความ Output 10 วิ ไม่ตรงของเดิม'

    # ★ ตัวกลาง (ไม่ผูกความยาว) ยังอยู่ที่ brain.mn.sys เหมือนเดิม — เปลี่ยนเฉพาะขอบเขต
    cfg['brain']['mn']['sys'] = head_mark.lstrip('\n') + body
    op['systemInstruction'] = {'op': 'concat', 'parts': [
        {'op': 'lookup', 'table': 'lenSys', 'key': '{values.svSec}', 'fallback': lk['lenSys']['10']},
        '\n', '{brain.mn.sys}', '\n\n',
        {'op': 'lookup', 'table': 'lenOut', 'key': '{values.svSec}', 'fallback': lk['lenOut']['10']},
    ]}

    # บล็อกรายฉาก → หัวแถวมาจาก lookup · {values.svCam*}/{values.svPres*} ยังอยู่นอกตาราง (ดูเหตุผลใน build_lookups)
    parts = op['prompt']['parts']
    hit = 0
    for i, p in enumerate(parts):
        if isinstance(p, str) and 'ข้อกำหนดรายฉากจากผู้ใช้ (ค่าว่าง = ออกแบบเอง):' in p:
            mk = scene_marker(p)
            assert mk is not None, 'บล็อกรายฉากใน mnPlan เปลี่ยนโครง'
            a, b = mk
            old = p[a:b]
            rows: list = [{'op': 'lookup', 'table': 'lenActHead', 'key': '{values.svSec}', 'fallback': lk['lenActHead']['10']}]
            for n in range(1, 6):
                rows.append({'op': 'lookup', 'table': 'lenAct', 'key': '{values.svSec}|%d' % n, 'fallback': lk['lenAct']['10|%d' % n]})
                rows.append(' — มุมกล้อง: {values.svCam%d} · การนำเสนอ: {values.svPres%d}\n' % (n, n))
            rows.append({'op': 'lookup', 'table': 'lenActTail', 'key': '{values.svSec}', 'fallback': ''})
            # ★พิสูจน์ว่าเส้นทาง 10 วิ ประกอบกลับได้ตัวอักษรเดิมเป๊ะ ก่อนจะยอมเขียนทับ
            rebuilt = lk['lenActHead']['10'] + ''.join(
                lk['lenAct']['10|%d' % n] + ' — มุมกล้อง: {values.svCam%d} · การนำเสนอ: {values.svPres%d}\n' % (n, n)
                for n in range(1, 6))
            assert rebuilt == old, 'ประกอบบล็อกรายฉาก 10 วิ กลับแล้วไม่ตรงของเดิม'
            parts[i] = {'op': 'concat', 'parts': [p[:a]] + rows + [p[b:]]}
            hit += 1
    assert hit == 1, 'หาบล็อกรายฉากใน mnPlan ได้ %d จุด (ต้อง 1)' % hit

    op['logRun'] = {'op': 'concat', 'parts': [
        '[{item.name}] หมีกำลังคิดบท {values.clipsPerProduct} คลิป (',
        {'op': 'lookup', 'table': 'lenScenes', 'key': '{values.svSec}', 'fallback': '5'},
        ' ฉาก/คลิป · ',
        {'op': 'lookup', 'table': 'lenLabel', 'key': '{values.svSec}', 'fallback': '10 วินาที'},
        ')']}


def scene_marker(p):
    a = p.find('\n\nข้อกำหนดรายฉากจากผู้ใช้ (ค่าว่าง = ออกแบบเอง):')
    if a < 0: return None
    end = p.find('ฉาก 5 ชวนซื้อ — มุมกล้อง: {values.svCam5} · การนำเสนอ: {values.svPres5}\n')
    if end < 0: return None
    return a, end + len('ฉาก 5 ชวนซื้อ — มุมกล้อง: {values.svCam5} · การนำเสนอ: {values.svPres5}\n')


# ─────────────────────────────────────────────────────────────────────────────
def labelize(cfg, op, kind):
    """เปลี่ยนป้ายฉากที่ฮาร์ดโค้ดไว้ในprompt → lookup ที่ขึ้นกับความยาว
       kind='th' (บอร์ด: เลขฉาก+ช่วงเวลาของทั้งคลิป) · 'en' (วิดีโอ: เวลานับใหม่ในก้อนตัวเอง)"""
    tbl = 'sceneLab' if kind == 'th' else 'sceneEN'
    lk = cfg['lookups'][tbl]
    pats = [(n, lab_th(10, n) if kind == 'th' else lab_en(10, n)) for n in range(1, 6)]
    done = set()

    def fix(s):
        for n, lit in pats:
            if lit in s and n not in done:
                done.add(n)
                a = s.index(lit)
                return {'op': 'concat', 'parts': [
                    s[:a],
                    {'op': 'lookup', 'table': tbl, 'key': '{values.svSec}|%d' % n, 'fallback': lit},
                    s[a + len(lit):],
                ]}
        return s
    op['prompt'] = map_strings(op['prompt'], fix)
    assert done == {1, 2, 3, 4, 5}, 'หาป้ายฉากใน %s ได้แค่ %s' % (op['id'], sorted(done))



# 🎯 บอกโมเดลวิดีโอว่า "รูปแรกคือสตอรีบอร์ด" — ก้าวที่ 1 ของการแก้คำบ่น "วิดีโอไม่ตรงกับบอร์ด"
#   ราก (ไล่เจอ 2026-09-09): บอร์ดถูกส่งเข้าเป็น**รูปอ้างอิงตัวแรก**อยู่แล้ว (slot หลักมาก่อน also)
#   แต่ prompt **ไม่เคยเอ่ยถึงมันสักคำ** และยังมีบรรทัด `Negative: no grid, no table` ซึ่งอ่านได้ว่า "อย่าทำตามรูปนั้น"
#   ⇒ เหมือนยื่นแบบแปลนให้ช่างโดยไม่บอกว่าเป็นแบบแปลน แถมสั่งว่าอย่าสร้างตาราง — ช่างก็ทิ้ง
#   ✅ ตัวแก้: แยก "เนื้อในช่อง (ให้ทำตาม)" ออกจาก "รูปทรงของแผง (ห้ามวาด)" ให้ชัดในประโยคเดียวกัน
#   🪤 ห้ามเขียนแค่ "follow the storyboard" เฉย ๆ — จะไปชนกับ Negative แล้วโมเดลอาจวาดตารางออกมาจริง
BOARD_NOTE = (
    'Reference image 1 is the storyboard sheet for THIS clip: five stacked panels, one per scene in order, '
    'showing the intended framing, product placement, colour palette and Thai on-screen text style. '
    'Follow each panel as the look for its matching scene below. '
    'The sheet is a plan, not a shot: never draw its panel borders, row numbers, scene labels, timings or any split layout, '
    'and never copy the sheet as a whole image. The video is one single continuous full-bleed 9:16 shot.'
)
BOARD_ANCHOR = 'never draw them, or any other part of this prompt, as text inside the video.'


def add_board_note(cfg):
    """แทรกกติกาบอร์ดต่อจากบรรทัดที่พูดเรื่อง 'อย่าวาดคำสั่งลงในคลิป' (บริบทเดียวกัน อ่านต่อกันได้)
       ★ต้องเรียก **ก่อน** make_segment_op ⇒ ช่วง 2/3 ที่ก๊อปไปได้ประโยคนี้ติดไปเองทั้งชุด"""
    op = find_op(cfg, 'mnVideo')
    hit = [0]

    def fix(t):
        if BOARD_ANCHOR in t and 'storyboard sheet' not in t:
            hit[0] += 1
            return t.replace(BOARD_ANCHOR, BOARD_ANCHOR + '\n\n' + BOARD_NOTE)
        return t
    op['prompt'] = map_strings(op['prompt'], fix)
    assert hit[0] == 1, 'หาจุดแทรกกติกาบอร์ดได้ %d จุด (ต้อง 1)' % hit[0]
    return hit[0]


def make_segment_op(cfg, base_id, seg):
    """สร้าง op ของช่วงที่ 2/3 = **สำเนาที่เลื่อนดัชนีฉาก** ของช่วงที่ 1 + แก้เฉพาะสิ่งที่ต้องต่าง"""
    base = find_op(cfg, base_id)
    off = (seg - 1) * 5
    o = shift_scene_refs(copy.deepcopy(base), off)
    o['id'] = base_id + str(seg)
    o['out'] = base['out'] + str(seg)
    o['when'] = 'values.svSec>%d' % ((seg - 1) * 10)      # 10 วิ (หรือค่าหาย=0) → เท็จ = ไม่มีช่วงนี้
    # ป้ายฉาก: key ของ lookup ต้องเลื่อนตามด้วย (shift_scene_refs แตะเฉพาะ {item.*})
    o['prompt'] = map_strings(o['prompt'], lambda s: s)
    _shift_label_keys(o, off)

    if base_id == 'mnBoard':
        o['prompt'] = map_strings(o['prompt'], lambda s: _board_seg_text(s, seg, off))
        # 🎯 ให้บอร์ดช่วงนี้ **เห็นบอร์ดที่ผลิตไปแล้ว** — ไม่งั้นมันเจนแยกกันคนละครั้ง แสง/ฉากหลัง/โทนหลุดกันได้
        #   (พิสูจน์แล้วว่าโมเดลวิดีโอตามบอร์ด 80-90% ⇒ บอร์ดที่หลุดโทนกัน = คลิปหลุดโทนตาม)
        #   ★ต่อท้าย also ⇒ รูปสินค้ายังเป็นตัวหลัก (product fidelity เป็น hard lock ของแอปนี้ ห้ามลดชั้น)
        #
        # 🔴🔴 ต้องอ้าง "ช่วงที่ผลิตไปแล้ว" ไม่ใช่ "ช่วงก่อนหน้าตามเลข" — ผมเขียนผิดทางนี้มาแล้ว 1 รอบ
        #   ลำดับ op คือ mnBoard3 → mnBoard2 → mnBoard (ช่วงท้ายก่อน · ห้ามสลับ ดูกฎข้างบน)
        #   ⇒ ตอน mnBoard2 ทำงาน slot `board` **ยังว่าง** · lookupRefs กรอง slot ว่างทิ้ง**เงียบ**
        #   ⇒ ได้ config ที่หน้าตาเหมือนมีความต่อเนื่อง แต่ไม่เคยแนบรูปสักใบ **และไม่มี error ให้เห็นเลย**
        #   ✅ สไตล์/แสง/ฉากหลังเป็นของ **สมมาตร** (ใครตามใครก็ได้ ขอให้ชุดเดียวกัน) ⇒ กลับทางแล้วไม่เสียอะไร
        # ★ช่วง 3 ผลิต **เป็นใบแรก** ⇒ ยังไม่มีอะไรให้อ้าง — ต้องข้าม ไม่ใช่ไปอ้าง board2 ที่ยังว่าง
        #   (เทสจับได้จริงตอนแก้: 'บอร์ดใบแรกที่ผลิตไม่อ้างบอร์ดใคร')
        prev = 'board3' if seg == 2 else None
        if prev:
            o['refs'] = copy.deepcopy(o['refs'])
            # 🪤 ประตูรายตัว: ที่ 20 วิ ช่วง 3 ไม่ถูกผลิตเลย ⇒ ref นี้จะชี้ slot ว่าง (ถูกกรองทิ้งเงียบ ไม่พังแต่ก็ไม่ควรมี)
            #   ใส่ประตูให้ตรงกับ "ช่วงนั้นถูกผลิตจริงไหม" — เจตนาอ่านออกจาก config ไม่ต้องไปนึกเอง
            o['refs'].setdefault('also', []).append({'from': 'tasks', 'by': '{item.id}', 'slot': prev, 'when': 'values.svSec>20'})
            o['prompt'] = map_strings(o['prompt'], lambda s: _board_prev_note(s, seg))
        o['logRun'] = '[{item.productName} คลิป {item.clipIndex}] กำลังวาดสตอรีบอร์ดช่วงที่ %d' % seg
        o['logDone'] = '[{item.productName} คลิป {item.clipIndex}] สตอรีบอร์ดช่วงที่ %d เสร็จแล้ว' % seg
    else:
        o['prompt'] = _video_seg_prompt(o['prompt'], seg, off)
        o['refs'] = json.loads(json.dumps(base['refs']).replace('"slot": "board"', '"slot": "board%d"' % seg))
        o['logRun'] = '[{item.productName} คลิป {item.clipIndex}] กำลังสร้างวิดีโอช่วงที่ %d (10 วิ)' % seg
        o['logDone'] = '[{item.productName} คลิป {item.clipIndex}] วิดีโอช่วงที่ %d เสร็จแล้ว' % seg
    return o


def _shift_label_keys(node, off):
    """เลื่อนคีย์ของ lookup ป้ายฉาก ('{values.svSec}|3' → '|8') ในที่ (in place)"""
    for _, n in walk(node):
        if isinstance(n, dict) and n.get('op') == 'lookup' and n.get('table') in ('sceneLab', 'sceneEN'):
            m = re.match(r'^\{values\.svSec\}\|(\d+)$', str(n.get('key', '')))
            if m:
                old = int(m.group(1))
                n['key'] = '{values.svSec}|%d' % (old + off)
                n['fallback'] = ''      # ช่วง 2/3 มีได้เฉพาะตอน svSec>10 ⇒ ไม่มีทางตกมา fallback


def _board_seg1_continuity(cfg):
    """ช่วงที่ 1 ผลิต **ท้ายสุด** ⇒ เห็นบอร์ดช่วง 3 (หมุด) + ช่วง 2 (ตัวก่อนหน้า) ได้จริงทั้งคู่
    🪤 ต้อง gate ราย entry ด้วย svSec — คลิป 10 วิ ไม่มี board2/board3 · `also` รองรับ `when` รายตัว
       (ไม่ gate ก็ไม่พัง เพราะ slot ว่างถูกกรองทิ้ง แต่ gate ไว้ = เจตนาอ่านออกจาก config)"""
    o = next(x for x in cfg['ops'] if x['id'] == 'mnBoard')
    also = o.setdefault('refs', {}).setdefault('also', [])
    for slot, sec in (('board3', 20), ('board2', 10)):   # หมุดก่อน แล้วตัวที่ผลิตติดกันอยู่ท้าย = โมเดลเห็นเป็นตัวล่าสุด
        also.append({'from': 'tasks', 'by': '{item.id}', 'slot': slot, 'when': 'values.svSec>%d' % sec})
    o['prompt'] = map_strings(o['prompt'], lambda s: _board_prev_note(s, 1))
    return 1


def _board_prev_note(s, seg):
    """บอกโมเดลภาพว่ารูปสุดท้ายคือบอร์ดช่วงก่อนหน้า ให้ยึดโทนตาม — แทรกต่อจากกติกาสไตล์ภาพรวม"""
    anchor = 'กติกาสำคัญ: ใช้ "สินค้าที่แนบมา" เป็นต้นแบบ'
    if anchor not in s or 'บอร์ดของช่วงอื่นในคลิปเดียวกัน' in s: return s
    add = ('กติกาความต่อเนื่อง: **ถ้ามี**บอร์ดของช่วงอื่นในคลิปเดียวกันแนบมาด้วย (รูปท้าย ๆ) — '
           'ต้องใช้โทนสี แสง ฉากหลัง พื้นผิว และสไตล์ตัวหนังสือชุดเดียวกันกับบอร์ดนั้นทุกประการ '
           'เพื่อให้คลิปที่ต่อกันดูเป็นคลิปเดียว · แต่ **ห้ามลอกภาพในช่องมาซ้ำ** — ฉากในแผงนี้เป็นฉากของตัวเองตามบทด้านล่าง\n\n')
    return s.replace(anchor, add + anchor, 1)


def _board_seg_text(s, seg, off):
    a, b = off + 1, off + 5
    s = s.replace('สร้างแผงสตอรีบอร์ด 5 ช่อง สำหรับโฆษณาสินค้า',
                  'สร้างแผงสตอรีบอร์ด 5 ช่อง (ช่วงที่ %d ของคลิป — ฉาก %d ถึง %d) สำหรับโฆษณาสินค้า' % (seg, a, b))
    s = s.replace('ฉาก 1,2,3,4,5 ครบทุกฉากตามลำดับ',
                  'ฉาก %d,%d,%d,%d,%d ครบทุกฉากตามลำดับ' % (a, a + 1, a + 2, a + 3, b))
    return s


def _video_seg_prompt(prompt, seg, off):
    """แทรกกติกา 'ต่อจากก้อนก่อนหน้า' ต้นprompt — เนื้อหาที่เหลือเป็นสำเนาเลื่อนดัชนีล้วน"""
    cont = ('CONTINUATION SHOT — this is part %d of a single longer commercial. '
            'It continues directly from the previous 10 seconds, same story, same take. '
            'Same product, same set, same background, same lighting, same colour palette and the same person as before. '
            'Do NOT re-introduce the product, do NOT restart the story, do NOT add an ending unless these are the final scenes. '
            'Start exactly where the previous part left off.\n\n' % seg)
    p = copy.deepcopy(prompt)
    p['parts'] = [cont] + p['parts']
    return p


def patch_ops(cfg):
    labelize(cfg, find_op(cfg, 'mnBoard'), 'th')
    labelize(cfg, find_op(cfg, 'mnVideo'), 'en')
    add_board_note(cfg)      # ★ก่อน make_segment_op — ช่วง 2/3 จะได้ติดไปด้วย
    new = [make_segment_op(cfg, 'mnBoard', 2), make_segment_op(cfg, 'mnBoard', 3),
           make_segment_op(cfg, 'mnVideo', 2), make_segment_op(cfg, 'mnVideo', 3)]
    have = {o['id'] for o in cfg['ops']}
    for o in new:
        if o['id'] in have: cfg['ops'] = [x for x in cfg['ops'] if x['id'] != o['id']]
    # ⭐ เรียง **ช่วงท้ายก่อน** (board3 → board2 → board · video3 → video2 → video)
    #   เหตุผลที่ไม่ใช่ความสวยงาม: ทั้งแอปมีเงื่อนไข "คลิปนี้เสร็จหรือยัง" กระจายอยู่หลายที่
    #   (แกลเลอรี repeat where slots.video!= · zip · ประตูปุ่มวิดีโอ · หน้า derived · การ์ดสถานะ)
    #   ถ้าช่วงที่ 1 เสร็จก่อน slots.video จะไม่ว่างตั้งแต่ยังทำไม่ครบ ⇒ **ทุกที่พร้อมใจกันโกหกว่าเสร็จแล้ว**
    #   และลูกค้าจะกดโหลดได้คลิป 10 วิ ทั้งที่สั่ง 30 วิ โดยไม่มีใครเตือน
    #   ⇒ กลับลำดับให้ช่วงที่ 1 เป็นตัวสุดท้ายที่เติม ⇒ `slots.video != ''` แปลว่า "ครบทุกช่วง" โดยอัตโนมัติ
    #     ทุกเงื่อนไขเดิมในแอปจึงถูกต้องทันทีโดยไม่ต้องไล่แก้สักจุด (และไม่ต้องพึ่งความจำของคนที่มาแก้ทีหลัง)
    #   🪤 ห้ามสลับกลับเป็นลำดับ 1→2→3 ถ้าไม่ได้แก้ทุกเงื่อนไข "เสร็จหรือยัง" ให้ดูช่วงสุดท้ายแทน
    order = ['mnPlan', 'mnQueue', 'mnBoard3', 'mnBoard2', 'mnBoard', 'mnVideo3', 'mnVideo2', 'mnVideo']
    by = {o['id']: o for o in cfg['ops']}
    for o in new: by[o['id']] = o
    cfg['ops'] = [by[i] for i in order if i in by] + [o for o in cfg['ops'] if o['id'] not in order]
    # ⚠️ ทีม hardsell ทักว่า "ความถูกต้องผูกกับลำดับที่มองไม่เห็นในโค้ด = เปราะ" — จริง
    #   คนที่มาอ่านทีหลังจะนึกว่าเรียงมั่วแล้ว "จัดระเบียบ" ให้เป็น 1→2→3 ⇒ แอปพังเงียบ ไม่มี error
    #   ⇒ เขียนเหตุผลไว้ **ตรงจุดที่คนจะไปแก้** (engine อ่านแค่ s.op — คีย์อื่นถูกมองข้าม)
    #   🪤 ถ้าวันไหนเพิ่ม field สถานะจริง (แบบที่ hardsell ใช้) ต้องลบโน้ตนี้ด้วย ไม่งั้นกลายเป็นคำเตือนที่หมดอายุ
    WHY = ('★ลำดับนี้ตั้งใจกลับด้าน — ช่วงท้ายต้องเสร็จก่อน ห้ามเรียงเป็น 1→2→3 '
           'เพราะทั้งแอปตัดสิน "คลิปเสร็จหรือยัง" จาก slots.video ของช่วงแรก '
           '(แกลเลอรี · zip · ประตูปุ่ม · หน้า derived) ⇒ สลับแล้วจะบอกว่าเสร็จตั้งแต่ได้ 10 วิแรก โดยไม่มี error')
    cfg['stages'] = [({'op': i, '__why': WHY} if i in ('mnBoard3', 'mnVideo3') else {'op': i}) for i in order] \
        + [s for s in cfg['stages'] if 'checkpoint' in s]


# ─────────────────────────────────────────────────────────────────────────────
SEGS = [{'slot': 'video'}, {'slot': 'video2'}, {'slot': 'video3'}]


LBL_CLS = ('!text-[13px] @[640px]:!text-[12.5px] !text-[var(--ev-text)] opacity-65 '
           'uppercase tracking-[0.14em] font-black px-0.5')
SUB_CLS = '!text-[15px] @[640px]:!text-[14px] opacity-70 px-0.5'


def field_label(icon, text):
    """ป้ายหัวช่อง = ไอคอนนำหน้า + ข้อความ (แบบเดียวกับ FieldLabel ของ hardsell · พี่หมีสั่ง 2026-09-09)
       ★ใช้ชุด class ของ minimal เอง ไม่ลอก class ของ hardsell มา — เอาแค่ 'ทรง' ไม่เอาธีม"""
    return {'el': 'row', 'className': 'items-center gap-1.5 px-0.5', 'style': {'flexWrap': 'nowrap'}, 'card': [
        {'el': 'icon', 'icon': icon, 'textSize': 'text-[16px]',
         'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center opacity-80 shrink-0'},
        {'el': 'text', 'value': text, 'className': LBL_CLS + ' !px-0'},
    ]}


# ⚡ เครดิตที่โมเดลวิดีโอกินต่อ 1 ช่วง (10 วินาที) — ตัวเลขจากพี่หมี · แก้ที่นี่ที่เดียวแล้วการ์ดคิดใหม่เอง
CREDIT_PER_SEG = 15
SEG_COUNT = {'op': 'div', 'a': '{values.svSec}', 'b': 10}                  # จำนวนช่วง = วินาที / 10
#   🪤 ห้ามตั้งชื่อว่า SEGS — ชนกับ SEGS ที่เป็นรายชื่อ slot ของ el.segments (เคยชนจริง: ทางออกวิดีโอ 8 จุด
#      กลายเป็นสูตรหารแทนรายชื่อ slot = การรวมคลิปพังทั้งแอป · เทสข้อ ⑥ จับได้)
CREDIT_TOTAL = {'op': 'mul', 'a': CREDIT_PER_SEG, 'b': dict(SEG_COUNT)}    # เครดิตรวมต่อคลิป


def credit_card():
    """การ์ดเตือนเครดิต — โผล่เฉพาะตอนเลือก 20/30 วิ (พี่หมีสั่ง 2026-09-09)
       ★ตัวเลขคำนวณจาก values.svSec ทั้งหมด ไม่ได้พิมพ์ค่าตายตัว ⇒ เพิ่มความยาวใหม่วันหลังการ์ดถูกเอง
       ใช้ทรงการ์ดเตือนสีเหลืองที่แอปนี้ใช้อยู่แล้ว (ชุดเดียวกับ 'ยังไม่มีรูปใบหน้า')"""
    return {'el': 'row', 'when': 'values.svSec>10',
            'className': ('items-center gap-3.5 bg-amber-500/[0.07] border border-amber-500/25 '
                          'rounded-2xl p-3 @[420px]:p-4 mt-0.5'),
            'style': {'flexWrap': 'nowrap'}, 'card': [
        {'el': 'box', 'className': 'w-[42px] h-[42px] rounded-xl bg-amber-500/[0.14] flex items-center justify-center shrink-0',
         'card': [{'el': 'icon', 'icon': 'bolt', 'textSize': 'text-[20px]',
                   'className': '!text-amber-500 leading-none flex items-center justify-center'}]},
        {'el': 'box', 'className': 'flex-1 min-w-0 flex flex-col gap-0.5', 'card': [
            {'el': 'text', 'className': '!text-[16px] @[640px]:!text-[15px] font-bold !text-amber-600',
             'value': {'op': 'concat', 'parts': [
                 'คลิป ', '{values.svSec}', ' วินาที ใช้เครดิต ', dict(SEG_COUNT), ' เท่า']}},
            {'el': 'text', 'className': '!text-[14px] @[640px]:!text-[13px] !text-amber-600 opacity-80 leading-relaxed',
             'value': {'op': 'concat', 'parts': [
                 str(CREDIT_PER_SEG), ' เครดิต × ', dict(SEG_COUNT), ' ช่วง = ', dict(CREDIT_TOTAL),
                 ' เครดิต ต่อ 1 คลิป · ทำหลายคลิปคูณเพิ่มตามจำนวน']}},
        ]},
    ]}


def len_picker():
    """ความยาวคลิป — toggle สั้น ๆ 10/20/30 วิ (พี่หมีสั่งให้ทำแบบ hardsell)
       ไม่มีคำอธิบายใต้ toggle · มีแต่การ์ดเตือนเครดิตที่โผล่เฉพาะตอนเลือก 20/30 วิ"""
    return {'el': 'box', 'className': 'flex flex-col gap-1.5', 'card': [
        field_label('timer', 'ความยาวคลิป'),
        # ★การ์ดเดียว 3 ตัวเลือก ทรงเดียวกับ "สไตล์ตัวอักษร" (พี่หมีสั่ง) — `contained` = กรอบเดียวครอบทั้งชุด
        #   🪤 ไม่ตั้ง mobile.cols = 1 เหมือนสไตล์ตัวอักษร เพราะป้ายสั้น ("10 วิ") 3 ช่องเรียงแถวเดียวได้แม้จอ 390
        {'el': 'grid-select', 'field': 'svSec', 'cols': 3, 'contained': True,
         # ★2 บรรทัดต่อตัวเลือก: label = ความยาว · desc = เครดิต (พี่หมีสั่ง — บอกราคาในปุ่มเลย ดีกว่ามีการ์ดเตือนแยก)
         #   เลขเครดิตคิดจาก CREDIT_PER_SEG ที่เดียว ⇒ แก้ค่าเดียวแล้วทั้ง 3 ตัวเลือกถูกพร้อมกัน
         'options': [{'value': str(sec), 'label': '%d วิ' % sec,
                      'desc': 'ใช้ %d เครดิต' % (CREDIT_PER_SEG * segs_of(sec))} for sec in LENS],
         'className': '!min-h-[48px] @[420px]:!min-h-0'},
    ]}



def patch_ui(cfg):
    """UI: ทางออกวิดีโอต้องรวมช่วง · ปุ่มรันต้องเรียก op ครบ · ปุ่มเลือกความยาว · บอร์ดช่วง 2/3 · แถวบทฉาก 6-15"""
    n_seg = n_phase = n_board = 0
    for _, n in walk(cfg.get('phases')):
        if not isinstance(n, dict): continue
        el = n.get('el')
        # ① ทุกทางที่วิดีโอออกจากแอป → el.segments (engine รวมช่วงให้เอง · ช่วงเดียว = ใช้ตรง ไม่เรียก ffmpeg)
        #    ★ต้องครบทั้ง 3 ทาง (ดู · ดาวน์โหลด · zip) — ตกทางใดทางหนึ่ง ลูกค้าจะได้แค่ 10 วิแรกโดยไม่มีใครเตือน
        if el == 'download-button' and n.get('to') == '{item.slots.video}':
            n['segments'] = copy.deepcopy(SEGS); n_seg += 1
        elif el == 'zip-export' and n.get('coll') == 'tasks':
            n['segments'] = copy.deepcopy(SEGS); n_seg += 1
        elif el == 'media-slot' and n.get('src') == '{item.slots.video}':
            n['segments'] = copy.deepcopy(SEGS); n_seg += 1
        # ② ปุ่มรันเป็นชุด → ต้องรวม op ของช่วง 2/3 ด้วย (op ที่ไม่ถึงคิวถูก when กันเอง)
        #    ★ลำดับต้องเป็น ช่วง3 → ช่วง2 → ช่วง1 เหมือนใน stages (เหตุผลอยู่ที่ patch_ops)
        if el == 'gen-phase' and isinstance(n.get('ops'), list):
            ops = n['ops']
            for base in ('mnBoard', 'mnVideo'):
                if base in ops and base + '2' not in ops:
                    i = ops.index(base)
                    ops[i:i + 1] = [base + '3', base + '2', base]
                    n_phase += 1
        # ③ (เลิกใช้ 2026-09-10) เดิมต่อบอร์ดช่วง 2/3 เป็นกล่องแยกมีป้ายกำกับต่อท้ายกล่องเดิม
        #    ตอนนี้ใช้ตัวเลื่อน < > ในกรอบเดียว (patch_board_carousel) แทน — พี่หมีว่าสวยกว่าและใช้ง่ายกว่า
        #    🪤 ถ้าปล่อยของเดิมไว้ = บอร์ด 2/3 โผล่ซ้ำใต้กรอบที่เลื่อนได้อยู่แล้ว (เจอจริงบนจอคอม)

    # ④ กลุ่ม "การผลิต" — ★ความยาวคลิปต้องมา **ก่อน** จำนวนคลิป (ลำดับเดียวกับ hardsell) + ป้ายหัวช่องมีไอคอน
    n_pick = 0
    for _, n in walk(cfg.get('phases')):
        if isinstance(n, dict) and n.get('el') == 'group' and isinstance(n.get('card'), list):
            body = json.dumps(n, ensure_ascii=False)
            if '"clipsPerProduct"' in body and '"svSec"' not in body:
                at = next((i for i, c in enumerate(n['card'])
                           if '"clipsPerProduct"' in json.dumps(c, ensure_ascii=False)), 0)
                n['card'].insert(at, len_picker()); n_pick += 1     # insert(at) = แทรกไว้ข้างหน้า
    n_chip = patch_step_chips(cfg)
    n_dur = patch_duration_labels(cfg)
    n_ta = patch_toggle_all(cfg)
    n_ch = patch_item_chains(cfg)
    n_bt = patch_board_carousel(cfg)
    n_bt += patch_viewmode_align(cfg)
    n_bt += patch_drop_col_divider(cfg)
    n_bt += patch_video_placeholder(cfg)
    n_bt += patch_default_tab(cfg)
    n_bt += patch_media_col_mobile(cfg)
    n_bt += patch_done_card_tint(cfg)
    n_bt += patch_drop_eng(cfg)
    n_bt += patch_grid_drop_bar(cfg)
    n_bt += patch_grid_no_hover(cfg)
    _board_seg1_continuity(cfg)
    n_lbl = patch_setup_labels(cfg)
    n_rows = patch_script_rows(cfg)
    return n_seg, n_phase, n_board, n_pick, n_rows, n_lbl, n_chip, n_dur, n_ta, n_ch, n_bt


# ปุ่มรายคลิป (ในการ์ดงาน) ต้องทำครบทุกช่วง ไม่ใช่แค่ช่วงแรก (พี่หมีสั่ง 2026-09-09)
#   gen-button ส่งได้ op เดียว ⇒ คลิป 20/30 วิ กดแล้วได้บอร์ด/วิดีโอใบเดียว **แล้วดูเหมือนเสร็จ**
#   ✅ engine รองรับ el.chain (รันหลาย op บน item เดียว ผ่าน on.chainItem) แล้ว — แค่เปลี่ยน op → chain
#   ★ลำดับเดียวกับ stages: ช่วงท้ายก่อน ⇒ slots.board/video ของช่วงแรกยังเป็นตัวชี้ว่า "ครบแล้ว"
CHAINS = {'mnBoard': ['mnBoard3', 'mnBoard2', 'mnBoard'], 'mnVideo': ['mnVideo3', 'mnVideo2', 'mnVideo']}


def patch_item_chains(cfg):
    hit = 0
    for _, n in walk(cfg.get('phases')):
        if not (isinstance(n, dict) and n.get('el') in ('gen-button', 'retry-button')): continue
        base = n.get('op')
        if base not in CHAINS or n.get('chain'): continue
        n['chain'] = list(CHAINS[base])
        hit += 1
    return hit


# ประตูแบบ Binding (ไม่ใช่ predicate string) — ต้องใช้แบบนี้เมื่อจะ **ผสมกับ when เดิม**
#   🪤 string predicate ('values.svSec>10') เอาไปใส่ใน and/not ไม่ได้ — resolveValue จะอ่านเป็น path/ข้อความ ไม่ใช่เงื่อนไข
def GT(a, b): return {'op': 'gt', 'a': a, 'b': b}
def NOT(a): return {'op': 'not', 'a': a}
def _and(a, b):
    if b is None: return a
    assert not isinstance(b, str), 'when เดิมเป็น predicate string — ผสมกับ and ไม่ได้ (ต้องแปลงเป็น Binding ก่อน)'
    return {'op': 'and', 'a': a, 'b': b}


# ── การ์ดงานในโหมดทำทีละขั้น: คลิป 20/30 วิ มีบอร์ดหลายใบ แต่การ์ดโชว์ใบเดียว ────────
#   ⇒ ผู้ใช้กด "ภาพโอเค — สร้างวิดีโอ" โดยเห็นแผนแค่ครึ่งเดียว (อีกครึ่งไปโผล่ตอนได้คลิปแล้ว = สายไป)
#   ✅ 10 วิ ใช้ของเดิมทุกพิกเซล (ประตู not(svSec>10) → ไฟล์เซฟเก่าที่ svSec ว่างก็เข้าทางเดิม)
#      >10 วิ = สลับเป็นแถวไทล์เท่ากันทุกใบ **ไม่ใช่ใบใหญ่ 1 + ใบเล็ก 2** เพราะครึ่งหลังก็ต้องตรวจเท่ากัน
#   🪤 ป้ายต้องเป็นเลขลอย ๆ (1/2/3) ห้ามใช้คำว่า "ช่วง" — ผู้ใช้ไม่ต้องรู้ว่าเบื้องหลังแบ่งเป็นช่วง
def _grid_view_ids(cfg):
    """โหนดทั้งหมดที่อยู่ใต้บล็อก "มุมมองกริด" ของหน้าผลิต

    🪤 ห้ามใช้ `'grid-cols-2' in className` เป็นตัวแยก — วัดแล้วมันแมตช์ **28 โหนด**ทั่วแอป
       (`grid-cols-1 @[900px]:grid-cols-2` ของฟอร์มธรรมดาก็ติด) ⇒ ตัดของที่ไม่ควรตัดเพียบ
       ใช้ "สิ่งที่บล็อกนั้นเป็นจริง ๆ" แทน = บล็อกที่ `when` ผูกกับ `values.viewMode == 'grid'`
       (ตระกูลเดียวกับบทเรียน "ยามต้องผูกกับกฎ ไม่ใช่รูปทรง")
    """
    ids = set()
    for _, n in walk(cfg.get('phases')):
        if not isinstance(n, dict) or 'when' not in n: continue
        w = json.dumps(n.get('when'), ensure_ascii=False)
        if '{values.viewMode}' in w and '"grid"' in w:
            for _, m in walk(n): ids.add(id(m))
    return ids



# ชุดภาพให้ไลท์บ็อกซ์กด < > สลับ — ใบที่ยังไม่มี engine กรองทิ้งเอง (ตัวนับ N/M จึงตรงเสมอ)
BOARD_GALLERY = ['{item.slots.board}', '{item.slots.board2}', '{item.slots.board3}']
NB = {'op': 'div', 'a': '{values.svSec}', 'b': 10}                    # จำนวนบอร์ดทั้งหมด
# 🔴 ต้องบีบเป็นสตริงก่อนด้วย concat — field ที่ยังไม่เคยถูกเขียนจะ resolve เป็น `undefined`
#    แล้ว Number(undefined) = NaN ⇒ max(NaN,1) = NaN ⇒ ป้ายขึ้น "NaN / 3" และไม่มีใบไหนแมตช์เลย
#    concat ใช้ resolveStr ซึ่งคืน '' เมื่อไม่มีค่า → Number('') = 0 → max = 1 ✓
CUR = {'op': 'max', 'a': {'op': 'concat', 'parts': ['{item.bview}']}, 'b': 1}   # ใบที่กำลังดู (ว่าง → 1)



def _board_frames(ms, extra_cls=''):
    """3 ใบซ้อนกัน โชว์ทีละใบตาม item.bview — ใบแรกเป็น "ค่าตั้งต้น" ไม่ใช่ eq(cur,1)
    (field ที่ยังไม่เคยเขียน = NaN ⇒ ถ้าใช้ eq เป๊ะจะไม่มีใบไหนแมตช์ → กล่องยุบ ของ absolute กองทับกัน)"""
    out = []
    for k in range(1, 4):
        slot = 'board' if k == 1 else 'board%d' % k
        f = dict(copy.deepcopy(ms), src='{item.slots.%s}' % slot, gallery=BOARD_GALLERY)
        if extra_cls: f['className'] = (f.get('className') or '') + ' ' + extra_cls
        f['when'] = ({'op': 'not', 'a': {'op': 'or', 'list': [{'op': 'eq', 'a': CUR, 'b': 2}, {'op': 'eq', 'a': CUR, 'b': 3}]}}
                     if k == 1 else {'op': 'eq', 'a': CUR, 'b': k})
        out.append(f)
    return out


def _arrow(side):
    """ปุ่มเลื่อน — วาง**ข้างภาพ** (ซ้าย/ขวา กลางแนวตั้ง) ตามที่พี่หมีสั่ง
    🪤 มือถือต้อง ≥44px (ด่าน mobile-tier) แล้วค่อยหดที่จอใหญ่ · quiet=True ไม่งั้นแค่เลื่อนดูภาพ คลิปกลาย stale"""
    left = side < 0
    return {'el': 'button', 'action': 'setField', 'to': 'bview', 'quiet': True, 'label': '',
            'icon': 'chevron_left' if left else 'chevron_right',
            'when': GT('{values.svSec}', 10),
            'value': ({'op': 'max', 'a': {'op': 'sub', 'a': CUR, 'b': 1}, 'b': 1} if left
                      else {'op': 'min', 'a': {'op': 'add', 'a': CUR, 'b': 1}, 'b': NB}),
            'className': ('absolute ' + ('left-1' if left else 'right-1') + ' top-1/2 -translate-y-1/2 z-30 '
                          'justify-center !gap-0 !w-11 !h-11 @[420px]:!w-8 @[420px]:!h-8 !min-h-0 !p-0 '
                          '!rounded-full !bg-[#17253a]/75 !text-white !border-0 backdrop-blur-sm')}


def _counter(cls, label=''):
    """ป้ายบอกว่ากำลังดูใบไหน — label ใส่คำว่า 'บอร์ด' นำหน้าได้ (แถบล่างของกริด)"""
    return {'el': 'row', 'when': GT('{values.svSec}', 10), 'style': {'flexWrap': 'nowrap'},
            'className': cls + ' z-30 items-center px-2 py-1 rounded-lg bg-[#17253a]/80 backdrop-blur-sm pointer-events-none',
            'card': [{'el': 'text', 'value': {'op': 'concat', 'parts': [label, CUR, '/', NB]},
                      'className': '!text-[11px] font-black !text-white tabular-nums whitespace-nowrap'}]}


def _board_chips():
    """แถวชิป [1][2][3] ใต้ภาพ — ลิสต์ใช้ตัวนี้แทนปุ่มทับภาพ

    🔴 ทำไมไม่ทับภาพเหมือนกริด: **สตอรีบอร์ดเป็นเอกสาร ไม่ใช่รูปสินค้า**
       5 แถว × 4 คอลัมน์ (เลขฉาก · ภาพ · มุมกล้อง · บทพูด) — ทุกตารางนิ้วมีของที่ต้องอ่าน
       ปุ่มทับกลางภาพ = บังฉาก 3-4 · ป้าย n/n ทับหัวเรื่อง (พี่หมีเห็นกับตา 2026-09-10)
       ลิสต์มีที่ว่างใต้ภาพอยู่แล้ว (เหนือปุ่ม บอร์ด|วิดีโอ) ⇒ ไม่มีเหตุผลต้องทับ
    ★ชิปที่เลือกอยู่ = ตัวบอกว่ากำลังดูใบไหน ⇒ **ไม่ต้องมีป้าย n/n แยกอีก** ภาพสะอาดขึ้นอีกชั้น
    ★3 ใบกดตรงไปเลย ไม่ต้องกด › สองครั้งเพื่อไปใบสุดท้าย
    ★ไม่มีคำว่า "บอร์ด" ในแถวนี้ — บรรทัดถัดลงไปคือปุ่ม [บอร์ด|วิดีโอ] อยู่แล้ว และกล่องนี้ทั้งกล่อง
      โผล่เฉพาะตอน view != video ⇒ เขียนซ้ำ = คำเดียวกันโผล่ 2 บรรทัดติดกัน
      (กริดต้องมีคำนี้ เพราะกริดไม่มีปุ่ม บอร์ด|วิดีโอ ให้อ้าง — คนละสถานการณ์ อย่ายกไปใช้ข้ามกัน)

    🔴 **ห้ามใส่ `!bg-…` ใน className ฐาน แล้วหวังให้ classWhen ทับ** — วัดจริงในแล็บรอบนี้:
       ชิปที่เลือกอยู่ได้ทั้ง `!bg-surface2` และ `!bg-accent` พร้อมกัน **ทั้งคู่เป็น !important**
       ⇒ ผู้ชนะตัดสินด้วย**ลำดับใน stylesheet ไม่ใช่ลำดับใน class** (โรคเดียวกับ flex-1 ทับ basis-full)
       ผลจริงที่วัดได้: bg = rgb(234,239,245) ซีด + text = ขาว ⇒ **ชิปที่กำลังเลือกอยู่อ่านไม่ออก**
       ⇒ แยกสองสถานะเป็น classWhen คนละข้อที่ไม่มีวันจริงพร้อมกัน แล้ว className ฐานห้ามมีสี
    """
    chips = []
    for k in (1, 2, 3):
        on = {'op': 'eq', 'a': CUR, 'b': k}
        c = {'el': 'button', 'action': 'setField', 'to': 'bview', 'quiet': True,
             'label': str(k), 'value': str(k),
             'className': ('justify-center !min-w-[40px] !h-11 @[420px]:!h-8 !min-h-0 !px-2 !rounded-lg '
                           '!text-[12px] font-black border'),
             'classWhen': [{'when': on,
                            'class': '!bg-[var(--ev-accent)] !text-white !border-[var(--ev-accent)]'},
                           {'when': {'op': 'not', 'a': on},
                            'class': '!bg-[var(--ev-surface2)] !text-[var(--ev-text)] !border-[var(--ev-border)]'}]}
        if k > 1: c['when'] = GT('{values.svSec}', (k - 1) * 10)
        chips.append(c)
    return {'el': 'row', 'when': GT('{values.svSec}', 10), 'style': {'flexWrap': 'nowrap'},
            'className': 'items-center gap-1.5 mt-2 justify-center', 'card': chips}


def _grid_bar():
    """กริด: แถบเดียวใต้ภาพ  ‹ บอร์ด 1/3 ›  — พี่หมีสั่งรวมคำว่าบอร์ดไว้ในแถบ (ป้าย 'N บอร์ด' แยกเกะกะ เอาออกแล้ว)"""
    # 🪤 มือถือต้อง ≥44px เหมือนกัน (ด่าน mobile-tier จับได้) — โปสเตอร์กริดกว้าง ~180px
    #    แถบ 44+44+ตัวเลข ≈ 138px ยังอยู่ในกรอบ · จอใหญ่ค่อยหดเป็น 32px ให้ไม่เกะกะ
    mk = lambda side: dict(_arrow(side), className=(
        'justify-center !gap-0 !w-11 !h-11 @[420px]:!w-8 @[420px]:!h-8 !min-h-0 !p-0 '
        '!rounded-full !bg-white/15 !text-white !border-0'))
    return {'el': 'row', 'when': GT('{values.svSec}', 10), 'style': {'flexWrap': 'nowrap'},
            'className': ('absolute bottom-9 left-1/2 -translate-x-1/2 z-30 items-center gap-1 px-1 py-1 '
                          'rounded-full bg-[#17253a]/85 backdrop-blur-sm'),
            'card': [mk(-1),
                     {'el': 'text', 'value': {'op': 'concat', 'parts': ['บอร์ด ', CUR, '/', NB]},
                      'className': '!text-[11px] font-black !text-white tabular-nums px-1.5 whitespace-nowrap'},
                     mk(1)]}


def patch_viewmode_align(cfg):
    """ปุ่มสลับมุมมอง (ลิสต์/กริด) ต้องชิดขวาบนจอคอม
    🪤 ของเดิมเขียน `@[420px]:justify-start` = พอพ้นจอมือถือกลับไปชิดซ้าย ⇒ ลอยอยู่กลางแถบเปล่า ๆ
    """
    hit = 0
    for _, n in walk(cfg.get('phases')):
        if not isinstance(n, dict): continue
        cn = str(n.get('className') or '')
        if '@[420px]:w-auto @[420px]:justify-start' in cn and 'justify-end' in cn:
            n['className'] = cn.replace('@[420px]:w-auto @[420px]:justify-start', '@[420px]:justify-end')
            hit += 1
    return hit


def patch_drop_col_divider(cfg):
    """เอาเส้นคั่นระหว่างคอลัมน์ของการ์ดงานออก (พี่หมีสั่ง — "ของคอลัมน์ออกก็ได้")
    ★เส้นนี้มีมาก่อนงานคลิปยาว (ของเดิมในดีไซน์) ไม่ใช่ของที่เพิ่มรอบนี้ ⇒ จดไว้ว่าเป็นการถอดของเดิมโดยตั้งใจ
    """
    hit = 0
    for _, n in walk(cfg.get('phases')):
        if not isinstance(n, dict): continue
        cn = str(n.get('className') or '')
        if '@[880px]:border-l' in cn:
            n['className'] = cn.replace('@[880px]:border-l ', '').replace('@[880px]:border-l', '').strip()
            hit += 1
    return hit


def patch_done_card_tint(cfg):
    """การ์ดคลิปที่เสร็จแล้ว: พื้นเขียวไม่เคยขึ้นเลย เพราะ gradient ทับอยู่ (ทีม showhow ชี้ 2026-09-10)

    ต้นเหตุ — **`!important` ที่ไม่ได้ทับอะไรเลย** (ร้ายกว่าแบบชนกันเอง เพราะดูเหมือนบังคับแล้ว):
      className ฐาน  : `bg-gradient-to-br from-[var(--ev-surface)] to-[var(--ev-bg)]` = **background-image**
      classWhen เสร็จ: `!bg-green-500/[0.05]`                                        = **background-color**
      ⇒ คนละ property กัน `!` ไม่ได้แข่งกับใคร · และ background-image วาดทับ background-color เสมอ
      ⇒ ธีมสว่าง (#ffffff → #f4f6f9 ทึบทั้งคู่) = **สีเขียวถูกบังสนิท 100%**
    วัดจริงในเบราว์เซอร์ (ไม่ใช่อ่านจากโค้ด): bgColor `rgba(34,197,94,0.05)` มาแล้วจริง
      แต่ bgImage `linear-gradient(…, rgb(255,255,255), rgb(244,246,249))` ทับหมด · ขอบเขียวขึ้นปกติ
    ⇒ เติม `!bg-none` เพื่อล้าง background-image ก่อน สีพื้นถึงจะโผล่
    🪤 ยาม ⑯ ใน minimal-cliplen เฝ้าคู่ "gradient ↔ สีพื้น" ไว้แล้ว — ห้ามถอด !bg-none ออกเฉย ๆ
    """
    hit = 0
    for _, n in walk(cfg.get('phases')):
        if not isinstance(n, dict) or not isinstance(n.get('classWhen'), list): continue
        base = str(n.get('className') or '')
        if 'bg-gradient-' not in base or 'bg-none' in base: continue
        for w in n['classWhen']:
            cls = str((w or {}).get('class') or '')
            if re.search(r'(^|\s)!?bg-(?!gradient|none|\[url)', cls) and 'bg-none' not in cls:
                w['class'] = '!bg-none ' + cls; hit += 1
    return hit


def patch_media_col_mobile(cfg):
    """คอลัมน์สื่อของการ์ดงาน: มือถือขยายภาพให้ใหญ่ขึ้น (พี่หมีสั่งตั้งแต่รอบออกแบบ 3 คอลัมน์)

    ของเดิม `w-[170px]` ใช้เลขเดียวกันทุกจอ ⇒ บนมือถือกว้าง 390 การ์ดกว้าง ~330
    แต่สตอรีบอร์ดได้แค่ 168px = **5 แถว × 4 คอลัมน์ในความกว้างเท่านิ้วโป้ง อ่านไม่ออกจริง ๆ**
    (เดสก์ท็อป 170 ถูกแล้ว เพราะข้าง ๆ ยังมีอีก 2 คอลัมน์ที่ต้องได้ที่)
    ⇒ ≤420px ใช้ 230px · เกินนั้นกลับเป็น 170 เท่าเดิม ⇒ **เดสก์ท็อปไม่ขยับสักพิกเซล**
    """
    OLD, NEW = 'relative w-[170px] mx-auto @[420px]:mx-0', 'relative w-[230px] @[420px]:w-[170px] mx-auto @[420px]:mx-0'
    hit = 0
    for _, n in walk(cfg.get('phases')):
        if isinstance(n, dict) and n.get('className') == OLD:
            n['className'] = NEW; hit += 1
    return hit


# ═══ ล็อกความเหมือนของสินค้า + บทพูดต้องเต็มความยาว (พี่หมีเจอจากการทดสอบ 2026-09-10) ═══

_PROD_OLD = 'กติกาสำคัญ: ใช้ "สินค้าที่แนบมา" เป็นต้นแบบ คงรูปทรง สี ฉลาก และดีไซน์ของสินค้า 100% ห้ามเปลี่ยนแปลงรายละเอียดสินค้า'

_PROD_NEW = (
    'กติกาเหล็ก — ความเหมือนของสินค้า (สำคัญกว่าความสวยของภาพ):\n'
    '- สินค้าในทุกช่องต้องเป็นชิ้นเดียวกันกับรูปที่แนบมาแบบเป๊ะ — ถือรูปที่แนบเป็นภาพถ่ายของจริง ไม่ใช่แค่แรงบันดาลใจ\n'
    '- ห้ามเปลี่ยน: สี เฉดสี รูปทรง สัดส่วน ขนาด วัสดุ พื้นผิว ฉลาก โลโก้ ตัวอักษรบนสินค้า จำนวนชิ้นและส่วนประกอบ\n'
    '- ห้ามวาดใหม่ ห้ามตีความใหม่ ห้ามทำให้เป็นภาพวาดหรือการ์ตูน ห้ามเพิ่มหรือลบรายละเอียดใดของตัวสินค้า\n'
    '- สไตล์มินิมอลสแกนดิเนเวียนและโทนพาสเทลใช้กับ ฉาก พื้นหลัง แสง และเลย์เอาต์ของแผง เท่านั้น '
    'ห้ามใช้กับตัวสินค้า — ตัวสินค้าคงสีและวัสดุจริงตามรูปที่แนบเสมอ\n'
    '- ถ้ามุมกล้องที่บทระบุเป็นมุมที่รูปที่แนบไม่มี ให้ใช้มุมที่ใกล้เคียงที่สุดจากรูปที่แนบ '
    'และห้ามเดารายละเอียดด้านที่มองไม่เห็น')

_VID_OLD = ('Keep the product 100% identical to the reference image throughout — same shape, color, label, and design.')

_VID_NEW = (
    'PRODUCT LOCK (this outranks every style instruction): the product must be the exact same physical object '
    'as in the attached reference photo. Treat the reference as a real photograph of the real product, not as inspiration. '
    'Never change its colour, shade, shape, proportion, size, material, texture, label, logo, on-product lettering, '
    'or the number of parts. Do not redraw, restyle, illustrate or cartoonify it, and never add or remove any part of it. '
    'The Scandinavian-minimal pastel styling applies ONLY to the set, background, lighting and composition — never to the '
    'product itself. If a shot calls for an angle the reference does not show, use the closest angle the reference does show '
    'and never invent unseen details.')


def patch_product_lock(cfg):
    """สินค้าเพี้ยนตอนวาดสตอรีบอร์ด (พี่หมีเจอจากการทดสอบจริง)

    🔴 ราก = **ตระกูลเดียวกับ "มินิมอลหลุดเข้าบทขาย" ที่เคยแก้ไปแล้ว** — คำสั่งสไตล์ไม่ได้บอกขอบเขต
       prompt เดิมวาง "สไตล์ภาพรวม: มินิมอลสแกนดิเนเวียน พื้นหลังโทนพาสเทล" ไว้ **ก่อน** และยาวกว่า
       กติกาความเหมือนสินค้าซึ่งเป็นประโยคเดียวสั้น ๆ ⇒ โมเดลคลี่ความขัดแย้งด้วยการ **จับสินค้าเข้าสไตล์**
    ⇒ ยาคือบอกขอบเขตให้ชัด: **สไตล์เป็นของฉาก ไม่ใช่ของสินค้า** + ระบุรายการที่ห้ามเปลี่ยนเป็นข้อ ๆ
    ★ต้องมี "ทางออก" ให้ด้วย (ถ้ามุมที่บทขอไม่มีในรูป ให้ใช้มุมใกล้สุด) — ห้ามล้วน ๆ โดยไม่มีทางออก
      โมเดลจะเดารายละเอียดเองอยู่ดี (บทเรียนเดิม: กฎ "ชนิด" ต้องมาคู่กฎ "จำนวน/ทางเลือก")
    """
    hit = 0
    for o in cfg['ops']:
        if not o['id'].startswith(('mnBoard', 'mnVideo')): continue
        txt = json.dumps(o['prompt'], ensure_ascii=False)
        old, new = (_PROD_OLD, _PROD_NEW) if o['id'].startswith('mnBoard') else (_VID_OLD, _VID_NEW)
        j_old = json.dumps(old, ensure_ascii=False)[1:-1]
        j_new = json.dumps(new, ensure_ascii=False)[1:-1]
        if j_old not in txt: continue
        o['prompt'] = json.loads(txt.replace(j_old, j_new))
        hit += 1
    return hit


def _vo_rule(sec):
    """กฎความยาวบทพูดต่อความยาวคลิป — ต้องสเกลตามจำนวนฉาก ไม่ใช่เลขตายตัว"""
    scenes = sec // 2
    lo, hi = scenes * 5, scenes * 7
    return ('กฎความยาวบทพูด (ต้องพูดต่อเนื่องเต็มความยาว ห้ามมีช่วงเงียบ):\n'
            '- คลิปนี้ยาว %d วินาที มี %d ฉาก ฉากละ 2 วินาที — vo1 ถึง vo%d ต้องมีบทพูดครบทุกฉาก '
            'ห้ามเว้นว่างแม้แต่ฉากเดียว\n'
            '- ฉากละ 5-7 คำไทย รวมทั้งคลิป %d-%d คำ — ให้พูดเต็ม 2 วินาทีของฉากนั้นพอดี ไม่เหลือช่องเงียบ\n'
            '- เขียนให้ vo1 ถึง vo%d ต่อกันเป็นย่อหน้าเดียวที่อ่านรวดเดียวจบพอดี %d วินาที '
            'ไม่ใช่วลีสั้นที่จบห้วนแยกกัน (แยกกันเมื่อไหร่จะเกิดช่วงเงียบคั่นระหว่างฉาก)'
            % (sec, scenes, scenes, lo, hi, scenes, sec))


def patch_vo_fill(cfg):
    """คลิป 20/30 วิ มีช่วงเงียบยาว (พี่หมีเจอจากการทดสอบจริง)

    🔴 ราก **วัดเป็นตัวเลขได้**: กฎเดิมเขียนตายตัวว่า "รวมทั้งคลิป 20-30 คำไทย เฉลี่ย 4-6 คำต่อฉาก"
       และมันอยู่ในส่วนของ sys ที่ **ไม่ผูกกับความยาว** ⇒ คลิป 30 วิ ก็ยังได้งบ 20-30 คำเท่าเดิม
       ภาษาไทยพูดจังหวะโฆษณา ~3 คำ/วินาที ⇒ 25 คำ ≈ 8 วินาที ⇒ **คลิป 30 วิ เงียบไปกว่า 20 วินาที**
    ⇒ ย้ายงบคำไปเป็น lookup ต่อความยาว (ฉากละ 5-7 คำ × จำนวนฉาก) แล้วต่อท้าย systemInstruction
    ★สั่ง "เขียนต่อกันเป็นย่อหน้าเดียว" ด้วย — ไม่งั้นได้วลีสั้น N ชิ้นที่จบห้วน แล้วเกิดช่องเงียบคั่นอยู่ดี
    """
    lk = cfg['lookups']
    lk['lenVo'] = {str(s): _vo_rule(s) for s in (10, 20, 30)}
    op = find_op(cfg, 'mnPlan')
    si = op['systemInstruction']
    assert isinstance(si, dict) and si.get('op') == 'concat', 'systemInstruction ไม่ใช่ concat — patch_plan ยังไม่ได้รัน?'
    if any(isinstance(x, dict) and x.get('table') == 'lenVo' for x in si['parts']): return 0
    tail = {'op': 'lookup', 'table': 'lenVo', 'key': '{values.svSec}', 'fallback': lk['lenVo']['10']}
    si['parts'] = si['parts'][:-1] + ['\n\n', tail, '\n\n'] + si['parts'][-1:]
    # เลขตายตัวในตัวกลางต้องออก ไม่งั้นขัดกับกฎใหม่ (โมเดลจะเลือกอันที่เจอก่อน)
    OLDL = '- รวมทั้งคลิป 20-30 คำไทย เฉลี่ย 4-6 คำต่อฉาก พูดต่อเนื่องลื่นไหล น้ำเสียงอบอุ่นเป็นมิตร'
    NEWL = '- พูดต่อเนื่องลื่นไหล น้ำเสียงอบอุ่นเป็นมิตร (จำนวนคำต่อฉากดูที่กฎความยาวบทพูดท้ายคำสั่ง)'
    assert OLDL in cfg['brain']['mn']['sys'], 'ไม่เจอบรรทัดงบคำเดิมใน sys'
    cfg['brain']['mn']['sys'] = cfg['brain']['mn']['sys'].replace(OLDL, NEWL, 1)
    return 1


_AUD_ANCHOR = "\n\nAudio: "
_AUD_FILL = ('The narration must run continuously for the whole clip — start speaking at 0.0s and keep speaking '
             'until the last second. No silent gap at the start, between scenes, or at the end. ')


def patch_vo_seam(cfg):
    """รอยต่อระหว่างช่วง: โมเดลสร้างทีละ 10 วิ ⇒ ถ้าเว้นจังหวะท้ายช่วง + ต้นช่วงถัดไป จะได้ช่องเงียบคู่ตรงรอยต่อ
       ★แทนบนข้อความ JSON ⇒ ต้องแปลง anchor ด้วย json.dumps ก่อน (ขึ้นบรรทัดใหม่ในไฟล์ = `\\n` สองตัวอักษร)
       🪤 รอบแรกเขียน anchor เป็นสตริงที่มีขึ้นบรรทัดจริง แล้ว **ไม่แมตช์อะไรเลยแบบเงียบ ๆ** (hit=0 ไม่มี error)
          ⇒ ต้องมี assert ว่าแทนได้จริง ไม่ใช่ปล่อยให้ 0 ผ่านไป (ตระกูลยามหลับ)
    """
    a = json.dumps(_AUD_ANCHOR, ensure_ascii=False)[1:-1]
    f = json.dumps(_AUD_ANCHOR + _AUD_FILL, ensure_ascii=False)[1:-1]
    hit = 0
    for o in cfg['ops']:
        if not o['id'].startswith('mnVideo'): continue
        txt = json.dumps(o['prompt'], ensure_ascii=False)
        if f[:60] in txt or a not in txt: continue
        o['prompt'] = json.loads(txt.replace(a, f, 1)); hit += 1
    assert hit > 0, 'patch_vo_seam ไม่ได้แทนอะไรเลย — anchor เปลี่ยน?'
    return hit


def patch_grid_no_hover(cfg):
    """กริด: ไม่ต้องมีไอคอนลูกตาตอน hover (พี่หมีสั่ง 2026-09-10) — ลิสต์ยังมีเหมือนเดิม

    เหตุผล: โปสเตอร์กริด **มี overlay ของตัวเองอยู่แล้ว** (ปุ่ม Gen วิดีโอ / เลือกวิดีโอ กลางภาพ)
      ⇒ พอเอาเมาส์ไปวาง จะได้ไอคอนลูกตา 42px ซ้อนทับปุ่มอีกชั้น = รก และกดอะไรก็ไม่รู้
    ★ลิสต์ไม่เป็น เพราะภาพในลิสต์สะอาด ไม่มีปุ่มทับ ⇒ ไอคอนลูกตาเป็นตัวบอกว่า "กดดูใหญ่ได้" ที่มีประโยชน์
    ⚠️ ใช้ `el.hoverIcon: false` ของ engine (เพิ่มใหม่รอบเดียวกัน) — **ต้อง deploy engine ก่อนถึงจะมีผล**
    """
    gids = _grid_view_ids(cfg)
    hit = 0
    for _, n in walk(cfg.get('phases')):
        if not (isinstance(n, dict) and n.get('el') == 'media-slot'): continue
        if id(n) not in gids: continue
        if n.get('hoverIcon') is False: continue
        n['hoverIcon'] = False; hit += 1
    return hit


def patch_drop_eng(cfg):
    """ตัดคำว่า "เอง" ออกจากป้ายปุ่มเลือกไฟล์ (พี่หมีสั่ง 2026-09-10 · ข้อความตกบรรทัดในกริด)

    "เลือกวิดีโอเอง" ยาว 13 ตัวอักษร ⇒ ในโปสเตอร์กริดที่ปุ่มกว้างแค่ ~130px มันตกเป็น 2 บรรทัด
    ★ความหมายไม่หาย เพราะมันอยู่คู่กับ "Gen วิดีโอ" อยู่แล้ว — Gen = ให้ AI สร้าง · เลือก = หยิบไฟล์ที่มี
    """
    hit = 0
    for _, n in walk(cfg.get('phases')):
        if isinstance(n, dict) and isinstance(n.get('label'), str) and n['label'].endswith('เอง'):
            n['label'] = n['label'][:-3].rstrip(); hit += 1
    return hit


def patch_grid_drop_bar(cfg):
    """กริด: เอาแถบ ‹ บอร์ด N/N › ออก แล้วย้ายการสลับใบไปอยู่ใน "จอเต็ม" แทน (พี่หมีถาม 2026-09-10)

    เหตุผล (ทำไมเอาออกดีกว่าออกแบบใหม่):
      ① **กริดคือแผ่นคอนแทค ไม่ใช่ที่ตรวจแผน** — โปสเตอร์กว้าง ~180px อ่านบทไม่ออกอยู่แล้ว
         การสลับใบตรงนั้นจึงได้ประโยชน์น้อย แต่จ่ายด้วยการบังฉากที่ 5 ทุกใบ
      ② **ของที่มันทำ มีที่อื่นทำได้ดีกว่าอยู่แล้ว** — แตะภาพ = เปิดจอเต็ม ซึ่งมี ‹ › + ตัวนับ +
         ลูกศรคีย์บอร์ด (`el.gallery` ของ v1.7.6) และภาพใหญ่พอให้อ่านบทได้จริง
      ③ ⇒ ได้โปสเตอร์ที่ **ไม่มีอะไรทับเลย** = ตรงกับหลักเดิมของรอบนี้ (สตอรีบอร์ด = เอกสาร)
    ★แต่ยังต้องบอกให้รู้ว่า "คลิปนี้มีหลายใบ" ⇒ เติมตัวเลขลง **แถบชื่อล่างที่มีอยู่แล้ว**
      (ไม่ใช่ป้ายลอยใบใหม่ — พี่หมีเคยสั่งเอาป้าย "N บอร์ด" แบบลอยออกไปแล้วเพราะเกะกะ)
    """
    hit = 0
    for _, n in walk(cfg.get('phases')):
        if not (isinstance(n, dict) and isinstance(n.get('card'), list)): continue
        before = len(n['card'])
        n['card'] = [c for c in n['card'] if not _is_grid_bar(c)]
        hit += before - len(n['card'])
    # เติมตัวนับลงแถบชื่อล่างของโปสเตอร์ (แถบเดิม ไม่ได้สร้างใหม่)
    for _, n in walk(cfg.get('phases')):
        if not (isinstance(n, dict) and n.get('el') == 'row' and isinstance(n.get('card'), list)): continue
        cn = str(n.get('className') or '')
        if 'absolute bottom-0' not in cn or 'from-black/70' not in cn: continue
        if any(isinstance(c, dict) and 'ภาพ' in str(c.get('value') or '') for c in n['card']): continue
        # ★ไอคอน+เลข ชิดขวา — ไม่ใช้คำ เพราะแถบนี้แคบและมีชื่อสินค้าแย่งที่อยู่แล้ว
        #   `ml-auto` ดันไปสุดขอบขวา ⇒ ชื่อสินค้ากับ "คลิปที่ N/N" อยู่ซ้าย จำนวนบอร์ดอยู่ขวา = อ่านเป็น 2 กลุ่ม
        n['card'].append({
            'el': 'row', 'when': GT('{values.svSec}', 10), 'style': {'flexWrap': 'nowrap'},
            'className': ('ml-auto shrink-0 items-center gap-1 px-1.5 py-0.5 rounded-md '
                          'bg-[var(--ev-surface2)] opacity-85 leading-none'),
            'card': [{'el': 'icon', 'icon': 'burst_mode', 'textSize': 'text-[14px]',
                      'className': '!text-[var(--ev-text)] leading-none flex items-center'},
                     {'el': 'text', 'value': NB,
                      'className': '!text-[11px] font-bold !text-[var(--ev-text)] whitespace-nowrap leading-none flex items-center'}]})
        hit += 1
    return hit


def _is_grid_bar(c):
    """แถบ ‹ บอร์ด N/N › ของกริด — จับจาก **สิ่งที่มันเป็น** (แถบ absolute ที่มีปุ่ม bview + ข้อความมีคำว่าบอร์ด)
       🪤 ห้ามจับด้วย className อย่างเดียว — เดี๋ยวไปโดนแถบชื่อล่างที่ absolute เหมือนกัน"""
    if not (isinstance(c, dict) and c.get('el') == 'row' and isinstance(c.get('card'), list)): return False
    if 'absolute' not in str(c.get('className') or ''): return False
    kids = c['card']
    has_nav = any(isinstance(k, dict) and k.get('to') == 'bview' for k in kids)
    has_lbl = 'บอร์ด ' in json.dumps(kids, ensure_ascii=False)
    return has_nav and has_lbl


# วัดจริงในแล็บ 2026-09-10 — ความกว้างชิปเมื่อแบ่งเต็มคอลัมน์สื่อ:
#   3 ใบ คอม 49 · มือถือ 68   ✅        5 ใบ คอม 26 · มือถือ 38   ❌
#   4 ใบ คอม 35 · มือถือ 49   ✅        6 ใบ คอม 23 · มือถือ 30   ❌ (เล็กกว่ามาตรฐาน 44px ถึง 1 ใน 3)
# ⇒ เส้นแบ่งอยู่ระหว่าง 4 กับ 5 — ไม่ใช่การเดา
CHIP_MAX_SEC = 40   # ≤ 40 วิ (4 ใบ) = ชิป · เกินนี้ = ตัวเดินหน้าถอยหลัง


def _chip_bar():
    """≤4 ใบ: ชิป [1][2][3][4] — พี่หมีเลือกแบบนี้หลังเทียบของจริง 3 แบบ

    ★กดถึงทุกใบใน 1 คลิก · เห็นจำนวนใบทั้งหมดโดยไม่ต้องอ่านตัวหนังสือ
    🔴 quiet:true ต้องมี — ไม่งั้นแค่เลื่อนดูบอร์ด คลิปที่ done กลาย stale แล้วถูกผลิตซ้ำ เสียเครดิตฟรี
    🔴 className ฐานห้ามมีสี (กฎ !important ชนกัน) ⇒ แยก 2 สถานะเป็น classWhen คนละข้อ
    ★จอคอมเตี้ยกว่าปุ่ม [บอร์ด|วิดีโอ] (32 vs 40) = ไม่แข่งกัน · มือถือคง 44px ตามกฎ tap target
    """
    chips = []
    for k in range(1, CHIP_MAX_SEC // 10 + 1):
        on = {'op': 'eq', 'a': CUR, 'b': k}
        c = {'el': 'button', 'action': 'setField', 'to': 'bview', 'quiet': True,
             'label': str(k), 'value': str(k),
             'className': ('flex-1 justify-center !h-11 @[420px]:!h-8 !min-h-0 !px-2 '
                           '!rounded-lg !text-[11.5px] font-black !border-0'),
             'classWhen': [{'when': on, 'class': '!bg-[var(--ev-accent)] !text-white'},
                           {'when': {'op': 'not', 'a': on},
                            'class': '!bg-transparent !text-[var(--ev-text)] opacity-70'}]}
        if k > 1: c['when'] = GT('{values.svSec}', (k - 1) * 10)
        chips.append(c)
    return {'el': 'row', 'style': {'flexWrap': 'nowrap'},
            'when': {'op': 'and', 'a': GT('{values.svSec}', 10),
                     'b': {'op': 'not', 'a': GT('{values.svSec}', CHIP_MAX_SEC)}},
            'className': ('w-full mt-2 @[420px]:mt-1.5 items-center gap-1 rounded-xl border p-1 '
                          '@[420px]:rounded-lg @[420px]:p-0.5 '
                          'bg-[var(--ev-surface)] border-[var(--ev-border)]'), 'card': chips}


def _step_bar():
    """>4 ใบ: ‹ 3/6 › — สำรองไว้สำหรับคลิป 50/60 วิ ในอนาคต (พี่หมีสั่งเก็บไว้ 2026-09-10)

    🔴 ทำไมต้องมี: ชิปที่ 5 ใบ เหลือกว้าง 38px บนมือถือ · 6 ใบ เหลือ 30px = **ต่ำกว่ามาตรฐาน 44px**
       (วัดจริง ไม่ได้เดา — ตัวเลขอยู่ในคอมเมนต์ CHIP_MAX_SEC ข้างบน)
    ★ไม่มีคำว่า "บอร์ด" — ปุ่ม [บอร์ด|วิดีโอ] ที่อยู่ใต้ลงไปบอกอยู่แล้ว · เลขตัวใหญ่เด่นแทน (พี่หมีสั่ง)
    ⏳ **ตอนนี้ยังไม่มีทางเข้าถึง** เพราะ svSec สูงสุด 30 — เป็นของที่เตรียมไว้ล่วงหน้าโดยตั้งใจ
       ⇒ ยามต้องเช็คว่ามันยังอยู่และประตูไม่ทับกัน ไม่งั้นวันที่เปิด 60 วิ จะไม่มีใครรู้ว่ามันตายไปแล้ว
    """
    def arw(left):
        return {'el': 'button', 'action': 'setField', 'to': 'bview', 'quiet': True, 'label': '',
                'icon': 'chevron_left' if left else 'chevron_right',
                'value': ({'op': 'max', 'a': {'op': 'sub', 'a': CUR, 'b': 1}, 'b': 1} if left
                          else {'op': 'min', 'a': {'op': 'add', 'a': CUR, 'b': 1}, 'b': NB}),
                'className': ('justify-center !gap-0 !w-11 !h-11 @[420px]:!w-8 @[420px]:!h-8 !min-h-0 !p-0 '
                              '!rounded-lg !bg-[var(--ev-surface2)] !text-[var(--ev-text)] !border-0')}
    return {'el': 'row', 'when': GT('{values.svSec}', CHIP_MAX_SEC), 'style': {'flexWrap': 'nowrap'},
            'className': ('w-full mt-2 @[420px]:mt-1.5 items-center gap-1 rounded-xl border p-1 '
                          '@[420px]:rounded-lg @[420px]:p-0.5 '
                          'bg-[var(--ev-surface)] border-[var(--ev-border)]'),
            'card': [arw(True),
                     {'el': 'text', 'value': {'op': 'concat', 'parts': [CUR, '/', NB]},
                      'className': 'flex-1 text-center !text-[14px] font-black !text-[var(--ev-text)] tabular-nums'},
                     arw(False)]}


def _is_video_tab(when):
    """แท็บนี้เป็นฝั่ง "วิดีโอ" ไหม — ตัดสินจาก **กฎ** คือมี `{item.view} == "video"` อยู่ในเงื่อนไข

    🪤 ของเดิมเช็คด้วย substring `'"video"' in json.dumps(when)` ⇒ พังทันทีที่เงื่อนไขไหน
       อ้าง `{item.slots.video}` (ซึ่ง patch_default_tab ทำให้เกิดขึ้นทุกโหนด) — คำว่า video โผล่
       ในชื่อ slot ด้วย ไม่ใช่แค่ค่าของแท็บ ⇒ ยามจะเหมาเอาโหนดฝั่งบอร์ดเป็นฝั่งวิดีโอแล้วข้ามทิ้งเงียบ
       (ตระกูลเดียวกับกฎ "ยามต้องผูกกับกฎ ไม่ใช่รูปทรง")
    """
    found = [False]
    def go(w):
        if isinstance(w, dict):
            if w.get('op') == 'eq' and w.get('a') == '{item.view}' and w.get('b') == 'video':
                found[0] = True
            for v in w.values(): go(v)
        elif isinstance(w, list):
            for v in w: go(v)
    go(when)
    return found[0]


# เงื่อนไข "แท็บ default" 2 ก้อนที่กระจายอยู่ทั้ง config (ลิสต์ + กริด · ก้อนละ 8 ที่)
#   ของเดิมผูกกับ **บอร์ด**: มีบอร์ดแล้ว → default = แท็บวิดีโอ
_DEF_VID = {'op': 'and', 'a': {'op': 'eq', 'a': '{item.view}', 'b': ''},
            'b': {'op': 'not', 'a': {'op': 'eq', 'a': '{item.slots.board}', 'b': ''}}}
_DEF_BRD = {'op': 'and', 'a': {'op': 'eq', 'a': '{item.view}', 'b': ''},
            'b': {'op': 'eq', 'a': '{item.slots.board}', 'b': ''}}


def patch_default_tab(cfg):
    """แท็บที่เปิดให้เองตอนยังไม่ได้กดเลือก = **ของชิ้นล่าสุดที่มีจริง** (มีวิดีโอ→วิดีโอ · ไม่มี→บอร์ด)

    🔴 ทำไมต้องมาคู่กับ patch_video_placeholder เสมอ ห้ามทำอันเดียว:
       กฎเดิมคือ "มีบอร์ดแล้ว = default ไปแท็บวิดีโอ" แล้วแท็บวิดีโอ **ยืมภาพบอร์ดมาโชว์**
       พร้อมป้าย "ได้ภาพแล้ว — รอวิดีโอ" ⇒ มันเลยดูเหมือนใช้ได้
       พอเอาภาพยืมออก (ตามที่พี่หมีสั่ง) แท็บ default จะกลายเป็น**การ์ดเปล่า**ทันทีหลังกดสร้างภาพเสร็จ
       = ผู้ใช้เพิ่งสร้างบอร์ด แต่จอไม่โชว์บอร์ด ต้องไปกดแท็บเอง (แย่กว่าเดิม)
    ⇒ ย้ายหลักจาก `slots.board` เป็น `slots.video` ⇒ ทั้ง 3 สถานะเข้าที่พร้อมกัน:
       ยังไม่มีบอร์ด → แท็บบอร์ด "รอวาดภาพ" · มีบอร์ดยังไม่มีวิดีโอ → แท็บบอร์ด (เห็นบอร์ดที่เพิ่งสร้าง)
       มีวิดีโอแล้ว → แท็บวิดีโอ (เห็นคลิป)
    ★เป็นการสลับ "ชื่อ slot" ตัวเดียวในก้อนเงื่อนไขที่มีรูปเป๊ะ ๆ — ไม่แตะโครงสร้างอะไรเลย
    ★`el:segmented field:view` 3 ตัวใช้ก้อนเดียวกันนี้เป็น when ⇒ ปุ่มที่ไฮไลต์ตรงกับของที่โชว์เองอัตโนมัติ
    """
    sv, sb = json.dumps(_DEF_VID, sort_keys=True), json.dumps(_DEF_BRD, sort_keys=True)
    hit = 0

    def go(n):
        nonlocal hit
        if isinstance(n, dict):
            for k, v in list(n.items()):
                if isinstance(v, dict) and json.dumps(v, sort_keys=True) in (sv, sb):
                    v['b'] = json.loads(json.dumps(v['b']).replace('{item.slots.board}', '{item.slots.video}'))
                    hit += 1
                else:
                    go(v)
        elif isinstance(n, list):
            for i, v in enumerate(n):
                if isinstance(v, dict) and json.dumps(v, sort_keys=True) in (sv, sb):
                    v['b'] = json.loads(json.dumps(v['b']).replace('{item.slots.board}', '{item.slots.video}'))
                    hit += 1
                else:
                    go(v)
    go(cfg.get('phases'))
    return hit


def patch_video_placeholder(cfg):
    """แท็บ "วิดีโอ" ตอนยังไม่มีวิดีโอ = **การ์ดขอบเส้นประ "รอสร้างวิดีโอ"** (พี่หมีสั่ง 2026-09-10)

    ของเดิม: แท็บวิดีโอ **เอาภาพบอร์ดมาโชว์** แล้วแปะป้าย "ได้ภาพแล้ว — รอวิดีโอ" ทับล่างภาพ
      ⇒ ① ป้ายทับฉากที่ 5 ของสตอรีบอร์ด (โรคเดียวกับปุ่ม ‹ › ที่เพิ่งเอาออก)
         ② คนดูนึกว่าภาพนั้น "คือวิดีโอ" ทั้งที่เป็นบอร์ด — แท็บบอกอย่าง ของที่เห็นเป็นอีกอย่าง
    ⇒ เปลี่ยนเป็นการ์ดเส้นประแบบเดียวกับฝั่งบอร์ด ("รอวาดภาพ") — ภาษาเดิมของแอป ไม่ได้คิดของใหม่
    ★สถานะ "กำลังทำ/พักก่อนลองใหม่" ไม่หาย — ย้ายเข้ามาอยู่ในการ์ดเส้นประ (สปินเนอร์ + ข้อความ)
      เหมือนที่ฝั่งบอร์ดทำอยู่แล้ว ⇒ ไม่มีอะไรทับภาพ และไม่เสีย feedback ระหว่างรัน
    ★สถานะ error มีสาขาของตัวเอง — ไม่งั้นพังแล้วยังขึ้นว่า "รอสร้างวิดีโอ" = โกหก
    """
    BUSY = {'op': 'or', 'list': [{'op': 'eq', 'a': '{item.status}', 'b': 'running'},
                                 {'op': 'eq', 'a': '{item.meta.retrying}', 'b': '1'}]}
    ERR = {'op': 'eq', 'a': '{item.status}', 'b': 'error'}
    IDLE = {'op': 'and', 'a': {'op': 'not', 'a': BUSY}, 'b': {'op': 'not', 'a': ERR}}
    body = [
        {'el': 'icon', 'icon': 'movie', 'textSize': 'text-[26px]', 'when': IDLE,
         'className': 'opacity-25 leading-none flex items-center justify-center'},
        # 🪤 opacity ต้อง ≥0.6 — กฎในโปรเจกต์ (จางกว่านี้พี่หมี reject) · วัดของเดิมได้ 0.45 = ผิดกฎตัวเอง
        {'el': 'text', 'value': 'รอสร้างวิดีโอ', 'when': IDLE,
         'className': '!text-[13px] font-bold opacity-60'},
        {'el': 'spinner', 'className': '!text-[24px]', 'when': BUSY},
        {'el': 'text', 'when': BUSY, 'className': '!text-[13px] font-bold !text-[var(--ev-accent)] text-center px-2',
         'value': {'op': 'lookup', 'table': 'opNames', 'key': '{values.__runStage}', 'fallback': 'กำลังทำ…'}},
        {'el': 'icon', 'icon': 'error_outline', 'textSize': 'text-[26px]', 'when': ERR,
         'className': '!text-rose-500 opacity-70 leading-none flex items-center justify-center'},
        {'el': 'text', 'value': 'สร้างวิดีโอไม่สำเร็จ', 'when': ERR,
         'className': '!text-[13px] font-bold !text-rose-500 text-center px-2'},
    ]
    hit = 0
    for _, n in walk(cfg.get('phases')):
        if not (isinstance(n, dict) and isinstance(n.get('card'), list)): continue
        cd = n['card']
        if not (cd and isinstance(cd[0], dict) and cd[0].get('el') == 'media-slot'
                and cd[0].get('src') == '{item.slots.board}'): continue
        if not _is_video_tab(n.get('when')): continue
        # ★ต้องเป็นสาขา "ยังไม่มีวิดีโอ" เท่านั้น — สาขาที่มีวิดีโอแล้วเป็นคนละโหนด (src = slots.video)
        if '"{item.slots.video}", "b": ""' not in json.dumps(n.get('when'), ensure_ascii=False): continue
        n['card'] = [dict(b) for b in body]
        n['className'] = ('aspect-[9/16] rounded-2xl border-2 border-dashed border-[var(--ev-border)] '
                          'bg-[var(--ev-bg)]/60 flex flex-col items-center justify-center gap-2')
        hit += 1
    return hit


def patch_board_carousel(cfg):
    """คลิป 20/30 วิ มีบอร์ดหลายใบ → ดูทีละใบเต็มกรอบ แล้วสลับใบด้วยตัวควบคุมนอกภาพ

    🔴 บทเรียน 4 รอบก่อนหน้า (พี่หมีเจอกับตาทุกรอบ):
      รอบ 1 เอาไทล์ไปแทน media-slot ทุกที่ ⇒ กริด (โปสเตอร์ที่ของ absolute ทับภาพ) ยุบ กองทับกัน
      รอบ 2 บีบ 3 ใบให้พอดีกรอบ ⇒ ใบละ 100px อ่านไม่ออก · และโหมด "วิดีโอ" ก็โชว์ 3 ใบด้วย (งง)
      รอบ 3 แถบเลื่อนแนวนอน ⇒ พี่หมีว่าปุ่มสลับสวยกว่าและใช้ง่ายกว่า
      รอบ 4 ปุ่ม ‹ › ทับกลางภาพทั้ง 2 มุมมอง ⇒ **บังเนื้อสตอรีบอร์ดจริง** (ฉาก 3-4 กับหัวเรื่อง)

    ⇒ จบที่ **คนละท่าตามที่ว่างที่มีจริง ไม่ใช่ท่าเดียวกันทุกที่**:
      · ลิสต์ = ชิป [1][2][3] **ใต้ภาพ** — ภาพไม่โดนบังสักตารางนิ้ว + กดถึงใบที่ต้องการทันที
      · กริด = แถบ ‹ บอร์ด 1/3 › ทับล่าง — เพราะช่องกริดเป็นโปสเตอร์ ไม่มีที่ว่างใต้ภาพให้วางอะไร
        และภาพกริดเป็นรูปย่อ (ดูคร่าว ๆ) ไม่ใช่ที่ที่ผู้ใช้อ่านบท ⇒ ยอมให้ทับได้
    ★โหมด "วิดีโอ" ไม่แตะ (บอร์ดตรงนั้นเป็นตัวแทนช่องวิดีโอที่ยังว่าง ไม่ใช่ที่ตรวจแผน)
    """
    gids = _grid_view_ids(cfg)
    hit = 0
    nodes = [n for _, n in walk(cfg.get('phases')) if isinstance(n, dict) and isinstance(n.get('card'), list)]
    for n in nodes:
        cd = n['card']
        if not (cd and isinstance(cd[0], dict) and cd[0].get('el') == 'media-slot'
                and cd[0].get('src') == '{item.slots.board}'): continue
        if _is_video_tab(n.get('when')): continue   # โหมดวิดีโอ = กรอบเดียวเหมือนเดิม
        ms = cd[0]
        if id(n) in gids:
            # กริด = โปสเตอร์ · ของ absolute เกาะกล่องนี้อยู่แล้ว → ใส่ปุ่ม/ป้ายลงไปตรง ๆ ได้
            #   มุมขวาบนมีป้ายสถานะ · ซ้ายบนมีเลขคลิป · ล่างมีแถบชื่อ ⇒ ป้าย n/n ลงใต้เลขคลิป
            cd[0:1] = _board_frames(ms)
            cd.append(_grid_bar())
        else:
            # ลิสต์ = กล่อง flex-col (ภาพ แล้วปุ่มด้านล่าง) ⇒ ต้องห่อเฉพาะภาพด้วย relative
            #   ไม่งั้นปุ่มจะไปอยู่กลางกล่องทั้งใบ ไม่ใช่กลางภาพ · มุมขวาบนของกล่องนี้ว่าง
            cd[0:1] = _board_frames(ms) + [_chip_bar(), _step_bar()]
        hit += 1
    return hit



def patch_toggle_all(cfg):
    """ปุ่ม "ใช้ทั้งหมด / ปิดทั้งหมด" ในหน้าจัดการสินค้า — ข้อความตกบรรทัดบนมือถือ (พี่หมีเจอ 2026-09-09)
       🪤 ต้นเหตุ: กลุ่มปุ่มมี `flex-1 min-w-0` ⇒ **ยุบได้ต่ำกว่าความกว้างของข้อความ** แล้วตัวหนังสือก็ตกบรรทัด
          (min-w-0 ใส่ไว้กันล้น แต่มันกันเกินไป — ของที่ยุบไม่ได้จริง ๆ ไม่ควรใส่)
       ✅ ถอด min-w-0 ออก ⇒ ความกว้างต่ำสุดของกลุ่ม = ความกว้างข้อความ
          ถ้าจอแคบจนไม่พอจริง แถวนอกมี `flex-wrap` อยู่แล้ว มันจะขึ้นบรรทัดใหม่ให้เอง = ไม่มีทางล้น
       + ใส่ whitespace-nowrap ที่ตัวปุ่มเป็นชั้นที่ 2 (กันไว้ตรง ๆ ว่าข้อความห้ามหัก)
       ★ทั้งสองปุ่มเป็นคู่แฝด แก้พร้อมกันเสมอ"""
    n_grp = n_btn = 0
    for _, n in walk(cfg.get('phases')):
        if not (isinstance(n, dict) and n.get('el') == 'button' and n.get('action') == 'set-all'): continue
        cls = n.get('className') or ''
        if 'whitespace-nowrap' not in cls:
            n['className'] = (cls + ' whitespace-nowrap').strip(); n_btn += 1
    for _, n in walk(cfg.get('phases')):
        if not (isinstance(n, dict) and n.get('el') == 'row' and isinstance(n.get('card'), list)): continue
        kids = [c for c in n['card'] if isinstance(c, dict)]
        if not kids or not all(c.get('action') == 'set-all' for c in kids): continue   # กลุ่มที่มีแต่ปุ่ม set-all
        cls = n.get('className') or ''
        if 'min-w-0' in cls:
            n['className'] = ' '.join(x for x in cls.split() if x != 'min-w-0'); n_grp += 1
    return n_grp, n_btn


def patch_step_chips(cfg):
    """ชิปแถบขั้นตอน (1 ตั้งค่า · 2 ผลิต · 3 คลังคลิป) — ป้ายห้ามตกบรรทัด (พี่หมีเจอ 2026-09-09)
       🪤 ต้นเหตุ: ชิปที่ **active** เป็น el:row ซึ่งมี whitespace-nowrap อยู่แล้ว
          แต่ชิปที่ยังไม่ active เป็น el:button ที่ไม่มี ⇒ หน้าไหนที่ชิปนั้นไม่ active ป้ายก็ตกบรรทัด
          = ตัวเดียวกันแท้ ๆ แต่หน้าตาต่างกันตามสถานะ — เห็นแล้วงงว่าทำไมบางหน้าตกบางหน้าไม่ตก
       ⇒ เติม whitespace-nowrap ให้ปุ่มชิปทุกตัว (แถวมี overflow-x-auto อยู่แล้ว เลื่อนได้ ไม่ล้น)"""
    hit = 0
    for _, n in walk(cfg.get('phases')):
        if not (isinstance(n, dict) and n.get('el') == 'button' and n.get('to') == '__page'): continue
        if not (isinstance(n.get('label'), str) and re.match(r'^[1-4] \S', n['label'])): continue
        cls = n.get('className') or ''
        if 'whitespace-nowrap' not in cls:
            n['className'] = (cls + ' whitespace-nowrap').strip(); hit += 1
    return hit


# ป้ายความยาวคลิปบนหน้าจอ — เดิมฮาร์ดโค้ด "10 วิ" ทุกที่ (พี่หมีเจอ 2026-09-09: เลือก 20/30 แล้วป้ายยังขึ้น 10)
#   🪤 ป้ายที่โกหกอันตรายกว่าที่คิด — มันทำให้แยกไม่ออกว่า "ระบบทำผิด" หรือ "ป้ายเขียนผิด"
#      ⇒ พอทำให้ป้ายพูดความจริง มันกลายเป็นเครื่องมือวินิจฉัยไปในตัว
SEC = {'op': 'lookup', 'table': 'lenSecs', 'key': '{values.svSec}', 'fallback': '10'}
DURATION_LABELS = {
    '10 วิ / คลิป':                 [dict(SEC), ' วิ / คลิป'],
    'Omni 1.1 Flash · 10 วิ · 9:16': ['Omni 1.1 Flash · ', dict(SEC), ' วิ · 9:16'],
}


def patch_duration_labels(cfg):
    hit = 0
    for _, n in walk(cfg.get('phases')):
        if not (isinstance(n, dict) and n.get('el') == 'text'): continue
        v = n.get('value')
        if isinstance(v, str) and v in DURATION_LABELS:
            n['value'] = {'op': 'concat', 'parts': copy.deepcopy(DURATION_LABELS[v])}
            hit += 1
    return hit


# ป้ายหัวช่องในหน้าตั้งค่า: (ข้อความเดิม) → (ไอคอน, ข้อความใหม่, คำอธิบายใหม่ · None = เอาคำอธิบายออก)
SETUP_LABELS = {
    'ชื่อโปรเจกต์': ('folder', 'ชื่อโปรเจกต์ (ไม่บังคับ)', 'เว้นว่าง = ตั้งให้จากชื่อสินค้าตัวแรก'),
    'จำนวนคลิป/สินค้า': ('content_copy', 'จำนวนคลิป/สินค้า', 'แต่ละคลิปบท/มุมกล้องต่างกัน · สูงสุด 10'),
}


def patch_setup_labels(cfg):
    """เติมไอคอนหน้าป้ายหัวช่อง + ย่อคำอธิบายให้กระชับ (พี่หมีสั่ง — ให้หน้าตาเป็นตระกูลเดียวกับ hardsell)"""
    hit = 0
    # 🪤 ต้องเก็บรายชื่อกล่องให้ครบ **ก่อน** แก้ — ป้ายใหม่ที่สร้างมีข้อความเดิมอยู่ข้างใน
    #    ถ้าแก้ไปเดินไป walk จะเดินเข้าไปเจอข้อความนั้นแล้วแทนตัวเองซ้อนไปเรื่อย ๆ (RecursionError)
    for box in [b for _, b in list(walk(cfg.get('phases')))]:
        if not (isinstance(box, dict) and isinstance(box.get('card'), list)): continue
        for i, c in enumerate(box['card']):
            # 🪤 value เป็น Binding (dict) ได้ — ต้องเช็คว่าเป็นสตริงก่อน ไม่งั้น `in SETUP_LABELS` โยน unhashable
            if not (isinstance(c, dict) and c.get('el') == 'text'
                    and isinstance(c.get('value'), str) and c['value'] in SETUP_LABELS): continue
            icon, label, sub = SETUP_LABELS[c['value']]
            box['card'][i] = field_label(icon, label)
            # คำอธิบายคือ text ตัวถัดไปในกล่องเดียวกัน — แก้ให้กระชับ หรือถอดทิ้งถ้า sub เป็น None
            nx = box['card'][i + 1] if i + 1 < len(box['card']) else None
            if isinstance(nx, dict) and nx.get('el') == 'text' and isinstance(nx.get('value'), str):
                if sub is None: box['card'].pop(i + 1)
                else: nx['value'] = sub
            hit += 1
            break
    return hit


# ─────────────────────────────────────────────────────────────────────────────
RE_FIELD_S = re.compile(r'^s(\d+)(th|en)$')
RE_FIELD_X = re.compile(r'^(ov|vo|cam)(\d+)$')


def shift_ui_row(node, off):
    """เหมือน shift_scene_refs แต่เลื่อน `"field": "s1th"` ของ UI ด้วย (ฝั่ง prompt ใช้ {item.*} · ฝั่ง UI ใช้ field)"""
    node = shift_scene_refs(node, off)

    def fix(n):
        if isinstance(n, dict):
            out = {}
            for k, v in n.items():
                if k in ('field', 'to') and isinstance(v, str):
                    m = RE_FIELD_S.match(v)
                    if m: v = 's%d%s' % (int(m.group(1)) + off, m.group(2))
                    else:
                        m = RE_FIELD_X.match(v)
                        if m: v = '%s%d' % (m.group(1), int(m.group(2)) + off)
                out[k] = fix(v)
            return out
        if isinstance(n, list): return [fix(x) for x in n]
        return n
    return fix(node)


def act_label(sec, n):
    k = per_act(sec)
    return ACT_NAME_TH[(n - 1) // k] + SUF_TH[(n - 1) % k]


def patch_script_rows(cfg):
    """หน้าบท: ป้ายองก์รายฉาก → lookup (10 วิ ได้คำเดิม) + สร้างแถวฉาก 6-15 เป็นสำเนาเลื่อนดัชนี"""
    lk = cfg['lookups']
    lk['sceneAct'] = {'%d|%d' % (sec, n): act_label(sec, n) for sec in LENS for n in range(1, scenes_of(sec) + 1)}

    def is_row(c, n):
        return isinstance(c, dict) and ('"field": "s%dth"' % n) in json.dumps(c, ensure_ascii=False)

    hits = 0
    for _, box in walk(cfg.get('phases')):
        if not (isinstance(box, dict) and isinstance(box.get('card'), list) and len(box['card']) == 5): continue
        if not all(is_row(box['card'][i], i + 1) for i in range(5)): continue
        # ★แถวฉาก 1-5: ป้ายชื่อองก์ต้องขึ้นกับความยาว (20 วิ ฉาก 2 = "เปิดตัว (ต่อ)" ไม่ใช่ "จุดเด่น")
        for i in range(5):
            box['card'][i] = label_row(box['card'][i], i + 1, ACT_NAME_TH[i])
        # แถวฉาก 6-15 = สำเนาเลื่อนดัชนีของแถว 1-5 + ประตูตามความยาว
        for seg in (2, 3):
            for i in range(5):
                n = seg * 5 - 5 + i + 1
                r = shift_ui_row(copy.deepcopy(box['card'][i]), (seg - 1) * 5)
                r = retime_row(r, n)
                r['when'] = 'values.svSec>%d' % ((seg - 1) * 10)
                box['card'].append(r)
        hits += 1
    return hits


def label_row(row, n, act10):
    """เปลี่ยนป้าย 'เปิดตัว' (คงที่) → lookup ตามความยาว · fallback = คำเดิมของ 10 วิ"""
    def fix(x):
        if isinstance(x, dict) and x.get('el') == 'text' and x.get('value') == act10:
            y = dict(x); y['value'] = {'op': 'lookup', 'table': 'sceneAct',
                                       'key': '{values.svSec}|%d' % n, 'fallback': act10}
            return y
        if isinstance(x, dict): return {k: fix(v) for k, v in x.items()}
        if isinstance(x, list): return [fix(v) for v in x]
        return x
    return fix(row)


def retime_row(row, n):
    """แถวที่ก๊อปมา: เลขฉาก + ช่วงเวลา + คีย์ lookup ต้องเป็นของฉากใหม่"""
    src = ((n - 1) % 5) + 1
    old_time, new_time = '%d-%d วิ' % ((src - 1) * 2, src * 2), '%d-%d วิ' % ((n - 1) * 2, n * 2)

    def fix(x):
        if isinstance(x, dict):
            y = {}
            for k, v in x.items():
                if k == 'value' and v == str(src) and x.get('el') == 'text': v = str(n)
                elif k == 'value' and v == old_time and x.get('el') == 'text': v = new_time
                elif k == 'key' and isinstance(v, str) and v.startswith('{values.svSec}|') and x.get('table') == 'sceneAct':
                    v = '{values.svSec}|%d' % n
                elif k == 'fallback' and x.get('table') == 'sceneAct': v = ''   # ฉาก 6-15 ไม่มีทางอยู่ในโหมด 10 วิ
                y[k] = fix(v)
            return y
        if isinstance(x, list): return [fix(v) for v in x]
        return x
    return fix(row)


# ─────────────────────────────────────────────────────────────────────────────
def main():
    files = sys.argv[1:] or ['minimal-lab.json']
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for fn in files:
        p = fn if os.path.isabs(fn) else os.path.join(root, fn)
        cfg = json.load(open(p, encoding='utf-8'))
        build_lookups(cfg)
        patch_values(cfg)
        patch_collections(cfg)
        patch_queue(cfg)
        patch_plan(cfg)
        patch_ops(cfg)
        ns, np_, nb, npk, nr, nl, nc, nd, nta, nch, nbt = patch_ui(cfg)
        # 🔴 ต้องรัน **หลัง** patch_ui — ประโยค 'กติกาสำคัญ: ใช้ "สินค้าที่แนบมา" เป็นต้นแบบ' ที่ patch นี้แทนที่
        #    เป็น **anchor ของ _board_prev_note** (บล็อกกติกาความต่อเนื่อง) ที่ patch_ui เรียก
        #    ⇒ รันก่อน = anchor หาย แล้วบล็อกความต่อเนื่องไม่ถูกแทรก **แบบเงียบ ๆ** (ยาม ⑪ จับได้)
        #    📌 บทเรียน: ข้อความใน prompt เป็น 'จุดยึด' ของ patch ตัวอื่นได้ — แทนที่เมื่อไหร่ต้องไล่ดูว่าใครใช้มันเป็น anchor
        n_pl = patch_product_lock(cfg) + patch_vo_fill(cfg) + patch_vo_seam(cfg)
        json.dump(cfg, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        open(p, 'a', encoding='utf-8').write('\n')
        print('✅ %-18s ops=%d · ป้ายฉาก %d คีย์ · ทางออกวิดีโอรวมช่วง %d · ปุ่มรันชุด %d · กล่องบอร์ด %d · ปุ่มเลือกความยาว %d · ชุดแถวบท %d · ป้ายหัวช่อง %d · ชิปขั้นตอน %d · ป้ายความยาว %d · ปุ่มทั้งหมด %s · ปุ่มรายคลิปทำครบช่วง %d · การ์ดโชว์บอร์ดครบ %d · ล็อกสินค้า+บทพูดเต็ม %d'
              % (os.path.basename(p), len(cfg['ops']), len(cfg['lookups']['sceneLab']), ns, np_, nb, npk, nr, nl, nc, nd, nta, nch, nbt, n_pl))


if __name__ == '__main__':
    main()
