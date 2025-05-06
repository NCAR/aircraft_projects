ZITH9tables = {
    'host': {  # enum from zith9 table "file"
        "campaign": 'campaign',
        "hpss": 'HPSS',
        "localhost": 'localhost',
    },
    'datacite_contributor_type': {  # enum from zith9 table "dataset_contact"
        1: 'Contactperson',
        2: 'DataCollector',
        3: 'DataCurator',
        4: 'DataManager',
        5: 'Distributor',
        6: 'Editor',
        7: 'Funder',
        8: 'HostingInstitution',
        9: 'Producer',
        10: 'ProjectLeader',
        11: 'ProjectManager',
        12: 'ProjectMember',
        13: 'RegistrationAgency',
        14: 'RegistrationAuthority',
        15: 'RelatedPerson',
        16: 'Researcher',
        17: 'ResearchGroup',
        18: 'RightsHolder',
        19: 'Sponsor',
        20: 'Supervisor',
        21: 'WorkPackageLeader',
        22: 'Other',
    },
    'iso_citation_role': {  # enum from zith9 table "dataset_contact"
        1: 'resourceProvider',
        2: 'custodian',
        3: 'owner',
        4: 'user',
        5: 'distributor',
        6: 'originator',
        7: 'pointOfContact',
        8: 'principalInvestigator',
        9: 'processor',
        10: 'publisher',
        11: 'author',
        12: 'EOL_internal',
        },
    'quality': {  # enum from zith9 table "file"
        1: 'preliminary',
        2: 'final',
        },
    'purpose': {  # enum from zith9 table "file"
        'data': 'data',
        'doc': 'doc',
        'eula': 'eula',
        'preview': 'preview',
        },
    'spatial_type': {  # enum from zith9 table "dataset"
        'unknown': 'unknown',
        'multiple': 'multiple',
        'grid': 'grid',
        'point': 'point',
        'raster': 'raster',
        'vector': 'vector',
        'textTable': 'textTable',
        'tin': 'tin',
        'stereoModel': 'stereoModel',
        'video': 'video',
        },
    'format': {},  # zith9 table "format"
    'codiac_contact_id_active': {},  # zith9 table "contact" with
                                     # active_editor set to 1
    'codiac_contact_id_all': {},  # zith9 table "contact"
    'category_id': {},  # zith9 "category"
    'frequency_id': {},  # zith9 "frequency"
    'platform_id': {},  # zith9 "platform"
    'instrument_id': {},  # zith9 "instrument"
    'xlink_id': {},
    'note_type_id': {
        1: 'Check',
        2: 'General',
        3: 'Ingest',
        4: 'Load',
        5: 'Process',
        },  # dmg_dts table "note_type"
    'dts_contact_id_active': {},  # dmg_dts table "contact" with
                                  # active_editor set to 1
    'dts_contact_id_all': {},   # dmg_dts table "contact"
    'dts_status_id': {},  # dmg_dts table "status"
}
