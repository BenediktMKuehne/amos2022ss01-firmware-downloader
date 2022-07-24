#!/bin/bash

RANDOM_PW=$(tr -dc 'a-zA-Z0-9' < /dev/urandom | fold -w 10 | head -n 1)

# first install
is_python_installed=0
if  [[ $(which python) ]] ; then
       echo "Python is installed"
        python --version
        is_python_installed=1
fi
if [[ $(which python3) ]] ; then
	echo "Python is installed"
	python3 --version
	is_python_installed=1
fi
if [[ $is_python_installed == 0 ]] ; then
	echo "Python installation not found"
	echo "installing python"
	export DEBIAN_FRONTEND=noninteractive
	apt-get update
	apt-get install -y software-properties-common
	add-apt-repository ppa:deadsnakes/ppa
	apt-get install -y python3.8
fi

pip install -U pip
# to install a requirements.txt file:
pip install -r requirements.txt

echo "Packages Installed Successfully"

USER_NAME="firmware.downloader"
PASSWORD=$RANDOM_PW

echo "{\"username\":\"${USER_NAME}\", \"password\":\"${PASSWORD}\"}" > config/auth_config.json

echo "DB Username=$USER_NAME"
echo "DB Password=$PASSWORD"
echo "Config File Created Successfully For DB Username and Password"
