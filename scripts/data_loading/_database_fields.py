#!/usr/bin/env python
from _zith9 import ZITH9tables
import re
from _mysql_connect import mysqlConnect

search_dict = { "dts_status_id": ['ingest_status_id_dts', 'load_status_id_dts',
                'approve_status_id_dts'], 
               'dts_contact_id_active':['ingest_contact_id_dts', 'load_contact_id_dts',
                'approve_contact_id_dts', 'internal_contact_id_dts',
                'author_id_dts'],
               "dts_contact_id_all": ['source_contact_id_dts', 'dts_contact_id_all'],
               "codiac_contact_id_all":['point_of_contact_id_codiac', 'contact_id_codiac',
                'codiac_contact_id_all'],
               "codiac_contact_id_active":['internal_contact_id_codiac',
                'codiac_contact_id_active']
    
}

class FieldsCheck:
    def __init__(self):
        self.tables = self.populate_table(ZITH9tables)
        self.search_dict = search_dict

    def populate_table(self, zith9dict):
        lF = mysqlConnect('loaddata.py')
        lF.connectCODIAC("full_name", "format", "format", zith9dict)
        lF.connectCODIAC("name", "frequency", "frequency_id", zith9dict)
        lF.connectCODIAC("name", "category", "category_id", zith9dict)
        lF.connectCODIAC("name", "platform", "platform_id", zith9dict)
        lF.connectCODIAC("id", "xlink", "xlink_id", zith9dict)
        lF.connectCODIAC("name", "instrument", "instrument_id", zith9dict)
        lF.connectCODIAC("person_name", "contact",
                                "codiac_contact_id_active", zith9dict)
        ##Populate DTS fields   
        lF.connectDTS("name", "status", "dts_status_id", zith9dict)

        lF.connectDTS("contact_short_name", "contact",
                                "dts_contact_id_active", zith9dict)

        lF.connectDTS("contact_short_name", "contact",
                                "dts_contact_id_all", zith9dict)


        lF.connectCODIAC("person_name", "contact",
                                    "codiac_contact_id_all", zith9dict)

        
        ##Switch keys and values to check the user's input
        """ for group in zith9dict:
            switched_dict ={}
            for key, value in zith9dict[group].items():
                switched_dict[value] = key
            zith9dict[group] =switched_dict """
        # Add the switched key-value pair to the new dictionary
        #   
        return zith9dict