# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — 2026-02-22

### Added
- **GitHub Actions workflow** (`.github/workflows/scrape.yml` — "Upload Audio to Hugging Face Hub"):
  manually triggered (`workflow_dispatch`) workflow that downloads the Alafasy 128 kbps audio
  zip from everyayah.com, uploads it to the Hugging Face dataset
  `druvx13/quran-audio-alafasy`, writes `config/audio_config.json` with the resolved
  download URL, and opens a pull request automatically.

---

## [Unreleased] — 2026-02-21

### Added
- **Full-text search page** (`docs/search.html` + `docs/search-data.js`):
  client-side search over Arabic text, Unicode transliteration, Yusuf Ali English, and
  Hindi Tafsir (Mokhtasar) for all 6 236 verses. Results paginate at 20 per page with
  keyword highlighting. URL parameter `?q=` enables deep linking.
- **Verse & Content Filter widget** on every surah page — collapsible
  `<details class="verse-chooser">` with:
  - *Show All* / *Hide All* buttons for verses.
  - *From / To + Apply Range* inputs to display a verse subset.
  - Content checkboxes to show/hide individual row types (Arabic, Audio,
    Transliteration × 2, English × 3, English Explanation, Hindi × 2, Hindi Tafsir).
  - URL hash navigation — range is encoded as `#from-to` or `#ayah`.
- **Surah navigator dropdown** in every page header — `<select>` to jump directly to
  any surah from any page.
- **Search link** in every page header (`🔍 Search`).
- **Yusuf Ali English translation** (`data/en.yusufali.txt`, `sura|ayah|text` format);
  output: `output/quran_english_yusufali.txt`; displayed in HTML as a new row per ayah.
- **Quran Unicode Project transliteration** (`data/translit_en.txt`, sequential `num|text`);
  output: `output/quran_translit_unicode.txt`; shown as a second transliteration row.
- **Abridged Explanation of the Quran** (`data/abridged-explanation-of-the-quran.json.zip`);
  output: `output/quran_english_abridged.txt`; shown as English Explanation row.
- **Hindi Tafsir — Al-Mokhtasar** (`data/hindi-mokhtasar.json.zip`);
  output: `output/quran_hindi_mokhtasar.txt`; shown as Hindi Tafsir row.
- `docs/index.html` now includes a surah navigator dropdown and a link to `search.html`.
- `docs/index.html` Public Domain Notice collapsible via `<details>`/`<summary>`.

### Changed
- **Audio source** moved from local Git LFS (`docs/audio/Alafasy/`) to the Hugging Face
  Space `https://druvx13-quran-audio-alafasy.hf.space/<sura><ayah>.mp3` — resolves
  GitHub Pages LFS pointer display issues.
- `src/gendocshtml.py` expanded from ~384 lines to 758 lines:
  - Added `make_surah_select()` and `make_verse_chooser()` helpers.
  - Added client-side JavaScript (`VC_JS`) for verse range filtering.
  - Added `search-data.js` generation (compact JSON array).
  - Added `search.html` generation with paginated search UI.
  - All `<tr>` elements now carry `data-ayah` attributes for JS filtering.
  - Audio `src` updated to Hugging Face Space URL.
- `src/gentxtforquran.py` updated to generate four additional output files:
  `quran_english_yusufali.txt`, `quran_translit_unicode.txt`,
  `quran_english_abridged.txt`, `quran_hindi_mokhtasar.txt`.
- All 114 surah HTML pages regenerated to include the new content rows, verse
  chooser widget, and surah navigator.

### Fixed
- Audio playback on GitHub Pages (replaced LFS-relative `src` paths with
  `media.githubusercontent.com` URLs, later superseded by the HF Space migration).

---

## [Unreleased] — 2026-02-21 (initial setup)

### Added
- `README.md` — professional project documentation with installation instructions,
  usage examples, directory layout, and tech-stack table.
- `CONTRIBUTING.md` — guidelines for contributors.
- `CHANGELOG.md` — this file.
- `LICENSE` — MIT licence for the project's scripts and configuration.
- `.gitignore` — ignore rules covering XeLaTeX build artefacts (`.aux`, `.log`, `.toc`,
  `.out`, `.synctex.gz`), generated PDF and plain-text outputs, Python cache, editor/OS
  metadata.
- `Makefile` — build file with targets: `all`, `generate-tex`, `generate-txt`,
  `generate-docs`, `clean`.
- **Per-ayah audio recitation** (Mishary Rashid Alafasy) integrated into the HTML website
  via `<audio>` players.
- `src/` directory — Python generator scripts.
- `data/` directory — source translation data files.
- `latex/` directory — LaTeX document templates and `quran.sty`.
- `output/` directory — generated plain-text files and compiled PDFs.
- `archive/` directory — legacy `Readme.txt` and original `makefile`.

### Changed
- Moved all Python scripts → `src/`.
- Moved all source data files → `data/`.
- Moved LaTeX templates and `quran.sty` → `latex/`.
- Moved generated intermediate `.tex` files → `latex/`.
- Moved generated plain-text output files → `output/`.
- Moved compiled PDFs → `output/`.
- Updated all file-path references in the three Python scripts.
- Added `#!/usr/bin/env python3` shebang and module-level docstrings to all scripts.

### Removed (moved to `archive/`)
- `Readme.txt` — superseded by `README.md`.
- `makefile` (lower-case) — superseded by `Makefile`.
