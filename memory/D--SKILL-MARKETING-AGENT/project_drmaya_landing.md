---
name: Dr.Maya — Landing page Dầu Húng Chanh trên thieuvananh.vn
description: Context cho landing page Dr.Maya Dầu Húng Chanh đã deploy lên Vercel với domain thieuvananh.vn
type: project
originSessionId: 0e6c5750-bc10-4521-bdc5-1c201304c2d3
---
User đã hoàn tất launch landing page Dr.Maya — sản phẩm **Dầu Húng Chanh** — vào ngày 2026-05-11.

**Stack & hạ tầng:**
- Source: `D:\SKILL MARKETING AGENT\landing-dau-hung-chanh\index.html` (HTML + Tailwind CDN, single file)
- Hosting: Vercel — project `landing-dau-hung-chanh` thuộc account `vananhlaclac2810-7436` (email `vananh.laclac2810@gmail.com` của Dr.Maya)
- Domain: `thieuvananh.vn` mua tại **iNET** (portal.inet.vn) — đã đổi nameserver sang `ns1.vercel-dns.com` + `ns2.vercel-dns.com`, Vercel tự quản lý DNS
- URL live: https://thieuvananh.vn và https://www.thieuvananh.vn
- URL Vercel dự phòng: https://landing-dau-hung-chanh.vercel.app

**Bảng màu brand Dr.Maya đang dùng:**
- Maya Green primary `#2E7D5B`
- Honey Gold accent `#E8A33D`
- Cream background `#FBF7F0`

**Sản phẩm:**
- Dầu Húng Chanh Dr.Maya cho bé từ 6 tháng tuổi, giá 250.000đ/chai 30ml
- 4 thành phần: húng chanh, mật ong rừng, gừng tươi, bạc hà

**Why:** User đang dùng landing này để bán sản phẩm Dr.Maya, target mẹ bỉm 25–40 tuổi. Mọi thay đổi UI/UX/copy cần giữ tone an toàn, dịu nhẹ, thiên nhiên, đáng tin.

**How to apply:** 
- Khi user yêu cầu sửa landing → edit `D:\SKILL MARKETING AGENT\landing-dau-hung-chanh\index.html` → deploy bằng `cd "D:/SKILL MARKETING AGENT/landing-dau-hung-chanh" && vercel deploy --prod --yes`
- Vercel CLI đã login sẵn với account `vananhlaclac2810-7436`
- Lưu ý font DM Serif Display hiện không support tốt dấu kép tiếng Việt ("ầ" bị tách thành "â`") — đã ghi nhận để fix
- Cần làm tiếp khi user yêu cầu: gắn Microsoft Clarity tracking, wire form → Telegram Bot, thay placeholder bằng asset thật
