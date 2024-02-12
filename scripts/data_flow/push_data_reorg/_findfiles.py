from _repetition import *
def step_through_files(self, datalist, fileext, reprocess):
    """
    Handle multiple files of a given type for a single flight.

    Input:
        datalist (list): List of files of the same type.
        fileext (str): File type extension (for user messages).
        reprocess (bool): Whether to prompt the user for file selection.

    Return:
        str: The chosen file from the list, or empty string if user cancels.
    """
    if not reprocess:
        log_and_print(f'Ship is set to True so no need to choose {fileext} to process.')
        return datalist[0]  # No need to choose, return the first file
    i = 0
    while reprocess:  # Loop continuously until user chooses a file
        log_and_print("Stepping through files, please select the right one.")
        datafile = datalist[i]
        message = f"Is this the correct {fileext} file? ({datafile}) (Y/N):"
        ans = input(message).lower()
        if ans == 'y':
            return datafile
        if ans =='n':
            i = (i + 1) % len(datalist)
        else:
            ('Invalid input: select y or n')