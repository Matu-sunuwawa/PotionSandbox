#!/bin/bash

echo "=== BUILD START ==="

# 1. Install dependencies
pip install -r requirements.txt

# 2. Apply migrations
python manage.py migrate --noinput

# 3. Create static directories
mkdir -p staticfiles/{admin,css,js}

# 4. Collect static files (including admin)
python manage.py collectstatic --noinput --clear

echo "=== BUILD COMPLETE ==="