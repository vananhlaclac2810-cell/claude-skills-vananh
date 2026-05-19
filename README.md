# claude-skills-vananh

Bộ skill cá nhân của **vananhlaclac2810** dùng với [Claude Code](https://claude.com/claude-code) — sync giữa nhiều máy tính qua GitHub.

**Nội dung:**
- 📦 **52 skills** (`skills/`) — biz-* / mkt-* / fb-* / design / market-research / ui-ux-pro-max / …
- 🤖 **2 agents** (`agents/`) — `mkt-script-hook-writer`, `mkt-full-video-phase3-packager`
- ⚙️ **settings.json** — config Claude (theme, etc.)
- 🧠 **memory/** — auto-memory cho dự án `D--SKILL-MARKETING-AGENT`

---

## 🚀 Cài trên máy mới (1 dòng)

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/vananhlaclac2810-cell/claude-skills-vananh/main/install.ps1 | iex
```

### Mac / Linux / WSL

```bash
curl -fsSL https://raw.githubusercontent.com/vananhlaclac2810-cell/claude-skills-vananh/main/install.sh | bash
```

Script tự động:
1. Backup `~/.claude/skills,agents,settings.json` cũ (nếu có) vào `~/.claude/backups/install-{timestamp}/`
2. Clone repo này
3. Copy `skills/`, `agents/`, `settings.json` vào `~/.claude/`
4. Copy `memory/D--SKILL-MARKETING-AGENT/` vào `~/.claude/projects/D--SKILL-MARKETING-AGENT/memory/`
5. Cleanup temp

Sau khi cài xong, mở Claude Code bất kỳ project nào → 52 skill + 2 agent sẽ có ngay.

---

## 🔄 Update trên máy mới (lần thứ 2 trở đi)

Đã có repo clone về (vd ở `~/claude-skills-vananh`):

```powershell
cd ~/claude-skills-vananh
git pull
.\install.ps1     # Windows
# bash install.sh   # Mac/Linux
```

Hoặc chạy lại one-liner ở trên (sẽ clone temp + cài đè).

---

## ⬆️ Push thay đổi lên GitHub (từ máy chính)

Khi cài/sửa skill ở `~/.claude/skills/` trên máy chính, sync ngược lên repo:

### Windows
```powershell
cd D:\claude-skills-vananh
.\sync.ps1
# hoặc kèm message: .\sync.ps1 "Thêm skill mkt-xyz"
```

Script `sync.ps1` sẽ:
1. Mirror `~/.claude/skills`, `agents`, `settings.json`, `projects/D--SKILL-MARKETING-AGENT/memory` → vào repo
2. `git add -A && git commit && git push`

### Mac/Linux (TODO)
Em sẽ viết sync.sh tương tự khi cần.

---

## 📁 Cấu trúc repo

```
claude-skills-vananh/
├── skills/                              ← ~/.claude/skills/
│   ├── biz-admin-leads-dashboard/
│   ├── biz-deploy-vercel/
│   ├── biz-email-setup/
│   ├── … (49 skill khác)
│   └── ui-ux-pro-max/
├── agents/                              ← ~/.claude/agents/
│   ├── mkt-full-video-phase3-packager.md
│   └── mkt-script-hook-writer.md
├── settings.json                        ← ~/.claude/settings.json
├── memory/
│   └── D--SKILL-MARKETING-AGENT/        ← ~/.claude/projects/D--SKILL-MARKETING-AGENT/memory/
│       ├── MEMORY.md
│       ├── project_*.md
│       ├── feedback_*.md
│       └── reference_*.md
├── install.ps1                          ← installer Windows
├── install.sh                           ← installer Mac/Linux
├── sync.ps1                             ← sync local → repo (Windows)
├── README.md
└── .gitignore
```

---

## ⚠️ Lưu ý

- **`~/.claude/.credentials.json` KHÔNG sync** — chứa token Claude account, mỗi máy login riêng.
- **`~/.claude/cache`, `sessions`, `shell-snapshots`, `file-history`, `backups` KHÔNG sync** — runtime data per machine.
- **MEMORY.md** chỉ là memory của 1 dự án (`D--SKILL-MARKETING-AGENT`). Dự án khác sẽ có memory riêng — KHÔNG bị ghi đè.
- Repo này PUBLIC — đừng commit anything có credential / API key.

---

## 🔗 Source

- Maintained by: vananhlaclac2810-cell <vananh.laclac2810@gmail.com>
- Skills gốc một phần từ: [Freedombuiders/BIZ.MKT.OS](https://github.com/Freedombuiders/BIZ.MKT.OS)
