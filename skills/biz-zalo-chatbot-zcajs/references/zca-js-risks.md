# ⚠️ zca-js Risks — Đọc bắt buộc trước khi triển khai

`zca-js` là thư viện **không chính thức** (unofficial, reverse-engineered) của bên thứ 3, giả lập trình duyệt để giao tiếp với Zalo Web. **Vi phạm Điều khoản dịch vụ của Zalo**.

Tài liệu này liệt kê **TẤT CẢ rủi ro thật** anh/chị phải biết trước khi đưa skill vào production.

---

## Top 5 risk lớn nhất

### 1. ⚠️ Account bị khóa vĩnh viễn — Risk cao nhất

Zalo có hệ thống detect bot dựa trên pattern:
- Tốc độ gửi tin nhắn quá cao (>5 tin/giây)
- Pattern reply quá đều đặn (mỗi tin reply trong đúng 1-2 giây)
- Gửi tin nhắn giống hệt nhau cho nhiều user
- Dùng IMEI/userAgent không khớp với device đăng ký gốc
- Hoạt động 24/7 không nghỉ
- Login từ IP server (Railway, AWS) — IP datacenter dễ bị flag

**Khi bị khóa**:
- KHÔNG có thông báo trước
- KHÔNG có form khiếu nại có ý nghĩa (Zalo bot reply giấy)
- Mất TOÀN BỘ contact, group, ảnh, history chat
- KHÔNG khôi phục được

**Mitigation**:
- ✅ Dùng số PHỤ riêng (skill đã enforce)
- ✅ Rate limit ≤1 reply/giây (skill đã built-in `lib/rate-limit.js`)
- ✅ Random delay 1-3 giây trước khi reply (tăng human-like)
- ✅ KHÔNG reply 100% tin nhắn — skip tin trong giờ đêm 23h-6h
- ✅ Sleep mode random 5-10 phút mỗi 4 giờ (giả lập "user offline")
- ✅ Personalize reply (LLM tự sinh, không gửi text giống hệt nhau)
- ❌ KHÔNG chạy listener 24/7 — schedule restart mỗi ngày
- ❌ KHÔNG gửi link rút gọn (bit.ly, t.co) — Zalo flag spam

### 2. ⚠️ Cookies expired định kỳ — Listener crash

Cookies `zpsid` mặc định expire sau 30 ngày. Khi cookies expire:
- Listener crash với log `EZINIT` hoặc `cookies invalid`
- Bot dừng trả lời ngay → khách bị bỏ rơi
- Anh/chị phải extract cookies lại + redeploy

**Mitigation**:
- ✅ Setup monitoring (UptimeRobot ping listener mỗi 5 phút)
- ✅ Wire alert (Telegram/email) khi listener crash
- ✅ Backup cookies extraction guide để re-deploy <10 phút
- ✅ Có script `npm run test:login` để verify cookies trước khi push

### 3. ⚠️ Library breaking change — zca-js update mạnh tay

`zca-js` là dự án open-source nhỏ, maintainer có thể:
- Release version mới với breaking API change
- Bỏ maintain (Zalo update web layer → reverse-engineering broken)
- Bị Zalo gửi DMCA takedown → repo bị xóa

**Mitigation**:
- ✅ Pin version trong package.json (`"zca-js": "2.1.1"`, không dùng `^2.x`)
- ✅ Lock npm shrinkwrap để không auto-update
- ✅ Fork repo về GitHub anh/chị làm backup
- ✅ Monitor GitHub issues của zca-js để biết khi có vấn đề lớn

### 4. ⚠️ Bot trả lời sai → mất khách / mất tiền

LLM hallucinate là thường. Nếu bot:
- Tự bịa giá sản phẩm thấp hơn thật → khách yêu cầu honor giá
- Tự cam kết khuyến mãi không có → mất uy tín
- Trả lời sai thông tin y khoa (nếu là sản phẩm sức khỏe) → có thể bị kiện
- Reply tin nhắn nhạy cảm (khiếu nại, phản hồi tiêu cực) với tone không phù hợp

