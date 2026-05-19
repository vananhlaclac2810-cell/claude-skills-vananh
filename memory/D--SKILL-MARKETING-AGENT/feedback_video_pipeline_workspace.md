---
name: Video pipeline — scaffold ở %TEMP%, chỉ MP4 final lưu ổ D
description: Mọi pipeline video (HyperFrames, HeyGen, talking-head, full-pipeline) scaffold project ở Windows %TEMP%\hyperframes\<slug>\, render xong copy MP4 final sang D:\SKILL MARKETING AGENT\videos-done\ — không để project folder + source.mp4 lằm ổ D
type: feedback
originSessionId: 81147b9a-3f98-4d6a-b084-746adcc22ac7
---
Khi chạy bất kỳ skill video nào (`mkt-hyperframe-talking-head-video`, `mkt-hyperframe-talking-head-video-16-9`, `mkt-full-video-with-11-hyperframe-heygen`, `mkt-full-video-with-11-hyperframe-heygen-16-9`, hay tương tự):

1. **Scaffold project ở temp**: `%TEMP%\hyperframes\<slug>\` (Windows temp, tự clean định kỳ, không tốn space ổ D).
2. **Preview Studio + render từ temp** — user duyệt xong + lệnh render → MP4 sinh trong temp.
3. **Chỉ copy MP4 final** sang `D:\SKILL MARKETING AGENT\videos-done\<slug>.mp4` (tạo folder nếu chưa có). KHÔNG copy project folder, sub-comps, SFX, source.mp4, transcript.json.
4. **Hỏi user trước khi xoá temp**: sau khi MP4 đã sang ổ D, hỏi "xoá project temp luôn không?" — default giữ tới khi user confirm để có thể iterate.

**Why:** Mỗi project ~80-150MB (source.mp4 70MB + assets + transcripts). Trước đây tất cả nằm `D:\SKILL MARKETING AGENT\hyperframes-*\` → ổ D nặng nhanh. Anh/chị xác nhận 2026-05-18: "muốn xem video trc, duyệt ok rồi mới lưu vào ổ".

**How to apply:**
- TRƯỚC khi mkdir project folder, dùng `%TEMP%\hyperframes\<slug>\` thay vì path trong `D:\SKILL MARKETING AGENT\`.
- Khi báo cáo final, link MP4 ở ổ D + path temp folder (để user có thể vào edit thêm nếu muốn) + nhắc "khi nào ok, em xoá temp giúp anh/chị".
- Ngoại lệ: nếu user EXPLICIT yêu cầu lưu project ra ổ D (vd "lưu luôn cả project vào D\drmaya-videos\"), tuân theo.
- Project `hyperframes-xite-baby` hiện tại (2026-05-18) là CASE CŨ — đang ở `D:\SKILL MARKETING AGENT\hyperframes-xite-baby\`, giữ tới khi xong rồi áp rule mới từ video sau.
