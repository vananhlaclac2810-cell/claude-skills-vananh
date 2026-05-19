---
name: biz-email-setup
description: "Setup Resend email auto-responder cho landing page bán hàng — tự động gửi email sau khi user điền form (tên/SĐT/email). Skill này (1) cài Resend SDK và Vercel serverless function/Next.js API route phù hợp với stack đang dùng, (2) đọc context từ `offer.json` + `conversion-copy.md` (từ `/biz-offer-alex-hormozi`) HOẶC đọc trực tiếp Next.js project đã build qua `ui-ux-pro-max` (file `app/page.tsx`) HOẶC đọc HTML landing page đã deploy để hiểu offer, dream outcome, mechanism, bonus. Lưu ý: skill `biz-sales-page-layout` đã DEPRECATED 2026-05-14 — pipeline mới skip layout/copy.json, (3) **draft 2 email**: email A — auto-responder gửi cho lead (warm welcome + deliver lead magnet/booking confirm/payment link tuỳ offer type), email B — notification gửi cho owner (lead alert + thông tin liên hệ), (4) **show draft cho user duyệt và chỉnh sửa** trước khi wire vào code, (5) wire form HTML/React lên API endpoint với SPF/DKIM domain verification guide, (6) suggest deploy lại qua `/biz-deploy-vercel`. Output: code patch + env vars list + test instructions + email preview HTML. Tiếng Việt thuần (xưng anh/chị), mobile-responsive email template, charm pricing VND. USE WHEN user says: 'setup resend', 'tích hợp resend', 'gửi email sau khi user điền form', 'auto-responder cho landing page', 'thank you email tự động', 'email confirmation cho lead', 'wire form to email', 'gửi email khi có lead', 'resend api setup', 'làm sao gửi email từ landing page', 'lead nurture email', 'biz-email-setup', 'sau khi deploy landing page muốn gửi email', 'form submission gửi mail', 'email tự động sau khi đăng ký', 'connect form to email service', 'transactional email setup'. Cũng trigger khi user vừa chạy xong `/biz-deploy-vercel` và muốn bước tiếp theo wire email; hoặc user có landing page đã deploy nhưng form chưa gửi email đi đâu. Skill này KHÔNG làm: email marketing broadcast/newsletter (đó là Mailchimp/ConvertKit/MailerLite use case); SMS auto-responder (skill khác); CRM integration (Hubspot/Pipedrive — skill khác); cold email outreach (đó là Instantly/Smartlead). Skill này chuyên transactional/auto-responder trigger từ form submission."
---

# Biz Resend Form Autoresponder — Auto-email sau khi lead điền form

Skill này biến **form đăng ký trên landing page** (tên/SĐT/email theo chuẩn VN traffic) thành **2 email tự động** ngay khi user submit: (A) email warm welcome gửi cho lead, (B) email notification gửi cho owner. Email được **draft riêng cho từng offer** dựa vào context có sẵn từ pipeline biz-* (không generic "Cảm ơn anh/chị đã đăng ký, chúng tôi sẽ liên hệ sớm" — đó là copy đốt lead).

> **Triết lý**: Email auto-responder là moment vàng. Lead vừa nhấn nút submit = đang ở peak intent. Email đến trong 30 giây phải (1) confirm họ submit đúng, (2) deliver thứ đã promise trong CTA (lead magnet / booking / payment link), (3) set expectation rõ bước tiếp theo. Một email auto-responder tốt = chuyển 20-40% lead nguội thành lead nóng. Một email generic = lead block sender hoặc forget tên brand trong 24h.
>
> **Tại sao Resend chứ không phải Gmail SMTP**: Gmail SMTP giới hạn 500/ngày, dễ bị Google flag spam, deliverability thấp khi gửi đến Outlook/Yahoo. Resend có free tier 3,000 email/tháng, deliverability cao (tier-1 IP pool), API gọn (1 function call), domain verification 10 phút, có log/replay/webhook — đáng setup từ đầu thay vì migrate sau.

Output skill: code patch + 2 email draft HTML responsive + env vars list + test plan. **Skill KHÔNG tự gửi test email** — user phải confirm draft trước, vì lead magnet link, brand voice, urgency wording đều thuộc tài sản của user.

