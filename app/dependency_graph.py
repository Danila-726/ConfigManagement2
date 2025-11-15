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
    
    def get_reverse_dependencies(self, target_package):
        """
        Поиск обратных зависимостей - пакетов, которые зависят от целевого пакета
        
        Args:
            target_package (str): Целевой пакет
            
        Returns:
            list: Список пакетов, которые зависят от целевого пакета
        """
        reverse_deps = []
        
        # Проходим по всем пакетам в графе и ищем те, которые зависят от target_package
        for package, dependencies in self.graph.items():
            if target_package in dependencies:
                reverse_deps.append(package)
        
        return reverse_deps
    
    def get_transitive_reverse_dependencies(self, target_package):
        """
        Поиск транзитивных обратных зависимостей с использованием DFS без рекурсии
        
        Args:
            target_package (str): Целевой пакет
            
        Returns:
            set: Множество всех пакетов, которые прямо или косвенно зависят от целевого пакета
        """
        if target_package not in self.graph:
            return set()
        
        transitive_reverse_deps = set()
        stack = [target_package]
        
        while stack:
            current_package = stack.pop()
            
            # Находим все пакеты, которые зависят от current_package
            for package, dependencies in self.graph.items():
                if current_package in dependencies and package not in transitive_reverse_deps:
                    transitive_reverse_deps.add(package)
                    stack.append(package)
        
        return transitive_reverse_deps
    
    def print_reverse_dependencies(self, target_package):
        """
        Вывод обратных зависимостей в консоль
        
        Args:
            target_package (str): Целевой пакет
        """
        direct_reverse = self.get_reverse_dependencies(target_package)
        transitive_reverse = self.get_transitive_reverse_dependencies(target_package)
        
        print(f"\nОбратные зависимости пакета '{target_package}':")
        
        print(f"\nПрямые обратные зависимости (пакеты, которые напрямую зависят от '{target_package}'):")
        if direct_reverse:
            for i, dep in enumerate(direct_reverse, 1):
                print(f"  {i}. {dep}")
        else:
            print("  Не найдено пакетов, которые напрямую зависят от данного")
        
        print(f"\nТранзитивные обратные зависимости (все пакеты, которые прямо или косвенно зависят от '{target_package}'):")
        if transitive_reverse:
            for i, dep in enumerate(transitive_reverse, 1):
                print(f"  {i}. {dep}")
        else:
            print("  Не найдено пакетов, которые транзитивно зависят от данного")
        
        print(f"\nСтатистика:")
        print(f"  Прямые обратные зависимости: {len(direct_reverse)}")
        print(f"  Транзитивные обратные зависимости: {len(transitive_reverse)}")
    
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