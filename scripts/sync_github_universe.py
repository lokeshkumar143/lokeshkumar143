#!/usr/bin/env python3
"""
Sync live GitHub profile, avatar & repositories for lokeshkumar143 and generate:
  - assets/portrait-terminal.svg (macOS Terminal ASCII Portrait from live GitHub avatar)
  - assets/terminal-identity.svg (macOS Terminal Live Neofetch & Career Telemetry)
  - assets/live-3d-universe.svg (3D Isometric Holographic Repo Metropolis)
  - assets/live-2d-blueprint.svg (2D Live Architectural Radar & Repo HUD)
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import io
import json
import math
import os
import urllib.request
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

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


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": f"{USERNAME}-live-universe"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def load_data(
    user_file: str | None,
    repos_file: str | None,
    avatar_file: str | None,
) -> tuple[dict, list[dict], Image.Image]:
    if user_file and repos_file:
        with open(user_file, encoding="utf-8") as f1, open(repos_file, encoding="utf-8") as f2:
            user = json.load(f1)
            repos = json.load(f2)
    else:
        token = os.environ.get("GITHUB_TOKEN")
        user = fetch_json(f"https://api.github.com/users/{USERNAME}", token)
        repos = fetch_json(
            f"https://api.github.com/users/{USERNAME}/repos?sort=updated&per_page=100",
            token,
        )

    if avatar_file and os.path.exists(avatar_file):
        avatar_img = Image.open(avatar_file).convert("RGB")
    else:
        avatar_url = user.get("avatar_url") or f"https://github.com/{USERNAME}.png"
        avatar_img = Image.open(io.BytesIO(fetch_bytes(avatar_url))).convert("RGB")

    return user, repos, avatar_img


def avatar_to_ascii_lines(img: Image.Image, cols: int = 78, rows: int = 50) -> list[str]:
    """Convert a portrait avatar into a clean, high-contrast ASCII silhouette."""
    w, h = img.size
    crop = img.crop((int(w * 0.14), int(h * 0.13), int(w * 0.86), int(h * 0.95)))
    small = crop.resize((cols, rows), Image.Resampling.LANCZOS)
    gray = ImageOps.autocontrast(small.convert("L"), cutoff=2)
    gray = ImageEnhance.Contrast(gray).enhance(1.55)
    edges = (
        crop.convert("L")
        .filter(ImageFilter.FIND_EDGES)
        .resize((cols, rows), Image.Resampling.LANCZOS)
    )

    ramp = " .:-=+*#%@"
    lines: list[str] = []
    for r in range(rows):
        ny = r / (rows - 1)
        row_chars: list[str] = []
        for c in range(cols):
            nx = c / (cols - 1)
            dx_h = (nx - 0.50) / 0.235
            dy_h = (ny - 0.34) / 0.255
            d_head = dx_h * dx_h + dy_h * dy_h

            in_neck = (0.48 <= ny <= 0.70) and (abs(nx - 0.50) <= 0.145)
            dx_s = (nx - 0.50) / 0.46
            dy_s = (ny - 1.04) / 0.45
            d_sh = dx_s * dx_s + dy_s * dy_s

            if not ((d_head <= 1.0) or in_neck or (ny >= 0.58 and d_sh <= 1.0)):
                row_chars.append(" ")
                continue

            lum = gray.getpixel((c, r))
            ed = edges.getpixel((c, r))

            if ny >= 0.62 and not in_neck:
                if 0.88 <= d_sh <= 1.0 or ed > 45:
                    val = max(lum, ed)
                    idx = min(len(ramp) - 1, max(1, int(val / 255 * (len(ramp) - 1))))
                    row_chars.append(ramp[idx])
                elif lum > 65:
                    row_chars.append(":")
                else:
                    row_chars.append(" ")
                continue

            if d_head > 0.88 and ny < 0.56:
                lum = int(lum * max(0.2, (1.0 - d_head) / 0.12))
            val = min(255, int(lum * 0.92 + ed * 0.22))
            if val < 18:
                row_chars.append(".")
            else:
                idx = min(len(ramp) - 1, max(1, int(val / 255 * (len(ramp) - 1))))
                row_chars.append(ramp[idx])
        lines.append("".join(row_chars))
    return lines


def generate_portrait_terminal(user: dict, avatar_img: Image.Image) -> str:
    display_name = html.escape(user.get("name") or "Lokesh Kumar S")
    ascii_lines = avatar_to_ascii_lines(avatar_img, cols=78, rows=50)

    text_rows: list[str] = []
    start_y = 66
    dy = 9.4
    for i, line in enumerate(ascii_lines):
        y = start_y + i * dy
        # Highlight face/eyes region slightly brighter, hair/shoulders crisp silver-cyan
        fill = "#E2E8F0" if 11 <= i <= 32 else "#94A3B8"
        text_rows.append(
            f'<text x="46" y="{y:.1f}" xml:space="preserve" class="ascii" fill="{fill}">{html.escape(line)}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 600" width="100%" role="img" aria-label="macOS Terminal ASCII Portrait of {display_name}">
  <defs>
    <linearGradient id="pt-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090D16" />
      <stop offset="100%" stop-color="#0E1420" />
    </linearGradient>
    <linearGradient id="pt-scan" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#00F5D4" stop-opacity="0" />
      <stop offset="50%" stop-color="#00F5D4" stop-opacity="0.14" />
      <stop offset="100%" stop-color="#00F5D4" stop-opacity="0" />
    </linearGradient>
    <clipPath id="pt-clip">
      <rect x="4" y="4" width="492" height="592" rx="14" />
    </clipPath>
    <style>
      .mono {{ font-family: ui-monospace, "SF Mono", Menlo, Monaco, Consolas, "Courier New", monospace; }}
      .ascii {{
        font-family: ui-monospace, "SF Mono", Menlo, Monaco, Consolas, "Courier New", monospace;
        font-size: 8.6px;
        letter-spacing: 0.2px;
      }}
      @keyframes blinkCursor {{
        0%, 49% {{ opacity: 1; }}
        50%, 100% {{ opacity: 0; }}
      }}
      .cursor {{ animation: blinkCursor 1.1s infinite; }}
    </style>
  </defs>

  <rect x="4" y="4" width="492" height="592" rx="14" fill="url(#pt-bg)" stroke="#263042" stroke-width="1.4" />

  <g clip-path="url(#pt-clip)">
    <!-- Title Bar -->
    <rect x="4" y="4" width="492" height="38" fill="#131926" />
    <line x1="4" y1="42" x2="496" y2="42" stroke="#222B3B" stroke-width="1" />
    <circle cx="26" cy="23" r="5.5" fill="#FF5F56" />
    <circle cx="45" cy="23" r="5.5" fill="#FFBD2E" />
    <circle cx="64" cy="23" r="5.5" fill="#27C93F" />
    <text x="250" y="27" text-anchor="middle" class="mono" font-size="11.5" fill="#94A3B8">lokesh@github: ~$ ./portrait.sh</text>

    <!-- Subtle Futuristic Hologram Scanline -->
    <rect x="4" y="42" width="492" height="28" fill="url(#pt-scan)">
      <animate attributeName="y" values="42;545;42" dur="7s" repeatCount="indefinite" />
    </rect>

    <!-- Live ASCII Portrait from GitHub Avatar -->
    {''.join(text_rows)}

    <!-- Terminal Prompt Footer -->
    <line x1="18" y1="554" x2="482" y2="554" stroke="#222B3B" stroke-width="1" />
    <text x="22" y="579" class="mono" font-size="12" fill="#94A3B8">
      <tspan fill="#00F5D4">lokesh@github</tspan>:<tspan fill="#38BDF8">~</tspan>$ whoami <tspan fill="#F8FAFC" font-weight="700">{display_name}</tspan>
    </text>
    <rect x="336" y="568" width="7" height="14" rx="1" fill="#00F5D4" class="cursor" />
  </g>
</svg>
"""