---

## Khi nào dùng skill này

- User vừa deploy landing page xong (qua `/biz-deploy-vercel`) và form đang submit vào hư không.
- User có landing page sẵn (Next.js, Vite, hoặc static HTML trên Vercel) và muốn wire email auto-responder.
- User đang build mới và muốn email integration ngay từ đầu trước khi deploy.
- User hỏi "làm sao gửi email khi có lead mà không dùng Gmail SMTP".

**KHÔNG dùng skill này khi:**
- User muốn email marketing broadcast (newsletter, drip campaign 7-30 ngày) → Mailchimp/ConvertKit/MailerLite phù hợp hơn.
- User muốn SMS/Zalo OA auto-responder → use case khác.
- User muốn CRM tích hợp (lead vào Hubspot/Pipedrive/Notion DB) → skill khác.
- User cần cold email outreach hàng loạt → Instantly/Smartlead, không phải transactional.

---

## Workflow tổng quan (7 phase)

```
Phase 0: DETECT PROJECT STACK (Next.js App / Pages / Vite / static HTML)
       ↓
Phase 1: GATHER CONTEXT (offer.json + conversion-copy.md, hoặc đọc Next.js app/page.tsx, hoặc đọc HTML đã deploy)
       ↓
Phase 2: PICK EMAIL PATTERN (lead magnet / booking / payment / nurture)
       ↓
Phase 3: DRAFT 2 EMAIL (auto-responder + owner notification) — show user
       ↓
Phase 4: USER REVIEW & EDIT — iterate cho đến khi user duyệt
       ↓
Phase 5: WIRE CODE (install SDK + API route + form binding + env vars)
       ↓
Phase 6: DOMAIN VERIFY + TEST PLAN — hướng dẫn add DNS record, test live
```

Mỗi phase **dừng để user xác nhận** — đặc biệt Phase 3-4 (email content) và Phase 6 (domain DNS) vì đó là tài sản brand của user. Code generation ở Phase 5 thì skill chủ động hơn.

---

## Phase 0 — Detect Project Stack

Đọc file root của project để xác định stack. Stack quyết định: API route đặt ở đâu, syntax import Resend SDK, kiểu form binding (fetch hay form action).

| File phát hiện | Stack | API route path | Form binding |
|---|---|---|---|
| `next.config.js/mjs/ts` + `app/` folder | **Next.js App Router** | `app/api/submit/route.ts` | client component `fetch('/api/submit')` |
| `next.config.js/mjs/ts` + `pages/` folder | **Next.js Pages Router** | `pages/api/submit.ts` | client component `fetch('/api/submit')` |
| `vite.config.js/ts` | **Vite (React/Vue/Svelte)** | `api/submit.js` (Vercel function) | client component `fetch('/api/submit')` |
| `package.json` không có framework, có `index.html` | **Static HTML** | `api/submit.js` (Vercel function) | inline `<script>` với `fetch('/api/submit')` |
| Không có project local, chỉ có URL | **Existing deployed page** | Cần user clone repo trước hoặc chỉ ra repo path | — |

**Đọc thêm để xác định form fields**:
- Tìm `<form>` trong code → liệt kê các `<input name="...">` đã có
- Default expected (per project memory): `name`, `phone`, `email`. Một số page thêm: `company`, `message`, `budget`, `utm_source`.
- Nếu form chưa có → skill sẽ tạo form mới với 3 field tối thiểu (tên/SĐT/email) trong Phase 5.

**Quan trọng**: Nếu user chưa có project local (chỉ deploy được URL), dừng lại hỏi: *"Anh/chị có repo local để em wire code không? Em cần edit file source. Nếu chỉ có URL, anh/chị clone repo về và chỉ em đường dẫn nhé."* Không thể wire chỉ qua URL.

---

## Phase 1 — Gather Context

Mục tiêu: hiểu offer đủ sâu để draft email không generic. 3 mode input:

