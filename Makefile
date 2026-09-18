PYTHON ?= python3

.PHONY: help validate report test verify

help:
	@echo "make validate  Validate project data"
	@echo "make report    Refresh the sample report"
	@echo "make test      Run the test suite"
	@echo "make verify    Run strict validation, report drift check, and tests"

validate:
	$(PYTHON) scripts/validate_controls.py

report:
	$(PYTHON) scripts/generate_report.py

test:
	$(PYTHON) -m unittest discover -s tests -v

verify:
	$(PYTHON) scripts/validate_controls.py --strict-warnings
	$(PYTHON) scripts/generate_report.py --strict-warnings
	$(PYTHON) -m unittest discover -s tests -v
	git diff --exit-code -- reports/sample_report.md
