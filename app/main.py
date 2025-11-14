#!/usr/bin/env python3

import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import setup_arg_parser, validate_arguments, print_configuration
from repository import RepositoryManager
from apk_parser import APKParser
from exceptions import ValidationError, RepositoryError, PackageNotFoundError, APKParseError

def main():
    parser = setup_arg_parser()
    
    try:
        args = parser.parse_args()
        
        # Валидация параметров
        validate_arguments(args)
        
        # Вывод конфигурации (требование этапа 1)
        print_configuration(args)
        
        # Создание менеджера репозитория
        repo_manager = RepositoryManager(args.repo, args.test_repo_mode)
        
        # Создание парсера APK
        apk_parser = APKParser(repo_manager)
        
        # Получение зависимостей пакета
        dependencies = apk_parser.get_package_dependencies(args.package)
        
        # Вывод зависимостей (требование этапа 2)
        apk_parser.print_dependencies(args.package, dependencies)
        
        print("\nПриложение успешно завершило работу!")
        
    except (ValidationError, RepositoryError, PackageNotFoundError, APKParseError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nПрервано пользователем", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()