"""Build the profile header SVGs (light and dark) from theme.json.

Standard library only:  python3 assets/src/build.py
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape

SRC = Path(__file__).parent
OUT = SRC.parent

W, H = 1200, 352
PAD = 56
TITLEBAR = 40
PIXEL = 9          # one '#' of the banner
GAP = 1.5          # space between pixels
LINE = 30          # terminal line height
FONT_SIZE = 19

# Terminal session shown under the name. Each line is a list of (token, text).
SESSION = [
    [("prompt", "~ "), ("faint", "$ "), ("ink", "whoami")],
    [("muted", "Management Engineering graduate · University of Bologna")],
    [("prompt", "~ "), ("faint", "$ "), ("ink", "ls projects/")],
    [("accent", "industrial-manual-ingestion  "), ("accent", "career-day  "),
     ("accent", "audiopro  "), ("accent", "ferrari-optimization")],
    [("prompt", "~ "), ("faint", "$ "), ("cursor", "")],
]


def banner_pixels():
    rows = (SRC / "name-banner.txt").read_text().splitlines()
    return [(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch == "#"], len(rows)


def build(mode, theme):
    c = theme[mode]
    mono = theme["font_mono"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-labelledby="t d">',
        '<title id="t">Michele Mazza</title>',
        '<desc id="d">Terminal-style header: Management Engineering graduate, University of Bologna. '
        'Projects: industrial-manual-ingestion, career-day, audiopro, ferrari-optimization.</desc>',
        # window
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{c["window"]}" stroke="{c["border"]}"/>',
        f'<path d="M14.5 0.5 H{W-14.5} A14 14 0 0 1 {W-0.5} 14.5 V{TITLEBAR} H0.5 V14.5 A14 14 0 0 1 14.5 0.5 Z" '
        f'fill="{c["titlebar"]}" stroke="{c["border"]}"/>',
    ]
    for i, col in enumerate(theme["traffic_lights"]):
        parts.append(f'<circle cx="{24 + i*20}" cy="{TITLEBAR/2}" r="6" fill="{col}"/>')
    parts.append(
        f'<text x="{W/2}" y="{TITLEBAR/2 + 5}" text-anchor="middle" font-family="{escape(mono)}" '
        f'font-size="13" fill="{c["faint"]}">michele@cometasensitiva: ~</text>'
    )

    # pixel banner: a cobalt offset layer under the lavender one
    pixels, nrows = banner_pixels()
    top = TITLEBAR + 44
    size = PIXEL - GAP
    for layer, colour, off in (("shadow", c["accent_shadow"], 2.5), ("face", c["accent"], 0)):
        parts.append(f'<g fill="{colour}">')
        for x, y in pixels:
            parts.append(
                f'<rect x="{PAD + x*PIXEL + off:.1f}" y="{top + y*PIXEL + off:.1f}" '
                f'width="{size}" height="{size}" rx="1.5"/>'
            )
        parts.append('</g>')

    # terminal session
    colours = {"prompt": c["action"], "faint": c["faint"], "ink": c["ink"],
               "muted": c["muted"], "accent": c["accent"]}
    y = top + nrows*PIXEL + 52
    for line in SESSION:
        spans, cursor = [], False
        for token, text in line:
            if token == "cursor":
                cursor = True
                continue
            spans.append(f'<tspan fill="{colours[token]}">{escape(text)}</tspan>')
        parts.append(
            f'<text x="{PAD}" y="{y}" font-family="{escape(mono)}" font-size="{FONT_SIZE}" '
            f'xml:space="preserve">{"".join(spans)}</text>'
        )
        if cursor:
            # after "~ $ " = 4 characters of a monospace font (≈0.6 em each)
            cx = PAD + 4 * FONT_SIZE * 0.6
            parts.append(
                f'<rect x="{cx:.1f}" y="{y - FONT_SIZE + 3}" width="{FONT_SIZE*0.55:.1f}" height="{FONT_SIZE}" '
                f'fill="{c["accent"]}"><animate attributeName="opacity" values="1;1;0;0" '
                f'keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></rect>'
            )
        y += LINE

    parts.append('</svg>')
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    theme = json.loads((SRC / "theme.json").read_text())
    for mode in ("dark", "light"):
        path = OUT / f"header-{mode}.svg"
        path.write_text(build(mode, theme))
        print("wrote", path.relative_to(OUT.parent))
