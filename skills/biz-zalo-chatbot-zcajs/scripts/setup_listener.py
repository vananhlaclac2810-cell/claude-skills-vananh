#!/usr/bin/env python3
"""
setup_listener.py — Python helper chạy 1 lần để scaffold zalo-listener.

Usage:
    python setup_listener.py [TARGET_DIR]

Default target dir: ./zalo-listener (current working directory)

Steps:
    1. Copy templates/zalo-listener/ vào TARGET_DIR
    2. npm install (nếu Node.js + npm available)
    3. Prompt user paste cookies + imei + userAgent + openrouter key
    4. Generate .env file với các giá trị paste
    5. Print next steps cho user
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import secrets
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATE_DIR = SKILL_DIR / "templates" / "zalo-listener"


def ask(prompt: str, default: str = "", multiline: bool = False) -> str:
    """Prompt user. Return stripped string (or default if blank)."""
    if multiline:
        print(prompt)
        print("(Paste xong rồi gõ EOF ở dòng riêng để kết thúc)")
        lines = []
        for line in sys.stdin:
            if line.strip() == "EOF":
                break
            lines.append(line.rstrip("\n"))
        result = "\n".join(lines).strip()
    else:
        result = input(prompt).strip()
    return result or default


def copy_template(target: Path) -> None:
    """Copy templates/zalo-listener/ vào target dir."""
    if target.exists():
        choice = ask(
            f"⚠️ Folder {target} đã tồn tại. Overwrite? (y/N): ", default="n"
        )
        if choice.lower() != "y":
            print("Aborted.")
            sys.exit(1)
        shutil.rmtree(target)

    print(f"[1/5] Copy template vào {target}...")
    shutil.copytree(TEMPLATE_DIR, target)
    print(f"  ✓ Copied")


def run_npm_install(target: Path) -> None:
    """Run npm install nếu npm available."""
    print("[2/5] Running npm install...")
    try:
        subprocess.run(
            ["npm", "install"],
            cwd=target,
            check=True,
            shell=(os.name == "nt"),  # Windows cần shell=True cho npm
        )
        print("  ✓ npm install xong")
    except FileNotFoundError:
        print("  ⚠️ npm không tìm thấy. Anh/chị cài Node.js trước: https://nodejs.org")
        print(f"     Sau đó chạy: cd {target} && npm install")
    except subprocess.CalledProcessError as err:
        print(f"  ⚠️ npm install fail: {err}")
        print(f"     Chạy lại thủ công: cd {target} && npm install")


def prompt_credentials() -> dict[str, str]:
    """Prompt user nhập credentials."""
    print()
    print("[3/5] Cần các thông tin sau (xem references/zalo-account-setup.md):")
    print()

    cookies = ask(
        "▸ ZALO_COOKIES_JSON (paste JSON array, 1 dòng):\n  ",
        multiline=False,
    )
    imei = ask(
        "▸ ZALO_IMEI (từ localStorage.getItem('z_uuid')):\n  ",
    )
    user_agent = ask(
        "▸ ZALO_USER_AGENT (từ navigator.userAgent):\n  ",
    )
    openrouter_key = ask(
        "▸ OPENROUTER_API_KEY (sk-or-v1-...):\n  ",
    )
    brand_name = ask(
        "▸ BRAND_NAME (mặc định 'Dr.Maya'): ",
        default="Dr.Maya",
    )
    notify_recipients = ask(
        "▸ ZALO_NOTIFY_RECIPIENTS (CSV user_id owner, có thể để trống điền sau): ",
        default="",
    )

    # Auto-generate API key cho /send endpoint
    send_api_key = secrets.token_hex(24)
    print(f"  → Đã tự generate ZALO_SEND_API_KEY: {send_api_key}")
    print("    (Lưu key này để paste vào Vercel .env cùng giá trị)")

    return {
        "ZALO_COOKIES_JSON": cookies,
        "ZALO_IMEI": imei,
        "ZALO_USER_AGENT": user_agent,
        "OPENROUTER_API_KEY": openrouter_key,
        "OPENROUTER_MODEL": "google/gemini-3-flash-preview",
        "BRAND_NAME": brand_name,
        "BRAND_SITE_URL": "",
        "BOT_TONE": "than_thien_anh_chi",
        "ZALO_SEND_API_KEY": send_api_key,
        "SEND_PORT": "3001",
        "ZALO_NOTIFY_RECIPIENTS": notify_recipients,
    }


def write_env(target: Path, creds: dict[str, str]) -> None:
    """Write .env file."""
    print(f"[4/5] Write .env vào {target}...")
    env_path = target / ".env"
    lines = []
    for key, value in creds.items():
        # Escape value: nếu chứa space hoặc special chars, wrap quotes
        if " " in value or "{" in value or "[" in value:
            # Single-quote, escape internal single quotes
            escaped = value.replace("'", "'\\''")
            lines.append(f"{key}='{escaped}'")
        else:
            lines.append(f"{key}={value}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  ✓ {env_path}")
    print("  ⚠️ .env đã được .gitignore — KHÔNG commit lên Git")


def print_next_steps(target: Path) -> None:
    """Print hướng dẫn cuối."""
    print()
    print("[5/5] DONE. Anh/chị làm tiếp:")
    print()
    print(f"  cd {target}")
    print()
    print("  # 1. Test login (verify cookies/imei/userAgent đúng)")
    print("  npm run test:login")
    print()
    print("  # 2. Edit knowledge base — paste FAQ + product info vào")
    print("  notepad zalo-knowledge/example.md  # Windows")
    print("  # hoặc tạo file mới: zalo-knowledge/faq.md, product.md, ...")
    print()
    print("  # 3. Test LLM với knowledge")
    print("  npm run test:llm")
    print()
    print("  # 4. Start listener local")
    print("  npm start")
    print()
    print("  # 5. (Sau khi test OK) Deploy lên Railway:")
    print("  # Xem references/deployment-railway.md")
    print()


def main() -> int:
    if not TEMPLATE_DIR.exists():
        print(f"[fatal] Template dir not found: {TEMPLATE_DIR}")
        return 1

    target_arg = sys.argv[1] if len(sys.argv) > 1 else "./zalo-listener"
    target = Path(target_arg).resolve()

    print("=" * 60)
    print("biz-zalo-chatbot-zcajs — Listener Setup")
    print("=" * 60)
    print()
    print(f"Target dir: {target}")
    print()
    print("⚠️ CẢNH BÁO: zca-js là unofficial library. Account Zalo có nguy cơ")
    print("   bị khóa. Đọc references/zca-js-risks.md trước khi production.")
    print()
    confirm = ask("Tiếp tục? (Y/n): ", default="y")
    if confirm.lower() not in ("y", "yes", ""):
        print("Aborted.")
        return 0

    copy_template(target)
    run_npm_install(target)
    creds = prompt_credentials()
    write_env(target, creds)
    print_next_steps(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
