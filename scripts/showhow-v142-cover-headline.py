#!/usr/bin/env python3
"""showhow-v142 — หัวเรื่องบนปก TikTok (mnCover) ต้องเป็นอักษรไทยตรงตัว ห้ามแปล ห้ามแปะแคปชันทั้งย่อหน้า
ต้นเรื่อง: เทสจริง minimal 26 พ.ย. — ปกแปลหัวเรื่องไทยเป็นอังกฤษ + แปะ {item.caption} ทั้งย่อหน้าเป็นป้ายรอง
showhow v140 ไม่ได้ส่ง caption เข้าปกอยู่แล้ว แต่ให้โมเดล "คิดหัวเรื่องไทย 2-6 คำเอง" = เสี่ยงสะกดเพี้ยน/แปล
ใหม่ (พากย์ไทย): ให้ข้อความสำเร็จรูปในเครื่องหมายคำพูด = ov1 (หัวเรื่องเปิดคลิป ≤~22 ตัว) · ไม่มี ov1 = ชื่องานตัดที่ 20 ตัว
  "copy it letter for letter in Thai script, never translate" · ห้ามบรรทัดที่สอง/ป้ายรอง/แคปชัน
พากย์ English = คงเดิม (หัวเรื่องอังกฤษสั้น) + ห้ามแคปชันเช่นกัน
ใช้: python3 scripts/showhow-v142-cover-headline.py  (รันบน v141 · รันซ้ำ = ไม่ทำอะไร)
"""
import json, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
s0 = open(P, encoding='utf-8').read()
c = json.loads(s0)
assert json.dumps(c, ensure_ascii=False, indent=1) + '\n' == s0
op = next(o for o in c['ops'] if o['id'] == 'mnCover')
parts = op['prompt']['parts']
TH_OLD = "big bold short Thai title (2-6 words) about this job, exact correct Thai spelling,"
blk = next(p for p in parts if isinstance(p, dict) and p.get('op') == 'block' and any(x.get('value') == TH_OLD for x in p['parts']))
if 'caption' in json.dumps(op['prompt'], ensure_ascii=False):
    raise SystemExit('mnCover อ้าง caption — ตรวจมือก่อน')
TITLE = {'op': 'cond', 'when': {'op': 'not', 'a': {'op': 'eq', 'a': '{item.ov1}', 'b': ''}},
         'then': {'op': 'clamp', 'value': '{item.ov1}', 'max': 24},
         'else': {'op': 'clamp', 'value': '{item.productName}', 'max': 20}}
for x in blk['parts']:
    if x.get('value') == TH_OLD:
        x['value'] = {'op': 'concat', 'parts': ['the exact Thai text "', TITLE,
                      '" — copy it letter for letter in Thai script, big and bold, never translate or reword it, on a single line,']}
    elif x.get('when') == 'values.svLang=English':
        x['value'] = "big bold short English title (2-5 words) about this job, on a single line,"
i = parts.index("Bright, clean, high-contrast TikTok cover look, at most one small arrow or sparkle accent. No other text, no logos, no watermark, no emoji.")
parts[i] = "Bright, clean, high-contrast TikTok cover look, at most one small arrow or sparkle accent. No other text: no subtitle, no caption paragraph, no labels, no logos, no watermark, no emoji."
print('✅ v142: หัวเรื่องปกตรงตัว (ov1 → ชื่องาน) · ห้ามแคปชัน/ป้ายรอง')
open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
