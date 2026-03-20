#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate print-ready HTML for Hindi Mokhtasar translation.

Run from repository root:
    python3 src/gen_hindi_mokhtasar_print_html.py
"""

import html
import os
import re

IN_FILE = "output/quran_hindi_mokhtasar.txt"
OUT_FILE = "output/hindi_mokhtasar_print.html"


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

    # Ensure any open surah sections are balanced
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
  <title>Hindi Mokhtasar (Print)</title>
  <style>
    @font-face{
      font-family:'TiroDevaHindi';
      src:url('../fonts/TiroDevaHindi-Regular.ttf') format('truetype');
      font-weight:400;
      font-style:normal;
      font-display:swap;
    }
    :root{--page-w:210mm}
    *{box-sizing:border-box}
    body{
      margin:0 auto;
      padding:16mm 14mm;
      max-width:var(--page-w);
      color:#111;
      background:#fff;
      font-family:'TiroDevaHindi','Noto Serif Devanagari','Nirmala UI','Mangal',serif;
      font-size:13.5pt;
      line-height:1.6;
    }
    h1{margin:0 0 4mm;font-size:22pt}
    h2{
      margin:10mm 0 4mm;
      font-size:16pt;
      border-bottom:1px solid #999;
      padding-bottom:2mm;
      page-break-after:avoid;
    }
    .meta{margin:0 0 3mm}
    .ayah{
      margin:0 0 3.2mm;
      padding:0 0 2.4mm;
      border-bottom:1px dotted #d0d0d0;
      page-break-inside:avoid;
      break-inside:avoid;
    }
    .ref{
      font-size:10.5pt;
      font-weight:700;
      color:#333;
      margin-bottom:1mm;
      letter-spacing:.2px;
    }
    .txt{margin:0;text-align:justify}
    @media print{
      @page{size:A4;margin:12mm}
      html,body{background:#fff}
      body{
        margin:0;
        padding:0;
        max-width:none;
        font-size:12.5pt;
        line-height:1.55;
      }
      h1,h2,.ayah{break-inside:avoid;page-break-inside:avoid}
      section.surah{break-before:page}
      section.surah:first-of-type{break-before:auto}
    }
  </style>
</head>
<body>
  <h1>कुरआन हिंदी तफ़्सीर (अल-मुख़्तसर)</h1>
  __BODY__
</body>
</html>
"""

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(out.replace("__BODY__", "\n  ".join(html_body)))

    print("Written: %s" % OUT_FILE)


if __name__ == "__main__":
    main()
