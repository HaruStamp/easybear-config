// gen-hardsell-config.ts — สร้าง hardsell.json จาก pack จริง (option lists sync กับ hooks-hardsell เสมอ)
// รัน: cd easybear-starter && npx tsx ../easybear-config/scripts/gen-hardsell-config.ts
// theme + model options ยืมจาก film.json (มาตรฐานเดียวกัน) · เขียนทับ easybear-config/hardsell.json (indent=2 ไม่มี trailing newline)
// โครง UI = ต้นฉบับ easybear-hardsell design lock v2 (mockups/mockup.html + src/components) — หน้าเดียว 2 คอลัมน์
//   ซ้าย: wizard ①-④ ↔ SummaryCard + log + ปุ่มควบคุมเดียว · ขวา: idle / Run monitor (header+grid/list)
//   หน้าแยก: จัดการสินค้า / จัดการตัวละคร (สลับด้วย values.__page) + เซฟ/โหลดราย list
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

// ---- option lists จาก pack (sync อัตโนมัติ) ----
const TEMPLATE_OPTS = (cat?: string) => HS_SCENE_TEMPLATES.filter(t => !cat || t.category === cat).map(t => ({ value: t.id, label: t.name, desc: t.desc, icon: t.icon }));
const TONE_OPTS = HS_TONES.map(t => ({ value: t.id, label: t.name, desc: t.desc, icon: t.icon }));
const STYLE_OPTS = HS_TEXT_STYLES.map(s => ({ value: s.id, label: s.name, desc: s.desc, ...(s.colors.length ? { colors: s.colors } : { icon: 'shuffle' }) }));
const AGE_OPTS = ['วัยรุ่น (18-25)', 'วัยทำงาน (25-35)', 'กลางคน (35-50)', 'สูงวัย (50+)'].map(a => ({ value: a, label: a }));   // string ตรง CharacterEditor ต้นฉบับ (มีวงเล็บ)
const catCount = (c: string) => HS_SCENE_TEMPLATES.filter(t => t.category === c).length;

// ---- ตาราง lookup (banner + ป้ายสรุป/การ์ด) ----
const LOOKUPS: Record<string, Record<string, string>> = {
  opBanner: { hsContent: '1', hsImage: '1', hsVideo1: '1', hsVideo2: '1' },
  opNames: { hsQueue: 'จัดคิวผลิต', hsContent: 'เขียนบทขาย', hsPrompts: 'เตรียมพรอมพ์', hsImage: 'สร้างภาพเฟรมแรก', hsVideo1: 'สร้างวีดีโอ ช่วง 1', hsVideo2: 'ต่อฉาก ช่วง 2' },
  opPhase: { hsContent: '1/3', hsImage: '2/3', hsVideo1: '3/3', hsVideo2: '3/3' },
  tplNames: Object.fromEntries(HS_SCENE_TEMPLATES.map(t => [t.id, t.name])),
  toneNames: Object.fromEntries(HS_TONES.map(t => [t.id, t.name])),
  styleNames: Object.fromEntries(HS_TEXT_STYLES.map(s => [s.id, s.name])),
  textModeTh: { overlay: 'มีข้อความ', none: 'ไม่มีข้อความ' },
  genderTh: { female: 'หญิง', male: 'ชาย' },
  zeroChar: { '0': 'AI สุ่มตัวละครให้เอง' },
  modelShort: Object.fromEntries([...IMAGE_MODELS, ...VIDEO_MODELS].map((o: any) => [o.value, String(o.label || o.value).replace('🍌 ', '')])),
};

// ---- shorthand helpers (generator เท่านั้น — output เป็น JSON ล้วน) ----
const tx = (value: any, className: string, when?: any, icon?: string): any => ({ el: 'text', value, className, ...(when != null ? { when } : {}), ...(icon ? { icon } : {}) });
const box = (className: string, card: any[], when?: any, style?: any): any => ({ el: 'box', className, card, ...(when != null ? { when } : {}), ...(style ? { style } : {}) });
const row = (className: string, card: any[], when?: any): any => ({ el: 'row', className, style: { flexWrap: 'nowrap' }, card, ...(when != null ? { when } : {}) });
const fieldLabel = (icon: string, label: string) => tx(label, 'flex items-center gap-1 !text-[10px] uppercase tracking-[0.06em] font-semibold opacity-50 px-1 mb-1.5', undefined, icon);   // flex items-center = icon กึ่งกลางแนวตั้งกับข้อความ (ตาม FieldLabel ต้นฉบับ HomeScreen.tsx:24)
const EQ = (a: any, b: any) => ({ op: 'eq', a, b });
const NEQ = (a: any, b: any) => ({ op: 'not', a: { op: 'eq', a, b } });
const AND = (...list: any[]) => ({ op: 'and', list });
const OR = (...list: any[]) => ({ op: 'or', list });
const CONCAT = (...parts: any[]) => ({ op: 'concat', parts });
const LK = (table: string, key: any, fallback?: any) => ({ op: 'lookup', table, key, ...(fallback != null ? { fallback } : {}) });

// ---- เงื่อนไขสถานะ (ปุ่มควบคุมเดียว + จอขวา — ตรรกะตาม MainScreen.tsx ต้นฉบับ) ----
const ST_RUNNING = OR(EQ('{values.__runState}', 'running'), EQ('{values.__runState}', 'cooldown'), EQ('{values.__runState}', 'retrying'));
// มีงาน gen วิ่งอยู่ทางไหนก็ตาม (batch ทั้งคิว หรือ retry รายคลิปที่ไม่แตะ __runState) — ใช้ล็อกปุ่มลบคลัง (ต้นฉบับล็อก manager ทั้ง 2 เคสเหมือนกัน)
const ANY_GEN = OR(ST_RUNNING, { op: 'some', from: 'tasks', where: 'status=running' });
const NOT_RUNNING = { op: 'not', a: ST_RUNNING };
const COUNT_TASKS = { op: 'count', from: 'tasks' };
const HAS_TASKS = { op: 'gt', a: COUNT_TASKS, b: 0 };
const NO_TASKS = EQ(COUNT_TASKS, 0);
const COUNT_RUNNING = { op: 'count', from: 'tasks', where: 'status=running' };
const COUNT_ERROR = { op: 'count', from: 'tasks', where: 'status=error' };
const HAS_ERROR = { op: 'gt', a: COUNT_ERROR, b: 0 };
const NO_ERROR = { op: 'not', a: HAS_ERROR };
// เสร็จจริงต่อคลิป = มีวิดีโอช่วงสุดท้ายของโหมดนั้น (8 วิ = video1 · 16 วิ = video2)
const COUNT_DONE = { op: 'add',
  a: { op: 'count', from: 'tasks', where: 'clipLength=8', slot: 'video1' },
  b: { op: 'count', from: 'tasks', where: 'clipLength=16', slot: 'video2' } };
const ALL_DONE = AND(HAS_TASKS, EQ(COUNT_DONE, COUNT_TASKS));
const NOT_ALL_DONE = { op: 'not', a: ALL_DONE };
const ENABLED_PRODUCTS = { op: 'count', from: 'products', where: 'enabled=true' };
const TOTAL_CLIPS = { op: 'mul', a: ENABLED_PRODUCTS, b: '{values.clipsPerProduct}' };
const READY = AND({ op: 'gt', a: ENABLED_PRODUCTS, b: 0 }, { op: 'all', from: 'products', where: 'enabled=true', slot: 'image' });
const ENABLED_CHARS = { op: 'count', from: 'characters', where: 'enabled=true' };
// เส้นผลิตทั้งคิว (ข้ามตัวที่เสร็จแล้วเอง + retry ตัวพลาดเอง = พฤติกรรม autoProduce ต้นฉบับ)
const CHAIN = ['hsQueue', 'hsContent', 'hsPrompts', 'hsImage', 'hsVideo1', 'hsVideo2'];

// ═══════════ ซ้าย: WIZARD ①-④ (accordion ตาม HomeScreen.tsx) ═══════════
const stepBadge = (n: string) => box('w-[34px] h-[34px] rounded-full flex items-center justify-center shrink-0',
  [tx(n, '!text-[15px] font-black !text-white')], undefined,
  { background: 'linear-gradient(135deg, var(--ev-accent), color-mix(in srgb, var(--ev-accent) 75%, #7f1d1d))' });
const cardTitle = (t: string) => tx(t, 'font-bold !text-[15px] !text-[var(--ev-text)]');
const manageBtn = (label: string, page: string) => box('ml-auto shrink-0', [
  { el: 'button', action: 'set', to: '__page', value: page, label, icon: 'tune', size: 'sm', variant: 'outline-accent', className: '!h-8 font-bold !text-[12px] !bg-[var(--ev-accent)]/10' },
]);
const WIZ_CARD = '!rounded-[24px] !p-5 bg-[var(--ev-surface)] !border-[#595959]';   // การ์ดระดับบนสุดขอบเข้ม #595959 ตามต้นฉบับ (แยกลำดับชั้นจากการ์ดย่อย --ev-border)

// แถวสินค้าอ่านอย่างเดียว (ใช้ทั้ง wizard ① และ SummaryCard)
const productRow = {
  el: 'repeat', coll: 'products', where: 'enabled=true', empty: 'ยังไม่ได้เลือกใช้สินค้า — กด "จัดการสินค้า" เพื่อเพิ่ม/ติ๊กใช้',
  card: [box('bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-2xl p-2.5 flex flex-row items-center gap-2.5', [
    box('w-5 h-5 rounded-full bg-[var(--ev-surface2)] flex items-center justify-center shrink-0', [tx({ op: 'add', a: { op: 'index' }, b: 1 }, '!text-[11px] font-bold opacity-70 tabular-nums')]),
    { el: 'media-slot', src: '{item.slots.image}', aspect: '1:1', className: '!w-11 shrink-0 !rounded-lg' },
    box('flex-1 min-w-0', [
      tx('{item.name}', 'font-medium !text-[14px] truncate !text-[var(--ev-text)]'),
      row('gap-1.5 items-center', [
        tx('{item.price}', '!text-[12px] opacity-50 truncate', 'item.price!='),
        tx('{item.promotion}', '!text-[12px] opacity-50 truncate', 'item.promotion!='),
        tx('ยังไม่มีรูป — ไม่เข้าคิว', '!text-[12px] !text-amber-400', 'item.slots.image='),
      ]),
    ]),
  ])],
};

// chips ตัวละครที่เลือกใช้ (wizard ② = flex-wrap · SummaryCard = grid 3 คอลัมน์แน่นตามต้นฉบับ)
const charChips = (wrapCls: string) => box(wrapCls, [{
  el: 'repeat', coll: 'characters', where: 'enabled=true',
  card: [box('bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-xl pl-2 pr-3.5 py-2 flex flex-row items-center gap-2.5 min-w-0', [
    { el: 'media-slot', src: '{item.slots.image}', aspect: '1:1', className: '!w-9 shrink-0 !rounded-lg' },
    box('min-w-0', [
      tx('{item.name}', '!text-[12px] font-bold !text-[var(--ev-text)] leading-tight truncate'),
      { el: 'text', value: CONCAT(LK('genderTh', '{item.gender}', '{item.gender}'), ' · {item.ageRange}'), className: '!text-[10px] opacity-50 mt-0.5 truncate' },
    ]),
  ])],
}], { op: 'gt', a: ENABLED_CHARS, b: 0 });
const casinoCard = (when: any) => box('rounded-2xl p-4 flex flex-row items-center gap-3.5 bg-[var(--ev-surface)] border border-[var(--ev-border)]', [
  { el: 'icon', icon: 'casino', textSize: 'text-[34px]', className: 'text-[var(--ev-accent)] shrink-0' },
  box('min-w-0', [
    tx('AI สุ่มตัวละครให้เอง', 'font-bold !text-[14px] !text-[var(--ev-text)]'),
    tx('ไม่ได้เลือกตัวละคร — แต่ละคลิป AI จะสุ่มสร้างคนรีวิวให้เข้ากับสินค้า', '!text-[11px] opacity-50 mt-0.5'),
  ]),
], when);

