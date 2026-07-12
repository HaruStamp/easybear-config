// gen-hardsell-config.ts — สร้าง hardsell.json จาก pack จริง (option lists sync กับ hooks-hardsell เสมอ)
// รัน: cd easybear-starter && npx tsx ../easybear-config/scripts/gen-hardsell-config.ts
// theme + model options ยืมจาก film.json (มาตรฐานเดียวกัน) · เขียนทับ easybear-config/hardsell.json (indent=2 ไม่มี trailing newline)
// โครง UI = ต้นฉบับ easybear-hardsell design lock v2 (mockups/mockup.html + src/components) — หน้าเดียว 2 คอลัมน์
import * as fs from 'fs';
import * as path from 'path';
import { HS_SCENE_TEMPLATES, HS_TONES, HS_TEXT_STYLES, HS_BLOCKED_DEFAULT } from '../../easybear-starter/src/framework/hooks-hardsell';

const CFG = path.resolve(__dirname, '..');
const film = JSON.parse(fs.readFileSync(path.join(CFG, 'film.json'), 'utf8'));

// ---- ยืมของกลางจาก film (มาตรฐาน Engine เดียวกัน) ----
const findEl = (o: any, pred: (x: any) => boolean): any => {
  if (o && typeof o === 'object') {
    if (!Array.isArray(o) && pred(o)) return o;
    for (const v of Array.isArray(o) ? o : Object.values(o)) { const r = findEl(v, pred); if (r) return r; }
  }
  return null;
};
const imageModelEl = findEl(film, (x) => x.el === 'dropdown' && x.field === 'imageModel');
const videoModelEl = findEl(film, (x) => x.el === 'dropdown' && x.field === 'videoModel');
const IMAGE_MODELS = imageModelEl?.options || [];
const VIDEO_MODELS = videoModelEl?.options || [];
if (!IMAGE_MODELS.length || !VIDEO_MODELS.length) throw new Error('ดึง model options จาก film.json ไม่ได้');
// default ตาม HsSettings เดิม: Nano Banana Pro + Veo 3.1 - Fast
const DEF_IMG = (IMAGE_MODELS.find((o: any) => o.value === '🍌 Nano Banana Pro') || IMAGE_MODELS[0]).value;
const DEF_VID = (VIDEO_MODELS.find((o: any) => o.value === 'Veo 3.1 - Fast') || VIDEO_MODELS[0]).value;

// ---- runBanner popup ความคืบหน้า: derive จาก film (มาตรฐานเดียวกัน ตามธีมอยู่แล้ว) — เปลี่ยนแค่ title ---
if (!film.components?.runBanner) throw new Error('film.json ไม่มี components.runBanner');
const RUN_BANNER = JSON.parse(JSON.stringify(film.components.runBanner).split('Gen ทั้งหมด').join('ผลิตคลิป'));
// patch กล่อง "เสร็จ": อย่าโชว์เมื่อ stage สุดท้ายไม่มีงาน (hsVideo2 โหมด 8 วิ → total=0) — เติมเงื่อนไข __runTotal != 0
{
  const doneWhen = RUN_BANNER?.[1]?.when?.list?.[1]?.list?.[1]?.list;
  if (!Array.isArray(doneWhen)) throw new Error('โครง runBanner จาก film เปลี่ยน — patch done-box ไม่เจอ');
  doneWhen.push({ op: 'not', a: { op: 'eq', a: '{values.__runTotal}', b: '0' } });
}
// ตาราง lookup ที่ banner อ้าง (opBanner = stage ไหนโชว์ popup · opNames/opPhase = ป้ายบรรทัดล่าง)
const LOOKUPS = {
  opBanner: { hsContent: '1', hsImage: '1', hsVideo1: '1', hsVideo2: '1' },
  opNames: { hsQueue: 'จัดคิวผลิต', hsContent: 'เขียนบทขาย', hsPrompts: 'เตรียมพรอมพ์', hsImage: 'สร้างภาพเฟรมแรก', hsVideo1: 'สร้างวีดีโอ ช่วง 1', hsVideo2: 'ต่อฉาก ช่วง 2' },
  opPhase: { hsContent: '1/3', hsImage: '2/3', hsVideo1: '3/3', hsVideo2: '3/3' },
};

