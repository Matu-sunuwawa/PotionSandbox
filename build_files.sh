#!/bin/bash

echo "BUILD START"

# Ensure Python 3.12 is available
python3.12 --version || echo "Python 3.12 not found"

# Upgrade pip and install dependencies
python3.12 -m pip install --upgrade pip setuptools wheel
python3.12 -m pip install -r requirements.txt

# Create required directories
mkdir -p static
mkdir -p staticfiles_build/static

# Collect static files
python3.12 manage.py collectstatic --noinput --clear

echo "BUILD END"