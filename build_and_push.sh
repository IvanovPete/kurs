#!/bin/bash
set -e

# === НАСТРОЙКИ ===
DOCKER_USERNAME="your_dockerhub_username"  # <-- ИЗМЕНИТЕ НА СВОЙ
# =================

echo "=== Логинимся в Docker Hub ==="
docker login

echo ""
echo "=== Собираем образ бэкенда ==="
docker build -t $DOCKER_USERNAME/kurs-backend:latest ./kurs_backend

echo ""
echo "=== Собираем образ nginx с фронтом ==="
# Контекст — корень проекта, чтобы nginx/Dockerfile мог скопировать kurs_frontend
docker build -t $DOCKER_USERNAME/kurs-nginx:latest -f ./nginx/Dockerfile .

echo ""
echo "=== Пушим образы ==="
docker push $DOCKER_USERNAME/kurs-backend:latest
docker push $DOCKER_USERNAME/kurs-nginx:latest

echo ""
echo "=== Готово! ==="
echo "Образы загружены:"
echo "  - $DOCKER_USERNAME/kurs-backend:latest"
echo "  - $DOCKER_USERNAME/kurs-nginx:latest"
