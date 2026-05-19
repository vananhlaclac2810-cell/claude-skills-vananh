# claude-skills-vananh sync (Windows)
# Đẩy thay đổi từ ~/.claude/ về repo này rồi commit + push lên GitHub.
#
# Cách dùng:
#   cd D:\claude-skills-vananh
#   .\sync.ps1
#   # hoặc thêm message: .\sync.ps1 "Thêm skill XYZ"

param([string]$Message = "")

$ErrorActionPreference = "Stop"
$CLAUDE_DIR = "$env:USERPROFILE\.claude"
$REPO_DIR = $PSScriptRoot

if (-not $REPO_DIR) { $REPO_DIR = (Get-Location).Path }

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  claude-skills-vananh SYNC" -ForegroundColor Cyan
Write-Host "  $REPO_DIR <- $CLAUDE_DIR" -ForegroundColor Gray
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Mirror skills, agents, settings, memory FROM ~/.claude TO repo
Write-Host "[1/3] Mirror skills + agents + settings + memory về repo..." -ForegroundColor Green

# Skills (mirror — xoá skill không còn tồn tại ở ~)
if (Test-Path "$REPO_DIR\skills") { Remove-Item -Recurse -Force "$REPO_DIR\skills" }
Copy-Item -Recurse "$CLAUDE_DIR\skills" "$REPO_DIR\skills"
$skillCount = (Get-ChildItem -Directory "$REPO_DIR\skills").Count
Write-Host "  ✓ $skillCount skills" -ForegroundColor Gray

# Agents
if (Test-Path "$REPO_DIR\agents") { Remove-Item -Recurse -Force "$REPO_DIR\agents" }
Copy-Item -Recurse "$CLAUDE_DIR\agents" "$REPO_DIR\agents"
$agentCount = (Get-ChildItem "$REPO_DIR\agents").Count
Write-Host "  ✓ $agentCount agents" -ForegroundColor Gray

# Settings
Copy-Item "$CLAUDE_DIR\settings.json" "$REPO_DIR\settings.json" -Force
Write-Host "  ✓ settings.json" -ForegroundColor Gray

# Memory
$memSrc = "$CLAUDE_DIR\projects\D--SKILL-MARKETING-AGENT\memory"
$memDst = "$REPO_DIR\memory\D--SKILL-MARKETING-AGENT"
if (Test-Path $memSrc) {
    if (Test-Path $memDst) { Remove-Item -Recurse -Force $memDst }
    New-Item -ItemType Directory -Force -Path $memDst | Out-Null
    Copy-Item -Recurse "$memSrc\*" $memDst
    $memCount = (Get-ChildItem $memDst).Count
    Write-Host "  ✓ memory D--SKILL-MARKETING-AGENT ($memCount file)" -ForegroundColor Gray
}

# Step 2: Git diff preview
Write-Host "[2/3] Git status..." -ForegroundColor Green
Set-Location $REPO_DIR
$gitStatus = git status --short
if ([string]::IsNullOrWhiteSpace($gitStatus)) {
    Write-Host "  ✓ Không có thay đổi, không cần commit." -ForegroundColor Gray
    Write-Host ""
    Write-Host "✅ DONE — repo đã đồng bộ với máy local." -ForegroundColor Green
    return
}
Write-Host $gitStatus -ForegroundColor Gray

# Step 3: Commit + push
Write-Host "[3/3] Commit + push..." -ForegroundColor Green
git add -A
if ([string]::IsNullOrWhiteSpace($Message)) {
    $Message = "Sync skills/agents/settings/memory from local — $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}
git commit -m $Message
git push

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  ✅ PUSHED!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Trên máy khác chỉ cần:"
Write-Host "  cd <thư mục clone>; git pull; .\install.ps1" -ForegroundColor Yellow
Write-Host ""
