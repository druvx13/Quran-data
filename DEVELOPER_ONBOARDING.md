# Developer Onboarding

Welcome to the Qur'an Multi-Translation Study Website & PDF Typesetting project. This guide walks you through everything you need to set up your development environment, run the build pipeline, and make your first contribution.

<!-- TOC -->
- [1. Prerequisites](#1-prerequisites)
  - [1.1 Python 3.6+](#11-python-36)
  - [1.2 XeLaTeX (for PDF compilation only)](#12-xelatex-for-pdf-compilation-only)
  - [1.3 GNU Make](#13-gnu-make)
- [2. Getting the Code](#2-getting-the-code)
- [3. Repository Overview (5-Minute Tour)](#3-repository-overview-5-minute-tour)
- [4. Running the Pipeline](#4-running-the-pipeline)
  - [4.1 Generate Plain-Text Files](#41-generate-plain-text-files)
  - [4.2 Regenerate the HTML Website](#42-regenerate-the-html-website)
  - [4.3 Generate LaTeX Content and Compile PDFs](#43-generate-latex-content-and-compile-pdfs)
- [5. Making Changes](#5-making-changes)
  - [5.1 Adding a New Translation](#51-adding-a-new-translation)
  - [5.2 Modifying the HTML Website](#52-modifying-the-html-website)
  - [5.3 Modifying LaTeX Output](#53-modifying-latex-output)
- [6. Verifying Your Changes](#6-verifying-your-changes)
- [7. Submitting a Pull Request](#7-submitting-a-pull-request)
- [8. Environment Notes by OS](#8-environment-notes-by-os)
  - [8.1 macOS](#81-macos)
  - [8.2 Ubuntu / Debian Linux](#82-ubuntu--debian-linux)
  - [8.3 Windows](#83-windows)
<!-- /TOC -->

---

## 1. Prerequisites

### 1.1 Python 3.6+

Check your Python version:
```bash
python3 --version
```

The scripts use only the standard library (`json`, `os`, `re`, `zipfile`) — no `pip install` required.

### 1.2 XeLaTeX (for PDF compilation only)

**Only needed if you plan to compile PDFs.** If you only need to generate plain-text files or the HTML website, you can skip this.

XeLaTeX is part of TeX Live (Linux/macOS) or MiKTeX (Windows):
```bash
xelatex --version  # should print something like "XeTeX 3.141592..."
```

Required LaTeX packages (usually included in a full TeX Live installation):
- `quran` — provides `\quranayah` macro and Arabic text
- `polyglossia` — multilingual support
- `fontspec` — custom font loading
- `xltxtra` / `xunicode` — XeTeX Unicode support

### 1.3 GNU Make

```bash
make --version  # should print "GNU Make 4.x"
```

On macOS, `make` is part of Xcode Command Line Tools. On Linux, it is typically pre-installed.

---

## 2. Getting the Code

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR-USERNAME/Quran-data.git
cd Quran-data

# Add the upstream remote for staying up-to-date:
git remote add upstream https://github.com/druvx13/Quran-data.git
```

> 💡 **Branch convention:** Always create your feature branch from `cairo` (the default branch):
> ```bash
> git checkout cairo
> git pull upstream cairo
> git checkout -b my-feature-branch
> ```

---

## 3. Repository Overview (5-Minute Tour)

```
Quran-data/
├── src/          ← Python scripts — THIS IS WHERE YOU WORK
├── data/         ← Input translation files — READ ONLY (unless fixing a typo)
├── latex/        ← LaTeX templates + generated content files
├── output/       ← Generated .txt files and PDFs
├── docs/         ← Generated HTML website (GitHub Pages)
└── archive/      ← Legacy reference files (ignore these)
```

**The three scripts in `src/` are the heart of the project:**

| Script | What it does | When to run |
|--------|-------------|-------------|
| `gentxtforquran.py` | data/ → output/*.txt | After adding/changing data files |
| `gentexforquran.py` | data/ → latex/q*.tex | Before compiling PDFs |
| `gendocshtml.py` | output/ + data/ → docs/ | After running gentxtforquran.py |

All scripts **must be run from the repository root directory**, not from inside `src/`.

---

## 4. Running the Pipeline

### 4.1 Generate Plain-Text Files

This is the most common operation. It reads translation data from `data/` and writes formatted plain-text files to `output/`:

```bash
python3 src/gentxtforquran.py
```

Expected output: 71 lines like:
```
Generated: output/quran_arabic.txt
Generated: output/quran_english_sahih.txt
...
Generated: output/quran_roman_gujarati_rabila.txt
```

**Time:** ~5–10 seconds on a modern machine.

Alternatively, using Make:
```bash
make generate-txt
```

### 4.2 Regenerate the HTML Website

> ⚠️ **Requires step 4.1 to have been run first.** `gendocshtml.py` reads from `output/`, which must exist and be populated.

```bash
python3 src/gendocshtml.py
```

Expected output: ~120 lines like:
```
Generated: docs/001.html
Generated: docs/002.html
...
Generated: docs/search-data.js
```

**Time:** ~30–60 seconds (generates 120+ HTML files).

Using Make:
```bash
make generate-docs
```

**To preview the website locally:**
```bash
cd docs
python3 -m http.server 8000
# Open http://localhost:8000 in your browser
```

> 💡 **Why use a local server?** Some browser security policies block `file://` URLs from loading JavaScript modules. A local HTTP server avoids this.

### 4.3 Generate LaTeX Content and Compile PDFs

> ⚠️ **Requires XeLaTeX to be installed** (see §1.2).

**Step 1:** Generate intermediate LaTeX content files:
```bash
python3 src/gentexforquran.py
# OR: make generate-tex
```

**Step 2:** Compile PDFs:
```bash
make all
```

This runs XeLaTeX for each of the 5 templates. Expected output per PDF:
```
cd latex && xelatex farooq.tex && mv farooq.pdf ../output/
```

**Individual PDF compilation:**
```bash
cd latex && xelatex farooq.tex    # → output/farooq.pdf  (Hindi Farooq Khan)
cd latex && xelatex suhail.tex    # → output/suhail.pdf  (Hindi Suhail)
cd latex && xelatex sahih.tex     # → output/sahih.pdf   (English Saheeh Intl)
cd latex && xelatex translit.tex  # → output/translit.pdf (English Transliteration)
cd latex && xelatex pickthall.tex # → output/pickthall.pdf (English Pickthall)
```

> 💡 XeLaTeX may need to run **twice** for correct table of contents generation.

---

## 5. Making Changes

### 5.1 Adding a New Translation

This is the most common type of contribution. The process:

1. **Obtain the data file** — download from tanzil.net, quran.com, quranenc.com, or another source. Identify the format (one-per-line, pipe-delimited, JSON ZIP).

2. **Place the file in `data/`** — follow the naming convention:
   - `en.AUTHORNAME.txt` for English
   - `ur.AUTHORNAME.txt` for Urdu
   - `hi.AUTHORNAME.txt` for Hindi
   - `hi.roman.AUTHORNAME.txt` for Romanized Hindi
   - `ur.romanAUTHORNAME.txt` for Romanized Urdu
   - `gu.roman.AUTHORNAME.txt` for Romanized Gujarati

3. **Add an entry to `src/gentxtforquran.py`** — in the `translations` list:
   ```python
   ('data/en.newauthor.txt', 'output/quran_english_newauthor.txt', 'New Author Name', 'English'),
   ```

4. **Run `python3 src/gentxtforquran.py`** — verify the new output file is generated correctly.

5. **Spot-check the output:**
   ```bash
   head -20 output/quran_english_newauthor.txt
   grep -c "^\[" output/quran_english_newauthor.txt  # Should be 6236
   ```

6. **Update `src/gendocshtml.py`** (optional) — if you want the translation to appear on the website, add it to the HTML generator. This requires modifying the data-loading section and the per-ayah HTML row generation.

7. **Update `README.md`** — add the new file to the repository structure and output file tables.

8. **Update `CHANGELOG.md`** — document what you added.

### 5.2 Modifying the HTML Website

All HTML is generated by `src/gendocshtml.py`. **Never edit `docs/*.html` directly** — your changes will be overwritten the next time the generator runs.

To change the website:
1. Edit `src/gendocshtml.py`
2. Run `python3 src/gendocshtml.py`
3. Preview at `http://localhost:8000` (after `cd docs && python3 -m http.server 8000`)

Common modification areas in `gendocshtml.py`:
- **CSS styles:** Search for inline `<style>` blocks in the page template strings
- **Dark mode colours:** Look for `prefers-color-scheme: dark` or dark mode class variables
- **Content Filter checkboxes:** The `details`/`summary` section in each surah page template
- **Audio URL:** Search for `hf.space` to find and update the audio base URL
- **Search index:** The `search-data.js` generation is near the end of the script

### 5.3 Modifying LaTeX Output

To change the PDF layout or typography:
1. Edit the relevant template in `latex/` (e.g., `latex/farooq.tex`)
2. Edit `latex/quran.sty` for global style changes
3. Re-run `python3 src/gentexforquran.py` if you changed content generation logic in the script
4. Re-compile with `cd latex && xelatex farooq.tex`

---

## 6. Verifying Your Changes

### Verify plain-text output files

```bash
# Check line count — every output file should have exactly 6236 data lines:
grep -c "^\[" output/quran_english_newauthor.txt
# Expected: 6236

# Check ayah 1:1 (Bismillah / first ayah):
grep "^\[1:1\]" output/quran_english_newauthor.txt

# Check last ayah (114:6 — last ayah of An-Nas):
grep "^\[114:6\]" output/quran_english_newauthor.txt

# Check header:
head -5 output/quran_english_newauthor.txt

# Check for blank lines in unexpected places:
grep -n "^\[\|^Surah\|^-" output/quran_english_newauthor.txt | tail -20
```

### Verify HTML output

```bash
cd docs && python3 -m http.server 8000
```

Open `http://localhost:8000` and:
- Verify the surah grid loads correctly on the homepage
- Click through a few surah pages
- Test the search functionality
- Toggle dark mode
- Check on a narrow viewport (or use browser DevTools mobile emulation)
- Test the Content Filter widget

### Verify PDFs

Open the generated `.pdf` in a PDF viewer and check:
- All 114 chapters are present
- Arabic text renders correctly (right-to-left, Hafs font)
- Translation text is below/beside each Arabic ayah
- Table of contents is correct

---

## 7. Submitting a Pull Request

1. **Commit your changes** with a clear message:
   ```bash
   git add data/en.newauthor.txt src/gentxtforquran.py output/quran_english_newauthor.txt README.md CHANGELOG.md
   git commit -m "Add English translation by New Author (quran.com)"
   ```

2. **Push to your fork:**
   ```bash
   git push origin my-feature-branch
   ```

3. **Open a PR against `cairo`** on GitHub.

4. **PR description should include:**
   - What you added or changed
   - Source of any new data (URL, license confirmation)
   - How you verified the output (e.g., line count check, visual inspection)

---

## 8. Environment Notes by OS

### 8.1 macOS

```bash
# Install Homebrew if not already installed:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 3 (usually pre-installed on macOS 12+):
brew install python3

# TeX Live (full installation, ~5 GB):
brew install --cask mactex

# Or minimal installation with required packages:
brew install --cask mactex-no-gui
sudo tlmgr install quran polyglossia fontspec xltxtra

# GNU Make (part of Xcode Command Line Tools):
xcode-select --install
```

### 8.2 Ubuntu / Debian Linux

```bash
# Python 3:
sudo apt install python3

# TeX Live (full):
sudo apt install texlive-full

# Or targeted packages:
sudo apt install texlive-xetex texlive-lang-arabic texlive-lang-other \
                 texlive-fonts-recommended

# The quran package may need manual installation:
sudo tlmgr install quran

# GNU Make:
sudo apt install make
```

### 8.3 Windows

**Python:**
- Download from [python.org](https://www.python.org/downloads/)
- Ensure `python` is in PATH
- Use `python` instead of `python3` if `python3` is not recognized

**TeX Live:**
- Download the TeX Live installer from [tug.org/texlive](https://www.tug.org/texlive/)
- Or install MiKTeX from [miktex.org](https://miktex.org/)

**GNU Make:**
- Install via [chocolatey](https://chocolatey.org/): `choco install make`
- Or use [Git for Windows](https://gitforwindows.org/) which includes a minimal Make

**Running scripts on Windows:**
```cmd
python src\gentxtforquran.py
python src\gentexforquran.py
python src\gendocshtml.py
```

> ⚠️ Line endings: Source data files use Unix line endings (`\n`). If you edit any file in `data/`, ensure your editor saves with LF (not CRLF) to avoid parsing errors.
