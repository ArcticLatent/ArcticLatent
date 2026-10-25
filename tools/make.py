#!/usr/bin/env python3
"""Draws the profile's images: the banner and a card per app, each in a dark
and a light version (the README shows the one matching the viewer's theme).

    python3 tools/make.py

Edit APPS or the banner text below, run it, and commit assets/. Fonts are
Geist (assets/fonts, OFL), embedded in each SVG so the text looks the same
for everyone; logos come from assets/logos."""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

THEMES = {
    "dark": dict(bg="#15161b", bg2="#1e2029", card="#1f2028", rule="#34353f", fg="#ecedf2", text="#c9cbd4",
                 muted="#9497a3", tile="#16191d", pill="#2a2b35", glow=0.30),
    "light": dict(bg="#fbfbfd", bg2="#eff0f6", card="#ffffff", rule="#e2e3ea", fg="#1b1c22", text="#3a3c45",
                  muted="#6a6d78", tile="#16191d", pill="#f0f0f5", glow=0.16),
}

# The four apps: logo (and whether it brings its own tile), accent colours,
# lines of text (wrapped by hand: SVG text doesn't wrap), tech and platforms.
APPS = [
    dict(key="harlo", name="harlo", logo="harlo.svg", tiled=True, accent=("#c6a0f6", "#8aadf4"),
         platforms="Linux · iPhone",
         lines=["Your coding agents in one native app: Claude Code,", "OpenCode, pi and Oh My Pi, with an iPhone app."],
         tech=["Rust", "Qt 6", "SwiftUI"]),
    dict(key="comfypilot", name="ComfyPilot", logo="comfypilot.svg", tiled=False, accent=("#bd93f9", "#ff79c6"),
         platforms="Linux · Windows",
         lines=["Install, run and keep ComfyUI up to date, with", "the right models, LoRAs and workflows."],
         tech=["Rust", "Qt 6", "ComfyUI"]),
    dict(key="bootcraft", name="Bootcraft", logo="bootcraft.svg", tiled=True, accent=("#5ee0b5", "#f5c66a"),
         platforms="Fedora · Arch · Ubuntu · Mint · Debian",
         lines=["Set up a fresh Linux install in one go: drivers,", "codecs, Flatpak and your apps."],
         tech=["Rust", "Qt 6", "Linux"]),
    dict(key="comfycatalog", name="ComfyCatalog", logo="comfypilot.svg", tiled=False, accent=("#ff79c6", "#bd93f9"),
         platforms="The catalog behind ComfyPilot",
         lines=["Curates ComfyPilot's models, LoRAs and workflows:", "from a link to a published catalog in a few clicks."],
         tech=["Rust", "TypeScript", "Supabase"]),
]

BANNER = dict(kicker="ARCTIC LATENT", title="Hi, I'm Burce.",
              lines=["VFX artist, 15+ years in film and TV.", "I build native apps for Linux, in Rust and Qt."])


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fonts():
    face = lambda w, f: ("@font-face{font-family:'Geist';font-weight:%d;src:url(data:font/woff2;base64,%s) format('woff2')}"
                         % (w, base64.b64encode((ASSETS / "fonts" / f).read_bytes()).decode()))
    return "<style>%s%s text{font-family:'Geist','Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif}</style>" % (
        face(400, "Geist-Regular.woff2"), face(600, "Geist-SemiBold.woff2"))


def logo(file, x, y, size, prefix):
    """The logo as a nested <svg>, its ids prefixed (several share a banner)."""
    s = (ASSETS / "logos" / file).read_text()
    s = re.sub(r"<!--.*?-->|<\?xml.*?\?>|<title[^>]*>.*?</title>|<desc[^>]*>.*?</desc>", "", s, flags=re.S)
    s = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{prefix}-{m[1]}"', s)
    s = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{prefix}-{m[1]})", s)
    s = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{prefix}-{m[1]}"', s)
    # Only the outer <svg>'s own size goes (its shapes keep theirs).
    root = re.search(r"<svg\b[^>]*>", s)
    tag = re.sub(r'\s(width|height|role|aria-labelledby)="[^"]*"', "", root[0])
    tag = tag.replace("<svg ", f'<svg x="{x}" y="{y}" width="{size}" height="{size}" ', 1)
    return (s[:root.start()] + tag + s[root.end():]).strip()


def tile(app, t, x, y, size, prefix):
    """An app's icon on its tile (harlo's and Bootcraft's bring their own)."""
    if app["tiled"]:
        return logo(app["logo"], x, y, size, prefix)
    pad = round(size * 0.16)
    return (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{round(size * 0.22)}" fill="{t["tile"]}"/>'
            + logo(app["logo"], x + pad, y + pad, size - 2 * pad, prefix))


