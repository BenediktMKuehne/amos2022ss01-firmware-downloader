#!/usr/bin/env bash

sudo apt-get install unzip

# download chromedriver
wget https://chromedriver.storage.googleapis.com/103.0.5060.134/chromedriver_linux64.zip

unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin
sudo chown root:root /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver

# Export paths
export PYTHONPATH="$PYTHONPATH: ../amos2022ss01-firmware-downloader"
export PIPENV_VENV_IN_PROJECT="True"

# get parent folder
cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd || exit 1

# go to parent folder
cd ../amos2022ss01-firmware-downloader || exit 1

# run all unit tests
python -c "import os, sys; sys.path.append(os.path.abspath(os.path.join('./amos2022ss01-firmware-downloader/', '')))"
python -c "from utils.chromium_downloader import ChromiumDownloader; ChromiumDownloader().executor()"
chmod u+r+x chromedriver.exe
python -m pytest --import-mode=append unit_tests/*