// ---- option lists จาก pack (sync อัตโนมัติ) ----
const TEMPLATE_OPTS = HS_SCENE_TEMPLATES.map(t => ({ value: t.id, label: t.name, desc: t.desc, icon: t.icon }));
const TONE_OPTS = HS_TONES.map(t => ({ value: t.id, label: t.name, desc: t.desc, icon: t.icon }));
const STYLE_OPTS = HS_TEXT_STYLES.map(s => ({ value: s.id, label: s.name, desc: s.desc, ...(s.colors.length ? { colors: s.colors } : { icon: 'shuffle' }) }));
const AGE_OPTS = ['วัยรุ่น 18-25', 'วัยทำงาน 25-35', 'กลางคน 35-50', 'สูงวัย 50+'].map(a => ({ value: a, label: a }));

// ---- UI helpers ----
const lbl = (v: string) => ({ el: 'text', value: v, className: 'text-[11px] font-bold uppercase tracking-wide opacity-40' });

// ---- เงื่อนไขสถานะ (ปุ่มควบคุมเดียว + จอขวา — ตรรกะตาม MainScreen.tsx ต้นฉบับ) ----
// กำลังรัน = engine กำลังเดิน op (running/cooldown/retrying)
const ST_RUNNING = { op: 'or', list: [
  { op: 'eq', a: '{values.__runState}', b: 'running' },
  { op: 'eq', a: '{values.__runState}', b: 'cooldown' },
  { op: 'eq', a: '{values.__runState}', b: 'retrying' },
] };
const NOT_RUNNING = { op: 'not', a: ST_RUNNING };
const COUNT_TASKS = { op: 'count', from: 'tasks' };
const HAS_TASKS = { op: 'gt', a: COUNT_TASKS, b: 0 };
const NO_TASKS = { op: 'eq', a: COUNT_TASKS, b: 0 };
const HAS_ERROR = { op: 'gt', a: { op: 'count', from: 'tasks', where: 'status=error' }, b: 0 };
const NO_ERROR = { op: 'not', a: HAS_ERROR };
// เสร็จจริงต่อคลิป = มีวิดีโอช่วงสุดท้ายของโหมดนั้น (8 วิ = video1 · 16 วิ = video2) — count+slot (Engine รองรับ)
const COUNT_DONE = { op: 'add',
  a: { op: 'count', from: 'tasks', where: 'clipLength=8', slot: 'video1' },
  b: { op: 'count', from: 'tasks', where: 'clipLength=16', slot: 'video2' } };
const ALL_DONE = { op: 'and', list: [HAS_TASKS, { op: 'eq', a: COUNT_DONE, b: COUNT_TASKS }] };
const NOT_ALL_DONE = { op: 'not', a: ALL_DONE };
const ENABLED_PRODUCTS = { op: 'count', from: 'products', where: 'enabled=true' };
const TOTAL_CLIPS = { op: 'mul', a: ENABLED_PRODUCTS, b: '{values.clipsPerProduct}' };
const READY = { op: 'and', list: [
  { op: 'gt', a: ENABLED_PRODUCTS, b: 0 },
  { op: 'all', from: 'products', where: 'enabled=true', slot: 'image' },
] };
// เส้นผลิตทั้งคิว (ข้ามตัวที่เสร็จแล้วเอง + retry ตัวพลาดเอง = พฤติกรรม autoProduce ต้นฉบับ)
const CHAIN = ['hsQueue', 'hsContent', 'hsPrompts', 'hsImage', 'hsVideo1', 'hsVideo2'];

