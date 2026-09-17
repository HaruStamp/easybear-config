# bear-flow-config

Config สำหรับ Architecture C spike — Flow interpreter app ดึงผ่าน jsdelivr
`https://cdn.jsdelivr.net/gh/HaruStamp/bear-flow-config@main/config.json`

## ทะเบียน config (ตรวจจริง 2026-09-17 · GCS vs repo vs การอ้างถึงใน repo ทีม)

| ไฟล์ | ใช้โดย | สถานะ |
|---|---|---|
| `apps.json` | launcher ของ golden EasyBear Engine (การ์ด 5 แอป → ชี้ `<app>-dev.json` ตั้งแต่ 2026-09-17) | ✅ live |
| `showhow-dev.json` · `hardsell-dev.json` · `minimal-dev.json` · `film-dev.json` · `flow-dev.json` | **มาตรฐาน -dev/-public (REGISTRY §EBS · 2026-09-17)** — สร้างขั้น ① จาก `showhow.json` / `hardsell-v2.json` / `minimal-lab.json` / `film.json` / `flow.json` (md5 เท่าต้นฉบับ) · ทีมแอปแก้/push ไฟล์ `-dev` ของตัวเอง · ชื่อเก่า = alias จนกว่าขั้น ⑥ | ✅ live |
| `minimal-public.json` | **ลูกค้า (สายเดียว · พี่หมีเคาะ "ยุบ" 2026-09-17)** = เนื้อ `minimal-v2.json` (md5 `tH6+aJ…` 1,344,506 B) · tool public v2.0.0 `bb6139f5` จะย้ายมาชี้ไฟล์นี้ (ขั้น ⑤) · ลูกค้าสาย v1.6.0 ย้ายไปใช้ tool v2 แล้ว `minimal.json` เลิก | 🔴 push เฉพาะพี่หมีสั่งออกรุ่น |
| `film.json` | การ์ด "การละคร" บน launcher (Engine + film.json) | ✅ live |
| `flow.json` | การ์ด "หมีทำแทน Flow" | ✅ live |
| `showhow.json` | การ์ด "ทำให้ดู" + Dev showhow (`9f906e67`) | ✅ live (ทีม showhow) |
| `hardsell-v2.json` | Dev hardsell (`40489601`) | ✅ live (ทีม hardsell) |
| `hardsell.json` | การ์ด "ขายดุ" บน launcher (hook-pack เดิม) | 🟡 live แต่แอปขายไม่ใช้แล้ว |
| `minimal.json` | ลูกค้าสาย v1.6.0 (public `3fff3b4c`) — **จะเลิกเมื่อพี่หมีย้ายลูกค้าไป tool v2** (ยุบสายเดียว 2026-09-17) | 🔴 live · ห้าม push/ลบ จนย้ายเสร็จ |
| `minimal-lab.json` | Lab minimal (`e8bac573`) · ยาม 11 ตัว | ✅ live (ทีม minimal) |
| `minimal-v2.json` | ลูกค้าสาย v2 — public `bb6139f5` ยังชี้ไฟล์นี้จนขั้น ⑤ ย้ายไป `minimal-public.json` (เนื้อเท่ากัน) · หลังนั้น = alias รอขั้น ⑥ | 🔴 live ลูกค้า · ห้าม push/ลบ จนขั้น ⑤ เสร็จ |
| `flim-v2-full.json` · โฟลเดอร์ `easybear-flim/` | อยู่บน GCS แต่**ไม่มีใน repo** — ของทีม flim | ❓ ถามทีม flim ก่อนแตะ |
| `flow-graph-config.json` · `flim-parity-config.json` | ยาม starter `flow-graph-dryrun` / `flim-parity-dryrun` โหลด (ไม่อยู่บน GCS) | 🧪 เก็บไว้เพื่อยาม |
| ~~15 ไฟล์ยุคทดลอง/showcase~~ (`config.json` `pipeline.json` `starter.json` `framework-default/showcase` `dashboard/widget/wizard-showcase` `storyboard-slice` `tier2-test*` `flim-architect/config` `hardsell-config`) | ไม่อยู่บน GCS · ไม่มีโค้ด/ยามอ้างถึง | 🗑️ **ลบออกจาก repo 2026-09-17** (กู้ได้จาก git ก่อน commit นี้) |
| `gcs-cors.json` | ตั้งค่า CORS ของ bucket (ใช้ตอน setup bucket) | 🔧 เครื่องมือ ไม่ใช่ config แอป |

- ไฟล์ที่ **push แล้วลูกค้าเห็นทันที** = ทุกตัวที่อยู่บน GCS (no-cache) ⇒ ก่อน `./push-gcs.sh <file>` ดูตารางนี้ว่าใครโหลดอยู่
- ตรวจซ้ำ: `gsutil ls gs://easybear-config-578946198765` เทียบ `ls *.json`
