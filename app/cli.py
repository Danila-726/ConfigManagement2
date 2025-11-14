import argparse
import os
from pathlib import Path
from exceptions import ValidationError

def setup_arg_parser():
    """Настройка парсера аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Инструмент визуализации графа зависимостей пакетов',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Обязательные параметры
    parser.add_argument(
        '--package',
        '-p',
        required=True,
        help='Имя анализируемого пакета'
    )
    
    parser.add_argument(
        '--repo',
        '-r',
        required=True,
        help='URL-адрес репозитория или путь к файлу тестового репозитория'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        required=True,
        help='Имя сгенерированного файла с изображением графа'
    )
    
    # Флаги
    parser.add_argument(
        '--test-repo-mode',
        '-t',
        action='store_true',
        help='Режим работы с тестового репозитория'
    )
    
    parser.add_argument(
        '--ascii-tree',
        '-a',
        action='store_true',
        help='Режим вывода зависимостей в формате ASCII-дерева'
    )
    
    return parser

def validate_arguments(args):
    """Валидация переданных аргументов"""
    
    # Проверка имени пакета
    if not args.package or not args.package.strip():
        raise ValidationError("Имя пакета не может быть пустым")
    
    if not is_valid_package_name(args.package):
        raise ValidationError(f"Некорректное имя пакета: {args.package}")
    
    # Проверка репозитория
    if not args.repo or not args.repo.strip():
        raise ValidationError("Репозиторий не может быть пустым")
    
    # Если включен режим тестового репозитория, проверяем что путь существует
    if args.test_repo_mode:
        if not os.path.exists(args.repo):
            raise ValidationError(f"Файл тестового репозитория не существует: {args.repo}")
        if not os.path.isfile(args.repo):
            raise ValidationError(f"Указанный путь не является файлом: {args.repo}")
    else:
        # Проверка URL (базовая валидация)
        if not is_valid_url_or_path(args.repo):
            raise ValidationError(f"Некорректный URL или путь: {args.repo}")
    
    # Проверка выходного файла
    if not args.output or not args.output.strip():
        raise ValidationError("Имя выходного файла не может быть пустым")
    
    output_dir = os.path.dirname(args.output) or '.'
    if not os.path.exists(output_dir):
        raise ValidationError(f"Директория для выходного файла не существует: {output_dir}")
    
    if not os.access(output_dir, os.W_OK):
        raise ValidationError(f"Нет прав на запись в директорию: {output_dir}")
    
    # Проверка расширения файла
    valid_extensions = {'.png', '.jpg', '.jpeg', '.svg', '.pdf'}
    file_ext = Path(args.output).suffix.lower()
    if file_ext and file_ext not in valid_extensions:
        raise ValidationError(f"Неподдерживаемое расширение файла: {file_ext}. Допустимые: {', '.join(valid_extensions)}")

def is_valid_package_name(package_name):
    """Проверка корректности имени пакета"""
    if not package_name:
        return False
    
    # Имя пакета не должно содержать запрещенных символов
    invalid_chars = {'/', '\\', ':', '*', '?', '"', '<', '>', '|'}
    if any(char in package_name for char in invalid_chars):
        return False
    
    return True

def is_valid_url_or_path(repo):
    """Базовая проверка URL или пути"""
    if not repo:
        return False
    
    # Проверка на базовые схемы URL
    if repo.startswith(('http://', 'https://', 'ftp://')):
        return True
    
    # Проверка что это может быть путь
    try:
        Path(repo)
        return True
    except Exception:
        return False

def print_configuration(args):
    """Вывод конфигурации параметров"""
    print("Настроенные параметры:")
    print(f"  Имя пакета: {args.package}")
    print(f"  Репозиторий: {args.repo}")
    print(f"  Режим тестового репозитория: {'Включен' if args.test_repo_mode else 'Выключен'}")
    print(f"  Выходной файл: {args.output}")
    print(f"  Режим ASCII-дерева: {'Включен' if args.ascii_tree else 'Выключен'}")