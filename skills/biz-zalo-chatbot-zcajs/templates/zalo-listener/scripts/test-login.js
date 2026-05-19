// scripts/test-login.js — Verify cookies/imei/userAgent đúng, không listen.
// Chạy: npm run test:login
// Exit 0 nếu login OK, exit 1 nếu fail.

import 'dotenv/config';
import { Zalo } from 'zca-js';

const required = ['ZALO_COOKIES_JSON', 'ZALO_IMEI', 'ZALO_USER_AGENT'];
for (const k of required) {
  if (!process.env[k]) {
    console.error(`[fatal] Missing env: ${k}`);
    process.exit(1);
  }
}

let cookies;
try {
  cookies = JSON.parse(process.env.ZALO_COOKIES_JSON);
} catch (err) {
  console.error('[fatal] ZALO_COOKIES_JSON not valid JSON');
  process.exit(1);
}

console.log('[test-login] Attempting login...');
const zalo = new Zalo({ selfListen: false, checkUpdate: false });

try {
  const api = await zalo.login({
    cookie: cookies,
    imei: process.env.ZALO_IMEI,
    userAgent: process.env.ZALO_USER_AGENT,
  });
  const ownId = await api.getOwnId?.() || 'unknown';
  console.log(`[test-login] ✓ OK. Own ID: ${ownId}`);
  process.exit(0);
} catch (err) {
  console.error(`[test-login] ✗ FAILED: ${err.message}`);
  console.error('Likely causes:');
  console.error('  - cookies expired (extract lại từ Chrome)');
  console.error('  - imei sai (lấy lại từ localStorage.getItem("z_uuid"))');
  console.error('  - userAgent không khớp browser đã extract cookies');
  console.error('  - account bị Zalo khóa');
  process.exit(1);
}
