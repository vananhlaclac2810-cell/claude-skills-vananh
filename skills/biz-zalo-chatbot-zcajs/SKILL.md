---
name: biz-zalo-chatbot-zcajs
description: "Cài trợ lý chat AI tự động trên Zalo CÁ NHÂN (qua thư viện unofficial `zca-js`) cho doanh nghiệp nhỏ Việt Nam — gồm 2 chức năng song song: (1) Bot 2 chiều listen tin nhắn khách từ Zalo friend / group, gọi OpenRouter LLM (mặc định `google/gemini-3-flash-preview`, có thể đổi sang `anthropic/claude-sonnet-4.6`) với knowledge base từ FAQ + tài liệu sản phẩm, gửi tin trả lời tự động cho khách; (2) Notification 1 chiều — endpoint HTTP `/send` trên listener server để Sepay webhook (hoặc bất kỳ webhook nào) gọi vào, gửi tin Zalo realtime báo có đơn hàng mới về cho owner / nhóm sale. Skill scaffold 2 phần riêng vì zca-js cần long-running process với WebSocket — KHÔNG chạy được trên Vercel serverless (timeout 60s): (a) standalone Node.js project `zalo-listener/` deploy lên Railway free trial / Render free tier / VPS riêng — chứa Zalo client + LLM router + sender server; (b) Next.js API route proxy `/api/zalo-notify` để Sepay webhook hoặc form submission gọi qua HTTP đến listener. Knowledge base load từ `zalo-knowledge/*.md` — user tự edit Markdown. Skill xử lý 6 phase: (0) detect Next.js stack + check existing zalo account chuẩn bị, (1) GUIDE user đăng ký Zalo phụ (không phải account chính) + extract cookies + lấy imei + userAgent từ Chrome DevTools, (2) install zca-js + scaffold listener project, (3) wire knowledge base + LLM prompt strategy, (4) wire Sepay webhook proxy nếu có, (5) deploy listener lên Railway step-by-step + setup env vars, (6) test plan 3 cấp (login Zalo verify → reply local test → notify webhook test). WARNING bắt buộc: zca-js là reverse-engineered unofficial library, account có nguy cơ bị Zalo khóa — phải dùng account phụ, áp rate limit ≤1 reply/giây, không spam, không tự động reply mọi tin nhạy cảm. USE WHEN user says: 'tạo chatbot zalo', 'bot zalo trả lời tự động', 'trợ lý zalo AI', 'auto reply zalo', 'zalo chatbot openrouter', 'zalo cá nhân bot', 'bot trả lời khách hàng zalo', 'zca-js setup', 'thông báo zalo khi có đơn hàng', 'zalo notify thanh toán Sepay', 'tích hợp zalo vào landing page', 'chat bot zalo Dr.Maya', 'gửi tin zalo từ webhook', 'wire sepay tới zalo', 'trợ lý zalo tự động cho fanpage', 'tự động trả lời tin zalo bằng AI', 'zalo bot openrouter gemini', 'zalo cá nhân chatbot openrouter sonnet', 'tích hợp ChatGPT/Claude vào Zalo cá nhân', 'biz-zalo-chatbot-zcajs'. Trigger CẢ KHI: (a) user vừa setup Sepay + Telegram notify xong và muốn bổ sung Zalo channel cho khách hàng tương tác trực tiếp, (b) user nói 'tự động hoá inbox Zalo', (c) user có nhiều tin nhắn FAQ trùng lặp trên Zalo và muốn AI trả lời thay. KHÔNG dùng skill này khi: (a) user muốn Zalo OA chính thức (Zalo Official Account verified business) — use case khác hoàn toàn (OA cần KYC, có API official, ToS khác), (b) user muốn integration Zalo từ Vercel serverless trực tiếp (không khả thi do WebSocket + timeout), (c) user không chấp nhận risk account bị khóa (skill này LUÔN có risk này dù mitigate)."
framework: "Standalone Node.js 20+ listener (long-running, WebSocket) + Next.js API route proxy (optional). zca-js 2.x cookie-based login. OpenRouter REST API non-streaming. Express mini-server expose /send endpoint. Deploy Railway / Render / VPS."
models: "google/gemini-3-flash-preview (mặc định, nhanh + rẻ) / anthropic/claude-sonnet-4.6 (chất lượng cao hơn ~10x giá)"
risk: "⚠️ zca-js là unofficial reverse-engineered library. Vi phạm Zalo ToS. Account dùng có thể bị khóa bất kỳ lúc nào. LUÔN dùng số phụ, không phải số chính. Đọc kỹ references/zca-js-risks.md trước khi triển khai production."
---

