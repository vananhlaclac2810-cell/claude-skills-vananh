# Troubleshooting — Resend Form Autoresponder

5 vấn đề thường gặp nhất + fix.

---

## 1. Email vào spam folder

**Triệu chứng**: Test ok, email gửi đi nhưng Gmail/Outlook đẩy vào Spam/Promotions.

**Nguyên nhân + fix theo thứ tự xác suất**:

1. **Domain chưa verify** → đang gửi từ `onboarding@resend.dev` (shared sender pool). Fix: verify domain (xem `domain-verification.md`).
2. **Thiếu SPF/DKIM** dù đã add domain → re-check DNS bằng `dig`. Cả hai phải có.
3. **Subject spam-y**: ALL CAPS, "FREE!!!", "$$$", "Act now", "100% guarantee". Fix: rewrite subject natural hơn.
4. **Body có nhiều link / chỉ 1 image full-width** → spam filter nghi ngờ. Fix: < 3 links, có cả text giải thích.
5. **Sending từ generic alias** `noreply@` → tốt hơn dùng `hello@` hoặc tên người thật `tony@`.
6. **Reply-to khác from**: nếu set reply-to khác domain → fail DMARC. Fix: reply-to cùng domain với from.
7. **Lead mark spam lần đầu** → ISP nhớ ngữ cảnh "brand này không welcome" → kéo cả pool xuống. Khó fix, chỉ phòng ngừa bằng content tốt.

**Test deliverability**: gửi test tới 3 email khác nhau (Gmail, Outlook, Yahoo), check folder. Hoặc dùng [mail-tester.com](https://www.mail-tester.com) — gửi 1 email tới address họ cho, họ trả score 0-10. Mục tiêu > 8/10.

---

## 2. API endpoint trả 500

**Triệu chứng**: Form submit, browser hiện error "Có lỗi gửi form".

**Check theo thứ tự**:

1. **Console log Vercel**: Vercel dashboard → Project → Logs → filter `/api/submit`. Đọc error message.
2. **Env var RESEND_API_KEY** thiếu/sai → log thường thấy `Resend: Invalid API key`. Fix: copy lại key từ resend.com → paste vào Vercel env vars → redeploy.
3. **Env var không sync sau khi add**: Vercel cần **redeploy** sau khi thêm env var (không hot-reload). Trigger redeploy: push commit mới hoặc Vercel dashboard → Deployments → "..." → Redeploy.
4. **Domain not verified** → Resend throw `Domain not verified, can't send from <email>`. Fix: verify hoặc tạm dùng `onboarding@resend.dev`.
5. **Rate limit**: free tier 100 email/ngày, 10/giây. Burst test có thể trigger. Fix: đợi 60s rồi retry.
6. **Recipient blocked**: nếu owner email là `@gmail.com` và Resend từng bị Gmail block → vào Resend → Settings → Suppression list.

---

## 3. Form submit không trigger gì cả

**Triệu chứng**: Click submit, không có loading state, không có error, không có gì xảy ra.

**Check**:

1. **Browser console**: F12 → Console tab. Tìm error JS. Thường gặp `fetch is not defined` (browser quá cũ) hoặc CORS error.
2. **Network tab**: F12 → Network → Submit form → có request `/api/submit` không? 
   - Nếu không có request → JS event listener fail. Check `<form onSubmit>` hoặc `addEventListener` syntax.
   - Nếu có request status 404 → API route chưa deploy. Run `vercel --prod` lại.
   - Nếu có request status 405 → method GET thay vì POST. Check fetch config.
3. **API route file location đúng chưa**:
   - Next.js App: `app/api/submit/route.ts` (folder tên `submit`, file tên `route.ts`)
   - Next.js Pages: `pages/api/submit.ts`
   - Vite/Static: `api/submit.js` ở root project (không trong `src/`)
4. **Vercel function config**: nếu deploy static + serverless, cần `vercel.json`:
```json
{ "functions": { "api/*.js": { "maxDuration": 10 } } }
```

---

## 4. Email gửi đi nhưng owner không nhận notification

**Triệu chứng**: Lead nhận email auto-responder OK, nhưng owner không thấy email mới.

**Check**:

1. **Env var `RESEND_OWNER_EMAIL`** đúng chưa → typo phổ biến.
2. **Owner email là alias** (ví dụ `info@brand.vn` forward sang Gmail) → check folder Gmail "All Mail" hoặc spam.
3. **Owner email cùng domain với FROM** → một số ISP filter "self-sending" làm spam. Fix: `from=hello@brand.vn`, `to=hoang.tran@gmail.com` (Gmail cá nhân khác domain).
4. **Resend log**: vào dashboard → Emails → search by recipient. Nếu thấy status `Delivered` nhưng owner không nhận → 99% là vào spam.
5. **`replyTo` set sai**: nếu set `replyTo: lead_email` cho email B → owner reply về sẽ về lead (đúng intent). Nhưng nếu set `replyTo: owner_email` cho email A → lead reply về owner (cũng OK). Confusion thường ở đây.

---

## 5. Tên/SĐT tiếng Việt hiển thị lỗi font (mojibake)

**Triệu chứng**: Email hiện "Nguy?n Vˆn A" thay vì "Nguyễn Văn A".

**Nguyên nhân**: charset encoding sai ở 1 trong các bước:
1. Form HTML thiếu `<meta charset="UTF-8">` → input bị mã hoá Latin-1.
2. API route không parse JSON đúng → body bị corrupt.
3. Email template thiếu `<meta charset="UTF-8">` trong `<head>`.

**Fix**:
- HTML form: `<meta charset="UTF-8" />` trong `<head>` của landing page.
- API route: dùng `await req.json()` (Next.js) hoặc `JSON.parse(req.body)` (Vercel function), không tự parse text.
- Email template: header `Content-Type: text/html; charset=UTF-8` — Resend SDK tự set, nhưng nếu inline HTML phải có `<meta charset="UTF-8">`.

---

## Quick sanity check trước khi blame Resend

```bash
# 1. API key đúng không
curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "onboarding@resend.dev",
    "to": "your-email@gmail.com",
    "subject": "Resend test",
    "html": "<p>Hello from Resend</p>"
  }'

# Expect: {"id":"..."}
# Nếu trả 401 → API key sai
# Nếu trả 422 → from address không verified
```

Pass step này = Resend setup OK, vấn đề nằm ở app code.
