#!/usr/bin/env python3
"""Shared helper — build HTML/CSS/JS snippet that mounts insert/burst/flash
density layers on top of the talking-head + slide root index.html.

Both editors (`mkt-hyperframe-talking-head-video` 9:16 and
`mkt-hyperframe-talking-head-video-16-9`) call `inject_density_layer()` on the
already-rendered index.html string before writing it to disk. Zero template
changes required.

Public API:

    inject_density_layer(html: str, scenes: list[dict], canvas: str = "16:9") -> str

`scenes` is the per-scene metadata list from scenes.json, each carrying
optional `inserts`, `bursts`, `flashes` arrays (see visual-plan.schema.json).

Injection point: right before `</body>` close tag. If marker not found, the
function returns the input unchanged (safe noop).
"""
from __future__ import annotations

import html as _html


def _css_block(canvas: str) -> str:
    # Per-canvas insert frame sizing.
    if canvas == "9:16":
        insert_w, insert_h = 1080, 1080  # square fills full vertical width
        flash_size = 360
    else:  # 16:9
        insert_w, insert_h = 720, 720
        flash_size = 280

    return f"""
<style>
  /* ---- density layer (inserts · bursts · flashes) ---- */
  .insert-mount {{
    position: absolute !important;
    top: 50%; left: 50%;
    width: {insert_w}px; height: {insert_h}px;
    margin: -{insert_h // 2}px 0 0 -{insert_w // 2}px;
    z-index: 45;
    background: transparent;
    border-radius: 24px;
    overflow: hidden;
    box-shadow: 0 18px 60px rgba(0,0,0,0.45);
    opacity: 0;
    will-change: opacity, transform;
  }}
  .insert-mount img {{
    width: 100%; height: 100%; object-fit: cover; display: block;
  }}
  .insert-mount.kind-before-after-wipe {{
    border-radius: 18px;
  }}
  .insert-mount.kind-screen-record {{
    border-radius: 14px;
    box-shadow: 0 24px 72px rgba(0,0,0,0.55), 0 0 0 2px rgba(255,255,255,0.08);
  }}

  .burst-item {{
    position: absolute !important;
    top: 50%; left: 50%;
    width: {insert_w // 2}px; height: {insert_w // 2}px;
    margin: -{(insert_w // 2) // 2}px 0 0 -{(insert_w // 2) // 2}px;
    z-index: 46;
    border-radius: 24px;
    background: rgba(20,20,19,0.92);
    box-shadow: 0 14px 48px rgba(0,0,0,0.5);
    display: flex; align-items: center; justify-content: center;
    overflow: hidden;
    opacity: 0;
    will-change: opacity, transform;
  }}
  .burst-item img {{
    max-width: 80%; max-height: 70%; object-fit: contain;
  }}
  .burst-item .burst-label {{
    position: absolute; bottom: 28px; left: 0; right: 0;
    text-align: center; color: #faf9f5; font-weight: 700;
    font-family: 'Be Vietnam Pro', 'Inter', Arial, sans-serif;
    font-size: 34px; letter-spacing: 0.02em;
    text-shadow: 0 2px 8px rgba(0,0,0,0.6);
  }}

  .flash-mount {{
    position: absolute !important;
    top: 50%; left: 50%;
    width: {flash_size}px; height: {flash_size}px;
    margin: -{flash_size // 2}px 0 0 -{flash_size // 2}px;
    z-index: 48;
    display: flex; align-items: center; justify-content: center;
    pointer-events: none;
    opacity: 0;
    will-change: opacity, transform;
  }}
  .flash-mount .flash-value {{
    font-family: 'Be Vietnam Pro', 'Inter', Arial, sans-serif;
    font-weight: 900;
    font-size: 152px;
    letter-spacing: -0.02em;
    line-height: 1;
    text-shadow: 0 6px 30px rgba(0,0,0,0.65), 0 0 60px currentColor;
  }}
  .flash-mount.color-amber  .flash-value {{ color: #fbbf24; }}
  .flash-mount.color-lime   .flash-value {{ color: #a3e635; }}
  .flash-mount.color-rose   .flash-value {{ color: #fb7185; }}
  .flash-mount.color-cyan   .flash-value {{ color: #67e8f9; }}
  .flash-mount.color-violet .flash-value {{ color: #a78bfa; }}
  .flash-mount.color-claude-orange .flash-value {{ color: #d97757; }}
  .flash-mount.style-keyword-stamp .flash-value {{
    font-size: 96px; font-style: italic;
    transform: rotate(-6deg);
    border: 6px solid currentColor;
    padding: 14px 32px;
    border-radius: 14px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }}
  .flash-mount.style-icon-pop .flash-value {{ font-size: 240px; }}
</style>
"""


