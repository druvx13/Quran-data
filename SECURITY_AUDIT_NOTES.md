# Security Audit Notes

A security assessment of the Qur'an data project, covering the codebase, dependencies, data handling, and the static website.

> **Context:** This is a static data-processing and site-generation project. There is no runtime server, no user authentication, no database, and no API backend. The attack surface is correspondingly narrow.

<!-- TOC -->
- [1. Executive Summary](#1-executive-summary)
- [2. Threat Model](#2-threat-model)
- [3. Python Scripts Analysis](#3-python-scripts-analysis)
  - [3.1 Path Traversal](#31-path-traversal)
  - [3.2 Zip File Handling](#32-zip-file-handling)
  - [3.3 JSON Parsing](#33-json-parsing)
  - [3.4 Shell Injection](#34-shell-injection)
  - [3.5 Input Data Trust Boundary](#35-input-data-trust-boundary)
- [4. Static Website Analysis](#4-static-website-analysis)
  - [4.1 Content Security Policy](#41-content-security-policy)
  - [4.2 Cross-Site Scripting (XSS)](#42-cross-site-scripting-xss)
  - [4.3 External Resource Loading](#43-external-resource-loading)
  - [4.4 Audio Server CORS](#44-audio-server-cors)
  - [4.5 User Data in localStorage](#45-user-data-in-localstorage)
- [5. Supply Chain Security](#5-supply-chain-security)
- [6. Secrets and Credentials](#6-secrets-and-credentials)
- [7. License Compliance](#7-license-compliance)
- [8. Recommendations](#8-recommendations)
<!-- /TOC -->

---

## 1. Executive Summary

| Category | Risk Level | Notes |
|----------|-----------|-------|
| Remote code execution | **None** | No runtime server |
| SQL injection | **None** | No database |
| Path traversal (Python scripts) | **Low** | Scripts run locally by trusted contributors |
| Zip bomb / malicious ZIP | **Low** | ZIP sources are trusted translation files |
| XSS in generated HTML | **Low** | Translation text is injected as text content, not innerHTML |
| External script injection | **Low** | Only Google Fonts CDN loaded externally |
| Credential exposure | **None** | No secrets in the codebase |
| Supply chain (PyPI) | **None** | No third-party Python packages used |

---

## 2. Threat Model

**Trusted parties:**
- Repository maintainers running Python scripts locally
- GitHub Actions (if any automated builds are added)

**Untrusted inputs:**
- Translation data files in `data/` (especially files sourced from external APIs)
- User search queries on the website (processed entirely client-side)

**What an attacker could theoretically do:**
- Supply a malicious translation file that causes unexpected script behavior
- Inject HTML/JavaScript into generated HTML pages via translation text
- Exploit a browser vulnerability via a malicious font or audio file loaded from external sources

---

## 3. Python Scripts Analysis

### 3.1 Path Traversal

All file paths in the scripts are **hardcoded** in the `translations` list and in the open() calls. There is no user-controlled path construction. Example:

```python
# All paths are string literals — no user input involved
with open('data/en.sahih.txt', 'r', encoding='utf-8') as f:
```

**Risk:** None under normal operation. If a contributor adds a new `translations` entry with a path like `'data/../../etc/passwd'`, the script would attempt to read it, but this would be caught in code review.

**Recommendation:** No action required. Document that the `translations` list should only reference files in `data/`.

### 3.2 Zip File Handling

The JSON ZIP files are opened and read using Python's `zipfile` module:

```python
with zipfile.ZipFile(src_file, 'r') as zf:
    json_name = next(n for n in zf.namelist() if n.endswith('.json'))
    with zf.open(json_name) as jf:
        ayah_data = json.load(jf)
```

**Zip bomb risk:** Python's `zipfile` module does not automatically protect against zip bombs (highly compressed files that expand to enormous sizes). However:
- The ZIP files are static, version-controlled source files
- Their expected uncompressed size is well-known (~0.5–1 MB each)
- The `json.load()` call would exhaust memory before the OS, triggering an `OverflowError` or `MemoryError`

**Path traversal via ZIP entries:** The `zf.namelist()` filter only selects entries ending in `.json`. The `zf.open(json_name)` call reads from within the ZIP, not the filesystem. No path traversal risk.

**Recommendation:** For additional safety, validate file sizes before `json.load()`:
```python
info = zf.getinfo(json_name)
assert info.file_size < 50_000_000  # 50 MB limit
```
This is a minor hardening measure, not a critical fix.

### 3.3 JSON Parsing

```python
ayah_data = json.load(jf)
```

Python's `json` module is safe against common JSON attack vectors. There is no `eval()` or deserialization of arbitrary objects.

**Risk:** None.

### 3.4 Shell Injection

The Makefile calls Python scripts via `$(PYTHON) src/...` and XeLaTeX via `$(LATEX)`. The variables `PYTHON` and `LATEX` can be overridden on the command line:

```bash
make generate-txt PYTHON="python3; rm -rf /"  # hypothetical injection
```

**Risk:** Low — only affects operators running `make` locally. GitHub Pages itself does not use `make`. No automated CI pipeline currently uses `make`.

**Recommendation:** Document that `PYTHON` and `LATEX` overrides should only be used to specify interpreter/compiler paths, not arbitrary shell commands.

### 3.5 Input Data Trust Boundary

Translation text from `data/*.txt` files is read and written to output files and injected into HTML. The scripts use Python's built-in string formatting (`%s`, `write()`) to embed this text.

**In `gentxtforquran.py`:** Text is written to plain `.txt` files. No security concern.

**In `gentexforquran.py`:** Translation text is embedded into `.tex` files:
```python
targetu.write("\\flushleft{%s}\n" % translation_line.rstrip('\n'))
```
A malicious translation line containing `\end{document}` or other LaTeX commands would corrupt the generated `.tex` file and could cause unexpected PDF output or XeLaTeX errors.

**In `gendocshtml.py`:** Translation text is embedded into HTML. The risk depends on how the text is inserted — if it's embedded as text content (not via `innerHTML`), it is safe from XSS.

**Recommendation:** For `gentexforquran.py`, consider sanitising translation text to escape backslashes and braces, or at minimum noting this as a known limitation when adding new translations. For `gendocshtml.py`, verify that translation text is HTML-escaped before injection into page content.

---

## 4. Static Website Analysis

### 4.1 Content Security Policy

The generated HTML pages in `docs/` do not include a `Content-Security-Policy` HTTP header or meta tag. GitHub Pages does not support custom HTTP headers natively.

**Implication:** Without CSP, a browser will permit inline scripts, external scripts, and external resources. This is acceptable for a static site with no user accounts, no sensitive data, and no payment flows.

**Recommendation:** Consider adding a CSP meta tag to the generated HTML:
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self' 'unsafe-inline'; 
               style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; 
               font-src https://fonts.gstatic.com; 
               media-src https://druvx13-quran-audio-alafasy.hf.space;">
```
This would block unexpected script or resource injection.

### 4.2 Cross-Site Scripting (XSS)

The website injects Qur'an translation text into HTML pages at generation time. The key question is whether this injection is done safely.

**Generation-time injection** (in `gendocshtml.py`): If translation text is injected using Python string formatting into HTML, and if it contains `<`, `>`, `&`, `"` characters without escaping, those characters would become literal HTML when the page loads.

- Arabic text may contain `&` in HTML entity references (from Tanzil's HTML-tagged transliteration)
- English translations are unlikely to contain HTML metacharacters, but not impossible

**Browser-time injection:** The JavaScript search functionality uses `innerHTML` or similar when displaying results, which could be an XSS vector if search result data is not properly escaped.

**Risk:** Low for the current data set (religious text is unlikely to contain malicious payloads), but a good practice issue.

**Recommendation:** Review `gendocshtml.py` to ensure translation text is HTML-escaped using Python's `html.escape()` where appropriate, especially in JavaScript-rendered contexts.

### 4.3 External Resource Loading

The website loads resources from two external origins:
1. **Google Fonts** (`fonts.googleapis.com`, `fonts.gstatic.com`) — for Amiri Quran and Noto Sans fonts
2. **Hugging Face Space** (`druvx13-quran-audio-alafasy.hf.space`) — for MP3 audio files

**Risk for Google Fonts:** Google Fonts are widely used and trusted. The main risk is availability (if Google's CDN goes down, Arabic text would fall back to system fonts). No security risk.

**Risk for Hugging Face Audio:** The audio `src` attribute points to an external server. An attacker who compromised the Hugging Face Space could serve arbitrary audio files, but MP3 audio files cannot contain executable code exploitable by standard browsers.

### 4.4 Audio Server CORS

The audio files are served cross-origin (website is on `github.io`, audio is on `hf.space`). The audio server must return `Access-Control-Allow-Origin: *` (or the specific GitHub Pages origin) for the `<audio>` elements to work.

**Risk:** If CORS is too permissive (`*`), it allows any website to embed the audio files. For public Qur'an recitation audio, this is acceptable and arguably desirable.

### 4.5 User Data in localStorage

The website uses `localStorage` for:
- **`quran-cf`** — translation visibility preferences (which content rows are shown)
- **`quran-history`** — single `{s, n, t}` object recording the most recently visited surah
- **`quran-bookmark`** — array of bookmark entries `[{s, a, n, t}, …]` (surah, ayah, name, timestamp)

No personally identifiable information (PII) is stored. No data is transmitted to any server. All data stays entirely within the user's browser. The bookmark export feature writes a JSON file to the user's local filesystem on demand — no server upload occurs.

This is privacy-safe.

---

## 5. Supply Chain Security

**Python dependencies:** None. All three Python scripts use only the standard library (`json`, `os`, `re`, `zipfile`). There are no `requirements.txt`, `setup.py`, or `pyproject.toml` files. No `pip install` is required.

**LaTeX dependencies:** The `quran`, `polyglossia`, `fontspec` LaTeX packages are from CTAN (the official TeX package registry) and are typically installed as part of TeX Live or MiKTeX. These are trusted, widely-used packages.

**No npm, no Node.js, no frontend build tools.** The website is pure HTML/CSS/JavaScript with no bundler, transpiler, or package manager.

**Risk:** Very low. The project has minimal dependencies and no automated package installation.

---

## 6. Secrets and Credentials

A search of the repository confirms:
- **No API keys** in any source file
- **No authentication tokens** or passwords
- **No private keys** or certificates
- **No hardcoded URLs** that require authentication (audio URLs are public)

The Hugging Face Space URL (`druvx13-quran-audio-alafasy.hf.space`) is a public endpoint — no credentials are required to access it.

**Risk:** None.

---

## 7. License Compliance

The project uses a custom "Unconditional Liberty Instrument" (ULI) license for its scripts and configuration. However, the translation texts in `data/` and `output/` are reproduced from external sources and are subject to their original copyrights:

- **Pickthall (1930):** Public domain ✅
- **Yusuf Ali (1934):** Public domain ✅
- **Arabic text (Uthmani, from tanzil.net):** Subject to tanzil.net's redistribution terms
- **Other translations:** Subject to their respective translators' or publishers' rights

> ⚠️ **Important:** The ULI license applies only to the Python scripts, Makefile, and configuration files — not to the translation data. Users of this project should independently verify they have the right to use each translation for their intended purpose (especially for commercial use).

---

## 8. Recommendations

**Priority: Medium**
1. Add HTML escaping (`html.escape()`) for translation text injected into HTML in `gendocshtml.py`, particularly in JavaScript contexts like the search index.
2. Add a CSP meta tag to generated HTML pages to reduce the impact of any future XSS vulnerability.

**Priority: Low**
3. Add ZIP file size validation before `json.load()` to guard against unexpectedly large files.
4. Document the LaTeX injection risk in `gentexforquran.py` for contributors who add new translations.

**Priority: Informational**
5. Clarify per-translation licensing in the README (which translations are fully public domain vs. restricted use).
6. Consider pinning the Google Fonts import to HTTPS to ensure font loading over a secure channel (it already is, but worth confirming after future regenerations).