**Mitigation**:
- ✅ System prompt có boundaries rõ ràng (KHÔNG cam kết giá ngoài bảng, KHÔNG khẳng định hiệu quả y khoa)
- ✅ Fallback "Anh/chị cần tư vấn thêm, em chuyển sale gọi lại nhé" khi LLM không chắc
- ✅ Human-in-the-loop: skill có pattern detect tin nhạy cảm (keyword: "khiếu nại", "hoàn tiền", "tệ", "lừa") → forward cho owner thay vì auto-reply
- ✅ Log toàn bộ conversation để review hằng tuần
- ✅ Disclaimer trong tin chào đầu: "Em là trợ lý AI tự động. Để chốt đơn / khiếu nại, anh/chị vui lòng nhắn 'gặp sale' để có người thật hỗ trợ."

### 5. ⚠️ Listener server bị tấn công / leak credentials

`zalo-listener` chứa cookies + imei + userAgent + OpenRouter key + Zalo send API key. Nếu server bị compromise:
- Hacker chiếm account Zalo bot
- Hacker gọi unlimited OpenRouter → cháy credit (∼$1000+)
- Hacker spam khách của anh/chị bằng tên brand → uy tín đi

**Mitigation**:
- ✅ Railway / Render auto-setup HTTPS + DDoS protection
- ✅ KHÔNG commit `.env` lên Git (skill đã add vào `.gitignore`)
- ✅ Rotate `ZALO_SEND_API_KEY` 3 tháng 1 lần
- ✅ Limit OpenRouter spend cap trong dashboard ($10/tháng max)
- ✅ Disable OpenRouter key cũ khi rotate
- ✅ Monitor Railway logs định kỳ

---

## Best practice human-in-the-loop

Bot KHÔNG nên trả lời 100% tin nhắn. Một số tin phải forward cho người thật:

| Tin nhắn | Bot hành xử |
|---|---|
| "Giá sản phẩm X bao nhiêu?" | ✅ Auto reply theo FAQ |
| "Sản phẩm dùng cho trẻ mấy tháng?" | ✅ Auto reply theo product.md |
| "Em muốn đặt 1 hộp" | ✅ Auto reply hướng dẫn link order |
| "Sản phẩm dùng có hết hen suyễn không?" | ⚠️ Fallback "em chuyển sale" (claim y khoa) |
| "Khiếu nại đơn hàng" | ⚠️ Fallback + forward Zalo owner ngay |
| "Sản phẩm dở quá, đòi hoàn tiền" | ⚠️ Fallback + forward owner |
| "Em là phóng viên, muốn phỏng vấn brand" | ⚠️ Fallback + forward owner |
| "Sản phẩm có an toàn cho bà bầu không?" | ⚠️ Fallback (claim y khoa) |
| Tin nhắn chính trị / tôn giáo | ⚠️ Fallback + KHÔNG reply nội dung |

Pattern detect — trong `index.js` listener, sau khi nhận tin nhắn:

```javascript
const SENSITIVE_KEYWORDS = [
  'khiếu nại', 'hoàn tiền', 'refund', 'tệ', 'dở', 'lừa', 'lừa đảo',
  'kiện', 'báo công an', 'tố cáo',
  'phỏng vấn', 'báo chí', 'phóng viên',
  'hết bệnh', 'khỏi bệnh', 'chữa khỏi', 'thay thế thuốc',
  'bà bầu', 'mang thai', 'cho con bú',
];

function isSensitive(msg) {
  return SENSITIVE_KEYWORDS.some(kw => msg.toLowerCase().includes(kw));
}

// Trong listener
if (isSensitive(message.data.content)) {
  await api.sendMessage(
    { msg: "Anh/chị thông cảm, câu hỏi này em xin chuyển sale có chuyên môn trả lời. Em sẽ nhắn lại trong vòng 30 phút ạ." },
    message.threadId, message.type
  );
  await notifyOwner(message); // Forward Zalo owner
  return;
}
```

