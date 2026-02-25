# Qur'an — Multi-Translation Study Website & PDF Typesetting

A static HTML website (GitHub Pages) for side-by-side study of the Qur'an — Arabic text, audio recitation, two transliterations, three English translations, an English explanation, two Hindi translations, and a Hindi Tafsir — plus typeset PDF editions generated with XeLaTeX.

[![License: ULI](https://img.shields.io/badge/License-ULI%201.0-blue.svg)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-live-brightgreen)](https://druvx13.github.io/Quran-data/)

---

## Live Website

[**https://druvx13.github.io/Quran-data/**](https://druvx13.github.io/Quran-data/)

Features:
- **114 Surah pages** — every ayah displayed with all content streams
- **Full-text search** (`search.html`) — searches Arabic, transliteration, Yusuf Ali translation, and Hindi Tafsir; results paginated with match highlighting
- **Surah navigator** — jump to any surah via a dropdown in the page header
- **Verse & Content Filter** — collapsible widget per surah to show specific verse ranges and toggle individual content rows on/off
- **Audio recitation** — per-ayah audio player (Mishary Rashid Alafasy, 128 kbps), streamed from Hugging Face Space

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| PDF typesetting | [XeLaTeX](https://xetex.sourceforge.net/) with `polyglossia`, `fontspec`, `quran` packages |
| Script language | Python 3.6+ |
| Web output | Static HTML (GitHub Pages via `docs/`) |
| Build system | GNU Make |
| Audio hosting | [Hugging Face Space](https://huggingface.co/spaces/druvx13/quran-audio-alafasy) (`druvx13-quran-audio-alafasy.hf.space`) |

---

## Repository Structure

```
.
├── src/                    # Python generator scripts
│   ├── gentexforquran.py   # Generate intermediate LaTeX content files
│   ├── gentxtforquran.py   # Generate formatted plain-text output files
│   └── gendocshtml.py      # Generate static HTML docs (docs/) + search-data.js
├── data/                   # Source translation data (input — do not modify)
│   ├── ar.quran.txt                         # Arabic Uthmani script (one line per ayah)
│   ├── hi.farooq.txt                        # Hindi – Muhammad Farooq Khan & Muhammad Ahmed
│   ├── hi.hindi.txt                         # Hindi – Suhel Farooq Khan & Saifur Rahman Nadwi
│   ├── en.sahih.txt                         # English – Saheeh International (one line per ayah)
│   ├── en.pickthall.txt                     # English – Pickthall (one line per ayah)
│   ├── en.yusufali.txt                      # English – Yusuf Ali (sura|ayah|text format)
│   ├── en.transliteration.txt               # Transliteration – Tanzil.net (one line per ayah)
│   ├── translit_en.txt                      # Transliteration – Quran Unicode Project (num|text)
│   ├── abridged-explanation-of-the-quran.json.zip  # English Explanation (JSON, "sura:ayah" keys)
│   ├── hindi-mokhtasar.json.zip             # Hindi Tafsir – Al-Mokhtasar (JSON, "sura:ayah" keys)
│   ├── rabila-al-umry-simple.json.zip       # Gujarati – Rabila Al-Umry (JSON, "sura:ayah" keys, "t" field)
│   ├── suranamemal.txt                      # Surah names – Malayalam script
│   └── surna.txt                            # Surah name reference data
├── latex/                  # LaTeX document sources & generated content
│   ├── farooq.tex          # Main document – Farooq Khan Hindi translation
│   ├── suhail.tex          # Main document – Suhel Farooq Khan Hindi translation
│   ├── sahih.tex           # Main document – Saheeh International English
│   ├── translit.tex        # Main document – Tanzil.net transliteration
│   ├── pickthall.tex       # Main document – Pickthall English
│   ├── hindi_mokhtasar.tex # Main document – Hindi Tafsir (Al-Mokhtasar) with Arabic & transliteration
│   ├── hilali.tex          # Main document – Hilali & Khan English translation with Arabic
│   ├── quran.sty           # Custom LaTeX style (Arabic ayah macros)
│   └── q*.tex              # Generated content files (written by gentexforquran.py)
├── output/                 # Generated output files
│   ├── quran_arabic.txt
│   ├── quran_english_pickthall.txt
│   ├── quran_english_sahih.txt
│   ├── quran_english_translit.txt
│   ├── quran_english_yusufali.txt
│   ├── quran_english_abridged.txt
│   ├── quran_english_hilali.txt
│   ├── quran_hindi_farooq.txt
│   ├── quran_hindi_suhail.txt
│   ├── quran_hindi_mokhtasar.txt
│   ├── quran_gujarati_rabila.txt
│   ├── quran_translit_unicode.txt
│   ├── farooq.pdf          # Compiled PDF
│   ├── suhail.pdf          # Compiled PDF
│   ├── hindi_mokhtasar.pdf # Compiled PDF (Arabic + transliteration + Hindi Tafsir)
│   └── hilali.pdf          # Compiled PDF (Arabic + Hilali & Khan English translation)
├── trans/                  # Tanzil.net transliteration with HTML tags (used by gendocshtml.py)
│   └── en.transliteration.txt
├── docs/                   # Generated static HTML – GitHub Pages
│   ├── index.html          # Surah index (with surah navigator + search link)
│   ├── search.html         # Client-side full-text search page
│   ├── search-data.js      # Search index (compact JSON, all 6236 verses)
│   └── 001.html … 114.html # Per-surah pages
├── archive/                # Legacy files (Readme.txt, original makefile)
├── Makefile
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

---

## Translations & Content

### PDF outputs

| Output file | Language | Translator |
|-------------|----------|-----------|
| `output/farooq.pdf` | Hindi | Muhammad Farooq Khan & Muhammad Ahmed |
| `output/suhail.pdf` | Hindi | Suhel Farooq Khan & Saifur Rahman Nadwi |
| *(sahih.pdf — build locally)* | English | Saheeh International |
| *(translit.pdf — build locally)* | Transliteration | Tanzil.net |
| *(pickthall.pdf — build locally)* | English | Pickthall (1930, Public Domain) |
| `output/hindi_mokhtasar.pdf` | Hindi Tafsir | Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim |
| `output/hilali.pdf` | English | Dr. Muhammad Taqi-ud-Din Al-Hilali & Dr. Muhammad Muhsin Khan |

### HTML website content per ayah

| Row | Content | Source |
|-----|---------|--------|
| Arabic | Arabic text (Uthmani script) | [tanzil.net](https://tanzil.net) |
| Audio | Recitation player | Mishary Rashid Alafasy (128 kbps) — [HF Space](https://druvx13-quran-audio-alafasy.hf.space) |
| Transliteration | Tanzil.net | `trans/en.transliteration.txt` (HTML-tagged) |
| Transliteration | Quran Unicode Project | `data/translit_en.txt` |
| English | Pickthall (1930, Public Domain) | `data/en.pickthall.txt` |
| English | Yusuf Ali (Public Domain) | `data/en.yusufali.txt` |
| English | Saheeh International | `data/en.sahih.txt` |
| English Explanation | Abridged Explanation of the Quran | `data/abridged-explanation-of-the-quran.json.zip` |
| Hindi (हिन्दी) | Muhammad Farooq Khan & Muhammad Ahmed | `data/hi.farooq.txt` |
| Hindi (हिन्दी) | Suhel Farooq Khan & Saifur Rahman Nadwi | `data/hi.hindi.txt` |
| Hindi Tafsir (हिन्दी तफ्सीर) | Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim | `data/hindi-mokhtasar.json.zip` |
| Gujarati (ગુજરાતી) | Rabila Al-Umry | `data/rabila-al-umry-simple.json.zip` |

---

## Prerequisites

- **XeLaTeX** (for PDF compilation only) — TeX Live or MiKTeX
  - Required fonts: `Scheherazade` / `Scheherazade New` (Arabic), `Lohit Hindi` (Devanagari)
  - Required packages: `polyglossia`, `fontspec`, `forloop`, `hyperref`, `menukeys`, `hologo`
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

Reads from `data/` and writes `latex/qum.tex`, `latex/qup.tex`, `latex/qus.tex`,
`latex/qut.tex`, and `latex/qupk.tex`.

### 2. Compile PDFs

```bash
# All PDFs via Make (step 1 must be run first):
make all

# Or individually:
cd latex && xelatex farooq.tex          # → output/farooq.pdf
cd latex && xelatex suhail.tex          # → output/suhail.pdf
cd latex && xelatex sahih.tex           # → output/sahih.pdf
cd latex && xelatex translit.tex        # → output/translit.pdf
cd latex && xelatex pickthall.tex       # → output/pickthall.pdf
cd latex && xelatex hindi_mokhtasar.tex # → output/hindi_mokhtasar.pdf
```

### 3. Generate formatted plain-text outputs

```bash
python3 src/gentxtforquran.py
```

Produces eleven files in `output/`:

| Output file | Source |
|-------------|--------|
| `quran_arabic.txt` | `data/ar.quran.txt` |
| `quran_english_pickthall.txt` | `data/en.pickthall.txt` |
| `quran_english_sahih.txt` | `data/en.sahih.txt` |
| `quran_english_translit.txt` | `data/en.transliteration.txt` |
| `quran_english_yusufali.txt` | `data/en.yusufali.txt` |
| `quran_english_abridged.txt` | `data/abridged-explanation-of-the-quran.json.zip` |
| `quran_hindi_farooq.txt` | `data/hi.farooq.txt` |
| `quran_hindi_suhail.txt` | `data/hi.hindi.txt` |
| `quran_hindi_mokhtasar.txt` | `data/hindi-mokhtasar.json.zip` |
| `quran_gujarati_rabila.txt` | `data/rabila-al-umry-simple.json.zip` |
| `quran_translit_unicode.txt` | `data/translit_en.txt` |

All output files use the `[sura:ayah] text` format, grouped by surah.

### 4. Regenerate the HTML website (GitHub Pages)

```bash
# Step 3 must be run first, then:
python3 src/gendocshtml.py
```

Regenerates all 114 surah pages, `docs/index.html`, `docs/search.html`, and
`docs/search-data.js`.

**Audio note:** Audio players stream MP3 files from
`https://druvx13-quran-audio-alafasy.hf.space/<sura><ayah>.mp3`.

### Make targets

```bash
make all           # Compile all PDFs (requires generate-tex first)
make generate-tex  # Run gentexforquran.py
make generate-txt  # Run gentxtforquran.py
make generate-docs # Run gendocshtml.py (requires generate-txt first)
make clean         # Remove LaTeX build artefacts (.aux, .log, .toc, .out, .synctex.gz)
```

---

## Hosting Your Own Audio Server

The audio players in `docs/` stream MP3 files from a Hugging Face Space that acts as
a simple open-directory HTTP server. If you want to host the Alafasy recitation yourself
(on Hugging Face Spaces, a VPS, or any Docker-capable host), use the following
`Dockerfile`:

```dockerfile
# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install required tools for downloading and unzipping
RUN apt-get update && \
    apt-get install -y wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Create a folder specifically for the public files
RUN mkdir -p /app/public

# Download the specific zip file
RUN wget -q https://everyayah.com/data/Alafasy_128kbps/000_versebyverse.zip -O /app/000_versebyverse.zip

# Extract the verses into the public folder
RUN unzip -q /app/000_versebyverse.zip -d /app/public/

# Clean up the original zip file to save disk space
RUN rm /app/000_versebyverse.zip

# Hugging Face Spaces expose port 7860 by default
EXPOSE 7860

# Switch working directory to the public folder so the server roots here
WORKDIR /app/public

# Start Python's built-in HTTP server to create the Open Directory
CMD ["python", "-m", "http.server", "7860"]
```

⚠️ In case this doesn't work
```
https://everyayah.com/data/Alafasy_128kbps/000_versebyverse.zip
```
, you may try 
```
https://web.archive.org/web/20260222041205/https://everyayah.com/data/Alafasy_128kbps/000_versebyverse.zip
```

Deploy this image on Hugging Face Spaces (Docker SDK), a VPS, or any Docker host.
Once running, update the audio `src` URLs in `src/gendocshtml.py` (look for
`hf.space` in the file) to point at your server, then re-run `python3 src/gendocshtml.py`.

---

## Data Sources

| Data | Source |
|------|--------|
| Arabic text (Uthmani script) | [tanzil.net](https://tanzil.net) |
| Hindi translations | [zekr.org](http://zekr.org) |
| Hindi Tafsir (Al-Mokhtasar) | Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim (JSON) |
| English translations (Tanzil.net, Saheeh) | [tanzil.net](https://tanzil.net) |
| English translation (Pickthall, 1930) | Public Domain |
| English translation (Yusuf Ali) | Public Domain |
| English Explanation (Abridged) | Abridged Explanation of the Quran (JSON) |
| Transliteration (Unicode) | Quran Unicode Project |
| Audio recitation | Mishary Rashid Alafasy, 128 kbps — [versebyversequran.com](https://versebyversequran.com) / [HF Hub](https://huggingface.co/datasets/druvx13/quran-audio-alafasy) |

---

## License

```
Copyright (C) 2026 Anonymous
This Work is licensed under the Unconditional Liberty Instrument (ULI), Version 1.0.
A copy of the License is included herein or is available at LICENSE.
```

This project's scripts and configuration are licensed under the [Unconditional Liberty Instrument (ULI), Version 1.0](LICENSE).

The translation texts, audio, and explanation data are reproduced verbatim and are subject
to their respective original copyrights and licenses. The Pickthall (1930) and Yusuf Ali
translations are in the public domain. All other translations and data are used for
non-commercial, educational purposes.
