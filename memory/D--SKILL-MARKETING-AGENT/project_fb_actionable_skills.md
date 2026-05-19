---
name: Bộ 3 skill viết bài Facebook actionable post (đã hoàn thành)
description: 3 skill viết bài FB tiếng Việt — core (nguyên tắc nền), megalist (cẩm nang/tra cứu), relatable-numbered (đồng cảm/viral). Đã cài tại `C:\Users\ADMIN\.claude\skills\`
type: project
originSessionId: 624400cb-4671-4013-baba-5289e87d66cf
---
## 3 skill đã tạo (2026-05-11)

| Skill | Dùng khi | Vị trí |
|---|---|---|
| `fb-actionable-post-core` | Meta — nguyên tắc nền chung cho mọi list post (hook, ẩn dụ, ngôn ngữ Việt, 8 anti-patterns, kết chốt). 2 skill kia đều tham chiếu vào đây | `C:\Users\ADMIN\.claude\skills\fb-actionable-post-core\SKILL.md` |
| `fb-megalist-post` | Bài liệt kê đầy đủ 15-40 mục, format `[Tên]: [giải thích 1 dòng]`, tone authority + trấn an. Phù hợp: triệu chứng, dấu hiệu, checklist, cẩm nang tra cứu | `C:\Users\ADMIN\.claude\skills\fb-megalist-post\SKILL.md` |
| `fb-relatable-numbered-post` | Bài "đặc sản / chuyện chỉ X mới hiểu" — 8-15 mục đánh số emoji, ẩn dụ sinh động + micro-scene, chuyển tông hài→sâu lắng. Mục tiêu: viral + share | `C:\Users\ADMIN\.claude\skills\fb-relatable-numbered-post\SKILL.md` |

**Nguồn pattern:** rút từ 2 bài Facebook user cung cấp (tổng hợp hiện tượng sinh lý trẻ sơ sinh + "Đặc sản em bé dưới 1 tháng" của Mẹ Thanh 2 lứa).

**Quyết định khi viết:**
- Domain: generic (dùng được mọi ngách) nhưng có note riêng cho mẹ & bé / Dr.Maya
- Cấu trúc: tách 3 skill thay vì 1 skill gộp 2 mode — trigger rõ ràng hơn
- Test cases: không setup eval formal, để user tự test bằng prompt gợi ý

**Why:** User muốn đóng gói pattern viết bài FB để tái sử dụng cho fanpage Dr.Maya và các ngành khác trong tương lai. Tách 3 skill cho phép dùng riêng từng dạng mà vẫn share được nguyên tắc nền qua skill core.

**How to apply:**
- Khi user yêu cầu viết bài FB cẩm nang/tra cứu → `fb-megalist-post` auto trigger
- Khi user yêu cầu viết bài "đặc sản"/viral → `fb-relatable-numbered-post` auto trigger
- Cả 2 skill trên đều yêu cầu đọc thêm `fb-actionable-post-core` để áp dụng nguyên tắc chung
- Nếu sau này user thấy skill trigger sai (over/under), chạy description optimization của skill-creator để chỉnh
