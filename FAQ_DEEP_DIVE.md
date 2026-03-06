# FAQ — Deep Dive

Anticipated questions about the Qur'an data project, with thorough answers.

<!-- TOC -->
- [General Questions](#general-questions)
- [Data and Translations](#data-and-translations)
- [Building and Running](#building-and-running)
- [Website Questions](#website-questions)
- [PDF Questions](#pdf-questions)
- [Contributing](#contributing)
- [Legal and Licensing](#legal-and-licensing)
<!-- /TOC -->

---

## General Questions

### Q: What does this repository actually do?

**A:** This repository provides three things:
1. **A static website** ([https://druvx13.github.io/Quran-data/](https://druvx13.github.io/Quran-data/)) where you can read all 114 surahs of the Qur'an with Arabic text, audio recitation, transliteration, and translations in English, Hindi, Urdu, Gujarati, and Nepali — side by side.
2. **Plain-text files** of 71 Qur'an translations (in `output/`), ready to use in any application.
3. **Typeset bilingual PDFs** of the Qur'an paired with Hindi or English translations, generated with XeLaTeX.

The Python scripts in `src/` generate all of these outputs from the raw translation data in `data/`.

### Q: Is this an official Islamic resource?

**A:** No. This is an independent, non-commercial, educational project. The translations used are all well-known works by recognized scholars, but the project itself has no religious authority. Translation texts are reproduced from their original sources and remain subject to those sources' terms.

### Q: How many translations are included?

**A:** As of the latest update, **71 translations** across multiple languages:
- **English:** 37 translations (Pickthall, Yusuf Ali, Saheeh International, and many others)
- **Urdu:** 14 translations
- **Hindi:** 6 translations (including Devanagari and Romanized)
- **Arabic:** 1 (the original Uthmani script)
- **Transliteration:** 2 (English phonetic)
- **Gujarati:** 2 (Gujarati script and Romanized)
- **Nepali:** 1
- **Roman Urdu:** 2

### Q: Does the website require a backend server?

**A:** No. The website is 100% static HTML/CSS/JavaScript hosted on GitHub Pages. There is no server-side processing, no database, and no API calls from the website itself (except for loading fonts from Google Fonts CDN and audio from the Hugging Face Space).

### Q: What is the "Quran Unicode Project" transliteration?

**A:** A transliteration (phonetic representation in Latin script) of the Arabic Qur'an produced by the Quran Unicode Project. It represents Arabic sounds using standard Latin letters. This is different from the Tanzil.net transliteration — both are included.

---

## Data and Translations

### Q: Why are there two Pickthall files?

**A:** `data/en.pickthall.txt` is a one-per-line format (used by `gentxtforquran.py` for the plain-text output and directly by `gendocshtml.py`). `data/en.pickthall.tanzil.txt` is the Tanzil.net pipe-delimited format (`sura|ayah|text`) with some textual variants. They contain the same translation but in different formats and potentially with minor differences.

### Q: Why are some translations in `.json.zip` format?

**A:** Four data sources — the Hindi Tafsir (Al-Mokhtasar), the English Explanation (Abridged), the Gujarati translation (Rabila Al-Umry), and the Nepali translation (Ahl-al-Hadith Nepal) — were originally distributed as JSON files. They are stored as ZIP archives to keep the repository size manageable while preserving the structured data format (which allows looking up any `sura:ayah` directly by key, rather than reading sequentially).

### Q: What is the difference between a "translation" and a "tafsir"?

**A:** A **translation** (Tarjuma) renders the Qur'anic Arabic into another language as a direct equivalent. A **tafsir** (exegesis) provides detailed explanation, context, and commentary on the meaning of each verse. In this project, the "Hindi Tafsir (Al-Mokhtasar)" and "English Explanation (Abridged)" are simplified tafsirs — they are shorter than traditional tafsirs but longer than bare translations.

### Q: Why are the output files in `[sura:ayah] text` format?

**A:** This format was chosen because it:
1. **Self-identifies** every line — you can grep any file for a specific ayah without knowing its position
2. **Survives editing** — if a blank line is accidentally added or removed, the [sura:ayah] marker preserves the reference
3. **Is human-readable** — the output files are intended to be usable as plain-text references, not just machine-readable data
4. **Groups by surah** — the header for each surah makes it easy to navigate in a text editor

### Q: Where does the Arabic text come from?

**A:** From [tanzil.net](https://tanzil.net), which provides the Uthmani script (Hafs narration) as a high-quality Unicode plain-text source. This is the same source used by many Qur'an applications worldwide.

### Q: Are any translations incomplete?

**A:** No. All 71 translations cover all 6,236 ayahs. The generator scripts are designed to fail (produce wrong line counts) if a source file is incomplete — spot-checking with `grep -c "^\[" output/...` confirms completeness.

### Q: Can I add a translation that is copyrighted?

**A:** Only with explicit permission from the copyright holder, or if the translation is clearly licensed for free redistribution. Public domain translations (Pickthall 1930, Yusuf Ali 1934) can be freely included. For other translations, the project relies on redistribution being permitted by the source website (tanzil.net, quran.com, etc.) for educational/non-commercial use. See also the Legal section below.

---

## Building and Running

### Q: Do I need to install any Python packages?

**A:** No. The scripts use only Python's standard library: `json`, `os`, `re`, `zipfile`. No `pip install` is required.

### Q: Why do the scripts require running from the repository root?

**A:** The scripts use relative paths (`data/`, `output/`, `docs/`, `latex/`) without any `__file__`-based path resolution. This is the simplest approach and avoids platform-specific path issues. The trade-off is that you must `cd` to the repo root before running them. This is documented in every script's docstring.

### Q: Do I need XeLaTeX to use this project?

**A:** Only if you want to compile PDFs. The plain-text output files and the HTML website do not require LaTeX. `gentxtforquran.py` and `gendocshtml.py` work with Python only.

### Q: What order do I run the scripts in?

**A:**
1. `python3 src/gentxtforquran.py` — generates `output/*.txt` (needed for the HTML website)
2. `python3 src/gendocshtml.py` — generates `docs/*.html` (uses `output/` files)
3. `python3 src/gentexforquran.py` — generates `latex/q*.tex` (for PDFs only; independent of steps 1–2)
4. `make all` — compiles PDFs from `latex/` (requires step 3)

Steps 3–4 are independent of steps 1–2.

### Q: How long does it take to regenerate everything?

**A:** 
- `gentxtforquran.py`: 5–10 seconds
- `gendocshtml.py`: 30–90 seconds
- `gentexforquran.py`: 1–3 seconds
- `make all` (5 PDFs): 15–40 minutes (XeLaTeX is slow)

See `PERFORMANCE_BENCHMARKS.md` for more details.

### Q: Can I regenerate only some output files?

**A:** `gentxtforquran.py` regenerates all 71 files every run. There is no incremental regeneration. However, the script is fast (~10 seconds), so regenerating all files is not a significant burden.

For HTML generation, `gendocshtml.py` also regenerates all 114 surah pages. Selective regeneration would require code changes.

---

## Website Questions

### Q: How does the search work?

**A:** Search is entirely client-side. When the search page loads, it imports `search-data.js` — a pre-built JavaScript file generated by `gendocshtml.py` that contains all searchable text (Arabic, transliteration, Yusuf Ali translation, Hindi Tafsir) for all 6,236 ayahs. The search function then does an in-memory text scan and returns matching ayahs. No server is involved.

### Q: Why is the search slow on first load?

**A:** The `search-data.js` file is large (several MB of JSON data). On the first visit, the browser must download and parse this file. On subsequent visits, it is loaded from the browser cache and search is instant.

### Q: Can I use the website offline?

**A:** Partially. If you clone the repository and serve `docs/` locally (`cd docs && python3 -m http.server 8000`), you can browse all pages. However:
- **Fonts** (Arabic: Amiri Quran) will fall back to system fonts if Google Fonts CDN is unavailable
- **Audio** will not work (it streams from Hugging Face, which requires internet)

For full offline use, you would need to download the fonts and host audio locally.

### Q: How do I jump to a specific surah?

**A:** Use the surah dropdown navigator in the page header. It lists all 114 surahs by name and number.

### Q: Can I link to a specific ayah?

**A:** Not currently with a direct URL anchor. The surah pages do not use `id` attributes on individual ayah rows. However, you can link to a specific surah: `https://druvx13.github.io/Quran-data/002.html` for Al-Baqarah.

### Q: Why does the audio sometimes not play immediately?

**A:** The Hugging Face Space hosting the audio is on the free tier, which puts Spaces to "sleep" after a period of inactivity. The first audio request wakes up the Space, which takes 30–60 seconds. After that, audio loads normally (0.5–2 seconds per file).

### Q: What fonts does the website use?

**A:** 
- **Arabic text:** Amiri Quran (via Google Fonts) — a traditional Naskh-style Arabic font optimised for Qur'an typesetting
- **Hindi/Devanagari text:** Noto Sans Devanagari (via Google Fonts)
- **Latin/other text:** System default sans-serif

---

## PDF Questions

### Q: What languages are available as PDFs?

**A:** Currently, 5 bilingual PDFs are supported (Arabic + translation):
- Hindi: Muhammad Farooq Khan & Muhammad Ahmed (`farooq.pdf`)
- Hindi: Suhel Farooq Khan & Saifur Rahman Nadwi (`suhail.pdf`)
- English: Saheeh International (`sahih.pdf`)
- English Transliteration (`translit.pdf`)
- English: Mohammed Marmaduke Pickthall (`pickthall.pdf`)

### Q: Why aren't more translations available as PDFs?

**A:** PDF generation with XeLaTeX requires:
1. A LaTeX template
2. A content generator block in `gentexforquran.py`
3. The correct LaTeX font packages for the translation's language/script
4. Compilation time (5–8 minutes per PDF)

Adding a new PDF edition is more complex than adding a plain-text translation. The 5 existing PDFs cover the original scope of the project.

### Q: The PDF has boxes/squares for Arabic text. How do I fix this?

**A:** The Arabic text requires the Amiri or Scheherazade New font to be installed on your system. Install these fonts and then re-run `xelatex`. See `TROUBLESHOOTING.md §2.3` for detailed instructions.

---

## Contributing

### Q: How do I add a new translation?

**A:** See `DEVELOPER_ONBOARDING.md §5.1` for a step-by-step walkthrough. The short version:
1. Place the data file in `data/`
2. Add one entry to the `translations` list in `src/gentxtforquran.py`
3. Run the script and verify output
4. Update README and CHANGELOG
5. Open a PR

### Q: Do I need to update the website when adding a new translation?

**A:** Not necessarily. Adding a translation to `gentxtforquran.py` adds it to the plain-text output files. Adding it to the website requires additional changes to `gendocshtml.py`. You can contribute a plain-text-only addition and leave website integration for a follow-up PR.

### Q: Can I contribute translation corrections?

**A:** Yes, but with care. Translation files in `data/` should only be modified to correct genuine transcription errors (e.g., a typo introduced during file download/conversion). Do not edit them to "improve" a translation or substitute your preferred rendering — that would be altering someone else's work. Document any corrections clearly in your PR.

---

## Legal and Licensing

### Q: What license does this project use?

**A:** The Python scripts, Makefile, and configuration files are licensed under the [Unconditional Liberty Instrument (ULI), Version 1.0](LICENSE) — a custom public-domain-equivalent license. You can use, modify, and distribute the scripts freely with no restrictions (other than including the license).

### Q: Can I use the translation text files in my own project?

**A:** The ULI license applies only to the **scripts**, not to the translation texts. Each translation is subject to its own copyright:
- **Public domain:** Pickthall (1930), Yusuf Ali (1934) — freely usable for any purpose
- **tanzil.net translations:** Check [tanzil.net](https://tanzil.net) terms of use
- **Other translations:** Check the copyright holder's terms

For personal, educational, or non-commercial use, most sources permit free use. For commercial applications, contact the copyright holders directly.

### Q: Can I fork this repository and create a competing website?

**A:** Yes, under the ULI license. The scripts are freely usable. However, the translation texts must comply with their own licenses (see above). When distributing or publishing, ensure you comply with all applicable licenses and provide proper attribution.

### Q: Does this project comply with GDPR?

**A:** The **static website** (GitHub Pages) does not collect any user data, set cookies, or run analytics. The only external connections are to Google Fonts (which may log requests per Google's privacy policy) and the Hugging Face audio server. The `localStorage` usage stores only user preferences (dark mode, content filter state) locally — no data leaves the browser. For a self-hosted deployment, no additional GDPR compliance measures are required beyond the hosting provider's own policies.
