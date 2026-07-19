import sys
import shutil
import subprocess
import re
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QComboBox, QLabel, QPushButton, 
    QVBoxLayout, QWidget, QFileDialog, QSlider, QHBoxLayout, 
    QLineEdit, QCheckBox, QStatusBar, QMessageBox, QProgressBar,
    QTextEdit, QFrame, QRadioButton, QGroupBox, QButtonGroup
)
from PySide6.QtCore import Qt, QThread, Signal, QSettings, QDateTime
from PySide6.QtGui import QPalette, QColor, QFont

# ═══════════════════════════════════════════════════════════════
# СЛОВАРЬ ПЕРЕВОДОВ
# ═══════════════════════════════════════════════════════════════
LANGUAGES = {
    'window_title': {'ru': "Конвертатор", 'en': "Converter"},
    'input_file_label': {'ru': "Выберите файл:", 'en': "Select File:"},
    'output_file_label': {'ru': "Сохранить как:", 'en': "Save As:"},
    'select_file_button': {'ru': "Выбрать", 'en': "Select"},
    'save_as_button': {'ru': "Сохранить как", 'en': "Save As"},
    'start_button': {'ru': "Начать конвертацию", 'en': "Start Conversion"},
    'stop_button': {'ru': "Остановить", 'en': "Stop"},
    'format_label': {'ru': "Формат выходного файла:", 'en': "Output Format:"},
    'quality_label': {'ru': "Качество:", 'en': "Quality:"},
    'lossless_checkbox': {'ru': "Без потери качества", 'en': "Lossless"},
    'status_label': {'ru': "Статус:", 'en': "Status:"},
    'video_codec_label': {'ru': "Кодек видео:", 'en': "Video Codec:"},
    'audio_codec_label': {'ru': "Кодек аудио:", 'en': "Audio Codec:"},
    'file_dialog_title': {'ru': "Открыть файл", 'en': "Open File"},
    'save_dialog_title': {'ru': "Сохранить как", 'en': "Save As"},
    'no_file_selected': {'ru': "Нет выбранного файла", 'en': "No file selected"},
    'no_output_path': {'ru': "Нет пути сохранения", 'en': "No output path"},
    'ffmpeg_checking': {'ru': "Проверка FFmpeg...", 'en': "Checking FFmpeg..."},
    'ffmpeg_found': {'ru': "✅ FFmpeg найден", 'en': "✅ FFmpeg found"},
    'ffmpeg_not_found': {'ru': "❌ FFmpeg не найден", 'en': "❌ FFmpeg not found"},
    'converting': {'ru': "Конвертирую", 'en': "Converting"},
    'conversion_complete': {'ru': "✅ Конвертация завершена!", 'en': "✅ Conversion complete!"},
    'conversion_error': {'ru': "❌ Ошибка конвертации!", 'en': "❌ Conversion error!"},
    'conversion_stopped': {'ru': "⏹️ Конвертация остановлена", 'en': "⏹️ Conversion stopped"},
    'ready': {'ru': "Готов к работе", 'en': "Ready"},
    'file_selected': {'ru': "Выбран файл:", 'en': "File selected:"},
    'output_selected': {'ru': "Путь сохранения:", 'en': "Save path:"},
    'format_selected': {'ru': "Выбран формат:", 'en': "Selected format:"},
    'codec_selected': {'ru': "Выбранный кодек:", 'en': "Selected codec:"},
    'audio_codec_selected': {'ru': "Выбранный аудиокодек:", 'en': "Selected audio codec:"},
    'quality_best': {'ru': "Наилучшее качество", 'en': "Best quality"},
    'quality_high': {'ru': "Высокое качество", 'en': "High quality"},
    'quality_medium': {'ru': "Среднее качество", 'en': "Medium quality"},
    'quality_low': {'ru': "Низкое качество", 'en': "Low quality"},
    'quality_lossless': {'ru': "Без потерь (Lossless)", 'en': "Lossless"},
    'lossless_enabled': {'ru': "Без потери качества ВКЛЮЧЕНО", 'en': "Lossless ENABLED"},
    'lossless_disabled': {'ru': "Без потери качества отключено", 'en': "Lossless disabled"},
    'ffmpeg_error_title': {'ru': "Ошибка: FFmpeg не найден", 'en': "Error: FFmpeg not found"},
    'ffmpeg_error_message': {
        'ru': (
            "FFmpeg не установлен или не добавлен в переменную PATH.\n\n"
            "Как установить FFmpeg:\n"
            "1. Скачайте FFmpeg с https://ffmpeg.org/download.html\n"
            "2. Распакуйте архив в папку (например, C:\\ffmpeg)\n"
            "3. Добавьте папку bin в переменную PATH\n"
            "   (C:\\ffmpeg\\bin)\n"
            "4. Перезапустите программу\n\n"
            "Или установите через менеджер пакетов:\n"
            "  - Windows 10 (1809 и новее)/11: winget install --id Gyan.FFmpeg -e\n"
            "  - Ubuntu: sudo apt install ffmpeg\n"
            "  - MacOS: brew install ffmpeg"
        ),
        'en': (
            "FFmpeg is not installed or not in PATH.\n\n"
            "How to install FFmpeg:\n"
            "1. Download FFmpeg from https://ffmpeg.org/download.html\n"
            "2. Extract to a folder (e.g., C:\\ffmpeg)\n"
            "3. Add bin folder to PATH\n"
            "   (C:\\ffmpeg\\bin)\n"
            "4. Restart the program\n\n"
            "Or install via package manager:\n"
            "  - Windows 10 (1809 or newer)/11: winget install --id Gyan.FFmpeg -e\n"
            "  - Ubuntu: sudo apt install ffmpeg\n"
            "  - MacOS: brew install ffmpeg"
        )
    },
    'file_error_title': {'ru': "Ошибка: файлы не выбраны", 'en': "Error: Files not selected"},
    'file_error_message': {
        'ru': "Пожалуйста, выберите входной и выходной файлы перед началом конвертации.",
        'en': "Please select input and output files before starting conversion."
    },
    'ffmpeg_path_label': {'ru': "Путь к FFmpeg:", 'en': "FFmpeg path:"},
    'conversion_failed': {'ru': "Конвертация не удалась", 'en': "Conversion failed"},
    'processing': {'ru': "Обработка...", 'en': "Processing..."},
    'progress': {'ru': "Прогресс:", 'en': "Progress:"},
    'log_label': {'ru': "Лог FFmpeg:", 'en': "FFmpeg Log:"},
    'clear_log': {'ru': "Очистить лог", 'en': "Clear Log"},
    'save_log': {'ru': "Сохранить лог", 'en': "Save Log"},
    'log_saved': {'ru': "Лог сохранён в:", 'en': "Log saved to:"},
    'log_save_error': {'ru': "Ошибка сохранения лога", 'en': "Error saving log"},
    'conversion_started': {'ru': "Конвертация началась", 'en': "Conversion started"},
    'conversion_success': {'ru': "Конвертация успешно завершена!", 'en': "Conversion completed successfully!"},
    'conversion_failed_msg': {'ru': "Конвертация не удалась. Проверьте лог для подробностей.", 'en': "Conversion failed. Check the log for details."},
    'estimated_size': {'ru': "Оценка размера:", 'en': "Estimated size:"},
    'original_size': {'ru': "Исходный размер:", 'en': "Original size:"},
    'file_not_found': {'ru': "Файл не найден", 'en': "File not found"},
    'settings_saved': {'ru': "Настройки сохранены", 'en': "Settings saved"},
    'media_type_video': {'ru': "Видео", 'en': "Video"},
    'media_type_audio': {'ru': "Аудио", 'en': "Audio"},
    'media_type_unknown': {'ru': "Неизвестно", 'en': "Unknown"},
    'warning_video_to_audio': {
        'ru': "Вы конвертируете видео в аудио. Это извлечёт только звук. Продолжить?",
        'en': "You are converting video to audio. This will extract only the sound. Continue?"
    },
    'warning_audio_to_video': {
        'ru': "Вы пытаетесь конвертировать аудио в видео. Это создаст видео только с аудиодорожкой (без картинки). Продолжить?",
        'en': "You are trying to convert audio to video. This will create a video with only audio track (no picture). Continue?"
    },
    'warning_title': {'ru': "Предупреждение", 'en': "Warning"},
    'media_type_label': {'ru': "Тип файла:", 'en': "File type:"},
    'keep_all_audio_tracks': {
        'ru': "Сохранить все аудиодорожки", 
        'en': "Keep all audio tracks"
    },
    'audio_tracks_detected': {
        'ru': "Обнаружено аудиодорожек: ", 
        'en': "Audio tracks detected: "
    },
    'keep_all_tracks_tooltip': {
        'ru': "При включении сохраняются все аудиодорожки из исходного файла. Отключите, чтобы оставить только первую дорожку.",
        'en': "When enabled, all audio tracks from the source file are preserved. Disable to keep only the first track."
    },
    'no_audio_tracks': {
        'ru': "Аудиодорожки не обнаружены", 
        'en': "No audio tracks detected"
    },
    'simple_mode': {'ru': "Простой режим", 'en': "Simple Mode"},
    'advanced_mode': {'ru': "Продвинутый режим", 'en': "Advanced Mode"},
    'mode_label': {'ru': "Режим:", 'en': "Mode:"},
    'custom_codec_hint': {'ru': "Введите кодек вручную", 'en': "Enter codec manually"},
    'custom_format_hint': {
        'ru': "Введите формат вручную (например: mkv, ac3, m4a)...",
        'en': "Enter format manually (e.g.: mkv, ac3, m4a)..."
    },
    'custom_format_tooltip': {
        'ru': "Любой формат, поддерживаемый FFmpeg.\nПримеры: mkv, ac3, m4a, opus, wma, m2ts, ts...",
        'en': "Any format supported by FFmpeg.\nExamples: mkv, ac3, m4a, opus, wma, m2ts, ts..."
    },
    'ffmpeg_args_label': {'ru': "Дополнительные аргументы FFmpeg:", 'en': "Additional FFmpeg arguments:"},
    'ffmpeg_args_hint': {
        'ru': "Введите дополнительные аргументы (например: -b:v 2M -preset slow)",
        'en': "Enter additional arguments (e.g.: -b:v 2M -preset slow)"
    },
    'ffmpeg_args_tooltip': {
        'ru': "Дополнительные аргументы будут добавлены в конец команды FFmpeg после всех основных параметров.",
        'en': "Additional arguments will be added at the end of the FFmpeg command after all main parameters."
    },
    'audio_mode': {'ru': "Аудио режим", 'en': "Audio Mode"},
    'video_mode': {'ru': "Видео режим", 'en': "Video Mode"},
    'mode_switcher_label': {'ru': "Режим конвертации:", 'en': "Conversion mode:"},
    'audio_bitrate_label': {'ru': "Битрейт аудио:", 'en': "Audio bitrate:"},
    'audio_bitrate_hint': {'ru': "Введите битрейт (например: 192k)", 'en': "Enter bitrate (e.g.: 192k)"},
    'save_log_dialog_title': {'ru': "Сохранить лог FFmpeg", 'en': "Save FFmpeg Log"},
    'log_file_filter': {'ru': "Текстовые файлы (*.txt);;Все файлы (*)", 'en': "Text files (*.txt);;All files (*)"},
    'copy_metadata': {
        'ru': "Копировать метаданные (ID3 теги, обложки)", 
        'en': "Copy metadata (ID3 tags, covers)"
    },
    'metadata_copied': {
        'ru': "Метаданные скопированы",
        'en': "Metadata copied"
    },
    'metadata_copy_failed': {
        'ru': "Не удалось скопировать метаданные",
        'en': "Failed to copy metadata"
    },
}

