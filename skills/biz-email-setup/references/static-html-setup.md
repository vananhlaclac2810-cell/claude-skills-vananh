# Static HTML + Vite Setup — Wiring chi tiết

Static HTML site (chỉ `index.html` + assets) hoặc Vite project (React/Vue/Svelte SPA) không có server-side. Để gửi email cần **Vercel serverless function** — Vercel tự host function ở `/api/*` mà không cần backend framework.

---

## Project structure sau khi setup

```
your-landing/
├── index.html                  # landing page (đã có)
├── styles.css                  # (đã có)
├── script.js                   # (đã có)
├── api/
│   └── submit.js               # NEW — serverless function
├── package.json                # NEW — chỉ để declare resend dependency
├── vercel.json                 # NEW (optional) — function config
└── .env.local                  # NEW — env vars (NOT commit)
```

---

## Bước 1 — Tạo `package.json` (nếu chưa có)

Static HTML site thường không có `package.json`. Tạo mới ở root:

```json
{
  "name": "landing-page",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "resend": "^4.0.0"
  }
}
```

Sau đó:
```bash
npm install
# hoặc pnpm install
```

→ tạo `node_modules/` và `package-lock.json`.

**Add vào .gitignore**:
```gitignore
node_modules/
.env*.local
```

---

## Bước 2 — Tạo serverless function

```bash
mkdir -p api
```

Copy `templates/api-route-vercel-function.js` → `api/submit.js`.

Sau đó thay placeholder `{{PRODUCT_NAME}}`, `{{BRAND_NAME}}`, etc. theo context Phase 1.

**Vercel auto-detect**: bất kỳ file `.js`/`.ts` trong folder `api/` đều thành serverless endpoint tại path `/api/<filename>`. Không cần config gì thêm.

---

## Bước 3 — (Optional) Tạo `vercel.json` cho function config

Nếu muốn tweak runtime hoặc maxDuration:

```json
{
  "functions": {
    "api/submit.js": {
      "maxDuration": 10
    }
  }
}
```

Default `maxDuration` là 10s, đủ cho 2 email Resend (mỗi cái <1s).

---

## Bước 4 — Wire form trong `index.html`

Mở `index.html`, tìm `<form>` hiện tại. 2 trường hợp:

### Case A: Đã có `<form>` với fields tên/SĐT/email

Replace nguyên block form bằng snippet trong `templates/form-binding-vanilla.html`. Snippet bao gồm:
- Form HTML với 3 input + button
- Inline CSS (có thể merge vào file css chính)
- Inline `<script>` xử lý submit + fetch /api/submit

### Case B: Chưa có form

Paste snippet vào section CTA. Ví dụ:

```html
<section id="cta" class="cta-section">
  <h2>{{CTA_HEADING}}</h2>
  <p>{{CTA_SUBHEADING}}</p>

  <!-- Paste form-binding-vanilla.html ở đây -->
</section>
```

**Quan trọng — charset UTF-8**: kiểm tra `<head>` của `index.html` có:
```html
<meta charset="UTF-8" />
```
Thiếu → tên tiếng Việt bị mojibake (xem `troubleshooting.md` #5).

---

## Bước 5 — Env vars

### Local dev với `vercel dev`

Tạo `.env.local`:
```env
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxx
RESEND_FROM_EMAIL=hello@yourbrand.vn
RESEND_OWNER_EMAIL=hoang.tran@prediction3d.com
LANDING_PAGE_URL=https://yourbrand.vn
```

Chạy local dev:
```bash
npm install -g vercel  # nếu chưa
vercel dev             # serve static + serverless function
```

→ mở `http://localhost:3000` test form thực tế.

**Không thể test bằng `python -m http.server` hoặc Live Server** vì những tool đó không chạy serverless function.

### Production

Vercel dashboard → Project → Settings → Environment Variables → add 4 keys → **Redeploy**.

---

## Bước 6 — Deploy

Trong skill chính, suggest user chạy `/biz-deploy-vercel`. Hoặc manual:

```bash
vercel --prod
```

Vercel auto-detect static HTML + serverless function trong `api/`. Không cần build step.

---

## Vite project (React/Vue/Svelte SPA)

Vite gần giống static HTML — không có server-side. Khác biệt:
- Project structure có `src/`, `index.html` ở root, build ra `dist/`.
- Resend wire vào `api/submit.js` cùng cấp với `vite.config.ts`.

```
your-vite-app/
├── index.html
├── vite.config.ts
├── src/
│   ├── App.tsx
│   ├── components/
│   │   └── LeadForm.tsx       # dùng templates/form-binding-react.tsx
│   └── main.tsx
├── api/
│   └── submit.js              # NEW — Vercel serverless function
├── package.json
└── vercel.json (optional)
```

`package.json` của Vite đã có rồi, chỉ cần `npm install resend`.

Trong React component, import + dùng `LeadForm` giống Next.js:
```tsx
// src/App.tsx
import LeadForm from "./components/LeadForm";

function App() {
  return (
    <main>
      {/* ... */}
      <LeadForm />
    </main>
  );
}
```

Vite **không có** `"use client"` directive (đó là Next.js App Router only). Xoá dòng đó khỏi `templates/form-binding-react.tsx` khi copy vào Vite project.

---

## Anti-pattern

- ❌ Cài Resend SDK qua CDN trong `<script>` tag của index.html → Resend SDK là server-side, không chạy được trong browser. Phải qua serverless function.
- ❌ Gọi Resend API trực tiếp từ frontend JS với API key trong client → expose key cho ai cũng đọc được, hacker dùng key gửi spam, account ban. Luôn proxy qua `/api/submit`.
- ❌ Quên `npm install` trước khi deploy → Vercel build sẽ fail vì thiếu `resend` package.
- ❌ Đặt `submit.js` ở `/api/v1/submit.js` rồi gọi `/api/submit` → 404. Path phải khớp file location.
