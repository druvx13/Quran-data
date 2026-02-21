#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate /docs HTML pages for the Qur'an website.

Run from the repository root:
    python3 src/gendocshtml.py

Sources used:
  - trans/en.transliteration.txt      : sura|ayah|transliteration (with HTML tags)
  - output/quran_translit_unicode.txt : [sura:ayah] Unicode transliteration (Quran Unicode Project)
  - output/quran_hindi_farooq.txt     : [sura:ayah] Hindi translation (Farooq Khan)
  - output/quran_hindi_suhail.txt     : [sura:ayah] Hindi translation (Suhail)
  - output/quran_hindi_mokhtasar.txt  : [sura:ayah] Hindi Tafsir (Al-Mokhtasar)
  - output/quran_english_abridged.txt : [sura:ayah] English Explanation (Abridged)
  - data/en.pickthall.txt             : one English line per ayah (Pickthall)
  - output/quran_english_yusufali.txt : [sura:ayah] English translation (Yusuf Ali)
  - output/quran_english_sahih.txt    : [sura:ayah] English translation (Saheeh International)
  - output/quran_arabic.txt           : [sura:ayah] Arabic text (Uthmani script)
"""

import os
import re

# ---------------------------------------------------------------------------
# Surah metadata
# ---------------------------------------------------------------------------
SURA_SIZE = [7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,
             110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,
             182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,
             29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,
             40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,
             11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]

SURA_NAME = [
    "Al-Fatihah (The Opening)","Al-Baqarah (The Cow)",
    "Al-'Imran (The Family of Amran)","An-Nisa' (The Women)",
    "Al-Ma'idah (The Food)","Al-An'am (The Cattle)",
    "Al-A'raf (The Elevated Places)","Al-Anfal (Voluntary Gifts)",
    "Al-Bara'at / At-Taubah(The Immunity)","Yunus (Jonah)","Hud (Hud)",
    "Yusuf (Joseph)","Ar-Ra'd (The Thunder)","Ibrahim (Abraham)",
    "Al-Hijr (The Rock)","An-Nahl (The Bee)","Bani Isra'il (The Israelites)",
    "Al-Kahf (The Cave)","Maryam (Mary)","Ta Ha (Ta Ha)",
    "Al-Anbiya' (The Prophets)","Al-Hajj (The Pilgrimage)",
    "Al-Mu'minun (The Believers)","An-Nur (The Light)",
    "Al-Furqan (The Discrimination)","Ash-Shu'ara' (The Poets)",
    "An-Naml (The Naml)","Al-Qasas (The Narrative)",
    "Al-'Ankabut (The Spider)","Ar-Rum (The Romans)","Luqman (Luqman)",
    "As-Sajdah (The Adoration)","Al-Ahzab (The Allies)",
    "Al-Saba' (The Saba')","Al-Fatir (The Originator)","Ya Sin (Ya Sin)",
    "As-Saffat (Those Ranging in Ranks)","Sad (Sad)",
    "Az-Zumar (The Companies)","Al-Mu'min (The Believer)","Ha Mim (Ha Mim)",
    "Ash-Shura (Counsel)","Az-Zukhruf (Gold)","Ad-Dukhan (The Drought)",
    "Al-Jathiyah (The Kneeling)","Al-Ahqaf (The Sandhills)",
    "Muhammad (Muhammad)","Al-Fath (The Victory)",
    "Al-Hujurat (The Apartments)","Qaf (Qaf)",
    "Ad-Dhariyat (The Scatterers)","At-Tur (The Mountain)",
    "An-Najm (The Star)","Al-Qamar (The Moon)",
    "Ar-Rahman (The Beneficent)","Al-Waqi'ah (The Event)",
    "Al-Hadid (Iron)","Al-Mujadilah (The Pleading Woman)",
    "Al-Hashr (The Banishment)",
    "Al-Mumtahanah (The Woman who is Examined)","As-Saff (The Ranks)",
    "Al-Jumu'ah (The Congregation)","Al-Munafiqun (The Hypocrites)",
    "At-Taghabun (The Manifestation of Losses)","At-Talaq (Divorce)",
    "At-Tahrim (The Prohibition)","Al-Mulk (The Kingdom)",
    "Al-Qalam (The Pen)","Al-Haqqah (The Sure Truth)",
    "Al-Ma'arij (The Ways of Ascent)","Nuh (Noah)","Al-Jinn (The Jinn)",
    "Al-Muzzammil (The One Covering Himself)",
    "Al-Muddaththir (The One Wrapping Himself Up)",
    "Al-Qiyamah (The Resurrection)","Al-Insan (The Man)",
    "Al-Mursalat (Those Sent Forth)","An-Naba' (The Announcement)",
    "An-Nazi'at (Those Who Yearn)","'Abasa (He Frowned)",
    "At-Takwir (The Folding Up)","Al-Infitar (The Cleaving)",
    "At-Tatfif (Default in Duty)","Al-Inshiqaq (The Bursting Asunder)",
    "Al-Buruj (The Stars)","At-Tariq (The Comer by Night)",
    "Al-A'la (The Most High)","Al-Ghashiyah (The Overwhelming Event)",
    "Al-Fajr (The Daybreak)","Al-Balad (The City)","Ash-Shams (The Sun)",
    "Al-Lail (The Night)","Ad-Duha (The Brightness of the Day)",
    "Al-Inshirah (The Expansion)","At-Tin (The Fig)",
    "Al-'Alaq (The Clot)","Al-Qadr (The Majesty)",
    "Al-Bayyinah (The Clear Evidence)","Al-Zilzal (The Shaking)",
    "Al-'Adiyat (The Assaulters)","Al-Qari'ah (The Calamity)",
    "At-Takathur (The Abundance of Wealth)","Al-'Asr (The Time)",
    "Al-Humazah (The Slanderer)","Al-Fil (The Elephant)",
    "Al-Quraish (The Quraish)","Al-Ma'un (Acts of Kindness)",
    "Al-Kauthar (The Abundance of Good)","Al-Kafirun (The Disbelievers)",
    "An-Nasr (The Help)","Al-Lahab (The Flame)","Al-Ikhlas (The Unity)",
    "Al-Falaq (The Dawn)","An-Nas (The Men)",
]

# ---------------------------------------------------------------------------
# Load transliteration  trans/en.transliteration.txt
# Format: sura|ayah|text_with_html_tags  (comment lines start with #)
# ---------------------------------------------------------------------------
translit = {}
with open('trans/en.transliteration.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        parts = line.split('|', 2)
        if len(parts) == 3:
            translit[(int(parts[0]), int(parts[1]))] = parts[2]

# ---------------------------------------------------------------------------
# Load Hindi translation  quran_hindi_farooq.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
hindi = {}
with open('output/quran_hindi_farooq.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            hindi[(int(m.group(1)), int(m.group(2)))] = m.group(3)

# ---------------------------------------------------------------------------
# Load Arabic text  quran_arabic.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
arabic = {}
with open('output/quran_arabic.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            arabic[(int(m.group(1)), int(m.group(2)))] = m.group(3)

# ---------------------------------------------------------------------------
# Load Pickthall translation  en.pickthall.txt  (sequential, one line/ayah)
# ---------------------------------------------------------------------------
pickthall = {}
with open('data/en.pickthall.txt', 'r', encoding='utf-8') as f:
    for sura_idx, size in enumerate(SURA_SIZE, 1):
        for ayah in range(1, size + 1):
            pickthall[(sura_idx, ayah)] = f.readline().rstrip('\n')

# ---------------------------------------------------------------------------
# Load Yusuf Ali English translation  quran_english_yusufali.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
yusufali = {}
with open('output/quran_english_yusufali.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            yusufali[(int(m.group(1)), int(m.group(2)))] = m.group(3)

# ---------------------------------------------------------------------------
# Load Saheeh International translation  quran_english_sahih.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
sahih = {}
with open('output/quran_english_sahih.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            sahih[(int(m.group(1)), int(m.group(2)))] = m.group(3)

# ---------------------------------------------------------------------------
# Load Suhail Hindi translation  quran_hindi_suhail.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
hindi_suhail = {}
with open('output/quran_hindi_suhail.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            hindi_suhail[(int(m.group(1)), int(m.group(2)))] = m.group(3)

# ---------------------------------------------------------------------------
# Load Hindi Tafsir (Mokhtasar)  quran_hindi_mokhtasar.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
hindi_mokhtasar = {}
with open('output/quran_hindi_mokhtasar.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            hindi_mokhtasar[(int(m.group(1)), int(m.group(2)))] = m.group(3)

# ---------------------------------------------------------------------------
# Load English Abridged Explanation  quran_english_abridged.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
eng_abridged = {}
with open('output/quran_english_abridged.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            eng_abridged[(int(m.group(1)), int(m.group(2)))] = m.group(3)

# ---------------------------------------------------------------------------
# Load Unicode transliteration  quran_translit_unicode.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
translit_unicode = {}
with open('output/quran_translit_unicode.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            translit_unicode[(int(m.group(1)), int(m.group(2)))] = m.group(3)

# ---------------------------------------------------------------------------
# HTML template helpers
# ---------------------------------------------------------------------------
CSS = """\
*,*::before,*::after{box-sizing:border-box}
body{margin:0;padding:0;font-family:system-ui,Arial,Helvetica,sans-serif;
  font-size:16px;background:#fff;color:#111;line-height:1.6}
header{background:#1a3a5c;color:#fff;padding:12px 16px;position:sticky;top:0;z-index:10}
header a{color:#ffd54f;text-decoration:none;font-weight:bold;font-size:1.1em}
header a:hover{text-decoration:underline}
main{padding:16px;max-width:900px;margin:0 auto}
h1{font-size:1.4em;margin:0 0 12px}
h2{font-size:1.2em;color:#1a3a5c;margin:20px 0 8px}
.surah-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;margin-top:16px}
.surah-grid a{display:block;padding:10px 12px;background:#f0f4f8;border:1px solid #ccd6e0;
  border-radius:6px;text-decoration:none;color:#1a3a5c;font-size:.95em}
.surah-grid a:hover{background:#dde8f2}
.notice{background:#fff8e1;border-left:4px solid #ffd54f;padding:12px 16px;margin-bottom:20px;font-size:.95em}
.notice summary{cursor:pointer}
.table-wrap{overflow-x:auto;width:100%}
table{width:100%;border-collapse:collapse;margin-bottom:24px}
th{background:#1a3a5c;color:#fff;padding:10px 12px;text-align:left;font-size:.9em}
td{padding:8px 12px;vertical-align:top;border:1px solid #ccd6e0}
.ayah-sep td{background:#1a3a5c;color:#fff;font-weight:bold;font-size:.9em;padding:6px 12px;border-color:#1a3a5c}
.label{color:#888;font-size:.82em;white-space:nowrap;width:110px}
.translit td{background:#f0f4f8}
.translit-unicode td{background:#e8eaf6}
.trans td{background:#fff}
.trans-yusuf td{background:#e8f5e9}
.trans-sahih td{background:#e3f2fd}
.hindi td{background:#f5f0ff}
.hindi-suhail td{background:#fff3e0}
.hindi-mokhtasar td{background:#e8f5e0}
.eng-abridged td{background:#e8f4fd}
.audio td{background:#e0f7fa}
.audio-player{width:100%;max-width:420px;height:36px;vertical-align:middle}
.translit-text{font-style:normal;font-weight:600}
.translit-unicode-text{font-style:normal;font-weight:600;color:#283593}
.hindi-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#3a2a6c}
.hindi-suhail-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#5d4037}
.hindi-mokhtasar-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#1b5e20}
.arabic td{background:#fff8e1}
.arabic-text{font-family:'Scheherazade New','Amiri','Traditional Arabic',serif;font-size:1.5em;direction:rtl;text-align:right;line-height:2}
nav.chapter-nav{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;
  padding:16px 0;margin-top:8px;border-top:1px solid #ccd6e0}
nav.chapter-nav a{display:inline-block;padding:8px 16px;background:#1a3a5c;color:#fff;
  border-radius:4px;text-decoration:none;font-size:.95em}
nav.chapter-nav a:hover{background:#2a5a8c}
footer{text-align:center;padding:20px;font-size:.85em;color:#666;border-top:1px solid #e0e0e0;margin-top:32px}"""

HEADER_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Surah {num}: {name}</title>
<style>
{css}
</style>
</head>
<body>
<header><a href="index.html">&#8962; Index</a></header>
<main>
<h1>Surah {num}: {name}</h1>
<div class='table-wrap'><table><thead><tr><th colspan='2'>Ayah &nbsp;&mdash;&nbsp; Arabic (Uthmani) &nbsp;/&nbsp; Audio (Mishary Alafasy) &nbsp;/&nbsp; Transliteration (Tanzil.net &amp; Unicode Project) &nbsp;/&nbsp; English (Pickthall, Yusuf Ali &amp; Saheeh Int&#x2019;l) &nbsp;/&nbsp; English Explanation (Abridged) &nbsp;/&nbsp; &#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2309;&#2344;&#2369;&#2357;&#2366;&#2342; (Farooq Khan &amp; Suhail) &nbsp;/&nbsp; &#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2340;&#2347;&#2381;&#2360;&#2368;&#2352; (Al-Mokhtasar)</th></tr></thead><tbody>
"""

FOOTER_HTML = """\
</tbody></table></div>
{nav}
</main>
<footer>Arabic Text: Standard Arabic Uthmani Script &nbsp;|&nbsp; Audio: Mishary Rashid Alafasy (versebyversequran.com) &nbsp;|&nbsp; Tanzil.net Transliteration &amp; Pickthall Translation &mdash; Public Domain &nbsp;|&nbsp; Quran Unicode Project Transliteration &nbsp;|&nbsp; Yusuf Ali Translation &mdash; Public Domain &nbsp;|&nbsp; Saheeh International Translation &nbsp;|&nbsp; English Explanation: Abridged Explanation of the Quran &nbsp;|&nbsp; Hindi: Farooq Khan &amp; Muhammad Ahmed &nbsp;|&nbsp; Hindi: Suhel Farooq Khan &amp; Saifur Rahman Nadwi &nbsp;|&nbsp; Hindi Tafsir: Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim</footer>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Generate surah HTML files
# ---------------------------------------------------------------------------
docs_dir = 'docs'
os.makedirs(docs_dir, exist_ok=True)

for sura_idx in range(1, 115):
    size = SURA_SIZE[sura_idx - 1]
    name = SURA_NAME[sura_idx - 1]
    filename = os.path.join(docs_dir, '%03d.html' % sura_idx)

    prev_link = ''
    next_link = ''
    if sura_idx > 1:
        prev_link = "<a href='%03d.html'>&laquo; Surah %d</a>" % (sura_idx - 1, sura_idx - 1)
    if sura_idx < 114:
        next_link = "<a href='%03d.html'>Surah %d &raquo;</a>" % (sura_idx + 1, sura_idx + 1)
    nav = "<nav class='chapter-nav'><span>%s</span><span>%s</span></nav>" % (prev_link, next_link)

    with open(filename, 'w', encoding='utf-8') as out:
        out.write(HEADER_HTML.format(num=sura_idx, name=name, css=CSS))
        for ayah in range(1, size + 1):
            tl = translit.get((sura_idx, ayah), '')
            tu = translit_unicode.get((sura_idx, ayah), '')
            pk = pickthall.get((sura_idx, ayah), '')
            ya = yusufali.get((sura_idx, ayah), '')
            sa = sahih.get((sura_idx, ayah), '')
            hi = hindi.get((sura_idx, ayah), '')
            hs = hindi_suhail.get((sura_idx, ayah), '')
            hm = hindi_mokhtasar.get((sura_idx, ayah), '')
            ea = eng_abridged.get((sura_idx, ayah), '')
            ar = arabic.get((sura_idx, ayah), '')
            out.write(
                "<tr class='ayah-sep'><td colspan='2'>Ayah %d</td></tr>\n"
                "<tr class='arabic'><td class='label'>&#1593;&#1614;&#1585;&#1614;&#1576;&#1616;&#1610;</td><td class='arabic-text'>%s</td></tr>\n"
                "<tr class='audio'><td class='label'>Audio (Alafasy)</td><td><audio class='audio-player' controls preload='none' src='https://media.githubusercontent.com/media/druvx13/Quran-data/cairo/docs/audio/Alafasy/%03d%03d.mp3'></audio></td></tr>\n"
                "<tr class='translit'><td class='label'>Transliteration (Tanzil)</td><td class='translit-text'>%s</td></tr>\n"
                "<tr class='translit-unicode'><td class='label'>Transliteration (Unicode)</td><td class='translit-unicode-text'>%s</td></tr>\n"
                "<tr class='trans'><td class='label'>English (Pickthall)</td><td>%s</td></tr>\n"
                "<tr class='trans-yusuf'><td class='label'>English (Yusuf Ali)</td><td>%s</td></tr>\n"
                "<tr class='trans-sahih'><td class='label'>English (Saheeh Int&#x2019;l)</td><td>%s</td></tr>\n"
                "<tr class='eng-abridged'><td class='label'>English (Abridged Expl.)</td><td>%s</td></tr>\n"
                "<tr class='hindi'><td class='label'>&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; (Farooq)</td><td class='hindi-text'>%s</td></tr>\n"
                "<tr class='hindi-suhail'><td class='label'>&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; (Suhail)</td><td class='hindi-suhail-text'>%s</td></tr>\n"
                "<tr class='hindi-mokhtasar'><td class='label'>&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2340;&#2347;&#2381;&#2360;&#2368;&#2352; (Mokhtasar)</td><td class='hindi-mokhtasar-text'>%s</td></tr>\n"
                % (ayah, ar, sura_idx, ayah, tl, tu, pk, ya, sa, ea, hi, hs, hm)
            )
        out.write(FOOTER_HTML.format(nav=nav))

    print('Written: %s' % filename)

# ---------------------------------------------------------------------------
# Regenerate index.html
# ---------------------------------------------------------------------------
index_path = os.path.join(docs_dir, 'index.html')
with open(index_path, 'w', encoding='utf-8') as out:
    out.write("""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Qur'an &ndash; Transliteration &amp; Translation</title>
<style>
%s
</style>
</head>
<body>
<header><a href="index.html">&#8962; Index</a></header>
<main>
<h1>Qur&#x2019;an &mdash; Arabic, Transliteration, English &amp; Hindi Translation</h1>
<details class="notice">
<summary><strong>Public Domain Notice &amp; Source Attribution</strong></summary>
<em>Arabic Text:</em> Standard Arabic Uthmani Script.<br>
<em>Audio Recitation:</em> Mishary Rashid Alafasy &mdash; via versebyversequran.com (see <a href="audio/Alafasy/000_license.html">license</a>).<br>
<em>Transliteration:</em> Tanzil.net English Transliteration of the Qur&#x2019;an.<br>
<em>Transliteration:</em> Quran Unicode Project (translit_en.txt).<br>
<em>English Translation:</em> Mohammed Marmaduke Pickthall, <em>The Meaning of the Glorious Koran</em> (1930) &mdash; Public Domain.<br>
<em>English Translation:</em> Abdullah Yusuf Ali, <em>The Holy Quran: Text, Translation and Commentary</em> &mdash; Public Domain.<br>
<em>English Translation:</em> Saheeh International.<br>
<em>English Explanation:</em> Abridged Explanation of the Quran.<br>
<em>Hindi Translation (&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2309;&#2344;&#2369;&#2357;&#2366;&#2342;):</em> Muhammad Farooq Khan &amp; Muhammad Ahmed.<br>
<em>Hindi Translation (&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2309;&#2344;&#2369;&#2357;&#2366;&#2342;):</em> Suhel Farooq Khan &amp; Saifur Rahman Nadwi.<br>
<em>Hindi Tafsir (&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2340;&#2347;&#2381;&#2360;&#2368;&#2352;):</em> Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim.<br>
Texts are reproduced verbatim; no alterations have been made.
</details>
<h2>Surahs (Chapters)</h2>
<div class="surah-grid">
""" % CSS)
    for i, name in enumerate(SURA_NAME, 1):
        out.write("<a href='%03d.html'><strong>%d.</strong> %s</a>\n" % (i, i, name))
    out.write("""\
</div>
</main>
<footer>Arabic Text: Standard Arabic Uthmani Script &nbsp;|&nbsp; Audio: Mishary Rashid Alafasy (versebyversequran.com) &nbsp;|&nbsp; Tanzil.net Transliteration &amp; Pickthall Translation &mdash; Public Domain &nbsp;|&nbsp; Quran Unicode Project Transliteration &nbsp;|&nbsp; Yusuf Ali Translation &mdash; Public Domain &nbsp;|&nbsp; Saheeh International Translation &nbsp;|&nbsp; English Explanation: Abridged Explanation of the Quran &nbsp;|&nbsp; Hindi: Farooq Khan &amp; Muhammad Ahmed &nbsp;|&nbsp; Hindi: Suhel Farooq Khan &amp; Saifur Rahman Nadwi &nbsp;|&nbsp; Hindi Tafsir: Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim</footer>
</body>
</html>""")

print('Written: %s' % index_path)
print('Done. %d surah files + index regenerated.' % 114)