# Видео форматы
VIDEO_FORMATS = ['mp4', 'avi', 'mkv', 'mov', 'webm']
# Аудио форматы
AUDIO_FORMATS = ['mp3', 'wav', 'flac', 'aac', 'ogg']

OUTPUT_FORMATS = {
    'mp4': 'MP4 Files (*.mp4)',
    'avi': 'AVI Files (*.avi)',
    'mkv': 'MKV Files (*.mkv)',
    'mov': 'MOV Files (*.mov)',
    'webm': 'WEBM Files (*.webm)',
    'mp3': 'MP3 Files (*.mp3)',
    'wav': 'WAV Files (*.wav)',
    'flac': 'FLAC Files (*.flac)',
    'aac': 'AAC Files (*.aac)',
    'ogg': 'OGG Files (*.ogg)'
}

# Кодеки с информацией о диапазоне качества
CODEC_INFO = {
    'libx264': {'type': 'cpu', 'param': 'crf', 'min': 0, 'max': 51, 'default': 23},
    'libx265': {'type': 'cpu', 'param': 'crf', 'min': 0, 'max': 51, 'default': 28},
    'h264_nvenc': {'type': 'gpu', 'param': 'cq', 'min': 0, 'max': 51, 'default': 23},
    'h264_amf': {'type': 'gpu', 'param': 'cq', 'min': 0, 'max': 51, 'default': 23},
    'h264_qsv': {'type': 'gpu', 'param': 'cq', 'min': 0, 'max': 51, 'default': 23},
    'hevc_nvenc': {'type': 'gpu', 'param': 'cq', 'min': 0, 'max': 51, 'default': 28},
    'libvpx-vp9': {'type': 'cpu', 'param': 'crf', 'min': 0, 'max': 63, 'default': 30},
    'mpeg4': {'type': 'cpu', 'param': 'qscale', 'min': 1, 'max': 31, 'default': 5},
}

# Аудио кодеки с информацией
AUDIO_CODEC_INFO = {
    'aac': {'default_bitrate': '192k', 'lossless': False},
    'mp3': {'default_bitrate': '192k', 'lossless': False},
    'flac': {'default_bitrate': None, 'lossless': True},
    'ogg': {'default_bitrate': '192k', 'lossless': False},
    'wav': {'default_bitrate': None, 'lossless': True},
}

CODECS = list(CODEC_INFO.keys())
AUDIO_CODECS = list(AUDIO_CODEC_INFO.keys())

# ═══════════════════════════════════════════════════════════════
# ФУНКЦИИ ОПРЕДЕЛЕНИЯ ТИПА ФАЙЛА
# ═══════════════════════════════════════════════════════════════

def detect_media_type_by_extension(file_path):
    audio_extensions = {
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', 
        '.opus', '.wma', '.aiff', '.alac', '.dsd', '.dff'
    }
    video_extensions = {
        '.mp4', '.avi', '.mkv', '.mov', '.webm', '.m4v',
        '.mpg', '.mpeg', '.flv', '.wmv', '.3gp', '.ts', '.m2ts'
    }
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext in audio_extensions:
        return "audio"
    elif ext in video_extensions:
        return "video"
    else:
        return "unknown"

