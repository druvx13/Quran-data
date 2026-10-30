#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Qur'an reader: static site generator (v2).

Run from the repository root:
    python3 src/gen_docs.py [--root .] [--out docs] [--no-fonts] [--clean]

Inputs   data/ and output/ text files (see CATALOG below)
Outputs  <out>/
           index.html, 001.html ... 114.html, search.html, config.html,
           bookmarks.html, sources.html, license.html, download.html
           assets/style.css, assets/app.js, assets/catalog.js
           data/surah/<id>/<NNN>.js   one small file per edition per surah
           data/search/<id>.js        one file per edition for search

Design notes
  * Surah pages ship only the Arabic text and the default editions. Every other
    edition is loaded on demand from data/surah/..., so pages stay small
    (the old version embedded ~80 hidden rows per verse in every page).
  * Data files are .js (not .json) so the site also works when opened from
    file:// after using the offline download.
  * All text is HTML-escaped. CSS and JS live in shared files, not in each page.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
TOTAL_AYAT = 6236
GITHUB = "https://github.com/druvx13/Quran-data"
AUDIO_URL = "https://druvx13-quran-audio-alafasy.hf.space/{s}{a}.mp3"

SURA_SIZE = (
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52, 99, 128, 111,
    110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83,
    182, 88, 75, 85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55, 78, 96,
    29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52, 44, 28, 28, 20, 56, 40, 31,
    50, 40, 46, 42, 29, 19, 36, 25, 22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5,
    8, 8, 11, 11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6,
)

# (transliterated name, English meaning). Names follow the common scholarly
# spellings; "also known as" forms are noted in the meaning.
SURA_NAMES = (
    ("Al-Fatihah", "The Opening"), ("Al-Baqarah", "The Cow"),
    ("Ali ‘Imran", "The Family of ‘Imran"), ("An-Nisa’", "The Women"),
    ("Al-Ma’idah", "The Table Spread"), ("Al-An‘am", "The Cattle"),
    ("Al-A‘raf", "The Heights"), ("Al-Anfal", "The Spoils of War"),
    ("At-Tawbah", "The Repentance (also Bara’ah)"), ("Yunus", "Jonah"),
    ("Hud", "Hud"), ("Yusuf", "Joseph"), ("Ar-Ra‘d", "The Thunder"),
    ("Ibrahim", "Abraham"), ("Al-Hijr", "The Rocky Tract"), ("An-Nahl", "The Bee"),
    ("Al-Isra’", "The Night Journey (also Bani Isra’il)"), ("Al-Kahf", "The Cave"),
    ("Maryam", "Mary"), ("Ta-Ha", "Ta-Ha"), ("Al-Anbiya’", "The Prophets"),
    ("Al-Hajj", "The Pilgrimage"), ("Al-Mu’minun", "The Believers"),
    ("An-Nur", "The Light"), ("Al-Furqan", "The Criterion"),
    ("Ash-Shu‘ara’", "The Poets"), ("An-Naml", "The Ants"),
    ("Al-Qasas", "The Stories"), ("Al-‘Ankabut", "The Spider"),
    ("Ar-Rum", "The Romans"), ("Luqman", "Luqman"), ("As-Sajdah", "The Prostration"),
    ("Al-Ahzab", "The Combined Forces"), ("Saba’", "Sheba"),
    ("Fatir", "The Originator"), ("Ya-Sin", "Ya-Sin"),
    ("As-Saffat", "Those Ranged in Ranks"), ("Sad", "Sad"),
    ("Az-Zumar", "The Groups"), ("Ghafir", "The Forgiver (also Al-Mu’min)"),
    ("Fussilat", "Explained in Detail (also Ha-Mim Sajdah)"),
    ("Ash-Shura", "Consultation"), ("Az-Zukhruf", "The Ornaments of Gold"),
    ("Ad-Dukhan", "The Smoke"), ("Al-Jathiyah", "The Kneeling Down"),
    ("Al-Ahqaf", "The Wind-Curved Sandhills"), ("Muhammad", "Muhammad"),
    ("Al-Fath", "The Victory"), ("Al-Hujurat", "The Private Apartments"),
    ("Qaf", "Qaf"), ("Adh-Dhariyat", "The Winnowing Winds"), ("At-Tur", "The Mount"),
    ("An-Najm", "The Star"), ("Al-Qamar", "The Moon"),
    ("Ar-Rahman", "The Most Merciful"), ("Al-Waqi‘ah", "The Inevitable Event"),
    ("Al-Hadid", "The Iron"), ("Al-Mujadilah", "She Who Pleads"),
    ("Al-Hashr", "The Gathering"), ("Al-Mumtahanah", "She Who Is Examined"),
    ("As-Saff", "The Ranks"), ("Al-Jumu‘ah", "Friday"),
    ("Al-Munafiqun", "The Hypocrites"), ("At-Taghabun", "Mutual Loss and Gain"),
    ("At-Talaq", "Divorce"), ("At-Tahrim", "Prohibition"), ("Al-Mulk", "Sovereignty"),
    ("Al-Qalam", "The Pen"), ("Al-Haqqah", "The Inevitable Reality"),
    ("Al-Ma‘arij", "The Ways of Ascent"), ("Nuh", "Noah"), ("Al-Jinn", "The Jinn"),
    ("Al-Muzzammil", "The Enwrapped One"), ("Al-Muddaththir", "The Cloaked One"),
    ("Al-Qiyamah", "The Resurrection"), ("Al-Insan", "The Human"),
    ("Al-Mursalat", "Those Sent Forth"), ("An-Naba’", "The Great News"),
    ("An-Nazi‘at", "Those Who Pull Out"), ("‘Abasa", "He Frowned"),
    ("At-Takwir", "The Folding Up"), ("Al-Infitar", "The Cleaving Apart"),
    ("Al-Mutaffifin", "The Defrauders"), ("Al-Inshiqaq", "The Splitting Open"),
    ("Al-Buruj", "The Constellations"), ("At-Tariq", "The Night Visitor"),
    ("Al-A‘la", "The Most High"), ("Al-Ghashiyah", "The Overwhelming Event"),
    ("Al-Fajr", "The Dawn"), ("Al-Balad", "The City"), ("Ash-Shams", "The Sun"),
    ("Al-Layl", "The Night"), ("Ad-Duha", "The Morning Brightness"),
    ("Ash-Sharh", "The Relief (also Al-Inshirah)"), ("At-Tin", "The Fig"),
    ("Al-‘Alaq", "The Clinging Clot"), ("Al-Qadr", "The Night of Power"),
    ("Al-Bayyinah", "The Clear Proof"), ("Az-Zalzalah", "The Earthquake"),
    ("Al-‘Adiyat", "The Racing Steeds"), ("Al-Qari‘ah", "The Striking Calamity"),
    ("At-Takathur", "Competing for More"), ("Al-‘Asr", "The Passage of Time"),
    ("Al-Humazah", "The Slanderer"), ("Al-Fil", "The Elephant"),
    ("Quraysh", "Quraysh"), ("Al-Ma‘un", "Small Kindnesses"),
    ("Al-Kawthar", "Abundance"), ("Al-Kafirun", "The Disbelievers"),
    ("An-Nasr", "Divine Support"), ("Al-Masad", "The Palm Fiber (also Al-Lahab)"),
    ("Al-Ikhlas", "Sincerity"), ("Al-Falaq", "The Daybreak"), ("An-Nas", "Mankind"),
)

# Chronological position of each surah (index 0 = Surah 1), standard Egyptian
# (1924) ordering. Scholars differ on some placements.
REV_ORDER = (
    5, 87, 89, 92, 112, 55, 39, 88, 113, 51, 52, 53, 96, 72, 54, 70, 50, 69, 44, 45,
    73, 103, 74, 102, 42, 47, 48, 49, 85, 84, 57, 75, 90, 58, 43, 41, 56, 38, 59, 60,
    61, 62, 63, 64, 65, 66, 95, 111, 106, 34, 67, 76, 23, 37, 97, 46, 94, 105, 101, 91,
    109, 110, 104, 108, 99, 107, 77, 2, 78, 79, 71, 40, 3, 4, 31, 98, 33, 80, 81, 24,
    7, 82, 86, 83, 27, 36, 8, 68, 10, 35, 26, 9, 11, 12, 28, 1, 25, 100, 93, 14, 30,
    16, 13, 32, 19, 29, 17, 15, 18, 114, 6, 22, 20, 21,
)
MEDINAN = {2, 3, 4, 5, 8, 9, 13, 22, 24, 33, 47, 48, 49, 55, 57, 58, 59, 60, 61, 62,
           63, 64, 65, 66, 76, 98, 99, 110}

JUZ_STARTS = [
    (1, 1), (2, 142), (2, 253), (3, 92), (4, 24), (4, 148), (5, 82), (6, 111), (7, 88),
    (8, 41), (9, 93), (11, 6), (12, 53), (15, 1), (17, 1), (18, 75), (21, 1), (23, 1),
    (25, 21), (27, 56), (29, 46), (33, 31), (36, 28), (39, 32), (41, 47), (46, 1),
    (51, 31), (58, 1), (67, 1), (78, 1),
]
JUZ_START_MAP = {sa: i for i, sa in enumerate(JUZ_STARTS, 1)}

# Verses of prostration (sajdat al-tilawah). 22:77 is counted by the Shafi'i and
# Hanbali schools only; 38:24 is counted differently across schools.
SAJDA = {(7, 206), (13, 15), (16, 50), (17, 109), (19, 58), (22, 18), (22, 77),
         (25, 60), (27, 26), (32, 15), (38, 24), (41, 38), (53, 62), (84, 21), (96, 19)}