const wizardForm: any[] = [
  // ① สินค้า
  { el: 'group', collapsible: true, startOpen: true, className: WIZ_CARD,
    head: [stepBadge('1'), cardTitle('สินค้า'), manageBtn('จัดการสินค้า', 'products')],
    summary: CONCAT('เลือกใช้ ', ENABLED_PRODUCTS, ' สินค้า'),
    card: [
      { el: 'text', value: CONCAT('เลือกใช้ ', ENABLED_PRODUCTS, ' สินค้า จาก ', { op: 'count', from: 'products' }, ' รายการ'), icon: 'check_circle', className: '!text-[11px] opacity-60 px-1' },
      productRow,
    ]},
  // ② ตัวละคร
  { el: 'group', collapsible: true, startOpen: true, className: WIZ_CARD,
    head: [stepBadge('2'), cardTitle('ตัวละคร (คนรีวิว)'), manageBtn('จัดการตัวละคร', 'characters')],
    summary: LK('zeroChar', ENABLED_CHARS, CONCAT('เลือกใช้ ', ENABLED_CHARS, ' ตัวละคร')),
    card: [
      { el: 'text', value: CONCAT('เลือกใช้ ', ENABLED_CHARS, ' ตัวละคร จาก ', { op: 'count', from: 'characters' }, ' รายการ · AI สุ่มให้แต่ละคลิป'), icon: 'check_circle', className: '!text-[11px] opacity-60 px-1', when: { op: 'gt', a: ENABLED_CHARS, b: 0 } },
      charChips('flex flex-row flex-wrap gap-2.5'),
      casinoCard(EQ(ENABLED_CHARS, 0)),
    ]},
  // ③ สไตล์คลิป
  { el: 'group', collapsible: true, startOpen: true, className: WIZ_CARD,
    head: [stepBadge('3'), cardTitle('สไตล์คลิป')],
    summary: CONCAT(LK('tplNames', '{values.templateId}', '{values.templateId}'), ' · ', LK('toneNames', '{values.toneId}', '{values.toneId}'), ' · ', LK('textModeTh', '{values.textMode}', '')),
    card: [
      fieldLabel('style', 'เทมเพลต (ฉาก/สไตล์)'),
      { el: 'segmented', field: 'styleCat', variant: 'pill', options: [
        { value: 'ugc', label: `UGC คนรีวิว ${catCount('ugc')}` },
        { value: 'style', label: `สไตล์อื่น ${catCount('style')}` },
        { value: 'd3', label: `การ์ตูน 3D ${catCount('d3')}` },
      ]},
      { el: 'grid-select', field: 'templateId', cols: 3, contained: false, options: TEMPLATE_OPTS('ugc'), when: 'styleCat=ugc' },
      { el: 'grid-select', field: 'templateId', cols: 3, contained: false, options: TEMPLATE_OPTS('style'), when: 'styleCat=style' },
      { el: 'grid-select', field: 'templateId', cols: 3, contained: false, options: TEMPLATE_OPTS('d3'), when: 'styleCat=d3' },
      tx('การ์ตูน 3D = เกริ่นปัญหา → สินค้าช่วยฉากท้าย · ทุกเทมเพลตกัน claims เสี่ยงแบนเหมือนกัน', '!text-[11px] opacity-40', undefined, 'info'),
      { el: 'spacer', className: 'h-1' },
      fieldLabel('mood', 'โทน / อารมณ์'),
      { el: 'dropdown', field: 'toneId', options: TONE_OPTS },
      { el: 'spacer', className: 'h-1' },
      tx('ข้อความบนภาพ', '!text-[10px] font-black uppercase tracking-[0.12em] opacity-40'),
      box('grid grid-cols-2 gap-3', [
        box('', [
          fieldLabel('title', 'ใส่ตัวหนังสือบนภาพ'),
          { el: 'segmented', field: 'textMode', variant: 'tab', options: [
            { value: 'overlay', label: 'ใส่' }, { value: 'none', label: 'ไม่ใส่' },
          ]},
        ]),
        box('', [
          fieldLabel('palette', 'สไตล์ตัวหนังสือ'),
          { el: 'dropdown', field: 'textStyleId', when: 'textMode=overlay', options: STYLE_OPTS },
          box('rounded-xl px-3.5 flex flex-row items-center gap-2 h-[46px] bg-[var(--ev-surface)] border border-dashed border-[var(--ev-border)]',
            [tx('คลิปจะไม่มีตัวหนังสือบนภาพ', '!text-[12px] opacity-60', undefined, 'info')], 'textMode=none'),
        ]),
      ]),
    ]},
  // ④ การผลิต
  { el: 'group', collapsible: true, startOpen: true, className: WIZ_CARD,
    head: [stepBadge('4'), cardTitle('การผลิต')],
    summary: '{values.clipLength} วิ · {values.clipsPerProduct} คลิป/สินค้า',
    card: [
      box('grid grid-cols-2 gap-3', [
        box('', [
          fieldLabel('timer', 'ความยาวคลิป'),
          { el: 'segmented', field: 'clipLength', variant: 'tab', selClass: 'bg-gradient-to-br from-orange-400 to-orange-600 text-white', options: [{ value: '8', label: '8 วิ' }, { value: '16', label: '16 วิ' }] },   // เลือกแล้ว = gradient ส้มตาม HomeScreen ต้นฉบับ (ไม่ใช่ขาว)
          tx('พูด 1 ช่วง · ฮุค → ปิดการขาย', '!text-[11px] opacity-40 mt-2 px-1', 'values.clipLength=8'),
          tx('พูด 2 ช่วง · ฮุค → โปร → ชวนซื้อ', '!text-[11px] opacity-40 mt-2 px-1', 'values.clipLength=16'),
        ]),
        box('', [
          fieldLabel('content_copy', 'จำนวนคลิป/สินค้า'),
          { el: 'stepper', field: 'clipsPerProduct', label: '', min: 1, max: 100, className: 'bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-xl px-2 py-1.5' },   // label:'' = กล่อง [− n +] เปล่า (หัวข้ออยู่บรรทัดบนแล้ว — เดิม fallback โชว์ชื่อ field CLIPSPERPRODUCT)
          tx('ต่างมุมขาย/บทพูด แต่ละคลิป', '!text-[11px] opacity-40 mt-2 px-1'),
        ]),
      ]),
      // ตั้งค่าขั้นสูง (พับ · default ปิด) — โมเดล + จังหวะพัก + กรองคำ
      { el: 'group', collapsible: true, label: 'ตั้งค่าการผลิต', icon: 'tune', className: '!rounded-2xl bg-[var(--ev-surface)]',
        summary: CONCAT(LK('modelShort', '{values.imageModel}', '{values.imageModel}'), ' · ', LK('modelShort', '{values.videoModel}', '{values.videoModel}')),
        card: [
          { el: 'dropdown', field: 'imageModel', label: 'โมเดลสร้างภาพ', options: IMAGE_MODELS },
          { el: 'dropdown', field: 'videoModel', label: 'โมเดลสร้างวีดีโอ', options: VIDEO_MODELS },
          box('bg-black/20 border border-[var(--ev-border)] rounded-xl px-4 divide-y divide-[var(--ev-border)]', [
            { el: 'stepper', field: 'maxParallel', label: 'ผลิตพร้อมกันสูงสุด', placeholder: '1 = ทีละคลิป เสถียรสุด', icon: 'layers', unit: 'งาน', min: 1, max: 4, className: 'py-3.5' },
            { el: 'stepper', field: 'staggerMs', label: 'พักระหว่างงาน', placeholder: 'เหลื่อมเวลาปล่อยงานขนาน', icon: 'bolt', unit: 'วิ', min: 0, max: 30000, step: 1000, divisor: 1000, className: 'py-3.5' },
            { el: 'stepper', field: 'batchDelay', label: 'พักระหว่างชุด', placeholder: 'จบชุดหนึ่ง พักก่อนชุดถัดไป (กันโดนลิมิต)', icon: 'restart_alt', unit: 'วิ', min: 0, max: 120, step: 5, className: 'py-3.5' },
            { el: 'stepper', field: 'retryDelay', label: 'พักก่อนลองใหม่', placeholder: 'ตอนงานพลาด รอเท่านี้ก่อนยิงใหม่', icon: 'replay', unit: 'วิ', min: 0, max: 60, className: 'py-3.5' },
            { el: 'stepper', field: 'maxAttempts', label: 'ลองใหม่สูงสุด', placeholder: 'ต่อชิ้นงาน รวมครั้งแรก', icon: 'repeat', unit: 'ครั้ง', min: 1, max: 5, className: 'py-3.5' },
          ]),
          row('items-center justify-between', [
            tx('กรองคำต้องห้าม', '!text-[10px] font-bold uppercase tracking-widest opacity-40', undefined, 'shield'),
            { el: 'switch', field: 'blocklistEnabled', label: 'เปิด' },
          ]),
          { el: 'taginput', field: 'blocklist', placeholder: 'พิมพ์คำที่ต้องการกรอง แล้ว Enter...', when: 'blocklistEnabled=true' },
          { el: 'button', action: 'set', to: 'blocklist', value: HS_BLOCKED_DEFAULT.join(','), label: 'รีเซ็ตค่าเริ่มต้น', icon: 'restart_alt', size: 'sm', variant: 'ghost', when: 'blocklistEnabled=true' },
        ]},
    ]},
];

