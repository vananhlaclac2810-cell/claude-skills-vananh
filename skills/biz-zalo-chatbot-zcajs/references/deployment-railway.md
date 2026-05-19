# Deployment Railway — Deploy zalo-listener lên Railway step-by-step

Hướng dẫn deploy `zalo-listener/` (Node.js long-running) lên Railway cho non-developer.

> **Tại sao Railway, không phải Vercel?** Vercel serverless function timeout 60s, không hỗ trợ WebSocket persistent. zca-js cần kết nối WebSocket liên tục với chat.zalo.me — Vercel KHÔNG chạy được.
>
> **Tại sao Railway, không phải Render?** Render free tier auto-sleep sau 15 phút inactive → bot offline → khách nhắn không reply. Render paid $7/tháng thì persistent nhưng workflow phức tạp hơn. Railway free trial $5 credit + persistent ngay = path of least resistance cho non-dev.
>
> **Tại sao Railway, không phải VPS (DigitalOcean/Vultr)?** VPS rẻ hơn ($4-6/tháng) nhưng cần biết Linux, SSH, PM2, systemd, nginx reverse proxy. Quá khó cho non-dev.

---

## Tổng quan chi phí

| Plan | Chi phí | Phù hợp |
|---|---|---|
| Free trial Railway | $5 one-time credit (~1 tháng) | Thử nghiệm 1-2 tuần |
| Hobby Railway | $5/tháng + usage (~$5-10/tháng total) | Production, traffic nhỏ |
| Render Starter | $7/tháng flat | Alternative nếu Railway không phù hợp |
| VPS DigitalOcean | $4/tháng flat | Cần biết Linux |

**Recommend**: bắt đầu Railway free trial. Hết trial → quyết định stay Railway hay migrate.

---

## Bước 1 — Tạo Railway account

```
1. Vào https://railway.app
2. Click "Login" góc phải trên → Sign up with GitHub
3. Authorize Railway access GitHub
4. Railway redirect về dashboard
5. Verify email
6. Free trial $5 credit tự động được apply (không cần nhập card)
```

**Lưu ý**: 
- Railway YÊU CẦU GitHub account. Nếu chị chưa có → tạo tại https://github.com/signup (miễn phí, 5 phút)
- Railway sẽ ask add credit card sau khi hết trial. Có thể skip, listener sẽ pause khi hết credit.

---

## Bước 2 — Push `zalo-listener/` lên GitHub

### 2.1 Cài GitHub CLI (nếu chưa có)

```bash
# Windows (PowerShell admin)
winget install --id GitHub.cli

# Verify
gh --version
```

### 2.2 Login GitHub CLI

```bash
gh auth login
# Chọn: GitHub.com → HTTPS → Login with browser → paste mã
```

### 2.3 Init repo + push

```bash
cd zalo-listener

# Đảm bảo .env KHÔNG bị commit (skill đã tạo .gitignore)
cat .gitignore | grep ".env"   # Phải thấy ".env"

git init
git add .
git commit -m "init zalo listener"

# Tạo repo PRIVATE trên GitHub + push
gh repo create zalo-listener --private --source=. --push
```

**Output**:
```
✓ Created repository owner/zalo-listener on GitHub
✓ Added remote https://github.com/owner/zalo-listener.git
✓ Pushed commits to https://github.com/owner/zalo-listener.git
```

⚠️ Tuyệt đối tạo **private repo** — nếu public, ai cũng đọc được code (dù .env không commit, vẫn có template + logic).

---

## Bước 3 — Connect Railway → GitHub repo

```
1. Railway dashboard → click "New Project"
2. Chọn "Deploy from GitHub repo"
3. Railway hỏi quyền access repo → "Configure" → chọn "Only select repositories" → tick "zalo-listener" → Save
4. Quay lại Railway, refresh → list repo hiện ra → click "zalo-listener"
5. Railway tự detect Node.js project → start build
```

Build log hiện trong panel:
```
[builder] Detected Node.js
[builder] Running npm install
[builder] Running npm start
[runtime] [zalo] Login OK, account: Trợ lý Dr.Maya
[runtime] [server] Listening on :3001
```

**Nếu build fail**:
- `EACCES: permission denied` → check `package.json` `"start"` script đúng (`node index.js`)
- `Cannot find module 'zca-js'` → run `npm install` local trước, commit lại với `package-lock.json`
- `ZALO_COOKIES_JSON is undefined` → chưa set env vars (Bước 4)

---

## Bước 4 — Set env vars trên Railway

```
1. Railway project → click vào service "zalo-listener"
2. Tab "Variables"
3. Click "+ New Variable" cho từng biến:
```

Paste theo bảng:

| Variable | Value | Note |
|---|---|---|
| `ZALO_COOKIES_JSON` | `[{"domain":".zalo.me","name":"zpsid",...}]` | Paste 1 dòng JSON, KHÔNG newline |
| `ZALO_IMEI` | `abcd1234-ef56-...` | Từ `localStorage.getItem('z_uuid')` |
| `ZALO_USER_AGENT` | `Mozilla/5.0 ...` | Từ `navigator.userAgent` |
| `OPENROUTER_API_KEY` | `sk-or-v1-xxxxx` | Từ https://openrouter.ai/keys |
| `OPENROUTER_MODEL` | `google/gemini-3-flash-preview` | Hoặc `anthropic/claude-sonnet-4.6` |
| `BRAND_NAME` | `Dr.Maya` | Brand name hiển thị trong tin reply |
| `BOT_TONE` | `than_thien_anh_chi` | Hoặc `formal_quy_khach` |
| `ZALO_SEND_API_KEY` | `random-string-32-chars-or-longer` | Generate bằng `openssl rand -hex 24` |
| `SEND_PORT` | `3001` | Port Express server |
| `ZALO_NOTIFY_RECIPIENTS` | `1234567890,9876543210` | CSV Zalo user_id của owner / sale |

