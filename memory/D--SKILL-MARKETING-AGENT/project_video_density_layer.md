---
name: Density layer (inserts/bursts/flashes) cho video editing skills
description: Bộ 3 skill video editing đã có density layer auto-detect cảnh chèn trám — schema v1.1, áp dụng cho cả 9:16 và 16:9
type: project
originSessionId: dde8441c-feb6-4cae-a0ae-1a5a5a828fd6
---
Ngày 2026-05-17 nâng cấp 3 skill video để fix vụ "thiếu cảnh chèn trám":

**Skill đã sửa:**
- `mkt-plan-short-video-edit-16-9` (planner) — schema v1.1
- `mkt-hyperframe-talking-head-video` (editor 9:16)
- `mkt-hyperframe-talking-head-video-16-9` (editor 16:9)

**Schema mới — 3 array optional trong `visual-plan.json` per scene:**
- `inserts[]` — cutaway 0.6-3s mid-scene (`macro-shot` / `screen-record` / `before-after-wipe` / `reaction-cut` / `icon-zoom` / `ai-stock`)
- `bursts[]` — chuỗi 2-5 visual back-to-back khi VO liệt kê (`logo-strip` / `icon-strip` / `card-stack` / `rapid-cut`)
- `flashes[]` — number/keyword pop-in 0.4-1.6s, render pure-CSS (`number-burst` / `keyword-stamp` / `icon-pop` / `emoji-rain`)

**Auto-detect heuristics (built into `plan_visuals.py`):**
- Flash: regex bắt số + unit (300%, 8h, 10tr, 5×, 100 trang) hoặc số ≥100
- Burst: 3+ brand keywords trong 8 tokens (chain `BRAND_KEYWORDS` set) hoặc "thứ nhất/hai/ba" enumeration
- Insert: action verb VI (gõ/click/kéo/mở/bấm) → macro-shot; comparison cue (trước đây/thay vì/so với) → before-after-wipe

**Target density:** Modern TikTok 3-5 visual events / 10s.

**Editor injection:** Helper `density_mounts.py` ở planner skill, cả 2 editor `generate_root_index.py` import lazy qua `_DENSITY_HELPER_CANDIDATES`. Post-process rendered HTML, inject CSS trước `</head>` + mount divs + GSAP wiring trước `</body>`. Templates không thay đổi.

**Backward-compatible:** plan v1.0 không có 3 array → render bình thường (safe noop).

**File mới:** `mkt-plan-short-video-edit-16-9/references/insert-density-guide.md` (anti-pattern + manual override examples)

**How to apply:** khi user nói "thêm cảnh chèn", "tăng density", "thiếu cảnh chèn trám", hoặc audit thấy video boring → check visual-plan.json có inserts/bursts/flashes không, nếu thiếu chạy lại `plan_visuals.py` để auto-detect.

**Why:** Lý do user feedback — video làm theo skill cũ ra style keynote/podcast (1 visual/scene), không match TikTok modern.
