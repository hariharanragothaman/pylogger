"""
Formatting class for the custom logger
"""
import logging

basestring_type = str
unicode_type = str
_TO_UNICODE_TYPES = (unicode_type, type(None))

# Helper method for handling unicode vs non-unicode content


def to_unicode(value):
    """
    Converts a string argument to a unicode string.
    If the argument is already a unicode string or None, it is returned
    unchanged.  Otherwise it must be a byte string and is decoded as utf8.
    """
    if isinstance(value, _TO_UNICODE_TYPES):
        return value
    if not isinstance(value, bytes):
        raise TypeError("Expected bytes, unicode, or None; got %r" % type(value))
    return value.decode("utf-8")


def _safe_unicode(s):
    try:
        return to_unicode(s)
    except UnicodeDecodeError:
        return repr(s)


class LogFormatter(logging.Formatter):
    """
    Log formatter used in Tornado.
    * Timestamps on every log line.
    * Robust against str/bytes encoding problems.
    """

    DEFAULT_FORMAT = "[%(levelname)1.1s %(asctime)s.%(msecs)03d %(module)s:%(lineno)d] [%(threadid)s] %(message)s"
    DEFAULT_DATE_FORMAT = "%y:%m:%d %H:%M:%S"

    def __init__(self, color=True, fmt=DEFAULT_FORMAT, date_format=DEFAULT_DATE_FORMAT):
        logging.Formatter.__init__(self, datefmt=date_format)
        self._fmt = fmt
        self._normal = ""

    def format(self, record):
        try:
            message = record.getMessage()
            assert isinstance(message, basestring_type)
            record.message = _safe_unicode(message)
        except AssertionError as exception:
            record.message = "Bad message (%r): %r" % (exception, record.__dict__)

        record.asctime = self.formatTime(record, self.datefmt)
        formatted = self._fmt % record.__dict__

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            # exc_text contains multiple lines.  We need to _safe_unicode
            # each line separately so that non-utf8 bytes don't cause
            # all the newlines to turn into '\n'.
            lines = [formatted.rstrip()]
            lines.extend(_safe_unicode(ln) for ln in record.exc_text.split("\n"))
            formatted = "\n".join(lines)
        return formatted.replace("\n", "\n    ")