// ═══════════ ซ้าย (ตอนมีคิว): SUMMARY CARD "การตั้งค่า" 🔒 (SummaryCard.tsx) ═══════════
const subHead = (icon: string, title: string) => box('flex flex-row items-center gap-2 pt-3 mt-1 border-t border-[var(--ev-border)]', [
  { el: 'icon', icon, textSize: 'text-[17px]', className: 'text-[var(--ev-accent)] opacity-80' },
  tx(title, '!text-[13px] font-bold !text-[var(--ev-text)]'),
]);
const valueRow = (icon: string, label: string, right: any[]) => box('bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-xl px-3.5 h-[40px] flex flex-row items-center justify-between !text-[12px]', [
  row('items-center gap-2', [{ el: 'icon', icon, textSize: 'text-[16px]', className: 'text-[var(--ev-accent)] opacity-80' }, tx(label, '!text-[12px] opacity-70')]),
  row('items-center gap-1.5 min-w-0 ml-2', right),
]);
const bigStat = (icon: string, label: string, value: any, unit: string) => box('bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-xl px-4 py-3 flex flex-row items-center gap-3', [
  { el: 'icon', icon, textSize: 'text-[22px]', className: 'text-[var(--ev-accent)] opacity-90' },
  box('', [
    tx(label, '!text-[9.5px] uppercase tracking-wider opacity-40 font-bold'),
    row('items-baseline gap-1', [tx(value, '!text-[19px] font-black leading-tight tabular-nums !text-[var(--ev-text)]'), tx(unit, '!text-[11px] opacity-40 font-medium')]),
  ]),
]);
const summaryCard = box(WIZ_CARD + ' border border-[var(--ev-border)] flex flex-col gap-2', [
  row('items-center justify-between', [
    tx('การตั้งค่า', 'font-bold !text-[14px] !text-[var(--ev-text)]'),
    box('!text-[10px] font-bold text-amber-400/90 bg-amber-500/10 border border-amber-500/20 rounded-full px-2.5 py-1 flex flex-row items-center gap-1',
      [{ el: 'icon', icon: 'lock', textSize: 'text-[12px]', className: 'text-amber-400' }, tx('ล็อกระหว่างผลิต', '!text-[10px] font-bold !text-amber-400/90')], NOT_ALL_DONE),
  ]),
  subHead('shopping_cart', 'สินค้า'),
  { el: 'group', collapsible: true, className: '!rounded-xl bg-[var(--ev-surface)] !p-3', chevClass: '!text-[var(--ev-accent)]',
    head: [
      { el: 'text', value: CONCAT('เลือกใช้ ', ENABLED_PRODUCTS, ' สินค้า · รวมคิวผลิต ', COUNT_TASKS, ' คลิป'), className: '!text-[12.5px] font-bold !text-[var(--ev-text)] truncate' },
      box('ml-auto shrink-0 !text-[11px] font-bold text-[var(--ev-accent)] px-2 py-1 rounded-lg border border-[var(--ev-accent)]/30 bg-[var(--ev-accent)]/[0.08]', [tx('ดูสินค้า', '!text-[11px] font-bold !text-[var(--ev-accent)]')]),
    ],
    card: [box('max-h-[170px] overflow-y-auto pr-1 flex flex-col gap-1.5', [productRow])] },
  subHead('group', 'ตัวละคร'),
  { el: 'group', collapsible: true, className: '!rounded-xl bg-[var(--ev-surface)] !p-3', chevClass: '!text-[var(--ev-accent)]',
    head: [
      { el: 'text', value: LK('zeroChar', ENABLED_CHARS, CONCAT('เลือกใช้ ', ENABLED_CHARS, ' ตัวละคร · AI สุ่มให้แต่ละคลิป')), className: '!text-[12.5px] font-bold !text-[var(--ev-text)] truncate' },
      box('ml-auto shrink-0 !text-[11px] font-bold text-[var(--ev-accent)] px-2 py-1 rounded-lg border border-[var(--ev-accent)]/30 bg-[var(--ev-accent)]/[0.08]', [tx('ดูตัวละคร', '!text-[11px] font-bold !text-[var(--ev-accent)]')]),
    ],
    card: [charChips('grid grid-cols-3 gap-1.5'), casinoCard(EQ(ENABLED_CHARS, 0))] },
  subHead('style', 'สไตล์คลิป'),
  box('grid grid-cols-2 gap-2', [
    valueRow('reviews', 'ฉาก', [tx(LK('tplNames', '{values.templateId}', '{values.templateId}'), '!text-[12px] opacity-70 truncate')]),
    valueRow('local_fire_department', 'โทน', [tx(LK('toneNames', '{values.toneId}', '{values.toneId}'), '!text-[12px] opacity-70 truncate')]),
  ]),
  valueRow('title', 'ข้อความ', [
    tx(CONCAT('ใส่ · สไตล์', LK('styleNames', '{values.textStyleId}', '{values.textStyleId}')), '!text-[12px] opacity-70 truncate', 'values.textMode=overlay'),
    tx('ไม่ใส่', '!text-[12px] opacity-70', 'values.textMode=none'),
  ]),
  subHead('settings', 'การผลิต'),
  box('grid grid-cols-2 gap-2', [
    bigStat('timer', 'ความยาวคลิป', '{values.clipLength}', 'วิ · 9:16'),
    bigStat('content_copy', 'คลิป/สินค้า', '{values.clipsPerProduct}', 'คลิป'),
  ]),
  valueRow('smart_toy', 'โมเดล', [
    tx(LK('modelShort', '{values.imageModel}', '{values.imageModel}'), '!text-[12px] opacity-70 truncate', undefined, 'image'),
    tx(LK('modelShort', '{values.videoModel}', '{values.videoModel}'), '!text-[12px] opacity-70 truncate', undefined, 'movie'),
  ]),
  valueRow('shield', 'กรองคำต้องห้าม', [
    box('flex flex-row items-center gap-1.5', [box('w-1.5 h-1.5 rounded-full bg-green-400', []), { el: 'text', value: CONCAT('เปิด · ', { op: 'listLen', value: '{values.blocklist}' }, ' คำ'), className: '!text-[12px] !text-green-400/90' }], 'values.blocklistEnabled=true'),   // "เปิด · N คำ" ตาม SummaryCard ต้นฉบับ
    tx('ปิด', '!text-[12px] opacity-40', 'values.blocklistEnabled!=true'),
  ]),
], HAS_TASKS);

// ═══════════ ซ้ายล่าง: ปุ่มควบคุมเดียว ปัก footer + hint ใต้ปุ่ม ═══════════
const CTRL_BTN = 'w-full justify-center !h-12 !rounded-2xl !text-[14px]';
const hintTx = (when: any, value: any) => tx(value, 'text-center !text-[11px] mt-2 opacity-70', when);
const controlFooter = box('p-4 pb-5 border-t border-[var(--ev-border)] shrink-0', [
  box('mb-2.5 flex flex-row items-start gap-2 bg-amber-500/[0.08] border border-amber-500/25 rounded-xl px-3 py-2', [
    { el: 'icon', icon: 'warning', textSize: 'text-[15px]', className: 'text-amber-400 shrink-0 mt-px' },
    tx(CONCAT('คิวนี้ ', TOTAL_CLIPS, ' คลิป (เกิน 100) — งานเยอะอาจทำให้แอปทำงานหนักหรือช้า แนะนำแบ่งทำเป็นรอบเล็กลง หรือเลือกคลิป 8 วิ เพื่อความลื่นไหล'), '!text-[11px] leading-relaxed !text-amber-300/90'),
  ], AND(NO_TASKS, { op: 'gt', a: TOTAL_CLIPS, b: 100 })),
  { el: 'gen-phase', ops: CHAIN, when: NO_TASKS, label: CONCAT('เริ่มผลิตคลิป · ', TOTAL_CLIPS, ' คลิป') as any, icon: 'play_arrow',   // ตัวเลขฝังในป้ายปุ่มตาม MainScreen ต้นฉบับ (Btn label ผ่าน resolveStr แล้ว)
    className: CTRL_BTN + ' font-black shadow-[0_0_20px_rgba(247,107,107,0.35)] disabled:!shadow-none disabled:!opacity-30',
    disabledWhen: { op: 'not', a: READY }, reason: 'เพิ่มสินค้า + ใส่รูปให้ครบก่อนเริ่มผลิต' },
  { el: 'button', action: 'stop', when: ST_RUNNING, label: 'หยุดชั่วคราว', icon: 'pause', variant: 'ghost',
    className: CTRL_BTN + ' font-bold !text-red-300 !bg-red-500/10 !border !border-red-500/35 hover:!bg-red-500/20' },
  { el: 'gen-phase', ops: CHAIN, when: AND(NOT_RUNNING, HAS_TASKS, NO_ERROR, NOT_ALL_DONE),
    label: CONCAT('ทำงานต่อ · เหลือ ', { op: 'sub', a: COUNT_TASKS, b: COUNT_DONE }, ' คลิป') as any, icon: 'play_arrow', className: CTRL_BTN + ' font-black' },
  { el: 'gen-phase', ops: CHAIN, when: AND(NOT_RUNNING, HAS_ERROR),
    label: 'ลองใหม่ที่พลาด', icon: 'replay', className: CTRL_BTN + ' font-black' },
  { el: 'confirm-button', action: 'hook', fn: 'hsResetRun', when: AND(HAS_TASKS, NOT_RUNNING),
    label: 'รีเซ็ตงาน', icon: 'refresh', placeholder: 'ยืนยันรีเซ็ต?', variant: 'outline',
    className: 'w-full justify-center !h-11 mt-2 !rounded-2xl !text-[13.5px] font-bold' },
  hintTx(ST_RUNNING, 'กำลังผลิตอยู่ — ดูความคืบหน้าได้ที่ฝั่งขวา'),
  hintTx(AND(NOT_RUNNING, HAS_ERROR), 'หยุดเพราะพบปัญหา — กดลองใหม่ที่พลาดเพื่อลองคลิปที่ล้มเหลวอีกครั้ง หรือรีเซ็ตงานเพื่อล้างคิว'),
  hintTx(AND(NOT_RUNNING, NO_ERROR, HAS_TASKS, NOT_ALL_DONE),
    CONCAT('หยุดพักไว้ — กดทำงานต่อเพื่อรันคิวที่เหลือ ', { op: 'sub', a: COUNT_TASKS, b: COUNT_DONE }, ' คลิป')),
  hintTx(AND(NOT_RUNNING, ALL_DONE),
    CONCAT('เสร็จครบ ', COUNT_DONE, ' คลิป — ดาวน์โหลดได้ทางขวา หรือกดรีเซ็ตงานเพื่อตั้งค่าผลิตรอบใหม่')),
  hintTx(AND(NO_TASKS, EQ(ENABLED_PRODUCTS, 0)), 'ยังไม่ได้เลือกใช้สินค้า — เพิ่ม/ติ๊กใช้ที่ "จัดการสินค้า" ก่อน'),
  hintTx(AND(NO_TASKS, { op: 'gt', a: ENABLED_PRODUCTS, b: 0 }, { op: 'not', a: { op: 'all', from: 'products', where: 'enabled=true', slot: 'image' } }),
    'มีสินค้าที่ยังไม่มีรูป — ใส่รูปก่อนเริ่มผลิต'),
  hintTx(AND(NO_TASKS, READY),
    CONCAT('จากสินค้าที่เลือกไว้ ', ENABLED_PRODUCTS, ' ชิ้น · รวมคิว ', TOTAL_CLIPS, ' คลิป')),
]);

// ═══════════ ขวา: idle empty state ═══════════
const stepDot = (n: string, label: string) => box('flex flex-row items-center gap-1', [
  box('w-[18px] h-[18px] rounded-full bg-[var(--ev-surface2)] flex items-center justify-center', [tx(n, '!text-[9px] font-bold opacity-70')]),
  tx(label, '!text-[11px] opacity-60'),
]);
const stepSep = { el: 'icon', icon: 'chevron_right', textSize: 'text-[13px]', className: 'opacity-20' };
const rightIdle = box('h-full flex flex-col items-center justify-center text-center px-6 py-16 min-[960px]:py-6', [
  box('w-16 h-16 rounded-full bg-[var(--ev-surface)] border border-[var(--ev-border)] flex items-center justify-center mb-5', [
    { el: 'icon', icon: 'movie', textSize: 'text-[30px]', className: 'opacity-25' }]),
  tx('ยังไม่มีคลิปที่ผลิต', '!text-[15px] font-bold !text-[var(--ev-text)] opacity-70'),
  row('items-center justify-center gap-1 mt-1.5', [
    tx('ตั้งค่าสินค้าและสไตล์ทางซ้าย แล้วกดปุ่ม', '!text-[12.5px] leading-relaxed opacity-50'),
    tx('เริ่มผลิตคลิป', '!text-[12.5px] font-bold !text-[var(--ev-text)] opacity-70'),
  ]),
  row('items-center gap-2 mt-6 justify-center', [
    stepDot('1', 'เพิ่มสินค้า'), stepSep, stepDot('2', 'ตัวละคร'), stepSep, stepDot('3', 'เลือกสไตล์'), stepSep, stepDot('4', 'เริ่มผลิต'),
  ]),
], NO_TASKS);

// ═══════════ ขวา: RUN MONITOR (RunScreen header + grid/list) ═══════════
const chipCount = (bg: string, dotCls: string, txtCls: string, label: string, value: any, when?: any) =>
  box(`flex flex-row items-center gap-1.5 px-2.5 py-1 rounded-full whitespace-nowrap ${bg}`, [
    box(`w-1.5 h-1.5 rounded-full ${dotCls}`, []),
    { el: 'text', value: CONCAT(label + ' ', value), className: `!text-[12px] ${txtCls}` },
  ], when);
const clipBadge = box('flex flex-row items-center gap-0.5 !text-[9px] font-bold bg-white/20 rounded px-1 py-0.5 shrink-0', [
  { el: 'icon', icon: 'smart_display', textSize: 'text-[11px]', className: 'text-white' },
  tx('{item.clipIndex}/{values.clipsPerProduct}', '!text-[9px] font-bold !text-white'),
], { op: 'gt', a: '{values.clipsPerProduct}', b: 1 });
const bottomBar = box('absolute bottom-0 left-0 right-0 px-[9px] pb-[9px] pt-[18px] bg-gradient-to-t from-black/85 via-black/35 to-transparent z-[1] pointer-events-none', [
  row('items-center gap-1.5', [tx('{item.productName}', '!text-[11px] font-medium truncate !text-white min-w-0'), clipBadge]),
]);
const gridCardShell = 'relative aspect-[9/16] rounded-2xl overflow-hidden flex flex-col items-center justify-center gap-1.5';
const stateBadge = (bg: string, icon: string, label: any, iconCls = 'text-[var(--ev-accent)]') =>
  box(`absolute top-2 left-2 z-[2] flex flex-row items-center gap-1 px-2 py-1 rounded-full ${bg}`, [
    { el: 'icon', icon, textSize: 'text-[12px]', className: iconCls },
    { el: 'text', value: label, className: '!text-[9px] font-bold !text-white whitespace-nowrap' },
  ]);
