#!/usr/bin/env bash

# download chromedriver
wget https://chromedriver.storage.googleapis.com/103.0.5060.134/chromedriver_linux64.zip

unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin
sudo chown root:root /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver
