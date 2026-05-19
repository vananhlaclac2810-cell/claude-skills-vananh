# Zalo Account Setup — Chuẩn bị account phụ + extract credentials

Hướng dẫn chi tiết để chuẩn bị 1 Zalo account phụ làm bot, sau đó extract `cookies` + `imei` + `userAgent` cho `zca-js` login.

> ⚠️ **TUYỆT ĐỐI KHÔNG dùng số chính của business cho bước này**. zca-js là unofficial library, account có thể bị Zalo khóa vĩnh viễn. Đọc thêm [`zca-js-risks.md`](zca-js-risks.md).

---

## Bước 1 — Chuẩn bị số điện thoại phụ

Anh/chị cần 1 SIM phụ (không phải số đang dùng cho Zalo cá nhân hay business chính).

**Lựa chọn nguồn SIM phụ**:

1. **SIM cũ trong nhà** — nếu còn SIM Viettel/Vinaphone/Mobi cũ chưa thu hồi → tốt nhất, miễn phí.
2. **SIM data giá rẻ** — ra cửa hàng mua SIM mới 50-100k, chỉ cần nhận SMS 1 lần để đăng ký Zalo.
3. **SIM số ảo (TUYỆT ĐỐI TRÁNH)** — Zalo detect SIM ảo ngay, ban account trong vài giờ. KHÔNG dùng.

**Lý do dùng số phụ**:
- Nếu account bị khóa, không mất Zalo chính của anh/chị (chứa toàn bộ contact, group, ảnh kỷ niệm)
- Nếu account khóa, có thể đăng ký lại ngay với số phụ khác mà không ảnh hưởng business

---

## Bước 2 — Đăng ký Zalo bằng số phụ

```
1. Cài app Zalo trên 1 điện thoại (Android/iOS đều OK)
2. Mở app → Đăng ký mới
3. Nhập số phụ → nhận OTP → xác nhận
4. Đặt tên hiển thị: dạng "[Brand] AI Support" hoặc "Trợ lý [Brand]"
   Ví dụ: "Trợ lý Dr.Maya", "AI Support Húng Chanh"
5. Đặt avatar logo brand (lấy từ landing page)
6. Cập nhật bio: "Trợ lý AI tư vấn 24/7 - Phản hồi trong 5 giây"
```

**Lưu ý quan trọng**:
- ✅ Dùng 1 điện thoại RIÊNG (hoặc điện thoại cũ) cho Zalo bot — không cài chung với app Zalo cá nhân.
- ✅ KHÔNG bật 2FA bằng SIM khác — nếu cookies expired sau này, cần OTP lại bằng SIM gốc.
- ❌ Không dùng emulator (BlueStacks/NoxPlayer) — Zalo detect, ban.

---

## Bước 3 — Login Zalo Web trên Chrome

```
1. Mở Chrome (KHUYẾN NGHỊ Chrome bình thường, KHÔNG dùng Incognito ở bước extract)
   Lý do: Incognito clear cookies khi đóng tab → mất hết. Dùng profile mới của Chrome:
   - Chrome → góc phải trên → bấm avatar → Add account → tạo profile "Zalo Bot"
2. Truy cập: https://chat.zalo.me
3. Trang hiện QR code
4. Trên điện thoại có app Zalo (bot) → vào menu Cài đặt → "Quản lý thiết bị" → "Quét QR" → quét QR trên Chrome
5. Web load giao diện chat hoàn chỉnh
6. ⚠️ KHÔNG ĐÓNG TAB này — phải mở để extract cookies
7. Test bằng cách tự gửi tin nhắn cho bản thân (chat với chính mình) → đảm bảo session live
```

---

## Bước 4 — Extract 3 thứ: cookies + imei + userAgent

### 4.1 — Extract cookies

```
1. Trong tab chat.zalo.me đang mở, bấm F12 (mở DevTools)
2. Tab "Application" (Chrome) hoặc "Storage" (Firefox)
3. Bên trái: panel Storage → mục "Cookies" → click "https://chat.zalo.me"
4. Bảng cookies hiện ra ở giữa
```

**Danh sách cookies cần extract** (copy TẤT CẢ những cái này):

| Tên cookies | Mục đích | Bắt buộc? |
|---|---|---|
| `zpsid` | Session ID chính | ✅ Bắt buộc |
| `zpw_sek` | Encryption key | ✅ Bắt buộc |
| `_zlang` | Language pref | ✅ Bắt buộc |
| `app.event.zalo.me` | Event tracking | ✅ Bắt buộc |
| `zpw_type` | Web type | Recommend |
| `atc` | Auth token cookie | Recommend |
| `_ga`, `_gid`, `_gat` | Google Analytics | Optional |

