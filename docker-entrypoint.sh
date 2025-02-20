#!/bin/bash

# Ждём, пока база данных будет доступна
echo "Waiting for PostgreSQL..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done
echo "PostgreSQL started"

# Применение миграций
echo "Applying migrations..."
python manage.py migrate

# Сборка статических файлов
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Передаём управление основной команде контейнера
exec "$@"
