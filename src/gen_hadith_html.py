#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download all available hadith collections and generate HTML pages + plain-text output.

Run from the repository root:
    python3 src/gen_hadith_html.py

Sources:
  - fawazahmed0/hadith-api (via jsDelivr CDN) — English + Arabic for all 10 collections
  - Hand-curated Hindi translations for Al-Nawawi's 40 Hadith

Collections (10 total):
  1. Forty Hadith of an-Nawawi       (42 hadiths)
  2. Forty Hadith Qudsi               (40 hadiths)
  3. Forty Hadith of Shah Waliullah Dehlawi (40 hadiths)
  4. Sahih al-Bukhari                 (7589 hadiths)
  5. Sahih Muslim                     (7563 hadiths)
  6. Sunan Abu Dawud                  (5274 hadiths)
  7. Jami At-Tirmidhi                 (3998 hadiths)
  8. Sunan Ibn Majah                  (4343 hadiths)
  9. Sunan an-Nasai                   (5765 hadiths)
 10. Muwatta Malik                    (1858 hadiths)

Outputs:
  - data/hadith/{collection}.json.zip   — compressed source data (English + Arabic)
  - docs/hadith/index.html              — collection browser
  - docs/hadith/{collection}.html       — small collections (all hadiths on one page)
  - docs/hadith/{collection}-book-NNN.html — large collections (one page per book)
  - output/hadith/hadith_{collection}_english.txt
  - output/hadith/hadith_{collection}_arabic.txt
  - output/hadith/hadith_{collection}_hindi.txt  (only for nawawi)
