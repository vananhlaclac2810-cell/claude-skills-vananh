// lib/rate-limit.js — Token bucket per-chatId
// Mục đích: ≤1 reply/giây/chat → giảm risk Zalo detect spam.

/**
 * @param {{tokensPerInterval: number, intervalMs: number}} opts
 */
export function createRateLimiter({ tokensPerInterval = 1, intervalMs = 1000 } = {}) {
  // Map<chatId, {tokens: number, lastRefill: number}>
  const buckets = new Map();

  function tryAcquire(chatId) {
    const now = Date.now();
    let bucket = buckets.get(chatId);

    if (!bucket) {
      bucket = { tokens: tokensPerInterval, lastRefill: now };
      buckets.set(chatId, bucket);
    }

    // Refill tokens dựa trên thời gian đã trôi
    const elapsed = now - bucket.lastRefill;
    if (elapsed >= intervalMs) {
      const intervalsPassed = Math.floor(elapsed / intervalMs);
      bucket.tokens = Math.min(tokensPerInterval, bucket.tokens + intervalsPassed * tokensPerInterval);
      bucket.lastRefill = now;
    }

    if (bucket.tokens >= 1) {
      bucket.tokens -= 1;
      return true;
    }

    return false;
  }

  // Cleanup old buckets mỗi 10 phút để không leak memory
  setInterval(() => {
    const cutoff = Date.now() - 10 * 60 * 1000;
    for (const [key, bucket] of buckets.entries()) {
      if (bucket.lastRefill < cutoff) {
        buckets.delete(key);
      }
    }
  }, 10 * 60 * 1000).unref();

  return { tryAcquire };
}
