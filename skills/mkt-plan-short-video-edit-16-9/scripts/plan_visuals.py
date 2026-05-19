#!/usr/bin/env python3
"""Build visual-plan.json scaffold from script.txt + transcript.json.

This is the MAIN planner. Two modes:

  native (default) — script writes a SCAFFOLD visual-plan.json with reasonable
                     defaults (5-scene knowledge skeleton, default tier-letters,
                     default metaphors per archetype). Surrounding LLM (Claude
                     in conversation) edits the file to fill scene-specific
                     details before approval.
  claude-api      — if ANTHROPIC_API_KEY env var is set, calls Claude with
                     extended thinking + system prompt built from references/.
                     Writes a complete plan automatically.

Usage:
    python3 plan_visuals.py --workspace <dir> [--llm-mode native|claude-api]
                            [--brand claude|deepseek|openai|gemini|generic]
                            [--scenes-outline <path>] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SCHEMA_PATH = SKILL_DIR / "assets" / "templates" / "visual-plan.schema.json"

# Path to the editor skill — we reuse its detect_scenes.py if present.
EDITOR_SKILL_CANDIDATES = [
    SKILL_DIR.parent / "mkt-hyperframe-talking-head-video-16-9" / "scripts" / "detect_scenes.py",
    Path.home() / ".claude" / "skills" / "mkt-hyperframe-talking-head-video-16-9" / "scripts" / "detect_scenes.py",
]


# ---------- helpers ----------

def find_editor_detect_scenes() -> Path | None:
    for c in EDITOR_SKILL_CANDIDATES:
        if c.exists():
            return c
    return None


def load_transcript(workspace: Path) -> list[dict]:
    cleaned = workspace / "transcript-cleaned.json"
    if cleaned.exists():
        return json.loads(cleaned.read_text())
    raw = workspace / "transcript.json"
    if raw.exists():
        return json.loads(raw.read_text())
    raise FileNotFoundError(f"Neither transcript-cleaned.json nor transcript.json found in {workspace}")


def load_or_build_outline(workspace: Path) -> list[dict]:
    """Return scene outline. Prefer existing scenes-outline.json; else call
    editor's detect_scenes.py if available; else build a heuristic 5-scene split.
    """
    outline_path = workspace / "scenes-outline.json"
    if outline_path.exists():
        return json.loads(outline_path.read_text())

    detect = find_editor_detect_scenes()
    if detect is not None:
        try:
            subprocess.run(
                ["python3", str(detect), "--workspace", str(workspace)],
                check=True, capture_output=True,
            )
            if outline_path.exists():
                return json.loads(outline_path.read_text())
        except subprocess.CalledProcessError as e:
            print(f"[plan] detect_scenes.py failed: {e.stderr.decode(errors='ignore')}", file=sys.stderr)

    # Fallback: 5-scene heuristic based on transcript word boundaries.
    words = load_transcript(workspace)
    if not words:
        raise RuntimeError("Empty transcript; cannot build outline.")
    total = float(words[-1]["end"])
    boundaries = [0.0, total * 0.22, total * 0.45, total * 0.78, total * 0.90, total]
    kinds = ["hook", "problem", "solution", "recap", "cta"]
    variants = ["tier-row", "chats-stack", "hero-orb", "counter-row", "terminal-row"]
    return [
        {
            "num": i + 1, "kind": kinds[i], "variant": variants[i],
            "start": round(boundaries[i], 2), "end": round(boundaries[i + 1], 2),
            "kicker": "", "heading": "",
        }
        for i in range(5)
    ]


# ---------- defaults per archetype (production-tested from loi-ich-claude-ai) ----------

DEFAULT_TIER_LETTER = {
    "hook": "8h", "problem": "3×", "solution": "∞", "recap": "15h", "cta": "AI",
    "fail": "✗", "pivot": "→", "differentiator": "✓", "proof": "100", "result": "+2",
}

DEFAULT_METAPHOR = {
    "hook": "dong-ho-cat",
    "problem": "broken-chain",
    "fail": "broken-chain",
    "pivot": "nga-ba-duong",
    "solution": "robot-orb-with-tasks",
    "differentiator": "scale-tilt",
    "proof": "paper-stack-100",
    "recap": "heo-dat-vo-ket-sat",
    "result": "heo-dat-vo-ket-sat",
    "cta": "gift-box-open",
}

# Default Visual Thinking type per archetype (see references/visual-thinking-types.md).
DEFAULT_VISUAL_TYPE = {
    "hook": "before-after",
    "problem": "icon-grid",
    "fail": "icon-grid",
    "pivot": "before-after",
    "solution": "three-pillar",
    "differentiator": "comparison-table",
    "proof": "number-infographic",
    "result": "number-infographic",
    "recap": "number-infographic",
    "cta": "icon-grid",
}

DEFAULT_PALETTE = {
    "hook": ["rose", "lime", "amber"],
    "problem": ["orange", "rose", "slate"],
    "fail": ["orange", "rose", "slate"],
    "pivot": ["violet", "amber"],
    "solution": ["violet", "cyan", "claude-orange"],
    "differentiator": ["cyan", "lime"],
    "proof": ["cyan", "amber"],
    "recap": ["lime", "amber", "rose"],
    "result": ["lime", "amber"],
    "cta": ["pink", "amber", "lime"],
}

DEFAULT_BADGES = {
    "hook": [
        {"pos": "tr", "color": "orange", "icon": "⏰", "num": "8h", "label": "Trước đây"},
        {"pos": "bl", "color": "green", "icon": "✅", "num": "0h", "label": "Giờ cần làm"},
    ],
    "problem": [
        {"pos": "tr", "color": "purple", "icon": "🔄", "num": "3×", "label": "Nhắc lại"},
        {"pos": "bl", "color": "orange", "icon": "😩", "num": "+", "label": "Mệt đầu"},
    ],
    "solution": [
        {"pos": "tr", "color": "cyan", "icon": "📄", "num": "100", "label": "Trang/lần"},
        {"pos": "br", "color": "orange", "icon": "✅", "num": "3", "label": "Output loại"},
    ],
    "recap": [
        {"pos": "tr", "color": "green", "icon": "⏱️", "num": "15h", "label": "Tiết kiệm/tuần"},
        {"pos": "bl", "color": "orange", "icon": "👥", "num": "+2", "label": "Khách hàng mới"},
    ],
    "cta": [
        {"pos": "tr", "color": "orange", "icon": "💬", "num": "AI", "label": "Comment ngay"},
    ],
}

DEFAULT_ITEMS = {
    "hook": [
        {"icon": "✍️", "label": "Soạn email"},
        {"icon": "📚", "label": "Đọc tài liệu"},
        {"icon": "📊", "label": "Tổng hợp báo cáo"},
    ],
    "problem": [
        {"icon": "💬", "label": "Đứt mạch giữa chừng"},
        {"icon": "🔁", "label": "Phải nhắc lại"},
    ],
    "solution": [
        {"icon": "📝", "label": "Bản nháp"},
        {"icon": "📊", "label": "Báo cáo"},
        {"icon": "📧", "label": "Email"},
        {"icon": "📦", "label": "100 trang"},
    ],
    "recap": [
        {"icon": "⏱️", "label": "−15h/tuần"},
        {"icon": "👥", "label": "+2 khách"},
    ],
    "cta": [
        {"icon": "🤖", "label": "Cách dùng tool"},
        {"icon": "⚡", "label": "Prompt + quy trình"},
    ],
}


# ---------- per-metaphor layout sketches (from visual-thinking-library.md) ----------

METAPHOR_LAYOUTS: dict[str, dict[str, str]] = {
    "dong-ho-cat": {
        "title": "TRƯỚC ĐÂY · 8H ↔ HÔM NAY · 0H",
        "subtitle": "Cùng một việc, hai trạng thái thời gian.",
        "layout": (
            "LEFT: hand-drawn hourglass đầy cát rose (#fb7185), đứng yên, label dưới: 'TRƯỚC ĐÂY · 8H'. "
            "RIGHT: hourglass vơi gần hết, cát còn ít hạt rơi cuối, label dưới 'HÔM NAY · 0H' màu lime (#a3e635). "
            "CENTER: mũi tên cong cream-edge nối từ trái sang phải, label hand-written serif italic 'Tự động'."
        ),
        "decor": "3 doodle annotation tags floating: 'Việc lặp đi lặp lại', 'Não mệt hơn tay', 'Sáng dậy việc xong'.",
    },
    "heo-dat-vo-ket-sat": {
        "title": "−15H/TUẦN · +2 KHÁCH HÀNG",
        "subtitle": "Cũ nứt vỡ. Mới gọn ghẽ.",
        "layout": (
            "LEFT BLOCK: heo đất hồng (#f9a8d4) lớn nứt vỡ, xu vàng tumble ra (ký hiệu $, ₫), label 'TRƯỚC' rose. "
            "RIGHT BLOCK: két sắt mini blue-grey #4d6bfe gọn, bo góc chắc, 1 xu trên nóc, label 'GIỜ' lime (#a3e635). "
            "CENTER: mũi tên cong rộng amber với chữ '−15h' bên trên + '+2 khách' bên dưới."
        ),
        "decor": "Tag floating 'Tiết kiệm 15h/tuần', '+2 khách không thuê thêm ai', 'Thời gian = tiền'.",
    },
    "broken-chain": {
        "title": "ĐỨT MẠCH GIỮA CHỪNG",
        "subtitle": "Hỏi đáp ổn — giao việc dài là rớt context.",
        "layout": (
            "CENTER: sợi xích kim loại 5 mắt nối ngang slate (#64748b), mắt giữa nứt vỡ với chip va chạm. "
            "LEFT END: AI logo tròn nhỏ (CHATGPT / GEMINI text label). "
            "RIGHT END: output trống dashed-border, dấu hỏi '?' ở giữa. "
            "Stamp đỏ orange (#fb923c) chéo góc dưới: 'ĐỨT MẠCH'."
        ),
        "decor": "3 chip va chạm văng ra, doodle 'ZAP', 'Phải nhắc lại từ đầu' annotation tag.",
    },
    "robot-orb-with-tasks": {
        "title": "GIAO VIỆC — ĐỂ NÓ TỰ CHẠY",
        "subtitle": "Một orb, nhiều output sẵn sàng.",
        "layout": (
            "CENTER: orb tròn glow violet (#a78bfa) với robot face minimal, label 'CLAUDE AI'. "
            "Từ orb radiate 4 mũi tên cream-edge ra 4 góc, mỗi mũi tên dẫn tới 1 output card: "
            "📝 'Bản nháp' (TL), 📊 'Báo cáo' (TR), 📧 'Email sẵn' (BL), 📦 '100 trang' (BR). "
            "Background: nhẹ glow violet."
        ),
        "decor": "Tag floating 'Tự bấm máy thay mình', 'Mình ngủ · sáng có output', 'Nhớ cả cuộc trò chuyện'.",
    },
    "ong-nuoc-flow": {
        "title": "TÀI LIỆU 100 TRANG → OUTPUT",
        "subtitle": "Một dòng chảy, không cần chia nhỏ.",
        "layout": (
            "LEFT: stack tài liệu dày '100 TRANG', cyan (#67e8f9). "
            "Ống nước (pipe) cong từ trái qua phải nối stack vào orb Claude (#a78bfa) ở giữa, sau đó toả ra 3 output ở phải. "
            "Label trên ống: 'Đọc một lần · Nhớ luôn'."
        ),
        "decor": "Doodle drip nhỏ rơi từ ống, tag 'Không cần chunk', 'Không cần re-prompt'.",
    },
    "nga-ba-duong": {
        "title": "RẼ HƯỚNG · TỪ HỎI ĐÁP SANG GIAO VIỆC",
        "subtitle": "Cùng cây cung — đường khác.",
        "layout": (
            "Bản đồ ngã ba đường hand-drawn cream. "
            "Đường trái dẫn vào màn hình chat 'HỎI ĐÁP' rose (#fb7185), bị tắc cuối đường. "
            "Đường phải dẫn vào tower orb violet (#a78bfa) 'GIAO VIỆC', open-ended. "
            "Mũi tên đi theo phải, có pin ghim đỏ."
        ),
        "decor": "Compass nhỏ góc phải, biển báo cũ 'HỎI HOÀI', biển báo mới 'GIAO LUÔN'.",
    },
    "canh-cua-mo": {
        "title": "CỬA MỞ · CONTEXT CŨ KHÔNG GIỚI HẠN",
        "subtitle": "Memory dài, không reset.",
        "layout": (
            "Cánh cửa gỗ hand-drawn mở rộng, ánh sáng cyan (#67e8f9) tỏa từ trong ra. "
            "Bên trong là book stack + chat bubbles cũ xếp tầng. "
            "Trên cửa label 'CONTEXT'. Bên ngoài cửa là người (silhouette) bước vào."
        ),
        "decor": "Tag 'Nhớ cuộc trò chuyện dài', 'Không cần nhắc lại', 'Phù hợp dự án nhiều tháng'.",
    },
    "oc-sen-ten-lua": {
        "title": "ỐC SÊN ↔ TÊN LỬA",
        "subtitle": "Tốc độ làm việc, không phải tốc độ trả lời.",
        "layout": (
            "LEFT: ốc sên hand-drawn slate, label 'AI HỎI ĐÁP' rose. "
            "RIGHT: tên lửa hand-drawn warm orange (#fb923c) bay lên, label 'AI GIAO VIỆC' violet. "
            "Khoảng giữa có dải sao li ti."
        ),
        "decor": "Tag '8h → 0h', '5×', 'Throughput chứ không phải latency'.",
    },
    "lego-ghep": {
        "title": "GHÉP TỪNG MIẾNG · MỘT KHỐI HOÀN CHỈNH",
        "subtitle": "Multi-step, không drop step nào.",
        "layout": (
            "5 miếng lego color-coded (rose, amber, lime, cyan, violet) ghép thành 1 khối tower hoàn chỉnh. "
            "Mỗi miếng có icon nhỏ: 📝 / 📊 / 📧 / ✅ / 📦. "
            "Ánh sáng nhẹ trên đỉnh khối."
        ),
        "decor": "Tag 'Đầy đủ steps', 'Không drop giữa chừng', 'Multi-step OK'.",
    },
    "bac-thang": {
        "title": "BƯỚC LÊN · MỖI NGÀY MỘT TIER",
        "subtitle": "Progression không reset.",
        "layout": (
            "5 bậc thang dốc lên, mỗi bậc có label: 'Ngày 1 · Hỏi đáp', 'Ngày 7 · Giao việc nhỏ', "
            "'Ngày 14 · Multi-step', 'Ngày 21 · Auto pipeline', 'Ngày 30 · Giao cả workflow'. "
            "Người silhouette đứng ở bậc cao nhất."
        ),
        "decor": "Mây cream nhẹ trên đỉnh, sun ray, tag 'Hành trình 30 ngày'.",
    },
    "coc-day-tran": {
        "title": "CỐC ĐẦY · KHÔNG RÓT THÊM",
        "subtitle": "Context window đã đủ.",
        "layout": (
            "LEFT: cốc nhỏ tràn nước rose, label 'GPT cũ — context tràn'. "
            "RIGHT: cốc lớn còn nửa, label 'CLAUDE — vẫn còn 50%'. "
            "Vòi nước phía trên đổ vào cả hai."
        ),
        "decor": "Tag '200K tokens', 'Đủ để đọc cả tài liệu dài', 'Không cần truncate'.",
    },
    "but-mau-ket-not": {
        "title": "NỐI Ý — BÚT CHÌ + BÚT BI",
        "subtitle": "Cùng nét, khác phong cách.",
        "layout": (
            "Hand-drawn 2 cây bút bắt chéo trên giấy cream. "
            "Bút trái: chì grey, vẽ outline. Bút phải: bi đỏ, fill detail. "
            "Tạo thành một sketch hoàn chỉnh ở giữa: chữ 'GIAO VIỆC + BỐI CẢNH = OUTPUT'."
        ),
        "decor": "Tag 'Prompt + memory', 'Không phải là một, mà là cả hệ', '1 + 1 = 3'.",
    },
    "magnifying-glass": {
        "title": "ZOOM VÀO TÀI LIỆU 100 TRANG",
        "subtitle": "Tìm chi tiết nhỏ trong khối lớn.",
        "layout": (
            "Stack tài liệu lớn, một kính lúp hand-drawn cyan (#67e8f9) zoom vào trang giữa. "
            "Trong vòng kính lúp hiện 1 đoạn highlight amber: 'Điều khoản số 47 · trang 82'. "
            "Bên dưới chú thích: 'Claude tìm trong 1 lần đọc, không cần grep'."
        ),
        "decor": "Tag 'Không cần chia nhỏ', 'Đọc 1 lần · nhớ luôn', '100 trang/file'.",
    },
    "scale-tilt": {
        "title": "CÁN CÂN NGHIÊNG VỀ AI",
        "subtitle": "−15h ↔ +2 khách.",
        "layout": (
            "Cán cân hand-drawn slate đơn giản. Đĩa trái nặng xuống: '40H/TUẦN' rose. "
            "Đĩa phải nhẹ lên: '25H/TUẦN' lime. "
            "Trên nóc cán cân số '−15H/TUẦN' lớn amber."
        ),
        "decor": "Tag '+2 khách', 'Không thuê thêm ai', 'Tỉ lệ thuận với hiệu quả'.",
    },
    "gear-chain": {
        "title": "MULTI-STEP · MỌI MẮT XÍCH KHỚP NHAU",
        "subtitle": "Workflow tự chạy không kẹt.",
        "layout": (
            "5 gear lớn nhỏ ghép thành chain ngang: gear 1 'INGEST', gear 2 'PARSE', "
            "gear 3 'PLAN', gear 4 'WRITE', gear 5 'DELIVER'. Tất cả xoay theo. "
            "Color: violet, cyan, lime, amber, claude-orange."
        ),
        "decor": "Tag 'Không kẹt giữa chừng', '5 steps · 1 prompt'.",
    },
    "gear-jam": {
        "title": "GEAR KẸT · GPT BỎ GIỮA CHỪNG",
        "subtitle": "Cố nối xích, mất cả ngày.",
        "layout": (
            "3 gear xếp ngang. Gear 2 ở giữa kẹt một viên đá. Gear 1 và 3 vẫn cố quay nhưng đứng yên. "
            "Gear màu rose. Tia điện zap nhỏ phát ra từ chỗ kẹt."
        ),
        "decor": "Tag 'Đứt mạch', 'Phải nhắc lại', 'Mệt cái đầu'.",
    },
    "gift-box-open": {
        "title": "COMMENT AI · NHẬN GIFT",
        "subtitle": "Tài liệu + workflow.",
        "layout": (
            "Hộp quà hand-drawn pink (#f0abfc) mở nắp, ribbon amber bay lên. "
            "Bên trong hiện 2 cards bay ra: card 1 '🤖 CÁCH DÙNG TOOL', card 2 '⚡ PROMPT + QUY TRÌNH'. "
            "Cả 2 đều có pill 'FREE' lime."
        ),
        "decor": "Confetti nhỏ, tag '👇 Lưu video · Comment AI 👇'.",
    },
    "lock-open": {
        "title": "MỞ KHÓA · OPEN ACCESS",
        "subtitle": "Free, public, MIT license.",
        "layout": (
            "Ổ khóa hand-drawn lớn slate, đang mở, chìa khóa cyan (#67e8f9) nằm bên cạnh. "
            "Phía sau là book + code stack."
        ),
        "decor": "Tag 'Open weight', 'MIT', 'Chạy local cũng được'.",
    },
    "light-bulb-off-on": {
        "title": "TẮT ↔ BẬT · INSIGHT MOMENT",
        "subtitle": "Khi giao việc thay vì hỏi đáp.",
        "layout": (
            "LEFT: bóng đèn hand-drawn slate tắt. RIGHT: bóng đèn warm amber sáng tỏa hào quang. "
            "Cùng 1 bóng đèn, 2 trạng thái side-by-side."
        ),
        "decor": "Tag 'Đổi tư duy', 'Cùng tool — khác cách dùng'.",
    },
    "sleeping-vs-working": {
        "title": "BẠN NGỦ · AI LÀM",
        "subtitle": "Sáng dậy là có output.",
        "layout": (
            "LEFT: silhouette người ngủ trên giường, ZZZ doodle phía trên. "
            "RIGHT: laptop sáng đang chạy, thanh progress amber, output hiện trên màn hình. "
            "Mặt trăng phía trên, sun rise nhẹ hơn nữa phía bên phải."
        ),
        "decor": "Tag '8h tự chạy', 'Bản nháp + email + báo cáo'.",
    },
    "paper-stack-100": {
        "title": "100 TRANG · MỘT LẦN ĐỌC",
        "subtitle": "Không cần chia nhỏ.",
        "layout": (
            "Stack tài liệu hand-drawn cao 100 trang, label '100 TRANG' bên cạnh. "
            "Mũi tên cyan (#67e8f9) trỏ từ stack vào orb Claude violet. "
            "Bên phải orb: 1 file 'TÓM TẮT' lime."
        ),
        "decor": "Tag 'Đọc 1 lần', 'Nhớ tất cả', 'Không cần chunk'.",
    },
    "network-graph": {
        "title": "MẠNG LƯỚI · CONTEXT KẾT NỐI",
        "subtitle": "Mọi thứ liên kết với nhau.",
        "layout": (
            "Network graph hand-drawn với 8 nodes, mỗi node 1 icon (📝 📧 📊 📦 🤖 💬 📅 ✅). "
            "Lines kết nối tất cả. Center node là Claude orb violet."
        ),
        "decor": "Tag 'Hệ thống · không phải tool đơn'.",
    },
    "tree-grow": {
        "title": "TỪ HẠT GIỐNG · ĐẾN CẢ HỆ",
        "subtitle": "Bắt đầu từ 1 prompt nhỏ.",
        "layout": (
            "Cây hand-drawn lá lime, gốc to, nhánh chia ra 5 hướng — mỗi nhánh 1 output (📝 📊 📧 📦 ✅). "
            "Hạt giống dưới đất, label '1 PROMPT'."
        ),
        "decor": "Tag 'Compound effect', '30 ngày · cả workflow'.",
    },
    "key-fits-lock": {
        "title": "KHỚP CHÌA · ĐÚNG WORKFLOW",
        "subtitle": "Không phải mọi tool đều đúng.",
        "layout": (
            "Chìa khóa cyan hình dạng đặc biệt hand-drawn, đang vừa khít vào ổ khóa pink. "
            "Bên trái 3 chìa khác (rose, slate, amber) bị gạch chéo — không vừa."
        ),
        "decor": "Tag 'Pick the right tool', 'Claude cho task dài'.",
    },
    "mountain-summit": {
        "title": "ĐỈNH NÚI · 30 NGÀY",
        "subtitle": "Trekking từng bước.",
        "layout": (
            "Núi hand-drawn 3 đỉnh tăng dần, người silhouette đang ở đỉnh cao nhất, lá cờ amber. "
            "Đường mòn ziczac từ chân lên với 5 pin ghim đánh dấu milestone."
        ),
        "decor": "Tag 'Ngày 1 → ngày 30', 'Cumulative learning'.",
    },
}


# Default split-labor messages per archetype.
# HTML carries DATA/SPECS, image carries METAPHOR/EMOTION.
DEFAULT_LAYER_MESSAGES = {
    "hook":     ("DATA — tier-letters trước/sau + items list + brand logo Claude",
                 "EMOTION — đồng hồ cát đầy↔vơi: thời gian từng cạn → giờ tự chạy"),
    "problem":  ("DATA — fail rows ChatGPT/Gemini + 'đứt mạch' stamp + logos",
                 "EMOTION — sợi xích kim loại nứt vỡ: cảm giác mất context"),
    "fail":     ("DATA — fail rows + ZAP indicator",
                 "EMOTION — bánh răng kẹt: workflow đứng im"),
    "pivot":    ("DATA — before/after columns",
                 "EMOTION — ngã ba đường: moment quyết định đổi cách làm"),
    "solution": ("DATA — 3 specs Claude (∞ memory · 100tr · 8h) + Claude logo trong orb",
                 "EMOTION — robot orb glow tỏa task: AI bấm máy thay mình"),
    "differentiator": ("DATA — comparison table feature×feature",
                       "EMOTION — cán cân nghiêng: lựa chọn rõ ràng"),
    "proof":    ("DATA — headline number + supporting metrics",
                 "EMOTION — chồng tài liệu được consumed 1 lần: scale tangible"),
    "result":   ("DATA — counter row 40h→25h + +2 khách",
                 "EMOTION — heo đất vỡ vs két sắt: tiền tiết kiệm thật"),
    "recap":    ("DATA — counter row 40h→25h + +2 khách",
                 "EMOTION — heo đất vỡ vs két sắt: tiền tiết kiệm thật"),
    "cta":      ("DATA — comment keyword + gift cards + Claude branding",
                 "EMOTION — hộp quà mở: lead-magnet reveal moment"),
}


def build_broll_for_metaphor(metaphor: str, visual_type: str, scene_num: int, brand: str, kind: str = "hook") -> dict:
    """Render a default broll[] entry given a metaphor name + visual_type + scene archetype."""
    spec = METAPHOR_LAYOUTS.get(metaphor)
    html_msg, image_msg = DEFAULT_LAYER_MESSAGES.get(kind, DEFAULT_LAYER_MESSAGES["hook"])
    if spec is None:
        # Custom / unknown metaphor — fail safe: produce a placeholder that
        # the validator will flag if user doesn't fix.
        return {
            "kind": "infographic-cream-paper",
            "visual_type": visual_type,
            "metaphor": "custom",
            "title_vi": "TODO: title",
            "subtitle_vi": "TODO: subtitle",
            "palette_accents": ["claude-orange", "cyan"],
            "layout_description": "TODO: describe layout block-by-block with metaphor.",
            "decorative_elements": "",
            "prompt_path": f"prompts.md#{scene_num}",
            "placeholder_filename": f"{scene_num}.png",
            "aspect": "16:10",
            "notes": "Metaphor 'custom' — please specify a real metaphor from visual-thinking-library.md",
            "html_layer_message": html_msg,
            "image_layer_message": image_msg,
            "composition_strategy": "pip-swap",
        }
    palette_by_brand = {
        "claude":   ["claude-orange", "amber", "lime"],
        "deepseek": ["deepseek-blue", "amber", "lime"],
        "openai":   ["green", "amber", "slate"],
        "gemini":   ["cyan", "amber", "lime"],
        "generic":  ["amber", "lime", "cyan"],
    }
    return {
        "kind": "infographic-cream-paper",
        "visual_type": visual_type,
        "metaphor": metaphor,
        "title_vi": spec["title"],
        "subtitle_vi": spec["subtitle"],
        "palette_accents": palette_by_brand.get(brand, palette_by_brand["claude"]),
        "layout_description": spec["layout"],
        "decorative_elements": spec.get("decor", ""),
        "prompt_path": f"prompts.md#{scene_num}",
        "placeholder_filename": f"{scene_num}.png",
        "aspect": "16:10",
        "notes": "",
        "html_layer_message": html_msg,
        "image_layer_message": image_msg,
        "composition_strategy": "pip-swap",
    }


# ---------- density detection (inserts / bursts / flashes) ----------
#
# Auto-suggest mid-scene cutaways, enumeration bursts, and number flashes by
# scanning the transcript words within each scene's [start, end) window.
# Targets Modern TikTok density: ~3-5 visual events per 10s.
#
# Hand-edits by LLM downstream are expected — these defaults are starting
# points, not finals. Patterns chosen conservatively so detection does not
# fire on noise (single number → flash; quantity + currency → stronger flash;
# 3+ proper-noun chain → burst).

# Brand keywords we recognize as logo-strip candidates inside burst items.
BRAND_KEYWORDS = {
    "chatgpt", "claude", "gemini", "perplexity", "grok", "midjourney",
    "deepseek", "qwen", "llama", "mistral", "anthropic", "openai", "google",
    "lovable", "cursor", "windsurf", "replit", "notion", "figma",
    "youtube", "tiktok", "facebook", "instagram", "linkedin", "twitter",
    "x.com", "reddit", "telegram", "zalo", "shopee", "tiki", "lazada",
    "vercel", "supabase", "n8n", "make.com", "zapier", "airtable",
}

# Action verbs that suggest a macro-shot cutaway is meaningful here.
ACTION_VERBS_VI = {
    "gõ", "click", "kéo", "mở", "đóng", "lưu", "tải", "tải xuống",
    "copy", "paste", "ghi", "viết", "vẽ", "chụp", "quay",
    "ấn", "bấm", "bật", "tắt", "chỉnh", "sửa", "xóa", "thêm",
    "nhập", "chọn", "swipe", "vuốt", "scroll", "lăn", "cuộn",
}

# Comparison cue words → before-after-wipe insert.
COMPARISON_CUES_VI = [
    "trước đây", "ngày trước", "ngày xưa", "trước kia",
    "bây giờ", "giờ thì", "hôm nay", "giờ đây",
    "thay vì", "thay vì là", "không còn",
    "so với", "khác với", "khác hẳn",
    "before", "after", "vs",
]

# Number-burst flash regex — captures quantity tokens with optional unit.
RE_NUMBER_WITH_UNIT = re.compile(
    r"\b(\d{1,4}(?:[.,]\d+)?)\s*"
    r"(%|tr|triệu|tỉ|tỷ|k|nghìn|đ|vnd|h|giờ|phút|s|ngày|tuần|tháng|năm|x|×|lần|người|trang)?\b",
    re.IGNORECASE,
)

# Strong number (must be flashed) — quantity + meaningful unit/percentage.
def _is_strong_number(value: str, unit: str | None) -> bool:
    if not unit:
        # Plain large number — flash if ≥ 100.
        try:
            return float(value.replace(",", ".")) >= 100
        except ValueError:
            return False
    unit_l = unit.lower()
    return unit_l in {
        "%", "tr", "triệu", "tỉ", "tỷ", "k", "nghìn", "đ", "vnd",
        "h", "giờ", "phút", "s", "ngày", "tuần", "tháng", "năm",
        "x", "×", "lần",
    }


def _fmt_flash_value(value: str, unit: str | None) -> str:
    """Compact display string for a number flash: '+300%', '8h', '10tr'."""
    val = value.replace(",", ".")
    # Strip trailing .0
    try:
        f = float(val)
        if f.is_integer():
            val = str(int(f))
    except ValueError:
        pass
    if not unit:
        return val
    u = unit.lower()
    short_map = {
        "triệu": "tr", "tỷ": "tỉ", "nghìn": "k", "vnd": "đ",
        "giờ": "h", "phút": "p", "ngày": "ng", "tuần": "tu",
        "tháng": "th", "năm": "y", "lần": "×",
    }
    u_short = short_map.get(u, u)
    return f"{val}{u_short}"[:12]


def _words_in_window(words: list[dict], start: float, end: float) -> list[dict]:
    return [w for w in words if w.get("start", 0) >= start and w.get("end", 0) <= end]


def _phrase_around(words: list[dict], idx: int, span: int = 5) -> str:
    lo = max(0, idx - span)
    hi = min(len(words), idx + span + 1)
    return re.sub(r"\s+", " ", " ".join(str(w.get("text", "")).strip() for w in words[lo:hi])).strip()


def detect_flashes(words: list[dict], start: float, end: float) -> list[dict]:
    """Return list of flash_clip dicts for numbers/quantities in window."""
    flashes: list[dict] = []
    in_win = _words_in_window(words, start, end)
    for i, w in enumerate(in_win):
        text = str(w.get("text", "")).strip()
        # Combine with next word for cases where unit is detached ("300", "%").
        next_text = str(in_win[i + 1].get("text", "")).strip() if i + 1 < len(in_win) else ""
        combo = f"{text} {next_text}".strip()
        m = RE_NUMBER_WITH_UNIT.search(combo)
        if not m:
            m = RE_NUMBER_WITH_UNIT.search(text)
            if not m:
                continue
        value, unit = m.group(1), m.group(2)
        if not _is_strong_number(value, unit):
            continue
        # Center the flash on the WORD that carries the unit (or the number if no unit).
        t = float(w.get("start", 0))
        # Avoid duplicates within 0.7s
        if flashes and abs(flashes[-1]["t"] - t) < 0.7:
            continue
        flashes.append({
            "t": round(t, 2),
            "duration": 0.9,
            "value": _fmt_flash_value(value, unit),
            "style": "number-burst",
            "trigger": _phrase_around(in_win, i, 3),
            "color": "amber",
        })
    return flashes


def detect_bursts(words: list[dict], start: float, end: float) -> list[dict]:
    """Return burst_clip dicts when transcript has 3+ proper-noun chain (brand list)
    or enumeration markers ('thứ nhất', 'thứ hai', ...)."""
    bursts: list[dict] = []
    in_win = _words_in_window(words, start, end)
    if not in_win:
        return bursts

    # Build a token list with lowercase text and start times.
    toks = [(str(w.get("text", "")).strip(), float(w.get("start", 0))) for w in in_win]

    # --- Brand-chain detection ---
    i = 0
    while i < len(toks):
        text, t = toks[i]
        if text.lower().strip(".,!?:;") in BRAND_KEYWORDS:
            chain = [(text, t)]
            j = i + 1
            # Walk forward up to 8 tokens; collect any more brand mentions if
            # they sit within 2 seconds of the last one.
            while j < len(toks) and j - i < 8:
                tt, tts = toks[j]
                if tt.lower().strip(".,!?:;") in BRAND_KEYWORDS and tts - chain[-1][1] < 2.5:
                    chain.append((tt, tts))
                j += 1
            if len(chain) >= 3:
                items = [
                    {
                        "asset": f"brand-{name.lower().strip('.,!?:;')}.png",
                        "duration": 0.5,
                        "label": name.strip(".,!?:;").title(),
                    }
                    for name, _ in chain[:5]
                ]
                bursts.append({
                    "t_start": round(chain[0][1], 2),
                    "items": items,
                    "trigger": ", ".join(n for n, _ in chain),
                    "style": "logo-strip",
                    "transition": "cut",
                })
                i = j
                continue
        i += 1

    # --- Enumeration markers ('thứ nhất, thứ hai, thứ ba') ---
    full = " ".join(t for t, _ in toks).lower()
    enum_markers = ["thứ nhất", "thứ hai", "thứ ba", "thứ tư", "thứ năm"]
    hits = [m for m in enum_markers if m in full]
    if len(hits) >= 3 and not bursts:
        # Find timestamp of "thứ nhất"
        for k in range(len(toks) - 1):
            two_word = f"{toks[k][0]} {toks[k+1][0]}".lower()
            if two_word == "thứ nhất":
                t0 = toks[k][1]
                items = [
                    {"asset": f"enum-{n+1}.png", "duration": 0.55, "label": f"#{n+1}"}
                    for n in range(min(len(hits), 5))
                ]
                bursts.append({
                    "t_start": round(t0, 2),
                    "items": items,
                    "trigger": " · ".join(hits),
                    "style": "card-stack",
                    "transition": "fade",
                })
                break
    return bursts


def detect_inserts(words: list[dict], start: float, end: float, scene_num: int) -> list[dict]:
    """Return insert_clip dicts for action verbs and comparison cues in window."""
    inserts: list[dict] = []
    in_win = _words_in_window(words, start, end)
    if not in_win:
        return inserts

    full = " ".join(str(w.get("text", "")).strip() for w in in_win).lower()
    n_inserts_per_scene = 0
    MAX_INSERTS_PER_SCENE = 2  # Hard cap so density stays usable.

    # --- Comparison cue → before-after-wipe ---
    for cue in COMPARISON_CUES_VI:
        if cue in full:
            # Find approximate timestamp of cue
            for i in range(len(in_win)):
                phrase = " ".join(
                    str(in_win[j].get("text", "")).strip().lower()
                    for j in range(i, min(i + 3, len(in_win)))
                )
                if phrase.startswith(cue):
                    t = float(in_win[i].get("start", 0))
                    if any(abs(ins["t"] - t) < 1.0 for ins in inserts):
                        break
                    inserts.append({
                        "t": round(t, 2),
                        "duration": 1.8,
                        "kind": "before-after-wipe",
                        "asset": f"insert-s{scene_num}-{len(inserts)+1}.png",
                        "reason": f"Cue '{cue}' — before/after wipe",
                        "transition": "fade",
                        "prompt_path": f"prompts.md#scene-{scene_num}-insert-{len(inserts)+1}",
                    })
                    n_inserts_per_scene += 1
                    break
            if n_inserts_per_scene >= MAX_INSERTS_PER_SCENE:
                break

    # --- Action verb → macro-shot ---
    if n_inserts_per_scene < MAX_INSERTS_PER_SCENE:
        for i, w in enumerate(in_win):
            text = str(w.get("text", "")).strip().lower().strip(".,!?:;")
            if text in ACTION_VERBS_VI:
                t = float(w.get("start", 0))
                if any(abs(ins["t"] - t) < 1.5 for ins in inserts):
                    continue
                inserts.append({
                    "t": round(t, 2),
                    "duration": 1.4,
                    "kind": "macro-shot",
                    "asset": f"insert-s{scene_num}-{len(inserts)+1}.png",
                    "reason": f"Action verb '{text}' — macro-shot",
                    "transition": "fade",
                    "prompt_path": f"prompts.md#scene-{scene_num}-insert-{len(inserts)+1}",
                })
                n_inserts_per_scene += 1
                if n_inserts_per_scene >= MAX_INSERTS_PER_SCENE:
                    break
    return inserts


def derive_pip_events(start: float, end: float) -> list[dict]:
    duration = max(0.0, end - start)
    if duration < 3.0:
        return []
    if duration < 12.0:
        t_in = round(start + 1.4, 2)
        t_out = round(min(end - 0.3, t_in + 3.5), 2)
        return [{"t_in": t_in, "t_out": t_out, "reason": "Tier-letter glow", "trigger": "tier-letter-glow"}]
    return [
        {"t_in": round(start + 1.4, 2), "t_out": round(start + 5.4, 2),
         "reason": "First tier-letter glow", "trigger": "tier-letter-glow"},
        {"t_in": round(start + 7.0, 2), "t_out": round(min(end - 0.3, start + 11.5), 2),
         "reason": "Second key-number reveal", "trigger": "key-number-reveal"},
    ]


def voiceover_anchor_from_transcript(words: list[dict], start: float, end: float) -> str:
    """Pick a 4-7 word phrase from middle of scene's transcript window."""
    in_window = [w for w in words if w.get("start", 0) >= start and w.get("end", 0) <= end]
    if not in_window:
        return ""
    mid = len(in_window) // 2
    chunk = in_window[max(0, mid - 3): mid + 4]
    text = " ".join(str(w.get("text", "")).strip() for w in chunk)
    return re.sub(r"\s+", " ", text).strip()


