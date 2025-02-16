#!/bin/bash

git config --global core.autocrlf false
git config --global core.eol lf

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate