# API Reference

> This document describes the **programmatic interface** of the three Python generator scripts in `src/`. All scripts are intended to be run directly from the command line; they expose no importable Python API. This reference documents each script's inputs, outputs, internal functions, constants, and data contracts.

<!-- TOC -->
- [1. gentxtforquran.py](#1-gentxtforquranpy)
  - [1.1 Invocation](#11-invocation)
  - [1.2 Constants](#12-constants)
  - [1.3 translations List](#13-translations-list)
  - [1.4 Language-Type Dispatch](#14-language-type-dispatch)
  - [1.5 Output Format Contract](#15-output-format-contract)
- [2. gentexforquran.py](#2-gentexforquranpy)
  - [2.1 Invocation](#21-invocation)
  - [2.2 Constants](#22-constants)
  - [2.3 Generated File Contract](#23-generated-file-contract)
- [3. gendocshtml.py](#3-gendocshtmlpy)
  - [3.1 Invocation](#31-invocation)
  - [3.2 Module-Level Constants](#32-module-level-constants)
  - [3.3 Input Sources](#33-input-sources)
  - [3.4 Output Files](#34-output-files)
  - [3.5 HTML Page Structure Contract](#35-html-page-structure-contract)
- [4. Makefile Targets](#4-makefile-targets)
- [5. Data File Contracts](#5-data-file-contracts)
  - [5.1 Format 1: One-Per-Line](#51-format-1-one-per-line)
  - [5.2 Format 2: Pipe-Delimited](#52-format-2-pipe-delimited)
  - [5.3 Format 3: num|text Sequential](#53-format-3-numtext-sequential)
  - [5.4 Format 4: JSON-in-ZIP](#54-format-4-json-in-zip)
<!-- /TOC -->

---

## 1. gentxtforquran.py

### 1.1 Invocation

```bash
# Run from the repository root directory:
python3 src/gentxtforquran.py
```

**Prerequisites:**
- Python 3.6+ (uses f-string-compatible features; actually uses `%` formatting)
- All files listed in the `translations` constant must exist under `data/`
- The `output/` directory is created automatically if it does not exist

**Exit behaviour:** Exits with code `0` on success. Unhandled exceptions (e.g., missing input file) will produce a traceback and exit with a non-zero code.

**Side effects:** Writes 71 files to `output/`. Prints one confirmation line per file to stdout.

### 1.2 Constants

#### `surasize`
```python
surasize: list[int]  # length = 114
```
Ayah counts for each surah, in Mushaf order (Surah 1 through 114). The sum of all values equals **6,236** — the total number of ayahs in the Qur'an.

| Index | Surah | Ayahs |
|-------|-------|-------|
| 0 | Al-Fatihah | 7 |
| 1 | Al-Baqarah | 286 |
| 2 | Al-'Imran | 200 |
| … | … | … |
| 113 | An-Nas | 6 |

#### `suraname`
```python
suraname: list[str]  # length = 114
```
English transliteration and translation of each surah name. Example: `"Al-Fatihah (The Opening)"`.

### 1.3 `translations` List

```python
translations: list[tuple[str, str, str, str]]
```

Each element is a 4-tuple:

| Index | Field | Description | Example |
|-------|-------|-------------|---------|
| 0 | `src_file` | Relative path to input data file | `'data/en.sahih.txt'` |
| 1 | `out_file` | Relative path to output file | `'output/quran_english_sahih.txt'` |
| 2 | `translator` | Human-readable translator/source name | `'Saheeh International'` |
| 3 | `lang` | Language-type identifier (see dispatch table) | `'English'` |

The list contains **71 entries** as of the current version.

### 1.4 Language-Type Dispatch

The `lang` field controls both the header text written to the output file and the input-parsing strategy:

| `lang` value | Header written | Input format | Parsing strategy |
|---|---|---|---|
| `'English'` | `Quran - English Translation` | One-per-line | `readline()` |
| `'English-Piped'` | `Quran - English Translation` | Pipe-delimited | `split('|', 2)[2]` |
| `'English-SuraAyah'` | `Quran - English Translation` | Pipe-delimited | `split('|', 2)[2]` |
| `'Arabic'` | `Quran - Arabic` | One-per-line | `readline()` |
| `'Hindi'` | `Quran - Hindi Anuvad` | One-per-line | `readline()` |
| `'Hindi-Tafsir-JSON'` | `Quran - Hindi Tafsir` | JSON ZIP | `entry.get('text', '')` |
| `'English-Tafsir-JSON'` | `Quran - English Explanation` | JSON ZIP | `entry.get('text', '')` |
| `'Gujarati-JSON'` | `Quran - Gujarati Bhashantar` | JSON ZIP | `entry.get('t', '')` |
| `'Nepali-JSON'` | `Quran - Nepali Anuvad` | JSON ZIP | `entry.get('t', '')` |
| `'Transliteration'` | `Quran - English Transliteration` | One-per-line | `readline()` |
| `'Transliteration-Sequential'` | `Quran - English Transliteration` | `num\|text` | `split('|', 1)[1]` |
| `'Urdu'` | `Quran - Urdu Tarjuma` | One-per-line | `readline()` |
| `'Urdu-SuraAyah'` | `Quran - Urdu Tarjuma` | Pipe-delimited | `split('|', 2)[2]` |
| `'Roman-Urdu'` | `Quran - Roman Urdu Tarjuma` | One-per-line | `readline()` |
| `'Roman-Hindi'` | `Quran - Roman Hindi Tarjuma` | One-per-line | `readline()` |
| `'Roman-Gujarati'` | `Quran - Roman Gujarati Bhashantar` | One-per-line | `readline()` |

### 1.5 Output Format Contract

Every output file produced by `gentxtforquran.py` follows this structure:

```
<TITLE LINE>\n
<CREDIT LINE>\n
============================================================\n
\n
Surah 1: Al-Fatihah (The Opening)\n
----------------------------------------\n
[1:1] <ayah text>\n
[1:2] <ayah text>\n
...
[1:7] <ayah text>\n
\n
Surah 2: Al-Baqarah (The Cow)\n
----------------------------------------\n
[2:1] <ayah text>\n
...
```

Key details:
- Title and credit lines vary by language type (see dispatch table)
- Separator is exactly 60 `=` characters
- Surah separator is exactly 40 `-` characters
- Ayah reference format: `[sura:ayah]` where both are unpadded integers
- Blank line after the last ayah of each surah (before the next `Surah` heading)
- Encoding: UTF-8
- Line endings: platform-native (`\n` on Unix)

---

## 2. gentexforquran.py

### 2.1 Invocation

```bash
python3 src/gentexforquran.py
```

**Prerequisites:**
- Python 3.6+
- `data/hi.farooq.txt`, `data/hi.hindi.txt`, `data/en.sahih.txt`, `data/en.transliteration.txt`, `data/en.pickthall.txt` must exist
- `latex/` directory is created automatically if it does not exist

**Side effects:** Writes 5 `.tex` files to `latex/`. Produces no stdout output.

### 2.2 Constants

`surasize` and `suraname` are identical in structure to those in `gentxtforquran.py` (see §1.2). They are defined inline in this script rather than being imported from a shared module.

### 2.3 Generated File Contract

Each generated content file (`qum.tex`, `qup.tex`, `qus.tex`, `qut.tex`, `qupk.tex`) contains interleaved Arabic and translation LaTeX markup:

```latex
\chapter{Al-Fatihah (The Opening)}
\begin{Arabic}
\Huge{\centerline{\basmalah}}\end{Arabic}
\flushright{\begin{Arabic}
\quranayah[1][1]
\end{Arabic}}
\flushleft{In the name of Allah, the Beneficent, the Merciful.}
\flushright{\begin{Arabic}
\quranayah[1][2]
\end{Arabic}}
\flushleft{All praise is due to Allah, the Lord of the Worlds.}
...
```

For Hindi content, the translation is wrapped in a `{hindi}` environment:
```latex
\flushleft{\begin{hindi}
<Hindi text line>
\end{hindi}}
```

For English content, it is emitted as plain LaTeX text:
```latex
\flushleft{<English text>}
```

**Generated file to template mapping:**

| Generated content file | LaTeX template | Translation source |
|----------------------|----------------|-------------------|
| `latex/qum.tex` | `latex/farooq.tex` | `data/hi.farooq.txt` |
| `latex/qup.tex` | `latex/suhail.tex` | `data/hi.hindi.txt` |
| `latex/qus.tex` | `latex/sahih.tex` | `data/en.sahih.txt` |
| `latex/qut.tex` | `latex/translit.tex` | `data/en.transliteration.txt` |
| `latex/qupk.tex` | `latex/pickthall.tex` | `data/en.pickthall.txt` |

---

## 3. gendocshtml.py

### 3.1 Invocation

```bash
python3 src/gendocshtml.py
```

**Prerequisites:**
- Python 3.6+ with `re` and `os` (both standard library)
- All files listed in §3.3 must exist

**Side effects:** Writes approximately 120+ files to `docs/`. Prints one line per generated file to stdout.

### 3.2 Module-Level Constants

| Constant | Type | Description |
|----------|------|-------------|
| `SURA_SIZE` | `list[int]` (114) | Ayah counts per surah (same data as `surasize` in other scripts) |
| `SURA_NAME` | `list[str]` (114) | English surah names |
| `SURAH_REV` | `list[tuple[int, str]]` (114) | `(revelation_order, 'M'/'D')` per surah |

### 3.3 Input Sources

| File | Format | Used for |
|------|--------|----------|
| `data/en.transliteration.tanzil.txt` | Pipe-delimited, HTML tags | Tanzil transliteration on surah pages |
| `output/quran_translit_unicode.txt` | `[sura:ayah] text` | Unicode transliteration rows |
| `output/quran_hindi_farooq.txt` | `[sura:ayah] text` | Hindi translation (Farooq Khan) |
| `output/quran_hindi_suhail.txt` | `[sura:ayah] text` | Hindi translation (Suhail) |
| `output/quran_hindi_mokhtasar.txt` | `[sura:ayah] text` | Hindi Tafsir (Al-Mokhtasar) |
| `output/quran_english_abridged.txt` | `[sura:ayah] text` | English Explanation (Abridged) |
| `data/en.pickthall.txt` | One-per-line | English translation (Pickthall) |
| `output/quran_english_yusufali.txt` | `[sura:ayah] text` | English translation (Yusuf Ali) |
| `output/quran_english_sahih.txt` | `[sura:ayah] text` | English translation (Saheeh Intl) |
| `output/quran_english_hilali.txt` | `[sura:ayah] text` | English translation (Hilali & Khan) |
| `output/quran_arabic.txt` | `[sura:ayah] text` | Arabic text display |
| `output/quran_gujarati_rabila.txt` | `[sura:ayah] text` | Gujarati translation |
| `output/quran_nepali_ahl_al_hadith.txt` | `[sura:ayah] text` | Nepali translation |
| `output/quran_roman_urdu_maududi.txt` | `[sura:ayah] text` | Roman Urdu (Maududi) |
| `output/quran_roman_urdu_junagarhi.txt` | `[sura:ayah] text` | Roman Urdu (Junagarhi) |
| `output/quran_hindi_omari.txt` | `[sura:ayah] text` | Hindi translation (Al-Omari) |

### 3.4 Output Files

| Output | Description |
|--------|-------------|
| `docs/001.html` … `docs/114.html` | Individual surah pages (zero-padded, 3 digits) |
| `docs/index.html` | Homepage with 114-surah grid, last-read card, last bookmark card |
| `docs/search.html` | Config-aware full-text search UI (lazy-loads per-field JSON files) |
| `docs/bookmarks.html` | Bookmark manager: list all bookmarks, export/import JSON, delete individual |
| `docs/sd/meta.json` | Surah/ayah index (~200 KB); always prefetched by search page |
| `docs/sd/{fieldkey}.json` | One flat text array per translation field (17 files); lazy-fetched per user settings |
| `docs/download.html` | Download links for output files |
| `docs/config.html` | User preferences / settings page |
| `docs/license.html` | License information page |

### 3.5 HTML Page Structure Contract

Each surah page (`docs/NNN.html`) contains the following semantic sections, in order:

1. **`<head>`** — charset, viewport meta, CSS (inline), Google Fonts import
2. **`<nav>`** — navigation bar with site title, surah dropdown, dark-mode toggle
3. **`<header>`** — surah name (Arabic + transliteration + English), revelation metadata
4. **Content Filter widget** — `<details>`/`<summary>` collapsible; one checkbox per content type
5. **`<table class="ayah-table">`** — one `<tr>` per ayah; columns:
   - Ayah number badge
   - Arabic text (`dir="rtl"`, Amiri Quran or Scheherazade New font)
   - `<audio>` element (Alafasy recitation)
   - Tanzil transliteration (HTML preserved)
   - Unicode transliteration
   - English translations (Pickthall, Yusuf Ali, Saheeh, Hilali, Explanation)
   - Hindi translations (Farooq, Suhail, Al-Omari, Tafsir)
   - Roman Urdu (Maududi, Junagarhi)
   - Gujarati, Nepali
6. **`<footer>`** — attribution, data sources, license note

**Audio URL pattern:**
```
https://druvx13-quran-audio-alafasy.hf.space/<SSS><AAA>.mp3
```
where `SSS` = zero-padded 3-digit surah number, `AAA` = zero-padded 3-digit ayah number.

---

## 4. Makefile Targets

| Target | Command | Prerequisites | Output |
|--------|---------|---------------|--------|
| `help` | (default) | none | Prints available targets to stdout |
| `generate-tex` | `python3 src/gentexforquran.py` | data files | `latex/q*.tex` |
| `all` | `xelatex` for each template | `generate-tex` run first | `output/*.pdf` |
| `generate-txt` | `python3 src/gentxtforquran.py` | data files | `output/*.txt` |
| `generate-docs` | `python3 src/gendocshtml.py` | `generate-txt` run first | `docs/*.html` |
| `clean` | `rm latex/*.aux *.log *.toc *.out *.synctex.gz` | none | Removes artefacts |

**Build variables** (overridable on the command line):

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHON` | `python3` | Python interpreter |
| `LATEX` | `xelatex` | LaTeX compiler |
| `LATEX_DIR` | `latex` | Directory containing `.tex` templates |
| `OUTPUT_DIR` | `output` | Directory for generated outputs |

Example override:
```bash
make generate-txt PYTHON=/usr/bin/python3.11
```

---

## 5. Data File Contracts

### 5.1 Format 1: One-Per-Line

- **Encoding:** UTF-8 (some files may have a leading BOM; scripts strip it via `readline()` + `rstrip('\n')`)
- **Length:** Exactly 6,236 lines (one per ayah, Mushaf order)
- **No header:** Line 1 is ayah 1:1, line 7 is ayah 1:7 (end of Al-Fatihah), line 8 is ayah 2:1, etc.

### 5.2 Format 2: Pipe-Delimited

```
<sura>|<ayah>|<text>
```

- **Encoding:** UTF-8
- **Comment lines:** Lines starting with `#` must be skipped (present in `en.yusufali.txt`)
- **Fields:** sura and ayah numbers are 1-indexed integers; text is everything after the second pipe
- **Length:** Exactly 6,236 data lines (plus optional comments/headers)

### 5.3 Format 3: num|text Sequential

```
<global_ayah_num>|<text>
```

- **Global ayah number:** Sequential 1–6,236 (not `sura:ayah`)
- **Encoding:** UTF-8
- **Length:** Exactly 6,236 lines

### 5.4 Format 4: JSON-in-ZIP

- **Container:** Standard ZIP archive (readable with Python's `zipfile` module)
- **Contents:** One `.json` file (name discovered by `zf.namelist()`)
- **JSON root:** Object with `"sura:ayah"` string keys
- **Value types:**
  - Object with `"text"` field: used by Hindi Tafsir and English Explanation
  - Object with `"t"` field: used by Gujarati and Nepali
  - String alias: some entries may be a string pointing to another key (double-lookup pattern)
- **Key coverage:** Must cover all 6,236 `"sura:ayah"` combinations; missing keys produce empty string output
