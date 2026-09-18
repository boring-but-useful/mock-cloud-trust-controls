PYTHON ?= python3

.PHONY: help validate report test verify

help:
	@echo "make validate  Validate project data"
	@echo "make report    Refresh Markdown, CSV, and JSON sample reports"
	@echo "make test      Run the test suite"
	@echo "make verify    Run strict validation, report drift check, and tests"

validate:
	$(PYTHON) scripts/validate_controls.py

report:
	$(PYTHON) scripts/generate_report.py
	$(PYTHON) scripts/generate_report.py --format csv
	$(PYTHON) scripts/generate_report.py --format json

test:
	$(PYTHON) -m unittest discover -s tests -v

verify:
	$(PYTHON) scripts/validate_controls.py --strict-warnings
	$(PYTHON) scripts/generate_report.py --strict-warnings
	$(PYTHON) scripts/generate_report.py --format csv --strict-warnings
	$(PYTHON) scripts/generate_report.py --format json --strict-warnings
	$(PYTHON) -m unittest discover -s tests -v
	git diff --exit-code -- reports/sample_report.md reports/sample_report.csv reports/sample_report.json
