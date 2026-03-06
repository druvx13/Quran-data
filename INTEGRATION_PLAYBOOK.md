# Integration Playbook

How to connect the Qur'an data project with external systems, embed content in other applications, and use the project as a data source.

<!-- TOC -->
- [1. Using the Plain-Text Output Files](#1-using-the-plain-text-output-files)
  - [1.1 Parsing the Output Format](#11-parsing-the-output-format)
  - [1.2 Extracting a Specific Ayah](#12-extracting-a-specific-ayah)
  - [1.3 Building a Simple API on Top of the Data](#13-building-a-simple-api-on-top-of-the-data)
- [2. Embedding the Website (iFrame)](#2-embedding-the-website-iframe)
- [3. Integrating the Audio Stream](#3-integrating-the-audio-stream)
  - [3.1 Direct Audio URL Construction](#31-direct-audio-url-construction)
  - [3.2 Embedding Audio in an HTML Page](#32-embedding-audio-in-an-html-page)
- [4. Using the Search Index](#4-using-the-search-index)
- [5. Forking and Customising the Website](#5-forking-and-customising-the-website)
  - [5.1 Adding a New Language to the Website](#51-adding-a-new-language-to-the-website)
  - [5.2 Changing the Website Theme](#52-changing-the-website-theme)
  - [5.3 Replacing the Audio Source](#53-replacing-the-audio-source)
- [6. PDF Integration](#6-pdf-integration)
  - [6.1 Downloading Pre-Built PDFs](#61-downloading-pre-built-pdfs)
  - [6.2 Generating Custom PDFs](#62-generating-custom-pdfs)
- [7. Data Source Integration](#7-data-source-integration)
  - [7.1 Adding Translations from tanzil.net](#71-adding-translations-from-tanzilnet)
  - [7.2 Adding Translations from quran.com API](#72-adding-translations-from-qurancom-api)
  - [7.3 Adding Translations from fawazahmed0/quran-api](#73-adding-translations-from-fawazahmed0quran-api)
  - [7.4 Adding Translations from quranenc.com](#74-adding-translations-from-quranenccom)
<!-- /TOC -->

---

## 1. Using the Plain-Text Output Files

The `output/*.txt` files are the most easily consumed data artefacts. They are plain UTF-8 text with a consistent format.

### 1.1 Parsing the Output Format

Every output file follows this structure:

```
Line 1: Title (e.g., "Quran - English Translation")
Line 2: Translator credit (e.g., "Translator: Saheeh International")
Line 3: ============================================================
Line 4: (blank)
Line 5: Surah 1: Al-Fatihah (The Opening)
Line 6: ----------------------------------------
Lines 7-13: [1:1] text, [1:2] text, ..., [1:7] text
Line 14: (blank)
Line 15: Surah 2: Al-Baqarah (The Cow)
...
```

**Python parser example:**

```python
def parse_quran_output(filepath):
    """Parse an output/*.txt file into a dict: {(sura, ayah): text}."""
    ayahs = {}
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('['):
                # Format: [sura:ayah] text
                bracket_end = line.index(']')
                ref = line[1:bracket_end]
                text = line[bracket_end+2:]  # skip '] '
                sura, ayah = map(int, ref.split(':'))
                ayahs[(sura, ayah)] = text
    return ayahs

# Usage:
sahih = parse_quran_output('output/quran_english_sahih.txt')
print(sahih[(1, 1)])  # → "In the name of Allah, the Entirely Merciful, the Especially Merciful."
print(sahih[(2, 255)])  # → Ayat al-Kursi
```

**Shell example (grep):**
```bash
# Get all ayahs from Surah 1:
grep "^\[1:" output/quran_english_sahih.txt

# Get Ayat al-Kursi (2:255):
grep "^\[2:255\]" output/quran_english_sahih.txt

# Count total ayahs in a file:
grep -c "^\[" output/quran_english_sahih.txt  # Should be 6236
```

### 1.2 Extracting a Specific Ayah

```bash
# Bash one-liner to get surah 36, ayah 1 (Ya-Sin) from all English translations:
for f in output/quran_english_*.txt; do
    echo "=== $f ===";
    grep "^\[36:1\]" "$f";
done
```

```python
# Python: get all translations of the Bismillah (1:1)
import os

ayahs = {}
for fname in os.listdir('output'):
    if fname.endswith('.txt'):
        fpath = os.path.join('output', fname)
        with open(fpath, encoding='utf-8') as f:
            for line in f:
                if line.startswith('[1:1]'):
                    ayahs[fname] = line[6:].rstrip('\n')
                    break

for name, text in sorted(ayahs.items()):
    print(f"{name}: {text}")
```

### 1.3 Building a Simple API on Top of the Data

**With Flask (Python):**

```python
from flask import Flask, jsonify
app = Flask(__name__)

def load_translation(filepath):
    data = {}
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            if line.startswith('['):
                ref, _, text = line.partition('] ')
                sura, ayah = map(int, ref[1:].split(':'))
                data.setdefault(sura, {})[ayah] = text.rstrip('\n')
    return data

TRANSLATIONS = {
    'sahih': load_translation('output/quran_english_sahih.txt'),
    'yusufali': load_translation('output/quran_english_yusufali.txt'),
}

@app.route('/api/<translation>/<int:sura>/<int:ayah>')
def get_ayah(translation, sura, ayah):
    t = TRANSLATIONS.get(translation)
    if not t:
        return jsonify(error='Unknown translation'), 404
    text = t.get(sura, {}).get(ayah)
    if text is None:
        return jsonify(error='Ayah not found'), 404
    return jsonify(sura=sura, ayah=ayah, text=text, translation=translation)

# GET /api/sahih/1/1 → {"sura": 1, "ayah": 1, "text": "In the name...", "translation": "sahih"}
```

---

## 2. Embedding the Website (iFrame)

The live website can be embedded in another page using an `<iframe>`:

```html
<!-- Embed a specific surah page -->
<iframe 
  src="https://druvx13.github.io/Quran-data/001.html"
  width="100%"
  height="600"
  title="Surah Al-Fatihah">
</iframe>

<!-- Embed the search page -->
<iframe 
  src="https://druvx13.github.io/Quran-data/search.html"
  width="100%"
  height="800"
  title="Quran Search">
</iframe>
```

> ⚠️ GitHub Pages does not set `X-Frame-Options: DENY` by default, so iFrame embedding should work. However, this may change; test before deploying in production.

---

## 3. Integrating the Audio Stream

### 3.1 Direct Audio URL Construction

```python
def audio_url(sura: int, ayah: int) -> str:
    """Construct the Alafasy audio URL for a given sura and ayah."""
    base = "https://druvx13-quran-audio-alafasy.hf.space"
    return f"{base}/{sura:03d}{ayah:03d}.mp3"

# Examples:
print(audio_url(1, 1))    # https://druvx13-quran-audio-alafasy.hf.space/001001.mp3
print(audio_url(2, 255))  # https://druvx13-quran-audio-alafasy.hf.space/002255.mp3
print(audio_url(114, 6))  # https://druvx13-quran-audio-alafasy.hf.space/114006.mp3
```

### 3.2 Embedding Audio in an HTML Page

```html
<!-- Direct audio player for a specific ayah -->
<audio controls preload="none">
  <source src="https://druvx13-quran-audio-alafasy.hf.space/001001.mp3" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>

<!-- With JavaScript-generated URLs -->
<script>
function playAyah(sura, ayah) {
    const url = `https://druvx13-quran-audio-alafasy.hf.space/${String(sura).padStart(3,'0')}${String(ayah).padStart(3,'0')}.mp3`;
    const audio = new Audio(url);
    audio.play();
}

// Play Surah 1, Ayah 1
playAyah(1, 1);
</script>
```

---

## 4. Using the Search Index

The `docs/search-data.js` file contains a pre-built JavaScript search index. You can use it in a custom search interface:

```html
<script src="https://druvx13.github.io/Quran-data/search-data.js"></script>
<script>
// searchData is now available as a global variable
// Structure: { "1": { name: "Al-Fatihah", ayahs: [{ref, ar, translit, ya, hi}, ...] }, ... }

function search(query) {
    const q = query.toLowerCase();
    const results = [];
    for (const [suraNum, suraData] of Object.entries(searchData)) {
        for (const ayah of suraData.ayahs) {
            if (ayah.ya?.toLowerCase().includes(q) || 
                ayah.translit?.toLowerCase().includes(q) ||
                ayah.ar?.includes(query)) {
                results.push({
                    sura: parseInt(suraNum),
                    suraName: suraData.name,
                    ref: ayah.ref,
                    text: ayah.ya || ayah.translit
                });
            }
        }
    }
    return results;
}

console.log(search('mercy'));
</script>
```

---

## 5. Forking and Customising the Website

### 5.1 Adding a New Language to the Website

After adding a translation to `data/` and `gentxtforquran.py` (see `DEVELOPER_ONBOARDING.md` §5.1), update `gendocshtml.py` to display it on surah pages:

1. **Load the new output file** (near the top of the data-loading section):
```python
# Example: load a new Swahili translation
swahili_lines = []
with open('output/quran_swahili_example.txt', encoding='utf-8') as f:
    for line in f:
        if line.startswith('['):
            swahili_lines.append(line.rstrip('\n').split('] ', 1)[1])
```

2. **Add a CSS class** for the new row (in the inline `<style>` block):
```python
# Add to the CSS template string:
css_extra = """
.swahili { background: #f0fff0; }
.swahili-text { font-family: sans-serif; color: #006600; }
"""
```

3. **Add the row** to the per-ayah HTML generation loop:
```python
# Inside the ayah loop:
row_swahili = f'<tr class="swahili"><td>Swahili</td><td class="swahili-text">{swahili_lines[ayah_idx]}</td></tr>'
```

4. **Add a Content Filter checkbox:**
```python
# In the filter widget HTML:
checkbox_swahili = '<label><input type="checkbox" class="filter-cb" data-row="swahili" checked> Swahili</label>'
```

5. **Regenerate:**
```bash
python3 src/gendocshtml.py
```

### 5.2 Changing the Website Theme

All CSS is inline in the generated HTML (inside `<style>` tags). To change colours, fonts, or layout:

1. Search `gendocshtml.py` for the CSS template string
2. Modify colour values, font families, or layout properties
3. Re-run `python3 src/gendocshtml.py`

Example: change the Arabic text colour:
```python
# Find and modify in gendocshtml.py:
# Before: ".arabic-text { color: #1a1a6e; }"
# After:  ".arabic-text { color: #8B0000; }"
```

### 5.3 Replacing the Audio Source

To use a different audio recitation or self-hosted audio:

1. Find the audio URL in `gendocshtml.py`:
```bash
grep -n "hf.space\|audio" src/gendocshtml.py | head -20
```

2. Replace the base URL:
```python
# Before:
AUDIO_BASE = "https://druvx13-quran-audio-alafasy.hf.space"

# After (example — your own server):
AUDIO_BASE = "https://audio.yoursite.com/alafasy"
```

3. If the file naming convention differs, also update the URL construction:
```python
# Default: {sura:03d}{ayah:03d}.mp3 (e.g., 001001.mp3)
# Custom naming: {sura}_{ayah}.mp3 (e.g., 1_1.mp3)
audio_url = f"{AUDIO_BASE}/{sura}_{ayah}.mp3"
```

4. Regenerate the HTML:
```bash
python3 src/gendocshtml.py
```

---

## 6. PDF Integration

### 6.1 Downloading Pre-Built PDFs

The current pre-built PDFs are available in the `output/` directory of the repository:
- `output/farooq.pdf` — Hindi (Farooq Khan) + Arabic
- `output/suhail.pdf` — Hindi (Suhail) + Arabic

> Note: `sahih.pdf`, `translit.pdf`, and `pickthall.pdf` are listed as gitignored build artefacts and may not be committed to the repository. Check the current state of `output/` in the repository.

### 6.2 Generating Custom PDFs

To create a PDF for a different translation:

1. **Create a new content generator** in `gentexforquran.py`:
```python
# Add a new block for your translation (e.g., Urdu Junagarhi):
with open('latex/quurdu.tex', 'w') as target, \
     open('output/quran_urdu_junagarhi.txt', 'r', encoding='utf-8') as source:
    for sura_idx in range(114):
        target.write("\\chapter{%s}\n" % suraname[sura_idx])
        target.write("\\begin{Arabic}\n\\Huge{\\centerline{\\basmalah}}\\end{Arabic}\n")
        # Skip the [sura:ayah] prefix in the output file format
        for ayah_num in range(surasize[sura_idx]):
            target.write("\\flushright{\\begin{Arabic}\n")
            target.write("\\quranayah[%d][%d]\n" % (sura_idx+1, ayah_num+1))
            target.write("\\end{Arabic}}\n")
            line = source.readline()
            # Strip [sura:ayah] prefix
            text = line.split('] ', 1)[1].rstrip('\n') if '] ' in line else line.rstrip('\n')
            target.write("\\flushleft{\\begin{urdu}\n%s\n\\end{urdu}}\n" % text)
```

2. **Create a LaTeX template** (copy from an existing template like `sahih.tex`):
```bash
cp latex/sahih.tex latex/urdu_junagarhi.tex
# Edit the template to reference quurdu.tex and set language to Urdu
```

3. **Compile:**
```bash
cd latex && xelatex urdu_junagarhi.tex
mv urdu_junagarhi.pdf ../output/
```

---

## 7. Data Source Integration

### 7.1 Adding Translations from tanzil.net

1. Visit [https://tanzil.net/trans/](https://tanzil.net/trans/)
2. Select the translation and download in "Simple" or "Simple (with aya numbers)" format
3. Verify the format: one line per ayah, or `sura|ayah|text`
4. Place in `data/` with appropriate naming
5. Add to `translations` list in `gentxtforquran.py`

### 7.2 Adding Translations from quran.com API

```python
import requests
import time

def fetch_quran_com_translation(translation_id: int, output_file: str):
    """Fetch all 6236 ayahs from quran.com API (translation ID)."""
    lines = []
    for sura in range(1, 115):
        url = f"https://api.quran.com/api/v4/verses/by_chapter/{sura}"
        params = {
            'translations': translation_id,
            'per_page': 300,
            'page': 1,
            'fields': ''
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        for verse in data['verses']:
            text = verse['translations'][0]['text']
            # Strip HTML tags if present:
            text = re.sub(r'<[^>]+>', '', text)
            lines.append(text)
        time.sleep(0.5)  # Be respectful to the API
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

# Example: fetch Mufti Usmani (translation ID 84)
fetch_quran_com_translation(84, 'data/en.usmani.txt')
```

### 7.3 Adding Translations from fawazahmed0/quran-api

```python
import requests

def fetch_fawaz_translation(lang_code: str, output_file: str):
    """Fetch a translation from fawazahmed0/quran-api via jsdelivr CDN."""
    url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/{lang_code}.min.json"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    
    lines = [verse['text'] for verse in data['quran']]
    assert len(lines) == 6236, f"Expected 6236 ayahs, got {len(lines)}"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

# Example: fetch Aisha Bewley English
fetch_fawaz_translation('en-bewleyaisha', 'data/en.aishabewley.txt')
```

> ⚠️ Always verify ayah count (`wc -l data/en.newfile.txt` should return 6236) after fetching.

### 7.4 Adding Translations from quranenc.com

```python
import requests
import time

def fetch_quranenc_translation(translation_code: str, output_file: str):
    """Fetch all ayahs from quranenc.com API."""
    lines = []
    for sura in range(1, 115):
        url = f"https://quranenc.com/api/v1/translation/sura/{translation_code}/{sura}"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get('result', []):
            text = item.get('translation', '')
            # Strip footnote markers like [1], [2]:
            text = re.sub(r'\[\d+\]', '', text).strip()
            lines.append(text)
        time.sleep(0.5)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

# Example: fetch Rowwad English Translation
fetch_quranenc_translation('english_rwwad', 'data/en.rwwad.txt')
```
