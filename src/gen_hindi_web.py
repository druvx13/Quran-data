#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate /hindi-web HTML pages — a complete Hindi-language Qur'an reader.

Run from the repository root:
    python3 src/gen_hindi_web.py

Sources used:
  - output/quran_arabic.txt            : [sura:ayah] Arabic text (Uthmani script)
  - output/quran_translit_unicode.txt  : [sura:ayah] Unicode transliteration
  - output/quran_hindi_farooq.txt      : [sura:ayah] Hindi translation (Farooq Khan)
  - output/quran_hindi_suhail.txt      : [sura:ayah] Hindi translation (Suhail)
  - output/quran_hindi_mokhtasar.txt   : [sura:ayah] Hindi Tafsir (Al-Mokhtasar)
  - output/quran_hindi_omari.txt       : [sura:ayah] Hindi translation (Al-Omari)

All UI text is in Hindi (Devanagari script).
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

# English surah name (for audio URLs and meta descriptions)
SURA_NAME_EN = [
    "Al-Fatihah","Al-Baqarah","Al-Imran","An-Nisa","Al-Maidah",
    "Al-Anam","Al-Araf","Al-Anfal","At-Tawbah","Yunus",
    "Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr",
    "An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta Ha",
    "Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan",
    "Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum",
    "Luqman","As-Sajdah","Al-Ahzab","Saba","Fatir",
    "Ya Sin","As-Saffat","Sad","Az-Zumar","Ghafir",
    "Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiyah",
    "Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf",
    "Ad-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman",
    "Al-Waqiah","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahanah",
    "As-Saff","Al-Jumuah","Al-Munafiqun","At-Taghabun","At-Talaq",
    "At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqah","Al-Maarij",
    "Nuh","Al-Jinn","Al-Muzzammil","Al-Muddaththir","Al-Qiyamah",
    "Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa",
    "At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj",
    "At-Tariq","Al-Ala","Al-Ghashiyah","Al-Fajr","Al-Balad",
    "Ash-Shams","Al-Layl","Ad-Duha","Ash-Sharh","At-Tin",
    "Al-Alaq","Al-Qadr","Al-Bayyinah","Az-Zalzalah","Al-Adiyat",
    "Al-Qariah","At-Takathur","Al-Asr","Al-Humazah","Al-Fil",
    "Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr",
    "Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas",
]

# Hindi surah names (Devanagari transliteration + Hindi meaning)
SURA_NAME_HI = [
    "अल-फ़ातिहा (प्रारंभ)",
    "अल-बक़रा (गाय)",
    "आल-इमरान (इमरान का परिवार)",
    "अन-निसा (महिलाएँ)",
    "अल-माइदा (दस्तरख़ान)",
    "अल-अनआम (मवेशी)",
    "अल-आराफ़ (उच्च स्थान)",
    "अल-अनफ़ाल (युद्ध का माल)",
    "अत-तौबा (क्षमायाचना)",
    "यूनुस (यूनुस)",
    "हूद (हूद)",
    "यूसुफ़ (यूसुफ़)",
    "अर-रअद (गड़गड़ाहट)",
    "इब्राहीम (इब्राहीम)",
    "अल-हिज्र (पत्थरों की भूमि)",
    "अन-नहल (मधुमक्खी)",
    "बनी-इसराईल (इसराईल की संतान)",
    "अल-कहफ़ (गुफ़ा)",
    "मरयम (मरयम)",
    "ता-हा (ता-हा)",
    "अल-अंबिया (पैग़म्बर)",
    "अल-हज्ज (हज)",
    "अल-मुमिनून (ईमानवाले)",
    "अन-नूर (प्रकाश)",
    "अल-फ़ुरक़ान (कसौटी)",
    "अश-शुअरा (कवि)",
    "अन-नम्ल (चींटी)",
    "अल-क़सस (कथाएँ)",
    "अल-अंकबूत (मकड़ी)",
    "अर-रूम (रोमन)",
    "लुक़मान (लुक़मान)",
    "अस-सज्दा (सज्दा)",
    "अल-अहज़ाब (संगठन)",
    "सबा (सबा)",
    "फ़ातिर (सृष्टिकर्ता)",
    "या-सीन (या-सीन)",
    "अस-साफ़्फ़ात (पंक्तिबद्ध)",
    "साद (साद)",
    "अज़-ज़ुमर (दल)",
    "ग़ाफ़िर (क्षमाकर्ता)",
    "फ़ुस्सिलत (विस्तृत)",
    "अश-शूरा (परामर्श)",
    "अज़-ज़ुख़्रुफ़ (सोना)",
    "अद-दुख़ान (धुआँ)",
    "अल-जासिया (घुटने टेकना)",
    "अल-अहक़ाफ़ (बालू पहाड़)",
    "मुहम्मद (मुहम्मद)",
    "अल-फ़तह (विजय)",
    "अल-हुजुरात (कमरे)",
    "क़ाफ़ (क़ाफ़)",
    "अज़-ज़ारियात (बिखेरने वाले)",
    "अत-तूर (पर्वत)",
    "अन-नज्म (तारा)",
    "अल-क़मर (चाँद)",
    "अर-रहमान (दयालु)",
    "अल-वाक़िआ (महाघटना)",
    "अल-हदीद (लोहा)",
    "अल-मुजादिला (वाद-विवाद करने वाली)",
    "अल-हश्र (एकत्र करना)",
    "अल-मुम्तहिना (परखी जाने वाली)",
    "अस-सफ़्फ़ (पंक्ति)",
    "अल-जुमुआ (जुमे का दिन)",
    "अल-मुनाफ़िक़ून (मुनाफ़िक़)",
    "अत-तग़ाबुन (हानि का प्रकटीकरण)",
    "अत-तलाक़ (तलाक़)",
    "अत-तहरीम (निषेध)",
    "अल-मुल्क (राज्य)",
    "अल-क़लम (क़लम)",
    "अल-हाक़्क़ा (निश्चित सत्य)",
    "अल-मआरिज (आरोहण के रास्ते)",
    "नूह (नूह)",
    "अल-जिन्न (जिन्न)",
    "अल-मुज़्ज़म्मिल (लिपटने वाला)",
    "अल-मुद्दस्सिर (लपेटने वाला)",
    "अल-क़ियामा (क़यामत)",
    "अल-इन्सान (मानव)",
    "अल-मुर्सलात (भेजे हुए)",
    "अन-नबा (समाचार)",
    "अन-नाज़िआत (निकालने वाले)",
    "अबस (मुँह फेरा)",
    "अत-तकवीर (लपेटना)",
    "अल-इन्फ़ितार (फटना)",
    "अल-मुतफ़्फ़िफ़ीन (कम तोलने वाले)",
    "अल-इन्शिक़ाक़ (चिरना)",
    "अल-बुरूज (तारामंडल)",
    "अत-तारिक़ (रात को आने वाला)",
    "अल-आला (सर्वोच्च)",
    "अल-ग़ाशिया (आच्छादित करने वाली)",
    "अल-फज्र (भोर)",
    "अल-बलद (नगर)",
    "अश-शम्स (सूरज)",
    "अल-लैल (रात)",
    "अज़-ज़ुहा (चाशत)",
    "अल-इन्शिराह (विस्तार)",
    "अत-तीन (अंजीर)",
    "अल-अलक़ (रक्त का थक्का)",
    "अल-क़द्र (शबे क़द्र)",
    "अल-बय्यिना (स्पष्ट प्रमाण)",
    "अज़-ज़िलज़ाल (भूकम्प)",
    "अल-आदियात (दौड़ने वाले)",
    "अल-क़ारिआ (महाविपदा)",
    "अत-तकासुर (अधिकता की होड़)",
    "अल-अस्र (समय)",
    "अल-हुमज़ा (चुगलखोर)",
    "अल-फ़ील (हाथी)",
    "क़ुरैश (क़ुरैश)",
    "अल-माऊन (सहायता)",
    "अल-कौसर (बहुतायत)",
    "अल-काफ़िरून (इनकारी)",
    "अन-नस्र (सहायता)",
    "अल-लहब (ज्वाला)",
    "अल-इख़्लास (एकनिष्ठता)",
    "अल-फ़लक़ (भोर)",
    "अन-नास (मानवजाति)",
]