assert len(SURA_SIZE) == 114 and sum(SURA_SIZE) == TOTAL_AYAT
assert len(SURA_NAMES) == 114 and sorted(REV_ORDER) == list(range(1, 115))
assert len(JUZ_STARTS) == 30 and JUZ_STARTS == sorted(JUZ_STARTS)


def juz_of(sura: int, ayah: int) -> int:
    return bisect_right(JUZ_STARTS, (sura, ayah))


def juz_span(sura: int) -> str:
    a, b = juz_of(sura, 1), juz_of(sura, SURA_SIZE[sura - 1])
    return str(a) if a == b else f"{a}–{b}"


# ---------------------------------------------------------------------------
# Editions catalogue
# ---------------------------------------------------------------------------
G_AR, G_TL, G_EN, G_HI, G_GU, G_NE, G_UR, G_RO = (
    "Arabic", "Transliteration", "English", "Hindi", "Gujarati", "Nepali", "Urdu",
    "Roman script",
)
GROUP_PREFIX = {G_TL: "Transliteration: ", G_EN: "English: ", G_HI: "Hindi: ",
                G_GU: "Gujarati: ", G_NE: "Nepali: ", G_UR: "Urdu: "}
KIND_TAG = {"tafsir": "Commentary", "ai": "AI-generated"}


@dataclass(frozen=True)
class Source:
    id: str
    label: str
    group: str
    lang: str
    path: str
    kind: str = "translation"      # arabic | transliteration | translation | tafsir | ai
    default: bool = False
    fmt: str = "bracket"           # bracket | pipe | lines
    fallback: tuple | None = None  # (path, fmt)

    @property
    def full(self) -> str:
        return GROUP_PREFIX.get(self.group, "") + self.label

    @property
    def rtl(self) -> bool:
        return self.lang.split("-")[0] in ("ar", "ur") and "Latn" not in self.lang

    @property
    def tag(self) -> str:
        return KIND_TAG.get(self.kind, "")


def _o(name: str) -> str:
    return f"output/quran_{name}.txt"


def _s(id_, label, group, lang, path, **kw) -> Source:
    return Source(id_, label, group, lang, path, **kw)


def _en(id_, label, name, **kw):
    return _s(id_, label, G_EN, "en", _o("english_" + name), **kw)


def _ur(id_, label, name, **kw):
    return _s(id_, label, G_UR, "ur", _o("urdu_" + name), **kw)


CATALOG: list[Source] = [
    _s("arabic", "Arabic(Uthmanic(minimal))", G_AR, "ar", _o("arabic"),
       kind="arabic", default=True),
    _s("arabic-simple", "Arabic(Simple)", G_AR, "ar", _o("arabic_simple"),
       kind="arabic"),
    _s("translit", "Tanzil", G_TL, "en-Latn", "data/en.transliteration.tanzil.txt",
       kind="transliteration", fmt="pipe"),
    _s("translit-unicode", "Unicode", G_TL, "en-Latn", _o("translit_unicode"),
       kind="transliteration", default=True),
    _s("translit-en", "English scheme", G_TL, "en-Latn", _o("english_translit"),
       kind="transliteration"),
    _s("trans", "Pickthall", G_EN, "en", _o("english_pickthall"),
       fallback=("data/en.pickthall.txt", "lines")),
    _en("trans-yusuf", "Yusuf Ali", "yusufali", default=True),
    _en("trans-sahih", "Saheeh International", "sahih"),
    _en("trans-qarai", "Ali Quli Qarai", "qarai"),
    _en("trans-hilali", "Muhsin Khan & Hilali", "hilali"),
    _en("eng-abridged", "Abridged Explanation of the Qur’an", "abridged", kind="tafsir"),
    _en("trans-ahmedali", "Ahmed Ali", "ahmedali"),
    _en("trans-ahmedraza", "Ahmed Raza Khan", "ahmedraza"),
    _en("trans-arberry", "A. J. Arberry", "arberry"),
    _en("trans-daryabadi", "Abdul Majid Daryabadi", "daryabadi"),
    _en("trans-itani", "Talal Itani", "itani"),
    _en("trans-maududi", "Abul A‘la Maududi", "maududi"),
    _en("trans-mubarakpuri", "Safiur Rahman Mubarakpuri", "mubarakpuri"),
    _en("trans-qaribullah", "Qaribullah & Darwish", "qaribullah"),
    _en("trans-sarwar", "Muhammad Sarwar", "sarwar"),
    _en("trans-shakir", "M. H. Shakir", "shakir"),
    _en("trans-wahiduddin", "Wahiduddin Khan", "wahiduddin"),
    _en("trans-rwwad", "Rowwad Translation Center", "rwwad"),
    _en("trans-asad", "Muhammad Asad", "asad"),
    _en("trans-usmani", "Taqi Usmani", "usmani"),
    _en("trans-abdelhaleem", "M. A. S. Abdel Haleem", "abdelhaleem"),
    _en("trans-aishabewley", "Aisha Bewley", "aishabewley"),
    _en("trans-aliunal", "Ali Ünal", "aliunal"),
    _en("trans-lalehbakhtiar", "Laleh Bakhtiar", "lalehbakhtiar"),
    _en("trans-edwardpalmer", "Edward Henry Palmer", "edwardpalmer"),
    _en("trans-farookmalik", "Farook Malik", "farookmalik"),
    _en("trans-georgesale", "George Sale", "georgesale"),
    _en("trans-hamidsaziz", "Hamid S. Aziz", "hamidsaziz"),
    _en("trans-johnrodwell", "J. M. Rodwell", "johnrodwell"),
    _en("trans-literal", "Literal", "literal"),
    _en("trans-miraneesuddin", "Mir Aneesuddin", "miraneesuddin"),
    _en("trans-mohammadshafi", "Mohammad Shafi", "mohammadshafi"),
    _en("trans-muhammadghali", "Muhammad Mahmoud Ghali", "muhammadghali"),
    _en("trans-khattab", "Mustafa Khattab", "khattab"),
    _en("trans-njdawood", "N. J. Dawood", "njdawood"),
    _en("trans-safikaskas", "Safi Kaskas", "safikaskas"),
    _en("trans-shabbirahmed", "Shabbir Ahmed", "shabbirahmed"),
    _en("trans-syedvickar", "Syed Vickar Ahamed", "syedvickar"),
    _en("trans-itaninew", "Talal Itani (new)", "itaninew"),
    _en("trans-tbirving", "T. B. Irving", "tbirving"),
    _en("trans-monotheist", "The Monotheist Group", "monotheist"),
    _en("trans-ummmuhammad", "Umm Muhammad", "ummmuhammad"),
    _s("trans-clearai", "Clear AI (machine-generated)", G_EN, "en", _o("clearai"), kind="ai"),
    _s("hindi", "Farooq Khan & Ahmed", G_HI, "hi", _o("hindi_farooq")),
    _s("hindi-suhail", "Suhel Farooq Khan", G_HI, "hi", _o("hindi_suhail"), default=True),
    _s("hindi-omari", "Azizul Haque al-Umari", G_HI, "hi", _o("hindi_omari")),
    _s("hindi-mokhtasar", "Mokhtasar Tafsir", G_HI, "hi", _o("hindi_mokhtasar"),
       kind="tafsir", default=True),
    _s("gujarati", "Rabila al-Umri", G_GU, "gu", _o("gujarati_rabila")),
    _s("nepali", "Ahl al-Hadith Central Society", G_NE, "ne", _o("nepali_ahl_al_hadith")),
    _ur("ur-jalandhry", "Fateh Muhammad Jalandhry", "jalandhry"),
    _ur("ur-ahmedali", "Ahmed Ali", "ahmedali"),
    _ur("ur-jawadi", "Zeeshan Haider Jawadi", "jawadi"),
    _ur("ur-kanzuliman", "Kanzul Iman (Ahmed Raza Khan)", "kanzuliman"),
    _ur("ur-maududi", "Maududi (Tafhim)", "maududi"),
    _ur("ur-qadri", "Tahir ul-Qadri (Irfan ul-Quran)", "qadri"),
    _ur("ur-junagarhi", "Muhammad Junagarhi", "junagarhi"),
    _ur("ur-najafi", "Muhammad Hussain Najafi", "najafi"),
    _ur("ur-mahmudalhasan", "Mahmud al-Hasan", "mahmudalhasan"),
    _ur("ur-zilalquran", "Fi Zilal al-Quran", "zilalquran", kind="tafsir"),
    _ur("ur-bayanulquran", "Bayan ul-Quran (Israr Ahmed)", "bayanulquran"),
    _ur("ur-wahiduddin", "Wahiduddin Khan", "wahiduddin"),
    _ur("ur-karamshah", "Pir Karam Shah al-Azhari", "karamshah"),
    _ur("ur-taqiusmani", "Taqi Usmani", "taqiusmani"),
    _s("roman-urdu", "Roman Urdu: Maududi", G_RO, "ur-Latn", _o("roman_urdu_maududi")),
    _s("roman-urdu-junagarhi", "Roman Urdu: Junagarhi", G_RO, "ur-Latn",
       _o("roman_urdu_junagarhi")),
    _s("rom-hindi-farooq", "Roman Hindi: Farooq", G_RO, "hi-Latn", _o("roman_hindi_farooq")),
    _s("rom-hindi-suhail", "Roman Hindi: Suhail", G_RO, "hi-Latn", _o("roman_hindi_suhail")),
    _s("rom-hindi-omari", "Roman Hindi: Omari", G_RO, "hi-Latn", _o("roman_hindi_omari")),
    _s("rom-guj-rabila", "Roman Gujarati: Rabila", G_RO, "gu-Latn",
       _o("roman_gujarati_rabila")),
]
assert len({s.id for s in CATALOG}) == len(CATALOG), "duplicate edition id"

# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
BRACKET = re.compile(r"^\[(\d+):(\d+)\]\s*(.*)$")
Verses = dict  # {(sura, ayah): text}


