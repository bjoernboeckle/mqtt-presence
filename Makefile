.PHONY: build clean version

version:
	python3 scripts/pre_build.py

pylint:
	python -m pylint mqtt_presence

build: version pylint
	python3 -m build

clean:
	rm -rf dist build *.egg-info mqtt_presence/version.py