# ---------------------------------------------------------------------------
# Revelation metadata: (revelation_order, 'M'=Meccan/'D'=Medinan) per surah
# ---------------------------------------------------------------------------
SURAH_REV = [
    (5,'M'),(87,'D'),(89,'D'),(92,'D'),(112,'D'),
    (55,'M'),(39,'M'),(88,'D'),(113,'D'),(51,'M'),
    (52,'M'),(53,'M'),(96,'D'),(72,'M'),(54,'M'),
    (70,'M'),(50,'M'),(69,'M'),(44,'M'),(45,'M'),
    (73,'M'),(103,'D'),(74,'M'),(102,'D'),(42,'M'),
    (47,'M'),(48,'M'),(49,'M'),(85,'M'),(84,'M'),
    (57,'M'),(75,'M'),(90,'D'),(58,'M'),(43,'M'),
    (41,'M'),(56,'M'),(38,'M'),(59,'M'),(60,'M'),
    (61,'M'),(62,'M'),(63,'M'),(64,'M'),(65,'M'),
    (66,'M'),(95,'D'),(111,'D'),(106,'D'),(34,'M'),
    (67,'M'),(76,'M'),(23,'M'),(37,'M'),(97,'D'),
    (46,'M'),(94,'D'),(105,'D'),(101,'D'),(91,'D'),
    (109,'D'),(110,'D'),(104,'D'),(108,'D'),(99,'D'),
    (107,'D'),(77,'M'),(2,'M'),(78,'M'),(79,'M'),
    (71,'M'),(40,'M'),(3,'M'),(4,'M'),(31,'M'),
    (98,'D'),(33,'M'),(80,'M'),(81,'M'),(24,'M'),
    (7,'M'),(82,'M'),(86,'M'),(83,'M'),(27,'M'),
    (36,'M'),(8,'M'),(68,'M'),(10,'M'),(35,'M'),
    (26,'M'),(9,'M'),(11,'M'),(12,'M'),(28,'M'),
    (1,'M'),(25,'M'),(100,'D'),(93,'D'),(14,'M'),
    (30,'M'),(16,'M'),(13,'M'),(32,'M'),(19,'M'),
    (29,'M'),(17,'M'),(15,'M'),(18,'M'),(114,'D'),
    (6,'M'),(22,'M'),(20,'M'),(21,'M'),
]

# Juz (para) start positions
JUZ_STARTS = {
    (1,1):1,  (2,142):2,  (2,253):3,  (3,92):4,   (4,24):5,
    (4,148):6,(5,82):7,   (6,111):8,  (7,88):9,   (8,41):10,
    (9,93):11,(11,6):12,  (12,53):13, (15,1):14,  (17,1):15,
    (18,75):16,(21,1):17, (23,1):18,  (25,21):19, (27,56):20,
    (29,46):21,(33,31):22,(36,28):23, (39,32):24, (41,47):25,
    (46,1):26,(51,31):27, (58,1):28,  (67,1):29,  (78,1):30,
}

# Sajda (Sujood Al-Tilawa) verses
SAJDA_VERSES = {
    (7,206),(13,15),(16,50),(17,109),(19,58),
    (22,18),(25,60),(27,26),(32,15),(38,24),
    (41,38),(53,62),(84,21),(96,19),
}