// การ์ดสินค้า (repeat products)
const productCard = {
  el: 'repeat', coll: 'products', empty: 'ยังไม่มีสินค้า — กดเพิ่มสินค้าด้านล่าง',
  card: [{
    el: 'box', className: 'border rounded-2xl p-4 flex flex-col gap-3 border-[var(--ev-border)] bg-[var(--ev-surface)]',
    card: [
      { el: 'row', className: 'gap-4 items-start flex-col sm:flex-row', card: [
        { el: 'box', className: 'w-full sm:w-[140px] shrink-0 flex flex-col gap-2', card: [
          { el: 'media-slot', slot: 'image', aspect: '1:1' },
          { el: 'upload', label: 'รูปสินค้า', into: 'image', resize: { maxPx: 400, quality: 0.7 } },
        ]},
        { el: 'box', className: 'flex-1 min-w-0 flex flex-col gap-2', card: [
          { el: 'input', field: 'name', label: 'ชื่อสินค้า *', placeholder: 'เช่น ครีมหมีขาว' },
          { el: 'row', className: 'gap-2', card: [
            { el: 'input', field: 'price', label: 'ราคา', placeholder: '฿390', className: 'flex-1' },
            { el: 'input', field: 'promotion', label: 'โปรโมชั่น', placeholder: 'ลด 50% วันนี้เท่านั้น', className: 'flex-1' },
          ]},
          { el: 'textarea', field: 'description', label: 'จุดขาย', placeholder: 'จุดเด่นของสินค้า ใช้แล้วได้อะไร' },
          { el: 'input', field: 'cta', label: 'CTA (ว่าง = AI คิดเอง)', placeholder: 'กดสั่งเลย', maxLength: 30 },
        ]},
      ]},
      { el: 'row', className: 'items-center justify-between', card: [
        { el: 'switch', field: 'enabled', label: 'ใช้สินค้านี้' },
        { el: 'delete-button', label: 'ลบ', size: 'sm' },
      ]},
    ],
  }],
};

// การ์ดตัวละคร (repeat characters)
const characterCard = {
  el: 'repeat', coll: 'characters', empty: 'ไม่บังคับ — ไม่เพิ่ม = AI สุ่มคนรีวิวเอง',
  card: [{
    el: 'box', className: 'border rounded-2xl p-4 flex flex-col gap-3 border-[var(--ev-border)] bg-[var(--ev-surface)]',
    card: [
      { el: 'row', className: 'gap-4 items-start flex-col sm:flex-row', card: [
        { el: 'box', className: 'w-full sm:w-[120px] shrink-0 flex flex-col gap-2', card: [
          { el: 'media-slot', slot: 'image', aspect: '1:1' },
          { el: 'upload', label: 'รูปคนรีวิว', into: 'image', resize: { maxPx: 400, quality: 0.7 } },
        ]},
        { el: 'box', className: 'flex-1 min-w-0 flex flex-col gap-2', card: [
          { el: 'input', field: 'name', label: 'ชื่อ (ไว้จำเอง)' },
          { el: 'segmented', field: 'gender', label: 'เพศ (คุมคำลงท้าย ค่ะ/ครับ + เสียง)', options: [
            { value: 'female', label: 'หญิง', icon: 'female' }, { value: 'male', label: 'ชาย', icon: 'male' },
          ]},
          { el: 'dropdown', field: 'ageRange', label: 'ช่วงวัย', options: AGE_OPTS },
        ]},
      ]},
      { el: 'row', className: 'items-center justify-between', card: [
        { el: 'switch', field: 'enabled', label: 'อยู่ใน pool สุ่ม' },
        { el: 'delete-button', label: 'ลบ', size: 'sm' },
      ]},
    ],
  }],
};

