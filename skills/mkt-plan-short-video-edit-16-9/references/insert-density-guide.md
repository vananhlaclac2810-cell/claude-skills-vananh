# Insert · Burst · Flash — density layer guide

Khi `visual-plan.json` của một scene đã có 1 `broll` chính + 1-2 `pip_events`, video vẫn có nguy cơ **đơn điệu** nếu scene dài 8s+ mà chỉ có duy nhất 1 visual element. Density layer giải quyết bằng cách thêm các shot ngắn (≤ 3s) ở timestamp tuyệt đối, **mount đè lên scene b-roll**.

Mục tiêu: đạt **Modern TikTok density 3-5 visual events / 10s** (Ali Abdaal, MrBeast tier), thay vì 1-2 events / 10s như keynote cũ.

---

## 3 loại

| Loại | Mục đích | Thời lượng | Khi nào fire |
|---|---|---|---|
| **insert** | Cutaway mid-scene — close-up tay/object, screen-record overlay, before/after wipe | 0.6 – 3.0s | Voiceover nhắc action verb ("gõ", "click", "kéo"), comparison cue ("trước đây", "thay vì") |
| **burst** | Chuỗi 2-5 visual chạy nhanh khi VO liệt kê | mỗi item 0.25 – 1.2s | VO liệt kê 3+ brand/tool ("ChatGPT, Claude, Gemini") hoặc enumeration ("thứ nhất, thứ hai, thứ ba") |
| **flash** | Number/keyword pop-in khi VO nói số | 0.4 – 1.6s | VO nhắc số có ý nghĩa (≥100, hoặc kèm unit %/tr/h/ngày/×) |

---

## Auto-detect heuristics (built into `plan_visuals.py`)

### Flashes — đơn giản nhất, fire nhiều nhất
- Regex bắt số + unit Việt/Anh (`300%`, `8h`, `10 triệu`, `5×`, `100 trang`)
- Số trần ≥ 100 cũng được flash
- Max 1 flash trong window 0.7s (tránh double-fire)
- Style mặc định `number-burst` màu `amber`, render bằng CSS (không cần PNG)

### Bursts — fire khi gặp pattern enumeration
- **Brand chain**: 3+ brand keywords trong 8 tokens & cách nhau < 2.5s → `logo-strip` (5 items max)
- **Vietnamese ordinal**: phát hiện "thứ nhất" + "thứ hai" + "thứ ba" trong scene → `card-stack`
- Asset filename: `brand-chatgpt.png`, `enum-1.png`, ...

### Inserts — fire conservative (max 2/scene)
- **Comparison cue** ("trước đây", "thay vì", "so với", "before/after") → `before-after-wipe` 1.8s
- **Action verb VI** ("gõ", "click", "kéo", "mở", "bấm") → `macro-shot` 1.4s
- Anti-collision: cách nhau ≥ 1.0s (wipe) hoặc 1.5s (verb)

---

## Density targets (Modern TikTok preset)

| Scene length | Min events | Recommended | Max |
|---|---|---|---|
| < 5s | 0 | 1 | 2 |
| 5-10s | 1 | 2-3 | 4 |
| 10-15s | 2 | 3-5 | 6 |
| 15s+ | 3 | 5-7 | 8 |

**Event** = 1 insert HOẶC 1 burst (count as 1, không count theo items) HOẶC 1 flash.

Bao gồm cả `pip_events` cũ:
- pip_event = 1 event
- broll mount = 1 event (scene base)

→ Một scene 10s nên có: 1 broll + 1 pip + 2 flash + 1 burst = **5 events**.

---

## Editor render behavior

| Loại | Mount as | Track z-index | Lifecycle |
|---|---|---|---|
| insert | `.clip.insert-mount` | 45 (dưới captions, trên scene) | Mount at `t`, unmount at `t + duration`, fade ±0.2s |
| burst | N consecutive `.clip.burst-item` | 45 | Mỗi item mount lần lượt back-to-back; cut transition default |
| flash | `.clip.flash-mount` | 48 | Mount at `t`, scale-in 0.15s → hold → fade 0.15s |

Captions track ALWAYS stay on top (z-index 100, track-index 60).

---

## Backward compatibility

Tất cả 3 array đều **optional** trong schema v1.1. visual-plan v1.0 (không có inserts/bursts/flashes) vẫn parse và render bình thường — editor sẽ skip mount step nếu array trống/missing.

Để **opt out**: set 3 array thành `[]` trong checkpoint review, planner sẽ giữ nguyên.

Để **opt in mạnh hơn**: user prompt LLM "tăng density lên 5-7 events/10s, thêm icon-pop flash cho mọi mention tên brand" → LLM hand-edit visual-plan.json.

---

## Anti-patterns

- ❌ **Flash mọi số trong VO** — nhỏ hơn 100 không có unit thì skip, tránh noise.
- ❌ **Burst > 5 items** — quá nhanh người xem không bắt kịp, hard cap 6 trong schema.
- ❌ **Insert trùng pip_event window** — insert mặc định đặt ở t ngoài pip, nếu trùng thì pip override (z-index cao hơn).
- ❌ **Macro-shot không liên quan VO** — `reason` field bắt buộc phải reference trực tiếp transcript phrase, nếu trống → reject.
- ❌ **Brand-strip cho 1-2 brand** — cần ≥ 3 để fire (single brand → flash icon-pop thay vì burst).

---

## Manual override examples

LLM downstream có thể hand-edit để thêm density không auto-detect được:

```jsonc
// VO không có verb nhưng muốn show screenshot:
"inserts": [
  { "t": 14.2, "duration": 2.0, "kind": "screen-record",
    "asset": "claude-ui-grok.png",
    "reason": "Show Claude.ai UI để minh họa 'giao việc cho AI'" }
]

// VO nói "Anthropic ra Claude 4.7 với context 1 triệu token" → flash chuỗi:
"flashes": [
  { "t": 22.4, "duration": 0.8, "value": "4.7", "style": "number-burst", "color": "claude-orange", "trigger": "Claude 4.7" },
  { "t": 23.3, "duration": 0.9, "value": "1tr", "style": "number-burst", "color": "lime",          "trigger": "1 triệu token" }
]
```
