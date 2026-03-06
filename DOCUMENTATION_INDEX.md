# Documentation Index

Master index of all documentation files in this repository.

**Repository:** druvx13/Quran-data  
**Analysis timestamp:** 2026-03-06  
**Documentation version:** 1.0  
**Branch:** cairo  

---

## 📚 Document Inventory

| # | Document | File | Purpose | Audience |
|---|----------|------|---------|----------|
| 0 | **README** | [README.md](README.md) | Project overview, live website link, tech stack, build instructions, data sources | Everyone |
| 1 | **Architecture** | [ARCHITECTURE.md](ARCHITECTURE.md) | System design, data flow diagrams (Mermaid), component descriptions, design decisions | Developers, architects |
| 2 | **API Reference** | [API_REFERENCE.md](API_REFERENCE.md) | Python script interfaces, data contracts, format specifications, Make targets | Developers |
| 3 | **Code Walkthrough** | [CODE_WALKTHROUGH.md](CODE_WALKTHROUGH.md) | File-by-file annotated guide to every source file | Developers (new contributors) |
| 4 | **Developer Onboarding** | [DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md) | Setup instructions, build pipeline walkthrough, first contribution guide | New contributors |
| 5 | **Deployment Runbook** | [DEPLOYMENT_RUNBOOK.md](DEPLOYMENT_RUNBOOK.md) | GitHub Pages deploy, audio server setup, rollback procedures, monitoring | Maintainers, operators |
| 6 | **Troubleshooting** | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common errors, diagnostics, and fixes for all pipeline stages | All contributors |
| 7 | **Glossary** | [GLOSSARY.md](GLOSSARY.md) | Domain terms, project-specific jargon, acronyms | Everyone |
| 8 | **Changelog Analysis** | [CHANGELOG_ANALYSIS.md](CHANGELOG_ANALYSIS.md) | Project history, major milestones, growth metrics, breaking changes | Maintainers, researchers |
| 9 | **Security Audit Notes** | [SECURITY_AUDIT_NOTES.md](SECURITY_AUDIT_NOTES.md) | Vulnerability assessment, best practices, recommendations | Security reviewers, maintainers |
| 10 | **Performance Benchmarks** | [PERFORMANCE_BENCHMARKS.md](PERFORMANCE_BENCHMARKS.md) | Build times, data volumes, website performance, optimization notes | Developers, operators |
| 11 | **Integration Playbook** | [INTEGRATION_PLAYBOOK.md](INTEGRATION_PLAYBOOK.md) | How to use data files, embed the website, build a custom API, fork and customize | Developers, integrators |
| 12 | **Contribution Guide** | [CONTRIBUTION_GUIDE.md](CONTRIBUTION_GUIDE.md) | PR process, coding standards, data standards, review workflow | Contributors |
| 13 | **FAQ Deep Dive** | [FAQ_DEEP_DIVE.md](FAQ_DEEP_DIVE.md) | Comprehensive answers to anticipated questions | Everyone |
| 14 | **Appendix: Raw Analysis** | [APPENDIX_RAW_ANALYSIS.md](APPENDIX_RAW_ANALYSIS.md) | Raw metrics, code analysis, edge cases, dependency inventory | Developers, researchers |
| — | **Changelog** | [CHANGELOG.md](CHANGELOG.md) | Version history in Keep a Changelog format | Everyone |
| — | **Contributing** | [CONTRIBUTING.md](CONTRIBUTING.md) | Quick contributor guide (summary of CONTRIBUTION_GUIDE.md) | Contributors |
| — | **License** | [LICENSE](LICENSE) | Unconditional Liberty Instrument (ULI) v1.0 | Legal |

---

## 🗺️ Navigation by Use Case

### "I want to browse the website"
→ [README.md](README.md) → Live website link

### "I want to bookmark a verse or see my saved bookmarks"
→ [bookmarks.html](https://druvx13.github.io/Quran-data/bookmarks.html) (live) — or use the 🔖 button on any verse page

### "I want to use the translation data files"
→ [INTEGRATION_PLAYBOOK.md §1](INTEGRATION_PLAYBOOK.md#1-using-the-plain-text-output-files) → [API_REFERENCE.md §5](API_REFERENCE.md#5-data-file-contracts)

### "I want to set up the project locally"
→ [DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)

### "I want to add a new translation"
→ [DEVELOPER_ONBOARDING.md §5.1](DEVELOPER_ONBOARDING.md#51-adding-a-new-translation) → [CONTRIBUTION_GUIDE.md §5](CONTRIBUTION_GUIDE.md#5-data-standards)

### "I want to understand how the code works"
→ [ARCHITECTURE.md](ARCHITECTURE.md) → [CODE_WALKTHROUGH.md](CODE_WALKTHROUGH.md)

### "I want to deploy or maintain the website"
→ [DEPLOYMENT_RUNBOOK.md](DEPLOYMENT_RUNBOOK.md)

### "Something broke"
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### "I don't understand a term"
→ [GLOSSARY.md](GLOSSARY.md)

### "I want to embed the audio in my app"
→ [INTEGRATION_PLAYBOOK.md §3](INTEGRATION_PLAYBOOK.md#3-integrating-the-audio-stream)

### "I want to contribute code"
→ [CONTRIBUTION_GUIDE.md](CONTRIBUTION_GUIDE.md) → [DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)

### "I have a security concern"
→ [SECURITY_AUDIT_NOTES.md](SECURITY_AUDIT_NOTES.md)

### "I want to understand the project history"
→ [CHANGELOG.md](CHANGELOG.md) → [CHANGELOG_ANALYSIS.md](CHANGELOG_ANALYSIS.md)

---

## 🏗️ Architecture Quick Reference

```
data/ ──► gentxtforquran.py ──► output/*.txt ──► gendocshtml.py ──► docs/
data/ ──► gentexforquran.py ──► latex/q*.tex ──► xelatex ──► output/*.pdf
```

See [ARCHITECTURE.md §3](ARCHITECTURE.md#3-system-diagram) for the full Mermaid diagram.

---

## 📊 Project Stats at a Glance

| Metric | Value |
|--------|-------|
| Translations | 71 |
| Languages | 8+ |
| Ayahs | 6,236 |
| Surahs | 114 |
| Website pages | 122+ (114 surah + index, search, bookmarks, config, sources, license, download) |
| Python scripts | 3 |
| Python LOC | ~2,276 |
| External dependencies | 0 (Python stdlib only) |
| License | ULI v1.0 (public-domain equivalent) |