# Biz Zalo Chatbot zca-js — Trợ lý AI tự động trên Zalo cá nhân + notification từ Sepay

Skill này cài **trợ lý chat AI** trên Zalo CÁ NHÂN (không phải Zalo OA) cho doanh nghiệp nhỏ Việt Nam, đồng thời cung cấp **endpoint notification** để Sepay webhook (hoặc webhook khác) bắn tin Zalo realtime báo có đơn hàng mới. Cả 2 chức năng dùng chung 1 listener server long-running.

> ⚠️ **CẢNH BÁO QUAN TRỌNG — ĐỌC TRƯỚC KHI TRIỂN KHAI**
>
> `zca-js` là thư viện **không chính thức** (reverse-engineered) của bên thứ 3, vi phạm Điều khoản dịch vụ Zalo. Account dùng skill này **có nguy cơ bị Zalo khóa vĩnh viễn** bất kỳ lúc nào, không có khiếu nại.
>
> **BẮT BUỘC**:
> - Dùng số điện thoại PHỤ riêng cho bot (không phải số chính của business)
> - Áp rate limit ≤1 reply/giây (đã built-in)
> - Không spam, không gửi link suspicious
> - Có backup plan: nếu account khóa thì khách hàng vẫn liên hệ được qua kênh khác (FB, hotline, website)
>
> Đọc kỹ [`references/zca-js-risks.md`](references/zca-js-risks.md) trước khi cài cho production.

---

## Triết lý

- **Tại sao Zalo cá nhân chứ không phải Zalo OA?** Zalo OA cần verified business account (3-7 ngày approve), KYC business license, monthly active user fee, và quan trọng nhất: **khách phải chủ động follow OA mới chat được**. Zalo cá nhân — khách thấy SĐT là chat được ngay, friend request là kết bạn liền. Cho solopreneur / micro-business VN, Zalo cá nhân là path of least resistance. Trade-off: dùng `zca-js` (unofficial) + risk khóa.
- **Tại sao tách listener + Next.js?** zca-js cần kết nối WebSocket persistent với chat.zalo.me. Vercel serverless function timeout 60s → không phù hợp. Phải có 1 server long-running riêng. Listener đó đồng thời expose HTTP endpoint `/send` cho Sepay webhook trên Vercel proxy qua.
- **Tại sao OpenRouter chứ không phải Claude/Gemini SDK trực tiếp?** Để user dễ swap model (Gemini Flash → Claude Sonnet) chỉ qua 1 env var. Pattern này giống skill `biz-nextjs-chatbot-openrouter` đã có.

---

## Khi nào dùng

- User có doanh nghiệp nhỏ VN, nhận inbox FAQ trùng lặp trên Zalo cá nhân (giá, lộ trình, hoàn tiền, hướng dẫn dùng sản phẩm) → muốn AI trả lời tự động 24/7.
- User đã setup Sepay payment và muốn nhận thông báo realtime trên Zalo khi có đơn hàng mới (thay/bổ sung Telegram notification).
- User có landing page bán hàng và muốn add Zalo bot làm support channel chính thức.
- User chấp nhận risk account zca-js có thể bị khóa, có account phụ riêng để chạy bot.

## Khi nào KHÔNG dùng

