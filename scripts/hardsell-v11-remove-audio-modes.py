#!/usr/bin/env python3
# hardsell-v11-remove-audio-modes.py — ถอดตัวเลือก "ไม่มีเสียงพากย์" + "ASMR" ออก ⇒ มีเสียงพากย์เสมอ (พี่หมีสั่ง 2026-09-27)
#
# ที่มา: แอป hardsell เดิม (Flow app ก่อน engine · `src/`) **ไม่มีตัวเลือกโหมดเสียงเลย** — พากย์เสมอ
#   ตัวเลือก 3 ทางติดมาตอนยกโครง minimal มาเป็น hardsell (`8b14752` · 2026-09-14) · พี่หมี: "Hardsell ไม่มีโหมด asmr"
#   ⇒ ถอดออกทั้งคู่ (พี่หมีเลือก) · ปัญหา "คำสั่งพูดขัดกับ AUDIO LOCK" ในโหมดไม่มีเสียง (§③ ข้อ 3③) หายไปทั้งหมด
#
# วิธี: ทุก `when` ที่อ้าง svAudio มี 4 รูปแบบ และ **อ้าง svAudio ล้วน ๆ ไม่ปนค่าอื่น** (ตรวจแล้ว · ยามข้างล่างบังคับ)
#   ⇒ ตรึง svAudio = 'มีเสียงพากย์' แล้วประเมินได้แน่นอน: เป็นจริง = แกะ `when` ออก · เป็นเท็จ = ลบทั้งก้อน
#   🪤 ไม่ใช้ท่า "ซ่อนตัวเลือกแต่ปล่อย branch ไว้" — ไฟล์เซฟเก่า/คำสั่ง set-values ตั้ง svAudio=ASMR ได้
#      แล้วผู้ใช้ไม่มีปุ่มให้กดกลับ ⇒ prompt ไม่มีทั้งบล็อกพากย์และบล็อก ASMR · ถอดจริงทำให้ค่านั้นไม่มีผลอะไรเลย
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEEP = 'มีเสียงพากย์'
DROP = ('ไม่มีเสียงพากย์', 'ASMR')
REF = '{values.svAudio}'


def refs(n):
    return 'svAudio' in json.dumps(n, ensure_ascii=False)


def ev(w):
    """ประเมิน when ที่อ้าง svAudio ล้วน โดยตรึง svAudio = KEEP · รูปแบบอื่น = หยุด (ห้ามเดา)"""
    op = w.get('op') if isinstance(w, dict) else None
    if op == 'eq':
        a, b = w['a'], w['b']
        assert REF in (a, b), 'eq ที่ไม่ได้เทียบ svAudio: %r' % w
        other = b if a == REF else a
        assert other in (KEEP,) + DROP, 'เทียบ svAudio กับค่าที่ไม่รู้จัก: %r' % other
        return other == KEEP
    if op == 'not':
        return not ev(w['a'])
    if op == 'and':
        return all(ev(x) for x in w['list'])
    if op == 'or':
        xs = w.get('list') or [w['a'], w['b']]
        return any(ev(x) for x in xs)
    raise AssertionError('รูปแบบ when ที่ไม่รู้จัก — หยุดก่อน ห้ามเดา: %s' % json.dumps(w, ensure_ascii=False)[:200])


stat = {'unwrap': 0, 'drop': 0}


def fix(n):
    """คืน (โหนดใหม่, เก็บไว้ไหม)"""
    if isinstance(n, list):
        out = []
        for x in n:
            y, keep = fix(x)
            if keep:
                out.append(y)
        return out, True
    if not isinstance(n, dict):
        return n, True
    if 'when' in n and refs(n['when']):
        if not ev(n['when']):
            stat['drop'] += 1
            return None, False
        stat['unwrap'] += 1
        rest = {k: v for k, v in n.items() if k != 'when'}
        if set(rest) == {'value'}:                       # {when, value} ⇒ เหลือแค่ value
            return fix(rest['value'])[0], True
        n = rest                                         # การ์ด/ปุ่มที่มี when ⇒ ถอดแค่ when
    return {k: fix(v)[0] for k, v in n.items()}, True


