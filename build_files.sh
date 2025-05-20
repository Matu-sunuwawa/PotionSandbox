#!/bin/bash

echo "BUILD START"

# Install dependencies
python3.12 -m pip install --upgrade pip
python3.12 -m pip install -r requirements.txt

# Verify Django installation
python3.12 -m django --version

# Apply migrations
python3.12 manage.py migrate --noinput

# Only run collectstatic if Django is properly installed
if python3.12 -c "import django; print(django.__version__)"; then
    python3.12 manage.py collectstatic --noinput --clear
else
    echo "Django not properly installed, skipping collectstatic"
fi

echo "BUILD END"