#! /usr/bin/env bash

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install Dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install --install-hooks