def _lines(path: Path) -> list[str]:
    # split on \n only: str.splitlines() would also split on U+2028 etc.
    return [ln.rstrip("\r") for ln in path.read_text(encoding="utf-8").split("\n")]


def parse_bracket(path: Path) -> Verses:
    out = {}
    for ln in _lines(path):
        m = BRACKET.match(ln)
        if m:
            out[(int(m[1]), int(m[2]))] = m[3].strip()
    return out


def parse_pipe(path: Path) -> Verses:
    out = {}
    for ln in _lines(path):
        if not ln.strip() or ln.startswith("#"):
            continue
        p = ln.split("|", 2)
        if len(p) == 3 and p[0].isdigit() and p[1].isdigit():
            out[(int(p[0]), int(p[1]))] = p[2].strip()
    return out


def parse_lines(path: Path) -> Verses:
    out, it = {}, iter(_lines(path))
    for s, size in enumerate(SURA_SIZE, 1):
        for a in range(1, size + 1):
            out[(s, a)] = next(it, "").strip()
    return out


PARSERS = {"bracket": parse_bracket, "pipe": parse_pipe, "lines": parse_lines}


def load_source(root: Path, src: Source) -> Verses:
    options = [(src.path, src.fmt)] + ([src.fallback] if src.fallback else [])
    for rel, fmt in options:
        f = root / rel
        if f.exists():
            data = PARSERS[fmt](f)
            return {k: v for k, v in data.items()
                    if 1 <= k[0] <= 114 and 1 <= k[1] <= SURA_SIZE[k[0] - 1]}
    return {}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def esc(s: str) -> str:
    return html.escape(s, quote=True)


def write(path: Path, text: str) -> bool:
    """Write only when content changed (keeps git diffs and mtimes quiet)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def js_json(obj) -> str:
    return (json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


CFG = {"fonts": True}
FONT_LINK = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
             'family=Amiri+Quran&family=Literata:wght@400;600&family=Noto+Nastaliq+Urdu'
             '&family=Noto+Sans+Devanagari&family=Noto+Sans+Gujarati&display=swap">')

# Applied before first paint so saved theme and text sizes never flash.
EARLY = ('<script>try{var u=JSON.parse(localStorage.getItem("quran-ui")||"{}"),'
         'r=document.documentElement;if(u.theme&&u.theme!=="auto")r.dataset.theme=u.theme;'
         'if(u.tx)r.style.setProperty("--tx",u.tx);if(u.ar)r.style.setProperty("--ar",u.ar)'
         '}catch(e){}</script>')

DISCLAIMER = ("Translations convey the meanings of the Qur’an in another language; "
              "only the Arabic text is the Qur’an itself. Items marked Commentary or "
              "AI-generated are explanations or machine output, not scripture.")


def page(title: str, body: str, page_id: str, *, desc: str = "", sura: int = 0,
         head_extra: str = "", foot_extra: str = "") -> str:
    sd = f' data-sura="{sura}"' if sura else ""
    desc = desc or "Read the Qur’an in Arabic with transliteration, audio and translations."
    fonts = FONT_LINK if CFG["fonts"] else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="color-scheme" content="light dark">
{EARLY}
{fonts}
<link rel="stylesheet" href="assets/style.css">
{head_extra}
</head>
<body data-page="{page_id}"{sd}>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><a class="brand" href="index.html">Qur’an</a><nav aria-label="Site"><a href="search.html">Search</a><a href="bookmarks.html">Bookmarks</a><a href="config.html">Settings</a></nav></header>
<main id="main">
{body}
</main>
<footer class="foot"><p><a href="sources.html">Sources</a> <a href="license.html">License</a> <a href="download.html">Offline copy</a> <a href="{GITHUB}" rel="noopener noreferrer">GitHub</a></p><p class="small muted">{esc(DISCLAIMER)}</p></footer>
<script src="assets/catalog.js" defer></script>
{foot_extra}<script src="assets/app.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Page bodies
# ---------------------------------------------------------------------------
def sura_info(n: int) -> dict:
    name, meaning = SURA_NAMES[n - 1]
    return {"n": n, "name": name, "meaning": meaning, "size": SURA_SIZE[n - 1],
            "type": "D" if n in MEDINAN else "M", "order": REV_ORDER[n - 1],
            "juz": juz_span(n)}


def type_label(t: str) -> str:
    return "Medinan" if t == "D" else "Meccan"


def tr_section(src: Source, text: str) -> str:
    if not text:
        return ""
    d = ' dir="rtl"' if src.rtl else ""
    tag = f'<span class="tag">{src.tag}</span>' if src.tag else ""
    return (f'<section class="tr" data-t="{src.id}" data-kind="{src.kind}" '
            f'lang="{src.lang}"{d}><h3>{esc(src.full)}{tag}</h3><p>{esc(text)}</p></section>')


def surah_body(s: int, data: dict[str, Verses], defaults: list[Source]) -> str:
    info = sura_info(s)
    parts: list[str] = []
    if s == 9:
        parts.append('<p class="small muted center">This surah is traditionally '
                     'recited without the Bismillah.</p>')
    elif s != 1:  # in Al-Fatihah the Bismillah is verse 1 itself
        parts.append('<p class="bismillah" lang="ar" dir="rtl">'
                     'بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ</p>')
    for a in range(1, info["size"] + 1):
        if (s, a) in JUZ_START_MAP:
            j = JUZ_START_MAP[(s, a)]
            parts.append(f'<div class="juz-mark" id="juz-{j}" data-a="{a}">Juz {j} begins</div>')
        badge = ""
        if (s, a) in SAJDA:
            badge = ('<span class="badge sajda" title="Verse of prostration (sajdat '
                     'al-tilawah). Schools differ on which verses are counted.">'
                     'Prostration</span>')
        rows = "".join(tr_section(src, data[src.id].get((s, a), "")) for src in defaults)
        parts.append(
            f'<article class="ayah" id="ayah-{a}" data-a="{a}">'
            f'<div class="ayah-head"><a class="ayah-no" href="#ayah-{a}" '
            f'aria-label="Verse {a}">{a}</a>{badge}</div>'
            f'<p class="ar" lang="ar" dir="rtl">{esc(data["arabic"].get((s, a), ""))}</p>'
            f'<div class="tr-list">{rows}</div></article>')

    prev_l = nxt_l = ""
    if s > 1:
        prev_l = f'<a class="btn sura-link" href="{s-1:03d}.html" rel="prev">Previous: {esc(SURA_NAMES[s-2][0])}</a>'
    if s < 114:
        nxt_l = f'<a class="btn sura-link" href="{s+1:03d}.html" rel="next">Next: {esc(SURA_NAMES[s][0])}</a>'
    pager = f'<nav class="pager" aria-label="Surah navigation">{prev_l}{nxt_l}</nav>'
    return f"""<h1>{s}. {esc(info['name'])}</h1>
<p class="meaning">{esc(info['meaning'])}</p>
<ul class="facts">
<li><span class="badge {'medinan' if info['type'] == 'D' else 'meccan'}">{type_label(info['type'])}</span></li>
<li>{info['size']} verses</li>
<li>Juz {info['juz']}</li>
<li title="Standard (Egyptian 1924) chronology; scholars differ on some placements.">Revelation order {info['order']}</li>
</ul>
<div class="toolbar"><label for="jump" class="small muted">Go to surah</label><select id="jump" aria-label="Go to surah"></select></div>
<details class="panel" id="panel"><summary>Display options</summary><div class="panel-body" id="panel-body"><p class="small muted">Loading options…</p></div></details>
<noscript><p class="note">JavaScript is needed for display options, audio, bookmarks and extra translations. The Arabic and default editions are shown below.</p></noscript>
<div id="rangebar" class="rangebar" hidden></div>
<p id="status" class="small muted" role="status" aria-live="polite"></p>
<div id="verses">
{chr(10).join(parts)}
</div>
{pager}
<p class="small muted">{esc(DISCLAIMER)}</p>"""


def index_body(sources: list[Source]) -> str:
    items = []
    for n in range(1, 115):
        i = sura_info(n)
        key = f"{n} {i['name']} {i['meaning']} {type_label(i['type'])}"
        items.append(
            f'<li data-k="{esc(key)}"><a class="sura-link" href="{n:03d}.html">'
            f'<span class="sn">{n}</span><span><strong>{esc(i["name"])}</strong>'
            f'<small>{esc(i["meaning"])}</small>'
            f'<small>{type_label(i["type"])}, {i["size"]} verses, Juz {i["juz"]}</small>'
            f'</span></a></li>')
    juz = "".join(
        f'<a class="btn small sura-link" href="{s:03d}.html#{a}" '
        f'title="{esc(SURA_NAMES[s-1][0])} {s}:{a}">Juz {j}</a>'
        for j, (s, a) in enumerate(JUZ_STARTS, 1))
    return f"""<h1>Qur’an Reader</h1>
<p class="lead">Read the Arabic with transliteration, verse audio and {len(sources) - 1} translations and commentaries. Choose what appears in <a href="config.html">Settings</a>.</p>
<aside id="welcome" class="note" hidden><p><strong>First visit?</strong> Open <a href="config.html">Settings</a> to pick the languages and translations you want with each verse.</p><button type="button" class="btn small" id="welcome-x">Got it</button></aside>
<section id="resume" hidden aria-label="Continue reading"></section>
<div class="field-row"><label for="filter">Find a surah</label><input id="filter" class="field" type="search" placeholder="Name, meaning or number" autocomplete="off"><span id="fcount" class="small muted" role="status" aria-live="polite"></span></div>
<ul class="sgrid" id="sgrid">
{chr(10).join(items)}
</ul>
<details class="panel"><summary>Browse by Juz</summary><div class="panel-body"><div class="chips">{juz}</div></div></details>
<details class="panel"><summary>About these texts</summary><div class="panel-body"><p>{esc(DISCLAIMER)}</p><p>Texts are reproduced from their sources; copyright and licence terms differ by edition. See <a href="sources.html">Sources</a> and <a href="license.html">License</a>.</p></div></details>"""


def config_body() -> str:
    return """<h1>Settings</h1>
