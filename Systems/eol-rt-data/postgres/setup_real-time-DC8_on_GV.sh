#!/bin/bash

# Dev note 'IF EXISTS' clause is only supported in Postgres version 9 and higher.

unset HOST
unset AIRCRAFT

HOST='hyper.raf-guest.ucar.edu'
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
SET statement_timeout = 0;
SET escape_string_warning = off;

--
-- Name: global_attributes; Type: TABLE; Schema: public; Owner: ads; Tablespace: 
--

-- ALTER TABLE ONLY global_attributes DROP CONSTRAINT IF EXISTS global_attributes_pkey;
-- DROP TABLE IF EXISTS global_attributes;

DROP TABLE global_attributes;

CREATE TABLE global_attributes (
    "key" text NOT NULL,
    value text
);

ALTER TABLE global_attributes OWNER TO ads;

INSERT INTO global_attributes VALUES ('Source', 'NASA/NSERC Dryden');
INSERT INTO global_attributes VALUES ('Platform', 'N817NA');
INSERT INTO global_attributes VALUES ('FlightNumber', 'FlightNumber');
INSERT INTO global_attributes VALUES ('ProjectName', 'ProjectName');
INSERT INTO global_attributes VALUES ('DataRate', '1');
INSERT INTO global_attributes VALUES ('latitude_coordinate', 'GGLAT');
INSERT INTO global_attributes VALUES ('longitude_coordinate', 'GGLON');
INSERT INTO global_attributes VALUES ('zaxis_coordinate', 'PALTF');
INSERT INTO global_attributes VALUES ('time_coordinate', 'datetime');
INSERT INTO global_attributes VALUES ('landmarks', '39.9088 -105.117 jeffco');
INSERT INTO global_attributes VALUES ('EndTime', '');
INSERT INTO global_attributes VALUES ('StartTime', '');

ALTER TABLE ONLY global_attributes
    ADD CONSTRAINT global_attributes_pkey PRIMARY KEY ("key");

CREATE RULE "update" AS ON UPDATE TO global_attributes DO NOTIFY current;

--
-- Name: variable_list; Type: TABLE; Schema: public; Owner: ads; Tablespace: 
--

-- ALTER TABLE ONLY variable_list DROP CONSTRAINT IF EXISTS variable_list_pkey;
-- DROP TABLE IF EXISTS variable_list;

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

INSERT INTO variable_list VALUES ('GGLAT',                 'degree_N', '', 'Reference GPS Latitude',                             '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('GGLON',                 'degree_E', '', 'Reference GPS Longitude',                            '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('PALTF',                 'feet',     '', 'NACA Pressure Altitude',                             '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('TASX',                  'm/s',      '', 'Aircraft True Airspeed Reference',                   '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('ATX',                   'deg_C',    '', 'Ambient Temperature, Reference',                     '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('DPXC',                  'deg_C',    '', 'Dew Point',                                          '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('WSC',                   'm/s',      '', 'GPS-Corrected Horizontal Wind Speed',                '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('WDC',                   'degree_T', '', 'GPS-Corrected Horizontal Wind Direction',            '', 1, '{1}', 0, '{}', -32767, 'Preliminary');
INSERT INTO variable_list VALUES ('WIC',                   'm/s',      '', 'GPS-Corrected Wind Vector Vertical Gust Component',  '', 1, '{1}', 0, '{}', -32767, 'Preliminary');

ALTER TABLE ONLY variable_list
    ADD CONSTRAINT variable_list_pkey PRIMARY KEY (name);

--
-- Name: raf_lrt; Type: TABLE; Schema: public; Owner: ads; Tablespace: 
--

-- ALTER TABLE ONLY raf_lrt DROP CONSTRAINT IF EXISTS raf_lrt_pkey;
-- DROP TABLE IF EXISTS raf_lrt;

DROP TABLE raf_lrt;

CREATE TABLE raf_lrt (
    datetime timestamp without time zone NOT NULL,
    gglat double precision,
    gglon double precision,
    paltf double precision,
    tasx double precision,
    atx double precision,
    dpxc double precision,
    wsc double precision,
    wdc double precision,
    wic double precision
);

ALTER TABLE raf_lrt OWNER TO ads;

ALTER TABLE ONLY raf_lrt
    ADD CONSTRAINT raf_lrt_pkey PRIMARY KEY (datetime);

--
-- PostgreSQL database dump complete
--
EOD
