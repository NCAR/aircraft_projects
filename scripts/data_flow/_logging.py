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
            self.log_and_print(f'Directory {d} created')
            
    def initializeFinalMessage(self, flight, project):
        '''
        Prepare for final message information
        '''
        self.final_message = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\r\n'
        self.final_message = (
            f'{self.final_message}Process and Push log for Project:{project}'
        )
        self.final_message = f'{self.final_message}  Flight:{flight}' + '\r\n'
        return self.final_message

    def report(self, final_message, status, project, flight, email, file_ext):
        final_message = final_message + '\nREPORT on shipping of files. \n\n'
        final_message = final_message + 'File Type\tStor\tShip\n'

        for key in file_ext:
            final_message = final_message + key + '\t\t' + str(status[key]["stor"]) + '\t' + str(status[key]["ship"]) + '\n'

        final_message = final_message + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"

        print(final_message)
        msg = MIMEText(final_message)
        msg['Subject'] = f'Process & Push message for:{project}  flight:{flight}'
        msg['From'] = 'ads@groundstation'
        msg['To'] = email

        s = smtplib.SMTP('localhost')
        s.sendmail('ads@groundstation', email, msg.as_string())
        s.quit()

        print("\r\nSuccessful completion. Close window to exit.")
    def _log_and_abort(self, message):
            self.log_and_print(message)
            sys.exit(0)
            
    def run_and_log(self,command, message):
        """Executes a command, logs the message, and handles success/failure.

        Args:
            command (str): The command to execute.
            message (str): The message to log.
        
        Returns:
            bool: True if the command executed successfully, False otherwise.
        """
        self.log_and_print(message)  # Assuming you have a 'log_and_print' function defined
        return os.system(command) == 0