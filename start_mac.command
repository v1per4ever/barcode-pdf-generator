#!/bin/bash

# Переходим в директорию скрипта
cd "$(dirname "$0")"

echo "Проверка зависимостей..."
python3 -m pip install -r requirements.txt --quiet

echo "Запуск веб-сервера..."
python3 app.py
