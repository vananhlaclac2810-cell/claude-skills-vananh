---
name: Dr.Maya TikTok carousel video recipe
description: Công thức build batch N video TikTok 9:16 (motion-graphics, không voiceover) cho Dr.Maya từ N ảnh tham khảo / N topic — user trigger ngắn gọn, em scaffold + snapshot + render parallel
type: project
originSessionId: c4d3892c-dd8f-4509-9f89-94092a5730d4
---
**Trigger phrases user thường dùng (lần sau gặp keyword này em làm luôn, không hỏi lại spec mặc định):**
- "tạo N video TikTok kiểu Dr.Maya từ [N ảnh / N chủ đề]"
- "làm video Dr.Maya từ mấy ảnh này, chạy [N] sub-agent"
- "video kiểu lần trước" / "format lần trước"
- "carousel post lên TikTok kiểu Dr.Maya"
- "nội dung chữ giống ảnh, background mẹ bầu"

**Spec mặc định (KHÔNG cần user nhắc lại):**
- TikTok 9:16, 1080×1920, 30fps, silent (no voiceover, no music)
- Duration 22-28s tuỳ density nội dung
- Background AI mẹ bầu via Pollinations.ai (`pregnant vietnamese mother + theme + soft pastel pink/peach light`), fallback Unsplash
- Dark overlay `linear-gradient(180deg, rgba(0,0,0,0.40) 0%, rgba(0,0,0,0.55) 100%)`
- Font Be Vietnam Pro Google Fonts (600/700/800/900)
- **Title 58-60px** weight 900, color `#FFFFFF`, line-height 1.08, `text-shadow: 0 4px 24px rgba(0,0,0,0.7)`
- **Eyebrow "DR.MAYA"** 24px weight 700 letter-spacing 7px color `#FFB7C5`
- **Safe zone TikTok**: padding-top 320-340px, padding-bottom 200-240px, padding L/R 70px
- **Glassmorphism card** chứa list: `background: rgba(0,0,0,0.32); backdrop-filter: blur(10px); border-radius: 28px; padding: 36-44px 32-40px`
- **List item**: pill số/icon weight 900 bg `#FFB7C5` color `#1A0E14` 60×60 border-radius 50% + label `#FFB7C5` weight 800 size 38-40px + desc white weight 600 size 30-32px
- **Footer "Dr.Maya"** bottom 170, font 24-26px weight 600 color `#FFB7C5` letter-spacing 2px
- Animation GSAP: eyebrow fade-down → title fade-down+scale → card fade-up → items stagger fade-up (gap 2.0-2.7s per item) → breathing zoom bg (scale 1.0→1.04, sine.inOut) → footer fade-in
- **Auto-play snippet bắt buộc** (xem `feedback_video_preview_before_render.md`) để preview panel xem được

**Workflow tự động (không hỏi lại trừ khi user explicitly nói khác):**
1. Đọc N ảnh user gửi (Vision) → extract title + items verbatim
2. Spawn N sub-agent song song (1 agent / 1 video), mỗi agent: download bg AI → scaffold HyperFrames → write index.html theo spec → snapshot PNG 3 frame
3. Show snapshot PNG cho user duyệt (BUỘC, theo memory rule)
4. User OK → spawn N agent render parallel → output MP4 ra `D:\SKILL MARKETING AGENT\videos-done\<slug>.mp4`
5. Tạo `preview-all.html` gallery trong videos-done/ để user xem chung 1 trang
6. Mở Explorer folder cho user

**Slug pattern:** `drmaya-NN-<vietnamese-slug>` (NN zero-padded 2 chữ số)

**Workspace:** `%TEMP%\hyperframes\drmaya-NN-<slug>\` (auto cleanup không cần dọn)

**Lưu ý nhanh:**
- User Vân Anh tiếng Việt, xưng anh/chị, không dùng emoji trừ khi user dùng trước
- Nếu user gửi ảnh dạng infographic có sẵn content text, parse text VERBATIM, không paraphrase
- Nếu user không nói rõ N, đếm số ảnh user gửi = N
- Render mỗi video mất ~3-5 phút wall time → 5 video parallel ~6-12 phút
