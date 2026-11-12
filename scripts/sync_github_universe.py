#!/usr/bin/env python3
"""
Sync live GitHub profile & repositories for lokeshkumar143 and generate:
  - assets/live-3d-universe.svg (3D Isometric Holographic Repo Metropolis)
  - assets/live-2d-blueprint.svg (2D Live Architectural Radar & Repo HUD)
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import os
import urllib.request
from pathlib import Path

USERNAME = "lokeshkumar143"
ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"

LANG_COLORS = {
    "Swift": "#F05138",
    "JavaScript": "#FACC15",
    "TypeScript": "#38BDF8",
    "Python": "#34D399",
    "R": "#A855F7",
    "Java": "#FB923C",
    "C++": "#F472B6",
    "HTML": "#FB7185",
    "CSS": "#60A5FA",
}


def fetch_json(url: str, token: str | None = None) -> dict | list:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-live-universe",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_data(user_file: str | None, repos_file: str | None) -> tuple[dict, list[dict]]:
    if user_file and repos_file:
        with open(user_file, encoding="utf-8") as f1, open(repos_file, encoding="utf-8") as f2:
            return json.load(f1), json.load(f2)
    token = os.environ.get("GITHUB_TOKEN")
    user = fetch_json(f"https://api.github.com/users/{USERNAME}", token)
    repos = fetch_json(
        f"https://api.github.com/users/{USERNAME}/repos?sort=updated&per_page=100",
        token,
    )
    return user, repos


def iso_project(x: float, y: float, z: float, cx: float, cy: float) -> tuple[float, float]:
    cos30 = 0.8660254
    sin30 = 0.5
    sx = cx + (x - y) * cos30
    sy = cy + (x + y) * sin30 - z
    return round(sx, 2), round(sy, 2)


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def shade(hex_color: str, factor: float) -> str:
    r, g, b = hex_to_rgb(hex_color)
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    return f"#{r:02X}{g:02X}{b:02X}"


def draw_iso_prism(
    cx: float,
    cy: float,
    gx: float,
    gy: float,
    w: float,
    h: float,
    color: str,
    base_z: float = 0.0,
) -> tuple[str, tuple[float, float]]:
    """Return SVG markup for a shaded 3D isometric tower and its top-center point."""
    hw = w / 2.0
    p00_b = iso_project(gx - hw, gy - hw, base_z, cx, cy)
    p10_b = iso_project(gx + hw, gy - hw, base_z, cx, cy)
    p11_b = iso_project(gx + hw, gy + hw, base_z, cx, cy)
    p01_b = iso_project(gx - hw, gy + hw, base_z, cx, cy)

    p00_t = iso_project(gx - hw, gy - hw, base_z + h, cx, cy)
    p10_t = iso_project(gx + hw, gy - hw, base_z + h, cx, cy)
    p11_t = iso_project(gx + hw, gy + hw, base_z + h, cx, cy)
    p01_t = iso_project(gx - hw, gy + hw, base_z + h, cx, cy)
    top_center = iso_project(gx, gy, base_z + h, cx, cy)

    top_col = shade(color, 1.0)
    left_col = shade(color, 0.55)
    right_col = shade(color, 0.34)
    edge_col = shade(color, 1.25)

    def pts(ps: list[tuple[float, float]]) -> str:
        return " ".join(f"{x},{y}" for x, y in ps)

    svg = (
        f'<polygon points="{pts([p01_b, p11_b, p11_t, p01_t])}" fill="{left_col}" fill-opacity="0.92" stroke="{edge_col}" stroke-width="0.9" stroke-opacity="0.7" />'
        f'<polygon points="{pts([p10_b, p11_b, p11_t, p10_t])}" fill="{right_col}" fill-opacity="0.94" stroke="{edge_col}" stroke-width="0.9" stroke-opacity="0.7" />'
        f'<polygon points="{pts([p00_t, p10_t, p11_t, p01_t])}" fill="{top_col}" fill-opacity="0.95" stroke="#FFFFFF" stroke-width="0.8" stroke-opacity="0.55" />'
    )
    return svg, top_center


def rank_repos(repos: list[dict]) -> list[dict]:
    """Select the most representative non-profile repos, prioritizing Swift/language & recent activity."""
    filtered = [r for r in repos if not r.get("fork") and r.get("name", "").lower() != USERNAME.lower()]

    def score(r: dict) -> tuple[int, str, int]:
        has_lang = 1 if r.get("language") else 0
        is_swift = 1 if r.get("language") == "Swift" else 0
        stars = int(r.get("stargazers_count", 0))
        size = int(r.get("size", 0))
        updated = r.get("updated_at", "")
        return (is_swift * 3 + has_lang * 2, updated, stars * 10 + min(size, 5000))

    return sorted(filtered, key=score, reverse=True)


def short_name(name: str, limit: int = 18) -> str:
    return name if len(name) <= limit else name[: limit - 1] + "…"


def generate_3d_universe(user: dict, repos: list[dict]) -> str:
    ranked = rank_repos(repos)
    top8 = ranked[:8]
    total_repos = int(user.get("public_repos", len(repos)))
    total_stars = sum(int(r.get("stargazers_count", 0)) for r in repos)
    sync_date = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    cx, cy = 480.0, 302.0
    step = 156.0

    # Grid coordinates around (0,0) center core
    slots = [
        (-1.0, -1.0),
        (0.0, -1.0),
        (1.0, -1.0),
        (-1.0, 0.0),
        (1.0, 0.0),
        (-1.0, 1.0),
        (0.0, 1.0),
        (1.0, 1.0),
    ]

    # Build isometric base grid lines
    grid_lines: list[str] = []
    for i in range(-2, 3):
        a1 = iso_project(i * 110, -220, 0, cx, cy)
        a2 = iso_project(i * 110, 220, 0, cx, cy)
        b1 = iso_project(-220, i * 110, 0, cx, cy)
        b2 = iso_project(220, i * 110, 0, cx, cy)
        grid_lines.append(f'<line x1="{a1[0]}" y1="{a1[1]}" x2="{a2[0]}" y2="{a2[1]}" stroke="#00F5D4" stroke-opacity="0.16" stroke-width="1" />')
        grid_lines.append(f'<line x1="{b1[0]}" y1="{b1[1]}" x2="{b2[0]}" y2="{b2[1]}" stroke="#38BDF8" stroke-opacity="0.16" stroke-width="1" />')

    # Prepare 9 towers (center core + 8 live repos), sorted back-to-front by (gx + gy)
    items: list[dict] = [
        {
            "gx": 0.0,
            "gy": 0.0,
            "is_core": True,
            "name": "LK.OS CORE",
            "lang": f"{total_repos} REPOS",
            "height": 96.0,
            "width": 58.0,
            "color": "#00F5D4",
            "delay": 0.0,
        }
    ]
    for idx, repo in enumerate(top8):
        sx, sy = slots[idx]
        lang = repo.get("language") or "Core"
        color = LANG_COLORS.get(lang, "#A855F7")
        size_kb = int(repo.get("size", 20))
        height = 38.0 + min(52.0, math.log1p(size_kb) * 7.2)
        if lang == "Swift":
            height = max(height, 78.0)
        items.append(
            {
                "gx": sx * step,
                "gy": sy * step,
                "is_core": False,
                "name": short_name(repo.get("name", "repo"), 16),
                "lang": lang,
                "height": round(height, 1),
                "width": 44.0,
                "color": color,
                "delay": (idx % 4) * 0.6,
            }
        )

    items.sort(key=lambda d: d["gx"] + d["gy"])

    core_top = iso_project(0, 0, 96.0, cx, cy)
    beams_svg: list[str] = []
    towers_svg: list[str] = []
    labels_svg: list[str] = []

    for idx, item in enumerate(items):
        prism_markup, top_pt = draw_iso_prism(
            cx, cy, item["gx"], item["gy"], item["width"], item["height"], item["color"]
        )
        color = item["color"]
        tx, ty = top_pt
        dur = 3.6 + (idx % 3) * 0.7

        if not item["is_core"]:
            beam_id = f"beam-{idx}"
            beams_svg.append(
                f'<path id="{beam_id}" d="M {tx},{ty} Q {(tx+core_top[0])/2},{min(ty,core_top[1])-34} {core_top[0]},{core_top[1]}" '
                f'fill="none" stroke="{color}" stroke-opacity="0.35" stroke-width="1.2" stroke-dasharray="5 5" />'
            )
            beams_svg.append(
                f'<circle r="2.8" fill="#FFFFFF" filter="url(#glow3d)">'
                f'<animateMotion dur="{2.0 + (idx % 3) * 0.5}s" repeatCount="indefinite"><mpath href="#{beam_id}" /></animateMotion>'
                f'</circle>'
            )

        tower_group = (
            f'<g>'
            f'  <animateTransform attributeName="transform" type="translate" values="0,0; 0,-5; 0,0" dur="{dur}s" repeatCount="indefinite" />'
            f'  {prism_markup}'
            f'  <line x1="{tx}" y1="{ty}" x2="{tx}" y2="{ty - 22}" stroke="{color}" stroke-width="1.6" stroke-opacity="0.8" />'
            f'  <circle cx="{tx}" cy="{ty - 22}" r="3.2" fill="{color}" filter="url(#glow3d)" />'
            f'</g>'
        )
        towers_svg.append(tower_group)

        # Holographic floating badge above spire
        lbl_y = ty - 38
        badge_w = 118 if not item["is_core"] else 126
        bx = max(18.0, min(942.0 - badge_w, tx - badge_w / 2.0))
        by = max(62.0, lbl_y - 16)
        safe_name = html.escape(item["name"])
        safe_lang = html.escape(item["lang"])
        labels_svg.append(
            f'<g>'
            f'  <animateTransform attributeName="transform" type="translate" values="0,0; 0,-5; 0,0" dur="{dur}s" repeatCount="indefinite" />'
            f'  <rect x="{bx:.1f}" y="{by:.1f}" width="{badge_w}" height="28" rx="7" fill="#060C18" fill-opacity="0.92" stroke="{color}" stroke-opacity="0.75" stroke-width="1.1" />'
            f'  <text x="{bx + badge_w/2:.1f}" y="{by + 12:.1f}" text-anchor="middle" class="mono" font-size="9.5" font-weight="700" fill="#F8FAFC">{safe_name}</text>'
            f'  <text x="{bx + badge_w/2:.1f}" y="{by + 23:.1f}" text-anchor="middle" class="mono" font-size="8.2" font-weight="700" fill="{color}">{safe_lang}</text>'
            f'</g>'
        )

    plat_p = [
        iso_project(-235, -235, -6, cx, cy),
        iso_project(235, -235, -6, cx, cy),
        iso_project(235, 235, -6, cx, cy),
        iso_project(-235, 235, -6, cx, cy),
    ]
    plat_pts = " ".join(f"{x},{y}" for x, y in plat_p)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 440" width="100%" role="img" aria-label="Live 3D Isometric GitHub Universe for {USERNAME}">
  <defs>
    <linearGradient id="u3d-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#02050D" />
      <stop offset="50%" stop-color="#060E1E" />
      <stop offset="100%" stop-color="#030712" />
    </linearGradient>
    <radialGradient id="u3d-halo" cx="50%" cy="62%" r="48%">
      <stop offset="0%" stop-color="#00F5D4" stop-opacity="0.22" />
      <stop offset="55%" stop-color="#38BDF8" stop-opacity="0.08" />
      <stop offset="100%" stop-color="#02050D" stop-opacity="0" />
    </radialGradient>
    <filter id="glow3d" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="3.5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <style>
      .mono {{ font-family: ui-monospace, "SF Mono", Menlo, Monaco, Consolas, monospace; }}
      .sans {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    </style>
  </defs>

  <rect x="6" y="6" width="948" height="428" rx="18" fill="url(#u3d-bg)" stroke="#1E293B" stroke-width="1.5" />
  <rect x="6" y="6" width="948" height="428" rx="18" fill="url(#u3d-halo)" />

  <!-- Top HUD Header -->
  <rect x="24" y="20" width="912" height="34" rx="10" fill="#071020" stroke="#00F5D4" stroke-opacity="0.35" stroke-width="1" />
  <circle cx="42" cy="37" r="4" fill="#00F5D4" filter="url(#glow3d)">
    <animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite" />
  </circle>
  <text x="56" y="41" class="mono" font-size="11" font-weight="700" fill="#00F5D4">LIVE 3D ISOMETRIC REPO UNIVERSE // @{USERNAME}</text>
  <text x="920" y="41" text-anchor="end" class="mono" font-size="10.5" fill="#94A3B8">
    REPOS: <tspan fill="#F8FAFC" font-weight="700">{total_repos}</tspan> &#160;|&#160; STARS: <tspan fill="#FACC15" font-weight="700">{total_stars}</tspan> &#160;|&#160; SYNCED: <tspan fill="#38BDF8">{sync_date}</tspan>
  </text>

  <!-- Isometric Base Platform -->
  <polygon points="{plat_pts}" fill="#071224" fill-opacity="0.72" stroke="#00F5D4" stroke-opacity="0.45" stroke-width="1.4" />
  {''.join(grid_lines)}

  <!-- Orbital Telemetry Ellipse Around City -->
  <ellipse cx="{cx}" cy="{cy+20}" rx="340" ry="128" fill="none" stroke="#38BDF8" stroke-opacity="0.22" stroke-width="1.2" stroke-dasharray="10 8" />

  <!-- Energy Conduits & Towers -->
  {''.join(beams_svg)}
  {''.join(towers_svg)}
  {''.join(labels_svg)}

  <!-- Bottom Legend -->
  <text x="480" y="420" text-anchor="middle" class="mono" font-size="10" fill="#64748B">
    AUTO-GENERATED FROM LIVE GITHUB API &#8226; <tspan fill="#F05138">&#9632; SWIFT</tspan> &#160;<tspan fill="#FACC15">&#9632; JAVASCRIPT</tspan> &#160;<tspan fill="#38BDF8">&#9632; TYPESCRIPT</tspan> &#160;<tspan fill="#A855F7">&#9632; AI / CORE</tspan>
  </text>
</svg>
"""