def _html_mounts(scenes: list[dict]) -> str:
    chunks: list[str] = []
    chunks.append("\n<!-- ===== density layer mounts (auto-generated) ===== -->\n")
    for s in scenes:
        scene_num = s.get("num", 0)
        # Inserts
        for i, ins in enumerate(s.get("inserts") or [], start=1):
            t = float(ins.get("t", 0))
            d = float(ins.get("duration", 1.4))
            asset = ins.get("asset", f"insert-s{scene_num}-{i}.png")
            kind = ins.get("kind", "macro-shot")
            ident = f"insert-s{scene_num}-{i}"
            chunks.append(
                f'<div class="clip insert-mount kind-{_html.escape(kind)}" id="{ident}" '
                f'data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="45">'
                f'<img src="{_html.escape(asset)}" alt="{_html.escape(ins.get("reason", ""))[:80]}" onerror="this.style.opacity=0"/>'
                f'</div>\n'
            )
        # Bursts — render each item as its own clip mount, back-to-back.
        for bi, b in enumerate(s.get("bursts") or [], start=1):
            t_cursor = float(b.get("t_start", 0))
            style = b.get("style", "logo-strip")
            for k, item in enumerate(b.get("items", []), start=1):
                d = float(item.get("duration", 0.5))
                asset = item.get("asset", "")
                label = item.get("label", "")
                ident = f"burst-s{scene_num}-{bi}-{k}"
                label_html = (
                    f'<span class="burst-label">{_html.escape(label)}</span>'
                    if label and style in ("logo-strip", "card-stack") else ""
                )
                img_html = (
                    f'<img src="{_html.escape(asset)}" alt="{_html.escape(label)}" onerror="this.style.display=\'none\'"/>'
                    if asset else ""
                )
                chunks.append(
                    f'<div class="clip burst-item style-{_html.escape(style)}" id="{ident}" '
                    f'data-start="{t_cursor:.2f}" data-duration="{d:.2f}" data-track-index="46">'
                    f'{img_html}{label_html}</div>\n'
                )
                t_cursor += d
        # Flashes — pure CSS, no image required.
        for fi, f in enumerate(s.get("flashes") or [], start=1):
            t = float(f.get("t", 0))
            d = float(f.get("duration", 0.9))
            value = str(f.get("value", ""))
            style = f.get("style", "number-burst")
            color = f.get("color", "amber")
            ident = f"flash-s{scene_num}-{fi}"
            chunks.append(
                f'<div class="clip flash-mount style-{_html.escape(style)} color-{_html.escape(color)}" id="{ident}" '
                f'data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="48">'
                f'<span class="flash-value">{_html.escape(value)}</span></div>\n'
            )
    return "".join(chunks)


