## 🇷🇺 Русская версия

# Конвертатор — конвертер аудио и видео

Простая программа для конвертации аудио и видео файлов. Работает на FFmpeg.

---

## Что умеет

- Конвертировать аудио (MP3, WAV, FLAC, AAC, OGG) и видео (MP4, AVI, MKV, MOV, WEBM)
- Два режима: простой (выбрал кодек и конвертировал) и продвинутый (ручной ввод кодеков, форматов и аргументов FFmpeg)
- Сохраняет теги (название, исполнитель, обложку)
- Показывает прогресс и лог FFmpeg
- Можно остановить конвертацию
- Есть тёмная тема
- Интерфейс на русском и английском

---

## Как использовать

### Скачать готовую программу
1. Идите в раздел [Releases](https://github.com/Guavvva/Video-Audio-Converter/releases)
2. Скачайте `Converter.exe`
3. Запустите (устанавливать не нужно)

### Запустить из исходников
```bash
git clone https://github.com/Guavvva/Video-Audio-Converter.git
cd Video-Audio-Converter
pip install -r requirements.txt
python converter.py
```

### Собрать EXE
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --version-file=version_info.txt --name="Конвертатор" converter.py
```

---

## Что нужно для работы

- Windows 7/10/11, Любой дистрибутив Linux, macOS (Не тестировалось)
- [FFmpeg](https://ffmpeg.org/download.html) (должен быть в PATH или установлен отдельно)
- Python 3.11+ (если запускаете из исходников)

---

## Зависимости

- PySide6
- FFmpeg (отдельно)

---

## Лицензия

CC0 — делайте что хотите 🎉

---

## Автор

LusterOK

---

---

## 🇬🇧 English Version

# Converter — audio and video converter

A simple program for converting audio and video files. Powered by FFmpeg.

---

## Features

- Convert audio (MP3, WAV, FLAC, AAC, OGG) and video (MP4, AVI, MKV, MOV, WEBM)
- Two modes: simple (pick a codec and convert) and advanced (manual codec, format, and FFmpeg arguments)
- Preserves tags (title, artist, cover art)
- Shows progress and FFmpeg log
- Can stop conversion
- Dark theme
- Russian and English interface

---

## How to use

### Download ready-to-use EXE
1. Go to [Releases](https://github.com/Guavvva/Video-Audio-Converter/releases)
2. Download `Converter.exe`
3. Run it (no installation needed)

### Run from source
```bash
git clone https://github.com/Guavvva/Video-Audio-Converter.git
cd Video-Audio-Converter
pip install -r requirements.txt
python converter.py
```

### Build EXE
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --version-file=version_info.txt --name="Converter" converter.py
```

---

## Requirements

- Windows 7/10/11, Any Linux distro, macOS (Not tested)
- [FFmpeg](https://ffmpeg.org/download.html) (must be in PATH or installed separately)
- Python 3.11+ (if running from source)

---

## Dependencies

- PySide6
- FFmpeg (separate)

---

## License

CC0 — do whatever you want 🎉

---

## Author

LusterOK

---
