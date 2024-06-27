import os
import logging  
import sys
import smtplib  
from email.mime.text import MIMEText



class MyLogger:
    """
    A class for logging and printing messages.

    Args:
        flight (str): The flight information.
        project (str): The project information.
        data_dir (str): The directory path for data.

    Attributes:
        logger (logging.Logger): The logger object.
        final_message (str): The final message for reporting.

    Methods:
        log_and_print: Logs and prints a message with optional log level.
        ensure_dir: Checks if the directory exists and creates it if not.
        initializeFinalMessage: Prepares the final message information.
        report: Generates a report and sends an email.
        _log_and_abort: Logs a message and aborts the program.
        run_and_log: Executes a command, logs the message, and handles success/failure.
    """
    
    def __init__(self):
        # Retrieve the already configured logger by name
        self.logger = logging.getLogger('myLogger')

    def log_and_print(self, message, log_level="info",stack=2):
        """Logs and prints a message with optional log level.

        Args:
            message (str): The message to log and print.
            log_level (str, optional): The log level for logging the message (e.g., "info", "debug", "error"). Defaults to "info".
        """
        getattr(self.logger, log_level)(message, stacklevel=stack)
        print(message)

    def ensure_dir(self, f):
        '''
        Check if the directory exists and make if not
        '''
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d)
            self.log_and_print(f'Directory {d} created', stack =3)
            

    
    def _log_and_abort(self, message):
            self.log_and_print(message, stack=3)
            sys.exit(0)
            
    def run_and_log(self,command, message):
        """Executes a command, logs the message, and handles success/failure.

        Args:
            command (str): The command to execute.
            message (str): The message to log.
        
        Returns:
            bool: True if the command executed successfully, False otherwise.
        """
        self.log_and_print(message,stack=3)  # Assuming you have a 'log_and_print' function defined
        return os.system(command) == 0