def detect_media_type(file_path):
    """
    Определяет тип медиафайла (видео или аудио).
    Сначала по расширению, затем ffprobe для уточнения.
    """
    if not os.path.exists(file_path):
        return "unknown"
    
    # ═══════════════════════════════════════════════════════════════
    # 1. СНАЧАЛА ОПРЕДЕЛЯЕМ ПО РАСШИРЕНИЮ (самый надёжный способ)
    # ═══════════════════════════════════════════════════════════════
    ext_type = detect_media_type_by_extension(file_path)
    
    # Если расширение определяет тип - возвращаем его
    if ext_type != "unknown":
        return ext_type
    
    # ═══════════════════════════════════════════════════════════════
    # 2. ЕСЛИ РАСШИРЕНИЕ НЕИЗВЕСТНО - ПРОБУЕМ FFPROBE
    # ═══════════════════════════════════════════════════════════════
    try:
        ffprobe_path = shutil.which("ffprobe")
        if not ffprobe_path:
            return "unknown"
        
        cmd = [
            ffprobe_path,
            '-v', 'error',
            '-show_entries', 'stream=codec_type',
            '-of', 'csv=p=0',
            file_path
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            return "unknown"
        
        streams = result.stdout.strip().split('\n')
        has_video = False
        has_audio = False
        
        for stream in streams:
            stream_type = stream.strip()
            if stream_type == 'video':
                has_video = True
            elif stream_type == 'audio':
                has_audio = True
        
        if has_video:
            return "video"
        if has_audio:
            return "audio"
        return "unknown"
            
    except subprocess.TimeoutExpired:
        return "unknown"
    except Exception:
        return "unknown"

def get_audio_tracks_count(file_path):
    if not os.path.exists(file_path):
        return 0
    try:
        ffprobe_path = shutil.which("ffprobe")
        if not ffprobe_path:
            return 0
        cmd = [
            ffprobe_path,
            '-v', 'error',
            '-select_streams', 'a',
            '-count_packets',
            '-show_entries', 'stream=index',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return 0
        streams = result.stdout.strip().split('\n')
        streams = [s for s in streams if s.strip()]
        return len(streams)
    except:
        return 0

# ═══════════════════════════════════════════════════════════════
# КЛАСС ДЛЯ КОНВЕРТАЦИИ АУДИО
# ═══════════════════════════════════════════════════════════════

class AudioConverterThread(QThread):
    status_update = Signal(str)
    progress_update = Signal(int)
    log_update = Signal(str)
    conversion_finished = Signal(bool, str)
    
    def __init__(self, input_file, output_file, format_, audio_codec, 
                 bitrate, quality, lossless, copy_metadata=True, ffmpeg_args=""):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.format_ = format_
        self.audio_codec = audio_codec
        self.bitrate = bitrate
        self.quality = quality
        self.lossless = lossless
        self.copy_metadata = copy_metadata
        self.ffmpeg_args = ffmpeg_args.strip()
        self.process = None
        self.is_running = False
        self.is_stopped = False
        self.total_duration = None
    
    def run(self):
        self.is_running = True
        self.is_stopped = False
        try:
            if not os.path.exists(self.input_file):
                self.log_update.emit(f"[ERROR] Входной файл не существует: {self.input_file}\n")
                self.conversion_finished.emit(False, f"Входной файл не существует: {self.input_file}")
                return
            if os.path.getsize(self.input_file) == 0:
                self.log_update.emit(f"[ERROR] Входной файл пуст: {self.input_file}\n")
                self.conversion_finished.emit(False, f"Входной файл пуст: {self.input_file}")
                return
            ffmpeg_path = shutil.which("ffmpeg")
            if not ffmpeg_path:
                self.log_update.emit("[ERROR] FFmpeg не найден в PATH\n")
                self.conversion_finished.emit(False, "FFmpeg не найден в PATH")
                return
            self.get_duration()
            command = self.build_ffmpeg_command()
            self.log_update.emit(f"[COMMAND] {' '.join(command)}\n")
            self.log_update.emit("[INFO] Запуск FFmpeg...\n")
            if self.ffmpeg_args:
                self.log_update.emit(f"[INFO] Дополнительные аргументы: {self.ffmpeg_args}\n")
            if self.copy_metadata:
                self.log_update.emit("[INFO] Копирование метаданных (ID3 теги, обложки)...\n")
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            error_lines = []
            while self.is_running:
                if self.process is None:
                    break
                if self.process.poll() is not None:
                    remaining_stdout, remaining_stderr = self.process.communicate()
                    if remaining_stdout:
                        for line in remaining_stdout.split('\n'):
                            if line.strip():
                                self.log_update.emit(f"[FFMPEG] {line}\n")
                    if remaining_stderr:
                        for line in remaining_stderr.split('\n'):
                            if line.strip():
                                self.log_update.emit(f"[FFMPEG] {line}\n")
                                error_lines.append(line)
                    break
                line = self.process.stderr.readline()
                if line:
                    line = line.rstrip()
                    self.log_update.emit(f"[FFMPEG] {line}\n")
                    error_lines.append(line)
                    progress = self.parse_progress(line)
                    if progress is not None:
                        self.progress_update.emit(progress)
                self.msleep(50)
            if self.is_stopped:
                self.terminate_process()
                self.log_update.emit("[INFO] Конвертация остановлена пользователем\n")
                self.conversion_finished.emit(False, "Конвертация остановлена пользователем")
                return
            if self.process:
                return_code = self.process.returncode
                if return_code == 0:
                    self.log_update.emit("[SUCCESS] Конвертация успешно завершена!\n")
                    if self.copy_metadata:
                        self.log_update.emit("[INFO] Метаданные скопированы\n")
                    self.conversion_finished.emit(True, "Конвертация успешно завершена")
                else:
                    error_msg = self.analyze_error(error_lines, return_code)
                    self.log_update.emit(f"[ERROR] {error_msg}\n")
                    self.conversion_finished.emit(False, error_msg)
            else:
                self.log_update.emit("[ERROR] Процесс FFmpeg не был запущен\n")
                self.conversion_finished.emit(False, "Процесс FFmpeg не был запущен")
        except Exception as e:
            error_msg = f"Ошибка конвертации: {str(e)}"
            self.log_update.emit(f"[ERROR] {error_msg}\n")
            self.conversion_finished.emit(False, error_msg)
        finally:
            self.is_running = False
            if self.process:
                self.process = None
    
    def get_duration(self):
        try:
            ffprobe_path = shutil.which("ffprobe")
            if not ffprobe_path:
                return
            cmd = [
                ffprobe_path,
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                self.input_file
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                duration = float(result.stdout.strip())
                self.total_duration = duration
                self.log_update.emit(f"[INFO] Длительность файла: {self.format_time(duration)}\n")
            else:
                cmd = ['ffmpeg', '-i', self.input_file]
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                match = re.search(r'Duration: (\d+):(\d+):(\d+\.?\d*)', result.stderr)
                if match:
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    seconds = float(match.group(3))
                    self.total_duration = hours * 3600 + minutes * 60 + seconds
                    self.log_update.emit(f"[INFO] Длительность файла: {hours}:{minutes:02d}:{seconds:05.2f}\n")
                else:
                    self.log_update.emit("[WARNING] Не удалось определить длительность файла\n")
                    self.total_duration = None
        except Exception as e:
            self.log_update.emit(f"[WARNING] Не удалось получить длительность: {e}\n")
            self.total_duration = None
    
    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:05.2f}"
    
    def analyze_error(self, error_lines, return_code):
        error_text = "\n".join(error_lines)
        error_patterns = {
            r'Invalid data found when processing input': 'Некорректные данные во входном файле. Возможно, файл повреждён.',
            r'Permission denied': 'Нет доступа к файлу. Проверьте права на чтение/запись.',
            r'No such file or directory': 'Файл не найден. Проверьте путь к файлу.',
            r'codec not found': 'Указанный кодек не поддерживается. Проверьте название кодека.',
            r'Unknown encoder': 'Неизвестный кодер. Проверьте название кодека.',
            r'Unable to find a suitable output format': 'Неподдерживаемый выходной формат.',
            r'ac3 muxer supports only codec ac3': 'Контейнер AC3 поддерживает только кодек AC3. Используйте кодек ac3 или формат MKV/MP4.',
            r'Exactly one MP3 audio stream is required': 'Ошибка MP3. Проверьте входной файл.',
        }
        for pattern, message in error_patterns.items():
            if re.search(pattern, error_text, re.IGNORECASE):
                return f"FFmpeg ошибка: {message} (код: {return_code})"
        if return_code == -22 or return_code == 4294967274:
            return f"FFmpeg ошибка: неверный аргумент или повреждённый файл (код: {return_code})."
        if len(error_text) > 0:
            lines = error_text.split('\n')
            last_lines = '\n'.join(lines[-5:]) if len(lines) > 5 else error_text
            return f"FFmpeg ошибка (код: {return_code}):\n{last_lines}"
        else:
            return f"FFmpeg ошибка с кодом: {return_code}"
    
    def build_ffmpeg_command(self):
        command = ['ffmpeg', '-i', self.input_file]
        command.extend(['-progress', 'pipe:1'])
        
        if self.copy_metadata:
            # Сначала извлекаем все метаданные
            command.extend(['-map_metadata', '0'])
            
            # Принудительно устанавливаем кодировку для всех метаданных
            # Это должно исправить кракозябры
            command.extend(['-metadata', 'encoding=UTF-8'])
            
            # Для MP3 - используем ID3v2.3 с поддержкой Unicode
            if self.format_ == 'mp3':
                command.extend(['-id3v2_version', '3'])
            
            # Для WAV
            if self.format_ == 'wav':
                command.extend(['-write_id3v1', '1'])
                command.extend(['-write_id3v2', '1'])
        
        command.extend(['-vn'])
        
        if self.audio_codec:
            command.extend(['-c:a', self.audio_codec])
        else:
            command.extend(['-c:a', 'aac'])
        
        if self.lossless:
            if self.audio_codec == 'flac':
                command.extend(['-compression_level', '0'])
        else:
            if self.audio_codec == 'mp3':
                if self.bitrate:
                    command.extend(['-b:a', self.bitrate])
                else:
                    command.extend(['-b:a', '192k'])
            elif self.audio_codec == 'aac':
                if self.bitrate:
                    command.extend(['-b:a', self.bitrate])
                else:
                    command.extend(['-b:a', '192k'])
            elif self.audio_codec == 'ogg':
                if self.bitrate:
                    command.extend(['-b:a', self.bitrate])
                else:
                    command.extend(['-q:a', '5'])
            elif self.audio_codec == 'flac':
                command.extend(['-compression_level', str(max(0, min(12, 12 - (self.quality - 23) * 0.2)))])
            else:
                command.extend(['-q:a', str(max(0, min(10, 10 - (self.quality - 23) * 0.2)))])
        
        if self.ffmpeg_args:
            import shlex
            try:
                args_list = shlex.split(self.ffmpeg_args)
                command.extend(args_list)
            except ValueError:
                command.extend(self.ffmpeg_args.split())
        
        command.append('-y')
        command.append(self.output_file)
        return command
    
    def parse_progress(self, line):
        time_match = re.search(r'out_time_ms=(\d+)', line)
        if time_match and self.total_duration and self.total_duration > 0:
            time_ms = int(time_match.group(1))
            current_time = time_ms / 1000000
            progress = int((current_time / self.total_duration) * 100)
            return max(0, min(100, progress))
        return None
    
    def terminate_process(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None
    
    def stop(self):
        self.is_stopped = True
        self.is_running = False
        self.terminate_process()


# ═══════════════════════════════════════════════════════════════
# КЛАСС ДЛЯ КОНВЕРТАЦИИ ВИДЕО
# ═══════════════════════════════════════════════════════════════

class VideoConverterThread(QThread):
    status_update = Signal(str)
    progress_update = Signal(int)
    log_update = Signal(str)
    conversion_finished = Signal(bool, str)
    
    def __init__(self, input_file, output_file, format_, video_codec, audio_codec, 
                 quality, lossless, keep_all_tracks, audio_tracks_count, ffmpeg_args=""):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.format_ = format_
        self.video_codec = video_codec
        self.audio_codec = audio_codec
        self.quality = quality
        self.lossless = lossless
        self.keep_all_tracks = keep_all_tracks
        self.audio_tracks_count = audio_tracks_count
        self.ffmpeg_args = ffmpeg_args.strip()
        self.process = None
        self.is_running = False
        self.is_stopped = False
        self.total_duration = None
    
    def run(self):
        self.is_running = True
        self.is_stopped = False
        try:
            if not os.path.exists(self.input_file):
                self.log_update.emit(f"[ERROR] Входной файл не существует: {self.input_file}\n")
                self.conversion_finished.emit(False, f"Входной файл не существует: {self.input_file}")
                return
            if os.path.getsize(self.input_file) == 0:
                self.log_update.emit(f"[ERROR] Входной файл пуст: {self.input_file}\n")
                self.conversion_finished.emit(False, f"Входной файл пуст: {self.input_file}")
                return
            ffmpeg_path = shutil.which("ffmpeg")
            if not ffmpeg_path:
                self.log_update.emit("[ERROR] FFmpeg не найден в PATH\n")
                self.conversion_finished.emit(False, "FFmpeg не найден в PATH")
                return
            self.get_duration()
            command = self.build_ffmpeg_command()
            self.log_update.emit(f"[COMMAND] {' '.join(command)}\n")
            self.log_update.emit("[INFO] Запуск FFmpeg...\n")
            if self.ffmpeg_args:
                self.log_update.emit(f"[INFO] Дополнительные аргументы: {self.ffmpeg_args}\n")
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            error_lines = []
            while self.is_running:
                if self.process is None:
                    break
                if self.process.poll() is not None:
                    remaining_stdout, remaining_stderr = self.process.communicate()
                    if remaining_stdout:
                        for line in remaining_stdout.split('\n'):
                            if line.strip():
                                self.log_update.emit(f"[FFMPEG] {line}\n")
                    if remaining_stderr:
                        for line in remaining_stderr.split('\n'):
                            if line.strip():
                                self.log_update.emit(f"[FFMPEG] {line}\n")
                                error_lines.append(line)
                    break
                line = self.process.stderr.readline()
                if line:
                    line = line.rstrip()
                    self.log_update.emit(f"[FFMPEG] {line}\n")
                    error_lines.append(line)
                    progress = self.parse_progress(line)
                    if progress is not None:
                        self.progress_update.emit(progress)
                self.msleep(50)
            if self.is_stopped:
                self.terminate_process()
                self.log_update.emit("[INFO] Конвертация остановлена пользователем\n")
                self.conversion_finished.emit(False, "Конвертация остановлена пользователем")
                return
            if self.process:
                return_code = self.process.returncode
                if return_code == 0:
                    self.log_update.emit("[SUCCESS] Конвертация успешно завершена!\n")
                    self.conversion_finished.emit(True, "Конвертация успешно завершена")
                else:
                    error_msg = self.analyze_error(error_lines, return_code)
                    self.log_update.emit(f"[ERROR] {error_msg}\n")
                    self.conversion_finished.emit(False, error_msg)
            else:
                self.log_update.emit("[ERROR] Процесс FFmpeg не был запущен\n")
                self.conversion_finished.emit(False, "Процесс FFmpeg не был запущен")
        except Exception as e:
            error_msg = f"Ошибка конвертации: {str(e)}"
            self.log_update.emit(f"[ERROR] {error_msg}\n")
            self.conversion_finished.emit(False, error_msg)
        finally:
            self.is_running = False
            if self.process:
                self.process = None
    
    def get_duration(self):
        try:
            ffprobe_path = shutil.which("ffprobe")
            if not ffprobe_path:
                return
            cmd = [
                ffprobe_path,
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                self.input_file
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                duration = float(result.stdout.strip())
                self.total_duration = duration
                self.log_update.emit(f"[INFO] Длительность файла: {self.format_time(duration)}\n")
            else:
                cmd = ['ffmpeg', '-i', self.input_file]
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                match = re.search(r'Duration: (\d+):(\d+):(\d+\.?\d*)', result.stderr)
                if match:
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    seconds = float(match.group(3))
                    self.total_duration = hours * 3600 + minutes * 60 + seconds
                    self.log_update.emit(f"[INFO] Длительность файла: {hours}:{minutes:02d}:{seconds:05.2f}\n")
                else:
                    self.log_update.emit("[WARNING] Не удалось определить длительность файла\n")
                    self.total_duration = None
        except Exception as e:
            self.log_update.emit(f"[WARNING] Не удалось получить длительность: {e}\n")
            self.total_duration = None
    
    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:05.2f}"
    
    def analyze_error(self, error_lines, return_code):
        error_text = "\n".join(error_lines)
        error_patterns = {
            r'Invalid data found when processing input': 'Некорректные данные во входном файле. Возможно, файл повреждён.',
            r'Permission denied': 'Нет доступа к файлу. Проверьте права на чтение/запись.',
            r'No such file or directory': 'Файл не найден. Проверьте путь к файлу.',
            r'codec not found': 'Указанный кодек не поддерживается. Проверьте название кодека.',
            r'Unknown encoder': 'Неизвестный кодер. Проверьте название кодека.',
            r'Unable to find a suitable output format': 'Неподдерживаемый выходной формат.',
        }
        for pattern, message in error_patterns.items():
            if re.search(pattern, error_text, re.IGNORECASE):
                return f"FFmpeg ошибка: {message} (код: {return_code})"
        if return_code == -22 or return_code == 4294967274:
            return f"FFmpeg ошибка: неверный аргумент или повреждённый файл (код: {return_code})."
        if len(error_text) > 0:
            lines = error_text.split('\n')
            last_lines = '\n'.join(lines[-5:]) if len(lines) > 5 else error_text
            return f"FFmpeg ошибка (код: {return_code}):\n{last_lines}"
        else:
            return f"FFmpeg ошибка с кодом: {return_code}"
    
    def build_ffmpeg_command(self):
        is_audio = self.format_ in AUDIO_FORMATS
        command = ['ffmpeg', '-i', self.input_file]
        command.extend(['-progress', 'pipe:1'])
        
        # Копируем метаданные для видео тоже
        command.extend(['-map_metadata', '0'])
        
        if is_audio:
            command.extend(['-vn'])
            if self.audio_codec:
                command.extend(['-c:a', self.audio_codec])
            else:
                command.extend(['-c:a', 'aac'])
            if self.lossless:
                command.extend(['-compression_level', '0'])
            else:
                if self.audio_codec == 'mp3':
                    bitrate = max(8, min(320, 320 - (self.quality - 23) * 10))
                    command.extend(['-b:a', f'{bitrate}k'])
                else:
                    command.extend(['-q:a', str(max(0, min(10, 10 - (self.quality - 23) * 0.2)))])
        else:
            if self.video_codec:
                command.extend(['-c:v', self.video_codec])
                quality_param = self.get_quality_param(self.video_codec, self.quality)
                if quality_param:
                    command.extend(quality_param)
            else:
                command.extend(['-c:v', 'libx264'])
                command.extend(['-crf', str(self.quality)])
            if self.audio_codec:
                command.extend(['-c:a', self.audio_codec])
            else:
                command.extend(['-c:a', 'aac'])
        if self.ffmpeg_args:
            import shlex
            try:
                args_list = shlex.split(self.ffmpeg_args)
                command.extend(args_list)
            except ValueError:
                command.extend(self.ffmpeg_args.split())
        command.append('-y')
        command.append(self.output_file)
        return command
    
    def get_quality_param(self, codec, quality):
        if codec not in CODEC_INFO:
            return ['-crf', str(quality)]
        info = CODEC_INFO[codec]
        param_name = info['param']
        clamped_quality = max(info['min'], min(info['max'], quality))
        return [f'-{param_name}', str(clamped_quality)]
    
    def parse_progress(self, line):
        time_match = re.search(r'out_time_ms=(\d+)', line)
        if time_match and self.total_duration and self.total_duration > 0:
            time_ms = int(time_match.group(1))
            current_time = time_ms / 1000000
            progress = int((current_time / self.total_duration) * 100)
            return max(0, min(100, progress))
        return None
    
    def terminate_process(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None
    
    def stop(self):
        self.is_stopped = True
        self.is_running = False
        self.terminate_process()


# ═══════════════════════════════════════════════════════════════
# ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
# ═══════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("VideoConverter", "Settings")
        
        self.current_language = self.settings.value("language", "ru")
        self.last_input_path = self.settings.value("last_input_path", "")
        self.last_output_path = self.settings.value("last_output_path", "")
        self.last_format = self.settings.value("last_format", "mp4")
        self.last_video_codec = self.settings.value("last_video_codec", "libx264")
        self.last_audio_codec = self.settings.value("last_audio_codec", "aac")
        self.last_quality = int(self.settings.value("last_quality", 23))
        self.last_lossless = self.settings.value("last_lossless", "false") == "true"
        self.last_keep_all_tracks = self.settings.value("last_keep_all_tracks", "true") == "true"
        self.last_mode = self.settings.value("mode", "simple")
        self.last_ffmpeg_args = self.settings.value("ffmpeg_args", "")
        self.last_conversion_mode = self.settings.value("conversion_mode", "video")
        self.last_copy_metadata = self.settings.value("copy_metadata", "true") == "true"
        
        self.converter_thread = None
        self.original_file_size = 0
        self.input_media_type = "unknown"
        self.audio_tracks_count = 0
        self.current_mode = "simple"
        self.conversion_mode = "video"
        
        self.setWindowTitle(LANGUAGES['window_title'][self.current_language])
        self.resize(850, 980)
        self.setMinimumSize(750, 800)

        self.create_ui_elements()
        self.connect_signals()
        self.load_saved_settings()
        self.update_ui_language(self.current_language)
        self.update_mode_ui()
        self.update_conversion_mode_ui()

    def create_ui_elements(self):
        """Создает все элементы интерфейса"""
        
        self.control_panel = QWidget()
        control_layout = QVBoxLayout(self.control_panel)
        control_layout.setSpacing(8)
        
        # ════════════════════════════════════════════════════════════
        # ВЕРХНЯЯ ПАНЕЛЬ: ЯЗЫК
        # ════════════════════════════════════════════════════════════
        
        top_layout = QHBoxLayout()
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Русский", "English"])
        top_layout.addWidget(self.language_combo)
        top_layout.addStretch()
        control_layout.addLayout(top_layout)
        
        # ════════════════════════════════════════════════════════════
        # ПЕРЕКЛЮЧАТЕЛЬ РЕЖИМОВ КОНВЕРТАЦИИ (VIDEO/AUDIO)
        # ════════════════════════════════════════════════════════════
        
        mode_switcher_layout = QHBoxLayout()
        self.mode_switcher_label = QLabel()
        mode_switcher_layout.addWidget(self.mode_switcher_label)
        
        self.video_mode_radio = QRadioButton()
        self.video_mode_radio.setChecked(True)
        mode_switcher_layout.addWidget(self.video_mode_radio)
        
        self.audio_mode_radio = QRadioButton()
        mode_switcher_layout.addWidget(self.audio_mode_radio)
        
        mode_switcher_layout.addStretch()
        control_layout.addLayout(mode_switcher_layout)
        
        # ════════════════════════════════════════════════════════════
        # ПЕРЕКЛЮЧАТЕЛЬ ПРОСТОЙ/ПРОДВИНУТЫЙ РЕЖИМ
        # ════════════════════════════════════════════════════════════
        
        mode_layout = QHBoxLayout()
        self.mode_label = QLabel()
        mode_layout.addWidget(self.mode_label)
        
        self.simple_mode_radio = QRadioButton()
        self.simple_mode_radio.setChecked(True)
        mode_layout.addWidget(self.simple_mode_radio)
        
        self.advanced_mode_radio = QRadioButton()
        mode_layout.addWidget(self.advanced_mode_radio)
        
        mode_layout.addStretch()
        control_layout.addLayout(mode_layout)
        
        # ════════════════════════════════════════════════════════════
        # ВХОДНОЙ ФАЙЛ
        # ════════════════════════════════════════════════════════════
        
        input_layout = QHBoxLayout()
        self.input_file_label = QLabel()
        self.select_file_button = QPushButton()
        input_layout.addWidget(self.input_file_label)
        input_layout.addWidget(self.select_file_button)
        control_layout.addLayout(input_layout)
        
        file_info_layout = QHBoxLayout()
        self.selected_file_label = QLabel()
        self.selected_file_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        self.media_type_label = QLabel()
        self.media_type_label.setStyleSheet("font-weight: bold; color: #666; padding-left: 10px;")
        file_info_layout.addWidget(self.selected_file_label)
        file_info_layout.addWidget(self.media_type_label)
        file_info_layout.addStretch()
        control_layout.addLayout(file_info_layout)
        
        # Информация о размерах
        size_info_layout = QHBoxLayout()
        self.original_size_label = QLabel()
        self.original_size_label.setStyleSheet("color: #666;")
        self.estimated_size_label = QLabel()
        self.estimated_size_label.setStyleSheet("color: #0066cc; font-weight: bold;")
        size_info_layout.addWidget(self.original_size_label)
        size_info_layout.addStretch()
        size_info_layout.addWidget(self.estimated_size_label)
        control_layout.addLayout(size_info_layout)
        
        # Аудиодорожки (только для видео)
        tracks_layout = QHBoxLayout()
        self.audio_tracks_label = QLabel()
        self.audio_tracks_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        tracks_layout.addWidget(self.audio_tracks_label)
        tracks_layout.addStretch()
        control_layout.addLayout(tracks_layout)
        
        # ════════════════════════════════════════════════════════════
        # ВЫХОДНОЙ ФАЙЛ
        # ════════════════════════════════════════════════════════════
        
        output_layout = QHBoxLayout()
        self.output_file_label = QLabel()
        self.save_as_button = QPushButton()
        output_layout.addWidget(self.output_file_label)
        output_layout.addWidget(self.save_as_button)
        control_layout.addLayout(output_layout)
        
        self.output_path_label = QLabel()
        self.output_path_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        control_layout.addWidget(self.output_path_label)
        
        # ════════════════════════════════════════════════════════════
        # ФОРМАТ (с выпадающим списком и ручным вводом)
        # ════════════════════════════════════════════════════════════
        
        format_layout = QHBoxLayout()
        self.format_label = QLabel()
        self.format_combo = QComboBox()
        self.format_combo.addItems(list(OUTPUT_FORMATS.keys()))
        self.format_combo.currentIndexChanged.connect(self.on_format_changed)
        
        # Поле для ручного ввода формата (показывается только в продвинутом режиме)
        self.format_line_edit = QLineEdit()
        self.format_line_edit.setPlaceholderText("Введите формат вручную (например: mkv, ac3, m4a)...")
        self.format_line_edit.setVisible(False)
        self.format_line_edit.textChanged.connect(self.on_manual_format_changed)
        
        format_layout.addWidget(self.format_label)
        format_layout.addWidget(self.format_combo)
        format_layout.addWidget(self.format_line_edit)
        control_layout.addLayout(format_layout)
        
        # ════════════════════════════════════════════════════════════
        # НАСТРОЙКИ КАЧЕСТВА (ВИДЕО)
        # ════════════════════════════════════════════════════════════
        
        self.video_settings_group = QGroupBox()
        video_settings_layout = QVBoxLayout(self.video_settings_group)
        
        # Качество
        quality_layout = QHBoxLayout()
        self.quality_label = QLabel()
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setMinimum(0)
        self.quality_slider.setMaximum(51)
        self.quality_slider.setValue(23)
        self.quality_slider.setTickInterval(5)
        self.quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.current_quality_label = QLabel(str(self.quality_slider.value()))
        self.current_quality_label.setMinimumWidth(30)
        quality_layout.addWidget(self.quality_label)
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.current_quality_label)
        video_settings_layout.addLayout(quality_layout)
        
        self.quality_description_label = QLabel()
        self.quality_description_label.setStyleSheet("color: #666; font-style: italic; font-weight: bold;")
        video_settings_layout.addWidget(self.quality_description_label)
        
        # Информация о кодеках
        self.codec_info_label = QLabel()
        self.codec_info_label.setStyleSheet("color: #888; font-size: 10px;")
        video_settings_layout.addWidget(self.codec_info_label)
        
        # Чекбоксы
        self.lossless_checkbox = QCheckBox()
        self.lossless_checkbox.setCheckState(Qt.CheckState.Unchecked)
        self.lossless_checkbox.stateChanged.connect(self.update_lossless_state)
        video_settings_layout.addWidget(self.lossless_checkbox)
        
        self.keep_all_tracks_checkbox = QCheckBox()
        self.keep_all_tracks_checkbox.setCheckState(Qt.CheckState.Checked)
        self.keep_all_tracks_checkbox.setToolTip(LANGUAGES['keep_all_tracks_tooltip']['ru'])
        self.keep_all_tracks_checkbox.stateChanged.connect(self.update_keep_tracks_state)
        video_settings_layout.addWidget(self.keep_all_tracks_checkbox)
        
        # Чекбокс для копирования метаданных
        self.copy_metadata_checkbox = QCheckBox()
        self.copy_metadata_checkbox.setCheckState(Qt.CheckState.Checked)
        self.copy_metadata_checkbox.setToolTip("Копировать все метаданные (ID3 теги, обложки, etc.) из исходного файла")
        video_settings_layout.addWidget(self.copy_metadata_checkbox)
        
        # Кодеки
        codec_layout = QHBoxLayout()
        self.video_codec_label = QLabel()
        self.codec_combo = QComboBox()
        self.codec_combo.addItems(CODECS)
        self.codec_combo.currentIndexChanged.connect(self.on_codec_changed)
        self.codec_line_edit = QLineEdit("libx264")
        self.codec_line_edit.setPlaceholderText("Введите кодек вручную...")
        codec_layout.addWidget(self.video_codec_label)
        codec_layout.addWidget(self.codec_combo)
        codec_layout.addWidget(self.codec_line_edit)
        video_settings_layout.addLayout(codec_layout)
        
        # Аудио кодек (для видео)
        audio_codec_layout = QHBoxLayout()
        self.audio_codec_label = QLabel()
        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.addItems(AUDIO_CODECS)
        self.audio_codec_line_edit = QLineEdit("aac")
        self.audio_codec_line_edit.setPlaceholderText("Введите аудиокодек вручную...")
        audio_codec_layout.addWidget(self.audio_codec_label)
        audio_codec_layout.addWidget(self.audio_codec_combo)
        audio_codec_layout.addWidget(self.audio_codec_line_edit)
        video_settings_layout.addLayout(audio_codec_layout)
        
        control_layout.addWidget(self.video_settings_group)
        
        # ════════════════════════════════════════════════════════════
        # НАСТРОЙКИ АУДИО (отдельная группа)
        # ════════════════════════════════════════════════════════════
        
        self.audio_settings_group = QGroupBox()
        audio_settings_layout = QVBoxLayout(self.audio_settings_group)
        
        # Аудио кодек (с выпадающим списком и ручным вводом)
        audio_only_codec_layout = QHBoxLayout()
        self.audio_only_codec_label = QLabel()
        self.audio_only_codec_combo = QComboBox()
        self.audio_only_codec_combo.addItems(AUDIO_CODECS)
        self.audio_only_codec_combo.currentIndexChanged.connect(self.on_audio_codec_changed)
        self.audio_only_codec_line_edit = QLineEdit("aac")
        self.audio_only_codec_line_edit.setPlaceholderText("Введите аудиокодек вручную...")
        self.audio_only_codec_line_edit.setVisible(False)
        audio_only_codec_layout.addWidget(self.audio_only_codec_label)
        audio_only_codec_layout.addWidget(self.audio_only_codec_combo)
        audio_only_codec_layout.addWidget(self.audio_only_codec_line_edit)
        audio_settings_layout.addLayout(audio_only_codec_layout)
        
        # Битрейт
        bitrate_layout = QHBoxLayout()
        self.audio_bitrate_label = QLabel()
        self.audio_bitrate_edit = QLineEdit("192k")
        self.audio_bitrate_edit.setPlaceholderText("192k")
        self.audio_bitrate_edit.setToolTip("Введите битрейт (например: 128k, 192k, 320k)")
        bitrate_layout.addWidget(self.audio_bitrate_label)
        bitrate_layout.addWidget(self.audio_bitrate_edit)
        audio_settings_layout.addLayout(bitrate_layout)
        
        # Lossless для аудио
        self.audio_lossless_checkbox = QCheckBox()
        self.audio_lossless_checkbox.setCheckState(Qt.CheckState.Unchecked)
        self.audio_lossless_checkbox.stateChanged.connect(self.on_audio_lossless_changed)
        audio_settings_layout.addWidget(self.audio_lossless_checkbox)
        
        # Чекбокс для копирования метаданных в аудио режиме
        self.audio_copy_metadata_checkbox = QCheckBox()
        self.audio_copy_metadata_checkbox.setCheckState(Qt.CheckState.Checked)
        self.audio_copy_metadata_checkbox.setToolTip("Копировать все метаданные (ID3 теги, обложки, etc.) из исходного файла")
        audio_settings_layout.addWidget(self.audio_copy_metadata_checkbox)
        
        control_layout.addWidget(self.audio_settings_group)
        
        # ════════════════════════════════════════════════════════════
        # ДОПОЛНИТЕЛЬНЫЕ АРГУМЕНТЫ
        # ════════════════════════════════════════════════════════════
        
        ffmpeg_args_layout = QVBoxLayout()
        self.ffmpeg_args_label = QLabel()
        ffmpeg_args_layout.addWidget(self.ffmpeg_args_label)
        
        self.ffmpeg_args_edit = QTextEdit()
        self.ffmpeg_args_edit.setPlaceholderText("-b:v 2M -preset slow -tune film")
        self.ffmpeg_args_edit.setMaximumHeight(60)
        self.ffmpeg_args_edit.setToolTip(LANGUAGES['ffmpeg_args_tooltip']['ru'])
        self.ffmpeg_args_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                font-family: Consolas;
                font-size: 11px;
            }
        """)
        self.ffmpeg_args_edit.textChanged.connect(self.save_settings)
        ffmpeg_args_layout.addWidget(self.ffmpeg_args_edit)
        control_layout.addLayout(ffmpeg_args_layout)
        
        # ════════════════════════════════════════════════════════════
        # ПРОГРЕСС И КНОПКИ
        # ════════════════════════════════════════════════════════════
        
        progress_layout = QHBoxLayout()
        self.progress_label = QLabel()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        control_layout.addLayout(progress_layout)
        
        # ════════════════════════════════════════════════════════════
        # КНОПКИ УПРАВЛЕНИЯ
        # ════════════════════════════════════════════════════════════
        
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton()
        self.start_button.setMinimumHeight(40)
        palette = self.start_button.palette()
        palette.setColor(QPalette.ColorRole.Button, QColor(0, 200, 0))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        self.start_button.setPalette(palette)
        self.start_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00cc00;
            }
            QPushButton:pressed {
                background-color: #009900;
            }
            QPushButton:disabled {
                background-color: #888888;
            }
        """)
        
        self.clear_log_button = QPushButton()
        self.clear_log_button.setMinimumHeight(30)
        
        self.save_log_button = QPushButton()
        self.save_log_button.setMinimumHeight(30)
        self.save_log_button.clicked.connect(self.save_log_to_file)
        self.save_log_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                border-radius: 5px;
                background-color: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.clear_log_button)
        buttons_layout.addWidget(self.save_log_button)
        control_layout.addLayout(buttons_layout)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.control_panel)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_layout.addWidget(separator)
        
        # Метка лога
        self.log_label = QLabel()
        self.main_layout.addWidget(self.log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.log_text.setMinimumHeight(200)
        self.main_layout.addWidget(self.log_text)
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_widget.setLayout(self.main_layout)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def connect_signals(self):
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        self.select_file_button.clicked.connect(self.open_file_dialog)
        self.save_as_button.clicked.connect(self.open_save_as_dialog)
        self.start_button.clicked.connect(self.start_conversion)
        self.clear_log_button.clicked.connect(self.clear_log)
        self.quality_slider.valueChanged.connect(self.update_quality_display)
        self.format_combo.currentIndexChanged.connect(self.on_format_changed)
        self.codec_combo.currentIndexChanged.connect(self.on_codec_changed)
        self.codec_line_edit.textChanged.connect(self.update_codec_display)
        
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.simple_mode_radio)
        self.mode_group.addButton(self.advanced_mode_radio)
        self.mode_group.buttonClicked.connect(self.on_mode_changed)
        
        self.conversion_group = QButtonGroup(self)
        self.conversion_group.addButton(self.video_mode_radio)
        self.conversion_group.addButton(self.audio_mode_radio)
        self.conversion_group.buttonClicked.connect(self.on_conversion_mode_changed)

    # ════════════════════════════════════════════════════════════════
    # МЕТОДЫ СОХРАНЕНИЯ ЛОГА
    # ════════════════════════════════════════════════════════════════
    
    def save_log_to_file(self):
        lang = self.get_current_language()
        log_content = self.log_text.toPlainText()
        if not log_content.strip():
            QMessageBox.information(
                self,
                LANGUAGES['log_label'][lang],
                "Лог пуст. Нечего сохранять."
            )
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            LANGUAGES['save_log_dialog_title'][lang],
            f"ffmpeg_log_{QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss')}.txt",
            LANGUAGES['log_file_filter'][lang]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                self.status_bar.showMessage(LANGUAGES['log_saved'][lang] + " " + file_path)
                QMessageBox.information(
                    self,
                    LANGUAGES['log_label'][lang],
                    LANGUAGES['log_saved'][lang] + "\n" + file_path
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    LANGUAGES['log_save_error'][lang],
                    f"Ошибка при сохранении лога:\n{str(e)}"
                )
                self.status_bar.showMessage(LANGUAGES['log_save_error'][lang] + ": " + str(e))

    # ════════════════════════════════════════════════════════════════
    # ОБРАБОТЧИКИ РЕЖИМОВ
    # ════════════════════════════════════════════════════════════════

    def on_mode_changed(self, button):
        if button == self.simple_mode_radio:
            self.current_mode = "simple"
        else:
            self.current_mode = "advanced"
        self.update_mode_ui()
        self.save_settings()

    def on_conversion_mode_changed(self, button):
        if button == self.video_mode_radio:
            self.conversion_mode = "video"
        else:
            self.conversion_mode = "audio"
        self.update_conversion_mode_ui()
        self.save_settings()

    def update_mode_ui(self):
        if self.current_mode == "simple":
            self.codec_line_edit.setVisible(False)
            self.audio_codec_line_edit.setVisible(False)
            self.codec_combo.setVisible(True)
            self.audio_codec_combo.setVisible(True)
            self.audio_only_codec_line_edit.setVisible(False)
            self.audio_only_codec_combo.setVisible(True)
            self.format_line_edit.setVisible(False)
            self.format_combo.setVisible(True)
            self.ffmpeg_args_label.setVisible(False)
            self.ffmpeg_args_edit.setVisible(False)
        else:
            self.codec_line_edit.setVisible(True)
            self.audio_codec_line_edit.setVisible(True)
            self.codec_combo.setVisible(False)
            self.audio_codec_combo.setVisible(False)
            self.audio_only_codec_line_edit.setVisible(True)
            self.audio_only_codec_combo.setVisible(False)
            self.format_line_edit.setVisible(True)
            self.format_combo.setVisible(False)
            self.ffmpeg_args_label.setVisible(True)
            self.ffmpeg_args_edit.setVisible(True)
    
    def update_conversion_mode_ui(self):
        lang = self.get_current_language()
        
        if self.conversion_mode == "video":
            self.video_settings_group.setVisible(True)
            self.audio_settings_group.setVisible(False)
            self.format_combo.clear()
            self.format_combo.addItems(list(OUTPUT_FORMATS.keys()))
        else:
            self.video_settings_group.setVisible(False)
            self.audio_settings_group.setVisible(True)
            self.format_combo.clear()
            self.format_combo.addItems(AUDIO_FORMATS)
        
        self.video_mode_radio.setText(LANGUAGES['video_mode'][lang])
        self.audio_mode_radio.setText(LANGUAGES['audio_mode'][lang])
        
        # Синхронизируем чекбоксы копирования метаданных
        if self.conversion_mode == "video":
            self.copy_metadata_checkbox.setChecked(self.last_copy_metadata)
        else:
            self.audio_copy_metadata_checkbox.setChecked(self.last_copy_metadata)
        
        if self.conversion_mode == "audio":
            self.status_bar.showMessage("🎵 " + LANGUAGES['audio_mode'][lang])
        else:
            self.status_bar.showMessage("🎬 " + LANGUAGES['video_mode'][lang])
    
    def on_audio_codec_changed(self):
        codec = self.audio_only_codec_combo.currentText()
        if codec in AUDIO_CODEC_INFO:
            info = AUDIO_CODEC_INFO[codec]
            if info['lossless']:
                self.audio_bitrate_edit.setEnabled(False)
                self.audio_lossless_checkbox.setChecked(True)
                self.audio_lossless_checkbox.setEnabled(False)
            else:
                self.audio_bitrate_edit.setEnabled(True)
                self.audio_lossless_checkbox.setEnabled(True)
                if info['default_bitrate']:
                    self.audio_bitrate_edit.setText(info['default_bitrate'])
    
    def on_audio_lossless_changed(self, state):
        if state == Qt.CheckState.Checked:
            self.audio_bitrate_edit.setEnabled(False)
        else:
            self.audio_bitrate_edit.setEnabled(True)

    # ════════════════════════════════════════════════════════════════
    # ФОРМАТ
    # ════════════════════════════════════════════════════════════════
    
    def on_format_changed(self):
        format_name = self.format_combo.currentText()
        self.update_output_extension(format_name)
        self.save_settings()
    
    def on_manual_format_changed(self):
        manual_format = self.format_line_edit.text().strip()
        if manual_format:
            self.update_output_extension(manual_format)
            self.save_settings()
    
    def update_output_extension(self, format_name):
        current_path = self.output_path_label.text()
        if current_path and current_path not in ["Нет пути сохранения", "No output path"]:
            base = os.path.splitext(current_path)[0]
            new_path = f"{base}.{format_name}"
            self.output_path_label.setText(new_path)
    
    def get_current_format(self):
        if self.current_mode == "advanced":
            manual_format = self.format_line_edit.text().strip()
            if manual_format:
                return manual_format
        return self.format_combo.currentText()

    # ════════════════════════════════════════════════════════════════
    # КОДЕКИ
    # ════════════════════════════════════════════════════════════════
    
    def on_codec_changed(self):
        codec = self.codec_combo.currentText()
        self.update_codec_info(codec)
        self.update_quality_slider_range(codec)
        self.update_quality_display()
        self.save_settings()
    
    def update_codec_info(self, codec):
        if codec in CODEC_INFO:
            info = CODEC_INFO[codec]
            param = info['param'].upper()
            codec_type = "GPU" if info['type'] == 'gpu' else "CPU"
            self.codec_info_label.setText(f"📊 {codec}: {param} ({codec_type}) | Диапазон: {info['min']}-{info['max']}")
        else:
            self.codec_info_label.setText("")
    
    def update_quality_slider_range(self, codec):
        if codec in CODEC_INFO:
            info = CODEC_INFO[codec]
            self.quality_slider.setMinimum(info['min'])
            self.quality_slider.setMaximum(info['max'])
            current_value = self.quality_slider.value()
            if current_value < info['min'] or current_value > info['max']:
                self.quality_slider.setValue(info['default'])
        else:
            self.quality_slider.setMinimum(0)
            self.quality_slider.setMaximum(51)

    # ════════════════════════════════════════════════════════════════
    # ЗАГРУЗКА/СОХРАНЕНИЕ НАСТРОЕК
    # ════════════════════════════════════════════════════════════════

    def load_saved_settings(self):
        lang_index = 0 if self.current_language == "ru" else 1
        self.language_combo.setCurrentIndex(lang_index)
        
        self.conversion_mode = self.last_conversion_mode
        if self.conversion_mode == "video":
            self.video_mode_radio.setChecked(True)
        else:
            self.audio_mode_radio.setChecked(True)
        
        self.current_mode = self.last_mode
        if self.current_mode == "simple":
            self.simple_mode_radio.setChecked(True)
        else:
            self.advanced_mode_radio.setChecked(True)
        
        if self.last_input_path and os.path.exists(self.last_input_path):
            self.selected_file_label.setText(self.last_input_path)
            self.get_file_size(self.last_input_path)
            self.detect_and_display_media_type(self.last_input_path)
            self.detect_and_display_audio_tracks(self.last_input_path)
        
        if self.last_output_path:
            self.output_path_label.setText(self.last_output_path)
        
        if self.last_format in OUTPUT_FORMATS:
            format_index = list(OUTPUT_FORMATS.keys()).index(self.last_format)
            self.format_combo.setCurrentIndex(format_index)
            self.format_line_edit.setText(self.last_format)
        
        if self.last_video_codec in CODECS:
            codec_index = CODECS.index(self.last_video_codec)
            self.codec_combo.setCurrentIndex(codec_index)
            self.codec_line_edit.setText(self.last_video_codec)
            self.on_codec_changed()
        
        if self.last_audio_codec in AUDIO_CODECS:
            audio_index = AUDIO_CODECS.index(self.last_audio_codec)
            self.audio_codec_combo.setCurrentIndex(audio_index)
            self.audio_codec_line_edit.setText(self.last_audio_codec)
            self.audio_only_codec_combo.setCurrentIndex(audio_index)
        
        self.quality_slider.setValue(self.last_quality)
        self.lossless_checkbox.setChecked(self.last_lossless)
        self.keep_all_tracks_checkbox.setChecked(self.last_keep_all_tracks)
        self.copy_metadata_checkbox.setChecked(self.last_copy_metadata)
        self.audio_copy_metadata_checkbox.setChecked(self.last_copy_metadata)
        
        if self.last_ffmpeg_args:
            self.ffmpeg_args_edit.setPlainText(self.last_ffmpeg_args)
        
        self.update_estimated_size()
        self.update_mode_ui()
        self.update_conversion_mode_ui()
        self.on_audio_codec_changed()

    def save_settings(self):
        languages = ["ru", "en"]
        self.settings.setValue("language", languages[self.language_combo.currentIndex()])
        self.settings.setValue("mode", self.current_mode)
        self.settings.setValue("conversion_mode", self.conversion_mode)
        self.settings.setValue("last_input_path", self.selected_file_label.text())
        self.settings.setValue("last_output_path", self.output_path_label.text())
        self.settings.setValue("last_format", self.format_combo.currentText())
        self.settings.setValue("last_video_codec", self.codec_combo.currentText())
        self.settings.setValue("last_audio_codec", self.audio_codec_combo.currentText())
        self.settings.setValue("last_quality", self.quality_slider.value())
        self.settings.setValue("last_lossless", self.lossless_checkbox.isChecked())
        self.settings.setValue("last_keep_all_tracks", self.keep_all_tracks_checkbox.isChecked())
        self.settings.setValue("copy_metadata", self.copy_metadata_checkbox.isChecked())
        self.settings.setValue("ffmpeg_args", self.ffmpeg_args_edit.toPlainText().strip())
        self.settings.sync()

    # ════════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ ЯЗЫКОМ
    # ════════════════════════════════════════════════════════════════

    def update_ui_language(self, lang):
        self.current_language = lang
        
        self.setWindowTitle(LANGUAGES['window_title'][lang])
        self.select_file_button.setText(LANGUAGES['select_file_button'][lang])
        self.save_as_button.setText(LANGUAGES['save_as_button'][lang])
        self.clear_log_button.setText(LANGUAGES['clear_log'][lang])
        self.save_log_button.setText(LANGUAGES['save_log'][lang])
        
        if self.converter_thread and self.converter_thread.is_running:
            self.start_button.setText(LANGUAGES['stop_button'][lang])
        else:
            self.start_button.setText(LANGUAGES['start_button'][lang])
        
        self.input_file_label.setText(LANGUAGES['input_file_label'][lang])
        self.output_file_label.setText(LANGUAGES['output_file_label'][lang])
        self.format_label.setText(LANGUAGES['format_label'][lang])
        self.quality_label.setText(LANGUAGES['quality_label'][lang] + ":")
        self.progress_label.setText(LANGUAGES['progress'][lang])
        self.video_codec_label.setText(LANGUAGES['video_codec_label'][lang] + ":")
        self.audio_codec_label.setText(LANGUAGES['audio_codec_label'][lang] + ":")
        self.lossless_checkbox.setText(LANGUAGES['lossless_checkbox'][lang])
        self.log_label.setText(LANGUAGES['log_label'][lang])
        
        self.audio_only_codec_label.setText(LANGUAGES['audio_codec_label'][lang] + ":")
        self.audio_only_codec_line_edit.setPlaceholderText(LANGUAGES['custom_codec_hint'][lang])
        self.audio_only_codec_line_edit.setToolTip(LANGUAGES['audio_codec_label'][lang])
        self.audio_bitrate_label.setText(LANGUAGES['audio_bitrate_label'][lang])
        self.audio_lossless_checkbox.setText(LANGUAGES['lossless_checkbox'][lang])
        
        self.keep_all_tracks_checkbox.setText(LANGUAGES['keep_all_audio_tracks'][lang])
        self.keep_all_tracks_checkbox.setToolTip(LANGUAGES['keep_all_tracks_tooltip'][lang])
        
        # Чекбоксы копирования метаданных
        self.copy_metadata_checkbox.setText(LANGUAGES['copy_metadata'][lang])
        self.audio_copy_metadata_checkbox.setText(LANGUAGES['copy_metadata'][lang])
        
        self.mode_label.setText(LANGUAGES['mode_label'][lang])
        self.simple_mode_radio.setText(LANGUAGES['simple_mode'][lang])
        self.advanced_mode_radio.setText(LANGUAGES['advanced_mode'][lang])
        self.codec_line_edit.setPlaceholderText(LANGUAGES['custom_codec_hint'][lang])
        self.audio_codec_line_edit.setPlaceholderText(LANGUAGES['custom_codec_hint'][lang])
        
        self.format_line_edit.setPlaceholderText(LANGUAGES['custom_format_hint'][lang])
        self.format_line_edit.setToolTip(LANGUAGES['custom_format_tooltip'][lang])
        
        self.mode_switcher_label.setText(LANGUAGES['mode_switcher_label'][lang])
        self.video_mode_radio.setText(LANGUAGES['video_mode'][lang])
        self.audio_mode_radio.setText(LANGUAGES['audio_mode'][lang])
        
        self.ffmpeg_args_label.setText(LANGUAGES['ffmpeg_args_label'][lang])
        self.ffmpeg_args_edit.setPlaceholderText(LANGUAGES['ffmpeg_args_hint'][lang])
        self.ffmpeg_args_edit.setToolTip(LANGUAGES['ffmpeg_args_tooltip'][lang])
        
        self.original_size_label.setText(LANGUAGES['original_size'][lang])
        self.estimated_size_label.setText(LANGUAGES['estimated_size'][lang])
        
        self.codec_line_edit.setToolTip(LANGUAGES['video_codec_label'][lang])
        self.audio_codec_line_edit.setToolTip(LANGUAGES['audio_codec_label'][lang])
        
        self.video_settings_group.setTitle(LANGUAGES['video_mode'][lang])
        self.audio_settings_group.setTitle(LANGUAGES['audio_mode'][lang])
        
        self.update_media_type_display()
        self.update_audio_tracks_display()
        
        if self.selected_file_label.text() in ["Нет выбранного файла", "No file selected"]:
            self.selected_file_label.setText(LANGUAGES['no_file_selected'][lang])
            self.original_size_label.setText(LANGUAGES['original_size'][lang] + " " + LANGUAGES['file_not_found'][lang])
            self.estimated_size_label.setText(LANGUAGES['estimated_size'][lang] + " " + LANGUAGES['file_not_found'][lang])
        
        if self.output_path_label.text() in ["Нет пути сохранения", "No output path"]:
            self.output_path_label.setText(LANGUAGES['no_output_path'][lang])
        
        self.update_quality_display()
        self.update_conversion_mode_ui()
        
        if not (self.converter_thread and self.converter_thread.is_running):
            self.status_bar.showMessage(LANGUAGES['status_label'][lang] + " " + LANGUAGES['ready'][lang])

    def on_language_changed(self, index):
        languages = ["ru", "en"]
        lang = languages[index]
        self.update_ui_language(lang)
        self.save_settings()

    def get_current_language(self):
        return self.current_language

    # ════════════════════════════════════════════════════════════════
    # ОСТАЛЬНЫЕ МЕТОДЫ
    # ════════════════════════════════════════════════════════════════

    def detect_and_display_media_type(self, file_path):
        self.input_media_type = detect_media_type(file_path)
        self.update_media_type_display()
        return self.input_media_type

    def update_media_type_display(self):
        lang = self.get_current_language()
        if self.input_media_type == "video":
            type_text = LANGUAGES['media_type_video'][lang]
            color = "#4CAF50"
        elif self.input_media_type == "audio":
            type_text = LANGUAGES['media_type_audio'][lang]
            color = "#FF9800"
        else:
            type_text = LANGUAGES['media_type_unknown'][lang]
            color = "#666"
        self.media_type_label.setText(f"[{type_text}]")
        self.media_type_label.setStyleSheet(f"font-weight: bold; color: {color}; padding-left: 10px;")

    def detect_and_display_audio_tracks(self, file_path):
        self.audio_tracks_count = get_audio_tracks_count(file_path)
        self.update_audio_tracks_display()
        if self.audio_tracks_count > 1:
            self.keep_all_tracks_checkbox.setChecked(True)
            self.keep_all_tracks_checkbox.setEnabled(True)
        else:
            self.keep_all_tracks_checkbox.setChecked(False)
            self.keep_all_tracks_checkbox.setEnabled(False)
        return self.audio_tracks_count

    def update_audio_tracks_display(self):
        lang = self.get_current_language()
        if self.audio_tracks_count == 0:
            self.audio_tracks_label.setText(LANGUAGES['no_audio_tracks'][lang])
            self.audio_tracks_label.setStyleSheet("color: #666; font-weight: bold;")
        else:
            self.audio_tracks_label.setText(
                LANGUAGES['audio_tracks_detected'][lang] + str(self.audio_tracks_count)
            )
            self.audio_tracks_label.setStyleSheet("color: #FF9800; font-weight: bold;")

    def update_keep_tracks_state(self, state):
        self.save_settings()
        lang = self.get_current_language()
        if state == Qt.CheckState.Checked:
            self.status_bar.showMessage(
                f"✅ {LANGUAGES['keep_all_audio_tracks'][lang]} ({self.audio_tracks_count} дорожек)"
            )
        else:
            self.status_bar.showMessage(
                f"❌ {LANGUAGES['keep_all_audio_tracks'][lang]} (только первая дорожка)"
            )

    def open_file_dialog(self):
        lang = self.get_current_language()
        start_dir = ""
        if self.last_input_path and os.path.exists(os.path.dirname(self.last_input_path)):
            start_dir = os.path.dirname(self.last_input_path)
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            LANGUAGES['file_dialog_title'][lang], 
            start_dir, 
            "All Files (*);;Video Files (*.mp4 *.avi *.mkv *.mov *.webm);;Audio Files (*.mp3 *.wav *.flac *.aac *.ogg)"
        )
        if file_path:
            self.selected_file_label.setText(file_path)
            self.status_bar.showMessage(LANGUAGES['file_selected'][lang] + " " + file_path)
            self.get_file_size(file_path)
            self.detect_and_display_media_type(file_path)
            self.detect_and_display_audio_tracks(file_path)
            self.update_estimated_size()
            self.save_settings()
            if self.input_media_type == "audio":
                self.audio_mode_radio.setChecked(True)
                self.on_conversion_mode_changed()

    def open_save_as_dialog(self):
        lang = self.get_current_language()
        start_dir = ""
        if self.last_output_path and os.path.exists(os.path.dirname(self.last_output_path)):
            start_dir = os.path.dirname(self.last_output_path)
        
        format_name = self.get_current_format()
        
        file_filter = "All Files (*)"
        for fmt, desc in OUTPUT_FORMATS.items():
            file_filter += f";;{desc}"
        
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, 
            LANGUAGES['save_dialog_title'][lang], 
            start_dir, 
            file_filter
        )
        
        if file_path:
            _, ext = os.path.splitext(file_path)
            if not ext:
                file_path = f"{file_path}.{format_name}"
            else:
                ext_without_dot = ext[1:].lower()
                if ext_without_dot not in OUTPUT_FORMATS:
                    file_path = f"{file_path}.{format_name}"
            self.output_path_label.setText(file_path)
            self.status_bar.showMessage(LANGUAGES['output_selected'][lang] + " " + file_path)
            self.save_settings()

    def clear_log(self):
        self.log_text.clear()

    def update_quality_display(self, value=None):
        if value is None:
            value = self.quality_slider.value()
        self.current_quality_label.setText(str(value))
        self.update_quality_description(value)
        self.update_estimated_size()
        self.save_settings()

    def update_quality_description(self, value):
        lang = self.get_current_language()
        codec = self.get_video_codec()
        if codec in CODEC_INFO:
            info = CODEC_INFO[codec]
            param = info['param'].upper()
            min_val = info['min']
            max_val = info['max']
            if param in ['crf', 'cq']:
                if max_val > min_val:
                    normalized = (value - min_val) / (max_val - min_val)
                else:
                    normalized = 0
                if value == min_val:
                    description = LANGUAGES['quality_best'][lang]
                elif normalized < 0.2:
                    description = LANGUAGES['quality_best'][lang]
                elif normalized < 0.4:
                    description = LANGUAGES['quality_high'][lang]
                elif normalized < 0.7:
                    description = LANGUAGES['quality_medium'][lang]
                else:
                    description = LANGUAGES['quality_low'][lang]
                self.quality_description_label.setText(f"{description} ({param}: {value})")
            else:
                if value <= min_val + 1:
                    description = LANGUAGES['quality_best'][lang]
                elif value <= min_val + (max_val - min_val) * 0.3:
                    description = LANGUAGES['quality_high'][lang]
                elif value <= min_val + (max_val - min_val) * 0.6:
                    description = LANGUAGES['quality_medium'][lang]
                else:
                    description = LANGUAGES['quality_low'][lang]
                self.quality_description_label.setText(f"{description} ({param}: {value})")
        else:
            if value < 18:
                description = LANGUAGES['quality_best'][lang]
            elif value < 24:
                description = LANGUAGES['quality_high'][lang]
            elif value < 30:
                description = LANGUAGES['quality_medium'][lang]
            else:
                description = LANGUAGES['quality_low'][lang]
            self.quality_description_label.setText(description)

    def update_lossless_state(self, state):
        lang = self.get_current_language()
        if state == Qt.CheckState.Checked:
            self.status_bar.showMessage("✅ " + LANGUAGES['lossless_enabled'][lang])
            self.quality_slider.setEnabled(False)
            self.quality_description_label.setText(LANGUAGES['quality_lossless'][lang])
        else:
            self.status_bar.showMessage("❌ " + LANGUAGES['lossless_disabled'][lang])
            self.quality_slider.setEnabled(True)
            self.update_quality_description(self.quality_slider.value())
        self.update_estimated_size()
        self.save_settings()

    def get_file_size(self, file_path):
        try:
            if os.path.exists(file_path):
                self.original_file_size = os.path.getsize(file_path)
                lang = self.get_current_language()
                size_mb = self.original_file_size / (1024 * 1024)
                self.original_size_label.setText(
                    LANGUAGES['original_size'][lang] + f" {size_mb:.2f} MB"
                )
            else:
                self.original_file_size = 0
        except Exception:
            self.original_file_size = 0

    def update_estimated_size(self):
        lang = self.get_current_language()
        if self.original_file_size == 0:
            self.estimated_size_label.setText(
                LANGUAGES['estimated_size'][lang] + " " + LANGUAGES['file_not_found'][lang]
            )
            return
        crf = self.quality_slider.value()
        if self.lossless_checkbox.isChecked():
            estimated_mb = (self.original_file_size / (1024 * 1024)) * 2.5
            self.estimated_size_label.setText(
                LANGUAGES['estimated_size'][lang] + f" ~{estimated_mb:.2f} MB (lossless)"
            )
            return
        track_multiplier = 1.0
        if self.keep_all_tracks_checkbox.isChecked() and self.audio_tracks_count > 1:
            track_multiplier = 1.0 + (self.audio_tracks_count - 1) * 0.3
        adjusted_crf = max(0, crf)
        ratio = 1 / (2 ** ((adjusted_crf - 17) / 6))
        ratio = max(0.01, min(15.0, ratio)) * track_multiplier
        estimated_bytes = self.original_file_size * ratio
        estimated_mb = estimated_bytes / (1024 * 1024)
        if estimated_mb < 0.1:
            estimated_kb = estimated_mb * 1024
            self.estimated_size_label.setText(
                LANGUAGES['estimated_size'][lang] + f" ~{estimated_kb:.1f} KB"
            )
        else:
            self.estimated_size_label.setText(
                LANGUAGES['estimated_size'][lang] + f" ~{estimated_mb:.2f} MB"
            )

    def update_codec_display(self):
        lang = self.get_current_language()
        selected_codec = self.get_video_codec()
        self.status_bar.showMessage(LANGUAGES['codec_selected'][lang] + " " + selected_codec)
        self.on_codec_changed()
        self.save_settings()

    def get_video_codec(self):
        if self.current_mode == "advanced":
            return self.codec_line_edit.text().strip() or "libx264"
        return self.codec_combo.currentText()
    
    def get_audio_codec(self):
        if self.current_mode == "advanced":
            return self.audio_codec_line_edit.text().strip() or "aac"
        return self.audio_codec_combo.currentText()
    
    def get_audio_only_codec(self):
        if self.current_mode == "advanced":
            return self.audio_only_codec_line_edit.text().strip() or "aac"
        return self.audio_only_codec_combo.currentText()
    
    def get_copy_metadata(self):
        if self.conversion_mode == "video":
            return self.copy_metadata_checkbox.isChecked()
        else:
            return self.audio_copy_metadata_checkbox.isChecked()
    
    def get_ffmpeg_args(self):
        if self.current_mode == "advanced":
            return self.ffmpeg_args_edit.toPlainText().strip()
        return ""

    def check_ffmpeg(self):
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            return True, ffmpeg_path
        else:
            return False, LANGUAGES['ffmpeg_not_found'][self.get_current_language()]

    # ════════════════════════════════════════════════════════════════
    # ЗАПУСК КОНВЕРТАЦИИ
    # ════════════════════════════════════════════════════════════════

    def start_conversion(self):
        if self.converter_thread and self.converter_thread.is_running:
            self.stop_conversion()
            return
        
        lang = self.get_current_language()
        self.status_bar.showMessage("🔄 " + LANGUAGES['ffmpeg_checking'][lang])
        
        ffmpeg_found, ffmpeg_result = self.check_ffmpeg()
        if not ffmpeg_found:
            QMessageBox.critical(
                self, 
                LANGUAGES['ffmpeg_error_title'][lang], 
                LANGUAGES['ffmpeg_error_message'][lang]
            )
            self.status_bar.showMessage(LANGUAGES['ffmpeg_not_found'][lang])
            return
        
        input_file = self.selected_file_label.text()
        output_file = self.output_path_label.text()
        
        no_file_ru = LANGUAGES['no_file_selected']['ru']
        no_file_en = LANGUAGES['no_file_selected']['en']
        no_output_ru = LANGUAGES['no_output_path']['ru']
        no_output_en = LANGUAGES['no_output_path']['en']
        
        if input_file in [no_file_ru, no_file_en] or output_file in [no_output_ru, no_output_en]:
            QMessageBox.critical(
                self, 
                LANGUAGES['file_error_title'][lang], 
                LANGUAGES['file_error_message'][lang]
            )
            self.status_bar.showMessage("⚠️ " + LANGUAGES['file_error_title'][lang])
            return
        
        if not os.path.exists(input_file):
            QMessageBox.critical(
                self,
                LANGUAGES['file_error_title'][lang],
                "Входной файл не существует!"
            )
            return
        
        format_ = self.get_current_format()
        ffmpeg_args = self.get_ffmpeg_args()
        copy_metadata = self.get_copy_metadata()
        
        self.log_text.clear()
        self.log_text.append(f"[INFO] ========================================\n")
        self.log_text.append(f"[INFO] {LANGUAGES['conversion_started'][lang]}\n")
        self.log_text.append(f"[INFO] Режим конвертации: {self.conversion_mode.upper()}\n")
        self.log_text.append(f"[INFO] Входной файл: {input_file}\n")
        self.log_text.append(f"[INFO] Выходной файл: {output_file}\n")
        self.log_text.append(f"[INFO] Формат: {format_}\n")
        self.log_text.append(f"[INFO] Копировать метаданные: {copy_metadata}\n")
        
        if self.conversion_mode == "audio":
            audio_codec = self.get_audio_only_codec()
            bitrate = self.audio_bitrate_edit.text().strip()
            lossless = self.audio_lossless_checkbox.isChecked()
            
            self.log_text.append(f"[INFO] Аудиокодек: {audio_codec}\n")
            if bitrate and not lossless:
                self.log_text.append(f"[INFO] Битрейт: {bitrate}\n")
            self.log_text.append(f"[INFO] Без потерь: {lossless}\n")
            if ffmpeg_args:
                self.log_text.append(f"[INFO] Доп. аргументы: {ffmpeg_args}\n")
            self.log_text.append(f"[INFO] ========================================\n")
            
            self.converter_thread = AudioConverterThread(
                input_file, output_file, format_, 
                audio_codec, bitrate, 0, lossless, 
                copy_metadata, ffmpeg_args
            )
        else:
            video_codec = self.get_video_codec()
            audio_codec = self.get_audio_codec()
            quality = self.quality_slider.value()
            lossless = self.lossless_checkbox.isChecked()
            keep_all_tracks = self.keep_all_tracks_checkbox.isChecked()
            
            self.log_text.append(f"[INFO] Видеокодек: {video_codec}\n")
            if video_codec in CODEC_INFO:
                info = CODEC_INFO[video_codec]
                self.log_text.append(f"[INFO] Параметр качества: {info['param'].upper()}={quality}\n")
            self.log_text.append(f"[INFO] Аудиокодек: {audio_codec}\n")
            self.log_text.append(f"[INFO] Без потерь: {lossless}\n")
            self.log_text.append(f"[INFO] Сохранить все дорожки: {keep_all_tracks}\n")
            if ffmpeg_args:
                self.log_text.append(f"[INFO] Доп. аргументы: {ffmpeg_args}\n")
            self.log_text.append(f"[INFO] ========================================\n")
            
            self.converter_thread = VideoConverterThread(
                input_file, output_file, format_, 
                video_codec, audio_codec, quality, lossless,
                keep_all_tracks, self.audio_tracks_count, ffmpeg_args
            )
        
        self.converter_thread.status_update.connect(self.on_status_update)
        self.converter_thread.progress_update.connect(self.on_progress_update)
        self.converter_thread.log_update.connect(self.on_log_update)
        self.converter_thread.conversion_finished.connect(self.on_conversion_finished)
        
        self.converter_thread.start()
        
        self.start_button.setText(LANGUAGES['stop_button'][lang])
        self.start_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
                background-color: #ff4444;
                color: white;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
        """)
        
        self.select_file_button.setEnabled(False)
        self.save_as_button.setEnabled(False)
        self.format_combo.setEnabled(False)
        self.format_line_edit.setEnabled(False)
        self.video_mode_radio.setEnabled(False)
        self.audio_mode_radio.setEnabled(False)
        self.simple_mode_radio.setEnabled(False)
        self.advanced_mode_radio.setEnabled(False)
        self.codec_combo.setEnabled(False)
        self.codec_line_edit.setEnabled(False)
        self.audio_codec_combo.setEnabled(False)
        self.audio_codec_line_edit.setEnabled(False)
        self.audio_only_codec_combo.setEnabled(False)
        self.audio_only_codec_line_edit.setEnabled(False)
        self.lossless_checkbox.setEnabled(False)
        self.audio_lossless_checkbox.setEnabled(False)
        self.keep_all_tracks_checkbox.setEnabled(False)
        self.copy_metadata_checkbox.setEnabled(False)
        self.audio_copy_metadata_checkbox.setEnabled(False)
        self.ffmpeg_args_edit.setEnabled(False)
        
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)
        
        self.status_bar.showMessage("🔄 " + LANGUAGES['converting'][lang] + "...")

    def stop_conversion(self):
        if self.converter_thread and self.converter_thread.is_running:
            self.converter_thread.stop()
            self.status_bar.showMessage("⏹️ " + LANGUAGES['conversion_stopped'][self.get_current_language()])
            lang = self.get_current_language()
            self.start_button.setText(LANGUAGES['start_button'][lang])
            self.start_button.setStyleSheet("""
                QPushButton {
                    font-weight: bold;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #00c800;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #00dd00;
                }
                QPushButton:pressed {
                    background-color: #009900;
                }
                QPushButton:disabled {
                    background-color: #888888;
                }
            """)

    def on_status_update(self, message):
        self.status_bar.showMessage(message)

    def on_progress_update(self, progress):
        self.progress_bar.setValue(progress)
        if progress >= 100:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #bbb;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 5px;
                }
            """)

    def on_log_update(self, line):
        self.log_text.append(line)
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()

    def on_conversion_finished(self, success, message):
        lang = self.get_current_language()
        
        self.start_button.setText(LANGUAGES['start_button'][lang])
        self.start_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
                background-color: #00c800;
                color: white;
            }
            QPushButton:hover {
                background-color: #00dd00;
            }
            QPushButton:pressed {
                background-color: #009900;
            }
            QPushButton:disabled {
                background-color: #888888;
            }
        """)
        
        self.select_file_button.setEnabled(True)
        self.save_as_button.setEnabled(True)
        self.format_combo.setEnabled(True)
        self.format_line_edit.setEnabled(True)
        self.video_mode_radio.setEnabled(True)
        self.audio_mode_radio.setEnabled(True)
        self.simple_mode_radio.setEnabled(True)
        self.advanced_mode_radio.setEnabled(True)
        self.codec_combo.setEnabled(True)
        self.codec_line_edit.setEnabled(True)
        self.audio_codec_combo.setEnabled(True)
        self.audio_codec_line_edit.setEnabled(True)
        self.audio_only_codec_combo.setEnabled(True)
        self.audio_only_codec_line_edit.setEnabled(True)
        self.lossless_checkbox.setEnabled(True)
        self.audio_lossless_checkbox.setEnabled(True)
        self.keep_all_tracks_checkbox.setEnabled(True)
        self.copy_metadata_checkbox.setEnabled(True)
        self.audio_copy_metadata_checkbox.setEnabled(True)
        self.ffmpeg_args_edit.setEnabled(True)
        
        if success:
            self.progress_bar.setValue(100)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #bbb;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 5px;
                }
            """)
            self.status_bar.showMessage("✅ " + message)
            QMessageBox.information(
                self, 
                LANGUAGES['conversion_complete'][lang], 
                LANGUAGES['conversion_success'][lang]
            )
        else:
            self.progress_bar.setValue(0)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #bbb;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: #ff4444;
                    border-radius: 5px;
                }
            """)
            self.status_bar.showMessage("❌ " + message)
            if "остановлен" in message or "stopped" in message:
                QMessageBox.information(
                    self, 
                    LANGUAGES['conversion_stopped'][lang], 
                    message
                )
            else:
                QMessageBox.critical(
                    self, 
                    LANGUAGES['conversion_error'][lang], 
                    LANGUAGES['conversion_failed_msg'][lang]
                )
        
        self.converter_thread = None

    def closeEvent(self, event):
        self.save_settings()
        if self.converter_thread and self.converter_thread.is_running:
            self.converter_thread.stop()
            self.converter_thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
