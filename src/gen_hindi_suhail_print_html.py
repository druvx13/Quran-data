#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate print-ready A5 HTML for Hindi Suhail translation.

Run from repository root:
    python3 src/gen_hindi_suhail_print_html.py
"""

import html
import os
import re

IN_FILE = "output/quran_hindi_suhail.txt"
OUT_FILE = "output/hindi_suhail_print.html"


def esc(s):
    return html.escape(s, quote=True)


def main():
    if not os.path.exists(IN_FILE):
        raise FileNotFoundError(IN_FILE)

    with open(IN_FILE, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f]

    body = []
    started = False

    for ln in lines:
        line = ln.strip()
        if not line:
            continue

        m_surah = re.match(r"^Surah\s+(\d+):\s*(.+)$", line)
        if m_surah:
            started = True
            sn = int(m_surah.group(1))
            body.append(
                "<section class='surah'><h2>सूरह %03d: %s</h2>" % (sn, esc(m_surah.group(2)))
            )
            continue

        if re.match(r"^-{5,}$", line):
            continue

        m_ayah = re.match(r"^\[(\d+):(\d+)\]\s*(.*)$", line)
        if m_ayah:
            started = True
            s = int(m_ayah.group(1))
            a = int(m_ayah.group(2))
            txt = esc(m_ayah.group(3))
            body.append(
                "<article class='ayah'><div class='ref'>[%d:%d]</div><p class='txt'>%s</p></article>"
                % (s, a, txt)
            )
            continue

        if not started:
            continue
        body.append("<p class='meta'>%s</p>" % esc(line))

    html_body = []
    open_section = False
    for chunk in body:
        if chunk.startswith("<section"):
            if open_section:
                html_body.append("</section>")
            open_section = True
        html_body.append(chunk)
    if open_section:
        html_body.append("</section>")

    out = """<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Hindi Suhail (Print A5)</title>
  <style>
    @font-face{
      font-family:'TiroDevaHindi';
      src:url('../fonts/TiroDevaHindi-Regular.ttf') format('truetype');
      font-weight:400;
      font-style:normal;
      font-display:swap;
    }
    :root{--page-w:148mm}
    *{box-sizing:border-box}
    body{
      margin:0 auto;
      padding:12mm 12mm 14mm;
      max-width:var(--page-w);
      color:#111;
      background:#fff;
      font-family:'TiroDevaHindi','Noto Serif Devanagari','Nirmala UI','Mangal',serif;
      font-size:11.4pt;
      line-height:1.55;
      text-wrap:pretty;
    }
    h1{margin:0 0 4mm;font-size:17pt}
    h2{
      margin:8mm 0 3mm;
      font-size:13pt;
      border-bottom:1px solid #999;
      padding-bottom:1.5mm;
      page-break-after:avoid;
    }
    .meta{margin:0 0 2.8mm}
    .ayah{
      margin:0 0 2.8mm;
      padding:0 0 2mm;
      border-bottom:1px dotted #d0d0d0;
      page-break-inside:avoid;
      break-inside:avoid;
    }
    .ref{
      font-size:9.3pt;
      font-weight:700;
      color:#333;
      margin-bottom:0.8mm;
      letter-spacing:.15px;
    }
    .txt{margin:0;text-align:justify}
    .print-page-number{display:none}
    @media print{
      @page{
        size:A5;
        margin:11mm 11mm 13mm;
      }
      html,body{background:#fff}
      body{
        margin:0;
        padding:0;
        max-width:none;
        font-size:11pt;
        line-height:1.5;
      }
      h1,h2,.ayah{break-inside:avoid;page-break-inside:avoid}
      section.surah{break-before:page}
      section.surah:first-of-type{break-before:auto}
      .print-page-number{
        display:block;
        position:fixed;
        left:0;
        right:0;
        bottom:4mm;
        text-align:center;
        font-size:9pt;
        color:#444;
      }
      .print-page-number::after{content:counter(page)}
    }
  </style>
</head>
<body>
  <h1>कुरआन हिंदी अनुवाद (सुहैल)</h1>
  __BODY__
  <div class="print-page-number"></div>
</body>
</html>
"""

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(out.replace("__BODY__", "\n  ".join(html_body)))

    print("Written: %s" % OUT_FILE)


if __name__ == "__main__":
    main()
