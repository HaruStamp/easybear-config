#!/usr/bin/env python3
"""showhow-v140 — แคปชัน + แฮชแท็ก + ปกคลิป TikTok (เจ้าของสั่ง 26 พ.ย. · ลอกท่า fashion-dev)
- บท (lenOut ทั้ง 6 ความยาว): เพิ่มคีย์ caption + hashtags ต่อจาก synopsis · ภาษาตามเสียงพากย์ (English = อังกฤษ · อื่น = ไทย)
- mnQueue: ส่ง caption/hashtags ลงงานย่อย · tasks.fields += caption, hashtags · tasks.slots += cover
- op ใหม่ mnCover (image 9:16 · over tasks · out cover · aux = ปุ่มกดเอง ไม่อยู่ใน stages/gens ตามแบบ fashion)
  อ้างอิง: บอร์ดช่วง 1 ของคลิป + รูปสินค้า + รูปหน้าตัวละคร (ถ้ามี) · มีหัวเรื่องบนปก ⇒ model = Nano Banana Pro (กติกา v137: มีข้อความบนภาพ → Pro)
- หน้าผลิต มุมมองการ์ด กล่อง 'วิดีโอเสร็จ': กล่อง 'โพสต์ TikTok' = ปก (ทำปก/ทำใหม่/โหลด) + แคปชัน + แฮชแท็ก + ปุ่มคัดลอก
ใช้: python3 scripts/showhow-v140-tiktok-cover.py  (รันบน v139)
"""
import json
P = 'showhow-dev.json'
s0 = open(P, encoding='utf-8').read()
c = json.loads(s0)
assert json.dumps(c, ensure_ascii=False, indent=1) + '\n' == s0
ops = {o['id']: o for o in c['ops']}
assert 'mnCover' not in ops, 'รันซ้ำ'
L = c['lookups']

# ── บท ──
ANCH = '"synopsis":"เรื่องย่อคลิป 1-2 ประโยค ภาษาไทย",'
ADD = ('"caption":"แคปชันโพสต์ TikTok 1 บรรทัด ไม่เกิน 80 ตัวอักษร บอกว่าทำอะไรแล้วได้ผลแบบไหน ชวนดูจนจบ ห้ามมี emoji · ภาษาไทย (พากย์ English = เขียนอังกฤษ)",'
       '"hashtags":"แฮชแท็ก 5-7 อัน คั่นด้วยเว้นวรรค ตรงกับงานนี้ ไทยปนอังกฤษ (พากย์ English = อังกฤษล้วน) ห้ามชื่อแบรนด์หรือร้าน",')
for k, v in L['lenOut'].items():
    assert v.count(ANCH) == 1, k
    L['lenOut'][k] = v.replace(ANCH, ANCH + ADD)
sp = ops['mnQueue']['spawn']['fields']
sp['caption'] = '{item.fields.caption}'; sp['hashtags'] = '{item.fields.hashtags}'
T = c['collections']['tasks']; T['fields'] += ['caption', 'hashtags']; T['slots'].append('cover')

# ── op ปก ──
SOLO, ATT = 'คนเดียวเต็มตัว', 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'
cover = {
 'id': 'mnCover', 'type': 'image', 'over': 'tasks', 'out': 'cover',
 'model': '🍌 Nano Banana Pro', 'aspectRatio': '9:16',
 'refs': {'op': 'lookupRefs', 'from': 'tasks', 'by': '{item.id}', 'slot': 'board', 'also': [
  {'from': 'products', 'by': '{item.refs.prod}', 'slot': 'image'},
  {'from': 'tasks', 'by': '{item.id}', 'slot': 'face', 'when': {'op': 'and', 'list': [{'op': 'eq', 'a': '{item.people}', 'b': SOLO}, {'op': 'not', 'a': {'op': 'eq', 'a': '{item.peopleSrc}', 'b': ATT}}]}},
  {'from': 'characters', 'by': '{values.charId}', 'slot': 'face', 'when': {'op': 'and', 'list': [{'op': 'eq', 'a': '{item.people}', 'b': SOLO}, {'op': 'eq', 'a': '{item.peopleSrc}', 'b': ATT}]}}]},
 'prompt': {'op': 'concat', 'parts': [
  'Design a scroll-stopping vertical 9:16 COVER (thumbnail) for a Thai how-to TikTok clip about "{item.productName}". ',
  'Attached image 1 = this clip\'s storyboard sheet (a grid of panels): use it only as reference — make ONE single full-bleed photo, never a grid, panels, borders or number marks. ',
  'Show the most satisfying moment: the finished result, big and clear, in the same place, same light, same person and same product as the sheet. ',
  {'op': 'block', 'sep': '', 'parts': [{'when': {'op': 'refsFilled', 'key': 'prod', 'from': 'products', 'slot': 'image'},
   'value': 'The attached product photo is the real product — keep its exact colour, shape, label and logo. '}]},
  {'op': 'block', 'sep': '', 'parts': [{'when': {'op': 'eq', 'a': '{item.people}', 'b': SOLO},
   'value': 'The attached face photo is the person — same face and hair; natural, not posing like a model. '}]},
  'Look: ',
  {'op': 'lookup', 'table': 'styleVideoEN', 'key': '{values.svStyle}', 'fallback': 'realistic documentary look of a real lived-in home'},
  '. Headline: ',
  {'op': 'block', 'sep': '', 'parts': [
   {'when': 'values.svLang=English', 'value': 'big bold short English title (2-5 words) about this job,'},
   {'when': 'values.svLang!=English', 'value': 'big bold short Thai title (2-6 words) about this job, exact correct Thai spelling,'}]},
  ' in the upper third, white letters with a thick dark outline and soft shadow, easy to read on a phone; keep faces and the product uncovered. ',
  'Bright, clean, high-contrast TikTok cover look, at most one small arrow or sparkle accent. No other text, no logos, no watermark, no emoji.']},
 'aux': True,
 'logRun': '[{item.productName} คลิป {item.clipIndex}] กำลังทำปก TikTok',
 'logDone': '[{item.productName} คลิป {item.clipIndex}] ปก TikTok เสร็จแล้ว',
 'timeoutMs': 180000,
}
c['ops'].append(cover)

