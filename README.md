# Linter_task
Для использования потребуется java файл с кодом и файл конфугурации

Файл конфигурации следует сохранить в одной директории с линтером в виде "config.yaml"
Файл конфигурации представляет из себя:

spacing:

\\Максимальное количество пробелов подряд

max_row: 2

\\Проверка пробелов вокруг операторов

  around_operators: true\false

\\Проверка пробелов после запятой

  after_commas: true\false

\\Проверка пробелов после ключевых слов(for\while\if и т.д.)

around_keywords: true\false

empty_lines:

\\Максимальное количество пробелов подряд

  max_consecutive_empty_lines: 2

\\Стили проверки нейминга, для отключения проверки вместо стиля оформления переменных напишите -

naming:

  variables: camelCase
    
  constants: UPPER_CASE

  methods: camelCase

  classes: PascalCase