- User cần Zalo OA chính thức (verified business) → use case khác hoàn toàn, cần API official + KYC + fee.
- User không có account Zalo phụ riêng và refuse risk → skill này KHÔNG safe trên số chính của business.
- User cần lưu lịch sử chat dài hạn vào DB → skill này stateless (chỉ giữ trong RAM listener).
- User cần multimedia (gửi ảnh, voice, file) — skill này text-only baseline (zca-js có hỗ trợ media nhưng skill base chưa wire).

---

## Output user sẽ nhận

Sau khi skill chạy xong:

1. **Standalone listener project** ở `zalo-listener/` (folder riêng, không nằm trong Next.js project):
   - `package.json` — declare zca-js + express + dotenv + openai (cho OpenRouter)
   - `index.js` — main entry: load cookies, init Zalo, register listener, route LLM, expose /send
   - `lib/openrouter.js` — wrapper gọi OpenRouter
   - `lib/knowledge.js` — load `zalo-knowledge/*.md` thành knowledge string
   - `lib/rate-limit.js` — token bucket ≤1 reply/giây/chat
   - `lib/sender.js` — function `sendZaloMessage(recipient, text)`
   - `lib/server.js` — Express expose `/send` (auth qua API key)
   - `.env.example` — list env vars
   - `zalo-knowledge/example.md` — template FAQ user fill
   - `README.md` — quick start

2. **Next.js integration (optional)** trong project Next.js đã có:
   - `app/api/zalo-notify/route.ts` — proxy route POST → listener `/send`

3. **Hướng dẫn cuối cùng**:
   - 6 bước user phải làm manual: tạo Zalo phụ, extract cookies, lấy OpenRouter key, deploy listener Railway, set env vars, test
   - Cách edit knowledge base sau này (chỉ cần edit `.md` rồi restart listener)
   - Cách đổi model OpenRouter

---

## Workflow tổng quan (6 phase)

```
Phase 0: DETECT Next.js stack (nếu có) + check existing zalo-listener folder
       ↓
Phase 1: GUIDE user chuẩn bị Zalo account phụ + extract cookies/imei/userAgent
       ↓ [GATE — đợi user paste cookies.json + imei + userAgent]
       ↓
Phase 2: SCAFFOLD zalo-listener/ project (copy templates + npm install local)
       ↓
Phase 3: WIRE knowledge base (user paste FAQ + product info → ghi vào zalo-knowledge/*.md)
       ↓
Phase 4: (OPTIONAL) WIRE Next.js Sepay webhook → /api/zalo-notify proxy → listener /send
       ↓
Phase 5: GUIDE user deploy listener lên Railway (hoặc Render fallback)
       ↓ [GATE — đợi user xong deploy, paste production URL]
       ↓
Phase 6: TEST plan 3 cấp (login Zalo verify → bot reply local → notify webhook test)
```

Phase 1 và Phase 5 có **gate đợi user** vì cần thao tác manual (DevTools, dashboard Railway).

---

## Phase 0 — Detect stack

Skill cài 2 phần. Phần listener luôn cài (standalone). Phần Next.js proxy CHỈ cài khi user có Next.js project và muốn wire vào Sepay webhook.

**Detect Next.js**:

```bash
# Trong cwd hoặc parent
test -f next.config.js -o -f next.config.mjs -o -f next.config.ts && echo "Next.js: ✓"
test -d app && echo "Router: App"
test -d pages && echo "Router: Pages"
```

**Detect listener đã có**:

```bash
test -d zalo-listener && echo "Listener folder: ✓"
test -d ../zalo-listener && echo "Listener parent: ✓"
```

**Hỏi user** (1 message gộp):