def generate_2d_blueprint(user: dict, repos: list[dict]) -> str:
    ranked = rank_repos(repos)
    top6 = ranked[:6]
    total_repos = int(user.get("public_repos", len(repos)))
    followers = int(user.get("followers", 0))

    # Language breakdown across all repos
    counts: dict[str, int] = {}
    for r in repos:
        lang = r.get("language") or "Systems / Lab"
        counts[lang] = counts.get(lang, 0) + 1
    top_langs = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:5]

    cards_svg: list[str] = []
    for i, repo in enumerate(top6):
        col = i % 3
        row = i // 3
        x = 24 + col * 308
        y = 104 + row * 102
        name = html.escape(short_name(repo.get("name", "repo"), 24))
        lang = repo.get("language") or "Core / QA"
        color = LANG_COLORS.get(lang, "#00F5D4")
        updated = (repo.get("updated_at") or "")[:10]
        size_kb = int(repo.get("size", 0))
        stars = int(repo.get("stargazers_count", 0))

        cards_svg.append(
            f'<g>'
            f'  <rect x="{x}" y="{y}" width="296" height="90" rx="10" fill="#071020" stroke="{color}" stroke-opacity="0.45" stroke-width="1.2" />'
            f'  <rect x="{x}" y="{y+14}" width="3.5" height="62" rx="1.75" fill="{color}" />'
            f'  <circle cx="{x+278}" cy="{y+20}" r="3.5" fill="{color}">'
            f'    <animate attributeName="opacity" values="1;0.25;1" dur="{1.6 + (i%3)*0.4}s" repeatCount="indefinite" />'
            f'  </circle>'
            f'  <text x="{x+16}" y="{y+25}" class="mono" font-size="9.5" font-weight="700" fill="{color}">NODE 0{i+1} // {html.escape(lang.upper())}</text>'
            f'  <text x="{x+16}" y="{y+48}" class="sans" font-size="15" font-weight="800" fill="#F8FAFC">{name}</text>'
            f'  <text x="{x+16}" y="{y+73}" class="mono" font-size="10" fill="#94A3B8">UPDATED {updated} &#8226; {size_kb} KB &#8226; &#9733; {stars}</text>'
            f'</g>'
        )

    lang_pills: list[str] = []
    px = 24
    for lang, cnt in top_langs:
        col = LANG_COLORS.get(lang, "#A855F7")
        lbl = f"{lang}: {cnt}"
        pw = max(92, len(lbl) * 7.6 + 22)
        lang_pills.append(
            f'<rect x="{px}" y="60" width="{pw:.0f}" height="24" rx="6" fill="#071020" stroke="{col}" stroke-opacity="0.5" stroke-width="1" />'
            f'<text x="{px + pw/2:.1f}" y="76" text-anchor="middle" class="mono" font-size="10" font-weight="700" fill="{col}">{html.escape(lbl)}</text>'
        )
        px += int(pw) + 10

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 326" width="100%" role="img" aria-label="Live 2D Architectural Repo Blueprint for {USERNAME}">
  <defs>
    <linearGradient id="b2d-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#030712" />
      <stop offset="100%" stop-color="#081122" />
    </linearGradient>
    <pattern id="b2d-grid" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#38BDF8" stroke-opacity="0.07" stroke-width="0.8" />
    </pattern>
    <style>
      .mono {{ font-family: ui-monospace, "SF Mono", Menlo, Monaco, Consolas, monospace; }}
      .sans {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    </style>
  </defs>

  <rect x="6" y="6" width="948" height="314" rx="16" fill="url(#b2d-bg)" stroke="#1E293B" stroke-width="1.4" />
  <rect x="6" y="6" width="948" height="314" rx="16" fill="url(#b2d-grid)" />

  <text x="24" y="38" class="mono" font-size="12" font-weight="700" fill="#38BDF8" letter-spacing="1.2">2D ARCHITECTURAL RADAR // LIVE REPOSITORY MATRIX</text>
  <text x="936" y="38" text-anchor="end" class="mono" font-size="11" fill="#94A3B8">
    PUBLIC REPOS: <tspan fill="#00F5D4" font-weight="700">{total_repos}</tspan> &#160;|&#160; FOLLOWERS: <tspan fill="#FF2E63" font-weight="700">{followers}</tspan>
  </text>

  {''.join(lang_pills)}
  {''.join(cards_svg)}
</svg>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-json", help="Optional path to cached user JSON")
    parser.add_argument("--repos-json", help="Optional path to cached repos JSON")
    args = parser.parse_args()

    user, repos = load_data(args.user_json, args.repos_json)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    (ASSETS_DIR / "live-3d-universe.svg").write_text(
        generate_3d_universe(user, repos), encoding="utf-8"
    )
    (ASSETS_DIR / "live-2d-blueprint.svg").write_text(
        generate_2d_blueprint(user, repos), encoding="utf-8"
    )
    print(f"Generated live 3D & 2D SVGs from {len(repos)} repos for @{USERNAME}.")


if __name__ == "__main__":
    main()
