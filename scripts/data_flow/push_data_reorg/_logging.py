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
        
def _initializeFinalMessage(self, flight, project):
    '''
    Prepare for final message information
    '''
    self.final_message = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\r\n'
    self.final_message = (
        f'{self.final_message}Process and Push log for Project:{project}'
    )
    self.final_message = f'{self.final_message}  Flight:{flight}' + '\r\n'
    return self.final_message
def _print_final_message(self, project, flight, nas_sync_dir, nas_data_dir):
    final_message = (
        '\n***CAUTION*CAUTION*CAUTION*CAUTION*CAUTION*CAUTION***\n\n'
        + 'Reprocessing so assume ADS already shipped during first processing\n'
    )
    final_message += 'If this is not the case, run\n\n'
    final_message = (
        f'{final_message}"cp /home/data/Raw_Data/{project}/*{flight}.ads {nas_sync_dir}'
        + '/ADS"\n\n'
    )
    final_message = (
        f'{final_message}"cp /home/data/Raw_Data/{project}/*{flight}.ads {nas_data_dir}'
        + '/ADS"\n\n'
    )
    final_message += 'when this script is complete\n\n'
    final_message += '***CAUTION*CAUTION*CAUTION*CAUTION*CAUTION*CAUTION***\n\n'
    log_and_print(final_message)

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
        log_and_print(message)
        sys.exit(0)