// การ์ดคลิป (repeat tasks — จอขวาชั่วคราว จนกว่า M5 Run monitor จะแทน)
const taskCard = {
  el: 'repeat', coll: 'tasks', empty: 'ยังไม่มีคิวงาน — กดปุ่ม "เริ่มผลิตคลิป" ทางซ้าย',
  card: [{
    el: 'box', className: 'border rounded-2xl p-4 flex flex-col gap-3 border-[var(--ev-border)] bg-[var(--ev-surface)]',
    card: [
      { el: 'row', className: 'items-center gap-2', style: { flexWrap: 'nowrap' }, card: [
        { el: 'text', value: '{item.productName}', className: 'font-bold text-sm truncate flex-1' },
        { el: 'stat-chip', value: 'คลิป {item.clipIndex}', icon: 'movie' },
        { el: 'stat-chip', value: '{item.clipLength} วิ', icon: 'timer' },
        { el: 'stat-chip', value: '{item.angle}', icon: 'campaign' },
      ]},
      { el: 'row', className: 'gap-3 flex-col md:flex-row', card: [
        { el: 'box', className: 'flex-1 flex flex-col gap-1.5', card: [lbl('ภาพเฟรมแรก'), { el: 'media-slot', slot: 'image', aspect: '9:16' }] },
        { el: 'box', className: 'flex-1 flex flex-col gap-1.5', card: [lbl('วิดีโอช่วง 1 (0-8 วิ)'), { el: 'media-slot', slot: 'video1', aspect: '9:16' }] },
        { el: 'box', className: 'flex-1 flex flex-col gap-1.5', when: 'item.clipLength=16', card: [lbl('วิดีโอช่วง 2 (8-16 วิ)'), { el: 'media-slot', slot: 'video2', aspect: '9:16' }] },
      ]},
      { el: 'box', when: 'item.h1!=', className: 'rounded-xl p-3 bg-black/20 border border-[var(--ev-border)] flex flex-col gap-1', card: [
        { el: 'text', value: 'H1 {item.h1} · H2 {item.h2}', className: 'text-[13px] font-bold' },
        { el: 'text', value: 'พูด: {item.speech}', className: 'text-xs opacity-80 whitespace-pre-wrap' },
        { el: 'text', value: 'พูดต่อ: {item.speech2}', when: 'item.speech2!=', className: 'text-xs opacity-80 whitespace-pre-wrap' },
        { el: 'text', value: 'CTA: {item.cta}', className: 'text-xs opacity-60' },
      ]},
      { el: 'row', className: 'gap-2 flex-wrap', card: [
        { el: 'gen-button', op: 'hsContent', label: 'เขียนบทใหม่', icon: 'edit_note', size: 'sm' },
        { el: 'gen-button', op: 'hsImage', label: 'สร้างภาพ', icon: 'image', size: 'sm', disabledWhen: { op: 'eq', a: '{item.h1}', b: '' }, reason: 'เขียนบทก่อน' },
        { el: 'gen-button', op: 'hsVideo1', label: 'วิดีโอช่วง 1', icon: 'movie', size: 'sm', disabledWhen: { op: 'not', a: { op: 'refsFilled', key: 'product', from: 'products', slot: 'image' } } },
        { el: 'gen-button', op: 'hsVideo2', label: 'วิดีโอช่วง 2', icon: 'movie_filter', size: 'sm', when: 'item.clipLength=16' },
        { el: 'download-button', to: 'video1', label: 'โหลดช่วง 1', size: 'sm' },
        { el: 'download-button', to: 'video2', label: 'โหลดช่วง 2', size: 'sm', when: 'item.clipLength=16' },
        { el: 'open-editor', coll: 'tasks', label: 'ตัดต่อ/รวมคลิป', size: 'sm' },
        { el: 'save-button', scope: 'tree', label: 'เซฟคลิปนี้', icon: 'save', size: 'sm', variant: 'outline' },
      ]},
    ],
  }],
};

