# bear-flow-config

Config สำหรับ Architecture C spike — Flow interpreter app ดึงผ่าน jsdelivr
`https://cdn.jsdelivr.net/gh/HaruStamp/bear-flow-config@main/config.json`

## ทะเบียน config (ตรวจจริง 2026-09-17 · GCS vs repo vs การอ้างถึงใน repo ทีม)

| ไฟล์ | ใช้โดย | สถานะ |
|---|---|---|
| `apps.json` | launcher ของ golden EasyBear Engine (การ์ด 5 แอป) | ✅ live |
| `film.json` | การ์ด "การละคร" บน launcher (Engine + film.json) | ✅ live |
| `flow.json` | การ์ด "หมีทำแทน Flow" | ✅ live |
| `showhow.json` | การ์ด "ทำให้ดู" + Dev showhow (`9f906e67`) | ✅ live (ทีม showhow) |
| `hardsell-v2.json` | Dev hardsell (`40489601`) | ✅ live (ทีม hardsell) |
| `hardsell.json` | การ์ด "ขายดุ" บน launcher (hook-pack เดิม) | 🟡 live แต่แอปขายไม่ใช้แล้ว |
| `minimal.json` | **ลูกค้าที่ซื้อแล้ว** (public minimal) | 🔴 live · ห้าม push ทับจนพี่หมีสั่ง |
| `minimal-lab.json` | Lab minimal (`e8bac573`) · ยาม 11 ตัว | ✅ live (ทีม minimal) |
| `minimal-v2.json` | ตัวขายรุ่นใหม่ (= minimal-lab ทุกไบต์ ณ 2026-09-13) | 🟡 live รอ cutover ลูกค้า |
| `flim-v2-full.json` · โฟลเดอร์ `easybear-flim/` | อยู่บน GCS แต่**ไม่มีใน repo** — ของทีม flim | ❓ ถามทีม flim ก่อนแตะ |
| `flow-graph-config.json` · `flim-parity-config.json` | ยาม starter `flow-graph-dryrun` / `flim-parity-dryrun` โหลด (ไม่อยู่บน GCS) | 🧪 เก็บไว้เพื่อยาม |
| ~~15 ไฟล์ยุคทดลอง/showcase~~ (`config.json` `pipeline.json` `starter.json` `framework-default/showcase` `dashboard/widget/wizard-showcase` `storyboard-slice` `tier2-test*` `flim-architect/config` `hardsell-config`) | ไม่อยู่บน GCS · ไม่มีโค้ด/ยามอ้างถึง | 🗑️ **ลบออกจาก repo 2026-09-17** (กู้ได้จาก git ก่อน commit นี้) |
| `gcs-cors.json` | ตั้งค่า CORS ของ bucket (ใช้ตอน setup bucket) | 🔧 เครื่องมือ ไม่ใช่ config แอป |

- ไฟล์ที่ **push แล้วลูกค้าเห็นทันที** = ทุกตัวที่อยู่บน GCS (no-cache) ⇒ ก่อน `./push-gcs.sh <file>` ดูตารางนี้ว่าใครโหลดอยู่
- ตรวจซ้ำ: `gsutil ls gs://easybear-config-578946198765` เทียบ `ls *.json`
