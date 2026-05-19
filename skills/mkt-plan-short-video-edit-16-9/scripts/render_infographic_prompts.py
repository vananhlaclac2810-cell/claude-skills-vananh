#!/usr/bin/env python3
"""Render prompts.md from visual-plan.json.

Reads each scene's broll[] entries with kind == "infographic-cream-paper",
renders a cream-paper editorial prompt via Jinja2 template, writes them
numbered (1.png, 2.png, …) into <workspace>/prompts.md.

Usage:
    python3 render_infographic_prompts.py --workspace <dir>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("[render] jinja2 missing — pip install jinja2", file=sys.stderr)
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR.parent / "assets" / "templates"


HEADER = """# Image prompts — visual-plan b-roll

Cinematic 3D + holographic UI style — Transform Group / Anthropic key-visual aesthetic. Dark navy / space-blue environments with floating holographic glass panels, neon edge-glow, glowing connector beams, numbered annotations, depth-of-field bokeh, volumetric haze. NOT flat infographic, NOT hand-drawn — photoreal 3D scene with composited UI overlays.

**How to use:** copy each prompt below, paste into AI33 / Nano Banana Pro / Midjourney. Save returned image into this same folder with the matching filename (`1.png`, `2.png`, …). HyperFrames editor's `<img onerror>` fallback will auto-render once present.

**Footer:** every image ends with `@tranvanhoang.com` in uppercase letterspaced light-grey type at bottom-center (film credit feel).

