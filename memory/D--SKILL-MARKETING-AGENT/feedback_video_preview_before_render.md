---
name: Luôn show preview PNG trước khi render video
description: Khi build video pipeline (HyperFrames/Remotion/AE-style), BUỘC PHẢI show screenshot/preview cho user duyệt trước khi chạy render MP4 cuối
type: feedback
originSessionId: c4d3892c-dd8f-4509-9f89-94092a5730d4
---
Khi build bất kỳ video pipeline nào (HyperFrames, Remotion, ffmpeg compositions), TUYỆT ĐỐI không được render MP4 ngay lần đầu. Phải:

1. Build HTML/composition xong
2. Capture 1-2 PNG snapshot ở frame tiêu biểu (dùng `npx hyperframes snapshot` hoặc Playwright screenshot)
3. Show PNG cho user duyệt layout/typography/màu
4. Đợi user OK rồi mới `npm run render` → MP4

**Why:** Render mỗi MP4 mất 1-8 phút, render 5 video song song mất 12+ phút và tốn nhiều resource. Nếu typography/layout sai (title cao quá, text tràn safe zone TikTok, font size lệch) thì phải render lại toàn bộ — rất phí thời gian. Lần trước render 5 video TikTok xong mới phát hiện title quá cao bị TikTok UI che → phải redo cả 5.

**How to apply:**
- Batch render N video cùng style → build 1 video làm prototype, snapshot preview, get approval, RỒI mới fan out N agent render parallel
- Single video → snapshot ở 2-3 frame quan trọng (intro/middle/outro) trước khi render full
- TikTok 9:16: nhớ safe zone top ~280px (search/tabs) + bottom ~650px (caption/buttons) — title KHÔNG đặt quá cao

**Live preview trong Claude Code panel (BUỘC PHẢI có cho mọi index.html dùng GSAP):**

GSAP `.from(opacity:0)` set ngay opacity 0 vào element khi register timeline → paused timeline ở progress 0 → panel hiện màn ĐEN. Fix bằng cách thêm SAU `window.__timelines["main"] = tl;` đoạn snippet này:

```js
// Jump timeline to final composed frame so preview panel shows visible content
// (GSAP .from() otherwise leaves elements at opacity 0). Hyperframes renderer
// overrides via per-frame seek+pause, so MP4 output is identical.
tl.progress(1).pause();

// Browser preview only — loop the animation. Renderer detection via navigator.webdriver.
const isRenderer =
  navigator.webdriver === true ||
  /headless/i.test(navigator.userAgent || "");
if (!isRenderer) {
  setTimeout(() => {
    tl.restart();
    tl.eventCallback("onComplete", () => {
      setTimeout(() => tl.restart(), 1800);
    });
  }, 1200);
}
```

**Why this snippet is safe for render:** Hyperframes renderer Puppeteer luôn `tl.seek(t); tl.pause();` cho từng frame, override mọi `progress()` hoặc `play()` state. `navigator.webdriver === true` trong Puppeteer/headless Chromium → skip auto-play branch luôn (defensive, không thực sự cần thiết vì renderer override).