> Em chuẩn bị cài 2 thứ:
> 1. **Listener server** (standalone Node.js) — bot Zalo + endpoint /send. Em sẽ tạo folder `zalo-listener/` ở đâu, anh/chị?
>    - Mặc định em đề xuất: `D:\SKILL MARKETING AGENT\zalo-listener\` (cùng cấp với landing page)
> 2. **Next.js proxy** (optional) — `/api/zalo-notify` route trong project Next.js để Sepay webhook gọi qua. Anh/chị có muốn em wire vào project Next.js nào không? (nếu có nhiều project, em sẽ list ra để chọn)
>
> Trả lời 2 câu này em đi tiếp Phase 1.

---

## Phase 1 — Chuẩn bị Zalo account phụ + extract credentials

Đọc [`references/zalo-account-setup.md`](references/zalo-account-setup.md) cho hướng dẫn chi tiết. Tóm tắt 4 bước:

### Bước 1 — Đăng ký số phụ làm Zalo bot

```
- Lấy 1 số điện thoại PHỤ (không phải số chính của business)
- Đăng ký Zalo bằng số đó: https://id.zalo.me/account/register
- Đặt tên bot dễ nhận diện: "Trợ lý Dr.Maya" (hoặc tương tự)
- Đặt avatar logo brand
- KHÔNG dùng số chính của business — risk bị khóa vĩnh viễn
```

### Bước 2 — Login Zalo Web trên Chrome

```
- Mở https://chat.zalo.me trên Chrome (khuyến nghị Chrome incognito để dễ extract cookies sạch)
- Quét QR bằng app Zalo trên số phụ
- Đợi load xong giao diện chat
- LƯU TAB này mở, không close
```

### Bước 3 — Extract cookies + imei + userAgent

Đọc [`references/zalo-account-setup.md`](references/zalo-account-setup.md) chi tiết. Tóm tắt:

```
1. F12 → tab Application → bên trái: Cookies → https://chat.zalo.me
2. Tìm các cookies: zpsid, zpw_sek, _zlang, app.event.zalo.me, zpw_type, atc
   Copy TẤT CẢ thành JSON array format (xem references file)
3. Tab Console → gõ:
     localStorage.getItem('z_uuid') || localStorage.getItem('sh_z_uuid')
   → copy giá trị (imei)
4. Tab Console → gõ:
     navigator.userAgent
   → copy giá trị (userAgent)
5. Paste cả 3 cho em (cookies.json + imei + userAgent)
```

**GATE QUAN TRỌNG**: KHÔNG đi tiếp Phase 2 cho đến khi user paste đủ 3 thứ. Lưu vào `.env.local` listener — KHÔNG commit Git.

### Bước 4 — Chuẩn bị OpenRouter key

```
- Vào https://openrouter.ai → Sign up (Google login OK)
- Vào https://openrouter.ai/keys → Create Key
- Nạp credit https://openrouter.ai/credits — $5 đủ cho hàng nghìn câu chat Gemini Flash
- Copy key dạng `sk-or-v1-xxxxx`
```

---

## Phase 2 — Scaffold listener project

Đọc [`templates/zalo-listener/`](templates/zalo-listener/) — đó là template hoàn chỉnh. Copy nguyên folder vào path user chỉ định ở Phase 0.

**Các file**:

| File | Mục đích |
|---|---|
| `package.json` | Declare dependencies: `zca-js`, `express`, `dotenv`, `openai` |
| `index.js` | Main entry: load `.env`, init Zalo, register listener, start Express |
| `lib/openrouter.js` | Gọi OpenRouter chat completion non-streaming |
| `lib/knowledge.js` | Đọc tất cả `.md` trong `zalo-knowledge/` → return string |
| `lib/rate-limit.js` | Token bucket per-chatId, ≤1 reply/giây |
| `lib/sender.js` | `sendZaloMessage(recipient, text)` — gọi `api.sendMessage` của zca-js |
| `lib/server.js` | Express mini-server expose `/send` (auth `x-api-key` header) |
| `.env.example` | List env vars (xem dưới) |
| `zalo-knowledge/example.md` | Template FAQ user fill |
| `README.md` | Quick start |

**Env vars** (`.env.example`):

```env
# Zalo credentials (lấy từ Phase 1)
ZALO_COOKIES_JSON=     # Paste cookies JSON array (1 line)
ZALO_IMEI=             # Từ localStorage z_uuid
ZALO_USER_AGENT=       # Từ navigator.userAgent

