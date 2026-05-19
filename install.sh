#!/usr/bin/env bash
# claude-skills-vananh installer (Mac/Linux/WSL)
# Cài 52 skill + 2 agent + settings + memory vào ~/.claude/
#
# Cách chạy 1 dòng trên máy mới:
#   curl -fsSL https://raw.githubusercontent.com/vananhlaclac2810-cell/claude-skills-vananh/main/install.sh | bash
#
# Hoặc clone rồi chạy:
#   git clone https://github.com/vananhlaclac2810-cell/claude-skills-vananh.git
#   cd claude-skills-vananh
#   bash install.sh

set -euo pipefail

C_CYAN='\033[0;36m'; C_GREEN='\033[0;32m'; C_YELLOW='\033[1;33m'; C_RED='\033[0;31m'; C_GRAY='\033[0;90m'; C_OFF='\033[0m'

echo ""
echo -e "${C_CYAN}================================================${C_OFF}"
echo -e "${C_CYAN}  claude-skills-vananh installer${C_OFF}"
echo -e "${C_CYAN}================================================${C_OFF}"
echo ""

REPO="https://github.com/vananhlaclac2810-cell/claude-skills-vananh.git"
CLAUDE_DIR="${HOME}/.claude"
TEMP_DIR="/tmp/claude-skills-vananh-$RANDOM"
TS=$(date +%Y%m%d-%H%M%S)
BACKUP="${CLAUDE_DIR}/backups/install-${TS}"

# Step 1: Detect run mode
if [ -d "./skills" ]; then
    echo -e "${C_GREEN}[1/5] Phát hiện chạy từ trong repo (skip clone)${C_OFF}"
    SRC="$(pwd)"
else
    echo -e "${C_GREEN}[1/5] Clone repo về ${TEMP_DIR} ...${C_OFF}"
    git clone --depth 1 "$REPO" "$TEMP_DIR" >/dev/null 2>&1 || {
        echo -e "${C_RED}  ❌ Clone fail. Check git cài chưa + có internet không.${C_OFF}"
        exit 1
    }
    SRC="$TEMP_DIR"
fi

# Step 2: Backup
echo -e "${C_GREEN}[2/5] Backup ~/.claude/ -> $BACKUP${C_OFF}"
mkdir -p "$BACKUP"
for item in skills agents settings.json; do
    if [ -e "${CLAUDE_DIR}/${item}" ]; then
        cp -r "${CLAUDE_DIR}/${item}" "${BACKUP}/"
        echo -e "${C_GRAY}  ✓ backup ${item}${C_OFF}"
    fi
done

# Step 3: Install skills + agents
echo -e "${C_GREEN}[3/5] Cài skills + agents${C_OFF}"
mkdir -p "${CLAUDE_DIR}/skills" "${CLAUDE_DIR}/agents"
cp -r "${SRC}/skills/." "${CLAUDE_DIR}/skills/"
SKILL_COUNT=$(find "${CLAUDE_DIR}/skills" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
echo -e "${C_GRAY}  ✓ ${SKILL_COUNT} skills installed${C_OFF}"

cp -r "${SRC}/agents/." "${CLAUDE_DIR}/agents/"
AGENT_COUNT=$(find "${CLAUDE_DIR}/agents" -maxdepth 1 -mindepth 1 | wc -l | tr -d ' ')
echo -e "${C_GRAY}  ✓ ${AGENT_COUNT} agents installed${C_OFF}"

# Step 4: Settings
echo -e "${C_GREEN}[4/5] settings.json${C_OFF}"
if [ -f "${CLAUDE_DIR}/settings.json" ]; then
    echo -e "${C_YELLOW}  ⚠️  ~/.claude/settings.json đã tồn tại — KHÔNG ghi đè (đã backup)${C_OFF}"
else
    cp "${SRC}/settings.json" "${CLAUDE_DIR}/settings.json"
    echo -e "${C_GRAY}  ✓ settings.json installed${C_OFF}"
fi

# Step 5: Memory
echo -e "${C_GREEN}[5/5] Memory dự án D--SKILL-MARKETING-AGENT${C_OFF}"
MEM_SRC="${SRC}/memory/D--SKILL-MARKETING-AGENT"
MEM_DST="${CLAUDE_DIR}/projects/D--SKILL-MARKETING-AGENT/memory"
if [ -d "$MEM_SRC" ]; then
    mkdir -p "$MEM_DST"
    cp -r "${MEM_SRC}/." "${MEM_DST}/"
    echo -e "${C_GRAY}  ✓ Memory dự án D--SKILL-MARKETING-AGENT đã cài${C_OFF}"
fi

# Cleanup
[ -d "$TEMP_DIR" ] && rm -rf "$TEMP_DIR"

echo ""
echo -e "${C_CYAN}================================================${C_OFF}"
echo -e "${C_GREEN}  ✅ DONE!${C_OFF}"
echo -e "${C_CYAN}================================================${C_OFF}"
echo ""
echo "Skills: ${CLAUDE_DIR}/skills/ (${SKILL_COUNT} items)"
echo "Agents: ${CLAUDE_DIR}/agents/ (${AGENT_COUNT} items)"
echo "Backup: ${BACKUP}"
echo ""
echo "Mở Claude Code bất kỳ project nào để dùng skill."
echo ""
echo -e "${C_YELLOW}Để update sau này:${C_OFF}"
echo -e "${C_YELLOW}  cd <thư mục clone>; git pull; bash install.sh${C_OFF}"
echo ""
