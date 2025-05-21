#!/bin/bash

echo "=== BUILD START ==="

# 1. Install dependencies
pip install -r requirements.txt

# 2. Create necessary directories (critical for Vercel)
mkdir -p staticfiles/admin
mkdir -p static

# 3. Apply migrations
python manage.py migrate --noinput

# 4. Collect static files with debug off (production mode)
DJANGO_SETTINGS_MODULE=core.settings \
DJANGO_DEBUG=False \
python manage.py collectstatic --noinput --clear

# 5. Verify static files were collected
echo "Collected static files:"
find staticfiles -type f | wc -l

echo "=== BUILD COMPLETE ==="