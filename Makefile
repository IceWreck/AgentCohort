#!make
-include .env
export $(shell sed 's/=.*//' .env)
SHELL := /bin/bash

IMAGE_NAME = example.com/packages/agentcohort:latest

.PHONY: *

develop:
	uv sync --all-extras
	touch .env

format:
	uv run ruff format ./src

lint:
	uv run ruff check --fix src/
	uv run ruff check

typecheck:
	uv run basedpyright ./src

build:
	uv export --format requirements.txt --no-emit-project --no-hashes -o requirements.txt
	uv build
	podman build -t $(IMAGE_NAME) .

publish: build
	uv publish
