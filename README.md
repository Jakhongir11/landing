# POS Light (MVP)

Минимально жизнеспособная POS-система для кафе/магазина с современным интерфейсом,
SQLite-хранилищем и модульной архитектурой. Запускается локально и подходит
для разработки в VS Code.

## Возможности

- Экран продаж: добавление товаров, количество, итоговая сумма, оплата, очистка.
- Управление товарами: добавление/удаление, категории, цены.
- История чеков: список операций и детали.
- Демонстрационные товары при первом запуске.
- Тёмная тема, горячие клавиши, имитация печати чека.

## Структура проекта

```
pos_app/
  controllers/
  ui/
  database.py
  models.py
  main.py
```

## Запуск в VS Code

1. Установите зависимости:

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

2. Запуск приложения:

```bash
python -m pos_app.main
```

## Сборка .exe через PyInstaller

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "POSLight" pos_app/main.py
```

Готовый файл появится в папке `dist/`.

## Горячие клавиши (экран продаж)

- `Ctrl+F` — фокус на поиск.
- `Ctrl+N` — очистка чека.
- `Ctrl+P` — оплата.
