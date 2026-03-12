# All scripts are run from the repository root.
PYTHON   = python3
LATEX    = xelatex
LATEX_DIR = latex
OUTPUT_DIR = output

.PHONY: all generate-tex generate-txt generate-docs generate-hindi-web clean help

## Show available targets.
help:
	@echo "Available targets:"
	@echo "  make generate-tex   Generate intermediate LaTeX content files (run first for PDFs)"
	@echo "  make all            Compile all PDFs (requires generate-tex first)"
	@echo "  make generate-txt   Generate formatted plain-text output files"
	@echo "  make generate-docs  Regenerate the docs/ HTML pages (requires generate-txt first)"
	@echo "  make generate-hindi-web Generate Hindi-only website into hindi-web/ (uses existing output files)"
	@echo "  make clean          Remove LaTeX build artefacts"

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

## Generate formatted plain-text output files.
generate-txt:
	$(PYTHON) src/gentxtforquran.py

## Regenerate the docs/ HTML pages (GitHub Pages).
## Requires generate-txt to have been run first.
generate-docs:
	$(PYTHON) src/gendocshtml.py

## Generate the Hindi-only website (hindi-web/).
## Requires output files to be present (run generate-txt first).
generate-hindi-web:
	$(PYTHON) src/gen_hindi_web.py

## Remove XeLaTeX build artefacts.
clean:
	rm -f $(LATEX_DIR)/*.aux $(LATEX_DIR)/*.log \
	      $(LATEX_DIR)/*.toc $(LATEX_DIR)/*.out \
	      $(LATEX_DIR)/*.synctex.gz
