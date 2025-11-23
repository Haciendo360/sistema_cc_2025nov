#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️  Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "👤 Creating superuser..."
python create_superuser.py

echo "✅ Build completed successfully!"
