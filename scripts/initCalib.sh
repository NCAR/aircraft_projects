#!/bin/bash

createdb -U postgres  calibrations

echo "CREATE TABLE calibrations (
    rid character(36) NOT NULL,
    pid character(36),
    site character varying(20),
    pulled character(1),
    removed character(1),
    exported character(1),
    cal_date timestamp without time zone,
    project_name character varying(32),
    username character varying(32),
    sensor_type character varying(20),
    serial_number character varying(20),
    var_name character varying(20),
    dsm_name character varying(16),
    cal_type character varying(16),
    channel character(2),
    gainbplr character(2),
    ads_file_name character varying(200),
    set_times timestamp without time zone[],
    set_points double precision[],
    averages double precision[],
    stddevs double precision[],
    cal double precision[],
    temperature double precision,
    comment character varying(256)
);" |psql -h localhost -U ads calibrations