**Aspect:** 16:10 by default (AI33 uses `16:9` ≈ 1344×768 since it doesn't support 16:10 natively).
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", "-w", default=".", help="Workspace folder")
    args = ap.parse_args()

    workspace = Path(args.workspace).resolve()
    plan_path = workspace / "visual-plan.json"
    if not plan_path.exists():
        print(f"[render] ERROR: {plan_path} not found. Run plan_visuals.py first.", file=sys.stderr)
        sys.exit(1)

    plan = json.loads(plan_path.read_text())

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tpl = env.get_template("infographic-prompt.j2")

    out_lines: list[str] = [HEADER]
    count = 0
    brand = plan.get("brand", "claude")
    brand_label_map = {
        "claude":   "CLAUDE, ANTHROPIC",
        "deepseek": "DEEPSEEK, MIT",
        "openai":   "OPENAI, GPT, CHATGPT",
        "gemini":   "GEMINI, GOOGLE",
        "generic":  "AI",
    }
    brand_list = brand_label_map.get(brand, "CLAUDE, ANTHROPIC")

    for scene in plan.get("scenes", []):
        for b in scene.get("broll", []) or []:
            if b.get("kind") != "infographic-cream-paper":
                continue
            count += 1
            fname = b.get("placeholder_filename", f"{count}.png")
            out_lines.append(f"\n---\n\n## {fname} — {b.get('title_vi', 'TODO')}\n")
            out_lines.append(
                f"[Aspect: {b.get('aspect', '16:10')} · Provider gợi ý: AI33 / Nano Banana Pro · "
                f"Visual type: `{b.get('visual_type', 'three-pillar')}` · Metaphor: `{b.get('metaphor', 'custom')}` · "
                f"Scene: {scene.get('num')} ({scene.get('kind')})]\n"
            )
            prompt = tpl.render(
                visual_type=b.get("visual_type", "three-pillar"),
                title_vi=b.get("title_vi", ""),
                subtitle_vi=b.get("subtitle_vi", ""),
                brand_list=brand_list,
                tech_or_symbols="currency/math symbols ($, %, ×, ₫, →)",
                layout_description=b.get("layout_description", ""),
                decorative_elements=b.get("decorative_elements", ""),
                palette_accents=b.get("palette_accents", ["claude-orange", "amber"]),
                metaphor_name=b.get("metaphor", "custom"),
                aspect=b.get("aspect", "16:10"),
            )
            out_lines.append(prompt)

    if count == 0:
        out_lines.append("\n_(No infographic-cream-paper b-roll entries in visual-plan.json. Nothing to render.)_\n")

    # ---------- density layer prompts (inserts / bursts / flashes) ----------
    # Density assets ride on top of the scene b-roll; they're short cutaways.
    # Prompt style: SAME cream-paper editorial vibe so it composites cleanly,
    # but ZOOMED IN — a single object, a single number, a single icon row.
    density_count = render_density_prompts(plan, out_lines)

    out_path = workspace / "prompts.md"
    out_path.write_text("\n".join(out_lines))
    print(f"[render] prompts.md — {count} main + {density_count} density prompts written to {out_path}")


# ---------- density renderer ----------

def render_density_prompts(plan: dict, out_lines: list[str]) -> int:
    """Append prompts for inserts/bursts/flashes. Returns count emitted."""
    total = 0
    # Group everything by scene so prompts stay grouped in the file.
    has_any = any(
        scene.get("inserts") or scene.get("bursts") or scene.get("flashes")
        for scene in plan.get("scenes", [])
    )
    if not has_any:
        return 0

    out_lines.append("\n---\n\n# Density layer — inserts · bursts · flashes\n")
    out_lines.append(
        "_Short cutaways stacked on top of the main scene b-roll. Style: cream-paper editorial, "
        "ZOOMED IN to single object / single number / single icon row. Aspect 1:1 (square) unless noted. "
        "Same font + palette as main prompts above._\n"
    )

    for scene in plan.get("scenes", []):
        scene_label = f"scene-{scene.get('num')} ({scene.get('kind')})"
        # ----- inserts -----
        for idx, ins in enumerate(scene.get("inserts", []) or [], start=1):
            total += 1
            out_lines.append(f"\n---\n\n## {ins.get('asset', f'insert-s{scene.get('num')}-{idx}.png')} — INSERT · {ins.get('kind', 'macro-shot')}\n")
            out_lines.append(
                f"[Aspect: 1:1 · Provider: Nano Banana Pro · Duration on screen: {ins.get('duration', 1.4)}s · "
                f"Reason: {ins.get('reason', '')} · {scene_label}]\n"
            )
            out_lines.append(_insert_prompt(ins))

        # ----- bursts -----
        for idx, b in enumerate(scene.get("bursts", []) or [], start=1):
            for k, item in enumerate(b.get("items", []), start=1):
                # Brand logos are usually fetched as official assets; AI prompt
                # only needed for generic icon-strip / card-stack styles.
                if b.get("style") == "logo-strip" and item.get("asset", "").startswith("brand-"):
                    continue
                total += 1
                out_lines.append(f"\n---\n\n## {item.get('asset')} — BURST item {k} · {b.get('style', 'logo-strip')}\n")
                out_lines.append(
                    f"[Aspect: 1:1 · Duration: {item.get('duration', 0.5)}s · "
                    f"Burst trigger: '{b.get('trigger', '')}' · {scene_label}]\n"
                )
                out_lines.append(_burst_item_prompt(item, b))

        # ----- flashes -----
        for idx, f in enumerate(scene.get("flashes", []) or [], start=1):
            # Pure CSS render by default — only emit prompt if `asset` overrides.
            if not f.get("asset"):
                continue
            total += 1
            out_lines.append(f"\n---\n\n## {f.get('asset')} — FLASH · {f.get('style', 'number-burst')}\n")
            out_lines.append(
                f"[Aspect: 1:1 · Duration: {f.get('duration', 0.9)}s · "
                f"Value: '{f.get('value', '')}' · Trigger: '{f.get('trigger', '')}' · {scene_label}]\n"
            )
            out_lines.append(_flash_prompt(f))

    if total == 0:
        out_lines.append(
            "\n_(All density-layer assets are either pure-CSS flashes or use external brand logos — no AI prompts needed.)_\n"
        )

    return total


def _insert_prompt(ins: dict) -> str:
    kind = ins.get("kind", "macro-shot")
    reason = ins.get("reason", "")
    base = (
        "Cream-paper editorial illustration, hand-drawn ink with watercolor accents. "
        "Square 1:1. Single subject centered, generous negative space, soft cream background (#fbf9f3). "
        "NO text overlays except where specified. Subtle paper-grain texture. "
        f"Footer micro-text bottom-center: '@tranvanhoang.com' light-grey letterspaced.\n\n"
    )
    by_kind = {
        "macro-shot": (
            "EXTREME CLOSE-UP of a single hand/finger/object in action — pencil to paper, finger tapping phone screen, "
            f"hand placing object, etc. Specifically: {reason}. "
            "Soft natural light, shallow depth of field, warm color palette."
        ),
        "screen-record": (
            "Floating browser/app window mockup, slight tilt 3°, drop-shadow. Cream-paper bg. "
            f"Specifically: {reason}. UI elements simplified — focus on ONE action."
        ),
        "before-after-wipe": (
            "Two-panel split horizontally. LEFT = 'TRƯỚC' state (faded, slate-grey). RIGHT = 'SAU' state (vivid, amber/lime). "
            f"Specifically: {reason}. Wipe-line in center cream-edge."
        ),
        "reaction-cut": (
            "Quick reaction beat — exclamation mark spike, eye widening, jaw-drop emoji-style icon. "
            f"Specifically: {reason}. High-contrast, single dominant color."
        ),
        "icon-zoom": (
            "Single oversized icon/glyph centered, ink-stamp finish, amber accent. "
            f"Specifically: {reason}. Surrounding cream space."
        ),
        "ai-stock": (
            "Generic editorial illustration in cream-paper style. "
            f"Specifically: {reason}."
        ),
    }
    return base + by_kind.get(kind, by_kind["macro-shot"]) + "\n"


def _burst_item_prompt(item: dict, burst: dict) -> str:
    label = item.get("label", "")
    style = burst.get("style", "logo-strip")
    if style == "card-stack":
        return (
            "Cream-paper editorial card 1:1. Bold numeral or enumeration marker centered "
            f"('{label}'), serif italic 'thứ X' label below. Ink-stamp finish, amber accent border, "
            "soft drop-shadow. Footer '@tranvanhoang.com' bottom-center.\n"
        )
    if style == "icon-strip":
        return (
            f"Cream-paper editorial icon 1:1. Single hand-drawn icon representing '{label}'. "
            "Watercolor wash amber accent, ink outline. Generous negative space. "
            "Footer '@tranvanhoang.com' bottom-center.\n"
        )
    if style == "rapid-cut":
        return (
            f"Cream-paper editorial illustration 1:1 of '{label}'. Single subject centered, "
            "ink-stamp finish, high-contrast, soft natural light. Footer '@tranvanhoang.com' bottom-center.\n"
        )
    # logo-strip fallthrough — should be skipped earlier, but render generic logo card.
    return (
        f"Editorial brand card 1:1. Centered logo wordmark '{label}'. Cream-paper bg, "
        "soft drop-shadow. Footer '@tranvanhoang.com' bottom-center.\n"
    )


def _flash_prompt(flash: dict) -> str:
    style = flash.get("style", "number-burst")
    value = flash.get("value", "")
    color = flash.get("color", "amber")
    if style == "number-burst":
        return (
            f"Cream-paper editorial number-burst 1:1. Giant numeral '{value}' centered, "
            f"display-serif italic, {color} ink, ink-stamp finish with subtle radiating burst lines. "
            "Negative space all around. Footer '@tranvanhoang.com' bottom-center.\n"
        )
    if style == "keyword-stamp":
        return (
            f"Cream-paper rubber-stamp impression 1:1. Bold uppercase keyword '{value}' "
            f"rotated 8° anti-clockwise, {color} ink slightly faded edges, paper-grain visible. "
            "Footer '@tranvanhoang.com' bottom-center.\n"
        )
    if style == "icon-pop":
        return (
            f"Cream-paper single-glyph 1:1. Oversized icon '{value}' centered, {color} watercolor wash, "
            "ink outline, soft drop-shadow. Footer '@tranvanhoang.com' bottom-center.\n"
        )
    if style == "emoji-rain":
        return (
            f"Cream-paper editorial 1:1. 4-5 small emoji-style icons '{value}' scattered diagonally "
            f"top-left to bottom-right, {color} accent ink-stamp. Footer '@tranvanhoang.com' bottom-center.\n"
        )
    return _flash_prompt({**flash, "style": "number-burst"})


if __name__ == "__main__":
    main()