def card(app, mode):
    t = THEMES[mode]
    w, h = 600, 258
    a1, a2 = app["accent"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(app["name"])}: {esc(" ".join(app["lines"]))}">',
           fonts(),
           f'<defs><linearGradient id="a" x1="0" x2="1"><stop offset="0" stop-color="{a1}"/><stop offset="1" stop-color="{a2}"/></linearGradient>'
           f'<clipPath id="c"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="20"/></clipPath></defs>',
           f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="20" fill="{t["card"]}" stroke="{t["rule"]}" stroke-width="1.5"/>',
           f'<rect x="0" y="0" width="{w}" height="5" fill="url(#a)" clip-path="url(#c)"/>',
           tile(app, t, 32, 36, 76, "l"),
           f'<text x="130" y="74" font-size="34" font-weight="600" letter-spacing="-0.5" fill="{t["fg"]}">{esc(app["name"])}</text>',
           f'<text x="130" y="104" font-size="17" fill="{t["muted"]}">{esc(app["platforms"])}</text>',
           # An "opens" arrow, top right.
           f'<path d="M{w - 50} 62 L{w - 34} 46 M{w - 46} 46 H{w - 34} V58" fill="none" stroke="{t["muted"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>']
    for i, line in enumerate(app["lines"]):
        out.append(f'<text x="32" y="{150 + i * 27}" font-size="19.5" fill="{t["text"]}">{esc(line)}</text>')
    x = 32
    for word in app["tech"]:
        pw = round(len(word) * 9.2 + 30)
        out.append(f'<rect x="{x}" y="{h - 54}" width="{pw}" height="32" rx="16" fill="{t["pill"]}"/>'
                   f'<text x="{x + pw / 2}" y="{h - 32.5}" font-size="16" font-weight="600" fill="{t["text"]}" text-anchor="middle">{esc(word)}</text>')
        x += pw + 8
    out.append("</svg>")
    return "\n".join(out)


def banner(mode):
    t = THEMES[mode]
    w, h = 1280, 340
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(BANNER["title"])} {esc(" ".join(BANNER["lines"]))}">',
           fonts(),
           f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg"]}"/><stop offset="1" stop-color="{t["bg2"]}"/></linearGradient>'
           f'<radialGradient id="g1"><stop offset="0" stop-color="#c6a0f6" stop-opacity="{t["glow"]}"/><stop offset="1" stop-color="#c6a0f6" stop-opacity="0"/></radialGradient>'
           f'<radialGradient id="g2"><stop offset="0" stop-color="#8aadf4" stop-opacity="{t["glow"]}"/><stop offset="1" stop-color="#8aadf4" stop-opacity="0"/></radialGradient>'
           '<linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="#c6a0f6"/><stop offset="1" stop-color="#8aadf4"/></linearGradient>'
           f'<clipPath id="c"><rect width="{w}" height="{h}" rx="24"/></clipPath></defs>',
           '<g clip-path="url(#c)">',
           f'<rect width="{w}" height="{h}" fill="url(#bg)"/>',
           '<circle cx="980" cy="40" r="360" fill="url(#g1)"/><circle cx="1180" cy="330" r="300" fill="url(#g2)"/><circle cx="120" cy="360" r="260" fill="url(#g1)"/>',
           f'<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="24" fill="none" stroke="{t["rule"]}" stroke-width="1.5"/>',
           f'<text x="72" y="108" font-size="16" font-weight="600" letter-spacing="3.5" fill="url(#name)">{esc(BANNER["kicker"])}</text>',
           f'<text x="70" y="176" font-size="62" font-weight="600" letter-spacing="-1.5" fill="{t["fg"]}">{esc(BANNER["title"])}</text>']
    for i, line in enumerate(BANNER["lines"]):
        out.append(f'<text x="72" y="{226 + i * 34}" font-size="23" fill="{t["muted"]}">{esc(line)}</text>')
    size, gap = 100, 22
    x0 = w - 72 - 4 * size - 3 * gap
    for i, app in enumerate(APPS):
        x, y = x0 + i * (size + gap), 104 + (18 if i % 2 else 0)
        out.append(tile(app, t, x, y, size, f"b{i}"))
        out.append(f'<text x="{x + size / 2}" y="{y + size + 28}" font-size="15" fill="{t["muted"]}" text-anchor="middle">{esc(app["name"])}</text>')
    out.append("</g></svg>")
    return "\n".join(out)


def main():
    (ASSETS / "cards").mkdir(exist_ok=True)
    for mode in THEMES:
        (ASSETS / f"banner-{mode}.svg").write_text(banner(mode) + "\n")
        for app in APPS:
            (ASSETS / "cards" / f"{app['key']}-{mode}.svg").write_text(card(app, mode) + "\n")
    print("wrote", ", ".join(str(p.relative_to(ROOT)) for p in sorted(ASSETS.rglob("*.svg")) if "logos" not in p.parts))


if __name__ == "__main__":
    main()
