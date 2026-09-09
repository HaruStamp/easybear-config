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
    cfg['stages'] = [{'op': i} for i in order] + [s for s in cfg['stages'] if 'checkpoint' in s]


# ─────────────────────────────────────────────────────────────────────────────
SEGS = [{'slot': 'video'}, {'slot': 'video2'}, {'slot': 'video3'}]


LBL_CLS = ('!text-[13px] @[640px]:!text-[12.5px] !text-[var(--ev-text)] opacity-65 '
           'uppercase tracking-[0.14em] font-black px-0.5')
SUB_CLS = '!text-[15px] @[640px]:!text-[14px] opacity-70 px-0.5'


def len_picker():
    """การ์ดเลือกความยาว — วางในกลุ่ม 3 การผลิต ต่อจากตัวนับจำนวนคลิป (ชุด class ยกจากตัวนับตัวนั้นมาเลย)"""
    return {'el': 'box', 'className': 'flex flex-col gap-2.5', 'card': [
        {'el': 'box', 'className': 'flex flex-col gap-1', 'card': [
            {'el': 'text', 'value': 'ความยาวคลิป', 'className': LBL_CLS},
            {'el': 'text', 'className': SUB_CLS,
             'value': 'ยาวขึ้น = เรื่องยาวขึ้น ไม่ใช่คลิปเดิมยืดออก · หมีเขียนบทรอบเดียวให้จบพอดีตามวินาทีที่เลือก'},
        ]},
        {'el': 'segmented', 'field': 'svSec',
         'labelClass': '!text-[18px] @[640px]:!text-[17px]',
         'options': [{'value': '10', 'label': '10 วินาที', 'icon': 'timer'},
                     {'value': '20', 'label': '20 วินาที', 'icon': 'timer'},
                     {'value': '30', 'label': '30 วินาที', 'icon': 'timer'}],
         'selClass': '!bg-[var(--ev-accent)] !text-white !border-transparent',
         'className': ('!min-h-[48px] @[420px]:!min-h-0 [&>div:last-child]:!grid '
                       '[&>div:last-child]:!grid-cols-3 @[420px]:[&>div:last-child]:!flex')},
        # ★บอกราคาไปเลยตั้งแต่ตอนเลือก — ยาวขึ้น = ยิงโมเดลวิดีโอมากขึ้นตามตรง ไม่ใช่ของฟรี
        {'el': 'text', 'when': 'values.svSec>10', 'className': SUB_CLS + ' !opacity-90',
         'value': {'op': 'concat', 'parts': [
             'คลิปนี้จะถูกสร้างเป็น ',
             {'op': 'max', 'a': {'op': 'div', 'a': '{values.svSec}', 'b': 10}, 'b': 1},
             ' ช่วง ช่วงละ 10 วินาที แล้วต่อกันให้อัตโนมัติ — ใช้โควตาวิดีโอเท่าจำนวนช่วง']}},
    ]}


def extra_board_slots():
    """บอร์ดช่วง 2/3 — ต่อท้ายกล่องบอร์ดเดิม โผล่เฉพาะตอนคลิปยาวพอ"""
    out = []
    for seg in (2, 3):
        out.append({'el': 'box', 'className': 'flex flex-col gap-1 mt-2',
                    'when': 'values.svSec>%d' % ((seg - 1) * 10), 'card': [
                        {'el': 'text', 'value': 'สตอรีบอร์ดช่วงที่ %d (ฉาก %d-%d)' % (seg, (seg - 1) * 5 + 1, seg * 5),
                         'className': LBL_CLS},
                        {'el': 'media-slot', 'src': '{item.slots.board%d}' % seg, 'aspect': '9:16',
                         'style': {'borderRadius': '16px'}, 'className': 'ring-1 ring-[var(--ev-border)]'},
                    ]})
    return out


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
        # ③ กล่องที่มีแต่บอร์ดช่วงแรก → ต่อบอร์ดช่วง 2/3 ท้ายกล่อง
        if el == 'box' and isinstance(n.get('card'), list) and len(n['card']) == 1 \
           and isinstance(n['card'][0], dict) and n['card'][0].get('src') == '{item.slots.board}' \
           and n['card'][0].get('el') == 'media-slot':
            n['card'] += extra_board_slots(); n_board += 1

    # ④ ปุ่มเลือกความยาว — กลุ่ม "การผลิต" ต่อจากตัวนับจำนวนคลิป
    n_pick = 0
    for _, n in walk(cfg.get('phases')):
        if isinstance(n, dict) and n.get('el') == 'group' and isinstance(n.get('card'), list):
            body = json.dumps(n, ensure_ascii=False)
            if '"clipsPerProduct"' in body and '"svSec"' not in body:
                at = next((i for i, c in enumerate(n['card'])
                           if '"clipsPerProduct"' in json.dumps(c, ensure_ascii=False)), 0)
                n['card'].insert(at + 1, len_picker()); n_pick += 1
    n_rows = patch_script_rows(cfg)
    return n_seg, n_phase, n_board, n_pick, n_rows


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
        ns, np_, nb, npk, nr = patch_ui(cfg)
        json.dump(cfg, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        open(p, 'a', encoding='utf-8').write('\n')
        print('✅ %-18s ops=%d · ป้ายฉาก %d คีย์ · ทางออกวิดีโอรวมช่วง %d · ปุ่มรันชุด %d · กล่องบอร์ด %d · ปุ่มเลือกความยาว %d · ชุดแถวบท %d'
              % (os.path.basename(p), len(cfg['ops']), len(cfg['lookups']['sceneLab']), ns, np_, nb, npk, nr))


if __name__ == '__main__':
    main()
