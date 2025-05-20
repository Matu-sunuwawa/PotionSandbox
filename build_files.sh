#!/bin/bash

echo "BUILD START"

# Set Python path explicitly
export PYTHONPATH=/vercel/path0

# Install dependencies with explicit paths
python3.12 -m pip install --user --upgrade pip setuptools wheel
python3.12 -m pip install --user -r requirements.txt

# Create directories
mkdir -p static
mkdir -p staticfiles_build/static

# Collect static files
python3.12 manage.py collectstatic --noinput --clear

python3.12 manage.py migrate --noinput

echo "BUILD END"