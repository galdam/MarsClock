
_LOG_NUMS = {
    'TRACE': 0,
    'DEBUG': 1,
    'INFO': 2,
    'WARN': 3
}

LOG_LEVEL = 'TRACE'


def trace(message, *args):
    _log_message('TRACE', message, *args)


def debug(message, *args):
    _log_message('DEBUG', message, *args)


def info(message, *args):
    _log_message('INFO', message, *args)


def _log_message(log_level, message, *args):
    if _LOG_NUMS[log_level] >= _LOG_NUMS[LOG_LEVEL]:
        print(log_level, message.format(*args))