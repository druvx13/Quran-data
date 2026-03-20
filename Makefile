# All scripts are run from the repository root.
PYTHON   = python3
LATEX    = xelatex
LATEX_DIR = latex
OUTPUT_DIR = output

.PHONY: all generate-tex generate-txt generate-hadith generate-hadith-html generate-how-html generate-docs generate-khattab-pdf generate-khattab-book-pdf generate-hindi-mokhtasar-print-html clean help

## Show available targets.
help:
	@echo "Available targets:"
	@echo "  make generate-tex    Generate intermediate LaTeX content files (run first for PDFs)"
	@echo "  make all             Compile all PDFs (requires generate-tex first)"
	@echo "  make generate-khattab-pdf       Generate Khattab English+Transliteration PDF (output/khattab.pdf)"
	@echo "  make generate-khattab-book-pdf  Generate professional A5 book PDF, English only (output/quran_khattab_english_a5.pdf)"
	@echo "  make generate-txt    Generate formatted plain-text output files"
	@echo "  make generate-hadith      Generate plain-text Hadith output files (output/hadith/)"
	@echo "  make generate-hadith-html Generate Hadith HTML website (docs/hadith/)"
	@echo "  make generate-how-html    Generate Ethical & Duty Guide website (docs/how/)"
	@echo "  make generate-hindi-mokhtasar-print-html  Generate print-ready Hindi Mokhtasar HTML (output/hindi_mokhtasar_print.html)"
	@echo "  make generate-docs        Regenerate the docs/ HTML pages (requires generate-txt first)"
	@echo "  make clean                Remove LaTeX build artefacts"

## Build all PDFs (requires generate-tex to have been run first).
all: $(OUTPUT_DIR)/farooq.pdf $(OUTPUT_DIR)/suhail.pdf \
     $(OUTPUT_DIR)/sahih.pdf $(OUTPUT_DIR)/translit.pdf \
     $(OUTPUT_DIR)/pickthall.pdf

## Step 1: generate intermediate LaTeX content files from source data.
generate-tex:
	$(PYTHON) src/gentexforquran.py

## Step 2: compile PDFs from the LaTeX templates.
$(OUTPUT_DIR)/%.pdf: $(LATEX_DIR)/%.tex | $(OUTPUT_DIR)
	cd $(LATEX_DIR) && $(LATEX) $(<F) && mv $(*F).pdf ../$(OUTPUT_DIR)/

$(OUTPUT_DIR):
	mkdir -p $(OUTPUT_DIR)

# Declare that each PDF depends on its corresponding generated content file.
$(OUTPUT_DIR)/farooq.pdf:   $(LATEX_DIR)/qum.tex
$(OUTPUT_DIR)/suhail.pdf:   $(LATEX_DIR)/qup.tex
$(OUTPUT_DIR)/sahih.pdf:    $(LATEX_DIR)/qus.tex
$(OUTPUT_DIR)/translit.pdf: $(LATEX_DIR)/qut.tex
$(OUTPUT_DIR)/pickthall.pdf: $(LATEX_DIR)/qupk.tex
$(OUTPUT_DIR)/khattab.pdf:  $(LATEX_DIR)/quk.tex

## Generate Khattab English translation + Unicode transliteration PDF (no Arabic).
## Requires generate-tex to have been run first.
generate-khattab-pdf: $(OUTPUT_DIR)/khattab.pdf

## Generate professional A5 book PDF — English translation only, no transliteration.
## Self-contained: runs gen_khattab_book.py then compiles with XeLaTeX (two passes for TOC).
generate-khattab-book-pdf: | $(OUTPUT_DIR)
	$(PYTHON) src/gen_khattab_book.py
	cd $(LATEX_DIR) && $(LATEX) -interaction=nonstopmode khattab_book.tex && \
	  $(LATEX) -interaction=nonstopmode khattab_book.tex && \
	  mv khattab_book.pdf ../$(OUTPUT_DIR)/quran_khattab_english_a5.pdf

## Generate formatted plain-text output files.
generate-txt:
	$(PYTHON) src/gentxtforquran.py

## Generate plain-text Hadith output files.
generate-hadith:
	$(PYTHON) src/gen_hadith_txt.py

## Generate Hadith HTML website (docs/hadith/).
generate-hadith-html:
	$(PYTHON) src/gen_hadith_html.py

## Generate Ethical & Duty Guide website (docs/how/).
generate-how-html:
	$(PYTHON) src/gen_how_html.py

## Generate print-ready Hindi Mokhtasar HTML (output/hindi_mokhtasar_print.html).
generate-hindi-mokhtasar-print-html:
	$(PYTHON) src/gen_hindi_mokhtasar_print_html.py

## Regenerate the docs/ HTML pages (GitHub Pages).
## Requires generate-txt to have been run first.
generate-docs:
	$(PYTHON) src/gendocshtml.py

## Remove XeLaTeX build artefacts.
clean:
	rm -f $(LATEX_DIR)/*.aux $(LATEX_DIR)/*.log \
	      $(LATEX_DIR)/*.toc $(LATEX_DIR)/*.out \
	      $(LATEX_DIR)/*.synctex.gz
