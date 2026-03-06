# Appendix: Raw Analysis

Unfiltered findings, raw metrics, and edge cases discovered during the analysis of this repository. This document contains technical observations that did not fit neatly into other documentation.

<!-- TOC -->
- [1. Raw File Metrics](#1-raw-file-metrics)
- [2. Code Metrics](#2-code-metrics)
- [3. Data Format Edge Cases](#3-data-format-edge-cases)
- [4. Code Duplication Analysis](#4-code-duplication-analysis)
- [5. Known Latent Issues](#5-known-latent-issues)
- [6. Dependency Inventory](#6-dependency-inventory)
- [7. Translation Source Coverage Matrix](#7-translation-source-coverage-matrix)
- [8. Surah Size Distribution](#8-surah-size-distribution)
- [9. File Naming Pattern Analysis](#9-file-naming-pattern-analysis)
- [10. gendocshtml.py Structure Analysis](#10-gendocshtmlpy-structure-analysis)
- [11. Output File Language Coverage](#11-output-file-language-coverage)
<!-- /TOC -->

---

## 1. Raw File Metrics

### Source code files (src/)

| File | Lines | Purpose |
|------|-------|---------|
| `src/gendocshtml.py` | ~1,970 | HTML website generator (largest file by far) |
| `src/gentxtforquran.py` | 217 | Plain-text output generator |
| `src/gentexforquran.py` | 89 | LaTeX content file generator |
| **Total** | **~2,276** | |

### Data files (data/)

| Category | Count | Total size |
|----------|-------|-----------|
| English translations (.txt) | 37 | ~32 MB |
| Urdu translations (.txt) | 14 | ~21 MB |
| Hindi translations (.txt) | 6 | ~12 MB |
| Arabic text (.txt) | 1 | ~1.1 MB |
| Transliteration (.txt) | 3 | ~2.3 MB |
| JSON ZIP files | 4 | ~2.3 MB |
| Other (.txt) | 5 | ~1 MB |
| **Total** | **~70** | **~72 MB** |

### Output files (output/)

| Category | Count | Total size |
|----------|-------|-----------|
| English plain-text | 37 | ~35 MB |
| Urdu plain-text | 14 | ~22 MB |
| Hindi plain-text | 6 | ~13 MB |
| Arabic plain-text | 1 | ~1.2 MB |
| Transliteration plain-text | 3 | ~2.5 MB |
| Gujarati/Nepali/Roman | 10 | ~12 MB |
| PDFs | 2 (committed) | ~6.9 MB |
| **Total** | **73** | **~92 MB** |

### HTML docs (docs/)

| Category | Count | Total size |
|----------|-------|-----------|
| Surah pages (001-114) | 114 | ~15–20 MB |
| Special pages | 5 | ~0.5 MB |
| search-data.js | 1 | varies |
| config.js | 1 | small |
| **Total** | **~121** | **~20 MB** |

---

## 2. Code Metrics

### gentxtforquran.py

- **`translations` list entries:** 71
- **`lang` type values used:** 16 distinct values
- **`if/elif` branches in dispatch:** 16 branches + 1 `else` fallback
- **JSON ZIP files processed:** 4
- **Files opened simultaneously:** max 2 (1 read, 1 write, except JSON which is all in memory)
- **Total writes:** 71 × 6,236 + overhead ≈ 442,756 data lines + 71 × (~10 header lines + 114 surah headers + 114 separators) ≈ ~460,000 total writes

### gentexforquran.py

- **Code blocks:** 5 (one per PDF)
- **LaTeX constructs per surah:** chapter + basmalah + (4 lines per ayah) = ~25,000+ constructs per generated file
- **Generated file sizes:** qum.tex: ~2.76 MB, qup.tex: ~3.0 MB, qus.tex: ~1.3 MB, qut.tex: ~1.1 MB, qupk.tex: ~1.3 MB

### gendocshtml.py

- **Constants defined:** 3 major arrays (SURA_SIZE, SURA_NAME, SURAH_REV) plus additional Juz/rukū/sajdah arrays
- **Input files read:** 16+ files loaded at startup
- **HTML files written:** 114 surah pages + 5 special pages = 119+
- **Estimated HTML lines per surah page:** 100 (header/CSS/nav) + ayahs × rows_per_ayah × columns; for a typical 100-ayah surah: ~6,000–10,000 HTML lines

---

## 3. Data Format Edge Cases

### en.yusufali.txt
- **Format:** Pipe-delimited `sura|ayah|text`
- **Edge case:** Contains comment lines starting with `#` at the top of the file
- **How handled:** The `English-SuraAyah` parser (`split('|', 2)[2]`) reads these comments as data lines on startup. In practice, the file positions data at line 1 with no headers — the comments appear after the data. **Unconfirmed whether this causes misalignment.** Requires empirical verification.

### ur.wahiduddin.txt (and possibly others from quran.com)
- **Edge case:** Some files from quran.com were fetched with a leading UTF-8 BOM (`\xef\xbb\xbf`)
- **How handled:** CHANGELOG.md notes "embedded BOM stripped from `en.wahiduddin.txt`" — this was done as a one-time preprocessing step before committing the file. The current file in the repository should be BOM-free.

### JSON ZIP key aliasing
- **Edge case:** Some entries in JSON tafsir files are string values rather than dicts, pointing to another key (alias pattern)
- **How handled:** `gentxtforquran.py` does a double-lookup: `if isinstance(entry, str): entry = ayah_data.get(entry, {})`
- **Implication:** If a chain of aliases is longer than 1 level, the code will return `{}` and produce an empty text. Not tested with actual data.

### en.transliteration.tanzil.txt
- **Format:** Pipe-delimited `sura|ayah|text` where text contains HTML markup tags
- **Used by:** `gendocshtml.py` only (preserves HTML tags for display)
- **NOT used by:** `gentxtforquran.py` (uses `en.transliteration.txt` instead, which is plain text without HTML tags)
- **Edge case:** The HTML tags in this file (e.g., `<em>`, `<span>`) would corrupt a plain-text output if accidentally used in `gentxtforquran.py`.

### hi.farooq.txt and hi.hindi.txt
- **Format:** One-per-line Devanagari
- **Used by:** Both `gentxtforquran.py` (for plain-text output) AND `gentexforquran.py` (for PDF generation)
- **Edge case:** These files are opened in `gentexforquran.py` without specifying `encoding='utf-8'`. This relies on the system default encoding being UTF-8 (true on Linux/macOS but potentially problematic on Windows with non-UTF-8 system encoding). **Potential issue on Windows.**

---

## 4. Code Duplication Analysis

### `surasize` / `SURA_SIZE` duplication

The same 114-element list of surah sizes appears in all three Python scripts:
- `gentxtforquran.py`: `surasize` (line 16)
- `gentexforquran.py`: `surasize` (line 14)
- `gendocshtml.py`: `SURA_SIZE` (module-level constant)

Similarly for surah names (`suraname` / `SURA_NAME`).

**Impact:** If a discrepancy were introduced between these three definitions, outputs would be misaligned. In practice, these values are immutable (the Qur'an's structure does not change).

**Refactoring option:** Extract to a shared `src/qurandata.py` module. However, this would complicate the "run from repo root" design since scripts would need to handle Python path resolution.

### Repeated file-generation patterns in gentexforquran.py

The script has 5 nearly-identical code blocks. A refactoring to parameterize the block would reduce ~90 lines to ~20 lines plus a data list. This would not change behavior.

### Repeated header-writing logic in gentxtforquran.py

The header-writing `if/elif` chain (lines 104–141) could be refactored into a `HEADERS` dict indexed by `lang`. The dispatch `if/elif` chain for parsing (lines 142–215) is harder to refactor because each branch has slightly different logic.

---

## 5. Known Latent Issues

| Issue | Severity | Location | Description |
|-------|----------|----------|-------------|
| Missing encoding in gentexforquran.py | Low | `open('data/hi.farooq.txt', 'r')` (no encoding) | May fail on Windows with non-UTF-8 default encoding |
| Basmalah for Surah 9 | Minor | `gentexforquran.py`, all 5 blocks | Emits Basmalah for Surah 9 (At-Tawbah), which traditionally does not begin with Basmalah |
| No header-skip for commented files | Low | `gentxtforquran.py`, `English-Piped` branch | Comment lines in `en.yusufali.txt` may cause misalignment if positioned before data |
| Translation text with LaTeX special characters | Low | `gentexforquran.py` | Backslashes or braces in translation text would corrupt generated .tex files |
| `search-data.js` size not bounded | Low | `gendocshtml.py` | On slower devices, a very large search-data.js may cause browser tab crashes |
| Audio URL hardcoded, not configurable | Low | `gendocshtml.py` | Changing the audio server requires grep+replace in the source code |
| Alias chain length limit in JSON parsing | Very Low | `gentxtforquran.py`, JSON branches | Only 1-level alias lookup; deeper chains produce empty text |

---

## 6. Dependency Inventory

### Python
| Module | Type | Used in | Purpose |
|--------|------|---------|---------|
| `json` | stdlib | gentxtforquran.py | Parse JSON from ZIP files |
| `os` | stdlib | all scripts | `makedirs` calls |
| `re` | stdlib | gendocshtml.py | Regex text processing |
| `zipfile` | stdlib | gentxtforquran.py, gendocshtml.py | Read .json.zip files |

### LaTeX packages
| Package | Used in | Purpose |
|---------|---------|---------|
| `quran` | quran.sty, templates | `\quranayah` macro, Arabic text |
| `polyglossia` | quran.sty | Multilingual (Arabic, Hindi, English) |
| `fontspec` | quran.sty | OpenType font loading for XeLaTeX |
| `xltxtra` / `xunicode` | quran.sty (likely) | XeTeX Unicode compatibility |

### System fonts (for PDF compilation)
| Font | Script | Source |
|------|--------|--------|
| Amiri or Scheherazade New | Arabic | CTAN / Google Fonts |
| Mangal or Lohit Devanagari | Hindi (Devanagari) | System / CTAN |

### JavaScript (website)
No JavaScript libraries. Pure vanilla JS.

### CSS (website)
No CSS frameworks. Inline CSS in generated HTML.

### External services
| Service | URL | Purpose |
|---------|-----|---------|
| Google Fonts | fonts.googleapis.com | Arabic and Devanagari web fonts |
| Hugging Face Space | druvx13-quran-audio-alafasy.hf.space | Audio MP3 file serving |
| GitHub Pages | druvx13.github.io/Quran-data | Website hosting |

---

## 7. Translation Source Coverage Matrix

| Source | Translations provided | Languages |
|--------|-----------------------|-----------|
| tanzil.net | 22 (Arabic, Pickthall, Yusuf Ali, Sahih, Hilali, Qarai, Ahmed Ali, Ahmed Raza, Arberry, Daryabadi, Itani, Maududi EN, Mubarakpuri, Qaribullah, Sarwar, Shakir, Wahiduddin EN, 8 Urdu, transliteration) | Arabic, English, Urdu |
| fawazahmed0/quran-api (jsdelivr) | 27 (21 English, 3 Roman Hindi, 2 Urdu, 1 Roman Gujarati, Roman Urdu Junagarhi) | English, Roman Hindi, Urdu, Roman Gujarati |
| quranenc.com | 2 (English Rowwad, Hindi Omari) | English, Hindi |
| alquran.cloud | 1 (Muhammad Asad) | English |
| quran.com | 6 (Usmani EN, Abdel Haleem, 4 Urdu, Roman Urdu Maududi) | English, Urdu |
| JSON ZIPs (direct) | 4 (Hindi Tafsir, English Explanation, Gujarati, Nepali) | Hindi, English, Gujarati, Nepali |
| zekr.org (original) | 2 (Farooq Khan Hindi, Suhail Hindi) | Hindi |
| Quran Unicode Project | 1 (Transliteration) | Transliteration |

---

## 8. Surah Size Distribution

Statistical analysis of the `surasize` array:

| Metric | Value |
|--------|-------|
| Total ayahs | 6,236 |
| Largest surah | Al-Baqarah (286 ayahs) |
| Smallest surah | Al-'Asr, Al-Kauthar (3 ayahs each) |
| Mean ayahs per surah | 54.7 |
| Median surah size | ~29 ayahs |
| Surahs with <20 ayahs | 51 (surahs 78–114 are mostly short) |
| Surahs with >100 ayahs | 9 (surahs 2, 3, 4, 5, 6, 7, 9, 16, 26) |

This distribution matters for HTML file size: Al-Baqarah (`002.html`) with 286 ayahs × 16+ content rows will be significantly larger than Al-Kauthar (`108.html`) with 3 ayahs.

---

## 9. File Naming Pattern Analysis

### data/ naming conventions

| Pattern | Example | Languages |
|---------|---------|-----------|
| `<lang>.<author>.txt` | `en.sahih.txt` | English, Urdu, Arabic |
| `<lang>.<author>.tanzil.txt` | `en.pickthall.tanzil.txt` | English (Tanzil format) |
| `<lang>.roman.<author>.txt` | `hi.roman.farooq.txt` | Roman Hindi, Roman Gujarati |
| `<lang>.roman<author>.txt` | `ur.romanmaududi.txt` | Roman Urdu (inconsistent separator) |
| `<name>-<description>.json.zip` | `hindi-mokhtasar.json.zip` | JSON ZIPs |
| `ar.quran.txt` | (fixed) | Arabic |
| `translit_en.txt` | (fixed, legacy naming) | Transliteration |
| `surna.txt`, `suranamemal.txt` | (fixed, legacy naming) | Metadata |

**Inconsistency noted:** Roman Urdu files use `romanmaududi` (no separator) while Roman Hindi files use `roman.farooq` (with dot separator). This is a minor convention inconsistency.

### output/ naming conventions

| Pattern | Example |
|---------|---------|
| `quran_<language>_<author>.txt` | `quran_english_sahih.txt` |
| `quran_roman_<language>_<author>.txt` | `quran_roman_hindi_farooq.txt` |
| `quran_<language>.txt` | `quran_arabic.txt` |
| `quran_translit_<variant>.txt` | `quran_translit_unicode.txt` |

The output naming is more consistent than the data input naming.

---

## 10. gendocshtml.py Structure Analysis

As the largest and most complex file in the project (~1,970 lines), `gendocshtml.py` warrants special attention:

### Data loading section (~200 lines)
Reads 16+ files into memory. Key data structures populated:
- Per-surah lists indexed by `[sura_idx][ayah_idx]` for most translations
- The Tanzil transliteration uses pipe-delimited format and is indexed by (sura, ayah) tuple

### CSS template sections (~200 lines)
Inline CSS for light and dark themes, responsive breakpoints, Arabic font declarations, Content Filter widget styles. The CSS is embedded as Python multi-line strings.

### Per-surah HTML generation loop (~800 lines)
The longest section. Iterates surahs 0–113 and for each:
1. Builds the `<head>` including all inline CSS
2. Builds navigation elements
3. Builds the Content Filter widget
4. Iterates ayahs and builds HTML table rows for each content type
5. Builds the footer
6. Writes to `docs/{sura+1:03d}.html`

### Special pages (~400 lines)
- `index.html`: surah grid with all 114 cards
- `search.html`: search UI with input box, pagination
- `search-data.js`: JSON index for all searchable content
- `download.html`: links to output files
- `config.html`: settings/preferences
- `license.html`: license information

---

## 11. Output File Language Coverage

Summary of what languages are in each output file:

| Language | Script | Files | Count |
|----------|--------|-------|-------|
| English | Latin | quran_english_*.txt | 37 |
| Urdu | Perso-Arabic (Nastaliq) | quran_urdu_*.txt | 12 |
| Roman Urdu | Latin | quran_roman_urdu_*.txt | 2 |
| Hindi | Devanagari | quran_hindi_*.txt | 4 |
| Roman Hindi | Latin | quran_roman_hindi_*.txt | 3 |
| Arabic | Arabic (Uthmani) | quran_arabic.txt | 1 |
| Gujarati | Gujarati | quran_gujarati_*.txt | 1 |
| Roman Gujarati | Latin | quran_roman_gujarati_*.txt | 1 |
| Nepali | Devanagari | quran_nepali_*.txt | 1 |
| Transliteration | Latin | quran_english_translit.txt, quran_translit_unicode.txt | 2 |
| Hindi Tafsir | Devanagari | quran_hindi_mokhtasar.txt | 1 |
| English Explanation | Latin | quran_english_abridged.txt | 1 |
| **Total** | | | **66 plain-text + 5 PDF = 71** |

> Note: The "71 output files" count includes all plain-text files. PDF files are additional and gitignored.