<p class="lead muted">Saved in this browser only.</p>
<section><h2>Appearance</h2>
<fieldset class="grp"><legend>Theme</legend>
<label class="radio"><input type="radio" name="theme" value="auto"> Match my device</label>
<label class="radio"><input type="radio" name="theme" value="light"> Light</label>
<label class="radio"><input type="radio" name="theme" value="dark"> Dark</label>
</fieldset>
<div id="cfg-sliders"></div></section>
<section><h2>Shown with each verse</h2><div id="cfg-chips"></div></section>
<section><h2>Your data</h2>
<div class="row"><button type="button" class="btn" id="cfg-reset">Restore default selection</button>
<button type="button" class="btn danger" id="cfg-clear">Clear bookmarks and reading history</button></div></section>"""


def bookmarks_body() -> str:
    return """<h1>Bookmarks</h1>
<p class="muted">Stored in this browser. Export them to move to another device.</p>
<div class="row"><button type="button" class="btn" id="bm-export">Export</button>
<label class="btn" for="bm-import">Import</label><input id="bm-import" type="file" accept="application/json,.json" hidden>
<button type="button" class="btn danger" id="bm-clear">Remove all</button></div>
<p id="bm-count" class="small muted" role="status"></p>
<ul class="bm-list" id="bm-list"></ul>"""


def search_body() -> str:
    return """<h1>Search</h1>
<form id="sform" class="searchbar" role="search"><label class="sr" for="q">Search the Qur’an</label>
<input id="q" class="field" type="search" placeholder="A word, a phrase, or a verse like 2:255" autocomplete="off" spellcheck="false">
<button class="btn primary" type="submit">Search</button></form>
<p id="scope" class="small muted"></p>
<p id="status" role="status" aria-live="polite"></p>
<ol class="results" id="results"></ol>
<button id="more" class="btn" type="button" hidden>Show more</button>"""


def download_body() -> str:
    pages = [("index", "Index"), ("bookmarks", "Bookmarks"), ("config", "Settings"),
             ("sources", "Sources"), ("license", "License")]
    chk = "".join(f'<label class="radio"><input type="checkbox" id="dl-p-{p}" checked> {n}</label>'
                  for p, n in pages)
    return f"""<h1>Offline copy</h1>
<p class="lead muted">Build a ZIP of this site with only the editions and surahs you want. It runs in your browser.</p>
<section><h2>Editions</h2><div id="dl-chips"></div></section>
<section><h2>Surahs</h2><div class="row"><label>From <input id="dl-from" class="num" type="number" min="1" max="114" value="1"></label>
<label>To <input id="dl-to" class="num" type="number" min="1" max="114" value="114"></label></div></section>
<section><h2>Pages</h2><div class="row">{chk}
<label class="radio"><input type="checkbox" id="dl-search" checked> Search (adds each selected edition again, so the ZIP grows)</label></div></section>
<p class="small muted">Each edition typically adds a few MB. Verse audio still needs an internet connection.</p>
<button type="button" class="btn primary" id="dl-go">Build ZIP</button>
<progress id="dl-prog" max="100" value="0" hidden></progress>
<p id="dl-status" role="status" aria-live="polite"></p>"""


def sources_body(sources: list[Source]) -> str:
    rows = "".join(
        f"<tr><td>{esc(s.group)}</td><td>{esc(s.label)}</td>"
        f"<td>{esc(KIND_TAG.get(s.kind, 'Translation' if s.kind == 'translation' else s.kind.title()))}</td></tr>"
        for s in sources)
    return f"""<h1>Sources and attribution</h1>
