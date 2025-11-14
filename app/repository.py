import urllib.request
import urllib.error
import tempfile
import os
from pathlib import Path
from exceptions import RepositoryError

class RepositoryManager:
    """Менеджер для работы с репозиториями Alpine Linux"""
    
    def __init__(self, repo_url, test_repo_mode=False):
        self.repo_url = repo_url
        self.test_repo_mode = test_repo_mode
        self._temp_files = []
    
    def __del__(self):
        """Очистка временных файлов"""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception:
                pass
    
    def get_repository_content(self):
        """
        Получение содержимого репозитория
        
        Returns:
            str: Путь к локальному файлу с содержимым репозитория
        """
        if self.test_repo_mode:
            return self._handle_test_repository()
        else:
            return self._handle_remote_repository()
    
    def _handle_test_repository(self):
        """Обработка тестового репозитория (локальный файл)"""
        if not os.path.exists(self.repo_url):
            raise RepositoryError(f"Файл репозитория не существует: {self.repo_url}")
        
        return self.repo_url
    
    def _handle_remote_repository(self):
        """Обработка удаленного репозитория"""
        try:
            # Создаем временный файл для хранения содержимого
            temp_file = tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix='.txt')
            self._temp_files.append(temp_file.name)
            
            # Загружаем содержимое репозитория
            with urllib.request.urlopen(self.repo_url, timeout=30) as response:
                if response.status != 200:
                    raise RepositoryError(f"Ошибка загрузки репозитория: HTTP {response.status}")
                
                # Читаем и сохраняем данные
                data = response.read()
                temp_file.write(data)
                temp_file.close()
                
                return temp_file.name
                
        except urllib.error.URLError as e:
            raise RepositoryError(f"Ошибка подключения к репозиторию: {e}")
        except Exception as e:
            raise RepositoryError(f"Ошибка при работе с репозиторием: {e}")