### Mode A — Có pipeline artifacts (richest)
User vừa chạy `/biz-offer-alex-hormozi` và/hoặc `ui-ux-pro-max` → có file:
- `output/<case-slug>/offer.json` — segment, dream outcome, mechanism, bonus stack, guarantee, pricing (PRIMARY source of truth)
- `output/<case-slug>/conversion-copy.md` — hero block paste-ready (headline, subhead, CTA wording)
- `output/<case-slug>/landing-page/app/page.tsx` — Next.js sales page hiện tại đã build (đọc để biết sections + form fields đang dùng)

> ⚠️ **Update 2026-05-14:** Pipeline cũ có `layout.json` + `copy.json` (từ `biz-sales-page-layout` đã DEPRECATED) — quy trình mới SKIP 2 file đó. Chỉ cần `offer.json` + đọc page.tsx là đủ context.

**Đọc 3 source trên**. Trích ra cho email:
- **Segment + dream outcome** → personalize subject line ("[Tên], lộ trình AI Agent 8 tuần đã sẵn sàng" thay vì "Welcome")
- **Mechanism name** → reinforce trong body ("Hệ thống PROMPT framework anh/chị sắp học...")
- **Bonus stack** → list trong email (nếu offer free/low-ticket có bonus deliver ngay)
- **Guarantee text** → quote nguyên trong email để giảm anxiety
- **CTA wording** → mirror trong email final CTA

### Mode B — Có landing page nhưng không có json
User có HTML deployed nhưng không chạy biz-offer/biz-sales-page. Skill đọc HTML:
- `curl -s <URL>` hoặc đọc file `index.html` local
- Parse hero h1, subheading, CTA button text, pricing block, guarantee block
- Từ đó infer offer type + segment

Mode B đủ tốt 80% case nhưng email kém personalized hơn Mode A. **Suggest user**: "Có thể chạy `/biz-offer-alex-hormozi` để có offer.json rồi quay lại đây, email sẽ chất hơn. Hoặc tiếp tục Mode B."

### Mode C — Không có gì
User chỉ có form HTML, chưa có context. Skill phải phỏng vấn 5 câu nhanh:
1. Sản phẩm/dịch vụ anh/chị bán là gì? (1 câu)
2. Sau khi user điền form, anh/chị muốn gửi cho họ thứ gì? (PDF tải về / link booking / link payment / chỉ confirm và sẽ gọi sau)
3. Tên brand + tên người gửi (sẽ hiện trong "From:")
4. Email anh/chị muốn nhận notification lead mới
5. Domain anh/chị sở hữu để Resend verify (ví dụ: yourbrand.vn)

---

## Phase 2 — Pick Email Pattern

**Mô hình 2-trigger (cho offer có checkout flow)**: Với low-ticket course / digital product có thanh toán online, có **2 trigger điểm khác nhau, gửi 2 email khác nhau**. Đừng gộp vào 1 email duy nhất.

```
Lead điền form trên landing page
         ↓
   [Trigger A — /api/submit]
         ↓
   Email P3 (PRE-PAYMENT REMINDER, slim)
         ↓
Lead thanh toán xong → payment provider webhook
         ↓
   [Trigger B — /api/payment-webhook]
         ↓
   Email P5 (POST-PURCHASE ONBOARDING, full)
```

**Quy tắc nội dung**:
- **P3 (pre-payment)**: chỉ có payment link + guarantee ngắn + urgency. **KHÔNG** list full deliverables/bonus stack — lead chưa "earn" được, list ra giảm urgency thanh toán.
- **P5 (post-payment)**: deliver TOÀN BỘ — access link, full deliverables, bonus stack, group link, lịch office hour, **1 câu hỏi follow-up** để personalize. Đây mới là moment vàng.

(Đọc memory `feedback_email-autoresponder-2-stage-flow` cho rationale chi tiết.)

---

Từ context Phase 1, chọn pattern phù hợp. Đọc `references/email-formulas.md` cho template chi tiết tiếng Việt.

