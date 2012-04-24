#!/bin/bash

unset HOST
unset AIRCRAFT

HOST='eol-rt-data.guest.ucar.edu'
AIRCRAFT='DC8'

USAGE="usage: $0 [-h] [-s ...] [-a ...]
        -h help
        -s server name (default $HOST)
        -a Aircraft name (default $AIRCRAFT)"

while getopts hs:a: c; do
    case $c in
    h)    echo "$USAGE"; exit ;;
    s)    HOST=$OPTARG ;;
    a)    AIRCRAFT=$OPTARG ;;
    esac
done

echo "HOST:" $HOST
echo "AIRCRAFT:" $AIRCRAFT

cat << EOD | psql -h $HOST -U ads -d real-time-$AIRCRAFT
--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: global_attributes; Type: TABLE; Schema: public; Owner: ads; Tablespace: 
--

DROP TABLE global_attributes;
CREATE TABLE global_attributes (
    "key" text NOT NULL,
    value text
);


ALTER TABLE public.global_attributes OWNER TO ads;

--
-- Data for Name: global_attributes; Type: TABLE DATA; Schema: public; Owner: ads
--

INSERT INTO global_attributes VALUES ('Source', 'NASA/NSERC Dryden');
INSERT INTO global_attributes VALUES ('Platform', 'N817NA');
INSERT INTO global_attributes VALUES ('latitude_coordinate', 'GGLAT');
INSERT INTO global_attributes VALUES ('longitude_coordinate', 'GGLON');
INSERT INTO global_attributes VALUES ('zaxis_coordinate', 'GGALT');
INSERT INTO global_attributes VALUES ('time_coordinate', 'datetime');
INSERT INTO global_attributes VALUES ('landmarks', '39.9088 -105.117 jeffco');


--
-- Name: global_attributes_pkey; Type: CONSTRAINT; Schema: public; Owner: ads; Tablespace: 
--

ALTER TABLE ONLY global_attributes
    ADD CONSTRAINT global_attributes_pkey PRIMARY KEY ("key");


--
-- Name: update; Type: RULE; Schema: public; Owner: ads
--

CREATE RULE "update" AS ON UPDATE TO global_attributes DO NOTIFY current;

--
-- Name: variable_list; Type: TABLE; Schema: public; Owner: ads; Tablespace: 
--

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


ALTER TABLE public.variable_list OWNER TO ads;

--
-- Data for Name: variable_list; Type: TABLE DATA; Schema: public; Owner: ads
--

INSERT INTO variable_list VALUES ('GGLAT',       'degree_N', '', 'Reference GPS Latitude',                             '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('GGLON',       'degree_E', '', 'Reference GPS Longitude',                            '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('GGALT',       'm',        '', 'Reference GPS Altitude (MSL)',                       '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('WGSALT',      'm',        '', 'WGS 84 Geoid Altitude',                              '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('PALTF',       'feet',     '', 'NACA Pressure Altitude',                             '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('HGM232',      'feet',     '', 'Radar Altimeter Altitude',                           '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('GSF',         'm/s',      '', 'IRS Aircraft Ground Speed',                          '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('TASX',        'm/s',      '', 'Aircraft True Airspeed Reference',                   '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('IAS',         'knots',    '', 'Indicated Airspeed',                                 '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('MACH_A',      '',         '', 'Aircraft Mach Number',                               '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('VSPD',        'm/s',      '', 'IRS Vertical Speed',                                 '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('THDG',        'degree_T', '', 'IRS Aircraft True Heading Angle',                    '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('TKAT',        'degree_T', '', 'IRS Aircraft Track Angle',                           '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('DRFTA',       'degree',   '', 'IRS Drift Angle',                                    '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('PITCH',       'degree',   '', 'IRS Aircraft Pitch Angle',                           '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('ROLL',        'degree',   '', 'IRS Aircraft Roll Angle',                            '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('SSLIP',       'degree',   '', 'Side Slip Angle',                                    '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('ATTACK',      'degree',   '', 'Angle of Attack',                                    '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('ATX',         'deg_C',    '', 'Ambient Temperature, Reference',                     '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('DPXC',        'deg_C',    '', 'Dew Point',                                          '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('TTX',         'deg_C',    '', 'Total Temperature',                                  '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('PSXC',        'hPa',      '', 'Corrected Static Pressure Reference',                '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('QCXC',        'hPa',      '', 'Dynamic Pressure (total minus static)',              '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('PCAB',        'hPa',      '', 'Cabin Pressure / Altitude',                          '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('WSC',         'm/s',      '', 'GPS-Corrected Horizontal Wind Speed',                '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('WDC',         'degree_T', '', 'GPS-Corrected Horizontal Wind Direction',            '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('WIC',         'm/s',      '', 'GPS-Corrected Wind Vector Vertical Gust Component',  '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('SOLZE',       'degree',   '', 'Solar Zenith Angle',                                 '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('Solar_El_AC', 'degree',   '', 'Sun Elevation from Aircraft',                        '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('SOLAZ',       'degree_T', '', 'Sun Azimuth from Ground',                            '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('Solar_Az_AC', 'degree_T', '', 'Sun Azimuth from Aircraft',                          '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
--
-- Name: variable_list_pkey; Type: CONSTRAINT; Schema: public; Owner: ads; Tablespace: 
--

ALTER TABLE ONLY variable_list
    ADD CONSTRAINT variable_list_pkey PRIMARY KEY (name);
--
-- PostgreSQL database dump complete
--
EOD
