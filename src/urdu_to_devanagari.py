#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Urdu (Nastaliq/Arabic script) to Devanagari transliteration.

Design principles
─────────────────
• No automatic virama is inserted between consecutive consonants.
  In Urdu (without harakat), the Devanagari inherent-'a' vowel is assumed
  between every pair of adjacent consonants.
  Virama is only added for an *explicit* sukun ( ْ ) in the source.
• و  is treated as vowel 'ो' when it follows a consonant, and as
  consonant 'व' when it begins a word (consonant_pending = False).
• ی  is treated as vowel 'ी' when it follows a consonant, and as
  consonant 'य' at word start.
• ے  is always the end-of-word 'े' matra.
• ا / آ  → 'अ'/'आ' standalone; 'ा' after a consonant.
• ع  is always a glottal/vowel carrier → अ.
• Word-level substitutions handle the most common lexical items.

Run from the repository root:
    python3 src/urdu_to_devanagari.py
"""
import re

# ─────────────────────────────────────────────────────────────────────────────
# Aspirated two-character combinations  (consonant + do-chashmi-he U+06BE)
# Processed FIRST, before single-character lookup.
# ─────────────────────────────────────────────────────────────────────────────
ASPIRATED = {
    'بھ': 'भ',    # ba + he  → bha
    'پھ': 'फ',    # pa + he  → pha
    'تھ': 'थ',    # ta + he  → tha
    'ٹھ': 'ठ',    # tta + he → ttha
    'جھ': 'झ',    # ja + he  → jha
    'چھ': 'छ',    # cha + he → chha
    'دھ': 'ध',    # da + he  → dha
    'ڈھ': 'ढ',    # dda + he → ddha
    'ڑھ': 'ढ़',   # rra + he → rrha
    'کھ': 'ख',    # ka + he  → kha
    'گھ': 'घ',    # ga + he  → gha
    'لھ': 'ल्ह',  # la + he
    'مھ': 'म्ह',  # ma + he
    'نھ': 'न्ह',  # na + he
    'رھ': 'र्ह',  # ra + he
}

# ─────────────────────────────────────────────────────────────────────────────
# Single-character consonant map
# ─────────────────────────────────────────────────────────────────────────────
CMAP = {
    # ── core consonants ────────────────────────────────────────────────────
    'ب': 'ब',    # U+0628  ba
    'پ': 'प',    # U+067E  pa   (Urdu)
    'ت': 'त',    # U+062A  ta
    'ٹ': 'ट',    # U+0679  tta  (Urdu)
    'ث': 'स',    # U+062B  sa   (tha)
    'ج': 'ज',    # U+062C  ja
    'چ': 'च',    # U+0686  cha  (Urdu)
    'ح': 'ह',    # U+062D  ha
    'خ': 'ख़',   # U+062E  kha
    'د': 'द',    # U+062F  da
    'ڈ': 'ड',    # U+0688  dda  (Urdu)
    'ذ': 'ज़',   # U+0630  za   (zal)
    'ر': 'र',    # U+0631  ra
    'ڑ': 'ड़',   # U+0691  rra  (Urdu)
    'ز': 'ज़',   # U+0632  za
    'ژ': 'झ',    # U+0698  zha
    'س': 'स',    # U+0633  sa   (sin)
    'ش': 'श',    # U+0634  sha  (shin)
    'ص': 'स',    # U+0635  sa   (swad)
    'ض': 'ज़',   # U+0636  za   (zwad)
    'ط': 'त',    # U+0637  ta   (toe)
    'ظ': 'ज़',   # U+0638  za   (zoe)
    'ع': 'अ',    # U+0639  ain  → vowel carrier 'a'
    'غ': 'ग़',   # U+063A  ghain
    'ف': 'फ़',   # U+0641  fa
    'ق': 'क़',   # U+0642  qa   (qaf)
    'ک': 'क',    # U+06A9  ka   (Urdu kaf)
    'گ': 'ग',    # U+06AF  ga   (Urdu)
    'ل': 'ल',    # U+0644  la
    'م': 'म',    # U+0645  ma
    'ن': 'न',    # U+0646  na
    # ── he / h sounds ──────────────────────────────────────────────────────
    'ہ': 'ह',    # U+06C1  he  (Urdu)
    'ه': 'ह',    # U+0647  he  (Arabic)
    'ة': 'त',    # U+0629  ta-marbuta
    # ── waw / ya as consonants (default; overridden in context) ────────────
    'و': 'व',    # U+0648  waw  → ो after consonant
    'ی': 'य',    # U+06CC  ye   → ी after consonant
    'ي': 'य',    # U+064A  ye   (Arabic)
    'ئ': 'य',    # U+0626  ye-hamza
    'ؤ': 'व',    # U+0624  waw-hamza
}

# Diacritics that carry an explicit vowel → output matra; sukun → virama
VOWEL_DIACRITICS = {
    '\u064E': 'ा',   # fatha
    '\u064F': 'ु',   # dhamma  (u)
    '\u0650': 'ि',   # kasra   (i)
    '\u064B': 'ं',   # tanwin fatha
    '\u064C': 'ं',   # tanwin dhamma
    '\u064D': 'ं',   # tanwin kasra
    '\u0652': '्',   # sukun   (explicit virama)
    '\u0653': 'ा',   # madda above
    '\u0670': 'ा',   # superscript alef (khari zabar)
}

# Diacritics to skip silently
SKIP_DIACRITICS = frozenset('\u0651\u0674')   # shadda, hamza-above

# Arabic-Indic → Devanagari numeral translation
ARABIC_NUMERALS = str.maketrans('٠١٢٣٤٥٦٧٨٩', '०१२३४५६७८९')

# ─────────────────────────────────────────────────────────────────────────────
# Word-boundary regex helpers
# ─────────────────────────────────────────────────────────────────────────────
# A "word boundary" character for Arabic/Urdu text: whitespace or common
# punctuation (both ASCII and Arabic/Urdu).
_WB = r'[\s()\[\]{},،.!؟۔।"\'،]'

def _word_sub(text: str, urdu: str, deva: str) -> str:
    """Replace *urdu* with *deva* only when *urdu* is a standalone word.

    Uses look-behind / look-ahead for word-boundary characters so that
    e.g. ہیں inside رہیں is not disturbed.
    """
    esc = re.escape(urdu)
    # Case 1: preceded by a boundary char (lookbehind for exactly 1 char)
    pat_mid = r'(?<=' + _WB + r')' + esc + r'(?=' + _WB + r'|$)'
    text = re.sub(pat_mid, deva, text, flags=re.MULTILINE)
    # Case 2: at the very start of the string / line
    pat_sol = r'^' + esc + r'(?=' + _WB + r'|$)'
    text = re.sub(pat_sol, deva, text, flags=re.MULTILINE)
    return text


# ─────────────────────────────────────────────────────────────────────────────
# Word-level substitutions
# Applied BEFORE character-level processing.
# All replacements use _word_sub() so partial matches inside longer words
# are never affected.  Order longest-first as extra safety.
# ─────────────────────────────────────────────────────────────────────────────
WORD_SUBS = [
    # ── Allah ─────────────────────────────────────────────────────────────
    ('الله',     'अल्लाह'),    # Arabic he form  (63 occ.)
    ('اللہ',     'अल्लाह'),    # Urdu he form

    # ── 8-char ────────────────────────────────────────────────────────────
    ('پروردگار', 'परवरदगार'),   # Parwardigār – Sustainer  (866x)

    # ── 6-char ────────────────────────────────────────────────────────────
    ('تمہارے',   'तुम्हारे'),   # tumhāre – your (m.pl.)  (755x)
    ('تمہاری',   'तुम्हारी'),   # tumhārī – your (f.)     (243x)

    # ── 5-char ────────────────────────────────────────────────────────────
    ('تمہارا',   'तुम्हारा'),   # tumhārā – your (m.sg.)  (262x)
    ('تمہیں',    'तुम्हें'),    # tumheṃ – to you (hon.)  (236x)
    ('انہیں',    'उन्हें'),     # unheṃ – to them         (106x)
    ('جنہیں',    'जिन्हें'),    # jinheṃ – whom           (3x)
    ('ایمان',    'ईमान'),       # īmān – faith            (510x)
    ('قیامت',    'क़ियामत'),    # qiyāmat – Judgement Day (180x)
    ('عبادت',    'इबादत'),      # ibādat – worship        (119x)
    ('ہوئیں',    'हुईं'),       # hū'īṃ – were (f.pl.)   (12x)
    ('جنہوں',    'जिन्हों'),    # jinhõ – those who (pl.) (74x)
    ('اُنہیں',   'उन्हें'),     # unheṃ alt. form         (1x)

    # ── 4-char ────────────────────────────────────────────────────────────
    ('نہیں',     'नहीं'),       # nahīṃ – not/no          (1861x)
    ('ہمیں',     'हमें'),       # hameṃ – to us           (126x)
    ('ہوئے',     'हुए'),        # hū'e  – happened (m.pl.)(248x)
    ('ہوئی',     'हुई'),        # hū'ī  – happened (f.)  (127x)
    ('مجھے',     'मुझे'),       # mujhe – to me           (215x)
    ('دنیا',     'दुनिया'),     # dunyā – world           (176x)
    ('آخرت',     'आख़िरत'),    # ākhirat – Hereafter     (137x)
    ('قرآن',     'क़ुरआन'),    # Qur'ān                  (131x)
    ('رسول',     'रसूल'),       # rasūl – Messenger       (101x)
    ('جہنم',     'जहन्नम'),     # jahannam – Hellfire     (49x)
    ('تیری',     'तेरी'),       # terī – your (f.)        (33x)
    ('شروع',     'शुरू'),       # shurū' – beginning      (12x)
    ('نعمت',     'नेमत'),       # ne'mat – blessing       (107x)
    ('انسان',    'इंसान'),      # insān – human           (109x)
    ('تعریف',    'तारीफ़'),     # ta'rīf – praise         (35x)
    ('جنت',      'जन्नत'),      # jannat – Paradise       (21x)
    ('انصاف',    'इंसाफ़'),     # insāf  – justice        (75x)
    ('محمد',     'मुहम्मद'),    # Muḥammad                (94x)
    ('تیار',     'तैयार'),      # taiyār – ready/prepared (143x)
    ('دلوں',     'दिलों'),      # dilõ   – hearts (pl.)  (108x)

    # ── 3-char ────────────────────────────────────────────────────────────
    ('ہیں',      'हैं'),        # haiṃ – are              (2608x)
    ('میں',      'में'),        # mẽ   – in               (3999x)
    ('اور',      'और'),         # aur  – and              (10248x)
    ('کیا',      'किया'),       # kiyā – did/what         (1289x)
    ('کیے',      'किए'),        # kiye – did (pl.)        (33x)
    ('کیوں',     'क्यों'),      # kyõ  – why              (142x)
    ('لیے',      'लिए'),        # liye – for              (363x)
    ('لیا',      'लिया'),       # liyā – took
    ('دیا',      'दिया'),       # diyā – gave
    ('گیا',      'गया'),        # gayā – went (m.)
    ('ہوا',      'हुआ'),        # huā  – happened         (252x)
    ('تجھ',      'तुझ'),        # tujh – you (obj.infml.) (53x)
    ('اسے',      'उसे'),        # use  – him/it/her       (268x)
    ('خدا',      'ख़ुदा'),      # Khudā – God             (3175x)
    ('موت',      'मौत'),        # maut  – death           (69x)
    ('مجھ',      'मुझ'),        # mujh  – me (direct)     (514x)
    ('اَے',      'ए'),          # ae    – O (vocative, with fatha)
    ('اے',       'ए'),          # ae    – O (vocative)

    # ── 2-char ────────────────────────────────────────────────────────────
    ('دل',       'दिल'),        # dil   – heart           (588x)
    ('ہے',       'है'),         # hai   – is/am/are       (4273x)
]


# ─────────────────────────────────────────────────────────────────────────────
# Core transliteration function
# ─────────────────────────────────────────────────────────────────────────────
def transliterate_urdu_to_devanagari(text: str) -> str:
    """Transliterate a string of Urdu text (Arabic script) to Devanagari."""

    # ── 1. word-level substitutions (word-boundary-safe) ──────────────────
    for urdu_word, deva_word in WORD_SUBS:
        text = _word_sub(text, urdu_word, deva_word)

    n = len(text)
    out: list[str] = []
    i = 0
    # True when last output was a Devanagari consonant (inherent 'a' open).
    consonant_pending = False

    while i < n:
        c = text[i]

        # ── ﷺ  keep as-is ────────────────────────────────────────────────
        if c == '\uFDFA':
            out.append(c)
            consonant_pending = False
            i += 1
            continue

        # ── Devanagari already inserted by word_subs – pass through ───────
        if '\u0900' <= c <= '\u097F':
            out.append(c)
            consonant_pending = ('\u0915' <= c <= '\u0939')
            i += 1
            continue

        # ── two-character aspirated combos ─────────────────────────────────
        two = text[i: i + 2]
        if two in ASPIRATED:
            out.append(ASPIRATED[two])
            i += 2
            consonant_pending = True
            if i < n and text[i] in VOWEL_DIACRITICS:
                out.append(VOWEL_DIACRITICS[text[i]])
                consonant_pending = (VOWEL_DIACRITICS[text[i]] == '्')
                i += 1
            continue

        # ── ا  alef ────────────────────────────────────────────────────────
        if c == '\u0627':
            out.append('ा' if consonant_pending else 'अ')
            consonant_pending = False
            i += 1
            continue

        # ── آ  alef-madda ──────────────────────────────────────────────────
        if c == '\u0622':
            out.append('ा' if consonant_pending else 'आ')
            consonant_pending = False
            i += 1
            continue

        # ── ں  noon-ghunna ─────────────────────────────────────────────────
        if c == '\u06BA':
            out.append('ं')
            consonant_pending = False
            i += 1
            continue

        # ── ے  bariye ─────────────────────────────────────────────────────
        if c == '\u06D2':
            out.append('े')
            consonant_pending = False
            i += 1
            continue

        # ── و  waw ────────────────────────────────────────────────────────
        if c == '\u0648':
            if consonant_pending:
                out.append('ो')
                consonant_pending = False
            else:
                out.append('व')
                consonant_pending = True
                if i + 1 < n and text[i + 1] in VOWEL_DIACRITICS:
                    i += 1
                    out.append(VOWEL_DIACRITICS[text[i]])
                    consonant_pending = (VOWEL_DIACRITICS[text[i]] == '्')
            i += 1
            continue

        # ── ی  ye ─────────────────────────────────────────────────────────
        if c == '\u06CC':
            if consonant_pending:
                out.append('ी')
                consonant_pending = False
            else:
                out.append('य')
                consonant_pending = True
                if i + 1 < n and text[i + 1] in VOWEL_DIACRITICS:
                    i += 1
                    out.append(VOWEL_DIACRITICS[text[i]])
                    consonant_pending = (VOWEL_DIACRITICS[text[i]] == '्')
            i += 1
            continue

        # ── Arabic ye ي ────────────────────────────────────────────────────
        if c == '\u064A':
            out.append('ी' if consonant_pending else 'य')
            consonant_pending = False
            i += 1
            continue

        # ── ع  ain ────────────────────────────────────────────────────────
        if c == '\u0639':
            out.append('अ')
            consonant_pending = False
            i += 1
            continue

        # ── ء  hamza ──────────────────────────────────────────────────────
        if c == '\u0621':
            if i + 1 < n and text[i + 1] in VOWEL_DIACRITICS:
                i += 1
                out.append(VOWEL_DIACRITICS[text[i]])
                consonant_pending = False
            i += 1
            continue

        # ── vowel diacritics ───────────────────────────────────────────────
        if c in VOWEL_DIACRITICS:
            out.append(VOWEL_DIACRITICS[c])
            consonant_pending = (VOWEL_DIACRITICS[c] == '्')
            i += 1
            continue

        # ── shadda ّ ───────────────────────────────────────────────────────
        if c == '\u0651':
            if out and consonant_pending:
                last = out[-1]
                out.append('्')
                out.append(last)
            i += 1
            continue

        # ── other skip-diacritics ──────────────────────────────────────────
        if c in SKIP_DIACRITICS:
            i += 1
            continue

        # ── consonants (CMAP) ──────────────────────────────────────────────
        if c in CMAP:
            out.append(CMAP[c])
            i += 1
            consonant_pending = True
            if i < n and text[i] in VOWEL_DIACRITICS:
                d = text[i]
                out.append(VOWEL_DIACRITICS[d])
                consonant_pending = (VOWEL_DIACRITICS[d] == '्')
                i += 1
                if i < n and text[i] == '\u0651':
                    i += 1
            continue

        # ── non-breaking space → regular space ─────────────────────────────
        if c == '\u00A0':
            out.append(' ')
            consonant_pending = False
            i += 1
            continue

        # ── punctuation ────────────────────────────────────────────────────
        if c == '\u060C':     # ،
            out.append(',')
            consonant_pending = False
            i += 1
            continue
        if c == '\u061F':     # ؟
            out.append('?')
            consonant_pending = False
            i += 1
            continue
        if c == '\u06D4':     # ۔
            out.append('।')
            consonant_pending = False
            i += 1
            continue

        # ── Arabic-Indic numerals → Devanagari ────────────────────────────
        if '\u0660' <= c <= '\u0669':
            out.append(c.translate(ARABIC_NUMERALS))
            consonant_pending = False
            i += 1
            continue

        # ── honorific signs – keep as-is ──────────────────────────────────
        if c in ('\u0611', '\u0613'):
            out.append(c)
            consonant_pending = False
            i += 1
            continue

        # ── everything else ────────────────────────────────────────────────
        out.append(c)
        consonant_pending = False
        i += 1

    return ''.join(out)


# ─────────────────────────────────────────────────────────────────────────────
# Line-level processing
# ─────────────────────────────────────────────────────────────────────────────
def _process_line(line: str) -> str:
    if (line.startswith('Quran')
            or line.startswith('Mutarjim')
            or line.startswith('===')
            or line.startswith('---')
            or line.startswith('Surah')
            or line.strip() == ''):
        return line

    if line.startswith('['):
        bracket_end = line.index(']')
        marker = line[:bracket_end + 2]        # "[N:M] "
        urdu_text = line[bracket_end + 2:]     # content + newline
        return marker + transliterate_urdu_to_devanagari(urdu_text)

    return transliterate_urdu_to_devanagari(line)


# ─────────────────────────────────────────────────────────────────────────────
# Public file-level API  (used by gentxtforquran.py)
# ─────────────────────────────────────────────────────────────────────────────
def transliterate_file(input_path: str, output_path: str) -> None:
    with open(input_path, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()

    with open(output_path, 'w', encoding='utf-8') as fh:
        fh.write('Quran - Urdu Tarjuma (Devanagari Lipi)\n')
        fh.write('Mutarjim: Fateh Muhammad Jalandhry\n')
        fh.write('=' * 60 + '\n')
        fh.write('\n')
        for line in lines[4:]:
            fh.write(_process_line(line))


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import os
    src = os.path.join('output', 'quran_urdu_jalandhry.txt')
    dst = os.path.join('output', 'quran_urdu_devanagari_jalandhry.txt')
    transliterate_file(src, dst)
    print(f'Generated: {dst}')
