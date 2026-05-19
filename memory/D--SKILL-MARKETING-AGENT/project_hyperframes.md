---
name: HyperFrames đã setup
description: HeyGen HyperFrames CLI + 14 skill agent + project demo đã cài vào workspace SKILL MARKETING AGENT (2026-05-11)
type: project
originSessionId: 5ac463d9-d661-4345-9650-b40decf57dbe
---
HyperFrames (heygen-com/hyperframes) đã được setup đầy đủ trong workspace.

**Why:** User muốn dùng HyperFrames để render video từ HTML cho marketing content (Dr.Maya, Euro Mũi Tẹt). HyperFrames cho phép AI agent compose video bằng HTML/CSS/JS thay vì học Remotion/React.

**How to apply:**
- Project demo có sẵn tại `D:\SKILL MARKETING AGENT\hyperframes-demo\` — chỉnh `index.html`, chạy `npm run dev` để preview, `npm run render` xuất MP4. Khi cần làm video mới có thể `cd` vào đó hoặc `npx hyperframes init <new-project>`.
- 14 skill đã cài tại `C:\Users\ADMIN\.claude\skills\.agents\skills\` (folder ẩn `.agents` nên PowerShell `Get-ChildItem` mặc định không thấy — phải dùng `-Force` hoặc bash `ls -la`). Các skill quan trọng: `hyperframes` (compose), `hyperframes-cli` (dev loop), `hyperframes-media` (TTS/Whisper/u2net), `website-to-hyperframes` (URL→video), `gsap`/`animejs`/`tailwind`/`three`/`lottie` (animation libs).
- Khi user yêu cầu làm video, gợi ý slash command `/hyperframes` (composition) hoặc `/website-to-hyperframes` (capture URL → video).
- Prerequisites đã sẵn sàng: Node v24.15.0, ffmpeg 8.1.1 (Gyan.FFmpeg via winget, tại `C:\Users\ADMIN\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_*\bin\`).
- Lệnh trong project demo (xem `hyperframes-demo/CLAUDE.md` để biết chi tiết): `npm run dev` (preview), `npm run check` (lint+validate+inspect), `npm run render` (MP4), `npm run publish` (shareable link).

**Quan trọng:** sau khi cài ffmpeg bằng winget, **terminal/IDE cũ vẫn dùng PATH cũ** — phải mở terminal mới để `ffmpeg` chạy được trực tiếp. Nếu lệnh `npm run render` bị lỗi không tìm thấy ffmpeg, đó là lý do.
