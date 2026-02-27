#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Urdu (Arabic/Nastaliq script)  →  Devanagari transliteration engine.

Rules applied for unvowelised Urdu text:
  Consonant + ا (alif)    → ā vowel sign (ा)
  Consonant + و (waw)     → o vowel sign (ो)  [unless وا → consonant व + ā]
  Consonant + ی (ya)      → ī vowel sign (ी)
  Consonant + ے (bari ya) → e vowel sign (े)
  Consonant + یٰ          → ā vowel sign (ा)   (e.g. موسیٰ)
  Word-initial ا + ے/ی/و → ए / ई / औ  (diphthongs)
  Word-initial و          → consonant व
  Word-initial ی          → consonant य
  ی after vowel sign      → consonant य
  ں (noon ghunna)         → anusvara ं
  Identical adjacent consonants → halant between them (gemination)
  Harakat diacritics      → matching Devanagari vowel signs
"""

import re

# ---------------------------------------------------------------------------
# Aspiration digraphs:  C + ھ (do-chashmi-he)  →  Devanagari aspirated C
# ---------------------------------------------------------------------------
ASPIRATED = {
    'بھ': 'भ',   'پھ': 'फ',   'تھ': 'थ',   'ٹھ': 'ठ',
    'جھ': 'झ',   'چھ': 'छ',   'دھ': 'ध',   'ڈھ': 'ढ',
    'کھ': 'ख',   'گھ': 'घ',   'لھ': 'ल्ह', 'نھ': 'न्ह',
    'رھ': 'र्ह', 'مھ': 'म्ह',
}

# ---------------------------------------------------------------------------
# Single-letter consonant map
# ---------------------------------------------------------------------------
CONSONANT_MAP = {
    # Standard Arabic
    'ب': 'ब',   'ت': 'त',   'ث': 'स',   'ج': 'ज',
    'ح': 'ह',   'خ': 'ख़',  'د': 'द',   'ذ': 'ज़',
    'ر': 'र',   'ز': 'ज़',  'س': 'स',   'ش': 'श',
    'ص': 'स',   'ض': 'ज़',  'ط': 'त',   'ظ': 'ज़',
    'غ': 'ग़',  'ف': 'फ़',  'ق': 'क़',  'ل': 'ल',
    'م': 'म',   'ن': 'न',   'ه': 'ह',   'ة': 'त',
    'ي': 'य',
    # Urdu-specific
    'پ': 'प',   'ٹ': 'ट',   'چ': 'च',   'ڈ': 'ड',
    'ڑ': 'ड़',  'ژ': 'ज़',  'ک': 'क',   'گ': 'ग',
    'ہ': 'ह',   'ھ': 'ह',   'ؤ': 'व',   'ئ': 'य',
}

# ---------------------------------------------------------------------------
# Harakat (vowel diacritics)  →  Devanagari vowel signs
# ---------------------------------------------------------------------------
DIACRITIC_MAP = {
    '\u064e': 'ा',   # zabar  (fatha)   → mapped to ā sign (inherent 'a' approximation
                      #                    for unvowelised text; short-a has no Devanagari sign)
    '\u0650': 'ि',   # zer    (kasra)   → i
    '\u064f': 'ु',   # pesh   (damma)   → u
    '\u0652': '्',   # jazm   (sukun)   → halant
    '\u0651': None,  # tashdeed (shadda) → double consonant
    '\u064b': 'ाँ',  # tanwin fath
    '\u064d': 'िँ',  # tanwin kasr
    '\u064c': 'ुँ',  # tanwin damm
    '\u0670': 'ा',   # superscript alif → ā
    '\u0653': '',    # maddah above
}

# Whole-word fixes (highest priority)
WORD_FIXES = {
    'الله':  'अल्लाह',
    'ہے':   'है',
    'ہیں':  'हैं',
    'نہیں': 'नहीं',
}

# Arabic punctuation that lives in the 0x0600-0x06FF block
_ARABIC_PUNCT = {
    '\u060c': ',',   # ،  Arabic comma
    '\u061f': '?',   # ؟  Arabic question mark
    '\u06d4': '।',   # ۔  Arabic full stop → Devanagari danda
}

# Devanagari vowel signs / independent vowels (used to decide ی consonant vs vowel)
_VOWEL_CHARS = frozenset('ािीुूेैोौृंःअआइईउऊएऐओऔ')

# Regex to strip trailing Arabic punctuation from a token
_TRAIL_PUNCT_RE = re.compile(r'^(.*?)([\u060c\u061f\u06d4]+)$', re.DOTALL)
_TRAIL_PUNCT_MAP = {'\u06d4': '।', '\u060c': ',', '\u061f': '?'}


def _is_arabic(c):
    cp = ord(c)
    return (0x0600 <= cp <= 0x06FF) or (0xFB50 <= cp <= 0xFDFF) or (0xFE70 <= cp <= 0xFEFF)


# ---------------------------------------------------------------------------
# Vowel absorption helper  (called right after writing a Devanagari consonant)
# ---------------------------------------------------------------------------
def _absorb_vowel(chars, i, n, dev_prev, result):
    """
    If chars[i] is a vowel letter or diacritic, absorb it and return i+1 (or i+2
    for two-char combinations).  Otherwise return i unchanged.
    """
    if i >= n:
        return i
    nc = chars[i]
    if not _is_arabic(nc) or nc in _ARABIC_PUNCT:
        return i

    if nc == 'ا':
        result.append('ा'); return i + 1

    if nc == 'آ':
        result.append('आ'); return i + 1

    if nc == 'ی':
        # یٰ  → long ā  (e.g. موسیٰ, عیسیٰ)
        if i + 1 < n and chars[i + 1] == '\u0670':
            result.append('ा'); return i + 2
        result.append('ी'); return i + 1

    if nc == 'ے':
        result.append('े'); return i + 1        # dependent e sign

    if nc == 'و':
        # وا pattern → leave و for main loop (it is consonant व before ā)
        nxt2 = chars[i + 1] if i + 1 < n else None
        if nxt2 == 'ا':
            return i
        result.append('ो'); return i + 1        # long o vowel

    if nc in DIACRITIC_MAP:
        d = DIACRITIC_MAP[nc]
        if d is None:                            # shadda → double consonant
            result.append('्')
            result.append(dev_prev)
        elif d:
            result.append(d)
        return i + 1

    return i                                     # nothing absorbed


# ---------------------------------------------------------------------------
# Segment transliteration  (pure character-level, no WORD_FIXES lookup)
# ---------------------------------------------------------------------------
def _trans_segment(text):
    chars  = list(text)
    n      = len(chars)
    result = []
    i      = 0
    in_word = False              # True while inside a run of Arabic characters

    while i < n:
        c  = chars[i]
        cp = ord(c)

        # ── Non-Arabic: pass through ────────────────────────────────────────
        if not _is_arabic(c):
            result.append(c)
            in_word = False
            i += 1
            continue

        # ── Arabic punctuation (within 0x0600–0x06FF) ───────────────────────
        if c in _ARABIC_PUNCT:
            result.append(_ARABIC_PUNCT[c])
            in_word = False
            i += 1
            continue

        # ── Keep special Arabic symbols unchanged ────────────────────────────
        if cp == 0xFDFA or cp in (0x0611, 0x0613):
            result.append(c)
            in_word = True
            i += 1
            continue

        # ── High hamza (ٴ U+0674): silent ───────────────────────────────────
        if cp == 0x0674:
            in_word = True
            i += 1
            continue

        # ── Noon ghunna (ں) → anusvara ──────────────────────────────────────
        if c == 'ں':
            result.append('ं')
            in_word = True
            i += 1
            continue

        # ── Hamza (ء): silent ────────────────────────────────────────────────
        if c == 'ء':
            in_word = True
            i += 1
            continue

        # ── Unabsorbed harakat ───────────────────────────────────────────────
        if c in DIACRITIC_MAP:
            d = DIACRITIC_MAP[c]
            if d:
                result.append(d)
            in_word = True
            i += 1
            continue

        # ── Alif madda (آ) ───────────────────────────────────────────────────
        if c == 'آ':
            result.append('आ' if not in_word else 'ा')
            in_word = True
            i += 1
            continue

        # ── Alif (ا) ─────────────────────────────────────────────────────────
        if c == 'ا':
            if not in_word:
                nxt = chars[i + 1] if i + 1 < n else None
                if   nxt == 'ے': result.append('ए'); i += 2   # اے → ए
                elif nxt == 'ی': result.append('ई'); i += 2   # ای → ई
                elif nxt == 'و': result.append('औ'); i += 2   # au diphthong: ا+و → औ (e.g. اور = aur)
                else:            result.append('अ'); i += 1
            else:
                result.append('ा')                              # post-consonant ā
                i += 1
            in_word = True
            continue

        # ── Waw (و) ──────────────────────────────────────────────────────────
        if c == 'و':
            if not in_word:
                # Word-initial → consonant व
                result.append('व')
                in_word = True
                i += 1
                # absorb immediately following diacritic if any
                if i < n and chars[i] in DIACRITIC_MAP:
                    d = DIACRITIC_MAP[chars[i]]
                    if d:
                        result.append(d)
                    i += 1
            else:
                nxt = chars[i + 1] if i + 1 < n else None
                if nxt == 'ا':
                    # وا pattern: و is consonant व, alif is ā
                    result.append('व'); i += 1
                    result.append('ा'); i += 1
                else:
                    result.append('ो')          # mid-word long o vowel
                    i += 1
                in_word = True
            continue

        # ── Farsi ya (ی) ─────────────────────────────────────────────────────
        if c == 'ی':
            nxt = chars[i + 1] if i + 1 < n else None
            if nxt == '\u0670':                 # یٰ → long ā
                result.append('आ' if not in_word else 'ा')
                i += 2
            elif not in_word:
                result.append('य')              # word-initial → consonant
                i += 1
            else:
                last = result[-1] if result else ''
                if last in _VOWEL_CHARS:
                    result.append('य')          # after vowel → consonant
                else:
                    result.append('ी')          # after consonant → long ī
                i += 1
            in_word = True
            continue

        # ── Bari ya (ے) ──────────────────────────────────────────────────────
        if c == 'ے':
            result.append('े' if in_word else 'ए')
            in_word = True
            i += 1
            continue

        # ── Ain (ع): vowel bearer ─────────────────────────────────────────────
        if c == 'ع':
            if not in_word:
                result.append('अ')              # word-initial ain → a
            # word-medial/final: silent
            in_word = True
            i += 1
            continue

        # ── Aspiration digraph  C + ھ ─────────────────────────────────────────
        if i + 1 < n and chars[i + 1] == 'ھ' and (c + 'ھ') in ASPIRATED:
            dev = ASPIRATED[c + 'ھ']
            i += 2
            result.append(dev)
            in_word = True
            i = _absorb_vowel(chars, i, n, dev, result)
            continue

        # ── Regular consonant ─────────────────────────────────────────────────
        if c in CONSONANT_MAP:
            dev = CONSONANT_MAP[c]
            # Gemination: same consonant immediately before → insert halant
            if in_word and result and result[-1] == dev:
                result.append('्')
            result.append(dev)
            in_word = True
            i += 1
            i = _absorb_vowel(chars, i, n, dev, result)
            continue

        # ── Unknown Arabic character → pass through ───────────────────────────
        result.append(c)
        in_word = True
        i += 1

    return ''.join(result)


# ---------------------------------------------------------------------------
# Token-level helper  (applies WORD_FIXES, handles trailing Arabic punct)
# ---------------------------------------------------------------------------
def _safe_trans_token(tok):
    """Translate one whitespace-delimited token."""
    if tok in WORD_FIXES:
        return WORD_FIXES[tok]
    # Try stripping trailing Arabic punctuation, then look up in WORD_FIXES
    m = _TRAIL_PUNCT_RE.match(tok)
    if m:
        word_part  = m.group(1)
        punct_part = ''.join(_TRAIL_PUNCT_MAP.get(c, c) for c in m.group(2))
        if word_part in WORD_FIXES:
            return WORD_FIXES[word_part] + punct_part
    return _trans_segment(tok)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def transliterate_urdu_to_devanagari(text):
    """
    Transliterate a string of Urdu (Arabic/Nastaliq script) to Devanagari.
    Non-Arabic characters are passed through unchanged.
    """
    tokens = re.split(r'(\s+)', text)
    return ''.join(_safe_trans_token(t) for t in tokens)


def transliterate_line(line):
    """
    Process one line from the Urdu Quran output file.
    Verse lines  ``[N:N] <Urdu text>``  →  keep [N:N], transliterate text.
    All other lines (headers, separators, surah titles) → unchanged.
    """
    stripped = line.rstrip('\n')
    nl = '\n' if line.endswith('\n') else ''
    if not stripped:
        return line
    m = re.match(r'^(\[\d+:\d+\]\s*)(.*)', stripped)
    if m:
        return m.group(1) + transliterate_urdu_to_devanagari(m.group(2)) + nl
    return line
