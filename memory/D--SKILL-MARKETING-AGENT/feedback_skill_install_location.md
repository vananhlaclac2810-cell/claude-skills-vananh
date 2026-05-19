---
name: Quy tắc cài skill — user-level mặc định
description: User prefers installing Claude Code skills to user-level (C:\Users\ADMIN\.claude\skills\) by default, only using project-level when skill is truly project-specific
type: feedback
originSessionId: 0e6c5750-bc10-4521-bdc5-1c201304c2d3
---
Khi cài skill mới cho user, **mặc định cài vào `C:\Users\ADMIN\.claude\skills\`** (user-level), không cài vào `.claude/skills/` của project trừ khi skill thực sự chỉ dùng riêng cho project đó.

**Quy tắc đơn giản:**
- Skill dùng được ở >1 project (UI/UX, design, general tooling) → **user-level (ổ C)**
- Skill chỉ project này hiểu (logic Dr.Maya/MamaJoy riêng, data project) → **project-level (ổ D)**

**Why:** User xác nhận đây là cách tổ chức hợp lý nhất — cài 1 lần xài mọi project, không mất khi đổi/xóa project, update 1 chỗ áp dụng all. Hỏi user trước khi chọn project-level, vì 90% trường hợp họ muốn user-level.

**How to apply:** Khi user yêu cầu cài skill từ GitHub/marketplace/source khác, mặc định copy vào `C:\Users\ADMIN\.claude\skills\<skill-name>\`. Chỉ đề xuất project-level nếu skill rõ ràng phụ thuộc data/logic riêng của project, hoặc user muốn commit vào git repo của project để share team.
