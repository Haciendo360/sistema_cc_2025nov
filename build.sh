#!/usr/bin/env bash
# Build script para Render.com
# Exit on error
set -o errexit

echo "🚀 Iniciando build para Render..."
echo "=================================="

echo ""
echo "📦 Paso 1: Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "🗄️  Paso 2: Ejecutando migraciones de base de datos..."
echo "Verificando migraciones pendientes..."
python manage.py showmigrations
echo ""
echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo ""
echo "📁 Paso 3: Recolectando archivos estáticos..."
python manage.py collectstatic --no-input --clear
echo "✅ Archivos estáticos recolectados exitosamente"

echo ""
echo "👤 Paso 4: Creando superusuario..."
python create_superuser.py

echo ""
echo "✅ Build completado exitosamente!"
echo "=================================="
