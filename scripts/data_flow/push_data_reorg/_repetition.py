import os
def log_and_print(self, message, log_level="info"):
    """Logs and prints a message with optional log level.

    Args:
        message (str): The message to log and print.
        log_level (str, optional): The log level for logging the message (e.g., "info", "debug", "error"). Defaults to "info".
    """
    getattr(self.logger, log_level)(message)
    print(message)

def ensure_dir(self, f):
        '''
    Check if the directory exists and make if not
    '''
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)