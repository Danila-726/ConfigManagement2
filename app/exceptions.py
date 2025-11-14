class ValidationError(Exception):
    """Кастомное исключение для ошибок валидации"""
    pass

class RepositoryError(Exception):
    """Ошибки работы с репозиторием"""
    pass

class PackageNotFoundError(Exception):
    """Пакет не найден в репозитории"""
    pass

class APKParseError(Exception):
    """Ошибка парсинга APK данных"""
    pass