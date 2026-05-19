---
name: TikTok @bssuame_bmc (Bác Sĩ Sữa Mẹ BMC)
description: TikTok kênh tư vấn sữa mẹ cùng ngách Dr.Maya. Snapshot 2026-05-12 đã scrape 300 video, lọc 39 video ≥100K view, có 35 transcript tiếng Việt.
type: project
originSessionId: 6cf6b371-4195-4b64-9b18-4a7c696b9d50
---
Channel: `https://www.tiktok.com/@bssuame_bmc` ("BMC" = Breast Milk Consultation)

**Why:** Cùng ngách mẹ bỉm / nuôi con sữa mẹ với Dr.Maya và page FB TuVanSuaMe. TikTok là kênh viral nhất của họ — viewing pattern khác FB (video ngắn, hook 3s đầu cực mạnh).

**How to apply:**
- Khi viết script TikTok cho Dr.Maya, tham khảo top 10 video ≥100K view của họ trước
- Data snapshot: `D:\SKILL MARKETING AGENT\bssuame_bmc_100k_FINAL.json` (full data), `bssuame_bmc_100k_REPORT.md` (transcript readable), `bssuame_bmc_100k_summary.csv` (table)
- 4 video chưa transcribe được (Apify free credit hết): IDs 7298169590368980226, 7149916370094787866, 7121295700612107546, 7128974710687190299 — chủ đề: đặt bé nằm sấp, bé ngủ không sâu, móng giò lợi sữa, kiêng tắm gội

**Insight chính từ top 5 video (≥250K view):**
- **Top 1 (1.3M view): "Khắc phục bế ngủ đặt xuống thức"** — chủ đề ngủ siêu hot, video format mẹ thực hành demo
- **Top 2 (815K): "Cách bế trẻ sơ sinh an toàn"** — kỹ thuật cơ bản, demo trực tiếp
- **Top 3 (612K): "Cách vỗ lưng giúp bé dễ ợ"** — hướng dẫn kỹ thuật chi tiết
- **Top 4 (310K): "Ăn uống lạnh khi cho con bú?"** — phá định kiến dân gian
- **Top 5 (256K): "Vì sao bé nấc cụt?"** — câu hỏi mẹ hay thắc mắc

**Pattern viral chung:**
1. Tiêu đề toàn CHỮ IN HOA + dấu hỏi (?) — tăng curiosity
2. Hook 0-3s: bác sĩ vào thẳng vấn đề bằng câu hỏi của mẹ (tương tự FB)
3. Chủ đề mass-market: ngủ, ợ hơi, bế bé, lợi sữa, kiêng cữ — chứ KHÔNG đi sâu các kỹ thuật chuyên biệt
4. Demo trực tiếp bằng tay bác sĩ — không slide, không animation
5. Video ngắn 30-60s, cắt nhanh

**Để cập nhật snapshot mới**: chạy lại `clockworks/tiktok-scraper` với `profiles:["bssuame_bmc"]`, `profileSorting:"popular"`, `resultsPerPage:300`, sau đó filter playCount≥100000.
