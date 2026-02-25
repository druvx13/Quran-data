#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate /docs HTML pages for the Qur'an website.

Run from the repository root:
    python3 src/gendocshtml.py

Sources used:
  - trans/en.transliteration.txt       : sura|ayah|transliteration (with HTML tags)
  - output/quran_translit_unicode.txt  : [sura:ayah] Unicode transliteration (Quran Unicode Project)
  - output/quran_hindi_farooq.txt      : [sura:ayah] Hindi translation (Farooq Khan)
  - output/quran_hindi_suhail.txt      : [sura:ayah] Hindi translation (Suhail)
  - output/quran_hindi_mokhtasar.txt   : [sura:ayah] Hindi Tafsir (Al-Mokhtasar)
  - output/quran_english_abridged.txt  : [sura:ayah] English Explanation (Abridged)
  - data/en.pickthall.txt              : one English line per ayah (Pickthall)
  - output/quran_english_yusufali.txt  : [sura:ayah] English translation (Yusuf Ali)
  - output/quran_english_sahih.txt     : [sura:ayah] English translation (Saheeh International)
  - output/quran_english_hilali.txt    : [sura:ayah] English translation (Hilali & Khan)
  - output/quran_arabic.txt            : [sura:ayah] Arabic text (Uthmani script)
  - output/quran_gujarati_rabila.txt   : [sura:ayah] Gujarati translation (Rabila Al-Umry)
  - output/quran_nepali_ahl_al_hadith.txt : [sura:ayah] Nepali translation (Ahl-al-Hadith Nepal)
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
# Load Ali Quli Qarai English translation  quran_english_qarai.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
qarai = {}
with open('output/quran_english_qarai.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            qarai[(int(m.group(1)), int(m.group(2)))] = m.group(3)

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
# Load Gujarati translation  quran_gujarati_rabila.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
gujarati = {}
with open('output/quran_gujarati_rabila.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            gujarati[(int(m.group(1)), int(m.group(2)))] = m.group(3)

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
# Load Hilali & Khan English translation  quran_english_hilali.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
hilali = {}
with open('output/quran_english_hilali.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            hilali[(int(m.group(1)), int(m.group(2)))] = m.group(3)

# ---------------------------------------------------------------------------
# Load Nepali translation  quran_nepali_ahl_al_hadith.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
nepali = {}
with open('output/quran_nepali_ahl_al_hadith.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            nepali[(int(m.group(1)), int(m.group(2)))] = m.group(3)

# ---------------------------------------------------------------------------
# HTML template helpers
# ---------------------------------------------------------------------------
CSS = """\
*,*::before,*::after{box-sizing:border-box}
body{margin:0;padding:0;font-family:system-ui,Arial,Helvetica,sans-serif;
  font-size:16px;background:#fff;color:#111;line-height:1.6}
header{background:#1a3a5c;color:#fff;padding:12px 16px;position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
header a{color:#ffd54f;text-decoration:none;font-weight:bold;font-size:1.1em}
header a:hover{text-decoration:underline}
.header-search{margin-left:auto}
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
.trans-qarai td{background:#e0f2f1}
.trans-hilali td{background:#f3e5f5}
.trans-hilali-text{color:#4a148c}
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
.gujarati td{background:#fce4ec}
.gujarati-text{font-family:'Noto Sans Gujarati',Arial,sans-serif;color:#880e4f}
.nepali td{background:#e8f5f0}
.nepali-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#1a5276}
.arabic td{background:#fff8e1}
.arabic-text{font-family:'Scheherazade New','Amiri','Traditional Arabic',serif;font-size:1.5em;direction:rtl;text-align:right;line-height:2}
nav.chapter-nav{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;
  padding:16px 0;margin-top:8px;border-top:1px solid #ccd6e0}
nav.chapter-nav a{display:inline-block;padding:8px 16px;background:#1a3a5c;color:#fff;
  border-radius:4px;text-decoration:none;font-size:.95em}
nav.chapter-nav a:hover{background:#2a5a8c}
footer{text-align:center;padding:20px;font-size:.85em;color:#666;border-top:1px solid #e0e0e0;margin-top:32px}
.surah-nav-select{padding:5px 8px;border-radius:4px;border:1px solid #ffd54f;background:#1a3a5c;color:#ffd54f;font-size:.9em;cursor:pointer;max-width:240px}
.surah-nav-select:focus{outline:2px solid #ffd54f;outline-offset:2px}
.verse-chooser{background:#f0f4f8;border:1px solid #ccd6e0;border-radius:6px;margin-bottom:16px}
.verse-chooser summary{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;cursor:pointer;user-select:none;list-style:none;background:#e8eef4;border-radius:6px}
.verse-chooser[open] summary{border-radius:6px 6px 0 0}
.verse-chooser summary::-webkit-details-marker{display:none}
.vc-title{font-size:1em;font-weight:bold;color:#1a3a5c}
.vc-arrow{color:#1a3a5c;transition:transform .2s}
.verse-chooser[open] .vc-arrow{transform:rotate(180deg)}
.vc-body{padding:10px 14px}
.vc-controls{display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap}
.vc-controls button{padding:6px 14px;border:none;border-radius:4px;cursor:pointer;font-size:.88em;background:#1a3a5c;color:#fff;min-height:36px}
.vc-controls button:hover{background:#2a5a8c}
.vc-range{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-top:6px}
.vc-range label{font-size:.88em;color:#1a3a5c;white-space:nowrap}
.vc-range input[type=number]{width:70px;padding:5px 6px;border:1px solid #ccd6e0;border-radius:4px;font-size:.88em;color:#111;background:#fff}
.vc-range input[type=number]:focus{outline:2px solid #ffd54f;outline-offset:2px}
.vc-section-title{font-size:.82em;font-weight:bold;color:#555;text-transform:uppercase;letter-spacing:.04em;margin:8px 0 4px}
.cf-list{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px}
.cf-item input[type=checkbox]{position:absolute;opacity:0;width:0;height:0}
.cf-item label{display:inline-flex;align-items:center;padding:5px 10px;background:#fff;border:1px solid #ccd6e0;border-radius:4px;cursor:pointer;font-size:.85em;color:#1a3a5c;user-select:none;white-space:nowrap}
.cf-item label:hover{background:#dde8f2}
.cf-item input:checked+label{background:#1a3a5c;color:#fff;border-color:#1a3a5c}
.cf-item input:focus+label{outline:2px solid #ffd54f;outline-offset:2px}
@media(max-width:600px){.vc-controls button{min-height:44px}.cf-item label{min-height:44px;padding:8px 10px}}
.noscript-warn{background:#fff3cd;border-left:4px solid #ffc107;padding:10px 14px;margin-bottom:12px;font-size:.93em;color:#856404}
@media(prefers-color-scheme:dark){
  body{background:#121212;color:#e8e8e8}
  header{background:#0d2136}
  main{color:#e8e8e8}
  h2{color:#90caf9}
  td{border-color:#333;color:#e8e8e8}
  .ayah-sep td{background:#0d2136;border-color:#0d2136}
  .label{color:#aaa}
  .translit td{background:#1e2a3a}
  .translit-unicode td{background:#1a1f3a}
  .trans td{background:#1a1a1a}
  .trans-yusuf td{background:#1a2a1a}
  .trans-sahih td{background:#132030}
  .trans-qarai td{background:#0d2520}
  .trans-hilali td{background:#1e0a2a}
  .hindi td{background:#1e1530}
  .hindi-suhail td{background:#2a1f10}
  .hindi-mokhtasar td{background:#102010}
  .eng-abridged td{background:#102028}
  .gujarati td{background:#200010}
  .nepali td{background:#0a1e18}
  .audio td{background:#0d2228}
  .arabic td{background:#2a2010}
  .surah-grid a{background:#1e2a3a;border-color:#334;color:#90caf9}
  .surah-grid a:hover{background:#263650}
  .notice{background:#2a2010;border-left-color:#ffc107;color:#e8e8e8}
  .verse-chooser{background:#1e2a3a;border-color:#334}
  .verse-chooser summary{background:#162030}
  .vc-title{color:#90caf9}
  .vc-arrow{color:#90caf9}
  .vc-range input[type=number]{background:#1a1a1a;border-color:#334;color:#e8e8e8}
  .cf-item label{background:#1a1a1a;border-color:#334;color:#90caf9}
  .cf-item label:hover{background:#263650}
  .cf-item input:checked+label{background:#1a3a5c;color:#fff}
  footer{color:#aaa;border-top-color:#333}
  th{background:#0d2136}
  .translit-unicode-text{color:#9fa8da}
  .hindi-text{color:#b39ddb}
  .hindi-suhail-text{color:#ffcc80}
  .hindi-mokhtasar-text{color:#a5d6a7}
  .gujarati-text{color:#f48fb1}
  .trans-hilali-text{color:#ce93d8}
  .nepali-text{color:#80cbc4}
}
@media print{
  header,nav.chapter-nav,.verse-chooser,footer{display:none!important}
  body{font-size:11pt;color:#000;background:#fff}
  td{border-color:#999;color:#000;background:#fff!important}
  .arabic-text{font-size:1.3em}
  .ayah-sep td{background:#ddd!important;color:#000!important}
  tr[data-ayah]{display:table-row!important}
}"""

HEADER_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Surah {num}: {name} \u2014 Arabic text, transliteration, and English &amp; Hindi translations of the Qur\u2019an.">
<title>Surah {num}: {name}</title>
<style>
{css}
</style>
</head>
<body>
<header><a href="index.html">&#8962; Index</a>{surah_select}<a class="header-search" href="search.html">&#128269; Search</a></header>
<main>
<h1>Surah {num}: {name}</h1>
<noscript><p class="noscript-warn">&#9888; The Verse &amp; Content Filter requires JavaScript. All verses are shown below.</p></noscript>
{verse_chooser}<div class='table-wrap'><table><thead><tr><th colspan='2'>Ayah &nbsp;&mdash;&nbsp; Arabic (Uthmani) &nbsp;/&nbsp; Audio (Mishary Alafasy) &nbsp;/&nbsp; Transliteration (Tanzil.net &amp; Unicode Project) &nbsp;/&nbsp; English (Pickthall, Yusuf Ali, Saheeh Int&#x2019;l, Qarai &amp; Hilali) &nbsp;/&nbsp; English Explanation (Abridged) &nbsp;/&nbsp; &#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2309;&#2344;&#2369;&#2357;&#2366;&#2342; (Farooq Khan &amp; Suhail) &nbsp;/&nbsp; &#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2340;&#2347;&#2381;&#2360;&#2368;&#2352; (Al-Mokhtasar) &nbsp;/&nbsp; &#2711;&#2753;&#2716;&#2736;&#2750;&#2724;&#2752; (Rabila Al-Umry) &nbsp;/&nbsp; Nepali (Ahl-al-Hadith)</th></tr></thead><tbody>
"""

FOOTER_HTML = """\
</tbody></table></div>
{nav}
</main>
<footer>Arabic Text: Standard Arabic Uthmani Script &nbsp;|&nbsp; Audio: Mishary Rashid Alafasy (versebyversequran.com) &nbsp;|&nbsp; Tanzil.net Transliteration &amp; Pickthall Translation &mdash; Public Domain &nbsp;|&nbsp; Quran Unicode Project Transliteration &nbsp;|&nbsp; Yusuf Ali Translation &mdash; Public Domain &nbsp;|&nbsp; Saheeh International Translation &nbsp;|&nbsp; Ali Quli Qarai Translation &nbsp;|&nbsp; Hilali &amp; Khan Translation &nbsp;|&nbsp; English Explanation: Abridged Explanation of the Quran &nbsp;|&nbsp; Hindi: Farooq Khan &amp; Muhammad Ahmed &nbsp;|&nbsp; Hindi: Suhel Farooq Khan &amp; Saifur Rahman Nadwi &nbsp;|&nbsp; Hindi Tafsir: Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim &nbsp;|&nbsp; Gujarati: Rabila Al-Umry &nbsp;|&nbsp; Nepali: Ahl-al-Hadith Central Society of Nepal</footer>
{script}</body>
</html>"""

# ---------------------------------------------------------------------------
# Generate surah HTML files
# ---------------------------------------------------------------------------

def make_surah_select(current=0):
    """Build the surah navigator <select> HTML."""
    opts = ['<option value="">Jump to Surah\u2026</option>']
    for i, n in enumerate(SURA_NAME, 1):
        sel = ' selected' if i == current else ''
        opts.append("<option value='%03d.html'%s>%d. %s</option>" % (i, sel, i, n))
    return (
        "<select class='surah-nav-select' onchange='location.href=this.value'"
        " aria-label='Navigate to Surah'>%s</select>" % ''.join(opts)
    )


def make_verse_chooser(size):
    """Build the verse chooser <details> HTML for a surah with `size` verses."""
    CF_ITEMS = [
        ('arabic',           'Arabic',                           True),
        ('audio',            'Audio',                            True),
        ('translit',         'Translit. (Tanzil)',               False),
        ('translit-unicode', 'Translit. (Unicode)',              True),
        ('trans',            'English (Pickthall)',              False),
        ('trans-yusuf',      'English (Yusuf Ali)',              True),
        ('trans-sahih',      'English (Saheeh Int\u2019l)',      False),
        ('trans-qarai',      'English (Qarai)',                  False),
        ('trans-hilali',     'English (Hilali)',                 False),
        ('eng-abridged',     'Abridged Expl.',                   False),
        ('hindi',            '\u0939\u093f\u0928\u094d\u0926\u0940 (Farooq)',              False),
        ('hindi-suhail',     '\u0939\u093f\u0928\u094d\u0926\u0940 (Suhail)',             True),
        ('hindi-mokhtasar',  '\u0939\u093f\u0928\u094d\u0926\u0940 \u0924\u092b\u094d\u0938\u0940\u0930 (Mokhtasar)', True),
        ('gujarati',         '\u0a97\u0ac1\u0a9c\u0ab0\u0abe\u0aa4\u0ac0 (Rabila)',                                  False),
        ('nepali',           'Nepali (Ahl-al-Hadith)',                                                                False),
    ]
    cf_html = []
    for idx, (cls, label, checked) in enumerate(CF_ITEMS):
        chk = ' checked' if checked else ''
        cf_html.append(
            "<span class='cf-item'>"
            "<input type='checkbox' id='cf-%d' data-rowclass='%s'%s>"
            "<label for='cf-%d'>%s</label>"
            "</span>" % (idx, cls, chk, idx, label)
        )
    return (
        "<details class='verse-chooser'>"
        "<summary><span class='vc-title'>&#x2714; Verse &amp; Content Filter</span>"
        "<span class='vc-arrow'>&#x25BC;</span></summary>"
        "<div class='vc-body'>"
        "<div class='vc-section-title'>Verse Range</div>"
        "<div class='vc-controls'>"
        "<button onclick='vcSelectAll()'>Show All</button>"
        "<button onclick='vcClearAll()'>Hide All</button>"
        "</div>"
        "<div class='vc-range'>"
        "<label>From <input type='number' id='vc-from' min='1' max='%d' value='1'></label>"
        "<label>To <input type='number' id='vc-to' min='1' max='%d' value='%d'></label>"
        "<button onclick='vcApplyRange()'>Apply Range</button>"
        "</div>"
        "<div class='vc-section-title' style='margin-top:12px'>Content</div>"
        "<div class='cf-list' id='cf-list'>%s</div>"
        "</div>"
        "</details>\n"
    ) % (size, size, size, ''.join(cf_html))


VC_JS = """\
<script>
(function(){
  var cfList=document.getElementById('cf-list');
  var fromInput=document.getElementById('vc-from');
  var toInput=document.getElementById('vc-to');
  var maxVerse=toInput?+toInput.max:0;
  var vcFrom=1,vcTo=maxVerse;
  var enabledTypes=new Set();
  if(cfList){
    cfList.querySelectorAll('input[type=checkbox]').forEach(function(cb){
      if(cb.checked)enabledTypes.add(cb.dataset.rowclass);
    });
    cfList.addEventListener('change',function(e){
      if(e.target.type!=='checkbox')return;
      if(e.target.checked)enabledTypes.add(e.target.dataset.rowclass);
      else enabledTypes.delete(e.target.dataset.rowclass);
      applyAllRows();
    });
  }
  function applyAllRows(){
    document.querySelectorAll('tr[data-ayah]').forEach(function(tr){
      var ayah=+tr.dataset.ayah;
      var inRange=(ayah>=vcFrom&&ayah<=vcTo);
      if(tr.classList.contains('ayah-sep')){
        tr.style.display=inRange?'':'none';
      }else{
        var typeEnabled=false;
        enabledTypes.forEach(function(t){if(tr.classList.contains(t))typeEnabled=true;});
        tr.style.display=(inRange&&typeEnabled)?'':'none';
      }
    });
    updateHash();
  }
  function updateHash(){
    if(vcFrom===1&&vcTo===maxVerse){
      history.replaceState(null,'',location.pathname+location.search);
    }else{
      history.replaceState(null,'','#'+vcFrom+(vcTo!==vcFrom?'-'+vcTo:''));
    }
  }
  function loadHash(){
    var h=location.hash.slice(1);
    if(!h)return;
    var m=h.match(/^(\\d+)(?:-(\\d+))?$/);
    if(m){
      vcFrom=+m[1];vcTo=m[2]?+m[2]:+m[1];
      if(fromInput)fromInput.value=vcFrom;
      if(toInput)toInput.value=vcTo;
    }
  }
  window.vcSelectAll=function(){
    vcFrom=1;vcTo=maxVerse;
    if(fromInput)fromInput.value=1;
    if(toInput)toInput.value=maxVerse;
    applyAllRows();
  };
  window.vcClearAll=function(){
    vcFrom=0;vcTo=0;
    applyAllRows();
  };
  window.vcApplyRange=function(){
    var f=parseInt(fromInput?fromInput.value:'1',10)||1;
    var t=parseInt(toInput?toInput.value:'1',10)||1;
    if(f>t){var tmp=f;f=t;t=tmp;}
    vcFrom=f;vcTo=t;
    if(fromInput)fromInput.value=f;
    if(toInput)toInput.value=t;
    applyAllRows();
  };
  loadHash();
  applyAllRows();
})();
</script>
"""

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
        out.write(HEADER_HTML.format(
            num=sura_idx, name=name, css=CSS,
            surah_select=make_surah_select(sura_idx),
            verse_chooser=make_verse_chooser(size),
        ))
        for ayah in range(1, size + 1):
            tl = translit.get((sura_idx, ayah), '')
            tu = translit_unicode.get((sura_idx, ayah), '')
            pk = pickthall.get((sura_idx, ayah), '')
            ya = yusufali.get((sura_idx, ayah), '')
            sa = sahih.get((sura_idx, ayah), '')
            qr = qarai.get((sura_idx, ayah), '')
            hl = hilali.get((sura_idx, ayah), '')
            hi = hindi.get((sura_idx, ayah), '')
            hs = hindi_suhail.get((sura_idx, ayah), '')
            hm = hindi_mokhtasar.get((sura_idx, ayah), '')
            ea = eng_abridged.get((sura_idx, ayah), '')
            ar = arabic.get((sura_idx, ayah), '')
            gu = gujarati.get((sura_idx, ayah), '')
            np_ = nepali.get((sura_idx, ayah), '')
            out.write(
                "<tr class='ayah-sep' data-ayah='%d' id='ayah-%d'><td colspan='2'>Ayah %d</td></tr>\n"
                "<tr class='arabic' data-ayah='%d'><td class='label'>&#1593;&#1614;&#1585;&#1614;&#1576;&#1616;&#1610;</td><td class='arabic-text' lang='ar'>%s</td></tr>\n"
                "<tr class='audio' data-ayah='%d'><td class='label'>Audio (Alafasy)</td><td><audio class='audio-player' controls preload='none' src='https://druvx13-quran-audio-alafasy.hf.space/%03d%03d.mp3' title='Surah %d, Ayah %d \u2014 Mishary Alafasy recitation'></audio></td></tr>\n"
                "<tr class='translit' data-ayah='%d'><td class='label'>Transliteration (Tanzil)</td><td class='translit-text'>%s</td></tr>\n"
                "<tr class='translit-unicode' data-ayah='%d'><td class='label'>Transliteration (Unicode)</td><td class='translit-unicode-text'>%s</td></tr>\n"
                "<tr class='trans' data-ayah='%d'><td class='label'>English (Pickthall)</td><td lang='en'>%s</td></tr>\n"
                "<tr class='trans-yusuf' data-ayah='%d'><td class='label'>English (Yusuf Ali)</td><td lang='en'>%s</td></tr>\n"
                "<tr class='trans-sahih' data-ayah='%d'><td class='label'>English (Saheeh Int&#x2019;l)</td><td lang='en'>%s</td></tr>\n"
                "<tr class='trans-qarai' data-ayah='%d'><td class='label'>English (Qarai)</td><td lang='en'>%s</td></tr>\n"
                "<tr class='trans-hilali' data-ayah='%d'><td class='label'>English (Hilali)</td><td class='trans-hilali-text' lang='en'>%s</td></tr>\n"
                "<tr class='eng-abridged' data-ayah='%d'><td class='label'>English (Abridged Expl.)</td><td lang='en'>%s</td></tr>\n"
                "<tr class='hindi' data-ayah='%d'><td class='label'>&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; (Farooq)</td><td class='hindi-text' lang='hi'>%s</td></tr>\n"
                "<tr class='hindi-suhail' data-ayah='%d'><td class='label'>&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; (Suhail)</td><td class='hindi-suhail-text' lang='hi'>%s</td></tr>\n"
                "<tr class='hindi-mokhtasar' data-ayah='%d'><td class='label'>&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2340;&#2347;&#2381;&#2360;&#2368;&#2352; (Mokhtasar)</td><td class='hindi-mokhtasar-text' lang='hi'>%s</td></tr>\n"
                "<tr class='gujarati' data-ayah='%d'><td class='label'>&#2711;&#2753;&#2716;&#2736;&#2750;&#2724;&#2752; (Rabila)</td><td class='gujarati-text' lang='gu'>%s</td></tr>\n"
                "<tr class='nepali' data-ayah='%d'><td class='label'>Nepali (Ahl-al-Hadith)</td><td class='nepali-text' lang='ne'>%s</td></tr>\n"
                % (ayah, ayah, ayah,
                   ayah, ar,
                   ayah, sura_idx, ayah, sura_idx, ayah,
                   ayah, tl,
                   ayah, tu,
                   ayah, pk,
                   ayah, ya,
                   ayah, sa,
                   ayah, qr,
                   ayah, hl,
                   ayah, ea,
                   ayah, hi,
                   ayah, hs,
                   ayah, hm,
                   ayah, gu,
                   ayah, np_)
            )
        out.write(FOOTER_HTML.format(nav=nav, script=VC_JS))

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
<header><a href="index.html">&#8962; Index</a>%s<a class="header-search" href="search.html">&#128269; Search</a></header>
<main>
<h1>Qur&#x2019;an &mdash; Arabic, Transliteration, English, Hindi, Gujarati &amp; Nepali Translation</h1>
<details class="notice">
<summary><strong>Public Domain Notice &amp; Source Attribution</strong></summary>
<em>Arabic Text:</em> Standard Arabic Uthmani Script.<br>
<em>Audio Recitation:</em> Mishary Rashid Alafasy &mdash; via <a href="https://druvx13-quran-audio-alafasy.hf.space" rel="noopener noreferrer">Hugging Face Space</a> (audio sourced from versebyversequran.com).<br>
<em>Transliteration:</em> Tanzil.net English Transliteration of the Qur&#x2019;an.<br>
<em>Transliteration:</em> Quran Unicode Project (translit_en.txt).<br>
<em>English Translation:</em> Mohammed Marmaduke Pickthall, <em>The Meaning of the Glorious Koran</em> (1930) &mdash; Public Domain.<br>
<em>English Translation:</em> Abdullah Yusuf Ali, <em>The Holy Quran: Text, Translation and Commentary</em> &mdash; Public Domain.<br>
<em>English Translation:</em> Saheeh International.<br>
<em>English Translation:</em> Ali Quli Qarai.<br>
<em>English Translation:</em> Dr. Muhammad Taqi-ud-Din Al-Hilali &amp; Dr. Muhammad Muhsin Khan.<br>
<em>English Explanation:</em> Abridged Explanation of the Quran.<br>
<em>Hindi Translation (&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2309;&#2344;&#2369;&#2357;&#2366;&#2342;):</em> Muhammad Farooq Khan &amp; Muhammad Ahmed.<br>
<em>Hindi Translation (&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2309;&#2344;&#2369;&#2357;&#2366;&#2342;):</em> Suhel Farooq Khan &amp; Saifur Rahman Nadwi.<br>
<em>Hindi Tafsir (&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2340;&#2347;&#2381;&#2360;&#2368;&#2352;):</em> Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim.<br>
<em>Gujarati Translation (&#2711;&#2753;&#2716;&#2736;&#2750;&#2724;&#2752; &#2733;&#2750;&#2743;&#2750;&#2690;&#2724;&#2736;):</em> Rabila Al-Umry.<br>
<em>Nepali Translation:</em> Ahl-al-Hadith Central Society of Nepal.<br>
Texts are reproduced verbatim; no alterations have been made.
</details>
<h2>Surahs (Chapters)</h2>
<div class="surah-grid">
""" % (CSS, make_surah_select(0)))
    for i, name in enumerate(SURA_NAME, 1):
        out.write("<a href='%03d.html'><strong>%d.</strong> %s</a>\n" % (i, i, name))
    out.write("""\
</div>
</main>
<footer>Arabic Text: Standard Arabic Uthmani Script &nbsp;|&nbsp; Audio: Mishary Rashid Alafasy (versebyversequran.com) &nbsp;|&nbsp; Tanzil.net Transliteration &amp; Pickthall Translation &mdash; Public Domain &nbsp;|&nbsp; Quran Unicode Project Transliteration &nbsp;|&nbsp; Yusuf Ali Translation &mdash; Public Domain &nbsp;|&nbsp; Saheeh International Translation &nbsp;|&nbsp; Ali Quli Qarai Translation &nbsp;|&nbsp; Hilali &amp; Khan Translation &nbsp;|&nbsp; English Explanation: Abridged Explanation of the Quran &nbsp;|&nbsp; Hindi: Farooq Khan &amp; Muhammad Ahmed &nbsp;|&nbsp; Hindi: Suhel Farooq Khan &amp; Saifur Rahman Nadwi &nbsp;|&nbsp; Hindi Tafsir: Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim &nbsp;|&nbsp; Gujarati: Rabila Al-Umry &nbsp;|&nbsp; Nepali: Ahl-al-Hadith Central Society of Nepal</footer>
</body>
</html>""")

print('Written: %s' % index_path)

# ---------------------------------------------------------------------------
# Generate search-data.js  (compact JSON array for client-side search)
# Each entry: [surahNum, ayahNum, surahName, arabic, translit_unicode, yusuf_ali, hindi_mokhtasar]
# ---------------------------------------------------------------------------
import json

search_data = []
for sura_idx in range(1, 115):
    size = SURA_SIZE[sura_idx - 1]
    name = SURA_NAME[sura_idx - 1]
    for ayah in range(1, size + 1):
        search_data.append([
            sura_idx,
            ayah,
            name,
            arabic.get((sura_idx, ayah), ''),
            translit_unicode.get((sura_idx, ayah), ''),
            yusufali.get((sura_idx, ayah), ''),
            hindi_mokhtasar.get((sura_idx, ayah), ''),
        ])

search_data_path = os.path.join(docs_dir, 'search-data.js')
with open(search_data_path, 'w', encoding='utf-8') as f:
    f.write('var QURAN_DATA=')
    json.dump(search_data, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';')
print('Written: %s' % search_data_path)

# ---------------------------------------------------------------------------
# Generate search.html
# ---------------------------------------------------------------------------
SEARCH_CSS = CSS + """
.search-box{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.search-box input[type=text]{flex:1;min-width:200px;padding:9px 12px;border:1px solid #ccd6e0;border-radius:4px;font-size:1em;color:#111}
.search-box input[type=text]:focus{outline:2px solid #ffd54f;outline-offset:2px}
.search-box button{padding:9px 18px;background:#1a3a5c;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:1em}
.search-box button:hover{background:#2a5a8c}
#search-status{font-size:.92em;color:#555;margin-bottom:10px}
.result-card{border:1px solid #ccd6e0;border-radius:6px;margin-bottom:12px;overflow:hidden}
.result-header{background:#1a3a5c;color:#fff;padding:7px 12px;font-size:.9em;display:flex;align-items:center;justify-content:space-between}
.result-header a{color:#ffd54f;text-decoration:none;font-weight:bold}
.result-header a:hover{text-decoration:underline}
.result-arabic{font-family:'Scheherazade New','Amiri','Traditional Arabic',serif;font-size:1.4em;direction:rtl;text-align:right;line-height:2;padding:8px 12px;background:#fff8e1}
.result-translit{padding:6px 12px;background:#e8eaf6;font-weight:600;color:#283593;font-size:.95em}
.result-trans{padding:6px 12px;background:#e8f5e9;font-size:.95em}
.result-highlight{background:#fff176;border-radius:2px}
.result-hindi-mokhtasar{padding:6px 12px;background:#e8f5e0;font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#1b5e20;font-size:.95em}
.pagination{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:16px 0;justify-content:center}
.pagination button{padding:7px 14px;border:none;border-radius:4px;cursor:pointer;background:#1a3a5c;color:#fff;font-size:.9em;min-width:36px}
.pagination button:hover:not(:disabled){background:#2a5a8c}
.pagination button:disabled{background:#ccd6e0;color:#888;cursor:default}
.pagination .pg-current{background:#ffd54f;color:#1a3a5c;font-weight:bold}
.pagination .pg-ellipsis{font-size:.9em;color:#555;padding:0 4px}
"""

SEARCH_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Search &ndash; Qur&rsquo;an</title>
<style>
{css}
</style>
</head>
<body>
<header><a href="index.html">&#8962; Index</a>{surah_select}<a class="header-search" href="search.html">&#128269; Search</a></header>
<main>
<h1>&#128269; Search the Qur&#x2019;an</h1>
<p style="font-size:.93em;color:#555;margin-bottom:14px">Search Arabic text, transliteration, English translation (Yusuf Ali), or &#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2340;&#2347;&#2381;&#2360;&#2368;&#2352; (Hindi Tafsir). Results link directly to the verse.</p>
<div class="search-box">
  <input type="text" id="q" placeholder="e.g. mercy, rahman, bismillah&hellip;" autofocus autocomplete="off" spellcheck="false">
  <button onclick="doSearch()">Search</button>
</div>
<div id="search-status"></div>
<div id="results"></div>
<div id="pagination"></div>
</main>
<footer>Arabic Text: Standard Arabic Uthmani Script &nbsp;|&nbsp; Audio: Mishary Rashid Alafasy (versebyversequran.com) &nbsp;|&nbsp; Yusuf Ali Translation &mdash; Public Domain</footer>
<script src="search-data.js"></script>
<script>
(function(){{
  var PAGE_SIZE = 20;
  var allMatches = [];
  var currentPage = 1;
  var currentTerms = [];
  var input = document.getElementById('q');
  var statusEl = document.getElementById('search-status');
  var resultsEl = document.getElementById('results');
  var paginEl = document.getElementById('pagination');

  function escHtml(s){{
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }}

  function highlight(text, terms){{
    var escaped = escHtml(text);
    terms.forEach(function(term){{
      if(!term) return;
      var re = new RegExp('(' + term.replace(/[.*+?^${{}}()|[\\]\\\\]/g,'\\\\$&') + ')', 'gi');
      escaped = escaped.replace(re, '<mark class="result-highlight">$1</mark>');
    }});
    return escaped;
  }}

  function renderPage(page){{
    var total = allMatches.length;
    var totalPages = Math.ceil(total / PAGE_SIZE);
    if(page < 1) page = 1;
    if(page > totalPages) page = totalPages;
    currentPage = page;
    var start = (page - 1) * PAGE_SIZE;
    var end = Math.min(start + PAGE_SIZE, total);
    statusEl.textContent = 'Showing ' + (start+1) + '\u2013' + end + ' of ' + total + ' result(s) for \u201c' + input.value.trim() + '\u201d';
    var html = '';
    for(var i=start;i<end;i++){{
      var row=allMatches[i];
      var sura=row[0],ayah=row[1],name=row[2],ar=row[3],tu=row[4],ya=row[5],hm=row[6]||'';
      var href=String(sura).padStart(3,'0')+'.html#'+ayah;
      html+='<div class="result-card">'
        +'<div class="result-header"><span>Surah '+sura+':'+ayah+' &mdash; '+escHtml(name)+'</span>'
        +'<a href="'+href+'">View verse &rarr;</a></div>'
        +'<div class="result-arabic">'+highlight(ar,currentTerms)+'</div>'
        +(tu?'<div class="result-translit">'+highlight(tu,currentTerms)+'</div>':'')
        +(ya?'<div class="result-trans">'+highlight(ya,currentTerms)+'</div>':'')
        +(hm?'<div class="result-hindi-mokhtasar">'+highlight(hm,currentTerms)+'</div>':'')
        +'</div>';
    }}
    resultsEl.innerHTML = html;
    var pgHtml = '';
    if(totalPages > 1){{
      pgHtml += '<div class="pagination">';
      pgHtml += '<button onclick="goPage('+(page-1)+')"'+(page<=1?' disabled':'')+'>&laquo; Prev</button>';
      var pStart=Math.max(1,page-3), pEnd=Math.min(totalPages,page+3);
      if(pStart>1){{
        pgHtml+='<button onclick="goPage(1)">1</button>';
        if(pStart>2) pgHtml+='<span class="pg-ellipsis">&hellip;</span>';
      }}
      for(var p=pStart;p<=pEnd;p++){{
        if(p===page) pgHtml+='<button class="pg-current" disabled>'+p+'</button>';
        else pgHtml+='<button onclick="goPage('+p+')">'+p+'</button>';
      }}
      if(pEnd<totalPages){{
        if(pEnd<totalPages-1) pgHtml+='<span class="pg-ellipsis">&hellip;</span>';
        pgHtml+='<button onclick="goPage('+totalPages+')">'+totalPages+'</button>';
      }}
      pgHtml += '<button onclick="goPage('+(page+1)+')"'+(page>=totalPages?' disabled':'')+'>Next &raquo;</button>';
      pgHtml += '</div>';
    }}
    paginEl.innerHTML = pgHtml;
  }}

  window.goPage = function(page){{
    renderPage(page);
    resultsEl.scrollIntoView({{behavior:'smooth',block:'start'}});
  }};

  window.doSearch = function(){{
    var q = input.value.trim();
    if(!q){{ resultsEl.innerHTML=''; statusEl.textContent=''; paginEl.innerHTML=''; allMatches=[]; return; }}
    currentTerms = q.toLowerCase().split(/\\s+/).filter(Boolean);
    allMatches = [];
    for(var i=0;i<QURAN_DATA.length;i++){{
      var row=QURAN_DATA[i];
      var sura=row[0],ayah=row[1],name=row[2],ar=row[3],tu=row[4],ya=row[5],hm=row[6]||'';
      var haystack=(ar+' '+tu+' '+ya+' '+hm+' '+name).toLowerCase();
      if(currentTerms.every(function(t){{ return haystack.indexOf(t)!==-1; }})) allMatches.push(row);
    }}
    if(allMatches.length===0){{
      statusEl.textContent='No results found.';
      resultsEl.innerHTML='';
      paginEl.innerHTML='';
      return;
    }}
    renderPage(1);
  }};

  input.addEventListener('keydown',function(e){{ if(e.key==='Enter') doSearch(); }});

  // Auto-search from URL ?q=...
  var params=new URLSearchParams(location.search);
  var qs=params.get('q');
  if(qs){{ input.value=qs; doSearch(); }}
}})();
</script>
</body>
</html>"""

search_html_path = os.path.join(docs_dir, 'search.html')
with open(search_html_path, 'w', encoding='utf-8') as f:
    f.write(SEARCH_HTML.format(
        css=SEARCH_CSS,
        surah_select=make_surah_select(0),
    ))
print('Written: %s' % search_html_path)

print('Done. %d surah files + index + search regenerated.' % 114)