// ชั้นภาพพื้นหลังของการ์ด (ต้นฉบับ style={bg} + overlay ดำ) — media-slot ปิด interaction แล้วหรี่ด้วย overlay
const cardImageLayer = box('absolute inset-0 pointer-events-none', [
  { el: 'media-slot', src: '{item.slots.image}', aspect: '9:16', className: '!absolute !inset-0 !h-full !border-0 !rounded-none' },
  box('absolute inset-0 bg-black/55', []),
], 'item.slots.image!=');
// การ์ดเสร็จ (คลิกดู = lightbox วิดีโอ · hover ปุ่มโหลด/ตัดต่อ) — เงื่อนไขความยาว+มีไฟล์รวมที่การ์ดเดียว (กัน cell เปล่าใน grid)
const doneCard = (len: string, slot: string) => box('relative aspect-[9/16] rounded-2xl overflow-hidden group', [
  { el: 'media-slot', src: '{item.slots.' + slot + '}', aspect: '9:16', className: '!rounded-2xl !border-0 !h-full' },   // (lightbox merged-preview + footer = รอ atoms deploy — จดใน memory)
  box('absolute top-2 left-2 z-[2] px-2 py-[3px] rounded-full bg-green-500 pointer-events-none', [tx('เสร็จ', '!text-[9px] font-bold !text-white')]),
  // 16 วิ = merge video1(trim 7)+video2 เป็นไฟล์เดียวก่อนโหลด (parity downloads ต้นฉบับ — รอยต่อเนียน) · 8 วิ = โหลดตรง
  { el: 'download-button', iconOnly: true, label: 'โหลดคลิป', icon: 'download', size: 'sm',
    ...(len === '16' ? { segments: [{ slot: 'video1', trimEndIfNext: 7 }, { slot: 'video2' }] } : { to: slot }),
    className: '!absolute top-[7px] right-[7px] z-[3] !w-7 !h-7 !p-0 !rounded-[9px] !bg-black/60 !border-0 !text-white opacity-0 group-hover:opacity-100 hover:!bg-[var(--ev-accent)]' },
  { el: 'open-editor', coll: 'tasks', only: true, iconOnly: true, icon: 'movie_edit', label: 'ตัดต่อคลิปนี้', size: 'sm',
    className: '!absolute top-[7px] right-[42px] z-[3] !w-7 !h-7 !p-0 !rounded-[9px] !bg-black/60 !border-0 !text-white opacity-0 group-hover:opacity-100 hover:!bg-[var(--ev-accent)]' },
  bottomBar,
], AND(EQ('{item.clipLength}', len), NEQ('{item.slots.' + slot + '}', '')));
const ITEM_RUNNING = EQ('{item.status}', 'running');
const ITEM_ERROR = AND(EQ('{item.status}', 'error'), NEQ('{item.meta.retrying}', '1'));
const ITEM_RETRYING = AND(NEQ('{item.status}', 'running'), EQ('{item.meta.retrying}', '1'));
const ITEM_LEFTOVER = AND(NEQ('{item.status}', 'running'), NEQ('{item.status}', 'error'), NEQ('{item.meta.retrying}', '1'),
  { op: 'not', a: OR(AND(EQ('{item.clipLength}', '8'), NEQ('{item.slots.video1}', '')), AND(EQ('{item.clipLength}', '16'), NEQ('{item.slots.video2}', ''))) });
const runGrid = box('grid gap-3 grid-cols-4 lg:grid-cols-5', [{
  el: 'repeat', coll: 'tasks',
  card: [
    doneCard('8', 'video1'),
    doneCard('16', 'video2'),
    // กำลังทำ — ภาพพื้นหลังหรี่ (ถ้ามีแล้ว) + badge ตาม stage + spinner + ป้ายขั้น (ตาม RunGrid ต้นฉบับ)
    box(gridCardShell + ' bg-[var(--ev-accent)]/5', [
      cardImageLayer,
      { ...stateBadge('bg-black/55', 'edit_note', 'เขียนบท'), when: EQ('{values.__runStage}', 'hsContent') },
      { ...stateBadge('bg-black/55', 'image', 'สร้างภาพ'), when: EQ('{values.__runStage}', 'hsImage') },
      { ...stateBadge('bg-black/55', 'image', 'ได้ภาพแล้ว'), when: EQ('{values.__runStage}', 'hsVideo1') },
      { ...stateBadge('bg-black/55', 'movie', 'ได้วีดีโอ 8วิ'), when: EQ('{values.__runStage}', 'hsVideo2') },
      { el: 'spinner', className: '!text-[28px] relative z-[1]' },
      { el: 'text', value: CONCAT(LK('opNames', '{values.__runStage}', 'กำลังทำ'), ' {item.meta.progress}%'), className: '!text-[10px] !text-[var(--ev-accent)] font-medium relative z-[1]', when: 'item.meta.progress!=' },
      { el: 'text', value: LK('opNames', '{values.__runStage}', 'กำลังทำ'), className: '!text-[10px] !text-[var(--ev-accent)] font-medium relative z-[1]', when: 'item.meta.progress=' },
      bottomBar,
    ], ITEM_RUNNING, { boxShadow: 'inset 0 0 0 1.5px color-mix(in srgb, var(--ev-accent) 60%, transparent)' }),
    // รอลองใหม่ (amber)
    box(gridCardShell + ' bg-amber-500/10 px-3', [
      stateBadge('bg-amber-500/90', 'hourglass_top', 'รอลองใหม่', 'text-white'),
      { el: 'icon', icon: 'hourglass_top', textSize: 'text-[28px]', className: 'text-amber-400 animate-pulse' },
      tx('{item.meta.error}', '!text-[10px] font-bold !text-amber-400 text-center leading-snug line-clamp-3'),
      // ตาม autoProduce ต้นฉบับ: "ลองใหม่ใน N วิ (ครั้งที่ X)" — countdown จาก __runCoolLeft/__runAttempt (global แต่ maxParallel=1 = คือใบนี้)
      { el: 'text', value: 'ลองใหม่ใน {values.__runCoolLeft} วิ (ครั้งที่ {values.__runAttempt})', className: '!text-[10px] !text-amber-300/80 font-medium', when: NEQ('{values.__runCoolLeft}', '0') },
      bottomBar,
    ], ITEM_RETRYING, { boxShadow: 'inset 0 0 0 1.5px rgba(245,158,11,0.5)' }),
    // ล้มเหลว (แดง + ปุ่มลองใหม่ตามขั้นที่ค้าง)
    box(gridCardShell + ' bg-red-500/10 gap-2 px-3', [
      stateBadge('bg-red-500/90', 'error', 'ล้มเหลว', 'text-white'),
      { el: 'icon', icon: 'error', textSize: 'text-[26px]', className: 'text-red-400' },
      tx('{item.meta.error}', '!text-[10px] font-bold !text-red-300 text-center leading-snug line-clamp-3'),
      { el: 'gen-button', op: 'hsContent', label: 'ลองเขียนบทใหม่', icon: 'replay', size: 'sm', when: 'item.h1=', className: '!text-[10px] !border-red-500/40 !text-red-300 !bg-red-500/[0.18]' },
      box('', [{ el: 'gen-button', op: 'hsImage', label: 'ลองสร้างภาพใหม่', icon: 'replay', size: 'sm', when: 'item.slots.image=', className: '!text-[10px] !border-red-500/40 !text-red-300 !bg-red-500/[0.18]' }], 'item.h1!='),
      box('', [box('', [{ el: 'gen-button', op: 'hsVideo1', label: 'ลองสร้างวีดีโอใหม่', icon: 'replay', size: 'sm', when: 'item.slots.video1=', className: '!text-[10px] !border-red-500/40 !text-red-300 !bg-red-500/[0.18]' }], 'item.slots.image!=')], 'item.h1!='),
      box('', [{ el: 'gen-button', op: 'hsVideo2', label: 'ลองต่อฉากใหม่', icon: 'replay', size: 'sm', when: 'item.clipLength=16', className: '!text-[10px] !border-red-500/40 !text-red-300 !bg-red-500/[0.18]' }], 'item.slots.video1!='),
      bottomBar,
    ], ITEM_ERROR, { boxShadow: 'inset 0 0 0 1.5px rgba(239,68,68,0.5)' }),
    // รอขั้นถัดไปตอนรัน (16 วิ: video1 เสร็จ status=done แต่ video2 ยังไม่เริ่ม — อย่าโชว์ "ไฟล์หาย" หลอกกลางคัน)
    box(gridCardShell + ' bg-[var(--ev-surface)]', [
      cardImageLayer,
      { el: 'icon', icon: 'hourglass_empty', textSize: 'text-[24px]', className: 'opacity-60 relative z-[1] animate-pulse' },
      tx('รอขั้นถัดไป...', '!text-[10px] opacity-60 font-medium relative z-[1]'),
      bottomBar,
    ], AND(ITEM_LEFTOVER, EQ('{item.status}', 'done'), ST_RUNNING), { boxShadow: 'inset 0 0 0 1px var(--ev-border)' }),
    // ไฟล์หาย (เคยเสร็จแต่สื่อหาย — design lock finalMissing) + Gen ใหม่ตามชิ้นที่ขาด — เฉพาะตอนไม่ได้รันอยู่
    box(gridCardShell + ' bg-[var(--ev-surface)] gap-2 px-3', [
      cardImageLayer,
      box('absolute top-2 left-2 z-[2] px-2 py-[3px] rounded-full bg-white/30 pointer-events-none', [tx('ไฟล์หาย', '!text-[9px] font-bold !text-white')]),
      { el: 'icon', icon: 'hide_image', textSize: 'text-[30px]', className: 'opacity-55 relative z-[1]' },
      tx('ภาพ/วีดีโอหาย — Gen ใหม่ได้เลย', '!text-[10px] opacity-55 font-medium text-center leading-snug relative z-[1]'),
      box('relative z-[1]', [{ el: 'gen-button', op: 'hsImage', label: 'Gen ภาพใหม่', icon: 'replay', size: 'sm', variant: 'outline', when: 'item.slots.image=' }]),
      box('relative z-[1]', [{ el: 'gen-button', op: 'hsVideo1', label: 'Gen วีดีโอใหม่', icon: 'replay', size: 'sm', variant: 'outline', when: 'item.slots.video1=' }], 'item.slots.image!='),
      box('relative z-[1]', [box('', [{ el: 'gen-button', op: 'hsVideo2', label: 'Gen ช่วง 2 ใหม่', icon: 'replay', size: 'sm', variant: 'outline', when: 'item.clipLength=16' }], 'item.slots.video2=')], 'item.slots.video1!='),
      bottomBar,
    ], AND(ITEM_LEFTOVER, EQ('{item.status}', 'done'), { op: 'not', a: ST_RUNNING }), { boxShadow: 'inset 0 0 0 1px var(--ev-border)' }),
    // ค้างกลางทาง (โดนหยุดไว้) — โชว์ภาพหรี่ + ขั้นที่ทำถึง (ตาม RunGrid ต้นฉบับ pending-partial)
    box(gridCardShell + ' bg-[var(--ev-surface)]', [
      cardImageLayer,
      { el: 'icon', icon: 'movie', textSize: 'text-[24px]', className: 'opacity-70 relative z-[1]', when: 'item.slots.video1!=' },
      { el: 'icon', icon: 'image', textSize: 'text-[24px]', className: 'opacity-70 relative z-[1]', when: 'item.slots.video1=' },
      tx('สร้างวีดีโอแล้ว', '!text-[10px] opacity-70 font-medium relative z-[1]', 'item.slots.video1!='),
      tx('สร้างภาพแล้ว', '!text-[10px] opacity-70 font-medium relative z-[1]', 'item.slots.video1='),
      bottomBar,
    ], AND(ITEM_LEFTOVER, NEQ('{item.status}', 'done'), NEQ('{item.slots.image}', '')), { boxShadow: 'inset 0 0 0 1px var(--ev-border)' }),
    // มีบทแล้ว (เทาจาง)
    box(gridCardShell + ' bg-[var(--ev-surface)]', [
      { el: 'icon', icon: 'description', textSize: 'text-[24px]', className: 'opacity-45' },
      tx('สร้างบทขายแล้ว', '!text-[10px] opacity-45 font-medium'),
      bottomBar,
    ], AND(ITEM_LEFTOVER, NEQ('{item.status}', 'done'), EQ('{item.slots.image}', ''), NEQ('{item.h1}', '')), { boxShadow: 'inset 0 0 0 1px var(--ev-border)' }),
    // รอคิว (ดำจาง)
    box(gridCardShell + ' opacity-50 bg-[var(--ev-surface)]', [
      { el: 'icon', icon: 'schedule', textSize: 'text-[24px]', className: 'opacity-40' },
      tx('รอคิว', '!text-[10px] opacity-50'),
      bottomBar,
    ], AND(ITEM_LEFTOVER, NEQ('{item.status}', 'done'), EQ('{item.slots.image}', ''), EQ('{item.h1}', '')), { boxShadow: 'inset 0 0 0 1px var(--ev-border)' }),
  ],
}], { op: 'not', a: EQ('{values.__view}', 'list') });   // คอลัมน์ตายตัว 4/5 ตาม RunGrid ต้นฉบับ (เดิม auto-fill ขนาดการ์ดไหลตามจอ)

