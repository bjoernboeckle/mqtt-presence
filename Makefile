.PHONY: pylint test build clean all


pylint:
	poetry run pylint mqtt_presence

test:
	poetry run pytest tests


build: test pylint
	poetry build 


clean:
	rm -rf dist build *.egg-info


all: clean build