<p>Text and translation data come from tanzil.net, quranenc.com, fawazahmed0/quran-api, quran.com, the Quran Unicode Project and the respective translators and publishers. Texts are reproduced verbatim; nothing is edited. Pickthall (d. 1936) is in the public domain in most jurisdictions. Other editions remain subject to their own copyright and licence terms, so check before redistributing.</p>
<p>Verse audio: Mishary Alafasy, streamed from a third-party host. Revelation order follows the standard Egyptian (1924) chronology; Meccan/Medinan labels follow common scholarly convention and some surahs are disputed. Prostration verses use the common list of 15; schools differ on 22:77 and 38:24.</p>
<p><strong>Commentary</strong> editions explain meanings rather than translate. <strong>AI-generated</strong> editions are machine output with no scholarly review and should not be relied on for religious rulings.</p>
<div class="table-wrap"><table><thead><tr><th>Language</th><th>Edition</th><th>Type</th></tr></thead><tbody>{rows}</tbody></table></div>"""


def license_body(text: str) -> str:
    return f'<h1>License</h1><pre class="license">{esc(text)}</pre>'


# ---------------------------------------------------------------------------
# Static assets
# ---------------------------------------------------------------------------
DARK_VARS = ("--bg:#0d1312;--surface:#141d1b;--ink:#e5ece9;--muted:#9aaba6;--line:#27332f;"
             "--soft:#1b2623;--head:#0a2220;--head-ink:#e5ece9;--on:#1e6f66;--on-ink:#fff;"
             "--link:#74d3c7;--accent:#e2ac52;--warn:#f0b66a;--mark:#5c4a0c;color-scheme:dark;")

STYLE_CSS = r"""
:root{--bg:#f3f6f5;--surface:#fff;--ink:#14201e;--muted:#52605c;--line:#d5dedb;--soft:#e8eeec;
--head:#0e4c47;--head-ink:#fff;--on:#0e4c47;--on-ink:#fff;--link:#0b5a53;--accent:#955a08;
--warn:#8a4b00;--mark:#ffe08a;--tx:1;--ar:2;
--ui:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
--serif:Literata,Georgia,"Times New Roman",serif;
--arabic:"Amiri Quran","Scheherazade New","Noto Naskh Arabic","Traditional Arabic",serif;
--ur:"Noto Nastaliq Urdu","Noto Naskh Arabic","Jameel Noori Nastaleeq",serif;
--dv:"Noto Sans Devanagari","Mangal",sans-serif;--gu:"Noto Sans Gujarati","Shruti",sans-serif;
color-scheme:light}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){%DARK%}}
:root[data-theme=dark]{%DARK%}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:1rem/1.6 var(--ui)}
[hidden]{display:none!important}
a{color:var(--link)}
:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.skip{position:absolute;left:-999px;top:0}.skip:focus{left:8px;top:8px;z-index:100;background:var(--surface);padding:8px 12px;border-radius:6px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.muted{color:var(--muted)}.small{font-size:.875rem}.center{text-align:center}
.top{background:var(--head);color:var(--head-ink);display:flex;align-items:center;flex-wrap:wrap;gap:0 18px;padding:6px 14px}
.top a{color:inherit;text-decoration:none;min-height:44px;display:inline-flex;align-items:center}
.top a:hover{text-decoration:underline}
.brand{font-weight:700;font-size:1.2rem;margin-right:auto}
.top nav{display:flex;gap:0 18px;flex-wrap:wrap}
main{max-width:46rem;margin:0 auto;padding:18px 14px 40px}
h1{font-size:1.6rem;line-height:1.25;margin:.2em 0 .15em}
h2{font-size:1.15rem;margin:1.6em 0 .5em}
.lead{font-size:1.05rem;margin:.2em 0 1em}
.meaning{margin:0 0 .6em;color:var(--muted)}
.facts{display:flex;flex-wrap:wrap;gap:4px 14px;list-style:none;padding:0;margin:0 0 14px;font-size:.9rem;color:var(--muted)}
.badge{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:0 9px;font-size:.8rem;line-height:1.6}
.badge.meccan{border-color:var(--accent);color:var(--accent)}.badge.medinan{border-color:var(--link);color:var(--link)}
.badge.sajda{border-color:var(--warn);color:var(--warn)}
.note{background:var(--soft);border-radius:10px;padding:10px 14px;margin:0 0 14px}
.note p{margin:0 0 6px}
.field,.num,select{font:inherit;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:9px 11px;min-height:44px}
.field{width:100%}.num{width:5.5em}
.field-row{display:grid;gap:4px;margin:0 0 12px}
.row{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin:8px 0}
.row>span:first-child{min-width:9rem}
.row input[type=range]{flex:1;min-width:9rem;min-height:32px}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:8px 14px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--link);font:inherit;text-decoration:none;cursor:pointer}
.btn:hover{background:var(--soft)}
.btn.small{min-height:36px;padding:4px 10px;font-size:.9rem}
.btn.primary{background:var(--on);color:var(--on-ink);border-color:var(--on)}
.btn.danger{color:var(--warn)}
.link{background:none;border:0;color:var(--link);font:inherit;text-decoration:underline;cursor:pointer;padding:0}
.radio{display:inline-flex;align-items:center;gap:8px;min-height:44px;margin-right:12px}
.radio input{width:20px;height:20px}
.sgrid{list-style:none;padding:0;margin:0 0 18px;display:grid;grid-template-columns:repeat(auto-fill,minmax(14.5rem,1fr));gap:8px}
.sgrid a{display:flex;gap:12px;align-items:center;padding:10px 12px;background:var(--surface);border:1px solid var(--line);border-radius:10px;text-decoration:none;color:var(--ink);height:100%}
.sgrid a:hover{border-color:var(--link)}
.sgrid small{display:block;color:var(--muted);font-size:.8rem;line-height:1.35}
.sn,.ayah-no{display:inline-grid;place-items:center;min-width:2.3rem;height:2.3rem;padding:0 6px;border:2px solid var(--accent);border-radius:999px;color:var(--accent);font-weight:700;font-size:.85rem;text-decoration:none;flex:none}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:10px;margin:0 0 14px}
.panel>summary{padding:12px 14px;cursor:pointer;font-weight:600;min-height:44px}
.panel-body{padding:2px 14px 14px;border-top:1px solid var(--line)}
.grp{border:0;padding:0;margin:14px 0 0;min-width:0}.grp legend{font-weight:600;font-size:.9rem;padding:0;margin-bottom:6px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{position:relative;display:inline-block}
.chip input{position:absolute;inset:0;width:100%;height:100%;opacity:0;margin:0;cursor:pointer}
.chip span{display:inline-block;padding:7px 12px;min-height:38px;border:1px solid var(--line);border-radius:999px;background:var(--surface);font-size:.9rem}
.chip em{font-size:.75rem;color:var(--warn);font-style:normal}
.chip input:checked+span{background:var(--on);color:var(--on-ink);border-color:var(--on)}
.chip input:checked+span em{color:inherit}
.chip input:focus-visible+span{outline:3px solid var(--accent);outline-offset:2px}
.toolbar{display:flex;align-items:center;gap:8px;margin:0 0 12px}
.toolbar select{flex:1;max-width:20rem}
.rangebar{background:var(--soft);border-radius:8px;padding:8px 12px;margin:0 0 12px}
.bismillah{font-family:var(--arabic);font-size:calc(var(--ar)*1.05rem);text-align:center;margin:10px 0 16px;line-height:2}
.juz-mark{text-align:center;color:var(--muted);font-size:.85rem;margin:18px 0 8px;padding:4px;border-block:1px dashed var(--line)}
.ayah{background:var(--surface);border:1px solid var(--line);border-radius:12px;margin:0 0 14px;padding:12px 14px 8px;scroll-margin-top:12px}
.ayah.playing{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent)}
.ayah.flash{animation:flash 1.6s ease-out}
@keyframes flash{0%{background:var(--mark)}100%{background:var(--surface)}}
.ayah-head{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.actions{margin-left:auto;display:flex}
.ib{width:44px;height:44px;display:grid;place-items:center;background:none;border:0;border-radius:8px;color:var(--muted);cursor:pointer}
.ib:hover{background:var(--soft)}.ib[aria-pressed=true]{color:var(--accent)}.ib[aria-pressed=true] svg{fill:currentColor}
.ar{font-family:var(--arabic);font-size:calc(var(--ar)*1rem);line-height:2.1;direction:rtl;text-align:right;margin:.3em 0 .4em}
.no-ar .ar,.no-audio .play{display:none}
.tr{border-inline-start:3px solid var(--line);padding:2px 0;padding-inline-start:12px;margin:12px 0;font-family:var(--serif)}
.tr[data-kind=transliteration]{border-color:var(--accent)}
.tr[data-kind=tafsir]{border-color:var(--link)}
.tr[data-kind=ai]{border-color:var(--warn);border-inline-start-style:dashed}
.tr h3{font:600 .78rem/1.3 var(--ui);color:var(--muted);margin:0 0 3px;direction:ltr;text-align:left}
.tr .tag{margin-left:8px;color:var(--warn)}
.tr p{margin:0;font-size:calc(var(--tx)*1.02rem);line-height:1.75}
.tr:lang(hi),.tr:lang(ne){font-family:var(--dv)}.tr:lang(gu){font-family:var(--gu)}
.tr:lang(ur){font-family:var(--ur)}.tr:lang(ur) p{font-size:calc(var(--tx)*1.25rem);line-height:2.2}
.tr:lang(hi-Latn),.tr:lang(gu-Latn),.tr:lang(ur-Latn),.tr:lang(en-Latn){font-family:var(--serif)}
.tr:lang(ur-Latn) p{font-size:calc(var(--tx)*1.02rem);line-height:1.75}
.pager{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;margin:20px 0}
.results,.bm-list{list-style:none;padding:0;margin:0}
.hit,.bm-list li{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:0 0 10px}
.hit-head{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;margin-bottom:4px}
.hit-text{margin:6px 0 0}.hit-label{display:block;font-size:.78rem;color:var(--muted)}
mark{background:var(--mark);color:inherit;border-radius:3px}
.searchbar{display:flex;gap:8px;margin:0 0 8px}
.bm-list li{display:flex;align-items:center;gap:10px;justify-content:space-between}
.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.92rem}
th,td{text-align:left;padding:6px 10px;border-bottom:1px solid var(--line)}
.license{white-space:pre-wrap;word-wrap:break-word;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px;font-size:.85rem}
progress{width:100%;height:14px;margin:10px 0}
.foot{max-width:46rem;margin:0 auto;padding:16px 14px 40px;border-top:1px solid var(--line);text-align:center}
.foot a{margin:0 8px;display:inline-block;min-height:32px}
.totop{position:fixed;right:16px;bottom:16px;width:46px;height:46px;border-radius:50%;border:0;background:var(--on);color:var(--on-ink);font-size:1.3rem;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.3)}
#toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);max-width:90vw;background:var(--ink);color:var(--bg);padding:10px 16px;border-radius:8px;opacity:0;pointer-events:none;transition:opacity .2s;z-index:50}
#toast.show{opacity:1}
@media(max-width:520px){h1{font-size:1.4rem}.row>span:first-child{min-width:100%}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
@media print{.top,.foot,.panel,.pager,.actions,.totop,#toast,.toolbar,.skip,#rangebar{display:none!important}
body{background:#fff;color:#000}.ayah{break-inside:avoid;border-color:#999;background:#fff}}
""".replace("%DARK%", DARK_VARS)

APP_JS = r"""
(()=>{
"use strict";
const C=window.QURAN_CATALOG||{suras:[],tr:[],defaults:{},audio:"",range:[1,114]};
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const pad=n=>String(n).padStart(3,"0");
const h=(tag,attrs={},...kids)=>{const e=document.createElement(tag);
  for(const[k,v]of Object.entries(attrs)){if(k==="text")e.textContent=v;else if(k==="html")e.innerHTML=v;
    else if(v===true)e.setAttribute(k,"");else if(v!==false&&v!=null)e.setAttribute(k,v);}
  kids.flat().forEach(c=>c!=null&&c!==false&&e.append(c));return e;};
const store={
  get(k,d){try{const v=localStorage.getItem(k);return v===null?d:JSON.parse(v);}catch{return d;}},
  set(k,v){try{localStorage.setItem(k,JSON.stringify(v));return true;}catch{return false;}},
  del(k){try{localStorage.removeItem(k);}catch{}}};
const ORD=Object.fromEntries(C.tr.map((t,i)=>[t.id,i]));
const sname=s=>C.suras[s-1]?C.suras[s-1].name:"Surah "+s;
const ago=t=>{const m=Math.round((Date.now()-t)/6e4);return m<1?"just now":m<60?m+" min ago":m<1440?Math.round(m/60)+" h ago":Math.round(m/1440)+" d ago";};

/* ---------- preferences ---------- */
let prefs=store.get("quran-cf",{});if(!prefs||typeof prefs!=="object"||Array.isArray(prefs))prefs={};
const isOn=id=>Object.prototype.hasOwnProperty.call(prefs,id)?!!prefs[id]:!!C.defaults[id];
const setOn=(id,v)=>{prefs[id]=!!v;store.set("quran-cf",prefs);};
let ui=store.get("quran-ui",{});if(!ui||typeof ui!=="object")ui={};
const applyUi=()=>{const r=document.documentElement;
  if(ui.theme&&ui.theme!=="auto")r.dataset.theme=ui.theme;else delete r.dataset.theme;
  r.style.setProperty("--tx",ui.tx||1);r.style.setProperty("--ar",ui.ar||2);};
const sliderRow=(label,key,min,max,step,def)=>{
  const i=h("input",{type:"range",min,max,step,value:ui[key]||def,"aria-label":label});
  i.addEventListener("input",()=>{ui[key]=+i.value;store.set("quran-ui",ui);applyUi();});
  return h("label",{class:"row"},h("span",{text:label}),i);};

/* ---------- ui helpers ---------- */
let tt;const toast=m=>{let t=$("#toast");if(!t){t=h("div",{id:"toast",role:"status","aria-live":"polite"});document.body.append(t);}
  t.textContent=m;t.classList.add("show");clearTimeout(tt);tt=setTimeout(()=>t.classList.remove("show"),2400);};
const copy=async text=>{try{await navigator.clipboard.writeText(text);return true;}catch{
  const t=h("textarea",{style:"position:fixed;opacity:0"});t.value=text;document.body.append(t);t.select();
  let ok=false;try{ok=document.execCommand("copy");}catch{}t.remove();return ok;}};
const ICONS={
  play:'<polygon points="6 4 20 12 6 20 6 4"/>',
  pause:'<rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>',
  bookmark:'<path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>',
  copy:'<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
  link:'<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>'};
const svg=n=>`<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[n]}</svg>`;
const iconBtn=(cls,icon,label,fn)=>{const b=h("button",{type:"button",class:"ib "+cls,"aria-label":label,title:label,html:svg(icon)});b.addEventListener("click",()=>fn(b));return b;};

/* ---------- search-friendly normalisation (Arabic marks, Latin accents, apostrophes) ---------- */
const MARKS=/[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u08D3-\u08FF\u0640]/;
const nch=c=>{if(MARKS.test(c))return"";
  if("\u0622\u0623\u0625\u0671".includes(c))return"\u0627";
  if(c==="\u0649"||c==="\u06CC")return"\u064A";if(c==="\u06A9")return"\u0643";
  if("'\u2019\u2018\u02BF\u02BE`".includes(c))return"";
  return c.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();};
const normMap=s=>{let t="";const m=[];for(let i=0;i<s.length;i++){const n=nch(s[i]);for(const ch of n){t+=ch;m.push(i);}}return{t,m};};
const norm=s=>normMap(s).t;

/* ---------- on-demand data (script tags so it also works from file://) ---------- */
const cache={},wait={};
window.QData=(k,a)=>{cache[k]=a;const w=wait[k];delete wait[k];(w||[]).forEach(p=>p[0](a));};
const load=k=>new Promise((ok,no)=>{
  if(cache[k])return ok(cache[k]);
  if(wait[k]){wait[k].push([ok,no]);return;}
  wait[k]=[[ok,no]];
  const s=document.createElement("script");s.src="data/"+k+".js";
  s.onerror=()=>{const w=wait[k];delete wait[k];s.remove();w.forEach(p=>p[1](new Error(k)));};
  document.head.append(s);});

/* ---------- edition picker (reader, settings, download) ---------- */
function chips(box,o){
  box.textContent="";
  const items=(o.audio?[{id:"audio",label:"Verse audio (Mishary Alafasy)",group:"Audio"}]:[]).concat(C.tr);
  const q=h("input",{type:"search",class:"field","aria-label":"Filter editions",placeholder:"Filter, e.g. Urdu or Yusuf"});
  const count=h("p",{class:"small muted","aria-live":"polite"});box.append(q,count);
  const groups=[],idx={};
  items.forEach(t=>{if(!(t.group in idx)){idx[t.group]=groups.length;groups.push({name:t.group,items:[]});}groups[idx[t.group]].items.push(t);});
  const upd=()=>{count.textContent=items.filter(t=>o.isOn(t.id)).length+" selected";};
  const sets=groups.map(g=>{
    const fs=h("fieldset",{class:"grp"},h("legend",{text:g.name})),row=h("div",{class:"chips"});
    g.items.forEach(t=>{
      const cb=h("input",{type:"checkbox"});cb.checked=!!o.isOn(t.id);
      cb.addEventListener("change",()=>{o.set(t.id,cb.checked);upd();if(o.change)o.change(t.id,cb.checked);});
      const sp=h("span",{text:t.label});if(t.tag)sp.append(" ",h("em",{text:t.tag}));
      row.append(h("label",{class:"chip","data-s":norm(`${t.full||t.label} ${g.name}`)},cb,sp));});
    fs.append(row);box.append(fs);return fs;});
  q.addEventListener("input",()=>{const w=norm(q.value).split(/\s+/).filter(Boolean);
    sets.forEach(fs=>{let any=false;$$(".chip",fs).forEach(l=>{const ok=w.every(x=>l.dataset.s.includes(x));l.hidden=!ok;if(ok)any=true;});fs.hidden=!any;});});
  upd();}

/* ---------- reader ---------- */
function initReader(){
  const s=+document.body.dataset.sura,meta=C.suras[s-1],size=meta.size,root=document.documentElement;
  const arts=$$(".ayah"),bar=$("#rangebar"),statusEl=$("#status");
  const jump=$("#jump");
  jump.append(h("option",{value:"",text:"Choose a surah"}));
  C.suras.forEach((m,i)=>{const n=i+1;if(n<C.range[0]||n>C.range[1])return;jump.append(h("option",{value:pad(n)+".html",text:`${n}. ${m.name}`,selected:n===s}));});
  jump.addEventListener("change",()=>{if(jump.value)location.href=jump.value;});
  const flags=()=>{root.classList.toggle("no-ar",!isOn("arabic"));root.classList.toggle("no-audio",!isOn("audio"));};

  /* range + deep links: #5 jumps to a verse, #5-9 shows only those verses */
  let from=1,to=size;const fi=h("input",{type:"number",class:"num",min:1,max:size,value:1,"aria-label":"From verse"}),ti=h("input",{type:"number",class:"num",min:1,max:size,value:size,"aria-label":"To verse"});
  const applyRange=(a,b,pushHash)=>{from=a;to=b;fi.value=a;ti.value=b;
    arts.forEach(x=>{const n=+x.dataset.a;x.hidden=n<a||n>b;});
    $$(".juz-mark").forEach(x=>{const n=+x.dataset.a;x.hidden=n<a||n>b;});
    const full=a===1&&b===size;bar.hidden=full;bar.textContent="";
    if(!full){bar.append(a===b?`Showing verse ${a} of ${size}. `:`Showing verses ${a}–${b} of ${size}. `,h("button",{type:"button",class:"link",text:"Show whole surah"}));
      $("button",bar).addEventListener("click",()=>applyRange(1,size,true));}
    if(pushHash)history.replaceState(null,"",full?location.pathname+location.search:`#${a}${a===b?"":"-"+b}`);};
  const focusAyah=n=>{const el=$("#ayah-"+n);if(!el)return;el.scrollIntoView({block:"start"});el.classList.add("flash");setTimeout(()=>el.classList.remove("flash"),1800);};
  const route=()=>{const m=/^#(?:ayah-)?(\d+)(?:-(\d+))?$/.exec(location.hash);if(!m)return;
    let a=+m[1],b=m[2]?+m[2]:a;if(a>b){const t=a;a=b;b=t;}if(a<1||a>size)return;b=Math.min(b,size);
    if(a!==b){applyRange(a,b,false);scrollTo({top:Math.max(0,bar.offsetTop-8)});}else{applyRange(1,size,false);focusAyah(a);}};

  /* bookmarks */
  const bms=()=>{const b=store.get("quran-bookmark",[]);return Array.isArray(b)?b:[];};
  const toggleBm=(a,btn)=>{const l=bms(),i=l.findIndex(b=>b.s===s&&b.a===a);
    if(i>=0){l.splice(i,1);btn.setAttribute("aria-pressed","false");toast("Bookmark removed");}
    else{l.unshift({s,a,n:meta.name,t:Date.now()});btn.setAttribute("aria-pressed","true");toast(`Bookmarked ${s}:${a}`);}
    store.set("quran-bookmark",l);};

  /* audio */
  let au=null;const cont=()=>store.get("quran-cont",true)!==false;
  const setPlay=(art,on)=>{const b=$(".play",art);if(!b)return;const a=+art.dataset.a;b.innerHTML=svg(on?"pause":"play");const l=on?`Pause verse ${a}`:`Play verse ${a}`;b.setAttribute("aria-label",l);b.title=l;};
  const stopAudio=()=>{if(au){au.pause();au.onended=au.onerror=null;au=null;}$$(".ayah.playing").forEach(x=>{x.classList.remove("playing");setPlay(x,false);});};
  const play=a=>{stopAudio();const art=$("#ayah-"+a);if(!art)return;
    au=new Audio(C.audio.replace("{s}",pad(s)).replace("{a}",pad(a)));art.classList.add("playing");setPlay(art,true);
    au.onended=()=>{stopAudio();const nx=$("#ayah-"+(a+1));if(cont()&&nx&&!nx.hidden){play(a+1);nx.scrollIntoView({block:"center",behavior:"smooth"});}};
    au.onerror=()=>{stopAudio();toast("Audio could not be loaded. Check your connection.");};
    au.play().catch(()=>{stopAudio();toast("Couldn’t start audio.");});};

  const verseText=art=>{const a=+art.dataset.a,L=[`${meta.name} (${s}:${a})`];
    if(isOn("arabic"))L.push($(".ar",art).textContent);
    $$(".tr",art).forEach(t=>L.push($("h3",t).firstChild.textContent+": "+$("p",t).textContent));return L.join("\n");};
  arts.forEach(art=>{const a=+art.dataset.a,box=h("div",{class:"actions"});
    box.append(
      iconBtn("play","play",`Play verse ${a}`,()=>{if(au&&art.classList.contains("playing"))stopAudio();else play(a);}),
      (()=>{const b=iconBtn("bm","bookmark",`Bookmark verse ${a}`,b=>toggleBm(a,b));b.setAttribute("aria-pressed",String(bms().some(x=>x.s===s&&x.a===a)));return b;})(),
      iconBtn("cp","copy",`Copy verse ${a} text`,async()=>toast(await copy(verseText(art))?"Verse copied":"Couldn’t copy")),
      iconBtn("ln","link",`Copy link to verse ${a}`,async()=>toast(await copy(location.href.split("#")[0]+"#"+a)?"Link copied":"Couldn’t copy")));
    $(".ayah-head",art).append(box);});

  /* on-demand editions */
  const trNode=(t,text)=>h("section",{class:"tr","data-t":t.id,"data-kind":t.kind,lang:t.lang,dir:t.rtl?"rtl":false},
    h("h3",{},t.full,t.tag?h("span",{class:"tag",text:t.tag}):null),h("p",{text}));
  const place=(art,t,text)=>{if(!text||$(`.tr[data-t="${t.id}"]`,art))return;
    const list=$(".tr-list",art),ref=[...list.children].find(c=>ORD[c.dataset.t]>ORD[t.id]);list.insertBefore(trNode(t,text),ref||null);};
  const sync=async()=>{
    $$(".tr[data-t]").forEach(n=>{if(!isOn(n.dataset.t))n.remove();});
    const need=C.tr.filter(t=>t.id!=="arabic"&&isOn(t.id)&&!$(`.tr[data-t="${t.id}"]`));
    if(!need.length){statusEl.textContent="";return;}
    statusEl.textContent="Loading…";
    const res=await Promise.all(need.map(t=>load(`surah/${t.id}/${pad(s)}`).then(a=>[t,a],()=>[t,null])));
    const fails=[];
    res.forEach(([t,arr])=>{if(!arr){fails.push(t.label);return;}if(!isOn(t.id))return;arts.forEach(art=>place(art,t,arr[+art.dataset.a-1]));});
    statusEl.textContent=fails.length?`Couldn’t load ${fails.join(", ")}. Check your connection and try again.`:"";};

  /* display panel */
  const body=$("#panel-body");body.textContent="";
  const go=h("button",{type:"button",class:"btn small",text:"Show"});
  go.addEventListener("click",()=>{let a=parseInt(fi.value,10)||1,b=parseInt(ti.value,10)||size;if(a>b)[a,b]=[b,a];applyRange(Math.max(1,a),Math.min(size,b),true);});
  const autoplay=h("input",{type:"checkbox"});autoplay.checked=cont();autoplay.addEventListener("change",()=>store.set("quran-cont",autoplay.checked));
  const chipBox=h("div");
  body.append(sliderRow("Translation text size","tx",0.85,1.6,0.05,1),sliderRow("Arabic text size","ar",1.4,3.4,0.1,2),
    h("div",{class:"row"},h("span",{text:"Show verses"}),fi,"to",ti,go),
    h("label",{class:"radio"},autoplay,"Play the next verse automatically"),
    h("h2",{text:"Shown with each verse"}),chipBox);
  chips(chipBox,{audio:true,isOn,set:setOn,change:()=>{flags();sync();}});

  /* reading position */
  let last=1,tm;const save=()=>store.set("quran-history",{s,a:last,n:meta.name,t:Date.now()});save();
  if("IntersectionObserver"in window){const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting)last=+e.target.dataset.a;});clearTimeout(tm);tm=setTimeout(save,1000);},{rootMargin:"0px 0px -75% 0px"});arts.forEach(a=>io.observe(a));}
  addEventListener("pagehide",save);addEventListener("hashchange",route);
  flags();sync();route();
}

