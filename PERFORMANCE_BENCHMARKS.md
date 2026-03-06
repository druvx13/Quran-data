# Performance Benchmarks

Timing data, resource usage estimates, and optimization guidance for the Qur'an data project's build pipeline.

> **Note:** These benchmarks are estimates based on the project's data volume and typical hardware. Actual times will vary depending on CPU speed, disk I/O, and available memory.

<!-- TOC -->
- [1. Pipeline Stage Benchmarks](#1-pipeline-stage-benchmarks)
  - [1.1 gentxtforquran.py](#11-gentxtforquranpy)
  - [1.2 gentexforquran.py](#12-gentexforquranpy)
  - [1.3 gendocshtml.py](#13-gendocshtmlpy)
  - [1.4 XeLaTeX PDF Compilation](#14-xelatex-pdf-compilation)
- [2. Data Volume Reference](#2-data-volume-reference)
- [3. Website Runtime Performance](#3-website-runtime-performance)
  - [3.1 Page Load](#31-page-load)
  - [3.2 Search Performance](#32-search-performance)
  - [3.3 Audio Playback Latency](#33-audio-playback-latency)
- [4. Memory Usage](#4-memory-usage)
- [5. Optimization Notes](#5-optimization-notes)
  - [5.1 Current Bottlenecks](#51-current-bottlenecks)
  - [5.2 Quick Wins (If Performance Becomes an Issue)](#52-quick-wins-if-performance-becomes-an-issue)
  - [5.3 What Does Not Need Optimizing](#53-what-does-not-need-optimizing)
- [6. Disk Space Reference](#6-disk-space-reference)
<!-- /TOC -->

---

## 1. Pipeline Stage Benchmarks

### 1.1 gentxtforquran.py

| Hardware | Estimated Time |
|----------|---------------|
| Modern laptop (2020+, SSD) | 5–10 seconds |
| Older laptop (HDD) | 10–30 seconds |
| CI/CD runner | 5–15 seconds |

**Breakdown:**
- **71 translations** processed sequentially
- For plain-text translations (one-per-line): ~6,236 `readline()` calls per translation = ~442,756 total reads
- For JSON ZIP files (4 files): one `json.load()` per file loading ~6,236 key-value pairs
- **Total writes:** ~71 × 6,236 = ~442,756 lines written to disk

**Dominant cost:** Disk I/O for writing 71 output files. On an SSD, this is fast. On HDD, disk seek time dominates.

**To measure:**
```bash
time python3 src/gentxtforquran.py
```

### 1.2 gentexforquran.py

| Hardware | Estimated Time |
|----------|---------------|
| Modern laptop (SSD) | 1–3 seconds |
| Older laptop (HDD) | 3–10 seconds |

**Breakdown:**
- **5 content files** generated sequentially
- Each file: 114 surah headers + 6,236 ayah blocks = ~6,350 LaTeX fragments
- Each generated file is large (~1–3 MB of LaTeX markup)

**To measure:**
```bash
time python3 src/gentexforquran.py
```

### 1.3 gendocshtml.py

| Hardware | Estimated Time |
|----------|---------------|
| Modern laptop (SSD) | 30–90 seconds |
| Older laptop (HDD) | 1–5 minutes |

**Breakdown:**
- **16+ input files** read into memory at startup
- **114 surah HTML files** written (each 50–200 KB of HTML)
- **search-data.js** written (large JSON index, ~5–20 MB)
- Total HTML output: ~10–25 MB across 114+ files

**Dominant cost:** The combination of memory-resident data manipulation for 6,236 × 16+ data points, and writing ~120 files to disk.

**To measure:**
```bash
time python3 src/gendocshtml.py
```

### 1.4 XeLaTeX PDF Compilation

| PDF | Estimated Time | Size |
|-----|---------------|------|
| `farooq.pdf` (Hindi Farooq Khan) | 3–8 minutes | ~3.2 MB |
| `suhail.pdf` (Hindi Suhail) | 3–8 minutes | ~3.4 MB |
| `sahih.pdf` (English Saheeh Intl) | 2–6 minutes | ~2–4 MB |
| `translit.pdf` (Transliteration) | 2–5 minutes | ~2–4 MB |
| `pickthall.pdf` (English Pickthall) | 2–5 minutes | ~2–4 MB |

**Total for `make all`:** ~15–40 minutes

XeLaTeX is significantly slower than plain LaTeX because it loads OpenType fonts at compile time. Each run processes ~6,350 LaTeX constructs including Arabic text rendering.

> 💡 **Tip:** To reduce XeLaTeX time during development, compile one PDF at a time rather than running `make all`.

---

## 2. Data Volume Reference

| Metric | Value |
|--------|-------|
| Total ayahs | 6,236 |
| Total surahs | 114 |
| Source data files | ~80 files |
| Source data size (total) | ~75 MB |
| Generated plain-text files | 71 |
| Generated plain-text size (total) | ~80 MB |
| Generated HTML files | 120+ |
| Generated HTML size (total) | ~15–25 MB |
| search-data.js | ~5–20 MB |
| PDF files | 5 |
| PDF size (total) | ~15–20 MB |
| Audio files (external) | 6,236 MP3 files |
| Audio size (external) | ~600 MB |

---

## 3. Website Runtime Performance

### 3.1 Page Load

Each surah page (`docs/NNN.html`) is a self-contained static HTML file with inline CSS. Initial load time depends primarily on:
- Font loading from Google Fonts (first visit; cached on subsequent visits)
- `search-data.js` is only loaded by `search.html`, not individual surah pages

**Typical first-load time:** 1–3 seconds on a broadband connection.
**Typical cached load time:** <0.5 seconds.

Large surahs (e.g., Al-Baqarah `002.html` with 286 ayahs × 16+ content rows) produce large HTML files (~200+ KB). Modern browsers render these without issue.

### 3.2 Search Performance

The full-text search on `search.html` is entirely client-side, using a pre-built JavaScript index in `search-data.js`.

**Index size:** `search-data.js` contains all searchable content (Arabic, transliteration, Yusuf Ali translation, Hindi Tafsir) for all 6,236 ayahs. Expected file size: 5–20 MB.

**Initial search page load:** May be slow on first visit due to `search-data.js` download. Subsequent searches are instant (file cached by browser).

**Search query time:** Typically <100 ms for any query (JavaScript `String.includes()` or similar over in-memory data).

> ⚠️ **Performance note:** On mobile devices with limited RAM, loading a large `search-data.js` may be slow or cause the tab to reload. Consider lazy-loading the search index only when the user interacts with the search box, rather than at page load.

### 3.3 Audio Playback Latency

Audio is streamed from the Hugging Face Space. Latency depends on:
1. **Space wake-up time:** If the Space has been sleeping (no activity for several hours on the free tier), the first audio request may take 30–60 seconds while the Space starts up.
2. **Network latency:** After wake-up, individual MP3 files load in 0.5–2 seconds.
3. **File size:** Each MP3 is approximately 30–150 KB (depending on ayah length).

---

## 4. Memory Usage

### gentxtforquran.py
- **Peak memory:** Low. Files are read and written sequentially; only one translation's data is in memory at a time.
- For JSON ZIP files: the full JSON for one ZIP is loaded into memory (~5–20 MB per file). After processing, it is garbage-collected before the next JSON ZIP is processed.

### gentexforquran.py
- **Peak memory:** Very low. File handles are open concurrently (source + target), but no data is buffered — content is written line by line.

### gendocshtml.py
- **Peak memory:** Medium to high. All 16+ translation datasets for all 6,236 ayahs are loaded into memory before any HTML generation begins. Estimated peak: 200–500 MB.

---

## 5. Optimization Notes

### 5.1 Current Bottlenecks

1. **`gendocshtml.py` memory:** All source data loaded upfront. Could be restructured to load one surah's data at a time, but this would complicate the code significantly.

2. **`gendocshtml.py` I/O:** 120+ separate file writes. Python's `open()` + `write()` per file is efficient, but on HDD systems, sequential write overhead is noticeable.

3. **XeLaTeX:** Font loading is inherently slow. No practical optimization short of switching to a different PDF engine (which would require major template changes).

### 5.2 Quick Wins (If Performance Becomes an Issue)

- **Parallel generation of surah pages:** `gendocshtml.py` generates pages sequentially. A `multiprocessing.Pool` could parallelize HTML generation across CPU cores. Expected speedup: 2–4× on a quad-core machine.

- **Avoid redundant file reads:** `gentxtforquran.py` and `gendocshtml.py` both read `surasize` and `suraname` from inline constants. Moving these to a shared module would eliminate duplication (code quality, not a performance issue).

- **Cache search-data.js generation:** If only a few translations change, regenerating the full search index is wasteful. A diff-based approach could regenerate only the changed entries.

### 5.3 What Does Not Need Optimizing

- **`gentxtforquran.py` and `gentexforquran.py`:** These scripts run in seconds. No optimization needed.

- **Website page load:** Files are static; GitHub Pages CDN provides global caching. Load times are already optimal for static hosting.

---

## 6. Disk Space Reference

| Directory | Size |
|-----------|------|
| `data/` | ~75 MB |
| `output/` (text files only) | ~80 MB |
| `output/` (with PDFs) | ~95–100 MB |
| `docs/` | ~15–25 MB |
| `latex/` (with generated .tex) | ~12 MB (templates) + ~8 MB (generated) |
| Total repository | ~200–250 MB (without PDFs) |

**Git repository size (approximate):** The `.git/` directory stores history for all tracked files. Since PDFs are gitignored and plain-text files are efficiently delta-compressed, the git history is likely 50–150 MB for a mature repository.