// ═══ list view — แถวกดกางดู timeline ละเอียด (ตาม RunList ต้นฉบับ) ═══
const CUR = (op: string) => AND(ITEM_RUNNING, EQ('{values.__runStage}', op));
const stepChip = (label: string, doneWhen: any, actWhen: any) => box('shrink-0', [
  box('px-[7px] py-[2px] rounded-[7px] bg-green-500/15', [tx(label, '!text-[10px] font-semibold !text-green-400 whitespace-nowrap')], doneWhen),
  box('px-[7px] py-[2px] rounded-[7px] bg-[var(--ev-accent)]/[0.18]', [tx(label, '!text-[10px] font-semibold !text-[var(--ev-accent)] whitespace-nowrap')], AND({ op: 'not', a: doneWhen }, actWhen)),
  box('px-[7px] py-[2px] rounded-[7px] bg-white/5', [tx(label, '!text-[10px] font-semibold opacity-40 whitespace-nowrap')], AND({ op: 'not', a: doneWhen }, { op: 'not', a: actWhen })),
]);
const chipArrow = { el: 'icon', icon: 'arrow_right_alt', textSize: 'text-[15px]', className: 'opacity-25 shrink-0' };
// จุด timeline ในส่วนกาง: เขียว=เสร็จ · ส้ม pulse=กำลังทำ · ขอบจาง=รอ
const tlRow = (label: string, doneWhen: any, actWhen: any, extra?: any) => box('relative flex flex-row items-center gap-2.5 py-1 pl-5', [
  { el: 'box', className: 'absolute left-0 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full shrink-0', card: [], classWhen: [
    { when: doneWhen, class: 'bg-green-500' },
    { when: AND({ op: 'not', a: doneWhen }, actWhen), class: 'bg-[var(--ev-accent)] animate-pulse shadow-[0_0_0_3px_rgba(247,107,107,0.25)]' },
    { when: AND({ op: 'not', a: doneWhen }, { op: 'not', a: actWhen }), class: 'border-2 border-white/20' },
  ] },
  tx(label, '!text-[12px] opacity-70', doneWhen),
  { el: 'text', value: label, className: '!text-[12px] !text-[var(--ev-accent)] font-medium', when: AND({ op: 'not', a: doneWhen }, actWhen) },
  { el: 'text', value: label, className: '!text-[12px] opacity-40', when: AND({ op: 'not', a: doneWhen }, { op: 'not', a: actWhen }) },
  ...(extra ? [box('ml-auto', [extra])] : []),
]);
const runList = box('flex flex-col gap-2', [{
  el: 'repeat', coll: 'tasks',
  card: [{
    ...{ el: 'group', collapsible: true, className: '!rounded-2xl !p-0 !border-0 !gap-0 overflow-hidden bg-[var(--ev-surface)]' },
    head: [
      box('flex flex-row items-center gap-3 py-2.5 px-3 w-full min-w-0', [
        tx({ op: 'add', a: { op: 'index' }, b: 1 }, '!text-[15px] font-extrabold opacity-40 w-7 text-center shrink-0 tabular-nums'),
        // thumb: ตอนกำลังสร้าง = สปินเนอร์เล็ก (media-slot overlay ใหญ่เกิน 52px) · ปกติ = รูป
        box('w-[52px] shrink-0', [{ el: 'media-slot', src: '{item.slots.image}', aspect: '1:1', className: '!rounded-[10px]' }], { op: 'not', a: ITEM_RUNNING }),
        box('w-[52px] h-[52px] shrink-0 rounded-[10px] bg-black/30 border border-[var(--ev-border)] flex items-center justify-center', [{ el: 'spinner', className: '!text-[20px]' }], ITEM_RUNNING),
        box('flex-1 min-w-0', [
          row('items-center gap-1.5', [tx('{item.productName}', '!text-[14px] font-medium truncate !text-[var(--ev-text)]'), clipBadge]),
          box('flex flex-row items-center gap-1 mt-1.5 flex-wrap', [
            stepChip('บทขาย', NEQ('{item.h1}', ''), CUR('hsContent')), chipArrow,
            stepChip('ภาพเฟรมเริ่ม', NEQ('{item.slots.image}', ''), CUR('hsImage')), chipArrow,
            stepChip('วีดีโอ 8วิ', NEQ('{item.slots.video1}', ''), CUR('hsVideo1')),
            box('flex flex-row items-center gap-1', [chipArrow, stepChip('วีดีโอ 16วิ', NEQ('{item.slots.video2}', ''), CUR('hsVideo2'))], 'item.clipLength=16'),
          ]),
        ]),
        box('shrink-0 flex flex-row items-center gap-2', [
          box('flex flex-row items-center gap-1.5 whitespace-nowrap', [{ el: 'spinner', className: '!text-[17px]' }, { el: 'text', value: LK('opNames', '{values.__runStage}', 'กำลังทำ'), className: '!text-[12px] font-bold !text-[var(--ev-accent)] whitespace-nowrap' }], ITEM_RUNNING),
          box('flex flex-row items-center gap-1.5 whitespace-nowrap', [{ el: 'icon', icon: 'hourglass_top', textSize: 'text-[16px]', className: 'text-amber-400 animate-pulse' }, tx('{item.meta.error}', '!text-[11px] font-bold !text-amber-300 max-w-[180px] truncate')], ITEM_RETRYING),
          tx('{item.meta.error}', '!text-[11px] font-bold !text-red-400/80 max-w-[180px] truncate', ITEM_ERROR),
          tx('รอคิว', '!text-[12px] opacity-40', AND(EQ('{item.status}', 'idle'), EQ('{item.h1}', ''))),
          { el: 'download-button', to: 'video1', iconOnly: true, icon: 'download', label: 'ดาวน์โหลด', size: 'sm', variant: 'ghost', when: AND(EQ('{item.clipLength}', '8'), NEQ('{item.slots.video1}', '')) },
          { el: 'download-button', segments: [{ slot: 'video1', trimEndIfNext: 7 }, { slot: 'video2' }], iconOnly: true, icon: 'download', label: 'ดาวน์โหลด', size: 'sm', variant: 'ghost', when: AND(EQ('{item.clipLength}', '16'), NEQ('{item.slots.video2}', '')) },   // 16 วิ = merge เต็มคลิปก่อนโหลด (เดิมได้ครึ่งหลัง)
        ]),
      ]),
    ],
    card: [
      box('pl-[60px] pr-4 pb-3.5', [
        box('relative flex flex-col ml-[5px] pl-0', [
          box('absolute left-[5px] top-[10px] bottom-[10px] w-[2px] bg-white/10', []),
          tlRow('คิดบทขาย', NEQ('{item.h1}', ''), CUR('hsContent'),
            { el: 'text', value: '"{item.h1}"', className: '!text-[11px] opacity-45 italic truncate max-w-[260px]', when: 'item.h1!=' }),   // โชว์ h1 หลังเขียนบทเสร็จ (RunList ต้นฉบับ)
          tlRow('ภาพเฟรมเริ่ม', NEQ('{item.slots.image}', ''), CUR('hsImage')),
          tlRow('วีดีโอ ช่วง 1 · 0-8 วิ', NEQ('{item.slots.video1}', ''), CUR('hsVideo1'),
            { el: 'download-button', to: 'video1', label: 'โหลดช่วงนี้', size: 'sm', variant: 'ghost', when: NEQ('{item.slots.video1}', '') }),
          box('', [tlRow('ต่อฉาก ช่วง 2 · 8-16 วิ', NEQ('{item.slots.video2}', ''), CUR('hsVideo2'),
            { el: 'download-button', to: 'video2', label: 'โหลดช่วงนี้', size: 'sm', variant: 'ghost', when: NEQ('{item.slots.video2}', '') })], 'item.clipLength=16'),
          box('flex flex-row gap-2 mt-2 pl-5', [
            { el: 'open-editor', coll: 'tasks', only: true, label: 'ตัดต่อคลิปนี้', icon: 'movie_edit', size: 'sm', variant: 'outline-accent' },
            { el: 'gen-button', op: 'hsContent', label: 'เขียนบทใหม่', icon: 'edit_note', size: 'sm', variant: 'ghost' },
          ]),
        ]),
      ]),
    ],
    classWhen: [
      { when: OR(AND(EQ('{item.clipLength}', '8'), NEQ('{item.slots.video1}', '')), AND(EQ('{item.clipLength}', '16'), NEQ('{item.slots.video2}', ''))), class: '!bg-green-500/[0.06] shadow-[inset_0_0_0_1px_rgba(34,197,94,0.2)]' },
      { when: ITEM_RUNNING, class: '!bg-[var(--ev-accent)]/[0.08] shadow-[inset_0_0_0_1px_rgba(247,107,107,0.6)]' },
      { when: ITEM_RETRYING, class: '!bg-amber-500/[0.08] shadow-[inset_0_0_0_1px_rgba(245,158,11,0.4)]' },
      { when: ITEM_ERROR, class: '!bg-red-500/[0.07] shadow-[inset_0_0_0_1px_rgba(239,68,68,0.4)]' },
    ],
  }],
}], EQ('{values.__view}', 'list'));

