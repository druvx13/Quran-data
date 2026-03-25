#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the LaTeX content file for the professional A5 Khattab book PDF.

Reads:
    data/en.khattab.txt — English translation (one verse per line)

Writes:
    latex/khattab_book_content.tex — body content for khattab_book.tex

English-only output: no Arabic script, no transliteration.
"""
import os
import re

os.makedirs('latex', exist_ok=True)

# --------------------------------------------------------------------------- #
# Surah metadata                                                               #
# --------------------------------------------------------------------------- #
SURA_SIZES = [
    7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,
    135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,
    54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,
    18,12,12,30,52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,
    19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6,
]

# Short transliterated name + English meaning for chapter headings
SURA_INFO = [
    ("Al-Fātiḥah",     "The Opening"),
    ("Al-Baqarah",     "The Cow"),
    ("Āl-ʿImrān",      "The Family of Imrān"),
    ("An-Nisāʾ",       "The Women"),
    ("Al-Māʾidah",     "The Spread Table"),
    ("Al-Anʿām",       "The Cattle"),
    ("Al-Aʿrāf",       "The Heights"),
    ("Al-Anfāl",       "The Spoils of War"),
    ("At-Tawbah",      "The Repentance"),
    ("Yūnus",          "Jonah"),
    ("Hūd",            "Hud"),
    ("Yūsuf",          "Joseph"),
    ("Ar-Raʿd",        "The Thunder"),
    ("Ibrāhīm",        "Abraham"),
    ("Al-Ḥijr",        "The Rocky Highlands"),
    ("An-Naḥl",        "The Bees"),
    ("Al-Isrāʾ",       "The Night Journey"),
    ("Al-Kahf",        "The Cave"),
    ("Maryam",         "Mary"),
    ("Ṭā Hā",          "Ṭā Hā"),
    ("Al-Anbiyāʾ",     "The Prophets"),
    ("Al-Ḥajj",        "The Pilgrimage"),
    ("Al-Muʾminūn",    "The Believers"),
    ("An-Nūr",         "The Light"),
    ("Al-Furqān",      "The Standard"),
    ("Ash-Shuʿarāʾ",  "The Poets"),
    ("An-Naml",        "The Ants"),
    ("Al-Qaṣaṣ",       "The Narration"),
    ("Al-ʿAnkabūt",   "The Spider"),
    ("Ar-Rūm",         "The Romans"),
    ("Luqmān",         "Luqmān"),
    ("As-Sajdah",      "The Prostration"),
    ("Al-Aḥzāb",       "The Combined Forces"),
    ("Sabaʾ",          "Sheba"),
    ("Fāṭir",          "The Originator"),
    ("Yā Sīn",         "Yā Sīn"),
    ("Aṣ-Ṣāffāt",     "Those Lined Up in Ranks"),
    ("Ṣād",            "Ṣād"),
    ("Az-Zumar",       "The Groups"),
    ("Ghāfir",         "The Forgiver"),
    ("Fuṣṣilat",       "Clearly Spelled Out"),
    ("Ash-Shūrā",      "The Consultation"),
    ("Az-Zukhruf",     "The Gold Ornaments"),
    ("Ad-Dukhān",      "The Haze"),
    ("Al-Jāthiyah",    "The Kneeling"),
    ("Al-Aḥqāf",       "The Sand Dunes"),
    ("Muḥammad",       "Muḥammad"),
    ("Al-Fatḥ",        "The Triumph"),
    ("Al-Ḥujurāt",     "The Private Quarters"),
    ("Qāf",            "Qāf"),
    ("Adh-Dhāriyāt",  "The Scattering Winds"),
    ("Aṭ-Ṭūr",         "The Mount"),
    ("An-Najm",        "The Stars"),
    ("Al-Qamar",       "The Moon"),
    ("Ar-Raḥmān",      "The Most Compassionate"),
    ("Al-Wāqiʿah",    "The Inevitable Event"),
    ("Al-Ḥadīd",       "Iron"),
    ("Al-Mujādilah",   "The Plea"),
    ("Al-Ḥashr",       "The Gathering"),
    ("Al-Mumtaḥanah",  "The Examined Woman"),
    ("Aṣ-Ṣaff",        "The Ranks"),
    ("Al-Jumuʿah",     "Friday"),
    ("Al-Munāfiqūn",   "The Hypocrites"),
    ("At-Taghābun",    "The Mutual Loss and Gain"),
    ("Aṭ-Ṭalāq",       "Divorce"),
    ("At-Taḥrīm",      "The Prohibition"),
    ("Al-Mulk",        "The Sovereignty"),
    ("Al-Qalam",       "The Pen"),
    ("Al-Ḥāqqah",      "The Inevitable Hour"),
    ("Al-Maʿārij",     "The Ascending Stairways"),
    ("Nūḥ",            "Noah"),
    ("Al-Jinn",        "The Jinn"),
    ("Al-Muzzammil",   "The Wrapped One"),
    ("Al-Muddaththir", "The Covered One"),
    ("Al-Qiyāmah",     "The Resurrection"),
    ("Al-Insān",       "Humanity"),
    ("Al-Mursalāt",    "Those Sent Forth"),
    ("An-Nabaʾ",       "The Momentous News"),
    ("An-Nāziʿāt",    "Those who Pull Out"),
    ("ʿAbasa",         "He Frowned"),
    ("At-Takwīr",      "The Folding Up"),
    ("Al-Infiṭār",     "The Splitting Apart"),
    ("Al-Muṭaffifīn",  "The Defrauders"),
    ("Al-Inshiqāq",    "The Splitting Open"),
    ("Al-Burūj",       "The Constellations"),
    ("Aṭ-Ṭāriq",       "The Nightly Star"),
    ("Al-Aʿlā",        "The Most High"),
    ("Al-Ghāshiyah",   "The Overwhelming Event"),
    ("Al-Fajr",        "The Dawn"),
    ("Al-Balad",       "The City"),
    ("Ash-Shams",      "The Sun"),
    ("Al-Layl",        "The Night"),
    ("Aḍ-Ḍuḥā",        "The Morning Brightness"),
    ("Ash-Sharḥ",      "The Relief"),
    ("At-Tīn",         "The Fig"),
    ("Al-ʿAlaq",       "The Clot"),
    ("Al-Qadr",        "The Night of Glory"),
    ("Al-Bayyinah",    "The Clear Proof"),
    ("Az-Zalzalah",    "The Earthquake"),
    ("Al-ʿĀdiyāt",    "The Galloping Horses"),
    ("Al-Qāriʿah",    "The Striking Calamity"),
    ("At-Takāthur",   "The Rivalry for Worldly Gain"),
    ("Al-ʿAṣr",       "The Time"),
    ("Al-Humazah",     "The Backbiter"),
    ("Al-Fīl",         "The Elephant"),
    ("Quraysh",        "Quraysh"),
    ("Al-Māʿūn",       "The Common Necessities"),
    ("Al-Kawthar",     "Abundance"),
    ("Al-Kāfirūn",    "The Disbelievers"),
    ("An-Naṣr",        "The Divine Support"),
    ("Al-Masad",       "The Palm Fibre"),
    ("Al-Ikhlāṣ",      "Sincerity of Faith"),
    ("Al-Falaq",       "The Daybreak"),
    ("An-Nās",         "Humanity"),
]

assert len(SURA_INFO) == 114, "SURA_INFO must have exactly 114 entries"
assert len(SURA_SIZES) == 114, "SURA_SIZES must have exactly 114 entries"


# --------------------------------------------------------------------------- #
# LaTeX escaping                                                               #
# --------------------------------------------------------------------------- #
_ESCAPE_MAP = str.maketrans({
    '\\': r'\textbackslash{}',
    '&':  r'\&',
    '%':  r'\%',
    '$':  r'\$',
    '#':  r'\#',
    '_':  r'\_',
    '{':  r'\{',
    '}':  r'\}',
    '~':  r'\textasciitilde{}',
    '^':  r'\textasciicircum{}',
    '\xa0': ' ',        # non-breaking space
})


def tex_escape(text: str) -> str:
    """Escape LaTeX special characters while preserving Unicode."""
    return text.translate(_ESCAPE_MAP)


# --------------------------------------------------------------------------- #
# Content generation                                                           #
# --------------------------------------------------------------------------- #
out_path = 'latex/khattab_book_content.tex'
with open(out_path, 'w', encoding='utf-8') as out, \
        open('data/en.khattab.txt', 'r', encoding='utf-8') as khattab_in:

    for sura_idx in range(114):
        arabic_name, english_name = SURA_INFO[sura_idx]
        sura_num   = sura_idx + 1
        verse_count = SURA_SIZES[sura_idx]

        # Short name for TOC entry and running header
        toc_entry = "%d. %s" % (sura_num, arabic_name)

        # Full chapter heading (displayed in PDF)
        out.write(
            "\\surahchapter[%s]{%d}{%s}{%s}{%d}\n"
            % (toc_entry, sura_num, tex_escape(arabic_name),
               tex_escape(english_name), verse_count)
        )

        for ayah_num in range(1, verse_count + 1):
            verse_text = tex_escape(khattab_in.readline().rstrip('\n'))
            out.write("\\vn{%d}%s\n\n" % (ayah_num, verse_text))

print("Written:", out_path)