# ---------------------------------------------------------------------------
# Helper: juz span for a surah
# ---------------------------------------------------------------------------
def surah_juz_span(sura_idx):
    size = SURA_SIZE[sura_idx - 1]
    juz_set = set()
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
    rev_order, rev_type = SURAH_REV[sura_idx - 1]
    type_label = 'मक्की' if rev_type == 'M' else 'मदनी'
    type_class = 'meccan' if rev_type == 'M' else 'medinan'
    juz = surah_juz_span(sura_idx)
    size = SURA_SIZE[sura_idx - 1]
    return (
        "<div class='surah-info-bar'>"
        "<span class='sib-type %s'>%s</span>"
        "<span>&#128336;&nbsp;अवतरण क्रम&nbsp;#%d</span>"
        "<span>&#128220;&nbsp;%d आयतें</span>"
        "<span>&#128366;&nbsp;पारा&nbsp;%s</span>"
        "</div>\n"
    ) % (type_class, type_label, rev_order, size, juz)


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
CSS = """\
*,*::before,*::after{box-sizing:border-box}
body{margin:0;padding:0;font-family:'Noto Sans Devanagari',system-ui,Arial,Helvetica,sans-serif;
  font-size:16px;background:#fff;color:#111;line-height:1.6}
header{background:#145a32;color:#fff;padding:12px 16px;position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
header a{color:#f9e79f;text-decoration:none;font-weight:bold;font-size:1.05em}
header a:hover{text-decoration:underline}
.header-search{margin-left:auto}
main{padding:16px;max-width:900px;margin:0 auto}
h1{font-size:1.4em;margin:0 0 12px}
h2{font-size:1.2em;color:#145a32;margin:20px 0 8px}
.surah-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:8px;margin-top:16px}
.surah-grid a{display:block;padding:10px 12px;background:#f0f7f4;border:1px solid #a9cfc0;
  border-radius:6px;text-decoration:none;color:#145a32;font-size:.93em;
  font-family:'Noto Sans Devanagari',system-ui,sans-serif}
.surah-grid a:hover{background:#d5ede5}
.sg-meta{display:flex;align-items:center;gap:6px;margin-top:4px;font-size:.78em;color:#555}
.notice{background:#fefbd8;border-left:4px solid #f9e79f;padding:12px 16px;margin-bottom:20px;font-size:.95em}
.notice summary{cursor:pointer}
.table-wrap{overflow-x:auto;width:100%}
table{width:100%;border-collapse:collapse;margin-bottom:24px}
th{background:#145a32;color:#fff;padding:10px 12px;text-align:left;font-size:.9em}
td{padding:8px 12px;vertical-align:top;border:1px solid #c8ddd6}
.ayah-sep td{background:#145a32;color:#fff;font-weight:bold;font-size:.9em;padding:6px 12px;border-color:#145a32}
.label{color:#666;font-size:.82em;white-space:nowrap;width:120px;vertical-align:top;
  font-family:'Noto Sans Devanagari',system-ui,sans-serif}
.arabic td{background:#fff8e1}
.arabic-text{font-family:'Scheherazade New','Amiri','Traditional Arabic',serif;font-size:1.5em;direction:rtl;text-align:right;line-height:2}
.audio td{background:#e0f7fa}
.audio-player{width:100%;max-width:420px;height:36px;vertical-align:middle}
.translit-unicode td{background:#e8eaf6}
.translit-unicode-text{font-style:normal;font-weight:600;color:#283593}
.hindi td{background:#f5f0ff}
.hindi-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#3a2a6c}
.hindi-suhail td{background:#fff3e0}
.hindi-suhail-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#5d4037}
.hindi-mokhtasar td{background:#e8f5e0}
.hindi-mokhtasar-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#1b5e20}
.hindi-omari td{background:#fff0f5}
.hindi-omari-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#880e30}
nav.chapter-nav{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;
  padding:16px 0;margin-top:8px;border-top:1px solid #c8ddd6}
nav.chapter-nav a{display:inline-block;padding:8px 16px;background:#145a32;color:#fff;
  border-radius:4px;text-decoration:none;font-size:.95em}
nav.chapter-nav a:hover{background:#1e8449}
footer{text-align:center;padding:16px 20px;font-size:.82em;color:#666;border-top:1px solid #e0e0e0;margin-top:32px;line-height:1.8}
footer a{color:#145a32;text-decoration:none;font-weight:600}
footer a:hover{text-decoration:underline}
.surah-nav-select{padding:5px 8px;border-radius:4px;border:1px solid #f9e79f;background:#145a32;color:#f9e79f;font-size:.9em;cursor:pointer;max-width:260px;
  font-family:'Noto Sans Devanagari',system-ui,sans-serif}
.surah-nav-select:focus{outline:2px solid #f9e79f;outline-offset:2px}
.verse-chooser{background:#f0f7f4;border:1px solid #a9cfc0;border-radius:6px;margin-bottom:16px}
.verse-chooser summary{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;cursor:pointer;user-select:none;list-style:none;background:#d5ede5;border-radius:6px}
.verse-chooser[open] summary{border-radius:6px 6px 0 0}
.verse-chooser summary::-webkit-details-marker{display:none}
.vc-title{font-size:1em;font-weight:bold;color:#145a32}
.vc-arrow{color:#145a32;transition:transform .2s}
.verse-chooser[open] .vc-arrow{transform:rotate(180deg)}
.vc-body{padding:10px 14px;max-height:340px;overflow-y:auto}
.vc-controls{display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap}
.vc-controls button{padding:6px 14px;border:none;border-radius:4px;cursor:pointer;font-size:.88em;background:#145a32;color:#fff;min-height:36px;
  font-family:'Noto Sans Devanagari',system-ui,sans-serif}
.vc-controls button:hover{background:#1e8449}
.vc-range{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-top:6px}
.vc-range label{font-size:.88em;color:#145a32;white-space:nowrap}
.vc-range input[type=number]{width:70px;padding:5px 6px;border:1px solid #a9cfc0;border-radius:4px;font-size:.88em;color:#111;background:#fff}
.vc-range input[type=number]:focus{outline:2px solid #f9e79f;outline-offset:2px}
.vc-section-title{font-size:.82em;font-weight:bold;color:#555;text-transform:uppercase;letter-spacing:.04em;margin:8px 0 4px}
.cf-list{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px}
.cf-item input[type=checkbox]{position:absolute;opacity:0;width:0;height:0}
.cf-item label{display:inline-flex;align-items:center;padding:5px 10px;background:#fff;border:1px solid #a9cfc0;border-radius:4px;cursor:pointer;font-size:.85em;color:#145a32;user-select:none;white-space:nowrap;
  font-family:'Noto Sans Devanagari',system-ui,sans-serif}
.cf-item label:hover{background:#d5ede5}
.cf-item input:checked+label{background:#145a32;color:#fff;border-color:#145a32}
.cf-item input:focus+label{outline:2px solid #f9e79f;outline-offset:2px}
.surah-info-bar{display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center;
  padding:8px 12px;background:#f0f7f4;border:1px solid #a9cfc0;border-radius:6px;
  margin-bottom:14px;font-size:.88em;color:#145a32}
.surah-info-bar span{white-space:nowrap}
.sib-type{font-weight:700;padding:2px 8px;border-radius:10px;font-size:.95em}
.sib-type.meccan{background:#fff8e1;color:#e65100;border:1px solid #ffcc80}
.sib-type.medinan{background:#e8f5e9;color:#1b5e20;border:1px solid #a5d6a7}
.juz-marker td{background:#145a32;color:#f9e79f;font-weight:700;font-size:.85em;
  padding:5px 12px;letter-spacing:.04em;border-color:#145a32;text-align:center}
.sajda-badge{display:inline-flex;align-items:center;gap:4px;
  background:#e8f5e9;color:#1b5e20;font-size:.78em;font-weight:600;
  padding:1px 6px;border-radius:8px;border:1px solid #a5d6a7;margin-left:8px;vertical-align:middle}
.copy-btn{background:none;border:1px solid #a9cfc0;border-radius:4px;
  padding:1px 7px;cursor:pointer;font-size:.75em;color:#666;margin-left:8px;vertical-align:middle;line-height:1.4}
.copy-btn:hover{background:#d5ede5;color:#145a32}
.bm-btn{background:none;border:1px solid #a9cfc0;border-radius:4px;
  padding:1px 7px;cursor:pointer;font-size:.75em;color:#666;margin-left:4px;
  vertical-align:middle;line-height:1.4;transition:background .15s,color .15s}
.bm-btn:hover{background:#fff8e1;color:#e65100}
.bm-btn.active{background:#fff8e1;color:#e65100;border-color:#ffa726}
@keyframes ayah-pulse{0%{background:#145a32}40%{background:#f9e79f}100%{background:#145a32}}
.ayah-anchor-highlight td{animation:ayah-pulse .8s ease-in-out 3}
.permalink{color:inherit;text-decoration:none;font-weight:bold}
.permalink:hover{text-decoration:underline}
.scroll-top-btn{position:fixed;bottom:24px;right:20px;width:42px;height:42px;
  border-radius:50%;background:#145a32;color:#f9e79f;font-size:1.2em;font-weight:bold;
  border:none;cursor:pointer;display:none;align-items:center;justify-content:center;
  box-shadow:0 2px 8px rgba(0,0,0,.3);z-index:100;line-height:1}
.scroll-top-btn:hover{background:#1e8449}
.vc-font-ctrl{display:flex;align-items:center;gap:6px;margin-bottom:8px;flex-wrap:wrap}
.vc-font-ctrl span{font-size:.85em;color:#555}
.vc-font-ctrl button{padding:3px 10px;border:1px solid #a9cfc0;border-radius:4px;
  cursor:pointer;font-size:.88em;background:#fff;color:#145a32;min-height:30px}
.vc-font-ctrl button:hover{background:#d5ede5}
.noscript-warn{background:#fff3cd;border-left:4px solid #ffc107;padding:10px 14px;margin-bottom:12px;font-size:.93em;color:#856404}
@media(max-width:600px){
  .vc-controls button{min-height:44px}
  .cf-item label{min-height:44px;padding:8px 10px}
  main{padding:10px 8px}
  h1{font-size:1.15em}
  .surah-nav-select{max-width:170px;font-size:.82em}
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
  .surah-grid{grid-template-columns:repeat(auto-fill,minmax(140px,1fr))}
  header{padding:8px 10px;gap:8px}
}
@media(prefers-color-scheme:dark){
  body{background:#0d1f17;color:#e8e8e8}
  header{background:#0a3d22}
  main{color:#e8e8e8}
  h2{color:#82e0aa}
  td{border-color:#2a4d3a;color:#e8e8e8}
  .ayah-sep td{background:#0a3d22;border-color:#0a3d22}
  .label{color:#aaa}
  .arabic td{background:#2a2010}
  .audio td{background:#0d2228}
  .translit-unicode td{background:#1a1f3a}
  .hindi td{background:#1e1530}
  .hindi-suhail td{background:#2a1f10}
  .hindi-mokhtasar td{background:#102010}
  .hindi-omari td{background:#200010}
  .surah-grid a{background:#122a1f;border-color:#2a4d3a;color:#82e0aa}
  .surah-grid a:hover{background:#1a3d2c}
  .sg-meta{color:#aaa}
  .notice{background:#1a2a10;border-left-color:#f9e79f;color:#e8e8e8}
  .verse-chooser{background:#122a1f;border-color:#2a4d3a}
  .verse-chooser summary{background:#0d2118}
  .vc-title{color:#82e0aa}
  .vc-arrow{color:#82e0aa}
  .vc-range input[type=number]{background:#0d1f17;border-color:#2a4d3a;color:#e8e8e8}
  .cf-item label{background:#0d1f17;border-color:#2a4d3a;color:#82e0aa}
  .cf-item label:hover{background:#1a3d2c}
  .cf-item input:checked+label{background:#145a32;color:#fff}
  footer{color:#aaa;border-top-color:#2a4d3a}
  footer a{color:#82e0aa}
  th{background:#0a3d22}
  .translit-unicode-text{color:#9fa8da}
  .hindi-text{color:#b39ddb}
  .hindi-suhail-text{color:#ffcc80}
  .hindi-mokhtasar-text{color:#a5d6a7}
  .hindi-omari-text{color:#f48fb1}
  .surah-info-bar{background:#122a1f;border-color:#2a4d3a;color:#82e0aa}
  .sib-type.meccan{background:#2a1f00;color:#ffcc80;border-color:#8b6914}
  .sib-type.medinan{background:#0a1e10;color:#a5d6a7;border-color:#2e7d32}
  .juz-marker td{background:#0a3d22;border-color:#0a3d22}
  .sajda-badge{background:#0a1e10;color:#a5d6a7;border-color:#2e7d32}
  .copy-btn{border-color:#2a4d3a;color:#82e0aa}
  .copy-btn:hover{background:#1a3d2c}
  .bm-btn{border-color:#2a4d3a;color:#aaa}
  .bm-btn:hover{background:#2a1f00;color:#ffcc80}
  .bm-btn.active{background:#2a1f00;color:#ffcc80;border-color:#8b6914}
  .vc-font-ctrl span{color:#aaa}
  .vc-font-ctrl button{background:#0d1f17;border-color:#2a4d3a;color:#82e0aa}
  .vc-font-ctrl button:hover{background:#1a3d2c}
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
  .table-wrap .label{width:120px!important;white-space:nowrap!important}
  td{border-color:#999;color:#000;background:#fff!important}
  .arabic-text{font-size:1.3em}
  .ayah-sep td{background:#ddd!important;color:#000!important}
  tr[data-ayah]{display:table-row!important}
}"""

