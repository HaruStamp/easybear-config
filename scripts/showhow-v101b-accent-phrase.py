#!/usr/bin/env python3
"""showhow-v101b — วลีสำเนียงใน prompt วิดีโอให้เป็นประโยคอังกฤษที่ถูก + สั้นลง
เดิม "continuous Thai in a natural Isan accent narration" (ไวยากรณ์เพี้ยน) → "continuous Isan-accented Thai narration"
ใช้: python3 scripts/showhow-v101b-accent-phrase.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
new = {'มาตรฐาน': 'Thai', 'กรุงเทพ': 'casual youthful Bangkok Thai', 'อีสาน': 'Isan-accented Thai',
       'เหนือ': 'Northern-accented Thai', 'ใต้': 'Southern-accented Thai'}
old = c['lookups']['accentVideoEN']
assert set(old) == set(new) and all(len(new[k]) <= len(old[k]) for k in new)
c['lookups']['accentVideoEN'] = new
print('accentVideoEN:', new)
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
