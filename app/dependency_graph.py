from collections import deque
from exceptions import PackageNotFoundError, APKParseError

class DependencyGraph:
    """Класс для построения графа зависимостей пакетов"""
    
    def __init__(self, apk_parser):
        self.apk_parser = apk_parser
        self.graph = {}
        self.visited = set()
        self.current_path = set()
        self.cycles = []
    
    def build_dependency_graph(self, root_package):
        """
        Построение полного графа зависимостей с использованием DFS без рекурсии
        
        Args:
            root_package (str): Корневой пакет для анализа
            
        Returns:
            dict: Граф зависимостей в формате {пакет: [зависимости]}
        """
        self.graph = {}
        self.visited = set()
        self.current_path = set()
        self.cycles = []
        
        # Используем стек для DFS без рекурсии
        stack = [(root_package, False)]  # (package, is_backtrack)
        
        while stack:
            current_package, is_backtrack = stack.pop()
            
            if is_backtrack:
                # Возвращаемся из рекурсивного вызова - удаляем из текущего пути
                self.current_path.remove(current_package)
                continue
            
            if current_package in self.visited:
                continue
                
            # Помечаем как посещенный
            self.visited.add(current_package)
            self.current_path.add(current_package)
            
            # Добавляем маркер возврата в стек
            stack.append((current_package, True))
            
            try:
                # Получаем зависимости текущего пакета
                dependencies = self.apk_parser.get_package_dependencies(current_package)
                self.graph[current_package] = dependencies
                
                # Проверяем циклические зависимости
                for dep in dependencies:
                    if dep in self.current_path:
                        # Найден цикл
                        cycle_path = list(self.current_path) + [dep]
                        self.cycles.append(cycle_path)
                        print(f"Предупреждение: обнаружена циклическая зависимость: {' -> '.join(cycle_path)}")
                    
                    if dep not in self.visited:
                        stack.append((dep, False))
                        
            except (PackageNotFoundError, APKParseError) as e:
                print(f"Предупреждение: не удалось получить зависимости для пакета '{current_package}': {e}")
                self.graph[current_package] = []
        
        return self.graph
    
    def get_transitive_dependencies(self, package_name):
        """
        Получение всех транзитивных зависимостей пакета
        
        Args:
            package_name (str): Имя пакета
            
        Returns:
            set: Множество всех транзитивных зависимостей
        """
        if package_name not in self.graph:
            return set()
        
        transitive_deps = set()
        queue = deque(self.graph[package_name])
        
        while queue:
            dep = queue.popleft()
            if dep not in transitive_deps and dep != package_name:
                transitive_deps.add(dep)
                if dep in self.graph:
                    queue.extend(self.graph[dep])
        
        return transitive_deps
    
    def print_dependency_tree(self, root_package):
        """
        Вывод дерева зависимостей в ASCII-формате
        
        Args:
            root_package (str): Корневой пакет
        """
        print(f"\nДерево зависимостей для пакета '{root_package}':")
        self._print_tree_recursive(root_package, "", set())
    
    def _print_tree_recursive(self, package, prefix, visited):
        """
        Рекурсивный вывод дерева зависимостей
        
        Args:
            package (str): Текущий пакет
            prefix (str): Префикс для отступов
            visited (set): Посещенные пакеты для обнаружения циклов
        """
        if package in visited:
            print(f"{prefix}└── {package} (ЦИКЛ)")
            return
            
        visited.add(package)
        print(f"{prefix}└── {package}")
        
        if package in self.graph:
            dependencies = self.graph[package]
            for i, dep in enumerate(dependencies):
                is_last = i == len(dependencies) - 1
                new_prefix = prefix + ("    " if is_last else "│   ")
                self._print_tree_recursive(dep, new_prefix, visited.copy())
    
    def get_cycles(self):
        """Получение списка обнаруженных циклов"""
        return self.cycles
    
    def has_cycles(self):
        """Проверка наличия циклических зависимостей"""
        return len(self.cycles) > 0