| Pattern | Trigger | Khi nào dùng | Subject hint |
|---|---|---|---|
| **P1 — Lead Magnet Delivery** | Form submit | Offer = tải PDF/ebook/template/swipe file/checklist free | "[Tên], tài liệu [X] đã sẵn sàng — mở file ngay 👇" |
| **P2 — Booking Confirmation** | Form submit | Offer = đặt lịch call/consultation/demo/free strategy session | "[Tên], đã ghi nhận đăng ký buổi tư vấn — bước tiếp theo bên trong" |
| **P3 — Pre-Payment Reminder** | Form submit (chưa pay) | Offer = sản phẩm low-ticket (199K-3M VND), email dẫn về checkout | "[Tên], link thanh toán [Khóa X] — giữ giá ưu đãi 24h ⏰" |
| **P4 — Nurture (Sale call upcoming)** | Form submit | Offer = high-ticket coaching/agency 5M-50M+ VND, sales team sẽ call trong 24h | "[Tên], em [Người gọi] sẽ liên hệ trong 24h — checklist chuẩn bị bên trong" |
| **P5 — Post-Purchase Onboarding** | **Payment webhook** | Lead vừa thanh toán xong — deliver full value + 1 câu hỏi personalize | "🎉 Chào mừng [Tên] vào [Khóa X] — mở khoá ngay" |

**Quy tắc chọn pattern**:
- Offer = free download/training → **P1 only** (1 trigger, 1 email).
- Offer = booking call free → **P2 only** (1 trigger, 1 email).
- Offer = low-ticket có thanh toán online (Stripe/Momo/ZaloPay/Sepay) → **P3 + P5** (2 trigger, 2 email).
- Offer = high-ticket sale call → **P4 only**, follow-up qua sales team (onboarding sau khi close deal là 1 process khác).

Skill **đề xuất pattern phù hợp + lý do**, hỏi user confirm. Ví dụ: *"Dựa vào offer.json em thấy đây là khoá 1.99M VND có payment integration. Em đề xuất setup **2 email**: P3 (nhắc thanh toán khi điền form) + P5 (onboarding sau khi pay xong + 1 câu hỏi personalize). Anh/chị đồng ý hay chỉ muốn 1 email P3 trước?"*

---

## Phase 3 — Draft 2 Email

Generate **2 email tiếng Việt thuần** (xưng anh/chị), mobile-responsive HTML.

### Email A — Auto-responder gửi cho lead

Cấu trúc 6 block (đọc `references/email-formulas.md` cho wording cụ thể per pattern):

1. **Subject line** — personalized với `{{name}}`, ngắn dưới 50 ký tự, có 1 emoji nhẹ ở cuối nếu phù hợp brand voice (✉️ 👇 ✓), tránh spam trigger ("FREE", "$$$", "guarantee" caps).
2. **Preview text** — 1 câu hiển thị dưới subject trong inbox, giải thích value email mở ra.
3. **Greeting** — "Chào anh/chị {{name}}," — không "Dear", không "Xin chào quý khách".
4. **Body chính** — theo pattern đã chọn. Quy tắc:
   - Ngắn (dưới 200 từ).
   - Có 1 link/button CTA primary rõ ràng.
   - Reference cụ thể tên offer/mechanism từ context (không "sản phẩm của chúng tôi").
   - Nếu Pattern P3/P4 → có 1 urgency reminder + 1 reassurance (guarantee).
5. **Signature** — Tên người gửi + tên brand + 1 link contact (Zalo/Phone/Website).
6. **Footer** — Address (luật anti-spam yêu cầu) + unsubscribe link (cần cho compliance, dù transactional cũng nên có).

### Email B — Notification gửi cho owner

Cấu trúc gọn (owner cần info nhanh, không cần style):

```
Subject: 🔥 Lead mới — {{name}} ({{phone}}) — {{landing_page_slug}}

Tên: {{name}}
SĐT: {{phone}}
Email: {{email}}
Source: {{utm_source || 'direct'}}
Page: {{landing_page_url}}
Thời gian: {{timestamp_vn}}

Suggested action: {{action_per_pattern}}
- P1: Lead vừa nhận PDF, follow-up trong 48h
- P2: Vào lịch call, gọi xác nhận trong 1h
- P3: Theo dõi payment, gọi nếu chưa pay sau 2h
- P4: Gọi ngay trong 5 phút (hot lead, intent peak)
```

### Show to user