// ---- ซ้าย: wizard ตั้งค่า (M3 จะจัดเป็น accordion ①-④ ตาม HomeScreen) ----
const wizardForm: any[] = [
  { el: 'section', label: 'สินค้า', icon: 'inventory_2' },
  productCard,
  { el: 'add-button', coll: 'products', label: 'เพิ่มสินค้า', icon: 'add', addDefaults: { name: '', enabled: 'true' } },
  { el: 'divider' },
  { el: 'section', label: 'คนรีวิว (ไม่บังคับ)', icon: 'person' },
  characterCard,
  { el: 'add-button', coll: 'characters', label: 'เพิ่มคนรีวิว', icon: 'person_add', addDefaults: { name: '', gender: 'female', ageRange: 'วัยทำงาน 25-35', enabled: 'true' } },
  { el: 'divider' },
  { el: 'section', label: 'สไตล์คลิป', icon: 'movie_filter' },
  { el: 'grid-select', field: 'templateId', label: 'ฉาก (22 แบบ)', cols: 4, options: TEMPLATE_OPTS },
  { el: 'segmented', field: 'toneId', label: 'โทนการขาย', options: TONE_OPTS },
  { el: 'row', className: 'gap-4 flex-col md:flex-row', card: [
    { el: 'segmented', field: 'textMode', label: 'ตัวหนังสือบนภาพ', className: 'flex-1', options: [
      { value: 'overlay', label: 'มีพาดหัว H1/H2', icon: 'title' }, { value: 'none', label: 'ภาพสะอาด', icon: 'hide_image' },
    ]},
    { el: 'dropdown', field: 'textStyleId', label: 'สไตล์ตัวหนังสือ', className: 'flex-1', when: 'textMode=overlay', options: STYLE_OPTS },
  ]},
  { el: 'divider' },
  { el: 'section', label: 'การผลิต', icon: 'factory' },
  { el: 'row', className: 'gap-4 flex-col md:flex-row', card: [
    { el: 'segmented', field: 'clipLength', label: 'ความยาวคลิป', className: 'flex-1', options: [
      { value: '8', label: '8 วินาที', icon: 'timer' }, { value: '16', label: '16 วินาที (2 ช่วงต่อกัน)', icon: 'timer' },
    ]},
    { el: 'stepper', field: 'clipsPerProduct', label: 'จำนวนคลิปต่อสินค้า', min: 1, max: 100, className: 'flex-1' },
  ]},
];

