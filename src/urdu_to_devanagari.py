#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Urdu (Nastaliq/Arabic script) to Devanagari transliteration module.

Converts Urdu text written in Arabic script into Devanagari script,
preserving Urdu phonetics using extended Devanagari characters for
Urdu-specific sounds (क़, ख़, ग़, ज़, फ़, etc.).

Usage:
    from urdu_to_devanagari import transliterate_urdu
    devanagari_text = transliterate_urdu("شروع الله کا نام")
"""

# ---------------------------------------------------------------------------
# Aspirated-consonant combinations: ب+ھ → भ, etc.
# Do-chashmi-he (ھ U+06BE) following a base consonant produces aspiration.
# ---------------------------------------------------------------------------
ASPIRATED = {
    'ب': 'भ',   # bh
    'پ': 'फ',   # ph
    'ت': 'थ',   # th
    'ٹ': 'ठ',   # ṭh
    'ج': 'झ',   # jh
    'چ': 'छ',   # ch
    'د': 'ध',   # dh
    'ڈ': 'ढ',   # ḍh
    'ر': 'रह',  # rh (no single Devanagari char)
    'ڑ': 'ढ़',  # ṛh
    'ک': 'ख',   # kh
    'گ': 'घ',   # gh
    'ل': 'लह',  # lh
    'م': 'मह',  # mh
    'ن': 'नह',  # nh
}

# ---------------------------------------------------------------------------
# Core consonant map: Urdu letter → Devanagari consonant (with inherent 'a').
# ---------------------------------------------------------------------------
CONSONANT_MAP = {
    'ب': 'ब',   # Ba
    'پ': 'प',   # Pa (Urdu-specific)
    'ت': 'त',   # Ta
    'ٹ': 'ट',   # Tta (retroflex)
    'ث': 'स',   # Tha (pronounced 's' in Urdu)
    'ج': 'ज',   # Jeem
    'چ': 'च',   # Cheh (Urdu-specific)
    'ح': 'ह',   # Hah (heavy h)
    'خ': 'ख़',  # Khah (extended Devanagari)
    'د': 'द',   # Dal
    'ڈ': 'ड',   # Ddal (retroflex)
    'ذ': 'ज़',  # Thal (pronounced 'z' in Urdu)
    'ر': 'र',   # Reh
    'ڑ': 'ड़',  # Rreh (retroflex)
    'ز': 'ज़',  # Zain
    'ژ': 'ज़',  # Jeh (pronounced 'z')
    'س': 'स',   # Seen
    'ش': 'श',   # Sheen
    'ص': 'स',   # Sad (pronounced 's' in Urdu)
    'ض': 'ज़',  # Dad (pronounced 'z' in Urdu)
    'ط': 'त',   # Tah (pronounced 't' in Urdu)
    'ظ': 'ज़',  # Zah (pronounced 'z' in Urdu)
    'ع': '',    # Ain (silent/vowel carrier; handled contextually)
    'غ': 'ग़',  # Ghain (extended Devanagari)
    'ف': 'फ़',  # Feh (extended Devanagari)
    'ق': 'क़',  # Qaf (extended Devanagari)
    'ک': 'क',   # Keheh (Urdu Ka)
    'گ': 'ग',   # Gaf (Urdu-specific)
    'ل': 'ल',   # Lam
    'م': 'म',   # Meem
    'ن': 'न',   # Noon
    'ں': 'ं',   # Noon Ghunna → anusvara
    'ہ': 'ह',   # Heh Goal (Urdu Ha)
    'ه': 'ह',   # Heh (Arabic Ha)
    'ة': 'त',   # Teh Marbuta
    'ھ': 'ह',   # Do Chashmi He (aspiration; handled in pairs above)
    'و': 'व',   # Waw (consonantal; vocalic handled separately)
    'ي': 'य',   # Yeh (Arabic)
    'ی': 'य',   # Farsi Yeh (Urdu Ya)
    'ے': 'ए',   # Yeh Barree (final long 'e')
    'ء': '',    # Hamza (silent)
    'ؤ': 'व',   # Waw with hamza
    'ئ': 'य',   # Yeh with hamza
}

# Independent (standalone) vowel forms used at the start of a word or after
# a vowel carrier (ا، ع، ء).
INDEPENDENT_VOWELS = {
    'ا': 'अ',   # Alef → 'a'
    'آ': 'आ',   # Alef Madda → 'aa'
}

# Vowel matras (dependent forms) that attach to the preceding consonant.
# After a consonant these replace the inherent 'a'.
VOWEL_MATRA = {
    'ا': 'ा',   # long 'aa' matra
    'آ': 'ा',   # Alef Madda → long 'aa' matra
    'ِ': 'ि',   # Kasra (short 'i')
    'َ': 'ा',   # Fatha (short 'a') → represented as long aa for clarity
    'ُ': 'ु',   # Damma (short 'u')
    'ً': 'ं',   # Fathatan → anusvara
    'ٌ': 'ं',   # Dammatan → anusvara
    'ٍ': 'ं',   # Kasratan → anusvara
    'ٰ': 'ा',   # Superscript Alef → long 'aa'
}

# Characters to silently drop (not rendered).
DROP_CHARS = {
    '\u0653',  # Maddah above (ٓ) — contextually part of آ
    '\u0651',  # Shadda (ّ) — gemination; not rendered separately
    '\u0670',  # Superscript Alef handled via VOWEL_MATRA above
    '\u0654',  # Hamza above
    '\u0655',  # Hamza below
    '\u0674',  # High Hamza (ٴ)
}

# Punctuation replacements.
PUNCT_MAP = {
    '،': ',',   # Arabic comma
    '؟': '?',   # Arabic question mark
    '۔': '।',   # Arabic full stop → Devanagari danda
    '\u00a0': ' ',  # Non-breaking space → regular space
}

# Special symbols that should be preserved verbatim.
PRESERVE = {
    '\ufdfa',  # ﷺ Arabic ligature Sallallahou Alayhe Wasallam
    '\u0611',  # ؑ Arabic Sign Alayhe Assallam
    '\u0613',  # ؓ Arabic Sign Radi Allahou Anhu
}


def transliterate_word(word):
    """Transliterate a single Urdu word to Devanagari."""
    result = []
    i = 0
    n = len(word)
    prev_was_consonant = False

    while i < n:
        ch = word[i]

        # --- Preserve special symbols verbatim ---
        if ch in PRESERVE:
            result.append(ch)
            prev_was_consonant = False
            i += 1
            continue

        # --- Silent / drop characters ---
        if ch in DROP_CHARS:
            i += 1
            continue

        # --- Punctuation ---
        if ch in PUNCT_MAP:
            result.append(PUNCT_MAP[ch])
            prev_was_consonant = False
            i += 1
            continue

        # --- Do-Chashmi-He: aspirated consonant pair ---
        if ch == 'ھ':
            # If previous output ended with a consonant char, merge into aspiration
            if result and result[-1] in ASPIRATED.values():
                # Already merged via look-ahead; shouldn't normally hit here.
                pass
            # Check look-behind via prev character in source
            if i > 0 and word[i - 1] in ASPIRATED:
                # Replace the last emitted consonant with its aspirated form
                # We need to find and replace the last appended consonant.
                base = word[i - 1]
                aspirated = ASPIRATED[base]
                # Walk back through result to replace the base consonant.
                base_deva = CONSONANT_MAP.get(base, '')
                if base_deva and result:
                    # Remove the last occurrence of base_deva at the end
                    joined = ''.join(result)
                    if joined.endswith(base_deva):
                        result = list(joined[: -len(base_deva)])
                        result.append(aspirated)
                    else:
                        result.append(CONSONANT_MAP['ھ'])
                else:
                    result.append(CONSONANT_MAP['ھ'])
            else:
                result.append(CONSONANT_MAP['ھ'])
            prev_was_consonant = True
            i += 1
            continue

        # --- Alef Madda (آ) ---
        if ch == 'آ':
            if prev_was_consonant:
                result.append('ा')
            else:
                result.append('आ')
            prev_was_consonant = False
            i += 1
            continue

        # --- Plain Alef (ا) ---
        if ch == 'ا':
            if prev_was_consonant:
                result.append('ा')
            else:
                result.append('अ')
            prev_was_consonant = False
            i += 1
            continue

        # --- Ain (ع) — silent/vowel carrier ---
        if ch == 'ع':
            if not prev_was_consonant:
                result.append('अ')
            # else: silent (vowel will come from next char)
            prev_was_consonant = False
            i += 1
            continue

        # --- Hamza variants (ء، ؤ handled as consonants below) ---
        if ch == 'ء':
            # Silent
            prev_was_consonant = False
            i += 1
            continue

        # --- Waw (و) — consonant 'v' or long vowel 'oo'/'o' ---
        if ch == 'و':
            if prev_was_consonant:
                # After a consonant, و is typically the long 'u'/'o' vowel
                result.append('ो')
                prev_was_consonant = False
            else:
                result.append('व')
                prev_was_consonant = True   # 'व' is a consonant
            i += 1
            continue

        # --- Farsi/Arabic Yeh (ی/ي) — consonant 'y' or long vowel 'ee'/'i' ---
        if ch in ('ی', 'ي'):
            if prev_was_consonant:
                result.append('ी')
                prev_was_consonant = False
            else:
                result.append('य')
                prev_was_consonant = True   # 'य' is a consonant
            i += 1
            continue

        # --- Yeh Barree (ے) — final long 'e' ---
        if ch == 'ے':
            if prev_was_consonant:
                result.append('े')
            else:
                result.append('ए')
            prev_was_consonant = False
            i += 1
            continue

        # --- Noon Ghunna (ں) — anusvara ---
        if ch == 'ں':
            result.append('ं')
            prev_was_consonant = False
            i += 1
            continue

        # --- Vowel diacritics ---
        if ch in VOWEL_MATRA:
            if prev_was_consonant:
                result.append(VOWEL_MATRA[ch])
            prev_was_consonant = False
            i += 1
            continue

        # --- Regular consonants ---
        if ch in CONSONANT_MAP:
            deva = CONSONANT_MAP[ch]
            result.append(deva)
            prev_was_consonant = bool(deva)
            i += 1
            continue

        # --- Pass through everything else (ASCII, digits, etc.) ---
        result.append(ch)
        prev_was_consonant = False
        i += 1

    return ''.join(result)


def transliterate_urdu(text):
    """Transliterate an entire Urdu text string to Devanagari.

    Preserves spaces, newlines, digits, ASCII punctuation, and Surah/Ayah
    markers exactly.  Only Urdu Arabic-script letters are converted.

    Args:
        text: A string in Urdu (Arabic-Nastaliq script).

    Returns:
        A string in Devanagari script with Urdu phonetics.
    """
    # Split on whitespace tokens but preserve the delimiters so we can
    # reconstruct the original spacing perfectly.
    import re
    # Tokenise: split into (non-space runs) and (space/newline runs).
    tokens = re.split(r'(\s+)', text)
    out = []
    for token in tokens:
        if not token:
            continue
        if token.isspace():
            out.append(token)
        else:
            out.append(transliterate_word(token))
    return ''.join(out)
