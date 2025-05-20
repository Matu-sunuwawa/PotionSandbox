#!/bin/bash

echo "BUILD START"
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt

# Create static directory if it doesn't exist
mkdir -p static

python3.9 manage.py collectstatic --noinput --clear

echo "BUILD END"