# OpenRouter
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_MODEL=google/gemini-3-flash-preview

# Brand
BRAND_NAME=Dr.Maya
BOT_TONE=than_thien_anh_chi

# Send endpoint
ZALO_SEND_API_KEY=     # Random string >= 32 chars, dùng để auth /send từ Vercel
SEND_PORT=3001

# Notify recipients — danh sách Zalo user_id của owner / sale team (CSV)
# Lấy bằng cách kết bạn với bot từ tài khoản owner rồi xem chatId
ZALO_NOTIFY_RECIPIENTS=1234567890,9876543210
```

**Sau khi copy template**, chạy:

```bash
cd zalo-listener
npm install
cp .env.example .env
# Skill chèn các giá trị user đã paste vào .env
```

**Test local nhanh** (chưa wire LLM):

```bash
npm run test:login   # Script verify cookies + imei + userAgent đúng — chỉ login + log "OK", không listen
```

Nếu test fail → cookies expired / sai → quay lại Phase 1 Bước 3.

---

## Phase 3 — Wire knowledge base + LLM prompt strategy

Đọc [`references/openrouter-prompt-strategy.md`](references/openrouter-prompt-strategy.md) cho chi tiết.

**Thu thập từ user** (1 message gộp):

```
Em cần 3 thứ để bot trả lời chuẩn:

1. **FAQ** — list câu hỏi thường gặp + câu trả lời. Paste trực tiếp hoặc đường dẫn file .md/.txt/.docx.
   (Ví dụ Dr.Maya: giá dầu húng chanh, công dụng, đối tượng dùng, cách dùng cho trẻ, đặt hàng…)

2. **Thông tin sản phẩm / dịch vụ** — mô tả chi tiết, bảng giá, COD/chuyển khoản, vùng giao hàng.

3. **Tone** — mặc định xưng "em" gọi khách "anh/chị". Nếu muốn khác (xưng "shop", gọi "chị"…) anh/chị nói.

Trả lời 1 lượt em chạy tiếp.
```

**Khi user paste**:
- Tạo file `zalo-listener/zalo-knowledge/faq.md` chứa FAQ
- Tạo file `zalo-listener/zalo-knowledge/product.md` chứa product info
- Tone inject vào system prompt trong `lib/openrouter.js`

**System prompt structure** (xem chi tiết trong `references/openrouter-prompt-strategy.md`):

```
Em là trợ lý AI của [BRAND_NAME].

NHIỆM VỤ:
- Trả lời câu hỏi của khách về sản phẩm/dịch vụ [BRAND_NAME]
- Hỗ trợ khách quyết định mua / đặt hàng
- KHÔNG bịa thông tin. Nếu không chắc: "Anh/chị cần tư vấn thêm, em chuyển sale gọi lại nhé"

GIỌNG ĐIỆU:
- Xưng em, gọi khách anh/chị
- Thân thiện, ngắn gọn (≤3 câu/lần trả lời trừ khi cần list)
- KHÔNG emoji spam (tối đa 1-2 emoji/tin)

BOUNDARIES:
- KHÔNG trả lời chính trị, tôn giáo, ý kiến cá nhân
- KHÔNG cam kết giá ngoài bảng giá chính thức
- KHÔNG khẳng định hiệu quả y khoa (nếu là sản phẩm sức khỏe)

THÔNG TIN SẢN PHẨM:
[product.md content]

