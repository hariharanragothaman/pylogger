import threading


class LogFilter:
    """Custom log filter for adding custom fields to log records."""

    def __init__(self):
        pass

    def filter(self, record):
        """Required method that is called when a log record is generated in a logger."""

        # add a custom thread ID to the log format object
        record.threadid = self.get_thread_id()
        return True

    def get_thread_id(self):
        return threading.get_ident()
