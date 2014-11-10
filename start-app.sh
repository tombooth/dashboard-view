#!/bin/bash

if [ ! -d venv/ ]
then
  virtualenv venv
fi

. venv/bin/activate
pip install -r requirements.txt

python main.py
