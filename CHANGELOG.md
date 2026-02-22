# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — 2026-02-22

### Added
- `data/en.yusufali.txt` — English translation by Abdullah Yusuf Ali (pipe-delimited `sura|ayah|text` format).
- `data/translit_en.txt` — English transliteration, sequential global-ayah format (Quran Unicode Project).
- `data/hindi-mokhtasar.json.zip` — Hindi Tafsir data (Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim) in JSON format.
- `data/abridged-explanation-of-the-quran.json.zip` — English Explanation (Abridged) in JSON format.
- `output/quran_english_yusufali.txt` — new plain-text output for Yusuf Ali English translation.
- `output/quran_translit_unicode.txt` — new plain-text output for Quran Unicode Project transliteration.
- `output/quran_hindi_mokhtasar.txt` — new plain-text output for Al-Mokhtasar Hindi Tafsir.
- `output/quran_english_abridged.txt` — new plain-text output for the Abridged English Explanation.
- `docs.zip` — ZIP archive of the generated `docs/` HTML pages.
- `.github/workflows/scrape.yml` — GitHub Actions workflow (`Upload Audio to Hugging Face Hub`) to download Alafasy recitation audio and upload it to a Hugging Face dataset, then open a PR with an updated `config/audio_config.json`.

### Changed
- `src/gentxtforquran.py` — extended to handle three additional input formats:
  - **Pipe-delimited** (`sura|ayah|text`) for Yusuf Ali.
  - **Sequential transliteration** (`num|text`) for the Quran Unicode Project file.
  - **JSON ZIP** (key `"sura:ayah"` → `{text}`) for Hindi Tafsir and English Explanation sources.
- `src/gendocshtml.py` — updated to incorporate all new translations (Yusuf Ali, Quran Unicode Project transliteration, Al-Mokhtasar Hindi Tafsir, Abridged English Explanation) into the generated HTML pages.

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
