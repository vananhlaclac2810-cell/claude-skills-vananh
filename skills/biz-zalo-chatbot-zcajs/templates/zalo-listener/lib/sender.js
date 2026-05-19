// lib/sender.js — Helper sendZaloMessage cho /send endpoint dùng
// Cần setApiInstance(api) được gọi từ index.js sau khi login xong.

import { ThreadType } from 'zca-js';

let apiInstance = null;

export function setApiInstance(api) {
  apiInstance = api;
}

/**
 * Gửi tin nhắn Zalo đến 1 hoặc nhiều recipient.
 * @param {string[]} recipients - Array of Zalo user_id (string)
 * @param {string} message - Text message
 * @param {ThreadType} [type=ThreadType.User] - User hoặc Group
 * @returns {Promise<{sent: number, failed: Array<{recipient: string, error: string}>}>}
 */
export async function sendZaloMessage(recipients, message, type = ThreadType.User) {
  if (!apiInstance) {
    throw new Error('Zalo API instance not initialized. Call setApiInstance() first.');
  }

  if (!Array.isArray(recipients)) {
    recipients = [recipients];
  }

  if (!message || typeof message !== 'string') {
    throw new Error('message must be non-empty string');
  }

  const failed = [];
  let sent = 0;

  for (const recipient of recipients) {
    try {
      await apiInstance.sendMessage({ msg: message }, recipient, type);
      sent += 1;
      // Small delay between sends to avoid burst
      await new Promise(r => setTimeout(r, 500));
    } catch (err) {
      console.error(`[sender] Failed for ${recipient}:`, err.message);
      failed.push({ recipient, error: err.message });
    }
  }

  return { sent, failed };
}