FAQ:
[faq.md content]
```

---

## Phase 4 — (Optional) Wire Sepay webhook → Zalo notify

**CHỈ chạy phase này NẾU** user có Next.js project với Sepay webhook đã setup (qua `/biz-setup-sepay-payment`).

**Detect Sepay webhook**:

```bash
# Trong project Next.js
ls app/api/sepay-webhook/ 2>/dev/null
ls app/api/payment-success/ 2>/dev/null
ls pages/api/sepay-webhook* 2>/dev/null
```

**Wire 3 file**:

### 4.1 Tạo `app/api/zalo-notify/route.ts` (template ở `templates/nextjs-integration/`)

Proxy POST từ Vercel → listener `/send`. Auth qua `x-api-key` (cùng key với `ZALO_SEND_API_KEY` trong listener).

### 4.2 Modify Sepay webhook handler

Thêm `sendZaloNotify()` vào `Promise.allSettled`:

```typescript
import { sendZaloNotify } from '@/lib/zalo-notify'; // helper gọi /api/zalo-notify

await Promise.allSettled([
  sendCustomerEmail(lead),
  sendOwnerEmail(lead),
  sendTelegramNotification(payload),
  sendZaloNotify({
    name: lead.name,
    phone: lead.phone,
    amount: payload.transferAmount,
    productName: lead.productName,
  }),
]);
```

### 4.3 Env vars trong Next.js `.env.local`

```env
# URL listener đã deploy (Phase 5 sẽ điền)
ZALO_LISTENER_URL=https://your-listener.up.railway.app
ZALO_SEND_API_KEY=     # Cùng với key trong listener
```

---

## Phase 5 — Deploy listener lên Railway

Đọc [`references/deployment-railway.md`](references/deployment-railway.md) chi tiết. Tóm tắt:

### Bước 1 — Tạo Railway account

```
1. Vào https://railway.app → Sign up bằng GitHub
2. Railway free trial: $5 credit one-time (đủ chạy listener ~1-2 tháng nếu light traffic)
3. Sau hết trial: chuyển sang plan $5/tháng (hoặc đổi sang Render free tier)
```

### Bước 2 — Push listener lên GitHub

```bash
cd zalo-listener
git init
git add .
git commit -m "init zalo listener"
gh repo create zalo-listener --private --source=. --push
```

### Bước 3 — Connect Railway → GitHub repo

```
1. Railway dashboard → New Project → Deploy from GitHub repo
2. Chọn zalo-listener
3. Railway tự detect Node.js, build + start
```

### Bước 4 — Set env vars trên Railway

```
1. Railway project → Variables tab
2. Paste TẤT CẢ env từ .env (ZALO_COOKIES_JSON, ZALO_IMEI, ZALO_USER_AGENT, OPENROUTER_API_KEY, ...)
3. Save → Railway auto-redeploy
```

### Bước 5 — Generate public domain

```
1. Railway project → Settings → Networking → Generate Domain
2. Railway tạo URL kiểu https://zalo-listener-xxxxx.up.railway.app
3. Copy URL → paste vào Vercel .env (ZALO_LISTENER_URL)
4. Redeploy Vercel
```

**Fallback nếu Railway không phù hợp**:
- **Render free tier**: free 750h/tháng, có sleep sau 15p inactive → KHÔNG phù hợp listener (cần persistent)
- **Render paid $7/tháng**: persistent, recommended fallback
- **VPS riêng** (DigitalOcean / Vultr $4-6/tháng): nhiều control hơn nhưng cần biết Linux/SSH

---

## Phase 6 — Test plan 3 cấp

### Test 1 — Login Zalo verify (chạy local)

```bash
cd zalo-listener
npm run test:login

# Expect:
# - Console: "[zalo] Login OK, account: Trợ lý Dr.Maya, uid: 1234567890"
# - Process exit 0
```

**Fail thường gặp**:
- `EZINIT` / `cookies invalid` → cookies expired → extract lại Phase 1
- `imei mismatch` → imei sai → lấy lại từ localStorage
- `userAgent mismatch` → dùng cùng Chrome đã extract cookies

### Test 2 — Bot reply local

```bash
cd zalo-listener
npm start

# Console:
# [zalo] Listening...
# [server] /send endpoint ready on port 3001

