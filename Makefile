.PHONY: build clean version

version:
	python3 scripts/pre_build.py

build: version
	python3 -m build

clean:
	rm -rf dist build *.egg-info mqtt_presence/version.py
