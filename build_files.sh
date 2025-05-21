#!/bin/bash

echo "BUILD START"

# Ensure latest pip/setuptools
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p static
mkdir -p staticfiles_build/static

# Collect static files
python manage.py collectstatic --noinput --clear

echo "BUILD END"