// ---- ซ้ายล่าง: ปุ่มควบคุมเดียว ปัก footer (เริ่ม → หยุด → ทำต่อ/ลองใหม่ → รีเซ็ต) + hint ใต้ปุ่ม ----
const CTRL_BTN = 'w-full justify-center !h-12 !rounded-2xl !text-[14px]';
const hintTx = (when: any, value: any) => ({ el: 'text', when, value, className: 'text-center text-[11px] mt-2 opacity-70' });
const controlFooter = {
  el: 'box', className: 'p-4 pb-5 border-t border-[var(--ev-border)] shrink-0',
  card: [
    { el: 'box', when: { op: 'and', list: [NO_TASKS, { op: 'gt', a: TOTAL_CLIPS, b: 100 }] },
      className: 'mb-2.5 flex items-start gap-2 bg-amber-500/[0.08] border border-amber-500/25 rounded-xl px-3 py-2',
      card: [
        { el: 'icon', icon: 'warning', textSize: 'text-[15px]', className: 'text-amber-400 shrink-0 mt-px' },
        { el: 'text', className: 'text-[11px] leading-relaxed text-amber-300/90',
          value: { op: 'concat', parts: ['คิวนี้ ', TOTAL_CLIPS, ' คลิป (เกิน 100) — งานเยอะอาจทำให้แอปทำงานหนักหรือช้า แนะนำแบ่งทำเป็นรอบเล็กลง หรือเลือกคลิป 8 วิ เพื่อความลื่นไหล'] } },
      ]},
    // เริ่มผลิต (ยังไม่มีคิว) — ส้ม/แดง gradient เรืองแสงตาม accent
    { el: 'gen-phase', ops: CHAIN, when: NO_TASKS, label: 'เริ่มผลิตคลิป', icon: 'play_arrow',
      className: CTRL_BTN + ' font-black', style: { boxShadow: '0 0 20px color-mix(in srgb, var(--ev-accent) 35%, transparent)' },
      disabledWhen: { op: 'not', a: READY }, reason: 'เพิ่มสินค้า + ใส่รูปให้ครบก่อนเริ่มผลิต' },
    // หยุดชั่วคราว (กำลังรัน) — แดงโปร่ง
    { el: 'button', action: 'stop', when: ST_RUNNING, label: 'หยุดชั่วคราว', icon: 'pause', variant: 'ghost',
      className: CTRL_BTN + ' font-bold !text-red-300 !bg-red-500/10 !border !border-red-500/35 hover:!bg-red-500/20' },
    // ทำงานต่อ (มีคิวค้าง ไม่พัง) — ทึบ
    { el: 'gen-phase', ops: CHAIN, when: { op: 'and', list: [NOT_RUNNING, HAS_TASKS, NO_ERROR, NOT_ALL_DONE] },
      label: 'ทำงานต่อ', icon: 'play_arrow', className: CTRL_BTN + ' font-black' },
    // ลองใหม่ที่พลาด (มีตัวพัง)
    { el: 'gen-phase', ops: CHAIN, when: { op: 'and', list: [NOT_RUNNING, HAS_ERROR] },
      label: 'ลองใหม่ที่พลาด', icon: 'replay', className: CTRL_BTN + ' font-black' },
    // รีเซ็ตงาน 2 จังหวะ (มีคิว + ไม่รัน) — ล้างคิวกลับไปตั้งค่า
    { el: 'confirm-button', action: 'hook', fn: 'hsResetRun', when: { op: 'and', list: [HAS_TASKS, NOT_RUNNING] },
      label: 'รีเซ็ตงาน', icon: 'refresh', placeholder: 'ยืนยันรีเซ็ต?', variant: 'outline',
      className: 'w-full justify-center !h-11 mt-2 !rounded-2xl !text-[13.5px] font-bold' },
    // hint ใต้ปุ่ม (ตรรกะตาม MainScreen ต้นฉบับ)
    hintTx(ST_RUNNING, 'กำลังผลิตอยู่ — ดูความคืบหน้าได้ที่ฝั่งขวา'),
    hintTx({ op: 'and', list: [NOT_RUNNING, HAS_ERROR] }, 'หยุดเพราะพบปัญหา — กดลองใหม่ที่พลาดเพื่อลองคลิปที่ล้มเหลวอีกครั้ง หรือรีเซ็ตงานเพื่อล้างคิว'),
    hintTx({ op: 'and', list: [NOT_RUNNING, NO_ERROR, HAS_TASKS, NOT_ALL_DONE] },
      { op: 'concat', parts: ['หยุดพักไว้ — กดทำงานต่อเพื่อรันคิวที่เหลือ ', { op: 'sub', a: COUNT_TASKS, b: COUNT_DONE }, ' คลิป'] }),
    hintTx({ op: 'and', list: [NOT_RUNNING, ALL_DONE] },
      { op: 'concat', parts: ['เสร็จครบ ', COUNT_DONE, ' คลิป — ดาวน์โหลดได้ทางขวา หรือกดรีเซ็ตงานเพื่อตั้งค่าผลิตรอบใหม่'] }),
    hintTx({ op: 'and', list: [NO_TASKS, { op: 'eq', a: ENABLED_PRODUCTS, b: 0 }] }, 'ยังไม่ได้เลือกใช้สินค้า — เพิ่มสินค้าและติ๊ก "ใช้สินค้านี้" ก่อน'),
    hintTx({ op: 'and', list: [NO_TASKS, { op: 'gt', a: ENABLED_PRODUCTS, b: 0 }, { op: 'not', a: { op: 'all', from: 'products', where: 'enabled=true', slot: 'image' } }] },
      'มีสินค้าที่ยังไม่มีรูป — ใส่รูปก่อนเริ่มผลิต'),
    hintTx({ op: 'and', list: [NO_TASKS, READY] },
      { op: 'concat', parts: ['จากสินค้าที่เลือกไว้ ', ENABLED_PRODUCTS, ' ชิ้น · รวมคิว ', TOTAL_CLIPS, ' คลิป'] }),
  ],
};

