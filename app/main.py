#!/usr/bin/env python3

import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import setup_arg_parser, validate_arguments, print_configuration
from repository import RepositoryManager
from apk_parser import APKParser
from dependency_graph import DependencyGraph
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
        
        # Получение прямых зависимостей пакета (требование этапа 2)
        dependencies = apk_parser.get_package_dependencies(args.package)
        apk_parser.print_dependencies(args.package, dependencies)
        
        # Построение полного графа зависимостей (требование этапа 3)
        print("\n" + "="*50)
        print("ПОСТРОЕНИЕ ПОЛНОГО ГРАФА ЗАВИСИМОСТЕЙ")
        print("="*50)
        
        graph_builder = DependencyGraph(apk_parser)
        full_graph = graph_builder.build_dependency_graph(args.package)
        
        # Вывод информации о графе
        print(f"\nГраф зависимостей построен успешно!")
        print(f"Всего пакетов в графе: {len(full_graph)}")
        print(f"Корневой пакет: {args.package}")
        
        # Получение транзитивных зависимостей
        transitive_deps = graph_builder.get_transitive_dependencies(args.package)
        print(f"Всего транзитивных зависимостей: {len(transitive_deps)}")
        
        # Проверка циклических зависимостей
        if graph_builder.has_cycles():
            cycles = graph_builder.get_cycles()
            print(f"Обнаружено циклических зависимостей: {len(cycles)}")
            for i, cycle in enumerate(cycles, 1):
                print(f"  Цикл {i}: {' -> '.join(cycle)}")
        else:
            print("Циклические зависимости не обнаружены")
        
        # Вывод ASCII-дерева если запрошено
        if args.ascii_tree:
            graph_builder.print_dependency_tree(args.package)
        
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