const runHeader = box(WIZ_CARD.replace('!p-5', 'p-5') + ' border border-[var(--ev-border)] flex flex-col gap-3', [
  row('items-start justify-between gap-3', [
    box('flex flex-row items-center gap-3 min-w-0', [
      // จุดสถานะ + ping ตอนรัน · ตอนพักตามจังหวะ (cooldown) = นาฬิกาทรายพลิก (animate-hgflip) แทนจุด — ตาม RunScreen ต้นฉบับ
      box('relative flex h-2.5 w-2.5 shrink-0', [
        box('animate-ping absolute inline-flex h-full w-full rounded-full opacity-60 bg-[var(--ev-accent)]', [], OR(EQ('{values.__runState}', 'running'), EQ('{values.__runState}', 'retrying'))),
        { el: 'box', className: 'relative inline-flex rounded-full h-2.5 w-2.5', card: [], classWhen: [
          { when: ST_RUNNING, class: 'bg-[var(--ev-accent)]' },
          { when: AND(NOT_RUNNING, HAS_ERROR), class: 'bg-red-500' },
          { when: AND(NOT_RUNNING, NO_ERROR, ALL_DONE), class: 'bg-green-500' },
          { when: AND(NOT_RUNNING, NO_ERROR, NOT_ALL_DONE), class: 'bg-white/40' },
        ] },
      ], { op: 'not', a: EQ('{values.__runState}', 'cooldown') }),
      { el: 'icon', icon: 'hourglass_top', textSize: 'text-[18px]', className: 'text-[var(--ev-accent)] animate-hgflip shrink-0', when: EQ('{values.__runState}', 'cooldown') },
      box('min-w-0', [
        tx('กำลังผลิตคลิป', 'font-bold !text-[16px] leading-tight !text-[var(--ev-text)]', OR(EQ('{values.__runState}', 'running'), EQ('{values.__runState}', 'retrying'))),
        { el: 'text', value: CONCAT('พักตามจังหวะ — อีก ', '{values.__runCoolLeft}', ' วิ'), className: 'font-bold !text-[16px] leading-tight !text-[var(--ev-text)]', when: EQ('{values.__runState}', 'cooldown') },
        tx('หยุดผลิต — มีคลิปล้มเหลว', 'font-bold !text-[16px] leading-tight !text-[var(--ev-text)]', AND(NOT_RUNNING, HAS_ERROR)),
        tx('ผลิตเสร็จแล้ว', 'font-bold !text-[16px] leading-tight !text-[var(--ev-text)]', AND(NOT_RUNNING, NO_ERROR, ALL_DONE)),
        tx('หยุดชั่วคราว', 'font-bold !text-[16px] leading-tight !text-[var(--ev-text)]', AND(NOT_RUNNING, NO_ERROR, NOT_ALL_DONE)),
        box('flex flex-row items-center gap-3 flex-wrap mt-0.5', [
          { el: 'text', value: CONCAT(ENABLED_PRODUCTS, ' สินค้า'), icon: 'shopping_cart', className: '!text-[12px] opacity-50' },
          tx('{values.clipsPerProduct} คลิป/สินค้า', '!text-[12px] opacity-50', undefined, 'content_copy'),
          tx('ความยาว {values.clipLength} วิ', '!text-[12px] opacity-50', undefined, 'timer'),
        ]),
      ]),
    ]),
    box('shrink-0 flex flex-col items-end gap-0.5', [
      { el: 'text', value: CONCAT('เริ่มเมื่อ ', { op: 'clock', value: '{values.__runStartedAt}' }), className: '!text-[11.5px] opacity-50', when: AND(ST_RUNNING, NEQ('{values.__runStartedAt}', '')) },   // นาฬิกาเริ่มรอบ ตาม RunScreen ต้นฉบับ
      { el: 'timer', value: '{values.__runStartedAt}', label: 'ผ่านไป', icon: 'schedule', className: '!text-[11.5px] opacity-70', when: ST_RUNNING },
      box('flex flex-row items-center gap-2', [
        // ตัดต่อจาก header = เปิดโปรแกรมตัดต่อเปล่า (ต้นฉบับไม่ pre-load — ใช้ control ที่ไม่มีสื่อเป็น source ว่าง)
        { el: 'open-editor', coll: 'control', label: 'ตัดต่อคลิป', icon: 'movie_edit', size: 'sm', variant: 'outline-accent', className: 'font-bold' },
        { el: 'zip-export', label: 'ดาวน์โหลดทั้งหมด', icon: 'download', size: 'sm', variant: 'contrast', className: 'font-bold',
          coll: 'tasks', where: 'status=done', mediaSlots: ['video1', 'video2'], prefix: 'clip', assetsFolder: 'assets',   // กรองเฉพาะงานเสร็จตาม downloadAll ต้นฉบับ (กันคลิปพัง/ครึ่งทางปน zip)
          header: [{ label: 'แอป', value: 'หมีแว่น ขายดุ' }],
          line: '{index}. {item.productName} · คลิป {item.clipIndex} ({item.clipLength} วิ) · H1: {item.h1} · H2: {item.h2} · พูด: {item.speech} {item.speech2} · CTA: {item.cta}' },
      ], AND(NOT_RUNNING, NO_ERROR, ALL_DONE)),
    ]),
  ]),
  row('items-center gap-4', [
    { el: 'progress-bar', value: { op: 'mul', a: { op: 'div', a: COUNT_DONE, b: COUNT_TASKS }, b: 100 }, className: 'flex-1 !h-2' },
    row('items-baseline gap-1 shrink-0', [
      tx(COUNT_DONE, '!text-[26px] font-black leading-none tabular-nums !text-[var(--ev-text)]'),
      { el: 'text', value: CONCAT('/ ', COUNT_TASKS, ' คลิป'), className: '!text-[13px] opacity-40 font-medium' },
    ]),
  ]),
  box('flex flex-row flex-wrap items-center gap-2', [
    chipCount('bg-green-500/[0.12]', 'bg-green-400', '!text-green-400', 'เสร็จ', COUNT_DONE),
    chipCount('bg-[var(--ev-accent)]/[0.12]', 'bg-[var(--ev-accent)]', '!text-[var(--ev-accent)]', 'กำลังทำ', COUNT_RUNNING),
    chipCount('bg-red-500/[0.14]', 'bg-red-400', '!text-red-300', 'ล้มเหลว', COUNT_ERROR, HAS_ERROR),
    chipCount('bg-white/5', 'bg-white/30', 'opacity-45', 'รอคิว', { op: 'sub', a: { op: 'sub', a: { op: 'sub', a: COUNT_TASKS, b: COUNT_DONE }, b: COUNT_RUNNING }, b: COUNT_ERROR }),
    box('ml-auto shrink-0', [
      { el: 'segmented', field: '__view', labelClass: 'hidden', options: [
        { value: 'list', label: 'มุมมองรายการ', icon: 'view_list' },
        { value: 'grid', label: 'มุมมองตาราง', icon: 'grid_view' },
      ]},
    ]),
  ]),
]);
const rightWork = box('p-5 flex flex-col gap-4', [runHeader, runGrid, runList], HAS_TASKS);

// ═══════════ หน้าจัดการคลัง (สลับด้วย values.__page) ═══════════
const managerHeader = (title: string, loadEl: any, saveEl: any) => row('items-center gap-2.5 mb-5', [
  { el: 'button', action: 'set', to: '__page', value: '', iconOnly: true, label: 'กลับหน้าหลัก', icon: 'arrow_back', className: '!w-9 !h-9 !p-0 !rounded-xl' },
  tx(title, 'font-black !text-[16px] !text-[var(--ev-text)]'),
  box('flex flex-row items-center gap-1 !text-amber-400', [
    { el: 'icon', icon: 'lock', textSize: 'text-[14px]', className: 'text-amber-400' },
    tx('กำลังผลิต — แก้ไขไม่ได้', '!text-[11px] !text-amber-400'),
  ], ST_RUNNING),
  box('ml-auto flex flex-row items-center gap-2', [loadEl, saveEl]),
]);
// การ์ดสถิติแนวนอนตามต้นฉบับ (icon-box 12x12 ซ้าย + เลขใหญ่ 28px + label uppercase) — atom stat-card เป็นแนวตั้งเลขเล็ก ไม่ตรงสไตล์
const statBox = (icon: string, iconCls: string, label: string, v: any) => box('bg-[var(--ev-surface)] border border-[#595959] rounded-[24px] p-4 flex flex-row items-center gap-3.5', [
  box('w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ' + iconCls, [{ el: 'icon', icon, textSize: 'text-[22px]' }]),
  box('min-w-0', [
    { el: 'text', value: v, className: '!text-[28px] font-black leading-none !text-[var(--ev-text)]' },
    tx(label, '!text-[10px] uppercase tracking-wide opacity-45 mt-1'),
  ]),
]);
const statPair = (icon1: string, label1: string, v1: any, label2: string, v2: any) => box('grid grid-cols-2 gap-4 mb-5', [
  statBox(icon1, 'bg-white/5', label1, v1),   // ต้นฉบับ: ใบซ้าย (ทั้งหมด) icon-box เทากลาง · ใบขวา (เลือกใช้) accent
  statBox('check_circle', 'bg-[var(--ev-accent)]/[0.12] text-[var(--ev-accent)]', label2, v2),
]);

// วงกลมติ๊ก "ใช้" (circle check ตามต้นฉบับ — ปุ่ม hook ปิดเองตอนกำลังผลิต = ล็อกตามต้นฉบับ)
const useCheck = (cls = '!w-6 !h-6 !p-0 !rounded-full shrink-0') => ({
  el: 'button', action: 'hook', fn: 'hsToggleEnabled', iconOnly: true, icon: 'check', label: 'ใช้',
  className: cls,
  classWhen: [
    { when: 'item.enabled=true', class: '!bg-[var(--ev-accent)] !text-white !border-transparent' },
    { when: 'item.enabled!=true', class: '!bg-transparent !text-transparent !border-2 !border-[var(--ev-border)]' },
  ],
});

// แถวคลังสินค้า (ตามต้นฉบับ ProductManager: check วงกลม · รูป · ชื่อ+คำอธิบาย · ราคา/โปร · ดินสอไปหน้าแก้ไข · ถังขยะ)
const productManagerRow = {
  el: 'repeat', coll: 'products', where: 'name,description~{values.__q}', empty: 'ยังไม่มีสินค้า — กดเพิ่มสินค้า หรือโหลดลิสต์เดิม',   // ค้นชื่อ+คำอธิบายตามต้นฉบับ (where LHS หลาย field = OR)
  card: [{
    ...box('bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-2xl p-3 pr-4 flex flex-row items-center gap-3.5', [
      useCheck(),
      { el: 'media-slot', src: '{item.slots.image}', aspect: '1:1', className: '!w-[54px] shrink-0 !rounded-xl' },
      box('flex-1 min-w-0', [
        row('items-center gap-1.5', [
          tx('{item.name}', 'font-bold !text-[14px] truncate !text-[var(--ev-text)]'),
          { el: 'icon', icon: 'warning', textSize: 'text-[14px]', className: 'text-amber-400', when: 'item.slots.image=' },
        ]),
        tx('{item.description}', '!text-[12px] opacity-40 truncate mt-0.5', 'item.description!='),
        tx('—', '!text-[12px] opacity-30 mt-0.5', 'item.description='),
      ]),
      box('text-right shrink-0 mr-1', [
        tx('{item.price}', 'font-bold !text-[14px] tabular-nums !text-[var(--ev-text)]', 'item.price!='),
        box('!text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-[var(--ev-accent)]/[0.14] inline-block mt-0.5', [tx('{item.promotion}', '!text-[10px] font-bold !text-[var(--ev-accent)]')], 'item.promotion!='),
      ]),
      { el: 'button', action: 'hook', fn: 'hsOpenEdit', to: 'productEdit', iconOnly: true, icon: 'edit', label: 'แก้ไข', variant: 'ghost', className: '!w-[34px] !h-[34px] !p-0 !rounded-[10px] shrink-0' },
      { el: 'delete-button', iconOnly: true, label: 'ลบ', size: 'sm', className: '!w-[34px] !h-[34px] !p-0 !rounded-[10px] shrink-0', disabledWhen: ANY_GEN, reason: 'กำลังผลิตอยู่ — ลบไม่ได้ (คลิปอ้างอิงตัวนี้อยู่)' },
    ]),
    classWhen: [{ when: 'item.enabled!=true', class: 'opacity-45' }],
  }],
};

