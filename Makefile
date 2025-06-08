.PHONY: $(COMMANDS) set-version

COMMANDS := clean pylint pytest build build-exe installer winget chocolatey all

$(COMMANDS):
	python ./scripts/make.py $@


set-version:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: Please provide VERSION=<new_version>"; \
		exit 1; \
	fi
	python ./scripts/make.py set-version $(VERSION)
