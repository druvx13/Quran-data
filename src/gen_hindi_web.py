#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a Hindi-only Qur'an website with audio and Unicode transliteration.

Outputs to: hindi-web/

Usage:
    python3 src/gen_hindi_web.py

The generated site keeps only Hindi translations (Farooq, Suhail, Mokhtasar,
Omari), the Arabic text, Unicode transliteration, and per-ayah audio players.
All UI strings are in Hindi.
"""

import html
import os
import re
from typing import Dict, Tuple

OUT_DIR = "hindi-web"

# ---------------------------------------------------------------------------
# Surah metadata (copied from gendocshtml.py to stay in sync)
# ---------------------------------------------------------------------------
SURA_SIZE = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52,
             99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88, 69,
             60, 34, 30, 73, 54, 45, 83, 182, 88, 75, 85, 54, 53, 89, 59, 37,
             35, 38, 29, 18, 45, 60, 49, 62, 55, 78, 96, 29, 22, 24, 13, 14,
             11, 11, 18, 12, 12, 30, 52, 52, 44, 28, 28, 20, 56, 40, 31, 50,
             40, 46, 42, 29, 19, 36, 25, 22, 17, 19, 26, 30, 20, 15, 21, 11,
             8, 8, 19, 5, 8, 8, 11, 11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]

SURA_NAME = [
    "Al-Fatihah (The Opening)", "Al-Baqarah (The Cow)",
    "Al-'Imran (The Family of Amran)", "An-Nisa' (The Women)",
    "Al-Ma'idah (The Food)", "Al-An'am (The Cattle)",
    "Al-A'raf (The Elevated Places)", "Al-Anfal (Voluntary Gifts)",
    "Al-Bara'at / At-Taubah(The Immunity)", "Yunus (Jonah)", "Hud (Hud)",
    "Yusuf (Joseph)", "Ar-Ra'd (The Thunder)", "Ibrahim (Abraham)",
    "Al-Hijr (The Rock)", "An-Nahl (The Bee)", "Bani Isra'il (The Israelites)",
    "Al-Kahf (The Cave)", "Maryam (Mary)", "Ta Ha (Ta Ha)",
    "Al-Anbiya' (The Prophets)", "Al-Hajj (The Pilgrimage)",
    "Al-Mu'minun (The Believers)", "An-Nur (The Light)",
    "Al-Furqan (The Discrimination)", "Ash-Shu'ara' (The Poets)",
    "An-Naml (The Naml)", "Al-Qasas (The Narrative)",
    "Al-'Ankabut (The Spider)", "Ar-Rum (The Romans)", "Luqman (Luqman)",
    "As-Sajdah (The Adoration)", "Al-Ahzab (The Allies)",
    "Al-Saba' (The Saba')", "Al-Fatir (The Originator)", "Ya Sin (Ya Sin)",
    "As-Saffat (Those Ranging in Ranks)", "Sad (Sad)",
    "Az-Zumar (The Companies)", "Al-Mu'min (The Believer)", "Ha Mim (Ha Mim)",
    "Ash-Shura (Counsel)", "Az-Zukhruf (Gold)", "Ad-Dukhan (The Drought)",
    "Al-Jathiyah (The Kneeling)", "Al-Ahqaf (The Sandhills)",
    "Muhammad (Muhammad)", "Al-Fath (The Victory)",
    "Al-Hujurat (The Apartments)", "Qaf (Qaf)",
    "Ad-Dhariyat (The Scatterers)", "At-Tur (The Mountain)",
    "An-Najm (The Star)", "Al-Qamar (The Moon)",
    "Ar-Rahman (The Beneficent)", "Al-Waqi'ah (The Event)",
    "Al-Hadid (Iron)", "Al-Mujadilah (The Pleading Woman)",
    "Al-Hashr (The Banishment)", "Al-Mumtahanah (The Woman who is Examined)",
    "As-Saff (The Ranks)", "Al-Jumu'ah (The Congregation)",
    "Al-Munafiqun (The Hypocrites)", "At-Taghabun (The Manifestation of Losses)",
    "At-Talaq (Divorce)", "At-Tahrim (The Prohibition)",
    "Al-Mulk (The Kingdom)", "Al-Qalam (The Pen)", "Al-Haqqah (The Sure Truth)",
    "Al-Ma'arij (The Ways of Ascent)", "Nuh (Noah)", "Al-Jinn (The Jinn)",
    "Al-Muzzammil (The One Covering Himself)",
    "Al-Muddaththir (The One Wrapping Himself Up)",
    "Al-Qiyamah (The Resurrection)", "Al-Insan (The Man)",
    "Al-Mursalat (Those Sent Forth)", "An-Naba' (The Announcement)",
    "An-Nazi'at (Those Who Yearn)", "'Abasa (He Frowned)",
    "At-Takwir (The Folding Up)", "Al-Infitar (The Cleaving)",
    "At-Tatfif (Default in Duty)", "Al-Inshiqaq (The Bursting Asunder)",
    "Al-Buruj (The Stars)", "At-Tariq (The Comer by Night)",
    "Al-A'la (The Most High)", "Al-Ghashiyah (The Overwhelming Event)",
    "Al-Fajr (The Daybreak)", "Al-Balad (The City)", "Ash-Shams (The Sun)",
    "Al-Lail (The Night)", "Ad-Duha (The Brightness of the Day)",
    "Al-Inshirah (The Expansion)", "At-Tin (The Fig)", "Al-'Alaq (The Clot)",
    "Al-Qadr (The Majesty)", "Al-Bayyinah (The Clear Evidence)",
    "Al-Zilzal (The Shaking)", "Al-'Adiyat (The Assaulters)",
    "Al-Qari'ah (The Calamity)", "At-Takathur (The Abundance of Wealth)",
    "Al-'Asr (The Time)", "Al-Humazah (The Slanderer)", "Al-Fil (The Elephant)",
    "Al-Quraish (The Quraish)", "Al-Ma'un (Acts of Kindness)",
    "Al-Kauthar (The Abundance of Good)", "Al-Kafirun (The Disbelievers)",
    "An-Nasr (The Help)", "Al-Lahab (The Flame)", "Al-Ikhlas (The Unity)",
    "Al-Falaq (The Dawn)", "An-Nas (The Men)",
]

# Revelation metadata: (revelation_order, 'M'=Meccan/'D'=Medinan)
SURAH_REV = [
    (5, 'M'), (87, 'D'), (89, 'D'), (92, 'D'), (112, 'D'),
    (55, 'M'), (39, 'M'), (88, 'D'), (113, 'D'), (51, 'M'),
    (52, 'M'), (53, 'M'), (96, 'D'), (72, 'M'), (54, 'M'),
    (70, 'M'), (50, 'M'), (69, 'M'), (44, 'M'), (45, 'M'),
    (73, 'M'), (103, 'D'), (74, 'M'), (102, 'D'), (42, 'M'),
    (47, 'M'), (48, 'M'), (49, 'M'), (85, 'M'), (84, 'M'),
    (57, 'M'), (75, 'M'), (90, 'D'), (58, 'M'), (43, 'M'),
    (41, 'M'), (56, 'M'), (38, 'M'), (59, 'M'), (60, 'M'),
    (61, 'M'), (62, 'M'), (63, 'M'), (64, 'M'), (65, 'M'),
    (66, 'M'), (95, 'D'), (111, 'D'), (106, 'D'), (34, 'M'),
    (67, 'M'), (76, 'M'), (23, 'M'), (37, 'M'), (97, 'D'),
    (46, 'M'), (94, 'D'), (105, 'D'), (101, 'D'), (91, 'D'),
    (109, 'D'), (110, 'D'), (104, 'D'), (108, 'D'), (99, 'D'),
    (107, 'D'), (77, 'M'), (2, 'M'), (78, 'M'), (79, 'M'),
    (71, 'M'), (40, 'M'), (3, 'M'), (4, 'M'), (31, 'M'),
    (98, 'D'), (33, 'M'), (80, 'M'), (81, 'M'), (24, 'M'),
    (7, 'M'), (82, 'M'), (86, 'M'), (83, 'M'), (27, 'M'),
    (36, 'M'), (8, 'M'), (68, 'M'), (10, 'M'), (35, 'M'),
    (26, 'M'), (9, 'M'), (11, 'M'), (12, 'M'), (28, 'M'),
    (1, 'M'), (25, 'M'), (100, 'D'), (93, 'D'), (14, 'M'),
    (30, 'M'), (16, 'M'), (13, 'M'), (32, 'M'), (19, 'M'),
    (29, 'M'), (17, 'M'), (15, 'M'), (18, 'M'), (114, 'D'),
    (6, 'M'), (22, 'M'), (20, 'M'), (21, 'M'),
]

JUZ_STARTS = {
    (1, 1): 1, (2, 142): 2, (2, 253): 3, (3, 92): 4, (4, 24): 5,
    (4, 148): 6, (5, 82): 7, (6, 111): 8, (7, 88): 9, (8, 41): 10,
    (9, 93): 11, (11, 6): 12, (12, 53): 13, (15, 1): 14, (17, 1): 15,
    (18, 75): 16, (21, 1): 17, (23, 1): 18, (25, 21): 19, (27, 56): 20,
    (29, 46): 21, (33, 31): 22, (36, 28): 23, (39, 32): 24, (41, 47): 25,
    (46, 1): 26, (51, 31): 27, (58, 1): 28, (67, 1): 29, (78, 1): 30,
}

def _build_juz_map():
    current = 1
    out = {}
    for sura_idx, size in enumerate(SURA_SIZE, 1):
        for ayah in range(1, size + 1):
            current = JUZ_STARTS.get((sura_idx, ayah), current)
            out.setdefault(sura_idx, set()).add(current)
    return {k: sorted(v) for k, v in out.items()}

JUZ_MAP = _build_juz_map()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def surah_juz_span(sura_idx: int) -> str:
    """Return juz coverage for the surah, e.g. '1' or '1–2'."""
    juz_list = JUZ_MAP[sura_idx]
    if len(juz_list) == 1:
        return str(juz_list[0])
    return f"{juz_list[0]}\u2013{juz_list[-1]}"


def load_bracket_file(path: str) -> Dict[int, Dict[int, str]]:
    """Parse [sura:ayah] formatted files into a nested dict."""
    data: Dict[int, Dict[int, str]] = {}
    pat = re.compile(r"\[(\d+):(\d+)\]\s+(.*)")
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            m = pat.match(line)
            if not m:
                continue
            s, a, text = int(m.group(1)), int(m.group(2)), m.group(3).strip()
            data.setdefault(s, {})[a] = text
    return data


def get_line(data: Dict[int, Dict[int, str]], sura: int, ayah: int) -> str:
    return data.get(sura, {}).get(ayah, "\u2014")


def ensure_out_dir() -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    return OUT_DIR


def write_style(out_dir: str) -> None:
    css = """@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600&family=Noto+Sans+Devanagari:wght@400;600&family=Noto+Naskh+Arabic:wght@400;600&display=swap');