# Map legacy editor variant names → planner variant enum.
LEGACY_VARIANT_REMAP = {
    "post-stack": "tier-row",
    "ai-window": "chats-stack",
    "app-card": "hero-orb",
    "team-grid": "counter-row",
    "comment-box": "terminal-row",
    "tier-row-before-after": "tier-row",
    "hero-orb-spec-trio": "hero-orb",
    "comment-terminal": "terminal-row",
    "stats-3card": "stats-3-card",
    "comparison-2col": "compare-2-col",
    "image-slot": "embedded-infographic",
}


def build_scene_entry(s: dict, words: list[dict], brand: str) -> dict:
    kind = s.get("kind", "hook")
    if kind == "lesson":
        # Legacy editor used kind="lesson" generic; fall back via num.
        positional = {1: "hook", 2: "problem", 3: "solution", 4: "recap", 5: "cta"}
        kind = positional.get(int(s.get("num", 1)), "hook")
    variant = s.get("variant") or s.get("mockup_variant") or "tier-row"
    variant = LEGACY_VARIANT_REMAP.get(variant, variant)
    num = int(s.get("num", 1))
    start = float(s.get("start", 0))
    end = float(s.get("end", 0))

    metaphor = DEFAULT_METAPHOR.get(kind, "robot-orb-with-tasks")
    visual_type = DEFAULT_VISUAL_TYPE.get(kind, "three-pillar")
    tier_letter = DEFAULT_TIER_LETTER.get(kind, "AI")
    badges = DEFAULT_BADGES.get(kind, [])
    items = DEFAULT_ITEMS.get(kind, [])

    accent_words: list[str] = []
    heading = s.get("heading", "")
    if heading:
        nums = re.findall(r"\d+\s*[a-zA-ZÀ-ỹ%]*", heading)
        accent_words = nums[:2] or [heading.split()[-1]] if heading.split() else []

    return {
        "id": f"scene-{num}",
        "num": num,
        "kind": kind,
        "variant": variant,
        "start": round(start, 2),
        "end": round(end, 2),
        "kicker": s.get("kicker", ""),
        "heading": heading,
        "accent_words": accent_words,
        "voiceover_anchor": voiceover_anchor_from_transcript(words, start, end),
        "tier_letter": tier_letter,
        "items": items,
        "badges": badges,
        "broll": [build_broll_for_metaphor(metaphor, visual_type, num, brand, kind)],
        "pip_events": derive_pip_events(start, end),
        "sfx_overrides": [],
        "inserts": detect_inserts(words, start, end, num),
        "bursts":  detect_bursts(words, start, end),
        "flashes": detect_flashes(words, start, end),
    }


