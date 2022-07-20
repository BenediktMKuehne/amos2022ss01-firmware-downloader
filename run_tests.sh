#!/usr/bin/env bash
export PYTHONPATH="$PYTHONPATH: ${PWD}/"
export PIPENV_VENV_IN_PROJECT="True"

# get parent folder
cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd || exit 1

# go to parent folder
cd ./amos2022ss01-firmware-downloader/amos2022ss01-firmware-downloader/ || exit 1

# run all unit tests
python -c "import os, sys; sys.path.append(os.path.abspath(os.path.join('./amos2022ss01-firmware-downloader/', '')))"
python -m pytest --import-mode=append ./amos2022ss01-firmware-downloader/unit_tests/*