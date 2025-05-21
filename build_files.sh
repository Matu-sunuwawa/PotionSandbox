#!/bin/bash

echo "=== BUILD START ==="

# 1. Install dependencies
pip install -r requirements.txt

# 2. Apply migrations
python manage.py migrate --noinput

# 3. Create static directory if it doesn't exist
mkdir -p static

# 4. Collect static files
python manage.py collectstatic --noinput --clear

echo "=== BUILD COMPLETE ==="