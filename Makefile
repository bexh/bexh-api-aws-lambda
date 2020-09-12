#!make

export PYTHON_VERSION := 3.8

#SHELL := /bin/bash

install-dev:
	@+pipenv install --python ${PYTHON_VERSION} --dev

install:
	@+pipenv install --python ${PYTHON_VERSION}

build:
	pip freeze > requirements.txt

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

local-setup:
	python scripts/local_setup.py
