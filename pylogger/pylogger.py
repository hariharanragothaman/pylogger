"""
Logging Utility for internal stuff
"""
import functools
import logging

from logging.handlers import RotatingFileHandler

from logfilter import LogFilter
from logformatter import LogFormatter

bytes_type = bytes
unicode_type = str
basestring_type = str

DEFAULT_LOGGER = "default"
INTERNAL_LOGGER_ATTR = "internal"
CUSTOM_LOGLEVEL = "customloglevel"
logger = None

# Current state of the internal logging settings
_loglevel = logging.DEBUG
_logfile = None
_formatter = None

####################################################################################################################

def get_logger(name=None, logfile=None, level=logging.DEBUG,
               formatter=None, maxBytes=0, backupCount=0, fileLoglevel=None):
    """
    Configures and Returns a logger instance

    :arg string name: Name of the logger object. (default: __name__)
     Multiple calls to ``get_logger()`` with the same name will always return a reference to the same Logger object.
    :param string logfile: Write logs to the specified filename.
    :param int level: Minimum logging-level; default: logging.DEBUG
    :param Formatter formatter: internal LogFormatter python object.
    :param int maxBytes: Size of the logfile when rollover should occur. Defaults to 0, rollover never occurs.
    :param int backupCount: Number of backups to keep. Defaults to 0, rollover never occurs.
    :param int fileLoglevel: Minimum logging-level for file logger
    :return: logging object that has been configured
    """
    _logger = logging.getLogger(name or __name__)
    _logger.propagate = False
    _logger.setLevel(level)

    _logger.addFilter(LogFilter())

    # Reconfigure existing handlers
    has_stream_handler = False
    for handler in list(_logger.handlers):
        if isinstance(handler, logging.StreamHandler):
            has_stream_handler = True

        if isinstance(handler, logging.FileHandler) and hasattr(handler, INTERNAL_LOGGER_ATTR):
            # Internal FileHandler needs to be removed and re-setup to be able
            # to set a new logfile.
            _logger.removeHandler(handler)
            continue

        # reconfigure handler
        handler.setLevel(level)
        handler.setFormatter(formatter or LogFormatter())

    if not has_stream_handler:
        stream_handler = logging.StreamHandler()
        setattr(stream_handler, INTERNAL_LOGGER_ATTR, True)
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter or LogFormatter())
        _logger.addHandler(stream_handler)

    if logfile:
        rotating_filehandler = RotatingFileHandler(filename=logfile, maxBytes=maxBytes, backupCount=backupCount)
        setattr(rotating_filehandler, INTERNAL_LOGGER_ATTR, True)
        rotating_filehandler.setLevel(fileLoglevel or level)
        rotating_filehandler.setFormatter(formatter or LogFormatter(color=False))
        _logger.addHandler(rotating_filehandler)

    return _logger


#######################################################################################################################


# some custom logic area

def setup_default_logger(logfile=None, level=logging.DEBUG, formatter=None, maxBytes=0, backupCount=0):
    global logger
    logger = get_logger(name=DEFAULT_LOGGER, logfile=logfile, level=level, formatter=formatter)
    return logger


def reset_default_logger():
    """
    Resets the internal default logger to the initial configuration
    """
    global logger
    global _loglevel
    global _logfile
    global _formatter
    _loglevel = logging.DEBUG
    _logfile = None
    _formatter = None
    logger = get_logger(name=DEFAULT_LOGGER, logfile=_logfile, level=_loglevel)


# Initially setup the default logger
reset_default_logger()


def loglevel(level=logging.DEBUG, update_custom_handlers=False):
    """
    Set the minimum loglevel for the default logger
    Reconfigures only the internal handlers of the default logger (eg. stream and logfile).
    Update the loglevel for custom handlers by using `update_custom_handlers=True`.

    :param int level: Minimum logging-level (default: `logging.DEBUG`).
    :param bool update_custom_handlers: custom handlers to this logger; set `update_custom_handlers` to `True`
    """
    logger.setLevel(level)

    # Reconfigure existing internal handlers
    for handler in list(logger.handlers):
        if hasattr(handler, INTERNAL_LOGGER_ATTR) or update_custom_handlers:
            # Don't update the loglevel if this handler uses a custom one
            if hasattr(handler, CUSTOM_LOGLEVEL):
                continue

            # Update the loglevel for all default handlers
            handler.setLevel(level)

    global _loglevel
    _loglevel = level


def formatter(formatter, update_custom_handlers=False):
    """
    Set the formatter for all handlers of the default logger
    :param Formatter formatter: default uses the internal LogFormatter.
    :param bool update_custom_handlers: custom handlers to this logger - set ``update_custom_handlers`` to `True`
    """
    for handler in list(logger.handlers):
        if hasattr(handler, INTERNAL_LOGGER_ATTR) or update_custom_handlers:
            handler.setFormatter(formatter)

    global _formatter
    _formatter = formatter


def logfile(filename, formatter=None, mode='a', maxBytes=0, backupCount=0, encoding=None, loglevel=None):
    """
    Function to handle the rotating fileHandler
    :param filename: filename logs are being collected
    :param mode: fileMode
    :param maxBytes: values for roll-over at a pre-determined size; if zero; rollover never occurs
    :param backupCount: if value is non-zero; system saves old logfiles; by appending extensions
    :param encoding: set encoding option; if not None; open file with that encoding.
    :param loglevel: loglevel set
    """
    # Step 1: If an internal RotatingFileHandler already exists, remove it
    for handler in list(logger.handlers):
        if isinstance(handler, RotatingFileHandler) and hasattr(handler, INTERNAL_LOGGER_ATTR):
            logger.removeHandler(handler)

    # Step 2: If wanted, add the RotatingFileHandler now
    if filename:
        rotating_filehandler = RotatingFileHandler(filename,
                                                   mode=mode,
                                                   maxBytes=maxBytes,
                                                   backupCount=backupCount,
                                                   encoding=encoding)

        # Set internal attributes on this handler
        setattr(rotating_filehandler, INTERNAL_LOGGER_ATTR, True)
        if loglevel:
            setattr(rotating_filehandler, CUSTOM_LOGLEVEL, True)

        # Configure the handler and add it to the logger
        rotating_filehandler.setLevel(loglevel or _loglevel)
        rotating_filehandler.setFormatter(formatter or _formatter or LogFormatter(color=False))
        logger.addHandler(rotating_filehandler)


def log_function_call(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        args_str = ", ".join([str(arg) for arg in args])
        kwargs_str = ", ".join(["%s=%s" % (key, kwargs[key]) for key in kwargs])
        if args_str and kwargs_str:
            all_args_str = ", ".join([args_str, kwargs_str])
        else:
            all_args_str = args_str or kwargs_str
        logger.debug("%s(%s)", func.__name__, all_args_str)
        return func(*args, **kwargs)
    return wrap

########################################## END OF CUSTOM LOGIC ######################################################

if __name__ == "__main__":
    _logger = get_logger()
    _logger.info("hello")
