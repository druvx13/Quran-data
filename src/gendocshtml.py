#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate /docs HTML pages for the Qur'an website.

Run from the repository root:
    python3 src/gendocshtml.py

Sources used:
  - data/en.transliteration.tanzil.txt : sura|ayah|transliteration (with HTML tags)
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
  - output/quran_roman_urdu_maududi.txt: [sura:ayah] Roman Urdu translation (Abul Ala Maududi)
  - output/quran_roman_urdu_junagarhi.txt: [sura:ayah] Roman Urdu translation (Muhammad Junagarhi)
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
# Revelation metadata: (revelation_order, 'M'=Meccan/'D'=Medinan) per surah
# Standard Islamic scholarly consensus order
# ---------------------------------------------------------------------------
SURAH_REV = [
    # 1-10
    (5,'M'),(87,'D'),(89,'D'),(92,'D'),(112,'D'),
    (55,'M'),(39,'M'),(88,'D'),(113,'D'),(51,'M'),
    # 11-20
    (52,'M'),(53,'M'),(96,'D'),(72,'M'),(54,'M'),
    (70,'M'),(50,'M'),(69,'M'),(44,'M'),(45,'M'),
    # 21-30
    (73,'M'),(103,'D'),(74,'M'),(102,'D'),(42,'M'),
    (47,'M'),(48,'M'),(49,'M'),(85,'M'),(84,'M'),
    # 31-40
    (57,'M'),(75,'M'),(90,'D'),(58,'M'),(43,'M'),
    (41,'M'),(56,'M'),(38,'M'),(59,'M'),(60,'M'),
    # 41-50
    (61,'M'),(62,'M'),(63,'M'),(64,'M'),(65,'M'),
    (66,'M'),(95,'D'),(111,'D'),(106,'D'),(34,'M'),
    # 51-60
    (67,'M'),(76,'M'),(23,'M'),(37,'M'),(97,'D'),
    (46,'M'),(94,'D'),(105,'D'),(101,'D'),(91,'D'),
    # 61-70
    (109,'D'),(110,'D'),(104,'D'),(108,'D'),(99,'D'),
    (107,'D'),(77,'M'),(2,'M'),(78,'M'),(79,'M'),
    # 71-80
    (71,'M'),(40,'M'),(3,'M'),(4,'M'),(31,'M'),
    (98,'D'),(33,'M'),(80,'M'),(81,'M'),(24,'M'),
    # 81-90
    (7,'M'),(82,'M'),(86,'M'),(83,'M'),(27,'M'),
    (36,'M'),(8,'M'),(68,'M'),(10,'M'),(35,'M'),
    # 91-100
    (26,'M'),(9,'M'),(11,'M'),(12,'M'),(28,'M'),
    (1,'M'),(25,'M'),(100,'D'),(93,'D'),(14,'M'),
    # 101-110
    (30,'M'),(16,'M'),(13,'M'),(32,'M'),(19,'M'),
    (29,'M'),(17,'M'),(15,'M'),(18,'M'),(114,'D'),
    # 111-114
    (6,'M'),(22,'M'),(20,'M'),(21,'M'),
]

# Juz (para) start positions: {(surah, ayah): juz_number}
JUZ_STARTS = {
    (1,1):1,  (2,142):2,  (2,253):3, (3,92):4,  (4,24):5,
    (4,148):6,(5,82):7,   (6,111):8, (7,88):9,  (8,41):10,
    (9,93):11,(11,6):12,  (12,53):13,(15,1):14, (17,1):15,
    (18,75):16,(21,1):17, (23,1):18, (25,21):19,(27,56):20,
    (29,46):21,(33,31):22,(36,28):23,(39,32):24,(41,47):25,
    (46,1):26,(51,31):27, (58,1):28, (67,1):29, (78,1):30,
}

# Sajda (Sujood Al-Tilawa) verses — 14 obligatory prostration positions
SAJDA_VERSES = {
    (7,206),(13,15),(16,50),(17,109),(19,58),
    (22,18),(25,60),(27,26),(32,15),(38,24),
    (41,38),(53,62),(84,21),(96,19),
}


def surah_juz_span(sura_idx):
    """Return a string describing the Juz span of a surah, e.g. '1', '1–2'."""
    size = SURA_SIZE[sura_idx - 1]
    juz_set = set()
    # current_juz tracks which juz each ayah falls in
    current = 1
    for ayah in range(1, size + 1):
        j = JUZ_STARTS.get((sura_idx, ayah))
        if j:
            current = j
        juz_set.add(current)
    juz_list = sorted(juz_set)
    if len(juz_list) == 1:
        return str(juz_list[0])
    return '%d\u2013%d' % (juz_list[0], juz_list[-1])


def make_surah_info_bar(sura_idx):
    """Return the surah metadata info-bar HTML."""
    rev_order, rev_type = SURAH_REV[sura_idx - 1]
    type_label = 'Meccan' if rev_type == 'M' else 'Medinan'
    type_class = 'meccan' if rev_type == 'M' else 'medinan'
    juz = surah_juz_span(sura_idx)
    size = SURA_SIZE[sura_idx - 1]
    return (
        "<div class='surah-info-bar'>"
        "<span class='sib-type %s'>%s</span>"
        "<span>&#128336;&nbsp;Revelation&nbsp;#%d</span>"
        "<span>&#128220;&nbsp;%d Verses</span>"
        "<span>&#128366;&nbsp;Juz&nbsp;%s</span>"
        "</div>\n"
    ) % (type_class, type_label, rev_order, size, juz)