"""

import os
import json
import zipfile
import urllib.request
import html as html_module

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(REPO_ROOT, "data", "hadith")
OUT_DIR   = os.path.join(REPO_ROOT, "output", "hadith")
DOCS_DIR  = os.path.join(REPO_ROOT, "docs", "hadith")
DOCS_ROOT = os.path.join(REPO_ROOT, "docs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUT_DIR,  exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

CDN_BASE = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions"

# ---------------------------------------------------------------------------
# Collection registry
# ---------------------------------------------------------------------------
COLLECTIONS = [
    {
        "id": "nawawi",
        "name_en": "Forty Hadith of an-Nawawi",
        "name_ar": "الأربعون النووية",
        "author": "Imam Yahya ibn Sharaf an-Nawawi (d. 676 AH)",
        "desc": "A collection of 42 fundamental hadith compiled by Imam Nawawi, covering the essential principles of Islam.",
        "large": False,
    },
    {
        "id": "qudsi",
        "name_en": "Forty Hadith Qudsi",
        "name_ar": "الأحاديث القدسية الأربعون",
        "author": "Various",
        "desc": "Forty Sacred (Qudsi) Hadith — narrations in which the Prophet (ﷺ) attributes words directly to Allah.",
        "large": False,
    },
    {
        "id": "dehlawi",
        "name_en": "Forty Hadith of Shah Waliullah Dehlawi",
        "name_ar": "أربعون حديثاً",
        "author": "Shah Waliullah Dehlawi (d. 1176 AH)",
        "desc": "A selection of 40 important hadith chosen by the 18th-century Indian scholar Shah Waliullah Dehlawi.",
        "large": False,
    },
    {
        "id": "bukhari",
        "name_en": "Sahih al-Bukhari",
        "name_ar": "صحيح البخاري",
        "author": "Imam Muhammad al-Bukhari (d. 256 AH)",
        "desc": "The most authentic collection of hadith, compiled by Imam Bukhari. Contains over 7,500 hadith in 97 books.",
        "large": True,
    },
    {
        "id": "muslim",
        "name_en": "Sahih Muslim",
        "name_ar": "صحيح مسلم",
        "author": "Imam Muslim ibn al-Hajjaj (d. 261 AH)",
        "desc": "The second most authentic hadith collection. Together with Bukhari, forms the 'Two Sahihs'.",
        "large": True,
    },
    {
        "id": "abudawud",
        "name_en": "Sunan Abu Dawud",
        "name_ar": "سنن أبي داود",
        "author": "Imam Abu Dawud as-Sijistani (d. 275 AH)",
        "desc": "One of the six canonical Sunni hadith collections, focusing on legal rulings.",
        "large": True,
    },
    {
        "id": "tirmidhi",
        "name_en": "Jami At-Tirmidhi",
        "name_ar": "جامع الترمذي",
        "author": "Imam Muhammad at-Tirmidhi (d. 279 AH)",
        "desc": "One of the six canonical Sunni hadith collections, known for grading each hadith.",
        "large": True,
    },
    {
        "id": "ibnmajah",
        "name_en": "Sunan Ibn Majah",
        "name_ar": "سنن ابن ماجه",
        "author": "Imam Muhammad ibn Yazid ibn Majah (d. 273 AH)",
        "desc": "The sixth of the six canonical Sunni hadith collections.",
        "large": True,
    },
    {
        "id": "nasai",
        "name_en": "Sunan an-Nasai",
        "name_ar": "سنن النسائي",
        "author": "Imam Ahmad ibn Shu'ayb an-Nasai (d. 303 AH)",
        "desc": "One of the six canonical Sunni hadith collections, noted for strict criteria.",
        "large": True,
    },
    {
        "id": "malik",
        "name_en": "Muwatta Malik",
        "name_ar": "موطأ مالك",
        "author": "Imam Malik ibn Anas (d. 179 AH)",
        "desc": "The earliest surviving collection of hadith; the foundational text of the Maliki school.",
        "large": True,
    },
]

# ---------------------------------------------------------------------------
# Hindi translations for Al-Nawawi's 40 Hadith
# ---------------------------------------------------------------------------
NAWAWI_HINDI = {
1: ("उमर बिन अल-खत्ताब (रज़ि.)",
    "बेशक सभी कार्य नीयत से होते हैं, और हर व्यक्ति को वही मिलता है जो उसने नीयत की। "
    "अतः जिसका हिजरत अल्लाह और उसके रसूल की ओर हो, उसका हिजरत अल्लाह और उसके रसूल की ओर है; "
    "और जिसका हिजरत दुनिया की किसी चीज़ को पाने या किसी स्त्री से विवाह करने के लिए हो, "
    "तो उसका हिजरत उसी की ओर है जिसके लिए उसने हिजरत की।"),
2: ("उमर (रज़ि.) — जिबरील का हदीस",
    "जब जिबरील (अलैहि.) इंसानी रूप में आए और इस्लाम, ईमान और इहसान के बारे में पूछा। "
    "आप (ﷺ) ने फ़रमाया: इस्लाम यह है कि तुम गवाही दो कि अल्लाह के सिवाय कोई इबादत के लायक नहीं "
    "और मुहम्मद (ﷺ) अल्लाह के रसूल हैं, नमाज़ क़ायम करो, ज़कात दो, रमज़ान के रोज़े रखो, "
    "और हज करो। ईमान यह है कि तुम अल्लाह, उसके फ़रिश्तों, उसकी किताबों, उसके रसूलों, "
    "आख़िरत के दिन और तक़दीर के अच्छे-बुरे पर ईमान रखो। और इहसान यह है कि "
    "तुम अल्लाह की इबादत इस तरह करो जैसे उसे देख रहे हो।"),
3: ("अब्दुल्लाह बिन उमर (रज़ि.)",
    "इस्लाम की बुनियाद पाँच चीज़ों पर है: इस बात की गवाही देना कि अल्लाह के सिवाय कोई "
    "इबादत के लायक नहीं और मुहम्मद (ﷺ) अल्लाह के रसूल हैं, नमाज़ क़ायम करना, "
    "ज़कात अदा करना, अल्लाह के घर का हज करना, और रमज़ान के रोज़े रखना।"),
4: ("अब्दुल्लाह बिन मसऊद (रज़ि.)",
    "तुम में से हर एक की पैदाइश उसकी माँ के पेट में चालीस दिन तक नुत्फ़े की शक्ल में, "
    "फिर उतने ही समय में 'अलक़' की शक्ल में, फिर उतने ही समय में 'मुज़्ग़ा' की शक्ल में रहती है। "
    "फिर एक फ़रिश्ता चार बातें लिखता है: रिज़्क़, उम्र, आमाल, और ख़ुश-नसीब या बदनसीब। "
    "इसके बाद उसमें रूह फूँकी जाती है।"),
5: ("उम्मुल मोमिनीन आइशा (रज़ि.)",
    "जिसने हमारे इस दीन में कोई ऐसी चीज़ ईजाद की जो उसमें नहीं, वह मर्दूद (अस्वीकृत) है।"),
6: ("नोमान बिन बशीर (रज़ि.)",
    "हलाल ज़ाहिर है और हराम भी ज़ाहिर है, और उन दोनों के बीच कुछ संदिग्ध चीज़ें हैं। "
    "जो संदिग्ध चीज़ों से बचा, उसने अपने दीन और अपनी इज्जत की हिफ़ाजत की। "
    "और जो संदिग्ध चीज़ों में पड़ गया वह हराम में पड़ गया।"),
7: ("शद्दाद बिन औस (रज़ि.)",
    "बेशक अल्लाह ने हर चीज़ पर इहसान फ़र्ज़ किया है। अतः जब तुम (किसी को) क़त्ल करो तो "
    "अच्छी तरह क़त्ल करो, और जब ज़बह करो तो अच्छी तरह ज़बह करो। छुरी तेज़ रखो।"),
8: ("अब्दुल्लाह बिन उमर (रज़ि.)",
    "मुझे तब तक लोगों से लड़ने का हुक्म दिया गया है जब तक वे गवाही न दें कि अल्लाह के सिवाय "
    "कोई इबादत के लायक नहीं और मुहम्मद (ﷺ) अल्लाह के रसूल हैं, नमाज़ क़ायम करें और ज़कात दें।"),
9: ("अबू हुरैरा (रज़ि.)",
    "जो मैंने तुम्हें हुक्म दिया हो उसे करते रहो और जो मना किया हो उससे रुको — "
    "जहाँ तक तुम्हारी ताक़त हो।"),
10: ("अबू हुरैरा (रज़ि.)",
    "बेशक अल्लाह पाक है और पाकी को ही पसंद करता है। वह तय्यिब है और तय्यिब को ही क़ुबूल करता है।"),
11: ("अल-हसन बिन अली (रज़ि.)",
    "जो चीज़ तुम्हें शक में डाले उसे छोड़ो और जो शक में न डाले उसे लो। "
    "सच्चाई में सुकून है और झूठ में शक।"),
12: ("अबू हुरैरा (रज़ि.)",
    "किसी इंसान के इस्लाम की ख़ूबी में से यह है कि वह फ़ुज़ूल बातों को छोड़ दे।"),
13: ("अनस बिन मालिक (रज़ि.)",
    "तुम में से कोई उस वक़्त तक मोमिन नहीं होता जब तक अपने भाई के लिए वही पसंद न करे "
    "जो अपने लिए पसंद करता है।"),
14: ("अब्दुल्लाह बिन मसऊद (रज़ि.)",
    "किसी मुसलमान का ख़ून तीन में से एक सूरत के बिना हलाल नहीं: शादीशुदा होते हुए ज़िना, "
    "जान के बदले जान, और अपना दीन छोड़कर जमाअत से अलग होना।"),
15: ("अबू हुरैरा (रज़ि.)",
    "जो अल्लाह पर और आख़िरत के दिन पर ईमान रखता हो, वह अच्छी बात कहे या ख़ामोश रहे; "
    "और अपने पड़ोसी को तकलीफ़ न दे; और अपने मेहमान की इज्जत करे।"),
16: ("अबू हुरैरा (रज़ि.)",
    "ग़ुस्सा मत करो।"),
17: ("शद्दाद बिन औस (रज़ि.)",
    "बेशक अल्लाह ने मुझ पर वह्य की कि तुम झुको (विनम्र रहो) यहाँ तक कि कोई किसी पर "
    "फ़ख्र न करे और कोई किसी पर ज़ुल्म न करे।"),
18: ("अबू ज़र (रज़ि.) और मुआज़ बिन जबल (रज़ि.)",
    "जहाँ भी रहो, अल्लाह से डरो, बुराई के बाद नेकी करो वह उसे मिटा देगी, "
    "और लोगों के साथ अच्छे अख़्लाक़ से पेश आओ।"),
19: ("अब्दुल्लाह बिन अब्बास (रज़ि.)",
    "अल्लाह की हिफ़ाज़त करो, अल्लाह तुम्हारी हिफ़ाज़त करेगा। अल्लाह को याद रखो, "
    "उसे अपने सामने पाओगे। जब माँगो तो अल्लाह से माँगो और जब मदद चाहो तो "
    "अल्लाह से मदद माँगो।"),
20: ("अबू मसऊद (रज़ि.)",
    "पहले नबुव्वत की जो बातें लोगों तक पहुँची हैं उनमें से यह है: "
    "जब तुम्हें शर्म न आए तो जो चाहो करो।"),
21: ("सुफ़यान बिन अब्दुल्लाह (रज़ि.)",
    "कहो: मैं अल्लाह पर ईमान लाया, फिर (उस पर) क़ायम रहो।"),
22: ("जाबिर बिन अब्दुल्लाह (रज़ि.)",
    "अगर तुम फ़र्ज़ नमाज़ें अदा करो, रमज़ान के रोज़े रखो, हलाल को हलाल और हराम को हराम समझो "
    "तो जन्नत में जाओगे।"),
23: ("अबू मालिक अल-अशअरी (रज़ि.)",
    "पाकी आधा ईमान है। 'अलहम्दुलिल्लाह' मीज़ान को भर देती है। "
    "'सुब्हानल्लाह' और 'अलहम्दुलिल्लाह' आसमान और ज़मीन के बीच की जगह को भर देती हैं। "
    "नमाज़ नूर है, सदक़ा दलील है, सब्र रोशनी है।"),
24: ("अबू ज़र अल-ग़िफ़ारी (रज़ि.) — हदीस क़ुदसी",
    "ऐ मेरे बंदो! मैंने अपने ऊपर ज़ुल्म हराम किया है और इसे तुम्हारे बीच भी हराम किया है, "
    "अतः एक-दूसरे पर ज़ुल्म न करो। ऐ मेरे बंदो! तुम सब गुमराह हो सिवाय उसके जिसे "
    "मैं हिदायत दूँ, अतः मुझसे हिदायत माँगो।"),
25: ("अबू हुरैरा (रज़ि.)",
    "लोगों में सबसे बुरा दुतरफ़ा बात करने वाला है जो एक तरफ़ की बात दूसरी तरफ़ पहुँचाता है।"),
26: ("अबू हुरैरा (रज़ि.)",
    "हर इंसान पर हर रोज़ जब उसकी हर हड्डी पर सूरज उगता है सदक़ा ज़रूरी है। "
    "दो लोगों के बीच इंसाफ़ करो — यह सदक़ा है। रास्ते से तकलीफ़देह चीज़ हटाना सदक़ा है।"),
27: ("नव्वास बिन समआन (रज़ि.)",
    "नेकी अच्छे अख़्लाक़ का नाम है, और गुनाह वह है जो तुम्हारी छाती में खटके "
    "और तुम नहीं चाहते कि लोग उससे बाख़बर हों।"),
28: ("इर्बाज़ बिन सारिया (रज़ि.)",
    "मैं तुम्हें अल्लाह के तक़वे की और सुनने और मानने की वसीयत करता हूँ। "
    "मेरी सुन्नत और हिदायत पाए हुए ख़ुलफ़ा-ए-राशिदीन की सुन्नत को लाज़िम पकड़ो।"),
29: ("मुआज़ बिन जबल (रज़ि.)",
    "जन्नत का रास्ता: अल्लाह की इबादत करो और उसके साथ किसी को शरीक न करो, "
    "नमाज़ क़ायम करो, ज़कात दो, रमज़ान के रोज़े रखो, और हज करो।"),
30: ("सुफ़यान बिन अब्दुल्लाह अस-सक़फ़ी (रज़ि.)",
    "अल्लाह ने फ़रमाया: बेशक यह मेरा सीधा रास्ता है, इसलिए इसी पर चलो "
    "और दूसरे रास्तों पर मत चलो।"),
31: ("अबू सालिब (रज़ि.)",
    "सत्य का रास्ता अपनाओ क्योंकि सत्य नेकी तक पहुँचाता है और नेकी जन्नत तक पहुँचाती है।"),
32: ("अबू सईद अल-ख़ुद्री (रज़ि.)",
    "नुक़सान न करो और न नुक़सान सहो।"),
33: ("इब्ने अब्बास (रज़ि.)",
    "सबूत देने की ज़िम्मेदारी दावा करने वाले पर है और क़सम उसके ज़िम्मे है जो इनकार करे।"),
34: ("अबू सईद अल-ख़ुद्री (रज़ि.)",
    "जिसने तुममें से कोई बुराई देखी, वह उसे अपने हाथ से बदल दे; अगर इसकी ताक़त न हो "
    "तो ज़बान से; अगर इसकी भी ताक़त न हो तो दिल से — और यह ईमान का सबसे कमज़ोर दर्जा है।"),
35: ("अबू हुरैरा (रज़ि.)",
    "आपस में हसद न करो, एक-दूसरे से नफ़रत न करो, मुसलमान मुसलमान का भाई है, "
    "उस पर ज़ुल्म नहीं करता, उसे बेसहारा नहीं छोड़ता।"),
36: ("अबू हुरैरा (रज़ि.)",
    "जो कोई किसी मोमिन की दुनिया की परेशानी दूर करे, अल्लाह उसकी क़यामत की "
    "परेशानी दूर करेगा। अल्लाह बंदे की मदद में रहता है जब तक बंदा "
    "अपने भाई की मदद में रहता है।"),
37: ("इब्ने अब्बास (रज़ि.)",
    "बेशक अल्लाह ने नेकियाँ और बुराइयाँ लिख दी हैं। जो नेकी का इरादा करे लेकिन न करे, "
    "अल्लाह उसके लिए एक पूरी नेकी लिखता है। और अगर कर भी लिया तो "
    "दस से सात सौ गुने तक नेकियाँ लिखता है।"),
38: ("अबू हुरैरा (रज़ि.) — हदीस क़ुदसी",
    "जो मेरे किसी ولी से दुश्मनी रखे, मैं उसके ख़िलाफ़ जंग का ऐलान करता हूँ। "
    "मेरा बंदा नफ़ल इबादत से मेरे क़रीब होता रहता है यहाँ तक कि मैं उससे प्यार करने लगता हूँ। "
    "जब मैं उससे प्यार करता हूँ तो मैं उसके कान, आँखें, हाथ और पाँव बन जाता हूँ।"),
39: ("इब्ने अब्बास (रज़ि.)",
    "बेशक अल्लाह ने मेरी उम्मत के लिए ग़लतियाँ, भूल और वह काम जिस पर उन्हें "
    "मजबूर किया जाए — माफ़ कर दिए हैं।"),
40: ("इब्ने उमर (रज़ि.)",
    "दुनिया में ऐसे रहो जैसे तुम परदेसी हो या राही (मुसाफ़िर)। "
    "जब शाम हो जाए तो सुबह का इंतज़ार न करो, और जब सुबह हो तो शाम का। "
    "बीमारी से पहले सेहत को और मौत से पहले ज़िंदगी को ग़नीमत जानो।"),
41: ("अब्दुल्लाह बिन अम्र बिन अल-आस (रज़ि.)",
    "तुम में से कोई उस वक़्त तक (पूरा) मोमिन नहीं होता जब तक उसकी इच्छाएँ उस दीन के "
    "ताबे न हो जाएँ जो मैं लेकर आया हूँ।"),
42: ("अनस बिन मालिक (रज़ि.) — हदीस क़ुदसी",
    "ऐ आदम के बेटे! जब तक तू मुझसे दुआ करता रहेगा और मुझसे उम्मीद रखेगा, "
    "मैं तेरे गुनाह माफ़ करता रहूँगा — चाहे वे जितने भी हों। "
    "ऐ आदम के बेटे! अगर तेरे गुनाह आसमान की बुलंदियों तक पहुँच जाएँ और "
    "फिर तू मुझसे माफ़ी माँगे, मैं तुझे माफ़ कर दूँगा।"),
}

# ---------------------------------------------------------------------------
# Shared CSS / header / footer
# ---------------------------------------------------------------------------
SHARED_CSS = """
*,*::before,*::after{box-sizing:border-box}
body{margin:0;padding:0;font-family:system-ui,Arial,Helvetica,sans-serif;
  font-size:16px;background:#fff;color:#111;line-height:1.6}
header{background:#1a3a5c;color:#fff;padding:12px 16px;position:sticky;top:0;z-index:10;
  display:flex;align-items:center;gap:12px;flex-wrap:wrap}
header a{color:#ffd54f;text-decoration:none;font-weight:bold;font-size:1.1em}
header a:hover{text-decoration:underline}
.breadcrumb{font-size:.9em;color:#aad4f5}
.breadcrumb a{color:#ffd54f;text-decoration:none}
.breadcrumb a:hover{text-decoration:underline}
main{padding:16px;max-width:900px;margin:0 auto}
h1{font-size:1.4em;margin:0 0 12px;color:#1a3a5c}
h2{font-size:1.15em;color:#1a3a5c;margin:20px 0 8px}
.desc{background:#f0f4f8;border-left:4px solid #1a3a5c;padding:10px 14px;
  margin-bottom:16px;font-size:.95em;line-height:1.7;border-radius:0 4px 4px 0}
.meta-info{font-size:.88em;color:#555;margin-bottom:16px}
.hadith-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));
  gap:8px;margin-top:16px}
.hadith-grid a{display:block;padding:10px 12px;background:#f0f4f8;border:1px solid #ccd6e0;
  border-radius:6px;text-decoration:none;color:#1a3a5c;font-size:.95em}
.hadith-grid a:hover{background:#dde8f2}
.coll-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
  gap:12px;margin-top:16px}
.coll-card{display:flex;flex-direction:column;padding:14px 16px;
  background:#f0f4f8;border:1px solid #ccd6e0;border-radius:8px;
  text-decoration:none;color:#111}
.coll-card:hover{background:#dde8f2;border-color:#aac0d6}
.coll-card .cc-name{font-weight:bold;font-size:1em;color:#1a3a5c;margin-bottom:4px}
.coll-card .cc-name-ar{font-family:'Scheherazade New','Amiri',serif;
  font-size:1.15em;direction:rtl;color:#7c5533;margin-bottom:6px}
.coll-card .cc-author{font-size:.82em;color:#666;margin-bottom:4px}
.coll-card .cc-desc{font-size:.85em;color:#444;line-height:1.55}
.coll-card .cc-count{font-size:.8em;font-weight:bold;color:#1a3a5c;margin-top:8px}
.table-wrap{overflow-x:auto;width:100%}
table{width:100%;border-collapse:collapse;margin-bottom:24px}
th{background:#1a3a5c;color:#fff;padding:10px 12px;text-align:left;font-size:.9em}
td{padding:8px 12px;vertical-align:top;border:1px solid #ccd6e0}
.hadith-sep td{background:#1a3a5c;color:#fff;font-weight:bold;
  font-size:.92em;padding:7px 12px;border-color:#1a3a5c}
.label{color:#777;font-size:.82em;white-space:nowrap;width:100px;vertical-align:top}
.arabic td{background:#fff8e1}
.arabic-text{font-family:'Scheherazade New','Amiri','Traditional Arabic',serif;
  font-size:1.5em;direction:rtl;text-align:right;line-height:2.1}
.eng td{background:#e3f2fd}
.eng-text{color:#1a237e;line-height:1.7}
.hindi td{background:#f5f0ff}
.hindi-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#3a2a6c;line-height:1.8}
.narrator td{background:#f0f4f8}
.narrator-text{font-style:italic;color:#555}
.grade td{background:#e8f5e9}
.grade-text{font-size:.85em;color:#2e7d32}
.ref td{background:#f9fbe7}
.ref-text{font-size:.82em;color:#558b2f}
nav.chapter-nav{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;
  padding:14px 0;margin-top:8px;border-top:1px solid #ccd6e0}
nav.chapter-nav a{display:inline-block;padding:8px 16px;background:#1a3a5c;color:#fff;
  border-radius:4px;text-decoration:none;font-size:.95em}
nav.chapter-nav a:hover{background:#2a5a8c}
footer{text-align:center;padding:16px 20px;font-size:.82em;color:#666;
  border-top:1px solid #e0e0e0;margin-top:32px;line-height:1.8}
footer a{color:#1a3a5c;text-decoration:none;font-weight:600}
footer a:hover{text-decoration:underline}
.book-list{list-style:none;padding:0;margin:0}
.book-list li{border-bottom:1px solid #eee}
.book-list a{display:block;padding:9px 12px;color:#1a3a5c;text-decoration:none;
  font-size:.95em}
.book-list a:hover{background:#f0f4f8}
.book-list .bl-count{float:right;font-size:.82em;color:#888;margin-top:2px}
.search-box{margin-bottom:16px;display:flex;gap:8px}
.search-box input{flex:1;padding:8px 12px;border:1px solid #ccd6e0;border-radius:4px;
  font-size:.95em}
.search-box button{padding:8px 16px;background:#1a3a5c;color:#fff;border:none;
  border-radius:4px;cursor:pointer;font-size:.95em}
.search-box button:hover{background:#2a5a8c}
@media(max-width:600px){
  main{padding:10px 8px}
  h1{font-size:1.15em}
  .arabic-text{font-size:1.25em}
  nav.chapter-nav a{padding:10px 14px;min-height:44px;display:inline-flex;align-items:center}
  footer{font-size:.78em;padding:12px 14px}
}
"""

FOOTER_HTML = """<footer>
  <a href="../index.html">Qur'an Home</a> &nbsp;|&nbsp;
  <a href="index.html">Hadith Home</a> &nbsp;|&nbsp;
  <a href="../sources.html">Sources</a> &nbsp;|&nbsp;
  <a href="https://github.com/druvx13/Quran-data" rel="noopener noreferrer">GitHub</a>
  <br>Hadith data sourced from
  <a href="https://github.com/fawazahmed0/hadith-api" rel="noopener noreferrer">fawazahmed0/hadith-api</a>
  (public domain). Hindi translations for Nawawi 40 are hand-curated.
</footer>"""

def make_header(title, breadcrumb_extra=""):
    bc = f'<span class="breadcrumb"><a href="../index.html">Qur\'an</a> › <a href="index.html">Hadith</a>{breadcrumb_extra}</span>'
    return f"""<header>
  <a href="../index.html">📖 Qur'an</a>
  <a href="index.html">📜 Hadith</a>
  {bc}
</header>"""

def truncate_words(text, max_chars=40):
    """Truncate at a word boundary, adding '…' if needed."""
    if len(text) <= max_chars:
        return text
    trunc = text[:max_chars].rsplit(" ", 1)[0]
    return trunc + "…"


def page_wrap(title, body, breadcrumb_extra="", lang="en"):
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_module.escape(title)} – Hadith Reader</title>
<style>{SHARED_CSS}</style>
</head>
<body>
{make_header(title, breadcrumb_extra)}
<main>
{body}
</main>
{FOOTER_HTML}
</body>
</html>"""

# ---------------------------------------------------------------------------
# Data download helpers
# ---------------------------------------------------------------------------

def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req).read()


def load_or_download(collection_id):
    """Return merged dict {hadithnumber: {en, ar, grades, reference, section}} for a collection."""
    zip_path = os.path.join(DATA_DIR, f"{collection_id}.json.zip")

    if os.path.exists(zip_path):
        print(f"  [cache] {collection_id}")
        with zipfile.ZipFile(zip_path) as zf:
            with zf.open(f"{collection_id}.json") as fh:
                return json.load(fh)

    print(f"  [download] {collection_id} ...")
    eng_url = f"{CDN_BASE}/eng-{collection_id}.min.json"
    ara_url = f"{CDN_BASE}/ara-{collection_id}.min.json"

    eng_data = json.loads(fetch_url(eng_url))
    ara_data = json.loads(fetch_url(ara_url))

    # Build section lookup: hadithnumber -> section name
    sections = eng_data["metadata"]["sections"]
    section_details = eng_data["metadata"]["section_details"]
    section_map = {}
    for sec_id, sec_detail in section_details.items():
        if sec_id == "0":
            continue
        sec_name = sections.get(sec_id, "")
        first = int(sec_detail.get("hadithnumber_first", 0))
        last  = int(sec_detail.get("hadithnumber_last", 0))
        for n in range(first, last + 1):
            section_map[n] = {"id": sec_id, "name": sec_name}

    # Build Arabic lookup
    ara_lookup = {h["hadithnumber"]: h["text"] for h in ara_data["hadiths"]}

    merged = {
        "collection_id": collection_id,
        "name_en": eng_data["metadata"]["name"],
        "sections": {k: v for k, v in sections.items() if k != "0"},
        "section_details": section_details,
        "hadiths": []
    }

    for h in eng_data["hadiths"]:
        num = h["hadithnumber"]
        sec = section_map.get(num, {})
        grades = [g.get("grade", "") for g in h.get("grades", []) if g.get("grade")]
        merged["hadiths"].append({
            "n": num,
            "an": h.get("arabicnumber", num),
            "en": h["text"],
            "ar": ara_lookup.get(num, ""),
            "sec_id": sec.get("id", ""),
            "sec_name": sec.get("name", ""),
            "grades": grades,
            "ref": h.get("reference", {}),
        })

    # Save to zip
    json_bytes = json.dumps(merged, ensure_ascii=False).encode("utf-8")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr(f"{collection_id}.json", json_bytes)

    size_kb = os.path.getsize(zip_path) // 1024
    print(f"  [saved]    data/hadith/{collection_id}.json.zip ({size_kb} KB, {len(merged['hadiths'])} hadiths)")
    return merged


# ---------------------------------------------------------------------------
# Text output generation
# ---------------------------------------------------------------------------

def write_text_outputs(coll_info, data):
    cid = coll_info["id"]
    name = coll_info["name_en"]

    def write_file(suffix, lines):
        path = os.path.join(OUT_DIR, f"hadith_{cid}_{suffix}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{'='*70}\n{name}\n{'='*70}\n\n")
            f.write("\n".join(lines))
        print(f"  [txt] output/hadith/hadith_{cid}_{suffix}.txt")

    eng_lines = []
    ara_lines = []
    cur_sec = None

    for h in data["hadiths"]:
        if h["sec_name"] and h["sec_name"] != cur_sec:
            cur_sec = h["sec_name"]
            sep = f"\n--- {cur_sec} ---\n"
            eng_lines.append(sep)
            ara_lines.append(sep)

        eng_lines.append(f"[{h['n']}] {h['en']}\n")
        ara_lines.append(f"[{h['n']}] {h['ar']}\n")

    write_file("english", eng_lines)
    write_file("arabic", ara_lines)

    # Hindi only for Nawawi
    if cid == "nawawi":
        hi_lines = []
        for h in data["hadiths"]:
            hi = NAWAWI_HINDI.get(h["n"])
            if hi:
                narrator, text = hi
                hi_lines.append(f"[{h['n']}] [{narrator}]\n{text}\n")
            else:
                hi_lines.append(f"[{h['n']}] {h['en']}\n")
        write_file("hindi", hi_lines)


# ---------------------------------------------------------------------------
# HTML for small collections (all hadiths on one page)
# ---------------------------------------------------------------------------

def render_hadith_rows(h, show_hindi=False):
    num  = h["n"]
    en   = html_module.escape(h["en"])
    ar   = html_module.escape(h["ar"]) if h["ar"] else ""
    sec  = html_module.escape(h["sec_name"]) if h["sec_name"] else ""
    grades_str = "; ".join(h["grades"]) if h["grades"] else ""
    ref  = h.get("ref", {})
    ref_str = ""
    if ref:
        ref_str = f"Book {ref.get('book', '')}, Hadith {ref.get('hadith', num)}"

    rows = []
    rows.append(f"<tr class='hadith-sep'><td colspan='2'>Hadith {num}{(' — '+sec) if sec else ''}</td></tr>")

    if ar:
        rows.append(f"<tr class='arabic'><td class='label'>Arabic</td>"
                    f"<td><span class='arabic-text'>{ar}</span></td></tr>")

    rows.append(f"<tr class='eng'><td class='label'>English</td>"
                f"<td><span class='eng-text'>{en}</span></td></tr>")

    if show_hindi:
        hi = NAWAWI_HINDI.get(num)
        if hi:
            narrator, text = hi
            rows.append(f"<tr class='narrator'><td class='label'>Narrator</td>"
                        f"<td><span class='narrator-text'>{html_module.escape(narrator)}</span></td></tr>")
            rows.append(f"<tr class='hindi'><td class='label'>हिन्दी</td>"
                        f"<td><span class='hindi-text'>{html_module.escape(text)}</span></td></tr>")

    if grades_str:
        rows.append(f"<tr class='grade'><td class='label'>Grade</td>"
                    f"<td><span class='grade-text'>{html_module.escape(grades_str)}</span></td></tr>")

    if ref_str and ref.get("book", 0) and ref.get("hadith", 0):
        rows.append(f"<tr class='ref'><td class='label'>Reference</td>"
                    f"<td><span class='ref-text'>{html_module.escape(ref_str)}</span></td></tr>")

    return "\n".join(rows)


def gen_small_collection_page(coll_info, data):
    cid   = coll_info["id"]
    name  = coll_info["name_en"]
    name_ar = coll_info["name_ar"]
    author = coll_info["author"]
    desc  = coll_info["desc"]
    show_hindi = (cid == "nawawi")

    rows_html = []
    for h in data["hadiths"]:
        rows_html.append(render_hadith_rows(h, show_hindi=show_hindi))

    body = f"""<h1>{html_module.escape(name)}</h1>
<div class="meta-info">
  <strong>Author:</strong> {html_module.escape(author)} &nbsp;|&nbsp;
  <strong>Arabic:</strong> <span style="font-family:'Scheherazade New',serif;font-size:1.1em">{html_module.escape(name_ar)}</span> &nbsp;|&nbsp;
  <strong>Total:</strong> {len(data['hadiths'])} hadith
</div>
<div class="desc">{html_module.escape(desc)}</div>
{"<div class='desc' style='background:#f5f0ff;border-color:#6a4c93'>🇮🇳 <strong>Hindi translation available</strong> for this collection.</div>" if show_hindi else ""}
<div class="table-wrap">
<table>
<thead><tr><th style="width:100px">Field</th><th>Content</th></tr></thead>
<tbody>
{"".join(rows_html)}
</tbody>
</table>
</div>
<nav class="chapter-nav">
  <a href="index.html">← All Collections</a>
  <a href="../index.html">Qur'an Home</a>
</nav>"""

    out_path = os.path.join(DOCS_DIR, f"{cid}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page_wrap(name, body, breadcrumb_extra=f" › {html_module.escape(name)}"))
    print(f"  [html] docs/hadith/{cid}.html")


# ---------------------------------------------------------------------------
# HTML for large collections (index + per-book pages)
# ---------------------------------------------------------------------------

def gen_large_collection_pages(coll_info, data):
    cid   = coll_info["id"]
    name  = coll_info["name_en"]
    name_ar = coll_info["name_ar"]
    author = coll_info["author"]
    desc  = coll_info["desc"]

    # Group hadiths by section
    sections_order = []
    sections_data  = {}
    for h in data["hadiths"]:
        sid  = h["sec_id"] or "0"
        sname = h["sec_name"] or "General"
        if sid not in sections_data:
            sections_order.append(sid)
            sections_data[sid] = {"name": sname, "hadiths": []}
        sections_data[sid]["hadiths"].append(h)

    total = len(data["hadiths"])

    # Build per-book pages
    book_links = []
    for idx, sid in enumerate(sections_order):
        sec  = sections_data[sid]
        sname = sec["name"]
        hadiths = sec["hadiths"]
        page_file = f"{cid}-book-{int(sid):03d}.html"
        first_n = hadiths[0]["n"]
        last_n  = hadiths[-1]["n"]

        rows_html = []
        for h in hadiths:
            rows_html.append(render_hadith_rows(h, show_hindi=False))

        prev_link = ""
        next_link = ""
        if idx > 0:
            prev_sid = sections_order[idx - 1]
            prev_file = f"{cid}-book-{int(prev_sid):03d}.html"
            prev_name = sections_data[prev_sid]["name"]
            prev_link = f'<a href="{prev_file}">← {html_module.escape(truncate_words(prev_name))}</a>'
        if idx < len(sections_order) - 1:
            next_sid = sections_order[idx + 1]
            next_file = f"{cid}-book-{int(next_sid):03d}.html"
            next_name = sections_data[next_sid]["name"]
            next_link = f'<a href="{next_file}">{html_module.escape(truncate_words(next_name))} →</a>'

        body = f"""<h1>{html_module.escape(name)}</h1>
<h2>{html_module.escape(sname)}</h2>
<div class="meta-info">
  Hadith {first_n}–{last_n} &nbsp;|&nbsp;
  <a href="{cid}.html">📚 Book Index</a>
</div>
<div class="table-wrap">
<table>
<thead><tr><th style="width:100px">Field</th><th>Content</th></tr></thead>
<tbody>
{"".join(rows_html)}
</tbody>
</table>
</div>
<nav class="chapter-nav">
  {prev_link if prev_link else '<span></span>'}
  <a href="{cid}.html">📚 Book Index</a>
  {next_link if next_link else '<span></span>'}
</nav>"""

        out_path = os.path.join(DOCS_DIR, page_file)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page_wrap(f"{name} — {sname}", body,
                              breadcrumb_extra=f" › <a href='{cid}.html'>{html_module.escape(name)}</a> › {html_module.escape(truncate_words(sname, 35))}"))

        book_links.append((page_file, sname, len(hadiths), first_n, last_n))

    print(f"  [html] docs/hadith/{cid}-book-NNN.html × {len(sections_order)} books")

    # Build collection index page
    book_items = []
    for page_file, sname, count, first_n, last_n in book_links:
        book_items.append(
            f'<li><a href="{page_file}">{html_module.escape(sname)}'
            f'<span class="bl-count">{count} hadith ({first_n}–{last_n})</span>'
            f'</a></li>'
        )

    body = f"""<h1>{html_module.escape(name)}</h1>
<div class="meta-info">
  <strong>Author:</strong> {html_module.escape(author)} &nbsp;|&nbsp;
  <strong>Arabic:</strong> <span style="font-family:'Scheherazade New',serif;font-size:1.1em">{html_module.escape(name_ar)}</span> &nbsp;|&nbsp;
  <strong>Total:</strong> {total:,} hadith
</div>
<div class="desc">{html_module.escape(desc)}</div>
<h2>Books / Chapters ({len(sections_order)})</h2>
<ul class="book-list">
{"".join(book_items)}
</ul>
<nav class="chapter-nav">
  <a href="index.html">← All Collections</a>
  <a href="../index.html">Qur'an Home</a>
</nav>"""

    out_path = os.path.join(DOCS_DIR, f"{cid}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page_wrap(name, body, breadcrumb_extra=f" › {html_module.escape(name)}"))
    print(f"  [html] docs/hadith/{cid}.html (index)")


# ---------------------------------------------------------------------------
# Hadith index page (docs/hadith/index.html)
# ---------------------------------------------------------------------------

def gen_index_page(collection_counts):
    cards = []
    for coll in COLLECTIONS:
        cid   = coll["id"]
        count = collection_counts.get(cid, "?")
        cards.append(
            f'<a class="coll-card" href="{cid}.html">'
            f'<div class="cc-name-ar">{html_module.escape(coll["name_ar"])}</div>'
            f'<div class="cc-name">{html_module.escape(coll["name_en"])}</div>'
            f'<div class="cc-author">{html_module.escape(coll["author"])}</div>'
            f'<div class="cc-desc">{html_module.escape(coll["desc"])}</div>'
            f'<div class="cc-count">📜 {count:,} hadith</div>'
            f'</a>'
        )

    body = f"""<h1>📜 Hadith Collections</h1>
<div class="desc">
  <strong>10 collections</strong> — from the concise 40-hadith compilations to the six canonical
  Sunni collections (<em>Kutub al-Sittah</em>). English and Arabic text for all collections;
  Hindi translation available for An-Nawawi's 40 Hadith.
</div>
<div class="coll-grid">
{"".join(cards)}
</div>
<nav class="chapter-nav">
  <a href="../index.html">← Qur'an Home</a>
</nav>"""

    out_path = os.path.join(DOCS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page_wrap("Hadith Collections", body))
    print("  [html] docs/hadith/index.html")


# ---------------------------------------------------------------------------
# Update docs/index.html to add Hadith section link
# ---------------------------------------------------------------------------

def update_quran_index():
    idx_path = os.path.join(DOCS_ROOT, "index.html")
    with open(idx_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if already updated
    if "hadith/index.html" in content:
        print("  [skip] docs/index.html already has Hadith link")
        return

    # Insert a Hadith section before the footer
    hadith_section = """
<section id="hadith-section" style="margin-top:28px">
  <h2 style="font-size:1.2em;color:#1a3a5c;margin-bottom:8px">📜 Hadith</h2>
  <div style="background:#f0f4f8;border:1px solid #ccd6e0;border-radius:8px;padding:14px 16px;margin-bottom:8px">
    <p style="margin:0 0 10px;font-size:.95em;line-height:1.6">
      Browse <strong>10 hadith collections</strong> — from the concise 40-hadith compilations
      (An-Nawawi, Qudsi, Dehlawi) to the six canonical Sunni collections (Bukhari, Muslim,
      Abu Dawud, Tirmidhi, Ibn Majah, Nasai) and Muwatta Malik.
      English + Arabic for all; Hindi for An-Nawawi's 40.
    </p>
    <a href="hadith/index.html" style="display:inline-block;padding:9px 20px;
       background:#1a3a5c;color:#fff;border-radius:4px;text-decoration:none;
       font-size:.95em;font-weight:bold">Browse Hadith Collections →</a>
  </div>
</section>"""

    # Insert before the last </main> tag
    if "</main>" in content:
        content = content.replace("</main>", hadith_section + "\n</main>", 1)
        with open(idx_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [html] docs/index.html — added Hadith section")
    else:
        print("  [warn] Could not find </main> in docs/index.html")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Hadith Generator")
    print("=" * 60)

    collection_counts = {}

    for coll in COLLECTIONS:
        cid = coll["id"]
        print(f"\n[{cid}] {coll['name_en']}")

        # 1. Load / download data
        data = load_or_download(cid)
        collection_counts[cid] = len(data["hadiths"])

        # 2. Text output
        write_text_outputs(coll, data)

        # 3. HTML pages
        if coll["large"]:
            gen_large_collection_pages(coll, data)
        else:
            gen_small_collection_page(coll, data)

    # 4. Hadith index page
    print("\n[index]")
    gen_index_page(collection_counts)

    # 5. Update Quran index
    print("\n[quran-index]")
    update_quran_index()

    total_hadiths = sum(collection_counts.values())
    print(f"\n{'='*60}")
    print(f"Done! Generated pages for {total_hadiths:,} hadith across {len(COLLECTIONS)} collections.")
    print(f"  docs/hadith/ — HTML pages")
    print(f"  output/hadith/ — plain-text files")
    print(f"  data/hadith/ — compressed JSON source data")
    print("=" * 60)


if __name__ == "__main__":
    main()
