#!/bin/bash

echo "BUILD START"

# Ensure latest pip/setuptools
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --clear

echo "BUILD END"