// lib/zalo-notify.ts
// Helper gọi /api/zalo-notify từ server-side code (Sepay webhook handler).
// Tương tự lib/telegram.ts trong skill biz-telegram-payment-notify.
//
// Usage trong Sepay webhook handler:
//
//   import { sendZaloNotification } from '@/lib/zalo-notify';
//   await Promise.allSettled([
//     sendCustomerEmail(lead),
//     sendOwnerEmail(lead),
//     sendTelegramNotification({...}),
//     sendZaloNotification({
//       name: lead.name,
//       phone: lead.phone,
//       amount: payload.transferAmount,
//       productName: lead.productName,
//     }),
//   ]);

type ZaloNotifyPayload = {
  name: string;
  phone: string;
  email?: string;
  amount: number;
  productName: string;
  referenceCode?: string;
};

export async function sendZaloNotification(payload: ZaloNotifyPayload): Promise<void> {
  const listenerUrl = process.env.ZALO_LISTENER_URL;
  const apiKey = process.env.ZALO_SEND_API_KEY;
  const recipientsCsv = process.env.ZALO_NOTIFY_RECIPIENTS;

  if (!listenerUrl || !apiKey || !recipientsCsv) {
    console.error('[zalo-notify] Missing ZALO_LISTENER_URL / ZALO_SEND_API_KEY / ZALO_NOTIFY_RECIPIENTS');
    return; // Không throw — Zalo fail không được block payment response
  }

  const recipients = recipientsCsv.split(',').map(s => s.trim()).filter(Boolean);
  if (recipients.length === 0) {
    console.warn('[zalo-notify] No recipients configured');
    return;
  }

  const message = formatMessage(payload);

  try {
    const res = await fetch(`${listenerUrl}/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
      },
      body: JSON.stringify({
        recipients,
        message,
        type: 'user',
      }),
      signal: AbortSignal.timeout(10000),
    });

    if (!res.ok) {
      const errBody = await res.text();
      console.error(`[zalo-notify] Send failed: ${res.status} ${errBody}`);
    }
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error('[zalo-notify] Network error:', msg);
    // Swallow — đừng để Zalo fail làm Sepay retry
  }
}

function formatMessage(p: ZaloNotifyPayload): string {
  const amountStr = p.amount.toLocaleString('vi-VN') + 'đ';
  const phoneStr = p.phone.replace(/(\d{4})(\d{3})(\d{3})/, '$1 $2 $3');
  const now = new Date().toLocaleString('vi-VN', {
    timeZone: 'Asia/Ho_Chi_Minh',
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });

  const lines = [
    '🎉 ĐƠN HÀNG MỚI',
    '',
    `Khách: ${p.name}`,
    `SĐT: ${phoneStr}`,
  ];
  if (p.email) lines.push(`Email: ${p.email}`);
  lines.push(`Tiền: ${amountStr} — ${p.productName}`);
  lines.push(`Giờ: ${now}`);
  if (p.referenceCode) lines.push(`Mã GD: ${p.referenceCode}`);

  return lines.join('\n');
}