/* ---------- index ---------- */
function initIndex(){
  const f=$("#filter"),items=$$("#sgrid li").map(li=>({li,k:norm(li.dataset.k)}));
  f.addEventListener("input",()=>{const q=norm(f.value).split(/\s+/).filter(Boolean);let n=0;
    items.forEach(({li,k})=>{const ok=q.every(t=>k.includes(t));li.hidden=!ok;if(ok)n++;});
    $("#fcount").textContent=q.length?`${n} surah${n===1?"":"s"} found`:"";});
  const hist=store.get("quran-history",null),res=$("#resume");
  if(hist&&hist.s&&C.suras[hist.s-1]){res.hidden=false;
    res.append(h("h2",{text:"Continue reading"}),h("a",{class:"btn",href:`${pad(hist.s)}.html#${hist.a||1}`,text:`${sname(hist.s)} ${hist.s}:${hist.a||1}, ${ago(hist.t)}`}));}
  const bm=store.get("quran-bookmark",[]);
  if(Array.isArray(bm)&&bm.length){res.hidden=false;res.append(" ",h("a",{class:"btn",href:"bookmarks.html",text:`${bm.length} bookmark${bm.length===1?"":"s"}`}));}
  if(!store.get("quran-seen",false)){const w=$("#welcome");w.hidden=false;$("#welcome-x").addEventListener("click",()=>{store.set("quran-seen",true);w.hidden=true;});}
}

