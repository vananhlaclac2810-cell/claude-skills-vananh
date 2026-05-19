---
name: Skill biz-zalo-chatbot-zcajs — Trợ lý AI Zalo cá nhân + notify từ Sepay
description: Skill mới scaffold 1 standalone Node.js listener dùng zca-js (unofficial Zalo API) + Express /send endpoint, listen tin nhắn Zalo cá nhân, gọi OpenRouter LLM trả lời tự động, đồng thời cho Sepay webhook gọi vào gửi notification.
type: project
originSessionId: dde8441c-feb6-4cae-a0ae-1a5a5a828fd6
---
## Vị trí

- Skill: `C:\Users\ADMIN\.claude\skills\biz-zalo-chatbot-zcajs\`
- Files chính:
  - `SKILL.md` — workflow 6 phase, USE WHEN ~20 keywords
  - `references/zalo-account-setup.md` — extract cookies/imei/userAgent
  - `references/zca-js-risks.md` — WARNING dài, risk top 5 + mitigation
  - `references/openrouter-prompt-strategy.md` — system prompt template tiếng Việt
  - `references/deployment-railway.md` — deploy step-by-step cho non-dev
  - `templates/zalo-listener/` — standalone Node project hoàn chỉnh
    - `package.json`, `index.js`, `lib/{openrouter,knowledge,rate-limit,sender,server}.js`
    - `scripts/{test-login,test-llm}.js`
    - `zalo-knowledge/example.md`, `.env.example`, `.gitignore`, `README.md`
  - `templates/nextjs-integration/`
    - `app/api/zalo-notify/route.ts` — proxy Vercel → Railway listener
    - `lib-zalo-notify.ts` — helper `sendZaloNotification()` cho Sepay webhook
    - `README.md`
  - `scripts/setup_listener.py` — Python helper 1-shot scaffold

## Tech stack đã chọn

| Thành phần | Choice | Lý do |
|---|---|---|
| Zalo API | `zca-js` 2.1.1 (pinned) | Library unofficial reverse-engineered, là option duy nhất cho Zalo cá nhân không cần OA |
| Login method | Cookie-based (zpsid + zpw_sek + imei + userAgent) | Stable hơn QR login cho server deploy |
| LLM | OpenRouter `google/gemini-3-flash-preview` default | Match pattern `biz-nextjs-chatbot-openrouter`. User đổi sang Sonnet qua env var |
| Long-running host | Railway free trial $5 → Hobby $5-10/tháng | Đơn giản nhất cho non-dev, persistent ngay (Render free sleep 15p, Fly.io không free 2026) |
| Web server | Express mini (~50 LOC) | Đủ cho /send + /health, không cần Fastify/Hono |
| Knowledge base | Markdown files trong `zalo-knowledge/` | User edit dễ, không cần DB/vector store cho early stage |
| Rate limit | Token bucket in-memory ≤1 reply/giây/chat | Built-in, không cần Redis |
| Auth /send | `x-api-key` header | Đơn giản nhất, match pattern `biz-admin-leads-dashboard` |

## Caveats — risk QUAN TRỌNG

⚠️ **zca-js là unofficial**. Vi phạm Zalo ToS. Account có thể bị khóa vĩnh viễn bất kỳ lúc nào.

Quy tắc mọi user dùng skill này PHẢI biết:
- BẮT BUỘC dùng số phụ riêng, KHÔNG dùng số chính của business
- Backup plan: phải có FB / hotline / web chatbot khác để khi Zalo bot khóa, khách vẫn liên hệ được
- Cookies expire mỗi ~30 ngày → cần re-extract định kỳ
- LLM hallucinate → đã có boundaries trong system prompt nhưng vẫn cần review log hằng tuần
- Tin nhạy cảm (khiếu nại, y khoa, chính trị) → bot fallback "em chuyển sale" thay vì auto-reply

## Integration với skill khác

| Skill | Quan hệ |
|---|---|
| `biz-setup-sepay-payment` | Tạo Sepay webhook + Vercel KV lead store. `biz-zalo-chatbot-zcajs` wire vào webhook cùng pattern với `biz-telegram-payment-notify` |
| `biz-telegram-payment-notify` | Cùng pattern fan-out `Promise.allSettled([email, telegram, zalo])` |
| `biz-email-setup` | Cùng pattern wire vào Sepay webhook, không xung đột |
| `biz-nextjs-chatbot-openrouter` | Pattern OpenRouter giống — knowledge base + system prompt format chung |

## Khi nào nên đề xuất Dr.Maya dùng skill này

- ✅ Khi inbox Zalo cá nhân Dr.Maya nhận quá nhiều câu hỏi FAQ trùng lặp (giá, ship, đối tượng dùng)
- ✅ Khi muốn thêm Zalo channel cho notify thanh toán bên cạnh Telegram
- ⚠️ NHƯNG: cần ưu tiên register Zalo OA chính thức nếu Dr.Maya scale >500 đơn/tháng — skill này chỉ là bootstrap

## Verified info (research 2026-05-17)

- `zca-js` v2.1.1 latest, GitHub `RFS-ADRENO/zca-js`, npm pkg name = `zca-js` (no scope)
- Login signature: `new Zalo({selfListen, checkUpdate})` rồi `await zalo.login({cookie, imei, userAgent})`
- Listener event: `api.listener.on('message', ...)` cho cả user + group (phân biệt qua `message.type === ThreadType.User/Group`)
- Send: `api.sendMessage({msg, quote?}, threadId, type)`
- Railway free trial $5 one-time credit 2026 — Render free tier sleep 15p, không phù hợp listener
