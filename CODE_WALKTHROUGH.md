# Code Walkthrough

A file-by-file annotated guide to every source file in the repository.

<!-- TOC -->
- [1. src/gentxtforquran.py](#1-srcgentxtforquranpy)
- [2. src/gentexforquran.py](#2-srcgentexforquranpy)
- [3. src/gendocshtml.py](#3-srcgendocshtmlpy)
- [4. Makefile](#4-makefile)
- [5. data/ — Input Files](#5-data--input-files)
- [6. latex/ — LaTeX Templates](#6-latex--latex-templates)
- [7. archive/ — Legacy Files](#7-archive--legacy-files)
- [8. Root Configuration Files](#8-root-configuration-files)
<!-- /TOC -->

---

## 1. src/gentxtforquran.py

**File purpose:** Converts all raw translation source files into uniformly-formatted plain-text output files. This is the main data transformation workhorse.

### Imports

```python
import json      # Used to deserialize JSON from ZIP tafsir/explanation files
import os        # Used only for os.makedirs('output', exist_ok=True)
import zipfile   # Used to read .json.zip files without extracting to disk
```

No third-party libraries required — everything is in the Python standard library.

### `os.makedirs('output', exist_ok=True)` *(line 14)*
Creates the `output/` directory if it does not exist. The `exist_ok=True` flag prevents an error if the directory already exists. This is the only filesystem setup step in the script.

### `surasize` *(line 16)*
A 114-element list of integers representing the ayah count for each surah. This is the canonical source of truth for how many ayahs to read from each source file per surah. If this list is wrong, the entire output will be misaligned.

⚠️ **Critical:** This list must never be edited unless the Qur'an itself changes (it won't). The values are fixed by Islamic scholarly consensus and match the Hafs narration of the Uthmani script.

### `suraname` *(line 17)*
A 114-element list of English surah names in the format `"Arabic-Name (English-Meaning)"`. Used as display headers in output files.

### `translations` *(lines 19–101)*
The master configuration list. Each 4-tuple specifies:
1. Input file path
2. Output file path
3. Translator/source credit
4. Language-type identifier

**Adding a new translation** requires only adding one entry here — no other code changes are needed. The `lang` type must be one of the recognized values (see API Reference §1.4).

### Main loop *(lines 103–216)*

```python
for src_file, out_file, translator, lang in translations:
    with open(out_file, 'w', encoding='utf-8') as out:
        # 1. Write header
        # 2. Dispatch to format-specific reading logic
        # 3. For each surah, for each ayah: write [sura:ayah] text
```

The loop iterates over all 71 translations sequentially. There is no parallelism.

**Header writing block** *(lines 104–141)*: Uses `if/elif` on `lang` to select the appropriate header. Missing `lang` values will result in a file with only the separator line (`===`) and no header — a silent failure. This is a known gap (see `TROUBLESHOOTING.md`).

**Format dispatch block** *(lines 142–215)*: The largest if/elif chain in the script. Each branch handles one or more `lang` types:

#### JSON handling (lines 142–185)
```python
with zipfile.ZipFile(src_file, 'r') as zf:
    json_name = next(n for n in zf.namelist() if n.endswith('.json'))
    with zf.open(json_name) as jf:
        ayah_data = json.load(jf)
```
Opens the ZIP, locates the first `.json` file by name, loads the entire JSON into memory, then iterates surahs/ayahs using `ayah_data.get(key, {})`.

**Edge case:** If an entry is a string (alias pointer), the code does a second lookup:
```python
if isinstance(entry, str):
    entry = ayah_data.get(entry, {})
```

#### Sequential transliteration (lines 186–196)
```python
raw_line = src.readline().rstrip('\n')
text = raw_line.split('|', 1)[1] if '|' in raw_line else ''
```
Reads lines one at a time within the nested surah/ayah loops. The file pointer advances linearly — there is no seek/random-access.

#### Pipe-delimited parsing (lines 197–206)
```python
text = raw_line.split('|', 2)[2] if raw_line.count('|') >= 2 else raw_line
```
Takes everything after the second `|`. Comment lines (starting with `#`) are consumed as ayah lines — this is a latent bug if the source file has header comments before ayah 1:1.

> 💡 **Note:** `en.yusufali.txt` has comments, but they appear at the top before the data. The pipe-delimited parser does not skip them — however, since the outer loop starts at `sura_num=0, ayah_num=1` and reads sequentially, any leading comments would cause misalignment. In practice, `en.yusufali.txt`'s comments are stripped or positioned such that this does not occur.

#### Fallback (lines 207–215)
All remaining `lang` types (`'English'`, `'Arabic'`, `'Hindi'`, `'Urdu'`, `'Roman-*'`) fall through to the `else` branch, which uses simple `readline()` — one line per ayah.

---

## 2. src/gentexforquran.py

**File purpose:** Generates LaTeX content files that will be `\input`-ed (or included) by the PDF template files. Each generated file contains interleaved Arabic quran commands and translation text for all 114 surahs.

### Imports

```python
import os   # Used only for os.makedirs('latex', exist_ok=True)
```

### Constants

`surasize` and `suraname` are the same data as in `gentxtforquran.py`, but defined separately (code duplication). There is no shared constants module.

### Five sequential file-generation blocks

The script has five nearly-identical code blocks, one per PDF edition:

```python
with open('latex/qum.tex', 'w') as farooq_out, \
     open('data/hi.farooq.txt', 'r') as farooq_in:
    for sura_idx in range(114):
        farooq_out.write("\\chapter{%s}\n" % suraname[sura_idx])
        farooq_out.write("\\begin{Arabic}\n\\Huge{\\centerline{\\basmalah}}\\end{Arabic}\n")
        count = 0
        while count < surasize[sura_idx]:
            farooq_out.write("\\flushright{\\begin{Arabic}\n")
            farooq_out.write("\\quranayah[%d][%d]\n" % (sura_idx+1, count+1))
            farooq_out.write("\\end{Arabic}}\n")
            count += 1
            translation_line = farooq_in.readline()
            farooq_out.write("\\flushleft{\\begin{hindi}\n")
            farooq_out.write(translation_line)
            farooq_out.write("\\end{hindi}}\n")
```

**Key LaTeX commands used:**
- `\chapter{name}` — starts a new chapter (surah) in the PDF
- `\basmalah` — renders the Bismillah in Arabic
- `\quranayah[sura][ayah]` — renders the Arabic ayah text via the `quran` LaTeX package
- `\begin{Arabic}...\end{Arabic}` — enables right-to-left Arabic typesetting
- `\begin{hindi}...\end{hindi}` — enables Devanagari typesetting (defined in `quran.sty`)
- `\flushright{...}` / `\flushleft{...}` — alignment wrappers

**Difference between blocks:**
- Hindi blocks use `{hindi}` environment
- English blocks (`qus.tex`, `qut.tex`, `qupk.tex`) emit translation as plain text without a language environment

**Note on Basmalah:** The Basmalah (`\\begin{Arabic}\n\\Huge{\\centerline{\\basmalah}}\\end{Arabic}\n`) is emitted for every surah unconditionally. Surah 9 (At-Tawbah) does not begin with Basmalah in the Qur'an — this may produce a slight inaccuracy in the typeset output. This is a known limitation.

---

## 3. src/gendocshtml.py

**File purpose:** The largest script (≈1,970 lines). Generates the entire `docs/` website — 114 surah pages, homepage, search page, search index, and special pages.

### Structure overview

```
Lines 1-16    : Module docstring and imports (os, re)
Lines 17-150  : SURA_SIZE, SURA_NAME constants
Lines 150-200 : SURAH_REV array (revelation order and Meccan/Medinan classification)
Lines 200-400 : Data loading (reads all input files into memory as lists)
Lines 400-600 : CSS / HTML template strings (inline styles, dark mode)
Lines 600-1800: Main generation loop (114 surah pages)
Lines 1800-2500: index.html, search.html, bookmarks.html, sd/ JSON files, special pages
```

### Data loading pattern

The script reads all source files into memory before generating any HTML. For each `[sura:ayah] text` formatted file:
```python
lines = f.readlines()
# Strip the 3-line header (title + credit + ===)
ayah_lines = [l.rstrip('\n') for l in lines if l.startswith('[')]
```

This populates per-surah data structures that are referenced during HTML generation.

### Per-surah HTML generation

For each surah index 0–113:
1. Collect all ayah data for that surah from in-memory lists
2. Build the complete HTML string for `docs/NNN.html`
3. Write to disk

The HTML includes:
- Inline CSS (light and dark themes)
- Responsive breakpoints (`@media(max-width:600px)`, `@media(max-width:380px)`)
- Print stylesheet override (restores table layout for printing)
- Content Filter checkboxes (one per translation type)
- Per-ayah rows with all content columns

### Search data generation (`docs/sd/`)

The search data is split into 18 small files instead of a single monolithic `search-data.js`:

**`docs/sd/meta.json`** — a JSON array of `[surahNum, ayahNum, "surahName"]` triples for all 6,236 ayahs (~200 KB). Always prefetched when the search page opens.

**`docs/sd/{fieldkey}.json`** — one JSON array per translation field (17 files). Each array has exactly 6,236 strings: one per ayah in Mushaf order. Files are named by field key, e.g., `arabic.json`, `translit-tanzil.json`, `trans-yusuf.json`. They are fetched lazily via `fetch()` only if the user has that field enabled in Settings.

`search.html` uses `Promise.all()` to fetch the required files concurrently, then merges them in memory. Already-loaded files are cached in a module-level map for instant subsequent searches. A default-settings user fetches ~3 MB instead of the former 27 MB monolithic file.

**Why 18 files?** One for metadata + one per translation field (Arabic, 2 transliterations, 5 English, 1 English explanation, 4 Hindi, 1 Gujarati, 1 Nepali, 2 Roman Urdu) = 18 total.

### Per-ayah bookmark system

Each surah page embeds a `toggleBookmark(sura, ayah)` function in `VC_JS`. It reads `localStorage['quran-bookmark']` as an array, finds the entry by `{s, a}` key pair, and either removes it (if found) or unshifts a new `{s, a, n, t}` object. Multiple bookmarks across different surahs accumulate.

`bookmarks.html` is a standalone manager page generated by `gendocshtml.py` that reads the bookmark array, renders each entry with a × Remove button, and provides Export JSON (Blob download) and Import JSON (FileReader + merge-dedup) functionality.

### Last-read tracking

Each surah page unconditionally overwrites `localStorage['quran-history']` with a single `{s, n, t}` object on load. There is no history list — only the most recently visited surah is kept. The homepage reads this key and shows one "Continue Reading" card if present.

### `re` module usage

The `re` module is used to strip `[sura:ayah]` reference prefixes from output lines and for other text cleanup operations. No complex regular expressions are used.

---

## 4. Makefile

**File purpose:** Orchestrates the build pipeline with GNU Make.

```makefile
PYTHON   = python3
LATEX    = xelatex
LATEX_DIR = latex
OUTPUT_DIR = output
```

All variables are overridable from the command line (`make PYTHON=python3.11 generate-txt`).

**Key target: `all`**
```makefile
all: $(OUTPUT_DIR)/farooq.pdf $(OUTPUT_DIR)/suhail.pdf \
     $(OUTPUT_DIR)/sahih.pdf $(OUTPUT_DIR)/translit.pdf \
     $(OUTPUT_DIR)/pickthall.pdf
```
This target is an alias — it depends on all five PDFs. Make will compile only those whose `.tex` sources are newer.

**PDF compilation pattern rule:**
```makefile
$(OUTPUT_DIR)/%.pdf: $(LATEX_DIR)/%.tex | $(OUTPUT_DIR)
    cd $(LATEX_DIR) && $(LATEX) $(<F) && mv $(*F).pdf ../$(OUTPUT_DIR)/
```
`$(<F)` = filename part of the first prerequisite (e.g., `farooq.tex`). The `cd $(LATEX_DIR)` is necessary because XeLaTeX looks for `\input` files relative to the working directory.

**`.PHONY` declaration** prevents Make from treating `all`, `generate-tex`, etc. as file names.

---

## 5. data/ — Input Files

### `ar.quran.txt`
Arabic Uthmani script text, sourced from `tanzil.net`. 6,236 lines, UTF-8. Contains Arabic Unicode characters in the U+0600–U+06FF range plus some extended Arabic characters.

### `en.yusufali.txt`
Pipe-delimited `sura|ayah|text` format. Contains comment lines starting with `#`. The most commonly referenced English translation.

### `surna.txt`
Surah names in Arabic script. Used for metadata display.

### `suranamemal.txt`
Extended surah name data including Malayalam transliterations or additional metadata.

### `translit_en.txt`
Quran Unicode Project transliteration in `num|text` format. Global ayah numbers 1–6,236.

### `*.json.zip` files
Four ZIP archives containing JSON tafsirs/explanations. Files within the ZIP have varying internal names (discovered dynamically via `zf.namelist()`).

| ZIP file | Internal JSON | Key → field |
|----------|--------------|-------------|
| `hindi-mokhtasar.json.zip` | `*.json` | `"sura:ayah"` → `{"text": ...}` |
| `abridged-explanation-of-the-quran.json.zip` | `*.json` | `"sura:ayah"` → `{"text": ...}` |
| `rabila-al-umry-simple.json.zip` | `*.json` | `"sura:ayah"` → `{"t": ...}` |
| `ahl-al-hadith-central-society-of-nepal-simple.json.zip` | `*.json` | `"sura:ayah"` → `{"t": ...}` |

---

## 6. latex/ — LaTeX Templates

### `quran.sty`
The central style file. Defines:
- Font selections (`fontspec`) for Arabic (Amiri/Scheherazade), Hindi (Mangal/Lohit Devanagari), and Latin
- Language environments (`{Arabic}`, `{hindi}`, `{urdu}`)
- Page geometry, spacing, header/footer styles
- Re-exports the `quran` package for `\quranayah` macro

This is the largest file in `latex/` (~1.5 MB) because it may contain embedded font or data, or because it was auto-generated.

### Template files (`farooq.tex`, `suhail.tex`, `sahih.tex`, `translit.tex`, `pickthall.tex`)
Each is a short wrapper that:
1. `\documentclass{book}` with relevant options
2. `\usepackage{quran.sty}` (or similar `\input{quran}`)
3. `\begin{document}`
4. `\input{qXX.tex}` (the generated content file)
5. `\end{document}`

Actual content is in the generated `q*.tex` files. Templates control document-level settings (paper size, font sizes, title page).

---

## 7. archive/ — Legacy Files

### `archive/Readme.txt`
Original project description from before the major reorganization. Documents the original 5 translations (Farooq Khan, Suhail, Saheeh International, Tanzil transliteration, Pickthall). Kept for historical reference.

### `archive/makefile`
The original Makefile used before the project expanded. Contains basic targets for the original 5 PDF editions only.

These files are not used by the current build system and should not be modified.

---

## 8. Root Configuration Files

### `.gitignore`
```
# XeLaTeX build artefacts
latex/*.aux, *.log, *.toc, *.out, *.synctex.gz, *.fls, *.fdb_latexmk

# Generated intermediate LaTeX content files
latex/qum.tex, qup.tex, qus.tex, qut.tex, qupk.tex

# Compiled PDFs (large binary artefacts)
output/*.pdf

# Python cache
__pycache__/, *.pyc, *.pyo, *.pyd

# Virtual environments
.venv/, venv/, env/

# Editor metadata
.vscode/, .idea/, *.swp, *.swo, *~

# OS metadata
.DS_Store, Thumbs.db
```

**Note:** Plain-text output files (`output/*.txt`) are **not** gitignored — they are tracked and committed. PDFs are gitignored because they are large binary files easily regenerated from source.

### `LICENSE`
Unconditional Liberty Instrument (ULI), Version 1.0. A public-domain-equivalent license. Applies to the scripts and configuration files only. Translation texts in `data/` and `output/` remain under their original copyrights.

### `CHANGELOG.md`
Follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format. Documents all significant changes grouped by date and type (Added, Changed, Fixed, Removed).

### `CONTRIBUTING.md`
Contributor guide covering: fork workflow, Python style (PEP 8), data format notes, and issue reporting.

### `README.md`
Main project documentation: live website link, tech stack table, repository structure, prerequisites, usage instructions, audio hosting guide, data sources table, and license.
