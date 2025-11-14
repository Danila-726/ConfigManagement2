import re
from pathlib import Path
from exceptions import PackageNotFoundError, APKParseError

class APKParser:
    """Парсер для работы с APK пакетами Alpine Linux"""
    
    def __init__(self, repository_manager):
        self.repository_manager = repository_manager
    
    def get_package_dependencies(self, package_name):
        """
        Получение прямых зависимостей пакета
        
        Args:
            package_name (str): Имя пакета
            
        Returns:
            list: Список прямых зависимостей
        """
        repo_file = self.repository_manager.get_repository_content()
        
        try:
            with open(repo_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Ищем секцию пакета
            package_section = self._find_package_section(content, package_name)
            if not package_section:
                raise PackageNotFoundError(f"Пакет '{package_name}' не найден в репозитории")
            
            # Извлекаем зависимости
            dependencies = self._extract_dependencies(package_section)
            return dependencies
            
        except (UnicodeDecodeError, IOError) as e:
            raise APKParseError(f"Ошибка чтения файла репозитория: {e}")
    
    def _find_package_section(self, content, package_name):
        """
        Поиск секции пакета в содержимом репозитория
        
        Args:
            content (str): Содержимое файла репозитория
            package_name (str): Имя пакета
            
        Returns:
            str: Секция пакета или None если не найдена
        """
        # Паттерн для поиска секции пакета в формате APKINDEX
        pattern = rf'P:{package_name}\n(.*?)(?=\nP:|\n\n|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        return match.group(0) if match else None
    
    def _extract_dependencies(self, package_section):
        """
        Извлечение зависимостей из секции пакета
        
        Args:
            package_section (str): Секция пакета
            
        Returns:
            list: Список зависимостей
        """
        dependencies = []
        
        # Ищем строку с зависимостями (D:)
        dep_match = re.search(r'D:(.*?)(?=\n[A-Z]:|\n\n|\Z)', package_section, re.DOTALL)
        if dep_match:
            deps_line = dep_match.group(1).strip()
            if deps_line:
                # Разделяем зависимости по пробелам и убираем версии
                raw_deps = deps_line.split()
                for dep in raw_deps:
                    # Убираем версии (все что после =, <, >, ~ и т.д.)
                    clean_dep = re.split(r'[=<>~]', dep)[0]
                    if clean_dep and clean_dep not in dependencies:
                        dependencies.append(clean_dep)
        
        return dependencies
    
    def print_dependencies(self, package_name, dependencies):
        """
        Вывод зависимостей в консоль
        
        Args:
            package_name (str): Имя пакета
            dependencies (list): Список зависимостей
        """
        print(f"\nПрямые зависимости пакета '{package_name}':")
        if dependencies:
            for i, dep in enumerate(dependencies, 1):
                print(f"  {i}. {dep}")
        else:
            print("  Пакет не имеет зависимостей")