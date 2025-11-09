import logging


def setup_logging():
    """Настройка системы логирования"""
    logging.basicConfig(
        filename='shell.log',
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        encoding='utf-8'
    )

def log_command(command):
    """Логирование введеной команды"""
    logging.info(command)

def log_error(error_message):
    """Логирование ошибки"""
    logging.error(error_message)

def log_warning(warning_message):
    """"Логирование предупреждения"""
    logging.warning(warning_message)

def log_success(success_message):
    """Логирование успешного выполнения команды"""
    logging.info(success_message)