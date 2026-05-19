# Zalo Listener — Trợ lý AI Zalo + Notification endpoint

Standalone Node.js project chạy 24/7, expose 2 chức năng:
1. **Bot 2 chiều**: listen tin nhắn Zalo cá nhân → gọi OpenRouter LLM → reply
2. **Notification endpoint** `/send`: webhook khác gọi POST để gửi tin Zalo

> ⚠️ Đọc `references/zca-js-risks.md` (trong skill folder) TRƯỚC khi production.
> Dùng số Zalo PHỤ, KHÔNG dùng số chính. Account có nguy cơ bị khóa.

---

## Quick start

```bash
# 1. Cài deps
npm install

# 2. Copy env template
cp .env.example .env
# → mở .env, điền cookies/imei/userAgent/openrouter key/...

# 3. Test login (verify cookies đúng)
npm run test:login

# 4. Test LLM (verify knowledge base + prompt)
npm run test:llm

# 5. Edit knowledge base
# → mở zalo-knowledge/example.md, thay thông tin brand vào
# → có thể tạo thêm file faq.md, product.md, shipping.md, ...

# 6. Start listener
npm start
```

---

## Folder structure

```
zalo-listener/
├── package.json
├── .env.example           # Template env vars
├── .env                   # (Tạo từ .env.example, KHÔNG commit)
├── .gitignore
├── index.js               # Main entry
├── lib/
│   ├── openrouter.js      # OpenRouter LLM wrapper
│   ├── knowledge.js       # Load .md files thành knowledge string
│   ├── rate-limit.js      # Token bucket ≤1 reply/giây/chat
│   ├── sender.js          # Helper sendZaloMessage
│   └── server.js          # Express /send endpoint
├── scripts/
│   ├── test-login.js      # Verify cookies đúng
│   └── test-llm.js        # Test LLM với 10 câu sample
└── zalo-knowledge/
    └── example.md         # Template knowledge — anh/chị thay thông tin brand
```

---

## Env vars (đầy đủ trong `.env.example`)

| Variable | Mục đích |
|---|---|
| `ZALO_COOKIES_JSON` | JSON array cookies từ chat.zalo.me |
| `ZALO_IMEI` | Từ `localStorage.getItem('z_uuid')` |
| `ZALO_USER_AGENT` | Từ `navigator.userAgent` |
| `OPENROUTER_API_KEY` | https://openrouter.ai/keys |
| `OPENROUTER_MODEL` | Default `google/gemini-3-flash-preview` |
| `BRAND_NAME` | Tên brand bot xưng |
| `ZALO_SEND_API_KEY` | Random 32+ chars để auth POST /send |
| `SEND_PORT` | Port Express server (default 3001) |
| `ZALO_NOTIFY_RECIPIENTS` | CSV user_id để forward tin nhạy cảm |

---

## API: POST /send

Gửi tin Zalo từ bên ngoài (Vercel webhook, n8n, Make...).

**Request**:
```http
POST /send HTTP/1.1
Content-Type: application/json
x-api-key: {ZALO_SEND_API_KEY}

{
  "recipients": ["1234567890", "9876543210"],
  "message": "🎉 Đơn hàng mới — Nguyễn Văn A 499.000đ",
  "type": "user"   // hoặc "group"
}
```

**Response**:
```json
{
  "ok": true,
  "sent": 2,
  "failed": []
}
```

**Errors**:
- `401` — API key sai
- `400` — thiếu recipients hoặc message
- `500` — Zalo gửi fail (chi tiết trong `failed` array)

---

## API: GET /health

Healthcheck cho UptimeRobot ping.

```http
GET /health
```

```json
{
  "status": "ok",
  "zalo": "connected",
  "uptime_seconds": 12345
}
```

---

## Deploy production

Xem `references/deployment-railway.md` trong skill folder để deploy lên Railway step-by-step.

Tóm tắt:
1. Push project lên GitHub PRIVATE repo
2. Railway → New Project → Deploy from GitHub
3. Set env vars trong Railway dashboard
4. Generate public domain
5. Setup UptimeRobot ping `/health` mỗi 5 phút

---

## Maintenance

- **Cookies expire mỗi ~30 ngày** → khi listener crash với `cookies invalid`, extract lại từ Chrome
- **Knowledge update**: edit `.md` trong `zalo-knowledge/` → push GitHub → Railway auto-redeploy
- **Đổi model**: sửa `OPENROUTER_MODEL` env → restart service
- **Review log hằng tuần**: check tin nhạy cảm bot fallback đúng không
