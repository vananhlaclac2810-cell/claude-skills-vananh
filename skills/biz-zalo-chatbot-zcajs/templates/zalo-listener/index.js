// index.js — Main entry cho Zalo listener
// Load env, init Zalo client, register listener, start Express /send server.
//
// ⚠️ CẢNH BÁO: zca-js là unofficial library — account có thể bị Zalo khóa.
// Đọc references/zca-js-risks.md trong skill folder trước khi production.

import 'dotenv/config';
import { Zalo, ThreadType } from 'zca-js';
import { askLLM } from './lib/openrouter.js';
import { loadKnowledge } from './lib/knowledge.js';
import { createRateLimiter } from './lib/rate-limit.js';
import { createSendServer } from './lib/server.js';
import { setApiInstance } from './lib/sender.js';

// ---------- Sensitive keywords — fallback for human ----------
const SENSITIVE_KEYWORDS = [
  'khiếu nại', 'hoàn tiền', 'refund', 'tệ quá', 'dở', 'lừa', 'lừa đảo',
  'kiện', 'báo công an', 'tố cáo',
  'phỏng vấn', 'báo chí', 'phóng viên',
  'hết bệnh', 'khỏi bệnh', 'chữa khỏi', 'thay thế thuốc',
  'mang thai', 'cho con bú',
];

const FALLBACK_MSG = 'Anh/chị thông cảm, câu hỏi này em xin chuyển sale có chuyên môn trả lời chính xác hơn. Sale sẽ phản hồi trong vòng 30 phút ạ.';

function isSensitive(msg) {
  const lower = msg.toLowerCase();
  return SENSITIVE_KEYWORDS.some(kw => lower.includes(kw));
}

// ---------- Validate env ----------
const required = ['ZALO_COOKIES_JSON', 'ZALO_IMEI', 'ZALO_USER_AGENT', 'OPENROUTER_API_KEY', 'ZALO_SEND_API_KEY'];
for (const k of required) {
  if (!process.env[k]) {
    console.error(`[fatal] Missing env: ${k}`);
    process.exit(1);
  }
}

// ---------- Init Zalo ----------
console.log('[zalo] Initializing...');
const zalo = new Zalo({
  selfListen: false,
  checkUpdate: false,
});

let cookies;
try {
  cookies = JSON.parse(process.env.ZALO_COOKIES_JSON);
} catch (err) {
  console.error('[fatal] ZALO_COOKIES_JSON is not valid JSON:', err.message);
  process.exit(1);
}

const api = await zalo.login({
  cookie: cookies,
  imei: process.env.ZALO_IMEI,
  userAgent: process.env.ZALO_USER_AGENT,
}).catch(err => {
  console.error('[fatal] Zalo login failed:', err.message);
  console.error('Likely cause: cookies expired, imei/userAgent mismatch, or account locked');
  process.exit(1);
});

const ownInfo = await api.getOwnId?.() || 'unknown';
console.log(`[zalo] Login OK. Own ID: ${ownInfo}`);

// Make api globally available for /send endpoint
setApiInstance(api);

// ---------- Load knowledge ----------
const knowledge = loadKnowledge();
console.log(`[knowledge] Loaded ${knowledge.length} chars from zalo-knowledge/`);

// ---------- Rate limiter — ≤1 reply/giây/chat ----------
const limiter = createRateLimiter({ tokensPerInterval: 1, intervalMs: 1000 });

// ---------- Message listener ----------
api.listener.on('message', async (message) => {
  try {
    // Skip self messages
    if (message.isSelf) return;

    // Only handle plain text
    const isPlainText = typeof message.data.content === 'string';
    if (!isPlainText) {
      console.log(`[skip] Non-text message from ${message.threadId}`);
      return;
    }

    const userMsg = message.data.content.trim();
    if (!userMsg) return;

    console.log(`[recv] [${message.type === ThreadType.Group ? 'GROUP' : 'USER'}] ${message.threadId}: ${userMsg.slice(0, 80)}`);

    // Rate limit check
    if (!limiter.tryAcquire(message.threadId)) {
      console.log(`[rate-limit] Skip ${message.threadId} (too fast)`);
      return;
    }

    // Sensitive keyword → fallback + notify owner
    if (isSensitive(userMsg)) {
      console.log(`[sensitive] Trigger fallback for ${message.threadId}`);
      await api.sendMessage(
        { msg: FALLBACK_MSG, quote: message.data },
        message.threadId,
        message.type
      );
      await notifyOwners(`⚠️ Tin nhạy cảm từ ${message.threadId}:\n"${userMsg}"\n\nVào Zalo xử lý gấp ạ.`);
      return;
    }

    // Random human-like delay 1-3 seconds
    await new Promise(r => setTimeout(r, 1000 + Math.random() * 2000));

    // Call LLM
    const reply = await askLLM(userMsg, knowledge);

    if (!reply || !reply.trim()) {
      console.log(`[empty-reply] LLM returned empty for ${message.threadId}`);
      return;
    }

    // Send reply
    await api.sendMessage(
      { msg: reply, quote: message.data },
      message.threadId,
      message.type
    );
    console.log(`[sent] -> ${message.threadId}: ${reply.slice(0, 80)}`);
  } catch (err) {
    console.error(`[error] Handler error for ${message.threadId}:`, err.message);
  }
});

async function notifyOwners(text) {
  const recipients = (process.env.ZALO_NOTIFY_RECIPIENTS || '').split(',').map(s => s.trim()).filter(Boolean);
  for (const r of recipients) {
    try {
      await api.sendMessage({ msg: text }, r, ThreadType.User);
    } catch (err) {
      console.error(`[notify] Failed for ${r}:`, err.message);
    }
  }
}

// ---------- Start listener ----------
api.listener.start();
console.log('[zalo] Listening for incoming messages...');

// ---------- Start Express /send server ----------
const port = Number(process.env.SEND_PORT || 3001);
const server = createSendServer({
  api,
  apiKey: process.env.ZALO_SEND_API_KEY,
});
server.listen(port, () => {
  console.log(`[server] /send endpoint ready on :${port}`);
});

// ---------- Graceful shutdown ----------
process.on('SIGTERM', () => {
  console.log('[shutdown] SIGTERM received, closing...');
  server.close();
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('[shutdown] SIGINT received, closing...');
  server.close();
  process.exit(0);
});
