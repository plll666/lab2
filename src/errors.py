class NotFlagError(Exception):
    """ошибка отсутствия флага"""
    pass

class InvalidInputError(Exception):
    """ошибка неправильного ввода пользователя"""
    pass

class ArchiveError(Exception):
    """ошибка архивации"""
    pass

class InvalidArchiveError(Exception):
    """Ошибка невалидного архива"""
    pass

class LenArgsError(Exception):
    """ошибка количества аргументов"""
    pass