# ---------- validation ----------

def validate_plan(plan: dict) -> list[str]:
    """Return list of validation error strings (empty = OK)."""
    errors: list[str] = []

    try:
        import jsonschema  # type: ignore
        schema = json.loads(SCHEMA_PATH.read_text())
        validator = jsonschema.Draft202012Validator(schema)
        for err in validator.iter_errors(plan):
            errors.append(f"schema: {'/'.join(str(p) for p in err.absolute_path)} — {err.message}")
    except ImportError:
        # No jsonschema installed — fall back to manual checks for the
        # important invariants (still useful even without the lib).
        for s in plan.get("scenes", []):
            for k in ["id", "num", "kind", "variant", "start", "end", "tier_letter", "broll", "pip_events"]:
                if k not in s:
                    errors.append(f"scene {s.get('num', '?')}: missing '{k}'")

    # Hard guardrail: every infographic-cream-paper b-roll MUST carry a
    # `visual_type` (slide structure) AND a `metaphor` (illustration). A pure
    # structural diagram with no metaphor is OK only if metaphor is the
    # explicit literal "none" — anything else means the planner forgot to fill.
    valid_visual_types = {
        "before-after", "mind-map", "flowchart", "matrix-2x2", "venn",
        "timeline", "pyramid", "comparison-table", "iceberg", "cycle",
        "funnel", "concept-map", "icon-grid", "number-infographic", "three-pillar",
    }
    for s in plan.get("scenes", []):
        for b in s.get("broll", []) or []:
            if b.get("kind") == "infographic-cream-paper":
                vt = (b.get("visual_type") or "").strip().lower()
                if vt not in valid_visual_types:
                    errors.append(
                        f"scene {s.get('num')}: infographic-cream-paper b-roll has invalid visual_type "
                        f"'{vt}' — pick one of 15 from visual-thinking-types.md."
                    )
                m = (b.get("metaphor") or "").strip().lower()
                if not m or m in {"null", "text-only", "text"}:
                    errors.append(
                        f"scene {s.get('num')}: infographic-cream-paper b-roll has no metaphor — "
                        "text-only slides are forbidden. Pick from visual-thinking-library.md "
                        "or set metaphor='none' for pure structural diagrams."
                    )
    # Tier-letter cap.
    for s in plan.get("scenes", []):
        tl = s.get("tier_letter", "")
        if isinstance(tl, str) and len(tl) > 5:
            errors.append(f"scene {s.get('num')}: tier_letter '{tl}' exceeds 5 chars.")

    # PIP overlap.
    for s in plan.get("scenes", []):
        evs = sorted(s.get("pip_events", []) or [], key=lambda e: e.get("t_in", 0))
        for i in range(1, len(evs)):
            if evs[i]["t_in"] < evs[i - 1]["t_out"] + 0.3:
                errors.append(f"scene {s.get('num')}: pip_events overlap at index {i} (need ≥0.3s gap).")

    # Density layer bounds: every insert/burst/flash must sit inside its scene window.
    for s in plan.get("scenes", []):
        sn = s.get("num", "?")
        s_start, s_end = float(s.get("start", 0)), float(s.get("end", 0))
        for ins in s.get("inserts", []) or []:
            t, d = float(ins.get("t", 0)), float(ins.get("duration", 0))
            if t < s_start - 0.1 or t + d > s_end + 0.1:
                errors.append(
                    f"scene {sn}: insert at t={t} duration={d} falls outside scene window [{s_start}, {s_end}]."
                )
        for b in s.get("bursts", []) or []:
            t0 = float(b.get("t_start", 0))
            total = sum(float(i.get("duration", 0)) for i in b.get("items", []))
            if t0 < s_start - 0.1 or t0 + total > s_end + 0.1:
                errors.append(
                    f"scene {sn}: burst at t_start={t0} total={total:.2f}s falls outside scene window."
                )
        for f in s.get("flashes", []) or []:
            t, d = float(f.get("t", 0)), float(f.get("duration", 0))
            if t < s_start - 0.1 or t + d > s_end + 0.1:
                errors.append(
                    f"scene {sn}: flash at t={t} duration={d} falls outside scene window."
                )

    return errors


