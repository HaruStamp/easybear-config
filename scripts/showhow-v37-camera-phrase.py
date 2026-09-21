#!/usr/bin/env python3
"""showhow v37 — บีบวลีมุมกล้องอัตโนมัติ 41 → 34 ตัวอักษร (คืน 35 ตัวอักษรต่อ prompt วิดีโอ)

ทำไม: ตัววัดในเครื่อง (ยืนยันตรงกับ engine v1.9.0 ทุกไบต์) ชั้นตัดสิน p95 พบ mnVideo* ยาวสุด 3,955/3,900
  หลัง v36 ถอด PACING แล้วยังเกิน 55 ⇒ ส่วนที่โดนตัดคือบรรทัด Negative (ซึ่งมีกฎ "no tripod or camera gear")
  ⇒ ต้องคืนที่อีกหน่อยให้ **แม้แต่เคสสังเคราะห์ p95 ทุกช่องพร้อมกัน ก็ยังไม่กินบรรทัด Negative**

เลือกจุดนี้เพราะเป็นข้อความ **fallback ของมุมกล้องอัตโนมัติ** (ผู้ใช้ไม่ได้เลือกมุมเอง) ซ้ำ 5 ฉาก × 6 ช่วง = 30 จุด
  ความหมายเท่าเดิม · ไม่ใช่กฎ ไม่ใช่ล็อก ⇒ ความเสี่ยงต่ำสุดในบรรดาที่บีบได้
🪤 ห้ามบีบถ้อยคำสายสินค้า/ล็อก — v18b เคยบีบแล้วผลจริงเพี้ยน (ขวดสีม่วง ห้องผิด) ต้องถอยกลับ v19
"""
import pathlib

P = pathlib.Path(__file__).resolve().parent.parent / 'showhow-dev.json'
s = P.read_text(encoding='utf-8')
OLD, NEW = 'smooth cinematic move that suits the scene', 'a cinematic move suiting the scene'
n = s.count(OLD)
assert n == 30, f'เจอ {n} จุด (คาด 30 = 5 ฉาก × 6 ช่วง) — หยุด'
P.write_text(s.replace(OLD, NEW), encoding='utf-8')
print(f'บีบ {n} จุด · คืน {(len(OLD)-len(NEW))*5} ตัวอักษรต่อ prompt (5 ฉาก/ช่วง)')
