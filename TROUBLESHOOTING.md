# Troubleshooting

Common errors, diagnostics, and fixes for the Qur'an data project.

<!-- TOC -->
- [1. Python Script Errors](#1-python-script-errors)
  - [1.1 FileNotFoundError on a data/ file](#11-filenotfounderror-on-a-data-file)
  - [1.2 Output file has wrong line count](#12-output-file-has-wrong-line-count)
  - [1.3 UnicodeDecodeError](#13-unicodedecodeerror)
  - [1.4 JSON decode error from ZIP file](#14-json-decode-error-from-zip-file)
  - [1.5 gendocshtml.py fails with KeyError or IndexError](#15-gendocshtmlpy-fails-with-keyerror-or-indexerror)
  - [1.6 Script must be run from the repository root](#16-script-must-be-run-from-the-repository-root)
- [2. LaTeX / PDF Errors](#2-latex--pdf-errors)
  - [2.1 xelatex: command not found](#21-xelatex-command-not-found)
  - [2.2 LaTeX package not found (quran.sty, polyglossia, etc.)](#22-latex-package-not-found-quransty-polyglossia-etc)
  - [2.3 Arabic text renders as boxes or question marks](#23-arabic-text-renders-as-boxes-or-question-marks)
  - [2.4 PDF has wrong content / misaligned chapters](#24-pdf-has-wrong-content--misaligned-chapters)
  - [2.5 xelatex exits with error in generated content file](#25-xelatex-exits-with-error-in-generated-content-file)
- [3. Website / HTML Issues](#3-website--html-issues)
  - [3.1 Search returns no results](#31-search-returns-no-results)
  - [3.2 Audio player shows error / no sound](#32-audio-player-shows-error--no-sound)
  - [3.3 Arabic text not rendering (boxes or mojibake)](#33-arabic-text-not-rendering-boxes-or-mojibake)
  - [3.4 Dark mode not working](#34-dark-mode-not-working)
  - [3.5 Content Filter checkboxes not hiding rows](#35-content-filter-checkboxes-not-hiding-rows)
  - [3.6 GitHub Pages shows old content after push](#36-github-pages-shows-old-content-after-push)
  - [3.7 Website gives 404 on all pages except index](#37-website-gives-404-on-all-pages-except-index)
- [4. Data Issues](#4-data-issues)
  - [4.1 Translation has garbled text or encoding issues](#41-translation-has-garbled-text-or-encoding-issues)
  - [4.2 Ayah text is offset (wrong ayah for each number)](#42-ayah-text-is-offset-wrong-ayah-for-each-number)
  - [4.3 Missing ayahs in output (some lines are blank)](#43-missing-ayahs-in-output-some-lines-are-blank)
- [5. Git / Build Issues](#5-git--build-issues)
  - [5.1 make: command not found](#51-make-command-not-found)
  - [5.2 make all fails because .tex files do not exist](#52-make-all-fails-because-tex-files-do-not-exist)
<!-- /TOC -->

---

## 1. Python Script Errors

### 1.1 FileNotFoundError on a data/ file

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/en.sahih.txt'
```

**Causes & Fixes:**
1. **Not running from the repository root.** All scripts expect to be run with `data/` as a relative path from the working directory:
   ```bash
   cd /path/to/Quran-data
   python3 src/gentxtforquran.py
   ```

2. **File actually missing.** Check if the file exists:
   ```bash
   ls -la data/en.sahih.txt
   ```
   If missing, restore it from git:
   ```bash
   git checkout -- data/en.sahih.txt
   ```

### 1.2 Output file has wrong line count

**Symptom:** `grep -c "^\[" output/quran_english_sahih.txt` returns a number other than 6,236.

**Diagnosis:**
```bash
# Count data lines:
grep -c "^\[" output/quran_english_sahih.txt

# Find the last ayah in the file:
grep "^\[" output/quran_english_sahih.txt | tail -3

# Find the first ayah where text is missing:
grep "^\[.*\] $" output/quran_english_sahih.txt | head -5
```

**Causes & Fixes:**
1. **Source file has fewer than 6,236 lines.** Count the source:
   ```bash
   wc -l data/en.sahih.txt
   ```
   The source must have exactly 6,236 non-empty lines. If it has more (e.g., trailing blank lines), the parser will read blanks as text. If fewer, the last ayahs will be empty.

2. **Source file is pipe-delimited but registered as one-per-line** (wrong `lang` type in the `translations` list). In this case the `[sura:ayah]` output will contain `sura|ayah|text` as the "text". Fix: change the `lang` value in `translations`.

3. **Comment lines in pipe-delimited files** counted as data lines. `en.yusufali.txt` has `#` comment lines — if a new similar file has unexpected comments, the parser will misalign. Fix: pre-process the file to remove comments, or update the parser to skip `#` lines.

### 1.3 UnicodeDecodeError

**Symptom:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0
```

**Causes & Fixes:**
1. **File has BOM (Byte Order Mark).** Some editors save UTF-8 files with a UTF-8 BOM (`\xef\xbb\xbf`). Open the file with `encoding='utf-8-sig'` instead of `'utf-8'`, or strip the BOM with:
   ```bash
   sed -i '1s/^\xEF\xBB\xBF//' data/en.wahiduddin.txt
   ```

2. **File is not UTF-8.** Check the encoding:
   ```bash
   file -i data/en.wahiduddin.txt
   # or:
   python3 -c "open('data/en.wahiduddin.txt', encoding='latin-1').read()"
   ```
   Convert to UTF-8:
   ```bash
   iconv -f latin-1 -t utf-8 data/en.wahiduddin.txt > /tmp/fixed.txt
   mv /tmp/fixed.txt data/en.wahiduddin.txt
   ```

### 1.4 JSON decode error from ZIP file

**Symptom:**
```
json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Causes & Fixes:**
1. **The ZIP file is corrupted.** Test the ZIP:
   ```bash
   python3 -c "import zipfile; z=zipfile.ZipFile('data/hindi-mokhtasar.json.zip'); print(z.namelist())"
   ```
   If this raises an error, the ZIP is corrupted — restore from git.

2. **Wrong file selected inside the ZIP.** The script uses `next(n for n in zf.namelist() if n.endswith('.json'))`. If the ZIP contains no `.json` file (e.g., a `.JSON` extension with uppercase), the generator will raise `StopIteration`. Fix: add `.JSON` to the filter or rename the file inside the ZIP.

### 1.5 gendocshtml.py fails with KeyError or IndexError

**Symptom:** Script crashes partway through generating surah pages.

**Likely cause:** The output files in `output/` are missing or have different line counts than expected. `gendocshtml.py` must be run after `gentxtforquran.py`.

**Fix:**
```bash
python3 src/gentxtforquran.py  # Ensure all output/ files are fresh
python3 src/gendocshtml.py
```

### 1.6 Script must be run from the repository root

**Symptom:** `FileNotFoundError` with a path like `data/...` or `output/...`.

**Fix:**
```bash
cd /path/to/Quran-data   # Navigate to repo root first
python3 src/gentxtforquran.py
```

All three scripts use relative paths (`data/`, `output/`, `docs/`) without any `__file__`-based path manipulation, so they must be invoked from the repository root.

---

## 2. LaTeX / PDF Errors

### 2.1 xelatex: command not found

**Symptom:**
```
make: xelatex: No such file or directory
```

**Fix:** Install TeX Live (see `DEVELOPER_ONBOARDING.md` §1.2 for OS-specific instructions).

### 2.2 LaTeX package not found (quran.sty, polyglossia, etc.)

**Symptom:**
```
! LaTeX Error: File `quran.sty' not found.
```

**Fix:**
```bash
# Install the missing package via tlmgr:
sudo tlmgr install quran
sudo tlmgr install polyglossia
sudo tlmgr install fontspec
```

If `tlmgr` is not available, install the full TeX Live distribution instead of a minimal one.

### 2.3 Arabic text renders as boxes or question marks

**Symptom:** The Arabic text in the PDF shows as empty boxes `□□□`.

**Causes & Fixes:**
1. **Amiri or Scheherazade New font not installed.** These fonts must be installed system-wide for XeLaTeX to find them:
   - Download from [CTAN](https://ctan.org/pkg/amiri) or [Google Fonts](https://fonts.google.com/noto)
   - Install to `~/.fonts/` (Linux) or `~/Library/Fonts/` (macOS)
   - Refresh font cache: `fc-cache -fv`

2. **quran package out of date.** Update:
   ```bash
   sudo tlmgr update quran
   ```

### 2.4 PDF has wrong content / misaligned chapters

**Symptom:** Ayah N in the PDF shows text from ayah N+1 or a different surah.

**Cause:** The generated content file (`latex/qum.tex` etc.) is out of date or was generated from a corrupted source. The content file and the source data file must be perfectly aligned.

**Fix:**
```bash
# Re-generate all content files from scratch:
python3 src/gentexforquran.py
# Then re-compile:
cd latex && xelatex farooq.tex
```

### 2.5 xelatex exits with error in generated content file

**Symptom:**
```
! Undefined control sequence.
<recently read> \quranayah
```

**Cause:** The `quran` LaTeX package is not installed or not loaded by `quran.sty`.

**Fix:**
```bash
sudo tlmgr install quran
```

If the `quran` package is installed but `\quranayah` is undefined, check that `quran.sty` correctly loads the package with `\usepackage{quran}` or similar.

---

## 3. Website / HTML Issues

### 3.1 Search returns no results

**Symptom:** Typing in the search box on `search.html` returns no results.

**Causes & Fixes:**
1. **`docs/sd/` files are missing.** The per-field JSON files are generated by `gendocshtml.py`. Regenerate them:
   ```bash
   python3 src/gendocshtml.py
   ```

2. **Browser blocked fetch requests.** If viewing via `file://` URL, browsers block `fetch()` calls to local files. Use a local HTTP server:
   ```bash
   cd docs && python3 -m http.server 8000
   ```

3. **No fields enabled in Settings.** `search.html` only fetches and searches fields the user has enabled in `config.html`. Open Settings and enable at least one translation field.

4. **Cached data from old session.** Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (macOS) to clear the in-memory cache.

### 3.2 Audio player shows error / no sound

**Symptom:** The audio player shows an error icon or no audio plays.

**Causes & Fixes:**
1. **Hugging Face Space is sleeping.** Hugging Face Spaces on the free tier go to sleep after inactivity. The first request may take 30–60 seconds to wake up. Wait and retry.

2. **CORS error.** Check the browser console for CORS errors. The audio server must include `Access-Control-Allow-Origin: *`.

3. **MP3 file missing on the server.** Verify the URL pattern. For Surah 2, Ayah 255 (Ayat al-Kursi):
   ```
   https://druvx13-quran-audio-alafasy.hf.space/002255.mp3
   ```

4. **Audio URL changed in gendocshtml.py.** If you updated the audio URL, regenerate the HTML.

### 3.3 Arabic text not rendering (boxes or mojibake)

**Symptom:** Arabic text on surah pages shows as boxes or garbled characters.

**Causes & Fixes:**
1. **Font not loaded.** The website loads Amiri Quran from Google Fonts. Check network connectivity and browser console for failed font requests.

2. **Browser doesn't support the font format.** Try a different browser. Modern Chrome, Firefox, and Safari all support WOFF2 (Google Fonts).

3. **Right-to-left not applied.** The Arabic `<td>` elements should have `dir="rtl"`. If they don't, the HTML was regenerated with a bug in `gendocshtml.py`.

### 3.4 Dark mode not working

**Symptom:** The dark mode toggle button does nothing.

**Likely cause:** JavaScript is disabled in the browser. Enable JavaScript or check for console errors.

### 3.5 Content Filter checkboxes not hiding rows

**Symptom:** Unchecking a translation checkbox in the filter widget does not hide those rows.

**Likely cause:** JavaScript error on the page. Check the browser console for errors. The Content Filter relies on JavaScript to add/remove CSS classes on table rows.

### 3.6 GitHub Pages shows old content after push

**Symptom:** The live website has not updated 10+ minutes after pushing to `cairo`.

**Diagnosis:**
1. Check the GitHub Actions tab for a failed "pages-build-deployment" run.
2. Check [githubstatus.com](https://www.githubstatus.com/) for a GitHub Pages outage.

**Fix:**
- If a workflow failed, check the error in the Actions log and fix the issue.
- If GitHub status shows an outage, wait and retry.
- If no outage, try making a trivial commit to force a re-deploy:
  ```bash
  git commit --allow-empty -m "Trigger Pages rebuild"
  git push origin cairo
  ```

### 3.7 Website gives 404 on all pages except index

**Symptom:** `https://druvx13.github.io/Quran-data/001.html` returns a 404 error.

**Likely cause:** The `docs/001.html` file is missing. This happens if `gendocshtml.py` was not run or if the `docs/` directory was accidentally deleted.

**Fix:**
```bash
python3 src/gendocshtml.py
git add docs/
git commit -m "Regenerate docs/"
git push origin cairo
```

---

## 4. Data Issues

### 4.1 Translation has garbled text or encoding issues

**Symptom:** Output file contains `Ã©` or similar multi-byte artifacts.

**Cause:** The source file was read with the wrong encoding and re-encoded when written.

**Fix:**
```bash
# Detect actual encoding:
python3 -c "import chardet; data=open('data/en.newfile.txt','rb').read(); print(chardet.detect(data))"
# or:
file -i data/en.newfile.txt
```

If the file is latin-1:
```bash
iconv -f latin-1 -t utf-8 data/en.newfile.txt > /tmp/fixed.txt
mv /tmp/fixed.txt data/en.newfile.txt
```

### 4.2 Ayah text is offset (wrong ayah for each number)

**Symptom:** `[1:1]` in the output contains the text that should be `[1:2]`, etc. — everything is shifted by one.

**Cause:** The source file has an extra header line (not a blank line, but a data line) before ayah 1:1. Common in files downloaded from APIs that prepend a metadata line.

**Diagnosis:**
```bash
# Check what the first line of the source contains:
head -1 data/en.newfile.txt
# Is it an ayah? Or metadata like "Translation by ..."?
```

**Fix:** Strip the header line from the source:
```bash
tail -n +2 data/en.newfile.txt > /tmp/fixed.txt
mv /tmp/fixed.txt data/en.newfile.txt
```

### 4.3 Missing ayahs in output (some lines are blank)

**Symptom:** `grep "^\[.*\] $" output/quran_english_newauthor.txt` finds many blank-text ayahs.

**Causes:**
1. **JSON file has missing keys.** For JSON ZIP sources, missing `"sura:ayah"` keys produce empty strings. Check the JSON file completeness.
2. **Source file has blank lines mid-file.** Count actual data lines: `grep -vc "^$" data/en.newfile.txt`. Should be 6,236.

---

## 5. Git / Build Issues

### 5.1 make: command not found

**Fix:**
- macOS: `xcode-select --install`
- Ubuntu: `sudo apt install make`
- Windows: Install via Chocolatey (`choco install make`) or use Git for Windows

### 5.2 make all fails because .tex files do not exist

**Symptom:**
```
make: *** No rule to make target 'latex/qum.tex', needed by 'output/farooq.pdf'.
```

**Cause:** `generate-tex` was not run before `all`.

**Fix:**
```bash
make generate-tex
make all
```

The generated content files (`latex/qum.tex`, `qup.tex`, etc.) are listed in `.gitignore` and are not tracked in git. They must be regenerated locally before compiling PDFs.