# ---------- main ----------

def build_plan(workspace: Path, brand: str) -> dict:
    outline = load_or_build_outline(workspace)
    words = load_transcript(workspace)
    total_duration = float(words[-1]["end"]) if words else float(outline[-1].get("end", 0))

    scenes = [build_scene_entry(s, words, brand) for s in outline]

    return {
        "workspace_slug": workspace.name,
        "total_duration": round(total_duration, 2),
        "brand": brand,
        "schema_version": "1.1",
        "scenes": scenes,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", "-w", default=".", help="Workspace folder")
    ap.add_argument("--llm-mode", choices=["native", "claude-api"], default="native")
    ap.add_argument("--brand", default="claude",
                    choices=["claude", "deepseek", "openai", "gemini", "generic"])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    workspace = Path(args.workspace).resolve()
    if not workspace.exists():
        print(f"[plan] ERROR: workspace {workspace} does not exist.", file=sys.stderr)
        sys.exit(1)

    if args.llm_mode == "claude-api":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("[plan] WARN: --llm-mode claude-api but ANTHROPIC_API_KEY missing. Falling back to native.", file=sys.stderr)

    plan = build_plan(workspace, args.brand)

    errors = validate_plan(plan)
    if errors:
        print("[plan] VALIDATION ERRORS:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        # In scaffold mode default content is internally consistent, so this
        # should not trip — but if it does, surface it loudly.
        sys.exit(1)

    if args.dry_run:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return

    out_path = workspace / "visual-plan.json"
    out_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2))
    print(f"[plan] visual-plan.json — {len(plan['scenes'])} scenes, total {plan['total_duration']}s")
    print(f"[plan] next: render_infographic_prompts.py --workspace {workspace}")


if __name__ == "__main__":
    main()
