# Contribution Guide

Thank you for contributing to the Qur'an Multi-Translation Study Website & PDF Typesetting project. This guide provides detailed information on the PR process, coding standards, data standards, and review workflow.

<!-- TOC -->
- [1. Getting Started](#1-getting-started)
- [2. Types of Contributions](#2-types-of-contributions)
- [3. Development Workflow](#3-development-workflow)
  - [3.1 Branch Naming](#31-branch-naming)
  - [3.2 Commit Messages](#32-commit-messages)
  - [3.3 PR Checklist](#33-pr-checklist)
- [4. Coding Standards](#4-coding-standards)
  - [4.1 Python Style](#41-python-style)
  - [4.2 Naming Conventions](#42-naming-conventions)
  - [4.3 Comments and Docstrings](#43-comments-and-docstrings)
- [5. Data Standards](#5-data-standards)
  - [5.1 Adding a New Translation File](#51-adding-a-new-translation-file)
  - [5.2 Data Quality Requirements](#52-data-quality-requirements)
  - [5.3 Source Attribution Requirements](#53-source-attribution-requirements)
- [6. HTML/CSS Standards](#6-htmlcss-standards)
- [7. LaTeX Standards](#7-latex-standards)
- [8. Documentation Standards](#8-documentation-standards)
- [9. Review Process](#9-review-process)
- [10. Code of Conduct](#10-code-of-conduct)
<!-- /TOC -->

---

## 1. Getting Started

Before contributing, please:
1. Read `README.md` to understand the project
2. Read `DEVELOPER_ONBOARDING.md` to set up your environment
3. Browse open issues on GitHub to find something to work on, or create a new issue to discuss your idea before starting

For a complete setup guide, see [DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md).

---

## 2. Types of Contributions

| Type | Description | Complexity |
|------|-------------|-----------|
| **Bug fix** | Fix incorrect output, parsing errors, display issues | Low–Medium |
| **New translation** | Add a new language or translator to the data set | Low |
| **Website improvement** | Improve HTML, CSS, JavaScript in `gendocshtml.py` | Medium |
| **PDF/LaTeX improvement** | Improve typesetting templates | Medium–High |
| **Documentation** | Improve README, CONTRIBUTING, or other docs | Low |
| **New feature** | Add new functionality (e.g., new website feature) | High |
| **Refactoring** | Clean up code without changing behavior | Medium |

Most contributions fall into the "new translation" or "website improvement" categories.

---

## 3. Development Workflow

### 3.1 Branch Naming

```
feature/add-swahili-translation
fix/correct-ayah-offset-en-sahih
docs/improve-contributing-guide
refactor/consolidate-sura-metadata
```

- Use lowercase with hyphens
- Start with a category prefix: `feature/`, `fix/`, `docs/`, `refactor/`, `chore/`
- Be descriptive but concise

### 3.2 Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) style:

```
<type>(<scope>): <short description>

[optional body]
[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `chore`

**Examples:**
```
feat(data): add Swahili translation by Ahmad Kheri

Source: quranenc.com (swahili_kheri)
6236 ayahs, one-per-line format, UTF-8

feat(website): add Swahili row to all surah pages

- New CSS classes .swahili and .swahili-text
- Content Filter checkbox added (unchecked by default)

fix(gentxtforquran): handle BOM in en.wahiduddin source file

docs(readme): update output/ table with new Swahili file
```

**Keep commits focused:** One logical change per commit. Don't mix data file additions with unrelated CSS changes.

### 3.3 PR Checklist

Before opening a pull request, verify:

**For new translations:**
- [ ] Data file placed in `data/` with correct naming convention
- [ ] Entry added to `translations` list in `src/gentxtforquran.py`
- [ ] `python3 src/gentxtforquran.py` runs without errors
- [ ] `grep -c "^\[" output/quran_<lang>_<name>.txt` returns `6236`
- [ ] First ayah (`[1:1]`) looks correct
- [ ] Last ayah (`[114:6]`) looks correct
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] `README.md` updated (data/ table, output/ table)
- [ ] If adding to website: `python3 src/gendocshtml.py` runs without errors, website previewed locally

**For website changes:**
- [ ] `python3 src/gendocshtml.py` runs without errors
- [ ] Site previewed locally with `python3 -m http.server 8000` from `docs/`
- [ ] Tested at mobile width (≤600px) using browser DevTools
- [ ] Dark mode verified
- [ ] Search functionality verified
- [ ] Content Filter widget verified
- [ ] `docs/` changes committed

**For Python script changes:**
- [ ] Script runs without errors from repository root
- [ ] Output files have correct line counts
- [ ] Existing translations still produce correct output (spot-check 2–3 files)

**For all PRs:**
- [ ] Branch created from latest `cairo`
- [ ] Commit messages follow the convention above
- [ ] PR title summarises the change
- [ ] PR description explains what changed and why
- [ ] PR description includes verification steps taken

---

## 4. Coding Standards

### 4.1 Python Style

Follow [PEP 8](https://peps.python.org/pep-0008/):

```python
# ✅ Good
surasize = [7, 286, 200, ...]  # spaces after commas
translations = [
    ('data/en.sahih.txt', 'output/quran_english_sahih.txt', 'Saheeh International', 'English'),
]

# ❌ Avoid
surasize=[7,286,200,...]  # no spaces (original scripts have this — new code should not)
```

**Target Python version:** 3.6+ (no f-strings beyond what's already in the codebase; use `%` formatting to match existing style).

**Indentation:** 4 spaces (no tabs). The existing scripts are already PEP 8-compliant in this respect.

**Line length:** Aim for ≤100 characters. Long `translations` list entries may exceed 80 characters — this is acceptable for readability.

**Imports:** Only standard library imports. Do not add third-party library dependencies.

### 4.2 Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Python variables | `snake_case` | `sura_num`, `out_file` |
| Python constants | `UPPER_CASE` in `gendocshtml.py`; `lower_case` in other scripts (historical) | `SURA_SIZE`, `surasize` |
| Data files | `<lang>.<author>.txt` | `en.sahih.txt`, `ur.junagarhi.txt` |
| Output files | `quran_<language>_<author>.txt` | `quran_english_sahih.txt` |
| CSS classes | `kebab-case` | `.arabic-text`, `.hindi-farooq` |

### 4.3 Comments and Docstrings

- Each script has a module-level docstring explaining its purpose and how to run it. Maintain this style for any new scripts.
- Inline comments in the `translations` list use the form `# Source or category description`.
- Do not add comments that simply restate what the code does — prefer comments that explain **why**.

```python
# ✅ Useful comment
# Strip footnote markers like [1], [2] added by quranenc.com
text = re.sub(r'\[\d+\]', '', text).strip()

# ❌ Useless comment
# Write the line to the output file
out.write("[%d:%d] %s\n" % (sura_num + 1, ayah_num, text))
```

---

## 5. Data Standards

### 5.1 Adding a New Translation File

**File placement:** `data/<lang>.<author>.txt` or `data/<lang>.<author>.json.zip`

**Encoding:** UTF-8 (no BOM). Strip any BOM before committing:
```bash
# Check for BOM:
python3 -c "f=open('data/new.txt','rb'); print(f.read(3).hex())"
# BOM = efbbbf — if present, strip it

# Strip BOM with sed:
sed -i '1s/^\xEF\xBB\xBF//' data/new.txt
```

**Line endings:** Unix (`\n`). Do not commit files with Windows CRLF (`\r\n`):
```bash
# Check for CRLF:
file data/new.txt  # Should say "ASCII text" or "UTF-8 Unicode text"

# Convert CRLF to LF:
sed -i 's/\r//' data/new.txt
```

**Line count:** Plain-text one-per-line files must have exactly 6,236 lines:
```bash
wc -l data/new.txt  # Should be 6236 (or 6237 if there is a trailing newline)
grep -c "." data/new.txt  # Count non-empty lines — should be 6236
```

### 5.2 Data Quality Requirements

Before committing a new data file:
1. **Verify line count:** 6,236 data lines for plain-text formats
2. **Verify encoding:** UTF-8, no BOM
3. **Spot-check key ayahs:**
   - `[1:1]` (Al-Fatihah verse 1 — Bismillah)
   - `[2:255]` (Ayat al-Kursi — famous verse)
   - `[112:1]` (Al-Ikhlas — short, easy to verify)
   - `[114:6]` (An-Nas verse 6 — last ayah)
4. **Verify no garbled characters:** Search for unexpected Unicode ranges
5. **Check for stripped footnote markers:** Markers like `[1]`, `[N]`, `{n}` from original sources should be stripped

### 5.3 Source Attribution Requirements

Every data file must have a documented source. In your PR:
1. State the source URL or database name
2. Confirm the translation is freely redistributable for this purpose (educational, non-commercial)
3. Note any preprocessing steps applied (footnote stripping, BOM removal, encoding conversion)

These details should appear in both the `CHANGELOG.md` entry and the `README.md` update.

---

## 6. HTML/CSS Standards

All HTML is generated by `src/gendocshtml.py`. No manual HTML editing.

When adding new CSS to the generator:
- Use descriptive class names: `.arabic-text` not `.at1`
- Add dark-mode variants for any new background or text colours
- Test responsive behaviour at 600px and 380px breakpoints
- Maintain the existing pattern of inline CSS (all styles are embedded in `<style>` tags per page)
- Add print stylesheet overrides for any new layout changes

**Accessibility:**
- `<audio>` elements must have `controls` attribute
- Language attributes (`lang="ar"`, `lang="hi"`, etc.) should be set on text content
- Checkboxes in the Content Filter should have associated `<label>` elements

---

## 7. LaTeX Standards

Generated content files (`latex/q*.tex`) are produced by `src/gentexforquran.py` — do not edit them by hand.

When modifying `gentexforquran.py`:
- Use `\\chapter`, `\\quranayah`, `\\basmalah` from the `quran` package
- Wrap Arabic text in `\\begin{Arabic}...\\end{Arabic}`
- Wrap Hindi text in `\\begin{hindi}...\\end{hindi}`
- Add new language environments to `latex/quran.sty` if needed
- Test by running `make generate-tex && cd latex && xelatex <template>.tex`

When modifying LaTeX templates:
- Templates are human-maintained (not generated)
- Use `\\input{quran}` or `\\usepackage{quran}` to load the required package
- Document any new font requirements in comments within the template

---

## 8. Documentation Standards

- Keep `README.md` as the primary entry point — it should always reflect the current state of the project
- Update `CHANGELOG.md` with every meaningful change under `[Unreleased]` before release
- Update `CONTRIBUTING.md` (this file) if the contribution process changes
- Use the same Markdown style as existing docs:
  - ATX-style headers (`##` not underline style)
  - Fenced code blocks with language identifiers (` ```python ` not ` ``` `)
  - Tables for structured comparisons

---

## 9. Review Process

PRs are reviewed by the repository maintainer. Typical review criteria:

1. **Correctness:** Does the change do what it claims? Is the output correct?
2. **Data quality:** For new translations, are the 6,236 ayahs present and properly formatted?
3. **Attribution:** Is the source documented? Is the license acceptable?
4. **Code quality:** Does Python code follow PEP 8? Are variable names clear?
5. **Completeness:** Are `README.md` and `CHANGELOG.md` updated?
6. **No regressions:** Do existing translations still produce correct output?

**Typical review timeline:** 1–7 days depending on the maintainer's availability.

**Addressing review comments:**
- Push additional commits to your branch to address comments
- Reply to review comments with a brief explanation of what you changed
- Do not force-push after a review has started (it makes it harder to see what changed)

---

## 10. Code of Conduct

This project deals with the holy Qur'an — a text of profound religious significance for over 1.8 billion Muslims worldwide. All contributions and discussions should reflect this sensitivity:

- Be respectful and constructive in all communications
- Approach all discussions of translations, interpretations, and textual matters with care
- Do not disparage any translation, translator, or religious tradition
- Prioritise accuracy and respect for the source material in all data contributions
- Remember that contributors come from diverse backgrounds — assume good faith

Disrespectful or inflammatory behaviour will result in removal from the project.

---

For questions or to discuss a potential contribution before starting, please open a GitHub issue with the `question` or `discussion` label.
