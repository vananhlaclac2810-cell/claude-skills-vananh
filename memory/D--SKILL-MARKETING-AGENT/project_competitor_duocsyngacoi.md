---
name: TikTok @duocsyngacoi (Dược Sỹ Ngà Coi)
description: TikTok kênh dược sỹ tư vấn mẹ bỉm cùng ngách Dr.Maya. Snapshot 2026-05-12 đã scrape 576 video, lọc 55 video ≥100K view, full transcript Vietnamese.
type: project
originSessionId: cab9d9b3-b3dd-4150-8073-9775b3156295
---
Channel: `https://www.tiktok.com/@duocsyngacoi` (Dược sỹ Ngà Coi — tư vấn mẹ bỉm / chăm bé sơ sinh)

**Why:** Cùng ngách với Dr.Maya, FB TuVanSuaMe, TikTok @bssuame_bmc. Đây là người dược sỹ chia sẻ, format video dài hơn (122-513s) vs @bssuame_bmc (30-60s) → angle phân tích khác.

**How to apply:**
- Khi viết script TikTok cho Dr.Maya, tham khảo top 10 video ≥100K view của kênh này trước
- Data snapshot ở `D:\SKILL MARKETING AGENT\`:
  - `duocsyngacoi_100k_FINAL.json` — full data (55 videos, transcript đầy đủ)
  - `duocsyngacoi_100k_REPORT.md` — markdown readable, sort theo view
  - `duocsyngacoi_100k_summary.csv` — table không có transcript
  - `duocsyngacoi_100k_full.csv` — table có cả transcript

**Top 5 video (≥440K view):**
1. **1.4M view** — Lý do em bé ngủ không ngon giấc (đặt bé nằm sấp/khóc đêm)
2. **1.2M view** — Sơ cứu em bé bị sặc/co giật (nắm chắc kỹ thuật)
3. **908K view** — Vitamin D3K2 mở nắp dùng được bao lâu
4. **827K view** — Xử lý khi em bé vừa chớ xong
5. **765K view** — Vệ sinh vùng kín cho bé trai

**Pattern viral chung (khác @bssuame_bmc):**
1. Hook bằng câu chuyện cá nhân: "Tôi đã mắc sai lầm khiến con tôi..."
2. Tone dân dã hơn: "mấy bà", "bà ơi", "tui", "thôi đừng cố"
3. Video dài (>2 phút) → dạng kể chuyện + kiến thức, không phải demo nhanh
4. Chủ đề lệch về phân tích/cảnh báo nhiều hơn là demo kỹ thuật
5. Caption hay bắt đầu "Trả lời @user" → reply theo comment → viral nhờ đẩy comment

**Để cập nhật snapshot mới**: chạy lại `yt-dlp --flat-playlist --dump-json` thay vì Apify (Apify đã hết quota). Pipeline: yt-dlp list → filter ≥100K → yt-dlp -f "h264_540p_888027-0/..." -x mp3 → faster-whisper small (vi). Script ở `duocsyngacoi_filter.py`, `duocsyngacoi_transcribe.py`, `duocsyngacoi_report.py`.
