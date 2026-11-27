// model-standard-proof.ts — พิสูจน์ว่า "เพิ่มแค่ตัวเลือก" (model-standard.py) ไม่เปลี่ยนคำขอที่ค่าเริ่มเลยสักไบต์
// ใช้ (รันจากราก engine · โหลด engine จาก cwd): npx tsx <config>/scripts/model-standard-proof.ts <ก่อน.json> <หลัง.json> <app>
// ทำ: ทุก op ของไฟล์ "ก่อน" × ชุด item/ค่าตัวอย่าง (ค่าเริ่มของแอป) → resolve คำขอแบบ engine-exec (prompt/sys/model/res/วินาที/refs/startFrame/when)
//     แล้วเทียบกับไฟล์ "หลัง" ต้องตรงทุกตัวอักษร · จากนั้นลองตัวเลือกใหม่ (Omni 1.2 + 360p + 10 วิ · ภาพ 2 Lite) ดูว่าคำขอเปลี่ยนจริง + prompt ≤ 3900
import * as fs from 'fs';
import * as path from 'path';
const FW = path.resolve('src/framework');
if (!fs.existsSync(FW + '/engine.ts')) { console.log('🔴 ต้องรันจากราก engine'); process.exit(1); }
const { buildStore, resolveValue, resolveStr, registerCombinators } = require(FW + '/engine');
const { selectHooks } = require(FW + '/hooks');
const [A, B, app] = process.argv.slice(2);
const ca = JSON.parse(fs.readFileSync(A, 'utf8')); const cb = JSON.parse(fs.readFileSync(B, 'utf8'));
registerCombinators(selectHooks(ca));
const MEDIA = (n: string) => ({ kind: 'image', mimeType: 'image/png', base64: 'B64_' + n, mediaId: 'M_' + n });
const VIDEO = { kind: 'video', mimeType: 'video/mp4', base64: 'V', mediaId: 'MV' };
const SLOTS: any = { board: MEDIA('board'), board2: MEDIA('board2'), master: MEDIA('master'), image: MEDIA('image'), face: MEDIA('face'), video: VIDEO, video2: VIDEO };
const ITEM_VARIANTS: Record<string, any[]> = {
  showhow: [{}, { arc: 'ไทม์แลปส์กล้องนิ่ง' }, { arc: 'ทัวร์จุดเด่น', endMode: 'custom' }, { arc: 'ก่อน → ลงมือ → หลัง' }],
  hardsell: [{ eSec: '' }, { eSec: '10' }, { eSec: '20' }, { eSec: '16' }],
  petdance: [{}, { clipStyle: 'selfie' }],
  podcast: [{}, { ep: '3', secAt: '60' }], parody: [{}], minimal: [{}, { pVidModel: 'Omni 1.2 Flash' }], fashion: [{}, { secAt: '20' }],
};
const VALUE_VARIANTS = [{}, { svSec: '10' }, { svSec: '20' }, { svTextOn: 'ข้อความสั้น' }];
const KEYS = ['prompt', 'systemInstruction', 'model', 'aspectRatio', 'durationSeconds', 'resolution', 'refs', 'startFrame', 'endFrame', 'when', 'where'];

