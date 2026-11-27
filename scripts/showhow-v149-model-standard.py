#!/usr/bin/env python3
# showhow-v149-model-standard — มาตรฐานโมเดลทุกแอป (พี่หมี 27 พ.ย. 2569): บล็อกตั้งค่าเดียวกันทุกแอป โมเดลภาพ 3 ปุ่ม · โมเดลวิดีโอ Omni 1.1/1.2 · ความละเอียด 720p/360p (ทั้ง 2 รุ่น) · สรุปเครดิต
#   ต้นฉบับเดียว = model-standard.py สูตร "showhow" (dev และตัวขาย · ค่าเริ่มคงเดิม · คำขอที่ค่าเริ่มเท่าเดิมทุกไบต์ ตรวจด้วย model-standard-proof.ts)
# ใช้: python3 scripts/showhow-v149-model-standard.py <ไฟล์>   (ค่าเริ่ม showhow-dev.json · ห้ามรันซ้ำ — assert ดักไว้)
import os, runpy, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
sys.argv = [sys.argv[0], 'showhow', F]
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model-standard.py'), run_name='__main__')