**Cách generate random API key** (PowerShell):
```powershell
[Convert]::ToHexString((1..24 | ForEach-Object {Get-Random -Max 256}))
```

Hoặc dùng https://www.random.org/strings/?num=1&len=48&digits=on&upperalpha=on&loweralpha=on

**Sau khi save**:
- Railway tự redeploy với env mới
- Build log phải show "[zalo] Login OK" — nếu show "cookies invalid" → cookies sai

---

## Bước 5 — Generate public domain

Mặc định Railway service KHÔNG có public URL (chỉ internal). Phải generate:

```
1. Railway project → service "zalo-listener" → tab "Settings"
2. Section "Networking" → "Public Networking"
3. Click "Generate Domain"
4. Railway tạo URL kiểu: https://zalo-listener-production-abc1.up.railway.app
5. COPY URL này
```

**Test public URL**:

```bash
curl https://zalo-listener-production-abc1.up.railway.app/health

# Expect:
# {"status":"ok","zalo":"connected","uptime":123}
```

Nếu fail → check logs (Railway dashboard → "Logs" tab) xem listener có start không.

---

## Bước 6 — Update Vercel với URL listener

Trong project Next.js (Vercel):

```
1. Vercel dashboard → project → Settings → Environment Variables
2. Add 2 biến:
   - ZALO_LISTENER_URL = https://zalo-listener-production-abc1.up.railway.app
   - ZALO_SEND_API_KEY = (cùng key với Railway)
3. Tick "Production" + "Preview" + "Development"
4. Save → Vercel auto-redeploy
```

---

## Bước 7 — Test end-to-end

```bash
# Test gửi tin Zalo từ Vercel
curl -X POST https://yourdomain.vercel.app/api/zalo-notify \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ZALO_SEND_API_KEY" \
  -d '{
    "recipients": ["1234567890"],
    "message": "🎉 Test deploy thành công!"
  }'

# Expect:
# - Response: {"ok":true}
# - Zalo của owner nhận tin "Test deploy thành công"
```

---

## Monitoring + Maintenance

### Setup UptimeRobot ping listener

Free service ping `/health` endpoint mỗi 5 phút, alert email/SMS khi down:

```
1. Vào https://uptimerobot.com → Sign up (free)
2. Add New Monitor → HTTP(s)
3. URL: https://zalo-listener-production-abc1.up.railway.app/health
4. Interval: 5 minutes
5. Alert contact: Email + SMS (số phụ owner)
```

Khi listener down → nhận alert trong 5-10 phút → re-deploy.

### Railway log review

Mỗi tuần check log 1 lần:
```
Railway dashboard → service → Logs tab → filter "error" hoặc "warn"
```

Pattern cần để ý:
- `cookies invalid` → cookies sắp expire, extract lại
- `rate limit hit` → bot gửi quá nhanh, check rate limit logic
- `LLM response empty` → OpenRouter có thể bị hết credit, top up

### Rotate keys mỗi 3 tháng

- `OPENROUTER_API_KEY`: tạo key mới ở openrouter.ai/keys → update Railway → revoke key cũ
- `ZALO_SEND_API_KEY`: generate random mới → update cả Railway + Vercel cùng lúc

---

## Migrate sang Render (nếu Railway hết phù hợp)

Render cũng tốt nếu chị muốn flat $7/tháng predictable thay vì usage-based Railway:

```
1. https://render.com → Sign up GitHub
2. New → Web Service → Connect GitHub repo "zalo-listener"
3. Plan: Starter $7/month (KHÔNG dùng free — sleep sau 15p)
4. Build Command: npm install
5. Start Command: node index.js
6. Add Environment Variables (paste như Bước 4 Railway)
7. Deploy
```

URL Render dạng: `https://zalo-listener.onrender.com`

Update `ZALO_LISTENER_URL` trong Vercel → done.

---

## Troubleshooting deployment

| Lỗi | Nguyên nhân | Fix |
|---|---|---|
| Build success nhưng "[zalo] Login failed" | Cookies/imei/userAgent sai hoặc Zalo đang block IP datacenter | Re-extract cookies từ Chrome cá nhân; nếu vẫn fail, thử proxy residential |
| `[server] EADDRINUSE :3001` | Port 3001 bị giữ bởi process cũ | Restart service trên Railway |
| Healthcheck fail timeout | Listener crash silent | Check logs, có thể OOM (out of memory) — upgrade plan Railway |
| Webhook /send trả 401 | API key Vercel khác với Railway | Verify 2 nơi cùng `ZALO_SEND_API_KEY` |
| Logs spam "rate limit hit" | Listener nhận quá nhiều tin cùng lúc | Tăng rate limit từ 1/s lên 2/s nếu cần, hoặc add queue |
| Railway billing alert "low credit" | Hết free trial $5 | Top up credit hoặc migrate Render |

---

## Tóm tắt — Checklist deploy

Trước khi deploy production:
- [ ] Listener test local pass (`npm run test:login` + `npm start` reply OK)
- [ ] `.env` đầy đủ 11 biến, KHÔNG commit lên Git
- [ ] `.gitignore` có `.env`, `node_modules`, `*.log`
- [ ] GitHub repo PRIVATE (không public)
- [ ] Railway service running 24h không crash
- [ ] Health endpoint `/health` return 200 OK
- [ ] UptimeRobot ping every 5 minutes setup
- [ ] Vercel env `ZALO_LISTENER_URL` + `ZALO_SEND_API_KEY` matched
- [ ] Test gửi tin từ Vercel → Zalo nhận
- [ ] Backup cookies + imei + userAgent vào password manager
