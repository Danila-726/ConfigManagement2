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
            
            # В тестовом режиме НЕ преобразуем имена пакетов - оставляем как есть
            # Реальный APKINDEX использует нижний регистр
            
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
        # Ищем блок от "P:package_name" до следующего "C:" или конца файла
        pattern = rf'P:{re.escape(package_name)}\n(.*?)(?=\nC:|\n\n|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return f"P:{package_name}\n{match.group(1)}"
        return None
    
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
                # Разделяем зависимости по пробелам
                raw_deps = deps_line.split()
                for dep in raw_deps:
                    # Очищаем зависимость от версий и префиксов
                    clean_dep = self._clean_dependency(dep)
                    if clean_dep and clean_dep not in dependencies:
                        dependencies.append(clean_dep)
        
        return dependencies
    
    def _clean_dependency(self, dependency):
        """
        Очистка зависимости от версий и специальных префиксов
        
        Args:
            dependency (str): Сырая зависимость
            
        Returns:
            str: Очищенное имя пакета или None если это не пакет
        """
        # Игнорируем зависимости с префиксами: so: (библиотеки), p: (предоставляемые пакеты), pc: (pkg-config)
        if dependency.startswith(('so:', 'p:', 'pc:', 'cmd:')):
            return None
        
        # Убираем версии (все что после =, <, >, ~ и т.д.)
        clean_dep = re.split(r'[=<>~]', dependency)[0]
        
        return clean_dep
    
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