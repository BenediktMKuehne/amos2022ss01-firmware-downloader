#!/usr/bin/env bash

# Export paths
export PYTHONPATH="$PYTHONPATH: ../amos2022ss01-firmware-downloader"
export PIPENV_VENV_IN_PROJECT="True"

# get parent folder
cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd || exit 1

# go to parent folder
cd ../amos2022ss01-firmware-downloader || exit 1

# run certain python prog and change file permission for chromedriver
python -c "import os, sys; sys.path.append(os.path.abspath(os.path.join('./amos2022ss01-firmware-downloader/', '')))"
python -c "from utils.chromium_downloader import ChromiumDownloader; ChromiumDownloader().executor()"
sudo chmod +rwx /home/runner/work/amos2022ss01-firmware-downloader/amos2022ss01-firmware-downloader/utils/chromedriver.exe
sudo chmod +rwx /home/runner/work/amos2022ss01-firmware-downloader/amos2022ss01-firmware-downloader/utils/chromedriver

# run all unit tests
python -m pytest --import-mode=append unit_tests/honeywell_unit_test.py
