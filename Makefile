.PHONY: build clean version

version:
	python3 scripts/pre_build.py

pylint:
	poetry run pylint mqtt_presence

build: version pylint
	poetry run pytest tests
	poetry build 

clean:
	rm -rf dist build *.egg-info mqtt_presence/version.py
