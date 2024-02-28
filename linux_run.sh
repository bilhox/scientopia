#!/bin/bash
sudo apt install python3-pip
sudo apt install python3-venv
python3 -m venv .venv
python3 -m pip install -r requirements.txt
python3 src/main.py