:root{
  --bg:#f9fafc;
  --card:#ffffff;
  --ink:#1b2a3a;
  --muted:#4f5d73;
  --border:#e2e8f0;
  --accent:#0f6cbf;
  --accent-2:#f4b400;
}
*{box-sizing:border-box}
body{
  margin:0;
  font-family:'Noto Sans Devanagari','Noto Sans',system-ui,-apple-system,sans-serif;
  background:var(--bg);
  color:var(--ink);
  line-height:1.6;
}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
header{
  position:sticky;top:0;z-index:10;
  background:rgba(255,255,255,0.9);
  backdrop-filter:blur(8px);
  border-bottom:1px solid var(--border);
  padding:10px 16px;
  display:flex;
  align-items:center;
  gap:12px;
}
header .title{font-weight:700;font-size:1.1rem;color:var(--ink)}
header select{
  padding:6px 10px;
  border:1px solid var(--border);
  border-radius:6px;
  font-size:.95rem;
  background:#fff;
}
.page{max-width:1080px;margin:0 auto;padding:20px 16px 32px;}
.hero{
  background:linear-gradient(135deg,#e8f1fc,#f7f3ff);
  border:1px solid var(--border);
  border-radius:12px;
  padding:20px;
  margin-bottom:18px;
  box-shadow:0 2px 10px rgba(0,0,0,0.03);
}
.hero h1{margin:0 0 8px;font-size:1.6rem;}
.hero p{margin:4px 0;color:var(--muted);}
.surah-grid{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  gap:12px;
  margin-top:14px;
}
.s-card{
  display:block;
  background:var(--card);
  border:1px solid var(--border);
  border-radius:10px;
  padding:14px;
  box-shadow:0 2px 6px rgba(0,0,0,0.02);
  transition:transform .1s ease, box-shadow .1s ease;
}
.s-card:hover{transform:translateY(-2px);box-shadow:0 6px 14px rgba(0,0,0,0.06);}
.s-card .num{font-weight:700;color:var(--accent);}
.s-card .name{margin:6px 0;font-weight:600;}
.s-card .meta{color:var(--muted);font-size:.9rem;}
.meta-row{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 14px;}
.pill{
  padding:4px 10px;
  border-radius:999px;
  font-size:.9rem;
  background:#edf2ff;
  color:#1f3c7a;
  border:1px solid #d6e0ff;
}
.pill.meccan{background:#fff4e5;color:#8a4b00;border-color:#ffd8a8;}
.pill.medinan{background:#e9f7ef;color:#0f5132;border-color:#c7eed8;}
.pill.juz{background:#e3f2fd;color:#0d47a1;border-color:#bbdefb;}
.pill.count{background:#f0f4f8;color:#374151;border-color:#e2e8f0;}
.ayah{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:12px;
  padding:14px;
  margin:0 0 14px;
  box-shadow:0 2px 6px rgba(0,0,0,0.02);
}
.ayah-header{
  display:flex;
  align-items:center;
  gap:12px;
  flex-wrap:wrap;
  margin-bottom:10px;
}
.ayah-num{
  background:var(--accent);
  color:#fff;
  padding:6px 10px;
  border-radius:8px;
  font-weight:700;
}
audio{width:260px;max-width:100%;}
.line{margin:6px 0;}
.line .label{font-weight:600;color:var(--muted);margin-right:6px;}
.arabic{
  font-family:'Noto Naskh Arabic','Scheherazade New','Amiri',serif;
  font-size:1.15rem;
  direction:rtl;
  text-align:right;
}
.translit{color:#1f2937;font-weight:600;}
.t-hi{color:#0f5132;}
.t-hi.alt{color:#7c2d12;}
.t-hi.tafseer{color:#0f3d3e;}
.t-hi.omari{color:#5b21b6;}
.footer{
  margin-top:18px;
  color:var(--muted);
  font-size:.95rem;
  text-align:center;
}
.sources{
  background:#f8fafc;
  border:1px dashed var(--border);
  padding:10px 12px;
  border-radius:8px;
  margin-top:10px;
  font-size:.92rem;
}
@media (prefers-color-scheme: dark){
  :root{--bg:#0f172a;--card:#111827;--ink:#e5e7eb;--muted:#9ca3af;--border:#1f2937;}
  header{background:rgba(17,24,39,0.9);}
  .hero{background:linear-gradient(135deg,#111827,#0f172a);border-color:var(--border);}
  .s-card{border-color:var(--border);}
  .pill{border-color:var(--border);}
  .sources{background:#0b1224;}
}
"""
    with open(os.path.join(out_dir, "style.css"), "w", encoding="utf-8") as f:
        f.write(css)


def make_surah_select(current: int) -> str:
    opts = ["<option value=''>सूरा चुनें\u2026</option>"]
    for idx, name in enumerate(SURA_NAME, 1):
        sel = " selected" if idx == current else ""
        opts.append(
            f"<option value='{idx:03d}.html'{sel}>{idx}. {html.escape(name)}</option>"
        )
    return (
        "<select aria-label='सूरा बदलें' onchange=\"if(this.value){location.href=this.value;}\">"
        f"{''.join(opts)}</select>"
    )


def make_meta_row(sura_idx: int) -> str:
    rev_order, rev_type = SURAH_REV[sura_idx - 1]
    rev_label = "मक्की" if rev_type == "M" else "मदीनी"
    rev_class = "meccan" if rev_type == "M" else "medinan"
    juz = surah_juz_span(sura_idx)
    size = SURA_SIZE[sura_idx - 1]
    return (
        "<div class='meta-row'>"
        f"<span class='pill {rev_class}'>{rev_label}</span>"
        f"<span class='pill'>प्रकाशन क्रम {rev_order}</span>"
        f"<span class='pill count'>{size} आयतें</span>"
        f"<span class='pill juz'>जुज़ {juz}</span>"
        "</div>"
    )


def make_ayah_block(
    sura: int,
    ayah: int,
    arabic: str,
    translit: str,
    translations: Tuple[Tuple[str, Tuple[str, str]], ...],
) -> str:
    audio_url = f"https://druvx13-quran-audio-alafasy.hf.space/{sura:03d}{ayah:03d}.mp3"
    t_lines = []
    for cls, (label, text) in translations:
        safe_text = html.escape(text)
        t_lines.append(
            f"<div class='line t-hi {cls}'><span class='label'>{label}:</span>{safe_text}</div>"
        )
    return f"""
    <section class="ayah" id="ayah-{ayah}">
      <div class="ayah-header">
        <div class="ayah-num">आयत {ayah}</div>
        <audio controls preload="none" src="{audio_url}" aria-label="सूरा {sura}, आयत {ayah} का ऑडियो"></audio>
      </div>
      <div class="line arabic" lang="ar" dir="rtl">{html.escape(arabic)}</div>
      <div class="line translit"><span class="label">लिप्यंतरण (यूनिकोड):</span>{html.escape(translit)}</div>
      {''.join(t_lines)}
    </section>
    """


def write_surah_pages(out_dir: str, data_bundle) -> None:
    arabic, translit, hi_farooq, hi_suhail, hi_mokhtasar, hi_omari = data_bundle
    for sura in range(1, 115):
        size = SURA_SIZE[sura - 1]
        body_parts = []
        for ayah in range(1, size + 1):
            translations = (
                ("", ("हिंदी (फ़ारूक़ खान)", get_line(hi_farooq, sura, ayah))),
                ("alt", ("हिंदी (सूहैल फ़ारूक़ खान)", get_line(hi_suhail, sura, ayah))),
                ("tafseer", ("हिंदी तफ़्सीर (अल-मुख़्तसर)", get_line(hi_mokhtasar, sura, ayah))),
                ("omari", ("हिंदी (अज़ीज़ुल हक़ अल-उमारी)", get_line(hi_omari, sura, ayah))),
            )
            body_parts.append(
                make_ayah_block(
                    sura,
                    ayah,
                    get_line(arabic, sura, ayah),
                    get_line(translit, sura, ayah),
                    translations,
                )
            )
        select_html = make_surah_select(sura)
        nav_prev = f"{sura - 1:03d}.html" if sura > 1 else ""
        nav_next = f"{sura + 1:03d}.html" if sura < 114 else ""
        nav_html = "<div class='meta-row' style='justify-content:space-between'>"
        if nav_prev:
            nav_html += f"<a href='{nav_prev}'>&larr; पिछला सूरा</a>"
        else:
            nav_html += "<span></span>"
        nav_html += f"<a href='index.html'>सूची पर लौटें</a>"
        if nav_next:
            nav_html += f"<a href='{nav_next}'>अगला सूरा &rarr;</a>"
        nav_html += "</div>"

        page_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>सूरा {sura}: {html.escape(SURA_NAME[sura-1])}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <span class="title">क़ुरआन (हिंदी)</span>
    {select_html}
    <a href="index.html">सूची</a>
  </header>
  <main class="page">
    <div class="hero">
      <h1>सूरा {sura}</h1>
      <p>{html.escape(SURA_NAME[sura-1])}</p>
      {make_meta_row(sura)}
      <p style="margin-top:8px;color:#2f3b4c;">केवल हिंदी अनुवाद, यूनिकोड लिप्यंतरण और अल-अफ़ासी की ऑडियो के साथ।</p>
    </div>
    {''.join(body_parts)}
    {nav_html}
    <div class="footer">
      <div>ऑडियो: मिशारी राशिद अल-अफ़ासी &mdash; स्रोत: versebyversequran.com (Hugging Face स्पेस)</div>
      <div class="sources">अनुवाद: फ़ारूक़ / सुहैल फ़ारूक़ खान, अल-मुख़्तसर तफ़्सीर, अज़ीज़ुल हक़ अल-उमारी &mdash; लिप्यंतरण: Quran Unicode Project</div>
      <div><a href="https://github.com/druvx13/Quran-data" rel="noopener noreferrer">GitHub</a></div>
    </div>
  </main>
</body>
</html>"""
        out_path = os.path.join(out_dir, f"{sura:03d}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page_html)
        print(f"लिखा गया: {out_path}")


def write_index(out_dir: str) -> None:
    cards = []
    for idx, name in enumerate(SURA_NAME, 1):
        cards.append(
            f"<a class='s-card' href='{idx:03d}.html'>"
            f"<div class='num'>सूरा {idx}</div>"
            f"<div class='name'>{html.escape(name)}</div>"
            f"<div class='meta'>{SURA_SIZE[idx-1]} आयतें</div>"
            "</a>"
        )
    html_out = f"""<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>क़ुरआन (हिंदी) &mdash; केवल हिंदी अनुवाद</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <span class="title">क़ुरआन (हिंदी)</span>
    {make_surah_select(0)}
  </header>
  <main class="page">
    <div class="hero">
      <h1>हिंदी वेबसाइट</h1>
      <p>केवल हिंदी अनुवादों के साथ क़ुरआन पढ़ें &mdash; हर आयत के लिए ऑडियो और यूनिकोड लिप्यंतरण उपलब्ध।</p>
      <p>अनुवाद: फ़ारूक़, सुहैल फ़ारूक़ खान, अल-मुख़्तसर तफ़्सीर, अज़ीज़ुल हक़ अल-उमारी।</p>
      <p>ऑडियो: मिशारी राशिद अल-अफ़ासी (Hugging Face स्पेस पर होस्टेड)।</p>
    </div>
    <div class="surah-grid">
      {''.join(cards)}
    </div>
    <div class="footer">
      <div class="sources">यह संस्करण केवल हिंदी सामग्री पर केंद्रित है। मूल बहुभाषी साइट के लिए <a href="../docs/index.html">docs/</a> देखें।</div>
      <div><a href="https://github.com/druvx13/Quran-data" rel="noopener noreferrer">GitHub</a></div>
    </div>
  </main>
</body>
</html>"""
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"लिखा गया: {out_path}")


def main():
    out_dir = ensure_out_dir()
    # Load required streams
    arabic = load_bracket_file("output/quran_arabic.txt")
    translit = load_bracket_file("output/quran_translit_unicode.txt")
    hi_farooq = load_bracket_file("output/quran_hindi_farooq.txt")
    hi_suhail = load_bracket_file("output/quran_hindi_suhail.txt")
    hi_mokhtasar = load_bracket_file("output/quran_hindi_mokhtasar.txt")
    hi_omari = load_bracket_file("output/quran_hindi_omari.txt")

    write_style(out_dir)
    write_index(out_dir)
    write_surah_pages(out_dir, (arabic, translit, hi_farooq, hi_suhail, hi_mokhtasar, hi_omari))
    print("पूरा हुआ: hindi-web तैयार है।")


if __name__ == "__main__":
    main()