---

## Backup plan — Nếu bot bị khóa

Ngày X account zca-js bị khóa, khách hàng vẫn phải liên hệ được. Backup plan BẮT BUỘC:

### Layer 1 — Khách thấy nhiều kênh liên hệ

Trên landing page + email signature + Zalo bot bio:
```
📞 Hotline: 0901 234 567 (8h-22h)
📧 Email: support@drmaya.vn (reply trong 24h)
🌐 Website: thieuvananh.vn (chatbot AI 24/7)
💬 Zalo: [link Zalo bot] (auto reply 24/7)
🔗 Fanpage: facebook.com/drmaya (rep trong 1-2 giờ)
```

Bot Zalo chỉ là 1 channel. Nếu fail, 4 channel khác vẫn live.

### Layer 2 — Re-deploy nhanh khi bot mới

Quy trình deploy lại:
1. Đăng ký Zalo với số phụ MỚI (giữ vài SIM dự phòng sẵn)
2. Đặt tên + avatar giống bot cũ
3. Login Chrome → extract cookies/imei/userAgent (10 phút)
4. Update Railway env vars (5 phút)
5. Redeploy (Railway auto < 2 phút)
6. Update landing page với link Zalo mới
7. Total: ≤30 phút từ lúc detect khóa đến lúc bot mới live

### Layer 3 — Migration sang Zalo OA chính thức

Nếu business lớn lên (>1000 đơn/tháng), nên migrate sang Zalo OA verified:
- Apply Zalo OA Business: 3-7 ngày approval
- Bot chính thức, không risk khóa
- API official, không cần zca-js
- Fee có nhưng đáng vì stability

Skill này là **bootstrap** cho early-stage, không phải solution lâu dài.

---

## Pháp lý

`zca-js` reverse-engineer Zalo private API. Về pháp lý ở VN:
- KHÔNG có precedent xử phạt cá nhân dùng zca-js cho mục đích nội bộ (business support bot)
- Zalo có quyền khóa account, KHÔNG có quyền kiện cá nhân (vi phạm ToS ≠ phạm pháp)
- NHƯNG: nếu dùng zca-js để spam tin nhắn / lừa đảo → Bộ luật hình sự VN xử lý theo điều 290 (lừa đảo), 174 (tài chính)

**Khuyến cáo**:
- Chỉ dùng cho **business hợp pháp** (bán sản phẩm có giấy phép, dịch vụ có ĐKKD)
- KHÔNG dùng cho: spam quảng cáo, lừa đảo, scam, gambling, "kèo lô đề", ICO crypto

---

## Tóm tắt — Bảng risk score

| Risk | Likelihood | Impact | Severity |
|---|---|---|---|
| Account khóa | Cao (40-60%/năm) | Cao (mất bot + history) | 🔴 Critical |
| Cookies expired | Trung (mỗi 30 ngày) | Trung (downtime 30 phút) | 🟡 Medium |
| zca-js breaking change | Thấp (1-2 lần/năm) | Cao (rewrite) | 🟡 Medium |
| LLM trả lời sai | Trung (~5% tin) | Trung (mất khách) | 🟡 Medium |
| Server compromise | Thấp | Cao (leak data) | 🟡 Medium |

**Risk total**: 🔴 HIGH. Skill này phù hợp:
- Solopreneur / micro-business chấp nhận risk để bootstrap nhanh
- Đã có backup channel (hotline, FB, web chatbot)
- Có quy trình re-deploy <30 phút khi khóa

**KHÔNG phù hợp**:
- Business critical, downtime không chấp nhận được
- Brand lớn (>$10M revenue) — risk uy tín cao hơn lợi ích bot
- Yêu cầu compliance nghiêm (y tế, tài chính, bảo hiểm)