Sau khi draft xong, **show full HTML preview của Email A** + plain text của Email B. Format response:

```
📧 EMAIL A (gửi cho lead) — Pattern P3

Subject: Anh Tony, link thanh toán "AI Agent + Personal Branding" bên trong — giữ giá 1.99M trong 24h ⏰

Preview: Em vừa nhận thông tin đăng ký của anh. Link thanh toán + lộ trình 8 tuần ngay dưới đây...

[HTML rendered]
<HTML preview here>

---

📧 EMAIL B (gửi cho owner — hoang.tran@prediction3d.com)

Subject: 🔥 Lead mới — Anh Tony (0901234567) — ai-agent-course

Tên: Tony
SĐT: 0901234567
Email: tony@example.com
...

---

Anh/chị review giùm em:
1. Subject line OK không, có muốn em thử variant?
2. Body tone đã đúng brand voice chưa?
3. CTA button có cần đổi text/link?
4. Có thiếu thông tin gì (URL bonus, guarantee detail, Zalo link)?
```

---

## Phase 4 — User Review & Edit

Đợi user feedback. 3 loại feedback thường gặp:

| Feedback | Hành động |
|---|---|
| "OK, gửi đi" / "Duyệt" | Đi Phase 5 wire code |
| "Đổi câu X thành Y" / "Subject ngắn hơn" / "Thêm link Zalo" | Edit inline, show lại preview, hỏi confirm |
| "Tone chưa đúng, làm lại từ đầu" | Hỏi rõ tone họ muốn (chuyên nghiệp / thân thiện / hài hước / formal), redraft |

**Quan trọng**: Không tự ý "polish" thêm khi user đã OK. User OK = wire code ngay. Skill bị fail mode là loop polish vô tận khi user đã sign-off.

---

## Phase 5 — Wire Code

Skill thực thi 4 thay đổi:

### 5.1 Install Resend SDK

```bash
# Detect package manager qua lockfile
# pnpm-lock.yaml → pnpm add resend
# yarn.lock → yarn add resend
# package-lock.json → npm install resend
# Static HTML không có package.json → tạo package.json mới với "resend": "^4.0.0"
```

### 5.2 Tạo API route

Theo stack đã detect Phase 0, đọc template tương ứng:

| Stack | Template | Đích copy |
|---|---|---|
| Next.js App Router | `templates/api-route-nextjs-app.ts` | `app/api/submit/route.ts` |
| Next.js Pages Router | `templates/api-route-nextjs-pages.ts` | `pages/api/submit.ts` |
| Vite / Static HTML | `templates/api-route-vercel-function.js` | `api/submit.js` |

API route làm 4 việc:
1. Parse body (JSON từ fetch hoặc form-data từ form action).
2. Validate fields cơ bản (name, phone, email không empty; email regex check; phone là string).
3. Render 2 email HTML từ template (inject biến `{{name}}`, `{{phone}}`, `{{offer_name}}`).
4. Gọi `resend.emails.send()` 2 lần (1 cho lead, 1 cho owner). `Promise.all()` để parallel.
5. Return `200 { ok: true }` hoặc `500 { error }`.

**Lý do tách 2 email call**: Owner email không cần `react-email` template phức tạp (plain HTML đủ), nhưng lead email cần responsive. Tách giúp debug dễ hơn khi 1 cái fail.

### 5.3 Wire form

Đọc HTML/JSX hiện tại, thay đổi:
- Form action: `<form onSubmit={handleSubmit}>` (React) hoặc `<form id="lead-form">` + inline script (static HTML)
- Add validation client-side cơ bản (required, type="email", pattern="[0-9]{9,11}" cho SĐT VN)
- Add loading state ("Đang gửi..." button text khi submit)
- Add success/error state hiển thị inline (không alert)

Template snippet: `templates/form-binding-react.tsx` và `templates/form-binding-vanilla.html`.

**Success state wording (VN)**:
> ✓ Đã nhận thông tin! Anh/chị check email (và spam folder) trong 1 phút tới. Có gì cần hỗ trợ liên hệ Zalo: 09xx.xxx.xxx