// ---- ขวา: ว่าง (idle) — empty state เงียบๆ + ขั้นตอน ①-④ จางบรรทัดเดียว ----
const stepDot = (n: string, label: string) => ({ el: 'box', className: 'flex items-center gap-1', card: [
  { el: 'box', className: 'w-[18px] h-[18px] rounded-full bg-[var(--ev-surface2)] flex items-center justify-center', card: [
    { el: 'text', value: n, className: '!text-[9px] font-bold opacity-70' }] },
  { el: 'text', value: label, className: '!text-[11px] opacity-60' },
]});
const stepSep = { el: 'icon', icon: 'chevron_right', textSize: 'text-[13px]', className: 'opacity-20' };
const rightIdle = {
  el: 'box', when: NO_TASKS, className: 'h-full flex flex-col items-center justify-center text-center px-6 py-16',
  card: [
    { el: 'box', className: 'w-16 h-16 rounded-full bg-[var(--ev-surface)] border border-[var(--ev-border)] flex items-center justify-center mb-5', card: [
      { el: 'icon', icon: 'movie', textSize: 'text-[30px]', className: 'opacity-25' }] },
    { el: 'text', value: 'ยังไม่มีคลิปที่ผลิต', className: '!text-[15px] font-bold !text-[var(--ev-text)] opacity-70' },
    { el: 'text', value: 'ตั้งค่าสินค้าและสไตล์ทางซ้าย แล้วกดปุ่ม "เริ่มผลิตคลิป"', className: 'text-[12.5px] mt-1.5 leading-relaxed opacity-50' },
    { el: 'row', className: 'items-center gap-2 mt-6 justify-center', style: { flexWrap: 'nowrap' }, card: [
      stepDot('1', 'เพิ่มสินค้า'), stepSep, stepDot('2', 'ตัวละคร'), stepSep, stepDot('3', 'เลือกสไตล์'), stepSep, stepDot('4', 'เริ่มผลิต'),
    ]},
  ],
};

// ---- ขวา: มีคิวแล้ว (M5 จะแทนด้วย Run monitor header + grid/list) ----
const rightWork = {
  el: 'box', when: HAS_TASKS, className: 'p-4 flex flex-col gap-4',
  card: [
    { el: 'row', className: 'items-center gap-2 flex-wrap', card: [
      { el: 'stat-card', label: 'คิวทั้งหมด', value: COUNT_TASKS, icon: 'movie' },
      { el: 'stat-card', label: 'เสร็จแล้ว', value: COUNT_DONE, icon: 'check_circle' },
    ]},
    taskCard,
  ],
};

// ---- โครงหน้าเดียว 2 คอลัมน์ (ซ้าย 460px / ขวา flex-1 · <1280 พับเป็นคอลัมน์เดียว) ----
const mainLayout = {
  el: 'box', className: 'flex flex-col min-[1280px]:flex-row min-[1280px]:h-[calc(100vh-70px)] w-full',
  card: [
    { el: 'box', className: 'flex flex-col min-h-0 w-full min-[1280px]:w-[460px] min-[1280px]:shrink-0 min-[1280px]:border-r border-[var(--ev-border)]',
      card: [
        { el: 'box', className: 'flex-1 min-h-0 min-[1280px]:overflow-y-auto p-4 space-y-3.5', card: wizardForm },
        controlFooter,
      ]},
    { el: 'box', className: 'flex-1 min-h-0 min-[1280px]:overflow-y-auto', card: [rightIdle, rightWork] },
  ],
};

