#!/usr/bin/env python3
# hardsell-dev v32: แคปชัน + แฮชแท็ก + ปก TikTok (เจ้าของสั่ง 26 พ.ย. ข้อ 13 · ลอกท่า minimal-v59/v61 + showhow-v140)
#   - mnPlan (systemInstruction ต่อจาก lenOut): ทุก object เพิ่มคีย์ caption + hashtags (ไทย · ไม่มี emoji · ไม่แต่งราคา/โปร)
#   - mnQueue: caption/hashtags ลงงานย่อย · tasks.fields += caption, hashtags · tasks.slots += cover
#   - op ใหม่ mnCover (image 9:16 · over tasks · out cover · aux:true = ปุ่มกดเอง ไม่อยู่ใน gens/stages
#     ★ ไม่ใส่ aux = itemRunCounts นับเป็นงานค้าง → นับคลิปเสร็จไม่ขึ้น (บทเรียน minimal v61))
#     อ้างอิง: ภาพเฟรมแรกของคลิป + รูปสินค้า + รูปหน้าตัวละคร (เมื่อเลือกใช้รูป) · มีหัวเรื่องบนปกเสมอ ⇒ model = 🍌 Nano Banana Pro
#   - หน้าผลิต มุมมองการ์ด คอลัมน์กลาง ต่อจากเรื่องย่อ: กล่องแคปชัน (ปุ่มคัดลอก) + กล่องปก (สร้าง/สร้างใหม่/โหลด)
# ใช้: python3 scripts/hardsell-v32-caption-cover.py [hardsell-dev.json]   (รันบน v31 · รันซ้ำได้)
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'hardsell-dev.json'
d = json.load(open(F, encoding='utf-8'))
L = d['lookups']
ops = {o['id']: o for o in d['ops']}
PRO = '🍌 Nano Banana Pro'
FACE = 'ใช้รูปใบหน้าที่แนบ — ล็อกหน้าเป็นคนเดิมทุกช็อต'

# ── บท: caption + hashtags ──
CAP = ('\n\nเพิ่มอีก 2 คีย์ในทุก object: "caption":"แคปชันโพสต์ TikTok ภาษาไทย 1-2 ประโยค ไม่เกิน 150 ตัวอักษร '
       'ฮุคแรงแบบขายดุ พูดถึงสินค้าและประโยชน์ ไม่มี emoji ไม่แต่งราคา/โปร/ของแถมที่ผู้ใช้ไม่ได้ให้",'
       '"hashtags":"แฮชแท็ก 5-7 อัน คั่นด้วยเว้นวรรค ไทยปนอังกฤษ ตรงกับสินค้านี้ ไม่มีชื่อร้าน"')
sysP = ops['mnPlan']['systemInstruction']['parts']
if not any(isinstance(x, str) and 'เพิ่มอีก 2 คีย์ในทุก object' in x for x in sysP):
    i = next(i for i, x in enumerate(sysP) if isinstance(x, dict) and x.get('table') == 'lenOut')
    sysP.insert(i + 1, CAP)
T = d['collections']['tasks']
for f in ('caption', 'hashtags'):
    if f not in T['fields']: T['fields'].append(f)
if 'cover' not in T['slots']: T['slots'].append('cover')
sp = ops['mnQueue']['spawn']['fields']
sp.setdefault('caption', '{item.fields.caption}'); sp.setdefault('hashtags', '{item.fields.hashtags}')

# ── op ปก ──
HEADLINE = {'op': 'cond', 'when': {'op': 'not', 'a': {'op': 'eq', 'a': '{item.ov1}', 'b': ''}}, 'then': '{item.ov1}', 'else': '{item.productName}'}
COVER = {
    'id': 'mnCover', 'type': 'image', 'over': 'tasks', 'out': 'cover', 'model': PRO, 'aspectRatio': '9:16',
    'where': 'slots.board!=',
    'refs': {'op': 'lookupRefs', 'from': 'tasks', 'by': '{item.id}', 'slot': 'board', 'also': [
        {'from': 'products', 'by': '{item.refs.prod}', 'slot': 'image'},
        {'from': 'characters', 'by': '{values.charId}', 'slot': 'face', 'when': {'op': 'and',
            'a': {'op': 'eq', 'a': {'op': 'lookup', 'table': 'tplChar', 'key': '{values.templateId}'}, 'b': 'yes'},
            'b': {'op': 'eq', 'a': '{values.svCharSrc}', 'b': FACE}}}]},
    'prompt': {'op': 'concat', 'parts': [
        'Design one scroll-stopping vertical 9:16 COVER image (thumbnail) for a Thai hard-sell TikTok product clip. '
        'Reference image 1 is this clip\'s first frame: keep its exact look (real photo or 3D render), place, light, palette and presenter (if any). '
        'The next image is the real product photo (plus the presenter\'s face if attached).\n'
        'PRODUCT LOCK: the product is the hero, large and sharp, exactly as photographed — same colour, shape, proportions, material, label, logo and lettering; never redraw or restyle it.\n'
        'HEADLINE text in Thai, spelled exactly: "', HEADLINE, '" — one or two short lines in the upper third, big bold letters with a thick dark outline and soft shadow, '
        'easy to read on a phone, never covering faces or the product.\n'
        'RULES: one single full-bleed image, no grid, no split screen, no collage; text spelled exactly, never mirrored; no other text; '
        'never invent prices, discounts, free shipping or stock claims; no shopping UI, no emoji, no logo or watermark of our own.']},
    'aux': True,
    'logRun': '[{item.productName} คลิป {item.clipIndex}] กำลังสร้างปก TikTok',
    'logDone': '[{item.productName} คลิป {item.clipIndex}] ปก TikTok เสร็จแล้ว',
    'timeoutMs': 180000,
}
if 'mnCover' not in ops: d['ops'].append(COVER)   # มีแล้ว = ไม่ทับ (v33/v34 แก้ต่อจากนี้ — ทับ = ถอยงานนั้น)
L['opNames']['mnCover'] = 'กำลังสร้างปก'; L['opIcons']['mnCover'] = 'image'

