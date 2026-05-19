# Next.js Setup — Wiring chi tiết

Next.js có 2 router (App vs Pages) → API route đặt khác chỗ, syntax import khác. Skill detect qua sự tồn tại của folder `app/` vs `pages/`.

---

## App Router (Next.js 13+)

### File location
`app/api/submit/route.ts`

### Install
```bash
# Detect package manager qua lockfile
pnpm add resend          # nếu pnpm-lock.yaml
# hoặc
npm install resend       # nếu package-lock.json
# hoặc
yarn add resend          # nếu yarn.lock
```

### Code
Copy `templates/api-route-nextjs-app.ts` → `app/api/submit/route.ts`, sau đó thay các placeholder `{{PRODUCT_NAME}}`, `{{BRAND_NAME}}`, etc. theo context Phase 1.

### Wire form component
Form là client component → cần `"use client"` directive ở đầu file.

Copy `templates/form-binding-react.tsx` → ví dụ `components/LeadForm.tsx`.

Import trong page (server component):
```tsx
// app/page.tsx
import LeadForm from "@/components/LeadForm";

export default function Home() {
  return (
    <main>
      {/* ... hero, body sections ... */}
      <section id="cta">
        <h2>{{CTA_HEADING}}</h2>
        <LeadForm />
      </section>
    </main>
  );
}
```

---

## Pages Router (Next.js 12 và pre-app dir)

### File location
`pages/api/submit.ts`

### Code (template tương tự App Router nhưng signature khác)

```ts
// pages/api/submit.ts
import type { NextApiRequest, NextApiResponse } from "next";
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);
// ... (validate, formatPhoneVN, renderEmailHTML giống App Router template)

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ ok: false, error: "Method not allowed" });
  }
  // ... same logic
}
```

### Form binding
Form binding code (`templates/form-binding-react.tsx`) work giống nhau ở Pages Router, không cần `"use client"`.

---

## Env vars (cả 2 router giống nhau)

### Local dev: `.env.local` ở root project

```env
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxx
RESEND_FROM_EMAIL=hello@yourbrand.vn
RESEND_OWNER_EMAIL=hoang.tran@prediction3d.com
LANDING_PAGE_URL=https://yourbrand.vn
```

### Production: Vercel dashboard

1. Vercel → Project → Settings → Environment Variables
2. Add từng key-value, scope = Production (+ Preview nếu muốn).
3. **Quan trọng**: sau khi add, phải **redeploy** (push commit hoặc Vercel UI → Deployments → "..." → Redeploy). Env vars không hot-reload.

### .gitignore

Đảm bảo `.env.local` được ignore:

```gitignore
# env files
.env*.local
.env
```

---

## Edge runtime vs Node runtime

Resend SDK dùng `fetch` internally → chạy được trên cả Edge và Node runtime.

**Khuyến nghị: dùng Node runtime** (default cho API routes) vì:
- Edge có cold start nhanh hơn nhưng giới hạn package size.
- Resend SDK ổn định hơn trên Node.
- Email gửi đi không cần latency cực thấp như edge function khác (5-15s đầu tiên ok).

Nếu muốn force Node runtime (Next.js 14+):
```ts
// app/api/submit/route.ts
export const runtime = "nodejs"; // default, không cần khai báo
```

Nếu muốn thử Edge:
```ts
export const runtime = "edge";
```

---

## Type safety (TypeScript)

Define type cho lead payload để IDE catch typo:

```ts
// types/lead.ts
export type LeadPayload = {
  name: string;
  phone: string;
  email: string;
  utm_source?: string;
  utm_campaign?: string;
  message?: string;
};
```

Reuse trong cả API route và form component.

---

## Server Action alternative (Next.js 14+)

Thay vì API route, có thể dùng Server Action:

```tsx
// app/actions/submit-lead.ts
"use server";

import { Resend } from "resend";

export async function submitLead(formData: FormData) {
  const resend = new Resend(process.env.RESEND_API_KEY);
  // ... validate, send emails
}
```

```tsx
// LeadForm.tsx
import { submitLead } from "@/app/actions/submit-lead";

<form action={submitLead}>
  ...
</form>
```

**Tradeoff**: Server Action gọn hơn (no API route), nhưng:
- Khó test bằng curl từ ngoài.
- Khó share endpoint với app mobile/extension sau này.
- Error handling phức tạp hơn (cần `useFormState`).

**Default recommendation**: dùng API route `/api/submit` — universal, debuggable, scaleable.
