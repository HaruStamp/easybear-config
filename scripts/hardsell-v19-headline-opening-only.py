#!/usr/bin/env python3
# hardsell-v19-headline-opening-only.py — โหมด "มีข้อความ": หัวข้อในภาพเฟรมแรกโชว์แค่ 1-2 วิแรก แล้วหาย (พี่หมีเคาะ 2026-09-30)
#   เดิม (v16): สั่ง Veo "keep ONLY the Thai headline … for the whole clip" ⇒ Veo วาดตัวหนังสือใหม่ทุกเฟรม เพี้ยน 5/5 คลิป
#   ใหม่: mnVideo = หัวข้อจากเฟรมแรกอยู่ได้ 1-2 วิแรกแล้วหาย หลังจากนั้นไม่มีตัวหนังสือ
#         mnVideo2 = ช่วง 2 เริ่มจากเฟรมท้ายช่วง 1 (ไม่มีหัวข้อแล้ว) ⇒ ใช้กฎเดียวกับ "ไม่มีข้อความ"
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OLD = ("\n\nOn-screen text: keep ONLY the Thai headline already in the first frame, unchanged and in the same place for the whole clip, "
       "plus text printed on the packaging; never add, change or animate any other text.")
NEW_V1 = ("\n\nOn-screen text: the Thai headline in the first frame may stay for the first 1-2 seconds, then it is gone; "
          "after that no captions, subtitles, titles or any new text — only text printed on the packaging.")
OFF = "\n\nOn-screen text: none — no captions, subtitles, titles, typography or watermarks; only text printed on the packaging."


def main():
    src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'hardsell-dev.json'))
    cfg = json.load(open(src, encoding='utf-8'))
    if 'may stay for the first 1-2 seconds' in json.dumps(cfg, ensure_ascii=False):
        print('⏭  แพตช์นี้ลงไปแล้ว — ไม่ทำอะไร'); return
    hits = {'mnVideo': 0, 'mnVideo2': 0}

    def walk(x, op):
        if isinstance(x, dict):
            if x.get('when') == 'values.svTextOn!=ไม่มีข้อความ' and x.get('value') == OLD:
                x['value'] = NEW_V1 if op == 'mnVideo' else OFF; hits[op] += 1
            for v in x.values(): walk(v, op)
        elif isinstance(x, list):
            for v in x: walk(v, op)

    for o in cfg['ops']:
        if o['id'] in hits: walk(o['prompt'], o['id'])
    assert hits == {'mnVideo': 1, 'mnVideo2': 1}, hits
    json.dump(cfg, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('✅ hardsell v19 ลงแล้ว — หัวข้อโชว์แค่ 1-2 วิแรกของช่วง 1 · ช่วง 2 ไม่มีตัวหนังสือ')


main()