# ---------------------------------------------------------------------------
# Content filter items (Hindi labels)
# ---------------------------------------------------------------------------
CF_ITEMS = [
    ('arabic',           'अरबी',                True),
    ('audio',            'ऑडियो',               True),
    ('translit-unicode', 'लिप्यंतरण (यूनिकोड)', True),
    ('hindi',            'हिंदी (फ़ारूक़)',        True),
    ('hindi-suhail',     'हिंदी (सुहेल)',         True),
    ('hindi-mokhtasar',  'हिंदी तफ़्सीर (मुख़्तसर)',True),
    ('hindi-omari',      'हिंदी (अल-ओमारी)',      False),
]


def make_surah_select(current=0):
    opts = ['<option value="">सूरह पर जाएँ\u2026</option>']
    for i, n in enumerate(SURA_NAME_HI, 1):
        sel = ' selected' if i == current else ''
        opts.append("<option value='%03d.html'%s>%d. %s</option>" % (i, sel, i, n))
    return (
        "<select class='surah-nav-select' onchange='location.href=this.value'"
        " aria-label='सूरह चुनें'>%s</select>" % ''.join(opts)
    )


def make_verse_chooser(size):
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
        "<summary><span class='vc-title'>&#x2714; आयत और सामग्री फ़िल्टर</span>"
        "<span class='vc-arrow'>&#x25BC;</span></summary>"
        "<div class='vc-body'>"
        "<div class='vc-font-ctrl'>"
        "<span>अक्षर आकार:</span>"
        "<button onclick='fsDecrease()' title='छोटा करें'>A&minus;</button>"
        "<button onclick='fsReset()' title='सामान्य'>A</button>"
        "<button onclick='fsIncrease()' title='बड़ा करें'>A+</button>"
        "</div>"
        "<div class='vc-section-title'>आयत सीमा</div>"
        "<div class='vc-controls'>"
        "<button onclick='vcSelectAll()'>सभी दिखाएँ</button>"
        "<button onclick='vcClearAll()'>सभी छुपाएँ</button>"
        "</div>"
        "<div class='vc-range'>"
        "<label>से <input type='number' id='vc-from' min='1' max='%d' value='1'></label>"
        "<label>तक <input type='number' id='vc-to' min='1' max='%d' value='%d'></label>"
        "<button onclick='vcApplyRange()'>लागू करें</button>"
        "</div>"
        "<div class='vc-section-title' style='margin-top:12px'>सामग्री</div>"
        "<div class='cf-list' id='cf-list'>%s</div>"
        "</div>"
        "</details>\n"
    ) % (size, size, size, ''.join(cf_html))


