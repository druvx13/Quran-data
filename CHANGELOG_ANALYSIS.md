# Changelog Analysis

A structured analysis of this project's evolution based on `CHANGELOG.md`. Covers major milestones, architectural shifts, and the growth trajectory of the data set.

<!-- TOC -->
- [1. Project Origins](#1-project-origins)
- [2. Chronological Milestones](#2-chronological-milestones)
  - [2.1 Foundation Phase: 5 Translations, 5 PDFs](#21-foundation-phase-5-translations-5-pdfs)
  - [2.2 Urdu Expansion (Multiple updates)](#22-urdu-expansion-multiple-updates)
  - [2.3 HTML Website Launch](#23-html-website-launch)
  - [2.4 Repository Reorganisation (Consolidation of trans/)](#24-repository-reorganisation-consolidation-of-trans)
  - [2.5 Major Translation Expansion (Feb 2026)](#25-major-translation-expansion-feb-2026)
  - [2.6 Hindi Al-Omari Addition](#26-hindi-al-omari-addition)
  - [2.7 Additional Languages (Gujarati, Nepali, Roman Scripts)](#27-additional-languages-gujarati-nepali-roman-scripts)
  - [2.8 fawazahmed0/quran-api Batch (27 new files, Feb 2026)](#28-fawazahmed0quran-api-batch-27-new-files-feb-2026)
- [3. Growth Metrics](#3-growth-metrics)
- [4. Breaking Changes History](#4-breaking-changes-history)
- [5. Recurring Patterns](#5-recurring-patterns)
<!-- /TOC -->

---

## 1. Project Origins

The project began as a simple XeLaTeX PDF typesetting exercise for a small number of Qur'an translations. The `archive/Readme.txt` documents the original scope: 5 translations compiled into PDFs using `gentextforquran.py` and basic LaTeX templates.

The original 5 translations:
1. Muhammad Farooq Khan & Muhammad Ahmed (Hindi) → `farooq.pdf`
2. Suhel Farooq Khan & Saifur Rahman Nadwi (Hindi) → `suhail.pdf`
3. Saheeh International (English) → `sahih.pdf`
4. Tanzil.net (English Transliteration) → `translit.pdf`
5. Mohammed Marmaduke Pickthall (English) → `pickthall.pdf`

---

## 2. Chronological Milestones

### 2.1 Foundation Phase: 5 Translations, 5 PDFs

**What changed:** Established the core pipeline — Python scripts reading from `data/`, generating LaTeX content files, compiled to PDF with XeLaTeX.

**Architecture introduced:**
- `gentexforquran.py` → `latex/q*.tex` → XeLaTeX → `output/*.pdf`
- `data/` directory with `ar.quran.txt`, `en.sahih.txt`, `en.pickthall.txt`, `en.transliteration.txt`, `hi.farooq.txt`, `hi.hindi.txt`

### 2.2 Urdu Expansion (Multiple updates)

**What changed:** Multiple Urdu translations from Tanzil.net were added: Jalandhry, Ahmed Ali, Jawadi, Kanz ul Iman, Maududi, Qadri, Junagarhi, Najafi. Later, Urdu translations from quran.com were added: Mahmud al-Hasan, Fe Zilal al-Quran, Bayan-ul-Quran, Wahiduddin Khan. Roman Urdu (Maududi from quran.com) was also added.

**New language-type identifiers introduced:** `Urdu`, `Urdu-SuraAyah`, `Roman-Urdu`

**Impact:** `gentxtforquran.py` grew from a small script to one covering 44 output files, with expanded `if/elif` dispatch logic.

### 2.3 HTML Website Launch

**What changed:** `src/gendocshtml.py` was created, generating the full 114-surah static website in `docs/`. This introduced:
- Per-surah HTML pages (`docs/001.html` … `docs/114.html`)
- `docs/index.html` with surah grid
- `docs/search.html` with full-text search
- `docs/search-data.js` pre-built search index (later replaced by `docs/sd/` lazy-loaded files in §2.9)
- Audio players streaming from Hugging Face Space
- Content Filter widget (per-ayah translation toggles)
- Dark/light mode support

**Architecture introduced:** `output/*.txt` → `gendocshtml.py` → `docs/`

### 2.4 Repository Reorganisation (Consolidation of trans/)

**What changed:** The `trans/` directory (previously a separate directory for Tanzil.net-format files) was removed. Files were moved and renamed:
- `trans/en.transliteration.txt` → `data/en.transliteration.tanzil.txt`
- `trans/en.pickthall.txt` → `data/en.pickthall.tanzil.txt`
- `trans/en.sahih.trans.zip` → `data/en.sahih.trans.zip`

**Impact:** `gendocshtml.py` updated to reference `data/en.transliteration.tanzil.txt`. `README.md` and `CONTRIBUTING.md` updated to remove `trans/`.

**Rationale:** Consolidating all source data into one `data/` directory simplifies the project layout.

**Responsive HTML redesign:** Mobile layout improvements were made at the same time:
- Responsive table with `@media(max-width:600px)`
- Additional breakpoint at `@media(max-width:380px)`
- Print stylesheet preserving table layout
- Touch-friendly button sizes (`min-height: 44px`)

### 2.5 Major Translation Expansion (Feb 2026)

**What changed:** 12 new English translations were added from Tanzil.net:
Ahmed Ali, Ahmed Raza Khan, A. J. Arberry, Abdul Majid Daryabadi, Talal Itani, Abul Ala Maududi (English), Safi-ur-Rahman al-Mubarakpuri, Hasan al-Fatih Qaribullah, Muhammad Sarwar, Mohammad Habib Shakir, Wahiduddin Khan, Rowwad Translation Center.

3 more from public APIs:
Muhammad Asad (alquran.cloud), Mufti Taqi Usmani (quran.com), M.A.S. Abdel Haleem (quran.com).

The Hindi translation by Azizul Haq Al-Omari was also added (quranenc.com).

**Impact:** `gentxtforquran.py` grew to 44 output files. New website rows and CSS classes were added in `gendocshtml.py`.

### 2.6 Hindi Al-Omari Addition

**What changed:** `data/hi.omari.txt` added (Azizul Haq Al-Omari Hindi translation from quranenc.com). New CSS classes `.hindi-omari` and `.hindi-omari-text`. New Content Filter checkbox added to all 114 surah pages.

**Source:** Fetched from quranenc.com API (`hindi_omari`); footnote markers stripped, whitespace normalized.

### 2.7 Additional Languages (Gujarati, Nepali, Roman Scripts)

**What changed:** Gujarati translation (Rabila Al-Umry) added from JSON ZIP. Nepali translation (Ahl-al-Hadith Central Society of Nepal) added from JSON ZIP.

**New language-type identifiers introduced:** `Gujarati-JSON`, `Nepali-JSON`

Roman Urdu Junagarhi added from fawazahmed0/quran-api.

### 2.8 fawazahmed0/quran-api Batch (27 new files, Feb 2026)

**What changed:** A large batch of 27 new data files from fawazahmed0/quran-api (served via jsdelivr CDN):

- 21 new English translations
- 3 Romanized Hindi translations
- 2 new Urdu translations (Karam Shah Al-Azhari, Muhammad Taqi Usmani)
- 1 Romanized Gujarati translation (Rabila Al-Omari)

**New language-type identifiers introduced:** `Roman-Hindi`, `Roman-Gujarati`

**Impact:** `gentxtforquran.py` grew to 71 output files. The `translations` list now spans ~100 lines of code.

### 2.9 Reader Features: Lazy Search, Bookmarks, Last-Read (Mar 2026)

**What changed:** Three new client-side reader features added to the website via `gendocshtml.py`:

- **Config-aware lazy search:** Replaced the monolithic `search-data.js` (~27 MB) with 18 small files in `docs/sd/` loaded on demand via `fetch()`. `sd/meta.json` (~200 KB) is prefetched; per-field JSONs are fetched lazily only for fields the user has enabled in Settings. A default-settings user now downloads ~3 MB instead of 27 MB.
- **Multi-bookmark system:** Each verse has a 🔖 button. `localStorage['quran-bookmark']` is now a newest-first array of `{s, a, n, t}` objects. A dedicated `bookmarks.html` page provides a full manager with per-entry Remove, Export JSON, and Import JSON capabilities.
- **Single last-read entry:** `localStorage['quran-history']` stores a single `{s, n, t}` object — only the most recently visited surah. Homepage shows one "Continue Reading" card.

**New generated files:** `docs/sd/meta.json`, `docs/sd/*.json` (17 files), `docs/bookmarks.html`

---

## 3. Growth Metrics

| Metric | Initial state | Current state |
|--------|--------------|---------------|
| Number of translations | 5 | 71 |
| Languages covered | 3 (Arabic, English, Hindi) | 8+ (Arabic, English, Hindi, Urdu, Roman Urdu, Roman Hindi, Gujarati, Roman Gujarati, Nepali, Transliteration) |
| Output plain-text files | 5 | 71 |
| PDFs | 5 | 5 (unchanged) |
| Website pages | 0 (no website) | 122+ (114 surah + index, search, bookmarks, config, sources, license, download) |
| Source data files | ~6 | 80+ |
| Data sources | 2 (tanzil.net, zekr.org) | 7+ (tanzil.net, quranenc.com, alquran.cloud, quran.com, fawazahmed0/quran-api, JSON ZIPs, Quran Unicode Project) |
| Lines of Python | ~50 | ~2,500+ |

---

## 4. Breaking Changes History

The following changes required downstream updates (re-running generators):

| Change | Impact | Mitigation |
|--------|--------|------------|
| `trans/` directory consolidated into `data/` | `gendocshtml.py` path references changed | Updated script to use new paths |
| New HTML template structure (responsive redesign) | All 114 HTML pages regenerated with new structure | Run `gendocshtml.py` |
| Content Filter widget added to surah pages | Page structure changed; old HTML files incompatible | Run `gendocshtml.py` |
| Audio URL moved to Hugging Face Space | Previous audio source became non-functional | Updated URL in `gendocshtml.py` |

---

## 5. Recurring Patterns

Across the project's history, several patterns repeat:

1. **Batch data additions:** New translations are added in batches from a single source (e.g., "12 English translations from Tanzil.net", "27 files from fawazahmed0/quran-api"). This reflects the ease of bulk download from structured APIs.

2. **Script extension over refactoring:** The `gentxtforquran.py` script has grown by adding new entries to the `translations` list and new `elif` branches to the dispatch logic, rather than being refactored into a more abstract data-driven system.

3. **HTML regeneration on content updates:** Every time a new translation is added to the website, all 114 surah HTML pages must be regenerated (because each page shows all translations). This is the cost of the static generation approach.

4. **Naming convention evolution:** Early files use short codes (e.g., `en.sahih.txt`); later additions from fawazahmed0/quran-api follow the same pattern. Romanized versions add `roman.` prefix (e.g., `hi.roman.farooq.txt`).

5. **Source diversification:** The project started with 2 data sources (tanzil.net and zekr.org). Over time, it expanded to 7+ sources. Each new source may have slightly different data formats, requiring new parsing logic or data cleaning steps.
