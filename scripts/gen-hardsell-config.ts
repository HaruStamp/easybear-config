// gen-hardsell-config.ts — สร้าง hardsell.json จาก pack จริง (option lists sync กับ hooks-hardsell เสมอ)
// รัน: cd easybear-starter && npx tsx ../easybear-config/scripts/gen-hardsell-config.ts
// theme + model options ยืมจาก film.json (มาตรฐานเดียวกัน) · เขียนทับ easybear-config/hardsell.json (indent=2 ไม่มี trailing newline)
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

// ---- option lists จาก pack (sync อัตโนมัติ) ----
const TEMPLATE_OPTS = HS_SCENE_TEMPLATES.map(t => ({ value: t.id, label: t.name, desc: t.desc, icon: t.icon }));
const TONE_OPTS = HS_TONES.map(t => ({ value: t.id, label: t.name, desc: t.desc, icon: t.icon }));
const STYLE_OPTS = HS_TEXT_STYLES.map(s => ({ value: s.id, label: s.name, desc: s.desc, ...(s.colors.length ? { colors: s.colors } : { icon: 'shuffle' }) }));
const AGE_OPTS = ['วัยรุ่น 18-25', 'วัยทำงาน 25-35', 'กลางคน 35-50', 'สูงวัย 50+'].map(a => ({ value: a, label: a }));

// ---- UI helpers ----
const lbl = (v: string) => ({ el: 'text', value: v, className: 'text-[11px] font-bold uppercase tracking-wide opacity-40' });
const noteTx = (v: string) => ({ el: 'note', tone: 'info', value: v });

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

// การ์ดคลิป (repeat tasks — หน้า produce)
const taskCard = {
  el: 'repeat', coll: 'tasks', empty: 'ยังไม่มีคิวงาน — กลับไปหน้าตั้งค่าแล้วกด "จัดคิวผลิต"',
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

const config = {
  schemaVersion: 1,
  title: 'หมีแว่น ขายดุ',
  icon: 'sell',
  app: { id: 'hardsell' },
  persistBar: true,
  theme: { ...film.theme, vars: { ...film.theme.vars, '--ev-accent': '#f76b6b', '--ev-accent-fg': '#ffffff' } },
  style: film.style || undefined,
  breakpoints: film.breakpoints || undefined,
  content: { item: { coll: 'tasks', label: 'คลิป' }, assets: ['products', 'characters'] },
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
    { checkpoint: 'setup', hard: true },
    { op: 'hsContent' },
    { op: 'hsPrompts' },
    { op: 'hsImage' },
    { op: 'hsVideo1' },
    { op: 'hsVideo2' },
    { checkpoint: 'produce', gate: { op: 'all', from: 'tasks', slot: 'video1' } },
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
      id: 'setup', title: 'ตั้งค่า', navLabel: 'ตั้งค่า',
      form: [
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
        noteTx('กด "จัดคิวผลิต" เพื่อสร้างคิวคลิปจากสินค้าที่ติ๊กใช้ · แล้วไปหน้า "ผลิต" เพื่อสั่งเดินงานทั้งคิว'),
        { el: 'gen-phase', ops: ['hsQueue'], label: 'จัดคิวผลิต', icon: 'playlist_add', className: 'w-full justify-center h-12' },
      ],
    },
    {
      id: 'produce', title: 'ผลิต', navLabel: 'ผลิต',
      form: [
        { el: 'row', className: 'items-center gap-2 flex-wrap', card: [
          { el: 'stat-card', label: 'คิวทั้งหมด', value: { op: 'count', from: 'tasks' }, icon: 'movie' },
          { el: 'stat-card', label: 'เสร็จแล้ว', value: { op: 'count', from: 'tasks', slot: 'video1' }, icon: 'check_circle' },
          { el: 'run-button', label: 'เริ่มผลิตทั้งคิว' },
        ]},
        taskCard,
      ],
    },
  ],
  brain: {},
};

const out = path.join(CFG, 'hardsell.json');
fs.writeFileSync(out, JSON.stringify(config, null, 2));
console.log('เขียน', out, JSON.stringify(config).length, 'bytes (compact)');