# ---------------------------------------------------------------------------
# JavaScript (same logic as docs, with Hindi copy/bookmark labels)
# ---------------------------------------------------------------------------
VC_JS = """\
<script>
/* ---- अंतिम पठित सूरह ट्रैकिंग ---- */
(function(){
  try{
    var _suraNum=+document.body.dataset.sura;
    if(!_suraNum)return;
    var _h1=document.querySelector('h1');
    var _suraLabel=_h1?_h1.textContent.trim():'सूरह '+_suraNum;
    localStorage.setItem('hindi-quran-history',JSON.stringify({s:_suraNum,n:_suraLabel,t:Date.now()}));
  }catch(_){}
})();
/* ---- बुकमार्क ---- */
(function(){
  var BM_KEY='hindi-quran-bookmark';
  var bms=[];
  try{bms=JSON.parse(localStorage.getItem(BM_KEY)||'[]');}catch(_){}
  if(!Array.isArray(bms))bms=[];
  var curSura=+document.body.dataset.sura;
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
      list.splice(idx,1);
      if(btn)btn.classList.remove('active');
    } else {
      var h1=document.querySelector('h1');
      var label=h1?h1.textContent.trim():'सूरह '+sura;
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

  var userPrefs=null;
  try{var raw=localStorage.getItem('hindi-quran-cf');if(raw)userPrefs=JSON.parse(raw);}catch(e){}

  var defaultOn={'arabic':true,'audio':true,'translit-unicode':true,'hindi':true,'hindi-suhail':true,'hindi-mokhtasar':true,'hindi-omari':false};

  if(cfList){
    cfList.querySelectorAll('input[type=checkbox]').forEach(function(cb){
      var key=cb.dataset.rowclass;
      var on;
      if(userPrefs&&userPrefs.hasOwnProperty(key)){on=userPrefs[key];}
      else{on=defaultOn.hasOwnProperty(key)?defaultOn[key]:false;}
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
    try{localStorage.setItem('hindi-quran-cf',JSON.stringify(prefs));}catch(e){}
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

  /* ---- अक्षर आकार नियंत्रण ---- */
  var FS_KEY='hindi-qfs';
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

  /* ---- ऊपर जाएँ बटन ---- */
  var stb=document.createElement('button');
  stb.className='scroll-top-btn';
  stb.title='ऊपर जाएँ';
  stb.innerHTML='&#8679;';
  stb.onclick=function(){window.scrollTo({top:0,behavior:'smooth'});};
  document.body.appendChild(stb);
  window.addEventListener('scroll',function(){
    stb.style.display=window.scrollY>400?'flex':'none';
  },{passive:true});

  /* ---- आयत कॉपी करें ---- */
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
      setTimeout(function(){btn.textContent='\\u29c9 कॉपी';},1200);
    });
  };

  /* ---- आयत लिंक ---- */
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

# ---------------------------------------------------------------------------
# Load data files
# ---------------------------------------------------------------------------
_VERSE_RE = re.compile(r'^\[(\d+):(\d+)\]\s*(.*)')

def load_verse_file(path):
    data = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            m = _VERSE_RE.match(line.rstrip('\n'))
            if m:
                data[(int(m.group(1)), int(m.group(2)))] = m.group(3)
    return data

arabic        = load_verse_file('output/quran_arabic.txt')
translit_uni  = load_verse_file('output/quran_translit_unicode.txt')
hindi_farooq  = load_verse_file('output/quran_hindi_farooq.txt')
hindi_suhail  = load_verse_file('output/quran_hindi_suhail.txt')
hindi_mokhtasar = load_verse_file('output/quran_hindi_mokhtasar.txt')
hindi_omari   = load_verse_file('output/quran_hindi_omari.txt')

# ---------------------------------------------------------------------------
# Header / Footer templates
# ---------------------------------------------------------------------------
HEADER_HTML = """\
<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="सूरह {num}: {name_hi} \u2014 अरबी पाठ, लिप्यंतरण और हिंदी अनुवाद।">
<title>सूरह {num}: {name_hi}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600&family=Scheherazade+New:wght@400;700&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body data-sura="{num}">
<header>
  <a href="index.html">&#8962; मुख्य पृष्ठ</a>
  {surah_select}
  <a class="header-search" href="bookmarks.html" title="बुकमार्क">&#128278; बुकमार्क</a>
