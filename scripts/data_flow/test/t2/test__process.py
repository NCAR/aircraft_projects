import pytest
from _process import Process

@pytest.mark.parametrize(
    "file_ext, data_dir, flight, filename, raw_dir, status, project,aircraft,inst_dir,rate,config_ext,file_type,proj_dir,file_prefix", [
        # Test Case 1:
        (
            {
                "ADS": "ads",
                "LRT": "nc",
                "HRT": "nc",
                "SRT": "nc",
                "threeVCPI": "2d",
                "ICARTT": "ict",
                "IWG1": "iwg"
            },
            "/Users/srunkel/dev/projects",
            "tf01",
            {},
            "/Users/srunkel/dev/projects",
            {"ADS": {"proc": "N/A", "ship": "No!", "stor": "No!"},
                    "LRT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "KML": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "HRT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "SRT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "ICARTT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "IWG1": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "PMS2D": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "threeVCPI": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "QCplots": {"proc": "No!", "ship": "No!", "stor": "No!"}},
            "CAESAR",
            "C130_N130AR",
            {
                "ADS": '/Users/srunkel/dev/projects',
                "LRT": '/Users/srunkel/dev/projects',
                "KML": '/Users/srunkel/dev/projects',
                "HRT": '/Users/srunkel/dev/projects',
                "SRT": '/Users/srunkel/dev/projects',
                "ICARTT": '/Users/srunkel/dev/projects',
                "IWG1": '/Users/srunkel/dev/projects',
                "PMS2D": '/Users/srunkel/dev/projects',
                "twods": '/Users/srunkel/dev/projects3v_cpi/2DS/CAESAR_TF01/',
                "oap": '/Users/srunkel/dev/projects3v_cpi/oapfiles/',
                "cpi": '/Users/srunkel/dev/projects3v_cpi/CPI/CAESAR_TF01/',
                },
            {
                "LRT": "1",
                "HRT": "25",
                "SRT": "0",
                },
            
            {"LRT": "", "HRT": "h", "SRT": "s", },
            {
                "ADS": "",
                "LRT": "",
                "KML": "",
                "HRT": "h",
                "SRT": "s",
                "ICARTT": "",
                "IWG1": "",
                "PMS2D": "",
                },
            '/Users/srunkel/dev/aircraft_projects',
            
            'CAESARtf01',
        ),
        # Test Case 2:
        (
            {   "ADS": "ads",
                "LRT": "nc",
                "HRT": "nc",
                "SRT": "nc",
                "threeVCPI": "2d",
                "ICARTT": "ict",
                "IWG1": "iwg"
            },
            "/Users/srunkel/dev/projects",
            "tf02",
            {},
            "/Users/srunkel/dev/projects",
            {"ADS": {"proc": "N/A", "ship": "No!", "stor": "No!"},
                    "LRT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "KML": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "HRT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "SRT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "ICARTT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "IWG1": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "PMS2D": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "threeVCPI": {"proc": "No!", "ship": "No!", "stor": "No!"},
                    "QCplots": {"proc": "No!", "ship": "No!", "stor": "No!"}},
            "CAESAR",
            "C130_N130AR",
            {
                "ADS": '/Users/srunkel/dev/projects',
                "LRT": '/Users/srunkel/dev/projects',
                "KML": '/Users/srunkel/dev/projects',
                "HRT": '/Users/srunkel/dev/projects',
                "SRT": '/Users/srunkel/dev/projects',
                "ICARTT": '/Users/srunkel/dev/projects',
                "IWG1": '/Users/srunkel/dev/projects',
                "PMS2D": '/Users/srunkel/dev/projects',
                "twods": '/Users/srunkel/dev/projects3v_cpi/2DS/CAESAR_TF01/',
                "oap": '/Users/srunkel/dev/projects3v_cpi/oapfiles/',
                "cpi": '/Users/srunkel/dev/projects3v_cpi/CPI/CAESAR_TF01/',
                },
            {
                "LRT": "1",
                "HRT": "25",
                "SRT": "0",
                },
            
            {"LRT": "", "HRT": "h", "SRT": "s", },
            {
                "ADS": "",
                "LRT": "",
                "KML": "",
                "HRT": "h",
                "SRT": "s",
                "ICARTT": "",
                "IWG1": "",
                "PMS2D": "",
                },
            '/Users/srunkel/dev/aircraft_projects',
            
            'CAESARtf02',
        ), 
        # ... more test cases with different inputs
    ]
)
def test_process(file_ext, data_dir, flight, filename, raw_dir, status, project,aircraft,inst_dir,rate,config_ext,file_type,proj_dir,file_prefix):
    # Create an instance of the Process class
    process_obj = Process(file_ext, data_dir, flight, filename, raw_dir, status, project,aircraft,inst_dir,rate,config_ext,file_type,proj_dir,file_prefix)

    # Call the process method
    # Assert the expected results
    assert process_obj.stat["LRT"]["proc"] == True
    assert process_obj.stat["HRT"]["proc"] == True
    assert process_obj.stat["SRT"]["proc"] == True
    assert process_obj.stat["threeVCPI"]["proc"] == True
    assert process_obj.stat["ICARTT"]["proc"] == True
    assert process_obj.stat["IWG1"]["proc"] == True
    assert process_obj.stat["PMS2D"]["proc"] == True