# minimal-dev v60: คืนบอร์ดเป็น ref ใบสุดท้ายของ mnVideo* (v59 ย้ายขึ้นใบแรก — ซ้ำรอยบั๊ก v28: แผ่นบอร์ดหลุดเต็มจอ 2 วิในคลิปลูกค้า 21 ก.ย.)
#   คงคำสั่งใหม่ของ v59 "ตามช่องบอร์ดทีละฉาก" แต่อ้างด้วย LAST (ตามที่ v28 พิสูจน์) · รูปสถานที่กลับเป็น "just before the storyboard"
import json, sys
F = sys.argv[1] if len(sys.argv) > 1 else 'minimal-dev.json'
d = json.load(open(F))
NEW = "\n\nThe LAST reference image is this clip storyboard sheet, a silent guide: follow each scene's panel (pose, framing, product); the sheet must NEVER appear on screen. Every frame is live-action photography."
OLD = "\n\nReference image 1 is this clip's storyboard sheet, a silent guide: follow each scene's panel (pose, framing, angle, product). The sheet must NEVER appear on screen. Every frame is live-action photography."
n = {'refs': 0, 'line': 0, 'loc': 0}
def rep(x):
    if isinstance(x, str):
        y = x.replace(OLD, NEW)
        if y != x: n['line'] += 1
        z = y.replace('(the last image)', '(just before the storyboard)')
        if z != y: n['loc'] += 1
        return z
    if isinstance(x, list): return [rep(v) for v in x]
    if isinstance(x, dict): return {k: rep(v) for k, v in x.items()}
    return x
for o in d['ops']:
    if o.get('id') not in ('mnVideo', 'mnVideo2', 'mnVideo3'): continue
    r = o['refs']
    if str(r.get('slot', '')).startswith('board'):
        board = {k: r[k] for k in ('from', 'by', 'slot')}
        first = r['also'].pop(0)
        r['from'], r['by'], r['slot'] = first['from'], first['by'], first['slot']
        r['also'].append(board); n['refs'] += 1
    o['prompt'] = rep(o['prompt'])
print(n)
assert n['refs'] == 3, n
open(F, 'w').write(json.dumps(d, ensure_ascii=False, indent=2))