# ---------------------------------------------------------------------------
# Load transliteration  data/en.transliteration.tanzil.txt
# Format: sura|ayah|text_with_html_tags  (comment lines start with #)
# ---------------------------------------------------------------------------
translit = {}
with open('data/en.transliteration.tanzil.txt', 'r', encoding='utf-8') as f:
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
# Load Hindi Al-Omari translation  quran_hindi_omari.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
hindi_omari = {}
with open('output/quran_hindi_omari.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            hindi_omari[(int(m.group(1)), int(m.group(2)))] = m.group(3)

# ---------------------------------------------------------------------------
# Load Roman Urdu (Maududi)  quran_roman_urdu_maududi.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
roman_urdu = {}
with open('output/quran_roman_urdu_maududi.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            roman_urdu[(int(m.group(1)), int(m.group(2)))] = m.group(3)

# ---------------------------------------------------------------------------
# Load Roman Urdu (Junagarhi)  quran_roman_urdu_junagarhi.txt
# Format: [sura:ayah] text
# ---------------------------------------------------------------------------
roman_urdu_junagarhi = {}
with open('output/quran_roman_urdu_junagarhi.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)', line)
        if m:
            roman_urdu_junagarhi[(int(m.group(1)), int(m.group(2)))] = m.group(3)

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
.surah-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px;margin-top:16px}
.surah-grid a{display:block;padding:10px 12px;background:#f0f4f8;border:1px solid #ccd6e0;
  border-radius:6px;text-decoration:none;color:#1a3a5c;font-size:.95em}
.surah-grid a:hover{background:#dde8f2}
.sg-meta{display:flex;align-items:center;gap:6px;margin-top:4px;font-size:.78em;color:#555}
.notice{background:#fff8e1;border-left:4px solid #ffd54f;padding:12px 16px;margin-bottom:20px;font-size:.95em}
.notice summary{cursor:pointer}
.table-wrap{overflow-x:auto;width:100%}
table{width:100%;border-collapse:collapse;margin-bottom:24px}
th{background:#1a3a5c;color:#fff;padding:10px 12px;text-align:left;font-size:.9em}
td{padding:8px 12px;vertical-align:top;border:1px solid #ccd6e0}
.ayah-sep td{background:#1a3a5c;color:#fff;font-weight:bold;font-size:.9em;padding:6px 12px;border-color:#1a3a5c}
.label{color:#888;font-size:.82em;white-space:nowrap;width:110px;vertical-align:top}
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
.hindi-omari td{background:#fff0f5}
.hindi-omari-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#880e30}
.roman-urdu td{background:#f0f4c3}
.roman-urdu-text{font-style:normal;font-weight:500;color:#33691e}
.roman-urdu-junagarhi td{background:#e8f5e9}
.roman-urdu-junagarhi-text{font-style:normal;font-weight:500;color:#1b5e20}
.arabic td{background:#fff8e1}
.arabic-text{font-family:'Scheherazade New','Amiri','Traditional Arabic',serif;font-size:1.5em;direction:rtl;text-align:right;line-height:2}
nav.chapter-nav{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;
  padding:16px 0;margin-top:8px;border-top:1px solid #ccd6e0}
nav.chapter-nav a{display:inline-block;padding:8px 16px;background:#1a3a5c;color:#fff;
  border-radius:4px;text-decoration:none;font-size:.95em}
nav.chapter-nav a:hover{background:#2a5a8c}
footer{text-align:center;padding:16px 20px;font-size:.82em;color:#666;border-top:1px solid #e0e0e0;margin-top:32px;line-height:1.8}
footer a{color:#1a3a5c;text-decoration:none;font-weight:600}
footer a:hover{text-decoration:underline}
.surah-nav-select{padding:5px 8px;border-radius:4px;border:1px solid #ffd54f;background:#1a3a5c;color:#ffd54f;font-size:.9em;cursor:pointer;max-width:240px}
.surah-nav-select:focus{outline:2px solid #ffd54f;outline-offset:2px}
.verse-chooser{background:#f0f4f8;border:1px solid #ccd6e0;border-radius:6px;margin-bottom:16px}
.verse-chooser summary{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;cursor:pointer;user-select:none;list-style:none;background:#e8eef4;border-radius:6px}
.verse-chooser[open] summary{border-radius:6px 6px 0 0}
.verse-chooser summary::-webkit-details-marker{display:none}
.vc-title{font-size:1em;font-weight:bold;color:#1a3a5c}
.vc-arrow{color:#1a3a5c;transition:transform .2s}
.verse-chooser[open] .vc-arrow{transform:rotate(180deg)}
.vc-body{padding:10px 14px;max-height:340px;overflow-y:auto}
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
@media(max-width:600px){
  .vc-controls button{min-height:44px}
  .cf-item label{min-height:44px;padding:8px 10px}
  main{padding:10px 8px}
  h1{font-size:1.15em}
  .surah-nav-select{max-width:160px;font-size:.82em}
  .table-wrap thead{display:none}
  .table-wrap table,.table-wrap tbody,.table-wrap tr{display:block;width:100%}
  .table-wrap td{display:block;width:100%;border-left:none;border-right:none;border-bottom:none;box-sizing:border-box}
  .table-wrap .label{padding:5px 10px 1px;font-size:.72em;width:auto;white-space:normal;border-top:2px solid rgba(0,0,0,.07)}
  .table-wrap td:not(.label){padding:2px 10px 8px}
  .table-wrap .ayah-sep td{border:none;padding:7px 10px}
  .arabic-text{font-size:1.25em}
  .audio-player{max-width:100%;height:40px}
  nav.chapter-nav a{padding:10px 14px;min-height:44px;display:inline-flex;align-items:center}
  footer{font-size:.78em;padding:12px 14px}
}
@media(max-width:380px){
  .surah-grid{grid-template-columns:repeat(auto-fill,minmax(130px,1fr))}
  header{padding:8px 10px;gap:8px}
}
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
  .hindi-omari td{background:#200010}
  .roman-urdu td{background:#1a2000}
  .roman-urdu-junagarhi td{background:#0a1a00}
  .surah-grid a{background:#1e2a3a;border-color:#334;color:#90caf9}
  .surah-grid a:hover{background:#263650}
  .sg-meta{color:#aaa}
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
  footer a{color:#90caf9}
  th{background:#0d2136}
  .translit-unicode-text{color:#9fa8da}
  .hindi-text{color:#b39ddb}
  .hindi-suhail-text{color:#ffcc80}
  .hindi-mokhtasar-text{color:#a5d6a7}
  .gujarati-text{color:#f48fb1}
  .trans-hilali-text{color:#ce93d8}
  .nepali-text{color:#80cbc4}
  .hindi-omari-text{color:#f48fb1}
}
@media(max-width:600px) and (prefers-color-scheme:dark){
  .table-wrap .label{border-top-color:rgba(255,255,255,.08)}
}
@media print{
  header,nav.chapter-nav,.verse-chooser,footer{display:none!important}
  body{font-size:11pt;color:#000;background:#fff}
  .table-wrap table,.table-wrap tbody,.table-wrap tr,.table-wrap td{display:table!important}
  .table-wrap tbody{display:table-row-group!important}
  .table-wrap tr{display:table-row!important}
  .table-wrap td{display:table-cell!important;width:auto!important}
  .table-wrap .label{width:110px!important;white-space:nowrap!important}
  td{border-color:#999;color:#000;background:#fff!important}
  .arabic-text{font-size:1.3em}
  .ayah-sep td{background:#ddd!important;color:#000!important}
  tr[data-ayah]{display:table-row!important}
}
.surah-info-bar{display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center;
  padding:8px 12px;background:#f0f4f8;border:1px solid #ccd6e0;border-radius:6px;
  margin-bottom:14px;font-size:.88em;color:#1a3a5c}
.surah-info-bar span{white-space:nowrap}
.sib-type{font-weight:700;padding:2px 8px;border-radius:10px;font-size:.95em}
.sib-type.meccan{background:#fff8e1;color:#e65100;border:1px solid #ffcc80}
.sib-type.medinan{background:#e8f5e9;color:#1b5e20;border:1px solid #a5d6a7}
.juz-marker td{background:#1a3a5c;color:#ffd54f;font-weight:700;font-size:.85em;
  padding:5px 12px;letter-spacing:.04em;border-color:#1a3a5c;text-align:center}
.sajda-badge{display:inline-flex;align-items:center;gap:4px;
  background:#e8f5e9;color:#1b5e20;font-size:.78em;font-weight:600;
  padding:1px 6px;border-radius:8px;border:1px solid #a5d6a7;margin-left:8px;
  vertical-align:middle}
.copy-btn{background:none;border:1px solid #ccd6e0;border-radius:4px;
  padding:1px 7px;cursor:pointer;font-size:.75em;color:#888;margin-left:8px;
  vertical-align:middle;line-height:1.4}
.copy-btn:hover{background:#e8eef4;color:#1a3a5c}
.bm-btn{background:none;border:1px solid #ccd6e0;border-radius:4px;
  padding:1px 7px;cursor:pointer;font-size:.75em;color:#888;margin-left:4px;
  vertical-align:middle;line-height:1.4;transition:background .15s,color .15s}
.bm-btn:hover{background:#fff8e1;color:#e65100}
.bm-btn.active{background:#fff8e1;color:#e65100;border-color:#ffa726}
@keyframes ayah-pulse{0%{background:#1a3a5c}40%{background:#ffd54f}100%{background:#1a3a5c}}
.ayah-anchor-highlight td{animation:ayah-pulse .8s ease-in-out 3}
.permalink{color:inherit;text-decoration:none;font-weight:bold}
.permalink:hover{text-decoration:underline}
.scroll-top-btn{position:fixed;bottom:24px;right:20px;width:42px;height:42px;
  border-radius:50%;background:#1a3a5c;color:#ffd54f;font-size:1.2em;font-weight:bold;
  border:none;cursor:pointer;display:none;align-items:center;justify-content:center;
  box-shadow:0 2px 8px rgba(0,0,0,.3);z-index:100;line-height:1}
.scroll-top-btn:hover{background:#2a5a8c}
.vc-font-ctrl{display:flex;align-items:center;gap:6px;margin-bottom:8px;flex-wrap:wrap}
.vc-font-ctrl span{font-size:.85em;color:#555}
.vc-font-ctrl button{padding:3px 10px;border:1px solid #ccd6e0;border-radius:4px;
  cursor:pointer;font-size:.88em;background:#fff;color:#1a3a5c;min-height:30px}
.vc-font-ctrl button:hover{background:#dde8f2}
@media(prefers-color-scheme:dark){
  .surah-info-bar{background:#1e2a3a;border-color:#334;color:#90caf9}
  .sib-type.meccan{background:#2a1f00;color:#ffcc80;border-color:#8b6914}
  .sib-type.medinan{background:#0a1e10;color:#a5d6a7;border-color:#2e7d32}
  .juz-marker td{background:#0d2136;border-color:#0d2136}
  .sajda-badge{background:#0a1e10;color:#a5d6a7;border-color:#2e7d32}
  .copy-btn{border-color:#334;color:#90caf9}
  .copy-btn:hover{background:#263650}
  .bm-btn{border-color:#334;color:#aaa}
  .bm-btn:hover{background:#2a1f00;color:#ffcc80}
  .bm-btn.active{background:#2a1f00;color:#ffcc80;border-color:#8b6914}
  .vc-font-ctrl span{color:#aaa}
  .vc-font-ctrl button{background:#1a1a1a;border-color:#334;color:#90caf9}
  .vc-font-ctrl button:hover{background:#263650}
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
<script src="config.js"></script>
</head>
<body data-sura="{num}">
<header><a href="index.html">&#8962; Index</a>{surah_select}<a class="header-search" href="config.html" title="Settings">&#9881;</a><a class="header-search" href="search.html">&#128269; Search</a></header>
<main>
<h1>Surah {num}: {name}</h1>
{surah_info}<noscript><p class="noscript-warn">&#9888; The Verse &amp; Content Filter requires JavaScript. All verses are shown below.</p></noscript>
{verse_chooser}<div class='table-wrap'><table><thead><tr><th colspan='2'>Ayah &nbsp;&mdash;&nbsp; Arabic (Uthmani) &nbsp;/&nbsp; Audio (Mishary Alafasy) &nbsp;/&nbsp; Transliteration (Tanzil.net &amp; Unicode Project) &nbsp;/&nbsp; English (Pickthall, Yusuf Ali, Saheeh Int&#x2019;l, Qarai &amp; Hilali) &nbsp;/&nbsp; English Explanation (Abridged) &nbsp;/&nbsp; &#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2309;&#2344;&#2369;&#2357;&#2366;&#2342; (Farooq Khan, Suhail &amp; Al-Omari) &nbsp;/&nbsp; &#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2340;&#2347;&#2381;&#2360;&#2368;&#2352; (Al-Mokhtasar) &nbsp;/&nbsp; &#2711;&#2753;&#2716;&#2736;&#2750;&#2724;&#2752; (Rabila Al-Umry) &nbsp;/&nbsp; Nepali (Ahl-al-Hadith) &nbsp;/&nbsp; Roman Urdu (Maududi &amp; Junagarhi)</th></tr></thead><tbody>
"""

COMPACT_FOOTER = '<footer><a href="sources.html">Sources &amp; Attribution</a> &nbsp;|&nbsp; <a href="license.html">License</a> &nbsp;|&nbsp; <a href="download.html">Download</a> &nbsp;|&nbsp; <a href="https://github.com/druvx13/Quran-data" rel="noopener noreferrer">GitHub</a></footer>'

FOOTER_HTML = """\
</tbody></table></div>
{nav}
</main>
""" + COMPACT_FOOTER + """
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
    ('hindi-omari',      '\u0939\u093f\u0928\u094d\u0926\u0940 (Al-Omari)',                                       False),
    ('roman-urdu',       'Roman Urdu (Maududi)',                                                                  False),
    ('roman-urdu-junagarhi', 'Roman Urdu (Junagarhi)',                                                              False),
]


def make_verse_chooser(size):
    """Build the verse chooser <details> HTML for a surah with `size` verses."""
    cf_html = []
    for idx, (cls, label, _default) in enumerate(CF_ITEMS):
        cf_html.append(
            "<span class='cf-item'>"
            "<input type='checkbox' id='cf-%d' data-rowclass='%s'>"
            "<label for='cf-%d'>%s</label>"
            "</span>" % (idx, cls, idx, label)
        )
    return (
        "<details class='verse-chooser'>"
        "<summary><span class='vc-title'>&#x2714; Verse &amp; Content Filter</span>"
        "<span class='vc-arrow'>&#x25BC;</span></summary>"
        "<div class='vc-body'>"
        "<div class='vc-font-ctrl'>"
        "<span>Font Size:</span>"
        "<button onclick='fsDecrease()' title='Decrease font size'>A&minus;</button>"
        "<button onclick='fsReset()' title='Reset font size'>A</button>"
        "<button onclick='fsIncrease()' title='Increase font size'>A+</button>"
        "</div>"
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
/* ---- Last Read tracking — stores only the single most-recently-read surah ---- */
(function(){
  try{
    var _suraNum=+document.body.dataset.sura;
    if(!_suraNum)return;
    var _h1=document.querySelector('h1');
    var _suraLabel=_h1?_h1.textContent.trim():'Surah '+_suraNum;
    localStorage.setItem('quran-history',JSON.stringify({s:_suraNum,n:_suraLabel,t:Date.now()}));
  }catch(_){}
})();
/* ---- Bookmarks (array, newest-first) ---- */
(function(){
  var BM_KEY='quran-bookmark';
  var bms=[];
  try{bms=JSON.parse(localStorage.getItem(BM_KEY)||'[]');}catch(_){}
  if(!Array.isArray(bms))bms=[];
  var curSura=+document.body.dataset.sura;
  /* Highlight all active bookmark buttons for this surah */
  bms.forEach(function(b){
    if(b.s===curSura){var btn=document.getElementById('bm-'+b.a);if(btn)btn.classList.add('active');}
  });
  window.toggleBookmark=function(sura,ayah){
    var btn=document.getElementById('bm-'+ayah);
    var list=[];
    try{list=JSON.parse(localStorage.getItem(BM_KEY)||'[]');}catch(_){}
    if(!Array.isArray(list))list=[];
    var idx=list.findIndex(function(b){return b.s===sura&&b.a===ayah;});
    if(idx!==-1){
      /* Remove bookmark */
      list.splice(idx,1);
      if(btn)btn.classList.remove('active');
    } else {
      /* Add bookmark to front */
      var h1=document.querySelector('h1');
      var label=h1?h1.textContent.trim():'Surah '+sura;
      list.unshift({s:sura,a:ayah,n:label,t:Date.now()});
      if(btn)btn.classList.add('active');
    }
    try{localStorage.setItem(BM_KEY,JSON.stringify(list));}catch(_){}
  };
})();
(function(){
  var cfList=document.getElementById('cf-list');
  var fromInput=document.getElementById('vc-from');
  var toInput=document.getElementById('vc-to');
  var maxVerse=toInput?+toInput.max:0;
  var vcFrom=1,vcTo=maxVerse;
  var enabledTypes=new Set();

  /* ---- Apply config defaults + user overrides to checkboxes ---- */
  var defaults=(typeof QURAN_CONFIG!=='undefined')?QURAN_CONFIG:{};
  var userPrefs=null;
  try{var raw=localStorage.getItem('quran-cf');if(raw)userPrefs=JSON.parse(raw);}catch(e){}

  if(cfList){
    cfList.querySelectorAll('input[type=checkbox]').forEach(function(cb){
      var key=cb.dataset.rowclass;
      var on;
      if(userPrefs&&userPrefs.hasOwnProperty(key)){on=userPrefs[key];}
      else{on=defaults.hasOwnProperty(key)?defaults[key]:false;}
      cb.checked=on;
      if(on)enabledTypes.add(key);
    });
    cfList.addEventListener('change',function(e){
      if(e.target.type!=='checkbox')return;
      if(e.target.checked)enabledTypes.add(e.target.dataset.rowclass);
      else enabledTypes.delete(e.target.dataset.rowclass);
      saveCfPrefs();
      applyAllRows();
    });
  }
  function saveCfPrefs(){
    if(!cfList)return;
    var prefs={};
    cfList.querySelectorAll('input[type=checkbox]').forEach(function(cb){
      prefs[cb.dataset.rowclass]=cb.checked;
    });
    try{localStorage.setItem('quran-cf',JSON.stringify(prefs));}catch(e){}
  }
  function applyAllRows(){
    document.querySelectorAll('tr[data-ayah]').forEach(function(tr){
      var ayah=+tr.dataset.ayah;
      var inRange=(ayah>=vcFrom&&ayah<=vcTo);
      if(tr.classList.contains('ayah-sep')||tr.classList.contains('juz-marker')){
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
      /* Only clear hash if it's a numeric range hash — preserve #ayah-N anchors */
      var curHash=location.hash;
      if(!curHash||/^#\\d+(-\\d+)?$/.test(curHash)){
        history.replaceState(null,'',location.pathname+location.search);
      }
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
  /* Scroll to #ayah-N anchor after config layout is applied */
  (function(){
    var h=location.hash;
    if(h&&/^#ayah-\\d+$/.test(h)){
      var el=document.getElementById(h.slice(1));
      if(el){
        setTimeout(function(){
          el.scrollIntoView({behavior:'smooth',block:'center'});
          el.classList.add('ayah-anchor-highlight');
          setTimeout(function(){el.classList.remove('ayah-anchor-highlight');},2400);
        },80);
      }
    }
  })();

  /* ---- Font size control ---- */
  var FS_KEY='qfs';
  var fsSteps=[0.8,0.9,1.0,1.1,1.25,1.4,1.6];
  var fsIdx=2;
  function loadFs(){
    var s=localStorage.getItem(FS_KEY);
    if(s!==null){fsIdx=parseInt(s,10)||2;}
    if(fsIdx<0)fsIdx=0;if(fsIdx>=fsSteps.length)fsIdx=fsSteps.length-1;
  }
  function applyFs(){
    var scale=fsSteps[fsIdx];
    document.querySelectorAll('.arabic-text').forEach(function(el){
      el.style.fontSize=(1.5*scale)+'em';
    });
    document.querySelectorAll('td:not(.label)').forEach(function(el){
      el.style.fontSize=(scale)+'em';
    });
    localStorage.setItem(FS_KEY,fsIdx);
  }
  window.fsIncrease=function(){if(fsIdx<fsSteps.length-1){fsIdx++;applyFs();}};
  window.fsDecrease=function(){if(fsIdx>0){fsIdx--;applyFs();}};
  window.fsReset=function(){fsIdx=2;applyFs();};
  loadFs();
  if(fsIdx!==2)applyFs();

  /* ---- Scroll-to-top button ---- */
  var stb=document.createElement('button');
  stb.className='scroll-top-btn';
  stb.title='Back to top';
  stb.innerHTML='&#8679;';
  stb.onclick=function(){window.scrollTo({top:0,behavior:'smooth'});};
  document.body.appendChild(stb);
  window.addEventListener('scroll',function(){
    stb.style.display=window.scrollY>400?'flex':'none';
  },{passive:true});

  /* ---- Copy verse ---- */
  window.copyVerse=function(btn,sura,ayah){
    var row=btn.closest('tr');
    if(!row)return;
    var tbod=row.parentNode;
    var texts=['['+sura+':'+ayah+']'];
    if(tbod){
      tbod.querySelectorAll('tr[data-ayah="'+ayah+'"]').forEach(function(tr){
        if(tr.classList.contains('ayah-sep'))return;
        if(tr.classList.contains('audio'))return;
        if(tr.style.display==='none')return;
        var lbl=tr.querySelector('.label');
        var val=tr.cells[1];
        if(lbl&&val)texts.push(lbl.textContent.trim()+': '+val.textContent.trim());
      });
    }
    var text=texts.join('\\n');
    navigator.clipboard&&navigator.clipboard.writeText(text).then(function(){
      btn.textContent='\\u2714';
      setTimeout(function(){btn.textContent='\\u29c9 Copy';},1200);
    });
  };

  /* ---- Verse permalink click ---- */
  document.querySelectorAll('a.permalink').forEach(function(a){
    a.addEventListener('click',function(e){
      e.preventDefault();
      var url=location.origin+location.pathname+'#'+a.dataset.ayah;
      navigator.clipboard&&navigator.clipboard.writeText(url);
      history.replaceState(null,'','#'+a.dataset.ayah);
    });
  });
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
            surah_info=make_surah_info_bar(sura_idx),
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
            ho = hindi_omari.get((sura_idx, ayah), '')
            ru = roman_urdu.get((sura_idx, ayah), '')
            rj = roman_urdu_junagarhi.get((sura_idx, ayah), '')

            # Juz marker row
            juz_num = JUZ_STARTS.get((sura_idx, ayah))
            if juz_num:
                out.write(
                    "<tr class='juz-marker' data-ayah='%d'>"
                    "<td colspan='2'>&#128366; Juz %d begins here</td></tr>\n"
                    % (ayah, juz_num)
                )

            # Sajda badge
            sajda_badge = ''
            if (sura_idx, ayah) in SAJDA_VERSES:
                sajda_badge = "<span class='sajda-badge'>&#9737; Sajda</span>"

            # Copy button
            copy_btn = (
                "<button class='copy-btn' onclick='copyVerse(this,%d,%d)'"
                " title='Copy this verse'>\u29c9 Copy</button>"
            ) % (sura_idx, ayah)

            # Bookmark button
            bm_btn = (
                "<button class='bm-btn' id='bm-%d' onclick='toggleBookmark(%d,%d)'"
                " title='Bookmark this verse'>&#128278;</button>"
            ) % (ayah, sura_idx, ayah)

            out.write(
                "<tr class='ayah-sep' data-ayah='%d' id='ayah-%d'><td colspan='2'>"
                "<a class='permalink' href='#%d' data-ayah='%d'>Ayah %d</a>"
                "%s%s%s</td></tr>\n"
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
                "<tr class='hindi-omari' data-ayah='%d'><td class='label'>&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; (Al-Omari)</td><td class='hindi-omari-text' lang='hi'>%s</td></tr>\n"
                "<tr class='roman-urdu' data-ayah='%d'><td class='label'>Roman Urdu (Maududi)</td><td class='roman-urdu-text' lang='ur-Latn'>%s</td></tr>\n"
                "<tr class='roman-urdu-junagarhi' data-ayah='%d'><td class='label'>Roman Urdu (Junagarhi)</td><td class='roman-urdu-junagarhi-text' lang='ur-Latn'>%s</td></tr>\n"
                % (ayah, ayah,
                   ayah, ayah, ayah,
                   sajda_badge, copy_btn, bm_btn,
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
                   ayah, np_,
                   ayah, ho,
                   ayah, ru,
                   ayah, rj)
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
<header><a href="index.html">&#8962; Index</a>%s<a class="header-search" href="config.html" title="Settings">&#9881;</a><a class="header-search" href="search.html">&#128269; Search</a></header>
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
<em>Hindi Translation (&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2309;&#2344;&#2369;&#2357;&#2366;&#2342;):</em> Azizul Haq Al-Omari &mdash; via quranenc.com.<br>
<em>Hindi Tafsir (&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2340;&#2347;&#2381;&#2360;&#2368;&#2352;):</em> Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim.<br>
<em>Gujarati Translation (&#2711;&#2753;&#2716;&#2736;&#2750;&#2724;&#2752; &#2733;&#2750;&#2743;&#2750;&#2690;&#2724;&#2736;):</em> Rabila Al-Umry.<br>
<em>Nepali Translation:</em> Ahl-al-Hadith Central Society of Nepal.<br>
<em>Roman Urdu Translation:</em> Abul Ala Maududi &mdash; via <a href="https://quran.com" rel="noopener noreferrer">quran.com</a>.<br>
<em>Roman Urdu Translation:</em> Muhammad Junagarhi &mdash; via <a href="https://github.com/fawazahmed0/quran-api" rel="noopener noreferrer">fawazahmed0/quran-api</a>.<br>
Texts are reproduced verbatim; no alterations have been made.
</details>
<section id="recent-section" style="display:none;margin-bottom:18px">
<h2 style="margin-bottom:8px">&#128214; Continue Reading</h2>
<div id="recent-list" class="recent-list"></div>
</section>
<section id="bookmark-section" style="display:none;margin-bottom:18px">
<h2 style="margin-bottom:8px">&#128278; Last Saved Bookmark</h2>
<a id="bookmark-link" href="#" class="recent-card bm-card" style="display:inline-flex;flex-direction:column;text-decoration:none;margin-bottom:6px">
  <span id="bookmark-label" class="recent-label"></span>
  <span id="bookmark-meta" class="recent-ago"></span>
</a>
<a id="bookmark-all-link" href="bookmarks.html" class="recent-card bm-card" style="display:none;font-size:.85em;padding:7px 12px;margin-top:4px;text-decoration:none"></a>
</section>
<h2>Surahs (Chapters)</h2>
<div class="surah-grid">
<a href='how/index.html' style='border:2px solid #ffd54f'><strong>&#9878; How</strong> Ethical &amp; Duty Guide<span class='sg-meta'><span>Comprehensive categorized guide</span></span></a>
""" % (CSS + """
.recent-list{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:4px}
.recent-card{display:flex;flex-direction:column;padding:10px 14px;background:#e8f5e9;border:1px solid #a5d6a7;border-radius:6px;text-decoration:none;color:#1a3a5c;font-size:.95em;min-width:160px}
.recent-card:hover{background:#c8e6c9}
.bm-card{background:#fff8e1;border-color:#ffcc80;color:#e65100}
.bm-card:hover{background:#fff3cd}
.recent-label{font-weight:600;font-size:.9em}
.recent-ago{font-size:.78em;color:#555;margin-top:2px}
@media(prefers-color-scheme:dark){
  .recent-card{background:#0a1e10;border-color:#2e7d32;color:#a5d6a7}
  .recent-card:hover{background:#122a18}
  .bm-card{background:#2a1f00;border-color:#8b6914;color:#ffcc80}
  .bm-card:hover{background:#332600}
  .recent-ago{color:#90a4ae}
}""", make_surah_select(0)))
    for i, name in enumerate(SURA_NAME, 1):
        rev_order, rev_type = SURAH_REV[i - 1]
        type_label = 'Meccan' if rev_type == 'M' else 'Medinan'
        type_class = 'meccan' if rev_type == 'M' else 'medinan'
        juz = surah_juz_span(i)
        out.write(
            "<a href='%03d.html'>"
            "<strong>%d.</strong> %s"
            "<span class='sg-meta'>"
            "<span class='sib-type %s'>%s</span>"
            "<span>Juz %s</span>"
            "</span></a>\n"
            % (i, i, name, type_class, type_label, juz)
        )
    out.write("""\
</div>
</main>
%s
<script>
/* ---- Continue Reading — last read surah (single entry) ---- */
(function(){
  var HIST_KEY='quran-history';
  var section=document.getElementById('recent-section');
  var list=document.getElementById('recent-list');
  if(!section||!list)return;
  var h=null;
  try{h=JSON.parse(localStorage.getItem(HIST_KEY)||'null');}catch(_){return;}
  if(!h||!h.s)return;
  var href=String(h.s).padStart(3,'0')+'.html';
  var ago='';
  var diff=Math.round((Date.now()-h.t)/60000);
  if(diff<1)ago='just now';
  else if(diff<60)ago=diff+'m ago';
  else if(diff<1440)ago=Math.round(diff/60)+'h ago';
  else ago=Math.round(diff/1440)+'d ago';
  list.innerHTML='<a href="'+href+'" class="recent-card"><span class="recent-label">'+h.n+'</span><span class="recent-ago">'+ago+'</span></a>';
  section.style.display='';
})();
/* ---- Last saved bookmark (single card, links to bookmarks.html for full list) ---- */
(function(){
  var BM_KEY='quran-bookmark';
  var section=document.getElementById('bookmark-section');
  if(!section)return;
  var bms=[];
  try{bms=JSON.parse(localStorage.getItem(BM_KEY)||'[]');}catch(_){}
  if(!Array.isArray(bms)||!bms.length)return;
  var bm=bms[0];
  var href=String(bm.s).padStart(3,'0')+'.html#ayah-'+bm.a;
  var ago='';
  var diff=Math.round((Date.now()-bm.t)/60000);
  if(diff<1)ago='just now';
  else if(diff<60)ago=diff+'m ago';
  else if(diff<1440)ago=Math.round(diff/60)+'h ago';
  else ago=Math.round(diff/1440)+'d ago';
  var linkEl=document.getElementById('bookmark-link');
  var labelEl=document.getElementById('bookmark-label');
  var metaEl=document.getElementById('bookmark-meta');
  var allEl=document.getElementById('bookmark-all-link');
  if(linkEl)linkEl.href=href;
  var suraName=bm.n||('Surah '+bm.s);
  if(labelEl)labelEl.textContent='\U0001F4D6 '+suraName+', Ayah '+bm.a;
  if(metaEl)metaEl.textContent='Bookmarked '+ago+(bms.length>1?' (+'+(bms.length-1)+' more)':'');
  if(allEl){allEl.style.display='';allEl.textContent='\U0001F4DA View all '+bms.length+' bookmark'+(bms.length===1?'':'s');}
  section.style.display='';
})();
</script>
</body>
</html>""" % COMPACT_FOOTER)

print('Written: %s' % index_path)

# ---------------------------------------------------------------------------
# Generate docs/sd/ — per-field JSON files for lazy-loaded search
# sd/meta.json  : [[surahNum, ayahNum, "name"], ...]  — always loaded (~200 KB)
# sd/{key}.json : ["text", "text", ...]  — one file per translation field
#                 indexed in the same order as meta.json
# ---------------------------------------------------------------------------
import json, os as _os

sd_dir = _os.path.join(docs_dir, 'sd')
_os.makedirs(sd_dir, exist_ok=True)

# Build ordered list of (sura, ayah) pairs — 6236 entries
_ayah_order = []
for sura_idx in range(1, 115):
    size = SURA_SIZE[sura_idx - 1]
    name = SURA_NAME[sura_idx - 1]
    for ayah in range(1, size + 1):
        _ayah_order.append((sura_idx, ayah, name))

# meta.json
meta = [[s, a, n] for s, a, n in _ayah_order]
with open(_os.path.join(sd_dir, 'meta.json'), 'w', encoding='utf-8') as f:
    json.dump(meta, f, ensure_ascii=False, separators=(',', ':'))
print('Written: %s' % _os.path.join(sd_dir, 'meta.json'))

# Per-field arrays: each is a flat list of strings, same order as meta.json
_FIELD_SOURCES = [
    ('arabic',               arabic),
    ('translit',             translit),
    ('translit-unicode',     translit_unicode),
    ('trans',                pickthall),
    ('trans-yusuf',          yusufali),
    ('trans-sahih',          sahih),
    ('trans-qarai',          qarai),
    ('trans-hilali',         hilali),
    ('eng-abridged',         eng_abridged),
    ('hindi',                hindi),
    ('hindi-suhail',         hindi_suhail),
    ('hindi-mokhtasar',      hindi_mokhtasar),
    ('gujarati',             gujarati),
    ('nepali',               nepali),
    ('hindi-omari',          hindi_omari),
    ('roman-urdu',           roman_urdu),
    ('roman-urdu-junagarhi', roman_urdu_junagarhi),
]
for field_key, field_dict in _FIELD_SOURCES:
    arr = [field_dict.get((s, a), '') for s, a, _ in _ayah_order]
    out_path = _os.path.join(sd_dir, field_key + '.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(arr, f, ensure_ascii=False, separators=(',', ':'))
    print('Written: %s' % out_path)

# ---------------------------------------------------------------------------
# Generate search.html
# ---------------------------------------------------------------------------
SEARCH_CSS = CSS + """
.search-box{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.search-box input[type=text]{flex:1;min-width:160px;padding:9px 12px;border:1px solid #ccd6e0;border-radius:4px;font-size:1em;color:#111}
.search-box input[type=text]:focus{outline:2px solid #ffd54f;outline-offset:2px}
.search-box button{padding:9px 18px;background:#1a3a5c;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:1em;min-height:44px}
.search-box button:hover{background:#2a5a8c}
#search-status{font-size:.92em;color:#555;margin-bottom:10px}
.result-card{border:1px solid #ccd6e0;border-radius:6px;margin-bottom:12px;overflow:hidden}
.result-header{background:#1a3a5c;color:#fff;padding:7px 12px;font-size:.9em;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:4px}
.result-header a{color:#ffd54f;text-decoration:none;font-weight:bold;white-space:nowrap}
.result-header a:hover{text-decoration:underline}
.result-field{padding:6px 12px;font-size:.95em}
.result-field.arabic{font-family:'Scheherazade New','Amiri','Traditional Arabic',serif;font-size:1.4em;direction:rtl;text-align:right;line-height:2;background:#fff8e1}
.result-field.translit{background:#f0f4f8;font-weight:600}
.result-field.translit-unicode{background:#e8eaf6;font-weight:600;color:#283593}
.result-field.trans{background:#fff}
.result-field.trans-yusuf{background:#e8f5e9}
.result-field.trans-sahih{background:#e3f2fd}
.result-field.trans-qarai{background:#e0f2f1}
.result-field.trans-hilali{background:#f3e5f5;color:#4a148c}
.result-field.eng-abridged{background:#e8f4fd}
.result-field.hindi{background:#f5f0ff;font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#3a2a6c}
.result-field.hindi-suhail{background:#fff3e0;font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#5d4037}
.result-field.hindi-mokhtasar{background:#e8f5e0;font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#1b5e20}
.result-field.gujarati{background:#fce4ec;font-family:'Noto Sans Gujarati',Arial,sans-serif;color:#880e4f}
.result-field.nepali{background:#e8f5f0;font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#1a5276}
.result-field.hindi-omari{background:#fff0f5;font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#880e30}
.result-field.roman-urdu{background:#f0f4c3;font-weight:500;color:#33691e}
.result-field.roman-urdu-junagarhi{background:#e8f5e9;font-weight:500;color:#1b5e20}
.result-highlight{background:#fff176;border-radius:2px}
.pagination{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:16px 0;justify-content:center}
.pagination button{padding:7px 14px;border:none;border-radius:4px;cursor:pointer;background:#1a3a5c;color:#fff;font-size:.9em;min-width:36px;min-height:40px}
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
<script src="config.js"></script>
</head>
<body>
<header><a href="index.html">&#8962; Index</a>{surah_select}<a class="header-search" href="config.html" title="Settings">&#9881;</a><a class="header-search" href="search.html">&#128269; Search</a></header>
<main>
<h1>&#128269; Search the Qur&#x2019;an</h1>
<p style="font-size:.93em;color:#555;margin-bottom:14px">Searches the content types you have enabled in <a href="config.html">Settings</a>. Results link directly to the verse.</p>
<div class="search-box">
  <input type="text" id="q" placeholder="e.g. mercy, rahman, bismillah&hellip;" autofocus autocomplete="off" spellcheck="false">
  <button onclick="doSearch()">Search</button>
</div>
<div id="search-scope" style="font-size:.82em;color:#888;margin-bottom:10px"></div>
<div id="search-status"></div>
<div id="results"></div>
<div id="pagination"></div>
</main>
<footer><a href="sources.html">Sources &amp; Attribution</a> &nbsp;|&nbsp; <a href="license.html">License</a> &nbsp;|&nbsp; <a href="download.html">Download</a> &nbsp;|&nbsp; <a href="https://github.com/druvx13/Quran-data" rel="noopener noreferrer">GitHub</a></footer>
<script>
(function(){{
  var PAGE_SIZE = 20;
  var allMatches = [];
  var currentPage = 1;
  var currentTerms = [];
  var input = document.getElementById('q');
  var statusEl = document.getElementById('search-status');
  var scopeEl = document.getElementById('search-scope');
  var resultsEl = document.getElementById('results');
  var paginEl = document.getElementById('pagination');

  /* ---- Resolve user config ---- */
  var defaults=(typeof QURAN_CONFIG!=='undefined')?QURAN_CONFIG:{{}};
  var userPrefs=null;
  try{{var raw=localStorage.getItem('quran-cf');if(raw)userPrefs=JSON.parse(raw);}}catch(_){{}}
  function cfEnabled(key){{
    if(userPrefs&&userPrefs.hasOwnProperty(key))return userPrefs[key];
    return defaults.hasOwnProperty(key)?defaults[key]:false;
  }}

  /* ---- Field map: config-key -> label (sd/<key>.json holds text array) ---- */
  var FIELD_MAP=[
    ['arabic',               'Arabic'],
    ['translit',             'Translit. (Tanzil)'],
    ['translit-unicode',     'Translit. (Unicode)'],
    ['trans',                'English (Pickthall)'],
    ['trans-yusuf',          'English (Yusuf Ali)'],
    ['trans-sahih',          'English (Saheeh Int\u2019l)'],
    ['trans-qarai',          'English (Qarai)'],
    ['trans-hilali',         'English (Hilali)'],
    ['eng-abridged',         'Abridged Expl.'],
    ['hindi',                '\u0939\u093f\u0928\u094d\u0926\u0940 (Farooq)'],
    ['hindi-suhail',         '\u0939\u093f\u0928\u094d\u0926\u0940 (Suhail)'],
    ['hindi-mokhtasar',      '\u0939\u093f\u0928\u094d\u0926\u0940 \u0924\u092b\u094d\u0938\u0940\u0930 (Mokhtasar)'],
    ['gujarati',             '\u0a97\u0ac1\u0a9c\u0ab0\u0abe\u0aa4\u0ac0 (Rabila)'],
    ['nepali',               'Nepali (Ahl-al-Hadith)'],
    ['hindi-omari',          '\u0939\u093f\u0928\u094d\u0926\u0940 (Al-Omari)'],
    ['roman-urdu',           'Roman Urdu (Maududi)'],
    ['roman-urdu-junagarhi', 'Roman Urdu (Junagarhi)']
  ];

  function getActiveFields(){{
    var active=[];
    FIELD_MAP.forEach(function(f){{if(cfEnabled(f[0]))active.push(f);}});
    return active;
  }}

  function updateScopeNote(){{
    var active=getActiveFields();
    var labels=active.map(function(f){{return f[1];}});
    labels.push('Surah name');
    if(scopeEl)scopeEl.textContent='Searching in: '+labels.join(', ')+'. Change in \u2699 Settings.';
  }}
  updateScopeNote();

  /* ---- Lazy JSON loader: fetch each sd/*.json file once, cache in memory ---- */
  var metaData=null;
  var fieldCache={{}};
  var _pending={{}};

  function fetchJson(url){{
    if(!_pending[url]){{
      _pending[url]=fetch(url).then(function(r){{
        if(!r.ok)throw new Error('HTTP '+r.status+' ('+url+')');
        return r.json();
      }});
    }}
    return _pending[url];
  }}

  function loadMeta(){{
    if(metaData)return Promise.resolve(metaData);
    return fetchJson('sd/meta.json').then(function(d){{metaData=d;return d;}});
  }}

  function loadField(key){{
    if(fieldCache[key])return Promise.resolve(fieldCache[key]);
    return fetchJson('sd/'+key+'.json').then(function(d){{fieldCache[key]=d;return d;}});
  }}

  /* Prefetch meta immediately so first search is fast */
  loadMeta();

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
    var activeFields=getActiveFields();
    for(var i=start;i<end;i++){{
      var m=allMatches[i];
      var href=String(m.s).padStart(3,'0')+'.html#ayah-'+m.a;
      html+='<div class="result-card">'
        +'<div class="result-header"><span>Surah '+m.s+':'+m.a+' &mdash; '+escHtml(m.n)+'</span>'
        +'<a href="'+href+'">View verse &rarr;</a></div>';
      activeFields.forEach(function(f){{
        var arr=fieldCache[f[0]]||[];
        var val=arr[m.i]||'';
        if(!val)return;
        html+='<div class="result-field '+f[0]+'">'+highlight(val,currentTerms)+'</div>';
      }});
      html+='</div>';
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
    var activeFields = getActiveFields();
    statusEl.textContent = 'Loading\u2026';
    resultsEl.innerHTML='';
    paginEl.innerHTML='';
    var fieldPromises = activeFields.map(function(f){{return loadField(f[0]);}});
    Promise.all([loadMeta()].concat(fieldPromises)).then(function(){{
      allMatches = [];
      for(var i=0;i<metaData.length;i++){{
        var row=metaData[i];
        var parts=[row[2]];
        activeFields.forEach(function(f){{
          var arr=fieldCache[f[0]]||[];
          parts.push(arr[i]||'');
        }});
        var haystack=parts.join(' ').toLowerCase();
        if(currentTerms.every(function(t){{return haystack.indexOf(t)!==-1;}})){{
          allMatches.push({{i:i,s:row[0],a:row[1],n:row[2]}});
        }}
      }}
      if(allMatches.length===0){{
        statusEl.textContent='No results found.';
        resultsEl.innerHTML='';
        paginEl.innerHTML='';
        return;
      }}
      renderPage(1);
    }}).catch(function(err){{
      statusEl.textContent='Error loading search data. Please try again.';
      console.error(err);
    }});
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

# ---------------------------------------------------------------------------
# Generate config.js  (universal default translation visibility)
# ---------------------------------------------------------------------------
config_js_path = os.path.join(docs_dir, 'config.js')
with open(config_js_path, 'w', encoding='utf-8') as f:
    f.write('/* Quran reader default translation visibility.\n')
    f.write('   Edit the true/false values below, or use the Settings page (config.html)\n')
    f.write('   to save personal overrides in your browser. */\n')
    f.write('var QURAN_CONFIG={\n')
    for i, (cls, label, default) in enumerate(CF_ITEMS):
        comma = ',' if i < len(CF_ITEMS) - 1 else ''
        val = 'true' if default else 'false'
        f.write('  "%s":%s%s\n' % (cls, val, comma))
    f.write('};\n')
print('Written: %s' % config_js_path)

# ---------------------------------------------------------------------------
# Generate config.html  (settings page for user preferences)
# ---------------------------------------------------------------------------
config_items_html = []
for cls, label, default in CF_ITEMS:
    config_items_html.append(
        "<div class='cfg-row'>"
        "<label class='cfg-switch'>"
        "<input type='checkbox' data-key='%s'>"
        "<span class='cfg-slider'></span>"
        "</label>"
        "<span class='cfg-label'>%s</span>"
        "</div>" % (cls, label)
    )

CONFIG_CSS = CSS + """
.cfg-card{background:#f0f4f8;border:1px solid #ccd6e0;border-radius:8px;padding:20px;max-width:600px;margin:0 auto}
.cfg-row{display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid #e0e0e0}
.cfg-row:last-child{border-bottom:none}
.cfg-label{font-size:.95em;color:#1a3a5c}
.cfg-switch{position:relative;display:inline-block;width:44px;height:24px;flex-shrink:0}
.cfg-switch input{opacity:0;width:0;height:0}
.cfg-slider{position:absolute;cursor:pointer;inset:0;background:#ccc;border-radius:24px;transition:.25s}
.cfg-slider::before{content:'';position:absolute;height:18px;width:18px;left:3px;bottom:3px;background:#fff;border-radius:50%;transition:.25s}
.cfg-switch input:checked+.cfg-slider{background:#1a3a5c}
.cfg-switch input:checked+.cfg-slider::before{transform:translateX(20px)}
.cfg-switch input:focus+.cfg-slider{outline:2px solid #ffd54f;outline-offset:2px}
.cfg-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}
.cfg-actions button{padding:8px 18px;border:none;border-radius:4px;cursor:pointer;font-size:.92em;min-height:40px}
.cfg-btn-reset{background:#e0e0e0;color:#333}
.cfg-btn-reset:hover{background:#bdbdbd}
.cfg-saved{color:#1b5e20;font-size:.88em;margin-left:8px;opacity:0;transition:opacity .3s}
.hist-card{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 12px;background:#e8f5e9;border:1px solid #a5d6a7;border-radius:6px;margin-bottom:6px;font-size:.9em}
.hist-card a{color:#1a3a5c;text-decoration:none;font-weight:600;flex:1}
.hist-card a:hover{text-decoration:underline}
.hist-ago{font-size:.8em;color:#555;white-space:nowrap}
@media(prefers-color-scheme:dark){
  .cfg-card{background:#1e2a3a;border-color:#334}
  .cfg-row{border-bottom-color:#333}
  .cfg-label{color:#90caf9}
  .cfg-slider{background:#555}
  .cfg-btn-reset{background:#333;color:#e8e8e8}
  .cfg-btn-reset:hover{background:#444}
  .cfg-saved{color:#a5d6a7}
  .hist-card{background:#0a1e10;border-color:#2e7d32}
  .hist-card a{color:#a5d6a7}
  .hist-ago{color:#90a4ae}
}"""

config_html_path = os.path.join(docs_dir, 'config.html')
with open(config_html_path, 'w', encoding='utf-8') as f:
    f.write("""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Settings &ndash; Qur&rsquo;an Reader</title>
<style>
%s
</style>
<script src="config.js"></script>
</head>
<body>
<header><a href="index.html">&#8962; Index</a>%s<a class="header-search" href="config.html" title="Settings">&#9881;</a><a class="header-search" href="search.html">&#128269; Search</a></header>
<main>
<h1>&#9881; Reader Settings</h1>
<p style="font-size:.93em;color:#555;margin-bottom:14px">Choose which translations appear by default when you open a Surah page. Your preferences are saved in your browser.</p>
<div class="cfg-card">
<h2 style="margin-top:0">Default Translation Visibility</h2>
%s
<div class="cfg-actions">
<button class="cfg-btn-reset" onclick="cfgReset()">Reset to Defaults</button>
<span class="cfg-saved" id="cfg-saved">&#10003; Saved</span>
</div>
</div>
<div class="cfg-card" style="margin-top:20px">
<h2 style="margin-top:0">&#128278; Saved Bookmarks</h2>
<div id="bm-display"><p style="font-size:.9em;color:#888">No bookmarks saved yet. Use the &#128278; button on any verse to bookmark it.</p></div>
<div class="cfg-actions">
<a href="bookmarks.html" class="cfg-btn-reset" style="text-decoration:none;display:inline-block">&#128218; Manage All Bookmarks &rarr;</a>
<button class="cfg-btn-reset" id="bm-clear-btn" onclick="clearBookmarks()" style="display:none">Clear All Bookmarks</button>
</div>
</div>
<div class="cfg-card" style="margin-top:20px">
<h2 style="margin-top:0">&#128214; Last Read</h2>
<div id="hist-list"><p style="font-size:.9em;color:#888">No history yet.</p></div>
<div class="cfg-actions">
<button class="cfg-btn-reset" onclick="clearHistory()">Clear</button>
</div>
</div>
</main>
<footer>Settings are stored locally in your browser via localStorage. &nbsp;|&nbsp; <a href="sources.html">Sources</a> &nbsp;|&nbsp; <a href="license.html">License</a> &nbsp;|&nbsp; <a href="download.html">Download</a> &nbsp;|&nbsp; <a href="https://github.com/druvx13/Quran-data" rel="noopener noreferrer">GitHub</a></footer>
<script>
(function(){
  var defaults=(typeof QURAN_CONFIG!=='undefined')?QURAN_CONFIG:{};
  var userPrefs=null;
  try{var raw=localStorage.getItem('quran-cf');if(raw)userPrefs=JSON.parse(raw);}catch(e){}

  var switches=document.querySelectorAll('.cfg-switch input[type=checkbox]');
  switches.forEach(function(sw){
    var key=sw.dataset.key;
    var on;
    if(userPrefs&&userPrefs.hasOwnProperty(key)){on=userPrefs[key];}
    else{on=defaults.hasOwnProperty(key)?defaults[key]:false;}
    sw.checked=on;
  });

  function savePrefs(){
    var prefs={};
    switches.forEach(function(sw){prefs[sw.dataset.key]=sw.checked;});
    try{localStorage.setItem('quran-cf',JSON.stringify(prefs));}catch(e){}
    var badge=document.getElementById('cfg-saved');
    if(badge){badge.style.opacity='1';setTimeout(function(){badge.style.opacity='0';},1500);}
  }

  switches.forEach(function(sw){
    sw.addEventListener('change',savePrefs);
  });

  window.cfgReset=function(){
    try{localStorage.removeItem('quran-cf');}catch(e){}
    switches.forEach(function(sw){
      var key=sw.dataset.key;
      sw.checked=defaults.hasOwnProperty(key)?defaults[key]:false;
    });
    var badge=document.getElementById('cfg-saved');
    if(badge){badge.style.opacity='1';setTimeout(function(){badge.style.opacity='0';},1500);}
  };

  /* ---- Last Read (single entry) ---- */
  var HIST_KEY='quran-history';
  function loadHistory(){
    var listEl=document.getElementById('hist-list');
    if(!listEl)return;
    var h=null;
    try{h=JSON.parse(localStorage.getItem(HIST_KEY)||'null');}catch(_){}
    if(!h||!h.s){listEl.innerHTML='<p style="font-size:.9em;color:#888">No history yet.</p>';return;}
    var href=String(h.s).padStart(3,'0')+'.html';
    var ago='';
    var diff=Math.round((Date.now()-h.t)/60000);
    if(diff<1)ago='just now';
    else if(diff<60)ago=diff+'m ago';
    else if(diff<1440)ago=Math.round(diff/60)+'h ago';
    else ago=Math.round(diff/1440)+'d ago';
    listEl.innerHTML='<div class="hist-card"><a href="'+href+'">'+h.n+'</a><span class="hist-ago">'+ago+'</span></div>';
  }
  window.clearHistory=function(){
    try{localStorage.removeItem(HIST_KEY);}catch(_){}
    loadHistory();
  };
  loadHistory();

  /* ---- Bookmarks (shows last saved, links to bookmarks.html) ---- */
  var BM_KEY='quran-bookmark';
  function loadBookmarks(){
    var dispEl=document.getElementById('bm-display');
    var clearBtn=document.getElementById('bm-clear-btn');
    if(!dispEl)return;
    var bms=[];
    try{bms=JSON.parse(localStorage.getItem(BM_KEY)||'[]');}catch(_){}
    if(!Array.isArray(bms)||!bms.length){
      dispEl.innerHTML='<p style="font-size:.9em;color:#888">No bookmarks saved yet. Use the \U0001F516 button on any verse to bookmark it.</p>';
      if(clearBtn)clearBtn.style.display='none';
      return;
    }
    var bm=bms[0];
    var href=String(bm.s).padStart(3,'0')+'.html#ayah-'+bm.a;
    var ago='';
    var diff=Math.round((Date.now()-bm.t)/60000);
    if(diff<1)ago='just now';
    else if(diff<60)ago=diff+'m ago';
    else if(diff<1440)ago=Math.round(diff/60)+'h ago';
    else ago=Math.round(diff/1440)+'d ago';
    var suraName=bm.n||('Surah '+bm.s);
    dispEl.innerHTML='<div class="hist-card"><a href="'+href+'">\U0001F4D6 '+suraName+', Ayah '+bm.a+'</a><span class="hist-ago">'+ago+(bms.length>1?' &mdash; '+(bms.length-1)+' more bookmark'+(bms.length===2?'':'s')+' saved':'')+'</span></div>';
    if(clearBtn)clearBtn.style.display='';
  }
  window.clearBookmarks=function(){
    try{localStorage.removeItem(BM_KEY);}catch(_){}
    loadBookmarks();
  };
  loadBookmarks();
})();
</script>
</body>
</html>""" % (CONFIG_CSS, make_surah_select(0), '\n'.join(config_items_html)))
print('Written: %s' % config_html_path)

# ---------------------------------------------------------------------------
# Generate bookmarks.html  (full bookmark manager: list, export, import)
# ---------------------------------------------------------------------------
BOOKMARKS_CSS = CSS + """
.bm-list{list-style:none;padding:0;margin:0}
.bm-item{display:flex;align-items:flex-start;gap:10px;padding:10px 14px;border-bottom:1px solid #dce8f0;font-size:.95em}
.bm-item:last-child{border-bottom:none}
.bm-item-info{flex:1}
.bm-item-info a{color:#1a3a5c;text-decoration:none;font-weight:600}
.bm-item-info a:hover{text-decoration:underline}
.bm-item-meta{font-size:.78em;color:#666;margin-top:2px}
.bm-item-del{flex-shrink:0;background:none;border:1px solid #e57373;color:#c62828;border-radius:4px;padding:3px 9px;cursor:pointer;font-size:.83em}
.bm-item-del:hover{background:#fdecea}
.bm-empty{color:#888;font-size:.9em;padding:12px 0}
.bm-actions{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}
.bm-actions button,.bm-actions label{padding:8px 16px;border:1px solid #ccd6e0;border-radius:4px;cursor:pointer;font-size:.9em;background:#fff;color:#1a3a5c}
.bm-actions button:hover,.bm-actions label:hover{background:#f0f4f8}
.bm-count{font-size:.85em;color:#555;margin-bottom:10px}
@media(prefers-color-scheme:dark){
  .bm-item{border-color:#1e3a4c}
  .bm-item-info a{color:#90caf9}
  .bm-item-meta{color:#90a4ae}
  .bm-item-del{border-color:#8b3a3a;color:#ef9a9a}
  .bm-item-del:hover{background:#2a1010}
  .bm-actions button,.bm-actions label{background:#0d1f2d;border-color:#1e3a4c;color:#90caf9}
  .bm-actions button:hover,.bm-actions label:hover{background:#162d40}
  .bm-count{color:#90a4ae}
}
"""

BOOKMARKS_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bookmarks &ndash; Qur&rsquo;an</title>
<style>
{css}
</style>
</head>
<body>
<header><a href="index.html">&#8962; Index</a>{surah_select}<a class="header-search" href="config.html" title="Settings">&#9881;</a><a class="header-search" href="search.html">&#128269; Search</a></header>
<main>
<h1>&#128278; My Bookmarks</h1>
<p style="font-size:.93em;color:#555;margin-bottom:14px">Bookmarks are stored in your browser. Use Export to save a backup and Import to restore them on another device.</p>
<div class="bm-actions">
  <button onclick="exportBm()">&#11015; Export JSON</button>
  <label>&#11014; Import JSON<input type="file" id="bm-import" accept=".json,application/json" style="display:none" onchange="importBm(this)"></label>
  <button onclick="clearAllBm()" style="border-color:#e57373;color:#c62828">&#128465; Clear All</button>
</div>
<div class="bm-count" id="bm-count"></div>
<ul class="bm-list" id="bm-list"></ul>
</main>
<footer><a href="sources.html">Sources &amp; Attribution</a> &nbsp;|&nbsp; <a href="license.html">License</a> &nbsp;|&nbsp; <a href="download.html">Download</a> &nbsp;|&nbsp; <a href="https://github.com/druvx13/Quran-data" rel="noopener noreferrer">GitHub</a></footer>
<script>
(function(){{
  var BM_KEY='quran-bookmark';

  function load(){{
    var bms=[];
    try{{bms=JSON.parse(localStorage.getItem(BM_KEY)||'[]');}}catch(_){{}}
    if(!Array.isArray(bms))bms=[];
    return bms;
  }}

  function save(bms){{
    try{{localStorage.setItem(BM_KEY,JSON.stringify(bms));}}catch(_){{}}
  }}

  function relTime(ts){{
    var diff=Math.round((Date.now()-ts)/60000);
    if(diff<1)return 'just now';
    if(diff<60)return diff+'m ago';
    if(diff<1440)return Math.round(diff/60)+'h ago';
    return Math.round(diff/1440)+'d ago';
  }}

  function escHtml(s){{
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }}

  function render(){{
    var bms=load();
    var listEl=document.getElementById('bm-list');
    var countEl=document.getElementById('bm-count');
    if(!listEl)return;
    if(!bms.length){{
      listEl.innerHTML='<li class="bm-empty">No bookmarks saved yet. Use the &#128278; button on any verse to add one.</li>';
      if(countEl)countEl.textContent='';
      return;
    }}
    if(countEl)countEl.textContent=bms.length+' bookmark'+(bms.length===1?'':'s')+' saved';
    var html='';
    for(var i=0;i<bms.length;i++){{
      var b=bms[i];
      var href=String(b.s).padStart(3,'0')+'.html#ayah-'+b.a;
      var suraName=escHtml(b.n||('Surah '+b.s));
      html+='<li class="bm-item">'
        +'<div class="bm-item-info">'
        +'<a href="'+href+'">\U0001F4D6 '+suraName+', Ayah '+b.a+'</a>'
        +'<div class="bm-item-meta">Bookmarked '+relTime(b.t)+'</div>'
        +'</div>'
        +'<button class="bm-item-del" onclick="deleteBm('+i+')" title="Delete this bookmark">&times; Remove</button>'
        +'</li>';
    }}
    listEl.innerHTML=html;
  }}

  window.deleteBm=function(idx){{
    var bms=load();
    bms.splice(idx,1);
    save(bms);
    render();
  }};

  window.clearAllBm=function(){{
    if(!confirm('Remove all '+load().length+' bookmark(s)?'))return;
    save([]);
    render();
  }};

  window.exportBm=function(){{
    var bms=load();
    var blob=new Blob([JSON.stringify(bms,null,2)],{{type:'application/json'}});
    var url=URL.createObjectURL(blob);
    var a=document.createElement('a');
    a.href=url;
    a.download='quran-bookmarks.json';
    document.body.appendChild(a);
    a.click();
    setTimeout(function(){{URL.revokeObjectURL(url);document.body.removeChild(a);}},100);
  }};

  window.importBm=function(input){{
    var file=input.files[0];
    if(!file)return;
    var reader=new FileReader();
    reader.onload=function(e){{
      try{{
        var data=JSON.parse(e.target.result);
        if(!Array.isArray(data))throw new Error('Not an array');
        /* Merge: deduplicate by surah+ayah (imported entries win on conflict) */
        var existing=load();
        var map={{}};
        existing.forEach(function(b){{map[b.s+':'+b.a]=b;}});
        data.forEach(function(b){{if(b.s&&b.a)map[b.s+':'+b.a]=b;}});
        var merged=Object.values(map).sort(function(a,b){{return b.t-a.t;}});
        save(merged);
        render();
        alert('Imported '+data.length+' bookmark(s). Total: '+merged.length+'.');
      }}catch(err){{
        alert('Import failed: '+err.message);
      }}
      input.value='';
    }};
    reader.readAsText(file);
  }};

  render();
}})();
</script>
</body>
</html>"""

bookmarks_html_path = os.path.join(docs_dir, 'bookmarks.html')
with open(bookmarks_html_path, 'w', encoding='utf-8') as f:
    f.write(BOOKMARKS_HTML.format(
        css=BOOKMARKS_CSS,
        surah_select=make_surah_select(0),
    ))
print('Written: %s' % bookmarks_html_path)

# ---------------------------------------------------------------------------
# Generate sources.html  (comprehensive source attribution page)
# ---------------------------------------------------------------------------
SOURCES_CSS = CSS + """
.src-section{margin-bottom:28px}
.src-section h2{color:#1a3a5c;margin:0 0 10px;font-size:1.15em;border-bottom:2px solid #ffd54f;padding-bottom:4px}
.src-table{width:100%;border-collapse:collapse;margin-bottom:8px}
.src-table th{background:#1a3a5c;color:#fff;padding:8px 12px;text-align:left;font-size:.88em}
.src-table td{padding:8px 12px;border:1px solid #ccd6e0;font-size:.92em;vertical-align:top}
.src-table tr:nth-child(even) td{background:#f7f9fb}
.src-note{font-size:.88em;color:#555;margin-top:6px;line-height:1.6}
@media(prefers-color-scheme:dark){
  .src-section h2{color:#90caf9;border-bottom-color:#ffd54f}
  .src-table td{border-color:#333;background:#121212}
  .src-table tr:nth-child(even) td{background:#1a1a1a}
  .src-note{color:#aaa}
}
@media(max-width:600px){
  .src-table,.src-table thead,.src-table tbody,.src-table tr,.src-table th,.src-table td{display:block;width:100%%}
  .src-table thead{display:none}
  .src-table td{border:none;border-bottom:1px solid #e0e0e0;padding:4px 8px}
  .src-table td::before{content:attr(data-label);font-weight:bold;display:block;font-size:.8em;color:#888;margin-bottom:2px}
}"""

sources_html_path = os.path.join(docs_dir, 'sources.html')
with open(sources_html_path, 'w', encoding='utf-8') as f:
    f.write("""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sources &amp; Attribution &ndash; Qur&rsquo;an Reader</title>
<style>
%s
</style>
</head>
<body>
<header><a href="index.html">&#8962; Index</a>%s<a class="header-search" href="config.html" title="Settings">&#9881;</a><a class="header-search" href="search.html">&#128269; Search</a></header>
<main>
<h1>&#128218; Sources &amp; Attribution</h1>
<p style="font-size:.93em;color:#555;margin-bottom:20px">All texts displayed on this website are reproduced verbatim from their original sources. No alterations have been made. Below is a comprehensive listing of every source used.</p>

<div class="src-section">
<h2>&#127770; Arabic Text</h2>
<table class="src-table">
<thead><tr><th>Source</th><th>Details</th></tr></thead>
<tbody>
<tr><td data-label="Source">Standard Uthmani Script</td><td data-label="Details">The Arabic text uses the standard Uthmani script of the Qur&#x2019;an, the universally recognized written form.</td></tr>
</tbody>
</table>
</div>

<div class="src-section">
<h2>&#127911; Audio Recitation</h2>
<table class="src-table">
<thead><tr><th>Reciter</th><th>Source</th></tr></thead>
<tbody>
<tr><td data-label="Reciter">Mishary Rashid Alafasy</td><td data-label="Source">Audio hosted via <a href="https://druvx13-quran-audio-alafasy.hf.space" rel="noopener noreferrer">Hugging Face Space</a>. Original audio sourced from <a href="https://versebyversequran.com" rel="noopener noreferrer">versebyversequran.com</a>.</td></tr>
</tbody>
</table>
</div>

<div class="src-section">
<h2>&#128221; Transliteration</h2>
<table class="src-table">
<thead><tr><th>Source</th><th>Details</th></tr></thead>
<tbody>
<tr><td data-label="Source">Tanzil.net</td><td data-label="Details">English transliteration of the Qur&#x2019;an from <a href="https://tanzil.net" rel="noopener noreferrer">Tanzil.net</a>.</td></tr>
<tr><td data-label="Source">Quran Unicode Project</td><td data-label="Details">Unicode-based transliteration (<code>translit_en.txt</code>) from the Quran Unicode Project.</td></tr>
</tbody>
</table>
</div>

<div class="src-section">
<h2>&#127468;&#127463; English Translations</h2>
<table class="src-table">
<thead><tr><th>Translator</th><th>Work / Notes</th></tr></thead>
<tbody>
<tr><td data-label="Translator">Mohammed Marmaduke Pickthall</td><td data-label="Notes"><em>The Meaning of the Glorious Koran</em> (1930) &mdash; <strong>Public Domain</strong>. Source: Tanzil.net.</td></tr>
<tr><td data-label="Translator">Abdullah Yusuf Ali</td><td data-label="Notes"><em>The Holy Quran: Text, Translation and Commentary</em> &mdash; <strong>Public Domain</strong>.</td></tr>
<tr><td data-label="Translator">Saheeh International</td><td data-label="Notes">Widely used modern English translation.</td></tr>
<tr><td data-label="Translator">Ali Quli Qarai</td><td data-label="Notes">Contemporary English translation.</td></tr>
<tr><td data-label="Translator">Dr. Muhammad Taqi-ud-Din Al-Hilali &amp; Dr. Muhammad Muhsin Khan</td><td data-label="Notes">Translation with parenthetical commentary.</td></tr>
</tbody>
</table>
</div>

<div class="src-section">
<h2>&#128214; English Explanation</h2>
<table class="src-table">
<thead><tr><th>Work</th><th>Details</th></tr></thead>
<tbody>
<tr><td data-label="Work">Abridged Explanation of the Quran</td><td data-label="Details">Concise English explanation of each verse.</td></tr>
</tbody>
</table>
</div>

<div class="src-section">
<h2>&#127470;&#127475; Hindi Translations (&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2309;&#2344;&#2369;&#2357;&#2366;&#2342;)</h2>
<table class="src-table">
<thead><tr><th>Translator</th><th>Details</th></tr></thead>
<tbody>
<tr><td data-label="Translator">Muhammad Farooq Khan &amp; Muhammad Ahmed</td><td data-label="Details">Hindi translation of the Qur&#x2019;an.</td></tr>
<tr><td data-label="Translator">Suhel Farooq Khan &amp; Saifur Rahman Nadwi</td><td data-label="Details">Hindi translation of the Qur&#x2019;an.</td></tr>
<tr><td data-label="Translator">Azizul Haq Al-Omari</td><td data-label="Details">Hindi translation via <a href="https://quranenc.com" rel="noopener noreferrer">quranenc.com</a>.</td></tr>
</tbody>
</table>
</div>

<div class="src-section">
<h2>&#128214; Hindi Tafsir (&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2340;&#2347;&#2381;&#2360;&#2368;&#2352;)</h2>
<table class="src-table">
<thead><tr><th>Work</th><th>Details</th></tr></thead>
<tbody>
<tr><td data-label="Work">Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim</td><td data-label="Details">Concise Hindi tafsir (exegesis) of the Qur&#x2019;an.</td></tr>
</tbody>
</table>
</div>

<div class="src-section">
<h2>&#127470;&#127475; Gujarati Translation (&#2711;&#2753;&#2716;&#2736;&#2750;&#2724;&#2752;)</h2>
<table class="src-table">
<thead><tr><th>Translator</th><th>Details</th></tr></thead>
<tbody>
<tr><td data-label="Translator">Rabila Al-Umry</td><td data-label="Details">Gujarati translation of the Qur&#x2019;an.</td></tr>
</tbody>
</table>
</div>

<div class="src-section">
<h2>&#127475;&#127477; Nepali Translation</h2>
<table class="src-table">
<thead><tr><th>Source</th><th>Details</th></tr></thead>
<tbody>
<tr><td data-label="Source">Ahl-al-Hadith Central Society of Nepal</td><td data-label="Details">Nepali translation of the Qur&#x2019;an.</td></tr>
</tbody>
</table>
</div>

<div class="src-section">
<h2>&#128221; Roman Urdu Translations</h2>
<table class="src-table">
<thead><tr><th>Translator</th><th>Source</th></tr></thead>
<tbody>
<tr><td data-label="Translator">Abul Ala Maududi</td><td data-label="Source">Roman Urdu translation via <a href="https://quran.com" rel="noopener noreferrer">quran.com</a>.</td></tr>
<tr><td data-label="Translator">Muhammad Junagarhi</td><td data-label="Source">Roman Urdu translation via <a href="https://github.com/fawazahmed0/quran-api" rel="noopener noreferrer">fawazahmed0/quran-api</a>.</td></tr>
</tbody>
</table>
</div>

<div class="src-section">
<h2>&#128279; API &amp; Data Sources</h2>
<table class="src-table">
<thead><tr><th>Source</th><th>URL</th></tr></thead>
<tbody>
<tr><td data-label="Source">Tanzil.net</td><td data-label="URL"><a href="https://tanzil.net" rel="noopener noreferrer">tanzil.net</a> &mdash; Qur&#x2019;an transliteration and Pickthall translation.</td></tr>
<tr><td data-label="Source">fawazahmed0/quran-api</td><td data-label="URL"><a href="https://github.com/fawazahmed0/quran-api" rel="noopener noreferrer">github.com/fawazahmed0/quran-api</a> &mdash; Additional translations (Roman Urdu, Romanized Hindi/Gujarati, Urdu).</td></tr>
<tr><td data-label="Source">quran.com</td><td data-label="URL"><a href="https://quran.com" rel="noopener noreferrer">quran.com</a> &mdash; Roman Urdu (Maududi) translation.</td></tr>
<tr><td data-label="Source">quranenc.com</td><td data-label="URL"><a href="https://quranenc.com" rel="noopener noreferrer">quranenc.com</a> &mdash; Hindi (Al-Omari) translation.</td></tr>
</tbody>
</table>
</div>

<p class="src-note"><strong>Note:</strong> All texts are reproduced verbatim from their respective sources. No alterations, abridgements, or editorial changes have been made. The Pickthall translation (1930) and Yusuf Ali translation are in the public domain. Other translations are reproduced under their original copyright and licence terms.</p>

</main>
<footer><a href="sources.html">Sources &amp; Attribution</a> &nbsp;|&nbsp; <a href="license.html">License</a> &nbsp;|&nbsp; <a href="download.html">Download</a> &nbsp;|&nbsp; <a href="https://github.com/druvx13/Quran-data" rel="noopener noreferrer">GitHub</a></footer>
</body>
</html>""" % (SOURCES_CSS, make_surah_select(0)))
print('Written: %s' % sources_html_path)

# ---------------------------------------------------------------------------
# Generate license.html  (project license page)
# ---------------------------------------------------------------------------
LICENSE_CSS = CSS + """
.license-card{background:#f0f4f8;border:1px solid #ccd6e0;border-radius:8px;padding:20px 24px;max-width:800px;margin:0 auto}
.license-card h2{color:#1a3a5c;margin:20px 0 8px;font-size:1.1em}
.license-card h2:first-child{margin-top:0}
.license-card p,.license-card li{font-size:.92em;line-height:1.7;color:#333}
.license-card pre{background:#fff;border:1px solid #ddd;border-radius:4px;padding:12px;font-size:.82em;overflow-x:auto;white-space:pre-wrap;word-wrap:break-word;line-height:1.5}
.license-note{background:#fff8e1;border-left:4px solid #ffd54f;padding:10px 14px;margin-top:16px;font-size:.9em;border-radius:0 4px 4px 0}
@media(prefers-color-scheme:dark){
  .license-card{background:#1e2a3a;border-color:#334}
  .license-card p,.license-card li{color:#e0e0e0}
  .license-card pre{background:#121212;border-color:#333;color:#e0e0e0}
  .license-card h2{color:#90caf9}
  .license-note{background:#2a2010;border-left-color:#ffc107;color:#e8e8e8}
}"""

# Read LICENSE file
license_text = ''
license_path_src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'LICENSE')
if os.path.exists(license_path_src):
    with open(license_path_src, 'r', encoding='utf-8') as lf:
        license_text = lf.read()
else:
    license_text = '(LICENSE file not found)'

# Escape HTML in license text
license_text_escaped = license_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

license_html_path = os.path.join(docs_dir, 'license.html')
with open(license_html_path, 'w', encoding='utf-8') as f:
    f.write("""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>License &ndash; Qur&rsquo;an Reader</title>
<style>
%s
</style>
</head>
<body>
<header><a href="index.html">&#8962; Index</a>%s<a class="header-search" href="config.html" title="Settings">&#9881;</a><a class="header-search" href="search.html">&#128269; Search</a></header>
<main>
<h1>&#128220; License</h1>
<div class="license-card">
<h2>Unconditional Liberty Instrument (ULI) &mdash; Version 1.0</h2>
<p>This project is licensed under the <strong>Unconditional Liberty Instrument (ULI)</strong>, Version 1.0. The full text of the license is reproduced below.</p>
<pre>%s</pre>
<div class="license-note">
<strong>Note:</strong> This licence applies to the scripts and configuration files in this repository. The translation texts in <code>data/</code> and <code>output/</code> are reproduced verbatim from their respective sources and remain subject to their original copyright and licence terms. The Pickthall translation (1930) is in the public domain.
</div>
</div>
<h2 style="margin-top:24px">&#128279; Repository</h2>
<p>The source code and all data files for this project are available on GitHub:</p>
<p style="font-size:1.05em"><a href="https://github.com/druvx13/Quran-data" rel="noopener noreferrer">github.com/druvx13/Quran-data</a></p>
</main>
<footer><a href="sources.html">Sources &amp; Attribution</a> &nbsp;|&nbsp; <a href="license.html">License</a> &nbsp;|&nbsp; <a href="download.html">Download</a> &nbsp;|&nbsp; <a href="https://github.com/druvx13/Quran-data" rel="noopener noreferrer">GitHub</a></footer>
</body>
</html>""" % (LICENSE_CSS, make_surah_select(0), license_text_escaped))
print('Written: %s' % license_html_path)

# ---------------------------------------------------------------------------
# Generate download.html  (client-side zip download page)
# ---------------------------------------------------------------------------
DOWNLOAD_CSS = CSS + """
.dl-section{margin-bottom:24px}
.dl-section h2{color:#1a3a5c;margin:0 0 10px;font-size:1.1em;border-bottom:2px solid #ffd54f;padding-bottom:4px}
.dl-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:6px;margin:10px 0}
.dl-grid label{display:flex;align-items:center;gap:6px;padding:6px 8px;background:#f7f9fb;border:1px solid #dde3ea;border-radius:4px;font-size:.9em;cursor:pointer;transition:background .15s}
.dl-grid label:hover{background:#e8eef4}
.dl-grid input[type=checkbox]{width:18px;height:18px;accent-color:#1a3a5c}
.dl-range{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:8px 0}
.dl-range label{font-size:.92em;font-weight:600;color:#333}
.dl-range input[type=number]{width:60px;padding:4px 6px;border:1px solid #ccd6e0;border-radius:4px;font-size:.9em}
.dl-btn{display:inline-block;padding:12px 28px;background:#1a3a5c;color:#fff;border:none;border-radius:6px;
  font-size:1em;font-weight:bold;cursor:pointer;margin-top:12px;transition:background .15s}
.dl-btn:hover{background:#2a5a8c}
.dl-btn:disabled{background:#999;cursor:not-allowed}
.dl-progress{margin-top:12px;display:none}
.dl-progress .dl-bar-wrap{background:#dde3ea;border-radius:4px;height:22px;overflow:hidden;margin:8px 0}
.dl-progress .dl-bar{background:#1a3a5c;height:100%%;width:0;border-radius:4px;transition:width .2s}
.dl-progress .dl-status{font-size:.88em;color:#555}
.dl-note{font-size:.85em;color:#666;margin-top:8px;line-height:1.6}
@media(prefers-color-scheme:dark){
  .dl-section h2{color:#90caf9;border-bottom-color:#ffd54f}
  .dl-grid label{background:#1e2a3a;border-color:#334;color:#e0e0e0}
  .dl-grid label:hover{background:#253a52}
  .dl-range label{color:#ccc}
  .dl-range input{background:#1e2a3a;color:#e0e0e0;border-color:#444}
  .dl-progress .dl-bar-wrap{background:#333}
  .dl-progress .dl-status{color:#aaa}
  .dl-note{color:#999}
}"""

download_items_html = []
for cls, label, default in CF_ITEMS:
    chk = ' checked' if default else ''
    download_items_html.append(
        "<label><input type='checkbox' value='%s'%s> %s</label>" % (cls, chk, label)
    )

download_html_path = os.path.join(docs_dir, 'download.html')
with open(download_html_path, 'w', encoding='utf-8') as f:
    f.write(("""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Download &ndash; Qur&rsquo;an Reader</title>
<style>
%s
</style>
</head>
<body>
<header><a href="index.html">&#8962; Index</a>%s<a class="header-search" href="config.html" title="Settings">&#9881;</a><a class="header-search" href="search.html">&#128269; Search</a></header>
<main>
<h1>&#128229; Download for Offline Use</h1>
<p style="font-size:.93em;color:#555;margin-bottom:16px">Generate a ZIP file of the entire Qur&rsquo;an website customised to your preferences. The ZIP can be opened directly in any browser for offline reading or hosted on any web server.</p>

<div class="dl-section">
<h2>&#9989; Select Translations</h2>
<p style="font-size:.88em;color:#666;margin:0 0 8px">Choose which content types to include. Deselected translations will be removed from the downloaded pages.</p>
<div class="dl-grid" id="dl-translations">
%s
</div>
<div style="margin-top:6px">
<button onclick="dlSelectAll()" style="padding:4px 12px;font-size:.85em;border:1px solid #ccd6e0;border-radius:4px;cursor:pointer;background:#f0f4f8">Select All</button>
<button onclick="dlDeselectAll()" style="padding:4px 12px;font-size:.85em;border:1px solid #ccd6e0;border-radius:4px;cursor:pointer;background:#f0f4f8;margin-left:4px">Deselect All</button>
</div>
</div>

<div class="dl-section">
<h2>&#128214; Surah Range</h2>
<div class="dl-range">
<label>From:</label><input type="number" id="dl-from" min="1" max="114" value="1">
<label>To:</label><input type="number" id="dl-to" min="1" max="114" value="114">
<span style="font-size:.85em;color:#888">(1&ndash;114)</span>
</div>
</div>

<div class="dl-section">
<h2>&#128230; Additional Pages</h2>
<div class="dl-grid" id="dl-extras">
<label><input type="checkbox" value="index" checked> Index Page</label>
<label><input type="checkbox" value="how" checked> How Guide</label>
<label><input type="checkbox" value="search" checked> Search Page</label>
<label><input type="checkbox" value="config" checked> Settings Page</label>
<label><input type="checkbox" value="sources" checked> Sources Page</label>
<label><input type="checkbox" value="license" checked> License Page</label>
<label><input type="checkbox" value="download" checked> Download Page</label>
</div>
</div>

<button class="dl-btn" id="dl-generate" onclick="generateZip()">&#128229; Generate &amp; Download ZIP</button>

<div class="dl-progress" id="dl-progress">
<div class="dl-bar-wrap"><div class="dl-bar" id="dl-bar"></div></div>
<div class="dl-status" id="dl-status">Preparing&hellip;</div>
</div>

<p class="dl-note"><strong>How it works:</strong> Your browser fetches each page, removes deselected translations, and packages everything into a ZIP file using <a href="https://stuk.github.io/jszip/" rel="noopener noreferrer">JSZip</a>. No data is sent to any server &mdash; everything happens locally in your browser. The resulting ZIP includes all HTML, CSS, and JavaScript needed for a fully self-contained offline Qur&rsquo;an reader.</p>
<p class="dl-note"><strong>License:</strong> The downloaded content is provided under the <a href="license.html">Unconditional Liberty Instrument (ULI)</a>. Translation texts remain subject to their original copyright terms.</p>

</main>
""" + COMPACT_FOOTER + """
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<script>
function dlSelectAll(){document.querySelectorAll('#dl-translations input').forEach(function(c){c.checked=true});}
function dlDeselectAll(){document.querySelectorAll('#dl-translations input').forEach(function(c){c.checked=false});}

async function generateZip(){
  var btn=document.getElementById('dl-generate');
  var prog=document.getElementById('dl-progress');
  var bar=document.getElementById('dl-bar');
  var status=document.getElementById('dl-status');
  btn.disabled=true;
  prog.style.display='block';
  bar.style.width='0%%';
  status.textContent='Preparing\\u2026';

  /* Gather selected translations */
  var selectedTrans=[];
  document.querySelectorAll('#dl-translations input:checked').forEach(function(c){selectedTrans.push(c.value);});

  /* Gather surah range */
  var fromS=Math.max(1,Math.min(114,parseInt(document.getElementById('dl-from').value)||1));
  var toS=Math.max(fromS,Math.min(114,parseInt(document.getElementById('dl-to').value)||114));

  /* Gather extra pages */
  var extras=[];
  document.querySelectorAll('#dl-extras input:checked').forEach(function(c){extras.push(c.value);});

  var zip=new JSZip();
  var allClasses=%s;
  var hardcodedDefaults=%s;

  /* Build list of files to fetch */
  var files=[];
  for(var i=fromS;i<=toS;i++){
    var fn=('00'+i).slice(-3)+'.html';
    files.push(fn);
  }
  var extraMap={'index':'index.html','how':'how/index.html','search':'search.html','config':'config.html','sources':'sources.html','license':'license.html','download':'download.html'};
  extras.forEach(function(e){if(extraMap[e])files.push(extraMap[e]);});

  /* Also include config.js and extra data files when needed */
  var needConfigJS=extras.indexOf('config')>=0||files.length>0;
  var needSearchJS=extras.indexOf('search')>=0;
  var needHowData=extras.indexOf('how')>=0;

  var total=files.length+(needConfigJS?1:0)+(needSearchJS?1:0);
  var done=0;

  function updateProgress(){
    done++;
    var pct=Math.round(done*100/total);
    bar.style.width=pct+'%%';
    status.textContent='Processing '+done+' of '+total+' files ('+pct+'%%)\\u2026';
  }

  /* Helper: clean up a parsed doc — remove links to excluded pages from footer/header */
  function cleanPageLinks(doc){
    /* Remove header links to excluded pages */
    if(extras.indexOf('config')<0){
      doc.querySelectorAll('a[href="config.html"]').forEach(function(a){a.remove();});
    }
    if(extras.indexOf('how')<0){
      doc.querySelectorAll('a[href="how/index.html"]').forEach(function(a){a.remove();});
    }
    if(extras.indexOf('search')<0){
      doc.querySelectorAll('a[href="search.html"]').forEach(function(a){a.remove();});
    }
    /* Remove index link from header if not included */
    if(extras.indexOf('index')<0){
      doc.querySelectorAll('header a[href="index.html"]').forEach(function(a){a.remove();});
    }
    /* Remove surah select options outside the chosen range */
    doc.querySelectorAll('.surah-nav-select option').forEach(function(opt){
      var m=opt.value.match(/^(\\d{3})\\.html$/);
      if(m){var n=parseInt(m[1],10);if(n<fromS||n>toS)opt.remove();}
    });
    /* Clean footer links */
    var footer=doc.querySelector('footer');
    if(footer){
      var links=footer.querySelectorAll('a');
      links.forEach(function(a){
        var href=a.getAttribute('href')||'';
        if(href==='sources.html'&&extras.indexOf('sources')<0){a.remove();}
        if(href==='license.html'&&extras.indexOf('license')<0){a.remove();}
        if(href==='download.html'&&extras.indexOf('download')<0){a.remove();}
        if(href==='index.html'&&extras.indexOf('index')<0){a.remove();}
      });
      /* Clean up orphan separators */
      footer.innerHTML=footer.innerHTML.replace(/(<\\/a>)\\s*&nbsp;\\|&nbsp;\\s*(&nbsp;|$)/g,'$1 ').replace(/^\\s*&nbsp;\\|&nbsp;\\s*/,'').replace(/\\s*&nbsp;\\|&nbsp;\\s*$/,'');
    }
  }

  /* Helper: strip deselected translations from surah HTML */
  function stripTranslations(html){
    var parser=new DOMParser();
    var doc=parser.parseFromString(html,'text/html');
    /* Remove table rows for deselected translation classes */
    allClasses.forEach(function(cls){
      if(selectedTrans.indexOf(cls)<0){
        doc.querySelectorAll('tr.'+cls).forEach(function(r){r.remove();});
        /* Also remove Content Filter checkboxes for this translation */
        doc.querySelectorAll('.cf-item input[data-rowclass="'+cls+'"]').forEach(function(inp){
          var span=inp.closest('.cf-item');
          if(span)span.remove();
        });
      }
    });
    /* Remove config.js script tag since we'll inline the selected config */
    doc.querySelectorAll('script[src="config.js"]').forEach(function(s){s.remove();});
    cleanPageLinks(doc);
    return '<!DOCTYPE html>\\n'+doc.documentElement.outerHTML;
  }

  /* Helper: strip deselected translations from config.html */
  function stripConfigPage(html){
    var parser=new DOMParser();
    var doc=parser.parseFromString(html,'text/html');
    allClasses.forEach(function(cls){
      if(selectedTrans.indexOf(cls)<0){
        doc.querySelectorAll('.cfg-row .cfg-switch input[data-key="'+cls+'"]').forEach(function(inp){
          var row=inp.closest('.cfg-row');
          if(row)row.remove();
        });
      }
    });
    doc.querySelectorAll('script[src="config.js"]').forEach(function(s){s.remove();});
    cleanPageLinks(doc);
    return '<!DOCTYPE html>\\n'+doc.documentElement.outerHTML;
  }

  /* Helper: strip deselected items from download.html */
  function stripDownloadPage(html){
    var parser=new DOMParser();
    var doc=parser.parseFromString(html,'text/html');
    /* Remove translation labels not selected */
    var dlTrans=doc.getElementById('dl-translations');
    if(dlTrans){
      allClasses.forEach(function(cls){
        if(selectedTrans.indexOf(cls)<0){
          dlTrans.querySelectorAll('input[value="'+cls+'"]').forEach(function(inp){
            var lbl=inp.closest('label');
            if(lbl)lbl.remove();
          });
        }
      });
    }
    /* Remove additional page labels not selected */
    var dlExtras=doc.getElementById('dl-extras');
    if(dlExtras){
    var extraKeys=['index','how','search','config','sources','license','download'];
      extraKeys.forEach(function(key){
        if(extras.indexOf(key)<0){
          dlExtras.querySelectorAll('input[value="'+key+'"]').forEach(function(inp){
            var lbl=inp.closest('label');
            if(lbl)lbl.remove();
          });
        }
      });
    }
    doc.querySelectorAll('script[src="config.js"]').forEach(function(s){s.remove();});
    cleanPageLinks(doc);
    return '<!DOCTYPE html>\\n'+doc.documentElement.outerHTML;
  }

  /* Fetch and process each file */
  for(var fi=0;fi<files.length;fi++){
    var fname=files[fi];
    try{
      status.textContent='Fetching '+fname+'\\u2026';
      var resp=await fetch(fname);
      if(!resp.ok){updateProgress();continue;}
      var html=await resp.text();
      if(/^\\d{3}\\.html$/.test(fname)){
        html=stripTranslations(html);
      }else if(fname==='config.html'){
        html=stripConfigPage(html);
      }else if(fname==='download.html'){
        html=stripDownloadPage(html);
      }else{
        /* For index, search, sources, license — just clean page links */
        var parser=new DOMParser();
        var doc=parser.parseFromString(html,'text/html');
        cleanPageLinks(doc);
        html='<!DOCTYPE html>\\n'+doc.documentElement.outerHTML;
      }
      zip.file(fname,html);
    }catch(e){
      console.warn('Failed to fetch '+fname,e);
    }
    updateProgress();
  }

  /* Add docs/how JSON data when How page is selected */
  if(needHowData){
    try{
      status.textContent='Fetching how/sd/translations.json\\u2026';
      var howMetaResp=await fetch('how/sd/translations.json');
      if(howMetaResp.ok){
        var howMetaText=await howMetaResp.text();
        zip.file('how/sd/translations.json',howMetaText);
        updateProgress();
        var howMeta=JSON.parse(howMetaText||'{}');
        var trList=(howMeta.translations||[]);
        for(var hi=0;hi<trList.length;hi++){
          var key=trList[hi].key;
          try{
            status.textContent='Fetching how/sd/t/'+key+'.json\\u2026';
            var one=await fetch('how/sd/t/'+key+'.json');
            if(one.ok){zip.file('how/sd/t/'+key+'.json',await one.text());}
          }catch(_){}
          updateProgress();
        }
      }
    }catch(_){}
  }

  /* Add config.js with smart defaults.
     If user selected <= 6 translations: all selected get true (small selection — show everything).
     If user selected > 6: use the curated hardcoded defaults so the page isn't overloaded
     (user can toggle the rest via Content Filter / Settings). */
  if(needConfigJS){
    var cfgObj={};
    var smartThreshold=6;
    if(selectedTrans.length<=smartThreshold){
      allClasses.forEach(function(cls){cfgObj[cls]=selectedTrans.indexOf(cls)>=0;});
    }else{
      allClasses.forEach(function(cls){
        if(selectedTrans.indexOf(cls)<0){cfgObj[cls]=false;}
        else{cfgObj[cls]=!!hardcodedDefaults[cls];}
      });
    }
    var cfgJS='var QURAN_CONFIG='+JSON.stringify(cfgObj,null,2)+';\\n';
    zip.file('config.js',cfgJS);
    updateProgress();
  }

  /* Add search-data.js if needed */
  if(needSearchJS){
    try{
      var sdResp=await fetch('search-data.js');
      if(sdResp.ok){zip.file('search-data.js',await sdResp.text());}
    }catch(e){}
    updateProgress();
  }

  /* Generate and trigger download */
  status.textContent='Compressing ZIP\\u2026';
  bar.style.width='95%%';
  var blob=await zip.generateAsync({type:'blob',compression:'DEFLATE',compressionOptions:{level:6}});
  bar.style.width='100%%';
  status.textContent='Download ready!';

  /* Trigger download */
  var a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='quran-reader-offline.zip';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(a.href);

  btn.disabled=false;
}
</script>
</body>
</html>""") % (DOWNLOAD_CSS, make_surah_select(0), '\n'.join(download_items_html),
              str([cls for cls, _, _ in CF_ITEMS]),
              json.dumps({cls: dflt for cls, _, dflt in CF_ITEMS})))
print('Written: %s' % download_html_path)

print('Done. %d surah files + index + search + config + bookmarks + sources + license + download regenerated.' % 114)