# Từ Zalo cá nhân khác, gửi tin nhắn cho bot:
# Ví dụ: "Dầu húng chanh giá bao nhiêu?"
# Bot phải reply trong ≤5s
```

### Test 3 — Notify webhook test

```bash
# Từ máy local, fake Sepay webhook gọi đến Vercel proxy:
curl -X POST http://localhost:3000/api/zalo-notify \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ZALO_SEND_API_KEY" \
  -d '{
    "recipients": ["1234567890"],
    "message": "🎉 ĐƠN HÀNG MỚI\n\nNguyễn Văn A — 0901234567\n499.000đ — Dầu húng chanh Dr.Maya"
  }'

# Expect:
# - Response: {"ok":true}
# - Zalo của owner (uid 1234567890) nhận tin
```

---

## Output cuối cùng skill trả về user

```
✓ Đã cài Zalo chatbot listener

📁 Đã tạo:
- zalo-listener/ (standalone Node project)
  - package.json + index.js + lib/* + zalo-knowledge/*
- (Nếu có Next.js) app/api/zalo-notify/route.ts
- .env files (placeholder)

🤖 Bot info:
- Account: [tên Zalo phụ]
- LLM: google/gemini-3-flash-preview qua OpenRouter
- Knowledge: zalo-knowledge/faq.md + product.md

🧪 Test đã chạy:
- Test 1 (login): ✓ / ✗
- Test 2 (reply local): chờ user test
- Test 3 (notify webhook): chờ user test

🔧 TODO của anh/chị:
1. Deploy listener lên Railway (Phase 5 — em đã in guide chi tiết)
2. Set env vars production trên Railway
3. Update ZALO_LISTENER_URL trong Vercel project
4. Test 1 đơn thật

⚠️ NHẮC LẠI RISK:
- Account zca-js có thể bị Zalo khóa bất kỳ lúc nào
- Dùng số phụ, KHÔNG số chính
- Nếu khóa: backup channel (FB/hotline/website) phải luôn live
```

---

## Reference files

- [`references/zalo-account-setup.md`](references/zalo-account-setup.md) — chi tiết extract cookies/imei/userAgent từ Chrome DevTools
- [`references/zca-js-risks.md`](references/zca-js-risks.md) — ⚠️ WARNING dài + best practice giảm risk
- [`references/openrouter-prompt-strategy.md`](references/openrouter-prompt-strategy.md) — hướng dẫn viết system prompt cho bot tiếng Việt
- [`references/deployment-railway.md`](references/deployment-railway.md) — step-by-step deploy listener lên Railway

## Templates

- [`templates/zalo-listener/`](templates/zalo-listener/) — standalone Node project hoàn chỉnh (package.json, index.js, lib/, zalo-knowledge/, README.md)
- [`templates/nextjs-integration/`](templates/nextjs-integration/) — Next.js API route proxy + README

## Scripts

- [`scripts/setup_listener.py`](scripts/setup_listener.py) — Python helper chạy 1 lần: copy template + npm install + generate .env

---

## Anti-pattern (đừng làm)

- ❌ Dùng SỐ CHÍNH của business — khóa vĩnh viễn = mất toàn bộ contact + group
- ❌ Reply mọi tin nhắn không filter — risk spam detection + ban
- ❌ Bot tự cam kết giá / khuyến mãi ngoài bảng giá — risk khách kiện
- ❌ Commit cookies.json / .env lên Git — leak = anyone steal account
- ❌ Deploy listener lên Vercel serverless — timeout 60s, WebSocket không persist
- ❌ Skip rate limit — gửi >5 tin/giây = Zalo flag spam → khóa
- ❌ Reply tin nhạy cảm (chính trị, khiếu nại) bằng bot — luôn fallback "em chuyển sale" cho human handle
- ❌ Hardcode cookies trong source code — luôn qua env var
- ❌ Bỏ qua [`references/zca-js-risks.md`](references/zca-js-risks.md) trước khi production