# ── หน้าผลิต (มุมมองการ์ด) คอลัมน์กลาง ต่อจากเรื่องย่อ ──
mid = d['phases'][0]['form'][3]['card'][0]['card'][7]['card'][0]['card'][0]['card'][1]
syn_i = next(i for i, x in enumerate(mid['card']) if '{item.synopsis}' in json.dumps(x, ensure_ascii=False))
BTN = 'w-full justify-center !h-12 !rounded-xl !text-[15px] @[640px]:!text-[14px] font-bold !min-h-[48px] @[420px]:!min-h-0'
BTN_SOLID = BTN + ' !bg-gradient-to-b !from-[#3f8ef0] !to-[#2571dd] !text-white'
BTN_GHOST = BTN + ' border border-[var(--ev-border)] !bg-[var(--ev-surface)]'
HEAD = lambda icon, txt: {'el': 'row', 'className': 'items-center !gap-1.5 px-0.5', 'style': {'flexWrap': 'nowrap'}, 'card': [
    {'el': 'icon', 'icon': icon, 'textSize': 'text-[16px]', 'className': '!text-[var(--ev-accent)] leading-none flex items-center justify-center opacity-80 shrink-0'},
    {'el': 'text', 'value': txt, 'className': '!text-[13px] @[640px]:!text-[12.5px] !text-[var(--ev-text)] opacity-65 uppercase tracking-[0.14em] font-black'}]}
BOXCLS = 'flex flex-col gap-2 rounded-2xl border border-[var(--ev-border)] bg-[var(--ev-bg)]/60 p-3'
cap_box = {'el': 'box', 'className': BOXCLS, 'when': 'item.caption!=', 'card': [
    HEAD('chat', 'แคปชัน TikTok พร้อมโพสต์'),
    {'el': 'text', 'value': '{item.caption}', 'className': '!text-[15px] @[640px]:!text-[14px] leading-relaxed whitespace-pre-line'},
    {'el': 'text', 'value': '{item.hashtags}', 'className': '!text-[14px] @[640px]:!text-[13px] leading-relaxed font-bold !text-[var(--ev-accent)] break-words', 'when': 'item.hashtags!='},
    {'el': 'copy-button', 'value': '{item.caption}\n\n{item.hashtags}', 'label': 'คัดลอกแคปชัน + แฮชแท็ก', 'icon': 'content_copy', 'variant': 'ghost', 'className': BTN_GHOST}]}
NOT_RUN = {'op': 'not', 'a': {'op': 'eq', 'a': '{item.status}', 'b': 'running'}}
NO_COVER = {'op': 'eq', 'a': '{item.slots.cover}', 'b': ''}
HAS_COVER = {'op': 'not', 'a': NO_COVER}
cov_box = {'el': 'box', 'className': BOXCLS, 'when': {'op': 'not', 'a': {'op': 'eq', 'a': '{item.slots.board}', 'b': ''}}, 'card': [
    HEAD('photo', 'ปก TikTok'),
    {'el': 'box', 'className': 'w-[140px]', 'when': HAS_COVER, 'card': [
        {'el': 'media-slot', 'src': '{item.slots.cover}', 'aspect': '9:16', 'style': {'borderRadius': '14px'}, 'className': 'ring-1 ring-[var(--ev-border)]'}]},
    {'el': 'text', 'value': 'ภาพปก 9:16 มีหัวข้อตัวใหญ่ จากภาพเฟรมแรกและรูปสินค้าของคลิปนี้ · ใช้เครดิตภาพ 1 ใบ (Nano Banana Pro)', 'className': '!text-[13px] @[640px]:!text-[12px] opacity-55 leading-snug', 'when': NO_COVER},
    {'el': 'gen-button', 'op': 'mnCover', 'label': 'สร้างปก', 'icon': 'auto_awesome', 'variant': 'solid', 'className': BTN_SOLID,
     'when': {'op': 'and', 'list': [NO_COVER, NOT_RUN]}},
    {'el': 'box', 'className': 'grid grid-cols-1 @[420px]:grid-cols-2 gap-2', 'when': HAS_COVER, 'card': [
        {'el': 'download-button', 'to': '{item.slots.cover}', 'label': 'โหลดปก', 'icon': 'download', 'variant': 'solid', 'className': BTN_SOLID},
        {'el': 'retry-button', 'op': 'mnCover', 'label': 'สร้างปกใหม่', 'icon': 'refresh', 'variant': 'ghost', 'className': BTN_GHOST, 'when': NOT_RUN}]}]}
if not any('{item.slots.cover}' in json.dumps(x, ensure_ascii=False) for x in mid['card']):
    mid['card'][syn_i + 1:syn_i + 1] = [cap_box, cov_box]

# ── ตรวจปิดท้าย ──
assert 'mnCover' not in d['auto']['productLoop']['gens'] and all(s.get('op') != 'mnCover' for s in d['stages'])
assert {o['id']: o for o in d['ops']}['mnCover']['aux'] is True
print('v32: caption/hashtags + mnCover (aux · Pro) + กล่องแคปชัน/ปก')
open(F, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2))
