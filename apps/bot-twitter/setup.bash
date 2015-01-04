#!/bin/bash

apt-get -y install python-virtualenv
virtualenv twitter-env
source twitter-env/bin/activate
pip install -r requirements.txt

