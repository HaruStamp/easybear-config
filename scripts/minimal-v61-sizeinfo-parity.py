# minimal-dev v61: products.fields ต้องตรง hardsell-dev ทุกไบต์ (ยาม cross-app-load · โหลดงานข้ามแอป) — hardsell v29 เพิ่ม sizeInfo ⇒ minimal เพิ่มช่องเดียวกัน (ยังไม่มี UI/prompt ใช้)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json'
d = json.load(open(F)); f = d['collections']['products']['fields']
if 'sizeInfo' not in f: f.insert(f.index('price') + 1, 'sizeInfo')
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))
# + mnCover ต้องเป็น aux (กดเอง) — ไม่งั้น itemRunCounts นับปกเป็นงานค้าง คลิปเสร็จไม่ถูกนับ (ยาม blank-page แดง 26 พ.ย.)
d = json.load(open(F))
for o in d['ops']:
    if o.get('id') == 'mnCover': o['aux'] = True
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))
