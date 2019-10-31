#!/bin/bash

# python3 -m venv PEX
virtualenv PEX
source PEX/bin/activate 
pip3 install --upgrade pip
pip3 install -r requirements.txt
