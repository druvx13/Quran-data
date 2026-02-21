# Qur'an — Hindi & English PDF Translations using XeLaTeX

Generate typeset PDF editions of the Qur'an with Arabic text alongside Hindi and English translations, plus a browsable HTML website for each Surah.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| PDF typesetting | [XeLaTeX](https://xetex.sourceforge.net/) with `polyglossia`, `fontspec`, `quran` packages |
| Script language | Python 3 |
| Web output | Static HTML (GitHub Pages via `docs/`) |
| Build system | GNU Make |

---

## Repository Structure

```
.
├── src/                    # Python generator scripts
│   ├── gentexforquran.py   # Generate intermediate LaTeX content files
│   ├── gentxtforquran.py   # Generate formatted plain-text output files
│   └── gendocshtml.py      # Generate static HTML documentation (docs/)
├── data/                   # Source translation data (input)
│   ├── ar.quran.txt                         # Arabic Uthmani script (one line per ayah)
│   ├── hi.farooq.txt                        # Hindi – Muhammad Farooq Khan & Muhammad Ahmed
│   ├── hi.hindi.txt                         # Hindi – Suhel Farooq Khan & Saifur Rahman Nadwi
│   ├── en.sahih.txt                         # English – Saheeh International
│   ├── en.pickthall.txt                     # English – Mohammed Marmaduke Pickthall
│   ├── en.yusufali.txt                      # English – Abdullah Yusuf Ali (sura|ayah|text)
│   ├── en.transliteration.txt               # English transliteration (Tanzil.net, sequential)
│   ├── translit_en.txt                      # English transliteration (Quran Unicode Project, sequential)
│   ├── abridged-explanation-of-the-quran.json.zip  # English Explanation (Abridged, JSON)
│   ├── hindi-mokhtasar.json.zip             # Hindi Tafsir – Al-Mokhtasar (JSON)
│   ├── suranamemal.txt                      # Surah name data (Malayalam script)
│   └── surna.txt                            # Surah name reference data
├── latex/                  # LaTeX document sources & generated content
│   ├── farooq.tex          # Main document – Farooq Khan Hindi translation
│   ├── suhail.tex          # Main document – Suhel Farooq Khan Hindi translation
│   ├── sahih.tex           # Main document – Saheeh International English
│   ├── translit.tex        # Main document – English transliteration
│   ├── pickthall.tex       # Main document – Pickthall English
│   ├── quran.sty           # Custom LaTeX style (Arabic ayah macros)
│   └── q*.tex              # Generated content files (created by gentexforquran.py)
├── output/                 # Generated output files (plain text & PDFs)
├── trans/                  # Transliteration source with HTML tags (used by gendocshtml.py)
├── docs/                   # Generated static HTML – GitHub Pages
│   ├── audio/Alafasy/      # Audio recitation MP3s – Mishary Rashid Alafasy
│   ├── index.html          # Surah index page
│   └── 001.html … 114.html # Per-surah pages
├── archive/                # Archived legacy files
├── Makefile
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

---

## Translations Included

### PDF outputs

| File | Language | Translator |
|------|----------|-----------|
| `farooq.pdf` | Hindi | Muhammad Farooq Khan & Muhammad Ahmed |
| `suhail.pdf` | Hindi | Suhel Farooq Khan & Saifur Rahman Nadwi |
| `sahih.pdf` | English | Saheeh International |
| `translit.pdf` | Transliteration | Tanzil.net |
| `pickthall.pdf` | English | Mohammed Marmaduke Pickthall (1930, Public Domain) |

### HTML website (GitHub Pages)

Each per-surah HTML page includes all of the following side-by-side:

| Content | Source |
|---------|--------|
| Arabic text (Uthmani script) | tanzil.net |
| Audio recitation | Mishary Rashid Alafasy – versebyversequran.com |
| Transliteration | Tanzil.net (HTML-tagged) |
| Transliteration | Quran Unicode Project |
| English translation | Pickthall (1930, Public Domain) |
| English translation | Abdullah Yusuf Ali (Public Domain) |
| English translation | Saheeh International |
| English explanation | Abridged Explanation of the Quran |
| Hindi translation (हिन्दी अनुवाद) | Muhammad Farooq Khan & Muhammad Ahmed |
| Hindi translation (हिन्दी अनुवाद) | Suhel Farooq Khan & Saifur Rahman Nadwi |
| Hindi Tafsir (हिन्दी तफ्सीर) | Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim |

Arabic text uses the Standard Arabic Uthmani Script sourced from [tanzil.net](https://tanzil.net).

---

## Prerequisites

- **XeLaTeX** — part of TeX Live or MiKTeX distributions
  - Required fonts: `Scheherazade` (Arabic), `Lohit Hindi` (Devanagari)
  - Required LaTeX packages: `polyglossia`, `fontspec`, `forloop`, `hyperref`, `menukeys`, `hologo`
- **Python 3.6+**
- **GNU Make** (optional, for convenience)

---

## Installation

### Ubuntu / Debian
```bash
sudo apt-get install texlive-xetex texlive-lang-arabic texlive-lang-other \
     fonts-lohit-deva fonts-smc-rachana python3
```

### macOS
```bash
brew install --cask mactex
brew install python3
```

---

## Usage

### 1. Generate intermediate LaTeX content files

```bash
python3 src/gentexforquran.py
```

This reads from `data/` and writes `latex/qum.tex`, `latex/qup.tex`, `latex/qus.tex`,
`latex/qut.tex`, and `latex/qupk.tex`.

### 2. Compile PDFs

```bash
# Using Make (all PDFs):
make all

# Or compile individually:
cd latex && xelatex farooq.tex    # → output/farooq.pdf  (Hindi – Farooq Khan)
cd latex && xelatex suhail.tex    # → output/suhail.pdf  (Hindi – Suhel Farooq Khan)
cd latex && xelatex sahih.tex     # → output/sahih.pdf   (English – Saheeh International)
cd latex && xelatex translit.tex  # → output/translit.pdf (Transliteration)
cd latex && xelatex pickthall.tex # → output/pickthall.pdf (English – Pickthall)
```

### 3. Generate formatted plain-text outputs

```bash
python3 src/gentxtforquran.py
```

Produces `output/quran_hindi_farooq.txt`, `output/quran_hindi_suhail.txt`,
`output/quran_hindi_mokhtasar.txt`, `output/quran_english_sahih.txt`,
`output/quran_english_yusufali.txt`, `output/quran_english_translit.txt`,
`output/quran_english_pickthall.txt`, `output/quran_english_abridged.txt`,
`output/quran_translit_unicode.txt`, and `output/quran_arabic.txt`.

### 4. Regenerate HTML documentation (GitHub Pages)

```bash
# First generate the plain-text outputs (step 3 above), then:
python3 src/gendocshtml.py
```

This regenerates the `docs/` HTML pages used for the GitHub Pages site.  Each
page embeds Arabic text, an audio player (Mishary Rashid Alafasy recitation
from `docs/audio/Alafasy/`), transliteration, and all translations listed in
the **HTML website** table above.

### Make targets

```bash
make all           # Generate all PDFs
make generate-tex  # Run gentexforquran.py
make generate-txt  # Run gentxtforquran.py
make generate-docs # Run gendocshtml.py
make clean         # Remove LaTeX build artefacts (aux, log, toc, out)
```

---

## Data Sources

- **Arabic text**: Standard Arabic Uthmani Script — [tanzil.net](https://tanzil.net)
- **Hindi translations**: Downloaded from [zekr.org](http://zekr.org)
- **Hindi Tafsir**: Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim (JSON)
- **English translations**: [tanzil.net](https://tanzil.net) and Pickthall (1930, Public Domain)
- **English translation**: Abdullah Yusuf Ali (Public Domain)
- **English Explanation**: Abridged Explanation of the Quran (JSON)
- **Transliteration (Unicode)**: Quran Unicode Project (`translit_en.txt`)
- **Audio recitation**: Mishary Rashid Alafasy — [versebyversequran.com](https://versebyversequran.com)

---

## License

This project's scripts and configuration are licensed under the [MIT License](LICENSE).

The translation texts are reproduced verbatim and are subject to their respective original
copyrights. The Pickthall translation (1930) is in the public domain. All other translations
are used for non-commercial, educational purposes.
