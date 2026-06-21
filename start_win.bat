@echo off
cd /d "%~dp0"

echo Проверка зависимостей...
pip install -r requirements.txt -q

echo Запуск веб-сервера...
python app.py
pause
