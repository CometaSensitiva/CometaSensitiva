"""Build 1280x640 project covers (profile README + repository social preview).

Each cover = project text on the left, a real screenshot on the right.
Rendering uses headless Google Chrome:  python3 assets/src/covers.py
Screenshots are read from the sibling repositories in ../ (Developer/github).
"""
import json
import subprocess
import tempfile
import time
from pathlib import Path

SRC = Path(__file__).parent
OUT = SRC.parent / "covers"
REPOS = SRC.parents[2]  # Developer/github
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PROJECTS = [
    {
        "slug": "industrial-manual-ingestion",
        "label": "01 · bachelor's thesis",
        "title": "Industrial Manual Ingestion",
        "line": "Industrial PDF manuals turned into structured, traceable content for RAG systems.",
        "tags": "Python · Docling · local vision model",
        "accent": "#6b4fc0",
        "image": "industrial-manual-ingestion/docs/viewer.png",
    },
    {
        "slug": "audiopro",
        "label": "02 · macOS app",
        "title": "AudioPro",
        "line": "Lecture recordings: merge, compress, transcribe locally, replay with synced text.",
        "tags": "Swift · SwiftUI · FFmpeg · WhisperKit",
        "accent": "#5b5bd6",
        "image": "AudioPro/docs/screenshots/audio-merge-preview.png",
    },
    {
        "slug": "career-day",
        "label": "03 · web app",
        "title": "Career Day UniBo 2026",
        "line": "Filter 174 companies, save favourites and plan a route on the stand map.",
        "tags": "JavaScript · Firebase · Python",
        "accent": "#9f1d20",
        "image": "Career-Day-UniBo-2026/docs/screenshots/dashboard-overview.png",
    },
    {
        "slug": "ferrari-optimization",
        "label": "04 · operations research",
        "title": "Ferrari Distribution Network",
        "line": "Integer-programming model of a two-stage network: one plant, four hubs, 15 destinations.",
        "tags": "Python · Pyomo · Erasmus, Madrid",
        "accent": "#b3261e",
        "image": "ferrari-distribution-optimization/docs/ferrari_logistics.svg",
        "frame": "ferrari.ipynb",
        "code_from": "ferrari-distribution-optimization/ferrari.ipynb",
    },
]

TEMPLATE = """<!doctype html><meta charset="utf-8">
<style>
  * {{ margin: 0; box-sizing: border-box; }}
  body {{ width: 1280px; height: 640px; overflow: hidden; background: #fcfcfd;
         font-family: {font_sans}; color: #1c1d2c; position: relative; }}
  .text {{ position: absolute; left: 72px; top: 0; bottom: 0; width: 430px;
          display: flex; flex-direction: column; justify-content: center; gap: 22px; }}
  .label {{ font: 500 17px {font_mono}; color: {accent}; letter-spacing: .02em; }}
  h1 {{ font-size: 50px; line-height: 1.05; font-weight: 700; letter-spacing: -.02em; }}
  p {{ font-size: 22px; line-height: 1.4; color: #4b4c5c; }}
  .tags {{ font: 16px {font_mono}; color: #676877; }}
  .bar {{ width: 56px; height: 5px; border-radius: 3px; background: {accent}; }}
  .sign {{ position: absolute; left: 72px; bottom: 34px; font: 15px {font_mono}; color: #9a9aab; }}
  .sign b {{ color: #3452d1; font-weight: 400; }}
  .shot {{ position: absolute; left: 540px; top: 64px; width: 860px; }}
  .shot img {{ width: 100%; display: block; }}
  .frame {{ position: absolute; left: 556px; top: 84px; width: 820px; height: 620px; background: #fff;
           border-radius: 14px; border: 1px solid #d9d8e1;
           box-shadow: 0 24px 60px rgba(28,29,44,.22), 0 4px 14px rgba(28,29,44,.10); overflow: hidden; }}
  .frame .tb {{ height: 40px; background: #f6f6f9; border-bottom: 1px solid #ebebf0; display: flex;
               align-items: center; gap: 8px; padding-left: 16px; font: 13px {font_mono}; color: #9a9aab; }}
  .frame .tb i {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; }}
  .frame img {{ width: 100%; padding: 30px 28px 10px; }}
  .frame.fit {{ width: 664px; height: auto; top: 110px; bottom: auto; }}
  pre {{ margin: 0 28px 26px; padding: 18px 20px; background: #f6f6f9; border-radius: 10px;
        font: 13px/1.7 {font_mono}; color: #1c1d2c; white-space: pre; overflow: hidden; }}
  pre .k {{ color: {accent}; }}
</style>
<div class="text">
  <div class="bar"></div>
  <div class="label">{label}</div>
  <h1>{title}</h1>
  <p>{line}</p>
  <div class="tags">{tags}</div>
</div>
<div class="sign"><b>~</b> $ github.com/CometaSensitiva</div>
{visual}
"""

FRAME = """<div class="frame{extra}"><div class="tb"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i>
<i style="background:#28c840"></i><span style="margin-left:10px">{name}</span></div><img src="{src}">{code}</div>"""


def notebook_model_lines(path):
    """Real Pyomo lines from the submitted notebook: variables, objective, constraints."""
    import html
    nb = json.loads(path.read_text())
    src = "".join(nb["cells"][1]["source"]).splitlines()
    keep = [l.strip().split("  #")[0] for l in src
            if any(k in l for k in ("= Var(", "= Objective(", "= Constraint("))]
    rows = []
    for l in keep[:9]:
        name, _, rest = l.partition(" = ")
        rows.append(f'{html.escape(name)} = <span class="k">{html.escape(rest.split("(")[0])}</span>'
                    f'({html.escape(rest.partition("(")[2])}')
    return "<pre>" + "\n".join(rows) + "</pre>"


def render(html_path, png_path):
    with tempfile.TemporaryDirectory() as profile:
        proc = subprocess.Popen(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
             f"--user-data-dir={profile}", "--window-size=1280,640", f"--screenshot={png_path}",
             html_path.as_uri()],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(120):  # Chrome may not exit on its own after writing the file
            if png_path.exists() and png_path.stat().st_size > 0 and proc.poll() is None:
                time.sleep(1)
                break
            if proc.poll() is not None:
                break
            time.sleep(0.5)
        proc.kill()


def main():
    theme = json.loads((SRC / "theme.json").read_text())
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for p in PROJECTS:
            image = (REPOS / p["image"]).resolve()
            if "frame" in p:
                code = notebook_model_lines(REPOS / p["code_from"]) if "code_from" in p else ""
                visual = FRAME.format(name=p["frame"], src=image.as_uri(), code=code,
                                      extra=" fit" if code else "")
            else:
                visual = f'<div class="shot"><img src="{image.as_uri()}"></div>'
            html = Path(tmp) / f"{p['slug']}.html"
            html.write_text(TEMPLATE.format(visual=visual, font_sans=theme["font_sans"],
                                            font_mono=theme["font_mono"], **p))
            png = OUT / f"{p['slug']}.png"
            png.unlink(missing_ok=True)
            render(html, png)
            print("wrote", png.relative_to(SRC.parents[1]))


if __name__ == "__main__":
    main()
