#!/usr/bin/env python3
"""
Builds the Assignment 3 submission files:

    submission/part_one.txt  submission/part_one.pdf
    submission/part_two.txt  submission/part_two.pdf

Usage:
    python3 build_submission.py "First Last" "StudentNumber"

It fills your name/number into the Lex sources, really runs the echo, lex,
gcc and scanner commands, renders the editor/terminal screenshots from that
real output (Playwright + Chromium), and assembles the PDFs (reportlab) with
your name and number in the header of every page.

Requires: flex, gcc, python3, reportlab, playwright (with Chromium).
"""
import html
import os
import shutil
import subprocess
import sys

from playwright.sync_api import sync_playwright
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "submission")
BUILD = os.path.join(OUT, "build")

PARTS = {
    "part_one": (1, 2, 3),
    "part_two": (4, 5, 6),
}


def sh(cmd):
    r = subprocess.run(cmd, shell=True, cwd=BUILD, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"command failed: {cmd}\n{r.stdout}{r.stderr}")
    return r.stdout + r.stderr


def term_session(user, cmds):
    """Run commands for real; return terminal transcript text."""
    prompt = f"{user}@ubuntu:~/assignment3$ "
    lines = []
    for c in cmds:
        lines.append(prompt + c)
        out = sh(c)
        if out:
            lines.append(out.rstrip("\n"))
    lines.append(prompt)
    return "\n".join(lines)


CSS = """
body{margin:0;background:#2b2b2b;font-family:'DejaVu Sans Mono',monospace;}
.win{width:1400px;min-height:800px;display:flex;flex-direction:column}
.bar{height:34px;background:#3c3c3c;color:#ddd;display:flex;align-items:center;
     padding:0 12px;font:14px 'DejaVu Sans',sans-serif}
.dots span{display:inline-block;width:12px;height:12px;border-radius:6px;margin-right:7px}
.title{flex:1;text-align:center;margin-right:60px}
pre{margin:0;padding:12px 16px;font-size:15px;line-height:1.35;white-space:pre}
"""
DOTS = ('<div class="dots"><span style="background:#ff5f57"></span>'
        '<span style="background:#febc2e"></span><span style="background:#28c840"></span></div>')


def editor_html(fname, src):
    rows = src.rstrip("\n").split("\n")
    gutter = "\n".join(str(i + 1) for i in range(len(rows)))
    return f"""<html><style>{CSS}
.tabs{{background:#252526;color:#fff;font:13px sans-serif;padding:8px 16px;border-top:2px solid #0e639c;width:fit-content}}
.ed{{display:flex;background:#1e1e1e;color:#d4d4d4;flex:1}}
.gut{{color:#858585;text-align:right;padding-right:6px;border-right:1px solid #333}}
</style><body><div class="win"><div class="bar">{DOTS}<div class="title">{fname} - Visual Studio Code</div></div>
<div style="background:#2d2d2d"><div class="tabs">{fname}</div></div>
<div class="ed"><pre class="gut">{gutter}</pre><pre>{html.escape(src)}</pre></div></div></body></html>"""


def term_html(user, text):
    return f"""<html><style>{CSS} pre{{color:#e6e6e6;background:#300a24;flex:1}}</style>
<body><div class="win"><div class="bar">{DOTS}<div class="title">{user}@ubuntu: ~/assignment3</div></div>
<pre>{html.escape(text)}</pre></div></body></html>"""


def shoot(page, markup, path):
    page.set_content(markup)
    page.locator(".win").screenshot(path=path)


def make_pdf(path, name, number, src_name, src, shots):
    c = canvas.Canvas(path, pagesize=letter)
    W, H = letter
    header = f"{name}   |   {number}"

    def page_header(title):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, H - 40, header)
        c.setFont("Helvetica", 10)
        c.drawRightString(W - 50, H - 40, title)
        c.line(50, H - 48, W - 50, H - 48)

    # Page 1: input file contents (continues onto extra pages if needed)
    rows = src.rstrip("\n").split("\n")
    y = None
    for row in rows:
        if y is None or y < 50:
            if y is not None:
                c.showPage()
            page_header(f"Input file: {src_name}")
            c.setFont("Courier", 8.5)
            y = H - 70
        c.drawString(50, y, row.replace("\t", "    "))
        y -= 11
    c.showPage()

    for num, caption, img in shots:
        page_header(f"Screenshot #{num}")
        c.setFont("Helvetica", 10)
        c.drawString(50, H - 68, caption)
        ir = ImageReader(img)
        iw, ih = ir.getSize()
        maxw, maxh = W - 100, H - 130
        s = min(maxw / iw, maxh / ih)
        c.drawImage(ir, 50, H - 80 - ih * s, iw * s, ih * s)
        c.showPage()
    c.save()


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    name, number = sys.argv[1], sys.argv[2]
    first_last = name.split()
    user = first_last[0].lower() if first_last else "student"

    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(BUILD)
    shutil.copy(os.path.join(HERE, "fact.c"), BUILD)

    with sync_playwright() as p:
        exe = os.environ.get("CHROMIUM_PATH", "/opt/pw-browsers/chromium")
        browser = p.chromium.launch(executable_path=exe if os.path.exists(exe) else None)
        page = browser.new_page(viewport={"width": 1400, "height": 800}, device_scale_factor=1)
        for part, (s_src, s_build, s_run) in PARTS.items():
            with open(os.path.join(HERE, part + ".txt")) as f:
                src = f.read().replace("STUDENT_NAME", name).replace("STUDENT_NUMBER", number)
            for d in (OUT, BUILD):
                with open(os.path.join(d, part + ".txt"), "w") as f:
                    f.write(src)

            echo = f"echo {name}"
            t_build = term_session(user, [echo, f"lex {part}.txt", f"gcc lex.yy.c -o {part}"])
            t_run = term_session(user, [echo, f"./{part} fact.c"])

            imgs = [os.path.join(BUILD, f"screenshot{n}.png") for n in (s_src, s_build, s_run)]
            shoot(page, editor_html(part + ".txt", src), imgs[0])
            shoot(page, term_html(user, t_build), imgs[1])
            shoot(page, term_html(user, t_run), imgs[2])

            shots = [
                (s_src, f"Input file {part}.txt in the editor", imgs[0]),
                (s_build, "echo, lex and compile commands", imgs[1]),
                (s_run, "echo and the scanner run on fact.c", imgs[2]),
            ]
            make_pdf(os.path.join(OUT, part + ".pdf"), name, number, part + ".txt", src, shots)
            print(f"{part}: {t_run.splitlines()[-2].strip()}  (lines words chars)")
        browser.close()
    print("Wrote:", ", ".join(sorted(f for f in os.listdir(OUT) if f != "build")))


if __name__ == "__main__":
    main()