# ── หน้าผลิต (มุมมองการ์ด) กล่องวิดีโอเสร็จ ──
done = c['phases'][0]['form'][3]['card'][0]['card'][5]['card'][0]['card'][0]['card'][2]['card'][7]
assert done['card'][0].get('el') == 'download-button' and done['card'][0].get('to') == '{item.slots.video}'
NOC = {'op': 'eq', 'a': '{item.slots.cover}', 'b': ''}
HAS = {'op': 'not', 'a': NOC}
BTN = 'w-full justify-center !h-11 !rounded-xl !text-[14px] @[640px]:!text-[13px] font-bold border border-[var(--ev-border)] !bg-[var(--ev-surface)] !min-h-[48px] @[420px]:!min-h-0'
tik = {
 'el': 'box', 'className': 'flex flex-col gap-2 rounded-xl border border-[var(--ev-border)] p-2.5',
 'card': [
  {'el': 'text', 'value': 'โพสต์ TikTok', 'icon': 'smartphone', 'className': '!text-[13px] @[640px]:!text-[12px] font-bold opacity-60'},
  {'el': 'media-slot', 'src': '{item.slots.cover}', 'aspect': '9:16', 'style': {'borderRadius': '12px'}, 'className': 'ring-1 ring-[var(--ev-border)]', 'when': HAS},
  {'el': 'gen-button', 'op': 'mnCover', 'label': 'ทำปก TikTok', 'icon': 'auto_awesome', 'variant': 'ghost', 'className': BTN, 'when': NOC},
  {'el': 'text', 'value': 'ภาพปก 9:16 จากบอร์ดคลิปนี้ · ใช้เครดิตภาพ 1 ใบ', 'className': '!text-[12px] @[640px]:!text-[11px] opacity-50', 'when': NOC},
  {'el': 'box', 'className': 'grid grid-cols-2 gap-2', 'when': HAS, 'card': [
   {'el': 'download-button', 'to': '{item.slots.cover}', 'label': 'โหลดปก', 'icon': 'download', 'variant': 'ghost', 'className': BTN},
   {'el': 'retry-button', 'chain': ['mnCover'], 'label': 'ทำปกใหม่', 'icon': 'refresh', 'variant': 'ghost', 'className': BTN}]},
  {'el': 'box', 'className': 'flex flex-col gap-1.5', 'when': 'item.caption!=', 'card': [
   {'el': 'text', 'value': '{item.caption}', 'className': '!text-[14px] @[640px]:!text-[13px] leading-snug !text-[var(--ev-text)]'},
   {'el': 'text', 'value': '{item.hashtags}', 'className': '!text-[13px] @[640px]:!text-[12px] leading-snug !text-[var(--ev-accent)]', 'when': 'item.hashtags!='},
   {'el': 'copy-button', 'value': '{item.caption}\n\n{item.hashtags}', 'label': 'คัดลอกแคปชัน + แฮชแท็ก', 'icon': 'content_copy', 'variant': 'ghost', 'className': BTN}]},
 ]}
done['card'].insert(1, tik)
print('✅ v140: บท caption/hashtags 6 ความยาว · op mnCover (aux) · กล่องโพสต์ TikTok ในการ์ดวิดีโอเสร็จ')
open(P, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
