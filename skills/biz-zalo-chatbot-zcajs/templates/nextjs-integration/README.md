# Next.js Integration — Wire Sepay webhook → Zalo notification

Hai file template để wire Sepay webhook (đã có sẵn từ `/biz-setup-sepay-payment`) sang Zalo notification qua listener đã deploy.

---

## File list

| File | Đích copy vào | Mục đích |
|---|---|---|
| `app/api/zalo-notify/route.ts` | `app/api/zalo-notify/route.ts` (App Router) | API endpoint proxy POST → listener `/send` |
| `lib-zalo-notify.ts` | `lib/zalo-notify.ts` | Helper `sendZaloNotification()` cho Sepay webhook handler |

> **Pages Router**: nếu project dùng Pages Router, copy `route.ts` thành `pages/api/zalo-notify.ts` (cần adapt sang `default export handler(req, res)` syntax).

---

## Wire vào Sepay webhook

Trong `app/api/sepay-webhook/route.ts` (hoặc `app/api/payment-success/route.ts`), thêm import + gọi:

```typescript
import { sendZaloNotification } from '@/lib/zalo-notify';
import { sendCustomerEmail, sendOwnerEmail } from '@/lib/resend'; // nếu có
import { sendTelegramNotification } from '@/lib/telegram'; // nếu có

export async function POST(req: Request) {
  const payload = await req.json();

  // [Existing] Validate Sepay auth + parse payload
  if (payload.transferType !== 'in') {
    return Response.json({ success: true });
  }

  const lead = await lookupLeadByTransferContent(payload.content);

  // Fan-out 4 side effects parallel — Zalo fail không block các cái khác
  await Promise.allSettled([
    sendCustomerEmail(lead),
    sendOwnerEmail(lead),
    sendTelegramNotification({ /* ... */ }),
    sendZaloNotification({
      name: lead.name,
      phone: lead.phone,
      email: lead.email,
      amount: payload.transferAmount,
      productName: lead.productName,
      referenceCode: payload.referenceCode,
    }),
  ]);

  return Response.json({ success: true });
}
```

---

## Env vars cần thêm vào Next.js `.env.local`

```env
# URL Railway listener (Phase 5 deployment guide)
ZALO_LISTENER_URL=https://zalo-listener-production-abc1.up.railway.app

# Cùng key với listener .env
ZALO_SEND_API_KEY=random-string-32-chars

# CSV danh sách Zalo user_id của owner / sale (cùng với listener)
ZALO_NOTIFY_RECIPIENTS=1234567890,9876543210
```

⚠️ Nhớ paste 3 biến trên vào Vercel dashboard → Settings → Environment Variables (Production + Preview) trước khi deploy.

---

## Test local

```bash
# 1. Listener phải running local hoặc Railway
# 2. Next.js dev
npm run dev

# 3. Curl test
curl -X POST http://localhost:3000/api/zalo-notify \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["1234567890"],
    "message": "🎉 Test notify"
  }'

# Expect: {"ok":true,"sent":1,"failed":[]}
# Zalo của user 1234567890 phải nhận tin trong < 5s
```

---

## Anti-pattern

- ❌ Throw error trong `sendZaloNotification` → Sepay nhận 500 → retry → duplicate notify
- ❌ Dùng `Promise.all` thay vì `allSettled` → 1 fail block tất cả
- ❌ Quên set timeout fetch → Vercel function timeout 30s nếu listener slow
- ❌ Bỏ qua `x-api-key` → ai cũng spam được listener
