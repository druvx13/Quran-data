# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — 2026-02-21

### Added
- **Audio recitation** embedded in every per-surah HTML page — Mishary Rashid Alafasy MP3 files stored in `docs/audio/Alafasy/` (sourced from versebyversequran.com; see `docs/audio/Alafasy/000_license.html`).
- **Yusuf Ali English translation** (`data/en.yusufali.txt`) — `sura|ayah|text` pipe-delimited format; output: `output/quran_english_yusufali.txt`.
- **Quran Unicode Project transliteration** (`data/translit_en.txt`) — sequential one-line-per-ayah format; output: `output/quran_translit_unicode.txt`.
- **Abridged Explanation of the Quran** (`data/abridged-explanation-of-the-quran.json.zip`) — JSON data; output: `output/quran_english_abridged.txt`.
- **Hindi Tafsir — Al-Mokhtasar** (`data/hindi-mokhtasar.json.zip`) — JSON data; output: `output/quran_hindi_mokhtasar.txt`.
- `src/gentxtforquran.py` now generates five additional output files: `quran_english_yusufali.txt`, `quran_translit_unicode.txt`, `quran_english_abridged.txt`, `quran_hindi_mokhtasar.txt`.
- `src/gendocshtml.py` now renders all ten content streams per ayah (Arabic, audio, two transliterations, three English translations, English explanation, two Hindi translations, Hindi Tafsir).
- `docs/index.html` updated with full source attribution for all new content streams.

### Changed
- Each per-surah HTML page now renders twelve table rows per ayah (one ayah-number separator row + eleven content rows: Arabic, audio, two transliterations, three English translations, English explanation, two Hindi translations, Hindi Tafsir).

---

## [Unreleased] — 2026-02-20

### Added
- `README.md` — professional project documentation with installation instructions, usage examples, directory layout, and tech-stack table.
- `CONTRIBUTING.md` — guidelines for contributors covering Python style, LaTeX templates, HTML docs, and translation data.
- `CHANGELOG.md` — this file.
- `LICENSE` — MIT licence for the project's scripts and configuration.
- `.gitignore` — comprehensive ignore rules covering XeLaTeX build artefacts (`.aux`, `.log`, `.toc`, `.out`), generated PDF and plain-text outputs, Python cache files, and editor/OS metadata.
- `Makefile` — updated build file (capitalized, standard convention) with targets: `all`, `generate-tex`, `generate-txt`, `generate-docs`, `clean`.
- `src/` directory — Python generator scripts now live here.
- `data/` directory — source translation data files (input) now live here.
- `latex/` directory — LaTeX document templates and `quran.sty` now live here.
- `output/` directory — generated plain-text files and compiled PDFs now live here.
- `archive/` directory — legacy files (`Readme.txt`, original `makefile`) preserved here.

### Changed
- Moved `gentexforquran.py`, `gentxtforquran.py`, `gendocshtml.py` → `src/`.
- Moved source data files (`ar.quran.txt`, `hi.farooq.txt`, `hi.hindi.txt`, `en.sahih.txt`, `en.pickthall.txt`, `en.transliteration.txt`, `suranamemal.txt`, `surna.txt`) → `data/`.
- Moved LaTeX templates and `quran.sty` → `latex/`.
- Moved generated intermediate tex files (`qum.tex`, `qup.tex`, `qus.tex`, `qut.tex`, `qupk.tex`) → `latex/` (co-located with the templates that `\input` them).
- Moved generated plain-text output files (`quran_*.txt`) → `output/`.
- Moved compiled PDFs (`farooq.pdf`, `suhail.pdf`) → `output/`.
- Updated all file-path references in `src/gentexforquran.py`, `src/gentxtforquran.py`, and `src/gendocshtml.py` to reflect the new directory structure.
- Updated shebang lines to `#!/usr/bin/env python3` and added module-level docstrings to all scripts.
- Archived `Readme.txt` and original `makefile` → `archive/`.

### Removed (moved to `archive/`)
- `Readme.txt` — superseded by `README.md`.
- `makefile` (lower-case) — superseded by `Makefile`.
