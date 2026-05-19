# Domain Verification cho Resend (SPF/DKIM/MX)

Resend bắt buộc verify domain trước khi gửi email production. Trước verify, chỉ dùng được `onboarding@resend.dev` (limited, dễ vào spam, không pro). Sau verify, gửi từ `noreply@yourbrand.vn` / `hello@yourbrand.vn` / bất kỳ alias nào trên domain.

Quy trình: ~10 phút thao tác + 5-30 phút đợi DNS propagate.

---

## Bước 1 — Add domain vào Resend

1. Login [resend.com](https://resend.com) → sidebar **Domains** → **Add Domain**
2. Nhập domain root (ví dụ `yourbrand.vn`, không `www.yourbrand.vn`)
3. Chọn region: **Asia/Pacific** (Singapore) cho VN traffic
4. Resend hiển thị 3 nhóm DNS record cần add

## Bước 2 — Add DNS record

Resend trả về 3 record (đôi khi 4 nếu enable receiving):

| Type | Name/Host | Value | Mục đích |
|---|---|---|---|
| **MX** (optional) | `send` (= `send.yourbrand.vn`) | `feedback-smtp.us-east-1.amazonses.com` priority 10 | Bounce/complaint receiving |
| **TXT (SPF)** | `send` (= `send.yourbrand.vn`) | `v=spf1 include:amazonses.com ~all` | ISP biết Resend được phép gửi thay anh/chị |
| **TXT (DKIM)** | `resend._domainkey` | `p=MIGfMA0GCS... (chuỗi dài)` | Chữ ký số chứng thực email không bị tamper |
| **TXT (DMARC, optional nhưng nên có)** | `_dmarc` | `v=DMARC1; p=none;` | Policy báo cho ISP khi SPF/DKIM fail |

---

## Hướng dẫn add theo DNS provider phổ biến VN

### Cloudflare (recommended — nhanh nhất, free)
1. Dashboard → chọn domain → tab **DNS** → **Add record**
2. Type = TXT (hoặc MX), Name = `send` hoặc `resend._domainkey`, Content = paste từ Resend
3. TTL = Auto, Proxy status = **DNS only** (mây xám, không cam — nếu cam Cloudflare sẽ proxy email gây lỗi)
4. Save. Propagate ~1-5 phút.

### Namecheap
1. Dashboard → Domain List → Manage → tab **Advanced DNS**
2. Add New Record → Type TXT/MX → Host = `send` (không gõ full `send.yourbrand.vn`), Value = paste
3. TTL = Automatic. Propagate 5-30 phút.

### GoDaddy
1. My Products → DNS → Add → chọn Type
2. Name = `send` hoặc `resend._domainkey`, Value = paste
3. TTL = 1 hour. Propagate 10-30 phút.

### PA Vietnam / Mắt Bão / Nhân Hòa (registrar VN phổ biến)
1. Đăng nhập control panel → Quản lý DNS / DNS Management
2. UI khác nhau, nhưng đều có "Thêm bản ghi" / "Add Record"
3. Chọn loại bản ghi (TXT, MX), nhập Host + Value như bảng trên
4. Một số provider VN không cho phép TTL thấp → propagate có thể lên 1-2h

### Vercel DNS (nếu domain mua qua Vercel)
1. Vercel dashboard → Domains → chọn domain → **DNS Records**
2. Add → Type TXT/MX, Name = `send` / `resend._domainkey`, Value = paste
3. Propagate ~1 phút.

---

## Bước 3 — Verify

1. Sau khi add xong, quay lại Resend → Domains → click **Verify**
2. Resend check DNS bằng `dig`. Nếu thấy đủ 3 record → status chuyển **Verified** ✓
3. Nếu fail → đợi thêm 5-10 phút và retry. Most common: TTL chưa propagate.

**Kiểm tra manual** (nếu Resend báo not found nhưng anh/chị đã add):
```bash
# Check SPF
dig +short TXT send.yourbrand.vn

# Check DKIM  
dig +short TXT resend._domainkey.yourbrand.vn

# Both phải trả về value khớp với Resend setup page
```

Nếu `dig` trả về rỗng = chưa propagate. Đợi thêm.
Nếu trả về giá trị khác = anh/chị paste sai value, vào DNS provider sửa lại.

---

## Bước 4 — Set FROM address

Sau khi verified, update env var:

```env
# Trước verify (chỉ dùng dev/test):
RESEND_FROM_EMAIL=onboarding@resend.dev

# Sau verify (production):
RESEND_FROM_EMAIL=hello@yourbrand.vn
# hoặc
RESEND_FROM_EMAIL=Tên Brand <hello@yourbrand.vn>
```

Format `"Tên Brand <email>"` cho phép custom display name trong inbox của lead — recommended cho B2C VN.

---

## Khi nào KHÔNG verify được

- **Domain mua trên Tencent/Aliyun (CN registrar)**: DNS propagation có thể bị block bởi GFW khi check từ AWS US. → Move DNS sang Cloudflare (free, fast).
- **Subdomain only (ví dụ `app.bigcorp.com`)**: Cần access DNS của parent domain. Nếu không có → dùng tracking subdomain Resend gợi ý.
- **Free hosting có DNS managed (Wix, Squarespace)**: Mỗi platform có UI khác, search "[platform] add TXT record". Đôi khi không cho phép subdomain custom — phải upgrade plan.

---

## Anti-pattern

- ❌ Add SPF cho root domain (`@`) thay vì subdomain `send` → conflict với SPF của Google Workspace/email server hiện tại.
- ❌ Wrap value SPF/DKIM bằng dấu nháy đôi khi paste vào DNS panel → một số provider tự thêm nháy, gây value sai. Paste raw không nháy.
- ❌ Set proxied (orange cloud) cho MX/TXT trên Cloudflare → Cloudflare reverse-proxy không apply cho DNS records, nhưng UI cho phép → confusion. Luôn để **DNS only** (gray cloud) cho mail records.
- ❌ Delete DKIM record sau verify để "clean DNS" → Resend re-check định kỳ, sẽ revoke verification.