function req(cfg: any, op: any, iv: any, vv: any) {
  const st: any = buildStore(cfg); Object.assign(st.values, vv);
  const prod = { id: 'p1', fields: { name: 'ครีมกันแดด', enabled: 'true', ...iv }, data: {}, slots: { ...SLOTS }, refs: {}, status: 'idle' };
  st.collections.products = [prod];
  st.collections.characters = [{ id: 'ch1', fields: {}, slots: { face: MEDIA('ch1') } }, { id: 'pet1', fields: {}, slots: { face: MEDIA('pet1') } }, { id: 'studio', fields: {}, slots: { room: MEDIA('room') } }];
  const task = { id: 't1', fields: { clipIndex: '1', productName: 'ครีมกันแดด', ...iv }, data: {}, slots: { ...SLOTS }, refs: { prod: ['p1'] }, status: 'idle' };
  st.collections.tasks = [task];
  const item: any = op.over === 'tasks' ? task : prod;
  const ctx: any = { store: st, item, lookups: cfg.lookups, brain: cfg.brain, parent: prod };
  const out: any = {};
  for (const k of KEYS) {
    if (op[k] == null) { out[k] = undefined; continue; }
    try {
      out[k] = (k === 'refs' || k === 'startFrame' || k === 'endFrame' || k === 'when') ? JSON.stringify(resolveValue(op[k], ctx) ?? null) : resolveStr(op[k], ctx);
    } catch (e: any) { out[k] = 'ERR ' + e.message; }
  }
  // ค่าว่าง = ไม่ส่งคีย์ (execLeaf) ⇒ '' กับไม่ตั้ง เท่ากัน
  if (!out.resolution) out.resolution = undefined;
  if (out.refs === '[]' || out.refs === 'null') out.refs = undefined;   // refs ว่าง = execLeaf ไม่ส่งคีย์ (เท่ากับไม่ตั้ง)
  return out;
}

let same = 0, diff = 0;
const ivs = ITEM_VARIANTS[app] || [{}];
for (const op of ca.ops) {
  const ob = cb.ops.find((x: any) => x.id === op.id);
  if (!ob) { console.log('🔴 หลังไม่มี op', op.id); diff++; continue; }
  for (const iv of ivs) for (const vv of VALUE_VARIANTS) {
    const ra = req(ca, op, iv, vv), rb = req(cb, ob, iv, vv);
    for (const k of KEYS) {
      if (ra[k] === rb[k]) { same++; continue; }
      diff++;
      if (diff <= 12) console.log(`🔴 ${op.id} ${k} ${JSON.stringify(iv)} ${JSON.stringify(vv)}\n   ก่อน ${String(ra[k]).slice(0, 160)}\n   หลัง ${String(rb[k]).slice(0, 160)}`);
    }
  }
}
if (cb.ops.length !== ca.ops.length) { console.log('🔴 จำนวน op ไม่เท่า', ca.ops.length, cb.ops.length); diff++; }
console.log(`${app}: ค่าเริ่ม ก่อน↔หลัง ตรง ${same} · ต่าง ${diff} (op ${ca.ops.length} × item ${ivs.length} × ค่า ${VALUE_VARIANTS.length} × ${KEYS.length} คีย์)`);

// ตัวเลือกใหม่
const NEW: any = { svModel: 'Omni 1.2 Flash', svRes: '360p', svSec: '10', imageModel: '🍌 Nano Banana 2 Lite' };
if (app === 'hardsell') { delete NEW.svModel; NEW.videoModel = 'Omni 1.2 Flash'; }
const seen: Record<string, Set<string>> = {}; let maxLen = 0, maxId = '';
for (const op of cb.ops) {
  if (op.type !== 'video' && op.type !== 'image') continue;
  for (const iv of ivs) for (const vv of [NEW, { ...NEW, svRes: '720p' }, { ...NEW, svModel: 'Omni 1.1 Flash', videoModel: 'Omni 1.1 Flash' }, { ...NEW, svTextOn: 'ข้อความสั้น' }]) {
    const r = req(cb, op, iv, vv);
    const key = op.type + ' ' + JSON.stringify(Object.fromEntries(Object.entries(vv).filter(([k]) => k !== 'svSec')));
    (seen[key] = seen[key] || new Set()).add(`${r.model} · res ${r.resolution ?? '-'} · startFrame ${r.startFrame && r.startFrame !== 'null' ? 'มี' : 'ไม่มี'}`);
    if (r.prompt.length > maxLen) { maxLen = r.prompt.length; maxId = op.id + ' ' + JSON.stringify(iv); }
  }
}
for (const [k, v] of Object.entries(seen)) console.log('  ', k, '→', [...v].join(' | '));
console.log(`   prompt ภาพ/วิดีโอ ยาวสุด (ตัวอย่างนี้) ${maxLen} ${maxId} ${maxLen <= 3900 ? '🟢' : '🔴 เกิน 3900'}`);
process.exit(diff ? 1 : 0);
