#!/usr/bin/env python3
# showhow v68 — ประตู "คลิปเสร็จ" ต้องตรวจ **ทุกช่วงที่ต้องมี** ไม่ใช่เดาจากช่วงแรก
#
# ของเดิม: `count(tasks, slot:'video') == count(tasks)` = "ช่วงแรกมีวิดีโอแล้ว = เสร็จ"
#   ถูกต้อง **เพราะบังเอิญ** เราผลิตวิดีโอ 6→1 (ช่วงแรกเสร็จท้ายสุด) — เป็นความรู้ที่ซ่อนอยู่ในลำดับ ไม่ได้เขียนไว้ในเงื่อนไข
#   🔴 พอจะทำ end-frame chaining (ช่วง K ต่อจากเฟรมท้ายช่วง K-1) ลำดับต้องเป็น 1→6 ⇒ ช่วงแรกเสร็จก่อน
#      ⇒ ประตูเดิมจะบอกว่า "เสร็จแล้ว" ทั้งที่เหลืออีกหลายช่วง (แกลเลอรี · ปุ่มดาวน์โหลด · zip เปิดหมด)
#
# v68: เขียนประตูให้ตรงความหมาย — ทุกช่วงที่ความยาวนี้ต้องมี ต้องมีวิดีโอครบ
#   and( video ครบ, svSec<=10 or video2 ครบ, svSec<=20 or video3 ครบ, … )
#   ⇒ ถูกต้องกับลำดับผลิตทุกแบบ · ไม่ต้องพึ่ง "ความบังเอิญของลำดับ" อีก
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))

ALLDONE = {'op': 'and', 'list': [
    {'op': 'eq', 'a': {'op': 'count', 'from': 'tasks', 'slot': 'video'}, 'b': {'op': 'count', 'from': 'tasks'}},
] + [
    {'op': 'or', 'list': [f'values.svSec<={k*10}',
                          {'op': 'eq', 'a': {'op': 'count', 'from': 'tasks', 'slot': f'video{k+1}'},
                           'b': {'op': 'count', 'from': 'tasks'}}]}
    for k in range(1, 6)
]}
OLD = {'op': 'eq', 'a': {'op': 'count', 'from': 'tasks', 'slot': 'video'}, 'b': {'op': 'count', 'from': 'tasks'}}
OLD_S = json.dumps(OLD, ensure_ascii=False, sort_keys=True)

n = 0
def walk(x):
    global n
    if isinstance(x, dict):
        if json.dumps(x, ensure_ascii=False, sort_keys=True) == OLD_S:
            n += 1
            return json.loads(json.dumps(ALLDONE, ensure_ascii=False))
        return {k: walk(v) for k, v in x.items()}
    if isinstance(x, list):
        return [walk(v) for v in x]
    return x

c['phases'] = walk(c['phases'])
assert n == 13, f'คาด 13 ประตู เจอ {n}'
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'v68 ok · เปลี่ยนประตู "คลิปเสร็จ" {n} จุด ให้ตรวจครบทุกช่วง')
