.PHONY: build clean version

version:
	python scripts/pre_build.py

build: version
	python -m build

clean:
	rm -rf dist build *.egg-info mqtt_presence/version.py