def main():
    src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json'))
    cfg = json.load(open(src, encoding='utf-8'))
    if 'svAudio' not in json.dumps(cfg, ensure_ascii=False):
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร'); return
    assert cfg['values'].get('svAudio') == KEEP, 'ค่าเริ่มต้น svAudio ต้องเป็น %r' % KEEP

    # ① ตัวเลือกบนหน้าตั้งค่า — ลบการ์ดที่ผูก field svAudio (ต้องเจอ 1 ใบพอดี)
    found = []
    def drop_field(n):
        if isinstance(n, list):
            keep = [x for x in n if not (isinstance(x, dict) and x.get('field') == 'svAudio')]
            found.extend(x for x in n if isinstance(x, dict) and x.get('field') == 'svAudio')
            n[:] = keep
            for x in n: drop_field(x)
        elif isinstance(n, dict):
            for v in n.values(): drop_field(v)
    drop_field(cfg['phases'])
    assert len(found) == 1, 'การ์ดตัวเลือก svAudio เจอ %d ใบ (ควร 1)' % len(found)
    assert [o['value'] for o in found[0]['options']] == [KEEP, *DROP], 'ตัวเลือกไม่ตรงที่ตรวจไว้'

    # ② ทุก when ที่อ้าง svAudio (ops + phases)
    cfg['ops'] = fix(cfg['ops'])[0]
    cfg['phases'] = fix(cfg['phases'])[0]

    # ②b ตารางที่ผูกกับโหมดที่ถอดออก
    #   audioPlan = คีย์ 'ไม่มีเสียงพากย์'/'ASMR' ล้วน · ถูกเรียกจากบล็อก mnPlan ที่ถูกลบในขั้น ② เท่านั้น ⇒ ลบทั้งตาราง
    assert sorted(cfg['lookups']['audioPlan']) == sorted(DROP), 'audioPlan มีคีย์อื่นนอกจาก 2 โหมดที่ถอด'
    assert 'audioPlan' not in json.dumps({k: v for k, v in cfg.items() if k != 'lookups'}, ensure_ascii=False), \
        'ยังมีที่เรียก audioPlan ค้าง'
    del cfg['lookups']['audioPlan']
    #   textPlan['ไม่มีข้อความ'] มีประโยคเงื่อนไข "ถ้าปิดเสียงพากย์ด้วย (เงียบ/ASMR)…" ⇒ ตอนนี้พากย์เปิดเสมอ ตัดเงื่อนไขทิ้ง
    TP_OLD = ('และให้เสียงพากย์ voN ทุกฉาก ช่วยแบกสารเฉพาะเมื่อโหมดเสียงพากย์เปิดอยู่ — ถ้าปิดเสียงพากย์ด้วย '
              '(เงียบ/ASMR) ต้องเล่าให้เข้าใจครบด้วยภาพล้วน ไม่มีทั้งตัวหนังสือและคำพูด')
    TP_NEW = 'และให้เสียงพากย์ voN ทุกฉาก ช่วยแบกสาร'
    tp = cfg['lookups']['textPlan']
    assert tp['ไม่มีข้อความ'].count(TP_OLD) == 1, 'ประโยคเงื่อนไขใน textPlan ไม่ตรงที่ตรวจไว้'
    tp['ไม่มีข้อความ'] = tp['ไม่มีข้อความ'].replace(TP_OLD, TP_NEW)

    # ③ ค่าใน values — ลบเมื่อไม่มีใครอ้างแล้วเท่านั้น
    body = json.dumps({k: v for k, v in cfg.items() if k != 'values'}, ensure_ascii=False)
    assert 'svAudio' not in body, 'ยังมีที่อ้าง svAudio ค้าง: %s' % body[body.index('svAudio') - 80:body.index('svAudio') + 40]
    del cfg['values']['svAudio']

    # ── ยาม ──
    s = json.dumps(cfg, ensure_ascii=False)
    assert 'svAudio' not in s
    assert 'AUDIO LOCK' not in s, 'บล็อก AUDIO LOCK (ของโหมดไม่มีเสียง) ต้องหายหมด'
    assert 'ASMR' not in s, 'คำว่า ASMR ต้องหายหมด'
    ops = {o['id']: o for o in cfg['ops']}
    for oid in ('mnVideo', 'mnVideo2'):
        p = json.dumps(ops[oid]['prompt'], ensure_ascii=False)
        assert 'continuous Thai narration' in p, '%s: บล็อกพากย์ต้องยังอยู่ (ถูกแกะ when ไม่ใช่ถูกลบ)' % oid
        assert 'voiceLockEN' in p, '%s: VOICE LOCK ต้องยังอยู่' % oid
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v11 ลงแล้ว — %s' % os.path.basename(src))
    print('   ① ลบการ์ดตัวเลือกเสียง 1 ใบ (มีเสียงพากย์ / ไม่มีเสียงพากย์ / ASMR)')
    print('   ② เงื่อนไขที่อ้างโหมดเสียง: แกะออก (เป็นจริงเสมอ) %d · ลบทิ้ง (เป็นไปไม่ได้แล้ว) %d' % (stat['unwrap'], stat['drop']))
    print('   ②b ลบตาราง audioPlan (มีแต่ 2 โหมดที่ถอด) · ตัดประโยค "ถ้าปิดเสียงพากย์ (เงียบ/ASMR)" ใน textPlan')
    print('   ③ ลบ values.svAudio (ไม่มีใครอ้างแล้ว)')


main()
