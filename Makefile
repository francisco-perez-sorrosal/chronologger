MODULE := chronologger
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CHRONOLOGGER_CONTAINER ?= chronologger-dev

install-dev:
	@pip install -r requirements_dev.txt
	@pip install -e .

clean:
	rm -rf .pytest_cache .coverage .pytest_cache coverage.xml

tests:
	@pytest -vv

lint:
	@echo "\n${BLUE}Running Pylint against source and test files...${NC}\n"
	@pylint --rcfile=setup.cfg **/*.py
	@echo "\n${BLUE}Running Flake8 against source and test files...${NC}\n"
	@flake8
	@echo "\n${BLUE}Running Bandit against source files...${NC}\n"
	@bandit -r --ini setup.cfg

dbuild:
	@docker build -f Dockerfile.dev -t chronologger-dev .

drun:
	@docker run -itd --name $(CHRONOLOGGER_CONTAINER) --mount type=bind,source="$(PWD)",target=/src/chronologger chronologger-dev:latest

dstart:
	@docker start $(CHRONOLOGGER_CONTAINER)

dstop:
	@docker stop $(CHRONOLOGGER_CONTAINER)

drm:
	@docker rm $(CHRONOLOGGER_CONTAINER)

dconn:
	@docker exec -it $(CHRONOLOGGER_CONTAINER) /bin/bash

dtests:
	@docker exec $(CHRONOLOGGER_CONTAINER) pytest


.PHONY: clean tests dbuild drun dstop dconn
