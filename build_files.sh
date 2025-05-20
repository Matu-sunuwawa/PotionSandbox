#!/bin/bash

echo "BUILD START"

# Ensure correct Python version is used
python3.9 -m ensurepip --upgrade
python3.9 -m pip install --upgrade pip setuptools wheel

# Install requirements
python3.9 -m pip install -r requirements.txt

# Create necessary directories
mkdir -p static
mkdir -p staticfiles_build/static

# Collect static files
python3.9 manage.py collectstatic --noinput --clear

echo "BUILD END"