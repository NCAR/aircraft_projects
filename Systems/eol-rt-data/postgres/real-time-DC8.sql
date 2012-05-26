--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET check_function_bodies = false;
SET client_min_messages = warning;
SET search_path = public, pg_catalog;
SET default_tablespace = '';
SET default_with_oids = false;
SET statement_timeout = 0;
SET escape_string_warning = off;

--
-- Name: global_attributes; Type: TABLE; Schema: public; Owner: ads; Tablespace: 
--

ALTER TABLE ONLY global_attributes DROP CONSTRAINT global_attributes_pkey;
DROP TABLE global_attributes;

CREATE TABLE global_attributes (
    "key" text NOT NULL,
    value text
);

ALTER TABLE global_attributes OWNER TO ads;

ALTER TABLE ONLY global_attributes ADD CONSTRAINT global_attributes_pkey PRIMARY KEY ("key");

INSERT INTO global_attributes VALUES ('Source', 'NASA/NSERC Dryden');
INSERT INTO global_attributes VALUES ('Platform', 'N817NA');
INSERT INTO global_attributes VALUES ('FlightNumber', 'FlightNumber');
INSERT INTO global_attributes VALUES ('ProjectName', 'ProjectName');
INSERT INTO global_attributes VALUES ('DataRate', '5');
INSERT INTO global_attributes VALUES ('latitude_coordinate', 'GGLAT');
INSERT INTO global_attributes VALUES ('longitude_coordinate', 'GGLON');
INSERT INTO global_attributes VALUES ('zaxis_coordinate', 'PALTF');
INSERT INTO global_attributes VALUES ('time_coordinate', 'datetime');
INSERT INTO global_attributes VALUES ('landmarks', '39.9088 -105.117 jeffco');
INSERT INTO global_attributes VALUES ('EndTime', '');
INSERT INTO global_attributes VALUES ('StartTime', '');

CREATE RULE "update" AS ON UPDATE TO global_attributes DO NOTIFY current;

--
-- Name: variable_list; Type: TABLE; Schema: public; Owner: ads; Tablespace: 
--

ALTER TABLE ONLY variable_list DROP CONSTRAINT variable_list_pkey;
DROP TABLE variable_list;

CREATE TABLE variable_list (
    name text NOT NULL,
    units text,
    uncalibrated_units text,
    long_name text,
    sampleratetable text,
    ndims integer,
    dims integer[],
    ncals integer,
    poly_cals double precision[],
    missing_value double precision,
    data_quality text
);

ALTER TABLE variable_list OWNER TO ads;

ALTER TABLE ONLY variable_list ADD CONSTRAINT variable_list_pkey PRIMARY KEY (name);