**Error state wording**:
> ⚠️ Có lỗi gửi form. Anh/chị thử lại hoặc liên hệ trực tiếp Zalo 09xx.xxx.xxx

### 5.4 Setup env vars

Tạo/update `.env.local` (nếu Next.js/Vite) hoặc thêm vào Vercel dashboard env (static HTML):

```env
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxx
RESEND_FROM_EMAIL=hello@yourbrand.vn
RESEND_OWNER_EMAIL=hoang.tran@prediction3d.com
LANDING_PAGE_URL=https://yourbrand.vn
```

**Quan trọng — không hardcode**:
- Add `.env.local` vào `.gitignore` nếu chưa có.
- Nếu deploy Vercel, hướng dẫn user vào Vercel dashboard → Project → Settings → Environment Variables → paste vào → redeploy. (Không thể setup env qua CLI nếu user chưa link project.)
- Cảnh báo nếu thấy hardcode API key trong code: rollback ngay.

---

## Phase 6 — Domain Verify + Test Plan

### 6.1 Domain verification

Đọc `references/domain-verification.md` cho hướng dẫn chi tiết. Tóm tắt:

1. User login resend.com → Domains → Add Domain → nhập `yourbrand.vn`.
2. Resend trả về 3-4 DNS record: 1 SPF (TXT), 2 DKIM (TXT hoặc CNAME), 1 MX (optional cho receiving).
3. User add vào DNS provider (Cloudflare, Namecheap, GoDaddy, hoặc admin VN như Mắt Bão/PA Vietnam).
4. Đợi 5-30 phút, Resend verify tự động.
5. **Sau khi verified**, `from` field trong code có thể dùng `noreply@yourbrand.vn` hoặc `hello@yourbrand.vn`. Trước verified chỉ dùng được `onboarding@resend.dev` (limited, không pro).

**Dừng skill ở đây nếu domain chưa verified**. Báo user: *"Em đã wire code xong. Anh/chị add 3 DNS record vào domain provider, đợi verify (5-30 phút), báo em khi xanh dấu tick để em test live."*

### 6.2 Test plan

3 cách test, đi từ nhẹ đến nặng:

**Test 1 — Local API endpoint (sanity check)**:
```bash
# Sau khi `npm run dev` chạy local
curl -X POST http://localhost:3000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","phone":"0901234567","email":"hoang.tran@prediction3d.com"}'

# Expect: {"ok":true}
# Check email hoang.tran@prediction3d.com — phải nhận 2 email (1 auto-responder + 1 notification).
```

**Test 2 — Live form trên localhost**:
- Mở `http://localhost:3000` (hoặc port tương ứng), điền form thực tế.
- Submit, xem có success state hiện không.
- Check email inbox + spam folder.

**Test 3 — Production sau khi deploy**:
- Suggest user chạy `/biz-deploy-vercel` để push code mới.
- Sau khi deploy, test live URL với email thực của owner.
- Check Resend dashboard → Logs → xem có 2 event "Delivered" không.

### 6.3 Monitor sau test

Suggest user pin Resend dashboard. Mỗi email gửi đi có log:
- **Delivered** ✓ = ISP nhận
- **Opened** = lead mở email (cần enable tracking)
- **Clicked** = lead click link CTA
- **Bounced** = email không tồn tại / mailbox full
- **Complained** = lead mark spam → cần xem lại content

Nếu thấy bounce rate >5% hoặc complaint >0.5% → email content có vấn đề, redraft.

---

## Quy tắc viết email tiếng Việt thuần (NEVER VIOLATE)