// ═══ หน้า เพิ่ม/แก้ไข สินค้า·ตัวละคร (pattern ProductEditor/CharacterEditor ต้นฉบับ — หน้าเต็มแยก ไม่ใช่ fold) ═══
const edLbl = (t: string) => tx(t, '!text-[10px] opacity-40 uppercase tracking-widest font-black px-1 mb-1.5');
const editHead = (addTitle: string, editTitle: string, backTo: string, coll: string, useLabel: string) => row('items-center justify-between mb-5', [
  row('items-center gap-2 min-w-0', [
    { el: 'button', action: 'hook', fn: 'hsCancelEdit', to: backTo, coll, iconOnly: true, icon: 'arrow_back', label: 'ย้อนกลับ', variant: 'ghost', className: '!w-9 !h-9 !p-0 shrink-0' },
    tx(addTitle, 'font-bold !text-[15px] !text-[var(--ev-text)]', 'values.__editNew=true'),
    tx(editTitle, 'font-bold !text-[15px] !text-[var(--ev-text)]', 'values.__editNew!=true'),
  ]),
  box('bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-xl px-3 py-2 flex flex-row items-center gap-2 shrink-0', [
    useCheck('!w-[22px] !h-[22px] !p-0 !rounded-[7px] shrink-0'),
    tx(useLabel, '!text-[13px] !text-[var(--ev-text)] whitespace-nowrap'),
  ]),
]);
// กล่องรูป reference: ไม่มีรูป = [อัพโหลด | เลือกภาพจากคลัง Flow] + เตือน · มีรูป = ตัวอย่าง + ASSET ACTIVE + ปุ่มเปลี่ยน/ลบ
const refImageBox = (headLabel: string, warnTitle: string, warnSub: string) => box('bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-2xl p-5 flex flex-col gap-3', [
  edLbl(headLabel),
  row('gap-6 items-stretch', [
    box('w-[140px] aspect-square shrink-0 rounded-2xl border-2 border-dashed border-[var(--ev-border)] bg-black/40 flex flex-col gap-2 p-2', [
      { el: 'upload', label: '', placeholder: 'อัพโหลด', icon: 'upload', into: 'image', resize: { maxPx: 400, quality: 0.7 },
        className: 'flex-1 w-full justify-center !rounded-xl !bg-[var(--ev-text)] !text-[var(--ev-bg)] !border-0 font-black !text-[11px] uppercase' },
      { el: 'pick-button', label: 'เลือกภาพ', icon: 'photo_library', filter: 'image', into: 'image', resize: { maxPx: 400, quality: 0.7 },
        className: 'flex-1 w-full justify-center !rounded-xl !bg-white/10 !text-[var(--ev-text)] !border-0 font-black !text-[11px] uppercase !h-auto' },
    ]),
    box('flex-1 flex flex-row items-center gap-3 p-4 rounded-2xl bg-amber-500/5 border border-amber-500/20', [
      { el: 'icon', icon: 'warning', textSize: 'text-[22px]', className: 'text-amber-400 shrink-0' },
      box('flex flex-col min-w-0', [
        tx(warnTitle, '!text-[11px] font-black !text-amber-400 uppercase tracking-widest'),
        tx(warnSub, '!text-[10px] mt-0.5 !text-[var(--ev-accent)]'),
      ]),
    ]),
  ], 'item.slots.image='),
  // มีรูปแล้ว (ตาม ProductEditor ต้นฉบับ): thumb = ตัวลบเอง (hover ขึ้น X · คลิกลบ กลับไปหน้าปุ่มอัพโหลด) · กล่องเขียวไม่มีปุ่ม — แค่ชื่อไฟล์ + แถว SOURCE
  row('gap-6 items-stretch', [
    box('w-[140px] shrink-0 relative group rounded-2xl overflow-hidden cursor-pointer', [
      { el: 'media-slot', src: '{item.slots.image}', aspect: '1:1', className: '!rounded-2xl' },
      { el: 'button', action: 'hook', fn: 'clearSlot', to: 'image', iconOnly: true, icon: 'close', label: 'ลบรูป',
        className: '!absolute !inset-0 !w-full !h-full !p-0 !rounded-2xl !border-0 !bg-black/60 !text-white opacity-0 group-hover:opacity-100 transition-opacity justify-center' },
    ]),
    box('flex-1 flex flex-col justify-center gap-3 p-4 rounded-2xl bg-green-500/5 border border-green-500/20', [
      row('items-center gap-3', [
        { el: 'icon', icon: 'check_circle', textSize: 'text-[22px]', className: 'text-green-400 shrink-0' },
        box('flex flex-col min-w-0', [
          tx('ASSET ACTIVE', '!text-[11px] font-black !text-green-400 uppercase tracking-widest'),
          tx('{item.imageName}', '!text-[10px] opacity-40 truncate', 'item.imageName!='),
          tx('จากคลัง Flow', '!text-[10px] opacity-40', 'item.imageName='),
        ]),
      ]),
      box('h-px bg-white/5 w-full', []),
      row('items-center justify-between', [
        tx('SOURCE', '!text-[9px] opacity-20 font-black uppercase tracking-widest'),
        tx('อัพโหลด · ฝัง base64', '!text-[9px] opacity-40', 'item.imageName!='),
        tx('คลัง Flow · ฝัง base64', '!text-[9px] opacity-40', 'item.imageName='),
      ]),
    ]),
  ], 'item.slots.image!='),
]);
const editFooter = (backTo: string, coll: string, saveLabel: string, saveGate?: any) => row('gap-3 pt-2', [
  { el: 'button', action: 'hook', fn: 'hsCancelEdit', to: backTo, coll, label: 'ยกเลิก', className: 'flex-1 justify-center !h-12 !rounded-xl !text-[14px]' },
  { el: 'button', action: 'hook', fn: 'hsCloseEdit', to: backTo, label: saveLabel, variant: 'solid', className: 'flex-[2] justify-center !h-12 !rounded-xl !text-[14px] font-bold', ...(saveGate ? { disabledWhen: saveGate, reason: 'กรอกชื่อก่อนบันทึก' } : {}) },
]);
const productEditPage = box('max-w-[680px] mx-auto p-6 w-full', [{
  el: 'repeat', coll: 'products', where: 'id={values.__editId}',
  card: [box('bg-[var(--ev-surface)] border border-[#595959] rounded-[24px] p-6 flex flex-col gap-4', [
    editHead('เพิ่มสินค้า', 'แก้ไขสินค้า', 'products', 'products', 'ใช้สินค้านี้'),
    refImageBox('รูปสินค้า * (ใช้เป็น REFERENCE — ระบบล็อกหน้าตาสินค้าตามรูปนี้)', 'ต้องเพิ่มรูปสินค้า', 'อัพโหลด หรือ เลือกจากคลัง Flow เพื่อใช้เป็น reference'),
    box('grid grid-cols-3 gap-3', [
      box('col-span-2', [edLbl('ชื่อสินค้า *'), { el: 'input', field: 'name', placeholder: 'เช่น เซรั่มหน้าใส วิตามินซี', className: '!h-[44px] !px-4 !rounded-xl' }]),
      box('', [edLbl('ราคา (ไม่บังคับ)'), { el: 'input', field: 'price', placeholder: '฿390', className: '!h-[44px] !px-4 !rounded-xl' }]),
    ]),
    box('', [edLbl('คำอธิบาย / จุดขาย'), { el: 'textarea', field: 'description', placeholder: 'จุดเด่นของสินค้า ยิ่งละเอียด AI ยิ่งเขียนบทขายได้ตรง', className: '!min-h-[96px] !p-4 !rounded-xl' }]),
    { el: 'group', collapsible: true, className: '!rounded-2xl bg-[var(--ev-surface)]',
      head: [
        { el: 'icon', icon: 'local_offer', textSize: 'text-[18px]', className: 'opacity-40' },
        tx('โปรโมชั่น + CTA', '!text-[13px] font-bold !text-[var(--ev-text)]'),
        tx('(ไม่บังคับ)', '!text-[13px] opacity-30'),
      ],
      card: [box('grid grid-cols-2 gap-3', [
        box('', [edLbl('โปรโมชั่น'), { el: 'input', field: 'promotion', placeholder: 'ลด 50% วันนี้เท่านั้น', className: '!h-[40px] !px-3 !rounded-lg' }]),
        box('', [edLbl('CTA (≤30 ตัว)'), { el: 'input', field: 'cta', maxLength: 30, placeholder: 'กดสั่งซื้อเลย', className: '!h-[40px] !px-3 !rounded-lg' }]),
      ])] },
    editFooter('products', 'products', 'บันทึกสินค้า', EQ('{item.name}', '')),
  ])],
}], EQ('{values.__page}', 'productEdit'));
const characterEditPage = box('max-w-[680px] mx-auto p-6 w-full', [{
  el: 'repeat', coll: 'characters', where: 'id={values.__editId}',
  card: [box('bg-[var(--ev-surface)] border border-[#595959] rounded-[24px] p-6 flex flex-col gap-4', [
    editHead('เพิ่มตัวละคร', 'แก้ไขตัวละคร', 'characters', 'characters', 'ใช้ตัวละครนี้'),
    refImageBox('รูปตัวละคร * (reference ใบหน้าคนรีวิว — ระบบล็อกหน้าตามรูปนี้)', 'ต้องเพิ่มรูปตัวละคร', 'อัพโหลด หรือ เลือกจากคลัง Flow เพื่อใช้เป็น reference คนรีวิว'),
    box('', [edLbl('ชื่อเรียก (ไม่บังคับ)'), { el: 'input', field: 'name', placeholder: 'เช่น พี่หมวย, น้องบีม', className: '!h-[44px] !px-4 !rounded-xl' }]),
    box('grid grid-cols-2 gap-3', [
      box('', [edLbl('เพศ (คุมคำลงท้าย ค่ะ/ครับ + เสียงพากย์)'), { el: 'segmented', field: 'gender', variant: 'tab', options: [
        { value: 'female', label: 'หญิง' }, { value: 'male', label: 'ชาย' },
      ]}]),
      box('', [edLbl('ช่วงอายุ (คร่าวๆ)'), { el: 'dropdown', field: 'ageRange', options: AGE_OPTS }]),
    ]),
    editFooter('characters', 'characters', 'บันทึกตัวละคร'),
  ])],
}], EQ('{values.__page}', 'characterEdit'));
const productsPage = box('max-w-[1080px] mx-auto p-6 w-full', [
  managerHeader('จัดการสินค้า',
    { el: 'load-button', expect: 'products', mode: 'replace', label: 'โหลดสินค้า', icon: 'upload_file' },
    { el: 'save-button', scope: 'products', label: 'เซฟสินค้า', icon: 'save', variant: 'outline' }),
  statPair('inventory_2', 'สินค้าทั้งหมด', { op: 'count', from: 'products' }, 'เลือกใช้', ENABLED_PRODUCTS),
  box(WIZ_CARD + ' border border-[var(--ev-border)] flex flex-col gap-3', [
    row('items-center gap-2 flex-wrap', [
      box('bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-xl px-3 h-[42px] flex flex-row items-center gap-2 flex-1 min-w-[180px] max-w-[320px]', [
        { el: 'icon', icon: 'search', textSize: 'text-[20px]', className: 'opacity-30' },
        { el: 'input', field: '__q', variant: 'bare', placeholder: 'ค้นหาสินค้า...' },
      ]),
      box('ml-auto flex flex-row items-center gap-2', [
        { el: 'button', action: 'hook', fn: 'hsToggleAll', coll: 'products', value: 'true', label: 'ใช้ทั้งหมด', icon: 'done_all', size: 'sm' },
        { el: 'button', action: 'hook', fn: 'hsToggleAll', coll: 'products', value: '', label: 'ปิดทั้งหมด', icon: 'close', size: 'sm' },
        { el: 'button', action: 'hook', fn: 'hsAddItem', coll: 'products', to: 'productEdit', addDefaults: { name: '', enabled: 'true' }, label: 'เพิ่มสินค้า', icon: 'add', variant: 'solid' },
      ]),
    ]),
    tx('ติ๊ก "ใช้" = สินค้าที่จะเอาไปปั่นคลิป · ปิด = ข้ามตัวนี้ · สินค้าต้องมีรูปจึงจะเข้าคิวผลิต', '!text-[11px] opacity-40 px-1', undefined, 'info'),
    { el: 'text', value: CONCAT('แสดง ', { op: 'count', from: 'products', where: 'name,description~{values.__q}' }, ' จาก ', { op: 'count', from: 'products' }, ' รายการ'), className: '!text-[11px] opacity-35 px-1' },   // "แสดง N จาก M" ตาม ProductManager ต้นฉบับ
    productManagerRow,
    { el: 'button', action: 'hook', fn: 'hsAddItem', coll: 'products', to: 'productEdit', addDefaults: { name: '', enabled: 'true' }, label: 'เพิ่มสินค้าใหม่', icon: 'add', className: 'w-full justify-center !h-auto py-4 !border-dashed opacity-60 hover:opacity-100' },
  ]),
], EQ('{values.__page}', 'products'));

