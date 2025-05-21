import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

try:
    connection.ensure_connection()
    print("✅ Database connection successful!")
    
    # Test raw SQL query
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        print("PostgreSQL version:", cursor.fetchone()[0])
except Exception as e:
    print(f"❌ Database connection failed: {e}")