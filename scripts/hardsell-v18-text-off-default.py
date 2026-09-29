#!/usr/bin/env python3
# hardsell-v18-text-off-default.py — ค่าตั้งต้นข้อความบนจอ = ไม่มีข้อความ (พี่หมีเคาะ 2026-09-29 · ข้อ ก)
#   หลักฐาน 5 คลิปจริงบนบัญชีสำรอง (A·C·D·E·F): Veo วาด/ขยับตัวหนังสือไทยแล้วเพี้ยนทุกครั้ง · ปิดข้อความ (B·G) = คลิปสะอาด
#   ผู้ใช้ยังเลือก "มีข้อความ" เองได้เหมือนเดิม — แก้แค่ค่าเริ่มต้นใน values
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json'))
    cfg = json.load(open(src, encoding='utf-8'))
    if cfg['values'].get('svTextOn') == 'ไม่มีข้อความ':
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร'); return
    assert cfg['values'].get('svTextOn') == 'มีข้อความ', cfg['values'].get('svTextOn')
    cfg['values']['svTextOn'] = 'ไม่มีข้อความ'
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v18 ลงแล้ว — ค่าตั้งต้น svTextOn = ไม่มีข้อความ')


main()
