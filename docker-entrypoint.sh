#!/bin/bash

# Exit on any error
set -e

echo "Waiting for MySQL to be ready..."
while ! python -c "
import sys
try:
    import MySQLdb
    conn = MySQLdb.connect(
        host='$DB_HOST',
        user='$DB_USER',
        passwd='$DB_PASSWORD',
        db='$DB_NAME'
    )
    conn.close()
    print('MySQL is ready!')
except ImportError:
    # If MySQLdb is not available, try using Django's database check
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silver_empire.settings')
    django.setup()
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    print('MySQL is ready!')
except Exception as e:
    print(f'MySQL not ready: {e}')
    sys.exit(1)
" 2>/dev/null; do
    echo "MySQL is not ready yet, waiting..."
    sleep 2
done

echo "MySQL is ready!"

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Initialize app with categories and superuser
echo "Initializing application data..."
python manage.py init_app

# Collect static files (in case there are new ones)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the Django development server
echo "Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000