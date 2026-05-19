// lib/server.js — Express mini-server expose /send endpoint
// Để Sepay webhook (qua Vercel proxy) hoặc bất kỳ webhook khác gọi vào gửi tin Zalo.
// Auth qua header `x-api-key`.

import express from 'express';
import { ThreadType } from 'zca-js';
import { sendZaloMessage } from './sender.js';

const STARTED_AT = Date.now();

export function createSendServer({ api, apiKey }) {
  if (!apiKey) {
    throw new Error('createSendServer requires apiKey');
  }

  const app = express();
  app.use(express.json({ limit: '256kb' }));

  // Health endpoint — KHÔNG auth, dùng cho UptimeRobot
  app.get('/health', (_req, res) => {
    res.json({
      status: 'ok',
      zalo: api ? 'connected' : 'disconnected',
      uptime_seconds: Math.floor((Date.now() - STARTED_AT) / 1000),
    });
  });

  // Send endpoint — yêu cầu x-api-key
  app.post('/send', async (req, res) => {
    // Auth
    const provided = req.header('x-api-key');
    if (!provided || provided !== apiKey) {
      return res.status(401).json({ ok: false, error: 'invalid api key' });
    }

    // Validate body
    const { recipients, message, type } = req.body || {};
    if (!recipients || !Array.isArray(recipients) || recipients.length === 0) {
      return res.status(400).json({ ok: false, error: 'recipients (array) is required' });
    }
    if (!message || typeof message !== 'string') {
      return res.status(400).json({ ok: false, error: 'message (string) is required' });
    }

    const threadType = type === 'group' ? ThreadType.Group : ThreadType.User;

    try {
      const result = await sendZaloMessage(recipients, message, threadType);
      return res.json({ ok: true, ...result });
    } catch (err) {
      console.error('[server] /send error:', err.message);
      return res.status(500).json({ ok: false, error: err.message });
    }
  });

  // 404
  app.use((_req, res) => res.status(404).json({ ok: false, error: 'not found' }));

  return app;
}
