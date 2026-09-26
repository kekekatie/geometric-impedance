#!/usr/bin/env python3
"""make_pdf.py -- MANUSCRIPT.md -> paper.html -> paper.pdf (headless Chromium). Needs `pip install markdown`."""
import os, subprocess, markdown

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
CSS = """
@page { size: A4; margin: 20mm 18mm; }
body { font-family: 'DejaVu Serif', Georgia, serif; font-size: 10.5pt; line-height: 1.45; color: #111; }
h1 { font-size: 17pt; line-height: 1.25; margin-bottom: 4pt; }
h2 { font-size: 13pt; margin-top: 16pt; border-bottom: 1px solid #ccc; padding-bottom: 2pt; }
h3 { font-size: 11.5pt; margin-top: 12pt; }
table { border-collapse: collapse; margin: 8pt 0; font-size: 9pt; width: 100%; }
th, td { border: 1px solid #bbb; padding: 3pt 5pt; vertical-align: top; }
th { background: #f0f0f0; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.8pt; background: #f5f5f5; padding: 0 2px; }
img { max-width: 100%; display: block; margin: 8pt auto 2pt; page-break-inside: avoid; }
hr { border: none; border-top: 1px solid #ccc; }
p, li { text-align: justify; }
"""


def main():
    md = open(os.path.join(HERE, "MANUSCRIPT.md")).read()
    body = markdown.markdown(md, extensions=["tables"])
    html = f"<!doctype html><html><head><meta charset='utf-8'><title>What should a memory keep?</title><style>{CSS}</style></head><body>{body}</body></html>"
    hp = os.path.join(HERE, "paper.html"); open(hp, "w").write(html)
    out = os.path.join(HERE, "paper.pdf")
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}", "file://" + hp], check=True, capture_output=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