/* ---------- settings ---------- */
function initConfig(){
  const build=()=>chips($("#cfg-chips"),{audio:true,isOn,set:setOn});build();
  $("#cfg-sliders").append(sliderRow("Translation text size","tx",0.85,1.6,0.05,1),sliderRow("Arabic text size","ar",1.4,3.4,0.1,2));
  $$("input[name=theme]").forEach(r=>{r.checked=r.value===(ui.theme||"auto");
    r.addEventListener("change",()=>{ui.theme=r.value;store.set("quran-ui",ui);applyUi();});});
  $("#cfg-reset").addEventListener("click",()=>{store.del("quran-cf");prefs={};build();toast("Defaults restored");});
  $("#cfg-clear").addEventListener("click",()=>{if(confirm("Remove all bookmarks and reading history from this browser?")){store.del("quran-bookmark");store.del("quran-history");toast("Cleared");}});
}

/* ---------- bookmarks ---------- */
function initBookmarks(){
  const list=$("#bm-list"),count=$("#bm-count");
  const get=()=>{const b=store.get("quran-bookmark",[]);return Array.isArray(b)?b:[];};
  const render=()=>{const b=get();list.textContent="";
    count.textContent=b.length?`${b.length} bookmark${b.length===1?"":"s"}`:"";
    if(!b.length){list.append(h("li",{text:"No bookmarks yet. Use the bookmark button on any verse."}));return;}
    b.forEach((x,i)=>{const rm=h("button",{type:"button",class:"btn small",text:"Remove","aria-label":`Remove bookmark ${x.s}:${x.a}`});
      rm.addEventListener("click",()=>{const l=get();l.splice(i,1);store.set("quran-bookmark",l);render();});
      list.append(h("li",{},h("span",{},h("a",{href:`${pad(x.s)}.html#${x.a}`,text:`${sname(x.s)} ${x.s}:${x.a}`}),h("br"),h("small",{class:"muted",text:ago(x.t)})),rm));});};
  $("#bm-clear").addEventListener("click",()=>{if(confirm("Remove all bookmarks?")){store.set("quran-bookmark",[]);render();}});
  $("#bm-export").addEventListener("click",()=>{const u=URL.createObjectURL(new Blob([JSON.stringify(get(),null,2)],{type:"application/json"}));
    const a=h("a",{href:u,download:"quran-bookmarks.json"});document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),500);});
  $("#bm-import").addEventListener("change",e=>{const f=e.target.files[0];if(!f)return;const r=new FileReader();
    r.onload=()=>{try{const d=JSON.parse(r.result);if(!Array.isArray(d))throw new Error("The file is not a list of bookmarks.");
      const m=new Map(get().map(b=>[b.s+":"+b.a,b]));
      d.filter(b=>b&&b.s>=1&&b.s<=114&&b.a>=1).forEach(b=>m.set(b.s+":"+b.a,{s:+b.s,a:+b.a,n:b.n||"",t:+b.t||Date.now()}));
      store.set("quran-bookmark",[...m.values()].sort((a,b)=>b.t-a.t));render();toast("Imported");}catch(err){toast("Import failed: "+err.message);}e.target.value="";};
    r.readAsText(f);});
  render();
}

/* ---------- search ---------- */
function initSearch(){
  const form=$("#sform"),q=$("#q"),status=$("#status"),list=$("#results"),more=$("#more");
  const fields=C.tr.filter(t=>isOn(t.id)),names=fields.map(f=>f.full);
  $("#scope").append("Searching in: ",names.length?(names.length>6?`${names.slice(0,5).join(", ")} and ${names.length-5} more`:names.join(", ")):"nothing selected"," ",h("a",{href:"config.html",text:"Change"}));
  const S=[],A=[];C.suras.forEach((m,i)=>{for(let a=1;a<=m.size;a++){S.push(i+1);A.push(a);}});
  const nameN=C.suras.map(m=>norm(m.name+" "+m.meaning)),ncache={};
  let hits=[],shown=0,terms=[],arrs=[];
  const highlight=(text,ts)=>{const nm=normMap(text),R=[];
    ts.forEach(t=>{let i=0;while((i=nm.t.indexOf(t,i))!==-1){R.push([nm.m[i],nm.m[i+t.length-1]+1]);i+=t.length;}});
    R.sort((x,y)=>x[0]-y[0]);const out=document.createDocumentFragment();let pos=0;
    R.forEach(r=>{if(r[1]<=pos)return;const s=Math.max(r[0],pos);if(s>pos)out.append(text.slice(pos,s));out.append(h("mark",{text:text.slice(s,r[1])}));pos=r[1];});
    if(pos<text.length)out.append(text.slice(pos));return out;};
  const render=()=>{const end=Math.min(shown+20,hits.length);
    for(;shown<end;shown++){const i=hits[shown],s=S[i],a=A[i];
      const card=h("li",{class:"hit"},h("div",{class:"hit-head"},h("strong",{text:`${sname(s)} ${s}:${a}`}),h("a",{href:`${pad(s)}.html#${a}`,text:"Open verse"})));
      fields.forEach((f,k)=>{const t=arrs[k][i];if(t)card.append(h("p",{class:"hit-text",lang:f.lang,dir:f.rtl?"rtl":false},h("span",{class:"hit-label",text:f.full}),highlight(t,terms)));});
      list.append(card);}
    status.textContent=`${hits.length} verse${hits.length===1?"":"s"} found${hits.length>shown?`, showing ${shown}`:""}.`;
    more.hidden=shown>=hits.length;more.textContent=`Show more (${hits.length-shown} left)`;};
  const run=async()=>{const text=q.value.trim();list.textContent="";more.hidden=true;hits=[];shown=0;
    history.replaceState(null,"",text?"?q="+encodeURIComponent(text):location.pathname);
    if(!text){status.textContent="";return;}
    const ref=/^(\d{1,3})\s*[:.]\s*(\d{1,3})$/.exec(text);
    if(ref&&+ref[1]>=1&&+ref[1]<=114&&+ref[2]>=1&&+ref[2]<=C.suras[ref[1]-1].size)
      list.append(h("li",{class:"hit"},h("a",{href:`${pad(+ref[1])}.html#${+ref[2]}`,text:`Go to ${sname(+ref[1])} ${+ref[1]}:${+ref[2]}`})));
    terms=norm(text).split(/\s+/).filter(Boolean);if(!terms.length)return;
    nameN.forEach((n,i)=>{if(terms.every(t=>n.includes(t))&&list.children.length<4)list.append(h("li",{class:"hit"},h("a",{href:pad(i+1)+".html",text:`Surah ${i+1}: ${C.suras[i].name} (${C.suras[i].meaning})`})));});
    if(!fields.length){status.textContent="Select at least one edition in Settings to search verse text.";return;}
    status.textContent="Searching…";
    try{arrs=await Promise.all(fields.map(f=>load("search/"+f.id)));}catch{status.textContent="Couldn’t load search data. Check your connection and try again.";return;}
    fields.forEach((f,k)=>{if(!ncache[f.id])ncache[f.id]=arrs[k].map(norm);});
    for(let i=0;i<S.length;i++){const hay=fields.map(f=>ncache[f.id][i]).join(" ");if(terms.every(t=>hay.includes(t)))hits.push(i);}
    if(!hits.length){status.textContent="No verses found. Try fewer or simpler words.";return;}
    render();};
  form.addEventListener("submit",e=>{e.preventDefault();run();});
  more.addEventListener("click",render);
  const init=new URLSearchParams(location.search).get("q");if(init){q.value=init;run();}
}