const charManagerRow = {
  el: 'repeat', coll: 'characters', empty: 'ยังไม่มีตัวละคร — กดเพิ่มตัวละคร หรือโหลดลิสต์เดิม',
  card: [{
    ...box('bg-[var(--ev-surface)] border border-[var(--ev-border)] rounded-2xl p-3 pr-4 flex flex-row items-center gap-3.5', [
      useCheck(),
      { el: 'media-slot', src: '{item.slots.image}', aspect: '1:1', className: '!w-[64px] shrink-0 !rounded-xl' },
      box('flex-1 min-w-0', [
        tx('{item.name}', 'font-bold !text-[14px] truncate !text-[var(--ev-text)]'),
        { el: 'text', value: CONCAT(LK('genderTh', '{item.gender}', '{item.gender}'), ' · {item.ageRange}'), className: '!text-[12px] opacity-40 mt-0.5' },
      ]),
      { el: 'button', action: 'hook', fn: 'hsOpenEdit', to: 'characterEdit', iconOnly: true, icon: 'edit', label: 'แก้ไข', variant: 'ghost', className: '!w-[34px] !h-[34px] !p-0 !rounded-[10px] shrink-0' },
      { el: 'delete-button', iconOnly: true, label: 'ลบ', size: 'sm', className: '!w-[34px] !h-[34px] !p-0 !rounded-[10px] shrink-0', disabledWhen: ANY_GEN, reason: 'กำลังผลิตอยู่ — ลบไม่ได้ (คลิปอ้างอิงตัวนี้อยู่)' },
    ]),
    classWhen: [{ when: 'item.enabled!=true', class: 'opacity-45' }],
  }],
};
const charactersPage = box('max-w-[1080px] mx-auto p-6 w-full', [
  managerHeader('จัดการตัวละคร',
    { el: 'load-button', expect: 'characters', mode: 'replace', label: 'โหลดตัวละคร', icon: 'upload_file' },
    { el: 'save-button', scope: 'characters', label: 'เซฟตัวละคร', icon: 'save', variant: 'outline' }),
  statPair('groups', 'ตัวละครทั้งหมด', { op: 'count', from: 'characters' }, 'เลือกใช้ (สุ่มจาก)', ENABLED_CHARS),
  box('rounded-2xl mb-5 flex flex-row items-center gap-3.5 p-4 bg-[var(--ev-accent)]/[0.08] border border-[var(--ev-accent)]/25', [
    { el: 'icon', icon: 'casino', textSize: 'text-[34px]', className: 'text-[var(--ev-accent)] shrink-0' },
    box('min-w-0', [
      tx('AI สุ่มตัวละครให้เอง', 'font-bold !text-[14px] !text-[var(--ev-text)]'),
      tx('ยังไม่ได้เลือกตัวละคร — แต่ละคลิป AI จะสุ่มสร้างคนรีวิวให้เข้ากับสินค้า · ติ๊กใช้ตัวละครในลิสต์เพื่อล็อกคนรีวิว', '!text-[11px] opacity-50 mt-0.5'),
    ]),
  ], EQ(ENABLED_CHARS, 0)),
  box(WIZ_CARD + ' border border-[var(--ev-border)] flex flex-col gap-3', [
    row('items-center gap-2 flex-wrap', [
      tx('รายการตัวละคร (คนรีวิว)', 'font-bold !text-[15px] !text-[var(--ev-text)]'),
      box('ml-auto flex flex-row items-center gap-2', [
        { el: 'button', action: 'hook', fn: 'hsToggleAll', coll: 'characters', value: 'true', label: 'ใช้ทั้งหมด', icon: 'done_all', size: 'sm' },
        { el: 'button', action: 'hook', fn: 'hsToggleAll', coll: 'characters', value: '', label: 'ปิดทั้งหมด', icon: 'close', size: 'sm' },
        { el: 'button', action: 'hook', fn: 'hsAddItem', coll: 'characters', to: 'characterEdit', addDefaults: { name: '', gender: 'female', ageRange: 'วัยทำงาน (25-35)', enabled: 'true' }, label: 'เพิ่มตัวละคร', icon: 'person_add', variant: 'solid' },
      ]),
    ]),
    box('grid grid-cols-1 sm:grid-cols-2 gap-3', [charManagerRow]),   // ต้นฉบับ CharacterManager = grid 2 คอลัมน์
    { el: 'button', action: 'hook', fn: 'hsAddItem', coll: 'characters', to: 'characterEdit', addDefaults: { name: '', gender: 'female', ageRange: 'วัยทำงาน (25-35)', enabled: 'true' }, label: 'เพิ่มตัวละคร', icon: 'person_add', className: 'w-full justify-center !h-auto py-4 !border-dashed opacity-60 hover:opacity-100' },
  ]),
], EQ('{values.__page}', 'characters'));

// ═══════════ โครงหน้าเดียว 2 คอลัมน์ ═══════════
const wizardWrap = box('flex flex-col gap-3.5', wizardForm, NO_TASKS);
const logPanel = { el: 'custom', fn: 'hsLog', when: HAS_TASKS };
const mainLayout = box('flex flex-col min-[960px]:flex-row min-[960px]:h-[calc(100vh-70px)] w-full', [
  box('flex flex-col min-h-0 w-full min-[960px]:w-[460px] min-[960px]:shrink-0 min-[960px]:border-r border-[var(--ev-border)]', [
    box('flex-1 min-h-0 min-[960px]:overflow-y-auto p-4 flex flex-col gap-3.5', [wizardWrap, summaryCard, logPanel]),
    controlFooter,
  ]),
  box('flex-1 min-h-0 min-[960px]:overflow-y-auto', [rightIdle, rightWork]),
], EQ('{values.__page}', ''));

const config = {
  schemaVersion: 1,
  title: 'หมีแว่น ขายดุ',
  icon: 'pets',
  app: { id: 'hardsell' },
  persistBar: true,
  devBar: false,
  theme: { ...film.theme, vars: { ...film.theme.vars, '--ev-accent': '#f76b6b', '--ev-accent-fg': '#ffffff' } },
  style: film.style || undefined,
  breakpoints: film.breakpoints || undefined,
  chrome: { content: { className: '!max-w-none !p-0' }, resume: { defaultAuto: false, restartFn: 'hsResetRun', restartLabel: 'ล้างคิว เริ่มใหม่' } },   // full-bleed 2 คอลัมน์ · modal งานค้าง: ไม่ pre-select + มีปุ่มล้างคิว (3 ทางเลือกตาม ResumeModal ต้นฉบับ)
  content: { item: { coll: 'tasks', label: 'คลิป' }, assets: ['products', 'characters'] },
  lookups: LOOKUPS,
  components: { runBanner: RUN_BANNER },
  home: {
    title: 'หมีแว่น ขายดุ', tag: 'EasyBear Hardsell',
    description: 'ใส่สินค้าเข้าลิสต์ แล้วปล่อยให้หมีปั่นคลิปรีวิวขายดุให้ทีละหลายคลิป',   // คำโปรยตรง LandingScreen ต้นฉบับ
    cta: 'สร้างโปรเจกต์ใหม่', ctaContrast: true, loadLabel: 'โหลดโปรเจกต์เดิม',
    footer: film.home?.footer || [],
  },
  values: {
    templateId: 'ugc-review', toneId: 'hardsell', textMode: 'overlay', textStyleId: 'golden-triangle',
    clipLength: '8', clipsPerProduct: '1', styleCat: 'ugc',
    imageModel: DEF_IMG, videoModel: DEF_VID,
    blocklistEnabled: 'true', blocklist: HS_BLOCKED_DEFAULT.join(','),
    maxParallel: '1', staggerMs: '3000', maxAttempts: '3', batchDelay: '10', retryDelay: '8',   // retryDelay 8 = ตาม projectStore ต้นฉบับ
    __page: '', __view: 'grid', __q: '', __editId: '', __editNew: '',
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
    // pace:false = string-builder ล้วนไม่ยิง API — ไม่ต้องพักระหว่างชุด (hsContent เป็น transform แต่เรียก LLM = ต้อง pace ปกติ)
    { id: 'hsQueue', type: 'transform', over: 'control', out: 'queued', fn: 'hsBuildTasks', pace: false },
    { id: 'hsContent', type: 'transform', over: 'tasks', out: 'written', fn: 'hsArchitectClip' },
    // where guard ทุก op หลัง hsContent: task ที่เขียนบทพัง (h1 ว่าง) ต้องไม่ไหลไปขั้นถัดไป
    // (กัน transform ทับ error เป็น done + กันเปลืองเควตา gen จาก prompt ขยะ — ต้นฉบับ abort ทั้งรอบ เราใช้ item-level gate แทน)
    { id: 'hsPrompts', type: 'transform', over: 'tasks', out: 'prompted', fn: 'hsBuildPrompts', where: 'h1!=', pace: false },
    {
      id: 'hsImage', type: 'image', over: 'tasks', out: 'image', where: 'imagePrompt!=',
      model: '{values.imageModel}', aspectRatio: '9:16', prompt: '{item.imagePrompt}',
      refs: { op: 'lookupRefs', from: 'products', by: '{item.refs.product}', slot: 'image', also: [{ from: 'characters', by: '{item.refs.char}', slot: 'image' }] },
    },
    {
      id: 'hsVideo1', type: 'video', over: 'tasks', out: 'video1', where: 'videoPrompt1!=',
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
  // ตัดต่อ: task 1 ใบ = คลิป 1 ตัว (16 วิ = 2 ช่วง fan-out + trim รอยต่อ 8-TAIL_TRIM=7 ตาม editorBridge ต้นฉบับ)
  editor: {
    sourceColl: 'tasks', defaultAspect: '9:16', defaultDuration: 8,
    map: { title: 'productName', segments: [{ slot: 'video1', trimEndIfNext: 7 }, { slot: 'video2' }] },
  },
  settings: {
    title: 'Settings', fullPage: true,   // ต้นฉบับ SettingsPage = หน้าเต็มแยก + หัวข้อ "Settings" (อังกฤษ)
    form: [box('bg-[var(--ev-surface)] border border-[#595959] rounded-[24px] p-5 flex flex-col gap-3', [   // ต้นฉบับห่อฟอร์มในการ์ด + แถวหัว icon "ตั้งค่าการผลิต"
      row('items-center gap-3 mb-1', [
        box('w-10 h-10 rounded-xl bg-[var(--ev-accent)]/15 text-[var(--ev-accent)] flex items-center justify-center shrink-0', [{ el: 'icon', icon: 'tune', textSize: 'text-[20px]' }]),
        box('min-w-0', [
          tx('ตั้งค่าการผลิต', 'font-bold !text-[15px] !text-[var(--ev-text)]'),
          tx('โมเดล AI · จังหวะการหน่วง · กรองคำต้องห้าม', '!text-[11px] opacity-40'),
        ]),
      ]),
      { el: 'dropdown', field: 'imageModel', label: 'โมเดลภาพ', options: IMAGE_MODELS },
      { el: 'dropdown', field: 'videoModel', label: 'โมเดลวิดีโอ', options: VIDEO_MODELS },
      { el: 'stepper', field: 'maxParallel', label: 'ผลิตพร้อมกันสูงสุด', placeholder: '1 = ทีละคลิป เสถียรสุด', icon: 'layers', unit: 'งาน', min: 1, max: 4 },
      { el: 'stepper', field: 'staggerMs', label: 'พักระหว่างงาน', placeholder: 'เหลื่อมเวลาปล่อยงานขนาน', icon: 'bolt', unit: 'วิ', min: 0, max: 30000, step: 1000, divisor: 1000 },
      { el: 'stepper', field: 'batchDelay', label: 'พักระหว่างชุด', placeholder: 'จบชุดหนึ่ง พักก่อนชุดถัดไป (กันโดนลิมิต)', icon: 'restart_alt', unit: 'วิ', min: 0, max: 120, step: 5 },
      { el: 'stepper', field: 'retryDelay', label: 'พักก่อนลองใหม่', placeholder: 'ตอนงานพลาด รอเท่านี้ก่อนยิงใหม่', icon: 'replay', unit: 'วิ', min: 0, max: 60 },
      { el: 'stepper', field: 'maxAttempts', label: 'ลองใหม่สูงสุด', placeholder: 'ต่อชิ้นงาน รวมครั้งแรก', icon: 'repeat', unit: 'ครั้ง', min: 1, max: 5 },
      { el: 'switch', field: 'blocklistEnabled', label: 'เปิดกรองคำต้องห้าม' },
      { el: 'taginput', field: 'blocklist', label: 'คำต้องห้าม (แตะเพื่อลบ)' },
      { el: 'button', action: 'set', to: 'blocklist', value: HS_BLOCKED_DEFAULT.join(','), label: 'รีเซ็ตคำต้องห้ามเป็นค่าเริ่มต้น', icon: 'restart_alt', size: 'sm', variant: 'ghost' },
    ])],
  },
  phases: [
    {
      id: 'main', title: '', navLabel: 'หน้าหลัก',
      form: [
        { el: 'use', component: 'runBanner' },
        mainLayout,
        productsPage,
        charactersPage,
        productEditPage,
        characterEditPage,
      ],
    },
  ],
  brain: {},
};

const out = path.join(CFG, 'hardsell.json');
fs.writeFileSync(out, JSON.stringify(config, null, 2));
console.log('เขียน', out, JSON.stringify(config).length, 'bytes (compact)');
