# claude-skills-vananh installer (Windows PowerShell)
# Cài 52 skill + 2 agent + settings + memory vào ~/.claude/
#
# Cách chạy 1 dòng trên máy mới:
#   irm https://raw.githubusercontent.com/vananhlaclac2810-cell/claude-skills-vananh/main/install.ps1 | iex
#
# Hoặc clone về rồi chạy:
#   git clone https://github.com/vananhlaclac2810-cell/claude-skills-vananh.git
#   cd claude-skills-vananh
#   .\install.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  claude-skills-vananh installer" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$REPO = "https://github.com/vananhlaclac2810-cell/claude-skills-vananh.git"
$CLAUDE_DIR = "$env:USERPROFILE\.claude"
$TEMP_DIR = "$env:TEMP\claude-skills-vananh-$(Get-Random)"
$TS = Get-Date -Format "yyyyMMdd-HHmmss"
$BACKUP = "$CLAUDE_DIR\backups\install-$TS"

# Step 1: Detect run mode (clone-then-run vs irm-piped)
$inRepo = Test-Path ".\skills" -PathType Container
if ($inRepo) {
    Write-Host "[1/5] Phát hiện chạy từ trong repo (skip clone)" -ForegroundColor Green
    $SRC = (Get-Location).Path
} else {
    Write-Host "[1/5] Clone repo về $TEMP_DIR ..." -ForegroundColor Green
    git clone --depth 1 $REPO $TEMP_DIR 2>&1 | Out-Null
    if (-not (Test-Path $TEMP_DIR)) {
        Write-Host "  ❌ Clone fail. Check git cài chưa + có internet không." -ForegroundColor Red
        exit 1
    }
    $SRC = $TEMP_DIR
}

# Step 2: Backup existing ~/.claude/skills, agents, settings
Write-Host "[2/5] Backup ~/.claude/ (skills + agents + settings) -> $BACKUP" -ForegroundColor Green
New-Item -ItemType Directory -Force -Path $BACKUP | Out-Null
foreach ($item in @("skills", "agents", "settings.json")) {
    $existing = Join-Path $CLAUDE_DIR $item
    if (Test-Path $existing) {
        Copy-Item -Recurse -Force $existing (Join-Path $BACKUP $item)
        Write-Host "  ✓ backup $item" -ForegroundColor Gray
    }
}

# Step 3: Install skills + agents
Write-Host "[3/5] Cài skills + agents vào ~/.claude/" -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "$CLAUDE_DIR\skills" | Out-Null
New-Item -ItemType Directory -Force -Path "$CLAUDE_DIR\agents" | Out-Null

Copy-Item -Recurse -Force "$SRC\skills\*" "$CLAUDE_DIR\skills\"
$skillCount = (Get-ChildItem -Directory "$CLAUDE_DIR\skills").Count
Write-Host "  ✓ $skillCount skills installed" -ForegroundColor Gray

Copy-Item -Recurse -Force "$SRC\agents\*" "$CLAUDE_DIR\agents\"
$agentCount = (Get-ChildItem "$CLAUDE_DIR\agents").Count
Write-Host "  ✓ $agentCount agents installed" -ForegroundColor Gray

# Step 4: Settings (merge nếu đã có theme khác)
Write-Host "[4/5] Cài settings.json (nếu chưa có)" -ForegroundColor Green
$settingsPath = "$CLAUDE_DIR\settings.json"
if (Test-Path $settingsPath) {
    Write-Host "  ⚠️  ~/.claude/settings.json đã tồn tại — KHÔNG ghi đè (đã backup)" -ForegroundColor Yellow
} else {
    Copy-Item "$SRC\settings.json" $settingsPath
    Write-Host "  ✓ settings.json installed" -ForegroundColor Gray
}

# Step 5: Memory (project-specific — chỉ cài nếu user xác nhận)
Write-Host "[5/5] Memory dự án D--SKILL-MARKETING-AGENT" -ForegroundColor Green
$memSrc = "$SRC\memory\D--SKILL-MARKETING-AGENT"
$memDst = "$CLAUDE_DIR\projects\D--SKILL-MARKETING-AGENT\memory"
if (Test-Path $memSrc) {
    New-Item -ItemType Directory -Force -Path $memDst | Out-Null
    Copy-Item -Recurse -Force "$memSrc\*" $memDst
    Write-Host "  ✓ Memory dự án D--SKILL-MARKETING-AGENT đã cài" -ForegroundColor Gray
}

# Cleanup temp
if (-not $inRepo -and (Test-Path $TEMP_DIR)) {
    Remove-Item -Recurse -Force $TEMP_DIR
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  ✅ DONE!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Skills: $CLAUDE_DIR\skills\ ($skillCount items)"
Write-Host "Agents: $CLAUDE_DIR\agents\ ($agentCount items)"
Write-Host "Backup: $BACKUP"
Write-Host ""
Write-Host "Mở Claude Code bất kỳ project nào để dùng skill."
Write-Host ""
Write-Host "Để update sau này:" -ForegroundColor Yellow
Write-Host "  cd <thư mục clone>; git pull; .\install.ps1" -ForegroundColor Yellow
Write-Host ""
