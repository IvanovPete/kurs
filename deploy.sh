#!/bin/bash
set -e

# =========================================
# Скрипт деплоя на сервере
# Используется вручную или через CI/CD
# =========================================

ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Файл $ENV_FILE не найден!"
  echo "Создайте его на основе .env.example"
  exit 1
fi

# Загружаем переменные
set -a
source "$ENV_FILE"
set +a

echo "=== Pulling latest images ==="
docker compose pull

echo "=== Restarting containers ==="
docker compose up -d --remove-orphans

echo "=== Cleaning old images ==="
docker image prune -af

echo ""
echo "✅ Deploy completed!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:8080"