const config = {
  schemaVersion: 1,
  title: 'หมีแว่น ขายดุ',
  icon: 'sell',
  app: { id: 'hardsell' },
  persistBar: true,
  devBar: false,
  theme: { ...film.theme, vars: { ...film.theme.vars, '--ev-accent': '#f76b6b', '--ev-accent-fg': '#ffffff' } },
  style: film.style || undefined,
  breakpoints: film.breakpoints || undefined,
  chrome: { content: { className: '!max-w-none !p-0' } },   // หน้าเดียว 2 คอลัมน์เต็มจอ (ตัดกรอบ 1180 + padding กลาง)
  content: { item: { coll: 'tasks', label: 'คลิป' }, assets: ['products', 'characters'] },
  lookups: LOOKUPS,
  components: { runBanner: RUN_BANNER },
  home: {
    title: 'หมีแว่น ขายดุ', tag: 'EasyBear Hardsell',
    description: 'ปั่นคลิปขายสินค้าสไตล์ TikTok — ฮุคแรง โน้มน้าว ปิดการขาย ครบจบทีละหลายคลิป',
    cta: 'สร้างโปรเจกต์ใหม่', ctaContrast: true, loadLabel: 'โหลดโปรเจกต์เดิม',
    footer: film.home?.footer || [],
  },
  values: {
    templateId: 'ugc-review', toneId: 'hardsell', textMode: 'overlay', textStyleId: 'golden-triangle',
    clipLength: '8', clipsPerProduct: '1',
    imageModel: DEF_IMG, videoModel: DEF_VID,
    blocklistEnabled: 'true', blocklist: HS_BLOCKED_DEFAULT.join(','),
    maxParallel: '1', staggerMs: '3000', maxAttempts: '3',
  },
  collections: {
    control: { fields: [] },
    products: { fields: ['name', 'price', 'description', 'promotion', 'cta', 'enabled'], slots: ['image'] },
    characters: { fields: ['name', 'gender', 'ageRange', 'enabled'], slots: ['image'] },
    tasks: {
      fields: ['productId', 'productName', 'clipIndex', 'angle', 'characterId', 'clipLength',
        'h1', 'h2', 'speech', 'speech2', 'cta', 'sceneIdea', 'reviewer', 'reviewerGender',
        'imagePrompt', 'videoPrompt1', 'videoPrompt2'],
      slots: ['image', 'video1', 'video2'],
    },
  },
  seed: { control: [{ id: 'ctl', fields: {} }] },
  // scope "รายกลุ่ม" ยึด control (ไม่ใช่ tasks) — กัน gen-phase จำกัดงานเหลือคลิปเดียว (content.item.coll=tasks ใช้เรื่อง label/save เท่านั้น)
  auto: { scopeColl: 'control' },
  ops: [
    { id: 'hsQueue', type: 'transform', over: 'control', out: 'queued', fn: 'hsBuildTasks' },
    { id: 'hsContent', type: 'transform', over: 'tasks', out: 'written', fn: 'hsArchitectClip' },
    { id: 'hsPrompts', type: 'transform', over: 'tasks', out: 'prompted', fn: 'hsBuildPrompts' },
    {
      id: 'hsImage', type: 'image', over: 'tasks', out: 'image',
      model: '{values.imageModel}', aspectRatio: '9:16', prompt: '{item.imagePrompt}',
      refs: { op: 'lookupRefs', from: 'products', by: '{item.refs.product}', slot: 'image', also: [{ from: 'characters', by: '{item.refs.char}', slot: 'image' }] },
    },
    {
      id: 'hsVideo1', type: 'video', over: 'tasks', out: 'video1',
      model: '{values.videoModel}', aspectRatio: '9:16', durationSeconds: 8,
      startFrame: '{item.slots.image}', prompt: '{item.videoPrompt1}',
    },
    {
      id: 'hsVideo2', type: 'video', over: 'tasks', out: 'video2', where: 'clipLength=16',
      model: '{values.videoModel}', aspectRatio: '9:16', durationSeconds: 8,
      startFrame: '{item.slots.video1}', tailTrim: 1, prompt: '{item.videoPrompt2}',
    },
  ],
  stages: [
    { op: 'hsQueue' },
    { op: 'hsContent' },
    { op: 'hsPrompts' },
    { op: 'hsImage' },
    { op: 'hsVideo1' },
    { op: 'hsVideo2' },
    { checkpoint: 'main' },
  ],
  run: { maxParallel: 1, staggerMs: 3000, maxAttempts: 3 },
  settings: {
    title: 'ตั้งค่า',
    form: [
      { el: 'dropdown', field: 'imageModel', label: 'โมเดลภาพ', options: IMAGE_MODELS },
      { el: 'dropdown', field: 'videoModel', label: 'โมเดลวิดีโอ', options: VIDEO_MODELS },
      { el: 'stepper', field: 'maxParallel', label: 'งานพร้อมกัน (1-4)', min: 1, max: 4 },
      { el: 'switch', field: 'blocklistEnabled', label: 'เปิดกรองคำต้องห้าม' },
      { el: 'taginput', field: 'blocklist', label: 'คำต้องห้าม (แตะเพื่อลบ)' },
    ],
  },
  phases: [
    {
      id: 'main', title: '', navLabel: 'หน้าหลัก',
      form: [
        { el: 'use', component: 'runBanner' },
        mainLayout,
      ],
    },
  ],
  brain: {},
};

const out = path.join(CFG, 'hardsell.json');
fs.writeFileSync(out, JSON.stringify(config, null, 2));
console.log('เขียน', out, JSON.stringify(config).length, 'bytes (compact)');
