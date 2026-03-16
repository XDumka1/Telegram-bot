# Telegram-бот для обработки фото

Telegram-бот автоматически удаляет фон с фотографий и улучшает их разрешение с помощью ИИ. Поддерживает обработку одной или нескольких фотографий за раз.
✨ Функции

  🗑️ Удаление фона — мгновенное удаление фона с помощью rembg

  🔍 Улучшение разрешения — апскейлинг 4x с REAL-ESRGAN

# Блок-схема

<img width="200" height="550" alt="diagram" src="https://github.com/user-attachments/assets/7b5f4b8a-8749-4230-9613-258d59de2ce4" />

# Установка
1. Подготовка окружения
Python 3.11

Установка библиотек

```bash
pip install telebot
pip install rembg
pip install Pillow
```

# Скачивание REAL-ESRGAN (NCNN версия)

  Перейдите по ссылке

  https://github.com/xinntao/Real-ESRGAN?tab=readme-ov-file#portable-executable-files-ncnn

  Скачайте realesrgan-ncnn-vulkan- для вашей ОС:

    realesrgan-ncnn-vulkan-*.zip (Windows/Linux/Mac)

  Распакуйте архив напрямую в папку проекта

# Создание config.py

```Python
TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"
