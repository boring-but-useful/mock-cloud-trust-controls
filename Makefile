PYTHON ?= python3
SAMPLE_AS_OF ?= 2026-09-18

.PHONY: help validate docs report test verify

help:
	@echo "make validate  Validate project data"
	@echo "make docs      Check local Markdown links"
	@echo "make report    Refresh Markdown, CSV, and JSON sample reports"
	@echo "make test      Run the test suite"
	@echo "make verify    Run validation, docs, report drift, and tests"

validate:
	$(PYTHON) scripts/validate_controls.py

docs:
	$(PYTHON) scripts/check_markdown_links.py

report:
	$(PYTHON) scripts/generate_report.py --as-of $(SAMPLE_AS_OF)
	$(PYTHON) scripts/generate_report.py --as-of $(SAMPLE_AS_OF) --format csv
	$(PYTHON) scripts/generate_report.py --as-of $(SAMPLE_AS_OF) --format json

test:
	$(PYTHON) -m unittest discover -s tests -v

verify:
	$(PYTHON) scripts/validate_controls.py --strict-warnings
	$(PYTHON) scripts/check_markdown_links.py
	$(PYTHON) scripts/generate_report.py --as-of $(SAMPLE_AS_OF) --strict-warnings
	$(PYTHON) scripts/generate_report.py --as-of $(SAMPLE_AS_OF) --format csv --strict-warnings
	$(PYTHON) scripts/generate_report.py --as-of $(SAMPLE_AS_OF) --format json --strict-warnings
	$(PYTHON) -m unittest discover -s tests -v
	git diff --exit-code -- reports/sample_report.md reports/sample_report.csv reports/sample_report.json