1. **Xưng hô**: "anh/chị" (default), hoặc "anh" / "chị" nếu biết giới tính từ form. Không "bạn", không "quý khách", không "Mr./Ms.".
2. **Người gửi xưng**: "em" (default cho B2C VN), hoặc "mình" (casual freelancer/coach), hoặc "chúng tôi" (corporate). Đọc `offer.json` `voice.register` hoặc Next.js `app/page.tsx` để decide.
3. **Currency**: VND, charm pricing "1.99M", "199K", "499K". Không "$99", không "1.990.000 VNĐ" lủng củng.
4. **Date format**: dd/mm/yyyy. Time: 14h30 (không 2:30 PM).
5. **Phone**: format VN "0901 234 567" (cách 3-3-3), không "+84-90-123-4567".
6. **Spam triggers tránh**: ALL CAPS subject, "FREE!!!", "100% guarantee", "Act now". Resend deliverability tốt nhưng vẫn nên tránh.
7. **Emoji**: tối đa 1 emoji ở subject, 0-2 emoji trong body. Không emoji-spam. Phù hợp: ✓ ⏰ 👇 ✉️ 🔥 📩. Tránh: 🎉🎊✨💯 (spam-y).
8. **CTA button text**: imperative ngắn — "Tải ngay", "Mở khóa truy cập", "Xem lộ trình 8 tuần", "Thanh toán giữ chỗ". Không "Click here", "Submit".
9. **No machine translation feel**: nếu thấy câu nào dịch từ template tiếng Anh, rewrite. Ví dụ: "We received your submission" → "Em vừa nhận thông tin anh/chị gửi" (không "Chúng tôi đã nhận được sự đệ trình của bạn").

---

## Output cuối cùng skill trả về user

Sau Phase 6, summary cho user:

```
✓ Đã wire xong Resend cho landing page

📁 File thay đổi:
- app/api/submit/route.ts (NEW)
- app/components/LeadForm.tsx (MODIFIED — wire fetch + validation)
- .env.local (NEW — KHÔNG commit)
- .gitignore (MODIFIED — add .env.local)

📧 Email đã setup:
- Email A (auto-responder): Pattern P3 — payment link
- Email B (notification): gửi tới hoang.tran@prediction3d.com

🔧 TODO của anh/chị (manual gate):
1. Login resend.com, lấy API key → paste vào RESEND_API_KEY trong .env.local
2. Add domain yourbrand.vn vào Resend → add 3 DNS record
3. Đợi domain verify (5-30 phút)
4. Test local: `npm run dev` rồi điền form
5. Khi pass test, deploy: chạy `/biz-deploy-vercel`
6. Add env vars trên Vercel dashboard trước khi deploy

📊 Monitor: resend.com/emails — xem log delivered/opened/bounced.
```

---

## Reference files

- `references/email-formulas.md` — 4 pattern email tiếng Việt chi tiết (P1/P2/P3/P4) với template subject + body + CTA
- `references/nextjs-setup.md` — Wiring chi tiết Next.js App Router + Pages Router
- `references/static-html-setup.md` — Wiring static HTML + Vercel serverless function
- `references/domain-verification.md` — SPF/DKIM setup theo từng DNS provider phổ biến VN
- `references/troubleshooting.md` — Common issues: domain chưa verify, email vào spam, rate limit, API key sai

## Templates

- `templates/api-route-nextjs-app.ts` — Next.js App Router API route
- `templates/api-route-nextjs-pages.ts` — Next.js Pages Router API route
- `templates/api-route-vercel-function.js` — Vercel serverless function cho static/Vite
- `templates/email-confirmation.html` — Lead auto-responder HTML responsive
- `templates/email-notification.html` — Owner notification HTML gọn
- `templates/form-binding-react.tsx` — React form với fetch + validation + states
- `templates/form-binding-vanilla.html` — Vanilla HTML form với inline script

---

## Anti-pattern (đừng làm)

- ❌ Gửi email "Cảm ơn anh/chị đã đăng ký, chúng tôi sẽ liên hệ sớm" — quá generic, không deliver value, lead quên brand trong 5 phút.
- ❌ Subject "[BRAND] - Notification #12345" — không personalized, đốt open rate.
- ❌ Hardcode API key trong source code → rotate ngay nếu thấy.
- ❌ Dùng `onboarding@resend.dev` làm from address cho production → unprofessional, dễ vào spam.
- ❌ Skip domain verification, gửi qua Gmail từ owner cá nhân → đập deliverability lâu dài.
- ❌ Tự ý gửi test email mass mà không hỏi user.
- ❌ Email A có 3-4 CTA cùng lúc → confused lead, drop conversion.
- ❌ Email B (owner notification) HTML rườm rà → owner cần info nhanh, plain text đủ.
