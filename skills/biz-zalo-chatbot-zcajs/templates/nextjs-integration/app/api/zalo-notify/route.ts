// app/api/zalo-notify/route.ts (Next.js App Router)
// Proxy POST từ Vercel → Railway listener `/send` endpoint.
// Dùng khi Sepay webhook hoặc form submission cần trigger Zalo notification.
//
// Env vars required:
//   ZALO_LISTENER_URL    — https://your-listener.up.railway.app
//   ZALO_SEND_API_KEY    — phải cùng với key trong listener

import { NextResponse } from 'next/server';

type RequestBody = {
  recipients: string[];
  message: string;
  type?: 'user' | 'group';
};

export const runtime = 'nodejs'; // KHÔNG dùng edge (cần fetch lâu hơn)

export async function POST(req: Request) {
  const listenerUrl = process.env.ZALO_LISTENER_URL;
  const apiKey = process.env.ZALO_SEND_API_KEY;

  if (!listenerUrl || !apiKey) {
    console.error('[zalo-notify] Missing ZALO_LISTENER_URL or ZALO_SEND_API_KEY');
    return NextResponse.json({ ok: false, error: 'server misconfigured' }, { status: 500 });
  }

  let body: RequestBody;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ ok: false, error: 'invalid json' }, { status: 400 });
  }

  if (!body.recipients || !Array.isArray(body.recipients) || body.recipients.length === 0) {
    return NextResponse.json({ ok: false, error: 'recipients (array) is required' }, { status: 400 });
  }
  if (!body.message || typeof body.message !== 'string') {
    return NextResponse.json({ ok: false, error: 'message (string) is required' }, { status: 400 });
  }

  try {
    const res = await fetch(`${listenerUrl}/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
      },
      body: JSON.stringify(body),
      // Timeout 10s — Vercel function tổng 30s, để Sepay webhook không timeout
      signal: AbortSignal.timeout(10000),
    });

    const data = await res.json().catch(() => ({}));
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error('[zalo-notify] Listener call failed:', msg);
    // KHÔNG throw — Sepay webhook không retry vì Zalo fail
    return NextResponse.json({ ok: false, error: 'listener unreachable: ' + msg }, { status: 502 });
  }
}