</header>
<main>
<h1>सूरह {num}: {name_hi}</h1>
{surah_info}<noscript><p class="noscript-warn">&#9888; आयत फ़िल्टर के लिए JavaScript आवश्यक है। सभी आयतें नीचे दिखाई जा रही हैं।</p></noscript>
{verse_chooser}<div class='table-wrap'><table><thead><tr><th colspan='2'>आयत &nbsp;&mdash;&nbsp; अरबी (उस्मानी) &nbsp;/&nbsp; ऑडियो (मिशारी अलफ़ासी) &nbsp;/&nbsp; लिप्यंतरण (यूनिकोड) &nbsp;/&nbsp; हिंदी अनुवाद (फ़ारूक़ खान, सुहेल, मुख़्तसर और अल-ओमारी)</th></tr></thead><tbody>
"""

COMPACT_FOOTER = (
    "<footer>"
    "<a href='https://github.com/druvx13/Quran-data' rel='noopener noreferrer'>GitHub</a>"
    " &nbsp;|&nbsp; <a href='https://quran.com' rel='noopener noreferrer'>Quran.com</a>"
    " &nbsp;|&nbsp; <span>ऑडियो: मिशारी रशीद अलफ़ासी</span>"
    "</footer>"
)

FOOTER_HTML = (
    "</tbody></table></div>\n"
    "{nav}\n"
    "</main>\n"
    + COMPACT_FOOTER + "\n"
    + "{script}</body>\n</html>"
)

# ---------------------------------------------------------------------------
# Generate surah pages
# ---------------------------------------------------------------------------
out_dir = 'hindi-web'
os.makedirs(out_dir, exist_ok=True)

for sura_idx in range(1, 115):
    size    = SURA_SIZE[sura_idx - 1]
    name_hi = SURA_NAME_HI[sura_idx - 1]

    prev_link = ''
    next_link = ''
    if sura_idx > 1:
        prev_link = (
            "<a href='%03d.html'>&laquo; सूरह %d: %s</a>"
            % (sura_idx - 1, sura_idx - 1, SURA_NAME_HI[sura_idx - 2])
        )
    if sura_idx < 114:
        next_link = (
            "<a href='%03d.html'>सूरह %d: %s &raquo;</a>"
            % (sura_idx + 1, sura_idx + 1, SURA_NAME_HI[sura_idx])
        )
    nav = "<nav class='chapter-nav'><span>%s</span><span>%s</span></nav>" % (prev_link, next_link)

    filename = os.path.join(out_dir, '%03d.html' % sura_idx)
    with open(filename, 'w', encoding='utf-8') as out:
        out.write(HEADER_HTML.format(
            num=sura_idx,
            name_hi=name_hi,
            css=CSS,
            surah_select=make_surah_select(sura_idx),
            verse_chooser=make_verse_chooser(size),
            surah_info=make_surah_info_bar(sura_idx),
        ))

        for ayah in range(1, size + 1):
            ar = arabic.get((sura_idx, ayah), '')
            tu = translit_uni.get((sura_idx, ayah), '')
            hi = hindi_farooq.get((sura_idx, ayah), '')
            hs = hindi_suhail.get((sura_idx, ayah), '')
            hm = hindi_mokhtasar.get((sura_idx, ayah), '')
            ho = hindi_omari.get((sura_idx, ayah), '')

            # Juz marker
            juz_num = JUZ_STARTS.get((sura_idx, ayah))
            if juz_num:
                out.write(
                    "<tr class='juz-marker' data-ayah='%d'>"
                    "<td colspan='2'>&#128366; पारा %d यहाँ से शुरू होता है</td></tr>\n"
                    % (ayah, juz_num)
                )

            # Sajda badge
            sajda_badge = ''
            if (sura_idx, ayah) in SAJDA_VERSES:
                sajda_badge = "<span class='sajda-badge'>&#9737; सजदा</span>"

            # Copy button
            copy_btn = (
                "<button class='copy-btn' onclick='copyVerse(this,%d,%d)'"
                " title='इस आयत को कॉपी करें'>\u29c9 कॉपी</button>"
            ) % (sura_idx, ayah)

            # Bookmark button
            bm_btn = (
                "<button class='bm-btn' id='bm-%d' onclick='toggleBookmark(%d,%d)'"
                " title='बुकमार्क करें'>&#128278;</button>"
            ) % (ayah, sura_idx, ayah)

            out.write(
                "<tr class='ayah-sep' data-ayah='%d' id='ayah-%d'><td colspan='2'>"
                "<a class='permalink' href='#%d' data-ayah='%d'>आयत %d</a>"
                "%s%s%s</td></tr>\n"
                "<tr class='arabic' data-ayah='%d'><td class='label'>अरबी</td><td class='arabic-text' lang='ar'>%s</td></tr>\n"
                "<tr class='audio' data-ayah='%d'><td class='label'>ऑडियो (अलफ़ासी)</td><td><audio class='audio-player' controls preload='none' src='https://druvx13-quran-audio-alafasy.hf.space/%03d%03d.mp3' title='सूरह %d, आयत %d \u2014 मिशारी अलफ़ासी'></audio></td></tr>\n"
                "<tr class='translit-unicode' data-ayah='%d'><td class='label'>लिप्यंतरण</td><td class='translit-unicode-text'>%s</td></tr>\n"
                "<tr class='hindi' data-ayah='%d'><td class='label'>हिंदी (फ़ारूक़)</td><td class='hindi-text' lang='hi'>%s</td></tr>\n"
                "<tr class='hindi-suhail' data-ayah='%d'><td class='label'>हिंदी (सुहेल)</td><td class='hindi-suhail-text' lang='hi'>%s</td></tr>\n"
                "<tr class='hindi-mokhtasar' data-ayah='%d'><td class='label'>हिंदी तफ़्सीर (मुख़्तसर)</td><td class='hindi-mokhtasar-text' lang='hi'>%s</td></tr>\n"
                "<tr class='hindi-omari' data-ayah='%d'><td class='label'>हिंदी (अल-ओमारी)</td><td class='hindi-omari-text' lang='hi'>%s</td></tr>\n"
                % (
                    ayah, ayah,
                    ayah, ayah, ayah,
                    sajda_badge, copy_btn, bm_btn,
                    ayah, ar,
                    ayah, sura_idx, ayah, sura_idx, ayah,
                    ayah, tu,
                    ayah, hi,
                    ayah, hs,
                    ayah, hm,
                    ayah, ho,
                )
            )

        out.write(FOOTER_HTML.format(nav=nav, script=VC_JS))

    print('लिखा: %s' % filename)

# ---------------------------------------------------------------------------
# Generate index.html
# ---------------------------------------------------------------------------
INDEX_CSS_EXTRA = """
.recent-list{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:4px}
.recent-card{display:flex;flex-direction:column;padding:10px 14px;background:#d5ede5;border:1px solid #82c3a5;border-radius:6px;text-decoration:none;color:#145a32;font-size:.95em;min-width:160px}
.recent-card:hover{background:#b8ddd1}
.bm-card{background:#fefbd8;border-color:#f0d060;color:#7d6000}
.bm-card:hover{background:#fdf5a0}
.recent-label{font-weight:600;font-size:.9em}
.recent-ago{font-size:.78em;color:#555;margin-top:2px}
@media(prefers-color-scheme:dark){
  .recent-card{background:#0d2a1f;border-color:#1e6e40;color:#82e0aa}
  .recent-card:hover{background:#143d2a}
  .bm-card{background:#2a2000;border-color:#8b7014;color:#f9e79f}
  .bm-card:hover{background:#332800}
  .recent-ago{color:#90a4ae}
}"""

index_path = os.path.join(out_dir, 'index.html')
with open(index_path, 'w', encoding='utf-8') as out:
    out.write("""\
<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="क़ुरआन हिंदी — अरबी पाठ, लिप्यंतरण और हिंदी अनुवाद के साथ सभी 114 सूरहें।">
<title>क़ुरआन &ndash; हिंदी अनुवाद</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600&display=swap" rel="stylesheet">
<style>
%s
</style>
</head>
<body>
<header>
  <a href="index.html">&#8962; मुख्य पृष्ठ</a>
  %s
  <a class="header-search" href="bookmarks.html" title="बुकमार्क">&#128278; बुकमार्क</a>
</header>
<main>
<h1>क़ुरआन &mdash; हिंदी अनुवाद</h1>
<details class="notice">
<summary><strong>स्रोत एवं श्रेय</strong></summary>
<em>अरबी पाठ:</em> मानक अरबी उस्मानी लिपि।<br>
<em>ऑडियो तिलावत:</em> मिशारी रशीद अलफ़ासी &mdash; <a href="https://druvx13-quran-audio-alafasy.hf.space" rel="noopener noreferrer">Hugging Face Space</a> के माध्यम से।<br>
<em>लिप्यंतरण:</em> Quran Unicode Project.<br>
<em>हिंदी अनुवाद:</em> मुहम्मद फ़ारूक़ खान एवं मुहम्मद अहमद।<br>
<em>हिंदी अनुवाद:</em> सुहेल फ़ारूक़ खान एवं सैफ़ुर रहमान नदवी।<br>
<em>हिंदी अनुवाद:</em> अज़ीज़ुल हक़ अल-ओमारी &mdash; quranenc.com के माध्यम से।<br>
<em>हिंदी तफ़्सीर:</em> अल-मुख़्तसर फ़ी तफ़्सीर अल-क़ुरआन अल-करीम।<br>
पाठ ज्यों के त्यों प्रस्तुत किए गए हैं; कोई परिवर्तन नहीं किया गया है।
</details>
<section id="recent-section" style="display:none;margin-bottom:18px">
<h2 style="margin-bottom:8px">&#128214; पढ़ना जारी रखें</h2>
<div id="recent-list" class="recent-list"></div>
</section>
<section id="bookmark-section" style="display:none;margin-bottom:18px">
<h2 style="margin-bottom:8px">&#128278; अंतिम बुकमार्क</h2>
<a id="bookmark-link" href="#" class="recent-card bm-card" style="display:inline-flex;flex-direction:column;text-decoration:none;margin-bottom:6px">
  <span id="bookmark-label" class="recent-label"></span>
  <span id="bookmark-meta" class="recent-ago"></span>
</a>
<a id="bookmark-all-link" href="bookmarks.html" class="recent-card bm-card" style="display:none;font-size:.85em;padding:7px 12px;margin-top:4px;text-decoration:none"></a>
</section>
<h2>सूरहें (अध्याय)</h2>
<div class="surah-grid">
""" % (CSS + INDEX_CSS_EXTRA, make_surah_select(0)))

    for i, name_hi in enumerate(SURA_NAME_HI, 1):
        rev_order, rev_type = SURAH_REV[i - 1]
        type_label = 'मक्की' if rev_type == 'M' else 'मदनी'
        type_class = 'meccan' if rev_type == 'M' else 'medinan'
        juz = surah_juz_span(i)
        out.write(
            "<a href='%03d.html'>"
            "<strong>%d.</strong> %s"
            "<span class='sg-meta'>"
            "<span class='sib-type %s'>%s</span>"
            "<span>पारा %s</span>"
            "</span></a>\n"
            % (i, i, name_hi, type_class, type_label, juz)
        )

    out.write("""\
</div>
</main>
%s
<script>
/* ---- पढ़ना जारी रखें ---- */
(function(){
  var HIST_KEY='hindi-quran-history';
  var section=document.getElementById('recent-section');
  var list=document.getElementById('recent-list');
  if(!section||!list)return;
  var h=null;
  try{h=JSON.parse(localStorage.getItem(HIST_KEY)||'null');}catch(_){return;}
  if(!h||!h.s)return;
  var href=String(h.s).padStart(3,'0')+'.html';
  var ago='';
  var diff=Math.round((Date.now()-h.t)/60000);
  if(diff<1)ago='अभी';
  else if(diff<60)ago=diff+' मिनट पहले';
  else if(diff<1440)ago=Math.round(diff/60)+' घंटे पहले';
  else ago=Math.round(diff/1440)+' दिन पहले';
  list.innerHTML='<a href="'+href+'" class="recent-card"><span class="recent-label">'+h.n+'</span><span class="recent-ago">'+ago+'</span></a>';
  section.style.display='';
})();
/* ---- अंतिम बुकमार्क ---- */
(function(){
  var BM_KEY='hindi-quran-bookmark';
  var section=document.getElementById('bookmark-section');
  if(!section)return;
  var bms=[];
  try{bms=JSON.parse(localStorage.getItem(BM_KEY)||'[]');}catch(_){}
  if(!Array.isArray(bms)||!bms.length)return;
  var bm=bms[0];
  var href=String(bm.s).padStart(3,'0')+'.html#ayah-'+bm.a;
  var ago='';
  var diff=Math.round((Date.now()-bm.t)/60000);
  if(diff<1)ago='अभी';
  else if(diff<60)ago=diff+' मिनट पहले';
  else if(diff<1440)ago=Math.round(diff/60)+' घंटे पहले';
  else ago=Math.round(diff/1440)+' दिन पहले';
  var linkEl=document.getElementById('bookmark-link');
  var labelEl=document.getElementById('bookmark-label');
  var metaEl=document.getElementById('bookmark-meta');
  var allEl=document.getElementById('bookmark-all-link');
  if(linkEl)linkEl.href=href;
  var suraName=bm.n||('सूरह '+bm.s);
  if(labelEl)labelEl.textContent='\U0001F4D6 '+suraName+', \u0906\u092f\u0924 '+bm.a;
  if(metaEl)metaEl.textContent=ago;
  if(bms.length>1&&allEl){allEl.textContent='सभी बुकमार्क देखें ('+bms.length+')';allEl.style.display='';}
  section.style.display='';
})();
</script>
</body>
</html>
""" % COMPACT_FOOTER)

print('लिखा: %s' % index_path)

# ---------------------------------------------------------------------------
# Generate bookmarks.html
# ---------------------------------------------------------------------------
bm_path = os.path.join(out_dir, 'bookmarks.html')
with open(bm_path, 'w', encoding='utf-8') as out:
    out.write("""\
<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>बुकमार्क &ndash; क़ुरआन हिंदी</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600&display=swap" rel="stylesheet">
<style>
%s
.bm-list{display:flex;flex-direction:column;gap:10px;margin-top:12px}
.bm-item{display:flex;align-items:center;gap:10px;padding:10px 14px;
  background:#f0f7f4;border:1px solid #a9cfc0;border-radius:6px}
.bm-item:hover{background:#d5ede5}
.bm-info{flex:1;min-width:0}
.bm-title{font-weight:600;font-size:.95em;color:#145a32;
  font-family:'Noto Sans Devanagari',system-ui,sans-serif}
.bm-meta{font-size:.78em;color:#666;margin-top:2px}
.bm-go{padding:6px 14px;background:#145a32;color:#fff;border:none;border-radius:4px;
  cursor:pointer;font-size:.9em;text-decoration:none;white-space:nowrap;
  font-family:'Noto Sans Devanagari',system-ui,sans-serif}
.bm-go:hover{background:#1e8449}
.bm-del{padding:6px 10px;background:#fff;color:#c0392b;border:1px solid #e88;
  border-radius:4px;cursor:pointer;font-size:.9em}
.bm-del:hover{background:#ffeaea}
.bm-actions{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.bm-actions button{padding:7px 16px;border:none;border-radius:4px;cursor:pointer;
  font-size:.9em;background:#145a32;color:#fff;
  font-family:'Noto Sans Devanagari',system-ui,sans-serif}
.bm-actions button:hover{background:#1e8449}
.bm-empty{color:#888;font-size:.95em;margin-top:16px;
  font-family:'Noto Sans Devanagari',system-ui,sans-serif}
@media(prefers-color-scheme:dark){
  .bm-item{background:#122a1f;border-color:#2a4d3a}
  .bm-item:hover{background:#1a3d2c}
  .bm-title{color:#82e0aa}
  .bm-meta{color:#aaa}
  .bm-del{background:#1a0a0a;color:#f1948a;border-color:#7b241c}
  .bm-del:hover{background:#2a1010}
}
</style>
</head>
<body>
<header>
  <a href="index.html">&#8962; मुख्य पृष्ठ</a>
  <a class="header-search" href="bookmarks.html">&#128278; बुकमार्क</a>
</header>
<main>
<h1>&#128278; मेरे बुकमार्क</h1>
<div class="bm-actions">
  <button onclick="exportBM()">&#128229; निर्यात करें (JSON)</button>
  <button onclick="document.getElementById('bm-import').click()">&#128228; आयात करें</button>
  <button onclick="clearAllBM()" style="background:#c0392b">&#128465; सभी हटाएँ</button>
</div>
<input type="file" id="bm-import" accept=".json" style="display:none" onchange="importBM(event)">
<div id="bm-list" class="bm-list"></div>
<p id="bm-empty" class="bm-empty" style="display:none">कोई बुकमार्क नहीं है। किसी आयत पर &#128278; बटन दबाएँ।</p>
</main>
%s
<script>
var BM_KEY='hindi-quran-bookmark';
function loadBMs(){
  var bms=[];
  try{bms=JSON.parse(localStorage.getItem(BM_KEY)||'[]');}catch(_){}
  return Array.isArray(bms)?bms:[];
}
function saveBMs(bms){
  try{localStorage.setItem(BM_KEY,JSON.stringify(bms));}catch(_){}
}
function timeAgo(t){
  var diff=Math.round((Date.now()-t)/60000);
  if(diff<1)return 'अभी';
  if(diff<60)return diff+' मिनट पहले';
  if(diff<1440)return Math.round(diff/60)+' घंटे पहले';
  return Math.round(diff/1440)+' दिन पहले';
}
function renderBMs(){
  var bms=loadBMs();
  var listEl=document.getElementById('bm-list');
  var emptyEl=document.getElementById('bm-empty');
  listEl.innerHTML='';
  if(!bms.length){emptyEl.style.display='';return;}
  emptyEl.style.display='none';
  bms.forEach(function(bm,idx){
    var href=String(bm.s).padStart(3,'0')+'.html#ayah-'+bm.a;
    var sura=bm.n||('सूरह '+bm.s);
    var div=document.createElement('div');
    div.className='bm-item';
    div.innerHTML=
      '<div class="bm-info">'
      +'<div class="bm-title">&#128214; '+sura+' &mdash; आयत '+bm.a+'</div>'
      +'<div class="bm-meta">'+timeAgo(bm.t)+'</div>'
      +'</div>'
      +'<a href="'+href+'" class="bm-go">जाएँ &#8594;</a>'
      +'<button class="bm-del" onclick="deleteBM('+idx+')" title="हटाएँ">&#10005;</button>';
    listEl.appendChild(div);
  });
}
window.deleteBM=function(idx){
  var bms=loadBMs();
  bms.splice(idx,1);
  saveBMs(bms);
  renderBMs();
};
window.clearAllBM=function(){
  if(confirm('क्या आप सभी बुकमार्क हटाना चाहते हैं?')){
    saveBMs([]);
    renderBMs();
  }
};
window.exportBM=function(){
  var bms=loadBMs();
  var blob=new Blob([JSON.stringify(bms,null,2)],{type:'application/json'});
  var a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='quran-hindi-bookmarks.json';
  a.click();
};
window.importBM=function(e){
  var file=e.target.files[0];
  if(!file)return;
  var reader=new FileReader();
  reader.onload=function(ev){
    try{
      var data=JSON.parse(ev.target.result);
      if(Array.isArray(data)){saveBMs(data);renderBMs();}
      else alert('अमान्य फ़ाइल।');
    }catch(_){alert('फ़ाइल पढ़ने में त्रुटि।');}
  };
  reader.readAsText(file);
  e.target.value='';
};
renderBMs();
</script>
</body>
</html>
""" % (CSS, COMPACT_FOOTER))

print('लिखा: %s' % bm_path)
print('\nसफलतापूर्वक %d सूरह पृष्ठ, index.html और bookmarks.html बनाए गए।' % 114)