def generate_terminal_identity(user: dict, repos: list[dict]) -> str:
    total_repos = int(user.get("public_repos", len(repos)))
    followers = int(user.get("followers", 0))
    ranked = rank_repos(repos)
    latest_repo = html.escape(ranked[0].get("name", "RecovFit.ios") if ranked else "RecovFit.ios")
    sync_date = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 600" width="100%" role="img" aria-label="macOS Terminal System Telemetry for {USERNAME}">
  <defs>
    <linearGradient id="ti-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090D16" />
      <stop offset="100%" stop-color="#0D1422" />
    </linearGradient>
    <linearGradient id="ti-bar" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00F5D4" />
      <stop offset="50%" stop-color="#38BDF8" />
      <stop offset="100%" stop-color="#FF2E63" />
    </linearGradient>
    <filter id="ti-glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3" result="blur" />
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

  <rect x="4" y="4" width="492" height="592" rx="14" fill="url(#ti-bg)" stroke="#263042" stroke-width="1.4" />

  <!-- Title Bar -->
  <path d="M 4 18 Q 4 4 18 4 L 482 4 Q 496 4 496 18 L 496 42 L 4 42 Z" fill="#131926" />
  <line x1="4" y1="42" x2="496" y2="42" stroke="#222B3B" stroke-width="1" />
  <circle cx="26" cy="23" r="5.5" fill="#FF5F56" />
  <circle cx="45" cy="23" r="5.5" fill="#FFBD2E" />
  <circle cx="64" cy="23" r="5.5" fill="#27C93F" />
  <text x="250" y="27" text-anchor="middle" class="mono" font-size="11.5" fill="#94A3B8">lokesh@github: ~$ ./neofetch --live</text>

  <!-- Live Sync Banner -->
  <rect x="22" y="58" width="456" height="36" rx="9" fill="#061220" stroke="#00F5D4" stroke-opacity="0.45" stroke-width="1" />
  <circle cx="40" cy="76" r="4" fill="#00F5D4" filter="url(#ti-glow)">
    <animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite" />
  </circle>
  <text x="54" y="80" class="mono" font-size="11" font-weight="700" fill="#00F5D4">LIVE GITHUB API SYNCED // @{USERNAME}</text>
  <text x="464" y="80" text-anchor="end" class="mono" font-size="10.5" fill="#94A3B8">{sync_date}</text>

  <!-- System Specs Section -->
  <text x="24" y="122" class="mono" font-size="11.5" font-weight="700" fill="#38BDF8">LOKESH.OS // ENGINEERING SPEC</text>
  <line x1="24" y1="130" x2="476" y2="130" stroke="#1E293B" stroke-width="1" />

  <text x="24" y="154" class="mono" font-size="12" fill="#CBD5E1"><tspan fill="#00F5D4" font-weight="700">ROLE     :</tspan> iOS Developer &amp; Technical Trainer</text>
  <text x="24" y="177" class="mono" font-size="12" fill="#CBD5E1"><tspan fill="#00F5D4" font-weight="700">ORG      :</tspan> SIMATS Engineering Institution</text>
  <text x="24" y="200" class="mono" font-size="12" fill="#CBD5E1"><tspan fill="#FF2E63" font-weight="700">GROWTH   :</tspan> Intern &#8594; Full-Time in 2 Months</text>
  <text x="24" y="223" class="mono" font-size="12" fill="#CBD5E1"><tspan fill="#38BDF8" font-weight="700">APPLE OS :</tspan> Swift &#183; SwiftUI &#183; UIKit &#183; App Store</text>
  <text x="24" y="246" class="mono" font-size="12" fill="#CBD5E1"><tspan fill="#38BDF8" font-weight="700">BACKEND  :</tspan> Firebase &#183; REST APIs &#183; PHP &#183; MySQL</text>
  <text x="24" y="269" class="mono" font-size="12" fill="#CBD5E1"><tspan fill="#A855F7" font-weight="700">QA LAYER :</tspan> Appium &#183; Selenium &#183; Postman &#183; Sec</text>
  <text x="24" y="292" class="mono" font-size="12" fill="#CBD5E1"><tspan fill="#A855F7" font-weight="700">CERT/EDU :</tspan> Oracle AI Certified &#183; B.E. CSE (7.9)</text>

  <!-- Live GitHub Telemetry Bento Cards -->
  <text x="24" y="330" class="mono" font-size="11.5" font-weight="700" fill="#FF2E63">LIVE GITHUB TELEMETRY</text>
  <line x1="24" y1="338" x2="476" y2="338" stroke="#1E293B" stroke-width="1" />

  <rect x="24" y="352" width="142" height="74" rx="10" fill="#060F1D" stroke="#00F5D4" stroke-opacity="0.45" stroke-width="1" />
  <text x="95" y="384" text-anchor="middle" class="sans" font-size="26" font-weight="800" fill="#00F5D4">{total_repos}</text>
  <text x="95" y="408" text-anchor="middle" class="mono" font-size="10" fill="#94A3B8">PUBLIC REPOS</text>

  <rect x="179" y="352" width="142" height="74" rx="10" fill="#060F1D" stroke="#38BDF8" stroke-opacity="0.45" stroke-width="1" />
  <text x="250" y="384" text-anchor="middle" class="sans" font-size="26" font-weight="800" fill="#38BDF8">4</text>
  <text x="250" y="408" text-anchor="middle" class="mono" font-size="10" fill="#94A3B8">QA DISCIPLINES</text>

  <rect x="334" y="352" width="142" height="74" rx="10" fill="#060F1D" stroke="#FF2E63" stroke-opacity="0.45" stroke-width="1" />
  <text x="405" y="384" text-anchor="middle" class="sans" font-size="26" font-weight="800" fill="#FF2E63">{followers}</text>
  <text x="405" y="408" text-anchor="middle" class="mono" font-size="10" fill="#94A3B8">FOLLOWERS</text>

  <!-- Flagship Spotlight Box -->
  <rect x="24" y="442" width="452" height="68" rx="10" fill="#07101E" stroke="#F05138" stroke-opacity="0.55" stroke-width="1.2" />
  <text x="40" y="465" class="mono" font-size="10.5" font-weight="700" fill="#F05138">FLAGSHIP SWIFT REPOSITORY // LIVE</text>
  <text x="40" y="489" class="sans" font-size="16" font-weight="800" fill="#F8FAFC">{latest_repo}</text>
  <text x="460" y="489" text-anchor="end" class="mono" font-size="10.5" fill="#6EE7B7">&#9679; APP STORE READY</text>

  <!-- Animated Energy Spectrum Bar -->
  <rect x="24" y="526" width="452" height="10" rx="5" fill="#0F172A" />
  <rect x="24" y="526" width="220" height="10" rx="5" fill="url(#ti-bar)">
    <animate attributeName="width" values="140;440;210;452;140" dur="6s" repeatCount="indefinite" />
  </rect>

  <!-- Terminal Prompt Footer -->
  <line x1="18" y1="554" x2="482" y2="554" stroke="#222B3B" stroke-width="1" />
  <text x="24" y="579" class="mono" font-size="11.5" fill="#94A3B8">
    <tspan fill="#00F5D4">status:</tspan> <tspan fill="#F8FAFC">open to iOS &amp; mobile product roles</tspan>
  </text>
