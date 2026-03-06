# Deployment Runbook

This document covers deploying and operating the Qur'an data project in production — primarily the GitHub Pages website and the audio hosting service.

<!-- TOC -->
- [1. GitHub Pages Deployment](#1-github-pages-deployment)
  - [1.1 How It Works](#11-how-it-works)
  - [1.2 Standard Deploy Process](#12-standard-deploy-process)
  - [1.3 Verifying a Deployment](#13-verifying-a-deployment)
- [2. Audio Server Deployment](#2-audio-server-deployment)
  - [2.1 Hugging Face Spaces (Current Setup)](#21-hugging-face-spaces-current-setup)
  - [2.2 Self-Hosting on a VPS](#22-self-hosting-on-a-vps)
  - [2.3 Updating the Audio Base URL](#23-updating-the-audio-base-url)
- [3. Rollback Procedures](#3-rollback-procedures)
  - [3.1 Rollback docs/ to a Previous Commit](#31-rollback-docs-to-a-previous-commit)
  - [3.2 Rollback a Broken Translation File](#32-rollback-a-broken-translation-file)
- [4. Monitoring](#4-monitoring)
- [5. Maintenance Checklist](#5-maintenance-checklist)
<!-- /TOC -->

---

## 1. GitHub Pages Deployment

### 1.1 How It Works

The live website at [https://druvx13.github.io/Quran-data/](https://druvx13.github.io/Quran-data/) is served directly from the `docs/` directory on the `cairo` branch via GitHub Pages.

GitHub Pages serves static files — there is no server-side processing. Every time you push a commit to `cairo` that contains changes in `docs/`, GitHub Pages automatically re-deploys within 1–5 minutes.

**Configuration:** GitHub Pages is set to serve from the `docs/` folder of the `cairo` branch. This is configured in the repository Settings → Pages.

### 1.2 Standard Deploy Process

A complete regeneration and deployment:

```bash
# 1. Ensure you are on the cairo branch with latest changes:
git checkout cairo
git pull origin cairo

# 2. Generate plain-text output files:
python3 src/gentxtforquran.py

# 3. Regenerate the HTML website:
python3 src/gendocshtml.py

# 4. Stage and review changes:
git diff --stat docs/

# 5. Commit and push:
git add docs/ output/
git commit -m "Regenerate docs/ and output/ with latest translations"
git push origin cairo
```

**Deployment timeline after push:** GitHub Pages typically deploys within 1–5 minutes. Check the Actions tab or the deployment badge on the repository page.

### 1.3 Verifying a Deployment

After pushing to `cairo`:

1. **Check GitHub Actions:** Navigate to the repository → Actions tab. Look for a "pages-build-deployment" workflow run. A green checkmark means the deployment succeeded.

2. **Check the live URL:** Open [https://druvx13.github.io/Quran-data/](https://druvx13.github.io/Quran-data/) in a browser (ideally in a private/incognito window to bypass cache).

3. **Spot-check a surah page:** Navigate to [https://druvx13.github.io/Quran-data/001.html](https://druvx13.github.io/Quran-data/001.html) and verify:
   - Arabic text displays correctly
   - Audio player loads
   - Translation rows are visible
   - Dark mode toggle works

4. **Test search:** Go to [https://druvx13.github.io/Quran-data/search.html](https://druvx13.github.io/Quran-data/search.html) and search for a common word (e.g., "mercy").

5. **Check the download page:** Verify links on `download.html` resolve to the correct output files.

---

## 2. Audio Server Deployment

### 2.1 Hugging Face Spaces (Current Setup)

The audio files are hosted at `druvx13-quran-audio-alafasy.hf.space`. This is a Hugging Face Space running a Docker container that serves MP3 files via Python's built-in HTTP server.

**Space URL:** `https://huggingface.co/spaces/druvx13/quran-audio-alafasy`

The Docker configuration:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y wget unzip && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /app/public
RUN wget -q https://everyayah.com/data/Alafasy_128kbps/000_versebyverse.zip -O /app/000_versebyverse.zip
RUN unzip -q /app/000_versebyverse.zip -d /app/public/
RUN rm /app/000_versebyverse.zip
EXPOSE 7860
WORKDIR /app/public
CMD ["python", "-m", "http.server", "7860"]
```

**File naming convention:** `<SSS><AAA>.mp3` where `SSS` = zero-padded 3-digit surah number and `AAA` = zero-padded 3-digit ayah number. Example: `001001.mp3` = Al-Fatihah ayah 1.

**If the Hugging Face Space goes offline or the ZIP source is unavailable:**
- Try the Wayback Machine archive:
  ```
  https://web.archive.org/web/20260222041205/https://everyayah.com/data/Alafasy_128kbps/000_versebyverse.zip
  ```
- Or download from Hugging Face Hub: `druvx13/quran-audio-alafasy`

### 2.2 Self-Hosting on a VPS

To host audio on your own server:

```bash
# 1. Download the audio ZIP (6,236 MP3 files, ~600 MB):
wget https://everyayah.com/data/Alafasy_128kbps/000_versebyverse.zip

# 2. Extract:
unzip 000_versebyverse.zip -d /var/www/quran-audio/

# 3. Serve with nginx (example config):
# server {
#     listen 80;
#     server_name audio.yourdomain.com;
#     root /var/www/quran-audio;
#     autoindex on;
#     add_header Access-Control-Allow-Origin "*";
# }

# 4. Or serve with Python for quick testing:
cd /var/www/quran-audio && python3 -m http.server 8080
```

> ⚠️ **CORS header required:** The website loads audio cross-origin. Your server must include `Access-Control-Allow-Origin: *` (or the specific GitHub Pages domain) in its response headers.

### 2.3 Updating the Audio Base URL

After deploying your own audio server, update the URL in `gendocshtml.py`:

```bash
# Find the current audio URL pattern:
grep -n "hf.space" src/gendocshtml.py

# Replace with your server URL (e.g., https://audio.yourdomain.com/):
# Edit src/gendocshtml.py line(s) found above

# Regenerate the HTML:
python3 src/gendocshtml.py

# Deploy:
git add docs/
git commit -m "Update audio server URL to self-hosted"
git push origin cairo
```

---

## 3. Rollback Procedures

### 3.1 Rollback docs/ to a Previous Commit

If a regeneration broke the website:

```bash
# Find the last good commit:
git log --oneline docs/ | head -10

# Revert docs/ to that commit:
git checkout <good-commit-hash> -- docs/

# Commit the rollback:
git commit -m "Rollback docs/ to <good-commit-hash>"
git push origin cairo
```

### 3.2 Rollback a Broken Translation File

If a data file in `data/` was incorrectly modified:

```bash
# Revert specific file:
git checkout <last-good-commit> -- data/en.sahih.txt

# Or revert to upstream:
git checkout origin/cairo -- data/en.sahih.txt

# Commit:
git commit -m "Revert data/en.sahih.txt to last known good version"
```

After rollback, re-run the generators:
```bash
python3 src/gentxtforquran.py
python3 src/gendocshtml.py
git add output/ docs/
git commit -m "Regenerate outputs after data rollback"
git push origin cairo
```

---

## 4. Monitoring

This project has no active server monitoring (it is a static site). Manual checks are sufficient:

| Check | Frequency | How |
|-------|-----------|-----|
| Website accessibility | Weekly | Open [https://druvx13.github.io/Quran-data/](https://druvx13.github.io/Quran-data/) |
| Audio player functionality | Weekly | Play a few ayahs on a surah page |
| Search functionality | Weekly | Run a test search on `search.html` |
| GitHub Pages build status | After each push | Check Actions tab |
| Hugging Face Space status | Monthly | Check space health on HF dashboard |

**GitHub Pages status page:** [https://www.githubstatus.com/](https://www.githubstatus.com/)

---

## 5. Maintenance Checklist

### Before each release / major push:

- [ ] Run `python3 src/gentxtforquran.py` and verify 71 files generated
- [ ] Run `grep -c "^\[" output/quran_arabic.txt` returns `6236`
- [ ] Run `python3 src/gendocshtml.py` without errors
- [ ] Preview site locally at `http://localhost:8000`
- [ ] Verify search works on `search.html`
- [ ] Verify audio plays on at least one surah page
- [ ] Verify dark mode toggle works
- [ ] Verify mobile layout at `max-width: 600px`
- [ ] Update `CHANGELOG.md`
- [ ] Push to `cairo` and verify GitHub Pages deploys successfully

### Periodic maintenance:

- [ ] Verify Hugging Face Space is still running (audio)
- [ ] Check if any translation sources have updated their data
- [ ] Review open GitHub issues
- [ ] Update documentation if scripts have changed
