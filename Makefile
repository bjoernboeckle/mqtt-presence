.PHONY: version pylint test build clean all

version:
	python3 scripts/pre_build.py

pylint:
	poetry run pylint mqtt_presence

test:
	poetry run pytest tests


build: version test pylint
	poetry build 


clean:
	rm -rf dist build *.egg-info mqtt_presence/version.py


all: clean build