**Cách copy chính xác** (làm theo từng bước):

1. Trên bảng cookies, **right-click vào row** của cookie cần copy
2. Chrome có option "Edit cookie" — click để xem full Value (vì panel cắt ngắn)
3. Copy `Name` + `Value` + `Domain` + `Path` + `Expires` + `HttpOnly` + `Secure`
4. Lặp lại cho TẤT CẢ cookies ở bảng trên

**Format cuối cùng** (lưu vào `cookies.json`):

```json
[
  {
    "domain": ".zalo.me",
    "name": "zpsid",
    "value": "abc123xyz...",
    "path": "/",
    "expires": 1747449600,
    "httpOnly": true,
    "secure": true
  },
  {
    "domain": ".zalo.me",
    "name": "zpw_sek",
    "value": "def456...",
    "path": "/",
    "expires": -1,
    "httpOnly": false,
    "secure": true
  },
  ...
]
```

**Cách nhanh hơn — dùng extension Chrome**:

1. Cài extension "EditThisCookie" hoặc "Cookie-Editor" từ Chrome Web Store
2. Vào tab chat.zalo.me → click icon extension
3. Bấm "Export" → chọn format JSON
4. Toàn bộ cookies copy vào clipboard sẵn dạng JSON array
5. Paste vào file `cookies.json`

> ⚠️ Extension cookies có quyền đọc TẤT CẢ cookies của TẤT CẢ trang web. Sau khi extract xong, **gỡ extension hoặc disable** để không leak data các trang khác.

### 4.2 — Extract imei

```
1. Vẫn trong DevTools, mở tab "Console"
2. Gõ lệnh:
     localStorage.getItem('z_uuid') || localStorage.getItem('sh_z_uuid')
3. Enter → console trả về string dạng:
     "abcd1234-ef56-7890-ghij-klmnop123456"
4. Copy chuỗi đó (KHÔNG copy dấu nháy kép bao ngoài)
5. Đó là IMEI dùng cho zca-js
```

**Nếu cả 2 key đều null**:
- Có thể anh/chị login bằng QR mà chưa tương tác đủ → gửi 1-2 tin nhắn trong web → reload → thử lại
- Hoặc dùng key thay thế: `localStorage.getItem('imei')` hoặc `localStorage.getItem('deviceUid')`

### 4.3 — Extract userAgent

```
1. Vẫn trong Console, gõ:
     navigator.userAgent
2. Enter → console trả về string dạng:
     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
3. Copy NGUYÊN VĂN chuỗi đó
```

**Quan trọng**: userAgent PHẢI khớp với Chrome mà anh/chị đã extract cookies. Nếu sau này deploy listener lên Railway, server không tự đổi userAgent — vẫn dùng chuỗi này.

---

## Bước 5 — Paste 3 thứ vào skill

Format paste cho Claude Code:

```
COOKIES:
[paste nguyên JSON array]

IMEI:
abcd1234-ef56-7890-ghij-klmnop123456

USER_AGENT:
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
```

Skill sẽ ghi vào `zalo-listener/.env` ở format:

```env
ZALO_COOKIES_JSON='[{"domain":".zalo.me","name":"zpsid",...}]'
ZALO_IMEI=abcd1234-ef56-7890-ghij-klmnop123456
ZALO_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...
```

---

## Cookies expiration — khi nào cần re-extract?

- `zpsid` mặc định expire sau **30 ngày** (Zalo tự gia hạn nếu session active)
- Nếu listener crash với log `cookies invalid` → quay lại Bước 3 (login Chrome lại + extract lại)
- Bot bị khóa account → KHÔNG re-extract được nữa, phải đăng ký Zalo mới với số khác

**Best practice**: 
- Mỗi 2-3 tuần kiểm tra log listener xem có error cookies không
- Setup alert (Telegram/email) khi listener crash để biết kịp
- Backup cookies.json + imei + userAgent vào password manager để re-deploy nhanh

---

## Troubleshooting

| Lỗi | Nguyên nhân | Fix |
|---|---|---|
| `EZINIT` khi login | Cookies không đầy đủ (thiếu `zpsid` hoặc `zpw_sek`) | Extract lại đầy đủ các cookies bắt buộc trên |
| `Invalid imei` | imei sai format hoặc null | Mở Console, chạy đúng lệnh `localStorage.getItem('z_uuid')` |
| `Login failed: 401` | Cookies expired | Login lại Chrome, extract lại |
| `User-Agent mismatch` | Dùng UA khác với UA lúc extract cookies | Copy đúng `navigator.userAgent` của browser đã login |
| `Account locked` (sau vài giờ chạy) | Zalo detect bot pattern | Đọc [`zca-js-risks.md`](zca-js-risks.md), có thể phải đăng ký account mới |