INSERT INTO variable_list VALUES ('GGLAT',                 'degree_N', '', 'Reference GPS Latitude',                             '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('GGLON',                 'degree_E', '', 'Reference GPS Longitude',                            '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('GGALT',                 'm',        '', 'Reference GPS Altitude (MSL)',                       '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('WGSALT',                'm',        '', 'WGS 84 Geoid Altitude',                              '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('PALTF',                 'feet',     '', 'NACA Pressure Altitude',                             '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('HGM232',                'feet',     '', 'Radar Altimeter Altitude',                           '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('GSF',                   'm/s',      '', 'IRS Aircraft Ground Speed',                          '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('TASX',                  'm/s',      '', 'Aircraft True Airspeed Reference',                   '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('IAS',                   'knots',    '', 'Indicated Airspeed',                                 '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('MACH_A',                '',         '', 'Aircraft Mach Number',                               '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('VSPD',                  'm/s',      '', 'IRS Vertical Speed',                                 '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('THDG',                  'degree_T', '', 'IRS Aircraft True Heading Angle',                    '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('TKAT',                  'degree_T', '', 'IRS Aircraft Track Angle',                           '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('DRFTA',                 'degree',   '', 'IRS Drift Angle',                                    '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('PITCH',                 'degree',   '', 'IRS Aircraft Pitch Angle',                           '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('ROLL',                  'degree',   '', 'IRS Aircraft Roll Angle',                            '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('SSLIP',                 'degree',   '', 'Side Slip Angle',                                    '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('ATTACK',                'degree',   '', 'Angle of Attack',                                    '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('ATX',                   'deg_C',    '', 'Ambient Temperature, Reference',                     '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('DPXC',                  'deg_C',    '', 'Dew Point',                                          '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('TTX',                   'deg_C',    '', 'Total Temperature',                                  '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('PSXC',                  'hPa',      '', 'Corrected Static Pressure Reference',                '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('QCXC',                  'hPa',      '', 'Dynamic Pressure (total minus static)',              '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('PCAB',                  'hPa',      '', 'Cabin Pressure / Altitude',                          '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('WSC',                   'm/s',      '', 'GPS-Corrected Horizontal Wind Speed',                '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('WDC',                   'degree_T', '', 'GPS-Corrected Horizontal Wind Direction',            '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('WIC',                   'm/s',      '', 'GPS-Corrected Wind Vector Vertical Gust Component',  '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('SOLZE',                 'degree',   '', 'Solar Zenith Angle',                                 '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('Solar_El_AC',           'degree',   '', 'Sun Elevation from Aircraft',                        '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('SOLAZ',                 'degree_T', '', 'Sun Azimuth from Ground',                            '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('Solar_Az_AC',           'degree_T', '', 'Sun Azimuth from Aircraft',                          '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('VNS_MMS',               '',         '', 'VNS_MMS',                                            '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('VEW_MMS',               '',         '', 'VEW_MMS',                                            '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('VUP_MMS',               '',         '', 'VUP_MMS',                                            '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('COLDCN',                '',         '', 'COLDCN',                                             '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('HOTCN',                 '',         '', 'HOTCN',                                              '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('DRYSCATTERING',         '',         '', 'DRYSCATTERING',                                      '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('CO',                    '',         '', 'CO',                                                 '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('CH4',                   '',         '', 'CH4',                                                '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('WVPPM',                 '',         '', 'WVPPM',                                              '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('C02',                   '',         '', 'C02',                                                '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('NO',                    '',         '', 'NO',                                                 '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('NOY',                   '',         '', 'NOY',                                                '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('O3',                    '',         '', 'O3',                                                 '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('SP2_INCPARTICLECOUNT',  '',         '', 'SP2_INCPARTICLECOUNT',                               '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('HSP2_INCPARTICLECOUNT', '',         '', 'HSP2_INCPARTICLECOUNT',                              '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('SO4',                   '',         '', 'SO4',                                                '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('NO3',                   '',         '', 'NO3',                                                '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('NH4',                   '',         '', 'NH4',                                                '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('TOTAL_ORGANIC',         '',         '', 'TOTAL_ORGANIC',                                      '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('CHLORIDE',              '',         '', 'CHLORIDE',                                           '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('MZ43',                  '',         '', 'MZ43',                                               '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('MZ44',                  '',         '', 'MZ44',                                               '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('MZ57',                  '',         '', 'MZ57',                                               '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('MZ60',                  '',         '', 'MZ60',                                               '', 1, '{1}', 0, '{}', -32767, 'Preliminary');

--
-- Name: raf_lrt; Type: TABLE; Schema: public; Owner: ads; Tablespace: 
--

ALTER TABLE ONLY raf_lrt DROP CONSTRAINT raf_lrt_pkey;
DROP TABLE raf_lrt;

CREATE TABLE raf_lrt (
    datetime timestamp without time zone NOT NULL,
    gglat double precision,
    gglon double precision,
    ggalt double precision,
    wgsalt double precision,
    paltf double precision,
    hgm232 double precision,
    gsf double precision,
    tasx double precision,
    ias double precision,
    mach_a double precision,
    vspd double precision,
    thdg double precision,
    tkat double precision,
    drfta double precision,
    pitch double precision,
    roll double precision,
    sslip double precision,
    attack double precision,
    atx double precision,
    dpxc double precision,
    ttx double precision,
    psxc double precision,
    qcxc double precision,
    pcab double precision,
    wsc double precision,
    wdc double precision,
    wic double precision,
    solze double precision,
    solar_el_ac double precision,
    solaz double precision,
    solar_az_ac double precision,
    vns_mms double precision,
    vew_mms double precision,
    vup_mms double precision,
    coldcn double precision,
    hotcn double precision,
    dryscattering double precision,
    co double precision,
    ch4 double precision,
    wvppm double precision,
    c02 double precision,
    no double precision,
    noy double precision,
    o3 double precision,
    sp2_incparticlecount double precision,
    hsp2_incparticlecount double precision,
    so4 double precision,
    no3 double precision,
    nh4 double precision,
    total_organic double precision,
    chloride double precision,
    mz43 double precision,
    mz44 double precision,
    mz57 double precision,
    mz60 double precision
);

ALTER TABLE raf_lrt OWNER TO ads;

ALTER TABLE ONLY raf_lrt ADD CONSTRAINT raf_lrt_pkey PRIMARY KEY (datetime);

--
-- PostgreSQL database dump complete
--
