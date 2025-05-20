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

# Test database connection
python3.12 -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
print('Database connection successful!')
"

echo "BUILD END"