</svg>
"""


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

    grid_lines: list[str] = []
    for i in range(-2, 3):
        a1 = iso_project(i * 110, -220, 0, cx, cy)
        a2 = iso_project(i * 110, 220, 0, cx, cy)
        b1 = iso_project(-220, i * 110, 0, cx, cy)
        b2 = iso_project(220, i * 110, 0, cx, cy)
        grid_lines.append(f'<line x1="{a1[0]}" y1="{a1[1]}" x2="{a2[0]}" y2="{a2[1]}" stroke="#00F5D4" stroke-opacity="0.16" stroke-width="1" />')
        grid_lines.append(f'<line x1="{b1[0]}" y1="{b1[1]}" x2="{b2[0]}" y2="{b2[1]}" stroke="#38BDF8" stroke-opacity="0.16" stroke-width="1" />')

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

        towers_svg.append(
            f'<g>'
            f'  <animateTransform attributeName="transform" type="translate" values="0,0; 0,-5; 0,0" dur="{dur}s" repeatCount="indefinite" />'
            f'  {prism_markup}'
            f'  <line x1="{tx}" y1="{ty}" x2="{tx}" y2="{ty - 22}" stroke="{color}" stroke-width="1.6" stroke-opacity="0.8" />'
            f'  <circle cx="{tx}" cy="{ty - 22}" r="3.2" fill="{color}" filter="url(#glow3d)" />'
            f'</g>'
        )

        lbl_y = ty - 38
        badge_w = 118 if not item["is_core"] else 126
        bx = max(18.0, min(942.0 - badge_w, tx - badge_w / 2.0))
        by = max(62.0, lbl_y - 16)
        labels_svg.append(
            f'<g>'
            f'  <animateTransform attributeName="transform" type="translate" values="0,0; 0,-5; 0,0" dur="{dur}s" repeatCount="indefinite" />'
            f'  <rect x="{bx:.1f}" y="{by:.1f}" width="{badge_w}" height="28" rx="7" fill="#060C18" fill-opacity="0.92" stroke="{color}" stroke-opacity="0.75" stroke-width="1.1" />'
            f'  <text x="{bx + badge_w/2:.1f}" y="{by + 12:.1f}" text-anchor="middle" class="mono" font-size="9.5" font-weight="700" fill="#F8FAFC">{html.escape(item["name"])}</text>'
            f'  <text x="{bx + badge_w/2:.1f}" y="{by + 23:.1f}" text-anchor="middle" class="mono" font-size="8.2" font-weight="700" fill="{color}">{html.escape(item["lang"])}</text>'
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

  <rect x="24" y="20" width="912" height="34" rx="10" fill="#071020" stroke="#00F5D4" stroke-opacity="0.35" stroke-width="1" />
  <circle cx="42" cy="37" r="4" fill="#00F5D4" filter="url(#glow3d)">
    <animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite" />
  </circle>
  <text x="56" y="41" class="mono" font-size="11" font-weight="700" fill="#00F5D4">LIVE 3D ISOMETRIC REPO UNIVERSE // @{USERNAME}</text>
  <text x="920" y="41" text-anchor="end" class="mono" font-size="10.5" fill="#94A3B8">
    REPOS: <tspan fill="#F8FAFC" font-weight="700">{total_repos}</tspan> &#160;|&#160; STARS: <tspan fill="#FACC15" font-weight="700">{total_stars}</tspan> &#160;|&#160; SYNCED: <tspan fill="#38BDF8">{sync_date}</tspan>
  </text>

  <polygon points="{plat_pts}" fill="#071224" fill-opacity="0.72" stroke="#00F5D4" stroke-opacity="0.45" stroke-width="1.4" />
  {''.join(grid_lines)}
  <ellipse cx="{cx}" cy="{cy+20}" rx="340" ry="128" fill="none" stroke="#38BDF8" stroke-opacity="0.22" stroke-width="1.2" stroke-dasharray="10 8" />

  {''.join(beams_svg)}
  {''.join(towers_svg)}
  {''.join(labels_svg)}

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
    parser.add_argument("--avatar-img", help="Optional path to cached avatar image")
    args = parser.parse_args()

    user, repos, avatar_img = load_data(args.user_json, args.repos_json, args.avatar_img)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    (ASSETS_DIR / "portrait-terminal.svg").write_text(
        generate_portrait_terminal(user, avatar_img), encoding="utf-8"
    )
    (ASSETS_DIR / "terminal-identity.svg").write_text(
        generate_terminal_identity(user, repos), encoding="utf-8"
    )
    (ASSETS_DIR / "live-3d-universe.svg").write_text(
        generate_3d_universe(user, repos), encoding="utf-8"
    )
    (ASSETS_DIR / "live-2d-blueprint.svg").write_text(
        generate_2d_blueprint(user, repos), encoding="utf-8"
    )
    print(f"Generated ASCII portrait, identity terminal, and live 3D/2D SVGs from {len(repos)} repos for @{USERNAME}.")


if __name__ == "__main__":
    main()
