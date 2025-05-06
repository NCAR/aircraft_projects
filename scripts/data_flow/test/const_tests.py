import os

# Constants for use in tests
PROJECT = "project_name"
FLIGHT = "tf01"
AIRCRAFT = "C130_N130AR"
DATA_DIR = "data_directory"
RAW_DIR = "raw_data_directory"
PROJ_DIR = "project_directory"
EMAIL = "test@example.com"
FILE_EXT = {
    "ADS": "ads",
    "LRT": "nc",
    "KML": "kml",
    "HRT": "nc",
    "SRT": "nc",
    "ICARTT": "ict",
    "IWG1": "iwg",
    "PMS2D": "2d",
    "threeVCPI": "2ds"
}

# Mock environment variables
env_vars = {
    'PROJECT': PROJECT,
    'DATA_DIR': DATA_DIR,
    'RAW_DATA_DIR': RAW_DIR,
    'PROJ_DIR': PROJ_DIR
}
# Mock user inputs
user_inputs = [
    FLIGHT,  # for readFlight
    EMAIL    # for readEmail
]


# Mock os.listdir return value
listdir_return_value = [AIRCRAFT]

# Mock os.environ.get to use our env_vars
def mock_getenv(var_name):
    return env_vars.get(var_name)

# Mock input to use our user_inputs
def mock_input(prompt):
    return user_inputs.pop(0) if user_inputs else ""