/* ---------- offline ZIP ---------- */
function initDownload(){
  const sel=Object.fromEntries(C.tr.map(t=>[t.id,!!C.defaults[t.id]]));
  chips($("#dl-chips"),{isOn:id=>sel[id],set:(id,v)=>{sel[id]=v;}});
  const st=$("#dl-status"),prog=$("#dl-prog"),btn=$("#dl-go");
  btn.addEventListener("click",async()=>{
    if(typeof JSZip==="undefined"){st.textContent="The ZIP library could not be loaded. Check your connection.";return;}
    const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
    const from=clamp(parseInt($("#dl-from").value,10)||1,1,114),to=clamp(parseInt($("#dl-to").value,10)||114,from,114);
    const ids=C.tr.filter(t=>sel[t.id]).map(t=>t.id);
    if(!ids.length){st.textContent="Select at least one edition.";return;}
    const withSearch=$("#dl-search").checked;
    const optional=["index","bookmarks","config","sources","license"].filter(p=>$("#dl-p-"+p).checked);
    const included=new Set(optional.map(p=>p+".html"));if(withSearch)included.add("search.html");
    const excluded=new Set(["index","bookmarks","config","sources","license","search","download"].map(p=>p+".html").filter(p=>!included.has(p)));
    const jobs=[{p:"assets/style.css"},{p:"assets/app.js"},{p:"assets/catalog.js",cat:1}];
    for(let s=from;s<=to;s++){jobs.push({p:pad(s)+".html",page:1});ids.forEach(id=>jobs.push({p:`data/surah/${id}/${pad(s)}.js`}));}
    included.forEach(p=>jobs.push({p,page:1}));
    if(withSearch)ids.forEach(id=>jobs.push({p:`data/search/${id}.js`}));
    btn.disabled=true;prog.hidden=false;prog.value=0;
    const zip=new JSZip(),missing=[];let done=0;
    const clean=doc=>{$$("a[href]",doc).forEach(a=>{const href=a.getAttribute("href"),m=/^(\d{3})\.html/.exec(href),pg=href.split("#")[0].split("?")[0];
      if((m&&(+m[1]<from||+m[1]>to))||excluded.has(pg)){const li=a.closest("li");(li&&$$("a",li).length===1?li:a).remove();}});
      $$(".tr[data-t]",doc).forEach(n=>{if(!ids.includes(n.dataset.t))n.remove();});};
    const run=async j=>{try{const r=await fetch(j.p);if(!r.ok)throw 0;let t=await r.text();
      if(j.page){const d=new DOMParser().parseFromString(t,"text/html");clean(d);t="<!DOCTYPE html>\n"+d.documentElement.outerHTML;}
      if(j.cat){const c=JSON.parse(t.slice(t.indexOf("=")+1).replace(/;\s*$/,""));
        c.tr=c.tr.filter(x=>ids.includes(x.id));c.range=[from,to];
        const keep=Object.keys(c.defaults).filter(k=>k==="audio"||ids.includes(k)&&c.defaults[k]);
        c.defaults=Object.fromEntries(keep.map(k=>[k,true]));
        if(!keep.some(k=>k!=="audio"))ids.slice(0,3).forEach(k=>c.defaults[k]=true);
        t="window.QURAN_CATALOG="+JSON.stringify(c)+";\n";}
      zip.file(j.p,t);}catch{missing.push(j.p);}
      prog.value=Math.round(++done*100/jobs.length);st.textContent=`Fetched ${done} of ${jobs.length} files`;};
    const queue=jobs.slice();await Promise.all(Array.from({length:8},async()=>{while(queue.length)await run(queue.shift());}));
    st.textContent="Compressing…";
    const blob=await zip.generateAsync({type:"blob",compression:"DEFLATE"});
    const u=URL.createObjectURL(blob),a=h("a",{href:u,download:"quran-reader-offline.zip"});document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),2000);
    st.textContent=missing.length?`Done, but ${missing.length} file(s) could not be fetched (for example ${missing[0]}).`:"Done. Open index.html from the extracted folder.";
    btn.disabled=false;});
}

/* ---------- boot ---------- */
applyUi();
const top=h("button",{class:"totop",type:"button","aria-label":"Back to top",html:"&#8593;"});
top.hidden=true;top.addEventListener("click",()=>scrollTo({top:0}));document.body.append(top);
addEventListener("scroll",()=>{top.hidden=scrollY<700;},{passive:true});
({reader:initReader,index:initIndex,search:initSearch,config:initConfig,bookmarks:initBookmarks,download:initDownload})[document.body.dataset.page]?.();
})();
"""


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".", help="repository root (default: .)")
    ap.add_argument("--out", default="docs", help="output folder inside root")
    ap.add_argument("--no-fonts", action="store_true",
                    help="do not link Google Fonts (privacy / fully self-hosted)")
    ap.add_argument("--clean", action="store_true", help="delete legacy docs/sd/ folder")
    args = ap.parse_args(argv)
    root, out = Path(args.root).resolve(), Path(args.root).resolve() / args.out
    CFG["fonts"] = not args.no_fonts

    # 1. load editions; drop any that are completely missing
    data: dict[str, Verses] = {}
    sources: list[Source] = []
    print("Loading editions")
    for src in CATALOG:
        d = load_source(root, src)
        if not d:
            print(f"  WARN  {src.id:<24} source file missing, edition skipped", file=sys.stderr)
            continue
        data[src.id] = d
        sources.append(src)
        flag = "" if len(d) == TOTAL_AYAT else "   <-- incomplete"
        print(f"  {src.id:<24} {len(d):>5}/{TOTAL_AYAT}{flag}")
    if "arabic" not in data:
        print("ERROR: the Arabic text (output/quran_arabic.txt) is required.", file=sys.stderr)
        return 1

    changed = 0

    def put(path: Path, text: str):
        nonlocal changed
        changed += write(path, text)

    defaults = [s for s in sources if s.default and s.id != "arabic"]

    # 2. shared assets
    catalog = {
        "suras": [{"name": n, "meaning": m, "type": "D" if i in MEDINAN else "M",
                   "order": REV_ORDER[i - 1], "juz": juz_span(i), "size": SURA_SIZE[i - 1]}
                  for i, (n, m) in enumerate(SURA_NAMES, 1)],
        "tr": [{"id": s.id, "label": s.label, "full": s.full, "lang": s.lang,
                "group": s.group, "kind": s.kind, "tag": s.tag, "rtl": s.rtl}
               for s in sources if s.id != "arabic" or True],
        "defaults": {**{s.id: s.default for s in sources}, "audio": True},
        "audio": AUDIO_URL,
        "range": [1, 114],
    }
    put(out / "assets" / "catalog.js", "window.QURAN_CATALOG=" + js_json(catalog) + ";\n")
    put(out / "assets" / "style.css", STYLE_CSS.strip() + "\n")
    put(out / "assets" / "app.js", APP_JS.strip() + "\n")

    # 3. data files (per surah per edition, plus whole-Qur'an files for search)
    for src in sources:
        d = data[src.id]
        for s, size in enumerate(SURA_SIZE, 1):
            arr = [d.get((s, a), "") for a in range(1, size + 1)]
            put(out / "data" / "surah" / src.id / f"{s:03d}.js",
                f'QData("surah/{src.id}/{s:03d}",{js_json(arr)});\n')
        full = [d.get((s, a), "") for s, size in enumerate(SURA_SIZE, 1)
                for a in range(1, size + 1)]
        put(out / "data" / "search" / f"{src.id}.js",
            f'QData("search/{src.id}",{js_json(full)});\n')
    if args.clean and (out / "sd").exists():
        shutil.rmtree(out / "sd")
        print("Removed legacy folder docs/sd/")

    # 4. pages
    for s in range(1, 115):
        n, m = SURA_NAMES[s - 1]
        put(out / f"{s:03d}.html", page(
            f"Surah {s}: {n} ({m}) | Qur’an Reader", surah_body(s, data, defaults), "reader",
            desc=f"Surah {s}, {n} ({m}): Arabic text, transliteration, audio and translations.",
            sura=s))
    lic = root / "LICENSE"
    lic_text = lic.read_text(encoding="utf-8") if lic.exists() else "(LICENSE file not found)"
    put(out / "index.html", page("Qur’an Reader", index_body(sources), "index"))
    put(out / "search.html", page("Search | Qur’an Reader", search_body(), "search"))
    put(out / "config.html", page("Settings | Qur’an Reader", config_body(), "config"))
    put(out / "bookmarks.html", page("Bookmarks | Qur’an Reader", bookmarks_body(), "bookmarks"))
    put(out / "sources.html", page("Sources | Qur’an Reader", sources_body(sources), "sources"))
    put(out / "license.html", page("License | Qur’an Reader", license_body(lic_text), "license"))
    put(out / "download.html", page(
        "Offline copy | Qur’an Reader", download_body(), "download",
        foot_extra='<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js" defer></script>\n'))

    print(f"Done: {len(sources)} editions, 114 surah pages, {changed} files written/changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
