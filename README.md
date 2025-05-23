# Linter_task
Java Code Linter - это инструмент для проверки стиля Java-кода с использованием конфигурационных файлов. Он анализирует:

Пробелы и отступы

Пустые строки

Соблюдение правил именования

# 📦 Установка

Клонируйте репозиторий:


git clone https://github.com/Homeaushi/Linter_task

cd Linter_task

# 🚀 Использование
Основные команды
- Проверить Java-файл:
python Linter.py lint path/to/your/file.java

- Создать конфигурационный файл по умолчанию:
python Linter.py init_config -f

Опции


- Использовать кастомный конфиг
python Linter.py lint file.java -c custom_config.yaml

- Отключить подробный вывод
python Linter.py lint file.java -v
