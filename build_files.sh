#!/bin/bash
set -e  # Exit immediately if any command fails

echo "BUILD START"

# create a virtual environment named 'venv' if it doesn't already exist
python -m venv venv

# activate the virtual environment
source venv/bin/activate

# install all dependencies in the virtual environment
venv/bin/pip install -r requirements.txt

# collect static files using the virtual environment's Python
venv/bin/python manage.py collectstatic --noinput

echo "BUILD END"

# [optional] Start the application here 
# venv/bin/python manage.py runserver