def _gsap_anims(scenes: list[dict]) -> str:
    """GSAP timeline calls to fade/scale density mounts in and out."""
    lines: list[str] = []
    lines.append("/* density-layer GSAP animations */")
    lines.append("(function(){")
    lines.append("  if (typeof tl === 'undefined' || !tl) return;")

    for s in scenes:
        scene_num = s.get("num", 0)
        for i, ins in enumerate(s.get("inserts") or [], start=1):
            t = float(ins.get("t", 0))
            d = float(ins.get("duration", 1.4))
            ident = f"insert-s{scene_num}-{i}"
            transition = ins.get("transition", "fade")
            if transition == "cut":
                lines.append(f"  tl.set('#{ident}', {{opacity:1}}, {t:.2f});")
                lines.append(f"  tl.set('#{ident}', {{opacity:0}}, {t + d:.2f});")
            elif transition == "whip":
                lines.append(
                    f"  tl.fromTo('#{ident}', {{opacity:0, scale:1.2, x:60}}, "
                    f"{{opacity:1, scale:1, x:0, duration:0.18, ease:'power3.out'}}, {t:.2f});"
                )
                lines.append(
                    f"  tl.to('#{ident}', {{opacity:0, scale:0.95, x:-40, duration:0.18, ease:'power2.in'}}, {t + d - 0.18:.2f});"
                )
            else:  # fade
                lines.append(
                    f"  tl.to('#{ident}', {{opacity:1, duration:0.2, ease:'power2.out'}}, {t:.2f});"
                )
                lines.append(
                    f"  tl.to('#{ident}', {{opacity:0, duration:0.2, ease:'power2.in'}}, {t + d - 0.2:.2f});"
                )

        for bi, b in enumerate(s.get("bursts") or [], start=1):
            t_cursor = float(b.get("t_start", 0))
            transition = b.get("transition", "cut")
            for k, item in enumerate(b.get("items", []), start=1):
                d = float(item.get("duration", 0.5))
                ident = f"burst-s{scene_num}-{bi}-{k}"
                if transition == "cut":
                    lines.append(f"  tl.set('#{ident}', {{opacity:1, scale:1}}, {t_cursor:.2f});")
                    lines.append(f"  tl.set('#{ident}', {{opacity:0}}, {t_cursor + d:.2f});")
                else:
                    lines.append(
                        f"  tl.fromTo('#{ident}', {{opacity:0, scale:0.85}}, "
                        f"{{opacity:1, scale:1, duration:0.15, ease:'back.out(1.6)'}}, {t_cursor:.2f});"
                    )
                    lines.append(
                        f"  tl.to('#{ident}', {{opacity:0, duration:0.12, ease:'power2.in'}}, {t_cursor + d - 0.12:.2f});"
                    )
                t_cursor += d

        for fi, f in enumerate(s.get("flashes") or [], start=1):
            t = float(f.get("t", 0))
            d = float(f.get("duration", 0.9))
            ident = f"flash-s{scene_num}-{fi}"
            lines.append(
                f"  tl.fromTo('#{ident}', {{opacity:0, scale:0.6}}, "
                f"{{opacity:1, scale:1, duration:0.15, ease:'back.out(2)'}}, {t:.2f});"
            )
            lines.append(
                f"  tl.to('#{ident}', {{opacity:0, scale:1.08, duration:0.18, ease:'power2.in'}}, {t + d - 0.18:.2f});"
            )

    lines.append("})();")
    return "\n".join(lines)


def has_any_density(scenes: list[dict]) -> bool:
    for s in scenes or []:
        if s.get("inserts") or s.get("bursts") or s.get("flashes"):
            return True
    return False


def inject_density_layer(html: str, scenes: list[dict], canvas: str = "16:9") -> str:
    """Inject density mounts (HTML+CSS+JS) into rendered index.html.

    - HTML mount divs go right before `</body>` (so they layer above other clips).
    - CSS goes right before `</head>` (gracefully degrades if missing).
    - GSAP animation block goes after the last existing `<script>` block,
      wrapped in IIFE so it picks up `tl` lazily.

    If `scenes` has no density data → return html unchanged (safe noop).
    """
    if not has_any_density(scenes):
        return html

    css = _css_block(canvas)
    mounts_html = _html_mounts(scenes)
    anim_script = (
        '\n<script>\n'
        '  // Density layer wires onto the global GSAP timeline after main script runs.\n'
        '  window.addEventListener("hyperframes:timeline-ready", function() {\n'
        f'    {_gsap_anims(scenes)}\n'
        '  });\n'
        '  // Fallback if the framework does not dispatch the event yet: defer 1 tick.\n'
        '  setTimeout(function() {\n'
        '    if (typeof window.__density_wired === "undefined" && typeof tl !== "undefined") {\n'
        f'      {_gsap_anims(scenes)}\n'
        '      window.__density_wired = true;\n'
        '    }\n'
        '  }, 200);\n'
        '</script>\n'
    )

    if "</head>" in html:
        html = html.replace("</head>", css + "</head>", 1)
    if "</body>" in html:
        html = html.replace("</body>", mounts_html + anim_script + "</body>", 1)
    else:
        html = html + mounts_html + anim_script
    return html
