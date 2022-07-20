#!/usr/bin/env bash
export PYTHONPATH="$PYTHONPATH: ${PWD}/"
export PIPENV_VENV_IN_PROJECT="True"

# get parent folder
cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd || exit 1

# go to parent folder
cd .. || exit 1

# run all unit tests
python -m pytest --import-mode=append unit_tests/